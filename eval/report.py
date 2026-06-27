"""Render the eval report: a markdown document + a zero-dependency SVG chart.

The headline is the hallucination rate, stated with its definition and denominator.
The report also shows the per-model comparison, a 3-way confusion matrix, where
errors concentrate, a couple of caught-hallucination examples, and an explicit
limitations + reproducibility footer.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from break_clause_analyzer.models import CONDITION_LABELS, DISCLAIMER, ConditionId, Verdict
from eval.metrics import MetricsReport

_VERDICTS = [Verdict.VALID, Verdict.INVALID, Verdict.AMBIGUOUS]


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def svg_hallucination_chart(reports: list[MetricsReport]) -> str:
    """A tiny hand-written horizontal bar chart — no matplotlib, byte-reproducible."""
    width, row_h, pad_l, pad_t = 560, 46, 180, 40
    height = pad_t + row_h * len(reports) + 30
    bar_max = width - pad_l - 60
    bars = []
    for i, r in enumerate(reports):
        y = pad_t + i * row_h
        rate = r.hallucination.rate
        bar_w = max(2, int(bar_max * rate))
        bars.append(
            f'<text x="{pad_l - 12}" y="{y + 20}" text-anchor="end" '
            f'font-size="14" fill="#0b1f33">{r.model_label}</text>'
            f'<rect x="{pad_l}" y="{y + 6}" width="{bar_w}" height="24" rx="3" fill="#c0392b"/>'
            f'<text x="{pad_l + bar_w + 8}" y="{y + 23}" font-size="13" '
            f'fill="#0b1f33">{_pct(rate)} ({r.hallucination.hallucinated}/{r.hallucination.total_assertions})</text>'
        )
    axis = (
        f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t + row_h * len(reports)}" '
        f'stroke="#9aa6b2" stroke-width="1"/>'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="system-ui,Segoe UI,Helvetica,Arial,sans-serif">'
        f'<text x="20" y="24" font-size="16" font-weight="600" fill="#0b1f33">'
        f'Hallucination rate (lower is better)</text>'
        f"{axis}{''.join(bars)}</svg>"
    )


def _comparison_table(reports: list[MetricsReport]) -> str:
    rows = [
        ("Hallucination rate ⬇", lambda r: f"**{_pct(r.hallucination.rate)}**"),
        ("  — ungrounded / misgrounded / overconfident", _htype_breakdown),
        ("  — case-level", lambda r: _pct(r.hallucination.case_level_rate)),
        ("Extraction accuracy ⬆", lambda r: _pct(r.extraction.accuracy)),
        ("Citation verbatim-rate ⬆", lambda r: _pct(r.faithfulness.verbatim_rate)),
        ("Citation support F1 ⬆", lambda r: _pct(r.faithfulness.support_f1)),
        ("Overall verdict accuracy ⬆", lambda r: _pct(r.calibration.overall_accuracy)),
        ("Coverage (answered) ⬆", lambda r: _pct(r.calibration.coverage)),
        ("Accuracy on answered ⬆", lambda r: _pct(r.calibration.accuracy_on_answered)),
        ("Abstention precision ⬆", lambda r: _pct(r.calibration.abstention_precision)),
        ("Abstention recall ⬆", lambda r: _pct(r.calibration.abstention_recall)),
    ]
    header = "| Metric | " + " | ".join(r.model_label for r in reports) + " |"
    sep = "|" + "---|" * (len(reports) + 1)
    lines = [header, sep]
    for label, fn in rows:
        lines.append("| " + label + " | " + " | ".join(fn(r) for r in reports) + " |")
    return "\n".join(lines)


def _htype_breakdown(r: MetricsReport) -> str:
    bt = r.hallucination.by_type
    return f"{bt.get('ungrounded', 0)} / {bt.get('misgrounded', 0)} / {bt.get('overconfident', 0)}"


def _confusion(r: MetricsReport) -> str:
    head = "| gold ↓ \\ system → | VALID | INVALID | AMBIGUOUS |"
    sep = "|---|---|---|---|"
    lines = [f"**{r.model_label}**", "", head, sep]
    for g in _VERDICTS:
        cells = " | ".join(str(r.calibration.confusion[g.value][s.value]) for s in _VERDICTS)
        lines.append(f"| {g.value} | {cells} |")
    return "\n".join(lines)


def _per_condition(r: MetricsReport) -> str:
    counter: Counter = Counter()
    for rec in r.hallucination.records:
        if rec.is_hallucination and rec.kind == "condition" and rec.condition:
            counter[rec.condition] += 1
    if not counter:
        return f"_{r.model_label}: no condition-level hallucinations._"
    lines = [f"**{r.model_label}** — hallucinations by condition:"]
    for cid in ConditionId:
        n = counter.get(cid.value, 0)
        if n:
            lines.append(f"- {CONDITION_LABELS[cid]}: {n}")
    return "\n".join(lines)


def _examples(r: MetricsReport, limit: int = 3) -> str:
    halluc = [rec for rec in r.hallucination.records if rec.is_hallucination and rec.kind == "condition"]
    if not halluc:
        return "_None — the system made no condition-level hallucinations._"
    lines = []
    for rec in halluc[:limit]:
        cond = CONDITION_LABELS[ConditionId(rec.condition)] if rec.condition else "clause"
        lines.append(
            f"- **{rec.case_id} · {cond}** — system asserted `{rec.asserted}`, "
            f"gold is `{rec.gold}` → caught as **{rec.htype}**."
        )
    return "\n".join(lines)


def render_markdown(reports: list[MetricsReport], mode: str, provenance: str) -> str:
    primary = reports[0]
    n = primary.n_cases
    parts: list[str] = []
    parts.append("# Evaluation Report — UK Break Clause Analyzer\n")
    parts.append(f"> {DISCLAIMER}\n")
    parts.append(f"**Run mode:** {mode}  \n**Cases (eval split):** {n}  \n**Provenance:** {provenance}\n")

    parts.append("## Headline — measured hallucination rate\n")
    head_bits = ", ".join(f"**{r.model_label}: {_pct(r.hallucination.rate)}**" for r in reports)
    parts.append(
        f"{head_bits}.\n\n"
        "A hallucination is any *asserted* condition or clause that is **ungrounded** "
        "(no verbatim support), **misgrounded** (real citation, wrong conclusion), or "
        "**overconfident** (a definite answer on a genuinely-ambiguous condition). "
        "Honest abstentions (`uncertain` / NOT_FOUND) are never counted. "
        "Denominator = total assertions made. See "
        "[`docs/METHODOLOGY.md`](../docs/METHODOLOGY.md) for the pre-registered definitions.\n"
    )
    parts.append("![Hallucination rate](hallucination_rate.svg)\n")

    parts.append("## All four metrics\n")
    parts.append(_comparison_table(reports) + "\n")

    parts.append("## Verdict confusion matrix\n")
    parts.append("\n\n".join(_confusion(r) for r in reports) + "\n")

    parts.append("## Where errors concentrate\n")
    parts.append("\n\n".join(_per_condition(r) for r in reports) + "\n")

    parts.append("## Caught-hallucination examples\n")
    parts.append("\n\n".join(f"**{r.model_label}**\n\n{_examples(r)}" for r in reports) + "\n")

    parts.append("## Limitations & reproducibility\n")
    parts.append(
        "- Synthetic, non-proprietary dataset on a deliberately simplified four-condition "
        "ruleset — not a measure of real-world legal accuracy.\n"
        "- Metrics are computed against gold labels (no LLM judge), so the scorer is "
        "deterministic and auditable; it was validated against a gold oracle and "
        "deliberately-broken systems (`tests/test_harness.py`).\n"
        "- Reproducibility comes from recorded cassettes, not from `temperature=0` (which "
        "the API does not guarantee). Re-run `scripts/run_eval.py` to regenerate.\n"
    )
    return "\n".join(parts)


def write_report(
    reports: list[MetricsReport], mode: str, provenance: str, out_dir: str | Path = "report"
) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "hallucination_rate.svg").write_text(svg_hallucination_chart(reports), encoding="utf-8")
    md_path = out / "report.md"
    md_path.write_text(render_markdown(reports, mode, provenance), encoding="utf-8")
    return md_path
