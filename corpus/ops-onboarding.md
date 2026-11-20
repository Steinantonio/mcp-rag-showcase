---
id: ops-onboarding
title: Your first week on call
tags: onboarding, access, on-call
---
## Before day one

Your manager files an access request before your start date. Access is granted by role, not by person: the
`engineer` role includes read access to dashboards, the incident channel and the deployment pipeline, but not the
credential vault. Vault access needs a second approver and is granted only after the security briefing.

You receive a laptop with the standard image, a hardware key registered to your account, and a pager account that
stays disabled until you finish the on-call shadow week. Do not ask for production credentials during onboarding.
Ask for a shadow shift instead.

## Day one to day three

Read the runbook index, then the incident history for the last ninety days. The history matters more than the
policies: it shows which alerts fire at night and which ones nobody answers. Open the monitoring dashboard and find
the four service-level indicators we track. If you cannot find one of them, that is a documentation bug and worth
reporting.

Pair with your buddy on one deployment. You drive, they watch. The goal is not to ship something; it is to see how
a change moves from a pull request to production and where it can stop.

## Day four to day five

Take a shadow on-call shift. You do not carry the pager. When an alert fires, write down three things: what the
alert said, what the dashboard showed, and what the responder did first. Compare notes with your buddy afterwards.
Most new engineers discover that the first action is almost never the fix; it is confirming the blast radius.

By the end of the week you should be able to answer three questions without help: who is on call right now, where
the runbooks live, and how to open an incident. If any answer is unclear, the onboarding checklist is incomplete.

## Access you will not get

Production database credentials, the payment provider console, and the root account of the cloud tenant are not
part of onboarding. They are granted per task, time-boxed, and logged. A request that says "for convenience" is
rejected by default.
