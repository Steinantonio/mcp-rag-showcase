---
id: ops-changelog
title: Changelog of operations policy
tags: changelog, policy, history
---
## This quarter

**Rotation window shortened.** The overlap between the old and new API key went from seventy-two hours to
twenty-four. Seventy-two hours was chosen when three services consumed the same key; that is no longer true, and
the longer window kept leaked credentials alive for a day longer than necessary.

**Friday deploy rule replaced.** The calendar ban became an availability rule: deploy when the author can respond
for two hours afterwards. The ban had moved risk to Monday morning, where it collided with the weekly planning.

**Restore drill made mandatory.** Restores are now exercised quarterly per service, with the time to restore
recorded. Two services had never restored from a snapshot before this policy.

## Last quarter

**SEV3 no longer pages.** Low-severity alerts became a morning digest. The pager volume dropped by sixty percent
and the response time to SEV1 did not change.

**Access review moved to a scheduled export.** The previous review started from a blank spreadsheet, which meant
nobody could see what had changed since the previous quarter. Comparing exports turned a two-hour meeting into a
forty-minute one.

**Egress declarations required.** Wildcard outbound rules were removed from every service definition. Three
services failed at first because their dependency was undocumented, which was the point.

## Older changes

**Backup verification added.** The backup job previously reported success when the snapshot file existed. It now
verifies that the snapshot mounts.

**Retention windows assigned.** Every dataset received an owner and a window; unowned datasets were scheduled for
deletion.

## How to change a policy

Write the change, the reason, and the date in this file in the same pull request that changes the behavior. A
policy change without an entry here is a rumour.
