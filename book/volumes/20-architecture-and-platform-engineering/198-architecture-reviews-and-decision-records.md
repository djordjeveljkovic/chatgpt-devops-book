---
book: The Complete DevOps Engineering Book
volume: 20
volume_title: "Architecture and Platform Engineering"
chapter: 198
title: "Architecture Reviews and Decision Records"
slug: architecture-reviews-and-decision-records
status: complete
summary: ../../_ai/chapter-summaries/198-architecture-reviews-and-decision-records.md
---

# Chapter 198 — Architecture Reviews and Decision Records

**Section outline:** review decisions against system goals and evidence; write concise records of context, choice and consequences; revisit decisions when assumptions or operating evidence change.

## Make the review useful to the team

An architecture review is a decision aid, not a ceremony for obtaining a senior person's signature. It should expose requirements, constraints, risks and alternatives while change is still affordable. Review depth should match impact and reversibility: a new internal library may need a local peer review; a new customer-data boundary or region failover design deserves security, operations, data and product input.

Begin with the decision owner and the question to resolve. Describe users and critical journeys, service objectives, data classification, scale assumptions, dependencies, operating model, cost envelope and constraints. Identify what is known, what is estimated and what remains uncertain. Bring a diagram that shows runtime, trust and data flows at the level relevant to the decision. Use concrete failure scenarios rather than labels such as “highly available.”

Compare plausible options, including doing nothing or delaying. State the reason each option fits or fails, and include operational workload, migration cost, skill availability, vendor/service limits, security, recovery and reversibility. Do not disguise preference as evidence. A proof of concept can answer a narrow technical uncertainty; it does not establish production readiness, total cost or long-term operability.

## Record decisions and consequences

An architecture decision record (ADR) captures one significant choice with its context, decision, alternatives and consequences. The [Microsoft ADR guidance](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record) recommends recording decisions that affect structure or quality attributes and maintaining them over the workload's life. Use a stable identifier and concise status such as proposed, accepted, superseded or rejected. Store the record beside the code or service documentation it governs and link implementation work.

A practical ADR template:

```markdown
# ADR-0042: Use a warm standby for regional recovery

Status: Proposed
Date: 2026-10-04
Decision owner: DispatchDesk service team

## Context
- User journey and impact:
- RTO/RPO and evidence:
- Constraints and assumptions:
- Security/data requirements:

## Options considered
- Option A — benefits, costs, risks:
- Option B — benefits, costs, risks:
- Retain current design — benefits and residual risk:

## Decision
What is selected, for which scope, and what is explicitly out of scope?

## Consequences
- Operational ownership and new failure modes:
- Cost and capacity:
- Migration and rollback:
- Validation and review date:
```

The example is a template only; it is not a recommendation that DispatchDesk must use warm standby. Avoid duplicating a full design document in every ADR. Link detailed diagrams, threat models, runbooks and test results. When one decision changes, write a new record that supersedes the old one rather than silently rewriting history. Mark records rejected if the proposal was not selected; retain why, because the context may recur.

## Turn review outcomes into verifiable work

Capture actions with owner, due date or trigger, and acceptance evidence. “Improve security” is not an action; “demonstrate that the recovery identity can decrypt an isolated backup without production credentials” is testable. Record accepted residual risks with an accountable owner, scope, expiry or review trigger, and compensating controls. Do not treat a meeting note as approval for a policy exception unless the responsible authority has actually accepted it.

DispatchDesk proposes multi-region failover after a regional provider incident. Reviewers ask whether its five-minute RPO is based on business impact or just a default. The team presents observed replication lag, the payment reconciliation path, monthly cost estimate, operational rota and a timed recovery exercise. It chooses to first improve multi-zone recovery and restore evidence, leaving regional recovery proposed pending business-owner confirmation. The ADR records both the choice and the trigger for revisiting it: a validated business requirement for recovery from regional loss. This is a completed decision even though the proposed technology was deferred.

Revisit decisions when a trigger changes: service objectives, regulations, data sensitivity, traffic, vendor support, incident history, team ownership or cost. Track these triggers in the record or service review. A stale ADR can be worse than none if readers mistake an old assumption for current practice. Assign a lightweight review cadence or explicit trigger to decisions with long-lived impact, and make the current owner visible in the service catalog. Architecture evolves through records plus operating evidence, not documentation alone.

A useful review also checks who will carry the pager after the decision. Ask whether the team can observe the new component, rotate credentials, patch it, restore its state and explain its failure modes. Review the proposed security boundary with the people who own identity and data policy, and ask finance or product for cost assumptions when those assumptions determine the choice. Keep the review open to dissent while making the accountable decision owner explicit. A decision log should make it possible for a future maintainer to understand why an option that now appears obvious was rejected under earlier constraints.

Exercises:

1. A review has 40 attendees and ends with “use Kubernetes.” What decision information is still missing?
2. An ADR states a database was selected because it is “scalable.” How can the record become useful?
3. A service has an accepted security exception with no expiry or owner. What corrective action is needed?
4. The architecture changed, but the original record remains marked accepted. How should history be maintained?

Answer guidance: name the owner, scope, requirements, alternatives, risks, operational costs, security/data implications, validation and consequences; reduce attendance to decision contributors. Specify workload evidence, scale dimension, threshold, alternatives and validation that support the claim. Assign accountable authority and owner, define scope, compensating controls, expiry/review trigger and evidence of remediation. Create a superseding ADR, preserve the historical record and link the implementation/current state.

Review questions:

- How should review depth relate to impact and reversibility?
- What context makes an ADR understandable years later?
- How do review actions become verifiable operational work?
- What events should trigger a decision review?

Takeaways:

- Frame the decision around user outcomes, constraints, evidence and accountable ownership.
- Compare real alternatives and include operational, security, cost and recovery consequences.
- Record significant choices and preserve superseded history with clear links.
- Assign review findings owners and measurable evidence; revisit decisions when assumptions change.

## Sources checked 2026-10-04

- [Microsoft Azure Well-Architected: Maintain an architecture decision record](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record) — ADR purpose and lifecycle.
- [Chapter 198 relates to Chapter 005 — Architecture as Tradeoffs](../01-engineering-mental-models/005-architecture-as-tradeoffs.md) — compare qualities and constraints.
- [Chapter 187 — Disaster Recovery and Failback](../19-site-reliability-and-recovery/187-disaster-recovery-and-failback.md) — operational evidence for recovery decisions.

All review scenarios are fictional; no architecture approval or exception was issued.
