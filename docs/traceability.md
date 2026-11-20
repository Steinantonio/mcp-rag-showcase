# Requirement traceability

Every requirement from `specs/000-product/spec.md` mapped to the spec that implements it and the evidence that proves
it. A requirement is `done` only when the evidence exists and is real.

**Status legend:** `todo` · `proven` · `accepted risk` (documented, not proven)

| Req | Statement | Spec | Evidence | Status |
|---|---|---|---|---|
| R-01 | Two independent MCP servers (.NET, Python) expose the same three tools | SPEC-003 | parity runner | todo |
| R-02 | Retrieval is deterministic for the same corpus and query | SPEC-002 | `tests/integration/test_determinism.py` (byte-identical across processes) | proven |
| R-03 | Both implementations return the same `docId` sequence per golden query | SPEC-003 | `tests/conformance/` | todo |
| R-04 | The corpus is authored here and auditable by hand | SPEC-001 | `corpus/*.md`, `corpus/README.md`, 21/21 shape checks | proven |
| R-05 | Answers are extractive and always carry citations | SPEC-002 | `tests/unit/test_engine.py::test_answer_is_extractive_ac_002_05` | proven |
| R-06 | A query with no lexical match returns zero chunks | SPEC-001, SPEC-002 | golden `no-match` + `test_search_with_no_lexical_match_returns_nothing` | proven |
| R-07 | The core imports no framework, transport or filesystem API | SPEC-002 | `lint-imports`: `1 kept, 0 broken` | proven (Python; .NET in SPEC-003) |
| R-08 | The system runs in containers from one compose file | SPEC-004 | CI `containers` job | todo |
| R-09 | Deployment costs nothing and requires no secret | SPEC-004 | `docs/qa/deploy.md`, live URL | todo |
| R-10 | CI verifies build, tests, parity, containers, IaC and contract drift | SPEC-005 | `.github/workflows/ci.yml` | todo |

## Accepted risks

| Risk | Why accepted | Where stated |
|---|---|---|
| Retrieval quality is not measured | needs a labeled relevance set; out of scope for a demo | README §Honest limitations |
| No semantic matching | embeddings do not fit the free tier; ADR 0001 | README, ADR 0001 |
| The .NET server has no public URL | one free service only; ADR 0003 | ADR 0003 |
| `answer` conformance is looser than `search` | sentence splitting differs across standard libraries | `docs/tool-contract.md` §7 |

*Updated at the end of every wave by the orchestrator.*
