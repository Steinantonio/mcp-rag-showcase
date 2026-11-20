from __future__ import annotations

from mcp_rag_py.core.chunker import MAX_CHUNK_CHARS, chunk_document
from mcp_rag_py.core.model import Document


def make_document(markdown: str) -> Document:
    return Document(
        doc_id="fixture",
        title="Fixture",
        tags=(),
        markdown=markdown,
        source="fixture.md",
    )


def test_three_sections_yield_three_chunks_ac_002_02() -> None:
    document = make_document(
        "## One\n\n" + "a" * 40 + "\n\n## Two\n\n" + "b" * 40 + "\n\n## Three\n\n" + "c" * 40
    )

    chunks = chunk_document(document)

    assert len(chunks) == 3
    assert [chunk.chunk_id for chunk in chunks] == ["fixture#00", "fixture#01", "fixture#02"]
    assert [chunk.heading for chunk in chunks] == ["One", "Two", "Three"]


def test_no_chunk_exceeds_the_limit() -> None:
    long_paragraph = " ".join(["word"] * 600)
    chunks = chunk_document(make_document(f"## Big\n\n{long_paragraph}"))

    assert len(chunks) > 1
    assert all(len(chunk.text) <= MAX_CHUNK_CHARS for chunk in chunks)


def test_content_before_the_first_heading_gets_an_empty_heading() -> None:
    chunks = chunk_document(make_document("intro text\n\n## One\n\nbody"))

    assert chunks[0].heading == ""
    assert chunks[0].text == "intro text"


def test_crlf_is_normalized() -> None:
    chunks = chunk_document(make_document("## One\r\n\r\nbody line\r\n"))

    assert chunks[0].text == "body line"


def test_chunk_ids_are_zero_padded_and_sequential() -> None:
    sections = "\n\n".join(f"## S{index}\n\nbody {index}" for index in range(11))
    chunks = chunk_document(make_document(sections))

    assert chunks[9].chunk_id == "fixture#09"
    assert chunks[10].chunk_id == "fixture#10"
