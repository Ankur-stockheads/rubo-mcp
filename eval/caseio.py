"""Load and validate synthetic case files.

A case file is Markdown with a YAML front-matter block:

    ---
    id: case-001
    label: INVALID
    ambiguous: false
    adversarial: false
    split: eval
    failure_modes: [notice_timing]
    gold_clause: "The Tenant may terminate this Lease ..."
    gold_conditions:
      - condition: notice_timing
        status: fail
        spans: ["... verbatim quote ...", "..."]
      - ...
    ---

    ## Lease
    ...provisions...

    ## Background Facts
    ...what the tenant did...

The body after the front-matter is the ``source`` the system sees. Every
``gold_clause`` and every gold ``span`` MUST be an exact verbatim substring of
that body — the loader raises ``CaseValidationError`` otherwise, because a gold
span that isn't verbatim would silently corrupt faithfulness scoring.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from break_clause_analyzer.models import CaseFile

CASES_DIR = Path(__file__).resolve().parent.parent / "data" / "cases"


class CaseValidationError(ValueError):
    """Raised when a case file's gold data is not verbatim-consistent with its source."""


def _split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise CaseValidationError("file does not start with a '---' front-matter block")
    # Split into: '', front-matter, body
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise CaseValidationError("front-matter block is not closed with a second '---'")
    front = yaml.safe_load(parts[1]) or {}
    body = parts[2].lstrip("\n")
    return front, body


def parse_case(text: str) -> CaseFile:
    """Parse case text into a validated CaseFile (raises on verbatim drift)."""
    front, body = _split_front_matter(text)
    front["source"] = body
    case = CaseFile(**front)
    _validate_verbatim(case)
    return case


def load_case(path: str | Path) -> CaseFile:
    return parse_case(Path(path).read_text(encoding="utf-8"))


def load_all_cases(cases_dir: str | Path | None = None) -> list[CaseFile]:
    directory = Path(cases_dir) if cases_dir else CASES_DIR
    # Only case-NNN.md files — never docs like README.md in the same directory.
    files = sorted(directory.glob("case-*.md"))
    if not files:
        raise CaseValidationError(f"no case files found in {directory}")
    cases = [load_case(p) for p in files]
    _validate_unique_ids(cases)
    return cases


def _validate_verbatim(case: CaseFile) -> None:
    src = case.source
    if case.gold_clause not in src:
        raise CaseValidationError(
            f"[{case.id}] gold_clause is not a verbatim substring of source:\n"
            f"  {case.gold_clause!r}"
        )
    for gc in case.gold_conditions:
        for span in gc.spans:
            if span not in src:
                raise CaseValidationError(
                    f"[{case.id}] gold span for {gc.condition.value} is not verbatim "
                    f"in source:\n  {span!r}"
                )
    # An ambiguous case must have at least one genuinely uncertain gold condition,
    # and its label must be AMBIGUOUS — otherwise the ambiguity flag is incoherent.
    from break_clause_analyzer.models import Status, Verdict

    if case.ambiguous:
        if case.label != Verdict.AMBIGUOUS:
            raise CaseValidationError(
                f"[{case.id}] ambiguous=true but label is {case.label.value}, not AMBIGUOUS"
            )
        if not any(gc.status == Status.UNCERTAIN for gc in case.gold_conditions):
            raise CaseValidationError(
                f"[{case.id}] ambiguous=true but no gold condition has status 'uncertain'"
            )


def _validate_unique_ids(cases: list[CaseFile]) -> None:
    seen: set[str] = set()
    for c in cases:
        if c.id in seen:
            raise CaseValidationError(f"duplicate case id: {c.id}")
        seen.add(c.id)
