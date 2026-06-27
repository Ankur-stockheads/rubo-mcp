"""Run a system over the dataset and score it.

Model-agnostic: the same harness scores the gold oracle (Phase 1), and later the
Haiku- and Sonnet-backed systems (Phase 3/5) by swapping the `System` passed in.
"""

from __future__ import annotations

from break_clause_analyzer.models import CaseFile
from eval.caseio import load_all_cases
from eval.metrics import CaseRun, MetricsReport, score_all
from eval.system import System


def run_system(system: System, cases: list[CaseFile]) -> list[CaseRun]:
    runs: list[CaseRun] = []
    for case in cases:
        clause = system.extract(case.source)
        assessment = system.assess(case.source)
        runs.append(CaseRun(case=case, clause=clause, assessment=assessment))
    return runs


def evaluate(
    system: System,
    cases: list[CaseFile] | None = None,
    split: str | None = None,
) -> MetricsReport:
    """Evaluate a system; optionally restrict to a dataset split ('dev'/'eval')."""
    cases = cases if cases is not None else load_all_cases()
    if split is not None:
        cases = [c for c in cases if c.split == split]
    runs = run_system(system, cases)
    return score_all(runs, model_label=system.name)
