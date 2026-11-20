# SPEC-003 — MCP servers and cross-language parity

- **Status:** implemented
- **Owner:** architect
- **Approved by:** orchestrator (owner decision, 2026-11-20)
- **Requirements:** R-01, R-03
- **ADRs:** 0001, 0002, 0004
- **Contract impact:** additive — adds MCP tool surfaces; no change to scoring, chunking or tokenization
- **Last updated:** 2026-11-20

## 1. Problem

The Python core works. Now the repository must prove the thing it exists to prove: that a second implementation, in a
different language, exposed through the same protocol, returns the same answers for the same queries. That means a C#
port of the core, an MCP tool surface on both sides, a test that compares them, and a container story that shows both
running side by side.

## 2. Scope

**In scope**

- C# implementation of the core: tokenizer, chunker, BM25, engine, typed errors. Same contract, same constants,
  same tie-break.
- MCP tool registration in Python (`mcp` SDK) and C# (`ModelContextProtocol` 2.4.0), both over stdio and streamable
  HTTP.
- Tokenizer differential test: a fixture of 200 strings, both implementations, identical token lists.
- Parity runner: the 10 golden queries against both engines via CLI JSON output, identical `docId` sequences.
- Architecture test in .NET (`NetArchTest`: `Core` references no ASP.NET, no MCP SDK, no filesystem).
- Dockerfiles: `infra/Dockerfile.py`, `infra/Dockerfile.net`.

**Out of scope**

- `compose.yaml` and the orchestration scripts (SPEC-004).
- CI pipeline (SPEC-005).
- HTTP transport for the .NET server's MCP tools (SPEC-004 — the stdio path is proven; HTTP is wired in compose).
- The parity runner comparing MCP JSON-RPC responses directly (SPEC-004 smoke script covers that).

## 3. Glossary

| Term | Meaning |
|---|---|
| Parity runner | A script that executes the same query against both engines and asserts identical `docId` sequences |
| Tokenizer differential | A test fixture of 200 plain strings; both tokenizers run on them and their output lists must match exactly |
| Streamable HTTP | MCP transport over HTTP, per the 2025 spec update, as opposed to the deprecated SSE transport |

## 4. User stories

| ID | Story |
|---|---|
| US-003-01 | As a reviewer, I want to see two MCP servers exposing the same tools, so that I can confirm the parity claim is not about one engine with two wrappers |
| US-003-02 | As a reviewer, I want a test that fails when the tokenizers diverge, so that the most likely drift vector is guarded |

## 5. Acceptance criteria

### AC-003-01 — The .NET engine passes the golden cases

- **Given** the C# `RagEngine` loaded with the real corpus
- **When** `search` runs for each of the 10 golden cases
- **Then** the returned `docId` sequences equal the expected sequences

### AC-003-02 — Tokenizer differential

- **Given** a fixture of 200 plain strings committed as `tests/fixtures/tokenizer_cases.json`
- **When** both the Python and the C# tokenizer run on every string
- **Then** the two token lists are identical for every string, and the test fails by naming the first diverging case

### AC-003-03 — Parity runner

- **Given** both engines loaded with the real corpus
- **When** the parity runner executes all 10 golden queries against both
- **Then** every query produces the same `docId` sequence from both implementations, and the runner exits `0`

### AC-003-04 — Architecture test in C#

- **Given** the `Mcp.Rag.Dotnet.Core` namespace
- **When** the NetArchTest rules run
- **Then** `Core` references no `ModelContextProtocol`, no `Microsoft.AspNetCore`, and no `System.IO` for corpus
  access

### AC-003-05 — Both servers speak MCP over stdio

- **Given** `dotnet run --project src/Mcp.Rag.Dotnet` and `python -m mcp_rag_py.apps.mcp --stdio`
- **When** an MCP client sends `tools/list` over stdio
- **Then** both return `search`, `get_document` and `answer` with the contract's JSON schemas

### AC-003-06 — Dockerfiles build

- **Given** `infra/Dockerfile.py` and `infra/Dockerfile.net`
- **When** `docker build` runs for each
- **Then** both build successfully, and the Python image's RSS at startup is below 120 MB

## 6. Rules and invariants

- The C# core is a port, not a reinterpretation. Every constant, regex and sort order matches the contract verbatim.
- The Python MCP tools call the same `RagEngine` methods the REST facade calls. No second code path.
- The parity runner asserts `docId` sequences, never floats (Constitution, Article 3).
- The tokenizer differential fixture is generated from the Python implementation and manually inspected for the first
  20 cases before committing. It is a regression guard, not a proof of correctness.

## 7. Open questions

| Question | Status | Owner |
|---|---|---|
| .NET project structure: single project or Core + Adapters + App? | resolved: single project with folder separation; architecture test enforces the boundary instead of assembly references | architect |
| Tokenizer fixture: capture Python output or list of inputs? | resolved: inputs only; both sides compute output and compare programmatically | architect |
| .NET MCP transport: stdio only or also HTTP? | resolved: stdio wired in Program.cs; HTTP transport wired in compose (SPEC-004) | architect |

## 8. Change log

| Date | Change | Reason | Approver |
|---|---|---|---|
| 2026-11-20 | Approved | Unblocks W3 | owner |
