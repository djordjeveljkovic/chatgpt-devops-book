---
book: The Complete DevOps Engineering Book
volume: 4
volume_title: "VPS and Server Operations"
chapter: 39
title: "Adding a Second Server"
slug: adding-a-second-server
status: complete
summary: ../../_ai/chapter-summaries/039-adding-a-second-server.md
---

# Chapter 39 — Adding a Second Server

## Two hosts change the failure model

Adding another VPS can increase application capacity and allow maintenance without stopping every API process. It also introduces network dependencies, coordination and shared-state questions. Two servers that both write independent local databases do not form one coherent service. A second machine helps only when traffic, authority, data placement and recovery are designed together.

Harbor's next step is two DispatchDesk API hosts behind a traffic router, with one authoritative PostgreSQL service and an optional cache that can be rebuilt. The API instances must be replaceable and must share the same acceptance contract. This is not yet high availability: a single database, proxy, DNS provider, account or network path may still be a failure point. Label the topology accurately and decide which failure the extra host is intended to tolerate.

Before provisioning, establish the reason for a second host with measurements: CPU saturation, memory pressure, deployment interruption, geographic access or a recovery objective. If PostgreSQL is saturated, adding API capacity may increase connection pressure and worsen latency. If a single VPS is hitting disk or memory limits, moving the database or resizing may solve the constraint more directly. The decision belongs to the measured bottleneck.

## Make application instances interchangeable

Both application instances need the same trusted artifact, compatible configuration, runtime identity, clock assumptions and service behavior. Build once and deploy the same immutable digest to each host. Do not manually patch one instance until it behaves differently. Keep secrets out of the artifact and distribute them through a restricted process. Configuration changes and schema migrations need an explicit compatibility window so old and new application versions can run at the same time during rollout.

The API instances should not rely on local memory or disk for authoritative orders, sessions required across requests, idempotency records, durable work or user uploads. Store accepted orders and notification intents in the shared PostgreSQL authority. If a session is needed, use a shared session mechanism or a stateless signed token with the required revocation and key-rotation policy. If the app writes files, move them to an explicitly shared durable service or define a safe synchronization protocol. Local caches are disposable only when a cache miss can reconstruct the value without violating correctness.

Run the notification worker separately from API scaling or give it an explicit shared ownership and concurrency model. If each API host starts its own worker, the database queue contract must ensure that work is claimed once at a time, recovered after a crash and safe under duplicate provider outcomes. A shared database alone does not make external notification delivery exactly once. Keep idempotent acceptance, stable provider request identity, bounded retries and reconciliation as explicit application responsibilities.

## Place traffic and database paths deliberately

The router can be a managed load balancer, a reverse proxy on a separate host or another supported traffic layer. Configure it to send requests only to instances that meet the application readiness contract. Liveness should not cause healthy instances to be removed merely because a downstream dependency is temporarily slow; readiness can stop new orders while the process remains available for diagnostics and controlled drain. Probe behavior, thresholds and fail-open or fail-closed policy affect real availability and must be tested.

If Nginx is used as the router, its `upstream` group can list multiple application addresses. A local Nginx process still creates a single proxy failure point, and upstream health behavior depends on the Nginx edition, version and configured checks. The default open-source upstream behavior should not be mistaken for an active health-check system. A router must remove an unhealthy instance according to a deliberate policy and permit graceful drain during deployments.

The database path now crosses a network. Place PostgreSQL on a private interface or managed service, allow connections only from the app hosts and operator paths that need them, and configure PostgreSQL listener and authentication policy together. Use TLS when the chosen network and threat model require encryption in transit, validate certificates, and use a dedicated application role with bounded permissions. Rotate credentials without leaving one instance on an obsolete secret. Monitor connection pool totals across both application hosts, worker processes, migrations and observers. More API replicas multiply potential database clients.

Do not move the database by copying its live data directory and pointing a new server at it. Select a supported migration: planned outage with a consistent backup and restore, logical replication or another version-appropriate method. Set a write freeze or replication catch-up boundary, validate row counts and application invariants, and define who authorizes traffic cutover. Keep the original database intact until the new authority passes validation and rollback criteria are met. Split-brain writes to two independently writable databases are a data-loss risk, not redundancy.

## Roll out without losing accepted work

Provision the second host from the same reviewed image and configuration process as the first. Apply the access baseline from Chapter 32, configure private routing and firewall allowlists, install the same systemd unit, deploy the same artifact digest and verify its database connection before admitting traffic. The readiness endpoint should remain false until the instance is configured to serve safely. A health endpoint that returns success before secrets, schema compatibility or required dependencies are ready can create avoidable failures.

Add the new instance to the router with a small or controlled share of traffic. Confirm distribution using server-side request counts and synthetic checks, not only a DNS lookup. Observe acceptance errors, latency, database pool waits and notification backlog. Increase traffic only while the error budget and business invariants remain healthy. Drain one instance by marking it unready, allowing in-flight requests to finish within a deadline, and stopping new background claims before shutdown. Do not kill a worker that may have an ambiguous provider request without following its reconciliation protocol.

For rollback, remove the instance from routing and preserve logs and configuration. Revert the application artifact only if it remains compatible with the current schema and shared state. A database migration may have crossed the point where code rollback is safe. Rollback should restore a known operating configuration, not erase accepted orders created during the deployment.

## Test failures intentionally

A second API host can fail while the database remains available. The router should stop sending new work there, existing accepted orders remain in shared storage, and the surviving instance should continue within its measured capacity. If the failed host contained an authoritative local SQLite file, this expectation is false; the topology is not ready for active-active traffic.

Test database unavailability, router health-check delay, one-host loss, credential rotation and slow database response in a controlled environment. Verify that retries do not create duplicate orders, that `/readyz` changes for the intended conditions, and that in-flight notifications remain recoverable. Measure recovery rather than assuming a health check or DNS TTL supplies a recovery-time guarantee. Include failure of the traffic router and database in the next architecture iteration; the two-host design does not eliminate them.

## Exercises and review questions

1. Sketch the two-host request path and identify every shared dependency and single failure point.
2. Which DispatchDesk data can remain local to an API instance? Explain why each local item is reconstructible or harmless to lose.
3. Calculate the maximum PostgreSQL connections if each host runs four API processes with a pool of eight, plus two workers with four connections each and six operational connections. What should you measure before accepting that total?
4. Design a database cutover checklist that proves the source is no longer writable before the new authority accepts traffic.

**Answer guidance:** For exercise 1, trace the public router, both API hosts, PostgreSQL, optional cache and notification worker; the database and router remain shared failure points. For exercise 2, keep only reconstructible caches, temporary files and instance-local telemetry on an API host; orders, intent and any coordination state must remain in the shared authority. For exercise 3, the exercise says four API processes on each of two hosts, so the API ceiling is `2 × 4 × 8 = 64`; add two workers at four connections each and six operational connections for a total of `64 + 8 + 6 = 78`. If the intended topology were four API processes total across both hosts, the total would instead be `4 × 8 + 2 × 4 + 6 = 46`. Treat either result as a ceiling, reserve administrative headroom, compare it with `max_connections`, and measure memory and query concurrency before accepting it. For exercise 4, stop or fence source writes, wait for replication or migration catch-up, verify counts and business invariants, revoke the old writer's credentials or network access, then enable writes and traffic on the new authority; retain a rollback path that cannot create a second writer.

A second server is useful when both the bottleneck and shared-state contract justify it. It adds capacity without duplicating the source of truth, while leaving router, database and provider failure modes visible for later design. Chapter 40 uses these layers to investigate VPS incidents and capacity limits.

## Sources and verification

The official Nginx [`ngx_http_upstream_module`](https://nginx.org/en/docs/http/ngx_http_upstream_module.html) documentation and PostgreSQL 18 [connection](https://www.postgresql.org/docs/18/runtime-config-connection.html) and [backup/restore](https://www.postgresql.org/docs/18/backup.html) guidance were inspected on 2026-10-04. This chapter is an architecture and rollout design; no second host, database migration, load balancer or traffic cutover was performed.
