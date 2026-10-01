---
book: The Complete DevOps Engineering Book
volume: 17
volume_title: "Distributed Systems and Data Operations"
chapter: 161
title: "Partial Failure and Timeouts"
slug: partial-failure-and-timeouts
status: draft
summary: ../../_ai/chapter-summaries/161-partial-failure-and-timeouts.md
---

# Chapter 161 — Partial Failure and Timeouts

## The caller and the server can disagree about what happened

A distributed operation can succeed at one boundary and fail at another. DispatchDesk can commit an order and its notification intent, then lose the connection before the caller receives202. A notification provider can accept a message, then return a response that never reaches the worker. The caller observes a timeout; the remote side may observe success. “The request failed” is therefore an incomplete incident statement unless it identifies the boundary and evidence.

[Cost and performance choices](../16-performance-and-capacity-engineering/160-cost-and-performance-tradeoffs.md) compared execution environments. A VPS, ECS task or Kubernetes pod can all encounter this ambiguity. A platform restart does not reveal whether an external effect occurred. Reliability depends on an application contract for uncertain outcomes, not on the process supervisor's ability to replace the process.

There are several useful states: not attempted, rejected before acceptance, accepted and durably recorded, completed externally, and unknown to this observer. Unknown is a valid state of knowledge. It is not equivalent to a negative result. A connection refusal before sending the request has different implications from a timeout while waiting for its response. Even that distinction depends on the client library and proxy path, so retain request phase and operation identity when available.

A client cancellation also has a scope. It can stop waiting locally, close a socket or signal cooperative cancellation. It does not necessarily roll back a committed transaction or retract an accepted provider message. A server can continue working after its client has disconnected. If the application wants cancellation of pending durable work, it needs a separate authorized state transition that resolves races with completion.

## Give the entire request a budget

A timeout limits waiting at a specified boundary. Connection timeout, TLS handshake timeout, response-header timeout, read-idle timeout and total deadline are different controls. A library's option called `timeout` may cover only some blocking operations. Inspect its documentation and test its behavior; a two-second socket timeout is not automatically a two-second end-to-end operation deadline.

For a hypothetical order request with a one-second server-side budget, reserve time for response serialization and routing. The request might allocate at most150milliseconds to pool acquisition and550to transactional database work, leaving300for validation, scheduling and response. These allocations are illustrative. If pool acquisition consumes140milliseconds, the downstream operation must receive the remaining budget rather than a fresh independent one-second timeout. Otherwise a chain of individually reasonable waits can exceed the customer's total deadline.

Use a monotonic clock for elapsed time inside one process. Wall clocks can be adjusted, and comparing unsynchronized clocks across machines can distort durations. To propagate a deadline between machines, account for the protocol and clock assumptions or transmit a remaining duration with an explicit handling policy. Never trust an unbounded client-provided budget: apply the service's maximum and authorize any privileged deadline extension.

Nested retries consume the same budget. If three layers each allow three attempts, a single original request can trigger as many as27leaf attempts under an unfortunate failure path. Queues and external calls amplify work separately. A dependency that is merely slow can become unavailable when excess retries exhaust pools. [The next chapter](162-retries-idempotency-and-backoff.md) owns retry classification and idempotency design.

Timeout values should follow measured latency distributions and product deadlines. Extremely short values reject healthy variation and manufacture retries. Very long values occupy worker slots and connections while users have already stopped waiting. Include connection establishment and cold-path behavior in testing; a warmed persistent connection can hide a startup handshake cost.

## A complete ambiguous-response lab

The following single-file lab models a provider that records an effect, then delays its response. It uses a local SQLite ledger so the result can be observed independently of the timed-out connection. It does **not** implement DispatchDesk order acceptance, send a real notification or model provider durability guarantees. A unique operation token enables reconciliation in the fake provider. The actual provider must explicitly support a comparable lookup or idempotency contract before a real worker can rely on it.

Save this as `uncertain_response.py` in a new disposable directory. Run it as an ordinary user with Python3 and its SQLite module available on Ubuntu, Fedora or RHEL. The script binds loopback8080, creates `effect-lab.sqlite`, performs one local HTTP request and a lookup, and shuts down its listener. Stop other8080labs first. No cloud identity, package download or privileged port is needed.

```python
import json
import sqlite3
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import URLError
from urllib.request import Request, build_opener, ProxyHandler

path = "effect-lab.sqlite"
with sqlite3.connect(path) as db:
    db.execute("CREATE TABLE IF NOT EXISTS effects "
               "(operation TEXT PRIMARY KEY, recorded_at TEXT NOT NULL)")

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def reply(self, status, value):
        data = json.dumps(value).encode()
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            print("response connection disappeared after ledger commit")

    def do_POST(self):
        if self.path != "/mock-notifications":
            self.reply(404, {"error": "route"})
            return
        token = self.headers.get("X-Lab-Operation", "")
        try:
            token = str(uuid.UUID(token))
        except ValueError:
            self.reply(400, {"error": "operation token required"})
            return
        with sqlite3.connect(path, timeout=1.0) as db:
            db.execute("INSERT OR IGNORE INTO effects VALUES (?, ?)",
                       (token, "lab-recorded"))
        # The connection context has committed before this delay.
        time.sleep(0.5)
        self.reply(202, {"operation": token, "recorded": True})

    def do_GET(self):
        prefix = "/mock-effects/"
        if not self.path.startswith(prefix):
            self.reply(404, {"error": "route"})
            return
        token = self.path[len(prefix):]
        with sqlite3.connect(path, timeout=1.0) as db:
            row = db.execute("SELECT operation FROM effects WHERE operation=?",
                             (token,)).fetchone()
        self.reply(200, {"operation": token, "recorded": row is not None})

server = ThreadingHTTPServer(("127.0.0.1", 8080), Handler)
thread = threading.Thread(target=server.serve_forever)
thread.start()
opener = build_opener(ProxyHandler({}))  # Keep this lab off configured proxies.
token = str(uuid.uuid4())
try:
    request = Request("http://127.0.0.1:8080/mock-notifications", data=b"",
                      headers={"X-Lab-Operation": token}, method="POST")
    try:
        with opener.open(request, timeout=0.1) as response:
            print("POST result:", response.read().decode())
    except (TimeoutError, URLError) as error:
        print("POST observer has uncertain outcome:", type(error).__name__)
    with opener.open("http://127.0.0.1:8080/mock-effects/" + token,
                     timeout=1.0) as response:
        print("independent reconciliation:", response.read().decode())
finally:
    server.shutdown()
    server.server_close()
    thread.join()
```

The intentional half-second response delay exceeds the client's blocking timeout. The expected evidence is an uncertain POST observation followed by a lookup showing the ledger record. Reader scheduling or a port conflict can affect the run; no transcript is fabricated here. `ProxyHandler({})` bypasses ambient proxy settings for the explicitly local lab rather than accidentally sending the fake request through corporate infrastructure. The HTTP server is a mechanics tool, not a production server, as [Python's server documentation](https://docs.python.org/3/library/http.server.html) cautions.

The unique key and `INSERT OR IGNORE` collapse repeated identical operation tokens in this mock. It stores no meaningful payload, so it does not solve conflicting reuse with different notification data. The next chapter handles that missing semantic contract. Each request opens its own SQLite connection; the transaction commits before response delay. SQLite's [transaction documentation](https://www.sqlite.org/lang_transaction.html) explains its single-writer behavior. This local ledger's commit evidence does not prove recovery after storage corruption, host loss or a real provider outage.

The [urllib documentation](https://docs.python.org/3.14/library/urllib.request.html) scopes its timeout to blocking operations. The lab exercises delayed response waiting; it does not implement a strict total-deadline wrapper. Cleanup, after the script exits, is removal of `uncertain_response.py` and `effect-lab.sqlite` from this disposable directory. The database contains only synthetic operation IDs. Preserve it until you have inspected the example if learning from the result.

## Cancellation should save work without lying about state

Before a transaction begins, cancellation can avoid work altogether. During a transaction, the application and database need a defined cancellation path and cleanup. After commit, the order exists even if response delivery fails. A handler should not record “rejected” merely because writing the response encounters a broken pipe; that would contradict durable state and confuse reconciliation.

Background notification work has its own deadline and ownership. If a worker's grace period expires, the process may be killed while its provider call remains uncertain. Keep the durable intent and its operation identity so a later worker can reconcile or repeat under the documented idempotency contract. Deleting the intent because the local task was canceled loses the recovery route.

Timeout handling must also release local resources. Close response bodies, return or discard database connections according to their health, cancel child work cooperatively and avoid retaining an unbounded goroutine/task per timed-out caller. A client that stops waiting while its server keeps running can produce an invisible concurrency buildup. Observe in-flight work and completions independently from client response counts.

## Follow one uncertain operation during an incident

Suppose Summit's worker logs a provider response timeout and its queue lease later expires. First preserve the durable notification ID, provider operation key, attempt timestamp, request phase and sanitized provider request identifier if returned. Confirm whether the provider offers authoritative status lookup and whether its idempotency window still covers the operation. An absent local success log is not proof the provider did nothing.

If lookup establishes completion, update durable local state through the permitted reconciliation transition and acknowledge the recovered job. If lookup establishes definite rejection, classify whether a retry is allowed. If the outcome remains uncertain and duplicate effects are harmful, use the product's explicit pending/manual-reconciliation path rather than improvise a new key. If duplicates are acceptable under a stated contract, retry can be chosen deliberately with the original identity and bounded policy.

For order acceptance, the API's durable idempotency result gives the caller a way to recover the original order identity. Inspect that authoritative record before creating another order with a new key. If a failover or replication lag affects the read, use the documented authority path rather than treating a stale “not found” as permission to repeat a mutation.

Recovery evidence includes reconciled durable state and customer-visible behavior. A provider becoming reachable again does not reconcile old uncertain calls. Replay can also create a sudden burst, so resume under concurrency and rate limits while tracking the age of unresolved intents. Keep uncertainty visible until evidence resolves it.

## Exercises and answer guidance

A client times out after the server committed an order. Should the server erase the order? No. The response observation does not undo the durable transaction. The client needs the original operation identity and idempotency/result lookup contract.

Three layers each permit three attempts. What is the possible leaf-attempt count?27under the stated independent worst-case model. Choose a responsible retry layer, remaining deadline and attempt budget rather than independently multiplying policies.

A socket timeout is set to one second. Can a large response that continuously delivers bytes necessarily finish within one second? Not from that setting alone. Inspect whether it is an idle/blocking timeout or a total deadline, then test the actual library behavior.

## Takeaways and verification

Partial failure creates uncertainty about outcomes, especially after durable or external effects. Bound the whole operation, preserve identities, and distinguish cancellation of waiting from reversal of committed state. Python HTTP/urllib and SQLite primary documentation was inspected on2026-10-01; the Python SQLite library page fetch failed, so only the engine transaction page was available for that source inspection. No local socket lab, provider call or production cancellation experiment was executed during authoring.

