# Chapter 136 continuation

Status: complete

## Written material

Expand/migrate/switch/contract sequence for an email-column rename; correct dual-writer/backfill ordering and source-of-truth transition; PostgreSQL-specific bounded `UPDATE` batch; engine-specific DDL, locks, index and backfill effects; message field/schema versioning, compatibility directions and business-semantic limits; old producer/worker overlap, retries, DLQ/replay and idempotency; DispatchDesk migration incident; exercises, answer guidance, review questions and takeaways.

## Concepts and terminology

Expand-and-contract, canonical field, transitional dual-writer, idempotent backfill, lock budget, backward/forward/transitive compatibility, event version, replay window, contract phase, recovery point of no return.

## Examples and cross-references

DispatchDesk `contact_email` to `notification_email` migration, PostgreSQL SQL illustration, and `order.created` JSON event evolution. Relative links to Chapters 134, 135, and 163; primary PostgreSQL 18 and Confluent schema-evolution docs.

## Open threads

Independent reviewer approved the final body hash after clarifying backward/forward/full/transitive schema compatibility and limiting old-column rollback eligibility once new-only writes begin. No database/DDL/backfill, queue, schema registry, consumer, restore, or migration was executed.

## Exact next section

None. Independently approved; continue to the next unfinished chapter.

## Verification

PostgreSQL 18 `ALTER TABLE`, `UPDATE`, and `CREATE INDEX` docs and current Confluent schema-evolution docs checked 2026-10-04. `python3 tools/check_book.py --chapters 136-136` passed one JSON parse and 1,425 global local links; no errors/warnings. `git diff --check` passed. Static checks do not test SQL execution or data compatibility.
