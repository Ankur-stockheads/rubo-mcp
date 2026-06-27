# Project Research Summary

**Project:** uk-break-clause-analyzer-mcp
**Domain:** Self-evaluating MCP server — grounded legal LLM decision-support with published hallucination rate
**Researched:** 2026-06-27
**Confidence:** HIGH

## Executive Summary

This project is a credibility artifact, not a legal tool: the headline deliverable is a reproducible, self-measured hallucination rate over a grounded LLM reasoning pipeline, demonstrated through a UK commercial-lease tenant break-clause assessment server. Experts in this space build reliability by separating LLM extraction from deterministic verification — the LLM proposes; deterministic Python disposes. Every cited span is verified verbatim against the source document or the citation is replaced with `NOT_FOUND`. The overall validity label (`VALID`/`INVALID`/`AMBIGUOUS`) is produced by a strict-precedence deterministic aggregator, never by LLM opinion. This architecture makes the hallucination claim falsifiable: the grounding gate is a chokepoint that cannot be bypassed, so a skeptical technical reviewer can audit exactly what "grounded" means.

The recommended approach is eval-first: build the labeled synthetic dataset and scoring harness before any server logic. This is the project's thesis — trustworthy ground truth must exist before the logic it scores. The harness runs against a stub/oracle server first, proving the measurement apparatus independently of the system under test. Real server logic is Phase 2+. The cassette layer (pytest-recording over VCR.py intercepting the httpx boundary inside the Anthropic SDK) makes the eval reproducible in CI with no API key in under two minutes, which is what makes the published number checkable.

The key credibility risk is an honest-looking but dishonest metric: defining "hallucination" as only fabricated citations, which the grounding gate makes impossible by construction, producing a trivially 0% rate that misses misgrounded reasoning (real citation, wrong conclusion). The second risk is over-abstention — a system that routes everything to human-verify has a perfect hallucination rate and is useless. Both failures must be pre-empted in Phase 1 by pre-registering a multi-category hallucination definition and measuring both coverage and accuracy-on-answered as calibration metrics from day one.

---

## Key Findings

### Recommended Stack

The stack is pinned and verified against live registries as of 2026-06-27. The single most important dependency decision: depend on `fastmcp>=3.4,<4` only — FastMCP already transitively pins `mcp<2.0,>=1.24.0`, so adding a redundant `mcp` pin risks a future resolver conflict. The official `mcp` SDK v2 is targeted for approximately 2026-07-27; the `<4` upper bound on FastMCP protects against intra-3.x breaking changes that have already shipped (e.g. decorator return type flip, async context state). Import from `from fastmcp import FastMCP`, never from `mcp.server.fastmcp` (that is the donated FastMCP 1.0 inside the SDK).

For charting the eval report, use a hand-written SVG with zero dependencies: one simple bar chart of hallucination rate by model is ~40 lines of Python string templating, byte-identical across machines, and inline-renderable in GitHub markdown — on-message for a reproducibility-themed repo. matplotlib is the fallback only if richer plots are needed later.

**Core technologies:**

- `Python 3.12` — runtime; within all dependency support windows; no reason to jump to 3.14
- `uv 0.11.x` (`>=0.11,<0.12`) — single tool for env + lock + build + run; `uv.lock` is the reproducibility mechanism for the CI eval
- `fastmcp>=3.4,<4` (3.4.2 current) — MCP server framework; `from fastmcp import FastMCP` + `@mcp.tool` + `mcp.run()`; transitively pins `mcp<2`
- `anthropic>=0.112,<1` (0.112.0 current) — server-side extraction/reasoning; use `client.messages.parse()` Pydantic helper with native Structured Outputs (GA, no beta header required on both target models)
- `pytest>=9,<10` (9.1.1 current) — eval harness runner; parametrize over labeled dataset
- `pytest-recording>=0.13,<0.14` (0.13.4 current) — VCR.py cassette record/replay over the httpx boundary; `--record-mode=none` in CI guarantees no live call and no key required
- `MCP Inspector npx @modelcontextprotocol/inspector@0.22` (0.22.0 current) — Node tool, NOT a Python dep; manual acceptance gate; run with STDIO transport
- Zero-dep SVG chart — hand-written Python string template; no matplotlib, no NumPy, no CI install time

**Model IDs for the Haiku-vs-Sonnet comparison:**

- `claude-haiku-4-5` — fast/cheap tier ($1/$5 per MTok)
- `claude-sonnet-4-6` — balanced tier ($3/$15 per MTok); same harness, run twice, separate cassette dirs

**Critical cassette configuration (lives in `tests/conftest.py`):**

- Redact `x-api-key` (Anthropic's auth header), not only `authorization` — copying generic VCR examples leaks the real key into a public repo
- Add `body` to `match_on` — all API calls hit the same URL (`/v1/messages`); without body matching, different prompts collide onto one cassette and silently replay the wrong response
- `record_mode="none"` in CI — missing cassette is a hard failure, never a silent live call

### Expected Features

The features divide cleanly into three layers: the credibility infrastructure (eval harness + grounding gate), the server surface (four MCP tools), and the published report. All three are P1 — none can be deferred without destroying the headline claim.

**Must have (table stakes — absence makes the reliability claim unbelievable):**

- Labeled gold dataset, 20-40 synthetic case files spanning all failure modes (missed date, defective notice, outstanding rent, vacant-possession breach, genuinely ambiguous wording) with known labels, gold citation spans per condition, and explicit ambiguity flags — this is the long pole; everything downstream depends on it
- Verbatim grounding gate with character offsets and `NOT_FOUND` as a first-class return — no path from LLM output to tool result bypasses this gate; canonical span is sliced from the source, never echoed from the model
- Four eval metrics with operational definitions pre-registered in the README before measuring: extraction accuracy (field-level + span overlap), citation faithfulness (verbatim presence AND support precision/recall), hallucination rate (ungrounded OR misgrounded assertion rate), calibration (coverage/accuracy-on-answered + abstention precision/recall + 3-way confusion matrix)
- Cassette replay: CI-reproducible, no API key, under 2 minutes — what makes the published number checkable
- Eval report with hallucination rate as headline, all four metrics in a Haiku-vs-Sonnet comparison table, 3-way confusion matrix, 2-3 caught-hallucination examples, cost/latency per model, and a limitations footer
- Four single-purpose MCP tools with output schemas, structured errors, and a `disclaimer` field on every response (schema-enforced and tested, not just in the README): `extract_break_clause`, `check_conditions`, `find_citation`, `assess_validity`
- Strict-precedence aggregator: any `fail` → INVALID; any `uncertain` (including NOT_FOUND-driven) → AMBIGUOUS; all `pass` → VALID — deterministic, total, property-tested over all 81 (3^4) input combinations
- Story-led README opening with a real-world missed-condition scenario, one architecture diagram, eval results, and a clone-to-running path verified to complete in under 2 minutes

**Should have (differentiators that beat both a parser and an average portfolio repo):**

- Haiku-vs-Sonnet comparison as a cost/deployment-decision frame (the FDE register) — same harness, two cassette dirs, nearly zero extra build cost
- Caught-hallucination examples in the report showing the gate rejecting a fabricated/misgrounded span — far more persuasive than an aggregate number alone
- Per-condition breakdown (notice timing, notice validity, no-arrears, vacant possession) showing where errors concentrate — signals diagnostic depth
- Case-file input model (lease provisions + Background Facts in one document, both grounded) — enables facts-grounded assessment of "can it actually be exercised"
- Adversarial-injection case in the dataset asserting the system still grounds/abstains correctly even when lease text contains embedded instructions
- Dev/eval dataset split documentation (or prompt frozen before final cases) so the published number is not a train-on-test fit statistic

**Defer (v2+):**

- Secondary semantic support check (NLI/entailment) reported separately from the exact-match gate — trigger is reviewers asking about paraphrase-drift
- Risk-coverage curve / AURC if a tunable confidence threshold is added later
- Additional model tiers in the comparison (e.g. Opus)
- Actual PyPI publication (already explicitly out of scope; packaged and publish-ready is enough)

### Architecture Approach

The architecture has one governing principle: deterministic code is the trust boundary. `core/` (grounding gate, date math, checklist, aggregator) is pure Python with no network access; `llm/` is the only network egress. `core/` must not import `llm/` — this is enforced structurally, not by convention. The MCP server layer (`server.py`) is a thin adapter: four `@mcp.tool` functions that validate I/O, call `core/` and `llm/`, and return structured Pydantic results. No business logic lives in the tool functions. The eval harness drives `assess_validity` directly and wraps the httpx boundary in `llm/client.py` with VCR.py cassettes; the deterministic core needs no cassettes because it has no network.

**Major components:**

1. `core/grounding.py` — verbatim span verifier (THE trust gate); `source_text.find(quoted_text)` with single-pass normalization; returns `Span(start, end, quoted_text)` sliced from source or `NOT_FOUND`; never returns the model's echo
2. `core/dates.py` — UK date parsing + "not less than N months" notice-period math using `dateutil.relativedelta`; pure functions, exhaustively unit-tested; the LLM never does arithmetic
3. `core/checklist.py` — four condition evaluators (notice timing, notice validity, no-arrears, vacant possession) over grounded inputs → `pass | fail | uncertain` each; absent/NOT_FOUND evidence → `uncertain`, never silently `pass`
4. `core/aggregate.py` — strict-precedence rollup; property-tested over all 81 input combinations; emits calibration field identifying which conditions forced the label
5. `llm/client.py` — only network egress; Anthropic SDK with `temperature=0`, model ID injectable; httpx layer intercepted by VCR.py for cassette record/replay
6. `server.py` — FastMCP 3.x with four `@mcp.tool` functions; thin adapters over `core/` + `llm/`; `main()` calls `mcp.run()` for stdio transport
7. Eval harness (`tests/eval/`) — loads case files, drives `assess_validity`, scores four metrics, records/replays cassettes, emits `report/report.md` + SVG chart; this is the primary deliverable, built first

**Key data flows:**

- LLM proposes quoted span → `grounding.verify()` searches source → returns `Span | NOT_FOUND` → NOT_FOUND propagates to `uncertain` → aggregator → AMBIGUOUS; a NOT_FOUND can never be upgraded downstream
- Model ID threads from harness → `llm/client.py`, enabling Haiku and Sonnet to run against separate cassette sets with the identical pipeline

### Critical Pitfalls

1. **Hallucination-rate definition gaming** — defining the metric as only "fabricated citations", which the grounding gate makes impossible by construction, producing a trivially 0% rate that misses misgrounded reasoning (real citation, wrong conclusion). Prevention: pre-register the four-category definition (fabricated citation, unsupported/non-entailed claim, invented obligation, overconfident ambiguity resolution) in the README before measuring; publish the denominator (N assertions, M hallucinations, K cases); never let the system under test be its own judge for categories 2-3.

2. **Calibration done wrong — the over-abstention failure mode** — a system that routes everything to AMBIGUOUS achieves a perfect hallucination rate and is useless. Prevention: report coverage (fraction of cases answered) AND accuracy-on-answered alongside hallucination rate from Phase 1; the calibration story is the three-cell view (correct abstention / over-abstention / overconfidence), not a single accuracy number.

3. **Fake/loose grounding** — the LLM "cleans up" quotes and a naive match passes anyway, admitting hallucinated citations while appearing grounded. Prevention: normalize source and query identically in a single documented pass; search in normalized space; return canonical span sliced from source, not the model's echo; property-test with a single-character edit injection.

4. **Non-reproducible eval** — `temperature=0` is not deterministic on the Anthropic API (confirmed). Prevention: cassettes are the reproducibility mechanism; CI runs `--record-mode=none`; the published headline number is the cassette-replayed number with a "last re-measured live: date" stamp; cassettes carry a model ID + prompt hash to detect staleness.

5. **Vacant-possession nuance mis-modelled** — VP sounds self-explanatory but the legal test is specific: fails if the tenant leaves people, chattels that substantially interfere with the landlord's use, or legal interests (*Riverside Park* [2016], *South Essex College* [2016]); does NOT fail merely because premises are in poor physical condition (*Capitol Park* [2021, CA]). Prevention: encode the actual test in the checklist; author cases on both sides of the line; cite the authorities in the dataset README.

6. **stdio transport corruption** — any `print()` or logging to stdout corrupts the JSON-RPC channel and kills the MCP Inspector connection. Prevention: all logging goes to stderr or a file; grep for `print()` as a CI/lint check; test with Inspector via STDIO transport early.

7. **Notice date arithmetic off-by-one** — "not less than N months" follows the corresponding-day rule (*Dodds v Walker*); naive `timedelta(days=30*N)` is legally wrong. Prevention: `dateutil.relativedelta(months=N)` with explicit boundary rules; unit-test the exact last valid service date, month-end edge cases, and leap-year cases.

8. **Untrustworthy ground truth** — labels written in the same pass as case text encode authorial intent rather than what the text supports; a too-easy dataset inflates metrics to ~100% and proves nothing. Prevention: separate authoring from labelling passes; every label must cite a verbatim span; engineer the difficulty distribution deliberately; include at least 3-5 genuine AMBIGUOUS cases.

---

## Implications for Roadmap

Based on combined research, the build order is non-negotiable: the labeled dataset and scoring harness come first. This is the project's thesis, not a preference. Building against a stub/oracle server proves the measurement apparatus independently of the system under test; without it, a passing eval is indistinguishable from a broken scorer.

### Phase 1: Synthetic Dataset + Scoring Harness + Cassette Infrastructure

**Rationale:** Everything downstream depends on the gold dataset. The harness must exist before the logic it scores, and metric definitions must be pre-registered before any prompt iteration begins. Cassette plumbing and secret hygiene belong here because they are part of the measurement infrastructure.

**Delivers:**
- 20-40 labeled synthetic case files (Markdown with `## Lease` and `## Background Facts`, YAML front-matter carrying label + gold spans + ambiguity flag)
- `core/models.py` Pydantic types as the data contract
- Scoring harness implementing all four metric definitions against a stub/oracle server
- Cassette plumbing: `vcr_config` fixture with `x-api-key` redaction, `body` in `match_on`, `record_mode="none"` for CI
- Report generator skeleton
- Metric definitions pre-registered in README

**Addresses:** labeled dataset (P1), all four eval metrics (P1), cassette replay (P1), hallucination-rate definition (pre-registered here), calibration metrics

**Avoids:** Pitfalls 2 (untrustworthy ground truth), 3 (non-reproducible eval), 4 (metric gaming), 8 (secrets + cassette hygiene)

**Domain requirements for case authoring:** VP cases on both sides of the chattels line; mid-quarter rent apportionment trap (*PCE Investors*); notice-timing traps at the exact deadline boundary and one day late (*Dodds v Walker*); notice-validity (wrong party/address) INVALID; at least 3-5 cases that should genuinely route to AMBIGUOUS; an adversarial-injection case

**Research flag:** Standard patterns — no additional research phase needed; apply PITFALLS.md domain guidance directly.

---

### Phase 2: Deterministic Core

**Rationale:** The data contract is fixed (Phase 1 types) and the scoring harness exists. Building the deterministic core next means it can be tested exhaustively with no LLM in the loop — fast, key-free, auditable. The trust boundary is established structurally before any LLM code exists.

**Delivers:**
- `core/grounding.py` — normalized exact-match gate with offset derivation and `NOT_FOUND` propagation; property-tested with single-character edit injection
- `core/dates.py` — UK date parsing + `relativedelta` month arithmetic with corresponding-day rule, month-end exceptions, and boundary unit tests
- `core/checklist.py` — four condition evaluators; absent/NOT_FOUND evidence → `uncertain`
- `core/aggregate.py` — strict-precedence rollup; property-tested over all 81 (3^4) combinations
- `tests/unit/` — key-free, fast unit tests; CI gate independent of the eval

**Avoids:** Pitfalls 1 (fake/loose grounding), 10 (date arithmetic), 9 (VP nuance), 11 (rent apportionment)

**Research flag:** Well-documented patterns; UK legal rules fully specified in PITFALLS.md. No additional research phase needed.

---

### Phase 3: LLM Adapter + Extraction

**Rationale:** The trust boundary is in place (Phase 2 core). Wire in the LLM as a proposal layer. Candidate spans and reasoning flow through the grounding gate before any result is returned. First real cassettes are recorded here.

**Delivers:**
- `llm/client.py` — Anthropic SDK wrapper with `temperature=0` and injectable model ID
- `llm/extract.py` — extraction prompt + `messages.parse()` Pydantic schema using native Structured Outputs
- `llm/reason.py` — per-condition reasoning prompt returning quoted evidence spans
- First recorded cassette sets for Haiku and Sonnet (`tests/eval/cassettes/haiku/`, `tests/eval/cassettes/sonnet/`)
- Cassette staleness detection: model ID + prompt hash stored alongside cassettes

**Avoids:** Pitfalls 3 (nondeterminism → cassettes), 8 (secrets — redact `x-api-key` before first commit, grep cassette YAML), prompt injection (spotlighting delimiter, constrained schema as injection backstop)

**Research flag:** Standard patterns for Anthropic SDK + VCR.py. One spot-check at phase start: confirm `messages.parse()` Pydantic helper form against current `anthropic` 0.112.0 docs (MEDIUM confidence on `output_config.format` vs `output_format` migration details).

---

### Phase 4: MCP Server Surface

**Rationale:** Core and LLM adapter are independently tested. The MCP surface is a thin wiring layer — four `@mcp.tool` functions that call `core/` and `llm/`. Building it last means tools are testable without a running server (FastMCP 3.x tools are plain callables).

**Delivers:**
- `server.py` with four `@mcp.tool` functions; `main()` calls `mcp.run()` for stdio transport
- `[project.scripts]` console entry
- `disclaimer` field schema-enforced on every tool response; test asserting its presence
- Import smoke test: imports server module and asserts all four tools are registered
- MCP Inspector pass (STDIO transport, no stdout writes)
- `uv build` producing the publish-ready wheel/sdist

**Avoids:** Pitfalls 6 (FastMCP API drift — pin exact version, verify symbols, smoke test), 7 (stdio corruption), 13 (legal-advice overreach — disclaimer schema-enforced and tested)

**Research flag:** FastMCP 3.x surface fully documented. One targeted check at phase start: verify exact `@mcp.tool` decorator signature and `mcp.run()` invocation against gofastmcp.com — do not rely on training-data recall.

---

### Phase 5: Full Eval, Report, and README

**Rationale:** All components exist. Run the full eval pipeline live for both models, record final cassettes, compute the four metrics, and produce the primary surface area.

**Delivers:**
- Live eval run for both models; cassettes finalized and scrubbed
- `report/report.md` with hallucination rate as headline (definition + denominator stated inline), per-metric Haiku-vs-Sonnet table, 3-way confusion matrix, per-condition breakdown, 2-3 caught-hallucination examples, cost/latency comparison, reproducibility footer with stated limitations
- Zero-dep SVG bar chart of hallucination rate by model
- Story-led README: real-world missed-condition opening, architecture diagram, eval results, clone-to-running path verified from a clean checkout in under 2 minutes
- Dev/eval split documented

**Avoids:** Pitfalls 3 (train-on-test — dev/eval hygiene documented here), 4 (metric definition verified against real model output), 5 (over-abstention — coverage/accuracy-on-answered in the report), 13 (legal-advice framing)

**Research flag:** Standard patterns. No additional research phase needed.

---

### Phase Ordering Rationale

- Phase 1 before all others: gold dataset and metric definitions are the precondition for everything; harness against a stub proves the measurement apparatus independently
- Phase 2 before Phase 3: trust boundary must be structural before LLM code exists; exhaustive unit testing of deterministic core is only possible after Phase 1 fixes the data contract
- Phase 3 before Phase 4: LLM adapter is the riskiest component (nondeterminism, secrets, prompt injection); must be separately wired and cassette-recorded before the MCP surface wraps it
- Phase 4 before Phase 5: server must pass MCP Inspector before the final eval run and README claim "runs via a single command"
- Phase 5 last: headline number computed on the frozen system; dev/eval split hygiene verifiable by commit history

### Research Flags

Phases with well-documented patterns (no additional research phase needed):
- **Phase 1** — dataset format, pytest parametrization, VCR.py `vcr_config`, UK legal domain traps: fully specified in STACK.md and PITFALLS.md
- **Phase 2** — `dateutil.relativedelta` and Pydantic v2 are standard; legal boundary rules specified in PITFALLS.md Pitfalls 9-12
- **Phase 3** — Anthropic SDK + VCR.py integration fully documented in STACK.md; one spot-check at phase start (see below)
- **Phase 4** — FastMCP 3.x skeleton fully specified; verify symbols at phase start, do not rely on training-data recall
- **Phase 5** — report generation and README structure are standard

Targeted verification steps at phase start (not full research phases):
- **Phase 3:** Confirm `messages.parse()` Pydantic helper form against `anthropic` 0.112.0 changelog — `messages.parse()` is the safe path that sidesteps the raw param migration ambiguity
- **Phase 4:** Verify exact FastMCP 3.x `@mcp.tool` decorator and `mcp.run()` signatures against gofastmcp.com before writing any tool code

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All version pins read directly from PyPI / npm registry JSON on 2026-06-27; transitive `mcp<2` constraint verified in `fastmcp-slim` metadata; one MEDIUM caveat on exact `output_config.format` vs `output_format` migration nuance in `anthropic` 0.112.0 |
| Features | HIGH | Four metric definitions anchored to ALCE, Stanford Legal-RAG-Hallucinations, SelectLLM (NeurIPS 2025), and TACL 2025 abstention survey; MCP tool design conventions from MCP 2025-06-18 spec and FastMCP 3.x docs; MEDIUM on exact legal-tech UX norms (narrower literature) |
| Architecture | HIGH | All engine decisions locked in PROJECT.md; stack/tooling verified against current FastMCP 3.x, Anthropic SDK, and VCR.py docs; architectural patterns (propose-then-verify, core/llm isolation, cassette boundary) are the load-bearing project decisions |
| Pitfalls | HIGH | FastMCP 3.4.1 changelog verified; MCP Inspector official docs; Anthropic SDK httpx confirmed; UK case law (Riverside Park, South Essex College, Capitol Park, PCE Investors, Dodds v Walker) reported and concrete; MEDIUM on eval methodology judgment calls |

**Overall confidence:** HIGH

### Gaps to Address

- **`messages.parse()` exact parameter form in `anthropic` 0.112.0** — both `output_config.format` and the legacy `output_format` param work during a transition window; `messages.parse()` with a Pydantic model is the safe path and sidesteps the raw param. Verify against current SDK docs at Phase 3 start.
- **FastMCP 3.x intra-line breaking-change exhaustive list** — sourced from changelog/launch blog posts, not read against current `main`. Structurally mitigated by pin `>=3.4,<4` plus committed `uv.lock`; verify every symbol against gofastmcp.com at Phase 4 start.
- **MCP Inspector 0.22.x exact flag surface** — `6274` default port and `npx ... <command>` form are well-established; minor UI/flag changes possible. Verify against `--help` at Phase 4 start.
- **Dataset legal correctness for trap cases** — synthetic labels for VP, apportionment, and notice-validity trap cases should be cross-checked against cited authorities during Phase 1 authoring; a second-pass label review (fresh-context model with no access to intended labels) is recommended for AMBIGUOUS cases.

---

## Sources

### Primary (HIGH confidence)

- PyPI JSON API (2026-06-27) — exact current versions + `requires_dist` for fastmcp 3.4.2 (`mcp<2.0,>=1.24.0`), anthropic 0.112.0, pytest 9.1.1, pytest-recording 0.13.4, vcrpy 8.2.1, uv 0.11.25
- npm registry `@modelcontextprotocol/inspector/latest` (2026-06-27) — Inspector 0.22.0
- gofastmcp.com — FastMCP 3.x import surface, `fastmcp-slim` split, `@mcp.tool`, `mcp.run()`
- platform.claude.com/docs — Anthropic SDK `messages.create`/`messages.parse`, Structured Outputs GA, model IDs and pricing
- modelcontextprotocol.io/specification/2025-06-18/server/tools — `isError`, `outputSchema`, `structuredContent`, tool annotations
- vcrpy.readthedocs.io + kiwicom/pytest-recording — `filter_headers`, `match_on`, `record_mode`, `x-api-key` redaction
- Magesh et al. 2024, arXiv:2405.20362 — correctness + groundedness hallucination framework; 17-33% real rates behind "hallucination-free" marketing
- Gao et al. 2023, ALCE (EMNLP) — citation recall/precision, NLI entailment formulation
- Wen et al. 2025, TACL — abstention precision/recall, appropriate vs over-abstention
- SelectLLM, NeurIPS 2025 — coverage, selective risk, AURC
- Riverside Park Ltd v NHS Property Services [2016] — VP/chattels test
- Secretary of State for Communities & Local Government v South Essex College [2016] — VP/chattels/key fobs
- Capitol Park Leeds v Global Radio [2021, CA] — VP is people/chattels/legal interests, not physical state
- PCE Investors Ltd v Cancer Research UK [2012] — mid-quarter break, full quarter's rent, no apportionment
- Dodds v Walker — corresponding-day rule for notice periods
- .planning/PROJECT.md — all engine decisions and locked constraints

### Secondary (MEDIUM confidence)

- Attribution/Citation/Quotation survey (arXiv 2508.15396) — citation recall/precision, AIS, quotation faithfulness
- CiteGuard (arXiv 2510.17853) — semantic vs exact-span contrast; LLM-judge recall limits (~16-17%)
- jlowin.dev/blog/fastmcp-3 + FastMCP changelog — FastMCP 3.0 GA, decorator mode flip, intra-line breaking changes
- github.com/modelcontextprotocol/python-sdk README — official `mcp` SDK v1.x; v2 beta ~2026-06-30
- anthropic-sdk-python issue #893 — temperature=0 not fully deterministic (confirmed)
- Microsoft MSRC spotlighting / arXiv 2403.14720 — prompt injection delimiting/datamarking defence

---
*Research completed: 2026-06-27*
*Ready for roadmap: yes*
