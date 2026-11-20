from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mcp_rag_py.adapters.rest import build_app
from mcp_rag_py.core.engine import RagEngine


@pytest.fixture(scope="module")
def client(engine: RagEngine) -> TestClient:
    return TestClient(build_app(engine))


def test_health_reports_corpus_stats(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["contractVersion"] == 1
    assert body["corpus"]["documents"] == 15
    assert body["corpus"]["chunks"] > 0


def test_search_returns_ranked_chunks(client: TestClient) -> None:
    response = client.get("/api/v1/search", params={"q": "restore a database backup", "k": 3})

    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["docId"] == "ops-backups"
    assert body["results"][0]["citation"] == body["results"][0]["chunkId"]
    assert body["totalMatched"] >= len(body["results"])


def test_empty_query_is_a_400_invalid_argument_ac_002_09(client: TestClient) -> None:
    response = client.get("/api/v1/search", params={"q": "", "k": 3})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_ARGUMENT"


def test_k_out_of_range_is_a_400(client: TestClient) -> None:
    response = client.get("/api/v1/search", params={"q": "backup", "k": 0})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_ARGUMENT"


def test_document_is_returned_with_chunk_count(client: TestClient) -> None:
    response = client.get("/api/v1/documents/ops-credentials")

    assert response.status_code == 200
    body = response.json()
    assert body["docId"] == "ops-credentials"
    assert body["chunkCount"] >= 2
    assert body["markdown"].startswith("## ")


def test_unknown_document_is_a_404_ac_002_09(client: TestClient) -> None:
    response = client.get("/api/v1/documents/does-not-exist")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOC_NOT_FOUND"


def test_answer_returns_citations(client: TestClient) -> None:
    response = client.post("/api/v1/answer", json={"query": "how do I rotate an api key", "k": 3})

    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is True
    assert body["citations"]


def test_answer_on_a_miss_is_ungrounded(client: TestClient) -> None:
    response = client.post("/api/v1/answer", json={"query": "kubernetes helm chart"})

    assert response.status_code == 200
    body = response.json()
    assert body["grounded"] is False
    assert body["citations"] == []


def test_answer_with_empty_query_is_a_400(client: TestClient) -> None:
    response = client.post("/api/v1/answer", json={"query": ""})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_ARGUMENT"
