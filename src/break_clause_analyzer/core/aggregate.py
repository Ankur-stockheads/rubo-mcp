"""Strict-precedence aggregation: roll a condition checklist into one verdict.

The rule, deliberately conservative so the system abstains under doubt:

    any condition FAIL      -> INVALID   (a clear breach defeats the break)
    else any UNCERTAIN      -> AMBIGUOUS  (cannot tell -> human verify)
    else (all PASS)         -> VALID

This is a total function over all 3^4 = 81 status combinations and is the single
source of truth for the verdict — used by the live system, the gold oracle, and
the dataset validator alike.
"""

from __future__ import annotations

from break_clause_analyzer.models import (
    CONDITION_LABELS,
    Assessment,
    ConditionId,
    ConditionResult,
    Status,
    Verdict,
)


def aggregate_statuses(statuses: list[Status]) -> Verdict:
    """Strict-precedence verdict from a bare list of statuses."""
    if Status.FAIL in statuses:
        return Verdict.INVALID
    if Status.UNCERTAIN in statuses:
        return Verdict.AMBIGUOUS
    return Verdict.VALID


def aggregate(conditions: list[ConditionResult]) -> tuple[Verdict, list[ConditionId]]:
    """Verdict plus the conditions that forced it (the calibration story).

    For INVALID, the decisive conditions are the failing ones; for AMBIGUOUS, the
    uncertain ones; for VALID, all conditions (each one had to pass).
    """
    fails = [c.condition for c in conditions if c.status == Status.FAIL]
    uncertains = [c.condition for c in conditions if c.status == Status.UNCERTAIN]
    if fails:
        return Verdict.INVALID, fails
    if uncertains:
        return Verdict.AMBIGUOUS, uncertains
    return Verdict.VALID, [c.condition for c in conditions]


def _labels(conditions: list[ConditionId]) -> str:
    return ", ".join(CONDITION_LABELS[c] for c in conditions)


def build_assessment(conditions: list[ConditionResult]) -> Assessment:
    """Deterministically build the full Assessment from a condition checklist.

    This is the 'dispose' half of propose-then-dispose: given per-condition
    statuses + grounded evidence (proposed upstream, gate-verified), it computes
    the verdict, the calibration note, and the mandatory human-verify gates. It
    contains no model calls and no I/O.
    """
    verdict, decisive = aggregate(conditions)

    if verdict is Verdict.INVALID:
        calibration = (
            f"INVALID — the break fails on: {_labels(decisive)}. "
            "A single failed condition precedent defeats the break."
        )
    elif verdict is Verdict.AMBIGUOUS:
        calibration = (
            f"AMBIGUOUS — cannot be determined from the text: {_labels(decisive)}. "
            "The system abstains rather than guess; a human must verify."
        )
    else:
        calibration = "VALID — all four conditions precedent are clearly satisfied on the text."

    human_verify: list[str] = []
    if verdict is Verdict.AMBIGUOUS:
        human_verify.append(
            "Overall assessment is AMBIGUOUS — a qualified person must review before relying on it."
        )
    for c in conditions:
        if c.status is Status.UNCERTAIN:
            human_verify.append(
                f"{CONDITION_LABELS[c.condition]}: could not be determined from the text — verify manually."
            )

    return Assessment(
        verdict=verdict,
        conditions=conditions,
        decisive_conditions=decisive,
        calibration=calibration,
        human_verify=human_verify,
    )
