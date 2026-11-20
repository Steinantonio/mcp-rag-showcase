# SPEC-002 — Retrieval core and PoC surface (CLI + REST)

- **Status:** approved
- **Owner:** architect
- **Approved by:** orchestrator (owner decision, 2026-11-20)
- **Requirements:** R-02, R-03, R-05, R-07
- **ADRs:** 0001, 0003, 0004
- **Contract impact:** implements `docs/tool-contract.md` §2–§5; publishes `docs/openapi.yaml`
- **Last updated:** 2026-11-20

## 1. Problem

Before any MCP server exists, the retrieval engine has to work and be observable. This is the proof-of-concept
milestone: corpus → chunks → BM25 → ranked citations → extractive answer, reachable from a terminal and a browser.
If this wave is green, the RAG works; MCP is then only a second door.

## 2. Scope

**In scope**

- Python package `mcp_rag_py` with a pure `core` (tokenizer, chunker, BM25, engine).
- Adapters: filesystem corpus source, CLI (`ingest`, `query`), REST facade with OpenAPI.
- Typed errors (`RagError`) crossing the boundary as results, not exceptions.
- Tests: tokenizer, chunker, BM25, engine, golden cases, REST, architecture boundary.

**Out of scope**

- Any MCP server (SPEC-003).
- The .NET implementation (SPEC-003).
- Containers and deployment (SPEC-004).
- Any generative model, embedding or reranker (ADR 0001).

## 3. Glossary

| Term | Meaning |
|---|---|
| Core | Pure functions with no I/O, no framework import, no clock |
| Adapter | Code that translates a protocol to core calls |
| Extractive answer | Up to three source sentences, verbatim, with citations |
| Grounded | `false` when no chunk scored above zero |

## 4. Acceptance criteria

### AC-002-01 — Tokenizer follows the contract exactly

- **Given** the input `"Rotate the API key! (v2)"`
- **When** it is tokenized
- **Then** the result is `["rotate", "the", "api", "key", "v2"]`

### AC-002-02 — Chunker is deterministic and bounded

- **Given** a document with three `##` sections
- **When** it is chunked
- **Then** it yields at least three chunks, ids are `docId#00`, `docId#01`, `docId#02`, and no chunk exceeds 1200
  characters

### AC-002-03 — Golden cases pass

- **Given** the 10 cases in `corpus/golden/queries.json`
- **When** `search` runs for each
- **Then** the returned `docId` sequence equals `expectDocIds` exactly

### AC-002-04 — A miss stays a miss

- **Given** the query `"kubernetes helm chart"`
- **When** `search` runs with `k = 5`
- **Then** `results` is empty, `totalMatched` is `0`, and `answer` returns `grounded: false` with the exact sentence
  `"No content in the corpus matches this question."`

### AC-002-05 — Answers are extractive

- **Given** any grounded answer
- **When** each sentence of `answer` is compared with the chunks named in `citations`
- **Then** every sentence appears verbatim in at least one cited chunk

### AC-002-06 — Determinism

- **Given** the same corpus and query
- **When** `search` runs twice in the same process and once in a fresh process
- **Then** the three JSON payloads are byte-identical

### AC-002-07 — The core has no dependencies on the outside

- **Given** the `mcp_rag_py.core` package
- **When** the architecture test runs
- **Then** no module in `core` imports `fastapi`, `mcp`, `httpx`, `os`, `pathlib` or `sys`

### AC-002-08 — The REST facade matches the committed spec

- **Given** the running app
- **When** `GET /openapi.json` is compared with `docs/openapi.yaml`
- **Then** paths, operation ids and schema names match

### AC-002-09 — Errors are typed and mapped

- **Given** `k = 0` on `GET /api/v1/search`
- **When** the request is served
- **Then** the response is `400` with `error.code = "INVALID_ARGUMENT"`
- **Given** an unknown document id
- **When** `GET /api/v1/documents/does-not-exist` is served
- **Then** the response is `404` with `error.code = "DOC_NOT_FOUND"`

## 5. Rules and invariants

- `core` is pure: no clock, no randomness, no network, no filesystem, no environment.
- One code path: the REST facade and the CLI call the same engine functions.
- Errors are `RagError` values with codes from contract §6; exceptions never cross the boundary.
- No dependency beyond `fastapi`, `uvicorn` and (later) `mcp`. No numpy: 5k tokens do not need it.

## 6. Open questions

| Question | Status | Owner |
|---|---|---|
| Package layout `core/ adapters/ apps/` vs flat modules | resolved: `core/`, `adapters/`, `apps/` | architect |
| Where does the index live | resolved: in memory, built at import of the app, not persisted | architect |

## 7. Change log

| Date | Change | Reason | Approver |
|---|---|---|---|
| 2026-11-20 | Approved | PoC milestone agreed with owner | owner |
