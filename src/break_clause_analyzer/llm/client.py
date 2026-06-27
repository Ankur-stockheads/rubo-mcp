"""The LLM client — the system's only network egress.

`AnthropicClient` makes the real server-side calls at temperature=0 with an
injectable model id, using native Structured Outputs (`messages.parse`). It runs
over httpx, so VCR.py cassettes replay it deterministically with no key.

`client_for()` returns the real client when ANTHROPIC_API_KEY is set, and
otherwise falls back to the heuristic baseline so the server and eval still run
(clearly labelled, never silently). All logging goes to stderr — writing to
stdout would corrupt the MCP stdio JSON-RPC channel.
"""

from __future__ import annotations

import os
import sys
from typing import Protocol, runtime_checkable

from break_clause_analyzer.llm.prompts import (
    EXTRACT_SYSTEM,
    REASON_SYSTEM,
    extract_user,
    reason_user,
)
from break_clause_analyzer.llm.schemas import ClauseExtraction, ConditionFindings

DEFAULT_MAX_TOKENS = 1500


class LLMError(RuntimeError):
    """Raised when the model call fails or returns no usable structured output."""


@runtime_checkable
class LLMClient(Protocol):
    model: str

    def extract_clause(self, source: str) -> ClauseExtraction: ...

    def reason_conditions(self, source: str) -> ConditionFindings: ...


class AnthropicClient:
    """Real server-side Anthropic client (temperature=0, structured outputs)."""

    def __init__(self, model: str, max_tokens: int = DEFAULT_MAX_TOKENS):
        from anthropic import Anthropic  # imported lazily so no-key paths don't need it

        self._client = Anthropic()
        self.model = model
        self._max_tokens = max_tokens

    def _structured(self, system: str, user: str, schema: type):
        try:
            parsed = self._client.messages.parse(
                model=self.model,
                max_tokens=self._max_tokens,
                temperature=0,
                system=system,
                messages=[{"role": "user", "content": user}],
                output_format=schema,
            )
        except Exception as exc:  # network/SDK errors -> our error type
            raise LLMError(f"Anthropic request failed: {exc}") from exc

        out = getattr(parsed, "parsed_output", None)
        if out is None:
            for block in getattr(parsed, "content", []) or []:
                block_out = getattr(block, "parsed_output", None)
                if block_out is not None:
                    out = block_out
                    break
        if out is None:
            raise LLMError("model returned no parsed structured output")
        return out

    def extract_clause(self, source: str) -> ClauseExtraction:
        return self._structured(EXTRACT_SYSTEM, extract_user(source), ClauseExtraction)

    def reason_conditions(self, source: str) -> ConditionFindings:
        return self._structured(REASON_SYSTEM, reason_user(source), ConditionFindings)


def have_api_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


def client_for(model: str, *, allow_heuristic_fallback: bool = True) -> LLMClient:
    """Real client if a key is present; heuristic baseline otherwise (labelled)."""
    if have_api_key():
        return AnthropicClient(model)
    if allow_heuristic_fallback:
        from break_clause_analyzer.llm.heuristic import HeuristicClient

        print(
            f"[break-clause-analyzer] ANTHROPIC_API_KEY not set — using the heuristic "
            f"baseline instead of '{model}'. Set the key for real LLM extraction.",
            file=sys.stderr,
        )
        return HeuristicClient()
    raise LLMError("ANTHROPIC_API_KEY is not set and heuristic fallback is disabled")
