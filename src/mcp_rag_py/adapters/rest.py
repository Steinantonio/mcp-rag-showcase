"""REST facade described by docs/openapi.yaml.

A serialization layer, not a second implementation: every handler calls the same engine method the MCP tools call.
No ranking, no chunking, no tokenizing here.
"""

from __future__ import annotations

import time

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field

from mcp_rag_py import CONTRACT_VERSION, __version__
from mcp_rag_py.core.engine import MAX_K_ANSWER, MAX_K_SEARCH, MAX_QUERY_CHARS, RagEngine
from mcp_rag_py.core.errors import ErrorCode, RagError
from mcp_rag_py.core.model import Answer as CoreAnswer
from mcp_rag_py.core.model import Document as CoreDocument
from mcp_rag_py.core.model import SearchResult

_STATUS = {
    ErrorCode.INVALID_ARGUMENT: 400,
    ErrorCode.DOC_NOT_FOUND: 404,
    ErrorCode.CORPUS_UNAVAILABLE: 503,
    ErrorCode.INTERNAL: 500,
}


class CorpusStatsModel(BaseModel):
    documents: int
    chunks: int
    tokens: int
    avgChunkTokens: float


class Health(BaseModel):
    status: str = "ok"
    contractVersion: int = CONTRACT_VERSION
    version: str = __version__
    uptimeSeconds: float
    corpus: CorpusStatsModel


class Chunk(BaseModel):
    docId: str
    chunkId: str
    title: str
    heading: str
    score: float
    citation: str
    text: str


class SearchResponse(BaseModel):
    query: str
    k: int
    totalMatched: int
    results: list[Chunk]


class Document(BaseModel):
    docId: str
    title: str
    tags: list[str]
    chunkCount: int
    markdown: str
    source: str


class AnswerRequest(BaseModel):
    query: str = Field(min_length=1, max_length=MAX_QUERY_CHARS)
    k: int = Field(default=3, ge=1, le=MAX_K_ANSWER)


class AnswerResponse(BaseModel):
    query: str
    answer: str
    citations: list[str]
    grounded: bool


class ErrorBody(BaseModel):
    code: str
    message: str


class Error(BaseModel):
    error: ErrorBody


def _error_response(error: RagError) -> JSONResponse:
    return JSONResponse(status_code=_STATUS[error.code], content=error.to_payload())


def _to_search_response(result: SearchResult) -> SearchResponse:
    return SearchResponse(
        query=result.query,
        k=result.k,
        totalMatched=result.total_matched,
        results=[
            Chunk(
                docId=hit.doc_id,
                chunkId=hit.chunk_id,
                title=hit.title,
                heading=hit.heading,
                score=hit.score,
                citation=hit.citation,
                text=hit.text,
            )
            for hit in result.results
        ],
    )


def _to_document_response(document: CoreDocument, chunk_count: int) -> Document:
    return Document(
        docId=document.doc_id,
        title=document.title,
        tags=list(document.tags),
        chunkCount=chunk_count,
        markdown=document.markdown,
        source=document.source,
    )


def _to_answer_response(answer: CoreAnswer) -> AnswerResponse:
    return AnswerResponse(
        query=answer.query,
        answer=answer.answer,
        citations=list(answer.citations),
        grounded=answer.grounded,
    )


def build_app(
    engine: RagEngine,
    *,
    started_at: float | None = None,
    lifespan: object | None = None,
) -> FastAPI:
    started = time.monotonic() if started_at is None else started_at

    app = FastAPI(
        title="mcp-rag-showcase REST facade",
        version="1.0.0",
        summary="Read-only HTTP view over the same retrieval engine exposed by both MCP servers.",
        description=(
            "This is a facade, not the product. The product is the MCP tool surface described in "
            "docs/tool-contract.md. These endpoints exist so a human can evaluate the engine in a browser "
            "without installing an MCP client. Responses come from the identical code path used by the tools."
        ),
        license_info={"name": "MIT"},
        lifespan=lifespan,
    )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, __: RequestValidationError) -> JSONResponse:
        return _error_response(RagError(ErrorCode.INVALID_ARGUMENT, "invalid request arguments"))

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        """A bare domain should not answer 404. Humans land on Swagger, scripts read /openapi.json."""
        return RedirectResponse(url="/docs", status_code=307)

    @app.get(
        "/health",
        response_model=Health,
        operation_id="getHealth",
        tags=["health"],
        summary="Liveness and corpus stats",
        responses={503: {"model": Error}},
    )
    def get_health() -> Health:
        stats = engine.stats()
        return Health(
            uptimeSeconds=round(time.monotonic() - started, 1),
            corpus=CorpusStatsModel(
                documents=stats.documents,
                chunks=stats.chunks,
                tokens=stats.tokens,
                avgChunkTokens=stats.avg_chunk_tokens,
            ),
        )

    @app.get(
        "/api/v1/search",
        response_model=SearchResponse,
        operation_id="search",
        tags=["retrieval"],
        summary="Ranked chunks for a query",
        responses={400: {"model": Error}},
    )
    def search(
        q: str = Query(..., min_length=1, max_length=MAX_QUERY_CHARS),
        k: int = Query(5, ge=1, le=MAX_K_SEARCH),
    ):
        result = engine.search(q, k)
        if not result.is_ok:
            return _error_response(result.error)
        return _to_search_response(result.value)

    @app.get(
        "/api/v1/documents/{docId}",
        response_model=Document,
        operation_id="getDocument",
        tags=["documents"],
        summary="Full document by id",
        responses={404: {"model": Error}},
    )
    def get_document(docId: str):
        result = engine.get_document(docId)
        if not result.is_ok:
            return _error_response(result.error)
        chunk_count = sum(1 for chunk in engine.chunks if chunk.doc_id == docId)
        return _to_document_response(result.value, chunk_count)

    @app.post(
        "/api/v1/answer",
        response_model=AnswerResponse,
        operation_id="answer",
        tags=["retrieval"],
        summary="Extractive answer with citations",
        responses={400: {"model": Error}},
    )
    def answer(payload: AnswerRequest):
        result = engine.answer(payload.query, payload.k)
        if not result.is_ok:
            return _error_response(result.error)
        return _to_answer_response(result.value)

    return app
