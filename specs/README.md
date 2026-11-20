# Specs — Spec-Driven Development

This directory is the **source of truth for what this repository must prove**. Code is a consequence of a spec.

The chain is deliberately small, has no tooling dependency, and mirrors the shape used in `IT_CrudWorks`:

```
brief (why) → constitution (rules) → spec (what) → plan (how) → tasks (steps)
   → red test → implementation → validation → evidence → learning
```

## 1. Artifacts

| Artifact | Answers | Owner | Location |
|---|---|---|---|
| Brief | Why does this exist? | Orchestrator | `README.md` §What this proves, `docs/concepts.md` |
| Constitution | What is never negotiable? | Orchestrator | `specs/constitution.md` |
| Spec | What must the system do? | Architect | `specs/NNN-*/spec.md` |
| Plan | How will we build it? | Architect | `specs/NNN-*/plan.md` |
| Tasks | What is the next small step? | Implementers | `specs/NNN-*/tasks.md` |
| Code and tests | Does it work? | Implementers | `src/`, `tests/` |
| Evidence | How do we know? | Every agent | `docs/ai/`, `docs/reviews/`, CI logs |

One artifact, one owner. A behavior change starts in the spec.

## 2. Lifecycle

| Status | Meaning | Who moves it |
|---|---|---|
| `draft` | being written, not safe to implement | Architect |
| `approved` | criteria are testable and scope is closed | Orchestrator |
| `implementing` | tasks in progress | Orchestrator |
| `implemented` | every criterion has evidence | Conformance engineer |
| `retired` | replaced; link the successor | Architect |

A spec is **approved** only when every acceptance criterion is testable (Given/When/Then), in-scope and out-of-scope
are explicit, the contract is unambiguous, requirements are listed by ID, and open questions are resolved or marked
as accepted risks.

Implementation never starts on a `draft`.

## 3. Naming

- Folder: `NNN-kebab-case` (`001-corpus`).
- Spec `SPEC-NNN` · Plan `PLAN-NNN` · Acceptance criterion `AC-NNN-XX` · Task `T-NNN-XX` · Requirement `R-XX`.
- Evidence entry: `docs/ai/NNN-topic.md`.
- Numbers are never reused.

## 4. Scenarios, not wishes

```md
### AC-001-03 — A zero-match query returns no chunks
- **Given** the corpus is loaded
- **When** `search("kubernetes helm chart")` is called
- **Then** `results` is empty and `totalMatched` is `0`
```

Avoid "search should be good". Name the input, the observable output, and the exact value.

## 5. Traceability

Every spec lists the requirement IDs it satisfies. The orchestrator keeps `docs/traceability.md` current. A
requirement is done only when a spec, a test and real evidence exist.

## 6. Change protocol

When behavior changes after approval:

1. Add a **Change log** entry to the spec: date, reason, approver.
2. Update the acceptance criteria and, if needed, the contract.
3. Update affected tasks and tests.
4. Record the change in `docs/ai/` and, if architectural, in an ADR.

Never "fix" code to match a new idea without this. The spec is the contract.

## 7. Templates

Copy `specs/_template/` when starting a capability: `spec.md`, `plan.md`, `tasks.md`. Keep a spec under ~150 lines;
if it needs more, split it.

## 8. Current specs

| ID | Capability | Status | Requirements | Waves |
|---|---|---|---|---|
| SPEC-000 | Product definition: the claims this repo must prove | approved | R-01…R-10 | W0 |
| SPEC-001 | Corpus and golden vectors | approved | R-04, R-06 | W1 |
| SPEC-002 | Retrieval core and PoC surface (CLI + REST) | implemented | R-02, R-03, R-05, R-07 | W2 |
| SPEC-003 | MCP servers (Python + .NET) and cross-language parity | draft (written at wave start) | R-01, R-03 | W3 |
| SPEC-004 | Automation, containers and free-tier deploy | draft (written at wave start) | R-08, R-09 | W4 |
| SPEC-005 | CI and contract guards | draft (written at wave start) | R-10 | W5 |

Specs 003–005 are written at the start of their wave, not in advance. A spec written before its inputs exist is
fiction, and fiction in a spec is worse than no spec.

## 9. The PoC milestone

SPEC-002 is the proof of concept: corpus → retrieval → grounded extractive answer, exposed through a CLI and the REST
facade, with no MCP server anywhere. If SPEC-002 is green, the RAG works. SPEC-003 then adds a second door and the
parity proof on top of a core that already stands on its own.
