---
book: The Complete DevOps Engineering Book
volume: 15
volume_title: "Observability and Telemetry"
chapter: 143
title: "PromQL for Operational Questions"
slug: promql-for-operational-questions
status: complete
summary: ../../_ai/chapter-summaries/143-promql-for-operational-questions.md
---

# Chapter 143 — PromQL for Operational Questions

**Section outline:** choose the mathematical meaning of a signal; aggregate after handling counter resets; read histogram estimates; make missing data visible; validate queries against controlled events.

Prerequisite: [Prometheus and exporters](142-prometheus-and-exporters.md). Query the local Prometheus server described there. Queries use PromQL, not shell syntax; paste them into its expression browser unless a command block explicitly invokes curl.

## Counters, gauges, rates and histograms

A question such as “Are more requests failing?” has several possible meanings. The number of errors may rise because total traffic rose while the error fraction stayed constant. A five-minute error fraction may look acceptable while one customer cohort is completely broken. A per-instance graph may look uneven because requests are intentionally routed unevenly. State the population and time window before constructing the expression.

A counter records cumulative events and can reset when its process restarts. A gauge records a current quantity that can move in either direction. Do not use PromQL `rate()` on a backlog gauge: it applies counter-reset handling and can misinterpret ordinary decreases. For gauge net change use `delta()` over a range; for a fitted per-second trend use `deriv()` when its regression meaning fits the question. Neither gives completion throughput because arrivals and departures both affect backlog. To know completion throughput, instrument completed events as a counter. Keep backlog size and oldest-message age as gauges because a small backlog can contain one very old stuck message.

The teaching API exposes `dispatchdesk_requests_total{result="accepted"}` and a corresponding rejected series. Its rejection population is application validation failures, not production availability failures. Use its data to learn query mechanics without calling the result an SLO. After sending several requests and waiting for enough scrapes, inspect:

```promql
rate(dispatchdesk_requests_total[5m])
```

This estimates events per second across a five-minute range for each series, with counter-reset handling. A rate is not an integer event count; extrapolation and observation timing can yield fractional estimates. A range needs sufficient samples. Choosing a window smaller than the scrape interval cannot magically provide information between scrapes.

For a count over the same range use:

```promql
increase(dispatchdesk_requests_total[5m])
```

The estimate still depends on scrape observations and is unsuitable as a financial ledger. Durable transactional records count individual business events; telemetry estimates service behavior. When investigating a billing discrepancy, use the database or audit ledger to reconcile exact events and metrics to identify when the discrepancy began.

Aggregation changes which distinctions remain visible. Compute per-series rate before summing across process identities:

```promql
sum by (result) (rate(dispatchdesk_requests_total[5m]))
```

The service-level view keeps the result label and removes instance-level distinctions. Handling resets before aggregation avoids hiding one process's reset behind another process's counter growth. A separate instance-level panel remains useful for finding a bad replica; one view should not try to answer both population health and individual placement questions.

## Aggregation and missing series

For a production API, assume a deliberately different metric contract: `dispatchdesk_http_requests_total` has bounded labels `service`, `route`, `method`, `status_class` and `instance`. Its producer increments the counter when a response outcome is known. `status_class="5xx"` represents server failure; the denominator below includes all observed response classes. This contract is a prerequisite for these queries, not a metric supplied by the previous chapter's small Python program.

```promql
sum by (service) (
  rate(dispatchdesk_http_requests_total{status_class="5xx"}[5m])
)
/
sum by (service) (
  rate(dispatchdesk_http_requests_total[5m])
)
```

The result is a fraction; multiply by 100 only when the panel displays percentage points rather than a fraction-formatted percentage. Grafana unit choices can otherwise create a hundredfold presentation error. Investigators should inspect the raw value when a panel looks implausible.

Both sides retain the same service label, making vector matching straightforward. If the numerator keeps `route` while the denominator removes it, the series no longer align automatically. Do not add `group_left` simply to silence a matching error. Decide whether you want a per-route fraction, a service-wide fraction or each route's contribution to total service errors. Those are distinct questions requiring distinct denominators.

There are three different empty situations. A known counter that remains zero produces a zero rate when sufficient observations exist. A metric that was never initialized may produce no series. A target that disappeared produces stale or missing observations rather than a new value of zero. Replacing every missing result with zero hides failures in instrumentation and discovery.

For a known scrape target, inspect:

```promql
up{job="dispatchdesk-api"}
```

For the absence of an entire job's observed up series, inspect:

```promql
absent(up{job="dispatchdesk-api"})
```

These distinguish an observed failed scrape from no matching target observations. They do not prove that the target inventory is complete. In a replicated deployment, compare expected replicas from the deployment system with observed targets. A disappearing target can make the remaining fleet look perfectly healthy unless coverage is measured separately.

At no traffic, the error ratio may be undefined. That is a useful state rather than an inconvenience to paint green. A public API may need an independent synthetic request to establish reachability during quiet periods. A private batch worker may instead use scheduled-work freshness. The mechanism should match the service promise.

## Histograms and latency

Averages hide tails. If 990 requests take 50 milliseconds and 10 requests take five seconds, the mean is about 99.5 milliseconds. A mean-latency objective might look acceptable even though one percent of users experience an obvious stall. Choose a latency objective based on the population that matters and retain a distribution around its threshold.

Assume classic histogram instrumentation named `dispatchdesk_http_request_duration_seconds` with bounded service and route labels. It exposes cumulative bucket counters plus sum and count families. The following estimate pools observations across replicas for each service:

```promql
histogram_quantile(
  0.95,
  sum by (service, le) (
    rate(dispatchdesk_http_request_duration_seconds_bucket[5m])
  )
)
```

The `le` label identifies classic bucket boundaries and must survive aggregation. The estimate depends on bucket placement and interpolation; it is not a stored list of durations. If the objective is 300 milliseconds, include a bucket at 0.3 seconds so that the fraction meeting that threshold can be measured directly with the classic bucket counters:

```promql
sum by (service) (
  rate(dispatchdesk_http_request_duration_seconds_bucket{le="0.3"}[5m])
)
/
sum by (service) (
  rate(dispatchdesk_http_request_duration_seconds_count[5m])
)
```

This expresses the fraction at or below the configured threshold, assuming the metric contract includes that bucket. Bucket schemas must remain compatible across instances when aggregating them. A deployment that changes bucket boundaries can make an otherwise reasonable expression produce misleading intermediate results. Review instrumentation and query changes together.

Native histograms have a different representation and query shape. They can improve distribution handling but require support across the client library, scraper, storage path and querying system. This chapter intentionally uses classic histograms to make the bucket mechanism inspectable. Do not enable an experimental or release-sensitive option by copying a line without checking the complete pipeline's support.

Client-calculated summary quantiles have another tradeoff: a quantile computed on one process generally cannot be averaged into a fleet quantile. An average of replica p95 values weights replicas rather than individual requests and discards distribution information. If one replica handles nearly all traffic, treating it equally with an idle replica is especially misleading. Use an aggregatable distribution for fleet questions.

## Investigating latency and error rates

A fictional DispatchDesk deployment raises its five-minute p95 from 180 to 900 milliseconds while the request rate remains steady. Break down by route, then instance. If only `/orders` worsens across every instance, a shared database or changed code path is more plausible than one bad host. If one instance dominates errors and has a different revision, investigate deployment drift. These comparisons narrow hypotheses; they do not establish causality alone.

Query completed requests, in-flight work and dependency durations together. A timeout may make observed latency appear capped at the timeout while errors increase. Requests that hang indefinitely may not enter a completion histogram at all. An in-flight gauge and a timeout counter expose that blind spot. A latency chart containing only successful completions can improve while users fail faster, so retain outcome context.

Use a controlled sequence in the lab. Send ten accepted requests, wait for scrapes, restart the API and send ten more. Compare raw counters with `increase` and `rate` over a window covering the restart. Inspect timestamps and scrape intervals rather than expecting an exact value of twenty. The durable number of requests you intentionally submitted is a reference for interpretation; scrape interpolation means the estimated increase can differ.

To retrieve an instant query from the local HTTP API, use curl from your workstation:

```bash
curl --fail --silent --show-error --get \
  --data-urlencode 'query=sum(rate(dispatchdesk_requests_total[5m]))' \
  http://127.0.0.1:9090/api/v1/query
```

`--get` puts the form parameter in the URL query string instead of sending a POST body. `--data-urlencode` protects PromQL punctuation during URL encoding. The endpoint evaluates at the request time unless you supply a documented time parameter. The response includes status and data; inspect both, because an empty result can be a valid evaluation rather than a transport failure. Ubuntu and Fedora/RHEL need no different PromQL; their curl package installation was covered in the prerequisite.

When a query becomes slow, first estimate the series selected and the repeated work in the expression. A broad selector across all services can force a panel to inspect far more data than it needs. Recording rules can precompute recurring aggregates, but each rule creates new stored series and must retain the dimensions later investigations require. A recording rule that removes route labels saves work but cannot answer route-specific questions afterward.

## Exercises, review and takeaways

1. Explain the difference between the backlog gauge's derivative and a completion counter's rate. Answer guidance: the former is net change after arrivals and departures; the latter describes completions directly.
2. A dashboard averages p95 across five replicas. Replace its design. Answer guidance: aggregate histogram bucket rates across replicas and calculate the quantile afterward, preserving `le` for classic histograms.
3. An error panel is blank overnight. List three hypotheses. Answer guidance: no traffic with an undefined ratio; missing initialized error series; or failed collection/discovery. Check the denominator and target coverage before choosing a presentation default.
4. Calculate mean latency for the 990 fast and 10 slow requests above. Answer guidance: `(990 × 0.05 + 10 × 5) / 1000 = 0.0995` seconds; it does not describe the slow users' experience.

Review the metric type, reset handling, population, matching labels, units, window and absence behavior for every operational query. A syntactically valid expression can still answer the wrong question.

Primary sources inspected 2026-10-01: [PromQL functions](https://prometheus.io/docs/prometheus/latest/querying/functions/) for rate and histogram-function behavior; [histograms and summaries](https://prometheus.io/docs/practices/histograms/) for representation tradeoffs. Production metric contracts and fictional incident numbers are original examples. Queries were not evaluated against a running server during authoring.

