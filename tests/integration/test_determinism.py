from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from mcp_rag_py.core.engine import RagEngine

REPO_ROOT = Path(__file__).resolve().parents[2]
QUERY = "restore a database backup"


def run_cli_query() -> str:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(REPO_ROOT / "src")
    completed = subprocess.run(
        [sys.executable, "-m", "mcp_rag_py.apps.cli", "query", QUERY, "-k", "3", "--json"],
        cwd=REPO_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout


def test_engine_is_deterministic_in_process_ac_002_06(engine: RagEngine) -> None:
    first = engine.search(QUERY, 3)
    second = engine.search(QUERY, 3)

    assert first == second


def test_cli_output_is_byte_identical_across_processes_ac_002_06() -> None:
    assert run_cli_query() == run_cli_query()
