"""The report renderer produces well-formed markdown + valid SVG."""

from __future__ import annotations

import xml.dom.minidom as minidom

from eval.caseio import load_all_cases
from eval.harness import run_system
from eval.metrics import score_all
from eval.report import render_markdown, svg_hallucination_chart
from eval.system import OracleSystem


def _report():
    cases = load_all_cases()
    return score_all(run_system(OracleSystem(cases), cases), "oracle")


def test_markdown_has_required_sections():
    md = render_markdown([_report()], "test-mode", "test-provenance")
    for needle in [
        "measured hallucination rate",
        "All four metrics",
        "confusion matrix",
        "Limitations & reproducibility",
        "NOT LEGAL ADVICE",
    ]:
        assert needle in md, f"report missing section: {needle}"


def test_svg_is_valid_xml():
    minidom.parseString(svg_hallucination_chart([_report()]))  # raises if malformed
