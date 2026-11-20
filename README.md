# mcp-rag-showcase

**One retrieval contract. Two MCP servers — C# and Python. Same answers, proven by a test.**

A minimal, fully free reference implementation of a RAG tool surface over the
[Model Context Protocol](https://modelcontextprotocol.io), written twice against one frozen spec and one shared
corpus. No API keys, no model downloads, no vector database, no cloud spend.

[![CI](https://github.com/Steinantonio/mcp-rag-showcase/actions/workflows/ci.yml/badge.svg)](https://github.com/Steinantonio/mcp-rag-showcase/actions/workflows/ci.yml)
![.NET](https://img.shields.io/badge/.NET-10-512BD4)
![Python](https://img.shields.io/badge/Python-3.12-3776AB)
![MCP](https://img.shields.io/badge/MCP-2.4%20%2F%202.3-6E56CF)
![License](https://img.shields.io/badge/license-MIT-blue)

## What it proves

| Claim | How you check it |
|---|---|
| The tool contract is language-agnostic | Three tools, implemented independently in C# and Python |
| Retrieval is reproducible | BM25 with frozen constants, no model, no randomness |
| Both implementations agree | `parity_runner.py` replays 10 golden queries and compares `docId` sequences |
| It runs in a container | `compose.yaml`, smoke-tested in CI over MCP |
| It costs nothing | No secret, no paid dependency; Render free tier |

## Quick start

```powershell
git clone https://github.com/Steinantonio/mcp-rag-showcase.git
cd mcp-rag-showcase

./scripts/bootstrap.ps1   # .venv + pip + dotnet restore
./scripts/test.ps1        # 72 pytest + 26 xunit + 10/10 parity
./scripts/serve.ps1       # Python on :8080 (REST + MCP)
```

Both services, side by side over MCP:

```powershell
./scripts/up.ps1          # docker compose up, both containers
./scripts/smoke.ps1       # same query, both servers, citations compared
```

## Surfaces

| Surface | Python | .NET |
|---|---|---|
| MCP (streamable HTTP) | `:8080/mcp` | `:8081/mcp` |
| REST + OpenAPI | `:8080/docs` | — |
| Health | `:8080/health` | `:8081/health` |

Tools in both: `search(query, k)`, `get_document(docId)`, `answer(query, k)`. Answers are **extractive** — source
sentences with citations, no generator model.

## Real output

```
$ ./scripts/smoke.ps1
query: restore a database backup
  python  ops-backups#00  ops-data-retention#01  ops-faq#01
  dotnet  ops-backups#00  ops-data-retention#01  ops-faq#01
  MATCH

5/5 queries matched
```

Full transcript: [`docs/demo.md`](docs/demo.md).

## Repository map

```
corpus/                 15 authored docs + 10 golden queries (frozen)
src/mcp_rag_py/         core/ (pure) · adapters/ (REST, MCP, filesystem) · apps/
src/Mcp.Rag.Dotnet/     Core/ (tokenizer, chunker, BM25, engine) · Adapters/
tests/                  unit · conformance · integration · arch · fixtures
specs/ agents/          spec-driven delivery and the six agent roles
docs/                   concepts · tool contract · ADRs · demo · deploy · OpenAPI
infra/                  Dockerfile x2 · main.bicep (validated, never deployed)
```

## Design decisions

| ADR | Decision |
|---|---|
| [0001](docs/adr/0001-lexical-retrieval.md) | BM25 and extractive answers instead of embeddings + LLM |
| [0002](docs/adr/0002-parity-contract.md) | Freeze the spec; prove parity with hand-derived vectors |
| [0003](docs/adr/0003-http-surfaces-and-render.md) | MCP + REST facade; one free service |
| [0004](docs/adr/0004-architecture-ports-and-adapters.md) | Ports and adapters with a pure core |

Architecture in four analogies: [`docs/concepts.md`](docs/concepts.md).

## Honest limitations

- **Lexical retrieval only.** No synonyms, no paraphrase. `"how long do we keep backups"` ranks a monitoring
  document first because of shared words — measured, documented, not hidden.
- **Extractive answers.** Stitched quotes, not prose.
- **15 documents.** Demonstrates the shape of a pipeline, not retrieval quality.
- **Cold start.** The deployed free instance sleeps after 15 idle minutes and takes ~1 minute to wake.
- **No auth.** The corpus is authored for this repo and is public on purpose.

## Docs

[Concepts](docs/concepts.md) · [Tool contract](docs/tool-contract.md) · [Demo](docs/demo.md) ·
[Deploy](docs/deploy.md) · [Methodology](docs/methodology.md) · [Build plan](docs/plan.md) · [OpenAPI](docs/openapi.yaml)

## License

MIT — see [LICENSE](LICENSE).
