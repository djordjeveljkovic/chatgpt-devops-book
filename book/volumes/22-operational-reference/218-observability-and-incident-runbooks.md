---
book: The Complete DevOps Engineering Book
volume: 22
volume_title: "Operational Reference"
chapter: 218
title: "Observability and Incident Runbooks"
slug: observability-and-incident-runbooks
status: complete
summary: ../../_ai/chapter-summaries/218-observability-and-incident-runbooks.md
---

# Chapter 218 — Observability and Incident Runbooks

Keep this reference accessible outside the monitoring platform it describes. Its purpose is to choose the next discriminating observation, record a controlled mitigation and hand the incident to another engineer. [Volume15](../15-observability-and-telemetry/README.md) teaches the telemetry tools; [Volume19](../19-site-reliability-and-recovery/README.md) teaches the response process. A dashboard screenshot is useful context, but a reproducible query with its time window and target is better evidence.

## Open an incident with an observable claim

Write an initial statement containing the affected customer action, first observed time, population, severity basis and uncertainty. For example: “Summit's order acceptance remains within its current objective, but oldest pending notification age has exceeded the agreed deadline since11:20UTC; affected region and accepted-order count are still being checked.” This hypothetical statement deliberately distinguishes synchronous order acceptance from asynchronous notification.

Assign coordination, technical operations and communication responsibilities appropriate to the team. Harbor's two developers may combine roles explicitly; Atlas can separate them. Choose an update time and shared record, then allow technical responders to investigate bounded questions. Google's incident-response chapter describes the incident commander, operations lead and communications lead and why clear coordination helps; it does not prescribe identical staffing for every company. See [Google's incident response workbook](https://sre.google/workbook/incident-response/) and [Chapter183](../19-site-reliability-and-recovery/183-incident-command-and-communication.md).

| Initial question | Evidence to obtain | What it does not establish |
|---|---|---|
| Can customers complete the action? | Independent client/synthetic result and business outcomes | Process uptime alone is insufficient. |
| How broad is impact? | Region, tenant class, route and release population | One successful request is not a full recovery sample. |
| When did behavior change? | Aligned query windows, deployments, dependency and configuration events | A nearby deployment is a hypothesis, not proof of cause. |
| Is telemetry trustworthy? | Scrape/collector health, freshness, query errors and independent signals | Empty results are not zero failures. |
| What can reduce harm now? | Reversible mitigation with owner, scope and outcome check | A mitigation need not identify every contributing cause. |

## Metric lookup without inventing an SLO

Use the exact instrumentation contract from [Chapter143](../15-observability-and-telemetry/143-promql-for-operational-questions.md). Its production example counter, `dispatchdesk_http_requests_total`, has bounded service/route/method/status-class/instance labels. It is distinct from Chapter141's small teaching API counter, whose rejected population contains validation failures. Neither metric automatically implements Harbor's time-based availability objective.

| Question | PromQL pattern | Interpretation |
|---|---|---|
| Which API targets scrape successfully? | `up{job="dispatchdesk-api"}` | Tests this scrape path, not customer order acceptance. |
| Is scrape evidence absent? | `absent_over_time(up{job="dispatchdesk-api"}[5m])` | An absent selected series can indicate discovery/configuration issues; it is not the same as a present zero. |
| What response rate was observed? | `sum by (service) (rate(dispatchdesk_http_requests_total[5m]))` | Requires the production metric contract and enough samples. |
| Which service reports server failures? | `sum by (service) (rate(dispatchdesk_http_requests_total{status_class="5xx"}[5m]))` | An error rate; a fraction needs a compatible denominator. |
| Did a counter restart? | `resets(dispatchdesk_http_requests_total[30m])` | Helps interpret counter history; labels changing can create new series instead. |

Apply `rate` to individual counter series before aggregation so resets are handled in their original series. Do not apply it to a queue-depth gauge. A rising queue age, completion rate and dependency ceiling can be more diagnostic than CPU. Query functions and reset behavior are documented in [Prometheus functions](https://prometheus.io/docs/prometheus/latest/querying/functions/); histogram pooling, denominators and no-traffic cases belong to the canonical PromQL chapter.

For a lab using Chapter142's loopback Prometheus server, capture a fixed window with a bounded API request. The dates below are an illustrative incident window and should be replaced with the window under investigation.

```bash
curl --fail-with-body --silent --show-error --max-time 10 --get \
  'http://127.0.0.1:9090/api/v1/query_range' \
  --data-urlencode 'query=up{job="dispatchdesk-api"}' \
  --data-urlencode 'start=2026-10-01T11:15:00Z' \
  --data-urlencode 'end=2026-10-01T11:30:00Z' \
  --data-urlencode 'step=30s' \
  --data-urlencode 'timeout=5s'
```

`--get` sends encoded parameters in a query string, `step` is evaluation spacing and `timeout` bounds server evaluation subject to server limits; curl's `--max-time` bounds the whole client operation. Inspect the HTTP status and JSON envelope, including warnings. A range result is not raw samples at every original scrape instant. The [Prometheus HTTP API](https://prometheus.io/docs/prometheus/latest/querying/api/) documents these parameters and error responses. For an authenticated production endpoint use its approved access path; do not expose the backend to the internet to make this command work.

## Logs and traces: fix the window first

In Grafana Explore select the intended data source, tenant/organization scope, absolute UTC range and relevant labels before searching. A dashboard variable can hide the affected release or region. Preserve the query and range in the incident record and identify any transformation or sample limit. [Grafana Explore](https://grafana.com/docs/grafana/latest/explore/) supports investigation across configured sources; cross-source correlation still depends on correct timestamps and instrumentation.

For Chapter146's local Loki lab, this command requests a bounded stream using its `service="dispatchdesk-worker"` and `environment="lab"` labels. The labels must actually exist in the target installation.

```bash
curl --fail-with-body --silent --show-error --max-time 10 --get \
  'http://127.0.0.1:3100/loki/api/v1/query_range' \
  --data-urlencode 'query={service="dispatchdesk-worker",environment="lab"} |= "provider_timeout"' \
  --data-urlencode 'start=2026-10-01T11:15:00Z' \
  --data-urlencode 'end=2026-10-01T11:30:00Z' \
  --data-urlencode 'limit=100' \
  --data-urlencode 'direction=forward'
```

This literal text filter searches for the literal `provider_timeout` present in Chapter146's controlled event; it does not recognize every failure or parse the JSON outcome field. A successful result capped at100 entries can be incomplete. Narrow the window or selector deliberately and retain evidence without repeatedly issuing an expensive unbounded search. The [Loki HTTP API](https://grafana.com/docs/loki/latest/reference/loki-http-api/) documents range, limit and direction. Tenant/authentication requirements belong to the configured gateway, and production access may differ from the single-tenant lab.

To correlate a request, obtain an authorized request or trace ID from a bounded event, then use the trace backend from [Chapter148](../15-observability-and-telemetry/148-tempo-jaeger-and-trace-investigation.md). Look for time spent waiting, retries and propagation breaks. A missing trace may result from sampling, exporter backlog, retention or permissions. A sampled trace showing a slow database operation is evidence about that request, not automatically every customer request. Avoid putting IDs into unbounded metric labels or copying personal payloads into a shared incident channel.

## Symptom-to-next-observation index

| Symptom | Next discriminating observation | Controlled response to consider |
|---|---|---|
| High API latency with low CPU | Queueing, thread/event-loop waits, pool saturation and dependency latency | Bound admission or recover a dependency; extra replicas can increase connection pressure. |
| High API latency with CPU pressure | Per-instance distribution, throttling, work per request and recent code path | Reduce expensive work, restore a release or add measured capacity within dependency budgets. |
| Pending notifications age while workers are healthy | Arrival/completion rate, provider quota, retries and poison messages | Respect downstream ceiling; isolate poison work and verify duplicate semantics. |
| Failures on one new replica | Release/configuration/platform difference, readiness and traffic assignment | Remove that replica from traffic through its controller and preserve its evidence. |
| Logs disappear during an outage | Disk, collector queue, authentication, backend health and retention | Restore the telemetry path while checking independent business evidence. |
| Database throughput falls | Active/waiting sessions, locks, I/O, connection budget and query changes | Mitigate the specific contention; terminate a session only after transaction impact assessment. |
| One region looks empty | Discovery and ingestion freshness versus actual request/business population | Establish whether traffic moved or telemetry disappeared before declaring recovery. |

For PostgreSQL, a bounded activity observation can distinguish wait categories without fetching full SQL text. Run through an authorized database session and interpret visibility according to the role's privileges.

```sql
SELECT state, wait_event_type, wait_event, count(*) AS sessions
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state, wait_event_type, wait_event
ORDER BY sessions DESC;
```

This query does not identify every blocker or prove a wait caused the incident. PostgreSQL documents activity visibility and wait categories in its [statistics system](https://www.postgresql.org/docs/current/monitoring-stats.html). The distributed-data volume teaches lock investigation and transaction effects; this lookup deliberately stops before a destructive intervention.

## Record a mitigation and recovery

Use a short transaction record: observation and query, hypothesis, intended change, scope, responsible engineer, expected effect, deadline, stop condition, recovery action and actual result. Make one coordinated change when feasible. If several responders change pools, replicas and timeouts simultaneously, both diagnosis and rollback become harder.

For example, Summit observes a provider limit of90 notifications/second and demand above it. Increasing workers may increase retries while completion remains capped. A controlled admission/queue policy needs an explicit customer contract, maximum age and durability check. The queue arithmetic in [Chapter217](217-scaling-and-architecture-decision-tables.md) helps distinguish individual waiting time from full backlog drain. Do not call the incident resolved merely because API acceptance stayed healthy while notifications aged.

Recovery evidence should show the customer outcome restored, traffic/population accounted for, backlog within policy, replicas/controllers stable and telemetry fresh. Observe for a window justified by workload recurrence and delayed failures. Include any temporarily relaxed control, manual change or outstanding data reconciliation with an owner and deadline.

## Handoff template and practice

Copy this original template into your team's approved incident record and fill every uncertainty honestly.

```text
Incident / severity / coordinator:
Affected customer action and population:
First observed time / current UTC time / next update:
Current known facts, query links and absolute time windows:
Hypotheses supported / ruled out / still untested:
Changes made, identities, scope and observed effects:
Current service, backlog and data-integrity state:
Next bounded question, owner and expected decision:
Recovery/stop conditions and dependencies:
Temporary controls, remaining risks and explicit owners:
Incoming responder's acknowledgement:
```

Practice with two ambiguous signals: `up=1` while customers time out, and an empty dashboard while support reports healthy orders. In the first, scrape availability differs from service outcome; inspect the customer path and dependencies. In the second, compare discovery/ingestion freshness and business evidence before concluding either outage or recovery. Then rehearse a handoff in which the outgoing engineer cannot stay available: the incoming engineer should be able to reproduce the current query and explain the next decision.

Primary tool and incident documentation was inspected on2026-10-01. Shell snippets were syntax checked; the Prometheus/Loki queries and PostgreSQL observation were not executed against live backends for this reference. Local HTTP instrumentation verification is documented in Chapter141 and does not establish end-to-end monitoring operation.
