"""Structured-output schemas the model fills in (Anthropic native Structured Outputs).

These are intentionally the *proposal* surface: raw verbatim quotes and extracted
facts. They are converted to the internal `ConditionProposal` and then verified by
the deterministic core — the model's `status` only survives where it grounds.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from break_clause_analyzer.models import ConditionId, ConditionProposal, Status


class ClauseExtraction(BaseModel):
    """The model's proposed break-clause extraction."""

    found: bool = Field(description="True if the document contains a tenant break clause.")
    clause_quote: str = Field(
        default="",
        description=(
            "The break clause copied VERBATIM, character-for-character, from the "
            "document. Do not paraphrase or correct. Empty string if not found."
        ),
    )


class ConditionFinding(BaseModel):
    """The model's proposed finding for one condition precedent."""

    condition: ConditionId
    status: Status = Field(
        description="pass if clearly satisfied, fail if clearly breached, uncertain if the text does not settle it."
    )
    evidence_quotes: list[str] = Field(
        default_factory=list,
        description="VERBATIM quotes from the document supporting the finding. Copy character-for-character.",
    )
    rationale: str = Field(default="", description="One sentence explaining the finding.")

    # notice_timing only — extract the facts; do NOT compute timing yourself.
    break_date: str | None = Field(default=None, description="The break date, e.g. '24 June 2025'.")
    notice_service_date: str | None = Field(
        default=None, description="The date notice was served, e.g. '5 March 2025'."
    )
    notice_period_months: int | None = Field(
        default=None, description="Required notice period in whole months, e.g. 6."
    )

    # vacant_possession only — the legal test signals (null if unknown).
    vp_people_left: bool | None = Field(default=None, description="Were people left on the premises?")
    vp_chattels_substantial: bool | None = Field(
        default=None, description="Were substantial chattels/goods left behind?"
    )
    vp_occupier_left: bool | None = Field(
        default=None, description="Was a subtenant/licensee/occupier left in occupation?"
    )

    def to_proposal(self) -> ConditionProposal:
        return ConditionProposal(
            condition=self.condition,
            status=self.status,
            evidence_quotes=list(self.evidence_quotes),
            rationale=self.rationale,
            break_date=self.break_date,
            notice_service_date=self.notice_service_date,
            notice_period_months=self.notice_period_months,
            vp_people_left=self.vp_people_left,
            vp_chattels_substantial=self.vp_chattels_substantial,
            vp_occupier_left=self.vp_occupier_left,
        )


class ConditionFindings(BaseModel):
    """The model's findings across all four conditions."""

    findings: list[ConditionFinding] = Field(default_factory=list)
