# Independent review — Chapter 170

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 0d1f7db024044144a556aabc1b5037f79ba156b7a487444965b192d25b674f84

## Scope and findings

Read complete current manuscript/summary, Chapter 170 brief and authoring-guide requirements, with relevant Chapters 164/165/168/169 prerequisite context. Inspected snapshot/CDC/delete ordering, PostgreSQL scope, keyed reconciliation SQL, write fencing/cutover and post-target-write rollback, catalog regression recovery, AWS DMS claims, practical assessment material and links. No material technical finding; chapter fulfills the brief and is approved.

The reconciliation SQL uses primary-keyed temporary relations and a FULL OUTER JOIN with COALESCE and null-safe IS DISTINCT FROM comparisons. Its first query finds precisely order-2 (field/version mismatch), order-3 (missing target) and order-4 (extra target); after copying the source fixture, no mismatch remains. TRUNCATE and DROP are limited explicitly to synthetic session-local relations, with authorized nonproduction database/role confirmation. No production extraction or concurrent comparison is falsely demonstrated. Canonical hashes, watermark equality and business invariants are appropriately separate; matching counts do not prove keyed equivalence.

Snapshot and captured changes must share a defined position, and key-range checkpoints must refer to that snapshot. Tombstones/delete records and monotonic identity/version prevent missing deletion and regressive overwrites. PostgreSQL logical replication is scoped to its own table synchronization and ordered transactional apply; schema DDL and sequence state are correctly excluded, with object/version/trigger/identity compatibility assigned to the actual migration plan. pg_dump snapshot coordination is described as a documented option, not automatic CDC creation. No blanket cross-engine or initial-table readiness guarantee is claimed.

Target writes remain blocked during copy. Cutover fences the old writer, drains transactions, records/applies final position and reconciles before authority routing. DNS/health/empty backlog are correctly insufficient to fence writers. Once target writes are accepted, rollback requires their capture/reconciliation or forward repair; the old source is not silently reopened as an independent writable authority. The failure example identifies version 7 overwriting 8 and pauses cutover while preserving the source, then reloads affected keys from an agreed version and reapplies subsequent changes. That is a concrete recovery procedure, not a green-dashboard success claim.

AWS DMS validation is limited to its source/target comparison and additional resource cost; it is not presented as universal cross-engine invariant proof. Sequence recovery, privacy, backlog throttling, synthetic transaction acceptance, consumer compatibility, and retention evidence remain visible. Outline, prerequisite links, exercises with guidance, review questions and takeaways are complete. SQL is portable across the named distributions given a compatible PostgreSQL client; connection setup points to Chapter 164.

Low optional observations:

- Backfill from a defined starting point, PostgreSQL initial synchronization paragraph: add that initial table-sync workers can expose individually copied tables before all subscribed tables reach their synchronized state. The existing final-position/reconciliation gate prevents premature authority, but the reminder would make the engine boundary especially clear.
- Compact summary, Written material: name Summit rather than DispatchDesk for the specific catalog version-regression scenario, consistent with its Examples section and the body.

## Primary evidence checked 2026-10-04

- [PostgreSQL 18 logical replication architecture](https://www.postgresql.org/docs/18/logical-replication-architecture.html): individual table snapshot/synchronization workers and ordered transactional change application.
- [PostgreSQL 18 logical replication restrictions](https://www.postgresql.org/docs/18/logical-replication-restrictions.html): DDL/sequence exclusions, large objects, supported relation types and replica identity constraints.
- [PostgreSQL 18 pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html): consistent export, snapshot coordination and single-database scope. No pg_dump execution claimed.
- [AWS DMS validation](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Validating.html): source/target row validation, selected endpoint/task limitations and added query/resource load; these do not establish business-invariant correctness.

## Validation and limits

`python3 tools/check_book.py --chapters 170-170` passed 1,464 global local links without warnings/errors. It reported no SQL parser/runtime validation. SQL syntax, fixture results and transaction/authority reasoning independently inspected statically. Exact stripped-front-matter hash calculated using `tools.promote_reviewed.body_hash`. No PostgreSQL session, pg_dump/export, logical replication, AWS DMS task, live migration, restore, cutover, target-write rollback or cross-engine transform executed. No client/server/distribution matrix tested. Primary documentation and synthetic SQL cannot prove production CDC completeness, snapshot/watermark coordination, write fencing, performance or recovery objectives. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Both optional observations resolved. Inspected the new initial-table synchronization paragraph against the primary PostgreSQL architecture documentation already reviewed: an individual copied table can be visible before all required tables are synchronized, and readiness/cutover therefore requires the complete invariant set and change position. This accurately qualifies the engine boundary without changing the earlier writer-fencing and post-target-write rollback requirements. The summary now names Summit consistently in both its written material and examples. No material issue introduced; approval remains.

Fresh body SHA256 computed with `tools.promote_reviewed.body_hash`: 0d1f7db024044144a556aabc1b5037f79ba156b7a487444965b192d25b674f84. `python3 tools/check_book.py --chapters 170-170` again passed 1,464 global local links without warnings/errors. Earlier complete assessment, primary evidence and SQL/runtime/migration nonexecution limits remain applicable. Only this separate review record updated.

Verdict: approved
