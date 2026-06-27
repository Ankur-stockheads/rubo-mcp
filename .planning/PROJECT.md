# UK Break Clause Analyzer (MCP)

## What This Is

A public, rigorously-evaluated MCP server that assesses whether a UK commercial-lease *tenant* break clause can actually be exercised — and proves it isn't hallucinating. It exposes single-purpose tools (extract the clause, check conditions, find citations, assess validity) that an orchestrating Claude composes, and ships a self-evaluating harness that publishes its own measured hallucination rate. Built as a credibility artifact for an Anthropic Applied AI / Forward Deployed Engineer application — the eval suite and reliability engineering are the headline, not the parsing.

## Core Value

Every asserted condition is grounded to a verbatim source span or returns `NOT_FOUND` — never invented — and the server proves with a published hallucination rate that it would rather say "ambiguous — human verify" than guess.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

(None yet — ship to validate)

### Active

<!-- Current scope. All hypotheses until shipped and validated. -->

- [ ] Synthetic dataset of 20–40 labelled UK commercial-lease break-clause **case files** with known-correct validity labels (valid / invalid / ambiguous), spanning all failure modes (missed date, defective notice, outstanding rent, vacant-possession breach, genuinely ambiguous wording)
- [ ] Scoring / eval harness (pytest) measuring extraction accuracy, citation faithfulness, hallucination rate, and calibration
- [ ] Eval report (markdown + simple chart) publishing all four metrics, hallucination rate as the headline, reported comparatively across Haiku and Sonnet
- [ ] Live + recorded-cassette eval mode — reproducible in CI with no API key, completing in under 2 minutes
- [ ] `extract_break_clause(lease_text)` — returns clause + verbatim source span
- [ ] `check_conditions(clause)` — deterministic checklist (notice timing, notice validity, rent/no-arrears, vacant possession): pass / fail / uncertain
- [ ] `find_citation(claim)` — exact verbatim supporting text or `NOT_FOUND`
- [ ] `assess_validity(...)` — orchestrated assessment + explicit calibration field + mandatory human-verify gates
- [ ] Deterministic grounding gate that rejects any cited span not found verbatim in the source
- [ ] Deterministic date-math + checklist aggregation using strict precedence (any fail → INVALID; any uncertain → AMBIGUOUS; all pass → VALID)
- [ ] Server runs via a single command and passes MCP Inspector
- [ ] Installable, publish-ready package (Python 3.12 + uv, FastMCP 3.x) with a `[project.scripts]` console entry
- [ ] Story-led README opening with a real-world missed-condition scenario, one architecture diagram, and the eval results — clone-to-running in under 2 minutes
- [ ] Decision-support disclaimer present in the README and in every tool output

### Out of Scope

<!-- Explicit boundaries with reasoning to prevent re-adding. -->

- Other lease provisions (rent review, alienation, repair, etc.) — narrow scope is the point; break clauses only
- Landlord break clauses — different machinery; the tenant break is the common, interesting case
- Real or client lease data — synthetic/public data only, for confidentiality and reproducibility
- Proprietary legal rules, prompts, or datasets — clean-room simplified ruleset only
- A covenant-compliance condition precedent — deliberately excluded to keep the ruleset simple and eval-focused
- Anything resembling a production legal engine — this is a decision-support demonstrator
- Actual PyPI publication in v1 — packaged and publish-ready, but not uploaded
- MCP sampling / client-LLM extraction — the server calls the API itself so the eval is self-contained

## Context

- Built as a portfolio / credibility artifact for an Anthropic Applied AI / Forward Deployed Engineer application. The intended reader is a technical hiring reviewer; the README and eval report are the primary surface area.
- The differentiator over a "boring parser" is reliability engineering: grounding, calibration, and a self-measured hallucination rate. The measured hallucination rate is the headline claim.
- Domain anchors (simplified, non-proprietary): UK commercial-lease break clauses turn on conditions precedent — notice timing/form, no rent arrears, and vacant possession (e.g., the classic trap of leaving contractors or chattels on site defeats vacant possession). Genuinely ambiguous wording should route to human verification rather than a confident guess.
- MCP architecture: tools each do one thing; the orchestrating Claude composes them. The server itself calls the Anthropic API for extraction/reasoning, then verifies every citation deterministically before returning it.

## Constraints

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

## Key Decisions

<!-- Decisions that constrain future work. Outcomes tracked as they're validated. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Server-side Claude API for extraction/reasoning (not deterministic-only, not MCP sampling) | Only design where the published hallucination rate measures a real LLM in the loop; keeps the eval self-contained and reproducible | — Pending |
| Deterministic grounding gate verifies every cited span verbatim, else `NOT_FOUND` | Turns a hallucination-prone LLM into a trustworthy system; this is the core reliability claim | — Pending |
| Eval runs live but records cassettes for deterministic, key-free CI replay | A reviewer reproduces it with no key in under 2 minutes; live re-measurement available anytime | — Pending |
| Report metrics comparatively across Haiku vs Sonnet | Frames reliability as a deployment/cost decision (the FDE register); cheap, since it's the same harness run twice | — Pending |
| Four conditions precedent: notice timing, notice validity, rent/no-arrears, vacant possession | Maps 1:1 to the target failure modes; simplified and non-proprietary | — Pending |
| Strict-precedence labelling (any fail → INVALID; any uncertain → AMBIGUOUS; all pass → VALID) | Conservative; defaults to human-verify under doubt — the calibration story | — Pending |
| Case-file input: lease provisions + Background Facts in one document, everything grounded | "Can it actually be exercised" needs facts, not just the clause; grounding both keeps nothing un-cited | — Pending |
| Tenant break clauses only | The common, interesting case; keeps scope deliberately narrow | — Pending |
| Installable + publish-ready, not published to PyPI in v1 | Zero external friction for a credibility repo | — Pending |
| Phase 1 = synthetic data + labels + scoring harness, before any server logic | Trustworthy ground truth must exist before the logic it scores; eval-first is the thesis | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-27 after initialization*
