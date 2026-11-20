---
id: ops-backups
title: Backups and restores
tags: backups, restore, snapshots, database
---
## What is backed up

Every production database is snapshotted every six hours, and the write-ahead log is shipped continuously. Object
storage is versioned rather than snapshotted, so a deleted object can be recovered by version. Configuration lives
in version control and is not backed up separately; a backup of a git repository is called a clone.

The backup job reports success only after it verifies that the snapshot is readable. A snapshot that exists but
cannot be mounted is a failed backup, and the job treats it as one.

## Restore procedure

Restore into an isolated environment first. Confirm row counts for the three largest tables and run the smoke
checks against the restored copy. Only then decide whether to restore over production, and if so, take a fresh
snapshot of production immediately before, so the restore itself is reversible.

A restore over production requires an incident number and the service owner. The number is not bureaucracy: it is
what lets the postmortem find the data that was overwritten.

## Targets

The recovery point objective is fifteen minutes of data loss, which the continuous log shipping satisfies. The
recovery time objective is two hours for a full restore. Both targets are measured in the quarterly restore drill,
not assumed.

If a restore takes longer than two hours, the target is wrong or the procedure is. Either answer requires a
written decision, not a shrug.

## What is not covered

Analytics warehouses and search indexes are rebuilt from source rather than restored. Rebuilding takes longer than
restoring, and the runbook for each says so, so nobody discovers it during an incident.
