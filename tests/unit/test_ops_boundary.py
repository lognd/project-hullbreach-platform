"""The server core never imports the operator tooling (which spawns processes).

frob's forbid_imports rule (POL-ops-outside-server) sees plain `import`
statements; this test also covers `from hullbreach_ops... import ...`.
"""

from __future__ import annotations

import ast
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2] / "src" / "hullbreach_server"


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.append(node.module)
    return names


def test_only_the_cli_entry_point_imports_hullbreach_ops() -> None:
    # frob:invariant INV-007
    offenders = sorted(
        str(path.relative_to(SERVER))
        for path in SERVER.rglob("*.py")
        if path.parent != SERVER
        and any(
            name == "hullbreach_ops" or name.startswith("hullbreach_ops.")
            for name in _imported_modules(path)
        )
    )
    assert offenders == []
    main = _imported_modules(SERVER / "__main__.py")
    assert any(name.startswith("hullbreach_ops") for name in main)
