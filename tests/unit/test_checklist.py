"""Condition checklist: deterministic timing, grounded-or-uncertain, VP legal test."""

from __future__ import annotations

from break_clause_analyzer.core.checklist import evaluate_checklist, evaluate_condition
from break_clause_analyzer.models import ConditionId, ConditionProposal, Status

SRC = (
    "The Tenant may break on 24 June 2025 by giving not less than six months' notice. "
    "The Tenant served notice on 5 March 2025. All rent was paid up to the Break Date. "
    "The Tenant left the premises empty and returned the keys."
)


def test_timing_is_recomputed_and_overrides_model_claim():
    # The model wrongly claims PASS; the core recomputes FAIL from the dates.
    p = ConditionProposal(
        condition=ConditionId.NOTICE_TIMING,
        status=Status.PASS,
        evidence_quotes=["The Tenant served notice on 5 March 2025"],
        break_date="24 June 2025",
        notice_service_date="5 March 2025",
        notice_period_months=6,
    )
    res = evaluate_condition(SRC, p)
    assert res.status is Status.FAIL
    assert res.evidence  # grounded evidence retained


def test_timing_uncertain_when_dates_missing():
    p = ConditionProposal(
        condition=ConditionId.NOTICE_TIMING,
        status=Status.PASS,
        evidence_quotes=["The Tenant served notice on 5 March 2025"],
        notice_period_months=6,  # break_date / service_date missing
    )
    assert evaluate_condition(SRC, p).status is Status.UNCERTAIN


def test_timing_uncertain_when_evidence_ungrounded():
    p = ConditionProposal(
        condition=ConditionId.NOTICE_TIMING,
        status=Status.PASS,
        evidence_quotes=["served notice on 1 January 2020"],  # not in source
        break_date="24 June 2025",
        notice_service_date="1 January 2020",
        notice_period_months=6,
    )
    assert evaluate_condition(SRC, p).status is Status.UNCERTAIN


def test_semantic_status_stands_only_when_grounded():
    grounded = ConditionProposal(
        condition=ConditionId.NO_ARREARS,
        status=Status.PASS,
        evidence_quotes=["All rent was paid up to the Break Date"],
    )
    assert evaluate_condition(SRC, grounded).status is Status.PASS


def test_semantic_ungrounded_is_uncertain_never_silent_pass():
    ungrounded = ConditionProposal(
        condition=ConditionId.NO_ARREARS,
        status=Status.PASS,  # model says pass...
        evidence_quotes=["the tenant had paid everything on time"],  # ...but not in source
    )
    assert evaluate_condition(SRC, ungrounded).status is Status.UNCERTAIN


def test_vacant_possession_legal_test_fails_on_chattels():
    p = ConditionProposal(
        condition=ConditionId.VACANT_POSSESSION,
        status=Status.PASS,  # model claims pass; the encoded test overrides
        evidence_quotes=["left the premises empty and returned the keys"],
        vp_people_left=False,
        vp_chattels_substantial=True,  # substantial chattels remained
        vp_occupier_left=False,
    )
    res = evaluate_condition(SRC, p)
    assert res.status is Status.FAIL
    assert "chattels" in res.rationale


def test_vacant_possession_legal_test_passes_when_all_clear():
    p = ConditionProposal(
        condition=ConditionId.VACANT_POSSESSION,
        status=Status.PASS,
        evidence_quotes=["left the premises empty and returned the keys"],
        vp_people_left=False,
        vp_chattels_substantial=False,
        vp_occupier_left=False,
    )
    assert evaluate_condition(SRC, p).status is Status.PASS


def test_vacant_possession_uncertain_when_ungrounded():
    p = ConditionProposal(
        condition=ConditionId.VACANT_POSSESSION,
        status=Status.PASS,
        evidence_quotes=["the premises were handed back spotless"],  # not in source
        vp_people_left=False,
        vp_chattels_substantial=False,
        vp_occupier_left=False,
    )
    assert evaluate_condition(SRC, p).status is Status.UNCERTAIN


def test_evaluate_checklist_fills_missing_conditions_as_uncertain():
    only_timing = [
        ConditionProposal(
            condition=ConditionId.NOTICE_TIMING,
            status=Status.PASS,
            evidence_quotes=["The Tenant served notice on 5 March 2025"],
            break_date="24 June 2025",
            notice_service_date="5 March 2025",
            notice_period_months=6,
        )
    ]
    results = evaluate_checklist(SRC, only_timing)
    assert [r.condition for r in results] == list(ConditionId)  # canonical order, all four
    missing = [r for r in results if r.condition is not ConditionId.NOTICE_TIMING]
    assert all(r.status is Status.UNCERTAIN for r in missing)
