from __future__ import annotations

import re

from mcp_rag_py.core.engine import NO_MATCH_ANSWER, RagEngine
from mcp_rag_py.core.errors import ErrorCode


def test_search_ranks_the_expected_document(small_engine: RagEngine) -> None:
    result = small_engine.search("key rotation", 2)

    assert result.is_ok
    assert result.value.results[0].doc_id == "alpha-doc"


def test_search_with_no_lexical_match_returns_nothing(small_engine: RagEngine) -> None:
    result = small_engine.search("kubernetes helm chart", 5)

    assert result.is_ok
    assert result.value.total_matched == 0
    assert result.value.results == ()


def test_get_document_returns_the_document(small_engine: RagEngine) -> None:
    result = small_engine.get_document("beta-doc")

    assert result.is_ok
    assert result.value.title == "Beta"


def test_get_document_unknown_id_is_a_typed_error(small_engine: RagEngine) -> None:
    result = small_engine.get_document("does-not-exist")

    assert not result.is_ok
    assert result.error.code is ErrorCode.DOC_NOT_FOUND


def test_answer_is_extractive_ac_002_05(small_engine: RagEngine) -> None:
    result = small_engine.answer("how do I rotate a key", 3)

    assert result.is_ok
    answer = result.value
    assert answer.grounded is True
    assert answer.citations

    cited_text = " ".join(
        chunk.text for chunk in small_engine.chunks if chunk.chunk_id in answer.citations
    )
    sentences = [part for part in re.split(r"(?<=[.!?])\s+", answer.answer) if part]
    assert sentences
    for sentence in sentences:
        assert sentence in cited_text, sentence


def test_answer_on_a_miss_is_not_grounded(small_engine: RagEngine) -> None:
    result = small_engine.answer("kubernetes helm chart", 3)

    assert result.is_ok
    assert result.value.grounded is False
    assert result.value.answer == NO_MATCH_ANSWER
    assert result.value.citations == ()


def test_invalid_arguments_are_rejected(small_engine: RagEngine) -> None:
    assert small_engine.search("", 5).error.code is ErrorCode.INVALID_ARGUMENT
    assert small_engine.search("   ", 5).error.code is ErrorCode.INVALID_ARGUMENT
    assert small_engine.search("alpha", 0).error.code is ErrorCode.INVALID_ARGUMENT
    assert small_engine.search("alpha", 21).error.code is ErrorCode.INVALID_ARGUMENT
    assert small_engine.answer("alpha", 11).error.code is ErrorCode.INVALID_ARGUMENT
    assert small_engine.search("x" * 513, 5).error.code is ErrorCode.INVALID_ARGUMENT


def test_stats_reflect_the_engine(small_engine: RagEngine) -> None:
    stats = small_engine.stats()

    assert stats.documents == 3
    assert stats.chunks == len(small_engine.chunks)
    assert stats.tokens > 0
