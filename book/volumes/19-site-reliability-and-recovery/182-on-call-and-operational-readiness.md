---
book: The Complete DevOps Engineering Book
volume: 19
volume_title: "Site Reliability and Recovery"
chapter: 182
title: "On-call and Operational Readiness"
slug: on-call-and-operational-readiness
status: complete
summary: ../../_ai/chapter-summaries/182-on-call-and-operational-readiness.md
---

# Chapter 182 — On-call and Operational Readiness

**Section outline:** build a staffed, sustainable response path; make alerts actionable and ownership clear; prepare services with runbooks, access, dependencies and recovery checks before they need an on-call engineer.

## Why readiness is a service property

DispatchDesk starts receiving a surge in failed order submissions at 03:15. The alert reaches an abandoned team alias, the runbook links to a retired dashboard, and the only engineer with production access is on holiday. The service was monitored, but the response system was not ready to act. On-call readiness includes people, permissions, information and recovery options as well as telemetry.

On-call coverage is a promise that a named responder can acknowledge and act within an agreed timeframe. Its design should follow the service's user impact and SLO, not a generic rota template. Define who is primary, who backs them up, when a page escalates, who can make a service-impacting decision and which partner team owns a dependency. Publish current contact and escalation paths in systems responders can reach during an outage.

## Staff a sustainable rotation

Match the rotation to the real coverage requirement. Define supported hours, response expectations, primary/secondary responsibilities, escalation delays, handoff time and coverage for leave or regional holidays. A rota with one name and no fallback is a single point of failure. A rotation with too few trained people may meet the calendar while producing fatigue and unreliable response. If staffing cannot support the desired coverage, narrow the service commitment, arrange an explicit partner escalation or reduce the operational load; do not hide the gap behind an unattended pager.

Clarify what each notification means. A page interrupts someone because a human should act promptly to reduce current or imminent user harm. A ticket requests timely follow-up during working hours. A log or dashboard preserves information without demanding immediate attention. Every page needs an owner, a user-impact statement, an acknowledgement expectation and an action path. Group alerts from the same incident to reduce fan-out, but preserve the underlying signals for diagnosis.

Measure response load and health of the rotation: pages per shift, after-hours interruptions, acknowledgement time, escalation misses, repeat pages, time spent on incident response and unplanned work. These measures help identify bad alerting and understaffing; they should not rank individuals or punish someone for receiving difficult events. Establish a mechanism to review overloaded periods and rebalance service work, alert thresholds or rota size. Follow local labor, compensation and rest requirements rather than assuming one organization's staffing norm is universal.

Every handoff should transfer current state, not just a calendar assignment. The outgoing responder should identify open incidents, risk decisions, changes in progress, temporary silences, expiring exceptions and the next scheduled maintenance. Include incident links, owners and expiry times. The incoming responder should acknowledge that they can reach the alert channel, runbook, service dashboards and escalation contacts. Do not include live passwords or tokens in handoff notes; provision named, auditable access through the standard identity system.

## Make the service operable before an incident

For each critical service, maintain an operational readiness record with:

- service owner and dependency owners, supported hours, customer impact and current SLO;
- dashboards for user-visible availability, latency, correctness, traffic, saturation and dependencies;
- page criteria, tested alert routes, fallback contact and escalation timing;
- a concise runbook for the first diagnostic steps, safe mitigations, rollback or isolation, and verification;
- access prerequisites with break-glass procedure and audit trail;
- deployment, configuration, secret and artifact references needed to identify the running version;
- backup, restore, failover and data-integrity references with last exercise date and known limitations;
- status communications, incident command and privacy/security escalation routes.

A runbook should answer the responder's immediate questions: what is broken for users, what changed, what is safe to try, how do I know it worked, and when should I escalate? Write steps as bounded actions with expected observations and stop conditions. Include the context or environment needed for a command. Avoid an unreviewed command that deletes state, broadens privileges or masks the symptom. Link detailed procedures when the first-response page would otherwise become too long.

Readiness includes observability quality. Verify that alerts route to the current schedule and that a test notification reaches the primary and escalation path. Ensure the service has at least one end-to-end signal and that alert conditions correspond to actionable user-impact or imminent resource exhaustion. Test when telemetry is absent, stale or malformed: silence caused by a dead collector should be detectable. Keep dashboards and runbook links under change control, and check them after service ownership, names, labels or monitoring systems change.

Access must be both available and controlled. A responder should use an individual identity with the minimum role needed for the task; standing administrator credentials stored in a runbook create a second incident. Break-glass access should be time-bound, logged and reviewed. Practice access recovery when the identity provider, VPN, secret manager or primary cloud region is part of the incident. Document what work can safely proceed with read-only access and what requires a second approver.

Keep an inventory of dependencies and their failure modes. For a user-facing API, the path may include DNS, edge proxy, identity provider, queue, database, payment integration and third-party messaging. Record owner, health signal, escalation contact and any dependency-specific timeout or degraded mode. Be precise about whether the team owns the component, consumes it, or only sees its external symptoms. Resilience plans should state what happens when the dependency is slow, unavailable, inconsistent or recovering.

## Validate readiness and repair gaps

Review readiness at launch and after significant changes to ownership, architecture, identity, dependencies or recovery design. Use a staged checklist rather than treating an approval meeting as proof. Confirm that the service has an owner; the alert routes; the primary and backup can access the required tools; the runbook points to current resources; and the documented rollback or degradation path preserves data. Record unresolved gaps with a risk owner, due date and interim mitigation.

A simple readiness exercise can simulate one alert without changing production: ask the scheduled responder to locate the service dashboard, identify the alert's likely user impact, find the escalation contact and explain the first safe diagnostic step. A more advanced game day can test failover or restore in an isolated environment. These activities have different risk and evidence; a paper walkthrough does not prove a live restore, and a test notification does not prove that an incident was detected.

For DispatchDesk, the first response reveals that every high-priority API page routes only to the primary engineer. The current secondary can read the runbook but lacks the production read-only role, while the write-up still references a retired dashboard. The team adds an independently routed fallback, provisions individual read-only access, updates and tests the dashboard links, and changes the alert to group related dependency failures under one incident. A later exercise confirms the on-call can identify the affected dependency and notify its owner without using shared credentials. The team separately schedules a staging restore test, because the exercise did not validate data recovery.

Exercises:

1. A page goes to the primary but receives no acknowledgement. What escalation and coverage information must already exist?
2. An alert fires every night for a condition that has no safe responder action. Should it page, become a ticket, or be removed? What evidence informs the decision?
3. A responder cannot access the dashboard because the identity provider is unavailable. Which access and escalation dependencies should readiness cover?
4. A tabletop confirms everyone knows the restore procedure. What additional evidence is required before claiming backups are recoverable?

Answer guidance: define acknowledgement timeout, backup schedule/contact and escalation ownership; assess user impact, urgency and safe action before choosing page/ticket/log, then inspect the alert's actionable rate and missed incidents. Document alternate access and a controlled break-glass route tested without exposing shared credentials. A tabletop proves procedural familiarity only; restore a representative backup in an isolated environment, validate data integrity and application behavior, measure recovery time against the objective, and record limitations.

Review questions:

- What makes on-call coverage a real service capability?
- How should a team distinguish pages, tickets and logs?
- What does a service readiness record give an on-call responder?
- Why do a tabletop and a restore test provide different evidence?

Takeaways:

- Staff a named, trained primary and fallback with clear response and escalation expectations.
- Keep alerts actionable, group related notifications and measure operational load to repair systemic overload.
- Maintain tested runbooks, individual access, ownership and recovery references alongside service telemetry.
- Distinguish a communication exercise from a test that demonstrates actual system recovery.

## Sources checked 2026-10-04

- [Google SRE: Being On-Call](https://sre.google/sre-book/being-on-call/) — rotation, escalation, workload sustainability and actionable alerting principles.
- [Google SRE: Service Best Practices](https://sre.google/sre-book/service-best-practices/) — operational coverage and balancing reliability work.
- [Google SRE: Tracking Outages](https://sre.google/sre-book/tracking-outages/) — alert acknowledgement and escalation-system concepts.
- [Chapter 181 — SLIs, SLOs and Error Budgets](181-slis-slos-and-error-budgets.md) — user impact and actionable reliability alerts.

The staffing figures in the cited Google materials describe that organization's practices, not universal minimums. This chapter presents no claims about DispatchDesk's actual rota, response times, backup integrity or tested recovery.
