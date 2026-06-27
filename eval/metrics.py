"""The four eval metrics, with pre-registered operational definitions.

See docs/METHODOLOGY.md for the prose definitions these implement. The headline
is the hallucination rate, defined to count BOTH fabrication and misgrounding so
it cannot be trivially driven to zero by a grounding gate.

All metrics are computed against the gold dataset; none uses an LLM judge, so the
scorer itself is deterministic and auditable.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from break_clause_analyzer.models import (
    Assessment,
    BreakClause,
    CaseFile,
    ConditionId,
    Span,
    Status,
    Verdict,
)


@dataclass
class CaseRun:
    """One case put through a system: the gold case + the system's outputs."""

    case: CaseFile
    clause: BreakClause
    assessment: Assessment


# --------------------------------------------------------------------------- #
# Low-level grounding helpers (offset arithmetic, no model calls).
# --------------------------------------------------------------------------- #


def is_verbatim(span: Span | None, source: str) -> bool:
    """True iff the span genuinely slices its quoted_text out of the source."""
    if span is None:
        return False
    if not (0 <= span.start <= span.end <= len(source)):
        return False
    return source[span.start : span.end] == span.quoted_text and span.quoted_text in source


def _offsets(source: str, quote: str) -> tuple[int, int] | None:
    idx = source.find(quote)
    return (idx, idx + len(quote)) if idx >= 0 else None


def _overlaps(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def _iou(a: tuple[int, int], b: tuple[int, int]) -> float:
    inter = max(0, min(a[1], b[1]) - max(a[0], b[0]))
    union = (a[1] - a[0]) + (b[1] - b[0]) - inter
    return inter / union if union > 0 else 0.0


def _answered(status: Status) -> bool:
    return status in (Status.PASS, Status.FAIL)


# --------------------------------------------------------------------------- #
# 1. Extraction accuracy
# --------------------------------------------------------------------------- #


@dataclass
class ExtractionMetrics:
    n: int
    found_rate: float
    exact_match_rate: float
    mean_iou: float
    accuracy: float  # fraction of cases with IoU >= 0.5 against gold clause


def score_extraction(runs: list[CaseRun]) -> ExtractionMetrics:
    n = len(runs)
    found = exact = good = 0
    iou_sum = 0.0
    for r in runs:
        src = r.case.source
        gold = _offsets(src, r.case.gold_clause)
        span = r.clause.span
        if not (r.clause.found and is_verbatim(span, src)) or gold is None:
            continue
        found += 1
        sys_off = (span.start, span.end)
        iou = _iou(sys_off, gold)
        iou_sum += iou
        if span.quoted_text == r.case.gold_clause:
            exact += 1
        if iou >= 0.5:
            good += 1
    return ExtractionMetrics(
        n=n,
        found_rate=found / n if n else 0.0,
        exact_match_rate=exact / n if n else 0.0,
        mean_iou=iou_sum / n if n else 0.0,
        accuracy=good / n if n else 0.0,
    )


# --------------------------------------------------------------------------- #
# 2. Citation faithfulness
# --------------------------------------------------------------------------- #


@dataclass
class FaithfulnessMetrics:
    cited_spans: int
    verbatim_rate: float  # presence: fraction of cited spans actually in source
    support_precision: float  # of asserted-condition evidence, fraction hitting gold
    support_recall: float  # of gold evidence for asserted conditions, fraction cited
    support_f1: float


def score_faithfulness(runs: list[CaseRun]) -> FaithfulnessMetrics:
    cited = 0
    verbatim = 0
    prec_hit = prec_total = 0
    rec_hit = rec_total = 0

    for r in runs:
        src = r.case.source
        # Presence over every cited span (clause + all condition evidence).
        all_spans: list[Span] = []
        if r.clause.span is not None:
            all_spans.append(r.clause.span)
        for c in r.assessment.conditions:
            all_spans.extend(c.evidence)
        for s in all_spans:
            cited += 1
            if is_verbatim(s, src):
                verbatim += 1

        # Support only over conditions the system actually asserted (pass/fail).
        gold_by_cond: dict[ConditionId, list[tuple[int, int]]] = {}
        for gc in r.case.gold_conditions:
            offs = [o for q in gc.spans if (o := _offsets(src, q)) is not None]
            gold_by_cond[gc.condition] = offs

        for c in r.assessment.conditions:
            if not _answered(c.status):
                continue
            gold_offs = gold_by_cond.get(c.condition, [])
            sys_offs = [(s.start, s.end) for s in c.evidence if is_verbatim(s, src)]
            # precision: system evidence that overlaps any gold span
            for so in sys_offs:
                prec_total += 1
                if any(_overlaps(so, go) for go in gold_offs):
                    prec_hit += 1
            # recall: gold spans overlapped by any system evidence
            for go in gold_offs:
                rec_total += 1
                if any(_overlaps(so, go) for so in sys_offs):
                    rec_hit += 1

    precision = prec_hit / prec_total if prec_total else 0.0
    recall = rec_hit / rec_total if rec_total else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return FaithfulnessMetrics(
        cited_spans=cited,
        verbatim_rate=verbatim / cited if cited else 1.0,
        support_precision=precision,
        support_recall=recall,
        support_f1=f1,
    )


# --------------------------------------------------------------------------- #
# 3. Hallucination rate  (THE headline)
# --------------------------------------------------------------------------- #


@dataclass
class HallucinationRecord:
    case_id: str
    kind: str  # "clause" | "condition"
    condition: str | None
    asserted: str
    gold: str
    htype: str | None  # None | "ungrounded" | "misgrounded" | "overconfident"

    @property
    def is_hallucination(self) -> bool:
        return self.htype is not None


@dataclass
class HallucinationMetrics:
    total_assertions: int
    hallucinated: int
    rate: float
    by_type: dict[str, int]
    case_level_rate: float
    records: list[HallucinationRecord] = field(default_factory=list)

    @property
    def grounded_assertions(self) -> int:
        return self.total_assertions - self.hallucinated


def score_hallucination(runs: list[CaseRun]) -> HallucinationMetrics:
    records: list[HallucinationRecord] = []
    cases_with_hallucination: set[str] = set()

    for r in runs:
        src = r.case.source
        cid = r.case.id

        # (a) Clause extraction is an assertion when the system claims to have found one.
        if r.clause.found:
            gold = _offsets(src, r.case.gold_clause)
            span = r.clause.span
            htype: str | None = None
            if not is_verbatim(span, src):
                htype = "ungrounded"  # claimed a clause but the span is not real text
            elif gold is not None and _iou((span.start, span.end), gold) == 0.0:
                htype = "misgrounded"  # grounded, but to the wrong text
            records.append(
                HallucinationRecord(cid, "clause", None, "found", "found", htype)
            )
            if htype:
                cases_with_hallucination.add(cid)

        # (b) Each definite (pass/fail) condition is an assertion.
        for c in r.assessment.conditions:
            if not _answered(c.status):
                continue  # abstention is never a hallucination
            gold_status = r.case.gold_status(c.condition)
            verbatim_evidence = [s for s in c.evidence if is_verbatim(s, src)]
            htype = None
            if not verbatim_evidence:
                htype = "ungrounded"  # asserted a status with no real supporting text
            elif gold_status is Status.UNCERTAIN:
                htype = "overconfident"  # resolved a genuinely ambiguous condition
            elif _answered(gold_status) and c.status != gold_status:
                htype = "misgrounded"  # real citation, wrong conclusion
            records.append(
                HallucinationRecord(
                    cid, "condition", c.condition.value, c.status.value, gold_status.value, htype
                )
            )
            if htype:
                cases_with_hallucination.add(cid)

    total = len(records)
    halluc = [r for r in records if r.is_hallucination]
    by_type = Counter(r.htype for r in halluc)
    return HallucinationMetrics(
        total_assertions=total,
        hallucinated=len(halluc),
        rate=len(halluc) / total if total else 0.0,
        by_type=dict(by_type),
        case_level_rate=len(cases_with_hallucination) / len(runs) if runs else 0.0,
        records=records,
    )


# --------------------------------------------------------------------------- #
# 4. Calibration
# --------------------------------------------------------------------------- #

_VERDICTS = [Verdict.VALID, Verdict.INVALID, Verdict.AMBIGUOUS]


@dataclass
class CalibrationMetrics:
    n: int
    coverage: float  # fraction of cases given a definite (non-AMBIGUOUS) verdict
    accuracy_on_answered: float  # of answered, fraction matching gold
    abstention_precision: float  # when it abstains, fraction that are truly ambiguous
    abstention_recall: float  # of truly-ambiguous cases, fraction it abstains on
    overall_accuracy: float  # 3-way exact match
    confusion: dict[str, dict[str, int]]  # gold -> system -> count


def score_calibration(runs: list[CaseRun]) -> CalibrationMetrics:
    n = len(runs)
    confusion = {g.value: {s.value: 0 for s in _VERDICTS} for g in _VERDICTS}
    answered = answered_correct = 0
    overall_correct = 0
    sys_abstain = gold_ambig = true_abstain = 0

    for r in runs:
        gold = r.case.label
        sysv = r.assessment.verdict
        confusion[gold.value][sysv.value] += 1
        if sysv == gold:
            overall_correct += 1
        if sysv is Verdict.AMBIGUOUS:
            sys_abstain += 1
        else:
            answered += 1
            if sysv == gold:
                answered_correct += 1
        if gold is Verdict.AMBIGUOUS:
            gold_ambig += 1
        if sysv is Verdict.AMBIGUOUS and gold is Verdict.AMBIGUOUS:
            true_abstain += 1

    return CalibrationMetrics(
        n=n,
        coverage=answered / n if n else 0.0,
        accuracy_on_answered=answered_correct / answered if answered else 0.0,
        abstention_precision=true_abstain / sys_abstain if sys_abstain else 1.0,
        abstention_recall=true_abstain / gold_ambig if gold_ambig else 1.0,
        overall_accuracy=overall_correct / n if n else 0.0,
        confusion=confusion,
    )


# --------------------------------------------------------------------------- #
# Top-level report
# --------------------------------------------------------------------------- #


@dataclass
class MetricsReport:
    model_label: str
    n_cases: int
    extraction: ExtractionMetrics
    faithfulness: FaithfulnessMetrics
    hallucination: HallucinationMetrics
    calibration: CalibrationMetrics


def score_all(runs: list[CaseRun], model_label: str) -> MetricsReport:
    return MetricsReport(
        model_label=model_label,
        n_cases=len(runs),
        extraction=score_extraction(runs),
        faithfulness=score_faithfulness(runs),
        hallucination=score_hallucination(runs),
        calibration=score_calibration(runs),
    )
