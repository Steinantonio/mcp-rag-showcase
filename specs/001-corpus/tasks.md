# TASKS-001 — Corpus and golden vectors

- **Spec:** `specs/001-corpus/spec.md`
- **Plan:** `specs/001-corpus/plan.md`
- **Status:** implementing
- **Last updated:** 2026-11-20

## Status legend

`todo` → `red` → `green` → `done` → `blocked`

## Tasks

| ID | Task | Owner | Depends on | Test / evidence | Status |
|---|---|---|---|---|---|
| T-001-01 | Write `corpus/README.md` (rules, clusters, freeze policy) | architect | — | file reviewed | done |
| T-001-02 | Write the credentials/runbook/faq cluster (3 docs) | architect | T-001-01 | AC-001-02, AC-001-05 | done |
| T-001-03 | Write the incidents/escalation cluster (2 docs) | architect | T-001-01 | AC-001-05 | done |
| T-001-04 | Write the backups/data-retention cluster (2 docs) | architect | T-001-01 | AC-001-05 | done |
| T-001-05 | Write the remaining 8 documents | architect | T-001-01 | AC-001-01, AC-001-02 | done |
| T-001-06 | Derive the 10 golden cases from the documents | architect | T-001-05 | AC-001-07 | done |
| T-001-07 | Cross-check each case by hand (rare terms, ties, misses) | architect | T-001-06 | AC-001-04, AC-001-06 | done |
| T-001-08 | Automated corpus assertions | python-implementer | SPEC-002 | `tests/corpus/test_corpus_shape.py` | todo (moves to SPEC-002) |

## Notes

- T-001-08 is intentionally deferred: the assertions need the chunker and tokenizer, which are SPEC-002 artifacts.
  Writing them here would mean writing a second, throwaway chunker.
- The corpus is frozen after T-001-07. Any later change is a new spec.
- **Process note:** this file was created during W0.5 scaffolding with the wave already executed, so the statuses
  were recorded at the end rather than as the work progressed. From SPEC-002 onward, tasks start as `todo` and are
  updated in the same commit as the change.
