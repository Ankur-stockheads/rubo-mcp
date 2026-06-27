"""The MCP server surface: four single-purpose tools over the tested pipeline.

Thin by design — every tool validates input, calls into `core`/`llm`, and returns
a typed Pydantic result whose schema carries a mandatory `disclaimer` field. No
business logic lives here.

Transport is stdio (JSON-RPC), so NOTHING may be written to stdout; all diagnostics
go to stderr. The console entry point is `break-clause-analyzer` (see pyproject).

Decision-support only. NOT legal advice.
"""

from __future__ import annotations

import sys

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from break_clause_analyzer.llm.client import LLMClient, client_for
from break_clause_analyzer.models import (
    DISCLAIMER,
    Assessment,
    BreakClause,
    Citation,
    ConditionResult,
    Verdict,
)
from break_clause_analyzer.pipeline import (
    assess_validity,
    check_conditions,
    extract_break_clause,
    find_citation,
)

# Model is configurable; defaults to the cheap/fast tier. Falls back to the
# heuristic baseline when ANTHROPIC_API_KEY is absent (logged to stderr).
import os

_MODEL = os.environ.get("BREAK_CLAUSE_MODEL", "claude-haiku-4-5")
_client_cache: LLMClient | None = None


def _client() -> LLMClient:
    global _client_cache
    if _client_cache is None:
        _client_cache = client_for(_MODEL)
    return _client_cache


# --------------------------------------------------------------------------- #
# Tool response models — each one carries the disclaimer in its schema (MCP-03).
# --------------------------------------------------------------------------- #


class ExtractResult(BaseModel):
    clause: BreakClause
    disclaimer: str = Field(default=DISCLAIMER)


class ConditionsResult(BaseModel):
    conditions: list[ConditionResult]
    disclaimer: str = Field(default=DISCLAIMER)


class CitationResult(BaseModel):
    citation: Citation
    disclaimer: str = Field(default=DISCLAIMER)


# Assessment already carries a `disclaimer` field, so assess_validity returns it directly.

mcp = FastMCP(
    name="uk-break-clause-analyzer",
    instructions=(
        "Assess whether a UK commercial-lease TENANT break clause can be exercised, "
        "grounding every claim to verbatim source text. Decision-support only — not "
        "legal advice. Tools are single-purpose; compose them: extract_break_clause to "
        "find the clause, check_conditions for the four-condition checklist, "
        "find_citation to verify any quote, assess_validity for the orchestrated verdict "
        "with calibration and human-verify gates."
    ),
)

_ANNOTATIONS = {"readOnlyHint": True, "openWorldHint": False}


@mcp.tool(
    name="extract_break_clause",
    annotations=_ANNOTATIONS,
    description="Extract the tenant break clause from a lease document, returning its "
    "verbatim text and source span (or found=false). Decision-support only.",
)
def extract_break_clause_tool(lease_text: str) -> ExtractResult:
    if not lease_text or not lease_text.strip():
        return ExtractResult(clause=BreakClause(found=False))
    return ExtractResult(clause=extract_break_clause(lease_text, _client()))


@mcp.tool(
    name="check_conditions",
    annotations=_ANNOTATIONS,
    description="Evaluate the four conditions precedent (notice timing, notice validity, "
    "rent/no-arrears, vacant possession) against the document, each pass/fail/uncertain "
    "with grounded evidence. Decision-support only.",
)
def check_conditions_tool(case_text: str) -> ConditionsResult:
    if not case_text or not case_text.strip():
        return ConditionsResult(conditions=[])
    return ConditionsResult(conditions=check_conditions(case_text, _client()))


@mcp.tool(
    name="find_citation",
    annotations=_ANNOTATIONS,
    description="Return the exact verbatim text in the source that supports a claim, or "
    "NOT_FOUND. Never invents text. Deterministic. Decision-support only.",
)
def find_citation_tool(source_text: str, claim: str) -> CitationResult:
    return CitationResult(citation=find_citation(source_text or "", claim or ""))


@mcp.tool(
    name="assess_validity",
    annotations=_ANNOTATIONS,
    description="Orchestrated assessment: VALID / INVALID / AMBIGUOUS with per-condition "
    "results, the conditions that forced the verdict, a calibration note, and mandatory "
    "human-verify gates. Abstains to AMBIGUOUS rather than guess. Decision-support only.",
)
def assess_validity_tool(case_text: str) -> Assessment:
    if not case_text or not case_text.strip():
        return Assessment(
            verdict=Verdict.AMBIGUOUS,
            conditions=[],
            decisive_conditions=[],
            calibration="No document was provided — cannot assess.",
            human_verify=["No document provided; supply the lease text and Background Facts."],
        )
    return assess_validity(case_text, _client())


def main() -> None:
    """Console entry point — runs the server over stdio."""
    print("[break-clause-analyzer] starting MCP server (stdio)…", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()
