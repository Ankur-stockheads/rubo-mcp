"""The trust boundary is structural: core/ must never import the LLM layer.

If this test fails, the 'LLM proposes, deterministic code disposes' guarantee has
been breached and the grounding/abstention claims can no longer be trusted.
"""

from __future__ import annotations

from pathlib import Path

import break_clause_analyzer.core as core_pkg

FORBIDDEN = ("break_clause_analyzer.llm", "from anthropic", "import anthropic")


def test_core_never_imports_llm_or_anthropic():
    core_dir = Path(core_pkg.__file__).resolve().parent
    offenders = []
    for py in sorted(core_dir.glob("*.py")):
        for line in py.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")):
                code = stripped.split("#", 1)[0]
                if any(f in code for f in FORBIDDEN):
                    offenders.append(f"{py.name}: {stripped}")
    assert not offenders, "core/ imports the LLM layer:\n" + "\n".join(offenders)
