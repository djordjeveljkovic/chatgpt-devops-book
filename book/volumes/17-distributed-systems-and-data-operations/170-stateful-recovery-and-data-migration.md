---
book: The Complete DevOps Engineering Book
volume: 17
volume_title: "Distributed Systems and Data Operations"
chapter: 170
title: "Stateful Recovery and Data Migration"
slug: stateful-recovery-and-data-migration
status: complete
summary: ../../_ai/chapter-summaries/170-stateful-recovery-and-data-migration.md
---

# Chapter 170 — Stateful Recovery and Data Migration

**Section outline:** establish source authority and a consistent starting point; backfill and capture concurrent changes; reconcile business invariants; cut over behind a write fence; preserve a real rollback path and recovery evidence.

## Why this matters

A data migration changes which system is authoritative for customer state. A successful copy can still lose a concurrent update, resurrect a deleted row, duplicate a payment or route a customer to stale data. “The task completed” describes a tool, not the correctness of the service. DispatchDesk must know which catalog or order record owns the answer at every migration phase and how to prove it.

[Chapter 169](169-messaging-and-event-driven-architecture.md) used an outbox to preserve publication intent alongside business state. That same principle helps with migration: a consistent snapshot starts the target, and a complete ordered change stream carries later mutations. [Chapter 165](165-replication-and-failover.md) separates replica progress from authority, and [Chapter 168](168-database-scaling-and-partitioning.md) explains partitioning and shard placement. A target that has copied bytes does not become authoritative until validation and cutover criteria are met.

Recovery uses similar evidence but a different goal. A restore returns data to a selected historical point; a migration transfers ongoing ownership to another schema, engine or service. A replica helps availability but may repeat corruption or deletion. A backup can restore history but may omit newer accepted work. Name the desired recovery point, expected loss window, acceptable outage, source-of-truth owner and reconciliation obligations before selecting a mechanism.

## Backfill from a defined starting point

An initial copy needs a consistency boundary. If each table is dumped at a different time while writes continue, related rows can disagree: an order may reference a customer row that was added after its table was copied, or an inventory value may precede the order that consumed it. PostgreSQL logical replication takes a snapshot for initial table data and then applies captured changes; within one subscription, changes are applied transactionally in publisher order. That is a useful engine capability, not a universal migration guarantee.

Initial table synchronization completes table by table. A copied table can become visible on the subscriber before every table in the migration is synchronized. Do not treat one table's ready state as proof that cross-table invariants or the whole target are ready; validate the complete required set and its change position before application cutover.

PostgreSQL logical replication does not replicate schema DDL or sequence state. The [restriction documentation](https://www.postgresql.org/docs/18/logical-replication-restrictions.html) requires operators to keep compatible schemas and account for sequences separately. The [initial snapshot architecture](https://www.postgresql.org/docs/18/logical-replication-architecture.html) explains how copied rows synchronize with later changes. For dump-based paths, [pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html) can coordinate a snapshot with a replication slot or concurrent session under its documented options. Confirm exact source and target versions, object types, identity columns, large objects, extensions, triggers, ownership, privileges and DDL differences before choosing the tool.

Keep the target protected from application writes during backfill unless the replication design explicitly supports them. Otherwise the importer and application can overwrite each other, create conflicting keys or invalidate the copy's comparison. Backfill in bounded batches, record checkpoints, throttle against source and target resource budgets, and make a restarted batch safe to repeat. A cursor or offset over a changing table is not a consistent checkpoint: inserted or deleted rows can shift the next page. Use a stable key range tied to a known snapshot or the migration tool's supported checkpoint.

Deletes require capture too. A system that copies only rows still present cannot distinguish “never existed” from “was deleted after the copy began.” Change capture needs tombstones or delete records retained until the target has applied them. Similarly, updates must carry a stable identity and ordering/version so that a delayed old change cannot overwrite a newer target value.

## Reconcile semantics, not only row counts

Counts detect some gaps but can hide replacements: a missing order and an unrelated duplicate leave the same total. Compare by stable primary/business key, then verify important fields and relationships. Use deterministic partitions such as tenant or time range so teams can isolate a mismatch. Hashes can narrow large comparisons when serialization, collation, numeric precision, timezone, null and JSON canonicalization rules are consistent; a matching hash is evidence about the chosen representation, not proof of every business invariant.

This small PostgreSQL exercise demonstrates a key-level comparison without changing persistent data. Connect as an authorized ordinary database user to a disposable nonproduction database using the process from [Chapter 164](164-database-connections-and-concurrency.md). It creates two session-local temporary tables with synthetic rows only. Ubuntu, Fedora and RHEL use the same SQL with a compatible `psql` client; repository, service and authentication details remain distribution-specific.

Run the script in one `psql` session. The target intentionally has one mismatched row, one missing source row and one extra target row. The reconciliation query should identify all three keys. The second query reports no mismatches after the fixture is corrected.

```sql
SELECT current_database(), current_user, version();
CREATE TEMP TABLE source_orders (
    order_id text PRIMARY KEY,
    state text NOT NULL,
    version bigint NOT NULL
);
CREATE TEMP TABLE target_orders (
    order_id text PRIMARY KEY,
    state text NOT NULL,
    version bigint NOT NULL
);

INSERT INTO source_orders VALUES
  ('order-1', 'accepted', 10),
  ('order-2', 'pending', 11),
  ('order-3', 'completed', 12);
INSERT INTO target_orders VALUES
  ('order-1', 'accepted', 10),
  ('order-2', 'completed', 12),
  ('order-4', 'cancelled', 13);

SELECT COALESCE(s.order_id, t.order_id) AS order_id,
       s.state AS source_state, t.state AS target_state,
       s.version AS source_version, t.version AS target_version
FROM source_orders AS s
FULL OUTER JOIN target_orders AS t USING (order_id)
WHERE s.order_id IS NULL OR t.order_id IS NULL
   OR s.state IS DISTINCT FROM t.state
   OR s.version IS DISTINCT FROM t.version
ORDER BY order_id;

TRUNCATE target_orders;
INSERT INTO target_orders SELECT * FROM source_orders;
SELECT COALESCE(s.order_id, t.order_id) AS mismatched_order
FROM source_orders AS s
FULL OUTER JOIN target_orders AS t USING (order_id)
WHERE s.order_id IS NULL OR t.order_id IS NULL
   OR s.state IS DISTINCT FROM t.state
   OR s.version IS DISTINCT FROM t.version;

DROP TABLE target_orders;
DROP TABLE source_orders;
```

The first result should show `order-2`, `order-3` and `order-4`; the final query should return no rows. This fixture does not model concurrent capture, large-table load, cross-database extraction or transaction invariants. `TRUNCATE` is limited to the explicitly named temporary target in this disposable example; never adapt it by replacing the name with an application table. Real validation must also test totals and constraints such as each accepted order's notification intent, currency rounding, tenant isolation and referential integrity.

Compare source and target at the same change position, not while changes continue without a watermark. Track copied range, captured/applied position, validation result, lag and failures with bounded dimensions. Full row validation can consume substantial read, CPU and network capacity; schedule and throttle it. AWS DMS documentation is one provider example: its [validation guide](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Validating.html) describes source/target comparisons and warns that validation queries use additional resources. A migration tool's green status never substitutes for application invariants.

## Define authority, cutover and rollback before the window

A live migration commonly expands in phases. First create the target schema and permissions without removing the source contract. Deploy code that can safely coexist with the migration path. Establish a consistent baseline, then capture source changes and apply them to the target. Reconcile while the source remains authoritative. Run shadow reads against the target and compare results without returning target answers to customers until the team accepts the differences and load.

At cutover, establish a write fence. Stop or reject new writes at the old authority, drain in-flight transactions, record the final source position, wait until the target has applied through it, and run the agreed final reconciliation. Change application routing and writer identity through the owning configuration. Verify one known synthetic transaction end to end, including related notification intent and consumer state. Confirm the old source rejects writes. A DNS update, green health check or empty replication backlog alone is not proof that stale writers have stopped.

Rollback depends on whether the new authority has accepted writes. Before target writes begin, route back to the unchanged source after fencing the target. After new writes have been accepted, simply switching back discards them. The rollback plan must then include reverse change capture, an explicit reconciliation and replay procedure, or a forward repair on the new authority. If none is safe, describe the operation as a one-way cutover with a recovery plan rather than promising instant rollback.

Preserve the old system read-only or otherwise fenced for an agreed observation period, with backups and logs protected under the retention policy. Do not keep two writable authorities “just in case.” Record cutover decision, observed positions, validation evidence, outstanding mismatches, rollback threshold and responsible owners. For a failed migration, stop at the last proven boundary, keep customer writes on the declared authority and retain both sides for investigation. Correct mapping or transform defects, replay only affected keys under stable identity, and reconcile again before advancing.

## Migrate a live catalog boundary without losing changes

Summit moves catalog ownership from a shared legacy table to a new catalog service because separate teams need independent release and scaling. The target offers a source-controlled API and database. The product contract permits catalog descriptions to be briefly stale, but checkout must validate price and availability against the authoritative current source. Orders and notification intent remain in the existing transactional database.

The team first adds an outbox change record to the legacy catalog transaction. Each record includes item ID, monotonic item version, operation type, schema version and the changed data or deletion tombstone. A backfill copies a consistent item snapshot to the new service; the consumer then applies later changes idempotently and in version order. A key-level reconciliation compares source and target item versions and required fields while writes remain on the legacy authority.

The failed assumption is “the backfill finished, so the target is current.” A catalog item changed while its key range was being copied; the later backfill value overwrote version 8 with version 7 because the importer did not compare versions. The consumer dashboard showed every batch complete, but reconciliation found a lower target version. Diagnosis pauses cutover, preserves the old writer, and identifies the affected key range and change position. Recovery reloads only those keys from an agreed source version, reapplies later events in order, and repeats the comparison. The application does not silently write version 8 back from a stale target read.

For rehearsal, route a small internal cohort to shadow reads and compare canonical responses, but keep checkout price validation on the old authority. At the cutover window, fence catalog writes on the old path, wait for the final event position, reconcile, then switch the catalog read/write owner. Keep the prior endpoint blocked from mutation. If target writes begin and a defect appears, pause them and reconcile accepted target changes before returning any authority; a blind DNS rollback would lose legitimate edits.

Harbor might instead perform a short maintenance window and a controlled export/import if its dataset and outage agreement permit. Atlas could require parallel validation and a staged tenant migration because its organizational ownership is broader. The same proof obligations remain even when a managed migration service performs the copying. Choose the path based on measured data volume, allowed write pause, transformation risk, consumer compatibility and recovery capacity.

## Exercises and answer guidance

A snapshot copied all rows, but a concurrent delete was not captured. What can happen? The deleted source row can reappear at the target. Preserve tombstones or another ordered delete record until the target has applied it.

Source and target row counts match but one order ID is duplicated and another is missing. Did reconciliation pass? No. Compare stable keys and business invariants, not only counts.

The target accepted writes after cutover, then a defect is discovered. Is routing back to the old database a safe rollback? Only if those new writes are captured and reconciled back, or the team has a defined repair path. Otherwise the switch loses accepted state.

A migration tool reports low lag, but the target sequence starts at 1. What needs verification? Sequence/identity state may not be replicated; advance or reconcile it using the engine's supported method before allowing inserts, and confirm uniqueness under the write fence.

## Review questions

- Which exact transaction position or watermark joins the baseline copy to subsequent changes?
- How are deletes, ordering, duplicate changes and interrupted batches represented and recovered?
- Which application invariant would expose a migration mismatch that a row count would miss?
- What is the rollback procedure before and after the target accepts customer writes?

## Takeaways and verification

State migration is a controlled authority change, not a bulk-copy command. Start from a consistent point, preserve concurrent mutations, reconcile keyed business invariants and cut over only after the old writer is fenced. Rollback must account for writes accepted by the new authority. PostgreSQL 18 logical replication/pg_dump and AWS DMS validation documentation were checked on 2026-10-04. The SQL comparison uses temporary tables; no live migration, restore, replication task or application cutover was executed while authoring.
