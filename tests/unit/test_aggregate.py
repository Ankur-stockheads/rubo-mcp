"""Strict-precedence aggregation, property-tested over all 81 combinations."""

from __future__ import annotations

from itertools import product

from break_clause_analyzer.core.aggregate import (
    aggregate,
    aggregate_statuses,
    build_assessment,
)
from break_clause_analyzer.models import (
    CONDITION_ORDER,
    DISCLAIMER,
    ConditionId,
    ConditionResult,
    Status,
    Verdict,
)


def _expected(statuses) -> Verdict:
    if Status.FAIL in statuses:
        return Verdict.INVALID
    if Status.UNCERTAIN in statuses:
        return Verdict.AMBIGUOUS
    return Verdict.VALID


def _conds(statuses) -> list[ConditionResult]:
    return [
        ConditionResult(condition=c, status=s, rationale="x", evidence=[])
        for c, s in zip(CONDITION_ORDER, statuses)
    ]


def test_aggregate_statuses_over_all_81_combinations():
    combos = list(product(list(Status), repeat=4))
    assert len(combos) == 81  # total function over the whole input space
    for combo in combos:
        assert aggregate_statuses(list(combo)) == _expected(combo), combo


def test_fail_dominates_uncertain():
    assert aggregate_statuses([Status.FAIL, Status.UNCERTAIN, Status.PASS, Status.PASS]) is Verdict.INVALID


def test_aggregate_decisive_conditions():
    inv, dec = aggregate(_conds([Status.PASS, Status.FAIL, Status.UNCERTAIN, Status.PASS]))
    assert inv is Verdict.INVALID
    assert dec == [ConditionId.NOTICE_VALIDITY]  # only the failing one is decisive

    amb, dec = aggregate(_conds([Status.PASS, Status.PASS, Status.UNCERTAIN, Status.PASS]))
    assert amb is Verdict.AMBIGUOUS
    assert dec == [ConditionId.NO_ARREARS]

    val, dec = aggregate(_conds([Status.PASS] * 4))
    assert val is Verdict.VALID
    assert len(dec) == 4  # every condition had to pass


def test_build_assessment_invalid():
    a = build_assessment(_conds([Status.PASS, Status.FAIL, Status.PASS, Status.PASS]))
    assert a.verdict is Verdict.INVALID
    assert ConditionId.NOTICE_VALIDITY in a.decisive_conditions
    assert a.calibration.startswith("INVALID")
    assert a.disclaimer == DISCLAIMER


def test_build_assessment_ambiguous_has_human_verify():
    a = build_assessment(_conds([Status.PASS, Status.PASS, Status.UNCERTAIN, Status.PASS]))
    assert a.verdict is Verdict.AMBIGUOUS
    assert a.human_verify  # must surface a human-verify gate
    assert any("verify" in h.lower() or "AMBIGUOUS" in h for h in a.human_verify)


def test_build_assessment_valid_is_clean():
    a = build_assessment(_conds([Status.PASS] * 4))
    assert a.verdict is Verdict.VALID
    assert a.human_verify == []
    assert a.calibration.startswith("VALID")
    assert a.disclaimer == DISCLAIMER
