# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-27)

**Core value:** Every asserted condition is grounded to a verbatim source span or returns NOT_FOUND — never invented — and the server proves with a published hallucination rate that it would rather say "ambiguous — human verify" than guess.
**Current focus:** Phase 1 — Dataset, Scoring Harness & Cassette Infrastructure

## Current Position

Phase: 1 of 5 (Dataset, Scoring Harness & Cassette Infrastructure)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-06-27 — Roadmap created (5 phases, eval-first horizontal layers, 32/32 requirements mapped)

Progress: [░░░░░░░░░░] 0%

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

- [Phase 3]: Spot-check `messages.parse()` Pydantic helper form against `anthropic` 0.112.0 docs at phase start (MEDIUM confidence on `output_config.format` vs `output_format` migration).
- [Phase 4]: Verify exact FastMCP 3.x `@mcp.tool` decorator and `mcp.run()` signatures against gofastmcp.com, and MCP Inspector 0.22.x flags via `--help`, at phase start — do not rely on training-data recall.

## Deferred Items

Items acknowledged and carried forward from previous milestone close:

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-06-27
Stopped at: Roadmap and STATE created; REQUIREMENTS.md traceability populated (32/32 mapped).
Resume file: None
