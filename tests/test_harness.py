"""Prove the measurement apparatus is correct, independently of any LLM.

Strategy: score the gold OracleSystem (must read ~perfect), then deliberately
perturb its output three ways and assert the scorer CATCHES each fault. If a
broken system scored clean, the eval would be worthless — these tests are what
let a reviewer trust the headline number.
"""

from __future__ import annotations

import copy

import pytest

from break_clause_analyzer.core.aggregate import build_assessment
from break_clause_analyzer.models import Span, Status, Verdict
from eval.caseio import load_all_cases
from eval.harness import run_system
from eval.metrics import CaseRun, score_all
from eval.system import OracleSystem


@pytest.fixture(scope="module")
def cases():
    return load_all_cases()


@pytest.fixture(scope="module")
def oracle_runs(cases) -> list[CaseRun]:
    return run_system(OracleSystem(cases), cases)


def _find(runs, predicate) -> CaseRun:
    return next(r for r in runs if predicate(r))


def test_oracle_scores_clean(cases, oracle_runs):
    """A perfect, fully-grounded system must score perfectly on every metric."""
    rep = score_all(oracle_runs, "oracle")

    assert rep.hallucination.rate == 0.0
    assert rep.hallucination.hallucinated == 0
    assert rep.hallucination.total_assertions > 0  # it did make assertions

    assert rep.extraction.found_rate == 1.0
    assert rep.extraction.accuracy == 1.0
    assert rep.extraction.exact_match_rate == 1.0

    assert rep.faithfulness.verbatim_rate == 1.0
    assert rep.faithfulness.support_precision == 1.0
    assert rep.faithfulness.support_recall == 1.0

    assert rep.calibration.overall_accuracy == 1.0
    n_amb = sum(1 for c in cases if c.label == Verdict.AMBIGUOUS)
    assert rep.calibration.coverage == pytest.approx((len(cases) - n_amb) / len(cases))
    assert rep.calibration.abstention_recall == 1.0
    assert rep.calibration.abstention_precision == 1.0


def test_fabricated_citation_is_caught(oracle_runs):
    """An evidence span that isn't really in the source -> verbatim<1 + ungrounded."""
    runs = copy.deepcopy(oracle_runs)
    target = _find(
        runs,
        lambda r: any(c.status in (Status.PASS, Status.FAIL) for c in r.assessment.conditions),
    )
    cond = next(c for c in target.assessment.conditions if c.status in (Status.PASS, Status.FAIL))
    cond.evidence = [Span(quoted_text="THIS PHRASE IS NOWHERE IN THE SOURCE", start=0, end=36)]

    rep = score_all(runs, "fabricator")
    assert rep.faithfulness.verbatim_rate < 1.0
    assert rep.hallucination.by_type.get("ungrounded", 0) >= 1
    assert rep.hallucination.rate > 0.0


def test_misgrounding_is_caught(oracle_runs):
    """Real citation, wrong conclusion: flip a failing condition to pass -> misgrounded."""
    runs = copy.deepcopy(oracle_runs)
    target = _find(
        runs,
        lambda r: r.case.label == Verdict.INVALID
        and any(c.status == Status.FAIL for c in r.assessment.conditions),
    )
    conds = target.assessment.conditions
    cond = next(c for c in conds if c.status == Status.FAIL)
    cond.status = Status.PASS  # keep the (gold) evidence, assert the wrong conclusion
    target.assessment = build_assessment(conds)  # recompute verdict coherently

    rep = score_all(runs, "misgrounder")
    assert rep.hallucination.by_type.get("misgrounded", 0) >= 1
    assert rep.calibration.overall_accuracy < 1.0  # verdict flipped away from gold


def test_over_abstention_is_caught(oracle_runs):
    """Abstaining on a clear case is penalised: coverage drops, abstention precision < 1."""
    runs = copy.deepcopy(oracle_runs)
    target = _find(runs, lambda r: r.case.label == Verdict.VALID)
    conds = target.assessment.conditions
    conds[0].status = Status.UNCERTAIN
    target.assessment = build_assessment(conds)
    assert target.assessment.verdict == Verdict.AMBIGUOUS

    rep = score_all(runs, "over-abstainer")
    assert rep.calibration.coverage < 1.0
    assert rep.calibration.abstention_precision < 1.0  # abstained on a non-ambiguous case


def test_overconfident_on_ambiguous_is_caught(oracle_runs):
    """Confidently resolving a genuinely-ambiguous condition counts as a hallucination."""
    runs = copy.deepcopy(oracle_runs)
    target = _find(
        runs,
        lambda r: r.case.ambiguous
        and any(c.status == Status.UNCERTAIN for c in r.assessment.conditions),
    )
    conds = target.assessment.conditions
    cond = next(c for c in conds if c.status == Status.UNCERTAIN)
    cond.status = Status.PASS  # pretend the ambiguous condition is settled
    target.assessment = build_assessment(conds)

    rep = score_all(runs, "overconfident")
    assert rep.hallucination.by_type.get("overconfident", 0) >= 1
