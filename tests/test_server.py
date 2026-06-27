"""MCP server surface: registration, schema-enforced disclaimer, stdout purity."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

import break_clause_analyzer as pkg
from break_clause_analyzer import server
from break_clause_analyzer.models import DISCLAIMER, Verdict
from eval.caseio import load_all_cases

EXPECTED_TOOLS = {"extract_break_clause", "check_conditions", "find_citation", "assess_validity"}


@pytest.fixture(autouse=True)
def _no_key(monkeypatch):
    # Force the heuristic backend so these tests need no API key.
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    server._client_cache = None
    yield
    server._client_cache = None


@pytest.fixture(scope="module")
def cases_by_id():
    return {c.id: c for c in load_all_cases()}


def _tools():
    return asyncio.run(server.mcp.list_tools())


def test_four_single_purpose_tools_registered():
    assert {t.name for t in _tools()} == EXPECTED_TOOLS


def test_every_tool_output_schema_carries_disclaimer():
    for t in _tools():
        schema = t.output_schema or {}
        assert "disclaimer" in schema.get("properties", {}), f"{t.name} lacks a disclaimer field"


def test_every_tool_is_read_only_and_closed_world():
    for t in _tools():
        ann = t.annotations
        assert ann is not None
        assert ann.readOnlyHint is True
        assert ann.openWorldHint is False


def test_assess_validity_on_real_case_is_invalid(cases_by_id):
    result = server.assess_validity_tool(cases_by_id["case-001"].source)
    assert result.verdict is Verdict.INVALID
    assert result.disclaimer == DISCLAIMER


def test_tools_return_disclaimer(cases_by_id):
    src = cases_by_id["case-002"].source
    assert server.extract_break_clause_tool(src).disclaimer == DISCLAIMER
    assert server.check_conditions_tool(src).disclaimer == DISCLAIMER
    assert server.find_citation_tool(src, "the Premises").disclaimer == DISCLAIMER


def test_empty_inputs_are_structured_not_crashes():
    assert server.extract_break_clause_tool("").clause.found is False
    assert server.check_conditions_tool("").conditions == []
    assert server.find_citation_tool("", "").citation.found is False
    empty = server.assess_validity_tool("")
    assert empty.verdict is Verdict.AMBIGUOUS
    assert empty.human_verify  # surfaces a 'no document' gate


def test_mcp_client_roundtrip_end_to_end(cases_by_id):
    """Connect as a real MCP client (in-memory transport), list tools, and call one.
    This is the headless equivalent of 'passes MCP Inspector'."""

    async def go():
        from fastmcp import Client

        async with Client(server.mcp) as client:
            tools = await client.list_tools()
            res = await client.call_tool(
                "assess_validity", {"case_text": cases_by_id["case-001"].source}
            )
            return {t.name for t in tools}, res

    names, res = asyncio.run(go())
    assert names == EXPECTED_TOOLS
    assert res.structured_content is not None
    assert "INVALID" in str(res.data.verdict)
    assert getattr(res.data, "disclaimer", "")


def test_no_stdout_writes_anywhere_in_package():
    """stdio JSON-RPC purity: every print() in the package must target stderr."""
    root = Path(pkg.__file__).resolve().parent
    for py in root.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        assert "sys.stdout" not in text, f"{py.name} references sys.stdout"
        i = 0
        while (i := text.find("print(", i)) != -1:
            assert "file=sys.stderr" in text[i : i + 300], f"{py.name}: a print() may hit stdout"
            i += 6
