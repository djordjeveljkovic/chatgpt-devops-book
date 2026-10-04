---
book: The Complete DevOps Engineering Book
volume: 16
volume_title: "Performance and Capacity Engineering"
chapter: 158
title: "Capacity Planning and Forecasting"
slug: capacity-planning-and-forecasting
status: complete
summary: ../../_ai/chapter-summaries/158-capacity-planning-and-forecasting.md
---

# Chapter 158 — Capacity Planning and Forecasting

**Section outline:** forecast workload by its consuming resource; model growth, seasonality and failure reserve; calculate scenario and retention budgets; inspect account/region quota limits; turn forecast triggers into owned decisions.

## Forecast demand in units the system actually consumes

Capacity planning connects a business forecast to resource demand and an operational boundary. It does not consist of extrapolating one CPU graph indefinitely. DispatchDesk's canonical starting workload is about one order request per second with short peaks near ten and a maximum request body of64KiB. A forecast might change order attempts, catalog reads, retained history, notification volume, report complexity or all of them. Those dimensions consume different resources.

A fictional Summit campaign forecasts four times as many orders. That does not imply exactly four times the database storage or CPU. Retries amplify attempts; indexes add storage; a new feature may issue more queries per order; a provider slowdown lengthens worker occupancy. An unchanged request rate can still need more capacity after a query loses selectivity as historical data grows. Preserve the workload mix and service version beside every measured capacity figure.

[Autoscaling](157-autoscaling-as-a-feedback-system.md) handles some variation inside a configured envelope. Planning defines that envelope, prepares dependencies and determines what happens outside it. A quota ceiling, database connection budget, subnet address shortage or storage growth can prevent an otherwise correct controller from delivering capacity.

Begin with three forecasts rather than a false point estimate: expected demand, a plausible low case, and a plausible high case with named causes. These are scenarios, not statistical confidence intervals unless a statistical model supports them. A high case might combine a campaign's larger audience with modest retry amplification; combining every worst imaginable assumption produces an unusable number. State which events can reasonably occur together.

## Growth, seasonality and failure reserve

Trend and seasonality operate on different time scales. Monthly retained data may grow steadily while order arrivals peak at lunch. A weekly backup can overlap a predictable campaign even when the average daily CPU is low. Keep short-window peaks for request capacity, sustained windows for queue drain and storage throughput, and longer windows for retained data. A monthly average cannot describe a ten-minute overload.

Suppose validated usable capacity is twenty attempts per second per API replica at the chosen workload mix and latency boundary. A forecast peak of seventy requires four replicas in normal operation by simple rounding. If the plan must retain that capacity after losing one replica, it requires five ready replicas, assuming work redistributes and shared dependencies remain available. If losing an entire zone removes two of the five, the one-replica model is inadequate. A reserve must name the failure it covers.

Do not count replicas that are merely requested or warming up as reserve. Nor should a “twenty percent spare” target obscure discrete failures: two replicas with twenty percent free each cannot necessarily carry all work after one disappears. For a cluster shared by several teams, per-service reserve also needs physical placement and available node capacity. Every service claiming the same spare node during a correlated failure is double-counting reserve.

Planned maintenance creates a different overlap. A rolling deployment may briefly add an API replica, raising database connection demand, or temporarily remove one, reducing serving capacity. A backup can consume storage bandwidth while a failover reheats caches. Plan the operations the team actually intends to perform while traffic continues. Failure reserve is useful only if the required secondary resources are also available.

## A complete forecasting worksheet

Create `capacity_cases.csv` with the following fictional scenarios. `observed_original_rps` is the measured rate of new logical submissions before retry amplification. `growth_factor` projects that pre-retry baseline, while `retry_factor` converts it to total API attempts under the scenario. A value of1.10 means ten percent more attempts than the projected original submissions, not a ten-percent increase in successful orders. `lost_replicas` names the modeled failure. These values are teaching inputs and should be replaced with evidence.

```csv
case,observed_original_rps,growth_factor,retry_factor,usable_rps_per_replica,lost_replicas
low,10,2.0,1.00,8,1
expected,10,3.0,1.05,8,1
high,10,4.5,1.10,8,2
```

Save this complete standard-library program as `capacity_forecast.py` in the same directory. Execute it as an ordinary user with `python3 capacity_forecast.py` on Ubuntu, Fedora or RHEL. It reads the local CSV and performs calculations; it neither queries nor changes infrastructure.

```python
import csv
import math

api_pool_max = 12
worker_connections = 40
rollout_extra_replicas = 1
connection_budget = 180

with open("capacity_cases.csv", newline="") as stream:
    for row in csv.DictReader(stream):
        demand = (float(row["observed_original_rps"]) *
                  float(row["growth_factor"]) *
                  float(row["retry_factor"]))
        rate = float(row["usable_rps_per_replica"])
        lost = int(row["lost_replicas"])
        if demand < 0 or rate <= 0 or lost < 0:
            raise ValueError("invalid capacity inputs")
        serving = math.ceil(demand / rate)
        installed = serving + lost
        connections = ((installed + rollout_extra_replicas) *
                       api_pool_max + worker_connections)
        print(f"{row['case']}: modeled demand={demand:.2f}/s; "
              f"ready replicas={installed}; "
              f"rollout connection maximum={connections}; "
              f"connections fit={connections <= connection_budget}")
```

The worksheet deliberately couples failure reserve to the connection budget. Reserving more replicas can increase their idle connection footprint even before a failure. If the high case exceeds that budget, the plan needs a smaller validated pool, a different worker budget, a database change or another explicit design adjustment. A printed `connections fit=True` cannot prove query throughput or memory capacity. Keep the pre-retry submission baseline alongside total attempts: CPU, API pools and providers consume attempts, while durable order storage should count unique accepted operations after idempotency.

Record the input measurements separately: date, release, data size, request mix, test duration, latency and correctness boundaries, warmup, dependency conditions and observed bottleneck. Rounding up a noisy unverified capacity number only creates a precise-looking error. Retest when a substantial release, dataset or infrastructure change invalidates the measurement.

## Storage forecasts need retention and amplification

Assume, illustratively, that retained order-related database data including the measured index contribution averages two KiB per accepted order. At one accepted order per second, this contributes roughly168.75MiB per day before backups, WAL, temporary space and other tables. Ninety days is about14.8GiB for that component. At ten continuously accepted orders per second, the component is ten times larger; a ten-second peak near ten is not equivalent to that sustained rate.

Logs and traces need separate retention policies and measured byte rates. A debug flag can change log volume abruptly without changing order rate. Backups require both storage and a restore-time budget. Compression ratios depend on real data. Leave space for index maintenance and temporary operations; a volume sized exactly to current live data can fail during routine database work even while logical row growth looks acceptable.

Forecast time-to-boundary rather than time-to-full alone. If the operational boundary is eighty percent of an allocated volume, compute days to that boundary using recent net growth and account for the lead time needed to expand or migrate. Deletion policies can change the trend, but prove that deletion and space reclamation behave as assumed. Deleting rows does not necessarily shrink an allocated file immediately.

## Quotas are planning inputs, not promised capacity

AWS Service Quotas distinguishes service limits and applied values, and quota increase requests can be approved, partially approved or denied. The inspected [Service Quotas documentation](https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html) makes this explicit. An approved quota also does not guarantee that the requested compute capacity is immediately available in a particular location.

For Summit, inventory the exact account and region involved in a launch. Compute, load-balancer targets, network addresses, security rules, API rates and observability ingestion may have different scopes. Do not invent default numbers from memory. An account's applied values and the service's documented limits are the evidence. Nonadjustable limits require design changes rather than a request form.

The following read-only discovery uses an existing AWS CLI v2 profile named `dispatchdesk-observer`, whose setup and permissions are prerequisites. See [Chapter 82](../09-aws-foundations/082-aws-cli-and-identity-sessions.md) for installation and profile setup, and [Chapter 215](../22-operational-reference/215-aws-cli-operational-reference.md) for command behavior. The commands run from the operator workstation as an ordinary user on any of the three Linux families. First inspect identity in its own block:

```bash
aws sts get-caller-identity --profile dispatchdesk-observer \
  --region eu-central-1 --no-cli-pager || exit 1
```

Confirm the returned Account and Arn are the intended observer identity before continuing. Do not paste the next block until that check is complete. Then list applied ECS quotas:

```bash
aws service-quotas list-service-quotas \
  --profile dispatchdesk-observer --region eu-central-1 \
  --service-code ecs --output json --no-cli-pager \
  --query 'Quotas[].{Name:QuotaName,Code:QuotaCode,Value:Value,Adjustable:Adjustable}'
```

`--service-code ecs` selects the service; `--query` projects names, discovered codes, values and adjustability from the response; JSON retains structured values; the profile and region prevent an implicit account or regional choice. Normal CLI pagination remains enabled. The [CLI reference](https://docs.aws.amazon.com/cli/latest/reference/service-quotas/list-service-quotas.html) notes that not every applied value is available through this operation. An absent item is not proof that no limit exists. No increase is requested by this example, and no fabricated output is supplied. Access-denied or missing-profile errors require correcting the observer setup, not bypassing identity checks.

Harbor's equivalent inventory is its VPS provider's supported sizes, volume limits, resize process and procurement lead time. Atlas additionally inventories node pools, scheduling constraints and team allocations. A Kubernetes resource quota is a policy boundary inside the cluster; it does not create physical capacity. Keep policy ceilings, provider ceilings and actual ready resources in separate columns.

## Turn a forecast into scheduled decisions

Every scenario should lead to a trigger, owner and deadline. A useful record says: “If weekly peak demand exceeds this measured threshold for two consecutive weeks, the service owner runs the bounded staging test and reviews the resize before the campaign date.” It does not say “monitor capacity.” Lead time includes review, procurement or quota approval, staging validation, rollout and recovery preparation.

Review forecast error after real events. If demand was lower, determine whether the campaign underperformed, the model overestimated attempts or the measurement included duplicates. If resource demand was higher at the same request rate, examine workload cost and retry behavior. Reducing reserve merely because one launch was quiet can make the next failure unsafe. Keep the forecast assumptions versioned so the team can learn rather than retroactively rewriting the prediction.

An incident can reveal a capacity forecast defect: the plan allowed six workers but only reserved provider throughput for three. Queue age rises despite low worker CPU. Recovery first respects the external limit, prioritizes deadline-sensitive work according to the product contract and controls retries. The long-term correction belongs in the shared-resource forecast and admission policy, not just a larger worker maximum.

## Exercises and answer guidance

A service needs70attempts per second and each validated replica supplies20within the boundary. How many ready replicas retain capacity after one loss? Five under the stated independent-replica model. For a zone loss, calculate the placement-specific number removed rather than reuse one.

A campaign forecast doubles unique accepted orders from a baseline of ten new submissions per second, while total attempts rise from ten to thirty per second. What changed? New logical demand rose to twenty per second while total attempt demand tripled to thirty, so attempts per logical order increased from1.0to1.5 through retries or rejected-request behavior. CPU and dependency budgets use attempts; durable order storage uses unique accepted records.

A volume has30days until the operational boundary, but migration preparation takes40days. Is current capacity sufficient? The deadline has already been missed under those assumptions. Short-term retention or expansion may buy time, but verify its effect and preserve required data.

## Takeaways and verification

A useful capacity plan includes workload cost, uncertainty, specific failures, deployment overlap, retention and lead time. Check shared-resource budgets across every scenario and keep requested capacity separate from ready capacity. Official AWS quota and CLI documentation was inspected on 2026-10-04. The CSV/Python worksheet and read-only CLI example are inline; no AWS query, quota request, production forecast validation or provider provisioning was executed while authoring.
