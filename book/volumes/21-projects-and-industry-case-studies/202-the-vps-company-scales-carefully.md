---
book: The Complete DevOps Engineering Book
volume: 21
volume_title: "Projects and Industry Case Studies"
chapter: 202
title: "The VPS Company Scales Carefully"
slug: the-vps-company-scales-carefully
status: complete
summary: ../../_ai/chapter-summaries/202-the-vps-company-scales-carefully.md
---

# Chapter 202 — The VPS Company Scales Carefully

**Section outline:** vertical growth and resource evidence; second host and managed database choices; why the team delays Kubernetes.

## Let measurements choose the next change

DispatchDesk grows to several hundred business users. A single VPS still handles normal traffic, but month-end imports make CPU and database latency rise. The team reviews four weeks of request volume, queue time, memory pressure, disk I/O, database connections, backup duration and user-visible errors. Averages hide a sharp hour-long peak, so they inspect percentiles and the actual import window. They confirm the dominant constraint is database I/O and lock contention, not application CPU.

Before buying larger machines, profile the slow queries, add an index tested against write cost, cap import concurrency and move noncritical email delivery to a durable queue. Set capacity thresholds with lead time for a change. A vertical resize is simple and can be a good step, but it does not eliminate a single failure domain and can hit provider limits. Compare the additional monthly price with the engineer time and outage risk the change avoids; Chapter 199 explains the cost model.

Protect the measurement system from the scaling event. Keep resource telemetry and application-level outcomes, verify alerts reach the responsible person, and check that monitoring does not depend entirely on the host being monitored. Maintain tested backups and a recovery runbook before increasing state volume. A larger database makes eventual restore and migration slower.

## Add a second host where it reduces a real risk

The team separates the application from PostgreSQL and moves the database to a managed service after comparing patching, backup retention, recovery behavior, network access, cost and provider limitations. This shifts some maintenance but does not transfer application data ownership or remove the need to test restore. Private networking and database identity are configured deliberately. The application remains on one VPS initially, so host failure still interrupts service; database separation is primarily for operational and I/O isolation.

Next, a second application host is considered. The team verifies sessions are externalized, uploaded objects are not stored on local disk, deployment state is consistent and the reverse proxy or load balancer can remove unhealthy instances. A second node without shared state or tested routing can create inconsistent behavior. The team rolls out one host at a time and checks capacity if either node is lost. It uses a small queue worker separately so import bursts do not starve request handling.

A managed database's automatic failover and backups have provider-specific semantics. Read the current service documentation, test application reconnect behavior and measure actual promotion time. Do not infer a recovery objective from a checkbox. Retain independent export or backup access if the recovery plan needs it, and test credentials from an isolated environment.

## Delay Kubernetes until its costs make sense

The team discusses Kubernetes because it promises standardized scheduling and deployment. Today it owns two application hosts, one database, a queue and a small rota. It would also need cluster upgrades, network and ingress policy, node capacity, secrets integration, observability, access control, backup of cluster state where relevant and 24-hour support decisions. A managed control plane removes some work but not workload operations or application recovery.

They delay Kubernetes. A systemd service plus configuration management and a load balancer meets current needs with lower cognitive and operating cost. They will reconsider when the number of workloads, deployment coordination, isolation needs or team count makes a shared orchestrator more valuable than its maintenance. This is an explicit architecture decision, revisited when evidence changes, not a rejection of containers.

The second-host transition also changes failure behavior. If the app can reach a managed database only through a private subnet, route tables, security groups, DNS and connection limits become production dependencies. Test whether a cold application instance can start after a database failover, refresh credentials and establish its pool without overwhelming the database. Keep a startup rate limit and bounded backoff; synchronized restarts can turn recovery into a connection storm. The team records which actions are provider-managed and which remain its responsibility, including regional recovery, encryption keys, access review and application-level integrity. A service catalogue entry links the owner, runbook, service objectives and current architecture decision.

 The team also plans for future ownership transfer: configuration, alert routing and database restore instructions live in a versioned repository, with a second engineer rehearsing each change. A deployment that only its author can perform is a hidden single point of failure. As the VPS model evolves, the team compares recovery time and operator load rather than relying on assumed cloud resilience.

Exercises:

1. CPU is low, but p99 order latency rises during imports. Which measurements separate database, lock and network causes?
2. A second app server is added, but customers report missing uploads. What state was not externalized?
3. A managed database advertises automatic failover. What must be tested before updating the recovery promise?
4. The team operates three services and proposes a Kubernetes cluster. Which costs belong in the comparison?

Answer guidance: trace request spans and database query/lock/wait metrics alongside storage I/O and connection saturation; test a bounded import. Local file state is missing across hosts; move objects to shared durable storage with access, retention and recovery semantics. Test client reconnect, endpoint changes, data loss/lag, measured promotion, backup restore and operator procedure. Include patching/upgrades, security, networking, monitoring, backup, capacity, on-call, expertise, migration and exit costs, not only VM prices.

Review questions:

- Which evidence distinguishes vertical resource shortage from a query bottleneck?
- What must be true before adding a second stateless app instance?
- Which managed-service responsibilities remain with the application team?
- What organizational or operational trigger would justify Kubernetes?

Takeaways:

- Profile the workload and user journey before scaling resources.
- Separate components when the boundary improves isolation or operation and the team can manage the seam.
- Verify provider failover and recovery behavior with the actual application.
- Compare total platform ownership and defer orchestration that solves no current constraint.

## Sources checked 2026-10-04

- [PostgreSQL monitoring statistics](https://www.postgresql.org/docs/current/monitoring-stats.html) — database workload evidence.
- [Kubernetes concepts](https://kubernetes.io/docs/concepts/) and [Chapter 204](204-the-kubernetes-platform-company.md) — orchestration scope and later justified use.
- Chapters 181, 186, 187 and 199 — service objectives, backups, recovery and engineering economics.

DispatchDesk growth and measurements are fictional. No provider failover or load test was run.
