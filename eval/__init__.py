"""Eval harness: the measurement apparatus.

Built and tested (Phase 1) against a stub oracle BEFORE any server logic exists,
so a passing eval proves the scorer is correct independently of the system under
test. The real LLM-backed system plugs into the same `System` interface later.
"""
