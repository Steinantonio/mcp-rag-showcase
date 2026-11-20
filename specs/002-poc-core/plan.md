# PLAN-002 — Retrieval core and PoC surface

- **Spec:** `specs/002-poc-core/spec.md`
- **Status:** approved
- **Owner:** architect
- **Last updated:** 2026-11-20

## 1. Architecture impact

| Layer | Change | Files |
|---|---|---|
| `core` | new: tokenizer, chunker, bm25, engine, error type | `src/mcp_rag_py/core/*.py` |
| `adapters/outbound` | new: filesystem corpus source | `src/mcp_rag_py/adapters/corpus_fs.py` |
| `adapters/inbound` | new: REST facade (FastAPI) | `src/mcp_rag_py/adapters/rest.py` |
| `apps` | new: CLI and app factory (composition root) | `src/mcp_rag_py/apps/cli.py`, `apps/http.py` |
| tests | unit + golden + REST + architecture | `tests/unit/*`, `tests/conformance/*`, `tests/arch/*` |

Must **not** change: nothing exists yet. What must not appear: any import of `mcp` in this wave.

## 2. Contract

Implements `docs/tool-contract.md` §2 (chunking), §3 (tokenization), §4 (BM25), §5 (tools) and §6 (errors), and
publishes `docs/openapi.yaml`. The contract is implemented, not reinterpreted: the regex, the constants and the
tie-break order are copied verbatim.

## 3. Test strategy

| Layer | What is proven | Where |
|---|---|---|
| Unit | tokenizer, chunker, BM25 math, tie-break, sentence selection | `tests/unit/` |
| Contract | the 10 golden cases, the miss case, extractive property | `tests/conformance/test_golden.py` |
| Integration | REST status codes, payload shape, OpenAPI document | `tests/integration/test_rest.py` |
| Architecture | `core` imports nothing from the outside | `tests/arch/test_boundaries.py` (import-linter) |
| Property | determinism across processes | `tests/integration/test_determinism.py` |

## 4. Task order

1. `core/errors.py` — `RagError` codes from contract §6.
2. `core/tokenizer.py` — test first (AC-002-01), then implement.
3. `core/chunker.py` — test first (AC-002-02), including the 1200-character packing rule.
4. `core/bm25.py` — test first: a hand-computed score for a 3-chunk fixture, plus tie-break ordering.
5. `core/engine.py` — `search`, `get_document`, `answer`; test with a 3-document fixture.
6. `adapters/corpus_fs.py` — restricted front matter parser, no YAML library.
7. `apps/cli.py` — `ingest` and `query` subcommands.
8. `adapters/rest.py` + `apps/http.py` — the four endpoints, error mapping.
9. Golden suite against the real corpus (AC-002-03, AC-002-04).
10. Architecture test and determinism test (AC-002-06, AC-002-07).
11. OpenAPI diff check (AC-002-08).

## 5. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Golden cases fail because an expectation is wrong | blocks the wave | re-derive by hand, inspect the corpus, fix the expectation or the case — never the algorithm |
| Front matter parser too permissive | silent corpus corruption | restricted grammar + explicit test for unknown keys being ignored |
| FastAPI's generated OpenAPI differs in naming | drift check red | align operation ids with `docs/openapi.yaml`, or fix the spec if the app is right |
| Sentence splitting differs from the contract | `answer` tests flaky | contract states the rule and conformance for `answer` asserts citations, not prose |

## 6. Definition of done for this wave

- [ ] `pytest` green, including the 10 golden cases and the architecture test.
- [ ] `python -m mcp_rag_py ingest` prints document, chunk and `avgdl` counts.
- [ ] `python -m mcp_rag_py query "how do I rotate an api key"` prints ranked citations.
- [ ] `uvicorn` serves `/docs` with the four endpoints; `400` and `404` codes match the contract.
- [ ] One local commit: `feat(poc): retrieval core with CLI and REST facade`.
