"""The committed OpenAPI document must describe the app that actually runs, SPEC-002 AC-002-08."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from mcp_rag_py.adapters.rest import build_app
from mcp_rag_py.core.engine import RagEngine

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = yaml.safe_load((REPO_ROOT / "docs" / "openapi.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def generated(engine: RagEngine) -> dict:
    return build_app(engine).openapi()


def test_paths_match_the_committed_spec(generated: dict) -> None:
    assert set(generated["paths"]) == set(SPEC["paths"])


def test_operation_ids_match_the_committed_spec(generated: dict) -> None:
    for path, operations in SPEC["paths"].items():
        for method, operation in operations.items():
            assert generated["paths"][path][method]["operationId"] == operation["operationId"], path


def test_every_committed_schema_exists_in_the_app(generated: dict) -> None:
    committed = set(SPEC["components"]["schemas"])
    produced = set(generated.get("components", {}).get("schemas", {}))
    assert committed <= produced, committed - produced


def test_documented_error_codes_are_reachable(engine: RagEngine) -> None:
    client = TestClient(build_app(engine))

    assert client.get("/api/v1/search", params={"q": "", "k": 3}).status_code == 400
    assert client.get("/api/v1/documents/missing").status_code == 404
