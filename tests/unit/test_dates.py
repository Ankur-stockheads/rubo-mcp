"""UK notice-period date arithmetic (corresponding-day rule)."""

from __future__ import annotations

from datetime import date

import pytest

from break_clause_analyzer.core.dates import (
    DateParseError,
    latest_service_date,
    notice_served_in_time,
    parse_uk_date,
)


def test_parse_uk_dates():
    assert parse_uk_date("24 June 2025") == date(2025, 6, 24)
    assert parse_uk_date("5 March 2025") == date(2025, 3, 5)
    assert parse_uk_date("29 September 2024") == date(2024, 9, 29)


def test_parse_rejects_garbage():
    with pytest.raises(DateParseError):
        parse_uk_date("not a date")


def test_latest_service_date_corresponding_day():
    # Six months before 24 June 2025 is 24 December 2024 (same day-of-month).
    assert latest_service_date(date(2025, 6, 24), 6) == date(2024, 12, 24)
    assert latest_service_date(date(2024, 9, 29), 9) == date(2023, 12, 29)


def test_served_on_the_boundary_is_in_time():
    # Exactly on the deadline gives "not less than" the period.
    assert notice_served_in_time(date(2025, 6, 24), 6, date(2024, 12, 24)) is True


def test_served_one_day_late_fails():
    assert notice_served_in_time(date(2025, 6, 24), 6, date(2024, 12, 25)) is False


def test_real_case_001_is_late():
    # case-001: 6 months before 24 June 2025 -> deadline 24 Dec 2024; served 5 Mar 2025.
    assert notice_served_in_time(date(2025, 6, 24), 6, date(2025, 3, 5)) is False


def test_served_after_break_date_fails():
    assert notice_served_in_time(date(2025, 6, 24), 6, date(2025, 7, 1)) is False


def test_month_end_clamps():
    # One month before 31 March 2025 clamps to 28 February 2025.
    assert latest_service_date(date(2025, 3, 31), 1) == date(2025, 2, 28)


def test_leap_year_clamps_to_29_feb():
    # Six months before 31 August 2024 is end of February 2024 (a leap year) -> 29 Feb.
    assert latest_service_date(date(2024, 8, 31), 6) == date(2024, 2, 29)


def test_non_positive_period_rejected():
    with pytest.raises(ValueError):
        latest_service_date(date(2025, 6, 24), 0)
