---
book: The Complete DevOps Engineering Book
volume: 16
volume_title: "Performance and Capacity Engineering"
chapter: 160
title: "Cost and Performance Tradeoffs"
slug: cost-and-performance-tradeoffs
status: complete
summary: ../../_ai/chapter-summaries/160-cost-and-performance-tradeoffs.md
---

# Chapter 160 — Cost and Performance Tradeoffs

**Section outline:** compare complete service boundaries; calculate successful-order unit economics; model recurring and migration ownership costs; test interruption and commitment assumptions; record a decision that can be revisited.

## Compare complete proposals at the same service boundary

The cheapest machine is not necessarily the cheapest service. A proposal must deliver the same durable order acceptance, notification deadline, security boundary, recovery expectations and workload. Comparing an unbacked-up VPS with a managed service that includes a tested recovery plan hides different products under one cost column. Comparing a Kubernetes cluster shared across fifty teams with a one-application cluster hides different allocation assumptions.

Harbor, Summit and Atlas therefore start with their constraints. Harbor has two developers, predictable demand and a tight cash budget. It can accept an agreed maintenance procedure and values a small operational surface. Summit has bursty demand and limited host-management capacity; managed databases, queues and ECS can fit that need. Atlas funds a platform team because many delivery teams need isolation, runtime contracts and controlled shared infrastructure. These choices can all be rational at the same order volume.

[Efficiency](159-caching-batching-and-efficiency.md) changes the work that must be purchased. [Forecasting](158-capacity-planning-and-forecasting.md) changes how much and when. Cost analysis must preserve both the resource model and its reliability assumptions. A configuration that reduces compute expense while increasing duplicate notifications or restore time has changed the service boundary.

## Unit economics needs a useful denominator

Cost per successful order can connect infrastructure spending to product value. Define “successful” precisely: durable acceptance alone, or acceptance with notification delivered within the promised deadline? Include retries in consumed resources but do not count them as additional successful orders. A service that rejects half its traffic can appear cheap per attempted request while disappointing users.

Separate variable and fixed components. Provider calls, transferred bytes and stored history can vary with work. Baseline replicas, managed-service minimums, monitoring and staff time can remain when traffic is low. A per-order average is therefore sensitive to volume. At low volume, optimizing a tiny CPU cost may matter less than reducing an unnecessary always-on component. At high volume, a small per-order saving can dominate.

Some costs belong to the delivery system rather than the serving request: CI runners, registry storage, staging environments, backup copies, on-call tooling and security maintenance. Shared services need an allocation rule. Allocating by request count might be fair for one workload and unfair for a reporting service that consumes far more CPU per request. Use a causal approximation where feasible, and expose uncertainty rather than manufacturing exactness.

Staff hours are not always cash that disappears from an invoice, but they are scarce engineering capacity. A managed service can release time for product work even if the provider bill is higher. A team can also overestimate that saving when it still needs database schema, recovery and application operations. Record which tasks transfer to the provider and which remain with the team.

## A complete fictional proposal comparison

The following numbers are invented **cost units** for a local reasoning exercise. They are not currencies, vendor prices, quotations or forecasts of a real provider. Each proposal is assumed to meet the same hypothetical workload and service boundary only after separate technical validation. The four `*_units` columns are recurring monthly amounts, and `ops_hours` is estimated recurring engineering hours per month; `migration_units` is a one-time transition estimate. The labor valuation is an explicit sensitivity input.

Save `proposals.csv`:

```csv
proposal,compute_units,storage_units,network_units,observability_units,ops_hours,migration_units
VPS-resize,90,25,10,15,12,120
ECS-managed,150,55,30,35,6,240
Kubernetes-shared,130,45,25,30,8,400
```

Save this complete Python program as `proposal_cost.py` in the same directory. Run `python3 proposal_cost.py` as an ordinary user with Python3 on Ubuntu, Fedora or RHEL. It reads local data and performs arithmetic; it makes no purchase or cloud call.

```python
import csv

successful_orders_per_month = 100_000
migration_months = 12
labor_units_per_hour_cases = (5, 20, 50)

with open("proposals.csv", newline="") as stream:
    proposals = list(csv.DictReader(stream))

for labor_units in labor_units_per_hour_cases:
    print(f"labor valuation: {labor_units} units/hour")
    scored = []
    for row in proposals:
        infrastructure = sum(float(row[key]) for key in (
            "compute_units", "storage_units", "network_units",
            "observability_units"))
        recurring = infrastructure + float(row["ops_hours"]) * labor_units
        amortized = recurring + float(row["migration_units"]) / migration_months
        per_order = amortized / successful_orders_per_month
        scored.append((amortized, row["proposal"]))
        print(f"  {row['proposal']}: monthly modeled={amortized:.2f}; "
              f"per successful order={per_order:.6f}")
    print("  lowest modeled cost:", min(scored)[1])
```

Changing the labor valuation can change the preferred proposal. The table is not a platform ranking: recurring hours, shared-cluster allocation, migration effort and resource assumptions are fictional. Run a second sensitivity case with lower order volume and inspect the per-order value. Then change the migration horizon if the product may be retired sooner. Amortizing a migration over three years is misleading when the team expects to replace the product in six months.

The program excludes taxes, support contracts, opportunity cost of delayed features, incident losses and uncertainty in staff estimates. Add them only when the organization can explain their treatment. Do not hide a poorly understood reliability risk inside an arbitrary “risk surcharge” and pretend the result is measured. A decision record can state that a proposal is technically disqualified until recovery testing succeeds, independent of its numerical score.

## Measure total ownership without duplicating costs

For a VPS proposal, include operating-system maintenance, database patching, backup automation, restore testing, certificate renewal, security updates and incident response. Explain what the team already does and what the proposal adds. Existing developer salaries are not a reason to assume their time is free; nor should every minute be counted both in a labor estimate and in an overlapping support charge.

For Summit's managed proposal, include database and queue charges, task baseline, burst consumption, load balancing, network paths, logging, backups and account controls. Evaluate data transfer across actual boundaries. A private address does not imply zero network charge. A change that sends every payload through an additional network service can become material at scale even when compute shrinks.

For Atlas, distinguish incremental service cost from allocated platform cost. A new namespace on a well-run shared cluster may have a modest incremental cost, while creating a new cluster and an on-call platform obligation is much larger. Reserve, unused fragments of nodes, control-plane services and platform engineering must be funded somewhere. Efficient bin packing must respect isolation and failure placement rather than pack every critical replica into the cheapest failure domain.

Tagging and billing allocation identify costs, but they do not fix architecture. Link cost trends to deployment releases, workload mix, retained data and observability policy. A log-volume spike may be a debug configuration change; a database bill increase may be an index or retention decision. Diagnose the cause before restricting resources that the service needs.

## Interruptible capacity requires an interruption-tolerant contract

Spot-style capacity exchanges lower cost for availability uncertainty. It can fit work that is durably queued, resumable, idempotent and not dependent on a guaranteed immediate start. It does not fit merely because a container can restart. A worker that has sent a notification but has not durably recorded its outcome still faces an ambiguous external effect after interruption.

AWS's [EC2 interruption notice documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html) describes best-effort warning and different hibernation behavior. Do not treat a warning interval as a durability guarantee. The design must recover after abrupt loss as well as after graceful termination. The [Fargate capacity-provider documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-capacity-providers.html) also states that unavailable Fargate Spot capacity is not automatically replaced with ordinary Fargate capacity. Summit must plan its baseline and interruption behavior explicitly.

A practical worker interruption test runs in staging with synthetic jobs and the existing durable queue contract. Begin a job, interrupt the worker at several boundaries, allow another worker to recover it, and reconcile provider effects against job state. Test before provider call, after an ambiguous provider timeout, after successful provider response but before durable completion, and after completion. Passing only the first case misses the hardest duplication window.

The cost comparison includes retried work, extra reserve and the engineering required for this recovery design. If a notification deadline requires immediate processing during Spot scarcity, retain an appropriately sized dependable baseline or another proven fallback. A capacity-provider weight is a placement preference, not evidence that sufficient dependable capacity exists during an interruption.

## Commitments reward stable demand and constrain change

A long-term commitment can reduce rates while making the organization responsible for a spending baseline. The inspected [Savings Plans overview](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html) describes hourly commitments over specified terms and varying eligible usage. Exact eligibility and prices require the organization's current account and contract review. This chapter neither recommends purchasing a plan nor invents savings percentages for DispatchDesk.

The planning question is how much stable eligible consumption remains after expected optimization, product change and migrations. Committing to the current peak ignores variation. Committing before a large efficiency project can lock in spending above the new need. A discount applied to waste still leaves waste. Use observed baseline behavior, scenario analysis and a clear owner for utilization review.

Separate a price commitment from a capacity guarantee. A lower billing rate does not itself ensure that a particular instance or placement is available when a failure occurs. The reliability plan still needs quotas, compatible replacements, ready reserve and recovery testing.

## Review three proposals as engineering decisions

Harbor's resize proposal can be strongest when the measured CPU or memory constraint is relieved, maintenance fits the product agreement, and tested backups preserve accepted orders. Its concentrated failure domain remains explicit. A second host might be justified for a stated recovery requirement rather than because a larger VPS looks unsophisticated.

Summit's managed proposal can be strongest when demand variability and limited operations time outweigh additional baseline and network charges. ECS tasks remain responsible for readiness, shutdown and bounded pools. RDS and SQS reduce specific operational burdens while leaving data modeling, access control and recovery validation with the team.

Atlas's shared Kubernetes proposal can be strongest when platform contracts amortize work across many teams and its isolation requirements are real. It needs actual platform staffing, scheduling reserve and supported runtime policies. A solo team adopting Atlas's design without those supporting conditions has copied the surface rather than the economics.

The final decision record names the chosen option, rejected alternatives, measured technical evidence, cost assumptions, uncertainty and reconsideration trigger. Revisit when traffic mix, team capacity or reliability requirements change. An old decision can have been correct and later become unsuitable without proving that its authors were careless.

## Exercises and answer guidance

A service cuts compute cost by twenty units but adds fifty units of logs and network transfer. What should the review conclude? Total modeled infrastructure cost rose; inspect whether the added telemetry or route is necessary and whether it improved the agreed outcome. A compute-only chart is incomplete.

A Spot worker can restart, but its external operation has no idempotency or reconciliation mechanism. Is it interruption tolerant? Restartability alone is insufficient. The ambiguous side-effect window needs a product and technical policy before interruption is treated as routine.

A shared cluster looks cheaper because platform engineering is omitted. How should the comparison change? Show incremental and allocated costs separately and explain the funding model. Do not charge one application the entire shared platform, but do not erase its operation either.

## Takeaways and verification

Compare complete services under the same customer and recovery boundary, expose cost assumptions, and test sensitivity to demand and staff time. Interruptible capacity and commitments change operational and spending obligations; they are architectural decisions as well as billing options. Official AWS documentation was inspected on2026-10-01. The proposal arithmetic is inline and fictional; no billing query, purchase, interruption experiment or provider provisioning was executed while authoring.
