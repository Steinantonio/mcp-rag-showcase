# SPEC-000 — Product definition: the claims this repository must prove

- **Status:** approved
- **Owner:** architect
- **Approved by:** orchestrator (owner decision, 2026-11-20)
- **Requirements:** R-01 … R-10
- **ADRs:** 0001, 0002, 0003, 0004
- **Contract impact:** none (defines the frame for all later specs)
- **Last updated:** 2026-11-20

## 1. Problem

Portfolio repositories that claim "MCP server" or "RAG pipeline" are usually unverifiable: one language, one model
call, one screenshot, no test that a stranger can run. This repository exists to make the claim falsifiable — a
reviewer should be able to clone it, break one constant, and watch the right test fail.

## 2. Scope

**In scope**

- A retrieval engine specified precisely enough to be implemented twice without discretionary choices.
- Two MCP servers exposing the same three tools over the same corpus.
- A conformance suite that asserts identical `docId` sequences across languages.
- A REST/OpenAPI facade so a human can evaluate the engine in a browser.
- Containers, PowerShell automation, IaC validated in CI, and a free-tier deployment.

**Out of scope**

- Any generative model, embedding model, reranker or vector database (ADR 0001).
- Authentication, multi-tenancy, persistence, write paths.
- Retrieval-quality metrics (recall@k, MRR) against a labeled relevance set.
- Scale beyond a 15-document corpus.

## 3. Glossary

| Term | Meaning |
|---|---|
| Chunk | A section of a document, at most 1200 characters, identified as `docId#NN` |
| Citation | A chunk identifier, stable across both implementations |
| Extractive answer | Sentences copied verbatim from retrieved chunks, with citations |
| Parity | Both servers return the same `docId` sequence for the same query |
| PoC milestone | SPEC-002: retrieval and answers working with no MCP server involved |

## 4. Requirements

| ID | Requirement | Proven by |
|---|---|---|
| R-01 | Two independent MCP servers (.NET, Python) expose the same three tools | SPEC-003 |
| R-02 | Retrieval is deterministic: same corpus and query give the same ranking | SPEC-002 |
| R-03 | Both implementations return the same `docId` sequence for every golden query | SPEC-003 |
| R-04 | The corpus is authored for this repository and auditable by hand | SPEC-001 |
| R-05 | Answers are extractive and always carry citations | SPEC-002 |
| R-06 | A query with no lexical match returns zero chunks, never a guess | SPEC-001, SPEC-002 |
| R-07 | The core imports no framework, transport or filesystem API | SPEC-002 (architecture test) |
| R-08 | The system runs in containers from one compose file | SPEC-004 |
| R-09 | Deployment costs nothing and requires no secret | SPEC-004 |
| R-10 | CI verifies build, tests, parity, containers, IaC and contract drift | SPEC-005 |

## 5. Acceptance criteria

### AC-000-01 — The claim is falsifiable

- **Given** a clean clone with dependencies installed
- **When** a reviewer changes `k1` from `1.2` to `2.0` in one implementation only
- **Then** the conformance suite fails and names the first query whose `docId` sequence diverged

### AC-000-02 — No secret, no account

- **Given** a machine with .NET 10 and Python 3.12 only
- **When** `scripts/bootstrap.ps1` and `scripts/test.ps1` run
- **Then** both complete with exit code `0` and no network credential is requested

### AC-000-03 — Limitations are stated before they are discovered

- **Given** the README
- **When** a reviewer looks for what the project does not do
- **Then** there is a section listing at least five concrete limitations, including the absence of semantic matching

## 6. Rules and invariants

- The contract (`docs/tool-contract.md`) is the only source of scoring behavior.
- No feature may be added that is listed in the README's "Not built on purpose" without editing that list in the
  same change (Constitution, Article 8).
- Every wave ends with a spec status update and one local commit.

## 7. Open questions

| Question | Status | Owner |
|---|---|---|
| Add an optional local LLM generator? | deferred to W6, requires ADR | owner |
| Add a retrieval-quality metric? | accepted risk: not measured, stated in README | owner |

## 8. Change log

| Date | Change | Reason | Approver |
|---|---|---|---|
| 2026-11-20 | Initial approval | Unblocks SPEC-001 and SPEC-002 | owner |
