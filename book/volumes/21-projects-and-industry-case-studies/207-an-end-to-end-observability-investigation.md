---
book: The Complete DevOps Engineering Book
volume: 21
volume_title: "Projects and Industry Case Studies"
chapter: 207
title: "An End-to-end Observability Investigation"
slug: an-end-to-end-observability-investigation
status: complete
summary: ../../_ai/chapter-summaries/207-an-end-to-end-observability-investigation.md
---

# Chapter 207 — An End-to-end Observability Investigation

**Section outline:** instrumentation and user symptoms; metrics, logs and traces; a slow-order incident and resolution.

## Begin with the user symptom

At 09:12, DispatchDesk support reports that some customers wait several seconds after submitting an order. The web page eventually shows success, but the confirmation email arrives late. The team avoids starting with “CPU is high” and defines the symptom: successful order submission should return within 500 ms at p95, while asynchronous confirmation should be enqueued within two seconds. The actual target is fictional and must be agreed with product owners.

Check the service-level indicator by route and outcome, compare current and prior periods, then determine whether the latency is broad or isolated to a cohort. Ensure the metric counts valid user attempts and captures failures. A dashboard showing average latency can hide a small group of severe stalls. Chapter 143 develops PromQL investigation; Chapters 145–149 cover alerting, logs and tracing tools.

## Join evidence across signals

Metrics show p95 order submission increased from 180 ms to 2.4 s while request volume stayed near baseline. Error rate remains low because requests eventually succeed. Queue age for confirmation mail is elevated. Host CPU and memory are normal. This points toward waiting rather than saturation but does not establish cause.

The team chooses a slow trace and follows the request across API, order database, event publisher and email worker. The API span includes a 1.8-second synchronous call to a shipping-rate provider before the order transaction commits. Logs with a trace ID show repeated timeout and retry messages from the provider client. Avoid putting customer email or full order contents into metric labels; sensitive context is kept out or access-controlled in structured logs.

A trace can be incomplete because sampling, instrumentation gaps or asynchronous context propagation omit spans. Check trace coverage and clock assumptions before treating the picture as complete. Correlate with deploy/configuration change records and dependency health. Avoid broad dashboard searching without a hypothesis; choose the next query that can distinguish a cause.

## Mitigate, verify and prevent recurrence

The provider's latency began after a routing/config change. The API was designed to require a shipping quote before creating an order, even though product rules allow a provisional quote. The team disables the unsafe retry increase, restores the prior route and confirms p95 recovers. It then tests a design where order intent is committed idempotently and shipping calculation proceeds asynchronously with a clear customer-visible pending state. The API does not falsely claim a final rate before one exists.

The team monitors order acceptance, quote completion, queue age and duplicate rate during the staged rollout. It adds a dependency timeout budget that fits the user response contract and ensures retries use idempotency keys. The postmortem assigns an owner to make provider latency visible before customer impact. It reviews whether the SLO alert would have paged at an actionable time and keeps a dashboard link in the runbook.

For each incident, preserve the timeline and queries, distinguish observation from inference, and record what evidence would falsify the favored cause. A successful mitigation proves impact decreased; it does not prove every root cause. Follow with a controlled reproduction or code-level analysis before closing the causal action.

Before making the code change, the incident lead checks whether the behavior affects every tenant, one region or only requests using the slow shipping provider. The team uses a trace exemplar with no customer payload, verifies the span timestamps and compares healthy requests to slow ones. It checks connection-pool wait because client-side queueing may occur before the database span, and reads the latest deployment/configuration history. A bounded synthetic order uses a non-billing test account to validate the provider route. The rollback is approved because the new route is the only changed factor and the old configuration remains valid. The incident timeline separates these observations from the hypothesis that retry behavior caused the delay; a later controlled test confirms the retry amplification.

 The team also checks instrumentation quality during routine service reviews. It runs a known synthetic journey, verifies trace context crosses queue boundaries, checks that error events retain correlation IDs and reviews whether important alerts have a responder and a useful runbook. Sampling settings are documented so investigators know which requests are absent by design. A missing span is treated as missing evidence rather than proof that a dependency was not called.

Exercises:

1. Average latency is normal but p99 is four seconds. Which breakdowns help find a localized problem?
2. A trace lacks a database span and the database dashboard is healthy. Can the team rule out database delay?
3. Error rate improves after raising retries, but queue age and duplicates increase. Which outcome should guide the next mitigation?
4. A deployment happened shortly before the incident. What evidence establishes whether it is causal?

Answer guidance: inspect percentiles by route, dependency, region, tenant cohort where cardinality/privacy permits, request class and release; compare counts and exemplars. No: instrumentation or sampling may omit it, and database metrics may not reflect client-side pool wait; inspect connection wait, query evidence and trace coverage. User-visible completion and duplicate/business correctness matter; revert retry amplification and control backlog rather than optimizing one metric. Compare changed code/config path to observed traces/logs, reproduce or isolate with rollback/canary, and look for a specific mechanism; temporal order alone is not causation.

Review questions:

- How should an investigation translate a support report into measurable symptoms?
- What does each signal add, and what can it fail to show?
- How do teams test a hypothesis without confusing correlation and cause?
- Which user and system measures verify a mitigation?

Takeaways:

- Begin with the affected user journey and a measurable symptom.
- Combine metrics, logs, traces and change evidence while accounting for missing telemetry.
- Mitigate within business and safety constraints; validate the actual outcome.
- Turn confirmed causes into owned changes and update the runbook and alerts.

## Sources checked 2026-10-04

- [OpenTelemetry observability primer](https://opentelemetry.io/docs/concepts/observability-primer/) and [context propagation](https://opentelemetry.io/docs/concepts/context-propagation/) — signals and cross-service context.
- Chapters 141–150, 181, 183–185 — observability workflow, service objectives and incident learning.

The incident, thresholds and recovery are fictional. No telemetry or production system was accessed.
