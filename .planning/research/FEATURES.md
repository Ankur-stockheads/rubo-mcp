# Feature Research

**Domain:** Self-evaluating LLM decision-support MCP server (UK commercial-lease tenant break-clause assessment) + its evaluation harness
**Researched:** 2026-06-27
**Confidence:** HIGH on eval metrics and MCP conventions (anchored to ALCE, Stanford Legal-RAG-Hallucinations, abstention survey, MCP 2025-06-18 spec, FastMCP 3.x docs); MEDIUM on exact legal-tech UX norms (narrower literature)

---

## Framing: What "credible" means here

This is a **credibility artifact for an Anthropic Applied AI / FDE application**. The reviewer is a technical hiring manager, not a paying legal user. That reframes "table stakes":

- **Table stakes = what makes a reviewer trust the reliability claim.** Without these, the headline ("self-measured hallucination rate") is not believable and the project reads as a parser with marketing.
- **Differentiators = what makes this beat a boring deterministic parser** AND beat the average "I built an MCP server" portfolio piece. The reliability engineering *is* the differentiation.
- **Anti-features = scope creep and over-claiming.** In legal AI specifically, over-claiming is an active reputational hazard: the Stanford study found commercial tools (Lexis+ AI, Westlaw AI) that marketed themselves as "hallucination-free" actually hallucinate **17–33%** of the time ([Magesh et al. 2024](https://arxiv.org/abs/2405.20362)). The entire credibility of this project rests on *not* repeating that mistake — measuring honestly and refusing to over-state authority.

The single most important design consequence: **every metric must have a concrete, reproducible operational definition, and the system must be allowed to say "ambiguous — human verify" without that counting as failure.**

---

## Feature Landscape

### Table Stakes (Reviewer Expects These — Absence = Not Credible)

#### Server / tool surface

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Verbatim grounding gate** — every cited span must be found character-for-character in the source or the citation is rejected and replaced with `NOT_FOUND` | This is the core reliability mechanism. Without it the hallucination claim is unfalsifiable. The strict exact-match approach is *more* defensible than semantic matching for a credibility demo (see Differentiators / CiteGuard contrast) | MEDIUM | Normalize whitespace/quotes/casing before matching, then store **character offsets** `(start, end)` into the source so the claim is independently re-verifiable. Deterministic Python, not LLM. |
| **`NOT_FOUND` as a first-class return**, never an invented span | "Grounded or it says nothing" is the entire thesis (PROJECT.md Core Value) | LOW | Must propagate: a `find_citation` → `NOT_FOUND` should force the relevant condition to `uncertain`, not silently drop. |
| **Single-purpose tools with explicit schemas** (`extract_break_clause`, `check_conditions`, `find_citation`, `assess_validity`) | MCP convention: each tool does exactly one action; avoid `get_or_create`-style branching ([MCP best practices](https://thenewstack.io/15-best-practices-for-building-mcp-servers-in-production/), [Workato](https://docs.workato.com/en/mcp/mcp-server-tool-design.html)) | LOW | FastMCP derives input schema from type hints + docstrings. Declare **`outputSchema`** so structured results are validated client-side ([MCP 2025-06-18 tools spec](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)). |
| **Structured outputs** (`structuredContent` + Pydantic return models) | The orchestrating Claude composes these tools; typed outputs make composition reliable and let the eval parse results deterministically | LOW | FastMCP: object/Pydantic returns auto-produce `structuredContent`; also emit serialized JSON in a TextContent block for backward compat ([FastMCP tools](https://gofastmcp.com/servers/tools)). |
| **Structured, in-result errors** (`isError: true` / `ToolError`), not protocol crashes, for business-logic failures | MCP spec: tool execution errors go in the *result* so the LLM can see and react; reserve protocol-level JSON-RPC errors for unknown-tool/invalid-args ([MCP tools spec](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)) | LOW | Distinguish "I couldn't ground this" (a valid `uncertain` outcome) from "the tool failed" (an error). They are different. |
| **Explicit calibration / abstention field** on `assess_validity` (e.g. `label ∈ {VALID, INVALID, AMBIGUOUS}` + `confidence` + `human_verify_required: bool`) | A trustworthy decision-support system must express uncertainty rather than guess. Abstention is the established mechanism ([Wen et al., TACL 2025 abstention survey](https://aclanthology.org/2025.tacl-1.26.pdf)) | LOW | The label is produced by **deterministic precedence aggregation**, not the LLM's vibe (see below). |
| **Strict-precedence aggregation** (any condition fails → INVALID; any uncertain → AMBIGUOUS; all pass → VALID) | Conservative routing is the calibration story; defaulting to human-verify under doubt is the safe default for legal decision support | LOW | Pure function over the checklist. Deterministic = reproducible = auditable. |
| **Deterministic date math** for the notice-timing condition | Date arithmetic is exactly the kind of thing LLMs get subtly wrong; doing it in code is the reliability win | LOW | Keep the LLM out of arithmetic entirely; it only *extracts* the dates, code *computes*. |
| **Decision-support disclaimer in every tool output** (not just README) | Legal-tech norm and an over-claiming guardrail; "not legal advice" must travel with the data, because outputs get copy-pasted out of context | LOW | A short, fixed `disclaimer` field on every structured response. |
| **Runs via single command + passes MCP Inspector** | Baseline "it's a real MCP server" proof; reviewer will likely run Inspector | LOW | Already a stated requirement; table stakes for any MCP repo. |

#### Eval harness surface

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Labelled gold dataset (20–40 case files)** spanning every failure mode, with `valid/invalid/ambiguous` labels AND gold citation spans | You cannot measure extraction accuracy, faithfulness, or hallucination without ground truth. "Trustworthy ground truth before the logic it scores" (PROJECT.md Phase 1) | HIGH | Highest-effort, highest-value item. Must include **genuinely ambiguous** cases or the calibration metric is untestable. Synthetic/public only. Each case needs: lease+facts text, gold label, gold condition outcomes, gold spans. |
| **Extraction accuracy** vs gold labels | Baseline competence: did it find the right clause / dates / facts | LOW–MEDIUM | Field-level exact/normalized match for structured fields; span-overlap (offset IoU or exact-span match) for extracted spans. Report per-field. |
| **Citation faithfulness** metric | The literature-standard way to prove citations actually support claims ([ALCE](https://github.com/princeton-nlp/ALCE), [Attribution survey](https://arxiv.org/pdf/2508.15396)) | MEDIUM | See "Eval metric definitions" — for this system, faithfulness = (a) span is verbatim-present AND (b) span actually supports the asserted condition. |
| **Hallucination rate** as the headline metric | The entire pitch. Must be operationally defined, not asserted | MEDIUM | See definition below. Defensible def for this system = **ungrounded/unsupported assertion rate**. |
| **Calibration metric** for the 3-way label | Proves the "would rather say ambiguous than guess" claim is real | MEDIUM | See definition below — selective-prediction (coverage/risk) + ambiguity routing (abstention precision/recall) + a confusion matrix. |
| **Eval report (markdown + chart)** with all four metrics, hallucination rate as headline, **Haiku vs Sonnet** comparison | A reviewer expects to *see the numbers*, per-model, with caught examples | LOW–MEDIUM | See "Eval report contents." |
| **Recorded-cassette replay** — reproducible in CI, no API key, <2 min | A reviewer must reproduce it trivially; live re-measurement available on demand | MEDIUM | Record real API responses once; replay deterministically. This is what makes the published number *checkable*, which is what makes it credible. |

---

### Differentiators (What Beats a Boring Parser AND an Average Portfolio Repo)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Published self-measured hallucination rate as the headline claim** | Almost no portfolio MCP server *measures itself*. This reframes the project from "I built a tool" to "I built a tool and proved its reliability envelope" — exactly the FDE register | MEDIUM | The differentiator is the *honesty + reproducibility*, not a low number. A measured 4% with a cassette anyone can re-run beats a claimed 0%. |
| **Strict verbatim exact-match grounding (vs semantic/LLM-judge attribution)** | Stronger, falsifiable guarantee. CiteGuard and ALCE rely on NLI/retrieval/LLM-judge *semantic* alignment — powerful but soft and itself fallible (LLM-as-judge recall as low as ~16–17% in CiteGuard's own data, [arXiv 2510.17853](https://arxiv.org/html/2510.17853v1)). A deterministic exact-match gate is a *different, harder* promise: "the words are literally in the document" | MEDIUM | Frame this explicitly in the README as a deliberate design choice with a tradeoff (catches fabrication, not paraphrase-drift — so layer a support check on top). |
| **Calibration framed as a deployment/cost decision (Haiku vs Sonnet)** | Turns reliability into the language hiring teams use: "Haiku is X% cheaper but abstains Y% more / mis-routes Z% more." That's the FDE value-prop register | LOW (same harness, run twice) | Cheap to produce, disproportionately credible. Report cost/latency alongside reliability. |
| **Correct routing of genuinely-ambiguous cases** (not just abstaining a lot) | The sophisticated calibration story: a system that abstains on *everything* is useless; a system that abstains on the *right* cases is trustworthy. Measured via abstention precision/recall ([abstention survey](https://aclanthology.org/2025.tacl-1.26.pdf)) | MEDIUM | Requires the dataset to label *which* cases are genuinely ambiguous. This is the most defensible "we beat a parser" claim — a parser can't know it's unsure. |
| **Examples of caught hallucinations in the report** | Showing the gate rejecting a fabricated/misgrounded span is far more persuasive than an aggregate number | LOW | Curate 2–3 concrete before/after examples (LLM proposed span X → gate rejected → `NOT_FOUND` → routed to AMBIGUOUS). |
| **Case-file input model (provisions + Background Facts, both grounded)** | "Can it *actually be exercised*" requires facts, not just the clause text (e.g. the vacant-possession trap of chattels left on site). Grounding facts too means nothing is un-cited | MEDIUM | A genuine domain insight that distinguishes this from naive clause extraction. |
| **Confusion matrix across valid/invalid/ambiguous + per-condition breakdown** | Shows *where* errors concentrate (e.g. "vacant possession is where it's weakest"), which is what an engineer actually wants to see | LOW | Differentiator because most demos report a single accuracy number; this shows diagnostic depth. |

---

### Anti-Features (Tempting, but Build None of These)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Claiming "hallucination-free" / "100% accurate" / legal authority** | Sounds impressive; mirrors commercial vendor marketing | This is the *exact* failure the Stanford study exposed (17–33% real rate behind "hallucination-free" claims, [Magesh et al.](https://arxiv.org/abs/2405.20362)). For an Anthropic reviewer, over-claiming is disqualifying — it signals you don't understand calibration | Publish the *measured* rate with its envelope and limitations. Honesty is the flex. |
| **General-purpose legal analysis** (rent review, alienation, repair, dilapidations, landlord breaks) | "Make it do more" | Destroys the narrow, deep, defensible scope; multiplies dataset/labelling cost; dilutes the eval story. Already Out of Scope in PROJECT.md | Tenant break clauses only. Narrowness *is* the credibility. |
| **LLM-generated final validity verdict** (letting the model output VALID/INVALID directly) | Simpler; "just ask the model" | The reliability claim collapses — the verdict would be ungrounded and non-reproducible. The whole point is deterministic aggregation over grounded conditions | LLM extracts + reasons per-condition; **deterministic code** computes the final label via strict precedence. |
| **Semantic / fuzzy citation matching as the primary gate** | Catches paraphrases; higher "recall" of support | Re-introduces a fallible, non-deterministic, non-reproducible step into the *core guarantee*; an LLM judge can itself hallucinate support. Undermines the falsifiable promise | Keep exact-match as the hard gate. Optionally add a *secondary* support check (does the verbatim span actually entail the condition) and report it separately. |
| **Confidence as a raw LLM-emitted probability** (model self-reports "95% sure") | Easy uncertainty signal | LLM verbalized/token confidences are poorly calibrated and trivially gamed; a reviewer will not trust them | Derive the label from the deterministic checklist; report calibration via coverage/risk on *outcomes*, not the model's self-assessment. |
| **Real / client lease data** | More realistic | Confidentiality + non-reproducibility; a reviewer can't re-run it; ethical/legal exposure | Synthetic, public, hand-labelled corpus (already an Out-of-Scope constraint). |
| **Retrieval over a large legal corpus / case-law RAG** | "Real legal research tools do retrieval" | Massively expands scope and failure surface; the input here is a single self-contained case file — retrieval is unnecessary and would import the exact hallucination problems the project avoids | Single-document grounding. No external corpus. |
| **PyPI publication / auth / multi-user / web UI / persistence** | "Make it production-ready" | Pure scope creep for a credibility repo; zero marginal credibility, real maintenance cost. Already Out of Scope | Packaged + publish-ready, run locally, MCP Inspector + cassette CI. Stop there. |
| **Covenant-compliance condition precedent (full repairing/decoration checks)** | More legally complete | Explodes ruleset complexity; deliberately excluded to keep the eval focused | Four conditions only (notice timing, notice validity, no-arrears, vacant possession). |
| **Live API as the only eval mode** | "It's the real thing" | Non-reproducible, costs money, needs a key, can exceed 2 min, breaks CI | Live *and* recorded-cassette; cassette is the default reproducible path. |

---

## Eval Metric Definitions (operational, reproducible — the quality gate)

These four are the deliverable. Each is defined to be **computable in pytest against the gold dataset**, with no human-in-the-loop scoring at run time.

### 1. Extraction accuracy
**What it scores:** Did the system pull the correct structured facts (break date, notice deadline, rent status, possession facts) and the correct clause text from the case file?
**Operational definition:**
- **Field-level accuracy** = (# fields matching gold after normalization) / (# gold fields), reported per field type and aggregated. Normalization = trim/whitespace/case/date-format canonicalization.
- **Span localization** = for each extracted span, exact-span match against gold OR character-offset overlap (IoU ≥ threshold, e.g. 0.9). Report exact-match % as the strict number.
**Why this def:** Mirrors standard QA exact-match / span metrics ([faithfulness review, arXiv 2501.00269](https://arxiv.org/pdf/2501.00269)); field-level is interpretable and points to *which* extraction is weak.
**Dependencies:** gold dataset with per-field labels + gold spans.

### 2. Citation faithfulness
**What it scores:** When the system cites a span as supporting a condition outcome, is that citation *faithful* — i.e. genuinely present in and supportive of the source?
**Operational definition (two-part, both must hold):**
- **(a) Verbatim presence** (deterministic, the hard gate): the cited span is found character-for-character (post-normalization) in the source. Pass/fail per citation. This is computed by the grounding gate itself.
- **(b) Support / correct attribution**: the verbatim span actually supports the condition it's cited for. Scored against gold (the dataset records, per condition, which span(s) are the correct support). Report as **citation precision** (cited spans that are correct support / all cited spans) and **citation recall** (conditions whose required support was correctly cited / all conditions needing support) — the ALCE formulation ([Gao et al. 2023, ALCE](https://ar5iv.labs.arxiv.org/html/2305.14627); [GitHub](https://github.com/princeton-nlp/ALCE)).
**"Faithful citation" defined:** a citation is faithful iff the cited text is *actually in the source* (a) AND *actually supports the proposition it is attached to* (b). ALCE/AIS operationalize (b) via NLI entailment; this project can score (b) against gold labels (cleaner, no NLI model dependency) and report (a) deterministically.
**Why this def:** Directly the citation-recall/precision + AIS lineage that current LLM eval practice uses for attribution ([Attribution survey, arXiv 2508.15396](https://arxiv.org/pdf/2508.15396)).
**Dependencies:** gold support-span labels per condition; the grounding gate (for (a)).

### 3. Hallucination rate (HEADLINE)
**What it scores:** How often does the system make an assertion that is not faithfully grounded?
**Operational definition for THIS system — ungrounded/unsupported assertion rate:**
> hallucination rate = (# asserted condition-outcomes whose supporting citation fails verbatim presence OR fails to actually support the outcome) / (# asserted condition-outcomes)

i.e. an assertion is a **hallucination iff it is *ungrounded* (cited span not verbatim in source) OR *misgrounded* (verbatim span doesn't support the claimed outcome)**. This mirrors the Stanford Legal-RAG framework, where a response is a hallucination if it is **incorrect or misgrounded** — citations that *look* authoritative but don't support the proposition are the dangerous, subtle case ([Magesh et al. 2024](https://arxiv.org/abs/2405.20362); reproduced framing in [Stanford HAI summary](https://law.stanford.edu/publications/hallucination-free-assessing-the-reliability-of-leading-ai-legal-research-tools/)).
**Crucial design point:** an *honest* `NOT_FOUND` / `uncertain` that routes to AMBIGUOUS is **NOT** a hallucination — abstention is the opposite of hallucination. Only *confident-but-ungrounded* assertions count. This is what lets the system drive its hallucination rate toward zero by abstaining, and is the whole calibration story.
**Report it as a fraction with the denominator stated**, per model, with a cassette so it's re-derivable.
**Why defensible:** "supported claims / total claims" groundedness rate is the established inverse-of-hallucination metric for RAG ([groundedness/hallucination practice](https://www.blockchain-council.org/ai/evaluating-rag-systems-metrics-groundedness-hallucination-reduction/)); tying it to the deterministic gate makes it falsifiable.
**Dependencies:** grounding gate + citation-support scoring (metric 2).

### 4. Calibration (3-way valid/invalid/ambiguous)
**What it scores:** Does the system express uncertainty correctly — abstaining (AMBIGUOUS / human-verify) on the cases it *should*, and committing on the cases it *can*?
**Operational definition (three complementary numbers):**
- **Selective prediction — coverage & risk** ([SelectLLM, NeurIPS 2025](https://openreview.net/forum?id=JJPAy8mvrQ)):
  - **Coverage** = fraction of cases where the system commits (label ∈ {VALID, INVALID}, i.e. does *not* abstain).
  - **Selective risk** = error rate *among committed cases* (wrong VALID/INVALID / committed). Trustworthy = low selective risk even if coverage drops. Optionally report the **risk–coverage curve / AURC** if a confidence threshold is tunable.
- **Ambiguity routing — abstention precision/recall** ([abstention survey, TACL 2025](https://aclanthology.org/2025.tacl-1.26.pdf)):
  - **Abstention precision** = of cases labelled AMBIGUOUS, how many are *genuinely* ambiguous (per gold).
  - **Abstention recall** = of *genuinely* ambiguous cases, how many were correctly routed to AMBIGUOUS.
  - Together these prove it routes the *right* cases — not that it just abstains a lot (the over-abstention failure mode).
- **3-way confusion matrix** (predicted × gold over VALID/INVALID/AMBIGUOUS) as the at-a-glance calibration picture. The dangerous cell is *predicted VALID, gold INVALID* (a false green light); a well-calibrated system pushes errors into the AMBIGUOUS row instead.
**Why this def:** combines the two standard framings (selective prediction coverage/risk + abstention precision/recall) precisely for a 3-class label where AMBIGUOUS *is* the abstention class. Directly answers "does it correctly route genuinely-ambiguous cases."
**Dependencies:** dataset must label genuine ambiguity; strict-precedence aggregator produces the label.

---

## Eval Report Contents (what a reviewer expects to see)

A reviewer opening the report should find, in order:

1. **Headline hallucination rate**, per model, with the denominator and definition stated inline (e.g. "ungrounded/misgrounded assertions / total asserted conditions"). One number, prominently, then immediately defined — pre-empting the "defined how?" skepticism the Stanford paper trains reviewers to have.
2. **Per-metric table**: extraction accuracy (overall + per field), citation precision/recall, hallucination rate, calibration (coverage, selective risk, abstention precision/recall) — **columns = Haiku vs Sonnet**.
3. **3-way confusion matrix** (valid/invalid/ambiguous), per model, highlighting false-confident cells.
4. **Per-condition breakdown** (notice timing / notice validity / no-arrears / vacant possession) — shows *where* the system is weak.
5. **Caught-hallucination examples** (2–3): LLM-proposed span → gate verdict → routed outcome. Concrete, persuasive.
6. **Cost/latency per model** beside reliability — frames the Haiku-vs-Sonnet tradeoff as a deployment decision.
7. **Reproducibility footer**: exact command to re-run from cassette (<2 min, no key), dataset size, date, model versions/IDs, and **stated limitations** (synthetic data, simplified ruleset, narrow scope, exact-match catches fabrication not paraphrase). Limitations stated up-front are a credibility *gain* in this domain.

A simple bar chart (hallucination rate Haiku vs Sonnet, and/or coverage-vs-risk) satisfies the "simple chart" requirement; nothing fancier is needed.

---

## MCP Tool Design Conventions (applied to this server)

Anchored to the [MCP 2025-06-18 tools spec](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) and [FastMCP 3.x](https://gofastmcp.com/servers/tools):

- **One action per tool, no branching outputs.** `extract_break_clause`, `check_conditions`, `find_citation`, `assess_validity` each do exactly one thing ([New Stack 15 best practices](https://thenewstack.io/15-best-practices-for-building-mcp-servers-in-production/)). `assess_validity` *composes* the others (orchestration), it doesn't re-implement them.
- **Declare `outputSchema` / return Pydantic models** → FastMCP emits `structuredContent` (validated client-side) plus a JSON TextContent block for compat.
- **Errors via `isError`/`ToolError` in the result**, not protocol crashes, for business logic; reserve JSON-RPC protocol errors for unknown-tool/invalid-args. Keep messages actionable with machine-readable codes.
- **`NOT_FOUND` and `uncertain` are normal results, not errors.** Critical distinction: failing to ground something is a *valid, expected* outcome of a reliability-first tool.
- **Tool annotations**: mark all four `readOnlyHint: true` (pure analysis, no side effects) and `openWorldHint: false` (closed-world: only the provided document). Note the spec says clients treat annotations as untrusted hints — they're advisory, not security.
- **Disclaimer field on every structured output** — satisfies the "disclaimer in every tool output" requirement and the human-in-the-loop guidance the spec flags for trust & safety (there SHOULD be a human able to deny/verify).
- **Clear docstrings** → FastMCP turns them into tool/parameter descriptions the orchestrating model reads to compose correctly.

---

## Feature Dependencies

```
Gold labelled dataset (cases + labels + gold spans + ambiguity flags)
    └──required by──> Extraction accuracy
    └──required by──> Citation faithfulness (support scoring)
    └──required by──> Calibration (needs genuine-ambiguity labels)
    └──required by──> Hallucination rate (needs gold support)

Verbatim grounding gate (deterministic exact-match + offsets)
    └──required by──> find_citation / NOT_FOUND behavior
    └──required by──> Citation faithfulness part (a)
    └──required by──> Hallucination rate (ungrounded detection)

Per-condition LLM extraction+reasoning  ──feeds──> Strict-precedence aggregator
Strict-precedence aggregator  ──produces──> VALID/INVALID/AMBIGUOUS label
    └──required by──> Calibration metric
    └──required by──> assess_validity output

Recorded cassettes  ──enable──> reproducible CI eval (<2 min, no key)
    └──enables──> credible published hallucination rate

Haiku-vs-Sonnet comparison ──enhances──> eval report (run same harness twice)
```

### Dependency Notes
- **Everything downstream depends on the gold dataset.** It is the long pole and the thesis ("trustworthy ground truth before the logic it scores"). Build/label it first (PROJECT.md Phase 1).
- **Hallucination rate depends on BOTH the grounding gate (part a) AND citation-support scoring (part b).** Don't ship the headline number until both halves exist, or it only measures fabrication and misses misgrounding — the subtler, more dangerous case.
- **Calibration depends on the dataset carrying explicit "genuinely ambiguous" labels.** Without them, abstention precision/recall is uncomputable and the calibration story is just an unverified coverage number.
- **Cassettes depend on a stable tool/output schema** — freeze the output shapes before recording, or cassettes invalidate on every refactor.

---

## MVP Definition

### Launch With (v1)
- [ ] Gold dataset (20–40 cases, all failure modes incl. genuine ambiguity, with labels + gold spans) — *everything depends on it*
- [ ] Verbatim grounding gate with offsets + `NOT_FOUND` — *the core guarantee*
- [ ] Four single-purpose tools with output schemas, structured errors, disclaimer field — *the server*
- [ ] Strict-precedence aggregator → VALID/INVALID/AMBIGUOUS + human-verify gate — *the calibration mechanism*
- [ ] All four metrics with the operational definitions above, in pytest — *the proof*
- [ ] Eval report (markdown + chart), hallucination rate headline, Haiku vs Sonnet, confusion matrix, caught examples, limitations footer — *the primary surface*
- [ ] Cassette replay: CI-reproducible, no key, <2 min — *what makes the number checkable*
- [ ] Story-led README + architecture diagram + results; passes MCP Inspector; single-command run

### Add After Validation (v1.x)
- [ ] Secondary semantic **support** check (NLI/entailment) reported *separately* from the exact-match gate — *trigger: reviewers ask about paraphrase-drift*
- [ ] Risk–coverage curve / AURC if a tunable confidence threshold is added — *trigger: deeper calibration questions*
- [ ] More cases / additional failure-mode coverage — *trigger: a condition shows weak per-condition numbers*

### Future Consideration (v2+)
- [ ] Additional models in the comparison (e.g. Opus tier) — *cheap, same harness; defer until v1 lands*
- [ ] Actual PyPI publication — *explicitly deferred; zero credibility marginal value now*

---

## Feature Prioritization Matrix

| Feature | Reviewer Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Gold labelled dataset (with ambiguity + gold spans) | HIGH | HIGH | P1 |
| Verbatim grounding gate + `NOT_FOUND` + offsets | HIGH | MEDIUM | P1 |
| Hallucination rate (ungrounded/misgrounded), defined + headline | HIGH | MEDIUM | P1 |
| Strict-precedence 3-way label + human-verify gate | HIGH | LOW | P1 |
| Calibration (coverage/risk + abstention precision/recall + confusion) | HIGH | MEDIUM | P1 |
| Citation faithfulness (verbatim + support precision/recall) | HIGH | MEDIUM | P1 |
| Extraction accuracy (field + span) | MEDIUM | LOW–MEDIUM | P1 |
| Cassette replay (<2 min, no key) | HIGH | MEDIUM | P1 |
| Eval report w/ Haiku-vs-Sonnet + caught examples + limitations | HIGH | LOW–MEDIUM | P1 |
| Single-purpose tools, output schemas, structured errors, disclaimer | MEDIUM | LOW | P1 |
| Tool annotations (readOnlyHint / openWorldHint:false) | LOW | LOW | P2 |
| Secondary semantic support (NLI) check, reported separately | MEDIUM | MEDIUM | P2 |
| Risk–coverage curve / AURC | LOW–MEDIUM | LOW | P2 |
| Additional models in comparison | LOW | LOW | P3 |
| PyPI publication | LOW | LOW | P3 (deferred) |

---

## Competitor / Reference Feature Analysis

| Aspect | Commercial legal AI (Lexis+ AI, Westlaw) | Citation-eval research (ALCE / CiteGuard) | Our Approach |
|--------|------------------------------------------|-------------------------------------------|--------------|
| Hallucination claim | Marketed "hallucination-free"; actually 17–33% ([Magesh 2024](https://arxiv.org/abs/2405.20362)) | N/A (they *measure*, don't ship product) | **Publish the measured rate honestly**, with cassette to re-verify |
| Citation verification | RAG + retrieval; misgrounded citations slip through subtly | NLI entailment / retrieval / LLM-judge — *semantic*, soft, itself fallible (CiteGuard LLM-judge recall ~16–17%) | **Deterministic exact-match gate** (hard guarantee) + optional separate support check |
| Uncertainty handling | Often answers confidently regardless | Selective prediction, abstention metrics | **Strict-precedence → AMBIGUOUS/human-verify**, measured via abstention precision/recall |
| Scope | Broad legal research | Broad attribution benchmarks | **Narrow**: tenant break clause, 4 conditions — narrowness *is* the credibility |
| Reproducibility | Closed, unverifiable | Open benchmarks | **Cassette-replayable in CI, no key, <2 min** |

---

## Sources

- [Magesh et al., "Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools" (Stanford, 2024/2025)](https://arxiv.org/abs/2405.20362) — correctness+groundedness hallucination framework; 17–33% real rates behind "hallucination-free" marketing — HIGH
- [Stanford Law publication page for the above](https://law.stanford.edu/publications/hallucination-free-assessing-the-reliability-of-leading-ai-legal-research-tools/) — HIGH
- [Gao et al., ALCE: "Enabling LLMs to Generate Text with Citations" (EMNLP 2023)](https://ar5iv.labs.arxiv.org/html/2305.14627) + [GitHub](https://github.com/princeton-nlp/ALCE) — citation recall/precision via NLI entailment — HIGH
- [Attribution/Citation/Quotation survey (arXiv 2508.15396)](https://arxiv.org/pdf/2508.15396) — citation recall/precision, AIS, quotation faithfulness, "faithful citation" definition — HIGH
- [Review of faithfulness metrics for hallucination (arXiv 2501.00269)](https://arxiv.org/pdf/2501.00269) — exact-match / NLI faithfulness methodologies — MEDIUM
- [CiteGuard: Faithful Citation Attribution via Retrieval-Augmented Validation (arXiv 2510.17853)](https://arxiv.org/html/2510.17853v1) — semantic vs exact-span contrast; LLM-judge recall limits — MEDIUM
- [Wen et al., "Know Your Limits: A Survey of Abstention in LLMs" (TACL 2025)](https://aclanthology.org/2025.tacl-1.26.pdf) — abstention, appropriate vs over-abstention, abstention precision/recall — HIGH
- [SelectLLM: "Calibrating LLMs for Selective Prediction: Balancing Coverage and Risk" (NeurIPS 2025)](https://openreview.net/forum?id=JJPAy8mvrQ) — coverage, selective risk, AURC, ECE — HIGH
- [RAG groundedness / hallucination-rate measurement practice](https://www.blockchain-council.org/ai/evaluating-rag-systems-metrics-groundedness-hallucination-reduction/) — groundedness rate = supported/total claims — MEDIUM
- [MCP 2025-06-18 Tools specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) — isError vs protocol errors, outputSchema/structuredContent, annotations, human-in-the-loop — HIGH
- [FastMCP 3.x Tools docs](https://gofastmcp.com/servers/tools) — tool definition, structured output, ToolError, schema derivation — HIGH
- [15 Best Practices for Building MCP Servers in Production (The New Stack)](https://thenewstack.io/15-best-practices-for-building-mcp-servers-in-production/) — single-purpose tools, structured errors — MEDIUM
- [Workato MCP server tool design](https://docs.workato.com/en/mcp/mcp-server-tool-design.html) — single-purpose / no-branching tool guidance — MEDIUM

---
*Feature research for: self-evaluating UK break-clause assessment MCP server + eval harness*
*Researched: 2026-06-27*
