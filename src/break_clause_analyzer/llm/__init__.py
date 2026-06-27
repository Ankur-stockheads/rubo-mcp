"""LLM adapter — the ONLY network egress.

The model proposes (extraction + per-condition findings); the deterministic
`core` package disposes (grounds every quote, recomputes timing, applies the
vacant-possession test, aggregates). `core` must never import this package.
"""
