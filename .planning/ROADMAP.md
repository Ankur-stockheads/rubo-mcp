# Roadmap: UK Break Clause Analyzer (MCP)

## Overview

This roadmap builds a self-evaluating MCP server eval-first: the trust infrastructure exists before the system it judges. Phase 1 lays down the load-bearing reliability apparatus — a labelled synthetic gold dataset, a pytest scoring harness implementing all four metric definitions against a stub oracle, and cassette plumbing for key-free CI replay — proving the measurement works independently of any server logic. Phase 2 builds the deterministic core (grounding gate, date math, checklist, strict-precedence aggregator) as a pure, key-free, exhaustively-tested trust boundary. Phase 3 wires in the riskiest layer — the server-side LLM adapter for extraction and reasoning — with every proposed span flowing through the Phase 2 gate, and records the first real Haiku and Sonnet cassettes. Phase 4 wraps the tested core and adapter in a thin FastMCP surface of four single-purpose tools, passes MCP Inspector, and produces a publish-ready package. Phase 5 runs the full comparative eval live for both models, finalizes cassettes, and ships the primary deliverable surface: the eval report with its headline hallucination rate and a story-led README. Build order is non-negotiable — trustworthy ground truth and a working scorer must precede the logic they score.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Dataset, Scoring Harness & Cassette Infrastructure** - Gold labelled dataset, four-metric pytest harness against a stub oracle, and key-free cassette replay
- [ ] **Phase 2: Deterministic Core** - Key-free grounding gate, date math, checklist, and strict-precedence aggregator, exhaustively tested
- [ ] **Phase 3: LLM Adapter & Extraction** - Server-side Anthropic extraction and reasoning behind the grounding gate, with first Haiku/Sonnet cassettes
- [ ] **Phase 4: MCP Server Surface** - Four single-purpose FastMCP tools, disclaimer field, Inspector pass, and a publish-ready package
- [ ] **Phase 5: Full Eval, Report & README** - Live comparative Haiku-vs-Sonnet eval, finalized cassettes, eval report, and story-led README

## Phase Details

### Phase 1: Dataset, Scoring Harness & Cassette Infrastructure
**Goal**: The reliability measurement apparatus exists and is provably correct before any system-under-test logic — a labelled gold dataset, a harness scoring all four metrics against a stub oracle, and cassette plumbing that replays with no API key.
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, DATA-06, DATA-07, EVAL-01, EVAL-02, EVAL-03, EVAL-04, EVAL-05, EVAL-06
**Success Criteria** (what must be TRUE):
  1. 20–40 synthetic case files exist, each one document with lease provisions plus a Background Facts section, carrying machine-readable front-matter with a VALID/INVALID/AMBIGUOUS label, gold citation spans per condition-relevant assertion, and an ambiguity flag; the set spans every failure mode (missed date, defective notice, outstanding rent, vacant-possession breach), includes 3–5 genuinely ambiguous cases and at least one adversarial prompt-injection case, and was labelled in a separate review pass from authoring.
  2. A documented dev/eval split (or frozen-before-final-cases protocol) exists so published metrics are not train-on-test.
  3. The pytest harness runs the full pipeline over the labelled dataset against a stub/oracle server and emits a report artifact scoring all four metrics: extraction accuracy (field-level + span overlap), citation faithfulness (verbatim presence + support vs gold), hallucination rate (pre-registered ungrounded-OR-misgrounded definition with published denominator), and calibration (coverage, accuracy-on-answered, abstention precision/recall, 3-way confusion matrix).
  4. The hallucination-rate and calibration definitions are pre-registered in writing (README) before any prompt iteration begins.
  5. The eval replays recorded cassettes with no API key in under 2 minutes: `x-api-key` is redacted, `body` is in `match_on`, and CI runs `record_mode=none` so a missing cassette is a hard failure rather than a silent live call.
**Plans**: TBD

### Phase 2: Deterministic Core
**Goal**: The deterministic trust boundary exists as pure, network-free Python — grounding gate, UK date math, four-condition checklist, and strict-precedence aggregator — exhaustively tested with no LLM in the loop.
**Depends on**: Phase 1
**Requirements**: GRND-01, GRND-02, GRND-03, ASMT-02, ASMT-03, ASMT-04, ASMT-05, ASMT-07
**Success Criteria** (what must be TRUE):
  1. The grounding gate verifies a cited span exists verbatim in the source via normalize-then-exact-match with code-derived character offsets, returns the canonical span sliced from the source (never the caller's echo), and a single-character edit injection is rejected.
  2. When a span cannot be grounded the gate returns NOT_FOUND, never substitutes invented or paraphrased text, and a NOT_FOUND can only degrade a verdict toward AMBIGUOUS — never be upgraded downstream.
  3. The checklist evaluates all four conditions precedent (notice timing, notice validity, rent/no-arrears, vacant possession) to pass/fail/uncertain, with absent or NOT_FOUND evidence yielding `uncertain` and never a silent `pass`; the vacant-possession check encodes the people/chattels/legal-interests test rather than mere physical condition.
  4. Notice date math ("not less than N months", break-date expiry) is computed deterministically by code using the corresponding-day rule, with the exact last valid service date, month-end, and leap-year boundaries unit-tested — never computed by an LLM.
  5. The strict-precedence aggregator rolls the checklist into VALID/INVALID/AMBIGUOUS (any fail → INVALID; any uncertain → AMBIGUOUS; all pass → VALID) deterministically and is property-tested over all 81 (3^4) input combinations.
**Plans**: TBD

### Phase 3: LLM Adapter & Extraction
**Goal**: The server-side LLM proposal layer is wired in behind the grounding gate — extraction and per-condition reasoning propose spans that are gate-verified before any result returns — and the first real Haiku and Sonnet cassettes are recorded.
**Depends on**: Phase 2
**Requirements**: ASMT-01, ASMT-06, GRND-04
**Success Criteria** (what must be TRUE):
  1. `extract_break_clause(case)` returns the break clause plus its verbatim source span, where the span is LLM-proposed and then verified by the Phase 2 grounding gate before being returned.
  2. `find_citation(claim)` returns exact verbatim supporting text or NOT_FOUND, routed through the same grounding gate so no paraphrased or invented text can be surfaced.
  3. `assess_validity` orchestrates the full LLM-propose → core-dispose pipeline and returns an explicit calibration field plus mandatory human-verify gates, identifying which conditions forced the label.
  4. The Anthropic adapter is the only network egress, runs at `temperature=0` with an injectable model ID, and first recorded cassette sets exist for both `claude-haiku-4-5` and `claude-sonnet-4-6`, each stamped with model ID + prompt hash for staleness detection and with `x-api-key` confirmed redacted before commit.
**Plans**: TBD

### Phase 4: MCP Server Surface
**Goal**: A thin FastMCP server exposes the four tested tools over stdio with a schema-enforced disclaimer, passes MCP Inspector with no stdout corruption, and builds into a publish-ready, fully self-contained package.
**Depends on**: Phase 3
**Requirements**: MCP-01, MCP-02, MCP-03, MCP-04, PKG-01, PKG-04
**Success Criteria** (what must be TRUE):
  1. A FastMCP server exposes the four single-purpose tools (`extract_break_clause`, `check_conditions`, `find_citation`, `assess_validity`), each with a typed output schema, as thin adapters over the Phase 2 core and Phase 3 adapter.
  2. Every tool response carries a schema-enforced decision-support disclaimer field, asserted by a test rather than living only in README prose.
  3. The server runs via a single command and passes MCP Inspector over stdio; business-logic failures return structured in-result tool errors and nothing is written to stdout (JSON-RPC purity, enforced by a check).
  4. `uv build` produces a publish-ready wheel/sdist for a Python 3.12 + uv package with a `[project.scripts]` console entry (runnable via `uvx`/`pip`, not published to PyPI), and the repo is verified to contain no external or proprietary imports or data anywhere.
**Plans**: TBD
**UI hint**: yes

### Phase 5: Full Eval, Report & README
**Goal**: The headline number is computed on the frozen system — a live comparative Haiku-vs-Sonnet eval with finalized cassettes — and the primary deliverable surface ships: the eval report and the story-led README, clone-to-running in under 2 minutes.
**Depends on**: Phase 4
**Requirements**: EVAL-07, EVAL-08, EVAL-09, PKG-02, PKG-03
**Success Criteria** (what must be TRUE):
  1. The eval runs comparatively across `claude-haiku-4-5` and `claude-sonnet-4-6` from a single model-agnostic harness, with cassettes finalized and scrubbed.
  2. An eval report (markdown + a zero-dependency SVG chart) publishes all four metrics with hallucination rate as the headline (definition + denominator stated inline), a per-model comparison table, a 3-way confusion matrix, a per-condition breakdown, and 2–3 caught-hallucination examples; coverage and accuracy-on-answered are shown so over-abstention is visible.
  3. The report states reproducibility provenance (date of last live re-measurement) and limitations.
  4. A story-led README opens with a real-world missed-condition scenario and includes one architecture diagram and the eval results.
  5. A clean clone-to-running path completes in under 2 minutes, verified from a fresh checkout, and the dev/eval split is documented so the published number is not train-on-test.
**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Dataset, Scoring Harness & Cassette Infrastructure | 0/TBD | Not started | - |
| 2. Deterministic Core | 0/TBD | Not started | - |
| 3. LLM Adapter & Extraction | 0/TBD | Not started | - |
| 4. MCP Server Surface | 0/TBD | Not started | - |
| 5. Full Eval, Report & README | 0/TBD | Not started | - |
