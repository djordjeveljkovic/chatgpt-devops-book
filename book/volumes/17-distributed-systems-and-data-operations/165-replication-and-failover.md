---
book: The Complete DevOps Engineering Book
volume: 17
volume_title: "Distributed Systems and Data Operations"
chapter: 165
title: "Replication and Failover"
slug: replication-and-failover
status: draft
summary: ../../_ai/chapter-summaries/165-replication-and-failover.md
---

# Chapter 165 — Replication and Failover

## Replication copies state under a particular acknowledgment rule

A second database copy improves some recovery options, but “replicated” does not specify which writes survive a failure. DispatchDesk may receive a commit acknowledgment from a primary before a standby has received or replayed that write. If the primary disappears permanently and the standby becomes authoritative, an acknowledged order can be absent from the promoted copy. The application contract must name the durability expectation and the configured acknowledgment boundary.

[Database concurrency](164-database-connections-and-concurrency.md) addressed transactions inside one authority. Replication adds another timeline of received, persisted and applied changes. A standby can have received data without making it visible to queries. A client reading immediately after a primary write may observe older state from an asynchronous read replica. Calling that result “order not found” can mislead a retrying caller into creating another operation.

Asynchronous replication usually avoids waiting for a remote copy on each commit, while accepting a possible loss window under defined failures. Synchronous configurations can wait for specified remote evidence, increasing latency or reducing write availability when required replicas are unavailable. The exact engine and setting decide whether the acknowledgment concerns remote receipt, durable flush or replay visibility. [PostgreSQL's standby documentation](https://www.postgresql.org/docs/current/warm-standby.html) defines its mechanisms; do not assume that every managed service or broker uses the same rule.

Replication is also not a backup. Accidental deletion or a harmful migration can propagate rapidly to every replica. A backup or point-in-time recovery path retains a historical state under an independent retention and access policy. Test both availability recovery and historical data recovery; they answer different questions.

## Measure the part of lag relevant to the decision

Lag can be expressed in bytes, positions, elapsed time or customer-visible freshness. Each has a denominator. A standby's last replay timestamp can be old because the primary has been idle, even when the standby is fully caught up. A small byte gap can contain an important recent order; a large gap can consist mostly of unrelated bulk work. Use the appropriate evidence for failover and read-freshness decisions.

For an existing authorized PostgreSQL primary and standby, inspect role and WAL positions through approved observer connections. [Chapter164](164-database-connections-and-concurrency.md) explains psql service selection and identity checks. Define separate controlled client services for the real primary and standby; this chapter neither provisions replication nor invents their credentials. The read-only SQL is the same on Ubuntu, Fedora and RHEL with compatible clients. Database setup, service units and security policies remain distribution-specific.

On the primary, after confirming the intended database and role:

```sql
SELECT current_database(), current_user, pg_is_in_recovery();
SELECT pg_current_wal_lsn() AS current_wal_position;
SELECT application_name, state, sync_state,
       sent_lsn, write_lsn, flush_lsn, replay_lsn,
       write_lag, flush_lag, replay_lag
FROM pg_stat_replication
ORDER BY application_name;
```

On the standby:

```sql
SELECT current_database(), current_user, pg_is_in_recovery();
SELECT pg_last_wal_receive_lsn() AS received_position,
       pg_last_wal_replay_lsn() AS replayed_position,
       pg_last_xact_replay_timestamp() AS last_replayed_transaction_time;
```

`pg_is_in_recovery()` helps distinguish a recovery-mode standby from a writable primary, but it is not a complete proof of cluster leadership authorization. Primary WAL position and sender rows give different parts of the replication path; standby receive and replay positions expose local progress. Statistics visibility requires approved privileges. [PostgreSQL's administration-function reference](https://www.postgresql.org/docs/current/functions-admin.html) defines these functions, while [monitoring statistics](https://www.postgresql.org/docs/current/monitoring-stats.html) defines sender fields and lag limitations.

Capture observation time and system identity beside the values. Comparing positions across different timelines after promotion needs engine-aware interpretation; do not subtract arbitrary hexadecimal strings from unrelated histories. A null field can mean no relevant progress or connection, not necessarily zero lag. A one-time query is insufficient to establish stable recovery readiness.

A read-after-write requirement can route the relevant lookup to the current write authority, wait for a known replication position under a bounded policy, or use another explicit consistency mechanism. Each costs something. Routing all reads to a replica while promising immediate visibility of newly accepted orders is an inconsistent contract unless the replication and read path actually support it.

## A complete local loss-window model

Save this as `replication_model.py` and run `python3 replication_model.py` as an ordinary user with Python3 on Ubuntu, Fedora or RHEL. It models lists of symbolic committed orders rather than a database protocol. It exposes which acknowledgments a chosen replica can recover; it does not implement WAL, replication, fsync or failover.

```python
primary = ["order-A", "order-B", "order-C", "order-D"]
standby_received = ["order-A", "order-B", "order-C"]
standby_replayed = ["order-A", "order-B"]

async_acknowledged = set(primary)
remote_flush_acknowledged = set(standby_received)
remote_apply_acknowledged = set(standby_replayed)

for name, acknowledged in (
    ("primary-only acknowledgment", async_acknowledged),
    ("modeled remote persistence acknowledgment", remote_flush_acknowledged),
    ("modeled remote visibility acknowledgment", remote_apply_acknowledged),
):
    recoverable_after_replay = set(standby_received)
    absent_on_recovered_copy = acknowledged - recoverable_after_replay
    not_yet_visible = acknowledged - set(standby_replayed)
    print(name)
    print("  acknowledged but absent after recovery:",
          sorted(absent_on_recovered_copy))
    print("  acknowledged but not visible in current replay state:",
          sorted(not_yet_visible))
```

The model assumes every received entry is safely persisted and can replay after failure, an assumption stronger than the variable name alone. Under its primary-only acknowledgment case, orderD is acknowledged but absent from the surviving copy. OrderC is present for recovery but not yet visible in the current replay state. That distinction explains why durability and read freshness need separate language.

The named acknowledgment cases are teaching abstractions, not exact configuration names or guarantees for a provider. Change the surviving copy and examine how the sets change. A synchronous acknowledgment to one particular replica does not automatically prove every different candidate has that data. Candidate selection must honor the actual replication contract. Cleanup removes the local model file; it created no infrastructure or durable customer records.

## Leadership requires exclusion as well as selection

Failover chooses a new write authority. It must also prevent the old authority from continuing to accept writes. A network partition can make a healthy primary unreachable to an observer while it remains reachable to some clients. Promoting a standby solely because one monitor timed out can create two writers with diverging histories.

Fencing is the mechanism that prevents obsolete authority from performing protected work. It might be enforced through storage access, network/control-plane isolation, power-off or an authority token checked by the resource receiving writes. The specific mechanism must remain effective under the modeled partition. A polite request telling the old leader to stop is inadequate if it cannot receive the request.

An epoch or increasing fencing token is useful only when the protected resource rejects older tokens. Logging a new epoch without enforcing it on mutations changes observability rather than safety. Similarly, a load balancer's new target list does not stop a forgotten client from writing directly to the old database address. Inventory all write paths, including administrative jobs, migrations and background workers.

[Consistency and consensus](166-consistency-and-consensus-concepts.md) explains how coordinated authority can be selected. Consensus among controllers does not by itself guarantee that an unrelated database or provider rejects a stale controller's action. The authority decision and the protected resource's enforcement boundary must connect.

## A controlled failover acceptance procedure

For a managed database, use its supported failover workflow and documented topology rather than manually promoting an internal standby. Summit's RDS configuration must distinguish a Multi-AZ DB instance from other RDS deployment types and read-replica arrangements. The inspected [RDS Multi-AZ instance failover guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.Failover.html) describes endpoint and connection recovery for that scope. It does not establish the behavior of every RDS engine, cluster topology or cross-region replica.

Before a staging rehearsal, name the failure, expected recovery point, recovery time, authoritative endpoint and rollback/rejoin route. Preserve a restorable backup, verify candidate health and record replication progress. Use synthetic orders with known IDs and a controlled notification destination. Confirm that the test includes ambiguous in-flight requests and connection-pool replacement, not merely idle database switchover.

During the rehearsal, stop or constrain writes as required by the supported workflow, establish exclusion of the old authority, perform the authorized promotion/failover and verify the new role. Do not publish a universal `promote` command divorced from fencing and candidate selection. Change routing through the owning configuration, then force the application to establish new healthy connections according to its client behavior. Long-lived pools can retain failed or obsolete connections after DNS changes.

Validate the accepted synthetic order set against the declared recovery point. Confirm each recovered order has its paired notification intent. Reconcile uncertain provider effects before allowing bulk replay. Observe latency and errors while caches and storage warm. Verify that old authority cannot accept protected writes, rather than relying only on a green new-primary dashboard.

For failback, do not simply restart the old primary and make it writable. Its history may have diverged. Rebuild or reconcile it through the engine's supported procedure, validate its role and data, and keep it excluded from writes until the topology is accepted. Failed nodes can contain valuable evidence, so preserve appropriate snapshots and logs before destructive reinitialization.

## Diagnose replication interruption before storage exhaustion

A standby can stop receiving because of authentication, network failure or missing retained WAL. It can receive but replay slowly because of storage, resource pressure or query conflicts. Inspect sender/receiver state, position progress, engine logs and storage pressure before restarting both sides. A restart may temporarily reduce symptoms while preserving the cause.

Replication slots or other retention mechanisms can retain change data for a lagging consumer. That protects catch-up only within the configured policy and available disk. A forgotten inactive consumer can contribute to primary storage exhaustion. Inventory ownership and retained bytes; do not delete a slot or archive blindly because a chart is large. Removing retention can make its consumer unrecoverable without reseeding, and archives may also serve backups.

Recovery can restore connectivity, correct credentials, reduce conflicting read workload or rebuild a standby from a trusted backup if required data is unavailable. Afterward verify sustained position progress and adequate primary storage reserve. A writable application can look healthy while its redundancy has silently disappeared, so degraded replication needs its own owner and alert.

## Exercises and answer guidance

A standby's last replayed transaction timestamp is one hour old during an idle period. Does that prove one hour of missing writes? No. Compare relevant positions and primary activity; timestamp age alone can represent no new work.

The promoted candidate contains all recent writes, but the old primary still accepts direct connections. Is failover safe? No. Exclude obsolete authority through a mechanism effective under the failure; routing preference alone does not fence direct writers.

A delete propagates to all replicas. Which recovery asset is needed? A suitable historical backup or point-in-time recovery path, with tested access and retention. Replication copied the unwanted mutation correctly.

## Takeaways and verification

Replication needs a precise acknowledgment and read-visibility contract. Failover needs candidate evidence, exclusion of stale authority, application connection recovery and durable-state reconciliation. PostgreSQL18 and scoped RDS Multi-AZ instance documentation was inspected on2026-10-01. Read-only SQL and the local symbolic model are inline; no replication setup, live database observation, promotion, managed failover or split-brain experiment was executed while authoring.

