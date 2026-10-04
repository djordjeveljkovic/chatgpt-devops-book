---
book: The Complete DevOps Engineering Book
volume: 21
volume_title: "Projects and Industry Case Studies"
chapter: 210
title: "Uber Observability and Alternative Growth Paths"
slug: uber-observability-and-alternative-growth-paths
status: complete
summary: ../../_ai/chapter-summaries/210-uber-observability-and-alternative-growth-paths.md
---

# Chapter 210 — Uber Observability and Alternative Growth Paths

**Section outline:** documented observability case studies; historical scope and architecture constraints; comparing real evidence with fictional company decisions.

## Understand the reported problem and system

Uber's public engineering posts describe observability systems developed for a large, rapidly growing microservice environment. In its 2018 article about [M3](https://www.uber.com/us/en/blog/m3/), Uber explains that existing Graphite/Carbon infrastructure faced scale limitations and introduces M3 as a metrics platform with long retention and Prometheus integration goals. A later post about [M3 ingestion latency](https://www.uber.com/us/en/blog/optimizing-m3/) traces a production latency regression through its ingestion pipeline and describes profiling, rollback and deeper investigation.

Uber also documented an [alerting ecosystem](https://www.uber.com/us/en/blog/observability-at-scale/), including metrics-based uMonitor and host-focused Neris, and described [Jaeger, M3 and XYS](https://www.uber.com/us/en/blog/optimizing-observability/) in the context of tracing, sampling and metrics. The posts explain why one signal is insufficient: metrics identify a pattern, traces connect a request's dependencies, and logs provide detailed event evidence. At very high dimensionality, cardinality, storage and query costs become system design constraints.

These are dated case studies, not an assertion that the named tools or architecture remain unchanged in 2026. The public articles report selected engineering details and do not expose every tradeoff, cost, failure or internal policy. Distinguish what the source says from what a reader infers.

## Compare different growth paths

DispatchDesk is far smaller. It starts with request metrics and structured logs, adds distributed tracing when requests cross services, and chooses a managed time-series backend. It uses bounded metric labels for route, result, region and service; request identifiers remain in logs/traces with access controls. It does not need Uber's custom metrics storage simply because Uber built M3. Its next investment is based on observed query volume, retention, cardinality and operator effort.

Another organization might grow through managed cloud services, a modular monolith, a small platform team, or multiple regional products. Each path changes its limiting constraints. A custom observability platform can be justified when existing systems fail measurable scale, retention, latency, tenancy or cost requirements and there is a team to own it. Otherwise, configuration and instrumentation improvements may create more value than operating another distributed database.

Uber's M3 ingestion article offers a transferable investigation pattern: detect user/operator impact, use evidence to locate the stage that accumulates delay, mitigate with rollback when warranted, profile the critical path, and verify the improvement. Its concrete implementation depended on Uber's own ingestion architecture; another system should form its own pipeline map and hypotheses.

## Reuse methods, not architecture diagrams

For DispatchDesk's slow-order exercise, metrics reveal elevated p95, traces locate a synchronous dependency, and logs show retries. The team changes the application contract and measures order completion, queue age and duplicate rate. It adopts the cross-signal investigation method but not M3's data topology. Chapter 207 develops that fictional incident in detail.

Use public case studies as a prompt for questions: What scale or failure forced this design? Which team owned it? What did the previous system fail to do? How were correctness and migration validated? Which costs were accepted? If sources do not answer, mark uncertainty instead of inventing rationale. Revisit architecture decisions as demand, organization and provider capabilities change.

Telemetry itself has a cost and failure domain. At high cardinality, ingestion and query capacity need explicit policy about what is emitted, aggregated, retained and sampled. Sampling can preserve broad traces while retaining errors or rare slow requests through a separate policy, but the chosen rules affect representativeness. A metrics backend outage should not disable the product; alerting may need a separate path for backend health. For smaller services, begin with a handful of business and dependency signals, validate alert usefulness and estimate retention cost. Expand dimensions only when an investigation or product question needs them and when cardinality impact is understood.

 The company should also decide how long each signal remains useful and who can query it. Longer retention increases storage and index cost; shorter retention may remove context before a delayed incident is discovered. Redact secrets and sensitive identifiers at instrumentation boundaries, apply role-based access and define deletion obligations. Alert rules should be tested against known incidents and benign traffic shifts to understand false positives and missed detection. The owner should periodically review alert volume and retire rules that no longer produce a useful action.

Exercises:

1. A dashboard is slow and alerts arrive late. Which pipeline stages should be measured before replacing the metrics backend?
2. A service wants user ID as a metric label to make dashboards easier. What are the scale and privacy risks?
3. An engineer claims Uber's public M3 article proves it is the best choice for a mid-size company. What evidence is missing?
4. A trace-based investigation points to a dependency, but sampled spans are missing. How should confidence be expressed?

Answer guidance: measure collection, aggregation, ingestion, storage, query, dashboard and alert evaluation delays, plus volume/cardinality and saturation; identify which stage dominates. Per-user dimensions can create massive series cardinality, storage/query expense and sensitive-data exposure; use logs/traces under controls or bounded cohorts. Requirements, workload, operating expertise, cost, alternatives, migration and support evidence are missing. State the suspected path and uncertainty, inspect sampling/instrumentation coverage, correlate logs/metrics and seek independent evidence before declaring root cause.

Review questions:

- What problems did Uber's dated M3 and alerting posts describe?
- How do metrics, traces and logs contribute different evidence?
- Which organizational capacity is required to own a custom observability platform?
- How can another team reuse the method while choosing a different architecture?

Takeaways:

- Read Uber's observability posts as historical case studies with bounded claims.
- Instrument the whole telemetry path and account for cardinality, delay and retention costs.
- Reuse investigation methods rather than copying a scale-specific stack.
- Choose a platform from measured requirements and the team's ability to operate it.

## Sources checked 2026-10-04

- [Uber: M3 Metrics Platform (2018)](https://www.uber.com/us/en/blog/m3/).
- [Uber: Observability at Scale (2018)](https://www.uber.com/us/en/blog/observability-at-scale/).
- [Uber: Optimizing M3 Ingestion Latency (2019)](https://www.uber.com/us/en/blog/optimizing-m3/) and [Jaeger, M3 and XYS (2019)](https://www.uber.com/us/en/blog/optimizing-observability/).
- Chapters 141–150, 199 and 207 — observability design, cost and investigation.

Uber material is attributed to dated public posts; no current internal access is claimed. DispatchDesk is fictional and no telemetry system was operated.
