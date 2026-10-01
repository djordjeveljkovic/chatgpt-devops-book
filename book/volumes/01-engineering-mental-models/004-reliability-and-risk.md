---
book: The Complete DevOps Engineering Book
volume: 1
volume_title: "Engineering Mental Models"
chapter: 4
title: "Reliability and Risk"
slug: reliability-and-risk
status: complete
summary: ../../_ai/chapter-summaries/004-reliability-and-risk.md
---

# Chapter 4 — Reliability and Risk

## Availability, durability and correctness

A DispatchDesk outage can take several forms. Customers may be unable to submit orders. Accepted orders may disappear. Orders may survive but contain the wrong item quantities. Notifications may reveal another customer's information. These are all failures, but a single uptime percentage cannot describe their different consequences.

This chapter follows [How Computers Execute Services](003-how-computers-execute-services.md). Its purpose is to help you choose which risks to reduce first and which limitations to state openly. The calculations are small paper and local-Python exercises; they do not provision infrastructure. Detailed recovery objectives and service-level policies have canonical treatment in [Volume 19](../19-site-reliability-and-recovery/181-slis-slos-and-error-budgets.md).

**Availability** concerns whether useful service is obtainable under the defined conditions. For DispatchDesk, order acceptance and notification delivery are separate journeys. A notification-provider outage can leave order acceptance available. If a synchronous provider call is placed inside the API's acceptance path, the same outage can block both. Availability therefore depends on the chosen dependency graph, not just the provider's advertised reliability.

**Durability** concerns retaining data across specified failures and time. A durable order store is expected to keep accepted orders through the failures its contract covers. “Survives an application restart” is weaker than “survives the loss of the host and its disks.” A replica and a backup serve different purposes: a replica can make another copy available quickly, while a retained backup can recover earlier state. A mistaken delete can propagate to a replica; recovering the previous state requires a suitable recovery history.

**Correctness** concerns whether behavior matches its contract. An API that returns quickly with another customer's order is available in a superficial sense but incorrect and harmful. A worker that sends every notification twice can meet a completion-time target while violating the intended delivery behavior. Treat incorrect behavior as a first-class failure, even when process and infrastructure metrics look healthy.

These properties can conflict during an incident. If a release exposes cross-customer data, stopping affected access sacrifices availability to limit harm. If the database is uncertain after storage failure, reopening writes prematurely may make recovery harder. The service charter should identify who can make that decision and what evidence they need. Responders should not have to invent the business's priorities under pressure.

Google's 2016 [Embracing Risk chapter](https://sre.google/sre-book/embracing-risk/) presents reliability as a business tradeoff rather than a quest for perfect uptime. Its useful lesson here is to align engineering effort with the consequences the business is willing to bear. The numeric targets in this book's fictional cases are teaching assumptions, not Google's targets or universal recommendations.

## Failure domains and correlated failure

A **failure domain** is a boundary within which one cause can affect several components. A process is a boundary for some software crashes. A host is a boundary for kernel failure or host power loss. A location can be a boundary for power or connectivity interruption. An administrative account can be a boundary for accidental deletion or compromised credentials.

Two API processes on one VPS can protect against some process failures, but both disappear when the host fails. Two hosts in one location can survive a host failure while sharing power or upstream networking. Two hosts in separate locations can still receive the same faulty release. Name the cause before judging the redundancy.

**Correlated failure** occurs when a common cause affects multiple components. Redundancy reduces risk only to the extent that the copies avoid the relevant common causes. Independent hardware does not make configuration independent. Independent locations do not make a shared identity provider independent. A global change can cross physical isolation boundaries in seconds.

AWS [Availability Zone documentation](https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/availability-zones.html) describes infrastructure separation intended to reduce shared physical failures. It does not imply that deploying across zones protects an application from every cause. Summit, our fictional managed AWS company, must still consider release sequencing, shared quotas, data dependencies and operator actions. Atlas's Kubernetes replicas likewise need an actual placement policy before replica count says anything about host failure.

For Harbor's single VPS, a useful first risk map is:

| Cause | Immediate effect | Existing mitigation | Remaining question |
|---|---|---|---|
| API process crash | Order requests stop | Supervision restarts process | Can in-flight work be reconciled? |
| VPS disk loss | API and local data unavailable | Off-host backup planned | Has restoration been measured? |
| Incorrect schema change | Old and new releases may fail | Release review | Is data recovery possible? |
| Provider outage | Notifications delayed | Durable pending work | How old can pending work become? |
| Account compromise | Hosts/backups may be altered | Restricted access | Is recovery access independent? |

“Planned” is not an existing verified capability. The table intentionally exposes that gap. A real readiness review would assign an owner and deadline before relying on the backup. Writing down residual risk is more useful than declaring the system resilient because it has several components.

## Choosing an acceptable risk budget

Suppose Harbor explicitly adopts a learning objective of 99.5% time-based availability for order acceptance over a 30-day window, counting planned maintenance. This is a new scenario objective; Chapter 2's earlier seven-day request-latency example remains a separate illustrative metric. The monthly time window has 43,200 minutes, so the permitted unavailable time under this model is 216 minutes.

You can check the arithmetic locally, as an ordinary user with Python 3, in any working directory:

```bash
python3 - <<'PY'
window_minutes = 30 * 24 * 60
availability_target = 0.995
allowed_minutes = window_minutes * (1 - availability_target)
print(f'{allowed_minutes:.1f} minutes')
PY
```

`30 * 24 * 60` converts the specified window to minutes. The target is a fraction; subtracting it from one yields the permitted unavailable fraction. Formatting rounds the display to one decimal place. The expected arithmetic result is 216.0 minutes. The script changes no files and requires no cleanup. It is an arithmetic illustration, not a measured service-level report.

That figure is not permission to cause a three-hour outage. A long interruption during a busy sales period can have different impact from several short interruptions during low demand. A request-based objective would count unsuccessful valid requests instead of minutes, and cannot be converted to downtime without assumptions about traffic. Keep the measurement model visible.

A budget becomes useful when it informs choices. A planned maintenance operation lasting twenty minutes consumes time in this fictional model. If the service is already near its limit, the team may postpone a discretionary change, reduce its scope or provide an alternative service path. If the service has abundant measured headroom, the team can still reject a change that risks order loss: an availability budget is not a data-loss allowance.

Assess risk using both consequence and likelihood, while acknowledging uncertainty. A frequent harmless retry and an uncommon loss of the only order copy should not receive equal attention simply because the former appears on more dashboards. Estimates often begin qualitatively. Record why a failure is plausible, what boundary limits its impact, how it is detected and how long recovery takes. Update estimates after rehearsals and incidents rather than treating an early score as scientific precision.

Mitigations also create risk. Adding a database replica introduces replication lag, promotion choices and split-brain concerns. Adding a second provider creates routing and reconciliation complexity. Adding Kubernetes creates a shared operational system with its own access and recovery requirements. Prefer the smallest change that reduces the important risk under the team's constraints, and measure whether it actually does so.

## A backup whose recovery path shared the failure

Harbor stores nightly backups outside its VPS, but the only backup download credential and restore instructions are on the VPS. A disk failure destroys the server. The backup objects still exist, yet responders cannot obtain the credential or the documented procedure. The team had separated data storage physically while retaining a common recovery-access dependency.

The responder's first task is to establish which resources remain trustworthy and accessible. They contact the accountable account owner through the team's existing recovery process, obtain authorized backup access, and provision a replacement only after identifying a compatible restore procedure. They retain evidence about the backup time and the last known accepted orders. They do not promise zero data loss because the nightly copy may exclude later records.

After restoration in an isolated environment, the team verifies known orders, checks the restored boundary, confirms configuration and access, and decides how to handle orders accepted after the backup. Only then does it reopen the normal path. If external systems hold additional records, reconciliation can improve recovery, but that capability must be demonstrated rather than assumed.

PostgreSQL's [backup overview](https://www.postgresql.org/docs/18/backup.html) distinguishes several backup approaches and emphasizes their assumptions. Which technique Harbor chooses is a later decision. Here the failure would affect any backup method if its only recovery credential and knowledge disappeared with the primary host.

The lasting repair stores approved recovery instructions where responders can reach them during host loss, provides controlled recovery access independent of the failed machine, and rehearses from an environment without the original host. The rehearsal records retrieval time, restore time, verification time and actual recoverable data. A backup upload success message covers only a small part of that chain.

## Exercises and answer guidance

1. Harbor adds two API workers on its existing VPS. Which risks improve and which remain? Process-level interruption or workload sharing may improve; host power, kernel and disk failure still affect both. State what supervision and data dependencies are assumed.
2. Calculate allowed time for a 99.9% target in the same 30-day model. The result is 43.2 minutes. Explain why this does not establish the engineering work needed to meet that target, or predict how outages distribute.
3. List three shared causes affecting replicas in different locations. A common bad release, shared administrative credentials and a shared upstream dependency are plausible. For each, propose a mitigation that addresses the cause rather than merely increasing replica count.
4. A restore recovers every order through midnight, while failure occurs at noon. What may be lost? Orders after the recoverable boundary may be absent. Whether they can be reconciled depends on additional retained evidence. Never infer a twelve-hour bound from backup schedule alone without checking successful backup and restore history.

## Review questions and takeaways

How do availability, durability and correctness differ? Which failure domain does each proposed replica avoid? What counts as planned maintenance in the objective? Which recovery resources disappear with the primary host? What uncertainty should remain visible when choosing a mitigation?

Reliability is a set of customer-relevant properties, with explicit failure boundaries and recovery evidence. Redundancy must address common causes. An availability budget helps guide change but cannot replace correctness and data-protection requirements. Continue with [Architecture as Tradeoffs](005-architecture-as-tradeoffs.md).

## Sources and verification

Inspected on 2026-10-01: Google's 2016 SRE risk chapter, AWS Availability Zone fault-isolation documentation, and PostgreSQL 18's backup overview. No current provider guarantee or price is asserted. All company cases and numeric objectives are fictional. The arithmetic example is a local calculation; no live availability, backup, restore or cloud experiment was performed. Independent review remains pending.
