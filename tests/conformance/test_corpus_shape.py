"""Structural and statistical assertions on the corpus, SPEC-001 AC-001-01…07."""

from __future__ import annotations

import json
import re
from pathlib import Path

from mcp_rag_py.core.chunker import MAX_CHUNK_CHARS
from mcp_rag_py.core.engine import RagEngine
from mcp_rag_py.core.model import Chunk
from mcp_rag_py.core.tokenizer import tokenize

REPO_ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = REPO_ROOT / "corpus"
DOC_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

CLUSTERS = (
    ("ops-credentials", "ops-runbook"),
    ("ops-credentials", "ops-faq"),
    ("ops-runbook", "ops-faq"),
    ("ops-incidents", "ops-escalation"),
    ("ops-backups", "ops-data-retention"),
)


def chunks_of(chunks: tuple[Chunk, ...], doc_id: str) -> tuple[Chunk, ...]:
    return tuple(chunk for chunk in chunks if chunk.doc_id == doc_id)


def token_set(chunks: tuple[Chunk, ...], doc_id: str) -> set[str]:
    return {token for chunk in chunks_of(chunks, doc_id) for token in tokenize(chunk.text)}


def test_exactly_fifteen_documents_with_valid_ids_ac_001_01(engine: RagEngine) -> None:
    assert len(engine.documents) == 15
    ids = [document.doc_id for document in engine.documents]
    assert len(set(ids)) == 15
    assert all(DOC_ID.match(doc_id) for doc_id in ids)


def test_every_document_yields_at_least_two_chunks_ac_001_02(engine: RagEngine) -> None:
    for document in engine.documents:
        assert len(chunks_of(engine.chunks, document.doc_id)) >= 2, document.doc_id


def test_no_chunk_exceeds_the_limit_ac_001_02(engine: RagEngine) -> None:
    assert max(len(chunk.text) for chunk in engine.chunks) <= MAX_CHUNK_CHARS


def test_front_matter_is_minimal(engine: RagEngine) -> None:
    for document in engine.documents:
        assert document.title
        assert document.tags
        assert document.markdown.startswith("## ")


def test_ranking_is_non_trivial_ac_001_04(engine: RagEngine) -> None:
    golden = json.loads((CORPUS_DIR / "golden" / "queries.json").read_text(encoding="utf-8"))
    for case in golden["cases"]:
        if not case["expectDocIds"]:
            continue  # the deliberate-miss case is covered by AC-001-06
        terms = set(tokenize(case["query"]))
        documents_with_term = {
            chunk.doc_id for chunk in engine.chunks if terms & set(tokenize(chunk.text))
        }
        assert len(documents_with_term) >= 2, case["id"]


def test_clusters_overlap_ac_001_05(engine: RagEngine) -> None:
    for left, right in CLUSTERS:
        left_terms = token_set(engine.chunks, left)
        right_terms = token_set(engine.chunks, right)
        shared = left_terms & right_terms
        containment = len(shared) / min(len(left_terms), len(right_terms))
        assert containment >= 0.20, f"{left}/{right} containment {containment:.3f}"


def test_deliberate_miss_ac_001_06(engine: RagEngine) -> None:
    result = engine.search("kubernetes helm chart", 5)

    assert result.is_ok
    assert result.value.total_matched == 0
    assert result.value.results == ()


def test_golden_file_shape_ac_001_07() -> None:
    golden = json.loads((CORPUS_DIR / "golden" / "queries.json").read_text(encoding="utf-8"))

    assert golden["contractVersion"] == 1
    assert len(golden["cases"]) == 10
    for case in golden["cases"]:
        assert case["id"]
        assert case["query"]
        assert isinstance(case["k"], int) and case["k"] >= 1
        assert isinstance(case["expectDocIds"], list)
        assert isinstance(case["expectGrounded"], bool)
