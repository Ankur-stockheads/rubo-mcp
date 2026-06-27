"""Orchestration: the four operations the MCP tools expose.

This is the propose -> gate -> dispose pipeline made concrete:
  extract_break_clause  — model proposes a clause quote; the gate grounds it.
  check_conditions      — model proposes findings; the core grounds + evaluates them.
  assess_validity       — check_conditions, then deterministic aggregation + calibration.
  find_citation         — pure grounding gate over a claim.

Nothing here trusts model text that hasn't passed the grounding gate.
"""

from __future__ import annotations

from break_clause_analyzer.core.aggregate import build_assessment
from break_clause_analyzer.core.checklist import evaluate_checklist
from break_clause_analyzer.core.grounding import ground, ground_span
from break_clause_analyzer.llm.client import LLMClient
from break_clause_analyzer.models import (
    Assessment,
    BreakClause,
    Citation,
    ConditionResult,
)


def extract_break_clause(source: str, client: LLMClient) -> BreakClause:
    """ASMT-01: the model proposes a clause quote; the gate grounds it verbatim.

    If the proposed quote cannot be grounded, we return found=False rather than
    surface ungrounded model text.
    """
    extraction = client.extract_clause(source)
    if not extraction.found or not extraction.clause_quote.strip():
        return BreakClause(found=False)
    span = ground_span(source, extraction.clause_quote)
    if span is None:
        return BreakClause(found=False)
    return BreakClause(found=True, clause_text=span.quoted_text, span=span)


def check_conditions(source: str, client: LLMClient) -> list[ConditionResult]:
    """ASMT-02: model proposes per-condition findings; the core grounds + evaluates."""
    findings = client.reason_conditions(source)
    proposals = [f.to_proposal() for f in findings.findings]
    return evaluate_checklist(source, proposals)


def assess_validity(source: str, client: LLMClient) -> Assessment:
    """ASMT-05/06: orchestrated assessment with calibration + human-verify gates."""
    conditions = check_conditions(source, client)
    return build_assessment(conditions)


def find_citation(source: str, claim: str) -> Citation:
    """GRND-04: exact verbatim supporting text, or NOT_FOUND. Pure gate, no model."""
    return ground(source, claim)
