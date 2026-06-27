"""The grounding gate — the system's trust chokepoint.

Given the source text and a quote proposed by the model, the gate locates the
quote and returns a `Span` **sliced from the source** (so the returned text is
verbatim by construction), or `NOT_FOUND`. It never returns the model's echo.

Matching is *normalize-then-exact*, NOT fuzzy: whitespace runs are collapsed and a
few unicode look-alikes (curly quotes, en/em dashes, non-breaking spaces) are
folded, so trivial transcription drift still matches — but there is no similarity
threshold, no edit-distance, nothing that could admit a hallucinated quote. A
one-character change that isn't one of those folds fails to ground.

The offsets are derived in code from an index map back to the original source, so
`source[start:end] == quoted_text` always holds for a grounded span.
"""

from __future__ import annotations

from break_clause_analyzer.models import Citation, Span

# 1:1, offset-preserving folds for common unicode look-alikes.
_FOLD = {
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"', "‟": '"',
    "–": "-", "—": "-", "−": "-",
    " ": " ",
}


def _normalize_with_map(text: str) -> tuple[str, list[int]]:
    """Return (normalized_text, index_map) where index_map[k] is the original
    index of normalized character k. Whitespace runs collapse to a single space
    mapped to the first whitespace char; other chars fold 1:1."""
    out: list[str] = []
    idx_map: list[int] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            out.append(" ")
            idx_map.append(i)
            i += 1
            while i < n and text[i].isspace():
                i += 1
        else:
            out.append(_FOLD.get(ch, ch))
            idx_map.append(i)
            i += 1
    return "".join(out), idx_map


def _normalize(text: str) -> str:
    norm, _ = _normalize_with_map(text)
    return norm


def ground_span(source: str, quote: str) -> Span | None:
    """Locate `quote` in `source`; return a source-sliced Span, or None (NOT_FOUND)."""
    if quote is None or not quote.strip():
        return None
    src_norm, idx_map = _normalize_with_map(source)
    q_norm = _normalize(quote).strip()
    if not q_norm:
        return None
    pos = src_norm.find(q_norm)
    if pos < 0:
        return None
    start = idx_map[pos]
    # End = one past the original index of the last matched normalized char.
    end = idx_map[pos + len(q_norm) - 1] + 1
    return Span(quoted_text=source[start:end], start=start, end=end)


def ground(source: str, quote: str) -> Citation:
    """Grounding gate: a verbatim Citation, or NOT_FOUND. Never invents text."""
    span = ground_span(source, quote)
    return Citation.grounded(span) if span is not None else Citation.not_found()
