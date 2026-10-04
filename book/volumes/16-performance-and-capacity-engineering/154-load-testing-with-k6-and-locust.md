---
book: The Complete DevOps Engineering Book
volume: 16
volume_title: "Performance and Capacity Engineering"
chapter: 154
title: "Load Testing with k6 and Locust"
slug: load-testing-with-k6-and-locust
status: complete
summary: ../../_ai/chapter-summaries/154-load-testing-with-k6-and-locust.md
---

# Chapter 154 — Load Testing with k6 and Locust

**Section outline:** assemble an isolated teaching target; generate an explicit arrival stream with k6; model a waiting user population with Locust; separate warmup and correctness; diagnose generator ceilings and recover staging.

Prerequisite: [shared resource bottlenecks](153-disk-network-and-connection-bottlenecks.md) and the charter in [Chapter 151](151-workload-models-and-measurement.md). Every run needs a named question and a defined stop condition.

## Open and closed workload models

k6 and Locust execute scripted interactions and report observations. They cannot decide whether the scripted interaction represents DispatchDesk's users or whether HTTP success corresponds to a correct order. Choose the model before choosing virtual-user count. A k6 arrival-rate executor can schedule iterations independently of prior completion; the Locust example below uses users that wait between tasks and therefore couples their request rate to completion time.

Use k6 when a JavaScript test and explicit arrival scheduling fit the experiment. Use Locust when Python-based user behavior, reusable application helpers and interactive user-population scenarios fit. Both require generator headroom and careful metric interpretation. Neither an HTTP client nor a script automatically behaves like a browser with rendering and asset loading.

The complete local teaching target below responds to one read-only endpoint. It deliberately has no database, authentication, order acceptance or notifications. Its purpose is to assemble the tools without causing real business effects. Passing this lab cannot establish DispatchDesk capacity. Save `load_target.py` in a new scratch directory:

```python
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/healthz":
            self.send_error(404)
            return
        body = json.dumps({"status": "lab-ready"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, format, *args):
        pass

ThreadingHTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
```

The standard-library server is a lab responder, not a production deployment stack. Loopback confines it to the local host. Run `python3 load_target.py` as an ordinary user; Ctrl-C stops it. Use an unused local port if 8080 is occupied, changing both test targets consistently. Do not kill an unknown listener to make the lab fit.

Install a verified k6 release through the official supported route. For equal Linux treatment, the upstream archive matching the workstation architecture can be unpacked in this user-owned directory on Ubuntu 24.04, Fedora 44 or RHEL 9-compatible systems. Verify its published checksum, record the release and run the unpacked binary's version command. This avoids assuming that a distribution package name supplies the intended release. Production CI should pin the approved tool artifact and review upgrades independently from test changes.

## An explicit k6 arrival stream

Save `health-arrivals.js` beside the target program:

```javascript
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    health_arrivals: {
      executor: 'constant-arrival-rate',
      rate: 5,
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 10,
      maxVUs: 20,
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
    http_req_duration: ['p(95)<500'],
    dropped_iterations: ['count==0'],
  },
};

export default function () {
  const response = http.get('http://127.0.0.1:8080/healthz', {
    timeout: '2s',
    tags: { name: 'GET /healthz' },
  });
  check(response, {
    'HTTP 200': (r) => r.status === 200,
    'expected lab body': (r) => {
      try { return r.json('status') === 'lab-ready'; }
      catch (_) { return false; }
    },
  });
}
```

The scenario requests five iterations per second for thirty seconds. One iteration performs one request, making iteration and request rate comparable in this specific script. Preallocated users provide execution capacity; the maximum bounds further allocation. They are not five simultaneous users. The timeout bounds each client attempt, and the name tag gives statistics a stable operation label.

The checks inspect status and body, while thresholds turn aggregate requirements into the tool's pass/fail outcome. A failed check alone and a failed threshold are different mechanisms; keep both their meanings visible. These thresholds normally determine the final test result after metrics are collected; they do not stop this run immediately when a limit is crossed. If a production-like test needs a fast safety abort, k6 supports `abortOnFail: true` on a threshold, optionally with `delayAbortEval` so startup samples do not trigger premature abort. Retain an independent wall-clock limit and operator stop path. The dropped-iterations threshold prevents a green latency report from hiding that the generator failed to start the requested schedule. The latency threshold is a fictional lab requirement of 500 milliseconds at p95, not a production objective.

From the lab directory run `./k6 run health-arrivals.js` using the unpacked executable named `k6`. Inspect the exit status and summary. Expected evidence includes started/completed iterations, failed requests, check results, latency distribution and dropped iterations. Do not infer exact request count merely from rate multiplied by duration; inspect actual completion, interruption and scheduling evidence. This integration was not executed during authoring.

## A Locust user population

Create an isolated Python environment for Locust. On Ubuntu use the supported `python3-venv` package if needed; on Fedora/RHEL use the enabled supported Python runtime and verify its venv capability. Run as an ordinary user from the lab directory:

```bash
python3 -m venv .locust-venv
.locust-venv/bin/python -m pip install locust
.locust-venv/bin/python -m pip freeze > locust-requirements.lock.txt
```

Package resolution requires network access and records the actual selected versions. The freeze is lab evidence, not a complete production hash-pinned dependency policy. Do not install into the OS interpreter with sudo. Save `locustfile.py`:

```python
from locust import HttpUser, task, between

class HealthVisitor(HttpUser):
    wait_time = between(0.5, 1.0)

    @task
    def inspect_health(self):
        with self.client.get("/healthz", name="GET /healthz",
                             timeout=2, catch_response=True) as response:
            if response.status_code != 200:
                response.failure("Expected HTTP 200")
                return
            try:
                valid = response.json().get("status") == "lab-ready"
            except ValueError:
                valid = False
            if not valid:
                response.failure("Unexpected lab response body")
```

The user waits between half a second and one second after a task. `catch_response=True` lets the test mark a response as failed based on its body even when HTTP status is successful. Grouping under a stable name keeps operation statistics bounded. The base target comes from the command rather than being silently embedded in a class attribute.

Run a bounded headless experiment:

```bash
.locust-venv/bin/locust -f locustfile.py \
  --headless --users 5 --spawn-rate 1 --run-time 30s \
  --host http://127.0.0.1:8080 --csv locust-health
```

The file flag selects the complete script. Headless mode avoids the UI; user count targets five concurrent user objects; spawn rate introduces one per second; run time bounds the test from its start; host selects the loopback target; CSV prefix writes result artifacts in the current lab directory. At timeout, Locust stops running tasks immediately by default, without waiting for in-flight requests. Add `--stop-timeout 5s` when the experiment needs a bounded grace period for active task iterations to finish; verify the installed release's behavior and choose the grace period to fit the task. Review output and exit behavior before making a CI gate depend on them. Do not assume that the k6 and Locust commands generate the same rate: one schedules five arrivals per second, while the other schedules five waiting users.

## Warmup, test data and correctness

For the actual staged DispatchDesk experiment, replace the read-only teaching operation with the authenticated order contract in an isolated staging environment, not with an arbitrary public URL. A test tenant must be identifiable for reconciliation and cleanup. Each new order gets a unique caller-supplied idempotency key; a retry reuses its original key. Record returned order IDs under controlled access and verify one durable order plus notification intent per logical submission.

Do not make every test iteration generate a new metric label or an unbounded result name. Use route templates for operational statistics while keeping individual test references in a restricted reconciliation artifact. A failed body assertion should be visible even when the status is 202. A status alone does not prove the service committed the intended record or applied the tenant boundary.

Warm the selected candidate only when the charter asks about steady-state behavior. Measure cold startup separately for rollout and autoscaling. Use a representative synthetic database working set, explicit cache policy and a controlled provider boundary. A local health responder's timing cannot substitute for transaction and provider-path evidence.

Run smoke validation at one request per second, then the canonical ten-per-second peak, then explicitly named growth plateaus only after checking headroom and correctness. Hold each plateau long enough to observe queues and resource behavior, not merely the first seconds of successful cache hits. Change one important dimension at a time when the aim is causal comparison.

## Failure evidence, diagnosis and recovery

If k6 reports dropped iterations, compare target duration and generator CPU/memory before raising VU limits. A slow target can need more execution slots to maintain the intended offered rate; a saturated generator can fail independently. Scaling the generator without checking resource capacity moves the failure into another limit. Report the test as incomplete until the intended schedule is demonstrated.

If Locust throughput falls as latency grows, the closed-user model is behaving as designed. It may accurately describe users waiting, but it cannot establish a fixed external arrival stream. Select the model appropriate to the question instead of tuning wait time to manufacture an attractive number.

If correctness fails, stop new work immediately and preserve evidence. Drain or pause workers according to the charter, reconcile durable state and remove only identified synthetic records through the reviewed procedure. A load test finishing leaves its created work behind. Stop the local lab responder with Ctrl-C; its GET-only tests create no business records. CSV and lock files remain as local artifacts and can be retained or removed deliberately after review.

Exercises: compare the two scripts' offered-work mechanisms; break the body assertion and inspect failure evidence; explain why dropped iterations invalidate a fixed-rate capacity claim; design an idempotent retry check for staging. Answer guidance: independent arrivals versus waiting users, content validation must affect recorded failure, unstarted work never reached the target, and repeated use of one key must preserve one logical order/intent.

## Review questions

- Does the chosen executor preserve the real arrival process when the target slows down?
- What makes a response an accepted order rather than merely an HTTP success?
- How can dropped iterations, generator saturation or early threshold abort distort a capacity claim?
- Which staging data and external effects must be reconciled after test shutdown?

## Takeaways

- Match the load model to the question: k6 arrival-rate scenarios schedule offered work independently, while this Locust user model waits between tasks.
- A test script must assert response meaning and business correctness; a successful HTTP status alone is insufficient.
- k6 thresholds report whether criteria passed, and only abort early when configured to do so; keep separate run-time and operator stop controls.
- Locust headless duration bounds the run, but its default shutdown interrupts tasks; use a bounded stop timeout when an iteration needs grace to finish.
- Protect staging, bound test data, inspect generator health and dropped work, then drain and reconcile generated records after the run.

Sources inspected 2026-10-04: [k6 installation](https://grafana.com/docs/k6/latest/set-up/install-k6/), [arrival executor](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/), [thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/), [Locust script model](https://docs.locust.io/en/stable/writing-a-locustfile.html) and [headless execution](https://docs.locust.io/en/stable/running-without-web-ui.html), the latter pages showing Locust 2.46.6. No tool installation, load execution, staging order or provider integration was performed during authoring.
