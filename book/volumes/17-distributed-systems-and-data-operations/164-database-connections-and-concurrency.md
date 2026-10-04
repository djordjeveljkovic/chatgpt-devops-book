---
book: The Complete DevOps Engineering Book
volume: 17
volume_title: "Distributed Systems and Data Operations"
chapter: 164
title: "Database Connections and Concurrency"
slug: database-connections-and-concurrency
status: complete
summary: ../../_ai/chapter-summaries/164-database-connections-and-concurrency.md
---

# Chapter 164 — Database Connections and Concurrency

**Section outline:** distinguish pool acquisition from database work; keep business transactions short; reproduce row-lock contention with two sessions; inspect bounded blocker metadata; recover deadlocks and saturation safely.

## A pool is a concurrency boundary

A database pool limits active connections and reuses expensive connection setup. It does not increase the database's ability to execute queries or remove transaction contention. DispatchDesk can have spare API CPU while every request waits for a pool slot. It can also have many available connections while all writers wait on one locked row. Those situations require different repairs.

[Queue backpressure](163-queues-and-backpressure.md) bounded worker delivery. The same reasoning applies to database acquisition: bound waiting callers, give acquisition a deadline, and return connections reliably. A timeout at the pool boundary means no connection became available in time. It does not prove that PostgreSQL was unreachable. Distinguish acquisition time, execution time, lock waiting and transaction duration in telemetry.

Calculate pool demand across processes, replicas, background jobs and rollout overlap. Four API replicas with twenty connections each plus three worker replicas with ten each permit 110 connections. A fifth temporary API replica raises the maximum to 130. Reserve administrative and recovery access separately. The relevant ceiling is the database's authorized service budget, which can be below its global connection setting. Pools often open lazily or retain idle connections; inspect the actual client's behavior instead of assuming the maximum is the observed steady count.

More concurrency can reduce throughput once lock contention, storage or CPU saturates. A smaller bounded pool can improve latency by preventing the database from scheduling excessive simultaneous work. It can also increase application-side waiting, so compare the full path and rejection policy. An unbounded waiting queue outside a tiny pool simply moves overload into application memory.

For Python, keep transaction and connection context aligned; returning a connection while it still has an open transaction contaminates the next borrower. PHP-FPM can multiply per-process database sessions, so pool assumptions must reflect the number of children and persistence settings. A Go `database/sql` pool belongs to the process, not every goroutine; configuring goroutine concurrency without a connection budget misses the boundary. Node.js handlers need to release a borrowed client even when promises reject. The runtime details differ, but ownership must be explicit.

## Keep business transactions short and complete

A transaction groups changes under a database contract. DispatchDesk's order and notification intent must commit together before acceptance. The external notification provider does not belong inside that transaction: holding database locks while waiting on a remote HTTP response expands contention and still cannot atomically commit that independent provider effect. Record intent, commit, then deliver through the worker's recovery contract.

An idle connection is not automatically a problem. A connection idle **inside a transaction** can retain locks or an old snapshot while doing no useful database work. Long transactions can obstruct maintenance and accumulate waiting writers. Inspect transaction age and state rather than only counting connections. Avoid printing full SQL text if it can contain customer data or credentials.

Isolation describes which concurrent effects a transaction may observe and which anomalies the database prevents. PostgreSQL's default Read Committed uses statement-level snapshots; two statements in one transaction can observe different committed changes. Stronger isolation changes that contract and can require whole-transaction retries after serialization failures. Consult the exact engine behavior in [PostgreSQL's isolation documentation](https://www.postgresql.org/docs/current/transaction-iso.html), not a generic claim that “a transaction means nobody else can change anything.”

A read-then-write business rule needs an appropriate mechanism: an atomic conditional update, a uniqueness constraint, a row lock or a suitable isolation level. Raising isolation everywhere without understanding the invariant can add contention while leaving external effects uncontrolled. Retry only the safe transaction boundary and preserve the operation's idempotency identity.

## A complete two-session row-lock experiment

This lab requires an existing authorized disposable PostgreSQL database and the `psql` client. [The single-host database chapter](../04-vps-and-server-operations/036-database-and-cache-operations-on-one-host.md) supplies the Linux service context; [RDS operations](../10-aws-production-services/095-rds-and-managed-database-operations.md) supplies the managed alternative. The experiment does not provision a database. Use a dedicated nonproduction database where you may create and remove the named schema, with no customer data or other consumers.

Ubuntu, Fedora and RHEL use the same SQL and psql arguments when a compatible client is installed. Their package repositories, PostgreSQL streams, service units, authentication and SELinux/AppArmor paths differ; retain the setup chapter's actual chosen engine/client rather than guessing that a generic package name supplies the same version everywhere. The SQL behavior was checked against PostgreSQL 18 documentation. It uses established features, but confirm the installed version and privileges before execution.

Configure an approved password-free-on-command-line connection service named `dispatchdesk-lab` in the user's controlled [PostgreSQL connection service file](https://www.postgresql.org/docs/current/libpq-pgservice.html), using the organization's credential mechanism. A service definition must supply the actual host, port, database and user; remote TLS verification follows the approved server certificate contract. The connection service is a reader prerequisite, not an invented hostname or credential. Launch each terminal with:

```bash
psql 'service=dispatchdesk-lab' -X
```

`-X` skips local psql startup files so unexpected personal settings do not alter the lab. The quoted connection string selects the approved named service. In the first session, inspect identity and create synthetic state only after verifying the database:

```sql
SELECT current_database(), current_user, version();
CREATE SCHEMA dispatchdesk_concurrency_lab;
CREATE TABLE dispatchdesk_concurrency_lab.inventory (
    item text PRIMARY KEY,
    remaining integer NOT NULL CHECK (remaining >= 0)
);
INSERT INTO dispatchdesk_concurrency_lab.inventory VALUES ('synthetic-book', 1);
```

If the schema already exists, stop and establish its owner rather than reusing or dropping unfamiliar data. The synthetic table begins with one available item. Now, in session A, acquire an update lock and leave the transaction open:

```sql
SET application_name = 'dispatchdesk-lock-lab-A';
BEGIN;
UPDATE dispatchdesk_concurrency_lab.inventory
SET remaining = remaining - 1
WHERE item = 'synthetic-book' AND remaining > 0
RETURNING item, remaining;
```

Do not commit yet. In session B, request the same conditional update with a bounded lock wait:

```sql
SET application_name = 'dispatchdesk-lock-lab-B';
BEGIN;
SET LOCAL lock_timeout = '2s';
SET LOCAL statement_timeout = '5s';
UPDATE dispatchdesk_concurrency_lab.inventory
SET remaining = remaining - 1
WHERE item = 'synthetic-book' AND remaining > 0
RETURNING item, remaining;
```

SessionB should encounter the lock-wait boundary while sessionA retains the row lock. `lock_timeout` bounds lock acquisition; `statement_timeout` bounds statement execution under [PostgreSQL's documented timeout semantics](https://www.postgresql.org/docs/current/runtime-config-client.html). They are session-local transaction settings here, not a global production policy. After the error, run `ROLLBACK;` in sessionB to leave its failed transaction. Run `COMMIT;` in sessionA.

Then repeat in sessionB without the held competitor:

```sql
BEGIN;
SET LOCAL lock_timeout = '2s';
UPDATE dispatchdesk_concurrency_lab.inventory
SET remaining = remaining - 1
WHERE item = 'synthetic-book' AND remaining > 0
RETURNING item, remaining;
COMMIT;
SELECT item, remaining FROM dispatchdesk_concurrency_lab.inventory;
```

The conditional update should now affect zero rows because the remaining count is zero. This is expected evidence to verify, not a fabricated psql transcript. The check constraint also prevents a negative count, but a thrown constraint error is not a complete customer-facing reservation contract. The application must interpret zero updated rows as the defined unavailable result and avoid claiming acceptance.

The [explicit-locking documentation](https://www.postgresql.org/docs/current/explicit-locking.html) explains competing row updates and transaction-held locks. The experiment isolates one row and two callers; it does not model full DispatchDesk order creation, distributed failover or an inventory business requirement. Cleanup after both sessions have ended their transactions is:

```sql
DROP TABLE dispatchdesk_concurrency_lab.inventory;
DROP SCHEMA dispatchdesk_concurrency_lab;
```

These commands delete only the synthetic table and schema you created. Avoid `CASCADE`: an unexpected dependency should stop cleanup for investigation. Quit psql with `\q`. If a terminal disappears while its transaction is open, confirm the session ended and its transaction rolled back before rerunning the lab.

## Observe blockers without exposing request payloads

From an authorized observation connection, the following read-only query lists bounded metadata for DispatchDesk sessions. It assumes the application supplies a recognizable `application_name`; permissions determine which fields are visible. The observer needs documented statistics access, not unrestricted administrator rights merely to see a dashboard.

```sql
SELECT pid, application_name, state,
       wait_event_type, wait_event,
       clock_timestamp() - xact_start AS transaction_age,
       pg_blocking_pids(pid) AS blocking_pids
FROM pg_stat_activity
WHERE datname = current_database()
  AND application_name LIKE 'dispatchdesk%'
ORDER BY xact_start NULLS LAST
LIMIT 20;
```

`pid` identifies a current backend, not a durable identity across restarts. `wait_event_type` and `wait_event` classify current waiting; transaction age exposes long-lived work; `pg_blocking_pids` identifies blockers according to the engine's lock view. Limiting rows keeps the inspection readable. The query intentionally omits full SQL text. [PostgreSQL statistics documentation](https://www.postgresql.org/docs/current/monitoring-stats.html) explains activity and visibility; join with approved application traces to interpret the actual request boundary.

A snapshot can miss a brief lock and does not prove the absence of contention. Correlate time series of pool waiting, transaction duration and rejected acquisition with sampled backend state. Treat “active” as a database state, not proof that every backend is actively consuming CPU.

## Deadlocks and transaction retry

A deadlock can occur when one transaction holds rowA and wants rowB while another holdsB and wantsA. The database detects the cycle and aborts a participant. Consistent lock acquisition order reduces that pattern, but arbitrary application paths and migrations can reintroduce it. Keep transactions short, document lock order and inspect the actual deadlock report under controlled access.

Recovery starts by rolling back the failed transaction. Retry the whole safe business transaction under its attempt and deadline budget, not just the last statement whose assumptions may now be stale. A provider call executed inside the aborted transaction has not necessarily been undone externally, which is another reason to keep that effect outside the database transaction. [Idempotency](162-retries-idempotency-and-backoff.md) supplies the repeatable acceptance identity.

Serialization failures similarly signal that the transaction could not satisfy its requested concurrency contract. They are not proof of database corruption. The application must handle them as designed, with bounded whole-transaction retry and fresh reads. An infinite retry loop can transform normal contention into a service outage.

## Diagnose a saturated database-backed service

Suppose Atlas increases API replicas and sees acquisition timeouts while PostgreSQL CPU remains moderate. First inventory pool maxima, actual connection counts and rollout overlap. If connections are exhausted, reduce unnecessary idle allocation or cap concurrency according to the validated service budget. Raising the global database ceiling without memory and workload analysis can move the failure into the server.

If slots remain available but transactions wait on one blocker, identify its owner and age. A deployment may have left an idle transaction open, or a report may hold a lock longer than expected. Coordinate cancellation or termination through the database incident procedure: termination rolls back work and can affect legitimate operations. Do not kill every backend matching an application name as a routine repair. Preserve the blocker evidence and fix the code path that failed to complete its transaction.

If execution is slow with little lock waiting, inspect query plans, row estimates, storage and data growth. A pool change cannot repair a missing index or expensive query. If only new connections fail, investigate authentication, TLS, DNS and server limits separately from already-established sessions. Recovery acceptance includes successful durable order transactions, stable acquisition time and notification progression, not merely fewer open connections.

## Exercises and answer guidance

A pool timeout occurs while database connections are all idle in transaction. What should the team inspect? Transaction owners, age, unfinished code paths and held locks; simply increasing the pool can conceal the leak.

After a lock-timeout error, sessionB remains in an aborted transaction. What happens before more useful work? Roll back that transaction. Do not assume a later SELECT repairs its state.

An inventory row has one unit. Why is `UPDATE ... WHERE remaining > 0` stronger than reading one and later writing zero in unrelated operations? The mutation evaluates its condition within the database's concurrency behavior rather than trusting a stale application observation; inspect affected rows to determine the business result.

## Takeaways and verification

Connection limits, pool waiting, locks and isolation are different concurrency boundaries. Keep acceptance transactions complete and short, put external effects in recoverable work, and diagnose the actual wait before changing capacity. PostgreSQL 18 primary documentation was inspected on 2026-10-01. The two-session lab and observer query are complete for an existing authorized database; no PostgreSQL connection, row-lock experiment, cancellation or production pool change was executed while authoring.
