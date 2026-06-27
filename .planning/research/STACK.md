# Stack Research

**Domain:** Self-evaluating MCP server (UK commercial-lease break-clause analyzer) — eval/reliability harness is the headline; parsing is commodity
**Researched:** 2026-06-27
**Confidence:** HIGH (all version pins verified against PyPI / npm registry / official docs on 2026-06-27; caveats flagged inline)

## TL;DR — Pin These

```
Python      3.12
uv          0.11.x        (>=0.11.25 ; ">=0.11,<0.12" in tooling notes)
fastmcp     >=3.4,<4      (3.4.2 current; pulls mcp<2 transitively — DO NOT also pin mcp yourself)
mcp         (transitive)  fastmcp-slim already constrains it to mcp<2.0,>=1.24.0 — leave it implicit
anthropic   >=0.112,<1    (0.112.0 current)
pytest      >=9,<10       (9.1.1 current)
pytest-recording  >=0.13,<0.14   (0.13.4 current — the VCR.py plugin)
vcrpy       (transitive)  pulled by pytest-recording (8.2.1 current)
matplotlib  >=3.11,<4     (3.11.0 current; OPTIONAL — see Charting)
MCP Inspector  npx @modelcontextprotocol/inspector@0.22  (Node tool, not a Python dep)
```

The single most important version fact: **FastMCP 3.x already depends on the official `mcp` SDK and already constrains it to `<2.0`.** You do not write your own `mcp` pin — adding a second, redundant constraint is how you create the version-drift the brief warns about. Let FastMCP own that transitive pin.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Python** | `3.12` | Runtime | Project constraint. 3.12 is mature, fast, and within every dependency's support window. `matplotlib` 3.11 dropped 3.10 (needs `>=3.11`); `fastmcp`/`mcp`/`anthropic`/`pytest` all support `>=3.10`. 3.12 is the sweet spot. (Do not jump to 3.14 — no reason to, and it widens the wheel-availability surface.) |
| **uv** | `0.11.25` (pin `>=0.11,<0.12`) | Package/project manager, lockfile, venv, `uvx` runner | Project constraint, and the right call: single tool for env + lock + build + run. `uv lock` gives the reproducible CI the brief demands; `uvx uk-break-clause-analyzer` runs the published console script with zero install. Verified current on PyPI 2026-06-27. |
| **FastMCP** | `3.4.2` (pin `>=3.4,<4`) | MCP server framework | Project constraint ("FastMCP latest stable 3.x"). 3.4.2 is the current stable on PyPI (2026-06-27); 3.x is GA. Import surface is `from fastmcp import FastMCP` + `@mcp.tool` decorators. See the dedicated FastMCP section below for the mcp-SDK relationship — this is the load-bearing decision. |
| **anthropic** | `0.112.0` (pin `>=0.112,<1`) | Official Anthropic Python SDK — server-side extraction/reasoning calls | Project constraint (server makes its own API calls). 0.112.0 current on PyPI (2026-06-27). Sub-1.0, so cap at `<1` to avoid a future breaking major. Provides `client.messages.create(...)` and — critically for this project — **native Structured Outputs** and a `client.messages.parse()` Pydantic helper (see Anthropic section). |
| **pytest** | `9.1.1` (pin `>=9,<10`) | Eval harness test runner | Project constraint ("pytest for the eval harness"). v9 is current (2026-06-27). The eval harness IS the headline deliverable, so pytest is load-bearing, not incidental — parametrize over the labelled dataset, one assertion per metric. |
| **pytest-recording** | `0.13.4` (pin `>=0.13,<0.14`) | Record/replay Anthropic HTTP calls (VCR cassettes) for deterministic, key-free CI | The chosen cassette library (full rationale in its own section). Wraps VCR.py with clean pytest ergonomics: `@pytest.mark.vcr`, a `vcr_config` fixture for header redaction, and `--record-mode` on the CLI. This is what makes "reproducible in CI with no API key in under 2 minutes" true. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **vcrpy** | `8.2.1` (transitive) | Underlying HTTP record/replay engine | Pulled in by `pytest-recording`. Don't depend on it directly; configure it through the plugin's `vcr_config` fixture. Intercepts the `httpx` calls the anthropic SDK makes. |
| **pydantic** | `>=2.11` (transitive) | Typed extraction schemas | Already a dependency of both `fastmcp` and `anthropic`. Use it for the structured-extraction models fed to `client.messages.parse()` and for tool input/output types. No separate pin needed. |
| **python-dotenv** | `>=1.1` (transitive) | Load `ANTHROPIC_API_KEY` from `.env` in live mode | Already pulled by `fastmcp-slim`. Use for local live runs; CI replay needs no key at all. |
| **matplotlib** | `3.11.0` (pin `>=3.11,<4`) | One chart in the eval report (OPTIONAL) | Only if you want a raster/SVG bar chart of hallucination rate by model. Verified to support Python 3.12–3.14. Strongly consider the no-dep SVG alternative instead — see Charting. |
| **pytest-cov** | `7.1.0` | Coverage of the deterministic engine (grounding gate, date math) | Optional but cheap credibility signal for a reliability-focused repo. The deterministic code (not the LLM) is what coverage meaningfully measures. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| **MCP Inspector** | Manual/interactive testing of the running server | Run via `npx @modelcontextprotocol/inspector@0.22 <your-server-command>`. Node tool, **not** a Python dependency — keep it out of `pyproject.toml`. Current npm version 0.22.0 (verified on the npm registry 2026-06-27). Opens a browser UI at `http://localhost:6274`. See the Inspector section for what "passes Inspector" means. |
| **ruff** | Lint + format | Not required by the brief, but conventional in a uv/2026 Python repo and a free polish signal for a portfolio artifact. Add as a dev dependency if desired; not load-bearing. |
| **uv** (again) | `uv run pytest`, `uv build`, `uv lock` | The whole dev loop runs through uv. `uv build` produces the publish-ready wheel/sdist (built but not uploaded, per the brief). |

---

## Project Layout (Python 3.12 + uv, publish-ready console script)

Recommended `src/` layout so the installed package — not the working tree — is what gets tested and what `uvx` runs:

```
uk-break-clause-analyzer-mcp/
├── pyproject.toml
├── uv.lock                      # committed — reproducible CI
├── README.md
├── src/
│   └── uk_break_clause_analyzer/
│       ├── __init__.py
│       ├── server.py            # FastMCP server + main() entry point
│       ├── tools/               # extract_break_clause, check_conditions, find_citation, assess_validity
│       ├── grounding.py         # deterministic verbatim-span gate
│       ├── engine.py            # deterministic date math + strict-precedence aggregation
│       └── llm.py               # thin anthropic client wrapper (extraction/reasoning)
├── data/
│   └── cases/                   # 20–40 synthetic labelled case files + labels
├── tests/
│   ├── conftest.py              # vcr_config fixture (header redaction) lives here
│   ├── cassettes/               # committed VCR cassettes (key-redacted)
│   ├── test_extraction.py
│   ├── test_grounding.py
│   └── test_eval.py             # parametrized over data/cases, emits metrics
└── reports/
    └── eval_report.md           # generated; chart alongside
```

Minimal `pyproject.toml` (uv-native, `[project.scripts]` console entry):

```toml
[project]
name = "uk-break-clause-analyzer-mcp"
version = "0.1.0"
description = "Self-evaluating MCP server for UK commercial-lease tenant break-clause assessment"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
dependencies = [
    "fastmcp>=3.4,<4",      # pulls mcp<2 transitively — do NOT add a second mcp pin
    "anthropic>=0.112,<1",
]

[project.scripts]
# installable via uvx/pip; this is the "single command" that runs the server
uk-break-clause-analyzer = "uk_break_clause_analyzer.server:main"

[dependency-groups]            # uv-native dev deps (PEP 735); not shipped to end users
dev = [
    "pytest>=9,<10",
    "pytest-recording>=0.13,<0.14",
    "pytest-cov>=7,<8",
    # "matplotlib>=3.11,<4",   # only if you choose matplotlib over no-dep SVG
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Notes:
- **`main()` must call `mcp.run()`** (FastMCP's stdio transport is the default). The console-script target is `module:function`, e.g. `uk_break_clause_analyzer.server:main`. Keep the `if __name__ == "__main__": main()` guard too, so the module also runs as `python -m`.
- **`requires-python = ">=3.12"`** ties the package to the constraint while staying installable on 3.13/3.14 CI if ever needed.
- **`hatchling`** as build backend is the conventional, low-friction choice for a `src/` layout; `uv build` uses it to produce the wheel/sdist. (`uv_build` is also viable but hatchling is the safer, more widely understood default for a portfolio repo.)
- Confidence: **HIGH** on layout and `[project.scripts]` mechanics; `[dependency-groups]` (PEP 735) is the current uv-native dev-dep convention.

---

## FastMCP 3.x vs the `mcp` SDK — the load-bearing decision

**Verified against live sources on 2026-06-27:**

- **PyPI `fastmcp` latest = 3.4.2.** Its metadata depends on `fastmcp-slim[client,server]==3.4.2` (FastMCP 3.3 split the importable code into a `fastmcp-slim` distribution; `fastmcp` is now a thin meta-package over it — an internal detail, you still `pip install fastmcp`).
- **`fastmcp-slim` 3.4.2** `requires_dist` includes, for the `server` and `client` extras: **`mcp<2.0,>=1.24.0`**. So **standalone FastMCP 3.x uses the official `mcp` SDK underneath and already constrains it below v2.**
- **PyPI `mcp` latest = 1.28.1**, i.e. still on the 1.x line. The official SDK's **v2 is targeted for ~2026-07-27** (beta ~2026-06-30) — *after* today. FastMCP 3.0 was deliberately timed as a major release so it can absorb the SDK's v2 breaking changes under its own major-version bump (per the FastMCP 3.0 launch write-up).

**What this means for you (prescriptive):**

1. **Depend on `fastmcp>=3.4,<4` only.** Do **not** add `mcp` to your `dependencies`. The brief says "pin the official `mcp` SDK below v2 *if used*" — it is used, but transitively, and FastMCP *already* pins it `<2.0`. Adding your own `mcp<2` line is redundant at best and a future conflict at worst when FastMCP moves its own bound. Let FastMCP own the transitive constraint; `uv.lock` records the exact resolved `mcp` version for reproducibility.
2. **Two different "FastMCP"s exist — use the standalone one.** The official `mcp` SDK also ships a *bundled* `mcp.server.fastmcp.FastMCP` (the donated FastMCP 1.0). **That is not what 3.x is.** Import from the standalone package: `from fastmcp import FastMCP`. Importing `from mcp.server.fastmcp import FastMCP` would silently give you the old 1.0-era API and none of the 3.x features — a classic, easy-to-miss trap.
3. **Pin `<4`.** 3.x had real breaking changes inside the line (e.g. 3.0.2 removed `RouteType`/`FastMCPOpenAPI`/`get_prompts()`); the broader ecosystem broke when people left FastMCP unpinned and got pulled onto 3.x. `>=3.4,<4` plus a committed `uv.lock` is the safe envelope.

Canonical server skeleton (3.x import surface):

```python
# src/uk_break_clause_analyzer/server.py
from fastmcp import FastMCP

mcp = FastMCP("uk-break-clause-analyzer")

@mcp.tool
def extract_break_clause(lease_text: str) -> dict:
    """Extract the tenant break clause and its verbatim source span."""
    ...

def main() -> None:
    mcp.run()  # stdio transport by default

if __name__ == "__main__":
    main()
```

Confidence: **HIGH** on the version numbers and the transitive-`mcp<2` fact (read directly from PyPI metadata). **HIGH** on "import from `fastmcp`, not `mcp.server.fastmcp`". **MEDIUM** on the exact 3.x breaking-change list (sourced from the FastMCP changelog/launch posts, not re-read line by line) — pinning `<4` makes this moot.

---

## Anthropic SDK — structured extraction for grounded spans

**Verified on 2026-06-27:** `anthropic` 0.112.0 on PyPI; current model IDs from the official models-overview page.

**Current model IDs (the Haiku-vs-Sonnet comparison the brief wants):**

| Tier | API model ID | Alias | Pricing (in / out per MTok) |
|------|--------------|-------|------------------------------|
| Fast / cheap | `claude-haiku-4-5-20251001` | `claude-haiku-4-5` | $1 / $5 |
| Balanced | `claude-sonnet-4-6` | `claude-sonnet-4-6` | $3 / $15 |

Use the **aliases** (`claude-haiku-4-5`, `claude-sonnet-4-6`) in code/config; both are pinned snapshots in the 4.5/4.6 generation. Report both in the eval — same harness, run twice, framing reliability as a cost/deployment decision.

**Minimal call pattern:**

```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

msg = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": prompt}],
)
text = msg.content[0].text
```

**For grounded span extraction — use native Structured Outputs, not the old forced-tool-use trick.** This is a meaningful 2026 update versus what training data would suggest:

- The historical pattern was: define a "tool", set `tool_choice={"type":"tool","name":...}`, and read the tool-call JSON. It worked but did **not** guarantee schema-valid output, so you needed retries/repair.
- **Now: native Structured Outputs (GA).** Pass a JSON schema via `output_config={"format": {"type": "json_schema", "schema": {...}}}` and get grammar-constrained, schema-valid JSON. **No beta header required** as of 2026 (the old `structured-outputs-2025-11-13` header and `output_format` param still work during a transition window). Supported on `claude-haiku-4-5` and `claude-sonnet-4-6` — i.e. both models in your comparison.
- The SDK exposes a Pydantic helper: **`client.messages.parse(..., output_format=MyModel)`** returns `response.parsed_output` as a typed object. Use this for `extract_break_clause` — define a Pydantic model with the clause text + the verbatim span, and let the schema enforce shape.

```python
from pydantic import BaseModel
from anthropic import Anthropic

class BreakClauseExtraction(BaseModel):
    clause_text: str
    source_span: str          # MUST be verbatim — your grounding gate re-checks this
    found: bool

client = Anthropic()
resp = client.messages.parse(
    model="claude-haiku-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": f"Extract the tenant break clause...\n\n{lease_text}"}],
    output_format=BreakClauseExtraction,
)
extraction = resp.parsed_output      # typed BreakClauseExtraction
```

**Critical reliability point:** Structured Outputs guarantees the JSON *shape*, not the *truth* of `source_span`. The model can still emit a plausible-but-not-verbatim span. Your **deterministic grounding gate must independently verify `source_span` appears verbatim in `lease_text`, else force `NOT_FOUND`** — exactly the project's core thesis. Structured Outputs removes JSON-parsing failure modes so your eval measures *hallucination*, not *malformed-JSON noise*. Net: it strengthens the headline metric's cleanliness.

Why structured outputs over tool-use here: simpler call, guaranteed-valid JSON (no parse/repair branch polluting the harness), and one fewer source of non-determinism in the metric. Reserve forced tool-use only if you later need the orchestrating Claude to *call* these as MCP tools — which is the MCP layer, a separate concern from the server's own extraction calls.

Confidence: **HIGH** on SDK version and the `messages.create`/`messages.parse` surface (official Python SDK page). **HIGH** on model IDs (official models-overview page). **HIGH** that Structured Outputs is GA and supersedes forced-tool-use for JSON; **MEDIUM** on the precise `output_config.format` vs legacy `output_format` migration details (transition window means both work, so low risk).

---

## Cassette / record-replay — chosen library + pitfalls

**Recommendation: `pytest-recording` (0.13.4)**, which drives `vcrpy` (8.2.1) under the hood. This is the best fit for "record live Anthropic calls once, replay deterministically in CI with no API key, in under 2 minutes."

**Why this over the alternatives:**

| Option | Verdict | Reason |
|--------|---------|--------|
| **pytest-recording** (chosen) | ✅ Use | Actively maintained VCR.py plugin with the cleanest pytest ergonomics: `@pytest.mark.vcr`, a `vcr_config` fixture for redaction, and `--record-mode=none/once/rewrite` on the CLI. CI runs with `--record-mode=none` → fails loudly if a cassette is missing → guarantees *no* live call (and no key) in CI. Intercepts the `httpx` transport the anthropic SDK uses, so it captures the real requests transparently. |
| **vcrpy** (direct) | ➖ Indirect | It's the engine, and you'll depend on it transitively — but using it directly means hand-rolling fixtures pytest-recording already gives you. Use it *through* the plugin. |
| **pytest-vcr** | ❌ Avoid | Older, thinner, less maintained than pytest-recording; pytest-recording is its de-facto successor with better record-mode control. |
| **anthropic's own request mocking / `respx`** | ❌ Avoid | Mocking returns canned responses you wrote — that defeats the entire point. The eval's credibility rests on replaying *real, recorded* model outputs. Hand-written mocks would let you fake the hallucination rate; recorded cassettes prove it. |
| **Thin custom JSON cassette** | ❌ Avoid | Reinventing VCR. More code, more bugs, no redaction tooling, and a reviewer has to trust your bespoke harness instead of a known library. Only consider if you needed to record something VCR can't intercept — not the case here (it's plain HTTPS via httpx). |

**Configuration (lives in `tests/conftest.py`):**

```python
import pytest

@pytest.fixture(scope="module")
def vcr_config():
    return {
        # Anthropic auth header is x-api-key (NOT Authorization) — redact it.
        "filter_headers": [
            ("x-api-key", "REDACTED"),
            ("authorization", "REDACTED"),   # belt-and-braces
        ],
        # Match replay on method + URL + body so different prompts -> different cassettes.
        "match_on": ["method", "scheme", "host", "port", "path", "body"],
        "record_mode": "none",               # default for CI; override locally to record
    }
```

Record locally once with a real key:
```bash
ANTHROPIC_API_KEY=sk-... uv run pytest --record-mode=once
```
Then CI (no key) replays:
```bash
uv run pytest --record-mode=none        # missing cassette => hard failure, never a live call
```

**Pitfalls (call these out explicitly):**

1. **Redact the right header — Anthropic uses `x-api-key`, not `Authorization`.** The most-cited VCR examples redact `authorization` (HTTP Basic / Bearer). If you copy those blindly, your **real API key gets committed into a cassette in a public portfolio repo.** Redact `x-api-key` (and `authorization` defensively). Verify the first recorded cassette by eye before committing.
2. **Body matching is required, not optional.** Default VCR matching is method+URI, which ignores the request body. Two different lease prompts hit the *same* URL (`/v1/messages`), so without `body` in `match_on` they'd collide onto one cassette and replay the wrong response — silently corrupting the eval. Match on `body`.
3. **Structured-Outputs / system-prompt drift breaks body matching.** If you tweak the prompt or schema, the request body changes and the old cassette won't match → re-record. That's correct behaviour (the recording is stale), but budget for re-recording when prompts change, and don't let `--record-mode=once` silently fall back to a live call in CI (use `none` in CI).
4. **Determinism of model output:** even recorded, set generation params explicitly (e.g. low/zero temperature where the harness wants determinism) *before* recording, so the captured response reflects the eval's intended config. The cassette freezes whatever the live call returned.
5. **Cassette size / secrecy review:** cassettes contain full request+response bodies (lease text + model output). Since data is synthetic (per project constraints) this is fine — but confirm no real key, no real lease text ever enters a cassette. This dovetails with the project's "synthetic data only" gate.

Confidence: **HIGH** on library choice, versions, and the `x-api-key` redaction pitfall (Anthropic's documented auth header). **HIGH** on body-matching necessity (VCR's documented default behaviour).

---

## pytest harness — version + plugins

- **pytest 9.1.1** (pin `>=9,<10`). Current major; nothing in the harness needs a pre-9 feature.
- **pytest-recording 0.13.4** — cassettes (above). The one essential plugin.
- **Parametrization over the labelled dataset:** use built-in `@pytest.mark.parametrize` driven by a fixture that loads `data/cases/*`. One test per case, or one test per metric parametrized across cases. No extra plugin needed — keep the harness legible for a reviewer.
- **pytest-cov 7.1.0** (optional) — coverage of the *deterministic* engine (grounding gate, date math, aggregation). That's where coverage is meaningful; don't chase coverage of the LLM-call paths.
- **Reporting:** prefer to **compute the four metrics in the harness and write `reports/eval_report.md` yourself** (you control the format, the headline hallucination-rate framing, and the Haiku-vs-Sonnet table). A plugin like `pytest-md-report` (0.8.0) exists but produces a generic pass/fail table — not the bespoke metrics report the project needs. **Do not** outsource the headline artifact to a generic plugin.
- **`pytest-asyncio` (1.4.0)** — add **only if** you make the anthropic calls async (`AsyncAnthropic`). For a 20–40 case eval, sync is simpler and fast enough under cassette replay; skip async and skip this plugin unless you have a concrete latency reason.

Confidence: **HIGH** on pytest 9 and plugin versions (PyPI verified 2026-06-27); **HIGH** on "write the report yourself" as the right call for a portfolio metric artifact.

---

## MCP Inspector — how it's run, and what "passes" means

**How (mid-2026):** Inspector is a Node tool run via npx — **not** a Python dependency:

```bash
npx @modelcontextprotocol/inspector@0.22 uk-break-clause-analyzer
# or, before install:
npx @modelcontextprotocol/inspector@0.22 uvx uk-break-clause-analyzer
```

Current npm version **0.22.0** (verified on the npm registry 2026-06-27). It launches your server as a stdio child process and opens a browser UI (default `http://localhost:6274`) to list tools, inspect their schemas, and invoke them with arguments.

**What "passes Inspector" means operationally** (this is your manual acceptance gate):
1. **Server launches and handshakes** — Inspector connects over stdio without protocol errors (initialize succeeds).
2. **All four tools are discovered** — `extract_break_clause`, `check_conditions`, `find_citation`, `assess_validity` appear in the tool list with correct names/descriptions.
3. **Input schemas are well-formed** — each tool shows the expected parameters (derived from your type hints / Pydantic models); no missing or malformed schema.
4. **Tools execute end-to-end** — invoking each with a sample case returns a valid, schema-conforming result (and, for the grounded tools, a real verbatim span or `NOT_FOUND` — never an invented citation).
5. **No stderr protocol contamination** — your logging goes to stderr/files, not stdout (stdout is the JSON-RPC channel; printing there corrupts the protocol). A clean Inspector session confirms this.

Treat a clean pass as a README-worthy checklist item ("runs via a single command and passes MCP Inspector"). It's a *manual* gate — distinct from the automated pytest eval — and both should be green.

Confidence: **HIGH** on the npx invocation and version (npm registry); **HIGH** on the operational checklist (standard Inspector behaviour).

---

## Charting — lightest dependable option

**Recommendation: emit a hand-written SVG bar chart with zero charting dependencies** for the hallucination-rate-by-model figure, and reserve matplotlib only if you later need richer plots.

Rationale (favouring minimal deps + reproducibility, per the brief):
- The eval report needs *one* simple comparative bar chart (hallucination rate: Haiku vs Sonnet, maybe alongside the other three metrics). That's a handful of `<rect>`/`<text>` elements — ~40 lines of Python string-templating, **no dependency, no binary wheels, byte-identical output across machines**, and it renders inline in GitHub markdown. For a reliability/reproducibility-themed repo, "the chart has no dependencies and is deterministic" is itself on-message.
- **matplotlib 3.11.0** is the fallback. It's excellent and verified to support Python 3.12, but it's a heavy dependency (NumPy + native wheels), adds CI install time against the under-2-minute budget, and its raster output isn't byte-reproducible by default (font/AA differences across platforms). Pin `>=3.11,<4` *only if* you adopt it, and keep it in the `dev` group (it's a report-generation tool, not a runtime dep).

| Approach | Deps | Reproducible | Use when |
|----------|------|--------------|----------|
| **No-dep SVG** (recommended) | none | Yes (deterministic text) | One/few simple bar charts — exactly this project |
| **matplotlib** | NumPy + native | Not by default | You need many or complex plots, or polished styling |
| **Markdown table only** | none | Yes | Fallback if even SVG is overkill; less visually striking for a portfolio reviewer |

A pragmatic middle path: render the SVG **and** include a plain markdown metrics table — the table is the source of truth, the SVG is the visual. Both deterministic, both zero-dep.

Confidence: **HIGH** on matplotlib version/Python-3.12 support (PyPI verified); **HIGH** on the no-dep-SVG recommendation as the minimal-dep/reproducible choice (this is a judgement call the brief explicitly asked for, and it aligns with the project's reproducibility thesis).

---

## Installation

```bash
# Bootstrap the project (uv creates venv + pins Python 3.12)
uv init --package uk-break-clause-analyzer-mcp
uv python pin 3.12

# Runtime deps
uv add "fastmcp>=3.4,<4" "anthropic>=0.112,<1"
#  ^ fastmcp pulls mcp<2 transitively — do NOT `uv add mcp`

# Dev deps (eval harness)
uv add --dev "pytest>=9,<10" "pytest-recording>=0.13,<0.14" "pytest-cov>=7,<8"
# Optional charting (prefer no-dep SVG instead):
# uv add --dev "matplotlib>=3.11,<4"

# Lock for reproducible CI
uv lock

# Build the publish-ready (but unpublished) artifact
uv build

# Run the server (the [project.scripts] console entry)
uv run uk-break-clause-analyzer
# ...or via uvx once built/installed:
uvx uk-break-clause-analyzer

# Inspect (Node tool, separate from Python deps)
npx @modelcontextprotocol/inspector@0.22 uvx uk-break-clause-analyzer

# Eval: record once locally, replay key-free in CI
ANTHROPIC_API_KEY=sk-... uv run pytest --record-mode=once   # local, real calls
uv run pytest --record-mode=none                            # CI, no key, replay only
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `fastmcp` (standalone 3.x) | Bundled `mcp.server.fastmcp` from the `mcp` SDK | Never for this project — the brief mandates FastMCP 3.x. The bundled one is FastMCP 1.0-era and lacks 3.x features. Only relevant if you deliberately wanted the low-level SDK. |
| Let `fastmcp` pin `mcp` transitively | Add explicit `mcp<2` to your deps | Only if you call the `mcp` SDK *directly* (you don't — you go through FastMCP). Avoid the redundant pin. |
| Native Structured Outputs (`messages.parse`) | Forced tool-use (`tool_choice`) for JSON | Use tool-use when the *orchestrating* Claude must call your tools as MCP tools (the MCP layer) — not for the server's own extraction calls. |
| pytest-recording | pytest-vcr | If a dependency forced an older VCR integration — not the case here. pytest-recording is the maintained successor. |
| No-dep SVG chart | matplotlib | When you need many/complex/styled plots. For one bar chart, the dependency cost isn't worth it. |
| Sync `Anthropic` client | `AsyncAnthropic` + pytest-asyncio | If eval latency against *live* calls matters at scale. Under cassette replay with 20–40 cases, sync is fast enough and simpler. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| A hand-pinned `mcp<2` in `dependencies` | Redundant with FastMCP's own transitive `mcp<2.0,>=1.24.0`; risks a future resolver conflict when FastMCP moves its bound | Depend on `fastmcp>=3.4,<4` only; let `uv.lock` record the resolved `mcp` |
| `from mcp.server.fastmcp import FastMCP` | That's the donated FastMCP 1.0 inside the SDK — wrong API, none of the 3.x features, silent mismatch | `from fastmcp import FastMCP` |
| Unpinned `fastmcp` | 3.x shipped intra-line breaking changes; the ecosystem broke when people got auto-upgraded onto 3.x unpinned | `fastmcp>=3.4,<4` + committed `uv.lock` |
| Hand-written mocks / `respx` for Anthropic | Canned responses you authored let you (accidentally or not) fake the hallucination rate — destroys the eval's credibility | Recorded VCR cassettes via pytest-recording (real model outputs, replayed) |
| Redacting only `Authorization` in cassettes | Anthropic auth is `x-api-key`; copying generic VCR examples leaks your real key into a public repo | Redact `x-api-key` (and `authorization` defensively); eyeball the first cassette |
| Default VCR method+URI matching | All calls hit `/v1/messages`; without body matching, different prompts collide onto one cassette and replay wrong responses | Add `body` to `match_on` |
| matplotlib for one bar chart | Heavy (NumPy + native wheels), slows CI against the <2-min budget, not byte-reproducible by default | No-dep hand-written SVG (+ a markdown metrics table) |
| `--record-mode=once`/`any` in CI | Can silently fall through to a live call (needs a key, non-deterministic, may hit network) | `--record-mode=none` in CI — missing cassette is a hard failure |
| Pre-9 pytest, pre-3.x FastMCP, anthropic without `<1` cap | Stale APIs / unguarded breaking majors | The pins in the TL;DR table |

---

## Version Compatibility

| Package | Compatible with | Notes |
|---------|-----------------|-------|
| `fastmcp 3.4.2` | `mcp <2.0,>=1.24.0` | Constraint comes from `fastmcp-slim`; verified in PyPI metadata 2026-06-27. `mcp` 1.28.1 is current; v2 lands ~2026-07-27 — FastMCP's `<2` cap protects you. |
| `fastmcp 3.4.2` / `mcp` / `anthropic` / `pytest 9` | Python `>=3.10` (you use 3.12) | All comfortably support 3.12. |
| `matplotlib 3.11.0` | Python `>=3.11` (3.12/3.13/3.14 OK) | Dropped 3.10. Fine on 3.12. |
| `pytest-recording 0.13.4` | `vcrpy 8.2.1`, `pytest 9` | Plugin tracks current pytest; vcrpy pulled transitively. |
| `anthropic 0.112.0` | `httpx` (its HTTP backend) | VCR/pytest-recording intercepts at the httpx layer — this is *why* recording works transparently. |
| Structured Outputs | `claude-haiku-4-5`, `claude-sonnet-4-6` | Both models in your comparison support it; no beta header required as of 2026. |

---

## Confidence Caveats (what I could NOT fully verify against a live source)

- **FastMCP 3.x exact intra-line breaking-change list** — sourced from the FastMCP changelog/launch blog posts, not re-read line by line against the current `main`. Mitigation: pin `>=3.4,<4` + `uv.lock`. (MEDIUM)
- **`output_config.format` vs legacy `output_format` migration nuance** — official docs say both work during a transition window; I did not exhaustively confirm which is canonical in `anthropic` 0.112.0 specifically. The `messages.parse()` Pydantic helper sidesteps the raw param entirely — prefer it. (MEDIUM)
- **MCP Inspector 0.22.x exact default port / flag surface** — `6274` and the `npx ... <command>` form are well-established, but verify against `--help` when you first run it; minor UI/flag changes between 0.2x releases are possible. (MEDIUM)
- Everything in the TL;DR pin table (fastmcp 3.4.2, mcp 1.28.1, anthropic 0.112.0, pytest 9.1.1, pytest-recording 0.13.4, vcrpy 8.2.1, matplotlib 3.11.0, uv 0.11.25, Inspector 0.22.0) was read **directly from PyPI / npm registry JSON on 2026-06-27** — **HIGH** confidence on the numbers themselves.

---

## Sources

- **PyPI JSON API** (read 2026-06-27) — exact current versions + `requires_python` + `requires_dist` for: `fastmcp` (3.4.2), `fastmcp-slim` (3.4.2 → `mcp<2.0,>=1.24.0`), `mcp` (1.28.1), `anthropic` (0.112.0), `pytest` (9.1.1), `pytest-recording` (0.13.4), `vcrpy` (8.2.1), `pytest-vcr` (1.0.2), `pytest-asyncio` (1.4.0), `pytest-cov` (7.1.0), `matplotlib` (3.11.0 → Python 3.12–3.14), `uv` (0.11.25). **HIGH**
- **npm registry** (`@modelcontextprotocol/inspector/latest`, read 2026-06-27) — Inspector **0.22.0**. **HIGH**
- **gofastmcp.com** — `/getting-started/welcome`, `/getting-started/installation`, `/servers/server` — FastMCP 3.x import surface (`from fastmcp import FastMCP`, `@mcp.tool`, `mcp.run()`), `fastmcp-slim` split, install commands. **HIGH**
- **github.com/modelcontextprotocol/python-sdk** (README) — official `mcp` SDK on v1.x; v2 beta ~2026-06-30, stable ~2026-07-27; bundles its own `mcp.server.fastmcp`. **HIGH**
- **jlowin.dev/blog/fastmcp-3** (+ PrefectHQ/jlowin fastmcp releases/changelog) — FastMCP 3.0 GA, primitives rework, intra-line breaking changes, deliberate timing vs SDK v2. **MEDIUM** (blog/changelog, not package metadata)
- **platform.claude.com/docs** — `/cli-sdks-libraries/sdks/python` (SDK usage, `messages.create`, tool helpers), `/build-with-claude/structured-outputs` (`output_config.format`, `messages.parse`, GA, no beta header), `/about-claude/models/overview` (model IDs: `claude-haiku-4-5`, `claude-sonnet-4-6`, pricing). **HIGH**
- **modelcontextprotocol.io/docs/tools/inspector** + **github.com/modelcontextprotocol/inspector** — npx invocation, stdio child process, `localhost:6274`. **HIGH**
- **vcrpy.readthedocs.io (advanced)** + **kiwicom/pytest-recording** + Simon Willison's pytest-recording TIL + imoskvin redaction post — `filter_headers`, `match_on` body matching, `record_mode`, redaction-before-commit. **HIGH** on mechanics; **HIGH** on the `x-api-key` (Anthropic-specific) redaction point.

---
*Stack research for: self-evaluating UK break-clause analyzer MCP server (Python 3.12 + uv + FastMCP 3.x)*
*Researched: 2026-06-27*
