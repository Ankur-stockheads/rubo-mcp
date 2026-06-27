"""The grounding gate: verbatim or NOT_FOUND, never the model's echo."""

from __future__ import annotations

from break_clause_analyzer.core.grounding import ground, ground_span

SOURCE = (
    "Clause 12. The Tenant may terminate this Lease on 24 June 2025 by giving\n"
    "the Landlord not less than six months’ prior written notice."
)


def test_exact_substring_grounds_with_correct_offsets():
    span = ground_span(SOURCE, "may terminate this Lease on 24 June 2025")
    assert span is not None
    assert SOURCE[span.start : span.end] == span.quoted_text
    assert span.quoted_text == "may terminate this Lease on 24 June 2025"


def test_invariant_span_is_sliced_from_source():
    cit = ground(SOURCE, "may terminate this Lease")
    assert cit.found and cit.span is not None
    assert SOURCE[cit.span.start : cit.span.end] == cit.span.quoted_text


def test_whitespace_drift_still_grounds_but_returns_source_text():
    # Query collapses the newline the source contains; it should still match,
    # and the returned text must be the SOURCE's text (with its newline), not the echo.
    query = "by giving the Landlord not less than"
    span = ground_span(SOURCE, query)
    assert span is not None
    assert "\n" in span.quoted_text  # came from the source, not the single-spaced query
    assert span.quoted_text != query
    assert SOURCE[span.start : span.end] == span.quoted_text


def test_unicode_quote_fold_grounds():
    # Source has a curly apostrophe; query uses a straight one.
    span = ground_span(SOURCE, "six months' prior written notice")
    assert span is not None
    assert "’" in span.quoted_text  # the returned text keeps the source's curly quote


def test_single_character_edit_does_not_ground():
    # One wrong character (5 -> 6) must fail — no fuzzy/threshold matching.
    assert ground_span(SOURCE, "24 June 2026") is None
    assert ground("nonsense that is not present", SOURCE).found is False


def test_empty_and_whitespace_quote_not_found():
    assert ground_span(SOURCE, "") is None
    assert ground_span(SOURCE, "   \n  ") is None
    assert ground(SOURCE, "").found is False


def test_not_found_returns_not_found_citation():
    cit = ground(SOURCE, "the tenant must repaint the premises")
    assert cit.found is False
    assert cit.span is None
