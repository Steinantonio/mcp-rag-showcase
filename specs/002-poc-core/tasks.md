# TASKS-002 — Retrieval core and PoC surface

- **Spec:** `specs/002-poc-core/spec.md`
- **Plan:** `specs/002-poc-core/plan.md`
- **Status:** approved
- **Last updated:** 2026-11-20

## Status legend

`todo` → `red` → `green` → `done` → `blocked`

## Tasks

| ID | Task | Owner | Depends on | Test / evidence | Status |
|---|---|---|---|---|---|
| T-002-01 | `core/errors.py` with the contract §6 codes | python-implementer | — | import test | todo |
| T-002-02 | Tokenizer: test then implementation | python-implementer | T-002-01 | `test_tokenizer.py` (AC-002-01) | todo |
| T-002-03 | Chunker: test then implementation | python-implementer | T-002-02 | `test_chunker.py` (AC-002-02) | todo |
| T-002-04 | BM25: hand-computed fixture, then implementation | python-implementer | T-002-02 | `test_bm25.py` | todo |
| T-002-05 | Engine: `search`, `get_document`, `answer` | python-implementer | T-002-03, T-002-04 | `test_engine.py` (AC-002-05) | todo |
| T-002-06 | Filesystem corpus adapter with restricted front matter | python-implementer | T-002-03 | `test_corpus_fs.py` | todo |
| T-002-07 | Corpus shape assertions (AC-001-01…05) | conformance-engineer | T-002-06 | `test_corpus_shape.py` | todo |
| T-002-08 | CLI `ingest` and `query` | python-implementer | T-002-05, T-002-06 | manual run output | todo |
| T-002-09 | REST facade + error mapping | python-implementer | T-002-05 | `test_rest.py` (AC-002-08, AC-002-09) | todo |
| T-002-10 | Golden suite against the real corpus | conformance-engineer | T-002-09 | `test_golden.py` (AC-002-03, AC-002-04) | todo |
| T-002-11 | Architecture test with import-linter | conformance-engineer | T-002-05 | `test_boundaries.py` (AC-002-07) | todo |
| T-002-12 | Determinism test across processes | conformance-engineer | T-002-08 | `test_determinism.py` (AC-002-06) | todo |
| T-002-13 | OpenAPI drift check against `docs/openapi.yaml` | conformance-engineer | T-002-09 | `test_openapi.py` (AC-002-08) | todo |

## Notes

- T-002-01 through T-002-05 are pure functions: every one has a failing test before implementation.
- T-002-07 belongs here, not in SPEC-001, because it needs the real chunker and tokenizer.
- No task in this wave may import `mcp`. If one seems to need it, the spec is wrong.
