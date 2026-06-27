"""The `System` interface and the gold `OracleSystem`.

Everything the harness scores is a `System`: something that, given the raw case
text, extracts the break clause and produces an Assessment. The real LLM-backed
system (Phase 3) implements exactly this interface. In Phase 1 we score the
`OracleSystem` — a perfect reference built from the gold labels — to prove the
scorer reports ~100% on a known-correct system (and, in the tests, that it
*catches* injected errors).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from break_clause_analyzer.core.aggregate import build_assessment
from break_clause_analyzer.llm.client import LLMClient
from break_clause_analyzer.models import (
    Assessment,
    BreakClause,
    CaseFile,
    ConditionResult,
    Span,
)
from break_clause_analyzer.pipeline import assess_validity, extract_break_clause


def span_of(source: str, quote: str) -> Span | None:
    """Ground a verbatim quote against the source by slicing it out (or None)."""
    idx = source.find(quote)
    if idx < 0:
        return None
    return Span(quoted_text=quote, start=idx, end=idx + len(quote))


@runtime_checkable
class System(Protocol):
    name: str

    def extract(self, source: str) -> BreakClause: ...

    def assess(self, source: str) -> Assessment: ...


class OracleSystem:
    """A perfect reference system: returns fully-grounded, gold-correct output."""

    name = "oracle"

    def __init__(self, cases: list[CaseFile]):
        self._by_source = {c.source: c for c in cases}

    def _case(self, source: str) -> CaseFile:
        try:
            return self._by_source[source]
        except KeyError as exc:  # pragma: no cover - guards against harness misuse
            raise KeyError("OracleSystem given a source it has no gold for") from exc

    def extract(self, source: str) -> BreakClause:
        case = self._case(source)
        return BreakClause(
            found=True,
            clause_text=case.gold_clause,
            span=span_of(source, case.gold_clause),
        )

    def assess(self, source: str) -> Assessment:
        case = self._case(source)
        conditions: list[ConditionResult] = []
        for gc in case.gold_conditions:
            evidence = [s for q in gc.spans if (s := span_of(source, q)) is not None]
            conditions.append(
                ConditionResult(
                    condition=gc.condition,
                    status=gc.status,
                    rationale="gold reference",
                    evidence=evidence,
                )
            )
        return build_assessment(conditions)


class LlmSystem:
    """The real system under test: the propose->gate->dispose pipeline behind an
    LLM client. Works with the Anthropic client (key/cassettes) or the heuristic
    baseline. This is what the eval actually measures."""

    def __init__(self, client: LLMClient):
        self._client = client
        self.name = client.model

    def extract(self, source: str) -> BreakClause:
        return extract_break_clause(source, self._client)

    def assess(self, source: str) -> Assessment:
        return assess_validity(source, self._client)
