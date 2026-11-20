# Build plan

**Objective:** a public repo that proves, in under five minutes of reading and one minute of clicking, that the same
MCP + RAG contract can be implemented twice (.NET, Python), containerized, and shipped on a free tier — with parity
that is mechanically verified.

**Non-goals:** a framework, a library, a benchmark, a product, a production deployment, anything requiring a key.

Status legend: `todo` · `in progress` · `done`

---

## Waves

| # | Wave | Spec | Deliverable | Status |
|---|---|---|---|---|
| W0 | Documentation | SPEC-000 | README, tool contract, OpenAPI (lint-clean), 3 ADRs, plan, LICENSE, render.yaml | **done** |
| W0.5 | Methodology | SPEC-000 | `AGENTS.md`, `specs/` (constitution + 000/001/002), `agents/` (6 + pilot), `templates/`, `docs/methodology.md`, ADR 0004 | **done** |
| W1 | Corpus | SPEC-001 | 15 authored docs + `corpus/golden/queries.json` with hand-derived expectations | **done** |
| W2 | PoC core | SPEC-002 | Pure core (tokenizer, chunker, BM25, engine) + CLI + REST/OpenAPI + tests | **done** |
| W3 | MCP + parity | SPEC-003 | MCP servers in Python and .NET, tokenizer differential test, parity runner, Dockerfiles | **done** |
| W4 | Automation | SPEC-004 | compose, PowerShell lifecycle scripts, `render.yaml`, deploy notes, demo transcript | **in progress** (compose pending CI) |
| W5 | CI + polish | SPEC-005 | GitHub Actions (5 jobs), OpenAPI drift check, badges, final README pass | **done** |
| W6 | Optional | — | Ollama generator behind a flag, MCP Inspector walkthrough | deferred |

Each wave is a spec: written, approved, implemented, then evidenced. Specs 003–005 are written at the start of their
wave, not in advance.

---

## W1 — Corpus (the actual product)

**Why first:** every downstream number depends on it. `avgdl` and `N` come from the corpus, so hand-derived golden
expectations must be written against a frozen corpus. Editing corpus after W3 means re-deriving everything.

Content: a fictional internal operations handbook — 15 markdown files, 300–600 words each, 3–5 H2 sections, with
overlapping vocabulary across documents (so ranking is non-trivial) and three near-duplicate clusters (so BM25 and
the tie-break rule are exercised, not vocabulary alone).

Document set: `ops-onboarding`, `ops-credentials`, `ops-runbook`, `ops-incidents`, `ops-backups`,
`ops-monitoring`, `ops-networking`, `ops-deployments`, `ops-access-review`, `ops-faq`, `ops-glossary`,
`ops-escalation`, `ops-data-retention`, `ops-cost-controls`, `ops-changelog`.

Clusters: credentials/runbook/faq · incidents/escalation · backups/data-retention.

**Acceptance**

- [ ] `python scripts/check_corpus.py` (or the test in W2) reports: 15 docs, ids unique and schema-valid, no doc
      with fewer than 2 chunks, no chunk over 1200 chars.
- [ ] `corpus/golden/queries.json` has 10 cases, each with `expectDocIds` written by hand from the spec.
- [ ] Cases include: one zero-match query, one repeated-token query, one query that only ranks correctly when IDF is
      applied, one `grounded: false` case.

---

## W2 — PoC core (the RAG, with no MCP anywhere)

This is the proof-of-concept milestone: corpus → chunks → BM25 → citations → extractive answer, reachable from a
terminal and a browser. If this wave is green, the RAG works and the rest is doors.

Layout:

```
src/mcp_rag_py/
  core/
    errors.py        # RagError codes, contract §6
    tokenizer.py     # contract §3
    chunker.py       # contract §1–2
    bm25.py          # contract §4
    engine.py        # search / get_document / answer, contract §5
  adapters/
    corpus_fs.py     # restricted front matter parser + filesystem loader
    rest.py          # FastAPI: /health, /api/v1/*, /docs, /openapi.json
  apps/
    cli.py           # ingest | query
    http.py          # composition root
tests/
  unit/  conformance/  integration/  arch/
```

Dependencies: `fastapi`, `uvicorn`, `pytest`, `httpx`, `import-linter`. No numpy, no `mcp` in this wave.

**Acceptance**

- [ ] `pytest` green, including the 10 golden cases (as `pytest.mark.parametrize`) and the architecture test.
- [ ] `python -m mcp_rag_py ingest` prints `15 documents, N chunks, avgdl X`.
- [ ] `python -m mcp_rag_py query "how do I rotate an api key"` prints ranked citations.
- [ ] `uvicorn` serves `/docs`; `400`/`404` codes match contract §6.
- [ ] Two runs produce byte-identical JSON.

---

## W3 — MCP servers and parity

Layout:

```
src/mcp_rag_py/adapters/mcp_server.py   # tools over stdio + streamable HTTP
src/Mcp.Rag.Dotnet/
  Program.cs             # host + transport switch (stdio default, --http for container)
  Core/Chunker.cs        # contract §1–2
  Core/Tokenizer.cs      # contract §3
  Core/Bm25.cs           # contract §4
  Core/RagEngine.cs      # contract §5
  Adapters/McpTools.cs   # [McpServerTool] registrations
tests/Mcp.Rag.Dotnet.Tests/    # xunit: mirrors the Python test names
tests/conformance/             # parity runner: both servers, same queries
```

Pinned to `ModelContextProtocol` **2.4.0** (stable) and `ModelContextProtocol.AspNetCore` 2.4.0. Target `net10.0`.

**Acceptance**

- [ ] `dotnet test` green, including the 10 golden cases.
- [ ] Tokenizer differential test: 200 fixed strings → identical token lists to the Python tokenizer (fixture file
      shared by both suites, so a divergence names the offending string).
- [ ] Parity runner: same 10 queries, both servers, identical `docId` sequences.
- [ ] `dotnet run --project src/Mcp.Rag.Dotnet` speaks MCP over stdio; verified with a scripted JSON-RPC exchange.
- [ ] `docker build -f infra/Dockerfile.py` and `infra/Dockerfile.net` succeed; Python container RSS < 120 MB.

---

## W4 — Automation and deployment

Scripts (Windows PowerShell 5.1+ compatible — PowerShell 7 is **not** installed on the author's machine, so no
.NET Core-only APIs and no `pwsh` shebang):

| Script | Does |
|---|---|
| `bootstrap.ps1` | creates `.venv`, `pip install -e .[dev]`, `dotnet restore`; idempotent |
| `test.ps1` | `pytest` + `dotnet test` + conformance runner; single exit code |
| `serve.ps1` | runs the Python service on `:8080` in the foreground |
| `up.ps1` | `docker compose up --build -d` + waits on both `/health` endpoints |
| `smoke.ps1` | calls `search` on both servers, prints the side-by-side table; exits non-zero on any mismatch |
| `down.ps1` / `clean.ps1` | compose down / remove venv, bin, obj, images |

`compose.yaml` runs `py` on 8080 and `net` on 8081, both with healthchecks, both read-only mounts of `corpus/`.

**Acceptance**

- [ ] `./scripts/up.ps1` then `./scripts/smoke.ps1` prints 3 `MATCH` lines for 5 different queries.
- [ ] `render.yaml` present; `docs/deploy.md` documents the exact dashboard clicks and states that no env vars and
      no secrets are required.
- [ ] `docs/demo.md` holds a real transcript (not invented) of bootstrap → test → up → smoke, pasted verbatim into
      the README.
- [ ] Deployed URL responds on `/health` after a cold start; measured wake time recorded in `docs/deploy.md`.

---

## W5 — CI and polish

`ci.yml` jobs, all on `ubuntu-latest`, all free for a public repo:

1. `python` — 3.12, `pytest`, coverage report.
2. `dotnet` — `dotnet test` on .NET 10.
3. `containers` — build both images, `docker compose up`, wait for health, run the smoke assertions, dump `docker
   stats` for the RSS check.
4. `iac` — `bicep build infra/main.bicep` (validate only, never deploy) + `docker compose config -q`.
5. `contract` — OpenAPI drift diff + `contractVersion` consistency across both servers and the golden file.

**Acceptance**

- [ ] All five jobs green on a clean clone.
- [ ] `npx --yes @redocly/cli@latest lint docs/openapi.yaml` passes with the repo's `redocly.yaml`
      (verified locally already: 0 errors, 2 warnings disabled by config).
- [ ] A deliberately broken BM25 constant turns `contract`/`python`/`dotnet` red (verify once, then revert).
- [ ] README badges resolve; quick-start commands are copy-paste correct; `<owner>` placeholders replaced.

---

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `ModelContextProtocol` 2.x API differs from the 0.x tutorials that dominate search results | high | pin 2.4.0, read the package's own samples, keep the tool layer thin |
| Hand-derived golden expectations are wrong | medium | derive twice (once per implementation, independently) and reconcile against the spec, not against each other |
| Free-tier cold start makes the live demo look broken | high | document it, link `/health`, keep the service warm only during a demo |
| No Docker locally → container feedback only in CI | certain | native smoke first (W4), container verification in CI; optionally install Docker Desktop or Podman |
| PowerShell 7 is not installed (5.1 only) | certain | scripts target 5.1+; `sync-agents.ps1` was rewritten after hitting `Path.GetRelativePath`, which is .NET Core-only |
| Corpus too small → rankings are trivially all-zero or all-first | medium | W1 requires overlapping vocabulary and near-duplicates; zero-match case catches over-matching |
| Scope creep (eval harness, hybrid search, auth) | medium | the "Not built on purpose" section in the README is the contract with the reader |

## Open questions

1. ~~**GitHub owner handle**~~ — resolved: `Steinantonio`, applied to the README badges, clone URL and LICENSE.
2. **Render service name** — assumed `mcp-rag-showcase`; the OpenAPI `servers` entry uses
   `https://mcp-rag-showcase.onrender.com`.
3. **Commit identity** — the global git identity is a corporate address. For a public portfolio repo, use a personal
   address or the GitHub noreply form.

## Time budget

W1 ≈ 2 h · W2 ≈ 4 h · W3 ≈ 4 h · W4 ≈ 3 h · W5 ≈ 2 h. Roughly 1.5 working days of agent time, plus one manual
Render deploy and one manual badge/URL fixup.
