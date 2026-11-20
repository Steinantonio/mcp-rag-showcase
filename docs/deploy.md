# Deploying to Render (free tier)

The repository ships `render.yaml`, a blueprint for one free web service running the Python image. No environment
variable is required beyond `PORT`, which Render injects.

## What gets deployed

| Item | Value |
|---|---|
| Service | `mcp-rag-showcase` (web service, Docker runtime) |
| Plan | Free — 0.1 CPU, 512 MB RAM |
| Image | `infra/Dockerfile.py` (same file compose uses) |
| Health check | `/health` |
| Public surfaces | `/docs`, `/openapi.json`, `/api/v1/*`, `/mcp` |

Both MCP servers run **stateless**: no session id, no affinity, every request stands alone. That matters on a free
tier behind a proxy, and it is why the same smoke script works against a container, a local process and the deployed
service.

The .NET server is **not** deployed. One free service means one cold start and one set of logs; the .NET side is
proven in CI and in compose. See ADR 0003 for the trade-off.

## Steps

1. Push the repository to GitHub.
2. In the Render dashboard: **New → Blueprint**, select the repository. Render reads `render.yaml`.
3. Accept the free plan and create the service.
4. Wait for the first build (about 3–6 minutes: Python base image plus `pip install`).
5. Open `https://<service>.onrender.com/health`. The first request after 15 idle minutes takes about a minute.

If you prefer not to use the blueprint, create a **Web Service → Docker**, point it at `infra/Dockerfile.py`, set the
health check path to `/health`, and leave every environment variable empty.

## Free-tier limits that shape the design

| Limit | Consequence |
|---|---|
| Spins down after 15 minutes idle, ~1 minute to wake | Documented; `/health` is the first call to make |
| Ephemeral filesystem | The index is rebuilt from `corpus/` at boot; nothing is persisted |
| 512 MB RAM | No torch, no embeddings; BM25 over 63 chunks uses a fraction of that |
| 750 instance hours/month | One sleeping service stays well inside the budget |
| No shell, no one-off jobs | Logs are the only diagnostic; the app fails fast and loud at boot |

## Verifying a deploy

```powershell
$svc = "https://<service>.onrender.com"

curl.exe -s "$svc/health"

curl.exe -s "$svc/api/v1/search?q=restore%20a%20database%20backup&k=3" |
  ConvertFrom-Json | Select-Object -ExpandProperty results | Format-Table chunkId, score

Invoke-RestMethod -Method Post -Uri "$svc/api/v1/answer" -ContentType "application/json" `
  -Body (@{ query = "how do I rotate an api key"; k = 3 } | ConvertTo-Json)
```

The citations must match `ops-backups#00`, `ops-data-retention#01`, `ops-faq#01` — the same three the local
parity runner produces. If they differ, the deployed corpus is not the committed corpus.

## Why there is no secret

Nothing here calls an external model, a database or a third-party API. The only environment variable is `PORT`.
A deployment that needs no secret cannot leak one.
