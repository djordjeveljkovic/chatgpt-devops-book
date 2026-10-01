---
book: The Complete DevOps Engineering Book
volume: 15
volume_title: "Observability and Telemetry"
chapter: 150
title: "Observability at Scale"
slug: observability-at-scale
status: complete
summary: ../../_ai/chapter-summaries/150-observability-at-scale.md
---

# Chapter 150 — Observability at Scale

**Section outline:** calculate series and payload budgets; assign telemetry service objectives; inspect growth with bounded queries; survive collection/backend outages; conduct a capacity review and choose a reversible change.

Prerequisite: [search and managed telemetry workflows](149-elastic-opensearch-and-cloudwatch.md). This chapter treats the observability system itself as an operated service.

## Cardinality, storage and ingestion budgets

A production monitoring system competes for CPU, memory, disk, network bandwidth and human attention. Its demand is driven by both business traffic and instrumentation choices. An application can keep the same request rate while a new label multiplies time-series count or a debug setting multiplies log volume. Review telemetry changes as capacity changes, not merely as developer convenience.

Consider an expanded fictional Atlas scenario with 20 services, three environments, ten replicas per service, eight route templates and five status classes. A metric emitted for every observed combination can create up to 20 × 3 × 10 × 8 × 5 = 24,000 series before method, region or histogram buckets are added. A classic histogram with twelve exposed bucket boundaries plus sum and count creates fourteen series per dimensional combination, potentially 336,000 series for that family alone. Actual combinations may be sparse, but the possible product identifies a risky design early.

Now add a customer identifier with 10,000 possible values. Even if traffic never exercises the full Cartesian product, the design makes series churn follow customers rather than the service's stable shape. Querying the total service rate becomes more expensive because the backend must inspect the expanded population to aggregate it away. Removing the label in the dashboard does not remove ingestion and storage cost. Fix the producer contract or deliberately drop the dimension before storage.

Metrics, logs and traces need separate budgets. Metrics demand depends strongly on active series, scrape interval and churn. Logs depend on events, payload size, stream/index design and retention. Traces depend on requests, spans per request, attributes, sampling placement and search requirements. One ratio such as “telemetry is five percent of production compute” cannot replace those mechanisms.

Use planning estimates as hypotheses. At 100,000 active series observed every fifteen seconds, ingestion is about 6,667 samples per second. Fourteen days contain 1,209,600 seconds, so the retained sample count is roughly 8.064 billion. A measured bytes-per-sample factor can estimate block data, but memory, indexes, write-ahead logging, compaction and filesystem headroom add costs. Measure actual storage growth for the workload and chosen release instead of using a compression claim as a capacity guarantee.

For logs at 2,000 events per second averaging 700 bytes, raw payload is about 1.4 MB per second, or 120.96 GB per day before compression and indexing. If a debugging deployment doubles rate and increases payload to 1,400 bytes, raw volume quadruples. The traffic graph can remain unchanged while the log budget fails. Separate temporary debug collection from durable default policy and define an expiry for exceptional settings.

## Service objectives for telemetry

Define what responders need during an incident. Recent metrics might need to appear within thirty seconds, traces within two minutes and searchable logs within one minute for an explicitly chosen scenario. Historical reporting may tolerate longer delay. These targets are examples, not provider guarantees. Decide which freshness and retention requirements are essential before adding replicas or distributed storage.

Monitor collection coverage, ingestion freshness, dropped records, export backlog, query latency and storage headroom. A monitoring server's uptime does not prove any of these. A scraper may be healthy while discovery omits new replicas; a Collector may be alive while its exporter drops after exhausting retries; a dashboard may render quickly from old cached data. Put a timestamp or age signal close to the impact panels.

A separate lightweight synthetic check can detect the monitoring system's absence. Avoid depending solely on the system being monitored to notify about its own total outage. This can be a modest external check with a reviewed owner, not necessarily an expensive second full platform. The escalation procedure should state how to retrieve direct application, database and host evidence when the usual UI is unavailable.

Atlas's platform team can own shared ingestion and query services while application teams own instrumentation contracts. Harbor may assign both roles to the same two developers and keep fewer moving pieces. Summit can delegate infrastructure maintenance to a provider while retaining responsibility for freshness, retention and query charges. Ownership should follow the ability to change the failing boundary.

## A practical growth inspection

Use the local Prometheus API from the earlier lab as an ordinary workstation user. The following commands are read-only queries, but a broad query on a large production server can still consume substantial resources. Begin with a limited window and avoid repeatedly launching expensive fleet queries during an incident.

```bash
curl --fail --silent --show-error --get \
  --data-urlencode 'query=prometheus_tsdb_head_series' \
  http://127.0.0.1:9090/api/v1/query
curl --fail --silent --show-error --get \
  --data-urlencode 'query=sum by (job) (scrape_samples_post_metric_relabeling)' \
  http://127.0.0.1:9090/api/v1/query
```

The first inspects active-head series reported by Prometheus itself; the second compares last-scrape sample populations by job. The generated scrape metrics require observed targets and sufficient scrape success to be meaningful. Compare the timestamp and target health as well as the value. The URL is local to the host command; a remote or containerized server needs its actual reachable protected API endpoint.

To identify metric families represented in recent data, use a deliberately bounded operational query only after assessing its cost:

```promql
topk(10, count by (__name__) ({job="dispatchdesk-api"}))
```

The selector restricts one job; the grouping counts series by metric name; topk returns the ten largest counts. This can still be expensive for a very large job and does not identify every churned series over retention. Use backend-specific cardinality tooling and recorded historical growth when the instantaneous query is insufficient. Do not paste an unrestricted selector into a struggling backend simply because it is convenient.

Correlate growth with deployment history. If one metric family grows after adding an exception-message label, roll back that instrumentation change and confirm active-series growth stabilizes. Historical storage will not instantly shrink because old series and retained blocks remain. The recovery criterion is restored ingestion/query behavior and a sustainable growth trajectory, not immediate disappearance of every historical byte.

Ubuntu, Fedora and RHEL use the same HTTP API and PromQL. Host capacity evidence still uses distribution-neutral commands such as `df -h` for filesystem availability and `free -h` for memory accounting, with security/access policy respected. These commands report host state; they do not tell you which telemetry component is responsible. Inspect process/service metrics and actual data directories before changing resources.

## Buffering and telemetry outages

An export queue absorbs a temporary mismatch between arrival and completion rate. It cannot solve a sustained deficit. If telemetry enters at 10 MB per second and the backend accepts 6 MB per second, queued payload grows at 4 MB per second until a limit or recovery intervenes. A 1 GB payload budget would last roughly 250 seconds under those constant assumptions; actual queue memory includes object and metadata overhead. Use measured sizes to choose the limit.

Persistent queues can retain selected data across Collector restarts when the distribution and exporter support the intended configuration. They add disk capacity, ownership, corruption and recovery concerns. Retry policy, queue limits and backend outage duration determine how much evidence survives. No amount of buffering recovers spans dropped by the SDK before they entered the queue.

For a short backend outage, restore connectivity, observe exporter success and verify backlog drain without overwhelming the backend. For a long outage, prioritize essential metrics and outcome events, sample or drop lower-value diagnostic volume under an explicit policy, and record the gap. If the application synchronously blocks on remote telemetry, containment may require changing that path so business service can continue under a bounded logging/export policy.

A full telemetry disk can become a wider incident when colocated with application data. Separate capacity budgets and reserve headroom. Do not delete arbitrary live database or index files. Use the selected product's documented retention, snapshot and recovery procedures. The Prometheus local-storage documentation distinguishes local single-node storage, retained blocks and write-ahead state; a size target is not a replacement for filesystem safety margin.

Recovery verification includes a controlled new event or trace, advancing sample timestamps, known-target coverage, stable free space and representative query latency. Historical evidence may have a permanent gap. A postmortem should distinguish missing telemetry from missing business records so the team understands what can still be reconciled.

## Capacity review and alternatives

A quarterly Atlas review can begin with a table of measured demand: active series and churn, sample rate, log bytes, span rate, retention, p95 query duration, busiest tenant and storage growth. Add projected service onboarding and explicitly scoped incident/debug bursts. Assign owners to unexplained growth. A telemetry budget should be visible to teams before an ingestion limit suddenly removes their incident evidence.

Choose the smallest change that repairs the measured constraint. Removing an unbounded label often beats resizing. A longer scrape interval may fit slow-moving capacity signals but harm fast incident detection. Recording rules can reduce repeated query work while adding stored aggregates. Shorter retention can reduce storage while losing historical comparison. A remote backend can improve scale and availability but adds export dependencies and cost. Sharding ingestion can spread work while complicating cross-shard queries and recovery.

Distinguish vertical and horizontal telemetry scaling. More memory and faster storage on one server may be operationally simpler for Harbor, but host failure remains one domain. Multiple independent scrapers can improve collection redundancy but duplicate data unless the remote path handles replica identity deliberately. A distributed log or trace backend can scale independently by component, yet requires operators to understand queues, partitions and shared storage. The next volume applies the same reasoning to application capacity.

Exercises: calculate the histogram series product; estimate buffering during a five-minute backend outage at a 4 MB-per-second deficit; design an external check that remains useful when Grafana and its backend are unreachable; explain why reducing displayed dashboard labels does not reduce ingestion cardinality. Answer guidance: 336,000 possible histogram series, 1.2 GB raw deficit before overhead, an independently operated freshness/reachability signal with a usable direct-evidence runbook, and aggregation happens after collection unless the producer or pipeline changes.

Review whether every retained signal supports a named decision, whether capacity arithmetic includes churn and bursts, and whether the team can investigate when the preferred backend fails. Observability succeeds when evidence remains usable under the failures it is meant to explain.

Sources inspected 2026-10-01: [Prometheus storage](https://prometheus.io/docs/prometheus/latest/storage/), [instrumentation practices](https://prometheus.io/docs/practices/instrumentation/) and [Collector resiliency](https://opentelemetry.io/docs/collector/resiliency/). All capacity values are fictional planning arithmetic. No production cardinality query, outage experiment, storage recovery or benchmark was executed.

