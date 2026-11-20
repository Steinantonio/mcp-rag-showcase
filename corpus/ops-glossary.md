---
id: ops-glossary
title: Glossary
tags: glossary, definitions
---
## Availability and reliability

**SLO** — a target success ratio over a window, for example 99.9 percent of requests over thirty days. **Error
budget** — the failure the SLO permits. **RTO** — how long a restore may take. **RPO** — how much data a restore
may lose.

## Incident terms

**SEV1** — total loss of the primary path or confirmed data exposure. **SEV2** — significant degradation with a
workaround. **Incident commander** — the person who runs the incident, not the person who fixes it. **Blast
radius** — what is affected right now, confirmed rather than assumed.

## Credentials

**Rotation** — issuing a new credential and revoking the old one, with a deliberate overlap window. **Revocation**
— making a credential stop working immediately. **Scope** — the single service and environment a credential may
address. **Break-glass** — standing emergency access that is logged and reviewed afterwards.

## Delivery

**Canary** — a small slice of traffic sent to a new version before the full rollout. **Artifact** — the immutable
build output that gets deployed. **Expand and contract** — the two-step schema migration that keeps rollback
possible.

## Data

**Snapshot** — a point-in-time copy of a database. **Retention window** — how long a dataset is kept before
deletion. **Synthetic data** — generated records used in place of production data.

## Rule of thumb

If a term needs a paragraph to explain during an incident, it needs a line here instead.
