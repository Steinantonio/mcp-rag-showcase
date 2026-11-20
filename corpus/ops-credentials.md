---
id: ops-credentials
title: Rotating API keys
tags: security, credentials, api, keys
---
## Why rotation exists

An API key is a bearer credential: whoever holds it is the service. Rotation limits the damage window of a leak
from "forever" to "until the next cycle". Every key issued by the platform has a maximum lifetime of ninety days,
and every key is scoped to a single service and a single environment. A key that works in staging and production
at the same time is a defect, not a convenience.

## How to rotate a key

Create the new key first. Deploy it to the service that consumes it, and confirm in the dashboard that requests
carry the new key identifier. Only then revoke the old key. The overlap window is twenty-four hours, which is
enough for a rollout but short enough that a forgotten consumer fails loudly instead of silently using a stale
credential.

Never rotate a key by editing it in place. Keys are immutable; rotation means a new key and a revocation. If a
service cannot accept two keys at once, that service needs a change before the rotation, not during it.

## Revoking a leaked key

If a key leaks, revoke it immediately and do not wait for the rotation window. Expect the affected service to
fail; that failure is the correct signal. Open a SEV2 incident, notify the service owner, and record the time of
revocation. Then rotate the replacement, and only after the service is healthy, write the postmortem.

Leaked keys found in a repository history require a full rotation of every key that ever appeared in that
repository, not just the one in the current commit.

## What the audit shows

The credential vault logs every issuance, use and revocation with a timestamp and an actor. The audit is the
source of truth when a postmortem asks "who had this key". Access to the audit is read-only and granted to every
engineer, because hiding the log protects nobody.
