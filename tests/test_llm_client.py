"""Tests for the Anthropic client adapter and the client factory.

The real network call can't run without a key, but its response handling — pulling
the parsed Structured Output off a ParsedMessage — is logic we can and should test
by mocking the SDK boundary.
"""

from __future__ import annotations

import anthropic
import pytest

from break_clause_analyzer.llm import client as clientmod
from break_clause_analyzer.llm.client import (
    AnthropicClient,
    LLMError,
    client_for,
    have_api_key,
)
from break_clause_analyzer.llm.heuristic import HeuristicClient
from break_clause_analyzer.llm.schemas import ClauseExtraction


class _FakeParsed:
    def __init__(self, parsed_output=None, content=None):
        self.parsed_output = parsed_output
        self.content = content or []


class _FakeBlock:
    def __init__(self, parsed_output):
        self.parsed_output = parsed_output


def _install_fake_anthropic(monkeypatch, response):
    class FakeMessages:
        def parse(self, **kwargs):
            return response

    class FakeAnthropic:
        def __init__(self, *a, **k):
            self.messages = FakeMessages()

    monkeypatch.setattr(anthropic, "Anthropic", FakeAnthropic)


def test_client_for_falls_back_to_heuristic_without_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert have_api_key() is False
    assert isinstance(client_for("claude-haiku-4-5"), HeuristicClient)


def test_client_for_uses_anthropic_with_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    _install_fake_anthropic(monkeypatch, _FakeParsed())
    client = client_for("claude-sonnet-4-6")
    assert isinstance(client, AnthropicClient)
    assert client.model == "claude-sonnet-4-6"


def test_anthropic_reads_parsed_output(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    extraction = ClauseExtraction(found=True, clause_quote="the break clause")
    _install_fake_anthropic(monkeypatch, _FakeParsed(parsed_output=extraction))
    out = AnthropicClient("claude-haiku-4-5").extract_clause("doc")
    assert out.found and out.clause_quote == "the break clause"


def test_anthropic_falls_back_to_content_block(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    extraction = ClauseExtraction(found=True, clause_quote="from block")
    response = _FakeParsed(parsed_output=None, content=[_FakeBlock(extraction)])
    _install_fake_anthropic(monkeypatch, response)
    out = AnthropicClient("claude-haiku-4-5").extract_clause("doc")
    assert out.clause_quote == "from block"


def test_anthropic_raises_when_no_structured_output(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    _install_fake_anthropic(monkeypatch, _FakeParsed(parsed_output=None, content=[]))
    with pytest.raises(LLMError):
        AnthropicClient("claude-haiku-4-5").extract_clause("doc")
