---
book: The Complete DevOps Engineering Book
volume: 17
volume_title: "Distributed Systems and Data Operations"
chapter: 168
title: "Database Scaling and Partitioning"
slug: database-scaling-and-partitioning
status: complete
summary: ../../_ai/chapter-summaries/168-database-scaling-and-partitioning.md
---

# Chapter 168 — Database Scaling and Partitioning

**Section outline:** improve the measured query before adding topology; separate write authority from read capacity; use partitioning for pruning and lifecycle management; recognize hot keys and scatter/gather costs; choose and rehearse the smallest scaling step that meets the contract.

## Why this matters

A larger database bill or a high CPU graph does not identify the right scaling change. The limiting work may be one unindexed query, a single hot tenant, lock contention, a slow storage path or reads that could tolerate replica lag. Each remedy changes different behavior. DispatchDesk needs durable order acceptance and prompt notification intent; its catalog search can have a different freshness contract. Scaling must preserve those boundaries.

[Database connections](164-database-connections-and-concurrency.md) distinguishes pool waits from query execution and lock waits. [Replication](165-replication-and-failover.md) explains why a read copy can lag, while [cache design](167-cache-design-and-invalidation.md) treats derived state separately. Use their evidence before adding another database or changing where a customer read goes.

The order of investigation matters. First identify the slow or saturated operation, including its tenant and data-age pattern. Then examine the plan, rows read, locks, pool wait and storage behavior. Add the least complex correction that changes the measured bottleneck. A read replica cannot accelerate a write-bound transaction; a partition cannot divide one hot key; a shard cannot fix an inefficient query that runs on every shard.

## Improve the query and index before multiplying systems

Indexes trade storage and write work for faster access patterns. A multicolumn B-tree is most effective when query predicates constrain its leading columns; PostgreSQL may combine indexes in some plans, but more indexes are not free. Every index consumes space and adds maintenance to inserts, updates and vacuum work. Choose it from frequent, important query shapes and verify with representative parameters and table statistics.

The following bounded exercise uses an existing authorized **nonproduction** PostgreSQL database and the `psql` client. It creates a temporary table containing synthetic events and removes it by rolling back the transaction. It does not create a persistent schema or touch application tables. Open a connection service for the intended staging database using the approach in [Chapter 164](164-database-connections-and-concurrency.md); on Ubuntu, Fedora and RHEL the SQL below is identical when a compatible client is installed, while packages, service units, authentication and security policy remain distribution-specific.

Start one `psql` session, confirm `current_database()` and `current_user`, then run this complete experiment. `EXPLAIN ANALYZE` executes each `SELECT`; the input is only the synthetic temporary table. Do not point it at a production table or a query with side effects.

```sql
SELECT current_database(), current_user, version();
BEGIN;
CREATE TEMP TABLE synthetic_events AS
SELECT n::bigint AS event_id,
       (n % 1000)::integer AS tenant_id,
       TIMESTAMPTZ '2026-01-01 00:00:00+00'
           + n * INTERVAL '1 second' AS occurred_at
FROM generate_series(1, 50000) AS generated(n);
ANALYZE synthetic_events;

EXPLAIN (ANALYZE, BUFFERS)
SELECT event_id, occurred_at
FROM synthetic_events
WHERE tenant_id = 42
  AND occurred_at >= TIMESTAMPTZ '2026-01-01 12:00:00+00'
ORDER BY occurred_at DESC
LIMIT 20;

CREATE INDEX synthetic_events_tenant_time_idx
    ON synthetic_events (tenant_id, occurred_at DESC);
ANALYZE synthetic_events;

EXPLAIN (ANALYZE, BUFFERS)
SELECT event_id, occurred_at
FROM synthetic_events
WHERE tenant_id = 42
  AND occurred_at >= TIMESTAMPTZ '2026-01-01 12:00:00+00'
ORDER BY occurred_at DESC
LIMIT 20;
ROLLBACK;
```

Compare actual and estimated rows, scan type, buffers and execution time. The result can vary with PostgreSQL version, host cache, planner choices and concurrent work; no plan or speedup is promised here. A sequential scan over fifty thousand narrow temporary rows may be cheaper than index setup for one query. That is a useful outcome: keep the index only when the workload and repeated benefit justify its storage and write cost. `EXPLAIN ANALYZE` measures one controlled execution, not a production percentile or a durable benchmark.

The [PostgreSQL index documentation](https://www.postgresql.org/docs/18/indexes.html) describes index choices, and its [multicolumn index guide](https://www.postgresql.org/docs/18/indexes-multicolumn.html) explains leading-column behavior. Avoid adding a wide “cover everything” index based on one plan. Query parameters, data distribution and result size matter. For a slow query, compare the plan with the expected work and use the observed rows and buffers to decide whether to rewrite the query, add an index, update statistics or investigate storage.

## Separate read demand only when the contract allows it

A read replica can add capacity for suitable reads, but it moves consistency and operations into the request path. The replica may not yet have applied a committed write. A request that confirms an order immediately after acceptance should use its authoritative result path or another explicit read-your-writes design. A product listing or older report may tolerate a measured stale interval. Route by the business contract, not by HTTP verb alone: some `GET` requests reconcile mutations, and some reads require current authorization.

Amazon RDS for PostgreSQL describes its read replicas as asynchronous physical copies using PostgreSQL replication. That is a scoped product example, not a guarantee about all managed database products. The [RDS PostgreSQL read-replica guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PostgreSQL.Replication.ReadReplicas.html) also cautions that reported lag can rise during idle periods until WAL switches. Measure relevant positions and customer-visible freshness instead of interpreting a single timestamp as lost work.

Read scaling does not divide writes, locks or shared storage constraints automatically. Replicas also need monitoring, retention capacity, failover planning and a safe response when they fall behind. If the application can keep issuing reads to a replica whose lag violates the contract, add an explicit lag policy: temporarily use the primary, wait within a bounded request deadline, or return an honest unavailable/stale result. Test the policy during disconnect and recovery.

## Partitioning manages one logical table in smaller pieces

Partitioning keeps one logical table interface while assigning rows to child tables by a partition key and bounds. It can help when common queries constrain that key, when a large table's working indexes no longer fit the workload, or when old data must be detached or retired by range. It does not split a single hot partition across machines. Every query still needs useful predicates, and partition count, index upkeep, constraint design and data routing become operating responsibilities.

For time-bounded event history, monthly range partitions can make retention work on whole old ranges rather than deleting millions of rows individually. This only helps if queries filter by time often enough for partition pruning, and if the team creates future partitions before inserts need them. A query for one customer's full history across all years may still touch many partitions. For transactional orders, partitioning by creation month can also complicate global uniqueness: PostgreSQL requires a partitioned unique or primary-key constraint to include all partition-key columns. An order ID that must be unique across all months may need a different authority design.

PostgreSQL's [declarative partitioning documentation](https://www.postgresql.org/docs/18/ddl-partitioning.html) describes pruning, partition bounds and constraints. Use partitions for a demonstrated access or lifecycle need. A local table split into hundreds of partitions can increase planning and schema-management work without improving the actual query. Validate representative plans and test inserts near partition boundaries, retention detach/drop procedures and backup/restore behavior before applying a production migration.

## Sharding changes ownership and makes cross-key work explicit

Sharding assigns separate key ranges or tenants to different database authorities. It can raise aggregate write and storage capacity when one authority has reached a measured limit and the workload can be divided. It also changes connections, schema deployment, backups, migrations, uniqueness, reporting and failure handling. A shard key becomes part of the product's data ownership contract.

Tenant-based placement can keep a tenant's orders and notifications together, simplifying common tenant-scoped transactions. It can also create a hot shard when one tenant grows much faster than others. Hashing tenants may distribute average load but does not split a single dominant tenant. Time-based sharding can distribute new writes only if the key and query patterns align; otherwise common lookups scatter across authorities. A move plan needs mapping versions, dual-read/write rules, reconciliation, rollback boundaries and a source of truth for placement.

Cross-shard queries may require scatter/gather: send a request to every shard and merge results. Latency then depends on the slowest relevant response, and partial failure can leave an incomplete answer. Global uniqueness and multi-shard atomic transactions need an explicit coordinator or a changed business contract. Do not imply that a database transaction can span independent engines just because both use PostgreSQL.

Before sharding, measure whether better indexing, query changes, vertical capacity, pooling or replicas can meet the next workload stage. Estimate per-tenant and per-key skew, not only the average. Keep a reversible placement migration and practice moving one synthetic tenant before a customer move. A complicated topology is justified when its capacity and isolation benefits exceed its permanent operational cost.

## Choose a data-scaling path from observed constraints

Summit's catalog request becomes slow after growth. The team compares four hypotheses: an inefficient plan; primary read saturation; a large time-series history; and one tenant whose workload dominates. It first records request latency by query family, pool acquisition and execution time, plan rows/buffers, write rate, replication lag and per-tenant distribution. It uses bounded samples without collecting full customer payloads.

If the plan reads far more rows than it returns, test a focused index or query rewrite in staging and confirm write overhead. If many independent reads dominate while writes and authority requirements remain healthy, test a replica route for explicitly stale-tolerant endpoints. If retention scans and time-bounded queries dominate a very large history table, prototype range partitions using realistic predicates and a retention procedure. If a single writer or hot tenant saturates the authority after those options, model a shard move with cross-shard operations and failover included.

The failed assumption is “adding a replica fixes the slow request.” During a rehearsal, the catalog list improves but order confirmation reads stale state from the replica, while writes remain queued on the same primary. Diagnosis separates read latency from write saturation and confirms replica lag. Recovery routes order confirmation back to its authoritative path and keeps the replica only for the tolerant catalog list. Acceptance requires the new request path to meet its stated freshness and latency conditions together; a lower average alone is not success.

## Exercises and answer guidance

A multicolumn index is `(tenant_id, occurred_at)`. Which query is most likely to benefit? A tenant equality plus a time range or ordering, because the predicate constrains the leading key and then the time key. Confirm with plans and write-cost measurements.

A read replica has low average lag but order confirmation cannot tolerate a stale “not found.” Should it serve that lookup? No, unless an explicit consistency mechanism proves the read includes the accepted write. Average lag is not a per-request guarantee.

A monthly-partitioned table receives a new month's data before that partition exists. What must the design do? Ensure partitions are created ahead of routing needs or define a carefully managed default path; inspect and alert on unplanned rows so the lifecycle cannot silently break.

A tenant-keyed shard has one tenant consuming half the write capacity. Will hashing the same tenant key fix it? No. The key still maps that tenant's work to one shard. A split or sub-key design may help only if transaction and uniqueness boundaries permit it.

## Review questions

- Which observed measurements distinguish slow query execution from pool wait, lock wait and replica lag?
- What read-after-write and failure behavior does the application promise before any endpoint is routed to a replica?
- Which query predicates, retention tasks and unique constraints justify a partition key?
- Which cross-tenant transactions, hot keys and reporting queries become harder after sharding?

## Takeaways and verification

Scale from the measured bottleneck and keep consistency requirements attached to each read and write path. Indexes, replicas, partitions and shards solve different constraints and each adds ongoing cost or correctness obligations. PostgreSQL 18 index/partition documentation and RDS for PostgreSQL read-replica behavior were checked on 2026-10-04. The inline SQL is a bounded temporary-table exercise; no database session, replica, migration, shard move or production benchmark was run while authoring.
