"""The shared data contract for the whole system.

Every layer — the deterministic core, the LLM adapter, the MCP server, and the
eval harness — speaks in these types. Defining them once, here, is what lets the
eval harness be built and tested (Phase 1) before any server logic exists.

Decision-support only. NOT legal advice.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

# The disclaimer is a first-class, schema-enforced field on every assessment —
# not just README prose. Required by MCP-03.
DISCLAIMER = (
    "DECISION-SUPPORT ONLY — NOT LEGAL ADVICE. This tool applies a deliberately "
    "simplified, non-proprietary ruleset to synthetic data and can be wrong. A "
    "qualified solicitor must independently verify any real break-clause decision."
)


class ConditionId(str, Enum):
    """The four conditions precedent for a tenant break (the simplified ruleset)."""

    NOTICE_TIMING = "notice_timing"
    NOTICE_VALIDITY = "notice_validity"
    NO_ARREARS = "no_arrears"
    VACANT_POSSESSION = "vacant_possession"


# Stable display/order for reports and human-readable output.
CONDITION_LABELS: dict[ConditionId, str] = {
    ConditionId.NOTICE_TIMING: "Notice timing",
    ConditionId.NOTICE_VALIDITY: "Notice validity",
    ConditionId.NO_ARREARS: "Rent / no arrears",
    ConditionId.VACANT_POSSESSION: "Vacant possession",
}

CONDITION_ORDER: list[ConditionId] = list(ConditionId)


class Status(str, Enum):
    """Per-condition status. UNCERTAIN is a first-class outcome, never a guess."""

    PASS = "pass"
    FAIL = "fail"
    UNCERTAIN = "uncertain"


class Verdict(str, Enum):
    """Overall assessment. AMBIGUOUS means 'human verify', not a coin-flip."""

    VALID = "VALID"
    INVALID = "INVALID"
    AMBIGUOUS = "AMBIGUOUS"


class Span(BaseModel):
    """A span grounded verbatim in the source text.

    Invariant enforced by the grounding gate: ``source[start:end] == quoted_text``.
    A ``Span`` is only ever constructed by slicing the source — never by trusting
    text echoed back by a model.
    """

    quoted_text: str
    start: int
    end: int


class Citation(BaseModel):
    """The result of grounding a claim.

    ``found=False`` is the NOT_FOUND outcome: the system could not locate verbatim
    support and refuses to invent any. There is no path that substitutes model text
    for a real span.
    """

    found: bool
    span: Span | None = None

    @classmethod
    def not_found(cls) -> "Citation":
        return cls(found=False, span=None)

    @classmethod
    def grounded(cls, span: Span) -> "Citation":
        return cls(found=True, span=span)


class ConditionResult(BaseModel):
    """The system's verdict on one condition precedent, with grounded evidence."""

    condition: ConditionId
    status: Status
    rationale: str
    evidence: list[Span] = Field(default_factory=list)


class BreakClause(BaseModel):
    """Output of extract_break_clause: the clause + its grounded span, or not found."""

    found: bool
    clause_text: str | None = None
    span: Span | None = None


class ConditionProposal(BaseModel):
    """What the LLM proposes for one condition, BEFORE the deterministic core checks it.

    The core grounds every `evidence_quote`, recomputes notice timing from the
    extracted dates, and applies the vacant-possession legal test to the flags. The
    model's `status` only survives for the semantic conditions, and only when its
    evidence grounds.
    """

    condition: ConditionId
    status: Status
    evidence_quotes: list[str] = Field(default_factory=list)
    rationale: str = ""

    # notice_timing only — the core recomputes timing from these, deterministically.
    break_date: str | None = None
    notice_service_date: str | None = None
    notice_period_months: int | None = None

    # vacant_possession only — the legal test (people / chattels / occupiers left).
    vp_people_left: bool | None = None
    vp_chattels_substantial: bool | None = None
    vp_occupier_left: bool | None = None


class Assessment(BaseModel):
    """Output of assess_validity: the orchestrated, calibrated assessment."""

    verdict: Verdict
    conditions: list[ConditionResult]
    # Which conditions forced the verdict (the calibration story made explicit).
    decisive_conditions: list[ConditionId] = Field(default_factory=list)
    calibration: str
    # Mandatory human-verify gates surfaced to the caller.
    human_verify: list[str] = Field(default_factory=list)
    disclaimer: str = DISCLAIMER


# --------------------------------------------------------------------------- #
# Gold-dataset types (the trustworthy ground truth the eval scores against).
# --------------------------------------------------------------------------- #


class GoldCondition(BaseModel):
    """Known-correct status for one condition, plus verbatim supporting quotes.

    Every string in ``spans`` MUST be an exact substring of the case ``source``.
    The dataset loader validates this; a mismatch is a hard error, because a gold
    span that isn't verbatim would silently break faithfulness scoring.
    """

    condition: ConditionId
    status: Status
    spans: list[str] = Field(default_factory=list)


class CaseFile(BaseModel):
    """One synthetic, labelled case: lease provisions + Background Facts in one doc."""

    id: str
    label: Verdict
    ambiguous: bool = False
    adversarial: bool = False
    split: str = "eval"  # "dev" or "eval"
    failure_modes: list[str] = Field(default_factory=list)
    gold_clause: str  # verbatim quote of the break clause
    gold_conditions: list[GoldCondition]
    source: str  # the full case text (lease + facts) the system sees
    notes: str | None = None

    def gold_status(self, condition: ConditionId) -> Status:
        for gc in self.gold_conditions:
            if gc.condition == condition:
                return gc.status
        return Status.UNCERTAIN
