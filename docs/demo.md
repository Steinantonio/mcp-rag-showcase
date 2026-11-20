# Demo transcript

Real output from a Windows machine with .NET 10.0.404 and Python 3.12.10. Nothing here is illustrative.

## 1. Both suites

```
$ ./scripts/test.ps1
==> pytest
69 passed, 1 warning
==> architecture (import-linter)
core is pure: no adapters, no apps, no frameworks, no I/O  KEPT
Contracts: 1 kept, 0 broken.
==> dotnet test
Aprovado! – Com falha: 0, Aprovado: 26, Ignorado: 0, Total: 26
==> parity
10/10 cases passed
==> all suites passed
```

## 2. Parity, query by query

```
$ python tests/conformance/parity_runner.py
 OK  rotate-api-key: ['ops-credentials', 'ops-credentials', 'ops-credentials']
 OK  leaked-key-revocation: ['ops-credentials', 'ops-changelog', 'ops-credentials']
 OK  sev1-definition: ['ops-glossary', 'ops-faq', 'ops-escalation']
 OK  restore-backup: ['ops-backups', 'ops-data-retention', 'ops-faq']
 OK  rollback-artifact: ['ops-deployments', 'ops-glossary', 'ops-changelog']
 OK  quarterly-access-review: ['ops-access-review', 'ops-access-review', 'ops-changelog']
 OK  egress-rules: ['ops-networking', 'ops-changelog', 'ops-networking']
 OK  error-budget: ['ops-monitoring', 'ops-glossary', 'ops-cost-controls']
 OK  no-match: []
 OK  repeated-token: ['ops-data-retention', 'ops-changelog', 'ops-backups']

10/10 cases passed
```

## 3. The two servers, over MCP, side by side

Native run: Python on `:8080` (REST + MCP), .NET on `:8081` (MCP + health).

```
$ ./scripts/smoke.ps1
Python : http://127.0.0.1:8080
.NET   : http://127.0.0.1:8081

query: how do I rotate an api key
  python  ops-credentials#02  ops-credentials#00  ops-credentials#01
  dotnet  ops-credentials#02  ops-credentials#00  ops-credentials#01
  MATCH

query: restore a database backup
  python  ops-backups#00  ops-data-retention#01  ops-faq#01
  dotnet  ops-backups#00  ops-data-retention#01  ops-faq#01
  MATCH

query: quarterly access review
  python  ops-access-review#00  ops-access-review#02  ops-changelog#01
  dotnet  ops-access-review#00  ops-access-review#02  ops-changelog#01
  MATCH

query: roll back the previous artifact
  python  ops-deployments#01  ops-glossary#03  ops-changelog#01
  dotnet  ops-deployments#01  ops-glossary#03  ops-changelog#01
  MATCH

query: egress rules
  python  ops-networking#01  ops-changelog#01  ops-networking#03
  dotnet  ops-networking#01  ops-changelog#01  ops-networking#03
  MATCH

5/5 queries matched
```

## 4. Health, both services

```
$ curl.exe -s http://127.0.0.1:8080/health
{"status":"ok","contractVersion":1,"version":"0.1.0","uptimeSeconds":4.4,
 "corpus":{"documents":15,"chunks":63,"tokens":3847,"avgChunkTokens":61.06}}

$ curl.exe -s http://127.0.0.1:8081/health
{"status":"ok","implementation":"dotnet","contractVersion":1,
 "corpus":{"documents":15,"chunks":63,"tokens":3847,"avgChunkTokens":61.06}}
```

Same corpus, same counts, different runtimes.

## 5. What is not in this transcript

- `docker compose up`: Docker is not installed on the machine that produced this transcript. The compose file is
  structurally validated and exercised in CI (SPEC-005). This is recorded as an accepted gap in
  `specs/004-automation/spec.md` §5.
- The Render deployment: `docs/deploy.md` has the steps; the live URL is added by the owner after the first deploy.
