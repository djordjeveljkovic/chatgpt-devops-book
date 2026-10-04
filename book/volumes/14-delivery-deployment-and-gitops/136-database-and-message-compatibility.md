---
book: The Complete DevOps Engineering Book
volume: 14
volume_title: "Delivery, Deployment and GitOps"
chapter: 136
title: "Database and Message Compatibility"
slug: database-and-message-compatibility
status: complete
summary: ../../_ai/chapter-summaries/136-database-and-message-compatibility.md
---

# Chapter 136 — Database and Message Compatibility

## Why schema changes are releases too

Application code is often rolled out gradually. During that time, old and new processes may read and write the same database, queue, cache, or object store. A schema change that works with only the new binary can break the still-running old version, a delayed job, a scheduled report, or a message that was produced hours earlier. Database and message compatibility are therefore part of release engineering, not separate cleanup work for a database team.

The safest general shape is expand, migrate, switch, contract. First add a structure that lets old and new code coexist. Then move existing data and clients to the new form. Only after all readers, writers, workers, and rollback paths have stopped depending on the old form should you remove it. These phases can span several application releases. [Chapter 134](134-rolling-updates-and-blue-green.md) explains why mixed versions are normal during rollout; [Chapter 135](135-canary-releases-and-feature-flags.md) explains how gradual exposure adds evidence but cannot make an incompatible schema safe. This chapter focuses on changes that remain compatible while releases and old messages overlap.

## Expand-and-contract schema changes

Consider DispatchDesk renaming `customers.contact_email` to `customers.notification_email`. A direct rename may immediately break every still-running binary that queries `contact_email`. Dropping the old column after a backfill is also unsafe if an old worker, delayed task, report, or rollback version can still read it. Instead, use explicit application and data phases.

| Phase | Schema/data | Application behavior | Release gate |
|---|---|---|---|
| Expand | Add the nullable `notification_email` column; keep `contact_email` | Existing version continues unchanged | Confirm the additive DDL and operational lock impact are acceptable |
| Compatible writer | Both columns exist | New transitional version continues reading the old column and writes both values in one database transaction | Wait until old-only writers are gone |
| Backfill | Copy old values into the new column in bounded batches | Transitional code remains authoritative on the old field while both writes continue | Check progress, locks, replication lag, and row consistency |
| Switch readers | Both columns remain populated | New version reads the new column and still writes both | Verify reads and rollback to transitional code |
| Stop old writes | Both columns remain during the new-field-compatible rollback window | New version reads and writes only the new column | Verify no old reader, writer, report, or old-column-only rollback candidate remains |
| Contract | Drop the old column in a later change | All supported versions use only the new column | Recheck dependencies, backups, migration plan, and recovery limits |

The order matters. While old-only writers still run, the new column is incomplete and cannot be treated as authoritative. If a transitional version writes both columns while an old version writes only the old one, the two fields can temporarily disagree. Keep the old field canonical until old-only writers have drained; then backfill again or catch up the differences before switching reads. This avoids a subtle lost-update bug in which the new field contains a stale value and hides a later update written by old code. Write both fields in one transaction where possible. If transactionally synchronized dual writes are not possible, use an explicitly designed database trigger, compatibility view, change stream, or a controlled write pause; do not assume repeated backfills alone will win a race with active writers.

For a PostgreSQL-specific illustration, after all active writers use the transitional dual-write version, a batch can update rows where the new field differs from the old one:

```sql
WITH batch AS (
    SELECT id
    FROM customers
    WHERE notification_email IS DISTINCT FROM contact_email
    ORDER BY id
    LIMIT 500
    FOR UPDATE SKIP LOCKED
)
UPDATE customers AS customer
SET notification_email = customer.contact_email
FROM batch
WHERE customer.id = batch.id;
```

This statement illustrates one idempotent batch, not a complete migration runner. Execute it repeatedly in bounded transactions with an explicit progress/checkpoint mechanism, a pause or rate limit, and a final catch-up pass. The primary key and table are fictional. Validate the PostgreSQL syntax against the supported server version and inspect the execution plan in a safe environment first. `SKIP LOCKED` can let concurrent workers avoid waiting on locked rows, but a final pass without skipped rows is needed to prove no mismatches remain. Monitor transaction time, lock waits, replication lag, disk growth, query latency, and autovacuum behavior; PostgreSQL warns that large updates can increase bloat, lock contention, and replica lag ([PostgreSQL `UPDATE`](https://www.postgresql.org/docs/18/sql-update.html)).

DDL also has operational behavior. In PostgreSQL, lock level varies by `ALTER TABLE` operation, and most forms acquire an `ACCESS EXCLUSIVE` lock. A metadata-only change can still wait behind a long transaction; once a strong lock request queues, later work may also be delayed. Plan for the specific engine and version, use an appropriate lock timeout or migration tool policy, and split risky operations into separate reviewed releases. Building an index can scan a large table and affect writes. PostgreSQL’s `CREATE INDEX CONCURRENTLY` avoids locks that prevent normal writes but takes longer, has caveats, and cannot run inside a transaction block. Other database engines have different online DDL capabilities and locking rules; do not assume PostgreSQL behavior applies to MySQL, SQL Server, or a managed database variant ([PostgreSQL `ALTER TABLE`](https://www.postgresql.org/docs/18/sql-altertable.html), [`CREATE INDEX`](https://www.postgresql.org/docs/current/sql-createindex.html)).

An additive column is not automatically harmless. A `NOT NULL` requirement, default expression, large rewrite, index, foreign key validation, trigger, or database-version difference may turn it into a blocking or resource-intensive operation. Design the first migration around the actual target engine, table size, write rate, replication mode, and lock budget. A change that cannot complete within its lock and maintenance budget should be redesigned or performed with an engine-specific online migration technique. The application can tolerate both structures while the schema moves; the database still needs its own plan for safe execution and recovery.

Backfill correctness needs an invariant, not just a row count. If the old and new fields should be equal, compare null-aware values and investigate every mismatch. If a transformation is lossy or maps multiple old values to one new value, define how to detect and resolve conflicts before cutover. Preserve the original field until the new representation has been verified and the rollback window has passed. Take a backup or snapshot according to the system’s recovery objective, but remember a snapshot does not make a bad migration safe; restoration must also be tested and may lose writes after the snapshot.

## Backfills and mixed-version messages

Database and queue changes share a compatibility problem: different versions may observe the same data at different times. A database reader sees rows already committed; a queue worker may receive an event created by an older producer and retained for later delivery. Queue retention and retry behavior can extend the compatibility window beyond the normal application rollout. Draining a service to zero does not prove that no old-format message remains in a queue or dead-letter queue.

For message evolution, prefer additive changes that old consumers can ignore and new consumers can handle when a field is absent. For example, add an optional `source` field to a `dispatchdesk.order.created` event while preserving the existing `order_id` and `customer_id` meanings:

```json
{
  "event_type": "dispatchdesk.order.created",
  "schema_version": 2,
  "order_id": "ord_01J8EXAMPLE",
  "customer_id": "cus_01J8EXAMPLE",
  "source": "web"
}
```

The identifiers and payload are fictional. Before producers emit version 2, deploy consumers that tolerate both the old message and the new optional field. If any old consumer rejects unknown fields, either keep the new field out of messages until all such consumers are retired, route versions separately, or use a compatibility adapter. Do not rely on JSON libraries ignoring unknown properties without checking their configured behavior. A schema registry can validate specific formats and compatibility modes, but its rules are format- and policy-specific. Backward compatibility means a new consumer/schema can read data written with the prior schema; this supports deploying compatible consumers before producers change. Forward compatibility means an old consumer/schema can read data written with the newer schema; this supports producer changes while older consumers remain. Full compatibility requires both directions for the versions being compared. A transitive mode checks compatibility against all earlier registered versions rather than only the most recent one. These checks do not guarantee that an event retains the same business meaning. Confluent’s registry documentation describes the modes and notes that allowed changes depend on the schema format and original field definition ([schema evolution and compatibility](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)).

Use an explicit schema or event version when consumers need to choose interpretation. Do not reuse a field name with a new meaning, silently change units, reinterpret an identifier, or change a timestamp from seconds to milliseconds while keeping the same shape. Prefer stable units and names; introduce a new field or event type when semantics change. A default value is a business decision: `"source": "unknown"` can preserve old events for analytics, but inventing a default that changes order handling can corrupt behavior. Unknown message versions should have a defined path such as a quarantine queue, alert, and operator review rather than an infinite retry loop.

Consumers should tolerate retry and duplicate delivery as well as schema drift. Idempotency keys, conditional state transitions, and deduplication windows determine whether processing the same event again repeats an external action. A compatibility rollout should also respect ordering and partition keys where the broker uses them. Chapter 163 covers backpressure and queue operations; this chapter focuses on the producer/consumer version contract.

## Releasing without breaking old workers

DispatchDesk uses an API to publish `order.created` events and a worker to send notifications. A new notification template needs a locale field. The team first changes the consumer to accept events both with and without `locale`; absent values use a safe, documented fallback. That consumer is deployed and confirmed across all worker pools. Only then does the API start including the optional field. Old messages remain valid, and rollback to the prior API still emits the original form. When the queue’s maximum retention, retry, and dead-letter reprocessing windows have elapsed, the team can consider removing old-format support in a separate release.

Do not assume every worker is part of one deployment. There may be a delayed autoscaled worker, a scheduled batch job, a second region, a manual replay tool, a data export, or a rarely used admin command. Inventory all producers and consumers before changing a shared schema. Tag metrics and logs with service version and event version; watch decode failures, retry counts, dead-letter volume, oldest message age, and business completion. Sample payloads carefully and redact personal or payment data. If the team cannot prove old workers are gone, design the new format for old workers to tolerate.

A common failure occurs when the API publishes the new event before all old workers are replaced. One old worker rejects the new field and retries the message until it reaches the dead-letter queue. The API dashboard remains green because it successfully wrote to the queue. Diagnose the issue by checking consumer version distribution and error class, comparing a redacted message schema to the worker’s decoder, and inspecting retry/DLQ metrics. Stop the producer’s new format or disable the feature that emits it, then deploy a compatible consumer. Re-drive affected messages only after idempotency and ordering implications are understood; replay can repeat side effects.

Database rollback has similar limits. If the new application writes a value that the old version cannot read, reverting the binary can make the system worse. If a contract migration drops the old column, rolling back only the application cannot recreate its data. During the phase that stops writes to the old column, the old column remains present but becomes stale; only releases that read the new column remain valid rollback candidates. Remove old-column-only binaries and rollback targets before that phase. Keep the old structure through the remaining new-field-compatible rollback window, then choose the point of no return explicitly. After that point, repair-forward or restore-and-replay may be safer than rolling back code. A migration ledger should record which application versions require which schema and message versions, and which rollback targets remain valid.

## Exercises

1. A new binary reads `notification_email`, but half the old workers still update only `contact_email`. Why can a backfill performed before deployment leave stale values later?
2. A large PostgreSQL table needs a new index during a busy period. Compare ordinary `CREATE INDEX` with `CREATE INDEX CONCURRENTLY`, and list operational checks before either runs.
3. A new producer adds an optional JSON field. Some old consumers reject unknown fields. Design a release order that avoids dead-lettering messages.
4. The queue is empty immediately after deployment. Why might it still be unsafe to remove support for the old event format?
5. A contract migration has dropped the old database column and a new release fails. Why may rolling back the application not restore service, and what evidence informs recovery?

### Answer guidance

1. Old workers continue writing only the old field after the backfill, so the new field can become stale or remain null. Keep the old field authoritative, replace old-only writers with code that dual-writes transactionally, then backfill/catch up and verify before switching reads.
2. An ordinary PostgreSQL index build can block table writes while it runs. `CONCURRENTLY` permits normal writes during the build but takes longer, has failure caveats, and cannot run inside a transaction block. Check server version, table size, lock and disk budget, long transactions, write load, replica lag, index definition, migration-tool transaction behavior, and a recovery plan; validate on representative data.
3. Deploy consumers that accept both message shapes first and confirm every pool and replay path is updated. Then enable the producer’s new optional field. Keep the old format available for rollback until the full compatibility window expires.
4. Delayed messages, retries, dead-letter queues, scheduled producers, or archived replay payloads may still contain old events. Check the retention and re-drive windows and consumer inventory; preserve old-format parsing until those sources are handled or retired.
5. The old binary may reference a column that no longer exists, and the dropped data may not be recoverable from a schema-only rollback. Inspect the migration ledger, backups/PITR window, writes since backup, affected rows, and compatibility of candidate versions. Decide among repair-forward, restore-and-replay, or another tested recovery path; do not assume redeploying old code is enough.

## Review questions

- Why does expand-and-contract require several releases instead of a rename and one application deployment?
- During which phase is it safe for a new field to become authoritative?
- What is the difference between backward-compatible schema syntax and compatible business semantics?
- Which sources can keep old message formats alive after the main worker deployment finishes?
- When is rollback no longer a safe substitute for repair-forward or data recovery?

## Takeaways

- Keep the current schema and clients working while adding the next representation; contract only after every dependency has moved.
- Treat active writers as part of backfill correctness; dual-write and catch-up ordering matters.
- Design messages for both old and new producers/consumers through the queue, retry, dead-letter, and replay window.
- Validate engine-specific DDL locking, index behavior, version support, and backfill impact before production execution.
- Record the point where old code or data can no longer be restored, and maintain a recovery plan for that boundary.

## Further reading

- [Chapter 134 — Rolling Updates and Blue Green](134-rolling-updates-and-blue-green.md)
- [Chapter 135 — Canary Releases and Feature Flags](135-canary-releases-and-feature-flags.md)
- [Chapter 163 — Queues and Backpressure](../17-distributed-systems-and-data-operations/163-queues-and-backpressure.md)
- [PostgreSQL `ALTER TABLE`](https://www.postgresql.org/docs/18/sql-altertable.html)
- [PostgreSQL `UPDATE`](https://www.postgresql.org/docs/18/sql-update.html)
- [PostgreSQL `CREATE INDEX`](https://www.postgresql.org/docs/current/sql-createindex.html)
- [Confluent Schema Registry compatibility](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html)

Sources reviewed 2026-10-04. SQL and event payloads are illustrative; no production database, migration, queue, or consumer was changed or run.
