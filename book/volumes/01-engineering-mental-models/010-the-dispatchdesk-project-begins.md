---
book: The Complete DevOps Engineering Book
volume: 1
volume_title: "Engineering Mental Models"
chapter: 10
title: "The DispatchDesk Project Begins"
slug: the-dispatchdesk-project-begins
status: complete
summary: ../../_ai/chapter-summaries/010-the-dispatchdesk-project-begins.md
---

# Chapter 10 — The DispatchDesk Project Begins

## A small order and notification product

DispatchDesk accepts orders, records them and arranges notifications. We will grow this product through Linux supervision, networking, containers, release automation and observability. Each addition must answer a stated need. The project is not a race toward a prescribed stack: a VPS, managed AWS services and Kubernetes are alternative operating paths under different company constraints.

Read [Teams, Ownership and Operational Work](009-teams-ownership-and-operational-work.md) first. The local example requires Python 3 with its SQLite module, Bash and a writable disposable directory on Linux. It runs as an ordinary user under Ubuntu, Fedora or RHEL and does not bind a network port. Later chapters provide their own complete service setup rather than assuming this example left files behind.

The first contract is deliberately small. An order has an identifier, a customer reference and a positive item count. Acceptance stores the order and the intent to notify together, then returns the identifier. Notification sending is outside that acceptance transaction. An accepted order must remain retrievable after the program exits. This is a learning data model, not a complete commercial order system: it omits pricing, inventory, payment, tenancy authorization and personal destination data.

Separating notification intent from notification delivery matters. If the external provider is unavailable, accepted orders should not disappear. The stored intent makes delayed work observable. It does not solve delivery by itself; a later worker must define attempts, acknowledgements and uncertain provider results. Redis remains optional derived state unless a later chapter explicitly adopts another authority contract.

The eventual HTTP interface uses `POST /orders`, `GET /orders/{id}`, `GET /healthz` and `GET /readyz`, normally listening on unprivileged port 8080. Health means the process can respond; readiness means it can safely accept its routed work under a defined dependency policy. When client retries become part of the interface, order creation includes a caller-supplied idempotency key. This chapter's CLI is single-invocation teaching code and does not implement that retry contract.

## A complete local acceptance example

Create a disposable directory in one Bash terminal and retain its path for cleanup:

```bash
project_lab=$(mktemp -d)
cd "$project_lab" || exit 1
```

Save the following complete file as `dispatchdesk.py` in that directory using your editor. It uses only Python's standard library. The database file is explicitly relative to this lab directory; a supervised production process would use a deliberately configured persistent location.

```python
import argparse
import json
import sqlite3
import uuid

parser = argparse.ArgumentParser(description="DispatchDesk local learning CLI")
commands = parser.add_subparsers(dest="command", required=True)
create = commands.add_parser("create")
create.add_argument("customer")
create.add_argument("item_count", type=int)
show = commands.add_parser("show")
show.add_argument("order_id")
commands.add_parser("pending")
args = parser.parse_args()

if args.command == "create" and args.item_count <= 0:
    parser.error("item_count must be positive")

connection = sqlite3.connect("dispatchdesk.sqlite3")
try:
    connection.execute("PRAGMA foreign_keys = ON")
    with connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                customer TEXT NOT NULL,
                item_count INTEGER NOT NULL CHECK (item_count > 0)
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS notification_intent (
                order_id TEXT PRIMARY KEY REFERENCES orders(id),
                state TEXT NOT NULL CHECK (state IN ('pending', 'sent'))
            )
        """)

    if args.command == "create":
        order_id = str(uuid.uuid4())
        with connection:
            connection.execute(
                "INSERT INTO orders VALUES (?, ?, ?)",
                (order_id, args.customer, args.item_count),
            )
            connection.execute(
                "INSERT INTO notification_intent VALUES (?, 'pending')",
                (order_id,),
            )
        print(order_id)
    elif args.command == "show":
        row = connection.execute(
            "SELECT id, customer, item_count FROM orders WHERE id = ?",
            (args.order_id,),
        ).fetchone()
        if row is None:
            raise SystemExit("order not found")
        print(json.dumps(dict(zip(("id", "customer", "item_count"), row))))
    else:
        rows = connection.execute(
            "SELECT order_id, state FROM notification_intent ORDER BY order_id"
        ).fetchall()
        for row in rows:
            print(json.dumps(dict(zip(("order_id", "state"), row))))
finally:
    connection.close()
```

`argparse` selects an explicit operation. Positive item count is checked both before insertion and by the database constraint. Parameter placeholders separate values from SQL text; customer input is not concatenated into a query. A UUID supplies a local identifier. The connection context commits the paired inserts on successful exit and rolls back their transaction if an insert raises an exception. The identifier is printed after that context exits, so the program does not report acceptance before its database commit.

The explicit `finally` closes the connection; the connection's transaction context should not be confused with closing it. SQLite's [transactional description](https://www.sqlite.org/transactional.html) explains the engine's atomic transaction model. Actual durability depends on the deployed storage and settings; this local example does not test power failure or host-loss recovery. It also does not change journal or synchronization settings to make an unsupported performance promise.

Run the operations sequentially in the same directory:

```bash
order_id=$(python3 dispatchdesk.py create demo-customer 3) || exit 1
python3 dispatchdesk.py show "$order_id"
python3 dispatchdesk.py pending
python3 dispatchdesk.py create demo-customer 0
```

The first command captures the accepted identifier. The guarded assignment stops if creation fails; it does not treat an error as an order ID. `show` starts another Python process, proving retrieval does not depend on the first process's memory. `pending` displays stored intent. The final command is an intentional negative test and should exit with an item-count error before creating an order. Do not append an unconditional “success” message that conceals this failure.

Expected evidence is a JSON order with count three, one pending intent referencing the same identifier, and rejection of zero count. Output identifiers vary. The code does not send a notification, enforce tenant access or deduplicate repeated `create` invocations. Running `create` twice creates two distinct orders by design at this stage.

A missing SQLite module is an environment prerequisite failure. “Unable to open database file” suggests an unavailable path or permissions. “Database is locked” can indicate competing writers; this novice example does not hide contention with an unlimited retry. Read the error and preserve the file before experimenting with changes. Later chapters replace the teaching setup with explicit operational configuration.

After finishing, delete only the known lab files from the lab directory:

```bash
rm -- dispatchdesk.py dispatchdesk.sqlite3
cd /tmp || exit 1
rmdir -- "$project_lab"
```

This deliberately destroys the lab orders. If unexpected files remain, `rmdir` fails; inspect them instead of widening removal. Do not use this cleanup on real data. No companion source directory is required: the entire reader program stays inline here.

## Workload, budget and reliability assumptions

The learning workload remains one order per second typically and ten at peak, with payloads bounded to 64 KiB once HTTP is introduced. These are fictional planning inputs. The CLI has not been benchmarked to meet them, and its command-line arguments are not an implementation of the HTTP payload limit. A later load test must exercise the actual running service and realistic data shape.

Harbor's two developers share operations and have a tight cash budget. Chapter 4 introduced a fictional 99.5% time-based order-acceptance objective over 30 days, counting maintenance. That target is a planning choice, not an achieved result or contractual promise. Notification delay is measured separately. The learning program establishes basic persistence behavior, but backup retention, host-loss recovery and response coverage remain unresolved.

Budget includes operator time. A low-priced server requires updates, access control, disk monitoring, database maintenance and restoration. A managed service can remove selected duties while introducing integration and provider dependencies. Record the costs relevant to the actual company rather than inventing prices. Later AWS examples identify billable actions beside their commands without running them during authoring.

The application's languages will vary where their operational behavior is informative. Python can demonstrate a small process and database boundary; PHP examples explain PHP-FPM and proxy lifecycles; Go can demonstrate a compiled service and shutdown; JavaScript can demonstrate event-loop and asynchronous behavior. Language differences should teach real runtime consequences, not imply that rewriting a service is necessary to change its hosting.

## Three companies with different constraints

Harbor begins with one VPS and durable persistence. It investigates inefficient queries and considers resizing before adding hosts. It separates data and application hosting or adds a replica when measured constraints justify it. Recovery from losing the host must be explicit. Kubernetes may remain inappropriate because its operating burden exceeds Harbor's benefit.

Summit has burstier traffic and limited capacity for database and cluster maintenance. It favors managed AWS database, queue and container services when their contracts fit. IAM, network paths, quotas, billing and provider failures remain engineering responsibilities. A worker can scale separately from the API, but its redelivery behavior must preserve the notification contract.

Atlas has several application teams, different runtimes and shared governance requirements. Its platform team may choose Kubernetes to provide a common workload API and deployment capability. It can retain managed databases outside the cluster. Platform adoption responds to team and isolation needs, not to an assumption that every successful product eventually needs a cluster.

All three must preserve the order acceptance contract. Comparing them becomes meaningful only when workload and reliability assumptions are held constant or changes are stated. A larger Atlas scenario later in the book may have different traffic and tenancy; it must introduce those facts before using them to justify architecture.

## The two-write failure we avoided

Imagine the program commits the order, prints its identifier, then inserts notification intent in a separate transaction. The second insertion fails because storage becomes unavailable. The order is accepted, but no pending work exists. A retry of notification processing cannot discover work that was never recorded.

The paired transaction avoids that local gap: both order and intent are committed together or neither insert completes. This is a simple introduction to recording intent atomically, not a complete external-provider transaction. Sending to a provider cannot generally be rolled back by rolling back this local database. A later worker and reconciliation design must handle the boundary between provider action and local completion state.

Diagnosis of the broken variant compares accepted orders with intent records. Recovery preserves the accepted order, identifies missing intent and recreates it only under a controlled reconciliation procedure. The team also checks whether any external send occurred, because a blind repair could duplicate an effect. The lasting change makes the local invariant explicit and tests the insertion-failure path.

## Exercises and answer guidance

1. Run `show` from another directory without moving the database. Why may the order disappear from view? The program uses a relative database path and may create another empty database. Identify execution path before interpreting this as lost data.
2. Invoke `create` twice with the same arguments. Should the identifiers match? This version generates distinct orders. A later caller-key contract must deliberately add idempotency rather than assume customer and item count uniquely identify an order.
3. Where should a provider call occur? After durable intent exists, under a worker's explicit delivery contract. Calling it inside the acceptance transaction can hold resources and still cannot atomically roll back an external effect.

## Review questions and takeaways

What does the printed identifier promise? Which invariant does the paired transaction preserve? Which risks remain after a successful local retrieval? What company constraint would change the hosting decision? Which future test validates the assumed workload?

Start with a clear acceptance boundary and observable pending work. Keep data authoritative, document unimplemented guarantees and evolve hosting only when constraints change. Next, [The Shell and Command Execution](../02-linux-and-automation/011-the-shell-and-command-execution.md) develops the Linux tools used to operate the project.

## Sources and verification

SQLite's official transactional description was inspected on 2026-10-01. The Python sqlite3 documentation fetch returned a service error; no documentation verification is claimed for that attempt. The extracted complete program was executed locally with Python 3.14.7 and SQLite 3.53.4: creation, retrieval in a new process, matching pending intent, zero-count rejection and missing-order rejection passed. The disposable database was removed by the test context. No load, crash, tenant authorization, notification provider or host recovery test is claimed. All companies, traffic assumptions and reliability objectives are fictional. Independent review is pending.
