---
id: ops-data-retention
title: Data retention and deletion
tags: retention, data, backups, privacy
---
## Retention windows

Customer records are retained for as long as the account is active plus ninety days. Backups follow the same
window, which means a deleted record can reappear in a restore for up to ninety days after deletion. Support must
say this explicitly when a customer asks for deletion, because "deleted" and "unrecoverable" are different
promises.

Application logs are kept for thirty days. Audit logs are kept for one year. Metrics are aggregated after ninety
days and raw samples are dropped.

## Deletion requests

A deletion request is executed within thirty days, verified by a query that returns zero rows, and recorded in the
privacy log. The verification is the deliverable: a ticket that says "done" without a query result is not
evidence.

Deletion does not touch backups, because rewriting history in a backup invalidates every other restore. The
retention window is how the backup copy expires on its own.

## Data that never leaves

Production data is not copied into development environments. Synthetic data is generated for tests, and the
generator is versioned alongside the schema. When a bug only reproduces with real data, the investigation happens
in a read-only replica with access logged, not in a laptop copy.

## Retention is a cost decision

Storage is cheap; the compliance surface is not. Every dataset has a named owner and a stated retention window.
A dataset with no owner is scheduled for deletion after one quarter, which is the fastest way to find out whether
anyone still needed it.
