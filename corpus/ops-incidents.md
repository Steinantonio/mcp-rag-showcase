---
id: ops-incidents
title: Incident severity and response
tags: incidents, severity, on-call, postmortem
---
## Severity levels

A SEV1 is total loss of the primary customer path or confirmed data exposure. A SEV2 is significant degradation
with a workaround, or a broken secondary path. A SEV3 is a partial or cosmetic problem with no customer impact. The
severity is set by the first responder within ten minutes and can be raised later; lowering it requires the
incident commander.

Severity drives who is paged, not how hard people work. A SEV3 does not need a war room, and treating it like one
trains the team to ignore the pager.

## First ten minutes

Confirm the blast radius before touching anything. Check the dashboard, then the error rate, then the deploy
history. The most common cause of a long incident is a responder who applied a fix to the wrong service because
they skipped confirmation.

Open the incident channel, state the severity, and name an incident commander. The commander does not debug; they
keep the timeline, ask for updates every fifteen minutes, and decide when to escalate.

## Postmortems

Every SEV1 and SEV2 gets a written postmortem within five business days. The document has a timeline with
timestamps, the contributing factors, and at least one action item with an owner and a date. Blameless does not
mean vague: "human error" is not a contributing factor, it is a missing guardrail.

Action items without an owner are wishes. The incident commander is responsible for creating the tickets before
closing the postmortem.

## When to declare

Declare early. A declared incident that turns out to be nothing costs thirty minutes of attention. An undeclared
incident costs the afternoon of everyone who noticed it separately.
