---
book: The Complete DevOps Engineering Book
volume: 22
volume_title: "Operational Reference"
chapter: 220
title: "Production Readiness and Recovery Checklists"
slug: production-readiness-and-recovery-checklists
status: complete
summary: ../../_ai/chapter-summaries/220-production-readiness-and-recovery-checklists.md
---

# Chapter 220 — Production Readiness and Recovery Checklists

The final review asks whether a named service can meet its stated contract and recover under its actual operating constraints. It is not a test of how many tools a team has installed. Harbor may be ready on a carefully operated VPS; Atlas may be unready despite a large Kubernetes platform if nobody can restore its data or identify who owns a failing dependency.

Use the evidence tables below as a review record. For each applicable row record the owner, evidence location/date, result and unresolved action. “Not applicable” needs a reason. “Unknown” remains unknown until someone obtains evidence. Adapt the scope to the change: a static content update and a database ownership migration require different depth. Google's historical launch discussion explains how continuously curated, concrete questions support releases; this book's tables are original and tailored to DispatchDesk. See [Reliable Product Launches at Scale](https://sre.google/sre-book/reliable-product-launches/) and [AWS operational readiness](https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/operational-readiness.html).

## Service contract and ownership

| Review question | Evidence that answers it | Common incomplete answer |
|---|---|---|
| Who owns the service and its dependencies? | Named team, escalation contact, responsibility boundaries and handoff test | A repository has several maintainers. |
| Which customer action defines success? | Acceptance/notification contract, durable states and observable failure outcomes | The process responds to a health request. |
| What load and population are promised? | Measured or explicitly assumed rates, payloads, bursts, tenancy and regions | “It should scale.” |
| Which objective is being assessed? | SLI population, target, window and missing-data policy | A dashboard has a green average. |
| What operating hours and response commitments exist? | Actual coverage, escalation and dependency support terms | An engineer can usually answer a message. |
| What happens outside the supported envelope? | Admission/backpressure policy, terminal failures and customer communication | An unbounded queue absorbs it forever. |

For DispatchDesk, an accepted order and its notification intent must be durable before returning acceptance. Provider acceptance and recipient delivery are separate outcomes. A readiness endpoint must reflect the service's accept-work policy; liveness should not simply restart healthy processes whenever a dependency is unavailable. Inspect these claims in the actual implementation, not only its design document. [Chapters002–004](../01-engineering-mental-models/002-requirements-before-tools.md) establish requirements and objectives; [Chapter181](../19-site-reliability-and-recovery/181-slis-slos-and-error-budgets.md) develops the operational policy.

## Release and deployment evidence

| Review question | Required evidence | Release decision it informs |
|---|---|---|
| Which artifact will run? | Digest, platform, source revision, build provenance and promotion record | Whether the reviewed artifact is the deployed one. |
| Which execution identity and target apply? | Account/profile/region, cluster/context/namespace or host/user; effective rights | Whether this run can affect the intended scope only. |
| Is the plan/configuration assessed? | Effective IaC plan, service definition and policy checks with exact identities | Whether unexpected replacement or privilege expansion is understood. |
| Can versions coexist? | API/schema/message compatibility tests for mixed old/new deployment | Whether rolling/canary exposure preserves correctness. |
| What bounds the rollout? | Replica/surge and connection budget, progress deadline and stop condition | Whether additional replicas or incomplete readiness can overload a dependency. |
| How is customer acceptance checked? | Post-deployment checks of durable orders and notification outcomes | Whether controller success corresponds to service success. |
| Can the release be reversed or repaired? | Compatible earlier artifact/configuration plus data migration procedure | Whether rollback is possible after this specific transition. |
| Are concurrent writers coordinated? | Release serialization plus state/controller ownership | Whether two valid releases can interfere. |

Walk through a concrete release before the review. Identify the artifact leaving CI, the environment gate, credentials obtained, controller updated and observations used to continue exposure. For a schema transition, state which old/new readers and writers remain compatible and when the previous application becomes unusable. The delivery volume's [migration chapter](../14-delivery-deployment-and-gitops/136-database-and-message-compatibility.md) owns that mechanism; [Chapter216](216-infrastructure-and-pipeline-reference.md) provides the command lookup.

Avoid a generic “rollback tested” claim. Restoring an old API image might work before a contract column is removed and fail afterward. If the chosen recovery is forward repair, rehearse that repair and establish the time/data consequences. Preserve failed-release evidence before replacement or log rotation removes it.

## Capacity, cost and dependency boundaries

| Area | Evidence to inspect | Question for the reviewer |
|---|---|---|
| CPU/memory | Representative latency distribution, throttling, pressure, leak trend and startup behavior | Does the utilization measure match the actual bottleneck? |
| Connections | Global steady/surge/failure pool budget with administrative reserve | Can autoscaling exceed the database's safe concurrency? |
| Queues | Arrival/completion rates, oldest age, retries, dead-letter behavior and maximum retention | Can delayed work still meet its customer contract? |
| External provider | Quota, rate limiting, timeout, retry and duplicate semantics | Will increased workers amplify failures instead of increasing completion? |
| Failure domain | Surviving capacity and traffic/data behavior after the stated loss | Is spare capacity usable where the workload actually moves? |
| Cost | Normal/peak cost model, bounded autoscaling, retention and billing owners | Is the planned headroom affordable and observable? |
| Abuse/overload | Per-tenant admission and bounded request work | Can a small abusive population exhaust the shared service? |

Use the measured service envelope, not an arbitrary benchmark title. A load test is useful only when its data/work mix and observation windows address the proposed decision. The original arithmetic in [Chapter217](217-scaling-and-architecture-decision-tables.md) provides a review model: capacity, one-instance loss, connection pools and a separate provider ceiling must agree. Performance testing and its limitations belong in [Volume16](../16-performance-and-capacity-engineering/README.md).

## Security and telemetry readiness

| Review question | Evidence |
|---|---|
| Can secrets rotate without losing service? | Inventory, scoped access, tested staged rotation and invalidation of the old credential. |
| Can an untrusted pipeline obtain production identity? | Event/subject/audience restrictions, runner isolation, protected environments and negative checks. |
| Are artifacts assessed for known issues and origin? | Vulnerability disposition, SBOM/provenance where applicable, signature verification and exception ownership. |
| Are exposed paths intentional? | Host/provider/cluster network policy and tests from representative client positions. |
| Are host and runtime controls effective? | Patch/maintenance ownership, configured users, capabilities, MAC policy and enforcement observations. |
| Can an operator investigate without exposing customer data? | Bounded logs/traces, access/retention policy, audited investigation path and sensitive-field handling. |
| Will an alert reach someone able to act? | Alert delivery exercise, useful runbook, escalation and known data-source failure behavior. |
| Can the monitoring system fail independently? | Collection/freshness alerts and independent business/client evidence. |

Do not reduce security to a scanner count. An accepted vulnerability exception has a reason, compensating controls, owner and review deadline. Likewise, masked CI output does not establish that no secret reached an artifact. [Volume18](../18-security-and-software-supply-chains/README.md) teaches these boundaries; [Chapter218](218-observability-and-incident-runbooks.md) joins evidence collection to incident response.

## Backup and recovery evidence

| Recovery question | Evidence that must survive loss of the primary environment |
|---|---|
| What is being restored? | Business data, configuration, identity material, artifacts and dependencies inventory. |
| Where is the trusted recovery point? | Backup lineage, integrity checks, consistency method, retention and compromise considerations. |
| Can it be read when the primary account/host is lost? | Recovery identity, keys, access path and independent copies appropriate to the threat. |
| How much accepted data can be lost? | Measured recovery-point gap compared with the stated RPO. |
| How long does customer restoration take? | End-to-end timed exercise including provisioning, restore, startup, validation and traffic switch. |
| Can there be two active writers? | Fencing/ownership procedure, split-brain handling and reconciliation rules. |
| How are queued and external side effects reconciled? | Order/intent state, deduplication keys, provider status and controlled replay procedure. |
| What happens after failover? | Monitoring, capacity, new backup establishment and deliberate failback plan. |

PostgreSQL distinguishes logical dump, filesystem-level backup and continuous archiving, each with different assumptions and restore procedures; see its [Backup and Restore documentation](https://www.postgresql.org/docs/current/backup.html). The correct evidence is successful restoration of the application's required state, not simply a scheduled backup command exiting zero. Restoration compatibility, ownership, extensions and keys can all affect the result.

For DispatchDesk, validate a restored order's state and pending notification intent, then exercise controlled processing without accidentally contacting real recipients from an isolated rehearsal. Check for orders accepted after the restored point and document their loss or reconciliation path. Restoring a database does not automatically restore external provider state or make notification replay duplicate-safe. [Chapter186](../19-site-reliability-and-recovery/186-backup-engineering.md) covers backups and [Chapter187](../19-site-reliability-and-recovery/187-disaster-recovery-and-failback.md) covers the wider recovery sequence.

## Conduct the final service review

Before release, have another engineer follow the critical operating path using the recorded access and instructions. Can they establish identity, find the live artifact, reproduce the customer check, recognize a bounded failure and locate recovery material? The goal is usable operating knowledge, not memorizing every command. A novice can use the reference tables; an experienced reviewer should challenge assumptions that the tables expose.

Record the decision in this original template:

```text
Service / environment / proposed release:
Customer contract and objective assessed:
Artifact/configuration/data identities:
Reviewers and operating owner:
Evidence links, execution dates and exact scopes:
Applicable checks passed / failed / unknown:
Unresolved items with impact, owner and deadline:
Decision: proceed / constrained exposure / hold
Exposure and stop conditions:
Recovery action and compatibility boundary:
Next review trigger and responsible owner:
```

A constrained exposure is concrete: specify population, duration, acceptable error/age boundaries and who watches. “Monitor closely” without a condition or owner does not define a control. A hold should name the missing evidence and the action that could resolve it. Update the record when material configuration, data contracts, load or operating ownership change.

As a final drill, Summit has successful CI, a healthy ECS deployment and an untested restore. Its database migration removes a field required by the previous API release. Explain the release decision. A sound answer identifies that old-image rollback is no longer established, restore time/data loss remain unknown and deployment health does not settle either issue. It proposes a compatible migration sequence or proven forward repair, plus an appropriate recovery exercise, rather than merely demanding another green test badge.

The checklist is a reusable engineering review, not certification that the reader's service is ready. Primary launch, operational-readiness and backup sources were inspected on2026-10-01. No production review, paid cloud provisioning or recovery exercise was performed for this reference; completed experiments and unavailable integrations are recorded in the chapters that teach them.
