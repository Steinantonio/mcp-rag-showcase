from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcp_rag_py.core.engine import RagEngine

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN = json.loads((REPO_ROOT / "corpus" / "golden" / "queries.json").read_text(encoding="utf-8"))
CASES = GOLDEN["cases"]
CASE_IDS = [case["id"] for case in CASES]


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_search_matches_golden_doc_ids_ac_002_03(case: dict, engine: RagEngine) -> None:
    result = engine.search(case["query"], case["k"])

    assert result.is_ok
    assert [hit.doc_id for hit in result.value.results] == case["expectDocIds"]


@pytest.mark.parametrize("case", CASES, ids=CASE_IDS)
def test_answer_grounded_flag_matches_golden(case: dict, engine: RagEngine) -> None:
    result = engine.answer(case["query"], min(case["k"], 10))

    assert result.is_ok
    assert result.value.grounded is case["expectGrounded"]
