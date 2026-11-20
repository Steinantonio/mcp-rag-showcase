# TASKS-005 — CI and contract guards

- **Spec:** `specs/005-ci/spec.md`
- **Status:** implementing (pending first green run on GitHub)
- **Last updated:** 2026-11-20

## Tasks

| ID | Task | Owner | Evidence | Status |
|---|---|---|---|---|
| T-005-01 | `infra/main.bicep` (Container Apps, validated only) | conformance-engineer | `bicep build` → ARM template, 3720 bytes | done |
| T-005-02 | `.github/workflows/ci.yml` with five jobs | conformance-engineer | YAML parses; jobs `python, dotnet, parity, containers, iac` | done |
| T-005-03 | Contract version consistency test | conformance-engineer | `tests/conformance/test_contract_version.py` | done |
| T-005-04 | `Core/Contract.cs` so C# has a single constant | dotnet-implementer | health endpoint uses `Contract.Version` | done |
| T-005-05 | First green run on GitHub | owner | run 44816619920: 5/5 jobs success | done |
| T-005-06 | Verify the red path: break `k1` in one implementation | owner | `k1 = 2.0` → `10/10 cases failed`, `score drift on ...` | done |

## Notes

- **The red-path check found a real gap.** Changing `k1` did not change any `docId` sequence, so the original parity
  suite passed. The runner now compares scores with a `1e-4` tolerance as well; with that in place, `k1 = 2.0`
  fails 10/10 with `score drift`. ADR 0002 carries the amendment.
- **First CI run was red twice, for real reasons:** `.sln` vs `.slnx` (the .NET 10 solution format), then
  `dotnet/runtime` instead of `dotnet/aspnet` (the app needs `Microsoft.AspNetCore.App`). Both were invisible
  locally because Docker is not installed; both were fixed in the workflow and the Dockerfile.
- A stale-binary trap cost time locally: `Copy-Item -Force` preserves the source timestamp, so `dotnet build`
  skipped compilation and the old binary answered. `-t:Rebuild` plus a touched timestamp is the fix.

- Both services now run MCP **stateless**. This removed a class of deployment bugs (no session affinity) and let
  `smoke.ps1` drop header parsing that behaves differently between Windows PowerShell 5.1 and PowerShell 7.
  Recorded because it changes the smoke script contract.
- `bicep build` was verified locally with Bicep CLI 0.49.2, so the `iac` job is not a shot in the dark.
- `docker compose config -q` and the `containers` job cannot run locally (no Docker). They are the only two
  commands in this workflow that have never executed on this machine.
