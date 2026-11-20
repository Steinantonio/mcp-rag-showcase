---
id: ops-faq
title: Operations FAQ
tags: faq, credentials, backups, incidents
---
## How often do we rotate keys?

Every ninety days at most, and immediately after any suspected leak. The rotation is a new key plus a revocation,
never an edit. If a service cannot hold two keys during the overlap window, that is a bug in the service and it
gets fixed before the next cycle.

## Who can restore a backup?

Any engineer with the database role can start a restore into an isolated environment. Restoring over production
requires the service owner and an incident number. The reason is not distrust; it is that a production restore
destroys data that a postmortem may still need.

## What counts as a SEV1?

A SEV1 is total loss of the primary customer path, or confirmed data exposure. Partial degradation is SEV2. A
SEV1 pages the on-call engineer and the engineering manager at the same time, and opens a shared incident channel
within five minutes. If nobody is sure whether something is a SEV1, treat it as one until proven otherwise.

## Can I deploy on Friday?

Yes, if the change is reversible and the author is available for two hours after the deploy. The old rule banned
Friday deploys, which pushed risky changes to Monday morning where they competed with the start of the week. The
current rule bans unreversible changes, not days.

## Where do I ask for help?

The incident channel for anything active, the platform channel for anything that can wait, and the runbook index
for anything procedural. Asking in a public channel is not a sign of weakness; it is how the next person finds the
answer without asking.
