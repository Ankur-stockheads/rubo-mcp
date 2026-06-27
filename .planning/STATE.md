# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-27)

**Core value:** Every asserted condition is grounded to a verbatim source span or returns NOT_FOUND — never invented — and the server proves with a published hallucination rate that it would rather say "ambiguous — human verify" than guess.
**Current focus:** All 5 phases built and tested — v1 complete.

## Current Position

Phase: 5 of 5 (Full Eval, Report & README)
Plan: complete
Status: ✓ Built — 62 passing tests, 5 atomic phase commits, eval report + README shipped
Last activity: 2026-06-27 — Phases 1–5 implemented directly; `uv build` produces a publish-ready wheel; MCP server passes an in-memory client roundtrip.

Progress: [██████████] 100%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: — min
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: none yet
- Trend: —

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Eval-first ordering is non-negotiable — gold dataset + scoring harness + cassette infra is Phase 1, before any server logic; the harness is proven against a stub oracle independently of the system under test.
- [Roadmap]: Horizontal-layer structure (standard granularity) — deterministic core (P2) is a distinct key-free layer before the LLM adapter (P3); the MCP surface (P4) is a thin wrapper near the end; full comparative eval + report + README is the final deliverable (P5).
- [Roadmap]: Hallucination definition (ungrounded OR misgrounded) and calibration metrics are pre-registered in Phase 1 before any prompt iteration, to pre-empt metric-gaming and over-abstention.

### Pending Todos

[From .planning/todos/pending/ — ideas captured during sessions]

None yet.

### Blockers/Concerns

[Issues that affect future work]

- ✓ RESOLVED [Phase 3]: `anthropic` 0.112.0 uses `messages.parse(..., output_format=Model) -> ParsedMessage`; the parsed object is read from `.parsed_output` (verified against the installed SDK). Client response-parsing is unit-tested via a mock.
- ✓ RESOLVED [Phase 4]: FastMCP 3.4.2 verified against the installed package — `@mcp.tool` decorators return plain functions, `mcp.run()` defaults to stdio, tools expose `output_schema` + `annotations`. In-memory MCP client roundtrip passes.
- ⏳ OPEN (runtime, not a build gap): the comparative Haiku-vs-Sonnet headline number requires a one-time `scripts/run_eval.py --record` with `ANTHROPIC_API_KEY` to record cassettes. The committed report is the key-free heuristic baseline, clearly labelled.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-06-27
Stopped at: All 5 phases built and committed. 62 passing tests. Eval report + story-led README shipped. Next optional step: run `scripts/run_eval.py --record` with a key for the live Haiku-vs-Sonnet numbers.
Resume file: None
