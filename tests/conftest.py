from __future__ import annotations

import json
from pathlib import Path

import pytest

from mcp_rag_py.adapters.corpus_fs import load_documents
from mcp_rag_py.core.engine import RagEngine
from mcp_rag_py.core.model import Document

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = REPO_ROOT / "corpus"
GOLDEN_FILE = CORPUS_DIR / "golden" / "queries.json"


@pytest.fixture(scope="session")
def documents() -> tuple[Document, ...]:
    loaded = load_documents(CORPUS_DIR)
    assert loaded.is_ok, loaded.error
    return loaded.value


@pytest.fixture(scope="session")
def engine(documents: tuple[Document, ...]) -> RagEngine:
    return RagEngine(documents)


@pytest.fixture(scope="session")
def golden() -> dict:
    return json.loads(GOLDEN_FILE.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def small_engine() -> RagEngine:
    return RagEngine(
        (
            Document(
                doc_id="alpha-doc",
                title="Alpha",
                tags=("alpha",),
                markdown=(
                    "## Rotation\n\n"
                    "The api key rotation procedure takes about forty minutes to complete. "
                    "Rotate the key by creating a new one before revoking the old one.\n\n"
                    "## Revocation\n\n"
                    "Revoke a leaked key immediately and open an incident with the service owner."
                ),
                source="alpha-doc.md",
            ),
            Document(
                doc_id="beta-doc",
                title="Beta",
                tags=("beta",),
                markdown=(
                    "## Backups\n\n"
                    "Restore a database backup into an isolated environment before touching production."
                ),
                source="beta-doc.md",
            ),
            Document(
                doc_id="gamma-doc",
                title="Gamma",
                tags=("gamma",),
                markdown="## Weather\n\nCompletely unrelated notes about gardening and the weather.",
                source="gamma-doc.md",
            ),
        )
    )
