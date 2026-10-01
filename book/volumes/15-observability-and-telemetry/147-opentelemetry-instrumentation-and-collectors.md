---
book: The Complete DevOps Engineering Book
volume: 15
volume_title: "Observability and Telemetry"
chapter: 147
title: "OpenTelemetry Instrumentation and Collectors"
slug: opentelemetry-instrumentation-and-collectors
status: complete
summary: ../../_ai/chapter-summaries/147-opentelemetry-instrumentation-and-collectors.md
---

# Chapter 147 — OpenTelemetry Instrumentation and Collectors

**Section outline:** preserve causal context across boundaries; instrument a complete two-stage Python demonstration; route OTLP through a Collector; choose sampling placement; diagnose fragmented or missing traces.

Prerequisite: [structured logs and Loki](146-logs-with-journald-and-loki.md). Logs retain individual outcome evidence; tracing adds timed relationships, while durable order state remains authoritative.

## Context propagation and signals

An API request and the work it creates do not become one trace because they share a service name. The caller must inject context into the carrier, and the callee must extract it before starting the receiving operation. The carrier might be HTTP headers or message attributes. A proxy that strips headers, a queue publisher that forgets attributes or a consumer that creates a fresh context breaks that chain.

OpenTelemetry separates instrumentation APIs, SDK behavior, exporters and collection. A library can emit spans through the API while the application chooses the SDK and export destination. An exporter sends observations to a backend or Collector. This separation makes backend replacement possible, but it does not make schemas, signal semantics or operational costs identical across systems. Version compatibility and supported components still matter.

A resource describes the observed entity, such as a service and its deployment environment. A span describes an operation. Avoid treating `service.name` as an arbitrary per-request value: it should identify a stable service role. A span name should identify a bounded operation such as `POST /orders` or `notification.send`, not an order ID. Sensitive and unbounded attributes deserve controls even when the trace backend can technically store them.

Trace context is not authorization. An incoming client can send propagation headers, and those values must not grant privileges or determine tenant access. Baggage carries additional contextual values and can spread farther than intended, including to third parties. Use a reviewed allowlist; never propagate credentials or personal data merely because every downstream service could find them convenient.

Asynchronous work deserves an explicit causal model. If one accepted order produces one notification, the consumer can continue its context. A batch combining many orders cannot honestly claim one parent explains every item; span links may represent those relationships more accurately. A retry can preserve correlation without making an hours-long workflow look like one uninterrupted synchronous request. Choose span lifetime to describe actual work rather than how long a record exists.

## A complete propagation demonstration

This lab simulates producer and consumer stages in one Python process with two providers. It proves the mechanism of injection and extraction without pretending to provision a real queue or deploy multiple languages. Python's providers identify the API and worker separately. The carrier is an in-memory dictionary representing message metadata; its preservation is the queue integration's responsibility in production.

On Ubuntu 24.04 LTS install `python3-venv` using `sudo apt-get install python3-venv`; on Fedora 44 and RHEL 9-compatible systems use the supported Python package/runtime from enabled repositories and verify `python3 -m venv --help` works. RHEL Python streams and Fedora release packages differ, so choose and record the installed interpreter explicitly rather than assuming the same minor version. From a scratch directory, create an isolated environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install opentelemetry-api opentelemetry-sdk \
  opentelemetry-exporter-otlp-proto-http
.venv/bin/python -m pip freeze > requirements.lock.txt
```

The environment keeps lab dependencies away from the OS Python. The install resolves available compatible packages; the freeze records the actual resolved versions for the lab. It is not a reviewed production dependency lock or a hash-pinned supply-chain policy. Network access and package installation occur when readers perform this setup. Do not run pip with sudo.

Save `trace_message.py`:

```python
import json
import time
from opentelemetry import propagate
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import SpanKind

providers = []
def make_tracer(service):
    provider = TracerProvider(resource=Resource.create({"service.name": service}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
        endpoint="http://127.0.0.1:4318/v1/traces")))
    providers.append(provider)
    return provider.get_tracer("dispatchdesk.message-lab")

api = make_tracer("dispatchdesk-api-lab")
worker = make_tracer("dispatchdesk-worker-lab")
carrier = {}
try:
    with api.start_as_current_span("order.enqueue", kind=SpanKind.PRODUCER) as span:
        span.set_attribute("app.operation", "order_acceptance_demo")
        propagate.inject(carrier)
        print(json.dumps({"event": "message_context_created",
                          "trace_id": format(span.get_span_context().trace_id, "032x")}))
    parent = propagate.extract(carrier)
    with worker.start_as_current_span("notification.process", context=parent,
                                      kind=SpanKind.CONSUMER) as span:
        span.set_attribute("app.outcome", "simulated_acceptance")
        time.sleep(0.05)
        print(json.dumps({"event": "notification_simulated",
                          "trace_id": format(span.get_span_context().trace_id, "032x")}))
finally:
    for provider in providers:
        provider.force_flush()
        provider.shutdown()
```

The sleep simulates work; it is not a provider call or a performance measurement. Explicit flushing and shutdown give the batch processor an opportunity to export before the short-lived program exits. A long-running service instead integrates SDK lifecycle with its shutdown deadline. The code never commits an order or sends a notification. Its event names and outcome attribute make that limitation visible.

Run it with `.venv/bin/python trace_message.py` after starting the Collector below. The printed trace IDs should match if propagation succeeds; the receiving span should appear as a child of the producer span in exported evidence. Remove `propagate.inject(carrier)` for a negative test: extraction then lacks the producer context and the worker's span becomes a separate trace. This is a controlled reader experiment, not an executed author claim.

## Collector pipelines and sampling

Choose a verified Collector distribution containing the components used in your configuration. Core and contributed distributions include different component sets. A valid YAML shape does not prove the selected binary recognizes every receiver, processor or exporter. Record the distribution, release and checksum, then inspect its help and component documentation.

For this isolated lab, save `collector.yaml`:

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 127.0.0.1:4318
processors:
  memory_limiter:
    check_interval: 1s
    limit_mib: 128
    spike_limit_mib: 32
  batch:
    timeout: 1s
exporters:
  debug:
    verbosity: detailed
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [debug]
```

The receiver's HTTP endpoint matches the Python exporter protocol and port. The pipeline activates the named components: declaring a receiver outside an active pipeline is insufficient. The memory limiter and batch processor bound aspects of collection work, but the illustrative memory settings are not a universal sizing prescription. Detailed debug output can reveal sensitive attributes; keep it confined to the lab and disable it for production unless access and retention justify it.

Run the selected binary from the configuration directory using its actual executable name, for example `./otelcol --config=collector.yaml` for a core binary named `otelcol`. A contributed binary may instead be named `otelcol-contrib`. Bind loopback without root privileges. Inspect startup logs for unsupported components or configuration errors, then run the Python script. The debug exporter provides locally inspectable spans but no persistent searchable backend. Chapter 148 explains the next boundary.

Sampling decides which observations are retained. Head sampling makes a decision before the full request outcome is known, often reducing SDK and network work early. Tail sampling buffers traces and decides using later evidence such as errors or duration, trading richer selection for memory, delay and stateful routing needs. Applying tail sampling after aggressive head sampling cannot recover traces already discarded. For complete traces, spans belonging to one trace must reach the sampling decision together.

In an expanded fictional scenario with 200 requests per second, eight spans per request and average serialized span payload of 700 bytes, raw payload is approximately 1.12 MB per second before protocol and storage overhead. Retaining ten percent reduces retained volume only where the sampling decision occurs; a backend tail sampler still receives the unsampled input. These estimates expose placement tradeoffs rather than promising a specific Collector capacity.

## Tracing a multi-language request

A Python API, Go worker, PHP-FPM service and Node.js integration can share the same propagation contract while using different SDK lifecycles. Standard HTTP propagation allows a proxy or language boundary to preserve causal context without sharing an in-memory implementation. The producer injects the current context into outgoing HTTP headers or message attributes; each receiver extracts it before starting the receiving span. Each language's SDK still requires compatible instrumentations and an exporter with the intended protocol.

Python process shutdown must flush buffered exports within the service's allowed exit time. A Go service typically shuts down its tracer provider with a bounded context while draining its HTTP server. A Node.js service initializes instrumentation early enough to wrap the relevant libraries and awaits SDK shutdown on termination. PHP-FPM handles request lifecycles through worker processes; process/request behavior and exporter overhead differ from a continuously running Go server. Do not copy one language's lifecycle assumptions into another merely because OTLP is shared.

Automatic HTTP instrumentation provides transport boundaries, while manual spans can describe outbox commit, deduplication or provider acceptance. Avoid duplicate client/server spans from installing overlapping instrumentation packages. A trace should help explain business work; adding a span around every helper function raises volume and visual clutter without necessarily improving diagnosis.

## Failure evidence and recovery

When traces fragment, compare context at the sender, carrier and receiver. Verify the outgoing headers or message attributes under controlled conditions without logging their full sensitive contents. Check whether the proxy allowlist strips propagation, whether the message library copies attributes, and whether asynchronous execution loses the active context. Restore propagation at the first broken boundary, then verify a known request's parent relationships.

When no spans arrive, inspect SDK recording, exporter errors, protocol/port alignment, Collector reception, processor drops and backend export independently. HTTP on 4318 and gRPC on 4317 are conventional examples, not interchangeable transports. A healthy Collector endpoint can coexist with a pipeline exporting nowhere. An SDK that exits before its batch flush can lose the only spans in a short-lived job.

If Collector memory grows, investigate span arrival rate, export latency, buffering and tail-sampling state before adding replicas. More replicas can fragment traces if routing ignores trace identity. Recover by limiting incoming volume, restoring backend connectivity, reducing retained attributes or changing sampling deliberately. Preserve customer-boundary metrics so a tracing outage does not remove the primary impact signal.

Exercises: break propagation and explain the two trace IDs; switch the exporter URL to the wrong protocol and locate the failing boundary; estimate buffered data during sixty seconds of blocked export at the scenario's raw rate. Answer guidance: missing carrier context creates separate roots; exporter diagnostics and receiver protocol configuration identify alignment; the raw payload alone is about 67.2 MB, while actual memory includes objects, queues and overhead. Review SDK, Collector and backend separately before calling the whole pipeline healthy.

Sources inspected 2026-10-01: [Python instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/), [context propagation](https://opentelemetry.io/docs/concepts/context-propagation/), [Collector configuration](https://opentelemetry.io/docs/collector/configuration/) and [Collector scaling](https://opentelemetry.io/docs/collector/scaling/). Code, package resolution, Collector startup and export were not executed during authoring; release/component compatibility requires validation.

