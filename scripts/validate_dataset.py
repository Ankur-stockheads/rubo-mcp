"""Validate the synthetic dataset: verbatim gold spans + label coherence + coverage.

Run: `uv run python scripts/validate_dataset.py`
Exits non-zero if any case fails verbatim validation. Prints a coverage summary
so we can confirm every failure mode and the ambiguous/adversarial cases exist.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

# Make the project root importable so `eval` (top-level harness pkg) resolves
# regardless of how this script is invoked.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from break_clause_analyzer.core.aggregate import aggregate_statuses  # noqa: E402
from break_clause_analyzer.models import CaseFile, Status, Verdict  # noqa: E402
from eval.caseio import CaseValidationError, load_all_cases  # noqa: E402


def expected_verdict(case: CaseFile) -> Verdict:
    """Strict-precedence verdict implied by the gold conditions (single source of truth)."""
    return aggregate_statuses([gc.status for gc in case.gold_conditions])


def main() -> int:
    try:
        cases = load_all_cases()
    except CaseValidationError as exc:
        print(f"DATASET INVALID:\n{exc}")
        return 1

    n = len(cases)
    labels = Counter(c.label.value for c in cases)
    splits = Counter(c.split for c in cases)
    modes = Counter(m for c in cases for m in c.failure_modes)
    ambiguous = [c.id for c in cases if c.ambiguous]
    adversarial = [c.id for c in cases if c.adversarial]

    print(f"PASS — {n} cases load and every gold span is verbatim.\n")
    print(f"Labels:        {dict(labels)}")
    print(f"Splits:        {dict(splits)}")
    print(f"Failure modes: {dict(modes)}")
    print(f"Ambiguous:     {len(ambiguous)} -> {ambiguous}")
    print(f"Adversarial:   {len(adversarial)} -> {adversarial}")

    # Coverage assertions (the dataset must exercise every failure mode).
    required_modes = {
        "notice_timing",
        "notice_validity",
        "outstanding_rent",
        "vacant_possession",
    }
    problems = []
    if n < 20:
        problems.append(f"need >=20 cases, have {n}")
    missing_modes = required_modes - set(modes)
    if missing_modes:
        problems.append(f"missing failure modes: {sorted(missing_modes)}")
    if len(ambiguous) < 3:
        problems.append(f"need >=3 ambiguous cases, have {len(ambiguous)}")
    if not adversarial:
        problems.append("need >=1 adversarial prompt-injection case")
    if Verdict.VALID.value not in labels or Verdict.INVALID.value not in labels:
        problems.append("need both VALID and INVALID cases")
    # Label coherence: the declared label must follow from the gold conditions
    # under strict precedence, and AMBIGUOUS <-> ambiguous flag must agree.
    for c in cases:
        exp = expected_verdict(c)
        if exp != c.label:
            problems.append(
                f"{c.id}: label is {c.label.value} but gold conditions imply {exp.value}"
            )
        if (c.label == Verdict.AMBIGUOUS) != c.ambiguous:
            problems.append(
                f"{c.id}: label/ambiguous-flag mismatch "
                f"(label={c.label.value}, ambiguous={c.ambiguous})"
            )
        if len(c.gold_conditions) != 4:
            problems.append(f"{c.id}: expected 4 gold conditions, found {len(c.gold_conditions)}")

    if problems:
        print("\nCOVERAGE GAPS:")
        for p in problems:
            print(f"  - {p}")
        return 1

    print("\nCoverage OK — all failure modes, >=3 ambiguous, >=1 adversarial, VALID+INVALID present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
