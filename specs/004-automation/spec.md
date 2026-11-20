# SPEC-004 — Automation, containers and free-tier deploy

- **Status:** approved
- **Owner:** architect
- **Approved by:** orchestrator (owner decision, 2026-11-20)
- **Requirements:** R-08, R-09
- **ADRs:** 0003, 0004
- **Contract impact:** none
- **Last updated:** 2026-11-20

## 1. Problem

Two engines exist and agree, but nothing runs them together. A reviewer should be able to bring both up with one
command, call the same query against both, and see the same citations side by side. That requires HTTP transports on
both services, a compose file, PowerShell lifecycle scripts that work on Windows PowerShell 5.1, and a documented
free-tier deployment.

## 2. Scope

**In scope**

- Python: one process serving REST (`/health`, `/api/v1/*`, `/docs`) **and** MCP streamable HTTP at `/mcp`.
- .NET: HTTP mode (`--http`) serving `/health` and MCP at `/mcp`, keeping stdio as the default mode.
- `compose.yaml`: both services, healthchecks, read-only corpus mount.
- PowerShell scripts: `bootstrap`, `test`, `serve`, `up`, `smoke`, `down`, `clean` — 5.1 compatible.
- `docs/deploy.md`: exact Render steps, no secrets.
- `docs/demo.md`: a real transcript, pasted verbatim into the README.

**Out of scope**

- CI (SPEC-005).
- Building images locally on a machine without Docker (verified in CI instead; recorded as an accepted gap).
- Authentication, TLS termination, autoscaling.

## 3. Acceptance criteria

### AC-004-01 — One process, two surfaces (Python)

- **Given** `uvicorn mcp_rag_py.apps.http:app`
- **When** `/health`, `/api/v1/search?q=...`, `/docs` and `POST /mcp` (`tools/list`) are called
- **Then** all four respond successfully, and the MCP tool list contains `search`, `get_document`, `answer`

### AC-004-02 — .NET HTTP mode

- **Given** `dotnet run -- --http --port 8081`
- **When** `/health` and `POST /mcp` (`tools/list`) are called
- **Then** `/health` returns `{"status":"ok","implementation":"dotnet"}` and the tool list matches the Python one

### AC-004-03 — Compose brings both up

- **Given** `docker compose up --build -d`
- **When** both healthchecks pass
- **Then** `http://localhost:8080/health` and `http://localhost:8081/health` both return `200`

### AC-004-04 — Smoke script compares both servers

- **Given** both services are up
- **When** `./scripts/smoke.ps1` runs
- **Then** for each of 5 queries it prints the top-3 citations from each server and marks `MATCH`, exiting non-zero
  on any mismatch

### AC-004-05 — Scripts run on Windows PowerShell 5.1

- **Given** a machine with only Windows PowerShell 5.1
- **When** `bootstrap.ps1` and `test.ps1` run
- **Then** both exit `0` without using .NET Core-only APIs

### AC-004-06 — Deployment needs no secret

- **Given** `render.yaml` and `docs/deploy.md`
- **When** a reader follows the steps
- **Then** the service is created with the free plan, the Dockerfile path, and no environment variable other than
  `PORT`

## 4. Rules and invariants

- The Python MCP tools and the REST facade share one engine instance in one process.
- The .NET stdio mode remains the default; `--http` is additive.
- Scripts fail loudly (`$ErrorActionPreference = 'Stop'`) and never hide a non-zero exit code.
- The smoke script compares citations, not prose.

## 5. Open questions

| Question | Status | Owner |
|---|---|---|
| Docker not installed locally: how is compose verified? | accepted gap: structural validation locally, `docker compose up` in CI (SPEC-005) | owner |
| Mount MCP at `/` or at `/mcp` in FastAPI? | resolved: mount the sub-app at `/`, which exposes `/mcp` and keeps REST routes matched first | architect |

## 6. Change log

| Date | Change | Reason | Approver |
|---|---|---|---|
| 2026-11-20 | Approved | Unblocks W4 | owner |
