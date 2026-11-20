---
id: ops-cost-controls
title: Cost controls and budgets
tags: cost, budget, spend, idle
---
## Budgets per service

Every service has a monthly budget expressed in money, not in instances. The budget is visible on the same
dashboard as latency, because cost that is invisible is cost that surprises. When a service reaches eighty
percent of its budget, the owner gets a ticket; at a hundred percent, non-production environments are scaled down
automatically.

Scaling down non-production is safe by design: nothing that matters runs there. If something does, that is an
availability bug in the environment, not a reason to disable the guardrail.

## The three usual leaks

Idle resources, retention without a window, and cross-region traffic. Idle resources are the easiest to find:
anything with a low request rate and a fixed size is a candidate. Retention without a window grows forever
because nobody scheduled the deletion. Cross-region traffic is invisible until the invoice arrives, so the
architecture review asks about it explicitly.

## Cost of a deploy

Deploys are free at our scale, but canary infrastructure is not: a canary doubles the running instances for ten
minutes. That is a deliberate purchase, and the alternative, deploying without a canary, has cost more than once.

## What we do not optimize

We do not optimize the cost of observability below the level that lets us answer questions during an incident.
Cheap monitoring is expensive the first night it is needed.
