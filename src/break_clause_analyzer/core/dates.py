"""Deterministic UK notice-period date arithmetic.

"Not less than N months' notice" follows the corresponding-day rule (cf. Dodds v
Walker): N months before a break date is the same day-of-month N months earlier,
clamping at month end. Naive `timedelta(days=30*N)` is legally wrong, so the LLM
never computes this — it only extracts the dates; the maths lives here, in code,
and is exhaustively unit-tested.
"""

from __future__ import annotations

from datetime import date

from dateutil import parser as _dateparser
from dateutil.relativedelta import relativedelta


class DateParseError(ValueError):
    """Raised when a date string cannot be parsed."""


def parse_uk_date(text: str) -> date:
    """Parse a UK-style date such as '24 June 2025' or '5 March 2025'."""
    try:
        dt = _dateparser.parse(text, dayfirst=True, fuzzy=False)
    except (ValueError, OverflowError, TypeError) as exc:
        raise DateParseError(f"could not parse date: {text!r}") from exc
    if dt is None:
        raise DateParseError(f"could not parse date: {text!r}")
    return dt.date()


def latest_service_date(break_date: date, months: int) -> date:
    """The last date on which 'not less than `months`' notice can be served so as to
    give the full period before `break_date` (corresponding-day rule)."""
    if months <= 0:
        raise ValueError("notice period months must be positive")
    return break_date - relativedelta(months=months)


def notice_served_in_time(break_date: date, months: int, service_date: date) -> bool:
    """True iff `service_date` gives at least `months` notice before `break_date`."""
    return service_date <= latest_service_date(break_date, months)


def format_date(d: date) -> str:
    """Human-readable UK format, e.g. '24 December 2024' (no leading zero)."""
    return f"{d.day} {d:%B %Y}"
