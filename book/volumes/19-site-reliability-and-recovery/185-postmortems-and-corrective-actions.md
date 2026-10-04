---
book: The Complete DevOps Engineering Book
volume: 19
volume_title: "Site Reliability and Recovery"
chapter: 185
title: "Postmortems and Corrective Actions"
slug: postmortems-and-corrective-actions
status: complete
summary: ../../_ai/chapter-summaries/185-postmortems-and-corrective-actions.md
---

# Chapter 185 — Postmortems and Corrective Actions

**Section outline:** capture an accurate shared account of an incident; investigate contributing conditions without blame; turn findings into prioritized actions with owners, verification and follow-through.

## Why incidents need a written record

DispatchDesk's checkout outage is mitigated and customers can submit orders again. The team is eager to return to feature work, so the follow-up ticket says only “fix retry bug.” A similar failure occurs next month when a different service retries without backoff. The first incident generated activity but did not preserve what happened, why the safeguards failed or how the proposed fix would be verified.

A postmortem is a reviewed record of incident impact, events, response, contributing causes and corrective actions. Its purpose is to preserve learning and reduce the likelihood or impact of recurrence. Define criteria before incidents occur: user-visible impact, data loss or corruption, emergency mitigation, significant duration, a monitoring gap, an expensive recovery, or any stakeholder request. A near miss may deserve a review even when no outage occurred. The exact threshold should reflect service risk and organizational policy.

## Build an evidence-based timeline

Start from the incident record created during response in [Chapter 183](183-incident-command-and-communication.md), then verify times and claims against source evidence. Include detection, user impact, escalation, key decisions, mitigation, recovery and communication. Record timezone and whether an event time is observed, inferred or reported. Resolve conflicting clocks or preserve the disagreement. A timeline should explain how the incident unfolded, not create false precision from incomplete logs.

Describe user impact in measurable terms where evidence supports it: affected requests, users, regions, data integrity, duration, SLI/error-budget cost, support volume and recovery delay. State uncertainty and measurement limitations. Do not infer “no customer impact” merely because the dashboard lacks a matching alert. Keep personal data and secrets out of broadly shared documents; link to restricted evidence only when necessary.

Separate trigger from contributing causes. The trigger is the event that activated the failure mode, such as a deployment or demand increase. Contributing conditions explain why the system entered an undesirable state and why prevention, detection or recovery did not work as intended. A useful investigation asks what information was available to people at the time, which safeguards existed, how components interacted and where the system made failure hard to detect or contain. Avoid using “human error” as a terminal explanation; it describes an action without explaining the conditions that made that action likely or its consequences so large.

Blamelessness means examining system conditions without shaming individuals or teams. It does not mean removing accountability, concealing unsafe behavior or avoiding hard decisions. When an action contributed to an incident, document the context, incentives, interface, training and safeguards around it. The goal is to make the safe and correct action easier and to reduce the blast radius when something goes wrong.

## Create corrective actions that change outcomes

Each action should address a contributing factor and have a verifiable end state. Prefer changes that prevent a class of failure or limit its impact: bounded retries, a circuit breaker, rollout controls, overload isolation, a correctness check, an actionable alert or a recovery mechanism. Monitoring alone may detect a problem without preventing or containing it. Training alone is weak when a tool or workflow makes the unsafe action the path of least resistance.

For each action, record priority, owner, due date, affected service, prevention/mitigation/detection/recovery category, dependency and acceptance evidence. An action such as “make retries safer” is too broad. A stronger item is “cap checkout worker retries by request and time budget, add a test for duplicate-submit behavior, and verify retry rate stays below the agreed ceiling under dependency timeout.” Define the measurement or test before closing the action.

Prioritize by risk reduction, recurrence likelihood, user impact, implementation cost and dependencies. A high-risk prevention action may require architecture work; a smaller mitigation or detection action can reduce exposure while that work proceeds. If an action is deferred or rejected, record the decision owner, residual risk and review date. Do not close an action because a ticket moved to Done; inspect the deployed change or test result and link the evidence to the postmortem.

Review the document with people who operated, built and supported the affected system. Invite partner teams when their components or procedures were involved. A reviewer should challenge the timeline, impact estimate, causal depth and action quality. Share the approved record with teams who can use the learning while protecting customer and employee information. Track action completion and recurring incident patterns in an operational review; writing the report is not the same as reducing risk.

For DispatchDesk, the review finds that a database connection timeout caused workers to retry immediately, while the API's successful response path did not distinguish an accepted order from a completed downstream write. The retry behavior amplified load, and the alert watched pod health rather than order outcomes. The team creates three actions: enforce a bounded retry budget with jitter and backoff; make order submission idempotent and report persistence outcome; alert on the order SLI and retry saturation. Each action names an owner and acceptance test. The team also records what worked: responders paused the rollout, used cohort comparison, and communicated impact without making an unsupported data-loss claim. When one action slips because the API migration is larger than expected, the risk owner records a temporary mitigation and review date rather than leaving an invisible overdue item.

Exercises:

1. A draft timeline says the cause was “operator error” because a responder restarted workers. What questions would expose system conditions and decision context?
2. The impact dashboard had a 20-minute telemetry gap. How should the postmortem represent the affected interval?
3. “Add an alert” is proposed after a data-loss incident. What additional prevention, mitigation or recovery actions should the team consider?
4. An action has been marked complete but no evidence is attached. What should the reviewer ask before closing it?

Answer guidance: ask what the responder observed, which runbook and alternatives were available, whether restart safety was documented, and how retries/data-path design shaped impact. Record the gap, correlate independent evidence and provide a bounded estimate or state that impact is unknown. Consider durability/idempotency, tested backups, write verification, blast-radius control and alerting; select actions that address the failure mechanism. Require a test, deployed configuration or operational measurement tied to the stated end condition.

Review questions:

- What should an incident postmortem preserve?
- How does a trigger differ from contributing system conditions?
- What makes a corrective action verifiable?
- Why should action closure be reviewed after a postmortem is approved?

Takeaways:

- Set review criteria before an incident and reconstruct the record from evidence with explicit uncertainty.
- Investigate decisions and system conditions without blaming individuals or minimizing impact.
- Choose actions that prevent, detect, mitigate or recover from the failure mode, and define acceptance evidence.
- Track decisions, exceptions and overdue work until the risk is actually reduced or consciously accepted.

## Sources checked 2026-10-04

- [Google SRE Workbook: Postmortem Culture](https://sre.google/workbook/postmortem-culture/) — actionable, measurable follow-up and blameless review principles.
- [Google SRE: Postmortem Culture](https://sre.google/sre-book/postmortem-culture/) — triggers, impact, root/contributing causes, review and sharing.
- [Google SRE: Example Postmortem](https://sre.google/sre-book/example-postmortem/) — incident summary, timeline, root cause, impact and action record structure.
- [Chapter 183 — Incident Command and Communication](183-incident-command-and-communication.md) — live timeline and response record.

DispatchDesk details and measures are fictional. No production incident report or corrective action was created, closed or deployed.
