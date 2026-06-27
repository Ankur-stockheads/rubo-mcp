"""Evaluate the four conditions precedent from grounded, gate-checked evidence.

The governing rule throughout: **absent or ungroundable evidence yields
`uncertain`, never a silent `pass`.** That is what makes the system abstain
rather than guess.

- notice_timing: recomputed deterministically from the extracted dates (the model
  never decides timing).
- vacant_possession: the legal test is encoded over structured flags — people,
  substantial chattels, or occupiers/legal interests left behind defeat it
  (cf. NYK Logistics v Ibrend; Capitol Park Leeds v Global Radio). It is NOT about
  the physical condition of the premises.
- notice_validity, no_arrears: semantic — the model's judgment stands only when its
  evidence grounds verbatim.
"""

from __future__ import annotations

from break_clause_analyzer.core.dates import (
    DateParseError,
    format_date,
    latest_service_date,
    notice_served_in_time,
    parse_uk_date,
)
from break_clause_analyzer.core.grounding import ground_span
from break_clause_analyzer.models import (
    CONDITION_ORDER,
    ConditionId,
    ConditionProposal,
    ConditionResult,
    Span,
    Status,
)


def _ground_all(source: str, quotes: list[str]) -> list[Span]:
    return [s for q in quotes if (s := ground_span(source, q)) is not None]


def _uncertain(cid: ConditionId, why: str, evidence: list[Span] | None = None) -> ConditionResult:
    return ConditionResult(
        condition=cid, status=Status.UNCERTAIN, rationale=why, evidence=evidence or []
    )


def evaluate_condition(source: str, proposal: ConditionProposal) -> ConditionResult:
    grounded = _ground_all(source, proposal.evidence_quotes)
    if proposal.condition is ConditionId.NOTICE_TIMING:
        return _evaluate_timing(proposal, grounded)
    if proposal.condition is ConditionId.VACANT_POSSESSION:
        return _evaluate_vacant_possession(proposal, grounded)
    return _evaluate_semantic(proposal, grounded)


def evaluate_checklist(
    source: str, proposals: list[ConditionProposal]
) -> list[ConditionResult]:
    """Evaluate all four conditions in canonical order. Any condition not proposed
    is treated as uncertain (we never assume a missing condition passed)."""
    by_cond = {p.condition: p for p in proposals}
    results: list[ConditionResult] = []
    for cid in CONDITION_ORDER:
        proposal = by_cond.get(cid)
        if proposal is None:
            results.append(_uncertain(cid, "No evidence was extracted for this condition."))
        else:
            results.append(evaluate_condition(source, proposal))
    return results


def _evaluate_semantic(proposal: ConditionProposal, grounded: list[Span]) -> ConditionResult:
    cid = proposal.condition
    if not grounded:
        return _uncertain(cid, "No verbatim evidence could be grounded — cannot determine.")
    status = proposal.status if proposal.status in (Status.PASS, Status.FAIL) else Status.UNCERTAIN
    rationale = proposal.rationale or "Assessed from grounded evidence."
    return ConditionResult(condition=cid, status=status, rationale=rationale, evidence=grounded)


def _evaluate_timing(proposal: ConditionProposal, grounded: list[Span]) -> ConditionResult:
    cid = ConditionId.NOTICE_TIMING
    if not grounded:
        return _uncertain(cid, "Notice/break dates not grounded in the text — cannot determine timing.")
    if not (proposal.break_date and proposal.notice_service_date and proposal.notice_period_months):
        return _uncertain(
            cid, "Notice period or a relevant date is missing — cannot determine timing.", grounded
        )
    try:
        break_d = parse_uk_date(proposal.break_date)
        service_d = parse_uk_date(proposal.notice_service_date)
        months = int(proposal.notice_period_months)
        if months <= 0:
            raise ValueError("non-positive notice period")
    except (DateParseError, ValueError, TypeError):
        return _uncertain(cid, "Dates/period could not be parsed — cannot determine timing.", grounded)

    deadline = latest_service_date(break_d, months)
    in_time = notice_served_in_time(break_d, months, service_d)
    rationale = (
        f"{months} months' notice before {format_date(break_d)} required service by "
        f"{format_date(deadline)}; notice was served on {format_date(service_d)} "
        f"({'in time' if in_time else 'too late'})."
    )
    return ConditionResult(
        condition=cid,
        status=Status.PASS if in_time else Status.FAIL,
        rationale=rationale,
        evidence=grounded,
    )


def _evaluate_vacant_possession(
    proposal: ConditionProposal, grounded: list[Span]
) -> ConditionResult:
    cid = ConditionId.VACANT_POSSESSION
    if not grounded:
        return _uncertain(cid, "No grounded evidence on possession — cannot determine.")

    flags = {
        "people remained": proposal.vp_people_left,
        "substantial chattels remained": proposal.vp_chattels_substantial,
        "an occupier or legal interest remained": proposal.vp_occupier_left,
    }
    # The legal test is decidable only if every signal is known.
    if any(v is None for v in flags.values()):
        return _evaluate_semantic(proposal, grounded)

    defeats = [reason for reason, present in flags.items() if present]
    if defeats:
        return ConditionResult(
            condition=cid,
            status=Status.FAIL,
            rationale="Vacant possession not given: " + "; ".join(defeats) + ".",
            evidence=grounded,
        )
    return ConditionResult(
        condition=cid,
        status=Status.PASS,
        rationale="Vacant possession given: no people, substantial chattels, or occupiers remained.",
        evidence=grounded,
    )
