"""Parity runner: same golden queries, both engines, identical docId sequences. SPEC-003 AC-003-03."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN = json.loads((REPO_ROOT / "corpus" / "golden" / "queries.json").read_text("utf-8"))


def run_python_cli(query: str, k: int) -> dict:
    completed = subprocess.run(
        [
            sys.executable,
            "-m", "mcp_rag_py.apps.cli",
            "query", query, "-k", str(k), "--json",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
        env={**__import__("os").environ, "PYTHONPATH": str(REPO_ROOT / "src")},
    )
    return json.loads(completed.stdout)


def run_dotnet_cli(query: str, k: int) -> dict:
    completed = subprocess.run(
        ["dotnet", "run", "--no-build", "--project", str(REPO_ROOT / "src" / "Mcp.Rag.Dotnet"),
         "--", "--cli", "query", query, "-k", str(k), "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(completed.stdout)


def main() -> int:
    failures = 0
    for case in GOLDEN["cases"]:
        query = case["query"]
        k = case["k"]
        expected = case["expectDocIds"]

        try:
            py_result = run_python_cli(query, k)
            net_result = run_dotnet_cli(query, k)
        except subprocess.CalledProcessError as exc:
            print(f"FAIL {case['id']}: process error\n{exc.stderr}", file=sys.stderr)
            failures += 1
            continue

        py_ids = [hit["docId"] for hit in py_result["results"]]
        net_ids = [hit["docId"] for hit in net_result["results"]]

        if py_ids != net_ids:
            print(f"FAIL {case['id']}: python={py_ids} dotnet={net_ids}", file=sys.stderr)
            failures += 1
        else:
            print(f" OK  {case['id']}: {py_ids}")

    if failures:
        print(f"\n{failures}/{len(GOLDEN['cases'])} cases failed", file=sys.stderr)
        return 1

    print(f"\n{len(GOLDEN['cases'])}/{len(GOLDEN['cases'])} cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
