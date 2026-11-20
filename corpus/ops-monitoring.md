---
id: ops-monitoring
title: Monitoring, alerts and error budgets
tags: monitoring, alerts, slo, latency
---
## The four signals

Every service exposes four signals: request rate, error rate, latency at the ninety-fifth percentile, and
saturation of its scarcest resource. A dashboard that shows twenty metrics but not these four is decoration.

Latency is measured at the edge, not inside the handler. Internal timing is useful for debugging and useless for
promising anything to a customer.

## Alerts that deserve a pager

An alert pages a human only if it is actionable, urgent and customer-visible. Everything else becomes a ticket or
a dashboard. The test is simple: if the alert fires and the correct response is "wait", it should not page.

Every alert has a runbook link in its description. An alert without a runbook is a defect filed against the
service owner, not against the on-call engineer who received it.

## Error budgets

Each service has a service level objective expressed as a success ratio over thirty days. The error budget is what
remains. When the budget is exhausted, feature work on that service pauses until the ratio recovers or the
objective is renegotiated in writing.

The budget is not a punishment mechanism. It is the only honest way to answer "can we afford this risk" without
arguing about feelings.

## What we do not monitor

We do not monitor individual engineers, and we do not alert on deploy frequency. A metric that changes behavior
without changing customer experience is a metric that will be gamed.
