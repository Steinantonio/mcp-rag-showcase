"""MCP tool surface. The same engine methods the REST facade calls, exposed over the MCP protocol."""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from mcp_rag_py.core.engine import RagEngine
from mcp_rag_py.core.model import Answer, Document, SearchResult


def create_mcp_server(engine: RagEngine) -> MCPServer:
    server = MCPServer("rag-python")

    @server.tool()
    def search(query: str, k: int = 5) -> dict:
        """Search the corpus. Returns ranked chunks with citations."""
        result = engine.search(query, k)
        if not result.is_ok:
            raise RuntimeError(result.error.message)
        value: SearchResult = result.value
        return {
            "query": value.query,
            "k": value.k,
            "totalMatched": value.total_matched,
            "results": [
                {
                    "docId": hit.doc_id,
                    "chunkId": hit.chunk_id,
                    "title": hit.title,
                    "heading": hit.heading,
                    "score": hit.score,
                    "citation": hit.citation,
                    "text": hit.text,
                }
                for hit in value.results
            ],
        }

    @server.tool()
    def get_document(docId: str) -> dict:
        """Fetch a full corpus document by id."""
        result = engine.get_document(docId)
        if not result.is_ok:
            raise RuntimeError(result.error.message)
        document: Document = result.value
        chunk_count = sum(1 for chunk in engine.chunks if chunk.doc_id == docId)
        return {
            "docId": document.doc_id,
            "title": document.title,
            "tags": list(document.tags),
            "chunkCount": chunk_count,
            "markdown": document.markdown,
            "source": document.source,
        }

    @server.tool()
    def answer(query: str, k: int = 3) -> dict:
        """Answer a question using only corpus content. Extractive, with citations."""
        result = engine.answer(query, k)
        if not result.is_ok:
            raise RuntimeError(result.error.message)
        value: Answer = result.value
        return {
            "query": value.query,
            "answer": value.answer,
            "citations": list(value.citations),
            "grounded": value.grounded,
        }

    return server
