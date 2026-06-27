# Evaluation Report — UK Break Clause Analyzer

> DECISION-SUPPORT ONLY — NOT LEGAL ADVICE. This tool applies a deliberately simplified, non-proprietary ruleset to synthetic data and can be wrong. A qualified solicitor must independently verify any real break-clause decision.

**Run mode:** heuristic baseline (no ANTHROPIC_API_KEY, no cassettes)  
**Cases (eval split):** 17  
**Provenance:** deterministic heuristic — no API calls. Run `scripts/run_eval.py --record` with a key to measure claude-haiku-4-5 and claude-sonnet-4-6.

## Headline — measured hallucination rate

**heuristic-baseline: 13.8%**.

A hallucination is any *asserted* condition or clause that is **ungrounded** (no verbatim support), **misgrounded** (real citation, wrong conclusion), or **overconfident** (a definite answer on a genuinely-ambiguous condition). Honest abstentions (`uncertain` / NOT_FOUND) are never counted. Denominator = total assertions made. See [`docs/METHODOLOGY.md`](../docs/METHODOLOGY.md) for the pre-registered definitions.

![Hallucination rate](hallucination_rate.svg)

## All four metrics

| Metric | heuristic-baseline |
|---|---|
| Hallucination rate ⬇ | **13.8%** |
|   — ungrounded / misgrounded / overconfident | 0 / 9 / 2 |
|   — case-level | 64.7% |
| Extraction accuracy ⬆ | 100.0% |
| Citation verbatim-rate ⬆ | 100.0% |
| Citation support F1 ⬆ | 82.9% |
| Overall verdict accuracy ⬆ | 35.3% |
| Coverage (answered) ⬆ | 94.1% |
| Accuracy on answered ⬆ | 37.5% |
| Abstention precision ⬆ | 0.0% |
| Abstention recall ⬆ | 0.0% |

## Verdict confusion matrix

**heuristic-baseline**

| gold ↓ \ system → | VALID | INVALID | AMBIGUOUS |
|---|---|---|---|
| VALID | 0 | 5 | 0 |
| INVALID | 2 | 6 | 1 |
| AMBIGUOUS | 1 | 2 | 0 |

## Where errors concentrate

**heuristic-baseline** — hallucinations by condition:
- Notice timing: 1
- Notice validity: 2
- Rent / no arrears: 4
- Vacant possession: 4

## Caught-hallucination examples

**heuristic-baseline**

- **case-002 · Vacant possession** — system asserted `fail`, gold is `pass` → caught as **misgrounded**.
- **case-004 · Vacant possession** — system asserted `fail`, gold is `uncertain` → caught as **overconfident**.
- **case-006 · Rent / no arrears** — system asserted `fail`, gold is `pass` → caught as **misgrounded**.

## Limitations & reproducibility

- Synthetic, non-proprietary dataset on a deliberately simplified four-condition ruleset — not a measure of real-world legal accuracy.
- Metrics are computed against gold labels (no LLM judge), so the scorer is deterministic and auditable; it was validated against a gold oracle and deliberately-broken systems (`tests/test_harness.py`).
- Reproducibility comes from recorded cassettes, not from `temperature=0` (which the API does not guarantee). Re-run `scripts/run_eval.py` to regenerate.
