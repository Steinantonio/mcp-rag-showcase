---
id: ops-escalation
title: Paging and escalation paths
tags: escalation, paging, on-call, incidents
---
## Who gets paged

The pager follows the service, not the person. Each service has a primary and a secondary on-call rotation with a
one week cadence. The primary is paged first; if there is no acknowledgement in five minutes, the secondary is
paged. If neither acknowledges in ten minutes, the engineering manager is paged automatically.

Rotations are published two months ahead. Swapping a shift is allowed and does not require approval, but the
swap must be recorded in the rotation tool. An unrecorded swap is the most common reason an incident starts with
"nobody knew they were on call".

## Escalation ladder

Escalation is not punishment. The ladder exists so that a responder never has to decide alone whether a problem is
big enough to wake someone up.

| Level | Trigger | Who joins |
|---|---|---|
| 1 | alert fires | primary on-call |
| 2 | no fix in thirty minutes, or SEV1 declared | secondary, service owner |
| 3 | customer-visible for one hour, or data at risk | engineering manager, incident commander |
| 4 | legal, regulatory or payment impact | leadership, security |

## What the paged person owes

Acknowledge within five minutes, even if the answer is "looking". Silence is the only failure mode. If you cannot
respond, escalate immediately rather than waiting to see whether it resolves itself.

When the incident closes, the primary writes two lines in the channel: what it was and what stopped it. Not a
postmortem; just enough for the next rotation to recognize the same shape.

## Quiet hours

Alerts that are not customer-visible do not page anyone between ten at night and seven in the morning. They queue
and are delivered in the morning digest. The exception is any alert tied to a SEV1 signal, which pages regardless
of the hour.
