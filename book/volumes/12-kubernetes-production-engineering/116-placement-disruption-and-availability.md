---
book: The Complete DevOps Engineering Book
volume: 12
volume_title: "Kubernetes Production Engineering"
chapter: 116
title: "Placement, Disruption and Availability"
slug: placement-disruption-and-availability
status: complete
summary: ../../_ai/chapter-summaries/116-placement-disruption-and-availability.md
---

# Chapter 116 — Placement, Disruption and Availability

## Availability depends on placement and capacity

Three replicas do not provide three independent copies of a service if all three run on one node. A node failure can remove every replica at once; a zone failure can do the same when placement is concentrated in one zone. Kubernetes scheduling turns workload constraints and node capacity into placement decisions. High availability requires enough replicas, independent failure domains, working readiness checks, traffic routing, storage behavior, spare capacity and a recovery plan. Replica count alone is not an availability design.

Begin with the failure domains that matter to the service: process, Pod, node, rack, zone, region, cluster or external dependency. A workload's recovery objective and latency/cost requirements determine which domains it should span. The cluster must have enough schedulable capacity in the surviving domains to run the required replicas. A rule that spreads Pods across three zones cannot create a third zone, add addresses or supply capacity when a zone is lost. Validate node labels and actual infrastructure placement; a `topology.kubernetes.io/zone` label is only useful if it accurately represents the provider's failure boundary.

Kubernetes offers node selectors, node affinity, Pod affinity/anti-affinity and topology spread constraints. Required affinity is a hard scheduling filter; preferred affinity influences scoring but does not guarantee placement. Topology spread constraints distribute matching Pods across labeled domains. `DoNotSchedule` can leave replicas pending when constraints, labels or capacity make placement impossible; `ScheduleAnyway` favors balance while allowing a feasible placement. Multiple constraints combine, and selectors must match the workload's Pods. Check the [Pod assignment](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/) and [topology spread](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/) documentation for the exact semantics and cluster version.

Anti-affinity can prevent two replicas from occupying the same topology domain, but a strict hostname or zone rule can make a rollout unschedulable if capacity is scarce. Inter-Pod anti-affinity can add scheduling cost in large clusters. Spread constraints often provide a more flexible way to balance replicas, but they also depend on valid labels and selector behavior. Taints and tolerations help reserve or exclude nodes: a toleration allows a Pod to schedule onto a tainted node but does not require it to do so. Combine placement with resource requests, node capacity, autoscaler behavior, persistent-volume topology and any required GPU or hardware constraints.

## Readiness, health and disruption budgets

Availability is measured by the endpoints that can serve valid traffic, not by Pods in `Running` phase. A readiness probe controls whether a Pod is ready to receive Service traffic. Liveness probes can restart a container that is stuck, but an overly aggressive liveness probe can restart a slow dependency or overloaded process and worsen an outage. Startup probes can provide time for slow initialization before liveness checks begin. Probe design should distinguish process existence, ability to serve, and ability to make progress; do not make every dependency outage trigger a restart loop. Use application SLOs and controlled failure tests to set probe thresholds.

A PodDisruptionBudget (PDB) limits certain voluntary evictions through the Eviction API for a selected set of Pods. It helps cluster administrators and tools such as `kubectl drain` respect a service's disruption tolerance. It does not prevent involuntary failures such as node loss, and direct Pod or Deployment deletion can bypass the Eviction API and PDB. A PDB also does not control a Deployment or StatefulSet rolling update; configure the workload's rollout strategy and readiness behavior separately. If `minAvailable` or `maxUnavailable` is too strict for the number of replicas and failure state, maintenance can stall. If the budget is too permissive, a drain may remove too much healthy capacity. See the Kubernetes [disruption guide](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/) and PDB [configuration guide](https://kubernetes.io/docs/tasks/run-application/configure-pdb/).

An unavailable or unready Pod may affect whether voluntary eviction proceeds. Kubernetes documents an `unhealthyPodEvictionPolicy` setting; choose deliberately based on application recovery and maintenance needs rather than assuming every stuck Pod will be evicted or that `AlwaysAllow` is universally safe. PDB status, current healthy count and allowed disruptions are useful signals, but they describe the selected Pods and desired replicas, not end-user request success. Confirm that the PDB selector targets the intended workload, avoids unrelated Pods, and has a replica source the disruption controller can use.

Rollouts and node maintenance consume the same spare capacity. A Deployment's `maxSurge`, `maxUnavailable`, readiness and scheduling constraints interact. A strict zone spread plus insufficient zone headroom can prevent surge Pods from scheduling; a PDB cannot force capacity into existence. Before a node upgrade or drain, compare requested CPU, memory, ephemeral storage and volume attach limits with the capacity remaining after the operation. Include autoscaler delay and quota limits in the maintenance plan. [Chapter 117](117-horizontal-vertical-and-node-autoscaling.md) covers scaling behavior, while [Chapter 114](114-csi-and-production-storage.md) covers volume topology and attach constraints.

## A maintenance disruption scenario

DispatchDesk serves API traffic with three replicas. The team expects one replica in each zone and configures strict zone anti-affinity. During a node-image upgrade, a zone's node pool has no spare capacity and the Deployment uses a zero-unavailable rollout, so surge Pods remain Pending. At the same time, a separate replica is already unready; with a PDB requiring two healthy Pods, the remaining two are exactly at the minimum, leaving zero allowed disruptions and blocking the planned drain through the Eviction API. The team first checks actual zone labels and placements, resource requests, rollout status, PDB allowance and node-pool capacity. It pauses the upgrade, restores or adds capacity in the required domains, and verifies the workload is healthy before resuming one node at a time. The longer-term change aligns the spread strategy, rollout budget, PDB and capacity reserve with the service's real failure objective.

This example illustrates a common trap: each setting can look protective in isolation but combine into a deadlock. A PDB is not a general rollout control, a rollout strategy does not reserve node capacity, and hard anti-affinity does not repair a missing failure domain. Build a maintenance rehearsal that tests one node or zone at a time and records the remaining ready endpoints, request success, scheduling events and time to recover. An exception to a blocked drain should follow an explicit risk decision, not an improvised `--force` command.

Inspect current scheduling and disruption evidence from an authorized, verified context with read-only queries:

```bash
kubectl --context kind-dispatchdesk --namespace production get deployments,pods -o wide
kubectl --context kind-dispatchdesk --namespace production get pdb
kubectl --context kind-dispatchdesk --namespace production describe pdb dispatchdesk-api
kubectl --context kind-dispatchdesk get nodes -L topology.kubernetes.io/zone
kubectl --context kind-dispatchdesk --namespace production get events --sort-by=.lastTimestamp
```

The context is illustrative; confirm the API endpoint and account before use. Pod and node output relate placement to zone labels; Deployment status shows desired and ready replicas; PDB status includes healthy and allowed disruption counts. Events may expire, and none of these queries measures the real user path or provider failure-domain health. Avoid publishing internal node names or addresses. Do not start a drain or delete workloads as part of diagnosis; first review the maintenance change and application-specific recovery plan.

When a rollout or drain stalls, separate a policy block from a scheduling or admission failure. A PDB with zero allowed disruptions may be working as configured because a selected Pod is already unavailable or the healthy count is at the budget floor. Pending Pods may have unsatisfied affinity, taints, resource requests, volume topology or quota constraints. A ResourceQuota admission rejection prevents a new Pod object from being persisted; scheduler capacity constraints appear on a persisted Pending Pod. A Ready condition can be false due to a failed probe, and a green Ready state can still mask broken dependencies if the probe is shallow. Restore healthy replicas or capacity first when possible. If the planned maintenance cannot meet the budget, reschedule it or seek an explicit exception from the service owner with a quantified risk and monitoring plan. After the change, verify replica distribution, user-facing SLI, error budget impact and recovery time.

## Exercises and answer guidance

1. Three replicas all run on one node. What failure does this design not tolerate? Loss or maintenance of that node can remove all replicas; spread them across appropriate domains and ensure surviving capacity.
2. A Pod tolerates the `dedicated=storage` taint but keeps scheduling elsewhere. Is that a scheduler bug? No. A toleration permits placement on matching tainted nodes; node affinity or another placement constraint is needed to attract it.
3. A PDB reports zero allowed disruptions and a node drain stalls. What should be checked? Selected Pods, current versus desired health, selector accuracy, workload replica count, other failing replicas and whether a safe capacity path exists. Do not assume the PDB is stale.
4. A Deployment rollout removes two Pods despite a PDB that allows one. Is that impossible? No. Workload rolling updates are governed by the workload's rollout strategy rather than constrained by PDB eviction behavior; inspect `maxUnavailable`, surge and readiness.
5. A strict zone spread leaves a replica Pending after a zone disappears. What design inputs matter? Remaining zone capacity, eligible topology labels/domains, spread policy, requests, autoscaler/quota and whether the service can meet its SLO with fewer domains.

Review questions: how do hard and soft placement rules differ, which disruptions does a PDB constrain, how do rollouts use separate controls, and what capacity evidence is required before maintenance?

## Verification and primary sources

Official Kubernetes placement, topology spread and disruption documentation was inspected on 2026-10-04. The examples are read-only queries and were not run against a cluster. No workload, PDB, node, drain, autoscaler or provider setting was changed. Static checks cannot establish actual failure-domain independence, application readiness quality, service SLOs, spare capacity or safe drain behavior.

Primary references: [Assigning Pods to Nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/), [Pod Topology Spread Constraints](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/), [Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/), [PDB configuration](https://kubernetes.io/docs/tasks/run-application/configure-pdb/), [API-initiated Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/api-eviction/), and [Taints and Tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/).
