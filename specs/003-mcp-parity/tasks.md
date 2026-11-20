# TASKS-003 — MCP servers and cross-language parity

- **Spec:** `specs/003-mcp-parity/spec.md`
- **Plan:** `specs/003-mcp-parity/plan.md`
- **Status:** implemented
- **Last updated:** 2026-11-20

## Tasks

| ID | Task | Owner | Depends on | Test / evidence | Status |
|---|---|---|---|---|---|
| T-003-01 | Python: add `mcp` dep and MCP server adapter | python-implementer | — | `mcp_server.py` imports | done |
| T-003-02 | Python: MCP entry point (stdio + HTTP) | python-implementer | T-003-01 | `python -m mcp_rag_py.apps.mcp --help` | done |
| T-003-03 | .NET: scaffold solution, project and xunit project | dotnet-implementer | — | `dotnet build` | done |
| T-003-04 | .NET: `Core/Models.cs`, `Core/Errors.cs` | dotnet-implementer | T-003-03 | compilation | done |
| T-003-05 | .NET: `Core/Tokenizer.cs` (test first) | dotnet-implementer | T-003-04 | `TokenizerTests.cs` (5 tests) | done |
| T-003-06 | Generate tokenizer fixture from Python, commit | conformance-engineer | T-003-05 | `tests/fixtures/tokenizer_cases.json` (200 cases) | done |
| T-003-07 | .NET: tokenizer differential test | dotnet-implementer | T-003-06 | `TokenizerDifferentialTests.cs` (3 tests, AC-003-02) | done |
| T-003-08 | .NET: `Core/Chunker.cs`, `Core/Bm25.cs` (test first) | dotnet-implementer | T-003-05 | `ChunkerTests.cs` (4 tests), `Bm25Tests.cs` (5 tests) | done |
| T-003-09 | .NET: `Core/RagEngine.cs` (test first) | dotnet-implementer | T-003-08 | `EngineTests.cs` (9 tests, golden suite) | done |
| T-003-10 | .NET: `Adapters/CorpusSource.cs`, `Adapters/McpTools.cs` | dotnet-implementer | T-003-09 | `EngineTests` loads corpus via adapter | done |
| T-003-11 | .NET: `Program.cs` (stdio + CLI composition root) | dotnet-implementer | T-003-10 | `dotnet run -- --cli query ... --json` | done |
| T-003-12 | .NET: architecture test (NetArchTest) | dotnet-implementer | T-003-09 | `ArchitectureTests.cs` (2 tests, AC-003-04) | done |
| T-003-13 | Parity runner: CLI JSON comparison | conformance-engineer | T-003-09, T-003-02 | `parity_runner.py` (AC-003-03) | done |
| T-003-14 | Dockerfiles for both services | conformance-engineer | T-003-11, T-003-02 | `infra/Dockerfile.{py,net}` written; **build not verified locally** (no Docker) — CI in SPEC-005 | partial |

## Notes

- **Correction:** T-003-14 was marked `done` when the wave closed, but the images were never built: Docker is not
  installed on the author's machine. The Dockerfiles exist and were reviewed structurally; AC-003-06 stays unproven
  until CI runs `docker build`. Recorded here rather than left as a false green.

- 26 .NET tests pass (24 unit/conformance + 2 architecture), 69 Python tests pass. Parity runner: 10/10 cases
  produce identical `docId` sequences.
- The tokenizer differential fixture was generated from Python, manually inspected for the first 20 cases, and
  committed. The .NET tokenizer agrees on all 200.
- `ModelContextProtocol` 2.4.0 required `Microsoft.Extensions.Hosting` (not transitively available). The API uses
  `[McpServerTool]` without parameter attributes; the SDK auto-generates JSON schemas from C# method signatures.
- The .NET `Result<T>` discriminated union uses sealed records with pattern matching, matching the Python
  `Ok | Err` shape.
- Three compilation corrections were needed: missing `Err` import (caught by build), `RagError` getter on `Ok`
  (caught by tests), and `AddSingleton` requiring explicit `using Microsoft.Extensions.DependencyInjection`.
