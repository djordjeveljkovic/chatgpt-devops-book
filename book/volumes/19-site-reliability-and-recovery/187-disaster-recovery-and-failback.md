---
book: The Complete DevOps Engineering Book
volume: 19
volume_title: "Site Reliability and Recovery"
chapter: 187
title: "Disaster Recovery and Failback"
slug: disaster-recovery-and-failback
status: complete
summary: ../../_ai/chapter-summaries/187-disaster-recovery-and-failback.md
---

# Chapter 187 — Disaster Recovery and Failback

**Section outline:** define recovery time and data-loss objectives; select a recovery strategy and map dependency order; authorize failover and reconcile state before a controlled return to normal.

## Define what recovery means

DispatchDesk serves customers in two regions, but only one has a writable database. A regional outage lasts six hours. The standby application starts in minutes, yet its identity provider integration is unavailable and its database replica is several hours behind. The team can send traffic there, but cannot safely accept orders or determine which writes are missing. “We have two regions” did not define a usable disaster recovery capability.

High availability keeps a service running through component failures during normal operation. Disaster recovery (DR) plans how to restore service after a larger disruption makes a site or essential control plane unusable. The systems can share technology, but the recovery boundary, objectives and procedure differ. A redundant node in one region may improve availability without addressing the regional failure the business cares about.

Agree on a recovery time objective (RTO): maximum acceptable delay from interruption to restoration of a defined service level. Agree on a recovery point objective (RPO): maximum acceptable age of recoverable data at the interruption, or the corresponding permitted data-loss window. These are business-impact decisions implemented by technical systems. State the exact service operation and data set, not just “the platform.” A read-only account page and an order-acceptance API may have different objectives.

RTO and RPO are targets, not measured guarantees. Chapter 186's restore tests reveal actual recovery capability. The plan should include time to detect and declare the disaster, authorize failover, establish dependencies, restore or promote data, validate the application and route traffic. Data replication lag at the decision point informs RPO, but an asynchronous replica can still contain corrupt or malicious writes. A perfect data copy does not meet RTO if identity, DNS, capacity or operator access cannot be restored.

## Choose a strategy and order dependencies

Common approaches include backup and restore, pilot light, warm standby and active-active service. Backup and restore usually costs less and has slower recovery because compute and state must be restored. Pilot light keeps core data and some foundation components ready. Warm standby operates a scaled-down but functional service that can expand. Active-active serves from multiple sites and can reduce interruption, but adds cost and consistency/coordination complexity. These are patterns, not fixed RTO/RPO ranges; measured outcomes depend on architecture, volume, quotas, automation and practice.

Select a strategy from the required RTO/RPO, data consistency, business criticality, operational capacity, cost and dependencies. List recovery components and their order: responder communication and identity; network and DNS; keys and secrets; data stores; queue and event infrastructure; application and integrations; observability; customer traffic. Identify dependencies that rely on the failed region, such as control-plane APIs, image registries, key services, CI/CD or management consoles. Provide an out-of-band path for actions that must work when those services are unavailable.

Define the source of truth for recovery state. Specify which copy is promoted, how the latest safe recovery point is selected, whether writes are stopped or queued, and how duplicate or uncertain transactions are reconciled. For active-active systems, document conflict semantics and how divergent replicas are merged or discarded. For a single-writer system, name the process that fences the old writer and proves the new writer is authoritative. Never allow both sides to accept conflicting writes unless the application is designed to reconcile them.

Make failover authority explicit. Identify who can declare a disaster, who approves data-risk acceptance, who executes each step, and which signals trigger escalation. Automate repeatable operations but retain human confirmation for high-impact actions where false positives could cause split brain or irreversible data loss. A manual approval should not mean a person improvises commands; the playbook should make initiation, preconditions, expected result and rollback clear. When required objectives cannot be met, the business owner accepts the documented residual risk or adjusts scope/objectives through the established process.

## Fail over, then fail back deliberately

The recovery playbook should contain phases with preconditions, owners, evidence and stop conditions:

1. Declare the failure boundary and stop or fence writers at the unavailable site where possible.
2. Select and record the recovery copy, timestamp or log position, integrity status and estimated data gap.
3. Establish identity, secrets, networking, dependencies and adequate capacity in the recovery site.
4. Restore or promote data, validate the application and run a small safe transaction or business workflow.
5. Route a controlled amount of traffic, watch service SLIs and data correctness, then expand when agreed gates pass.
6. Communicate the recovery point and any data reconciliation needs; preserve the incident timeline and decision record.

Traffic redirection is only one step. Validate that clients actually reach the recovery service and that certificates, DNS caches, allowlists, webhooks and third-party callbacks work. Monitor queue backlogs and delayed jobs. Keep the old site isolated from writes until it is safe to rejoin. If the failed service returns unexpectedly, it must not become a second writer simply because its local health check is green.

Failback is a planned data and authority transition, not just changing the DNS record back. First understand the primary site's integrity and why it failed. Rebuild or resynchronize its state from the current authoritative recovery site. Confirm replication completeness and direction, version/configuration compatibility, keys, capacity and monitoring. If the recovery site has accepted writes, it is now the authoritative source; do not overwrite those writes with stale primary state. Choose a controlled cutover window, freeze or coordinate writes if required, validate the target, move authority once, and monitor before declaring the original topology restored. It may be safer to operate the recovery site as the new primary until a future planned migration.

Exercise the whole process at the level of risk the service can tolerate. A tabletop tests decisions and communication, a restore test checks data recovery, and a failover drill validates traffic and dependency behavior. Measure achieved RTO and RPO from defined start/end and recovery-point markers. Include unsuccessful steps and residual manual work. Update plans after architectural, provider, identity or data changes; DR documentation can drift even while replicated data stays current.

For DispatchDesk, the team chooses a warm standby for order acceptance and documents a 30-minute RTO and five-minute RPO as business-approved targets. A drill finds that the identity provider's regional endpoint and the application signing key were only available in the primary region. The first attempt cannot authenticate the recovery workload within the target time. The team establishes an independent identity path and protected key-recovery procedure, then repeats the drill with a known replica position and safe order transaction. During a simulated failover, they record replication lag and hold writes briefly while fencing the primary. The recovery site becomes authoritative; the plan explicitly prohibits automatic failback until the primary is rebuilt from that site and a single-writer cutover is approved. The objectives remain targets until the measured run demonstrates them under representative load.

Exercises:

1. A service's compute starts in the recovery region in ten minutes, but operators take two hours to restore identity and secret access. Which RTO should be reported, and what capability needs work?
2. The asynchronous replica is 12 minutes behind when the primary fails, but the approved RPO is five minutes. What decision and communication are required before accepting writes there?
3. The original primary returns while the recovery region is accepting writes. What prevents split brain and data loss during failback?
4. A team meets RTO in a tabletop but has never restored data or redirected traffic. What has the exercise demonstrated, and what remains unproven?

Answer guidance: measure from service interruption until the defined user operation is restored, including identity prerequisites; the compute startup time is only one phase. The team has a target breach and must record/authorize data exposure against it or choose a safer recovery copy, then tell stakeholders the expected gap. Fence the former writer, rebuild/resynchronize the old site from the current authoritative state, validate log position and integrity, and use one approved authority cutover. A tabletop demonstrates decision familiarity only; restore, application, identity, network/traffic, dependency and measured objective evidence remain to be tested.

Review questions:

- How do RTO and RPO differ, and how does each depend on a defined service boundary?
- Which dependencies commonly make a standby site unusable even when its application is running?
- Why is failback a data-authority change as well as a traffic change?
- What distinct evidence do tabletop, restore and failover exercises provide?

Takeaways:

- Define RTO/RPO from business impact and verify them with measured recovery tests.
- Select a recovery pattern based on objectives, cost, consistency and operational complexity.
- Recover dependencies in an explicit order with named authority, data source and stop conditions.
- Fence old writers and resynchronize from the current authority before an approved failback.

## Sources checked 2026-10-04

- [AWS Well-Architected: Define recovery objectives](https://docs.aws.amazon.com/wellarchitected/2024-06-27/framework/rel_planning_for_recovery_objective_defined_recovery.html) — RTO/RPO definitions and business-aligned selection.
- [AWS Well-Architected: Defined recovery strategies](https://docs.aws.amazon.com/wellarchitected/2022-03-31/framework/rel_planning_for_recovery_disaster_recovery.html) — backup/restore, pilot light, warm standby, active-active and failback planning.
- [AWS Well-Architected: Test disaster recovery](https://docs.aws.amazon.com/wellarchitected/2023-04-10/framework/rel_planning_for_recovery_dr_tested.html) — failover exercises as evidence for objective attainment.
- [Chapter 186 — Backup Engineering](186-backup-engineering.md) — recovery copies, restore validation and measured duration.

The RTO/RPO values and architecture are fictional examples, not cloud-service guarantees. No failover, traffic change, replication, data promotion, region operation or failback was executed.
