from __future__ import annotations

import math

import pytest

from mcp_rag_py.core.bm25 import Bm25Index
from mcp_rag_py.core.model import Chunk


def chunk(doc_id: str, index: int, text: str) -> Chunk:
    return Chunk(
        doc_id=doc_id,
        chunk_id=f"{doc_id}#{index:02d}",
        title=doc_id,
        heading="",
        text=text,
    )


def test_single_term_score_is_ln_two_when_tf_one_and_dl_equals_avgdl() -> None:
    # Two chunks of two tokens each: N=2, df=1, avgdl=2, dl=2, tf=1.
    # idf = ln(1 + (2-1+0.5)/(1+0.5)) = ln(2); denominator = 1 + 1.2*(0.25+0.75) = 2.2.
    # score = ln(2) * (1*2.2) / 2.2 = ln(2).
    index = Bm25Index((chunk("a", 0, "alpha beta"), chunk("b", 0, "gamma delta")))

    scored = index.score("alpha")

    assert len(scored) == 1
    assert scored[0].score == pytest.approx(math.log(2), rel=1e-12)


def test_chunks_without_the_term_are_excluded() -> None:
    index = Bm25Index((chunk("a", 0, "alpha beta"), chunk("b", 0, "gamma delta")))

    assert index.score("omega") == ()


def test_ties_break_on_doc_id_then_chunk_id() -> None:
    index = Bm25Index(
        (
            chunk("zulu", 0, "alpha"),
            chunk("alpha", 1, "alpha"),
            chunk("alpha", 0, "alpha"),
        )
    )

    scored = index.score("alpha")

    assert [item.chunk.chunk_id for item in scored] == ["alpha#00", "alpha#01", "zulu#00"]


def test_repeated_query_tokens_count_repeatedly() -> None:
    index = Bm25Index((chunk("a", 0, "alpha beta"), chunk("b", 0, "gamma delta")))

    once = index.score("alpha")[0].score
    twice = index.score("alpha alpha")[0].score

    assert twice == pytest.approx(once * 2, rel=1e-12)


def test_longer_chunk_scores_lower_for_the_same_term_frequency() -> None:
    index = Bm25Index(
        (
            chunk("short", 0, "alpha"),
            chunk("long", 0, "alpha beta gamma delta epsilon zeta eta theta"),
        )
    )

    scored = index.score("alpha")

    assert scored[0].chunk.doc_id == "short"
    assert scored[0].score > scored[1].score


def test_empty_index_scores_nothing() -> None:
    assert Bm25Index(()).score("alpha") == ()
