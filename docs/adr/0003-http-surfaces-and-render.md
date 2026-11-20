# ADR 0003 — Two HTTP surfaces, and exactly one free host

- **Status:** Accepted
- **Date:** 2026-11-20
- **Deciders:** repo owner
- **Contract impact:** adds the REST facade described by `docs/openapi.yaml`; does not change the MCP tool contract

## Context

The MCP tool surface is JSON-RPC over stdio or streamable HTTP. That is the right interface for a *client*, and the
wrong interface for a *human evaluating the repo*. A reviewer who wants to see the retrieval work should not have to
install an MCP client, edit a config file, and restart an app. They should open a URL and press "Try it out".

Separately, the deployment target is Render's free tier, which imposes real limits that the architecture has to
respect rather than discover in production:

| Limit (verified against Render's free-tier docs) | Architectural consequence |
|---|---|
| 0.1 CPU / 512 MB RAM | Rules out torch-based embeddings; keeps the index in memory |
| Spins down after 15 min without inbound traffic; ~1 min to wake | Cold-start must be documented, and must not depend on a warm cache or a background worker |
| Ephemeral filesystem; no persistent disks | Index is rebuilt from `corpus/` at every boot, never persisted |
| 750 instance hours/month per workspace | One sleeping service consumes far less than 750 h; two services double the risk |
| No shell access, no one-off jobs, single instance | No migrations, no cron warm-up hack, no SSH debugging — logs are the only diagnostic |
| Free Postgres expires in 30 days | Never introduce a database; it would expire and break the demo silently |

## Decision

1. **MCP is served over streamable HTTP**, mounted at `/mcp`, and additionally over **stdio** for desktop clients.
   Legacy SSE transport is not implemented — it is deprecated and would be dead code in a new repo.
2. **A thin REST facade exists on the Python service only**, described by a committed OpenAPI 3.1 document
   (`docs/openapi.yaml`) and browsable at `/docs`. It exposes `/health`, `/api/v1/search`, `/api/v1/documents/{id}`
   and `/api/v1/answer` — one endpoint per tool, plus health.
3. **The facade calls the same engine functions as the MCP tools**, in-process. It is a serialization layer, not a
   second implementation. There is no second code path that could drift.
4. **The .NET server stays MCP-only.** It is exercised by unit tests, the conformance suite, and `compose.yaml`.
   Duplicating the facade in C# would add a second OpenAPI document, a second deployment story and a second
   place for the contract to drift, for zero additional proof.
5. **Exactly one service is deployed: the Python one**, via `render.yaml` using the same `infra/Dockerfile.py` that
   `compose.yaml` uses. One build definition, one deployment target.
6. **CI guards the committed spec.** The app's generated OpenAPI document is diffed against `docs/openapi.yaml`;
   any difference fails the build. The document is a contract, so it must not silently lag the code.

## Consequences

**Good**

- A reviewer can evaluate the retrieval in a browser in under 30 seconds, cold start aside.
- The OpenAPI document doubles as human documentation and as the source for the Swagger UI page.
- One free service means one cold start, one set of logs, one thing to keep alive, and no risk of burning the
  750-hour budget with an idle duplicate.
- The stdio transport keeps the "works in Claude Desktop" story intact, which is the reason MCP exists.

**Bad**

- **Cold start is user-visible.** The first request after 15 idle minutes takes roughly a minute and Render shows
  its own loading page. Mitigation is honesty: the README states it, and `/health` is the documented first call.
  A cron-based warmer would consume free instance hours around the clock and is deliberately not used.
- **Only the Python implementation is publicly reachable.** The .NET server is proven in CI and in compose, not on
  a public URL. Anyone wanting to poke it must clone. This is the scope trade the ADR makes.
- **The facade is unauthenticated and public.** Acceptable because the corpus is authored for this repo and is
  already in the git history. Any real corpus would need auth, which needs a secret, which breaks "clone and run".
- **Spec drift risk** is real, hence the CI diff. Without that check the committed YAML would rot within two weeks.

## Alternatives rejected

| Alternative | Why rejected |
|---|---|
| Host both services on Render | Two cold starts, two services against the 750 h budget, and the second one proves nothing the first does not |
| Host the .NET service instead | Then the visual surface needs a C# OpenAPI/Swagger stack, and the Python side loses its deployment story; also loses the "REST + MCP in one FastAPI app" clarity |
| Only MCP, no REST facade | Correct purism, terrible review experience; the OpenAPI document is the cheapest possible "try it now" affordance |
| Document the MCP endpoint with OpenAPI | JSON-RPC does not map onto OpenAPI paths and schemas in any honest way; the result would be a fiction that tools cannot use |
| Render native Python runtime instead of Docker | Faster builds, but a second build definition that can diverge from the container path; one Dockerfile is the stronger invariant |
| Free Render Postgres for the index | Expires after 30 days; the demo would break on its own with no code change |
| Fly.io / Azure Container Apps free allowances | Fly's free allowance changed repeatedly; Azure's free grant is a credit, not a permanent free tier, and `bicep` deploy would spend it |
| Keep the service warm with a scheduled ping | Consumes free instance hours continuously to hide a 60-second delay that the README already explains |
| Serve the static Swagger UI from a Render static site | A second service for one HTML page; FastAPI serves it for free at `/docs` |

## Follow-up

- W4 adds `render.yaml` and a `docs/deploy.md` with the exact dashboard steps (repo connect → free plan → env vars,
  of which there are none).
- W5 adds the CI step that diffs the generated OpenAPI document against `docs/openapi.yaml`.
- If the demo ever needs to be always-warm, the honest change is a paid instance, not a ping loop.
