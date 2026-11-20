# TASKS-002 — Retrieval core and PoC surface

- **Spec:** `specs/002-poc-core/spec.md`
- **Plan:** `specs/002-poc-core/plan.md`
- **Status:** implemented
- **Last updated:** 2026-11-20

## Status legend

`todo` → `red` → `green` → `done` → `blocked`

## Tasks

| ID | Task | Owner | Depends on | Test / evidence | Status |
|---|---|---|---|---|---|
| T-002-01 | `core/errors.py` with the contract §6 codes | python-implementer | — | `tests/unit/test_engine.py::test_get_document_unknown_id_is_a_typed_error` | done |
| T-002-02 | Tokenizer: test then implementation | python-implementer | T-002-01 | `tests/unit/test_tokenizer.py` (5 tests, AC-002-01) | done |
| T-002-03 | Chunker: test then implementation | python-implementer | T-002-02 | `tests/unit/test_chunker.py` (5 tests, AC-002-02) | done |
| T-002-04 | BM25: hand-computed fixture, then implementation | python-implementer | T-002-02 | `tests/unit/test_bm25.py` (6 tests, `ln 2` fixture) | done |
| T-002-05 | Engine: `search`, `get_document`, `answer` | python-implementer | T-002-03, T-002-04 | `tests/unit/test_engine.py` (8 tests, AC-002-05) | done |
| T-002-06 | Filesystem corpus adapter with restricted front matter | python-implementer | T-002-03 | `tests/conformance/test_corpus_shape.py` (8 tests) | done |
| T-002-07 | Corpus shape assertions (AC-001-01…07) | conformance-engineer | T-002-06 | `test_corpus_shape.py` | done |
| T-002-08 | CLI `ingest`, `query`, `answer` | python-implementer | T-002-05, T-002-06 | real output in `docs/ai/002-poc-core.md` | done |
| T-002-09 | REST facade + error mapping | python-implementer | T-002-05 | `tests/integration/test_rest.py` (9 tests) | done |
| T-002-10 | Golden suite against the real corpus | conformance-engineer | T-002-09 | `tests/conformance/test_golden.py` (20 tests: 10 search + 10 grounded) | done |
| T-002-11 | Architecture test with import-linter | conformance-engineer | T-002-05 | `tests/arch/test_boundaries.py` (AC-002-07) | done |
| T-002-12 | Determinism test across processes | conformance-engineer | T-002-08 | `tests/integration/test_determinism.py` (AC-002-06) | done |
| T-002-13 | OpenAPI drift check against `docs/openapi.yaml` | conformance-engineer | T-002-09 | `tests/integration/test_openapi.py` (4 tests, AC-002-08) | done |

## Notes

- 69 tests pass; `lint-imports` reports `1 kept, 0 broken`.
- Two implementation defects were found and fixed inside the wave: a missing `Err` import in `engine.py`, and
  `include_external_packages = true` missing from the import-linter configuration. Both would have been caught by
  CI, which is the point of CI.
- One spec inconsistency was found by the new assertions and fixed at the spec level (SPEC-001 AC-001-04), not by
  weakening the test.
