# Independent review — Chapter 168

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 7cafd736766c44f169eab304fcba1de6fd79bb69754bd1178c2631e53f24c01b

## Scope and findings

Read current complete body and compact summary, Chapter 168 skeleton brief and authoring-guide requirements, with Chapters 164/165/167 prerequisite context. Reviewed PostgreSQL SQL and plan interpretation, indexes, partition pruning/uniqueness, RDS replica freshness, shard ownership/skew/scatter-gather, decision/recovery reasoning, Linux prerequisites, exercises/answer guidance, takeaways and local/source links. No material technical finding; chapter satisfies the brief.

The SQL is syntactically coherent on PostgreSQL 18: generate_series supplies bounded integer input, bigint ID and modulo tenant selection are valid, timestamp plus integer-times-interval is valid, and the multicolumn descending index supports the tenant equality/time range/order. The temporary relation and index are transaction-local and ROLLBACK removes them. Authorized nonproduction connection identity is required before the experiment; no application tables are modified. EXPLAIN ANALYZE executes the SELECT, and neither a particular plan nor a measured speedup is fabricated. Input size is bounded, not a wall-clock runtime guarantee. The selected tenant has six rows beyond noon; LIMIT 20 is an upper bound, not a promised result count. Index setup cost is separate from the plan's execution measurement and repeated-workload amortization remains necessary.

Index leading-column guidance is qualified rather than claiming later-column constraints cannot help; PostgreSQL 18 skip-scan behavior therefore does not contradict it. Write/storage/statistics costs remain visible. Declarative partitioning is distinguished from distributed write ownership; pruning depends on compatible predicates. Partitioned unique/primary keys must contain all partition columns, so order-ID-only global uniqueness is not promised. Future partitions/default routing and lifecycle/backup validation are included without supplying destructive production DDL.

RDS PostgreSQL read replicas are appropriately scoped as asynchronous physical replication. Idle lag growth until WAL switches is documented and is not treated as proof of data loss. Replica routing depends on per-request freshness, not GET versus mutation classification or average lag. Failure recovery restores authoritative confirmation reads while retaining only stale-tolerant catalog routing; primary write saturation remains a separate bottleneck.

Tenant hashing does not subdivide a dominant tenant. Sharding requires placement authority, skew measurements, cross-key transaction contracts, migration reconciliation and rollback boundaries. Scatter/gather includes slowest-response and incomplete-result concerns. Independent PostgreSQL engines do not magically share a transaction. The decision example includes observations, a failed assumption, diagnosis, recovery and joint latency/freshness acceptance. Exercises supply accurate answers, and the outline/questions/takeaways are explicit.

Low optional observation — compact summary, Examples and cross-references: it labels the fictional scaling decision DispatchDesk, while the body's decision section uses Summit (DispatchDesk supplies the opening contract). Name Summit there or both examples for exact summary attribution. This does not alter technical approval.

## Primary evidence checked 2026-10-04

- [PostgreSQL 18 multicolumn indexes](https://www.postgresql.org/docs/18/indexes-multicolumn.html): leading-column constraints and qualified skip-scan behavior.
- [PostgreSQL 18 EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html): ANALYZE execution, row/buffer and timing interpretation; no production percentile inference.
- [PostgreSQL 18 declarative partitioning](https://www.postgresql.org/docs/18/ddl-partitioning.html): routing/pruning, missing-partition failure, maintenance/locking and partitioned uniqueness limitations.
- [RDS PostgreSQL read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PostgreSQL.Replication.ReadReplicas.html): native replication and idle transaction/WAL-switch lag qualification.
- [RDS PostgreSQL replication monitoring](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PostgreSQL.Replication.ReadReplicas.Monitor.html): physical replication slots, replay-time lag and recovery/storage monitoring boundaries. Its historical tuning examples were not adopted as current PostgreSQL 18 commands.

## Validation and limits

`python3 tools/check_book.py --chapters 168-168` passed 1,455 global local links without warnings/errors. It reported no SQL parser/runtime check; SQL syntax/control flow and example selection were independently inspected statically. Exact stripped-front-matter body hash computed using `tools.promote_reviewed.body_hash`. No PostgreSQL session, plan output, index benchmark, RDS replica, production workload, migration, partition maintenance, shard move or recovery execution performed. No distribution/client/server matrix tested. Documentation and static reasoning cannot establish production query benefit, actual stale-age bounds or migration reversibility. Only this separate review record written.

Verdict: approved
