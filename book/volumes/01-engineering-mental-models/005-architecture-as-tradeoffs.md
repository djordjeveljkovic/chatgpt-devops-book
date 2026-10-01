---
book: The Complete DevOps Engineering Book
volume: 1
volume_title: "Engineering Mental Models"
chapter: 5
title: "Architecture as Tradeoffs"
slug: architecture-as-tradeoffs
status: complete
summary: ../../_ai/chapter-summaries/005-architecture-as-tradeoffs.md
---

# Chapter 5 — Architecture as Tradeoffs

## Quality attributes and competing objectives

An architecture is a set of consequential choices about where behavior lives, how components communicate, what they trust and how they recover. A diagram of boxes is useful only when it reveals those choices. For DispatchDesk, “API, database, worker” leaves open whether the components share one host, whether accepted work is durable, and whether the team can replace the host without losing its recovery access.

Read [Reliability and Risk](004-reliability-and-risk.md) first. This chapter compares plausible designs under explicit constraints, then records a decision that another engineer can challenge. You need no cloud account or container runtime. The examples are decision artifacts and failure analysis, with executable deployment deferred to the relevant volumes.

A **quality attribute** is a property of the system relevant to how it works: reliability, security, response time, recoverability, maintainability or cost efficiency. Attributes become useful when tied to scenarios. “Maintainable” could mean that a team can release a small change in an hour without one indispensable expert. “Recoverable” could mean that a replacement host can serve verified restored data within the team's agreed limit. The scenario prevents a broad adjective from becoming an untestable claim.

Attributes compete. More replicas may reduce a host's impact while increasing coordination work and infrastructure cost. Synchronous cross-location writes may reduce some data-loss exposure while increasing latency and dependency on connectivity. A strongly standardized platform may simplify support while limiting choices for unusual workloads. There is no design that maximizes every quality under a finite budget.

The initial DispatchDesk workload remains the fictional assumption from Chapter 2: one order per second normally and ten at peak, with bounded payloads. It does not inherently require microservices or a cluster. The relevant questions include whether one host can meet the measured response target, whether its failure can be recovered acceptably, whether the team can operate the dependencies, and whether upcoming product work creates new boundaries.

For an architecture discussion, order the attributes. Suppose Harbor ranks retained accepted orders first, a restore path second, simple releases third and rapid expansion fourth. An inexpensive design with no restore path loses despite its low invoice. Suppose Summit ranks burst handling and reduced database maintenance more highly because its product team lacks that expertise. A managed database may be appropriate even when its direct cost is higher. Suppose Atlas needs several teams to deploy independently with consistent governance; a shared workload platform may then have a clear purpose.

AWS's [Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html), whose inspected page lists a November 2024 publication date, provides a structured AWS-specific review framework. It is useful as a source of questions, not proof that an AWS design satisfies your service contract. The following fictional comparisons use their own assumptions and do not claim provider pricing or guarantees.

## Reversibility and decision records

A reversible decision can be changed at tolerable cost without violating important contracts. Some choices are easy to revise: changing a dashboard title or an internal command wrapper. Some are harder: changing identifiers stored in every order, adopting a data model that cannot represent required history, or integrating provider-specific delivery state throughout application code.

Reversibility is a spectrum, not a binary label. Moving an API from a VPS to a managed container service may be straightforward if the application is independently packaged, configuration is explicit and data remains accessible. It becomes harder if it expects a particular host path, writes durable records into its installation directory, or depends on manually configured host credentials. A small early investment in clear boundaries can preserve future options without building the future platform now.

Avoid confusing future flexibility with speculative complexity. Introducing a generic provider abstraction for ten nonexistent providers creates code that no real contract has tested. Instead, define the existing provider's observable acceptance and failure behavior, isolate its integration where appropriate, and retain enough state to reconcile uncertain work. That boundary is useful today and may help migration later.

A **decision record** captures the context, alternatives, chosen approach, consequences and review triggers. It should tell a future engineer why a seemingly obvious alternative was not selected. “Use a VPS because it is simple” is incomplete. State which responsibilities stay on the team, what risk is accepted and what evidence could overturn the choice.

```markdown
# ADR 001: initial DispatchDesk hosting

Status: accepted for the learning deployment
Decision owner: Harbor service team

## Context
Two developers share operations.
Assumed workload is one order per second, ten at peak.
Accepted orders must be persisted before acknowledgement.
The first deployment may be interrupted by loss of its only host.

## Alternatives considered
1. One Linux VPS with supervised API and durable local database.
2. Managed container execution with managed database.
3. Kubernetes workloads with an external database.

## Decision
Begin with one VPS and an independently packaged application.
Keep configuration explicit and keep durable data separate from release files.
Document and rehearse off-host backup recovery before real production use.

## Consequences
The team owns host updates, database maintenance and restore execution.
Host loss interrupts service; process restart alone is insufficient recovery.
The design avoids operating a cluster for the initial workload.

## Review triggers
Measured peak load exceeds the tested capacity.
A restore rehearsal misses the agreed recovery objective.
Several teams require independent deployment and shared governance.
```

This is a complete decision note, not configuration for an orchestration tool. “Accepted for the learning deployment” keeps its scope visible. Before production, the unresolved recovery objective must be defined and tested. Do not silently upgrade the note into proof of readiness.

## Comparing three viable architectures

Harbor's VPS route uses ordinary Linux processes supervised by systemd, a reverse proxy and persistent storage. The operating system can be Ubuntu or Fedora/RHEL under its actual support and package policies; this architecture does not require one particular distribution. The team owns updates, access, disk capacity, database operation and backups. Its main benefit is a small set of visible components and predictable responsibilities. Its main limitation is the host failure domain and the manual recovery work required to replace it.

Summit's managed AWS route uses a managed container execution service, a managed database and a managed queue when their contracts match the application. This can reduce host and database maintenance. It still requires IAM permissions, network access, deployable artifacts, secret management, observability, backup policy and cost control. Managed queues introduce their own acknowledgement and redelivery contracts; they do not eliminate duplicate-effect reasoning. The route fits when the team prefers those integrations to direct host maintenance and has the account expertise to govern them.

Atlas's Kubernetes route offers a shared API for workloads and a platform for several teams. The [Kubernetes overview](https://kubernetes.io/docs/concepts/overview/) describes its role in managing containerized workloads. Its usefulness here comes from actual organizational need: multiple runtimes, independent releases, isolation requirements and a platform team able to maintain the system. Kubernetes does not supply DispatchDesk's business correctness or make its database recovery automatic. An external managed database can remain the sensible choice.

| Question | Harbor VPS | Summit managed AWS | Atlas Kubernetes |
|---|---|---|---|
| Who maintains application host lifecycle? | Service team | Provider under chosen service contract | Platform/provider split |
| Who defines order correctness? | Application team | Application team | Application team |
| What makes deployment worth adopting? | Few components and direct control | Managed operations and burst integration | Shared workload interface for teams |
| What remains difficult? | Host loss, updates, restore | Permissions, service dependencies, bills | Platform upgrades, policies, shared failures |
| What validates the route? | Capacity and recovery rehearsals | Integration and permission tests | Workload, isolation and platform recovery tests |

The table avoids arbitrary numeric scores. A score of “nine out of ten reliability” hides the failure model. Discuss actual scenarios instead: what happens if the host vanishes, a release is wrong, a credential expires or a provider rejects work? The same customer contract makes those discussions comparable.

These routes are concurrent alternatives. Harbor need not pass through Summit before Atlas, and may never need either. Traffic growth alone may justify query optimization, host resizing or separating the database before introducing a cluster. Organizational scale can create a platform need even when individual service traffic is modest.

## A migration that moved the process but missed the state

Harbor decides to move the API to a container service. The image starts successfully and its health endpoint responds. The application still writes order data under a path inside its release filesystem. The first replacement task receives an empty path and reports no existing orders. The migration treated the running process as the service while ignoring where authoritative state lived.

Diagnosis begins by comparing the old and new write paths, persistence mounts or service connections, and known order identifiers. An image startup test provides no evidence of data continuity. The responder stops accepting new work through the incomplete destination, preserves any newly accepted records, and restores traffic to the compatible old path if it remains trustworthy. They record the two data boundaries so reconciliation can address orders accepted during the migration.

Recovery should not casually copy a live database directory between machines. The database's documented backup or replication procedure determines a consistent transfer. The team establishes a controlled cutover plan: create a recoverable copy, validate it in the destination, define the write boundary, transfer or reconcile changes, then move traffic with explicit rollback conditions. A rollback that points to stale state is not necessarily safe simply because the old process can start.

The corrective design separates release artifacts from authoritative data. The decision record gains a migration criterion covering known order retrieval across task replacement. This finding might change how Harbor packages the application today while leaving its VPS hosting choice intact. Architectural learning often improves a boundary without requiring a new platform.

## Exercises and answer guidance

1. Harbor has growing request latency but no evidence of the bottleneck. Compare host resizing, query optimization and adding replicas. A strong answer first measures the constrained stage. Query inefficiency may affect all replicas; resizing may buy headroom; replicas require state and routing boundaries. Explain what evidence justifies each.
2. Name a reversible and a costly-to-reverse DispatchDesk decision. A log display format may be relatively reversible; an externally promised order identifier format can be costly because clients retain it. Explain affected consumers and migration evidence.
3. Rewrite the ADR after three product teams begin deploying weekly. Do not immediately select Kubernetes. Record deployment friction, governance needs, available platform staffing and alternatives. A justified platform decision needs those constraints.

## Review questions and takeaways

Which quality attributes determine this design? What responsibility is reduced by a managed service, and what remains? Which evidence could overturn the decision? Where does authoritative data live? Can a rollback preserve orders accepted after cutover?

Choose architecture against scenarios and constraints. Preserve useful boundaries without implementing speculative systems. Record accepted risks and review triggers. Compare alternatives using the same service contract, and keep process placement separate from state migration. Continue with [Environments and Reproducibility](006-environments-and-reproducibility.md).

## Sources and verification

The AWS Well-Architected introduction and Kubernetes overview were inspected on 2026-10-01. This chapter uses only their general roles; exact deployment flags, versions and service contracts belong to later chapters. The ADR, companies and migration incident are fictional. No host, cloud service, cluster or database migration was executed. Independent review is required.
