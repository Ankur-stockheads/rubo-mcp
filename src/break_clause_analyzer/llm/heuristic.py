"""A no-LLM heuristic baseline client (regex + keywords).

This exists so the server and the eval run with NO API key. It is deliberately
honest about what it is: a weak baseline the grounded-LLM system is meant to beat.
Its quotes are real sentences from the document (so they ground), but its
*reasoning* is shallow — it will misjudge subtle validity cases and confidently
answer genuinely-ambiguous ones, which is exactly the behaviour the eval metrics
are designed to expose.
"""

from __future__ import annotations

import re

from break_clause_analyzer.llm.schemas import (
    ClauseExtraction,
    ConditionFinding,
    ConditionFindings,
)
from break_clause_analyzer.models import ConditionId, Status

_WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}
_DATE = r"\d{1,2}\s+[A-Z][a-z]+\s+\d{4}"


def _facts(source: str) -> str:
    """The Background Facts portion (where what-the-tenant-did lives)."""
    parts = re.split(r"Background Facts", source, maxsplit=1)
    return parts[1] if len(parts) > 1 else source


def _sentence_for(source: str, pattern: str, flags: int = re.IGNORECASE) -> str | None:
    """Return the verbatim sentence in `source` containing the first match, or None."""
    m = re.search(pattern, source, flags)
    if not m:
        return None
    start = source.rfind(".", 0, m.start())
    start = 0 if start < 0 else start + 1
    end = source.find(".", m.end())
    end = len(source) if end < 0 else end + 1
    return source[start:end].strip()


class HeuristicClient:
    model = "heuristic-baseline"

    def extract_clause(self, source: str) -> ClauseExtraction:
        m = re.search(
            r"The Tenant may (?:terminate|determine|break|end)\b[^.]*?\bnotice\b[^.]*?\.",
            source,
        )
        if not m:
            m = re.search(r"The Tenant may (?:terminate|determine|break|end)\b[^.]*?\.", source)
        if m:
            return ClauseExtraction(found=True, clause_quote=m.group(0).strip())
        return ClauseExtraction(found=False, clause_quote="")

    def reason_conditions(self, source: str) -> ConditionFindings:
        return ConditionFindings(
            findings=[
                self._timing(source),
                self._validity(source),
                self._arrears(source),
                self._vacant_possession(source),
            ]
        )

    # -- per-condition heuristics ------------------------------------------- #

    def _timing(self, source: str) -> ConditionFinding:
        facts = _facts(source)
        period = None
        pm = re.search(r"not less than (\w+) months", source, re.IGNORECASE)
        if pm:
            period = _WORD_NUM.get(pm.group(1).lower())
        bd = re.search(r"may (?:terminate|determine|break|end)[^.]*?on (" + _DATE + r")", source)
        sd = re.search(r"(?:served|gave|service)[^.]*?(" + _DATE + r")", facts) or re.search(
            r"notice[^.]*?on (" + _DATE + r")", facts
        )
        quotes = [q for q in (
            pm.group(0) if pm else None,
            _sentence_for(facts, r"(?:served|gave)[^.]*?notice"),
        ) if q]
        return ConditionFinding(
            condition=ConditionId.NOTICE_TIMING,
            status=Status.UNCERTAIN,  # the core recomputes from the facts below
            evidence_quotes=quotes,
            rationale="Heuristic: extracted dates; timing computed by the core.",
            break_date=bd.group(1) if bd else None,
            notice_service_date=sd.group(1) if sd else None,
            notice_period_months=period,
        )

    def _validity(self, source: str) -> ConditionFinding:
        facts = _facts(source)
        fail_pat = r"wrong|former landlord|agents[^.]*rather than|not in writing|orally|incorrect"
        pass_pat = r"registered office|in accordance with the Lease|address given in the Lease|notice address|valid written notice|in writing"
        if re.search(fail_pat, facts, re.IGNORECASE):
            status, quote = Status.FAIL, _sentence_for(facts, fail_pat)
        elif re.search(pass_pat, source, re.IGNORECASE):
            status, quote = Status.PASS, _sentence_for(source, pass_pat)
        else:
            status, quote = Status.UNCERTAIN, None
        return ConditionFinding(
            condition=ConditionId.NOTICE_VALIDITY,
            status=status,
            evidence_quotes=[quote] if quote else [],
            rationale="Heuristic keyword scan of notice service.",
        )

    def _arrears(self, source: str) -> ConditionFinding:
        facts = _facts(source)
        low = facts.lower()
        if re.search(r"unpaid|arrears of|remained unpaid|outstanding", low) and "no arrears" not in low:
            status, quote = Status.FAIL, _sentence_for(facts, r"unpaid|arrears|outstanding")
        elif re.search(r"no arrears|paid up to|had paid|paid the rents|paid all rent", low):
            status, quote = Status.PASS, _sentence_for(facts, r"no arrears|paid up to|had paid|paid the rents|paid all rent")
        else:
            status, quote = Status.UNCERTAIN, None
        return ConditionFinding(
            condition=ConditionId.NO_ARREARS,
            status=status,
            evidence_quotes=[quote] if quote else [],
            rationale="Heuristic keyword scan of rent status.",
        )

    def _vacant_possession(self, source: str) -> ConditionFinding:
        facts = _facts(source)
        low = facts.lower()
        people = bool(re.search(r"contractors|security guard|staff remained|personnel remained", low))
        chattels = bool(re.search(r"racking|chattels|goods remained|equipment remained|not finished clearing|left in place", low))
        occupier = bool(re.search(r"licensee|subtenant|occupier|concession|remained trading|in occupation", low))
        cleared = bool(re.search(r"vacant possession|returned (all )?the keys|removed all|left .{0,20}empty|premises empty", low))
        quote = _sentence_for(
            facts,
            r"vacant possession|returned|removed all|remained|racking|licensee|contractors|left in place",
        )
        if not quote:
            status = Status.UNCERTAIN
            return ConditionFinding(
                condition=ConditionId.VACANT_POSSESSION, status=status, evidence_quotes=[],
                rationale="Heuristic found no possession evidence.",
            )
        # Provide the legal-test flags; the core decides pass/fail from them.
        if not (people or chattels or occupier) and cleared:
            people = chattels = occupier = False
        return ConditionFinding(
            condition=ConditionId.VACANT_POSSESSION,
            status=Status.UNCERTAIN,  # the core's VP test decides from the flags
            evidence_quotes=[quote],
            rationale="Heuristic possession signals; core applies the VP legal test.",
            vp_people_left=people,
            vp_chattels_substantial=chattels,
            vp_occupier_left=occupier,
        )
