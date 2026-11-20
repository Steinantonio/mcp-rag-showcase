---
id: ops-access-review
title: Quarterly access review
tags: access, review, permissions, security
---
## Why quarterly

Permissions accumulate. Someone joins a project for a month and keeps the role for a year. The quarterly review
is the only mechanism that removes access nobody remembers granting, and it is scheduled rather than triggered
because access that is never used never generates a signal.

## The procedure

Each system owner exports the list of principals and their roles. The export is compared with the previous quarter,
so the reviewer sees additions rather than a wall of names. For every addition the reviewer answers one question:
would this person still need this access if they changed teams tomorrow?

Anything that cannot be justified in one sentence is removed. Re-granting takes minutes; an unnecessary
permission can last years.

## Least privilege in practice

The default role grants read access to dashboards and logs. Write access to a production system is granted per
task, time-boxed to thirty days, and recorded with the ticket that justified it. Standing write access exists only
for the on-call rotation, because paging someone who cannot act is worse than the risk.

Break-glass access exists for emergencies: it is always available, always logged, and always reviewed within
twenty-four hours. The review is what makes it safe, not the approval flow.

## Evidence

The review produces a table: principal, role, decision, date. The table is the deliverable. A meeting that ends
with "looks fine" produces nothing and will be repeated next quarter with the same result.
