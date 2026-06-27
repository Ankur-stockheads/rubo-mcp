"""Pytest + cassette configuration.

The Anthropic SDK talks HTTP over httpx, so VCR.py (via pytest-recording)
intercepts it transparently. Two project-specific safety rules live here:

  * filter_headers redacts BOTH `authorization` AND `x-api-key`. Anthropic
    authenticates with `x-api-key`; copying a generic VCR example that only
    scrubs `authorization` would leak a real key into this public repo.
  * `body` is in match_on. Every request hits the same URL (/v1/messages), so
    without body matching two different prompts would collide on one cassette
    and silently replay the wrong response.

Record mode is controlled by the CLI (`--record-mode`, default `none`): in CI a
missing cassette is a hard failure, never a silent live call. To (re)record:
`uv run pytest --record-mode=once` with ANTHROPIC_API_KEY set.
"""

from __future__ import annotations

import pytest


@pytest.fixture
def vcr_config() -> dict:
    return {
        "filter_headers": ["authorization", "x-api-key"],
        "match_on": ["method", "scheme", "host", "port", "path", "query", "body"],
        "decode_compressed_response": True,
    }
