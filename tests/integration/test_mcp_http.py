"""One process, two surfaces: REST and MCP over HTTP, SPEC-004 AC-004-01."""

from __future__ import annotations

from fastapi.testclient import TestClient

from mcp_rag_py.apps.http import create_app

MCP_HEADERS = {
    "accept": "application/json, text/event-stream",
    "content-type": "application/json",
}
INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "pytest", "version": "1.0"},
    },
}


def test_rest_and_mcp_share_one_process() -> None:
    with TestClient(create_app()) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/api/v1/search", params={"q": "egress rules", "k": 1}).status_code == 200
        assert client.get("/docs").status_code == 200


def test_mcp_lists_the_three_tools() -> None:
    with TestClient(create_app()) as client:
        handshake = client.post("/mcp", json=INITIALIZE, headers=MCP_HEADERS)
        assert handshake.status_code == 200, handshake.text

        session = handshake.headers.get("mcp-session-id")
        assert session, "server did not return a session id"

        headers = {**MCP_HEADERS, "mcp-session-id": session}
        client.post("/mcp", json={"jsonrpc": "2.0", "method": "notifications/initialized"}, headers=headers)

        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            headers=headers,
        )

    assert response.status_code == 200, response.text
    for tool in ("search", "get_document", "answer"):
        assert tool in response.text, f"{tool} missing from tools/list"
