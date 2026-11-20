"""Immutable values shared by the core. No behavior, no imports from outside core."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Document:
    doc_id: str
    title: str
    tags: tuple[str, ...]
    markdown: str
    source: str


@dataclass(frozen=True, slots=True)
class Chunk:
    doc_id: str
    chunk_id: str
    title: str
    heading: str
    text: str


@dataclass(frozen=True, slots=True)
class ScoredChunk:
    chunk: Chunk
    score: float


@dataclass(frozen=True, slots=True)
class SearchHit:
    doc_id: str
    chunk_id: str
    title: str
    heading: str
    score: float
    citation: str
    text: str


@dataclass(frozen=True, slots=True)
class SearchResult:
    query: str
    k: int
    total_matched: int
    results: tuple[SearchHit, ...]


@dataclass(frozen=True, slots=True)
class Answer:
    query: str
    answer: str
    citations: tuple[str, ...]
    grounded: bool


@dataclass(frozen=True, slots=True)
class CorpusStats:
    documents: int
    chunks: int
    tokens: int
    avg_chunk_tokens: float
