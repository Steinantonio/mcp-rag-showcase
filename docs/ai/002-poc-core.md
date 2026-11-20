# Evidence log 002 — retrieval core and PoC surface

- **Date:** 2026-11-20
- **Agent:** orchestrator + python implementer role
- **Spec / wave:** SPEC-002 / W2
- **Commit:** `feat(poc): retrieval core with CLI and REST facade`

## Prompt (faithful summary)

Implement SPEC-002: a pure Python core (tokenizer, chunker, BM25, engine) with typed errors, a filesystem corpus
adapter, a CLI (`ingest`, `query`, `answer`) and a FastAPI facade described by `docs/openapi.yaml`. No MCP server in
this wave. Every acceptance criterion needs a test; the golden vectors must pass against the real corpus.

## What was built

| Path | Role |
|---|---|
| `src/mcp_rag_py/core/{errors,model,tokenizer,chunker,bm25,engine}.py` | pure core: no I/O, no framework, no clock |
| `src/mcp_rag_py/adapters/corpus_fs.py` | restricted front matter parser, no YAML library |
| `src/mcp_rag_py/adapters/rest.py` | FastAPI facade, DTOs named per the OpenAPI document |
| `src/mcp_rag_py/apps/{config,http,cli}.py` | composition roots and CLI |
| `tests/{unit,conformance,integration,arch}/` | 69 tests |

## What I validated

| Claim | How it was checked | Result |
|---|---|---|
| All tests pass | `python -m pytest` | `69 passed` |
| Golden vectors pass | `pytest tests/conformance` | `28 passed` |
| The core is pure | `lint-imports` | `core is pure ... KEPT`, `1 kept, 0 broken` |
| CLI stats | `python -m mcp_rag_py.apps.cli ingest` | `15 documents, 63 chunks, avgdl 61.06` |
| CLI ranking matches the derivation | `... query "restore a database backup" -k 3` | `ops-backups#00 6.4293`, `ops-data-retention#01 5.9891`, `ops-faq#01 5.9054` |
| HTTP surface serves | `uvicorn mcp_rag_py.apps.http:app --port 8080` | `/health` → 200, `/docs` → 200, `/openapi.json` → the four documented paths |
| Error codes map | `tests/integration/test_rest.py` | `400 INVALID_ARGUMENT`, `404 DOC_NOT_FOUND` |
| Determinism across processes | `tests/integration/test_determinism.py` | byte-identical CLI JSON |

Real `/health` body:

```json
{"status":"ok","contractVersion":1,"version":"0.1.0","uptimeSeconds":4.4,
 "corpus":{"documents":15,"chunks":63,"tokens":3847,"avgChunkTokens":61.06}}
```

## What I corrected

1. **Missing `Err` import** in `engine.py` — every error path raised `NameError`. Caught by the unit tests.
2. **`include_external_packages = true`** missing from the import-linter config — the architecture test failed before
   checking anything, which is the correct failure: a guard that cannot run must not pass silently.
3. **SPEC-001 AC-001-04 contradicted AC-001-06.** The criterion demanded two matching documents for *every* golden
   query, including the deliberate miss. Fixed in the spec with a change-log entry; the test skips that case and
   AC-001-06 covers it.
4. **Contract §3 ambiguity.** `[^\p{L}\p{N}]+` cannot be written in Python's `re` (no `\p{...}`). Both sides now
   implement "Unicode letter or decimal digit" (`str.isalpha() or str.isdecimal()` / `char.IsLetterOrDigit`), which
   is the same set for our corpus. The contract was clarified rather than reinterpreted.

## What I rejected

- **numpy for scoring.** 63 chunks and 3 847 tokens; a Python loop is faster than the import.
- **A YAML parser for front matter.** The restricted grammar is 20 lines in both languages and cannot drift.
- **Returning one chunk per document in `search`.** Tidier demo, broken contract.
- **`httpx2`**, suggested by a Starlette deprecation warning. The warning is cosmetic; adding a dependency to silence
  a warning is how dependency trees rot. It is recorded here instead.

## Files changed

`pyproject.toml`, `src/mcp_rag_py/**`, `tests/**`, `specs/001-corpus/spec.md`, `specs/002-poc-core/tasks.md`,
`docs/traceability.md`, `docs/plan.md`.

## Open risks

- The `answer` output reads like stitched quotes, by design. A reader expecting prose will find it odd; the README
  says so.
- FastAPI's TestClient deprecation warning will become a real breakage at some Starlette major. Tracked here, not
  fixed now.
