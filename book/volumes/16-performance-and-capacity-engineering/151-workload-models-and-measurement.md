---
book: The Complete DevOps Engineering Book
volume: 16
volume_title: "Performance and Capacity Engineering"
chapter: 151
title: "Workload Models and Measurement"
slug: workload-models-and-measurement
status: draft
summary: ../../_ai/chapter-summaries/151-workload-models-and-measurement.md
---

# Chapter 151 — Workload Models and Measurement

**Section outline:** describe offered work rather than tool settings; relate arrival rate, residence time and concurrency; choose representative populations and percentiles; build a quantitative charter; reject misleading load evidence.

Prerequisite: [observability capacity](../15-observability-and-telemetry/150-observability-at-scale.md). A load test needs a telemetry path that can survive the test and distinguish application pressure from generator pressure.

## Arrival rates, concurrency and service time

DispatchDesk begins with the canonical fictional workload: roughly one order request per second ordinarily and ten at peak, with request payloads bounded to 64 KiB. That statement is more useful than “twenty users,” because the service performs work when requests arrive. Twenty people can be idle, typing, submitting or retrying. A workload model translates behavior into operations whose resource demand can be measured.

Arrival rate is offered work per unit time. Completion rate is finished work per unit time. Concurrency is work currently resident inside a chosen boundary. Service time describes active processing at a resource; response or residence time includes waiting and other stages. Using these terms interchangeably makes capacity arithmetic appear precise while referring to different systems.

For a stable measured population, average resident work is approximately arrival rate multiplied by average residence time. If ten orders per second take 0.2 seconds inside the API boundary on average, approximately two requests are resident there. If the same offered rate encounters two-second response time, approximately twenty are resident. The increased concurrency can consume connection pools and memory even though arrival rate did not change. Stability, consistent boundaries and sufficiently representative measurement are assumptions of this relationship; a queue growing without bound is not in a steady state.

A tenfold arrival increase does not necessarily demand a tenfold CPU increase. Request mix can change: cached reads, transactional writes and notification retries have different demand. Measure work per request at the bottleneck. If one order requires 20 milliseconds of CPU, fifty orders per second consume about one CPU-second each second before other tasks and overhead. A single serial worker may reach that ceiling even when the host has several idle cores. More cores help only if the runtime and work can use them.

Queue demand extends beyond the API. Each accepted order may produce one notification, but retries can produce several attempts. At ten accepted orders per second with an average of 1.4 attempts per notification, provider-attempt demand is fourteen per second. During a provider outage, attempt demand depends on backoff and retry limits, not merely new orders. Preserve durable intent and quantify the retry amplification instead of assuming every order costs one network call.

## Open and closed workload models

An open workload schedules arrivals independently of previous completion. It asks how the service behaves when the outside world keeps offering a specified rate. A closed workload uses a fixed population that waits for its current iteration before beginning another. It asks how a bounded group experiences the system. Both can be appropriate, but they answer different questions.

Suppose twenty virtual users each submit one request then wait one second. At a 100-millisecond response time, the approximate iteration cycle is 1.1 seconds, giving about eighteen requests per second. At a two-second response time, the cycle becomes three seconds, giving about 6.7 requests per second. The generator automatically reduces pressure when the service slows. This can conceal the behavior of a real arrival stream that continues at eighteen per second during slowdown.

An open arrival-rate test needs enough generator capacity to start work on schedule. If all virtual users are busy, the generator can drop scheduled iterations. Those dropped arrivals are evidence that the requested workload was not fully generated, whether the root cause is long target responses or insufficient generator capacity. Report offered, started and completed work separately. A test configured for 100 per second is not proof that 100 per second reached the API.

Do not replay traffic blindly. Real requests can create orders, charge accounts or contact third-party notification providers. A safe isolated test uses synthetic tenants, disposable data and a controlled provider stub or approved sandbox. Its result still has limits: the stub may not reproduce provider latency, throttling or failures. Record the boundary being simulated, then separately test the provider contract within its permitted scope.

## Percentiles and representative workloads

A percentile describes a ranked population. A p95 of 300 milliseconds means the chosen population's estimated ninety-fifth percentile lies at that duration; it does not mean every user sees 300 milliseconds or that every minute has the same p95. Define whether the population includes failed responses, retries, cold starts and all routes. A successful-only histogram can improve when failures become fast.

Enough observations are needed to interpret a tail. Ten requests cannot characterize a p99 reliably. Even thousands of observations can miss a rare cold path or a particular tenant's large order. Group by meaningful bounded cohorts and include worst legitimate payloads deliberately. Do not pool a cheap health endpoint with transactional orders and call the result “API latency.”

Model data cardinality, not only payload bytes. Ten thousand queries against one cached order exercise a different working set from ten thousand distinct orders across many tenants. A database seeded with a hundred rows may keep every index page in memory while production's working set spills to disk. Use synthetic data with realistic sizes, selectivity and distributions, avoiding copied sensitive production records unless a separately approved data process permits them.

Warmup changes interpretation. A cold application may establish connections, compile code, load modules or populate caches. A steady-state experiment can exclude a clearly reported warmup, but an autoscaling readiness experiment must include startup and cache behavior because those costs affect users. The test charter states which question is being answered before anybody discards inconvenient samples.

## Writing a load-test charter

A charter makes assumptions and stopping conditions reviewable. The following complete example is a fictional Harbor experiment, intended for a disposable staging system with the same artifact and database schema as its candidate release:

```yaml
experiment: harbor-order-acceptance-baseline
question: Can the candidate sustain the canonical ten-order-per-second peak?
target:
  environment: isolated-staging
  boundary: public-order-endpoint-to-durable-order-and-intent-commit
  artifact: record-the-actual-reviewed-artifact-identity
workload:
  model: open-arrival
  ordinary_rate_per_second: 1
  peak_rate_per_second: 10
  payload_limit_bytes: 65536
  mix:
    valid_new_order_percent: 90
    valid_idempotent_retry_percent: 10
  warmup_seconds: 120
  peak_hold_seconds: 600
data:
  tenant: synthetic-load-tenant
  provider: controlled-notification-stub
  existing_orders: synthetic-representative-working-set
measurements:
  - offered_started_completed_requests
  - acceptance_status_and_duplicate_order_count
  - acceptance_latency_distribution
  - oldest_notification_intent_age
  - database_pool_wait_and_query_duration
  - application_and_generator_cpu_memory_network
stop_conditions:
  - unexpected_contact_with_real_customer_or_provider
  - durable_order_or_intent_correctness_failure
  - staging_disk_headroom_below_reviewed_floor
  - sustained_acceptance_failure_above_reviewed_limit
recovery:
  - stop_generator
  - preserve_measurements_and_failed_order_references
  - allow_or_pause_worker_drain_under_the_test_plan
  - verify_staging_returns_to_baseline
  - remove_only_identified_synthetic_test_records
```

The artifact field is a recording instruction, not an invented digest. Fill the working-set and reviewed thresholds with actual values before execution. The mix includes valid retries only if the test application implements caller-supplied idempotency keys and durable deduplication. The Chapter 141 in-memory metrics endpoint does not implement this contract and must not be used to claim this charter's acceptance outcome.

Capture the candidate artifact, configuration, host/container limits, database size and pool settings. Capture the generator version, its script and the actual scenario parameters. Record when the workload begins and when each plateau changes. These details let another engineer reproduce the question rather than merely rerun a filename.

A small Python arithmetic tool can check the workload estimate before provisioning anything. Save `workload_budget.py` in a scratch directory and run it as an ordinary user with Python 3 on Ubuntu, Fedora or RHEL-compatible Linux:

```python
rate = 10.0
residence_seconds = 0.2
cpu_seconds_per_order = 0.02
attempts_per_notification = 1.4
print(f"Average resident API requests: {rate * residence_seconds:.1f}")
print(f"CPU seconds demanded each second: {rate * cpu_seconds_per_order:.2f}")
print(f"Notification attempts per second: {rate * attempts_per_notification:.1f}")
```

Run `python3 workload_budget.py` from its directory. The results are calculations from fictional assumptions, not measured capacity. Change residence time to two seconds and explain why expected concurrency changes while CPU demand in this simplified model does not. In reality, contention and retries may change CPU per order too; the next experiment must measure that effect.

## Failure evidence, diagnosis and recovery

A team reports that twenty users passed a ten-minute test, but the candidate still collapses during a marketing burst. Inspect actual arrival rate first. If closed users slowed down and reduced offered work, the original experiment never tested the sustained arrival stream. Repeat the isolated experiment with the intended open model, adequate generator capacity and explicit dropped-iteration reporting.

If latency rises while completion throughput stops increasing, inspect where resident work accumulates. A growing pool wait points toward connection demand; a growing CPU run queue points toward execution pressure; increasing provider timeout attempts point toward retry amplification. Do not resize the application before identifying the resource that constrains useful completions.

Stop a damaging experiment by stopping new generated work, then observe drain and recovery. A test ending does not make queued work disappear. Preserve synthetic order references and reconcile one accepted order to one durable notification intent. Verify that no duplicate business effects occurred, that old work age returns to baseline and that host/database pressure settles. Cleanup removes only the identified test population through the application's reviewed data procedure; truncating a shared database is not implicit authorization from running a load test.

Exercises: compute concurrency at ten per second and two seconds residence; compare twenty closed users at 0.1 versus two seconds response plus one second think time; explain why a provider stub limits the result; define one correctness check beyond HTTP status. Answer guidance: twenty resident requests, approximately eighteen versus 6.7 iterations per second, missing real provider constraints, and durable deduplication/intent reconciliation are the required distinctions.

The review questions are whether offered work matches the real arrival mechanism, whether the data set exercises the relevant working set, and whether “passed” names a precise latency and correctness boundary. Capacity evidence begins with a defensible workload model.

Primary sources inspected 2026-10-01: [k6 open and closed models](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/) and [constant arrival-rate executor](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/). Charter and arithmetic are original fictional planning material. No load experiment or provider interaction was executed.

