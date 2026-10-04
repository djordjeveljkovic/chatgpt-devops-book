---
book: The Complete DevOps Engineering Book
volume: 17
volume_title: "Distributed Systems and Data Operations"
chapter: 163
title: "Queues and Backpressure"
slug: queues-and-backpressure
status: complete
summary: ../../_ai/chapter-summaries/163-queues-and-backpressure.md
---

# Chapter 163 — Queues and Backpressure

**Section outline:** distinguish arrival from completion; apply backpressure at real capacity boundaries; use leases and acknowledgments safely; recover growing and dead-letter backlogs with bounded replay.

## A queue separates arrival from completion

DispatchDesk can record notification intent durably while a provider is unavailable, then let workers deliver it later. That separation protects order acknowledgment from the provider's response time, provided acknowledgment occurs only after the order and intent commit. The queue does not create unlimited capacity. It stores a difference between incoming work and completed work, and the oldest item's waiting time remains a customer outcome.

[Retry and idempotency](162-retries-idempotency-and-backoff.md) established stable operation identity and duplicate-effect handling. A queue adds delivery and temporary ownership, not a guarantee that every external operation happens once. Producers, storage, consumers and providers can fail independently. Decide which system owns accepted work and how to reconcile an intent that exists in the database but has not reached a broker.

The backlog change over an interval is approximately arrivals minus completions, with adjustments for cancellation, quarantine and redelivery accounting. At fifty arrivals per second and thirty-five completions per second, an initially empty backlog grows by 900 jobs per minute. If a later recovery supplies seventy completions per second while arrivals remain fifty, a 9,000-job backlog takes roughly 450 seconds to drain under stable assumptions. Adding workers is useful only if provider limits, database work and CPU permit that completion rate.

Age and depth answer different questions. Depth helps estimate remaining work; oldest age exposes a deadline breach. A small queue containing one permanently failing old notification can have severe customer impact. A large freshly enqueued campaign batch can be within its agreed delivery window. Approximate broker metrics and movement between queues can further change what an “oldest” number represents.

## Backpressure protects the next boundary

Backpressure means the receiving boundary limits work according to its capacity, and producers respond to that limit. It can take the form of a bounded in-memory channel, a maximum in-flight consumer count, database pool limits, a provider rate limiter or admission rejection. Moving work into another unbounded buffer is not backpressure; it postpones the visible failure until memory or storage runs out.

A worker should not receive thousands of jobs and then wait for a ten-slot provider pool. Its leases can expire while jobs wait locally, enabling duplicate processing elsewhere. Fetch only the amount the consumer can process or retain safely under the lease policy. Include retrying work in the same concurrency budget. A separate retry pool with no aggregate cap defeats the bound.

Producer behavior must also be explicit. If the order transaction cannot durably store an intent because storage is unavailable or full, the API must not return accepted. If a separate broker is temporarily unavailable while intent is safely stored in the transactional outbox, publication can recover later. Those are different acceptance paths. The [event-driven chapter](169-messaging-and-event-driven-architecture.md) supplies the outbox boundary in detail.

For Harbor, a database-backed work table can be sufficient at its measured scale. Summit can use SQS delivery with managed operations while retaining business identity and reconciliation state. Atlas may use a platform broker when ordering, throughput and governance justify it. Broker sophistication is not the same as correctness of the order-to-notification contract.

## Leases provide temporary ownership

A lease says that a worker owns an item until a defined deadline under the authority's clock. It must identify the owning attempt, not merely the worker name. If an old worker resumes after expiry and another worker has acquired the item, the old attempt should not be allowed to overwrite the newer local state. A conditional update using the current ownership token can enforce that rule for the database state.

The following complete local lab demonstrates expired ownership and bounded failure attempts. It uses a logical clock passed as an integer, so no wall-clock sleeping is necessary. It records synthetic jobs in `queue-lab.sqlite` and performs no external effects. Save it as `lease_lab.py` and run `python3 lease_lab.py` in a new disposable directory as an ordinary user with Python 3 and SQLite on Ubuntu, Fedora or RHEL.

```python
import sqlite3
import uuid

DB = "queue-lab.sqlite"

def open_db():
    return sqlite3.connect(DB, timeout=2.0, isolation_level=None)

def initialize():
    db = open_db()
    try:
        db.execute("""CREATE TABLE IF NOT EXISTS jobs (
          id TEXT PRIMARY KEY, payload TEXT NOT NULL, state TEXT NOT NULL,
          attempts INTEGER NOT NULL, eligible INTEGER NOT NULL,
          owner TEXT, lease_until INTEGER
        )""")
    finally:
        db.close()

def enqueue(payload):
    job = uuid.uuid4().hex
    db = open_db()
    try:
        db.execute("INSERT INTO jobs VALUES (?, ?, 'pending', 0, 0, NULL, NULL)",
                   (job, payload))
        return job
    finally:
        db.close()

def claim(now):
    db = open_db()
    try:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("""SELECT id, payload, attempts FROM jobs
          WHERE (state='pending' AND eligible<=?)
             OR (state='leased' AND lease_until<=?)
          ORDER BY id LIMIT 1""", (now, now)).fetchone()
        if row is None:
            db.execute("COMMIT")
            return None
        owner = uuid.uuid4().hex
        db.execute("UPDATE jobs SET state='leased', attempts=attempts+1, "
                   "owner=?, lease_until=? WHERE id=?", (owner, now + 10, row[0]))
        db.execute("COMMIT")
        return row[0], row[1], owner, row[2] + 1
    except Exception:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise
    finally:
        db.close()

def finish(job, now, success):
    job_id, payload, owner, attempts = job
    state = "completed" if success else ("dead" if attempts >= 3 else "pending")
    db = open_db()
    try:
        changed = db.execute("""UPDATE jobs SET state=?, eligible=?,
          owner=NULL, lease_until=NULL WHERE id=? AND state='leased'
          AND owner=? AND lease_until>?""",
          (state, now + 2, job_id, owner, now)).rowcount
        return changed == 1
    finally:
        db.close()

initialize()
first_id = enqueue("synthetic notification")
old_attempt = claim(0)
new_attempt = claim(11)
assert old_attempt[0] == new_attempt[0] == first_id
assert not finish(old_attempt, 11, True)
assert finish(new_attempt, 12, True)
second_id = enqueue("synthetic poison item")
for now in (20, 23, 26):
    attempt = claim(now)
    assert attempt[0] == second_id
    assert finish(attempt, now + 1, False)
db = open_db()
try:
    assert db.execute("SELECT state FROM jobs WHERE id=?",
                      (second_id,)).fetchone()[0] == "dead"
    print("expired owner rejected; new owner completed; poison item quarantined")
finally:
    db.close()
```

`BEGIN IMMEDIATE` serializes claim selection and update under SQLite's [transaction model](https://www.sqlite.org/lang_transaction.html). The completion condition checks both owner identity and unexpired lease. It prevents the old local attempt from marking the row completed after another acquisition. It does **not** retract an external notification already sent by that old attempt. Provider idempotency or reconciliation remains necessary.

The fake clock, order-by-ID selection and fixed ten-unit lease are teaching assumptions. This lab lacks a real-time lease authority, renewal, priority/fairness, schema constraints, crash durability testing and a broker integration. Its attempt cap moves handled failures to a terminal `dead` state. An attempt that repeatedly crashes before calling `finish` can be reclaimed indefinitely here, because the lab intentionally has no crash-reclamation cap. A production queue must count and handle that path too; do not advertise this small helper as a complete scheduler.

Each run creates unique synthetic IDs; prior completed and dead rows remain in the disposable database. It assumes no unrelated pending lab work exists, which is why a new directory is required. Cleanup after execution removes the script and synthetic database only. A production dead-letter store instead needs retention, access control and an accountable owner.

## Visibility and acknowledgment are not completion

In SQS, receiving a message temporarily changes visibility; deleting it acknowledges that delivery. The inspected [visibility-timeout documentation](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html) describes expiry and repeated-delivery limitations. Select a visibility interval that covers expected processing and its safety margin, and renew only while the attempt still owns useful work. Long invisibility slows recovery after a crash; short invisibility can overlap still-running work.

A receive count is not a count of successful provider attempts. A consumer can crash immediately after receipt. An acknowledgment before durable outcome recording can lose work. An acknowledgment after outcome recording can be followed by harmless repeated delivery only if the consumer recognizes the durable completion. The ambiguous provider-effect-before-recording window requires the preceding chapter's external contract.

A dead-letter queue isolates work that cannot progress after the configured policy. It is not a disposal chute that makes the service successful. Monitor its entries and age, retain enough sanitized reason and operation identity, and assign a review owner. AWS's [dead-letter guidance](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html) distinguishes retention behavior and warns about ordered-work consequences. Moving one failed event aside can allow later events to proceed, which may violate a strict business ordering requirement.

Replay needs a bounded procedure: correct the underlying defect, validate one synthetic or authorized sample, preserve original business identity, cap redrive rate and reconcile outcomes. Changing every key on replay can turn an idempotent recovery into a duplicate-send campaign. Deleting a dead-letter item without resolution needs an explicit product decision and audit evidence.

## Recover a growing backlog without causing another outage

Start by measuring incoming eligible work, successful completions, retries, in-flight count, oldest unresolved age, provider errors and queue-storage health. Separate work that is waiting for eligibility from work that is ready but lacks capacity. A large backoff population has a different immediate capacity need from an actively runnable population.

If completions fell after a release while arrivals remained stable, inspect worker readiness, schema parsing, lease renewal and provider behavior. A poisoned new payload can consume every worker attempt. Quarantine the classified bad work under the approved policy, repair compatibility and resume gradually. If provider throttling caused the decline, adding workers without a rate limit may make successful completion lower, not higher.

If genuine arrival growth exceeds validated throughput, calculate the required sustainable excess capacity and downstream budget. For a backlog B and desired drain time T with ongoing arrival rate λ, the modeled completion requirement is `λ + B/T`. State the assumptions and test the path. A backlog of 12,000 with arrivals at 20 per second and a ten-minute drain goal requires 40 completions per second under a steady model. Reserve for retries and variation separately.

During recovery, prioritize according to the product's stated deadline and fairness policy. Do not quietly starve old work by always selecting newest items. Preserve tenant isolation and avoid letting one customer's campaign monopolize all workers. Track per-class age with bounded dimensions and controlled diagnostic samples; unbounded per-order metrics remain inappropriate.

Completion of the incident requires durable reconciliation, not an empty broker alone. Jobs might have moved to dead letters, expired under retention or been incorrectly acknowledged. Compare accepted notification intent with completed, pending and terminally resolved states. A queue can be empty while work is lost.

## Exercises and answer guidance

Fifty jobs arrive each second and thirty-five complete. How quickly does depth grow? Fifteen per second, or 900 per minute under stable assumptions. Measure successful completion rather than receive rate.

The old lease owner is prevented from updating the database after expiry. Does that guarantee it cannot send externally? No. Local ownership checks fence local state; the external provider needs an applicable idempotency or authority mechanism.

Depth falls to zero after redrive, but the dead-letter queue grows. Is recovery complete? No. Work moved boundaries without satisfying the notification outcome. Review terminal states, owner and reconciliation evidence.

## Takeaways and verification

Queues absorb timing differences while exposing a finite waiting and ownership problem. Bound in-flight work, distinguish delivery from completion, and treat expired leases and dead letters as normal recovery paths with explicit limits. SQLite and AWS SQS primary documentation was inspected on 2026-10-01. The local lease lab ran under Python 3.14.7 in a temporary directory: expired-owner completion was rejected, the replacement owner completed, and the repeatedly failed synthetic item reached dead state; all assertions passed and the process exited 0. Logical time and local SQLite were tested, not real-time lease renewal, crash reclamation, external effects, a broker or production backlog recovery.
