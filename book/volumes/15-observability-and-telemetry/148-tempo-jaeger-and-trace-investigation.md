---
book: The Complete DevOps Engineering Book
volume: 15
volume_title: "Observability and Telemetry"
chapter: 148
title: "Tempo, Jaeger and Trace Investigation"
slug: tempo-jaeger-and-trace-investigation
status: complete
summary: ../../_ai/chapter-summaries/148-tempo-jaeger-and-trace-investigation.md
---

# Chapter 148 — Tempo, Jaeger and Trace Investigation

**Section outline:** interpret a span tree without inventing causality; run a transient Jaeger lab; connect a Collector to a trace backend; investigate a slow dependency; compare Tempo and Jaeger operationally.

Prerequisite: [OpenTelemetry instrumentation and collectors](147-opentelemetry-instrumentation-and-collectors.md). Reuse its complete Python propagation demonstration and its explicit simulated-work boundary.

## Spans, parent relationships and timing

A trace is a set of related operations, not automatically a complete diagram of the application. Instrumented calls appear; uninstrumented calls, discarded spans and lost propagation do not. A missing database span can mean the request avoided the database, the library was not instrumented, sampling removed evidence, or export failed. Begin an investigation by asking what the instrumentation contract actually covers.

The parent relationship describes causal context. It does not always imply that the parent's recorded duration fully contains every child's duration. Asynchronous work can start after a producer span ends. A worker may continue the producer's context while its actual work occurs later. A trace UI showing an apparent gap can be accurately describing queue delay rather than a broken clock. Compare timestamps with the application's enqueue and dequeue events.

Do not sum every span duration to calculate request latency. Parallel calls overlap. If a request makes three concurrent 100-millisecond downstream calls, their sum is 300 milliseconds while the critical path might remain near 100 milliseconds plus local overhead. Nested spans can also represent the same interval at different levels. Find the path that delays the user-visible outcome, and distinguish time waiting from time actively executing.

Cross-host clocks complicate visual interpretation. Each process can measure its own duration with a monotonic clock, but a backend places spans using recorded timestamps. Clock skew can make a child appear to begin before its parent. Inspect host time synchronization and backend adjustment behavior before accusing the application of impossible ordering. A trace is evidence with known limitations, not a stopwatch attached to the entire distributed system.

An error annotation records the instrumentation's interpretation of an operation. An HTTP 404 can be an expected application outcome; a 200 can carry an incorrect business result. Choose span status and attributes to describe the contract. For DispatchDesk, provider acceptance and durable final notification state are separate observations. A successful network span cannot prove that the database recorded completion.

## A transient Jaeger lab

The official Jaeger getting-started page inspected on 2026-10-01 documents Jaeger 2.21.0 and an all-in-one configuration with transient in-memory trace storage. This is a specifically verified example release, not a permanent recommendation to use that version. Before production use, evaluate a supported release and immutable image digest from the actual registry; do not invent a digest.

On a workstation with Docker Engine configured, run the following from any directory as the account authorized to use the engine:

```bash
docker run --rm --name dispatchdesk-jaeger-lab \
  -p 127.0.0.1:16686:16686 \
  -p 127.0.0.1:14318:4318 \
  cr.jaegertracing.io/jaegertracing/jaeger:2.21.0
```

`--rm` removes the stopped container. The name identifies the lab container. The first publication exposes the query UI only on loopback; the second maps host port 14318 to the container's OTLP HTTP receiver at 4318. The unusual host port avoids colliding with the Collector from Chapter 147. No persistence is configured: stopping the process loses its in-memory traces. Pulling the image requires network access and consumes local storage.

With Podman configured on Fedora or RHEL-compatible Linux, the same lab can use `podman run` with the same arguments and fully qualified image name. Rootless Podman can publish these unprivileged ports. Ubuntu can also use a supported Podman installation; the runtime choice is independent of the distribution label. No host-directory bind mount is used, so this lab avoids SELinux volume-label complications. If you later add persistence, use the runtime's documented ownership and security-label handling rather than disabling SELinux.

Replace the Chapter 147 Collector configuration with this complete lab configuration, retaining a local receiver at 4318 and sending onward to the mapped Jaeger endpoint:

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 127.0.0.1:4318
processors:
  batch:
    timeout: 1s
exporters:
  otlp_http/jaeger_lab:
    endpoint: http://127.0.0.1:14318
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp_http/jaeger_lab]
```

The inspected current core exporter documentation names this component `otlp_http`; `otlphttp` is its deprecated alias. Older distributions may require the older name, so verify the chosen distribution rather than assuming either name is universal. This HTTP exporter uses a base endpoint and appends the signal path according to its configuration behavior; the Python exporter in the prior chapter explicitly used a full `/v1/traces` URL. Check the installed Collector exporter documentation because component configuration is release-sensitive. Restart only the disposable lab Collector after validating the selected binary's configuration. Its loopback endpoint means these processes must share the stated host network context.

Run the Python message demonstration again. Open `http://127.0.0.1:16686`, select the lab API service and find the recent `order.enqueue` operation or search for the trace ID printed by the script. Inspect the worker span's parent relationship and simulated duration. Then stop and recreate the Jaeger lab container and confirm that old data is absent. This shows the difference between receiving traces and preserving incident history. The author did not run this integration; the expected observations are reader checks.

Cleanup is explicit: stop the foreground container with Ctrl-C or run `docker stop dispatchdesk-jaeger-lab` from another terminal; substitute `podman stop` for the Podman runtime. This interrupts the lab and destroys its transient trace history. Leave production containers alone.

## Sampling limits and backend choices

A trace backend stores and queries the spans that reach it. Its search result is a biased population when sampling policies favor errors or slow requests. A search showing fifty percent errors may describe intentionally retained exceptional traces rather than the service's actual error fraction. Use the service metric denominator for impact, and use selected traces for explanation.

Tempo fits teams that want tracing integrated with Grafana and a storage/query architecture suited to their deployment. Jaeger offers its tracing-focused query UI and configurable collection/storage roles. Both can consume OpenTelemetry data in supported configurations, but the deployment model, search behavior, storage integrations and operating burden need a concrete comparison. Avoid declaring either universally cheaper or faster without a measured workload and current storage prices.

For Harbor's small VPS team, a modest trace retention window or managed backend can be preferable to operating a distributed tracing estate. Summit may use a managed service or a managed storage path because staffing is constrained. Atlas can justify centralized tracing infrastructure when many application teams share the service and the platform team owns capacity, tenancy and incident recovery. None of these paths follows automatically from request rate alone.

TraceQL provides Tempo-specific ways to search spans and relationships. Jaeger query capabilities and its storage backend determine another set of search behaviors. A dashboard's trace-ID lookup is a narrower requirement than searching arbitrary attributes across months of data. State the required investigation: retrieving a known trace, finding slow spans for one service, examining dependencies or analyzing fleet-wide patterns. That requirement affects indexing, retention, query resources and budget.

Connect a Tempo data source to its query endpoint, not its ingestion receiver. In a distributed deployment, the query frontend and distributor have different roles; their service names depend on the actual installation. The official Tempo validation guide makes this distinction explicit. A successful Grafana data-source check establishes connectivity to the query surface, while a controlled trace establishes ingestion and retrieval. Require both before calling the tracing system ready.

## Finding a slow downstream dependency

In an expanded fictional DispatchDesk scenario, acceptance p95 rises to 900 milliseconds while the deployment's ordinary CPU remains below its previous saturation point. A selected slow trace shows an `order.persist` span of 720 milliseconds. A database client span accounts for only 80 milliseconds inside it. The difference suggests local work or waiting around the query rather than a slow executed SQL statement. Candidate causes include waiting for a connection pool, transaction retries, serialization, application locks or incomplete instrumentation.

Add or inspect a bounded span for connection acquisition and compare pool wait metrics. If a request spends 600 milliseconds obtaining a connection while query execution remains 80 milliseconds, increasing database query timeout will not reduce pool wait. Examine pool occupancy, connection leaks and transaction duration. Adding application replicas can multiply connection demand and worsen the shared bottleneck. Recover by releasing leaked connections, shortening transaction scope or constraining concurrency, then verify both acceptance latency and database pressure.

A different trace shows three provider retries inside one notification attempt. Each call times out after two seconds, and backoff adds several more seconds. The root duration is a result of retry policy, not a single eight-second provider response. Inspect attempt attributes and logs, ensure duplicate-effect controls exist, and honor the workflow's deadline. Increasing every timeout may increase backlog age and tie up workers longer.

Compare slow and ordinary traces rather than selecting only the worst example. One extreme trace can reveal a mechanism but cannot establish its frequency. Tie it back to population metrics by deployment window, route and outcome. Keep trace identifiers in incident notes only under the appropriate access controls.

## Missing traces and recovery

If the printed trace ID cannot be found, check the exporter and Collector logs, receiver/exporter protocol agreement, backend acceptance and search time range. A backend outage may leave spans buffered temporarily or lost when queues overflow. A trace with only API spans suggests propagation or worker export failure. A trace with only worker spans may result from separate sampling decisions or a producer pipeline failure. These hypotheses require boundary checks.

If storage or query latency degrades, distinguish write pressure from search pressure. A broad attribute query across long retention can compete with incident-time lookups. Bound incident queries by time and service, establish ingestion capacity budgets and reserve recovery headroom. Restore backend availability and confirm a newly generated controlled trace before assuming historical gaps will backfill. Lost unsaved spans may never be recoverable; the durable order ledger must still support reconciliation.

Exercises: calculate why three parallel 100-millisecond calls need not produce 300 milliseconds of request latency; explain why error-biased trace sampling cannot estimate fleet error fraction; recreate the lab backend and account for the missing history; identify the evidence that distinguishes pool wait from SQL execution. Answer guidance: overlap changes the critical path, sampled selection changes the denominator, in-memory storage vanishes on restart, and separate acquisition/query timing localizes the database boundary.

Primary sources inspected 2026-10-01: [Jaeger 2.21 getting started](https://www.jaegertracing.io/docs/2.21/getting-started/) (page modified 2026-09-15), [Jaeger architecture](https://www.jaegertracing.io/docs/2.21/architecture/), [Tempo deployment validation](https://grafana.com/docs/tempo/latest/set-up-for-tracing/setup-tempo/test/set-up-test-app/) and [TraceQL](https://grafana.com/docs/tempo/latest/traceql/). The [core OTLP HTTP exporter README](https://github.com/open-telemetry/opentelemetry-collector/blob/main/exporter/otlphttpexporter/README.md) was additionally inspected for the `otlp_http` component name and deprecated alias. Container execution, Collector forwarding and backend searches remain untested integration steps.

