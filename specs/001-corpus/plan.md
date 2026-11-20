# PLAN-001 — Corpus and golden vectors

- **Spec:** `specs/001-corpus/spec.md`
- **Status:** approved
- **Owner:** architect
- **Last updated:** 2026-11-20

## 1. Architecture impact

| Layer | Change | Files |
|---|---|---|
| `core` | none — the corpus is data, not code | — |
| `adapters` | none | — |
| `corpus` | 15 documents + golden file + README | `corpus/*.md`, `corpus/golden/queries.json` |
| tests | none yet; consumed from SPEC-002 onward | `tests/conformance/` (later) |

Nothing in `src/` changes in this wave. That is the point: data first, code second.

## 2. Contract

Implements `docs/tool-contract.md` §1 (corpus format) and produces the data consumed by §7 (conformance). Chunking
behavior itself is implemented in SPEC-002; this wave only guarantees the input shape.

## 3. Test strategy

| Layer | What is proven | Where |
|---|---|---|
| Structural | 15 docs, unique ids, front matter parses, ≥2 chunks each, no chunk > 1200 chars | `tests/corpus/test_corpus_shape.py` (SPEC-002) |
| Statistical | vocabulary overlap and near-duplicate ratio | same file, computed from token sets |
| Contract | every golden case has the required fields and a hand-written expectation | same file |

The corpus tests live with the implementation (SPEC-002) because they need the chunker and tokenizer. This wave
delivers the data plus a manual checklist, and the automated assertions land in the next wave.

## 4. Task order

1. Write `corpus/README.md` — the rules of the corpus and why it freezes.
2. Write the 15 documents, cluster by cluster, keeping the shared vocabulary deliberate.
3. Write the 10 golden cases by reasoning from the documents, before computing anything.
4. Verify each case against the contract by hand: which terms are rare (high IDF), which are everywhere (low IDF),
   which documents are near-duplicates.
5. Record disagreements between reasoning and the expected behavior, and resolve them by re-reading the corpus —
   never by accepting an output.

## 5. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Documents too similar → many ties | ranking decided by tie-break, weak demo | AC-001-05 caps overlap at ~20–40%; each doc has a distinct angle |
| Documents too short → 1 chunk | violates AC-001-02 | each doc has 3–5 H2 sections |
| Expectations wrong | SPEC-002 and SPEC-003 fail for the wrong reason | expectations derived from the spec and re-checked line by line |
| Corpus drifts after approval | all vectors invalid | Constitution Article 7 + explicit "frozen" note in `corpus/README.md` |

## 6. Definition of done for this wave

- [ ] 15 documents exist, each 300–600 words, each with 3–5 H2 sections.
- [ ] `corpus/README.md` explains the rules and the freeze.
- [ ] `corpus/golden/queries.json` has 10 cases covering hit, miss, tie, repeated token and rare-term cases.
- [ ] Manual checklist from §5 of the spec is satisfied.
- [ ] One local commit: `feat(corpus): add operations handbook and golden vectors`.
