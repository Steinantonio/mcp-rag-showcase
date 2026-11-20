"""Composition root for the HTTP server: REST facade and MCP streamable HTTP in one process.

One engine instance, two surfaces. The index is built once at boot; Render's free tier has an ephemeral
filesystem, so nothing is persisted.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from mcp.server.transport_security import TransportSecuritySettings

from mcp_rag_py.adapters.corpus_fs import load_documents
from mcp_rag_py.adapters.mcp_server import create_mcp_server
from mcp_rag_py.adapters.rest import build_app
from mcp_rag_py.apps.config import resolve_corpus_dir
from mcp_rag_py.core.engine import RagEngine


def create_app(directory: str | Path | None = None) -> FastAPI:
    loaded = load_documents(resolve_corpus_dir(directory))
    if not loaded.is_ok:
        raise RuntimeError(f"{loaded.error.code.value}: {loaded.error.message}")

    engine = RagEngine(loaded.value)
    mcp = create_mcp_server(engine)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        async with mcp.session_manager.run():
            yield

    app = build_app(engine, lifespan=lifespan)
    # The MCP sub-app serves its route at /mcp; mounting at / keeps REST routes matched first.
    #
    # DNS rebinding protection is disabled on purpose: this service is public, read-only and holds no
    # credentials, so the header check would only break deployments behind a hostname (Render) without
    # protecting anything. Set MCP_REBINDING_PROTECTION=true to re-enable it.
    rebinding = os.environ.get("MCP_REBINDING_PROTECTION", "").lower() in {"1", "true", "yes"}
    security = TransportSecuritySettings(enable_dns_rebinding_protection=rebinding)
    # Stateless: no session affinity, safe behind any load balancer or proxy, and identical to the .NET
    # transport. The demo is read-only, so there is no state worth keeping between requests.
    app.mount("/", mcp.streamable_http_app(stateless_http=True, transport_security=security))
    return app


app = create_app()
