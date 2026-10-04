---
book: The Complete DevOps Engineering Book
volume: 19
volume_title: "Site Reliability and Recovery"
chapter: 184
title: "Troubleshooting Under Pressure"
slug: troubleshooting-under-pressure
status: complete
summary: ../../_ai/chapter-summaries/184-troubleshooting-under-pressure.md
---

# Chapter 184 — Troubleshooting Under Pressure

**Section outline:** start from observed user symptoms; form and test bounded hypotheses; use correlated telemetry to isolate a fault domain; mitigate safely and verify the result.

## Start with the symptom and protect users

DispatchDesk's order API pages on a rise in timeouts. One engineer sees database CPU at 90% and begins an emergency resize; another restarts every API worker. Neither action is tied to a confirmed cause. The resize does not help, and the restarts increase retries to an already overloaded database. Under pressure, the goal is to reduce user harm while learning which explanation best fits the evidence.

First confirm the alert from an independent user-facing signal. State what users cannot do, which population or region is affected, when it began and whether the problem is worsening. Check the SLI and compare current behavior with its normal range, traffic and deployment events. Treat a process-up signal as evidence about that process, not proof that the end-to-end service works. Black-box probes reveal user-visible symptoms; white-box metrics, logs and traces help explain them.

If impact is active, take the safest effective mitigation in parallel with diagnosis. Pause a rollout, reduce a harmful retry pattern, route around a failed region or disable a nonessential feature only when the change has a defined scope and rollback. Use the incident command structure in [Chapter 183](183-incident-command-and-communication.md) when multiple responders or system changes need coordination. Record the change, owner, expected signal and stop condition.

## Build and test hypotheses

Write down a small set of plausible causes and the observations each predicts. For example, if a new release caused the timeouts, affected instances may share a version and the symptom may begin near the rollout. If a dependency is saturated, queue time and connection-pool wait may rise before API CPU. If one region has a routing issue, clients or synthetic probes from that region may fail while others remain healthy. These are testable hypotheses, not conclusions.

Use the system's dependency map to move from symptom toward a fault domain: client, DNS/edge, application, identity, queue, data store, network or external provider. Compare affected and unaffected requests, hosts, tenants, zones, regions and versions. Look for a meaningful boundary rather than collecting every dashboard. A request or trace identifier carried across components can connect an upstream failure to downstream logs; do not expose customer secrets when using example traces.

Prefer read-only observations first: error and latency distributions, request volume, saturation, queue age, retry rates, recent changes, dependency health and sampled traces. Confirm query scope, clock range, labels, sampling and retention. Aggregates can mask one tenant or region; a single log line can exaggerate a rare event. Use metrics to establish how often a condition occurs, logs for event detail and traces for a request path, while respecting each system's coverage and sampling limits.

Change one variable at a time when practical and make each test discriminating: it should produce different expected results under competing hypotheses. If a test can disrupt production, use a canary, read-only query or isolated reproduction first. Avoid running a broad debug command that leaks credentials, dumps all customer payloads or changes state. A command returning no result may indicate a bad query, missing permission, expired events or absent telemetry rather than a healthy system.

Maintain an evidence table as the investigation evolves:

| Observation | Supports | Weakens | Next safe test |
|---|---|---|---|
| Timeouts begin after 10% rollout; failures cluster on new image digest | release regression | global network event | pause rollout and compare old/new cohort metrics |
| Database pool wait rises in both image cohorts | shared data-path pressure | image-only code defect | check database latency, connections and queueing |
| Synthetic probe fails only in one region; other-region API and database signals are normal | regional path issue | global database failure | compare edge/DNS route and provider event evidence |

The table is a reasoning aid, not a scoring model. Record evidence that conflicts with the leading theory. If new data changes the best explanation, update the incident state rather than defending the first guess. Use a timebox to escalate an unresolved, high-impact fault to the owner with better visibility or access.

## Mitigate, verify and preserve learning

Choose mitigation based on expected user benefit, reversibility, blast radius and data risk. A rollback is useful when a recent release is strongly implicated and the prior version is compatible with current data. It may be dangerous after a schema migration or when the failing component is not the cause. A restart can clear a transient deadlock but also erase volatile state or intensify a retry storm. A capacity increase can relieve saturation but may overload a downstream dependency or violate a quota. State the prediction, observation window and rollback trigger before acting.

After the change, verify the service at the user boundary and check the dependency/resource signals that motivated the action. Compare a sufficient observation window with request volume and normal variability. Confirm errors and latency recover, queue age drains, background work catches up and no new data inconsistency appears. A green health check immediately after rollout does not establish that delayed jobs or user workflows recovered.

If the symptom changes but does not clear, the mitigation may have reduced one effect without removing the cause. Keep the incident open, update the hypothesis set and revisit scope. If telemetry disappears after a change, do not treat quiet dashboards as proof of recovery. Confirm data collection itself from a separate signal.

For DispatchDesk, responders confirm timeouts at the public API and see the rise begin with a new worker release. The operations lead pauses further rollout. Cohort comparison shows new workers issue a higher rate of retries after a pool timeout, while the database remains healthy for old workers. A small canary rollback reduces retries and restores the request SLI. The team observes the API and queue for a full work-cycle, checks that no orders were duplicated, and keeps the incident in recovery monitoring while tracing the pool timeout. The first CPU theory is discarded because it did not predict the cohort difference or the recovery after reducing retries.

Exercises:

1. API process health is green while external users see elevated timeouts. What independent signals establish the symptom and scope?
2. A new release and a database saturation alert occur at the same time. What cohort or dependency comparisons could separate cause from correlation?
3. A broad restart would likely help one suspected memory leak but could disrupt all tenants. What prediction, scope and rollback evidence should be agreed before the action?
4. Error rates recover after traffic is shifted, but queue age keeps increasing. Is the incident resolved? What else must be checked?

Answer guidance: use synthetic/client-side results and request SLI across region/tenant, then compare service and dependency telemetry. Compare old/new image cohorts and request/retry/pool-wait behavior while checking temporal order and traffic mix. Limit a test to a canary or representative instance, define expected memory and user-impact signals, preserve known-good state and stop if impact increases. The queue shows work remains delayed; verify backlog drains and data correctness over a representative processing interval before closure.

Review questions:

- How do symptoms differ from causes?
- What makes a hypothesis test useful during an incident?
- How should metrics, logs and traces complement one another?
- Why is recovery verification broader than checking whether an alert cleared?

Takeaways:

- Confirm user impact independently, then state scope and timing before choosing a cause.
- Test a small number of hypotheses with evidence that can distinguish them.
- Prefer bounded, reversible mitigation and record its predicted outcome and stop condition.
- Verify user behavior, delayed work, data correctness and telemetry before declaring recovery.

## Sources checked 2026-10-04

- [Google SRE: Effective Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/) — iterative hypothesis testing, system examination and correlated request identifiers.
- [Google SRE: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) — symptom versus cause and black-box/white-box monitoring.
- [Google SRE Workbook: Monitoring](https://sre.google/workbook/monitoring/) — metrics, logs, structured events and tracing roles in diagnosis.
- [Chapter 181 — SLIs, SLOs and Error Budgets](181-slis-slos-and-error-budgets.md) and [Chapter 183 — Incident Command and Communication](183-incident-command-and-communication.md) — user impact and coordinated response.

The example is fictional and no live diagnostics, mitigation, rollback, restart, capacity change or production recovery was executed.
