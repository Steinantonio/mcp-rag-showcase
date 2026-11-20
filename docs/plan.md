# Build plan

**Objective:** a public repo that proves, in under five minutes of reading and one minute of clicking, that the same
MCP + RAG contract can be implemented twice (.NET, Python), containerized, and shipped on a free tier — with parity
that is mechanically verified.

**Non-goals:** a framework, a library, a benchmark, a product, a production deployment, anything requiring a key.

Status legend: `todo` · `in progress` · `done`

---

## Waves

| # | Wave | Deliverable | Status |
|---|---|---|---|
| W0 | Documentation | README, tool contract, OpenAPI (lint-clean), 3 ADRs, this plan, LICENSE, render.yaml | **done** |
| W1 | Corpus | 15 authored docs + `golden/queries.json` with hand-derived expectations | todo |
| W2 | Python service | MCP + REST + BM25 + chunker + pytest + Dockerfile | todo |
| W3 | .NET service | MCP + BM25 + chunker + xunit + tokenizer differential test + Dockerfile | todo |
| W4 | Automation | compose, PowerShell lifecycle scripts, `render.yaml`, deploy notes, demo transcript | todo |
| W5 | CI + polish | GitHub Actions (5 jobs), OpenAPI drift check, badges, final README pass | todo |
| W6 | Optional | Ollama generator behind a flag, MCP Inspector walkthrough | deferred |

---

## W1 — Corpus (the actual product)

**Why first:** every downstream number depends on it. `avgdl` and `N` come from the corpus, so hand-derived golden
expectations must be written against a frozen corpus. Editing corpus after W3 means re-deriving everything.

Content: a fictional internal operations handbook — 15 markdown files, 400–900 words each, H2-sectioned, with
overlapping vocabulary across documents (so ranking is non-trivial) and at least three near-duplicate topics (so the
tie-break rule is exercised).

Suggested doc set: `ops-onboarding`, `ops-credentials`, `ops-runbook`, `ops-incidents`, `ops-backups`,
`ops-monitoring`, `ops-networking`, `ops-deployments`, `ops-access-review`, `ops-faq`, `ops-glossary`,
`ops-escalation`, `ops-data-retention`, `ops-cost-controls`, `ops-changelog`.

**Acceptance**

- [ ] `python scripts/check_corpus.py` (or the test in W2) reports: 15 docs, ids unique and schema-valid, no doc
      with fewer than 2 chunks, no chunk over 1200 chars.
- [ ] `corpus/golden/queries.json` has 10 cases, each with `expectDocIds` written by hand from the spec.
- [ ] Cases include: one zero-match query, one repeated-token query, one query that only ranks correctly when IDF is
      applied, one `grounded: false` case.

---

## W2 — Python service

Layout:

```
src/mcp_rag_py/
  __main__.py        # argparse: --stdio | --http --port | ingest | query
  corpus.py          # front-matter parse, chunker (spec §1–2)
  tokenizer.py       # spec §3
  bm25.py            # spec §4
  engine.py          # search / get_document / answer (spec §5)
  mcp_server.py      # tool registration, stdio + streamable HTTP
  rest.py            # FastAPI app: /health, /api/v1/*, /docs, /openapi.json
  settings.py
tests/
  test_tokenizer.py test_chunker.py test_bm25.py test_engine.py test_rest.py
```

Dependencies kept to `mcp`, `fastapi`, `uvicorn`, `pytest`, `httpx`. No numpy — a 5k-token corpus does not need it,
and dropping it keeps the image small enough for a fast free-tier build.

**Acceptance**

- [ ] `pytest` green, including the 10 golden cases (as `pytest.mark.parametrize`).
- [ ] `python -m mcp_rag_py ingest` prints `15 documents, N chunks, avgdl X`.
- [ ] `python -m mcp_rag_py --http` serves `/docs` with all four endpoints.
- [ ] `GET /openapi.json` output matches `docs/openapi.yaml` semantically (the CI diff in W5 formalizes this).
- [ ] `docker build -f infra/Dockerfile.py` succeeds; container starts in < 3 s; RSS < 120 MB (checked via
      `docker stats` in CI logs).

---

## W3 — .NET service

Layout:

```
src/Mcp.Rag.Dotnet/
  Program.cs             # host + transport switch (stdio default, --http for container)
  Corpus/Chunker.cs      # spec §1–2
  Corpus/Tokenizer.cs    # spec §3
  Ranking/Bm25.cs        # spec §4
  Engine/RagEngine.cs    # search / get_document / answer (spec §5)
  McpTools.cs            # [McpServerTool] registrations
tests/Mcp.Rag.Dotnet.Tests/   # xunit: mirror of the Python test names
```

Pinned to `ModelContextProtocol` **2.4.0** (stable) and `ModelContextProtocol.AspNetCore` 2.4.0. Target `net10.0`.

**Acceptance**

- [ ] `dotnet test` green, including the 10 golden cases.
- [ ] Tokenizer differential test: 200 fixed strings → identical token lists to the Python tokenizer (fixture file
      shared by both suites, so a divergence names the offending string).
- [ ] `dotnet run --project src/Mcp.Rag.Dotnet` speaks MCP over stdio; verified with the MCP Inspector in W6 or a
      scripted JSON-RPC exchange in W4.
- [ ] `docker build -f infra/Dockerfile.net` succeeds.

---

## W4 — Automation and deployment

Scripts (PowerShell 7, `#Requires -Version 7.0`, `$ErrorActionPreference = 'Stop'`):

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
