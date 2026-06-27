# Requirements: UK Break Clause Analyzer (MCP)

**Defined:** 2026-06-27
**Core Value:** Every asserted condition is grounded to a verbatim source span or returns NOT_FOUND — and the server proves with a published hallucination rate that it would rather say "ambiguous — human verify" than guess.

## v1 Requirements

Requirements for the initial release. Each maps to a roadmap phase.

### Dataset (DATA)

- [ ] **DATA-01**: 20–40 synthetic UK commercial-lease break-clause case files exist, each a single document containing the relevant lease provisions plus a Background Facts section
- [ ] **DATA-02**: Each case carries a known-correct validity label (VALID / INVALID / AMBIGUOUS) in machine-readable front-matter
- [ ] **DATA-03**: Each case carries gold citation spans for every condition-relevant assertion, as ground truth for grounding and faithfulness scoring
- [ ] **DATA-04**: The dataset spans all failure modes — missed date, defective notice, outstanding rent, vacant-possession breach — and includes at least 3–5 genuinely ambiguous cases
- [ ] **DATA-05**: The dataset includes at least one adversarial prompt-injection case (instructions embedded in lease text) that must still be grounded/abstained correctly
- [ ] **DATA-06**: Case authoring and labelling are separated by a label-review pass, so ground truth reflects what the text supports rather than authorial intent
- [ ] **DATA-07**: A dev/eval split (or frozen-before-final-cases protocol) is documented so published metrics are not train-on-test

### Grounding & Citation (GRND)

- [ ] **GRND-01**: A deterministic grounding gate verifies every cited span exists verbatim in the source (normalize-then-exact-match, with code-derived character offsets)
- [ ] **GRND-02**: When a span cannot be grounded, the system returns NOT_FOUND and never substitutes invented or paraphrased text
- [ ] **GRND-03**: A NOT_FOUND can only degrade a verdict toward AMBIGUOUS — it is never upgraded downstream
- [ ] **GRND-04**: `find_citation(claim)` returns exact verbatim supporting text or NOT_FOUND

### Assessment Logic (ASMT)

- [ ] **ASMT-01**: `extract_break_clause(case)` returns the break clause plus its verbatim source span (LLM-proposed, gate-verified)
- [ ] **ASMT-02**: `check_conditions` evaluates the four conditions precedent (notice timing, notice validity, rent/no-arrears, vacant possession) to pass / fail / uncertain
- [ ] **ASMT-03**: Notice date math ("not less than N months", break-date expiry) is computed deterministically using the corresponding-day rule — never by the LLM
- [ ] **ASMT-04**: Absent or NOT_FOUND evidence yields `uncertain`, never a silent `pass`
- [ ] **ASMT-05**: `assess_validity` aggregates the checklist via strict precedence (any fail → INVALID; any uncertain → AMBIGUOUS; all pass → VALID), deterministically
- [ ] **ASMT-06**: `assess_validity` returns an explicit calibration field and mandatory human-verify gates, identifying which conditions forced the label
- [ ] **ASMT-07**: The vacant-possession check encodes the legal test (people / chattels / legal interests left behind — not mere physical condition)

### Eval Harness & Report (EVAL)

- [ ] **EVAL-01**: A pytest scoring harness runs the full pipeline over the labelled dataset
- [ ] **EVAL-02**: The harness measures extraction accuracy (field-level correctness + span overlap)
- [ ] **EVAL-03**: The harness measures citation faithfulness (verbatim presence + support of the claim, scored against gold labels)
- [ ] **EVAL-04**: The harness measures hallucination rate, defined as the ungrounded OR misgrounded assertion rate, with the definition pre-registered and the denominator (assertions / cases) published
- [ ] **EVAL-05**: The harness measures calibration — coverage and accuracy-on-answered, abstention precision/recall, and a 3-way confusion matrix (so over-abstention is visible)
- [ ] **EVAL-06**: The eval replays recorded cassettes so it runs in CI with no API key in under 2 minutes (record live, redact the `x-api-key` header, match on request body, `record_mode=none` in CI)
- [ ] **EVAL-07**: The eval runs comparatively across `claude-haiku-4-5` and `claude-sonnet-4-6` from a single model-agnostic harness
- [ ] **EVAL-08**: An eval report (markdown + a zero-dependency SVG chart) publishes all four metrics with hallucination rate as the headline, a per-model comparison table, a confusion matrix, a per-condition breakdown, and 2–3 caught-hallucination examples
- [ ] **EVAL-09**: The report states reproducibility provenance (date of last live re-measurement) and limitations

### MCP Server Surface (MCP)

- [ ] **MCP-01**: A FastMCP server exposes the four single-purpose tools (`extract_break_clause`, `check_conditions`, `find_citation`, `assess_validity`), each with a typed output schema
- [ ] **MCP-02**: The server runs via a single command and passes MCP Inspector over stdio
- [ ] **MCP-03**: Every tool response carries a schema-enforced decision-support disclaimer field (tested, not just README prose)
- [ ] **MCP-04**: Business-logic failures return structured in-result tool errors, and nothing is written to stdout (stdio JSON-RPC purity)

### Packaging & README (PKG)

- [ ] **PKG-01**: The project is an installable, publish-ready Python 3.12 + uv package with a `[project.scripts]` console entry (runnable via `uvx`/`pip`), not published to PyPI in v1
- [ ] **PKG-02**: A story-led README opens with a real-world missed-condition scenario and includes one architecture diagram and the eval results
- [ ] **PKG-03**: A clean clone-to-running path completes in under 2 minutes, verified from a fresh checkout
- [ ] **PKG-04**: The repo is fully self-contained — no external or proprietary imports or data anywhere

## v2 Requirements

Deferred to a future release. Tracked but not in the current roadmap.

### Eval Enhancements

- **EVAL-10**: Secondary semantic support check (NLI / entailment judge) reported separately from the exact-match gate, for paraphrase-drift sensitivity
- **EVAL-11**: Risk–coverage curve / AURC, enabled by a tunable confidence threshold
- **EVAL-12**: Additional model tiers (e.g. Opus) in the comparative report

### Distribution

- **PKG-05**: Actual publication to PyPI (trusted publishing via CI)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Other lease provisions (rent review, alienation, repair, etc.) | Narrow scope is the point — break clauses only |
| Landlord break clauses | Different machinery; the tenant break is the common, interesting case |
| Real or client lease data | Synthetic/public data only — confidentiality and reproducibility |
| Proprietary legal rules, prompts, or datasets | Clean-room simplified ruleset only |
| Covenant-compliance condition precedent | Deliberately excluded to keep the ruleset simple and eval-focused |
| A production legal engine | This is a decision-support demonstrator, not advice |
| MCP sampling / client-LLM extraction | Server-side API calls so the eval is self-contained |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| DATA-04 | Phase 1 | Pending |
| DATA-05 | Phase 1 | Pending |
| DATA-06 | Phase 1 | Pending |
| DATA-07 | Phase 1 | Pending |
| GRND-01 | Phase 2 | Pending |
| GRND-02 | Phase 2 | Pending |
| GRND-03 | Phase 2 | Pending |
| GRND-04 | Phase 3 | Pending |
| ASMT-01 | Phase 3 | Pending |
| ASMT-02 | Phase 2 | Pending |
| ASMT-03 | Phase 2 | Pending |
| ASMT-04 | Phase 2 | Pending |
| ASMT-05 | Phase 2 | Pending |
| ASMT-06 | Phase 3 | Pending |
| ASMT-07 | Phase 2 | Pending |
| EVAL-01 | Phase 1 | Pending |
| EVAL-02 | Phase 1 | Pending |
| EVAL-03 | Phase 1 | Pending |
| EVAL-04 | Phase 1 | Pending |
| EVAL-05 | Phase 1 | Pending |
| EVAL-06 | Phase 1 | Pending |
| EVAL-07 | Phase 5 | Pending |
| EVAL-08 | Phase 5 | Pending |
| EVAL-09 | Phase 5 | Pending |
| MCP-01 | Phase 4 | Pending |
| MCP-02 | Phase 4 | Pending |
| MCP-03 | Phase 4 | Pending |
| MCP-04 | Phase 4 | Pending |
| PKG-01 | Phase 4 | Pending |
| PKG-02 | Phase 5 | Pending |
| PKG-03 | Phase 5 | Pending |
| PKG-04 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 32 (100%)
- Unmapped: 0

**Per-phase distribution:**
- Phase 1 (Dataset, Scoring Harness & Cassette Infrastructure): 13 — DATA-01..07, EVAL-01..06
- Phase 2 (Deterministic Core): 8 — GRND-01, GRND-02, GRND-03, ASMT-02, ASMT-03, ASMT-04, ASMT-05, ASMT-07
- Phase 3 (LLM Adapter & Extraction): 3 — GRND-04, ASMT-01, ASMT-06
- Phase 4 (MCP Server Surface): 6 — MCP-01, MCP-02, MCP-03, MCP-04, PKG-01, PKG-04
- Phase 5 (Full Eval, Report & README): 5 — EVAL-07, EVAL-08, EVAL-09, PKG-02, PKG-03

---

## Notes on Judgment Calls

- **Citation faithfulness scoring (EVAL-03):** v1 scores claim *support* against gold labels in the dataset (clean, no extra model dependency). An NLI/entailment judge (EVAL-10) is deferred to v2 — it adds a dependency and the gold-label approach is sufficient for a credible headline number.
- **Hallucination definition (EVAL-04):** counts both *ungrounded* assertions (no verbatim span) and *misgrounded* ones (real span, unsupported conclusion), pre-registered before measurement so the number is honest and hard to game.
- **`find_citation` placement (GRND-04 → Phase 3):** the grounding *gate* (GRND-01/02/03) is pure deterministic core (Phase 2), but the `find_citation(claim)` tool surfaces citation retrieval for an LLM-proposed claim, so it lands in Phase 3 alongside extraction/reasoning while reusing the Phase 2 gate.
- **`assess_validity` split (ASMT-05 vs ASMT-06):** the deterministic strict-precedence aggregation (ASMT-05) is Phase 2; the orchestrated `assess_validity` that ties LLM extraction/reasoning to the core and surfaces the calibration field + human-verify gates (ASMT-06) requires the full pipeline and lands in Phase 3.
- **Self-containment (PKG-04 → Phase 4):** treated as a packaging-integrity property gated at `uv build` time in Phase 4, rather than the final README phase.

---
*Requirements defined: 2026-06-27*
*Last updated: 2026-06-27 after roadmap traceability mapping*
