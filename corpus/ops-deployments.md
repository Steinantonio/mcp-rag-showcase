---
id: ops-deployments
title: Deploying and rolling back
tags: deployments, rollback, canary, pipeline
---
## The pipeline

Every change moves through the same four stages: build, test, canary, full rollout. The canary receives five
percent of traffic for ten minutes. If the error rate or the latency of the canary differs from the baseline by
more than the configured threshold, the rollout stops automatically and the previous version keeps serving.

No stage is skipped because the change is small. Small changes cause incidents at the same rate per deploy as
large ones, and the pipeline is what makes the rate visible.

## Rolling back

A rollback is a redeploy of the previous artifact, not a revert commit. The artifact is immutable and the pipeline
keeps the last ten, so a rollback takes about ninety seconds and does not require a build.

Reverting the commit is a separate action, done after the service is healthy, so that the next deploy does not
reintroduce the problem. Doing both at once is how teams end up rolling back the rollback.

## Database changes

A deploy that changes the schema runs in two steps: expand, then contract. The first deploy adds the new column
and writes to both; the second, a week later, removes the old one. A single-step migration that drops a column is
rejected in review, because it makes the rollback impossible.

## Friday and holidays

Deploys are allowed whenever the author is available for two hours afterwards. The rule targets availability, not
the calendar. A team that bans Friday deploys and allows an unrehearsed Tuesday migration has optimized the wrong
variable.
