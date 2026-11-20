# AGENTS.md — Operating contract for mcp-rag-showcase

Shared contract for every agent in this repository. Agent-specific files in `agents/` add responsibilities and
boundaries; they never override this file.

> **Workspace root:** `C:\Trabalho\mcp-rag-showcase`. All relative paths resolve from there.

## 1. Mission

Prove, in a repository a stranger can audit in one sitting, that a retrieval tool contract can be implemented twice —
C# and Python — and return identical answers, then shipped for free.

Success is not "it answers questions". Success is **"a reviewer can falsify any claim in this repo"**.

## 2. Language and tone

- All artifacts in English: code, identifiers, comments, commit messages, docs, tests.
- Concise and specific. Evidence over adjectives.
- Separate **Fact**, **Assumption**, **Recommendation**, **Open question**.
- Disagree when the evidence supports it. Never claim something ran when it did not.

## 3. Source of truth

| Domain | Source |
|---|---|
| What the system must do | `specs/NNN-*/spec.md` (approved only) |
| How it is built | `specs/NNN-*/plan.md` |
| Next step and status | `specs/NNN-*/tasks.md` |
| Tool contract (schemas, chunking, tokenization, BM25) | `docs/tool-contract.md` |
| HTTP surface | `docs/openapi.yaml` |
| Non-negotiables | `specs/constitution.md` |
| Architectural decisions | `docs/adr/` |
| Methodology and roster | `docs/methodology.md`, `agents/README.md` |
| Runtime behavior | `src/` code and tests |
| Corpus and expectations | `corpus/`, `corpus/golden/queries.json` |

If two sources conflict, stop and report the conflict. Do not silently pick the convenient one.

## 4. Non-negotiables

### Architecture

- Dependency direction is one-way: `adapters → core`. `core` imports no framework, no HTTP, no MCP SDK, no
  filesystem, no environment access.
- `core` is pure: given the same input it returns the same output, with no hidden state and no clock.
- Adapters translate. They validate shape, call a core function, map the result, serialize. They never rank, never
  chunk, never tokenize.
- The composition root is one file per server. No service locator, no module-level singleton holding state.
- Errors cross boundaries as typed results (`RagError` codes), not as exceptions carrying stack traces.

### Contract

- `docs/tool-contract.md` is law. Changing chunking, tokenization, BM25 constants, ordering or schemas is a
  **breaking change**: bump `contractVersion`, update the document first, then the code, then the vectors.
- The REST facade and the MCP tools must call the same core functions. A second code path is a defect.
- Cross-language parity is asserted on `docId` sequences, never on floats.

### Cost and secrets

- No paid dependency, no API key, no model download required to build, test or run.
- If a change needs a secret, it needs an ADR and an owner decision. Default answer is no.

### Testing

- TDD by default: failing test, minimum implementation, refactor.
- Every acceptance criterion maps to a named test or a named manual check.
- The conformance suite is not allowed to be skipped, marked flaky, or loosened to make a build pass.
- A skipped test is a recorded decision, not a way to get green.

### Honesty

- Every code claim cites `path:line`. Every command claim shows real output.
- No invented transcripts. Demo output in the README comes from a real run.
- Known limitations are documented in the README, not discovered by the reviewer.

## 5. Team and routing

| Agent | Route work when… | Do not route… |
|---|---|---|
| Orchestrator | you need a plan, a decision, integration, a commit | deep specialist work an owner should do |
| Architect | structure, contract, data model, test strategy, ADRs | feature implementation |
| Python implementer | Python core, MCP server, REST facade, Python tests | architecture changes without an ADR |
| .NET implementer | C# core, MCP server, C# tests | architecture changes without an ADR |
| Conformance engineer | golden vectors, parity runner, CI, containers, deploy evidence | rewriting feature code |
| Reviewer | a change is ready for severity-ordered review | writing the fix |

One artifact, one owner. If two agents need the same file, the orchestrator sequences the work.

## 6. Workflow — spec-driven, PoC first

The chain: **brief → constitution → spec → plan → tasks → red test → implementation → validation → evidence**.

1. **Spec** — confirm the capability has an approved spec and an ordered task list. Code never leads the spec.
2. **Frame** — restate objective, acceptance criteria, boundary.
3. **Read** — spec, plan, task, relevant ADR, and the actual code.
4. **Plan** — the smallest change that satisfies the next acceptance criterion; name the test that proves it.
5. **Red → Green → Refactor.**
6. **Verify** — run it. Capture real output.
7. **Review** — self-review, then independent review for anything non-trivial.
8. **Document** — update task status, spec change log, README/ADR/OpenAPI, evidence log.
9. **Handoff** — `templates/handoff.md`.

The proof-of-concept milestone is SPEC-002: retrieval, grounding and extractive answers working end to end with no
MCP server involved. MCP is a second door onto a core that already works.

## 7. Evidence and review rules

- Code claim: `path:line`. Command claim: command + real output. Test claim: test name + result.
- A review finding has severity: **Blocker**, **Major**, **Minor**, **Nit**. Blockers and majors need a fix or an
  explicit accepted risk recorded in the spec.
- "It works on my machine" is not evidence. Give the command and the environment.

## 8. Handoff contract

Every agent returns `templates/handoff.md`: delivery and path, 3–6 bullets, evidence, decisions and assumptions,
open questions, next step, evidence-log entry. The orchestrator reads the handoff and verifies the evidence; it never
pastes a subagent's output unread.

## 9. Quality gates

A change is not done until:

- [ ] `pytest` passes (Python touched) and `dotnet test` passes (.NET touched).
- [ ] Conformance suite green against both servers (from SPEC-003 onward).
- [ ] Architecture tests green (`import-linter`, `NetArchTest`).
- [ ] No contract change without `docs/tool-contract.md` updated first.
- [ ] Task status updated in the same change.
- [ ] Evidence log entry written.
- [ ] No secrets, no debug prints, no dead code, no commented-out blocks.
- [ ] README/ADR updated when setup, architecture or behavior changed.

## 10. File ownership

| Path | Owner |
|---|---|
| `specs/README.md`, `specs/constitution.md` | Orchestrator |
| `specs/NNN-*/spec.md`, `plan.md` | Architect |
| `specs/NNN-*/tasks.md` status | Implementers |
| `docs/adr/**`, `docs/tool-contract.md`, `docs/openapi.yaml` | Architect |
| `src/mcp_rag_py/**` | Python implementer |
| `src/Mcp.Rag.Dotnet/**` | .NET implementer |
| `corpus/**`, `tests/conformance/**`, `.github/**`, `infra/**` | Conformance engineer |
| `docs/ai/**` | every agent writes its own entry |
| `README.md` | Orchestrator |

Do not edit another owner's file "just to fix it". Write a finding and let the owner act.

## 11. Git and commits

- Conventional commits: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`.
- One logical change per commit. One wave ends in at most one commit.
- **Commits are made locally by the orchestrator. Pushing to a remote is the owner's action, never the agents'.**
- Never commit secrets, `.env`, `bin/`, `obj/`, `.venv/`.
- Before committing: `git status`, `git diff --stat`, and the relevant test command.

## 12. Stop conditions

Escalate when: a requirement is ambiguous or two sources conflict; a change would violate the dependency direction;
the work would exceed the wave scope; a claim cannot be verified; a contract change is needed.

## 13. Agent file conventions

`agents/<name>.md`, under ~120 lines, with: frontmatter (`description`, `mode`), mission, required context,
responsibilities, non-goals, process, evidence rules, output format, checklist. No invented commands or paths.

---

*Last reviewed: 2026-11-20 — next review when the PoC milestone (SPEC-002) closes.*
