# Evaluation Methodology (pre-registered)

This document fixes the metric definitions **before** any model is run or any
prompt is tuned. It is committed first so the headline number cannot be defined
after the fact to look good. The definitions here are implemented verbatim in
[`eval/metrics.py`](../eval/metrics.py) and proven correct against a gold oracle
and deliberately-broken systems in [`tests/test_harness.py`](../tests/test_harness.py).

> **Decision-support only — not legal advice.** Everything below is measured on a
> deliberately simplified, non-proprietary ruleset over synthetic data.

## The system under measurement

For each case the system extracts the break clause, then for each of the four
conditions precedent (notice timing, notice validity, rent/no-arrears, vacant
possession) it proposes a status — `pass` / `fail` / `uncertain` — with verbatim
evidence spans. Every span is checked by a deterministic **grounding gate**: if
the quoted text is not found verbatim in the source it becomes `NOT_FOUND` and
the condition degrades to `uncertain`. The verdict is the strict-precedence roll-up
(any `fail` → INVALID; else any `uncertain` → AMBIGUOUS; else VALID).

## Ground truth

24 synthetic case files, each labelled with a known-correct verdict, per-condition
gold statuses, and **gold evidence spans** (verbatim quotes). Cases were authored
and labelled in separate passes; a validator
([`scripts/validate_dataset.py`](../scripts/validate_dataset.py)) enforces that
every gold span is verbatim and that each label follows from its conditions under
the same strict-precedence rule. A documented **dev/eval split** (see
[`data/cases/README.md`](../data/cases/README.md)) keeps prompt-tuning off the
held-out cases.

## The four metrics

### 1. Extraction accuracy
Did the system pull out the right break clause? Per case we compute the character
**span IoU** between the extracted clause and the gold clause.
- `found_rate` — fraction where a verbatim clause span was returned.
- `exact_match_rate` — fraction matching the gold clause exactly.
- `accuracy` — fraction with IoU ≥ 0.5 (the headline extraction number).

### 2. Citation faithfulness
Two parts, because a citation can be *present* yet not *support* the claim.
- **Presence** — `verbatim_rate`: of all cited spans, the fraction that are
  genuinely verbatim in the source. (The gate should keep this at 1.0; we measure
  it anyway, because it is the falsifiable check on the gate.)
- **Support** — over conditions the system actually asserted (`pass`/`fail`):
  `support_precision` = fraction of cited spans that overlap a gold span for that
  condition; `support_recall` = fraction of gold spans the system cited;
  `support_f1` their harmonic mean.

### 3. Hallucination rate — *the headline*
An **assertion** is either (a) a claimed break-clause extraction, or (b) a
condition the system answered with a definite status (`pass`/`fail`). An
**abstention** (`uncertain` / `NOT_FOUND`) is *never* counted as an assertion and
*never* as a hallucination — abstaining honestly is the correct behaviour.

An assertion is a **hallucination** if it is any of:
- **ungrounded** — asserted with no verbatim evidence supporting it (fabrication);
- **misgrounded** — grounded to real text, but the conclusion contradicts the gold
  status (real citation, wrong conclusion);
- **overconfident** — a definite status asserted on a condition the gold marks
  genuinely `uncertain` (confidently resolving real ambiguity).

```
hallucination_rate = hallucinated_assertions / total_assertions
```

Both the numerator and denominator are published, plus the breakdown by type and a
case-level rate (fraction of cases with ≥1 hallucination).

**Why this definition is honest.** A deterministic grounding gate makes *fabricated*
citations ≈0 by construction. If we stopped there, the rate would be trivially zero
and meaningless. Counting **misgrounding** and **overconfidence** keeps the metric
measuring what actually matters — whether the system reaches wrong or overconfident
conclusions — so the number is hard to game. Abstaining lowers the denominator, but
[over-abstention is penalised by calibration](#4-calibration), so the system cannot
win by refusing to answer.

### 4. Calibration
Treating `AMBIGUOUS` as "abstain / human-verify", measured at the verdict level
against the gold label:
- `coverage` — fraction of cases given a definite (non-AMBIGUOUS) verdict.
- `accuracy_on_answered` — of those, the fraction matching gold.
- `abstention_precision` — when it abstains, the fraction that are genuinely
  ambiguous (catches **over-abstention**).
- `abstention_recall` — of the genuinely-ambiguous cases, the fraction it abstains
  on (catches **overconfidence**).
- `overall_accuracy` — 3-way exact verdict match, with a full confusion matrix.

Hallucination rate and calibration are reported **together**: a low hallucination
rate bought by abstaining on everything shows up immediately as collapsed coverage
and abstention precision.

## Reproducibility

The pipeline calls the Anthropic API; `temperature=0` is *not* a guarantee of
determinism, so reproducibility comes from **recorded cassettes** (pytest-recording
/ VCR.py). CI replays cassettes with `--record-mode=none` and **no API key**, so a
reviewer gets the same numbers in under two minutes. The published figures carry a
"last re-measured live" date; re-recording (`--record-mode=once` with a key)
regenerates them.
