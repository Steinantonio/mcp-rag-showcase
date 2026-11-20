"""Composition root for the HTTP server.

The index is built once at import. Render's free tier has an ephemeral filesystem, so nothing is persisted:
the corpus is the source of truth and the index is derived in milliseconds at boot.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from mcp_rag_py.adapters.corpus_fs import load_documents
from mcp_rag_py.adapters.rest import build_app
from mcp_rag_py.apps.config import resolve_corpus_dir
from mcp_rag_py.core.engine import RagEngine


def create_app(directory: str | Path | None = None) -> FastAPI:
    loaded = load_documents(resolve_corpus_dir(directory))
    if not loaded.is_ok:
        raise RuntimeError(f"{loaded.error.code.value}: {loaded.error.message}")
    return build_app(RagEngine(loaded.value))


app = create_app()
