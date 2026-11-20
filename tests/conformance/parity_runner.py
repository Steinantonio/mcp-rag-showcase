"""Parity runner: same golden queries, both engines, identical docId sequences. SPEC-003 AC-003-03."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN = json.loads((REPO_ROOT / "corpus" / "golden" / "queries.json").read_text("utf-8"))

# Scores are compared with a tolerance, never for ordering. The CLI payload rounds to 4 decimals, so the
# tolerance is one unit in the last place: tight enough to catch a changed constant, loose enough not to
# care about the last bits of two `ln` implementations.
SCORE_TOLERANCE = 1e-4


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
            continue

        # Ranking parity is not arithmetic parity: a change to k1, b or the IDF formula can reorder nothing
        # while moving every score. Compare scores with a tolerance, never for ordering.
        diverged = [
            (py_hit["chunkId"], py_hit["score"], net_hit["score"])
            for py_hit, net_hit in zip(py_result["results"], net_result["results"])
            if abs(py_hit["score"] - net_hit["score"]) > SCORE_TOLERANCE
        ]
        if diverged:
            chunk, py_score, net_score = diverged[0]
            print(
                f"FAIL {case['id']}: score drift on {chunk}: python={py_score} dotnet={net_score}",
                file=sys.stderr,
            )
            failures += 1
            continue

        if py_ids != expected:
            print(f"FAIL {case['id']}: ranking {py_ids} != expected {expected}", file=sys.stderr)
            failures += 1
            continue

        print(f" OK  {case['id']}: {py_ids}")

    if failures:
        print(f"\n{failures}/{len(GOLDEN['cases'])} cases failed", file=sys.stderr)
        return 1

    print(f"\n{len(GOLDEN['cases'])}/{len(GOLDEN['cases'])} cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
