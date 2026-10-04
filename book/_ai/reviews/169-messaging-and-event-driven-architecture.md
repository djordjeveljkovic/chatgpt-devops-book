# Independent review — Chapter 169

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: e35ac51c40029a760f59eac18e474615d9b2bbcaa202ca24ed5d49ca0e0bb823

## Scope and findings

Read complete current body, compact summary, Chapter 169 brief and authoring guide, with relevant Chapters 161/162/164/168 context. Reviewed PostgreSQL outbox SQL and cleanup, event identity/CloudEvents envelope, publisher lease and duplicate windows, inbox and provider effects, ordering/schema/replay, recovery and company-path reasoning, prerequisites/Linux differences, exercises/questions/takeaways and links. No material technical finding; approved.

The temporary-table lab correctly separates table creation from its two demonstration transactions: rollback removes both inserted rows, the second commit retains one matching order/outbox pair for inspection, and DROP removes the session-local tables. UUID, JSONB, timestamp defaults, adjacent string literals separated by newlines and join syntax are valid PostgreSQL syntax. Both copies use the same stable event identity and valid required CloudEvents metadata; source/event identity is later used jointly for the inbox key. This is a single-session local atomicity exercise, not a persistent production outbox or evidence of successful broker delivery. Fixed synthetic IDs are appropriate to the disposable example and are not a production ID-generation recipe.

Publisher claims are short atomic database operations separated from external calls. SKIP LOCKED is appropriately restricted to queue-like access, eligible unpublished rows and atomic ownership assignment. Broker acceptance before local completion and expiry/slow-old-owner send are distinct duplicate windows. The lease does not promise to fence an external send, and stable identity is preserved on retry. Owner conditions protect local completion; consumer/effect authority must still handle duplicates.

Local inbox uniqueness and the consumer effect share a transaction, while provider calls are explicitly outside that atomicity boundary. Persisted intent, provider idempotency and uncertain-result reconciliation are required. Retention horizons include manual replay, and dead-lettering remains unresolved business work. Event schema rules are producer-consumer contracts; aggregate sequence, transport order and externally visible effect order are not conflated. Replay preserves identity for the same fact and does not promise safe repeat email delivery. DispatchDesk acceptance-to-publication-to-provider observations and stage-specific recovery satisfy the brief; no publish metric is mislabeled delivery completion.

Low optional observations:

- Opening/context references: add the brief's prerequisite Chapter 168 as an actual relative link (for source ownership/sharding context). Relevant Chapters 97/161/162/164 are already linked, so this is a navigation refinement rather than missing technical setup.
- Connect acceptance to notification delivery, first paragraph: specify that the notification consumer resolves/reuses the API's already committed notification intent by stable identity. The chapter commits intent at acceptance and later maps the event to durable receipt intent; explicitly naming reuse prevents a reader mistaking those descriptions for two independent receipt intents. Existing stable-identity/idempotency guidance supports the correct interpretation.

## Primary evidence checked 2026-10-04

- [PostgreSQL 18 transactions](https://www.postgresql.org/docs/18/tutorial-transactions.html): all-or-nothing commit/rollback boundaries.
- [PostgreSQL 18 SELECT](https://www.postgresql.org/docs/18/sql-select.html): row locking and SKIP LOCKED inconsistent-view/queue-use limitations.
- [CloudEvents 1.0 specification](https://github.com/cloudevents/spec/blob/v1.0/spec.md): required context fields and source-scoped event identity. The pinned specification version is explicit; no newest-version claim is made.
- [SQS standard at-least-once delivery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html): possible repeated delivery and need for idempotent handling. No universal exactly-once provider-effect claim is made.

## Validation and limits

`python3 tools/check_book.py --chapters 169-169` passed 1,459 global local links without warnings/errors. It reported no SQL syntax/parser check. SQL and transaction/control-flow semantics independently inspected statically. Exact stripped-front-matter hash calculated with `tools.promote_reviewed.body_hash`. No PostgreSQL session, concurrent publisher, broker send/receive, inbox transaction, external provider call, replay, lease-expiry test or cloud configuration executed. No runtime/OS/server matrix tested. Static SQL and primary docs cannot establish production claim fairness, aggregate sequencing, provider idempotency retention or end-to-end delivery outcomes. Summary accurately records actual topics and nonexecution limits. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed both changed passages against the original complete assessment. Both optional observations are resolved. Chapter 168 is linked to the existing prerequisite file and its authority/scaling context is accurate. The final example now explicitly resolves the already committed receipt intent using stable order/event identity and uses that intent for the external provider call, preserving the authoritative order-plus-intent transaction taught in earlier chapters. It does not create an independent duplicate notification intent. No material issue introduced; earlier technical assessment and runtime/source limits remain applicable.

Fresh body SHA256 from `tools.promote_reviewed.body_hash`: e35ac51c40029a760f59eac18e474615d9b2bbcaa202ca24ed5d49ca0e0bb823. `python3 tools/check_book.py --chapters 169-169` passed 1,460 global local links without warnings/errors; no SQL parser or runtime execution claimed. Only this separate review record updated.

Verdict: approved
