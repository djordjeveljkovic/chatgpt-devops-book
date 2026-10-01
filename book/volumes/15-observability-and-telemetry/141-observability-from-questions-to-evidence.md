---
book: The Complete DevOps Engineering Book
volume: 15
volume_title: "Observability and Telemetry"
chapter: 141
title: "Observability from Questions to Evidence"
slug: observability-from-questions-to-evidence
status: complete
summary: ../../_ai/chapter-summaries/141-observability-from-questions-to-evidence.md
---

# Chapter 141 — Observability from Questions to Evidence

**Section outline:** choose signals from questions; define the customer boundary; instrument acceptance and notification; investigate contradictory evidence; assess coverage and cost.

## Metrics, logs, traces and profiles

DispatchDesk accepts orders and later sends notifications. Its users do not care whether a process has an open TCP socket. They care that a submitted order is recorded once, that the response arrives promptly, and that a notification is delivered within the promised window. Start an observability design with these questions. A dashboard that says every container is running can coexist with a service that silently loses orders.

A metric is a numerical observation associated with a bounded set of dimensions. A counter of accepted orders answers how much work has happened; its change over time answers the acceptance rate. A gauge of outstanding notifications describes current backlog. A histogram of request durations describes a distribution. These signals make broad comparisons cheap, but they deliberately discard individual narratives. A metric labeled with every order ID no longer provides economical aggregation: every new order creates another series, and storage grows with business events rather than with the shape of the service.

A log records an event with its context. A structured event such as `order_committed` can carry an order reference, a trace ID, a deployment revision, and a result. It supports investigation of a particular failure, provided the event is emitted at the right boundary and retained long enough. A log line saying `sending notification` proves that code reached that line; it does not prove that the remote provider accepted delivery. Use separate event names for attempted, accepted, retried, and permanently failed operations. Record the provider's acknowledged result without copying personal data or credentials into the record.

A trace associates spans across a request's path. A span is a timed operation with a parent relationship and attributes. A request may contain a database span and a queue-publish span; a worker may continue the context when handling the message. A trace helps distinguish time in application code from time waiting on dependencies. It is a sample of behavior, not a complete business ledger. A trace absent from a sampled backend does not prove the request never occurred.

A profile attributes resource use to code paths. A CPU profile can reveal expensive JSON serialization when the request metric says latency rose and the trace shows application time dominating. An allocation profile can expose object churn even when average resident memory is stable. Profiling overhead, permissions, symbols and runtime support differ across languages. Use profiles to test a concrete hypothesis; collecting them indefinitely without a retention or access plan produces another sensitive data store.

These signals complement each other because they preserve different information. The metric identifies a change in the population. The trace locates a slow portion of selected requests. The log explains an event's outcome. The profile identifies where process resources went. None removes the need to examine data correctness, dependency state or deployment history.

## User impact and service boundaries

Define the denominator before naming a success percentage. For DispatchDesk, an eligible order request is a syntactically valid authenticated attempt to submit an order. Validation failures caused by malformed input may be excluded from the availability objective but still matter to product teams. Server errors and responses that claim success before durable commit belong in the failure numerator. Otherwise the service can improve a dashboard by accepting less work or by reporting success too early.

Use two separate objectives: synchronous acceptance and asynchronous notification. A successful `202` response means the order and the intent to notify have been committed; it does not mean the notification was delivered. The notification objective measures elapsed time from that durable acceptance to a provider-confirmed outcome. If delivery is eventually impossible, expose a terminal state that support staff can reconcile. The business boundary prevents a queue consumer's uptime from masquerading as delivery reliability.

Suppose, as a fictional planning example, 40,000 eligible requests arrive in a day and 80 fail at the acceptance boundary. The daily success fraction is 39,920 / 40,000, or 99.8%. If another 600 notifications exceed their promised deadline, that is a different population and objective. Combining both counts into one percentage hides whether users could submit an order or whether follow-up work stalled. Preserve the stages and connect them through identifiers in investigation tools.

Instrument both positive and negative outcomes. A success-only counter cannot distinguish no traffic from broken instrumentation. Maintain total eligible attempts and failed attempts, initialize bounded label combinations where practical, and observe the scrape or export pipeline separately. A zero error count is reassuring only when requests are arriving and the telemetry path is functioning.

Deployment revision, service name, environment and region are often useful bounded dimensions. Order ID, email address, full URL and arbitrary exception messages are unsuitable metric labels. A route template such as `/orders/{id}` groups requests without creating one series per order. Keep individual correlation values in logs and traces under access controls.

## Instrumenting a meaningful request path

The following small Python program demonstrates the boundary without requiring a metrics library. It is a teaching endpoint, not the DispatchDesk production implementation: orders are stored in memory and disappear on restart. Its explicit limitation makes the example unsuitable for the durable acceptance objective described above. Save it as `observed_api.py` in a scratch directory on an Ubuntu, Fedora or RHEL-compatible workstation with Python 3 installed.

```python
import json
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

lock = threading.Lock()
counts = {"accepted": 0, "rejected": 0}
orders = {}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/metrics":
            self.send_error(404)
            return
        with lock:
            text = "# TYPE dispatchdesk_requests_total counter\n"
            text += "".join(
                f'dispatchdesk_requests_total{{result="{key}"}} {value}\n'
                for key, value in counts.items()
            )
        body = text.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        started = time.monotonic()
        request_id = str(uuid.uuid4())
        status = 400
        event = "order_rejected"
        try:
            if self.path != "/orders":
                raise ValueError("unsupported route")
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                raise ValueError("invalid body size")
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict) or not isinstance(payload.get("item"), str):
                raise ValueError("item must be a string")
            order_id = str(uuid.uuid4())
            with lock:
                orders[order_id] = payload["item"]
                counts["accepted"] += 1
            status = 202
            event = "order_accepted_in_memory"
            response = {"order_id": order_id, "request_id": request_id}
        except (ValueError, json.JSONDecodeError):
            with lock:
                counts["rejected"] += 1
            response = {"error": "invalid order", "request_id": request_id}
        print(json.dumps({"event": event, "request_id": request_id,
                          "status": status,
                          "duration_ms": round((time.monotonic() - started) * 1000, 3)}),
              flush=True)
        body = json.dumps(response).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

ThreadingHTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
```

Install the runtime with `sudo apt-get install python3 curl` on Ubuntu, or `sudo dnf install python3 curl` on Fedora and supported RHEL-compatible systems using their enabled repositories. These commands change the workstation's package state and require administrative rights. On subscribed RHEL, package access depends on configured entitlement and repositories. The application itself runs as your ordinary user; binding to loopback avoids exposing the teaching endpoint to other hosts.

Run `python3 observed_api.py` in one terminal. In another, from any directory, send a request and inspect the metrics:

```bash
curl --fail-with-body --silent --show-error \
  -H 'Content-Type: application/json' \
  --data '{"item":"packing-label"}' http://127.0.0.1:8080/orders
curl --fail --silent --show-error http://127.0.0.1:8080/metrics
```

The header tells the server the body format; `--data` supplies the body and selects POST. `--silent` removes the progress meter while `--show-error` preserves transport diagnostics. `--fail-with-body` makes HTTP failures return a failing exit status while preserving the JSON error body; verify that your installed curl supports it. The second command uses `--fail`, sufficient for the metrics endpoint. Inspect the returned request ID, the structured event in the first terminal and the accepted counter. No output here is presented as an executed measurement.

Send `{"item":17}` to exercise rejection. Its response should have status 400 and its log should say `order_rejected`; the rejected metric should increase. Stop the server with Ctrl-C, restart it and fetch metrics again. Counts reset and orders disappear. This is useful evidence: a counter reset is normal for a restarted process, while lost accepted orders violate a durable service contract. The next implementation step is a transaction that commits an order and an outbox record together, then counts success after commit. Instrumentation must follow that change.

## Investigating contradictory evidence

Consider an incident where acceptance metrics look normal but users report missing notifications. Begin at the affected boundary: measure the oldest outstanding outbox record and completed notification delay. Find a affected order through its business record, then use the corresponding request or trace ID to inspect commit, publish and provider-acknowledgment events. A missing publish log may be a collection failure; an unpublished durable outbox record is direct evidence that work remains.

Compare the worker's processing rate with arrival rate. If arrivals are 50 per second and completions 35 per second, backlog grows by approximately 15 per second while those conditions persist. Restarting the worker may briefly change the graph but cannot repair a sustained capacity deficit. If provider calls are timing out, increasing concurrency might worsen throttling. Recover by respecting provider limits, reducing repeated attempts and preserving work for retry. Verify that backlog age decreases and that delivery outcomes reconcile, not merely that CPU rose.

Telemetry itself can fail during the same incident. A full log disk may remove the most useful events and disrupt the application. An unavailable collector can drop spans after queues fill. Retain a lightweight independent health signal for the pipeline, and make incident procedures usable when the dashboard is unavailable. Decide which signals are essential for recovery, which can be sampled and which must remain in the transactional record.

## Exercises, review and takeaways

1. Add an event for provider acceptance. Answer guidance: emit it only after the provider acknowledges the operation; include a correlation reference and a bounded result, excluding credentials and message contents.
2. Explain why an order ID belongs in a log but usually not in a metric label. Answer guidance: logs retain individual events; metric labels create series whose count would grow with orders.
3. Define a test that distinguishes a dead worker from a broken telemetry exporter. Answer guidance: compare durable queue age and completed business records with worker/exporter health; neither dashboard absence nor process uptime proves delivery behavior.

Review whether each signal answers a named question, whether the observed boundary matches the promise, and whether a missing signal is distinguishable from zero activity. The key operational habit is to move from an impact statement to evidence that can disprove a hypothesis.

Primary context inspected on 2026-10-01: [Prometheus getting started](https://prometheus.io/docs/prometheus/latest/getting_started/) for metric scraping, and [OpenTelemetry Collector configuration](https://opentelemetry.io/docs/collector/configuration/) for the separate telemetry pipeline. The chapter's business-boundary design and Python example are original teaching material. Coordinator validation on 2026-10-01 ran the complete example with Python 3.14.7 on loopback, substituting an unused port for 8080: a valid item returned 202 with an order ID, an integer item returned 400, accepted and rejected counters each reached 1, and restarting reset accepted to 0. The test used temporary files outside the socket-restricted sandbox. No load, durability or provider integration test was performed.

