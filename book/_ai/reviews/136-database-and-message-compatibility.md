# Independent review — Chapter 136

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: b1514fa2159126240a4d0202d728948ff5204d7779dde20c23488f69360d4987

## Inspection scope and findings

Read complete body/summary, Chapter136 brief and authoring guide, with reviewed Chapters134–135 compatibility context. Checked dual-write authority, race ordering, bounded SQL, PostgreSQL version/locking, message directions, replay and rollback. No material technical finding.

Old field stays canonical while old-only writers exist; transitional writer reads old and transactionally writes both, old writers retire before backfill/catch-up, then reader switch preserves dual writes through its valid rollback window. This prevents stale-new-field authority. SQL selects unique fictional primary-key IDs, null-aware mismatches, ordered LIMIT500 with FOR UPDATE SKIP LOCKED and updates source row values in the same statement. PostgreSQL18 permits this CTE/update shape. Locks and transactional dual-write assumptions protect row updates; final non-skipping catch-up and invariant validation are appropriately required. Batch is explicitly not a complete runner.

PostgreSQL DDL lock qualifications and CREATE INDEX CONCURRENTLY write/transaction limitations are correct and not generalized to other engines. No OS-specific package or runtime operation occurs. Message optionality is qualified by decoder behavior; consumer-first evolution and absent-field fallback, business semantics, delayed/DLQ/archive sources, retry/idempotency/ordering and side-effect-aware re-drive are sound. Snapshot/PITR and contract point-of-no-return limits are explicit. Practical assessment and takeaways satisfy the brief. Compared with134: this provides canonical migration detail and does not repeat its traffic-strategy procedure.

Low — Backfills and mixed-version messages, compatibility paragraph: define directions directly (backward: new consumer reads old data; forward: old consumer reads new data; full: both), rather than only saying they differ. Summary lists transitive compatibility though body does not explain it; add a concise explanation or narrow terminology inventory.

Low — phase table Stop old writes: “both columns remain for rollback window” can suggest old-field-reading transitional code remains a valid rollback after new-only writes begin. Gate correctly says no old reader/rollback candidate remains; clarify it is then a new-field-compatible rollback window and old-only/transitional rollback eligibility ends before stopping old writes. Surrounding dependency gate and point-of-no-return reasoning already prevent this being a material procedural error.

## Primary evidence checked 2026-10-04

- [PostgreSQL18 UPDATE](https://www.postgresql.org/docs/18/sql-update.html): WITH/FROM update, batch locking and final no-skip pass, large-update impact.
- [PostgreSQL18 ALTER TABLE](https://www.postgresql.org/docs/18/sql-altertable.html): operation-dependent strong locks/rewrite qualifications.
- [PostgreSQL18 CREATE INDEX](https://www.postgresql.org/docs/18/sql-createindex.html): normal write blocking versus concurrent build and no transaction block.
- [Confluent schema evolution](https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html): directional/transitive modes and format/field definition conditions.

## Validation and limits

`python3 tools/check_book.py --chapters 136-136` passed: one JSON parse and1,425 global local links; no errors/warnings. Hash computed with tools.promote_reviewed.body_hash matches supplied value. No PostgreSQL SQL parser/server or migration run, EXPLAIN, lock contention, backfill concurrency, schema-registry validation, consumer compatibility, queue replay/idempotency or restore performed. No database-version/managed-engine/OS matrix tested. SQL reviewed against official18 documentation only; static JSON and sources cannot establish real data consistency, production lock budget or recoverability. Only this separate review record written.

## Final bounded refresh — 2026-10-04

Reviewed compatibility definitions and revised stop-old-writes gate against prior optional notes. Backward/new-reader old-data, forward/old-reader new-data and full/both direction descriptions are correct; transitive checks extend the chosen direction across earlier schemas. New-only writes now explicitly require removing old-field-only rollback candidates, leaving only new-field-compatible releases eligible. Both optional findings resolved; no remaining material finding. Hash recomputed and matchesb1514fa2159126240a4d0202d728948ff5204d7779dde20c23488f69360d4987. Focused checker passed, prior source evidence and SQL/runtime limits retained. Only this separate record changed.

Verdict: approved
