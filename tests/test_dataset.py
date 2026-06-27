"""Guard the dataset's integrity in CI: verbatim spans, coherence, coverage."""

from __future__ import annotations

from break_clause_analyzer.core.aggregate import aggregate_statuses
from break_clause_analyzer.models import Verdict
from eval.caseio import load_all_cases

REQUIRED_MODES = {"notice_timing", "notice_validity", "outstanding_rent", "vacant_possession"}


def test_dataset_loads_and_is_label_coherent():
    cases = load_all_cases()  # loader raises CaseValidationError on any verbatim drift
    assert len(cases) >= 20
    for c in cases:
        assert len(c.gold_conditions) == 4, f"{c.id}: expected 4 conditions"
        implied = aggregate_statuses([gc.status for gc in c.gold_conditions])
        assert implied == c.label, f"{c.id}: label {c.label.value} != implied {implied.value}"
        assert (c.label == Verdict.AMBIGUOUS) == c.ambiguous, f"{c.id}: ambiguous flag mismatch"


def test_dataset_coverage():
    cases = load_all_cases()
    modes = {m for c in cases for m in c.failure_modes}
    assert REQUIRED_MODES <= modes, f"missing failure modes: {REQUIRED_MODES - modes}"
    assert sum(1 for c in cases if c.ambiguous) >= 3
    assert any(c.adversarial for c in cases)
    labels = {c.label for c in cases}
    assert Verdict.VALID in labels and Verdict.INVALID in labels


def test_dataset_has_dev_and_eval_split():
    cases = load_all_cases()
    splits = {c.split for c in cases}
    assert "dev" in splits and "eval" in splits
