"""Filesystem corpus adapter: restricted front matter parsing, contract §1.

Deliberately not YAML: both implementations parse the same four-line grammar with the same twenty lines of code.
"""

from __future__ import annotations

import re
from pathlib import Path

from mcp_rag_py.core.errors import ErrorCode, Err, Ok, RagError, Result
from mcp_rag_py.core.model import Document

_DOC_ID = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


class CorpusError(ValueError):
    """Raised while parsing a corpus file; converted to CORPUS_UNAVAILABLE by the loader."""


def parse_document(raw: str, source: str) -> Document:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    if not lines or lines[0].strip() != "---":
        raise CorpusError(f"{source}: missing front matter")

    try:
        end = lines.index("---", 1)
    except ValueError:
        raise CorpusError(f"{source}: unterminated front matter") from None

    meta: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        if key in {"id", "title", "tags"}:
            meta[key] = value.strip()

    doc_id = meta.get("id", "")
    if not doc_id or not _DOC_ID.match(doc_id):
        raise CorpusError(f"{source}: invalid or missing id")

    tags = tuple(part.strip().lower() for part in meta.get("tags", "").split(",") if part.strip())
    markdown = "\n".join(lines[end + 1 :])

    return Document(
        doc_id=doc_id,
        title=meta.get("title", doc_id),
        tags=tags,
        markdown=markdown,
        source=source,
    )


def load_documents(corpus_dir: Path) -> Result[tuple[Document, ...]]:
    if not corpus_dir.is_dir():
        return Err(RagError(ErrorCode.CORPUS_UNAVAILABLE, f"corpus directory not found: {corpus_dir}"))

    documents: list[Document] = []
    try:
        for path in sorted(corpus_dir.glob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            documents.append(parse_document(path.read_text(encoding="utf-8"), str(path)))
    except (OSError, CorpusError) as error:
        return Err(RagError(ErrorCode.CORPUS_UNAVAILABLE, str(error)))

    if not documents:
        return Err(RagError(ErrorCode.CORPUS_UNAVAILABLE, f"no documents found in {corpus_dir}"))

    ids = [document.doc_id for document in documents]
    if len(ids) != len(set(ids)):
        return Err(RagError(ErrorCode.CORPUS_UNAVAILABLE, "duplicate document ids"))

    return Ok(tuple(documents))
