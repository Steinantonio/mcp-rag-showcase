"""BM25 scoring, contract §4.

Constants are contract, not tuning knobs. Changing them is a breaking change: bump contractVersion, update the
document first, then re-derive the golden vectors.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from mcp_rag_py.core.model import Chunk, ScoredChunk
from mcp_rag_py.core.tokenizer import tokenize

K1 = 1.2
B = 0.75


@dataclass(frozen=True, slots=True)
class _Entry:
    chunk: Chunk
    term_freq: dict[str, int]
    length: int


class Bm25Index:
    """Immutable index over a fixed set of chunks. No I/O, no state that changes after construction."""

    def __init__(self, chunks: Sequence[Chunk]) -> None:
        entries: list[_Entry] = []
        for chunk in chunks:
            tokens = tokenize(chunk.text)
            freq: dict[str, int] = {}
            for token in tokens:
                freq[token] = freq.get(token, 0) + 1
            entries.append(_Entry(chunk=chunk, term_freq=freq, length=len(tokens)))

        self._entries = tuple(entries)

        document_freq: dict[str, int] = {}
        for entry in self._entries:
            for term in entry.term_freq:
                document_freq[term] = document_freq.get(term, 0) + 1
        self._document_freq = document_freq

        self._total_tokens = sum(entry.length for entry in self._entries)
        self._avg_length = (self._total_tokens / len(self._entries)) if self._entries else 0.0

    @property
    def chunk_count(self) -> int:
        return len(self._entries)

    @property
    def total_tokens(self) -> int:
        return self._total_tokens

    @property
    def avg_chunk_tokens(self) -> float:
        return self._avg_length

    def score(self, query: str) -> tuple[ScoredChunk, ...]:
        """Ranked chunks with a positive score. Ordering: score desc, docId asc, chunkId asc."""
        tokens = tokenize(query)
        if not tokens or not self._entries:
            return ()

        count = len(self._entries)
        avg_length = self._avg_length
        scored: list[ScoredChunk] = []

        for entry in self._entries:
            score = 0.0
            for term in tokens:
                freq = entry.term_freq.get(term, 0)
                if not freq:
                    continue
                doc_freq = self._document_freq[term]
                idf = math.log(1 + (count - doc_freq + 0.5) / (doc_freq + 0.5))
                score += idf * (freq * (K1 + 1)) / (freq + K1 * (1 - B + B * entry.length / avg_length))
            if score > 0:
                scored.append(ScoredChunk(chunk=entry.chunk, score=score))

        scored.sort(key=lambda item: (-item.score, item.chunk.doc_id, item.chunk.chunk_id))
        return tuple(scored)
