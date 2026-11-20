"""Chunking, contract §1-2.

Deterministic, no overlap, no token counting: split on H2 headings, pack paragraphs up to 1200 characters.
"""

from __future__ import annotations

import re

from mcp_rag_py.core.model import Chunk, Document

MAX_CHUNK_CHARS = 1200

_HEADING = "## "
_PARAGRAPH_BREAK = re.compile(r"\n{2,}")


def normalize(body: str) -> str:
    """CRLF to LF, strip trailing whitespace per line, drop trailing blank lines."""
    text = body.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).strip("\n")


def _sections(body: str) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    heading = ""
    buffer: list[str] = []

    def flush() -> None:
        text = "\n".join(buffer).strip()
        if text:
            sections.append((heading, text))
        buffer.clear()

    for line in body.split("\n"):
        if line.startswith(_HEADING):
            flush()
            heading = line[len(_HEADING) :].strip()
        else:
            buffer.append(line)
    flush()

    return sections


def _split_long(text: str) -> list[str]:
    pieces: list[str] = []
    current = ""

    for paragraph in _PARAGRAPH_BREAK.split(text):
        if len(paragraph) > MAX_CHUNK_CHARS:
            if current:
                pieces.append(current)
                current = ""
            rest = paragraph
            while len(rest) > MAX_CHUNK_CHARS:
                cut = rest.rfind(" ", 0, MAX_CHUNK_CHARS)
                if cut <= 0:
                    cut = MAX_CHUNK_CHARS
                pieces.append(rest[:cut])
                rest = rest[cut:].lstrip()
            if rest:
                current = rest
            continue

        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if len(candidate) > MAX_CHUNK_CHARS:
            pieces.append(current)
            current = paragraph
        else:
            current = candidate

    if current:
        pieces.append(current)

    return pieces


def chunk_document(document: Document) -> list[Chunk]:
    body = normalize(document.markdown)
    chunks: list[Chunk] = []

    for heading, text in _sections(body):
        for piece in _split_long(text):
            index = len(chunks)
            chunks.append(
                Chunk(
                    doc_id=document.doc_id,
                    chunk_id=f"{document.doc_id}#{index:02d}",
                    title=document.title,
                    heading=heading,
                    text=piece,
                )
            )

    return chunks
