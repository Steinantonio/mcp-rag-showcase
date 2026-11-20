"""The engine: three use cases over the index, contract §5.

Pure: no clock, no I/O, no environment. Errors come back as values.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from mcp_rag_py.core.bm25 import Bm25Index
from mcp_rag_py.core.chunker import chunk_document
from mcp_rag_py.core.errors import ErrorCode, Err, Ok, RagError, Result, doc_not_found
from mcp_rag_py.core.model import (
    Answer,
    Chunk,
    CorpusStats,
    Document,
    ScoredChunk,
    SearchHit,
    SearchResult,
)
from mcp_rag_py.core.tokenizer import tokenize

MAX_QUERY_CHARS = 512
MAX_K_SEARCH = 20
MAX_K_ANSWER = 10
MAX_ANSWER_SENTENCES = 3
MIN_SENTENCE_CHARS = 20
NO_MATCH_ANSWER = "No content in the corpus matches this question."

_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+")


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in _SENTENCE_BREAK.split(text) if len(part.strip()) >= MIN_SENTENCE_CHARS]


def _validate(query: str, k: int, max_k: int) -> RagError | None:
    if not query.strip():
        return RagError(ErrorCode.INVALID_ARGUMENT, "query must not be empty")
    if len(query) > MAX_QUERY_CHARS:
        return RagError(ErrorCode.INVALID_ARGUMENT, f"query must be at most {MAX_QUERY_CHARS} characters")
    if k < 1 or k > max_k:
        return RagError(ErrorCode.INVALID_ARGUMENT, f"k must be between 1 and {max_k}")
    return None


def _to_hit(scored: ScoredChunk) -> SearchHit:
    chunk = scored.chunk
    return SearchHit(
        doc_id=chunk.doc_id,
        chunk_id=chunk.chunk_id,
        title=chunk.title,
        heading=chunk.heading,
        score=round(scored.score, 4),
        citation=chunk.chunk_id,
        text=chunk.text,
    )


class RagEngine:
    def __init__(self, documents: Sequence[Document]) -> None:
        self._documents = tuple(documents)
        self._by_id = {document.doc_id: document for document in documents}
        self._chunks: tuple[Chunk, ...] = tuple(
            chunk for document in documents for chunk in chunk_document(document)
        )
        self._index = Bm25Index(self._chunks)

    @property
    def documents(self) -> tuple[Document, ...]:
        return self._documents

    @property
    def chunks(self) -> tuple[Chunk, ...]:
        return self._chunks

    def stats(self) -> CorpusStats:
        return CorpusStats(
            documents=len(self._documents),
            chunks=self._index.chunk_count,
            tokens=self._index.total_tokens,
            avg_chunk_tokens=round(self._index.avg_chunk_tokens, 2),
        )

    def search(self, query: str, k: int = 5) -> Result[SearchResult]:
        error = _validate(query, k, MAX_K_SEARCH)
        if error is not None:
            return Err(error)

        ranked = self._index.score(query)
        return Ok(
            SearchResult(
                query=query,
                k=k,
                total_matched=len(ranked),
                results=tuple(_to_hit(item) for item in ranked[:k]),
            )
        )

    def get_document(self, doc_id: str) -> Result[Document]:
        document = self._by_id.get(doc_id)
        if document is None:
            return doc_not_found(doc_id)
        return Ok(document)

    def answer(self, query: str, k: int = 3) -> Result[Answer]:
        error = _validate(query, k, MAX_K_ANSWER)
        if error is not None:
            return Err(error)

        ranked = self._index.score(query)
        if not ranked:
            return Ok(Answer(query=query, answer=NO_MATCH_ANSWER, citations=(), grounded=False))

        query_terms = set(tokenize(query))
        candidates: list[tuple[int, int, int, str, str]] = []

        for rank, scored in enumerate(ranked[:k]):
            for position, sentence in enumerate(_sentences(scored.chunk.text)):
                overlap = len(query_terms & set(tokenize(sentence)))
                if overlap > 0:
                    candidates.append((overlap, rank, position, sentence, scored.chunk.chunk_id))

        if not candidates:
            # Chunks matched but no sentence kept its query term (a term split across a boundary, or a fragment
            # dropped by the length rule). Fall back to the opening sentences of the best chunk so the answer is
            # still grounded in retrieved text.
            fallback = _sentences(ranked[0].chunk.text)[:MAX_ANSWER_SENTENCES]
            if not fallback:
                return Ok(Answer(query=query, answer=NO_MATCH_ANSWER, citations=(), grounded=False))
            return Ok(
                Answer(
                    query=query,
                    answer=" ".join(fallback),
                    citations=(ranked[0].chunk.chunk_id,),
                    grounded=True,
                )
            )

        candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
        selected = sorted(candidates[:MAX_ANSWER_SENTENCES], key=lambda item: (item[1], item[2]))

        citations: list[str] = []
        for _, _, _, _, chunk_id in selected:
            if chunk_id not in citations:
                citations.append(chunk_id)

        return Ok(
            Answer(
                query=query,
                answer=" ".join(item[3] for item in selected),
                citations=tuple(citations),
                grounded=True,
            )
        )
