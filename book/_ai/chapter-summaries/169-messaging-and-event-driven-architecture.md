# Chapter 169 continuation

Status: complete

## Written material
Event facts versus commands; atomic source/outbox transaction; at-least-once publisher and consumer recovery; schema evolution, scoped ordering and replay; DispatchDesk order-to-notification path.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Transactional outbox/inbox; stable event identity; aggregate version; compatible schema evolution; per-key ordering; replay and consumer effect boundary.

## Examples and cross-references
DispatchDesk acceptance/outbox SQL using temporary tables; fictional Harbor/Summit/Atlas deployment choices; prerequisite references to Chapters 161, 162, 164 and 97. No service operation was executed.

## Open threads
Independent review findings and revisions remain before promotion.

## Verification
PostgreSQL 18 SELECT/transaction behavior, AWS SQS standard at-least-once semantics and CloudEvents 1.0 primary specification checked on 2026-10-04. Focused syntax/link validation pending independent review; no database, broker, consumer or provider runtime was executed.
