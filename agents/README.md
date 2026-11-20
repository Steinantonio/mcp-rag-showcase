# Agents — roster and conventions

Six agent definitions live here. This file is the contract for how they are written, routed and kept from stepping
on each other. Run `scripts/sync-agents.ps1` after any edit to refresh the copies in
`C:\Trabalho\.opencode\agents\mcp_rag_showcase\`.

## 1. Why a lean team

The repository is small but carries six distinct risks: architectural direction, protocol surface, retrieval
correctness in two languages, equivalence between them, and delivery. The roster mirrors those risks, not an org
chart.

- One owner per artifact.
- No agent whose only job is to restate another.
- No coordinator of coordinators.
- The orchestrator is the only primary agent; everyone else is a subagent.

## 2. Roster

| File | OpenCode ID (when synced) | Mode | Core question | Owns | Does not do |
|---|---|---|---|---|---|
| `orchestrator.md` | `mcp_rag_showcase/orchestrator` | primary | What is the smallest correct next step? | plan, delegation, integration, local commits | deep specialist work; unverified claims |
| `architect.md` | `mcp_rag_showcase/architect` | subagent | What is the right shape, and why? | specs, ADRs, tool contract, OpenAPI, test strategy | production code |
| `python-implementer.md` | `mcp_rag_showcase/python-implementer` | subagent | Does the Python service behave correctly? | `src/mcp_rag_py/**`, `tests/unit/**` | changing the contract; .NET code |
| `dotnet-implementer.md` | `mcp_rag_showcase/dotnet-implementer` | subagent | Does the .NET service behave correctly? | `src/Mcp.Rag.Dotnet/**`, `tests/Mcp.Rag.Dotnet.Tests/**` | changing the contract; Python code |
| `conformance-engineer.md` | `mcp_rag_showcase/conformance-engineer` | subagent | How do we prove equivalence? | golden vectors, parity runner, CI, containers, deploy evidence | rewriting feature code |
| `reviewer.md` | `mcp_rag_showcase/reviewer` | subagent | What would break in review? | severity-ordered findings, verdict | editing the fix |

Plus `adapters/shared-reviewer-pilot.md`, the independent read-only reviewer used as a second opinion on
non-trivial changes.

## 3. Handoff flow

```
Orchestrator
  ├── Architect ──────────> spec / plan / ADR / contract
  ├── Python implementer ─> core + adapters + unit tests
  ├── .NET implementer ───> core + MCP server + unit tests
  ├── Conformance engineer> golden vectors, parity, CI, containers, deploy
  └── Reviewer ───────────> findings + verdict
```

Rules:

- The orchestrator writes the delegation brief and reads the handoff.
- The architect decides the shape; implementers do not change it unilaterally.
- The reviewer never edits code. Findings go back to the owner.
- The conformance engineer never rewrites feature code. Failures go back to the owner.
- The orchestrator integrates and makes the local commit. **Pushing is the owner's action.**

## 4. Agent file anatomy

```yaml
---
description: <1–3 sentences: what it does, when to use it, what it does not do>
mode: primary | subagent
permissions:
  - action: edit
    resource: "*"
    effect: deny
  - action: edit
    resource: "<allowed path>"
    effect: allow
  - action: shell
    resource: "<allowed command>"
    effect: allow
  - action: subagent
    resource: "*"
    effect: deny
---
```

Body sections, in order: **Mission**, **Required context**, **Responsibilities**, **Non-goals**, **Process**,
**Evidence rules**, **Output format**, **Checklist**. Keep it under ~120 lines. A long prompt is not a better
prompt; a clear boundary is.

## 5. Permission design

Deny by default, then allow the smallest zone that lets the agent do its job.

| Agent | Edit | Shell | Subagent |
|---|---|---|---|
| Orchestrator | project and docs paths; deny `.git`, secrets | allow; ask before destructive | allow |
| Architect | `docs/**`, `specs/**` | read-only checks | deny |
| Python implementer | `src/mcp_rag_py/**`, `tests/unit/**`, `pyproject.toml` | allow `python`, `pytest`, `pip` | deny |
| .NET implementer | `src/Mcp.Rag.Dotnet/**`, `tests/Mcp.Rag.Dotnet.Tests/**`, `*.sln` | allow `dotnet` | deny |
| Conformance engineer | `corpus/golden/**`, `tests/conformance/**`, `tests/arch/**`, `.github/**`, `infra/**`, `scripts/**` | allow build/test/docker/bicep | deny |
| Reviewer | `docs/reviews/**` | read-only checks | deny |

Resources are workspace-prefixed (`mcp-rag-showcase/...`) because the OpenCode workspace root is `C:\Trabalho`.

## 6. Callability

The canonical files live in `agents/`. OpenCode discovers agents under `<workspace>/.opencode/agents/`, so
`scripts/sync-agents.ps1` copies the six definitions to `C:\Trabalho\.opencode\agents\mcp_rag_showcase\`.

- Restart OpenCode or start a new session after syncing.
- Edit the canonical files in `agents/`, never the copies.
- Re-run the script after every agent change; drift is otherwise silent.

## 7. Naming

Lowercase kebab-case, no numeric prefix. Each file ends with `Last reviewed: YYYY-MM-DD` and the trigger for the
next review. When scope changes, update this README and the agent file in the same change. Do not fix an agent by
making it broader; fix the boundary.
