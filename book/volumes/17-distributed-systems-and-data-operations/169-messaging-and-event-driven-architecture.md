---
book: The Complete DevOps Engineering Book
volume: 17
volume_title: "Distributed Systems and Data Operations"
chapter: 169
title: "Messaging and Event-driven Architecture"
slug: messaging-and-event-driven-architecture
status: complete
summary: ../../_ai/chapter-summaries/169-messaging-and-event-driven-architecture.md
---

# Chapter 169 — Messaging and Event-driven Architecture

**Section outline:** distinguish facts from requests; atomically persist business state and an outbox event; publish with at-least-once recovery; evolve schemas and preserve meaningful order; connect accepted orders to independently operated consumers.

## Events describe facts; commands request work

An event states that something happened: `OrderAccepted`, `CatalogItemChanged` or `NotificationDelivered`. A command asks an owner to do something: `SendReceipt` or `RecalculateCatalog`. Naming matters because consumers should not interpret an uncommitted intention as an accomplished fact. `OrderAccepted` belongs after the authoritative transaction succeeds. A command can still be rejected, delayed or superseded by policy.

[Chapter 97](../10-aws-production-services/097-sqs-sns-and-eventbridge.md) compares SQS work queues, SNS fanout and EventBridge routing. This chapter follows the data boundary that feeds those transports. A queue is not automatically an event log, and a router does not make a message authoritative. First decide who owns the fact, its stable identity, retention and recovery contract; then select delivery infrastructure.

[Chapter 168](168-database-scaling-and-partitioning.md) explains the database authority and scaling choices beneath the outbox. Those choices affect publisher capacity, but they do not change the requirement that source state and its publication intent share one durable transaction.

DispatchDesk must commit an order and a notification intent before returning acceptance. It should not wait for the email provider inside the database transaction, and it should not commit an order before attempting an unrelated broker send without a recovery record. A process can fail between any two operations. Separate services make that gap more visible, but even one process cannot atomically commit to two independent systems without a deliberate distributed transaction protocol.

For interoperable event metadata, [CloudEvents 1.0](https://github.com/cloudevents/spec/blob/v1.0/spec.md) defines context such as `specversion`, `id`, `source` and `type`. A format helps consumers identify and route events; it does not define DispatchDesk's business meaning, duplicate handling or schema compatibility. Stable application identifiers and documented event contracts remain necessary.

## Store accepted facts and publication intent together

The transactional outbox places the order and an event row in the same database transaction. A rollback removes both; a successful commit makes both durable under that database's contract. A separate publisher reads committed outbox rows and sends them to the broker. The publisher can be retried without losing the fact that publication was required.

This disposable PostgreSQL exercise uses temporary tables in one authorized nonproduction database session. Confirm the database and role first, following the connection approach in [Chapter 164](164-database-connections-and-concurrency.md). The SQL is the same on Ubuntu, Fedora and RHEL with a compatible PostgreSQL client; package, service and authentication setup varies by distribution. The experiment creates no persistent application tables or broker messages.

Create the temporary tables, then run the two transactions and inspect the result. The first transaction simulates a failure before commit and is rolled back. The second commits the same synthetic order and event. The stable synthetic event ID links the row to its envelope.

```sql
SELECT current_database(), current_user, version();
CREATE TEMP TABLE lab_orders (
    order_id uuid PRIMARY KEY,
    customer_ref text NOT NULL,
    item text NOT NULL
);
CREATE TEMP TABLE lab_outbox (
    event_id uuid PRIMARY KEY,
    aggregate_id uuid NOT NULL,
    aggregate_version integer NOT NULL,
    event_type text NOT NULL,
    envelope jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    published_at timestamptz
);

BEGIN;
INSERT INTO lab_orders VALUES
  ('00000000-0000-4000-8000-000000000001', 'synthetic-customer', 'book');
INSERT INTO lab_outbox
  (event_id, aggregate_id, aggregate_version, event_type, envelope)
VALUES
  ('00000000-0000-4000-8000-000000000002',
   '00000000-0000-4000-8000-000000000001', 1,
   'com.example.dispatchdesk.order.accepted.v1',
   '{"specversion":"1.0","id":"00000000-0000-4000-8000-000000000002",'
   '"source":"urn:dispatchdesk:orders",'
   '"type":"com.example.dispatchdesk.order.accepted.v1",'
   '"subject":"00000000-0000-4000-8000-000000000001",'
   '"data":{"item":"book"}}');
ROLLBACK;
SELECT (SELECT count(*) FROM lab_orders) AS orders,
       (SELECT count(*) FROM lab_outbox) AS events;

BEGIN;
INSERT INTO lab_orders VALUES
  ('00000000-0000-4000-8000-000000000001', 'synthetic-customer', 'book');
INSERT INTO lab_outbox
  (event_id, aggregate_id, aggregate_version, event_type, envelope)
VALUES
  ('00000000-0000-4000-8000-000000000002',
   '00000000-0000-4000-8000-000000000001', 1,
   'com.example.dispatchdesk.order.accepted.v1',
   '{"specversion":"1.0","id":"00000000-0000-4000-8000-000000000002",'
   '"source":"urn:dispatchdesk:orders",'
   '"type":"com.example.dispatchdesk.order.accepted.v1",'
   '"subject":"00000000-0000-4000-8000-000000000001",'
   '"data":{"item":"book"}}');
COMMIT;
SELECT o.order_id, e.event_id, e.aggregate_version,
       e.event_type, e.published_at
FROM lab_orders AS o
JOIN lab_outbox AS e ON e.aggregate_id = o.order_id;
DROP TABLE lab_outbox;
DROP TABLE lab_orders;
```

After rollback, both counts should be zero; after commit, one matching order/event pair should be visible with a null `published_at`. That is transaction evidence in this local database session, not proof of broker delivery or provider effects. A connection loss after sending to the broker but before recording `published_at` still leaves a duplicate-publication window.

## Publish outside the transaction and accept duplicates

A publisher should claim a bounded batch in a short database transaction, record an owner token and lease, then commit before contacting the broker. Never hold row locks across an unbounded network call. PostgreSQL's `FOR UPDATE SKIP LOCKED` can let several pollers claim different rows, but its [documentation](https://www.postgresql.org/docs/18/sql-select.html) warns that it intentionally presents an inconsistent view and suits queue-like access rather than ordinary queries. A claim query must select only eligible unpublished rows, use deterministic ordering and update ownership atomically.

The publisher sends each stored envelope with its existing event ID. After broker acknowledgment it conditionally marks that outbox row published using the current owner token. On a timeout with an ambiguous broker outcome, or a crash after broker acceptance but before that update, the lease eventually permits another attempt. The second send can duplicate the event; giving it a new ID would hide rather than solve the ambiguity. Keep publishing at-least-once and make consumers idempotent. This is the same effect boundary as [Chapter 162](162-retries-idempotency-and-backoff.md).

Leases bound stuck claims but do not fence a slow publisher's external send. An old process can pause, lose its lease, resume and still publish after a replacement has claimed the row. A database condition can stop the old process from overwriting local claim state, but the broker or consumer must deduplicate the stable event identity. If ordering matters per order, attach an aggregate version and serialize dispatch for that aggregate or make consumers reject/reconcile versions they cannot apply. A global publisher lock may preserve simple order at the cost of throughput and availability.

The consumer records processed event identity in the same transaction as its local database effect. A unique inbox key such as `(source, event_id)` can make a repeated delivery a no-op for that local effect. It does not make an external email call atomic with the inbox row. For the notification provider, persist a stable notification intent, use the provider's idempotency mechanism when available, and reconcile uncertain outcomes under the explicit recovery policy from [Chapter 161](161-partial-failure-and-timeouts.md).

Message retention, outbox retention and consumer-inbox retention need compatible horizons. Deleting an inbox key while a broker or operator can replay an old event reopens duplicate processing. Retain enough event metadata and payload to investigate safely, and avoid using unbounded customer content as diagnostic logs. A dead-letter event remains unresolved work with an owner, not a successfully completed business operation.

## Keep event contracts evolvable and ordering scoped

Event data is an API even when it stays inside one organization. Define the owner, source, event ID, type, schema version, occurrence time, tenant scope, privacy classification, retention and replay behavior. The event should describe the business fact needed by consumers, not expose an entire database row by convenience. Include only data consumers are authorized to receive and document whether they can fetch additional state from the source.

Prefer compatible additions such as a new optional field with a defined default. Do not change the meaning or unit of an existing field in place, silently rename a required field, or assume all consumers deploy simultaneously. If a breaking contract is necessary, publish a new event type/version, support an overlap period and observe old-consumer retirement before removing the prior form. Validate payloads at the producer and consumer boundaries; a schema registry can enforce selected structural rules but cannot guarantee business meaning or authorization.

Ordering is not automatically global. Two independent orders can be processed concurrently, while events for the same order may require a sequence. Use an aggregate version or sequence generated with the state transition. Broker partition/group keys can preserve ordering within a documented scope, often at the cost of serializing that key. Consumer concurrency, retries and dead-letter handling can still alter the order in which side effects become visible. If a consumer receives version 4 before version 3, it needs a policy: wait, buffer within a bound, reload authoritative state or reject for reconciliation.

Replay is a deliberate re-execution of an event contract. A new analytics consumer may safely rebuild derived data from retained events; an email consumer can send a second notification unless it recognizes prior work. Record replay scope and identity, preserve original event IDs when replaying the same fact, and assign a new event ID only when creating a genuinely new fact. Keep consumer-specific effect policy visible.

## Connect acceptance to notification delivery

The DispatchDesk API validates and authorizes the request, then commits order, notification intent and `OrderAccepted` outbox event together. It returns the order identity only after commit. The publisher forwards committed events. Analytics and audit consumers each have independent delivery state; the notification consumer resolves the already committed receipt intent by its stable order/event identity and uses that durable intent when calling its provider outside the order transaction.

The failed assumption is “the broker accepted the event, so the customer received the notification.” Broker acknowledgment establishes only the broker boundary. A consumer may be unavailable, a message may be delayed or duplicated, the provider may throttle, or the provider may have accepted a request whose response was lost. Diagnose each stage with stable order/event/intent identities, event age, outbox age, consumer lag, duplicate suppression, provider outcome and dead-letter counts. Do not label a publish metric as delivery success.

Recovery repairs the stage that owns the gap. If outbox age is growing, restore publisher capacity and check database claims without clearing unpublished rows. If one consumer is behind, correct that consumer or route and replay at a bounded rate. If provider outcome is uncertain, reconcile by the durable intent identity before sending again. Compare committed accepted orders against pending, completed and explicitly terminal notification intents. An empty queue alone does not prove that every order reached the promised state.

For Harbor, one database outbox table and a bounded worker may meet the workload with a small operating surface. Summit can publish to a managed queue and scale independent consumers, while still owning identities, schema and reconciliation. Atlas may use a shared event platform when multiple teams need governed routing and retention; platform ownership does not remove each consumer's delivery contract. Choose complexity only when independent scale, fanout, retention or ownership requirements justify it.

## Exercises and answer guidance

The order transaction commits, but the process crashes before sending an event. What recovers publication? The committed outbox row remains and a publisher can claim it later; sending directly after commit with no durable intent would leave a gap.

The broker accepted an event, but the publisher timed out before marking the row published. What should the retry do? Reuse the stable event identity and accept possible duplicate delivery; the consumer must deduplicate its local effect or reconcile an external one.

A consumer requires a newly added event field while older producers do not send it. Is this a safe additive change? Not for that consumer without a defined default or coordinated version transition. Compatibility is a producer-consumer contract, not a label on a schema edit.

A queue preserves per-key ordering, but two workers call an email provider concurrently for one order. Is visible side-effect order guaranteed? Not by broker delivery alone. Serialize the relevant consumer effect or enforce aggregate-version/idempotency rules at the effect boundary.

## Review questions

- Which durable write makes publication recoverable if a process dies immediately after accepting an order?
- At what two points can a publisher or consumer repeat an effect, and which stable identity supports recovery?
- What data and behavior belong in an event contract, and which changes require a new version?
- Which business operations require per-aggregate ordering, and what concurrency cost does that impose?

## Takeaways and verification

Messaging separates timing and ownership, but it does not remove partial failure. Commit publication intent with source state, publish outside the transaction, preserve stable identity across retries and give each consumer a compatible schema and recovery policy. PostgreSQL 18 transaction/`SKIP LOCKED` documentation, SQS standard delivery semantics and CloudEvents 1.0 were checked on 2026-10-04. The SQL lab is inline and temporary; no PostgreSQL connection, broker, consumer, provider, replay or cloud configuration was executed while authoring.
