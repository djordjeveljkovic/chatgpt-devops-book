---
book: The Complete DevOps Engineering Book
volume: 22
volume_title: "Operational Reference"
chapter: 217
title: "Scaling and Architecture Decision Tables"
slug: scaling-and-architecture-decision-tables
status: complete
summary: ../../_ai/chapter-summaries/217-scaling-and-architecture-decision-tables.md
---

# Chapter 217 — Scaling and Architecture Decision Tables

Scaling decisions begin with a service contract and evidence of the limiting resource. This reference gathers the questions that prevent “add replicas” or “buy a larger server” from becoming a substitute for diagnosis. The mechanisms and experiments belong to [Performance and Capacity Engineering](../16-performance-and-capacity-engineering/README.md), [Distributed Systems and Data Operations](../17-distributed-systems-and-data-operations/README.md), and [Architecture and Platform Engineering](../20-architecture-and-platform-engineering/README.md).

Separate the required customer outcome from its current implementation. DispatchDesk must durably accept valid orders and eventually process notification intent. That does not require its API, worker and database to scale in the same way. A faster API can worsen a notification backlog if the provider's throughput is unchanged. More application processes can exhaust the database's connection allowance even when each process uses less CPU.

## Choose an intervention from the evidence

| Evidence under a representative workload | Candidate intervention | Evidence needed before accepting it |
|---|---|---|
| Application CPU is the limiting resource and work is parallelizable | More cores, optimized code or more independent processes | Profile attribution, realistic per-instance throughput, correctness under concurrency and the shared dependency ceiling |
| One operation is largely serial | Faster single-core execution, a different algorithm or reduced work | Critical-path measurement; extra idle cores do not prove lower latency |
| Memory pressure follows the legitimate working set | Larger memory or a redesigned working set | Retention/allocation evidence and the effect of restart or workload size |
| Memory rises without a workload explanation | Find a leak or unbounded retention | Repeatable growth and allocation/lifetime evidence; a larger limit merely delays failure |
| Database time dominates | Query/index/transaction changes, data distribution or a measured database resize | Plans, lock waits, I/O, connection usage and unchanged correctness |
| Provider rate limit dominates worker throughput | Negotiated quota, eligible batching, another delivery route or admission policy | The actual contract, duplicate handling, delay objectives and cost |
| A hot key or partition dominates | Change placement, partitioning or the operation | Distribution evidence; adding unrelated capacity may leave the hot boundary intact |
| Occasional predictable bursts exceed capacity | Headroom, scheduled scaling or a bounded queue | Burst duration, startup delay, maximum acceptable waiting and post-burst drain time |
| One failure domain exceeds the acceptable outage | Independent placement and tested recovery | Correlated-dependency analysis, surviving capacity, state authority and a recovery rehearsal |

The interventions are alternatives to test, not universal prescriptions. Google's published [overload discussion](https://sre.google/sre-book/handling-overload/) illustrates why overload control and useful work matter alongside raw capacity. Apply that principle to the actual system rather than copying Google's organizational scale.

## Vertical versus horizontal scaling

| Dimension | Vertical change | Horizontal change |
|---|---|---|
| Capacity mechanism | Give a machine or process more of a constrained resource | Add independent work-serving units and distribute work |
| Application implications | May preserve a simple local-state design; actual benefit depends on its resource use | Requires a usable shared-state, partitioning or stateless-execution contract |
| Operational change | Can require restart, replacement or migration; rehearse interruption and recovery | Requires discovery, balancing, readiness and controlled replacement |
| Ceiling | Available hardware, platform limits, serial work and economics | Shared dependencies, coordination, skew, quotas and operational overhead |
| Failure implications | A larger machine is still one machine | Independent placement can reduce some failure impact; shared dependencies remain |
| Evidence of success | Useful throughput/latency improves for the same valid workload | Total useful capacity rises while correctness, tail latency and dependencies remain acceptable |

For Harbor, the small VPS company, a measured resize can be a sound choice. Its two developers avoid introducing a shared deployment platform before they can operate it. They still need a restore procedure and must accept or address the single-host interruption. For Summit, managed services can separate API capacity from queue and database maintenance. For Atlas, several teams may justify Kubernetes' shared workload interface; this changes placement and operations, not the fundamental database or provider limit.

The routes are not maturity levels. A large server can remain appropriate for a deliberately bounded product, and a small service can need independent availability because its interruption is expensive. Review workload, business consequence and staffing rather than treating a customer-count milestone as an automatic platform migration.

## A numerical capacity review

The following numbers are fictional planning observations, not a benchmark produced during authoring. Assume DispatchDesk has grown from its first 1–10 requests/second exercise to a sustained peak of 120 valid order requests/second. In a representative test, one API replica supports 30 requests/second while meeting the stated latency and correctness limits. The result already includes its normal database interaction; it is not a claim that arbitrary endpoints share this throughput.

At a nominal utilization target of 70%, the capacity estimate is:

```text
replicas = ceiling(arrival_rate / (per_replica_capacity × target_utilization))
         = ceiling(120 / (30 × 0.70))
         = 6
```

Six replicas provide a nominal 180 requests/second and run at about 66.7% of that estimated capacity. If one is unavailable, five provide 150 and the same workload consumes 80%. If 70% must also hold after one replica is lost, choose at least seven under these assumptions. Decide whether the degraded 80% case still meets the latency contract; utilization alone cannot answer that.

This calculation assumes comparable replicas, sufficiently balanced work and an unchanged shared dependency. It does not predict a percentile from first principles. CPU utilization is not interchangeable with a capacity fraction derived from a throughput test. Validate the proposed count with realistic traffic, placement and a controlled failure, and record uncertainty in the measured capacity. [Workload Models and Measurement](../16-performance-and-capacity-engineering/151-workload-models-and-measurement.md) and [Capacity Planning and Forecasting](../16-performance-and-capacity-engineering/158-capacity-planning-and-forecasting.md) explain how to build that evidence.

Now examine database connections. If each of six API processes permits a pool of 20 connections, their configured maximum is 120, before workers and maintenance sessions. A database application allowance of 80 cannot support that maximum simultaneously. Reducing the API pool to ten per replica gives a maximum of 60, leaving 20 for explicitly allocated worker and operational needs. That arithmetic still requires queueing and latency tests: a smaller pool can become a useful concurrency bound or an excessive wait point depending on workload.

An autoscaler that sees API CPU and adds replicas without understanding the connection budget can make the outage worse. Connection establishment, backend memory, lock contention and retries can increase even while request-serving processes appear healthy. Test the whole demand path and bound connection/retry behavior before increasing the replica ceiling.

## Notification capacity is a different problem

Assume every accepted order creates one notification intent and the provider permits 90 useful notifications/second. During a ten-minute peak of 120 orders/second, the theoretical backlog increase is:

```text
backlog_growth = (120 - 90) × 600 = 18,000 notifications
```

Adding worker concurrency cannot exceed a hard provider limit. It may instead produce more throttled attempts and consume quota on retries. If traffic subsequently returns to 60 orders/second while useful processing remains 90, the backlog drains at 30/second, taking roughly ten minutes to return to zero under these idealized assumptions. Individual FIFO waiting time near the peak boundary is approximately backlog divided by service rate, or 200 seconds; total drain time and an individual message's wait are different measures.

These estimates ignore provider latency variation, retries, prioritization and other traffic sharing the quota. Measure oldest-work age and useful completion rate rather than interpreting queue depth alone. If the product promises notification within one minute, this design fails that promise despite eventually draining. Options include negotiating capacity, reducing eligible work through legitimate batching, routing through an approved alternative, or changing admission and delivery expectations with the product owner. Losing accepted intent is not a scaling solution.

## Select the state and deployment boundary

| Decision | Simpler option can fit when | Added complexity is justified when |
|---|---|---|
| Local disk or remote durable storage | One host and an explicit backup/recovery boundary meet the requirement | Multiple workers, independent replacement or durability constraints require a separate data boundary |
| Monolith or separately deployed service | One team can change/release a coherent product safely | Independent ownership, lifecycle or failure isolation is a demonstrated need |
| Native service, container host or orchestrator | A few workloads have clear supervision and lifecycle procedures | Placement, tenant policy and many independent deployments justify a shared platform |
| Managed database or operated database | The service fits managed features and the team benefits from delegated maintenance | Required control or unsupported features outweigh staffing, upgrade and recovery work |
| Read replica or partitioning | Read load can tolerate its consistency and routing contract | Data size/write distribution or authority boundaries require a deeper redesign |
| Active-passive or active-active regions | A tested failover objective can satisfy the business | Latency or interruption requirements justify authority, conflict and reconciliation complexity |

For each row, identify the decision owner, the remaining failure modes and the trigger for reconsideration. An operationally simple design with an honest recovery limit can be better than a supposedly redundant design nobody has restored. A region does not become independent merely because the API replicas moved if both depend on the same identity, registry or writable database boundary.

## Scaling actions need a verification plan

In an already configured Kubernetes lab, the following is a real change to the named workload:

```bash
book_context='dispatchdesk-lab'
book_namespace='dispatchdesk'
kubectl --context "$book_context" --namespace "$book_namespace" \
  scale deployment/dispatchdesk-api --replicas=6
kubectl --context "$book_context" --namespace "$book_namespace" \
  rollout status deployment/dispatchdesk-api --timeout=120s
```

Replace the context and namespace with verified lab values. `scale` sets the desired replica count, while rollout status observes a controller condition. Neither applies the capacity reasoning automatically. An HPA or GitOps controller may own or overwrite that field; use the intended source of truth. Before executing, confirm resource requests, node capacity, shared budgets and reversal conditions. Record the previous desired state and use a controlled compatible change to return to it if the experiment harms the service.

For a VPS resize, preserve the provider's instance and storage identity, take an appropriate recovery point, rehearse the restart/replacement procedure and verify the original customer path afterward. Do not assume a snapshot of a running database is a complete consistent application backup. [Vertical Scaling Decisions](../16-performance-and-capacity-engineering/155-vertical-scaling-decisions.md) and [Horizontal Scaling Decisions](../16-performance-and-capacity-engineering/156-horizontal-scaling-decisions.md) provide detailed workflows.

## Decision record and review drill

Write a short record containing the affected journey, measured workload, limiting resource, candidate options, predicted effect, correctness/failure constraints, cost assumptions, experiment, rollback and review trigger. Include staff time and recovery work in the cost model. Hypothetical cost units can compare designs, but they are not provider prices.

Exercise: at the same 120 requests/second, capacity improves to 40 per replica after a measured optimization. At 70% normal utilization, the estimate becomes ceiling(120/28), or five replicas; strict tolerance of one loss at that target requires six. Re-run dependency and connection calculations rather than only changing the replica number.

Exercise: the peak lasts five minutes instead of ten. The provider-limited backlog grows by approximately 9,000 under the same constant-rate assumptions. Explain why that may change a delivery-delay decision without changing the API's durable-acceptance requirement. Then add a provider outage and determine which assumptions no longer hold.

The senior habit is to identify the actual ceiling, predict the proposed intervention's effect, test the contract and preserve an escape route. Keep the decision reversible where possible and expand complexity when evidence makes its benefit clear.

## Verification

The numerical workload, capacities, pool budgets and provider quota are explicitly fictional examples; arithmetic was checked during authoring, not derived from a live benchmark. Google's overload chapter was inspected on 2026-10-01 as a source of overload-control context. No scaling, load generation, provider request or infrastructure change was executed. Syntax and cross-reference validation are separate from capacity and failure testing.
