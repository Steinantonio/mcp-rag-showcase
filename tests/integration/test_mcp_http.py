"""One process, two surfaces: REST and MCP over HTTP, SPEC-004 AC-004-01.

Both services run MCP stateless, so no session id is involved: every request stands alone.
"""

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

        response = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            headers=MCP_HEADERS,
        )

    assert response.status_code == 200, response.text
    for tool in ("search", "get_document", "answer"):
        assert tool in response.text, f"{tool} missing from tools/list"


def test_mcp_tool_call_returns_citations() -> None:
    with TestClient(create_app()) as client:
        client.post("/mcp", json=INITIALIZE, headers=MCP_HEADERS)
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "search", "arguments": {"query": "restore a database backup", "k": 2}},
            },
            headers=MCP_HEADERS,
        )

    assert response.status_code == 200, response.text
    assert "ops-backups#00" in response.text
