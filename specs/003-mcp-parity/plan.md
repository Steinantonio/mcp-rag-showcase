# PLAN-003 — MCP servers and cross-language parity

- **Spec:** `specs/003-mcp-parity/spec.md`
- **Status:** approved
- **Owner:** architect
- **Last updated:** 2026-11-20

## 1. Architecture impact

| Layer | Change | Files |
|---|---|---|
| Python `core` | none — the core is closed | — |
| Python `adapters` | new MCP server (stdio + HTTP) | `src/mcp_rag_py/adapters/mcp_server.py` |
| Python `apps` | new MCP entry point | `src/mcp_rag_py/apps/mcp.py` |
| Python deps | add `mcp` | `pyproject.toml` |
| .NET `Core` | new: Models, Errors, Tokenizer, Chunker, Bm25, RagEngine | `src/Mcp.Rag.Dotnet/Core/*.cs` |
| .NET `Adapters` | new: CorpusSource, McpTools | `src/Mcp.Rag.Dotnet/Adapters/*.cs` |
| .NET composition | new: Program.cs | `src/Mcp.Rag.Dotnet/Program.cs` |
| .NET tests | new xunit project | `tests/Mcp.Rag.Dotnet.Tests/*.cs` |
| fixtures | new tokenizer differential input | `tests/fixtures/tokenizer_cases.json` |
| infra | new Dockerfiles | `infra/Dockerfile.py`, `infra/Dockerfile.net` |

Must **not** change: `core/` in either language after this wave, and the corpus.

## 2. Contract

Implements the MCP tool surface described by `docs/tool-contract.md` §5. The tools are thin adapters: they validate,
call the engine, and serialize. The tokenizer, chunker and BM25 are ported to C# following the contract verbatim, with
the one clarification recorded during SPEC-002 (L*/Nd rather than `\p{L}\p{N}`).

## 3. Test strategy

| Layer | What is proven | Where |
|---|---|---|
| .NET unit | tokenizer, chunker, BM25, engine, errors | `tests/Mcp.Rag.Dotnet.Tests/` |
| .NET contract | the 10 golden cases | same |
| Tokenizer differential | 200 strings → identical token lists | same, reads `tests/fixtures/tokenizer_cases.json` |
| Parity | both engines, same queries, same docId sequences | `tests/conformance/parity_runner.py` (calls both CLIs) |
| Architecture (.NET) | `Core` has no MCP/ASP.NET/IO references | `tests/Mcp.Rag.Dotnet.Tests/ArchitectureTests.cs` |
| Container | Dockerfiles build | `docker build -f infra/Dockerfile.{py,net} .` (manual or CI) |

## 4. Task order

1. Python: add `mcp` dep, write `adapters/mcp_server.py`, wire entry point.
2. .NET: scaffold solution + project + xunit project.
3. .NET: `Core/Models.cs`, `Core/Errors.cs` (Result<T>).
4. .NET: `Core/Tokenizer.cs` — test first, against contract examples.
5. Generate tokenizer fixture from Python, commit.
6. .NET: tokenizer differential test.
7. .NET: `Core/Chunker.cs`, `Core/Bm25.cs`, `Core/RagEngine.cs` — test first.
8. .NET: golden suite.
9. .NET: `Adapters/CorpusSource.cs`, `Adapters/McpTools.cs`.
10. .NET: `Program.cs` (stdio transport).
11. .NET: architecture test (NetArchTest).
12. Parity runner script.
13. Dockerfiles.

## 5. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| `ModelContextProtocol` 2.4.0 API unfamiliar | implementation stall | read the package samples, keep tools thin |
| BM25 arithmetic divergence (e.g. `Math.Log` vs `Math.Log` base difference) | ranking mismatch | the hand-computed `ln 2` test on both sides |
| Chunker paragraph splitting differs | chunk ids shift | the paragraph packing rule is algorithmic; port the test cases verbatim |
| .NET Docker image too large | bad demo | use `mcr.microsoft.com/dotnet/sdk:10.0` with multi-stage build |
| Tokenizer differential flaky on non-ASCII | test noise | the fixture is ASCII + Latin-1; exotic Unicode is documented as out of scope |

## 6. Definition of done for this wave

- [ ] `dotnet test` green, including the 10 golden cases, the tokenizer differential, and the architecture test.
- [ ] `pytest` green (existing 69 tests + MCP tool smoke test).
- [ ] Parity runner: `python tests/conformance/parity_runner.py` exits `0`.
- [ ] Both Dockerfiles build.
- [ ] One local commit: `feat(mcp): C# core, MCP servers and cross-language parity`.
