---
id: ops-runbook
title: Runbooks and quarterly drills
tags: runbook, drills, credentials, incidents
---
## What a runbook is

A runbook is a procedure a tired person can follow at three in the morning without thinking. It has a trigger, a
sequence of commands, a verification step, and a rollback. If a runbook needs judgment, it is not a runbook; it is
a note that says "ask someone senior", which is honest but should be labelled that way.

Every service has at least three runbooks: deploy, rollback, and credential rotation. The rotation runbook is the
one most often skipped in practice, which is why the quarterly drill exists.

## The rotation drill

Once a quarter, each service owner runs the credential rotation runbook end to end in production, during business
hours. The drill is not a test environment exercise: the point is to prove the overlap window works with real
traffic and real consumers. Expected duration is forty minutes. If it takes longer, the runbook is wrong or a
consumer is undocumented.

The drill produces three artifacts: a timestamped log of the rotation, a list of consumers that failed and had to
be fixed, and an updated runbook. The third artifact is the only one that survives.

## The restore drill

Backups that are never restored are a rumour. Every quarter, the owner restores a snapshot into an isolated
environment and runs the smoke checks against it. Record the time to restore and compare it with the target in the
service level objective. A restore that takes longer than the target is an incident waiting for a date.

## Runbooks go stale

A runbook that has not been executed in two quarters is presumed broken. The owner either runs it or deletes it.
Deleting is a valid outcome: a runbook nobody trusts is worse than no runbook, because it creates false
confidence during an incident.
