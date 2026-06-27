"""Self-containment (PKG-04): the package imports only stdlib + declared deps.

A static guarantee that nothing proprietary or out-of-tree has crept in.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import break_clause_analyzer as pkg

# Declared runtime dependencies (top-level import names).
ALLOWED_THIRD_PARTY = {"fastmcp", "anthropic", "pydantic", "dateutil", "mcp"}


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(n.name.split(".")[0] for n in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods.add(node.module.split(".")[0])
    return mods


def test_package_imports_are_self_contained():
    allowed = set(sys.stdlib_module_names) | ALLOWED_THIRD_PARTY | {"break_clause_analyzer"}
    root = Path(pkg.__file__).resolve().parent
    offenders: dict[str, set[str]] = {}
    for py in root.rglob("*.py"):
        for mod in _top_level_imports(py):
            if mod not in allowed:
                offenders.setdefault(py.name, set()).add(mod)
    assert not offenders, f"unexpected external imports (not self-contained): {offenders}"
