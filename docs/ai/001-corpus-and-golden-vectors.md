# Evidence log 001 — corpus and golden vectors

- **Date:** 2026-11-20
- **Agent:** architect (orchestrated)
- **Spec / wave:** SPEC-001 / W1
- **Commit:** `feat(corpus): add operations handbook and golden vectors`

## Prompt (faithful summary)

Build the W1 corpus: 15 authored documents forming an internal operations handbook, 300–600 words each, with
deliberate vocabulary overlap and three near-duplicate clusters, plus ten golden queries whose expected `docId`
sequences are derived from `docs/tool-contract.md` rather than captured from an implementation.

## What the model produced

- 15 documents (`corpus/ops-*.md`), 63 chunks in total, 3847 tokens, `avgdl` 61.06.
- `corpus/README.md` with the corpus rules, the clusters and the freeze policy.
- `corpus/golden/queries.json` with 10 cases, each carrying a `note` explaining why the expectation is what it is.

## What I validated

| Claim | How it was checked | Result |
|---|---|---|
| Exactly 15 documents, unique ids | structural check over `corpus/*.md` | 15 docs, 15 unique |
| Every document yields at least 2 chunks | chunker per contract §2 | minimum 4 chunks |
| No chunk exceeds 1200 characters | chunker per contract §2 | maximum 714 characters |
| Every golden case matches the contract arithmetic | replayed each case through a throwaway BM25 calculator | 10/10 |
| Cluster pairs share ≥20% of the smaller token set | containment over distinct token sets | 0.246 – 0.386 |
| The deliberate miss returns nothing | query with no corpus token | 0 results |
| Every query matches ≥2 distinct documents | token presence per document | 2 – 15 documents |

Command (scratch, not committed): a single-file Node implementation of contract §1–§4, run against `corpus/`.
Result: `21/21 checks passed`, `{ documents: 15, chunks: 63, tokens: 3847, avgdl: 61.06 }`.

## What I corrected

1. **AC-001-05 metric.** The criterion said "shares at least 20% of its distinct tokens", which is ambiguous between
   Jaccard (0.13–0.23, failing) and containment (0.25–0.39, passing). Restated as containment over the smaller set,
   because Jaccard punishes pairs whose vocabularies differ in size. Recorded in the spec change log.
2. **One golden query.** `"roll back a bad deployment"` ranked `ops-deployments#01` first but two `ops-onboarding`
   chunks second and third, because "deployment" is a shared word and the onboarding section is short. The ranking
   was defensible under the contract and useless as a probe, so the *query* changed to
   `"roll back the previous artifact"`. The algorithm was not touched. Recorded in the change log.

## What I rejected

- **Adding a stopword list** to fix queries like `"how long do we keep backups"` (which ranks
  `ops-monitoring#03` first because of "we do not monitor"). A stopword list is language-specific, breaks the
  language-agnostic tokenizer, and hides the real limitation. Instead the failure is documented in the README as
  what lexical retrieval looks like when it is wrong.
- **Capturing the calculator's output as the expectations.** The calculator is a check, not an oracle: it shares the
  spec's assumptions, so its agreement proves arithmetic, not correctness. Every case was reasoned from the
  documents first.
- **Making `search` return at most one chunk per document.** It would make the demo look tidier and would break
  contract §5 for no behavioral reason.

## Files changed

- `corpus/*.md` (15 documents), `corpus/README.md`, `corpus/golden/queries.json`
- `specs/001-corpus/spec.md` (AC-001-05 wording, change log)
- `specs/001-corpus/tasks.md` (status)
- `docs/traceability.md` (R-04, R-06)

## Open risks

- The corpus is now frozen. Any edit invalidates all ten expectations; that is intended and documented.
- Three golden cases put a different document second than a human would choose (`ops-changelog` twice). They are
  kept deliberately: they pin the behavior that vocabulary overlap produces, which is what a parity test needs.
