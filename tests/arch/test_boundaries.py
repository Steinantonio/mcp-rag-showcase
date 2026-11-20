"""The dependency rule is a test, not a code-review opinion, SPEC-002 AC-002-07."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def lint_command() -> list[str]:
    executable = "lint-imports.exe" if os.name == "nt" else "lint-imports"
    candidate = Path(sys.executable).parent / executable
    if candidate.exists():
        return [str(candidate)]
    return ["lint-imports"]


def test_core_imports_nothing_outside_core() -> None:
    completed = subprocess.run(
        lint_command(),
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    output = completed.stdout + completed.stderr
    assert completed.returncode == 0, output
    assert "core is pure" in output
