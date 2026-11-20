# TASKS-004 — Automation, containers and free-tier deploy

- **Spec:** `specs/004-automation/spec.md`
- **Status:** implementing
- **Last updated:** 2026-11-20

## Tasks

| ID | Task | Owner | Evidence | Status |
|---|---|---|---|---|
| T-004-01 | Python: REST + MCP in one process (`apps/http.py`) | python-implementer | `tests/integration/test_mcp_http.py` (2 tests) | done |
| T-004-02 | .NET: `--http` mode with `/health` and `/mcp` | dotnet-implementer | `/health` returns `implementation: dotnet` | done |
| T-004-03 | `compose.yaml` with both services and healthchecks | conformance-engineer | structural validation; CI in SPEC-005 | todo (pending CI) |
| T-004-04 | `scripts/bootstrap.ps1` | conformance-engineer | manual run | done |
| T-004-05 | `scripts/test.ps1` (pytest + lint + dotnet + parity) | conformance-engineer | real output in `docs/demo.md` | done |
| T-004-06 | `scripts/serve.ps1`, `up.ps1`, `down.ps1`, `clean.ps1` | conformance-engineer | `up.ps1` fails clearly without Docker | done |
| T-004-07 | `scripts/smoke.ps1` comparing both servers over MCP | conformance-engineer | 5/5 MATCH in `docs/demo.md` | done |
| T-004-08 | `docs/deploy.md` | architect | Render steps, no secrets | done |
| T-004-09 | `docs/demo.md` with real transcript | orchestrator | verbatim output | done |

## Notes

- **AC-004-03 is not proven locally.** Docker is not installed on the machine that built this wave. The compose file
  is written and `up.ps1` refuses to pretend (it throws a clear message when `docker` is absent). CI proves it in
  SPEC-005; until then this task stays `todo`.
- `smoke.ps1` revealed that the .NET HTTP transport is **stateless** (no session id). The script handles both
  stateful (Python) and stateless (.NET) servers; this is documented in the script comment.
- Windows PowerShell 5.1 compatibility shaped every script: no `Path.GetRelativePath`, no `pwsh`, no ternary
  operator.
