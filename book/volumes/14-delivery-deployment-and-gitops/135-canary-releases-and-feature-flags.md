---
book: The Complete DevOps Engineering Book
volume: 14
volume_title: "Delivery, Deployment and GitOps"
chapter: 135
title: "Canary Releases and Feature Flags"
slug: canary-releases-and-feature-flags
status: complete
summary: ../../_ai/chapter-summaries/135-canary-releases-and-feature-flags.md
---

# Chapter 135 — Canary Releases and Feature Flags

## Why expose a change gradually

A full production rollout asks every user to trust a new release at once. A canary reduces that initial exposure: a small, deliberate part of production receives the change, operators compare its behavior with an appropriate baseline, and the release advances only when evidence meets the agreed policy. This is useful when staging cannot reproduce the full range of production traffic, data shape, dependency behavior, or load. It is also useful when failures have meaningful blast radius, so early detection can limit user impact.

Canarying is not just “deploy to one server first.” The candidate group needs enough representative traffic and enough time for relevant failures to appear. A canary that receives ten requests may miss a rare customer workflow; an off-peak test may not reveal a latency regression under peak concurrency. Google’s SRE Workbook defines canarying as a partial, time-limited deployment and emphasizes representative traffic, attributable metrics, sample size, and avoiding noisy signals that reduce operator trust ([Canarying Releases](https://sre.google/workbook/canarying-releases/)).

Canary release and feature flag solve related but different problems. A canary changes which software version handles a selected portion of traffic. A feature flag changes which behavior is enabled for selected users or requests, often while all servers run the same binary. A flag can decouple deployment from feature exposure; it cannot replace a safe deployment process for the code that evaluates it. Combining both can limit exposure further, but makes it important to know whether an error came from the new binary, the flagged behavior, or their interaction. Chapter 134 compares rolling and blue/green infrastructure patterns; this chapter focuses on cohorts, evidence, and stopping a harmful change. [Chapter 136](136-database-and-message-compatibility.md) covers keeping old and new versions compatible during overlap.

## Cohorts, metrics, and decision windows

First define the cohort. It may be a percentage of requests routed to a candidate pool, a set of hosts or cells, or stable user/account identities selected by a deterministic rule. These are not interchangeable. A request-based 5% canary may send different versions to the same person on consecutive requests, which can break a workflow with in-memory state or multi-step transactions. A user-based cohort can keep a customer consistently on one behavior, but may create unequal request volume between control and treatment. Write down what “5%” means, who is eligible, and how the cohort is kept stable.

For a routing canary, keep the stable and canary versions identifiable in telemetry. Record the release digest or version, cohort, start time, traffic share, and promotion decision. Confirm that the router is actually sending the intended cohort to the candidate and that the candidate’s metrics can be separated from baseline. Without that separation, a graph that combines both groups can hide degradation in the small population. An uneven traffic split or a low-volume control is also a poor comparator. Avoid sampling or labels that accidentally put customer identifiers or secrets in metrics.

Choose a small set of signals tied to user and service health. A useful set may include request success rate, latency percentiles, correctness of a key operation, saturation, and a dependency-specific signal such as queue age. Compare the candidate against its control and against a fixed pre-release baseline where appropriate. Define thresholds before rollout: for example, pause if the candidate’s server-error rate exceeds the stable group by a specified margin for two consecutive windows, or if a synthetic DispatchDesk order fails. Exact thresholds come from service objectives and normal variability; a generic “error rate under one percent” can be dangerously permissive for a service whose normal rate is far lower.

Metrics must be attributable and statistically useful. A service-wide CPU increase may be caused by a traffic spike rather than the release. A single failure may be a real critical defect or a transient unrelated dependency issue. Decide which signals are immediate stop conditions, which require a sustained window, and which are diagnostic rather than promotion gates. Low traffic often needs a longer observation period to gather representative requests. High request volume does not guarantee coverage of rare paths, asynchronous work, scheduled jobs, or long-lived sessions. Combine telemetry with targeted synthetic transactions and business correctness checks.

A staged rollout might use this illustrative schedule:

| Stage | Exposure | Minimum evidence before proceeding |
|---|---:|---|
| Internal | Employee/test identities only | Startup, authentication, core synthetic transaction |
| Initial canary | 1% of eligible traffic | No stop condition; minimum sample and observation window reached |
| Wider canary | 5% then 25% | Candidate remains within the agreed error, latency, and saturation bounds |
| General availability | 100% | No unresolved alert; monitoring and rollback remain active through the bake period |

The percentages are examples, not a prescribed rollout policy. If the candidate reaches a failure threshold, stop increasing exposure and route traffic back to the stable version or disable the relevant feature. If the canary receives too little traffic to decide, keep it paused or choose a different validation method; do not label “no observed failure” as proof. A promotion record should retain the cohort definition, signal windows, thresholds, actual sample counts, operator or automation decision, and exact candidate digest.

## Flag lifecycle and rollback control

A feature flag is a runtime decision with an owner, default behavior, targeting rules, and an operational lifecycle. Teams often use flags for several purposes: release toggles that hide unfinished code, experiment toggles that compare behavior, operational switches that disable expensive or risky work, and permission controls that determine who may access a capability. These purposes have different risk and audit requirements. A release flag may be temporary; a permission flag may be long-lived and security-sensitive; a kill switch must be fast and safe when turned off.

Design flag evaluation so that the application remains understandable during provider or network failure. Choose a safe default for missing, malformed, stale, or unavailable configuration. For a nonessential recommendation feature, “off” may preserve the core order flow. For a safety-critical validation, silently defaulting to “off” could allow invalid work; the correct fallback may be to reject or pause the operation. Avoid a universal default rule. Document whether flag values are fetched at startup, polled, cached, or evaluated locally, and how quickly a change should reach all instances. A remote flag platform can itself become a dependency if every request waits synchronously for evaluation.

Use stable targeting keys that match the rollout intent. A customer or tenant cohort should normally remain consistent during an experiment; randomizing every request can send users through inconsistent workflows and contaminate comparisons. Keep targeting rules reviewable, limit who can change production flags, and log the evaluated flag key and variation without logging unnecessary personal data. Consider interactions among flags: if a new checkout path depends on a new payment client and both toggles are independently active, the combined configuration needs explicit testing. Many flags create a large state space and can make support reports impossible to reproduce.

Every temporary flag needs an owner and a removal condition. Once a release is fully enabled and stable, remove stale branches and their tests. Otherwise future code must preserve both paths indefinitely, and operators may flip an old control whose behavior is no longer understood. Review flags on a schedule, search for expired toggles in code, and remove them through normal review. Keep security authorization separate from a convenience release toggle: a client-visible flag is not an access-control boundary.

An operational kill switch is useful only if it has a tested control path, safe fallback, clear authority, and observable result. Practice disabling the feature while under load. Confirm that existing work drains or is handled safely, the flag reaches all serving instances within the expected time, and dashboards show the active state. An emergency flag may stop new expensive work without undoing work already queued or reversing side effects already sent. Record who changed it and why; after an incident, decide whether to keep it off, repair forward, or re-enable gradually.

Configuration rollout products can support staged exposure and alarm-driven rollback, but their behavior is product-specific. For example, AWS AppConfig can associate a deployment with CloudWatch alarms and automatically roll back configuration when an alarm fires during deployment monitoring. Reverting a deployment that already completed is a separate operation with its own time limit and permissions; it does not mean alarms monitor that configuration indefinitely. Either operation affects AppConfig configuration, not an arbitrary container image or database state. Understand the exact resource and deployment phase involved ([AWS AppConfig rollback and revert](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-deploying-reverting.html)). OpenFeature standardizes an API for evaluating feature flags and exposes evaluation lifecycle hooks, but it does not prescribe your targeting policy, provider availability, safe default, or rollout thresholds ([OpenFeature concepts](https://openfeature.dev/docs/reference/concepts/)).

## Stopping a harmful release early

DispatchDesk is releasing a new fraud-review path behind a flag. The code is deployed to every API instance, but the flag enables it only for a stable 1% cohort. During the first hour, overall request success looks unchanged. A cohort-specific metric shows that 8% of flagged orders fail when a particular payment provider returns a delayed response. The failed assumption was that healthy HTTP requests represented successful business outcomes. The right response is to stop exposure, disable the flag or exclude the affected provider cohort, and preserve request IDs and evaluation metadata for diagnosis. Do not continue to 5% just because aggregate error rate remains under a broad threshold.

For an infrastructure canary, a new API digest receives 5% of traffic through a routing rule. Its target health remains green, but p95 latency doubles and queue age begins rising. Stop the rollout, route new traffic back to stable, and confirm target weights and active version. Then inspect downstream saturation, connection pools, request mix, and release-specific telemetry. If the canary processed writes or enqueued messages, determine whether those records are compatible with the stable version before retrying. Reverting traffic is not equivalent to undoing side effects; this is one reason Chapters 134 and 136 emphasize shared-state compatibility.

Pre-agree on who can halt a rollout and what action the system takes. An automated analysis failure may pause at a step or abort and restore the stable routing weight, depending on the controller. An operator may need to stop promotion even while metrics remain within thresholds if data correctness or a security concern appears. Make “pause,” “abort,” “rollback,” and “disable flag” distinct actions in runbooks. A pause holds current exposure for more evidence; abort returns traffic or workload to the stable candidate; rollback changes a release target; disabling a flag changes application behavior. Each action has a different effect and can take a different amount of time.

If progressive delivery is automated, validate its telemetry queries with known-good and intentionally bad test signals before trusting it. Ensure missing metrics, empty samples, query errors, and delayed ingestion do not accidentally count as success. Argo Rollouts, for example, can pause at steps, evaluate analysis, and abort when analysis fails, but the routing integration and analysis definitions determine what actually happens ([Argo Rollouts canary strategy](https://argo-rollouts.readthedocs.io/en/stable/features/canary/), [analysis](https://argo-rollouts.readthedocs.io/en/latest/features/analysis/)). Do not copy a controller manifest from a different version or routing provider without checking its installed documentation.

After stopping a harmful change, confirm the result from user-facing evidence: cohort traffic no longer reaches the candidate, flag evaluation shows the safe variation, critical synthetic flows pass, and error/latency signals recover. Review logs and traces for the affected cohort without exposing personal data. Record whether the system was returned to the old artifact, only the behavior was disabled, or both. Update the release checklist if the canary failed to detect the defect earlier than expected.

## Exercises

1. A canary handles 1% of traffic for five minutes with zero failures. Why may that be insufficient evidence to promote a service with delayed queue processing and diverse customer workflows?
2. A feature flag is evaluated randomly on every request for a multi-step checkout. Explain the user and measurement risks, and choose a more stable targeting key.
3. The canary cohort’s error rate is flat, but its p95 latency is twice the stable cohort and queue age is increasing. What should happen next, and which signals should be investigated?
4. An AppConfig deployment rolls back after a CloudWatch alarm. Does that restore the previous container image and reverse database writes? Explain the resource boundary.
5. A feature flag has been fully enabled for six months, and no one knows its owner. Describe a safe path to remove it.

### Answer guidance

1. Five minutes and a small cohort may not produce enough requests or cover asynchronous, rare, or delayed paths. Define the required sample volume and observation window from traffic and failure characteristics; inspect queue age and correctness signals before promotion.
2. A user can switch behavior between steps, creating inconsistent state; the same account may appear in both control and treatment, weakening attribution. Use a stable account or tenant key, subject to privacy and experiment policy, and ensure a user remains in one cohort for the workflow.
3. Pause exposure or abort according to the pre-agreed stop policy; do not promote based on a flat error rate alone. Verify cohort routing and compare dependency latency, database or downstream saturation, connection pools, queue consumers, and request mix. After returning traffic, confirm whether canary writes/messages need reconciliation.
4. No. The documented rollback applies to the AppConfig configuration deployment. It does not automatically change an ECS/EKS image or reverse external data writes. Those need separate release and data recovery procedures.
5. Identify the flag’s behavior and history, find code paths and tests that depend on it, confirm the enabled or disabled behavior intended for all users, and verify authorization logic is not relying on it. Remove the obsolete branch in a reviewed release, test relevant paths, then delete the flag record under change control.

## Review questions

- What makes a canary representative of production behavior?
- Which attributes distinguish request-based, instance-based, and identity-based cohorts?
- Why is a healthy target group weaker evidence than business correctness and downstream health?
- What safe defaults should a feature flag define for provider and network failures?
- Which actions differ when an operator pauses, aborts, rolls back, or disables a flag?

## Takeaways

- A canary is a partial, time-limited exposure paired with explicit evidence and a promotion decision.
- Choose stable, representative cohorts and compare candidate behavior with an attributable baseline.
- Define sample size, observation windows, stop thresholds, and owners before rollout begins.
- Feature flags control behavior separately from artifact deployment; give each flag a safe default, owner, and removal plan.
- A configuration rollback, traffic rollback, artifact rollback, and data recovery change different parts of the system.

## Further reading

- [Chapter 134 — Rolling Updates and Blue Green](134-rolling-updates-and-blue-green.md)
- [Chapter 136 — Database and Message Compatibility](136-database-and-message-compatibility.md)
- [Google SRE Workbook: Canarying Releases](https://sre.google/workbook/canarying-releases/)
- [AWS AppConfig rollback behavior](https://docs.aws.amazon.com/appconfig/latest/userguide/appconfig-deploying-reverting.html)
- [OpenFeature concepts](https://openfeature.dev/docs/reference/concepts/)
- [Argo Rollouts canary strategy](https://argo-rollouts.readthedocs.io/en/stable/features/canary/)

Sources reviewed 2026-10-04. No canary traffic, feature flag provider, progressive-delivery controller, or configuration rollback was executed.
