# SPEC-005 — CI and contract guards

- **Status:** implemented
- **Owner:** architect
- **Approved by:** orchestrator (owner decision, 2026-11-20)
- **Requirements:** R-10
- **ADRs:** 0002, 0003
- **Contract impact:** none
- **Last updated:** 2026-11-20

## 1. Problem

Every claim in this repository is currently proven by hand, on one machine, with a local `.venv` and a local .NET
SDK. A stranger cannot verify anything without repeating that setup, and two claims — containers build, IaC is valid —
have never been proven at all. CI is the mechanism that turns local evidence into public evidence.

## 2. Scope

**In scope**

- `.github/workflows/ci.yml` with five jobs: python, dotnet, parity, containers, iac.
- `infra/main.bicep`: Container Apps definition, validated on every push, **never deployed**.
- A contract-version consistency check across Python, C#, golden vectors and the OpenAPI document.
- README badges and a final README pass with real CI-shaped commands.

**Out of scope**

- Deployment from CI (the owner deploys from the Render dashboard).
- Publishing images to GHCR (the compose job builds locally; publishing is a later, separate decision).
- Scheduled runs, matrix over OS versions, coverage thresholds.

## 3. Acceptance criteria

### AC-005-01 — Five jobs, all green on a clean clone

- **Given** a fresh checkout with no caches
- **When** the workflow runs on `push`
- **Then** `python`, `dotnet`, `parity`, `containers` and `iac` all succeed

### AC-005-02 — Containers are proven, not assumed

- **Given** the `containers` job
- **When** `docker compose up --build -d` runs
- **Then** both health endpoints answer `200`, `scripts/smoke.ps1` reports 5/5 `MATCH`, and the Python container's
  memory usage is printed by `docker stats --no-stream`

### AC-005-03 — IaC is valid and free

- **Given** `infra/main.bicep`
- **When** `bicep build` runs in the `iac` job
- **Then** it compiles with no errors, and the workflow contains no `az deployment` step

### AC-005-04 — Contract version cannot drift silently

- **Given** `CONTRACT_VERSION` in Python, `ContractVersion` in C#, `contractVersion` in the golden file and in
  `docs/openapi.yaml`
- **When** the `python` job runs
- **Then** all four are equal, or the build fails naming the file that disagrees

### AC-005-05 — A broken constant turns the build red

- **Given** a change that sets `K1 = 2.0` in one implementation only
- **When** CI runs
- **Then** the parity job fails with `score drift on <chunkId>`, naming the implementation pair

Note: this criterion originally said "the parity job fails and names the first diverging query", assuming the
`docId` sequence would move. It does not — the ranking survives a 70% score change on this corpus. The suite was
extended to compare scores with a `1e-4` tolerance (see ADR 0002, amendment). Without that extension the criterion
would have been a claim nobody had tested.

## 4. Rules and invariants

- No job requires a secret. `GITHUB_TOKEN` is not used for anything.
- The `containers` job always tears the stack down, even on failure, and dumps logs when it fails.
- `iac` validates; it never authenticates to Azure.
- Every job runs on `ubuntu-latest` with the toolchain version pinned.

## 5. Open questions

| Question | Status | Owner |
|---|---|---|
| Publish images to GHCR? | deferred: adds a registry credential surface for no demo value yet | owner |
| Run the workflow on `pull_request` too? | resolved: yes, same jobs, no extra cost on a public repo | architect |

## 6. Change log

| Date | Change | Reason | Approver |
|---|---|---|---|
| 2026-11-20 | Approved | Unblocks W5 | owner |
