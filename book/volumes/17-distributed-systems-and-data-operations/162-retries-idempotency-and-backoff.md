---
book: The Complete DevOps Engineering Book
volume: 17
volume_title: "Distributed Systems and Data Operations"
chapter: 162
title: "Retries, Idempotency and Backoff"
slug: retries-idempotency-and-backoff
status: draft
summary: ../../_ai/chapter-summaries/162-retries-idempotency-and-backoff.md
---

# Chapter 162 — Retries, Idempotency and Backoff

## A retry is another attempt, not a reversal

After [an uncertain response](161-partial-failure-and-timeouts.md), retrying can recover a result or duplicate an effect. The difference comes from the operation's contract. A GET commonly retrieves state without requesting a new business mutation. A POST may create a new order on every attempt unless the application supplies a durable idempotency mechanism. HTTP method semantics in [RFC9110](https://datatracker.ietf.org/doc/html/rfc9110#section-9.2.2) do not make an arbitrary custom POST safe to repeat.

Idempotency means repeated application of an operation has the intended same effect within its defined scope. It does not require identical timing, logs or every response header. DispatchDesk's acceptance contract should return the original order result for equivalent retries with the same authorized caller and key. Reusing that key for a different order meaning should be a conflict. A retry with a new key is a new operation, so a client that generates a fresh key after every timeout defeats the protection.

Define the key scope, payload comparison, retention period and result lookup before implementation. A key may be unique per tenant and operation. It is not authentication; another tenant must not retrieve an order simply by knowing its key. A hash of the request alone can collapse two intentionally separate identical orders, so it is not automatically an appropriate operation identity. A random caller-generated key, retained across retries of one intended operation, expresses that distinction.

## Atomically preserve order, intent and result

A naive implementation checks whether a key exists, creates an order, then stores the result. Two API replicas can pass the check simultaneously. A process can also crash after creating the order but before recording the key. The database transaction and uniqueness boundary must cover the durable acceptance result together with the order and notification intent.

The following complete local mechanics lab uses SQLite to demonstrate that boundary. It does not provide a production HTTP server, authentication, a provider worker, database failover or a backup plan. Save it as `idempotent_accept.py` in a new disposable directory and run `python3 idempotent_accept.py` as an ordinary user on Ubuntu, Fedora or RHEL with Python3 and its SQLite module. It creates `accept-lab.sqlite`, starts four concurrent local callers and verifies one order and intent. It sends no notifications and makes no cloud calls.

```python
import json
import sqlite3
import uuid
from concurrent.futures import ThreadPoolExecutor

DB = "accept-lab.sqlite"

def connect():
    db = sqlite3.connect(DB, timeout=5.0, isolation_level=None)
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA synchronous=FULL")
    return db

def initialize():
    db = connect()
    try:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            tenant TEXT NOT NULL,
            operation_key TEXT NOT NULL,
            canonical_payload TEXT NOT NULL,
            UNIQUE(tenant, operation_key)
        );
        CREATE TABLE IF NOT EXISTS notification_intents (
            order_id TEXT PRIMARY KEY REFERENCES orders(order_id),
            state TEXT NOT NULL CHECK(state IN ('pending', 'completed'))
        );
        """)
    finally:
        db.close()

def accept(tenant, key, payload):
    if not isinstance(tenant, str) or not tenant or len(tenant) > 100:
        raise ValueError("tenant required")
    if not isinstance(key, str) or not key or len(key) > 200:
        raise ValueError("bounded operation key required")
    if not isinstance(payload, dict) or set(payload) != {"item"}:
        raise ValueError("this lab accepts only an item field")
    if not isinstance(payload["item"], str) or not payload["item"]:
        raise ValueError("nonempty item required")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    if len(canonical.encode()) > 64 * 1024:
        raise ValueError("payload too large")
    db = connect()
    try:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT order_id, canonical_payload FROM orders "
            "WHERE tenant=? AND operation_key=?", (tenant, key)).fetchone()
        if row is not None:
            if row[1] != canonical:
                raise ValueError("key conflicts with a different payload")
            order_id = row[0]
        else:
            order_id = str(uuid.uuid4())
            db.execute("INSERT INTO orders VALUES (?, ?, ?, ?)",
                       (order_id, tenant, key, canonical))
            db.execute("INSERT INTO notification_intents VALUES (?, 'pending')",
                       (order_id,))
        db.execute("COMMIT")
        return {"order_id": order_id, "accepted": True}
    except Exception:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    initialize()
    key = "lab-" + uuid.uuid4().hex
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: accept("harbor", key, {"item": "book"}),
                                range(4)))
    assert len({result["order_id"] for result in results}) == 1
    try:
        accept("harbor", key, {"item": "different-book"})
    except ValueError as error:
        print("conflicting reuse rejected:", error)
    else:
        raise AssertionError("conflicting key was accepted")
    db = connect()
    try:
        orders = db.execute("SELECT count(*) FROM orders WHERE operation_key=?",
                            (key,)).fetchone()[0]
        intents = db.execute("SELECT count(*) FROM notification_intents "
                             "WHERE order_id=?",
                             (results[0]["order_id"],)).fetchone()[0]
        assert (orders, intents) == (1, 1)
        print("same-key attempts share one order and one pending intent")
    finally:
        db.close()
```

`BEGIN IMMEDIATE` acquires SQLite's write-transaction authority before the check, so these local callers serialize at that boundary. The unique constraint is an additional invariant. [SQLite transaction documentation](https://www.sqlite.org/lang_transaction.html) describes the single-writer model; a production PostgreSQL implementation needs its own concurrency handling rather than a verbatim SQLite transaction statement. The result is returned only after commit. A failed intent insertion rolls back the order insertion, preserving the paired acceptance contract.

The canonical JSON comparison is deliberately limited to a single validated string field. A production API must define semantic normalization, schema evolution and which fields participate. Treating arbitrary floating-point JSON, ignored fields or different encodings as equivalent needs more thought. The lab returns the original identity, not a fresh order for a duplicate. It scopes keys by tenant but assumes the caller's tenant has already been authenticated outside this function.

The synchronous setting is an explicit SQLite storage assumption documented in [PRAGMA guidance](https://www.sqlite.org/pragma.html#pragma_synchronous); it is not a backup or proof against host loss, faulty storage or corruption. Keep the database on a supported local storage path for this lab, not an improvised shared network filesystem. SQLite's conflict behavior also differs by option: [REPLACE can remove a preexisting row](https://www.sqlite.org/lang_conflict.html), so it is a poor substitute for retrieving the original order result.

Rerunning the program uses a new synthetic key and creates another legitimate lab order, while each run's four attempts share one result. Inspect that distinction before cleanup. After all callers exit, remove only this disposable script and database when no longer needed. This does not delete production records.

## Retention defines how long a duplicate can be recognized

An idempotency record cannot be discarded arbitrarily while a client or queue may still retry. Choose a retention window that covers the documented retry and reconciliation horizon, and define behavior after it expires. If records expire after one day but an offline client can resend an old order a week later, duplicates become possible unless another durable identity prevents them.

Retaining every raw request forever increases storage and privacy obligations. Store only the result and comparison material required by the contract, under appropriate access and retention. A cryptographic payload hash can reduce stored comparison bytes but does not replace careful canonicalization or permit public access to results. Record the relevant schema and comparison version when future changes could alter meaning.

External notification idempotency is a separate boundary. Local order idempotency prevents duplicate order acceptance; it does not prove a provider will suppress repeated sends. Use the stable notification operation identity with the provider's supported mechanism and verify its scope/window. When provider outcomes remain ambiguous beyond that window, reconciliation or a deliberate product policy is required.

## Classify retries and bound their cost

Some failures are unlikely to improve through immediate repetition: invalid payload, authorization denial, unsupported operation or an idempotency conflict. Repairing the input or authority is different from retrying the same call. Transient network failures, throttling and selected dependency errors can merit retries within a deadline. Respect documented service hints such as a retry-after interval where applicable. Never retry every exception indiscriminately.

Use a maximum attempt count, an elapsed deadline and a service-wide concurrency or retry budget. Backoff reduces repeated pressure; jitter prevents many callers from waking simultaneously. A common full-jitter model samples a delay between zero and a capped exponentially growing interval. It is a policy, not proof that the dependency will recover. A provider's rate limit still applies to original and retried work together.

This complete local delay planner shows the calculation without making requests or sleeping. Save as `retry_plan.py` and run `python3 retry_plan.py`. It requires only Python3 and works identically on the three Linux families.

```python
import random

rng = random.Random(7)  # Repeatable teaching sequence; not a production seed.
base_seconds = 0.2
cap_seconds = 3.0
remaining_deadline = 5.0
max_retries = 4
for retry_index in range(max_retries):
    upper = min(cap_seconds, base_seconds * (2 ** retry_index))
    delay = rng.uniform(0.0, upper)
    if delay >= remaining_deadline:
        print("stop: no budget remains for another delay and attempt")
        break
    remaining_deadline -= delay
    print(f"retry {retry_index + 1}: planned delay={delay:.3f}s; "
          f"budget before actual attempt={remaining_deadline:.3f}s")
print("Real attempt duration must also be subtracted from the same deadline.")
```

A real implementation recalculates remaining monotonic time before each sleep and attempt, reserves time for meaningful work, and interrupts waiting on shutdown. The example's fixed seed is only for a repeatable lab; using the same seed in all production processes can synchronize their supposedly randomized retries. The planner deliberately omits actual attempt time, which the final line exposes rather than pretending to validate a real retry deadline.

## A worker retry contract for all three companies

For Harbor, a database-backed worker can keep pending intent, attempt count, next-eligible time, temporary ownership and sanitized failure classification. For Summit, SQS provides delivery and visibility mechanisms while the database and provider contract preserve business identity. [SQS standard-queue documentation](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html) explicitly requires tolerance of repeated delivery. Atlas may use a broker selected by its platform, but a pod restart does not eliminate duplicate effects.

On receipt, acquire bounded ownership, confirm whether the notification is already completed, execute an eligible provider attempt with stable identity and deadline, persist the outcome, then acknowledge delivery. A crash between outcome persistence and acknowledgment causes redelivery; the completed-state check should suppress another send. A crash between provider effect and local persistence remains uncertain and needs provider idempotency or reconciliation. State these two windows separately.

Poison messages require a terminal or quarantined state with an owner, diagnostic reason and replay procedure. Infinite retrying of an invalid address consumes capacity and hides legitimate delay. Replay should preserve the original business identity unless a reviewed correction deliberately creates a new operation. Do not erase attempt history to make a retry appear fresh.

## Diagnose a retry storm

An incident might show original order arrival steady at ten per second while database attempts rise to sixty and successful acceptance falls. Compare original operations, total attempts, rejection classes and per-layer policies. If all clients retry synchronously after a short timeout, a slow dependency can become saturated by recovery traffic. A CPU chart alone can miss connection and lock pressure.

Recovery can reduce retry concurrency, raise an unrealistically short timeout within the product deadline, disable redundant retry layers and apply bounded admission. Preserve original keys so recovery does not create new orders. Resume gradually while tracking completion and unresolved age. A larger replica count that multiplies every retry pool can worsen the storm.

## Exercises and answer guidance

Four replicas check for a missing key before inserting outside a transaction. Why can duplicate orders result? Their checks race and no atomic authoritative result binds creation to the key. Use transactional uniqueness and retrieve the winning equivalent result.

A client generates a new idempotency key after timeout. What changed? It declared another operation; the original key's protection cannot match it. Retain the original identity across attempts of one intent.

A worker has persisted completion but crashes before acknowledgment. What should redelivery do? Observe the durable completed state and acknowledge without repeating the external effect. The earlier provider-effect-before-persistence window needs a different control.

## Takeaways and verification

Retries consume real capacity and can duplicate real effects. Bind equivalent attempts to a durable scoped result, reject conflicting reuse, preserve stable external identities and bound backoff by the operation deadline. SQLite, SQS and HTTP primary documentation was inspected on2026-10-01. The complete acceptance lab was executed under Python3.14.7 in a temporary local directory: four concurrent same-key callers returned one order identity, conflicting payload reuse was rejected, and the database contained one order and one pending intent for that key. The process exited successfully. This tests local SQLite concurrency only; no power-loss durability, host recovery, provider delivery, distributed database failover or queue integration was exercised.

