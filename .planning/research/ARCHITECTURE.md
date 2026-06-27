# Architecture Research

**Domain:** MCP server — LLM-backed legal decision-support with deterministic grounding + self-evaluating eval harness
**Researched:** 2026-06-27
**Confidence:** HIGH (engine decisions locked in PROJECT.md; stack/tooling verified against current FastMCP 3.x, Anthropic SDK, VCR.py docs)

---

## Architectural Thesis (read this first)

This is **not** a parser project with tests bolted on. It is an **eval harness that happens to drive a small MCP server**. The headline deliverable is a *measured hallucination rate*, which means the thing that must exist and be trustworthy **first** is the labeled dataset + scorer. The server is the system-under-test, not the product.

Two hard architectural rules fall out of this and shape everything below:

1. **The deterministic core is the trust boundary.** The LLM proposes (extraction, reasoning); deterministic code disposes (grounding verification, date math, label aggregation). No LLM output reaches a tool result without passing through a deterministic gate. This is the entire reliability claim.
2. **Eval-first build order is non-negotiable.** You cannot score logic that scores against ground truth you haven't built yet. Phase 1 builds data + harness + scorer against a **stub/oracle** server. Real server logic is Phase 2+. (Justified in detail in Build Order, below.)

---

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATION (outside the repo's trust boundary)                    │
│  Client-Claude / MCP Inspector / eval-runner composes the 4 tools     │
└───────────────┬──────────────────────────────────────────────────────┘
                │  MCP (stdio) — tool calls
┌───────────────▼──────────────────────────────────────────────────────┐
│  MCP SERVER LAYER  (FastMCP 3.x — src/<pkg>/server.py)                │
│  4 single-purpose @mcp.tool functions. Thin adapters: validate I/O,   │
│  call core, return structured Pydantic result. NO business logic here.│
│  ┌────────────────┐ ┌────────────────┐ ┌────────────┐ ┌────────────┐ │
│  │extract_break_  │ │check_conditions│ │find_       │ │assess_     │ │
│  │clause          │ │                │ │citation    │ │validity    │ │
│  └───────┬────────┘ └───────┬────────┘ └─────┬──────┘ └─────┬──────┘ │
├──────────┼──────────────────┼────────────────┼──────────────┼────────┤
│  DETERMINISTIC CORE  (src/<pkg>/core/ — pure Python, NO network)      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  grounding.py   verbatim span verifier (THE trust gate)         │ │
│  │  dates.py       UK date parse, "not less than N months" math    │ │
│  │  checklist.py   4 conditions → pass/fail/uncertain              │ │
│  │  aggregate.py   strict-precedence label (fail>uncertain>pass)   │ │
│  │  models.py      Pydantic types: Span, Clause, ConditionResult…  │ │
│  └────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────┤
│  LLM ADAPTER  (src/<pkg>/llm/ — the ONLY network egress)             │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  client.py   Anthropic SDK wrapper. temp=0. model injectable.   │ │
│  │  extract.py  prompt + tool-use schema → raw candidate spans     │ │
│  │  reason.py   prompt → condition reasoning (still ungrounded!)   │ │
│  └────────────────────────────────────────────────────────────────┘ │
│         │ httpx (intercepted by VCR.py during eval)                   │
│         ▼                                                              │
│   Anthropic API  (claude-haiku-4-5 | claude-sonnet-4-6)              │
└──────────────────────────────────────────────────────────────────────┘

           ╔══════════════════════════════════════════════════╗
           ║  EVAL HARNESS  (tests/eval/ + data/ + report/)    ║
           ║  Drives the server tools, scores against labels,  ║
           ║  records/replays cassettes, emits markdown+chart. ║
           ║  This is the PRIMARY deliverable. Built FIRST.    ║
           ╚══════════════════════════════════════════════════╝
```

### Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| **MCP server layer** (`server.py`) | Register 4 tools; marshal inputs/outputs; attach disclaimer. **No logic.** | FastMCP 3.x `@mcp.tool`; `[project.scripts]` → `mcp.run()` |
| **grounding.py** | Verify a claimed span occurs **verbatim** in source; return verified span or `NOT_FOUND`. The single trust gate. | Pure Python `str.find` / exact-substring; offset reconciliation |
| **dates.py** | Parse UK dates; compute notice-period math ("not less than N months"), break-date expiry, weekend/clear-days rules | Pure Python (`datetime` + `dateutil.relativedelta` for month math) |
| **checklist.py** | Evaluate the 4 conditions precedent → `pass` / `fail` / `uncertain` each | Pure Python rules over grounded inputs |
| **aggregate.py** | Strict-precedence rollup → `VALID` / `INVALID` / `AMBIGUOUS` + calibration | Pure Python; deterministic, total function |
| **models.py** | Shared Pydantic types crossing every boundary (`Span`, `Clause`, `ConditionResult`, `Assessment`) | Pydantic v2 |
| **llm/client.py** | Only network egress. Anthropic SDK, `temperature=0`, model param injectable | `anthropic` SDK (httpx under hood) |
| **llm/extract.py**, **reason.py** | Turn lease text into *candidate* spans / reasoning. Output is **untrusted** until grounded. | Tool-use / `messages.parse()` structured output |
| **Eval harness** | Load cases → run pipeline → score 4 metrics → emit report; cassette record/replay | pytest + pytest-recording (VCR.py) |

---

## Tool Boundaries (the four tools)

Design principle: **each tool does one verifiable thing; deterministic verification always wraps LLM output before return.** Client-Claude composes the tools; the *server* owns the API calls.

### 1. `extract_break_clause(lease_text: str) -> ExtractResult`
- **LLM-backed** (extraction) **+ deterministic gate.**
- Flow: `llm/extract` proposes the clause + a candidate span → `grounding.verify()` confirms the span is verbatim in `lease_text` → return `{clause_text, span, found: bool}`.
- **Returns `NOT_FOUND`** (not a fabricated clause) if the model's quoted span isn't a verbatim substring. This is the first place hallucination is caught.
- Output: clause text + **verified** `Span` (start, end, quoted_text).

### 2. `check_conditions(clause, facts) -> list[ConditionResult]`
- **Fully deterministic** over already-grounded inputs (plus optional LLM reasoning for the *uncertain* classification on genuinely fuzzy wording — but the pass/fail decision logic is code).
- Evaluates the **four conditions precedent**: notice timing, notice validity, rent/no-arrears, vacant possession.
- Each condition → `pass | fail | uncertain`, each carrying the grounded span(s) it relied on.
- Date-sensitive conditions (notice timing, break-date) call `dates.py`. No date arithmetic is ever done by the LLM.

### 3. `find_citation(claim: str, source_text: str) -> CitationResult`
- **Deterministic verifier**, exposed as a tool. This is `grounding.verify()` with a tool wrapper.
- Returns the **exact verbatim** supporting substring **or `NOT_FOUND`**. Never paraphrases, never "close enough".
- Why a standalone tool: lets client-Claude (and the eval) independently check any claim's groundedness — and it's the unit the citation-faithfulness metric scores directly.

### 4. `assess_validity(lease_text, facts) -> Assessment`
- **Orchestrating tool — but orchestration lives server-side here**, not only in client-Claude.
- Composes the others internally: `extract_break_clause` → `check_conditions` → (every asserted condition re-checked through `find_citation`/grounding) → `aggregate.py` for the strict-precedence label.
- Returns: `label ∈ {VALID, INVALID, AMBIGUOUS}`, per-condition results with citations, an explicit **calibration field**, and **mandatory human-verify gates** in the payload + disclaimer.
- Note for the roadmap: the *same composition* can be performed by client-Claude calling tools 1–3 directly; `assess_validity` is the server-side, self-contained path that the eval drives so the measurement is reproducible without a client LLM.

**Deterministic vs LLM split, at a glance:**

| Tool | LLM does | Deterministic code does |
|------|----------|-------------------------|
| extract_break_clause | propose clause + span | verify span verbatim → NOT_FOUND |
| check_conditions | (optional) flag uncertain wording | all pass/fail logic + date math |
| find_citation | nothing | exact-substring grounding |
| assess_validity | (via sub-tools only) | compose + aggregate + label |

---

## The Grounding Gate (core reliability mechanism)

**Placement:** `core/grounding.py`, called by every tool that emits a citation, **between** the LLM adapter and the tool return. It is the chokepoint — no path returns a citation without passing through it.

**Span representation — recommendation: quoted text + exact-substring check, with offsets derived deterministically.**
- The LLM returns the **quoted text** it claims supports the assertion. Models are unreliable at counting character offsets, so do **not** trust LLM-emitted offsets.
- Gate computes `idx = source_text.find(quoted_text)`. If `idx == -1` → **NOT_FOUND**. If found → the gate *derives* the authoritative `Span(start=idx, end=idx+len, quoted_text=...)`.
- Apply a single, documented normalization (collapse internal whitespace/newlines, NFC unicode) on **both** sides before matching — lease text wraps lines and the model rejoins them. Normalization must be deterministic and reversible to original offsets, or matching is done on a normalized copy with an offset map back to the raw source. Decide this once in Phase 2 and freeze it; it directly moves the citation-faithfulness number.

**NOT_FOUND propagation (how ungrounded claims are stopped at the boundary):**
```
LLM proposes span ──► grounding.verify(quoted, source)
                          │
              ┌───────────┴───────────┐
        verbatim match            no match
              │                       │
        Span(verified)           NOT_FOUND  ◄── never replaced by LLM text
              │                       │
              ▼                       ▼
   condition uses span      condition := uncertain (cannot rely on ungrounded claim)
              │                       │
              └──────────┬────────────┘
                         ▼
                  aggregate.py
   any fail → INVALID │ any uncertain (incl. NOT_FOUND-driven) → AMBIGUOUS │ all pass → VALID
```
A `NOT_FOUND` can never be upgraded to a citation by anything downstream. The strongest outcome a `NOT_FOUND`-backed condition can produce is `uncertain`, which forces **AMBIGUOUS** ("human verify") — exactly the conservative calibration the project promises. This is the mechanism that makes "would rather say ambiguous than guess" *true by construction*, not by prompt.

---

## Deterministic Core

### Date math (`dates.py`)
- **UK date formats:** DD/MM/YYYY, "1 September 2027", "1st Sept 2027". Parse explicitly to UK day-first; never rely on locale.
- **"not less than N months' notice":** add N calendar months to notice-service date and compare against break date. Use `dateutil.relativedelta(months=N)` for correct month arithmetic (Jan 31 → Feb edge cases). Encode the clause's own convention (clear days, corresponding-date rule) and **document the simplified ruleset** — this is a clean-room simplification, state its assumptions.
- **Break-date expiry:** if notice cannot be validly served in time to satisfy the notice period before the break date → notice-timing condition `fail`.
- Pure functions, fully unit-tested independent of the LLM (fast, in CI, no key).

### Checklist evaluation (`checklist.py`)
- One evaluator per condition; each takes grounded facts/spans, returns `ConditionResult{status, citations, reason}`.
- Missing or `NOT_FOUND` evidence for a condition → `uncertain` (never silently `pass`). Absence of evidence is not evidence of compliance.

### Strict-precedence aggregation (`aggregate.py`)
- Total, deterministic function over the 4 results:
  - **any `fail` → INVALID** (highest precedence)
  - else **any `uncertain` → AMBIGUOUS**
  - else **all `pass` → VALID**
- Emits the **calibration field** (e.g., which conditions forced the label, count of grounded vs ungrounded). Property-test it: exhaustive over 3⁴ = 81 input combinations — trivial and gives a hard correctness guarantee on the headline logic.

---

## Case-File Input Model

**One document = lease provisions + a `Background Facts` section.** "Can the break actually be exercised?" needs facts (was rent paid? was possession vacant? when was notice served?), not just the clause.

- **Both conditions AND facts are grounded against the same document.** A fact asserted in reasoning ("rent was in arrears") must cite a verbatim span from `Background Facts`, exactly like a clause citation. Nothing is un-cited.
- Recommended structure: a lightweight, parseable case file (Markdown with `## Lease` and `## Background Facts`, or YAML front-matter + body) so the harness can load `(lease_text, facts_text, expected_label, ground_truth_spans)` deterministically.
- Grounding source for `find_citation` is the **whole document** (lease + facts), so both provision-citations and fact-citations resolve through the identical gate.

---

## Eval Harness Architecture (the primary deliverable)

```
data/cases/*.md            tests/eval/                 report/
 ┌─────────────┐           ┌──────────────┐            ┌──────────────┐
 │ case_001.md │──load────►│ runner       │            │ report.md    │
 │  ## Lease   │           │  ↳ drives    │──scores──► │ metrics.json │
 │  ## Facts   │           │   assess_    │            │ chart.png/svg│
 │  ---meta--- │           │   validity   │            └──────────────┘
 │  label:     │           ├──────────────┤
 │  spans:     │           │ scorer       │   cassettes/
 └─────────────┘           │  4 metrics   │   ┌──────────────┐
                           ├──────────────┤   │ case_001.yaml│◄─record live
                           │ cassette I/O │──►│ (key stripped)│  replay in CI
                           └──────────────┘   └──────────────┘
```

### Dataset format (20–40 labeled cases)
Each case file carries: the document (lease + facts), the **known label** (`valid`/`invalid`/`ambiguous`), and **ground-truth spans** (the verbatim text the correct citation should return per condition). Coverage must span every failure mode: missed date, defective notice, outstanding rent, vacant-possession breach, and genuinely ambiguous wording (which must label `ambiguous`, validating calibration — not every case is decidable).

### Scorer (4 metrics)
| Metric | Measures | Computed as |
|--------|----------|-------------|
| Extraction accuracy | did it find the right clause | predicted clause span vs ground-truth span overlap |
| Citation faithfulness | are citations verbatim & correct | every returned citation is a verbatim substring AND matches ground-truth evidence |
| **Hallucination rate** (headline) | ungrounded claims that escaped | count of asserted-but-not-grounded citations / total claims — *target: 0; the gate should make this 0 by construction* |
| Calibration | does it abstain when it should | accuracy on `ambiguous` cases; false-confident rate (said VALID/INVALID where truth is ambiguous) |

### Cassette layer (record live → replay key-free in CI)
- **Tool:** `pytest-recording` (VCR.py 8.x). The Anthropic SDK uses **httpx** under the hood, which VCR.py intercepts cleanly — no manual mocking of the SDK.
- **Placement:** wraps the **LLM adapter boundary only** (`llm/client.py` HTTP calls). Deterministic core needs no cassettes — it has no network.
- **Record mode:** live run uses `--record-mode=once`/`all` with a real key to capture real model behavior (so the measured rate reflects a real LLM in the loop). CI uses **`record_mode="none"`** → replay only, **fails if an un-recorded request is attempted** → guarantees no key needed and full determinism.
- **Key safety:** `filter_headers=['authorization', 'x-api-key']` (and any `anthropic-*` auth headers) so no secret is ever written to a cassette committed to the repo. Verify cassettes are scrubbed before commit — this is a public credibility repo.
- **<2 min in CI:** replay is local file I/O; the whole 20–40 case suite runs in seconds once cassettes exist.

### Comparative Haiku vs Sonnet
- Model ID is **injected** into `llm/client.py` (`claude-haiku-4-5` vs `claude-sonnet-4-6`); the harness is parametrized over the model and run twice.
- **Separate cassette sets per model** (e.g., `cassettes/haiku/`, `cassettes/sonnet/`) — same harness, two recordings, two report columns. Frames reliability as a cost/deployment decision (the FDE register), at near-zero extra build cost.

### Report generator
- `report/` script reads `metrics.json` → emits `report.md` (hallucination rate as headline, all 4 metrics, Haiku-vs-Sonnet table) + one simple chart (matplotlib bar/SVG). Linked from the README. Keep it dependency-light.

---

## Recommended Project Structure

```
uk-break-clause-analyzer-mcp/
├── pyproject.toml              # Python 3.12, uv; [project.scripts] console entry
├── README.md                   # story-led; 1 diagram; eval results; <2min clone-to-run
├── src/
│   └── break_clause_analyzer/
│       ├── __init__.py
│       ├── server.py           # FastMCP app + 4 @mcp.tool; entry point target
│       ├── core/               # DETERMINISTIC — no network, no LLM imports
│       │   ├── grounding.py    # verbatim gate (THE trust boundary)
│       │   ├── dates.py        # UK date math
│       │   ├── checklist.py    # 4-condition evaluation
│       │   ├── aggregate.py    # strict-precedence label + calibration
│       │   └── models.py       # shared Pydantic types
│       └── llm/                # ONLY network egress
│           ├── client.py       # Anthropic SDK wrapper; temp=0; model injectable
│           ├── extract.py      # clause/span extraction prompt + schema
│           └── reason.py       # condition reasoning prompt
├── data/
│   └── cases/                  # 20–40 labeled case files (lease+facts+label+spans)
├── tests/
│   ├── unit/                   # core/* pure-function tests (fast, no key)
│   └── eval/
│       ├── runner.py           # load cases → drive tools → collect outputs
│       ├── scorer.py           # 4 metrics
│       ├── conftest.py         # pytest-recording config; header filtering
│       └── cassettes/
│           ├── haiku/          # recorded HTTP interactions (key-stripped)
│           └── sonnet/
└── report/
    ├── generate.py             # metrics.json → report.md + chart
    └── report.md               # published artifact (headline: hallucination rate)
```

### Structure Rationale
- **`core/` cannot import `llm/`** (enforce via import-lint or a simple test). This makes the trust boundary structural, not conventional: deterministic code physically cannot depend on the model.
- **`server.py` is thin** — tools are adapters over `core/` + `llm/`. Keeps tools individually testable and the MCP surface trivial to audit.
- **`data/` is first-class, sibling to `src/`** — signals it's a primary artifact, and the harness loads it by path (not packaged).
- **`tests/eval/` separate from `tests/unit/`** — unit tests run key-free always; eval replays cassettes in CI and records live on demand.
- **`[project.scripts]`** maps a console command (e.g., `break-clause-analyzer = "break_clause_analyzer.server:main"`) where `main()` calls `mcp.run()` — installable via `uvx`/`pip`, passes MCP Inspector with one command.

---

## Architectural Patterns

### Pattern 1: Propose-then-Verify (LLM proposes, deterministic code disposes)
**What:** Every LLM output is a *candidate* until a pure function verifies it. Grounding gate, date math, and aggregation are all deterministic verifiers.
**When:** Any time correctness/trust matters and the LLM is fallible.
**Trade-offs:** Slightly more code than "trust the model"; in exchange you get a *provable* hallucination rate and conservative failure. For this project that trade is the entire point.
```python
candidate = llm_extract(lease_text)            # untrusted
span = grounding.verify(candidate.quote, lease_text)  # -> Span | NOT_FOUND
return Clause(text=candidate.text, span=span)  # span may be NOT_FOUND, never fabricated
```

### Pattern 2: Deterministic-core / LLM-shell isolation
**What:** Network + non-determinism confined to `llm/`. `core/` is pure, total, unit-testable, key-free.
**When:** Whenever you need fast CI, reproducibility, and an auditable trust boundary.
**Trade-offs:** Discipline to keep the boundary clean (no sneaking an API call into a checklist). Payoff: 81-case exhaustive test of the label logic; date math tested with zero API cost.

### Pattern 3: Cassette-wrapped boundary for reproducible LLM eval
**What:** Record real HTTP at the SDK/httpx boundary once; replay deterministically forever; CI runs key-free.
**When:** Eval that must measure a real model yet reproduce identically in CI.
**Trade-offs:** Cassettes drift if prompts change (re-record). Must scrub auth headers (public repo). Payoff: a reviewer reproduces the headline number in <2 min with no key.

### Pattern 4: Strict-precedence aggregation as a total function
**What:** Label = deterministic fold over condition statuses with fixed precedence (fail > uncertain > pass).
**When:** You need conservative, explainable, calibratable verdicts.
**Trade-offs:** Cannot express nuanced weighting — by design. Conservatism (default to AMBIGUOUS) is the calibration story.

---

## Data Flow

### `assess_validity` request flow (server-side composition)
```
case document (lease + Background Facts)
        ↓
extract_break_clause ─► llm/extract ─► grounding.verify ─► Clause{span | NOT_FOUND}
        ↓
check_conditions ─► dates.py + checklist.py over GROUNDED inputs
        │   (each fact/condition citation re-verified via grounding gate)
        ↓
per-condition: pass | fail | uncertain  (NOT_FOUND ⇒ uncertain)
        ↓
aggregate.py (strict precedence) ─► label + calibration + human-verify gates
        ↓
Assessment{label, conditions[citations], calibration, disclaimer}
```

### Eval data flow
```
data/cases/*.md ─► runner ─► (server tools, LLM calls via cassette) ─► outputs
                                                                          ↓
ground-truth labels+spans ─────────────────► scorer ─► metrics.json ─► report
```

### Key data flows
1. **Grounding propagation:** candidate quote → verify → `Span | NOT_FOUND`; NOT_FOUND can only ever degrade a verdict toward AMBIGUOUS, never be replaced by model text.
2. **Model injection:** `model_id` threads from harness → `llm/client.py`, enabling the same pipeline to run as Haiku and Sonnet against separate cassette sets.

---

## Build Order (eval-first — make this unambiguous in the roadmap)

> **The labeled dataset + scoring harness come FIRST, before any server business logic.** This is the project's thesis, not a preference.

**Why first (justification for the roadmap):**
- You cannot measure a hallucination rate without ground truth to measure against. The scorer is meaningless until the labeled cases exist.
- Building the harness against a **stub/oracle server** (hand-written correct outputs for a few cases) proves the *measurement apparatus* is correct independently of the *system under test*. Otherwise a passing eval might mean "logic is right" OR "scorer is broken" — indistinguishable.
- It forces the data contract (`Span`, labels, case format) to be designed before code depends on it, so server tools are built to a known target.
- It is the headline deliverable; everything else is the system it grades.

**Recommended phase ordering:**

| Phase | Builds | Depends on | Proves |
|-------|--------|-----------|--------|
| **1 — Data + Harness (FIRST)** | 20–40 labeled case files; `models.py` (Span, labels); scorer (4 metrics); runner against a **stub/oracle** server; cassette plumbing (record/replay/CI key-free); report generator skeleton | nothing | the measurement apparatus is correct; ground truth exists |
| **2 — Deterministic core** | `grounding.py`, `dates.py`, `checklist.py`, `aggregate.py` + exhaustive unit tests (81-combo aggregate, date edge cases) | Phase 1 types | the trust boundary + verdict logic are provably correct, key-free |
| **3 — LLM adapter + extraction** | `llm/client.py` (temp=0, model-injectable), `extract.py`, `reason.py`; record first real cassettes | Phases 1–2 | real model in the loop; candidates flow into the gate |
| **4 — MCP server surface** | `server.py` 4 tools wiring core+llm; `[project.scripts]`; MCP Inspector pass | Phases 1–3 | composable tools; one-command run |
| **5 — Measure + report + compare** | run full eval live, record cassettes, Haiku-vs-Sonnet, publish report; README story + diagram + results | all | the headline hallucination rate, reproducibly |

Phases 2 and 3 can overlap only after Phase 1 fixes the data contract. **Nothing starts before Phase 1's dataset + scorer exist.**

---

## Anti-Patterns

### Anti-Pattern 1: Trusting LLM-emitted character offsets
**What people do:** Ask the model for `start`/`end` indices and store them as the span.
**Why it's wrong:** Models miscount offsets constantly; you'd cite the wrong text while "passing" grounding.
**Do this instead:** Take the model's **quoted text**, `find()` it in the source, derive offsets in code. Quote is the source of truth; offsets are computed.

### Anti-Pattern 2: Letting the LLM do date arithmetic or the final verdict
**What people do:** "Ask Claude whether the notice was in time / whether the break is valid."
**Why it's wrong:** Destroys reproducibility and the calibration guarantee; the verdict becomes a guess.
**Do this instead:** LLM extracts dates *as quoted text*; `dates.py` computes; `aggregate.py` labels. Determinism owns every decision.

### Anti-Pattern 3: Building server logic before the eval harness
**What people do:** Write the tools first, add tests later.
**Why it's wrong:** No ground truth ⇒ no way to know the logic is right; you can't distinguish a logic bug from a scorer bug; the headline metric becomes an afterthought instead of the design driver.
**Do this instead:** Phase 1 = data + scorer + stub. Eval-first.

### Anti-Pattern 4: Committing un-scrubbed cassettes / hard-failing CI on missing key
**What people do:** Record cassettes with the API key in headers, or let CI hit the network.
**Why it's wrong:** Leaks secrets in a public repo; CI becomes flaky/non-reproducible and needs a key.
**Do this instead:** `filter_headers=['authorization','x-api-key']`; CI `record_mode="none"` (replay-only, fail on un-recorded request).

### Anti-Pattern 5: Fat tools with business logic in `server.py`
**What people do:** Put grounding/date/label logic inside the `@mcp.tool` functions.
**Why it's wrong:** Logic becomes untestable without spinning up MCP; the audit surface balloons.
**Do this instead:** Tools are thin adapters; all logic in `core/` and `llm/`, tested directly.

---

## Integration Points

### External Services
| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Anthropic API | `anthropic` SDK in `llm/client.py`; httpx under hood; temp=0; model injectable | Only egress. VCR.py intercepts httpx for cassettes. Models: `claude-haiku-4-5`, `claude-sonnet-4-6` (verify exact IDs at build time). |
| MCP client (Claude / Inspector) | FastMCP 3.x over stdio | Composes the 4 tools. `[project.scripts]` → `mcp.run()`. |

### Internal Boundaries
| Boundary | Communication | Notes |
|----------|---------------|-------|
| server ↔ core | direct Python call | tools are thin adapters |
| server ↔ llm | direct Python call | only via tools that need extraction/reasoning |
| **core ↔ llm** | **none (forbidden)** | enforce: `core/` must not import `llm/` — structural trust boundary |
| eval ↔ server | drives tools / `assess_validity` | cassettes wrap the llm/httpx boundary beneath |
| eval ↔ data | file load by path | case files + ground truth |

---

## Scaling Considerations

This is a portfolio/credibility artifact with a fixed 20–40 case suite, not a multi-tenant service — "scale" here means **eval throughput and reproducibility**, not user load.

| Scale | Adjustments |
|-------|-------------|
| 20–40 cases (target) | Single process; cassette replay; whole suite in seconds (<2 min incl. report) |
| Hundreds of cases | Parametrized pytest + `pytest-xdist` for parallel replay; cassettes still local |
| Adding models | Extend model matrix; one cassette dir per model; report gains columns |

### Scaling Priorities
1. **First bottleneck:** live recording latency (real API). Fix: record once, replay in CI (`record_mode="none"`). Already the design.
2. **Second bottleneck:** cassette drift when prompts change. Fix: deterministic re-record step + scrub check in the harness.

---

## Stack Confirmation (verified for this architecture)

- **FastMCP 3.x** — GA since Jan 2026 (3.4.2 current, Jun 2026); Python >=3.10 (3.12 fine); `uv add fastmcp`; `@mcp.tool` + `mcp.run()`. [HIGH]
- **Anthropic Python SDK** — official; httpx under the hood (so VCR.py intercepts it); structured extraction via tool-use / `messages.parse()` with Pydantic; temperature 0 for determinism. [HIGH]
- **pytest-recording / VCR.py 8.x** — cassette record/replay; `record_mode="none"` for CI; `filter_headers` to strip auth. [HIGH]
- **dateutil** — `relativedelta` for correct month arithmetic in `dates.py`. [HIGH]
- **Pydantic v2** — shared boundary types. [HIGH]

---

## Sources

- FastMCP 3.0 GA / installation — https://gofastmcp.com/getting-started/installation , https://jlowin.dev/blog/fastmcp-3-launch , https://pypi.org/project/fastmcp/ [HIGH]
- FastMCP tools / server / running — https://gofastmcp.com/servers/tools.md , https://gofastmcp.com/deployment/running-server.md [HIGH]
- VCR.py usage / record modes / filtering — https://vcrpy.readthedocs.io/en/latest/usage.html , https://vcrpy.readthedocs.io/en/latest/advanced.html [HIGH]
- pytest-recording — https://pypi.org/project/pytest-recording/ [HIGH]
- Anthropic structured output / tool-use JSON extraction — https://platform.claude.com/docs/en/build-with-claude/structured-outputs , https://github.com/anthropics/anthropic-cookbook/blob/main/tool_use/extracting_structured_json.ipynb [HIGH]
- Claude model IDs (Haiku/Sonnet) — https://platform.claude.com/docs/en/about-claude/models/overview , https://github.com/anthropics/skills/blob/main/skills/claude-api/shared/models.md [MEDIUM — verify exact IDs at build time per PROJECT.md constraint]
- Project decisions — `.planning/PROJECT.md` (engine, grounding, eval-first, strict-precedence all locked) [HIGH]

---
*Architecture research for: UK commercial-lease break-clause analyzer (MCP, eval-first)*
*Researched: 2026-06-27*
