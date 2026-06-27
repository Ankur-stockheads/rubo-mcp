<!-- GSD:project-start source:PROJECT.md -->

## Project

**UK Break Clause Analyzer (MCP)**

A public, rigorously-evaluated MCP server that assesses whether a UK commercial-lease *tenant* break clause can actually be exercised — and proves it isn't hallucinating. It exposes single-purpose tools (extract the clause, check conditions, find citations, assess validity) that an orchestrating Claude composes, and ships a self-evaluating harness that publishes its own measured hallucination rate. Built as a credibility artifact for an Anthropic Applied AI / Forward Deployed Engineer application — the eval suite and reliability engineering are the headline, not the parsing.

**Core Value:** Every asserted condition is grounded to a verbatim source span or returns `NOT_FOUND` — never invented — and the server proves with a published hallucination rate that it would rather say "ambiguous — human verify" than guess.

### Constraints

- **Tech stack**: Python 3.12, managed with uv — modern, reproducible toolchain.
- **Tech stack**: FastMCP latest stable 3.x; confirm exact versions against gofastmcp.com and github.com/modelcontextprotocol/python-sdk before coding; pin the official `mcp` SDK below v2 if used — avoid version drift and hallucinated APIs.
- **Tooling**: pytest for the eval harness; MCP Inspector for manual testing.
- **Packaging**: PyPI-ready with a `[project.scripts]` console entry; installable via `uvx`/`pip`, not published in v1.
- **Data**: synthetic / public data only; never real client leases — confidentiality and reproducibility.
- **Self-containment**: generate all scaffolding, parsing, config, and logic from scratch; no external repos cloned, read, or imported; nothing proprietary present anywhere — enforced via gates.
- **Scope**: break clauses only; reject any expansion to other provisions.
- **Legal**: decision-support, not legal advice; disclaimer required in the README and in tool output.
- **Reproducibility**: the eval runs in under 2 minutes and is replayable in CI without an API key (recorded cassettes).
- **Engine**: deterministic code for date math, checklist, and grounding; the LLM is used only for extraction and reasoning; explicit grounding for every citation.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->

## Technology Stack

## TL;DR — Pin These

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

## Project Layout (Python 3.12 + uv, publish-ready console script)

# installable via uvx/pip; this is the "single command" that runs the server

- **`main()` must call `mcp.run()`** (FastMCP's stdio transport is the default). The console-script target is `module:function`, e.g. `uk_break_clause_analyzer.server:main`. Keep the `if __name__ == "__main__": main()` guard too, so the module also runs as `python -m`.
- **`requires-python = ">=3.12"`** ties the package to the constraint while staying installable on 3.13/3.14 CI if ever needed.
- **`hatchling`** as build backend is the conventional, low-friction choice for a `src/` layout; `uv build` uses it to produce the wheel/sdist. (`uv_build` is also viable but hatchling is the safer, more widely understood default for a portfolio repo.)
- Confidence: **HIGH** on layout and `[project.scripts]` mechanics; `[dependency-groups]` (PEP 735) is the current uv-native dev-dep convention.

## FastMCP 3.x vs the `mcp` SDK — the load-bearing decision

- **PyPI `fastmcp` latest = 3.4.2.** Its metadata depends on `fastmcp-slim[client,server]==3.4.2` (FastMCP 3.3 split the importable code into a `fastmcp-slim` distribution; `fastmcp` is now a thin meta-package over it — an internal detail, you still `pip install fastmcp`).
- **`fastmcp-slim` 3.4.2** `requires_dist` includes, for the `server` and `client` extras: **`mcp<2.0,>=1.24.0`**. So **standalone FastMCP 3.x uses the official `mcp` SDK underneath and already constrains it below v2.**
- **PyPI `mcp` latest = 1.28.1**, i.e. still on the 1.x line. The official SDK's **v2 is targeted for ~2026-07-27** (beta ~2026-06-30) — *after* today. FastMCP 3.0 was deliberately timed as a major release so it can absorb the SDK's v2 breaking changes under its own major-version bump (per the FastMCP 3.0 launch write-up).

# src/uk_break_clause_analyzer/server.py

## Anthropic SDK — structured extraction for grounded spans

| Tier | API model ID | Alias | Pricing (in / out per MTok) |
|------|--------------|-------|------------------------------|
| Fast / cheap | `claude-haiku-4-5-20251001` | `claude-haiku-4-5` | $1 / $5 |
| Balanced | `claude-sonnet-4-6` | `claude-sonnet-4-6` | $3 / $15 |

- The historical pattern was: define a "tool", set `tool_choice={"type":"tool","name":...}`, and read the tool-call JSON. It worked but did **not** guarantee schema-valid output, so you needed retries/repair.
- **Now: native Structured Outputs (GA).** Pass a JSON schema via `output_config={"format": {"type": "json_schema", "schema": {...}}}` and get grammar-constrained, schema-valid JSON. **No beta header required** as of 2026 (the old `structured-outputs-2025-11-13` header and `output_format` param still work during a transition window). Supported on `claude-haiku-4-5` and `claude-sonnet-4-6` — i.e. both models in your comparison.
- The SDK exposes a Pydantic helper: **`client.messages.parse(..., output_format=MyModel)`** returns `response.parsed_output` as a typed object. Use this for `extract_break_clause` — define a Pydantic model with the clause text + the verbatim span, and let the schema enforce shape.

## Cassette / record-replay — chosen library + pitfalls

| Option | Verdict | Reason |
|--------|---------|--------|
| **pytest-recording** (chosen) | ✅ Use | Actively maintained VCR.py plugin with the cleanest pytest ergonomics: `@pytest.mark.vcr`, a `vcr_config` fixture for redaction, and `--record-mode=none/once/rewrite` on the CLI. CI runs with `--record-mode=none` → fails loudly if a cassette is missing → guarantees *no* live call (and no key) in CI. Intercepts the `httpx` transport the anthropic SDK uses, so it captures the real requests transparently. |
| **vcrpy** (direct) | ➖ Indirect | It's the engine, and you'll depend on it transitively — but using it directly means hand-rolling fixtures pytest-recording already gives you. Use it *through* the plugin. |
| **pytest-vcr** | ❌ Avoid | Older, thinner, less maintained than pytest-recording; pytest-recording is its de-facto successor with better record-mode control. |
| **anthropic's own request mocking / `respx`** | ❌ Avoid | Mocking returns canned responses you wrote — that defeats the entire point. The eval's credibility rests on replaying *real, recorded* model outputs. Hand-written mocks would let you fake the hallucination rate; recorded cassettes prove it. |
| **Thin custom JSON cassette** | ❌ Avoid | Reinventing VCR. More code, more bugs, no redaction tooling, and a reviewer has to trust your bespoke harness instead of a known library. Only consider if you needed to record something VCR can't intercept — not the case here (it's plain HTTPS via httpx). |

## pytest harness — version + plugins

- **pytest 9.1.1** (pin `>=9,<10`). Current major; nothing in the harness needs a pre-9 feature.
- **pytest-recording 0.13.4** — cassettes (above). The one essential plugin.
- **Parametrization over the labelled dataset:** use built-in `@pytest.mark.parametrize` driven by a fixture that loads `data/cases/*`. One test per case, or one test per metric parametrized across cases. No extra plugin needed — keep the harness legible for a reviewer.
- **pytest-cov 7.1.0** (optional) — coverage of the *deterministic* engine (grounding gate, date math, aggregation). That's where coverage is meaningful; don't chase coverage of the LLM-call paths.
- **Reporting:** prefer to **compute the four metrics in the harness and write `reports/eval_report.md` yourself** (you control the format, the headline hallucination-rate framing, and the Haiku-vs-Sonnet table). A plugin like `pytest-md-report` (0.8.0) exists but produces a generic pass/fail table — not the bespoke metrics report the project needs. **Do not** outsource the headline artifact to a generic plugin.
- **`pytest-asyncio` (1.4.0)** — add **only if** you make the anthropic calls async (`AsyncAnthropic`). For a 20–40 case eval, sync is simpler and fast enough under cassette replay; skip async and skip this plugin unless you have a concrete latency reason.

## MCP Inspector — how it's run, and what "passes" means

# or, before install:

## Charting — lightest dependable option

- The eval report needs *one* simple comparative bar chart (hallucination rate: Haiku vs Sonnet, maybe alongside the other three metrics). That's a handful of `<rect>`/`<text>` elements — ~40 lines of Python string-templating, **no dependency, no binary wheels, byte-identical output across machines**, and it renders inline in GitHub markdown. For a reliability/reproducibility-themed repo, "the chart has no dependencies and is deterministic" is itself on-message.
- **matplotlib 3.11.0** is the fallback. It's excellent and verified to support Python 3.12, but it's a heavy dependency (NumPy + native wheels), adds CI install time against the under-2-minute budget, and its raster output isn't byte-reproducible by default (font/AA differences across platforms). Pin `>=3.11,<4` *only if* you adopt it, and keep it in the `dev` group (it's a report-generation tool, not a runtime dep).

| Approach | Deps | Reproducible | Use when |
|----------|------|--------------|----------|
| **No-dep SVG** (recommended) | none | Yes (deterministic text) | One/few simple bar charts — exactly this project |
| **matplotlib** | NumPy + native | Not by default | You need many or complex plots, or polished styling |
| **Markdown table only** | none | Yes | Fallback if even SVG is overkill; less visually striking for a portfolio reviewer |

## Installation

# Bootstrap the project (uv creates venv + pins Python 3.12)

# Runtime deps

#  ^ fastmcp pulls mcp<2 transitively — do NOT `uv add mcp`

# Dev deps (eval harness)

# Optional charting (prefer no-dep SVG instead):

# uv add --dev "matplotlib>=3.11,<4"

# Lock for reproducible CI

# Build the publish-ready (but unpublished) artifact

# Run the server (the [project.scripts] console entry)

# ...or via uvx once built/installed:

# Inspect (Node tool, separate from Python deps)

# Eval: record once locally, replay key-free in CI

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| `fastmcp` (standalone 3.x) | Bundled `mcp.server.fastmcp` from the `mcp` SDK | Never for this project — the brief mandates FastMCP 3.x. The bundled one is FastMCP 1.0-era and lacks 3.x features. Only relevant if you deliberately wanted the low-level SDK. |
| Let `fastmcp` pin `mcp` transitively | Add explicit `mcp<2` to your deps | Only if you call the `mcp` SDK *directly* (you don't — you go through FastMCP). Avoid the redundant pin. |
| Native Structured Outputs (`messages.parse`) | Forced tool-use (`tool_choice`) for JSON | Use tool-use when the *orchestrating* Claude must call your tools as MCP tools (the MCP layer) — not for the server's own extraction calls. |
| pytest-recording | pytest-vcr | If a dependency forced an older VCR integration — not the case here. pytest-recording is the maintained successor. |
| No-dep SVG chart | matplotlib | When you need many/complex/styled plots. For one bar chart, the dependency cost isn't worth it. |
| Sync `Anthropic` client | `AsyncAnthropic` + pytest-asyncio | If eval latency against *live* calls matters at scale. Under cassette replay with 20–40 cases, sync is fast enough and simpler. |

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

## Version Compatibility

| Package | Compatible with | Notes |
|---------|-----------------|-------|
| `fastmcp 3.4.2` | `mcp <2.0,>=1.24.0` | Constraint comes from `fastmcp-slim`; verified in PyPI metadata 2026-06-27. `mcp` 1.28.1 is current; v2 lands ~2026-07-27 — FastMCP's `<2` cap protects you. |
| `fastmcp 3.4.2` / `mcp` / `anthropic` / `pytest 9` | Python `>=3.10` (you use 3.12) | All comfortably support 3.12. |
| `matplotlib 3.11.0` | Python `>=3.11` (3.12/3.13/3.14 OK) | Dropped 3.10. Fine on 3.12. |
| `pytest-recording 0.13.4` | `vcrpy 8.2.1`, `pytest 9` | Plugin tracks current pytest; vcrpy pulled transitively. |
| `anthropic 0.112.0` | `httpx` (its HTTP backend) | VCR/pytest-recording intercepts at the httpx layer — this is *why* recording works transparently. |
| Structured Outputs | `claude-haiku-4-5`, `claude-sonnet-4-6` | Both models in your comparison support it; no beta header required as of 2026. |

## Confidence Caveats (what I could NOT fully verify against a live source)

- **FastMCP 3.x exact intra-line breaking-change list** — sourced from the FastMCP changelog/launch blog posts, not re-read line by line against the current `main`. Mitigation: pin `>=3.4,<4` + `uv.lock`. (MEDIUM)
- **`output_config.format` vs legacy `output_format` migration nuance** — official docs say both work during a transition window; I did not exhaustively confirm which is canonical in `anthropic` 0.112.0 specifically. The `messages.parse()` Pydantic helper sidesteps the raw param entirely — prefer it. (MEDIUM)
- **MCP Inspector 0.22.x exact default port / flag surface** — `6274` and the `npx ... <command>` form are well-established, but verify against `--help` when you first run it; minor UI/flag changes between 0.2x releases are possible. (MEDIUM)
- Everything in the TL;DR pin table (fastmcp 3.4.2, mcp 1.28.1, anthropic 0.112.0, pytest 9.1.1, pytest-recording 0.13.4, vcrpy 8.2.1, matplotlib 3.11.0, uv 0.11.25, Inspector 0.22.0) was read **directly from PyPI / npm registry JSON on 2026-06-27** — **HIGH** confidence on the numbers themselves.

## Sources

- **PyPI JSON API** (read 2026-06-27) — exact current versions + `requires_python` + `requires_dist` for: `fastmcp` (3.4.2), `fastmcp-slim` (3.4.2 → `mcp<2.0,>=1.24.0`), `mcp` (1.28.1), `anthropic` (0.112.0), `pytest` (9.1.1), `pytest-recording` (0.13.4), `vcrpy` (8.2.1), `pytest-vcr` (1.0.2), `pytest-asyncio` (1.4.0), `pytest-cov` (7.1.0), `matplotlib` (3.11.0 → Python 3.12–3.14), `uv` (0.11.25). **HIGH**
- **npm registry** (`@modelcontextprotocol/inspector/latest`, read 2026-06-27) — Inspector **0.22.0**. **HIGH**
- **gofastmcp.com** — `/getting-started/welcome`, `/getting-started/installation`, `/servers/server` — FastMCP 3.x import surface (`from fastmcp import FastMCP`, `@mcp.tool`, `mcp.run()`), `fastmcp-slim` split, install commands. **HIGH**
- **github.com/modelcontextprotocol/python-sdk** (README) — official `mcp` SDK on v1.x; v2 beta ~2026-06-30, stable ~2026-07-27; bundles its own `mcp.server.fastmcp`. **HIGH**
- **jlowin.dev/blog/fastmcp-3** (+ PrefectHQ/jlowin fastmcp releases/changelog) — FastMCP 3.0 GA, primitives rework, intra-line breaking changes, deliberate timing vs SDK v2. **MEDIUM** (blog/changelog, not package metadata)
- **platform.claude.com/docs** — `/cli-sdks-libraries/sdks/python` (SDK usage, `messages.create`, tool helpers), `/build-with-claude/structured-outputs` (`output_config.format`, `messages.parse`, GA, no beta header), `/about-claude/models/overview` (model IDs: `claude-haiku-4-5`, `claude-sonnet-4-6`, pricing). **HIGH**
- **modelcontextprotocol.io/docs/tools/inspector** + **github.com/modelcontextprotocol/inspector** — npx invocation, stdio child process, `localhost:6274`. **HIGH**
- **vcrpy.readthedocs.io (advanced)** + **kiwicom/pytest-recording** + Simon Willison's pytest-recording TIL + imoskvin redaction post — `filter_headers`, `match_on` body matching, `record_mode`, redaction-before-commit. **HIGH** on mechanics; **HIGH** on the `x-api-key` (Anthropic-specific) redaction point.

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
