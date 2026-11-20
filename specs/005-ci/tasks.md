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
| T-005-05 | First green run on GitHub | owner | Actions run URL | todo (needs push) |
| T-005-06 | Verify the red path: break `k1` in one implementation | owner | parity job fails, names the query | todo (needs push) |

## Notes

- Both services now run MCP **stateless**. This removed a class of deployment bugs (no session affinity) and let
  `smoke.ps1` drop header parsing that behaves differently between Windows PowerShell 5.1 and PowerShell 7.
  Recorded because it changes the smoke script contract.
- `bicep build` was verified locally with Bicep CLI 0.49.2, so the `iac` job is not a shot in the dark.
- `docker compose config -q` and the `containers` job cannot run locally (no Docker). They are the only two
  commands in this workflow that have never executed on this machine.
