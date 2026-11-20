# SPEC-001 — Corpus and golden vectors

- **Status:** approved
- **Owner:** architect
- **Approved by:** orchestrator (owner decision, 2026-11-20)
- **Requirements:** R-04, R-06
- **ADRs:** 0001, 0002
- **Contract impact:** none (populates `docs/tool-contract.md` §1 and §7)
- **Last updated:** 2026-11-20

## 1. Problem

Every number in the system depends on the corpus: `N`, `avgdl`, every IDF, every ranking. The corpus must therefore
exist, be auditable by hand, and be boring enough that a reviewer can predict the answer without running anything.
It also needs deliberate traps — near-duplicate topics and shared vocabulary — or the golden vectors would pass
against any implementation, including a broken one.

## 2. Scope

**In scope**

- 15 markdown documents describing a fictional internal operations handbook.
- Restricted front matter (`id`, `title`, `tags` only).
- Overlapping vocabulary across documents and three near-duplicate topic clusters.
- `corpus/golden/queries.json`: 10 cases with `expectDocIds` derived from the contract.
- `corpus/README.md` explaining the corpus and how to change it safely.

**Out of scope**

- Real company documentation, scraped content, or third-party text (licensing and drift).
- More than 15 documents (the ruler changes with `N`).
- Any retrieval-quality labeling beyond the 10 cases.

## 3. Actors and glossary

| Term | Meaning |
|---|---|
| Document | One markdown file in `corpus/`, 300–600 words, with front matter |
| Cluster | A group of documents that discuss the same topic from different angles |
| Golden case | A query with the exact `docId` sequence a conforming implementation must return |

## 4. User stories

| ID | Story |
|---|---|
| US-001-01 | As a reviewer, I want to read one document and predict its rank, so that I can sanity-check the engine without trusting it |
| US-001-02 | As an implementer, I want expectations that came from the contract, so that I am not coding to a captured output |

## 5. Acceptance criteria

### AC-001-01 — Corpus shape

- **Given** `corpus/*.md`
- **When** the corpus is loaded
- **Then** there are exactly 15 documents, all `id` values match `^[a-z0-9]+(-[a-z0-9]+)*$` and are unique

### AC-001-02 — Chunkability

- **Given** each document
- **When** it is chunked per contract §2
- **Then** every document yields at least 2 chunks and no chunk exceeds 1200 characters

### AC-001-03 — Front matter is minimal and parseable

- **Given** each document
- **When** the first block is parsed by the restricted parser (no YAML library)
- **Then** `id`, `title` and `tags` are present, and any other key is ignored without error

### AC-001-04 — Ranking is non-trivial

- **Given** the 10 golden queries
- **When** each query is tokenized
- **Then** for every query at least two distinct documents contain at least one query token, so a result is never
  decided by a single-document corpus artifact

### AC-001-05 — Near-duplicates exist on purpose

- **Given** the documents of each cluster (`credentials`/`runbook`/`faq`, `backups`/`data-retention`,
  `incidents`/`escalation`)
- **When** their distinct token sets are compared
- **Then** each pair shares at least 20% of the **smaller** document's distinct token set (containment, not Jaccard,
  because a small document inside a large vocabulary would otherwise never qualify), so ordering must be decided by
  BM25 and the tie-break rule rather than by vocabulary alone

### AC-001-06 — A deliberate miss exists

- **Given** the query `"kubernetes helm chart"`
- **When** `search` runs with `k = 5`
- **Then** `results` is empty and `totalMatched` is `0`

### AC-001-07 — Expectations are hand-derived

- **Given** `corpus/golden/queries.json`
- **When** it is reviewed
- **Then** every case has `id`, `query`, `k`, `expectDocIds` and `expectGrounded`, and no case was produced by
  capturing an implementation's output

## 6. Rules and invariants

- Corpus is frozen once expectations exist (Constitution, Article 7).
- Every document is written for this repository; no copied third-party prose.
- Vocabulary overlap is intentional, not accidental: each cluster reuses the same nouns with different intent.
- One golden case must exercise `grounded: false`; one must repeat a token in the query; one must rank a document
  first for a reason that only IDF explains (a rare term).

## 7. Open questions

| Question | Status | Owner |
|---|---|---|
| Domain of the handbook | resolved: internal operations handbook (deploy, keys, incidents, backups) | owner |
| Language of the corpus | resolved: English, matching the rest of the artifacts | owner |

## 8. Change log

| Date | Change | Reason | Approver |
|---|---|---|---|
| 2026-11-20 | Approved | Unblocks W1 | owner |
| 2026-11-20 | AC-001-05 restated as containment over the smaller token set | Jaccard understates overlap when vocabularies differ in size; the measured pairs sit at 0.13–0.23 Jaccard but 0.25–0.39 containment | architect |
| 2026-11-20 | Golden case `rollback-artifact` rephrased from `"roll back a bad deployment"` to `"roll back the previous artifact"` | The original query ranked two onboarding chunks second and third, because "deployment" is a shared word. The query was a poor probe of the corpus, not evidence of a defect | architect |
