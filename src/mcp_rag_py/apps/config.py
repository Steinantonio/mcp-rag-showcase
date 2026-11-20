"""Corpus location, resolved once for every entry point."""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_CORPUS_DIR = Path(__file__).resolve().parents[3] / "corpus"
ENV_VAR = "MCP_RAG_CORPUS"


def resolve_corpus_dir(explicit: str | Path | None = None) -> Path:
    if explicit is not None:
        return Path(explicit)
    from_env = os.environ.get(ENV_VAR)
    if from_env:
        return Path(from_env)
    return DEFAULT_CORPUS_DIR
