---
book: The Complete DevOps Engineering Book
volume: 11
volume_title: "Kubernetes Foundations"
chapter: 108
title: "Resource Requests, Limits and Scheduling"
slug: resource-requests-limits-and-scheduling
status: complete
summary: ../../_ai/chapter-summaries/108-resource-requests-limits-and-scheduling.md
---

# Chapter 108 — Resource Requests, Limits and Scheduling

## Scheduling and runtime enforcement

A Pod that fits on paper can still be slow or unstable if its resource settings do not fit its workload. Kubernetes uses resource requests when deciding where a Pod can run and limits to constrain some runtime consumption. Requests, limits and observed usage answer different questions. A request says how much capacity the scheduler should account for and influences relative CPU weight under contention. A limit sets a runtime ceiling for resources such as CPU and memory. Neither is a reservation of dedicated cores or memory pages, and neither replaces measurement.

For CPU, `1` means one CPU core (physical or virtual, depending on the node); `500m` means half a CPU. CPU is a compressible resource: when a container reaches its CPU limit, it is throttled even if the node has otherwise idle CPU time; contention can make that throttling more visible as latency. A memory request is used for scheduling and eviction decisions; it does not cap use. Memory is not compressible. A memory limit is enforced reactively by the node's kernel/runtime, often resulting in an OOM kill when the cgroup exceeds its limit. A process may exceed its request while there is headroom, but then contribute to node pressure. See Kubernetes [resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/).

The [Chapter 104](104-deployments-replicasets-and-jobs.md) Deployment set a request of 500m CPU and 512Mi memory but omitted limits to keep its rollout example focused. An application-specific resource policy might extend it like this:

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "1"
    memory: "768Mi"
```

These values are illustrative starting points, not a recommendation or sizing claim. The scheduler accounts for the request on each Pod; the limit does not make an extra 256Mi of memory available to every node. Three replicas with these requests account for 1.5 CPU and 1536Mi of memory before other containers, system reservations, DaemonSets and scheduling overhead. For a resource with a specified limit but no request, Kubernetes copies that limit into the request unless admission has already supplied a request. If neither a request nor a limit is specified and no admission default applies, the request is treated as zero for scheduling. Check the admitted Pod spec, not only the YAML a developer submitted.

The scheduler evaluates requests against node allocatable resources and other constraints. Allocatable is typically lower than node capacity because system components need resources too. It also considers taints and tolerations, node affinity, topology, volumes, extended resources and policy. Requests do not prove that a Pod will run: a cluster may lack capacity, quota may reject the Pod, or constraints may exclude every node. A Pod that cannot be placed remains Pending, and `kubectl describe pod` shows scheduler events such as insufficient CPU, insufficient memory or an unmatched constraint. Increasing the request can improve placement honesty but may make the Pod unschedulable; lowering it can overpack nodes and shift failures to runtime.

CPU requests also influence relative access when CPU is contended. They are not a hard cap: with spare node capacity, a container may use more CPU than its request unless a limit constrains it. When the node is busy, a larger CPU request generally gives the container a larger share than a smaller one. CPU limits are implemented through throttling and can introduce latency even when average CPU use seems modest. A service with tight response-time goals may need no CPU limit or a generous limit, subject to cluster policy and neighbor isolation. That is a tradeoff to test, not a universal rule.

Memory limits and requests should be considered together with the process's working set and transient peaks. A limit that is too low can repeatedly kill a healthy workload during traffic spikes, cache warmup or garbage collection. A request much lower than actual use lets the scheduler overcommit the node and increases eviction risk. A request equal to a limit for CPU and memory across all containers in a Pod is one condition for `Guaranteed` QoS; other combinations are `Burstable`, while Pods with no CPU or memory requests/limits are `BestEffort`. QoS affects node-pressure behavior and OOM scoring, but it is not a promise that a Pod is protected from every failure. Node-pressure eviction ordering also considers usage relative to requests and Pod priority.

Requests and limits are per container in the familiar resource API; Pod-level accounting is derived from the containers and may depend on newer feature support. Init containers and restartable sidecars have their own accounting rules. For a multi-container Pod, total the requests that Kubernetes will admit rather than sizing only the application container. Also account for `emptyDir`: a memory-backed volume consumes memory and may count toward a container's memory limit. Unbounded scratch data, page cache and native allocations can make observed use differ from a simple application heap metric. Configure resources alongside the probes and lifecycle behavior in [Chapter 107](107-probes-and-graceful-termination.md), since restarts and shutdown overlap affect observed peaks.

## CPU throttling and memory exhaustion

CPU throttling often appears as elevated latency before it appears as high average CPU usage. For example, an API may handle a burst with many runnable threads, consume its CPU quota early in each enforcement period, and then wait for the next period. The container can show moderate average usage while request durations climb and cgroup throttling counters increase. If a hard CPU ceiling causes user-visible latency, compare CPU usage, throttled time, concurrency, request latency and replica capacity before changing it. Raising or removing the limit may help, but it can allow one workload to starve neighbors; increasing the request or scaling replicas changes scheduling and contention differently.

Memory exhaustion has different evidence. A container may restart with reason `OOMKilled`; its exit code and previous logs can be incomplete because the kernel terminated it. A liveness probe can then turn memory pressure into a restart loop if the application starts allocating heavily again after each restart. Distinguish a cgroup limit OOM from node-level memory pressure and eviction. The former often points to a per-container peak above its limit; node pressure can evict a Pod that stays below its own limit when total demand exceeds allocatable memory. Use Pod events, node conditions and container termination state, and correlate with metrics over the same interval.

Ephemeral storage is another schedulable resource. Container writable layers, logs and disk-backed `emptyDir` can use node storage. A memory-backed `emptyDir` uses memory instead. An absent ephemeral-storage request means the scheduler does not reserve a declared amount for that demand; an absent limit does not switch off kubelet measurement or node-pressure eviction. Accounting and enforcement depend on the node's supported filesystem layout, and a limit constrains the container's measured local ephemeral use rather than every host or external resource. Diagnose `DiskPressure`, eviction events, filesystem capacity and log growth separately from CPU or memory.

Common command evidence, when the relevant APIs and metrics are installed, can be collected from a terminal with a configured kubectl client:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  describe pod POD_NAME
kubectl --context kind-dispatchdesk --namespace production \
  get pod POD_NAME -o jsonpath='{.status.containerStatuses[*].lastState.terminated.reason}{"\n"}'
kubectl --context kind-dispatchdesk --namespace production \
  top pod POD_NAME --containers
kubectl --context kind-dispatchdesk --namespace production \
  get events --sort-by=.lastTimestamp
```

Replace `POD_NAME` with a Pod from Chapter 104's Deployment. The first and last commands inspect conditions/events and can help identify scheduling or eviction causes. The JSONPath command reads the previous termination reason where one exists. `kubectl top` requires Metrics Server or another compatible resource metrics API; it reports a sample, not a historical profile and not CPU throttling. Use a metrics system with adequate retention for trend and peak analysis. Avoid pasting Secret-bearing environment or full Pod data into incident tickets.

## Right-sizing a workload from evidence

Consider an API whose replicas are Pending after a release because each requests 2 CPU and 4Gi memory. The author chose those values from a developer laptop, not production measurements. The failure is not solved by deleting constraints at random. First determine node allocatable capacity, already-accounted requests, namespace quotas, topology or affinity rules and scheduler events. If the requests exceed available capacity, decide whether the workload really needs that footprint, whether capacity should change, or whether placement policy is unnecessarily narrow. Only then adjust the manifest or the cluster through its normal review path.

For a running workload, gather representative data across normal traffic, peak traffic, startup, batch jobs and failure recovery. CPU request sizing should account for typical concurrency and the performance impact of contention; memory requests should approximate the working set the scheduler must make room for, with headroom for meaningful variation. Limits should reflect the acceptable failure or interference boundary, not an arbitrary multiple of a developer's observed average. Compare percentiles and maximums with application-level latency, error rate and restart signals. A short sample during a quiet hour is not enough evidence for a monthly billing workload or a seasonal service.

Suppose a month of measurements shows DispatchDesk API CPU usage usually between 180m and 420m, with brief peaks near 800m, while request latency becomes unacceptable when CPU throttling exceeds the agreed threshold. A 500m request and 1 CPU limit might still be wrong if several replicas peak together. The engineer should compare the chosen values against load tests and production concurrency, then decide whether to raise requests, raise/remove the limit, add replicas or reduce work per request. For memory, measure working set and restart/OOM history; do not infer safe limits solely from language heap settings because native memory, caches and buffers also consume the cgroup budget. These numbers are a fictional scenario, not measured results.

Use a controlled sequence: change one resource dimension for a small canary or staged rollout, watch scheduling, CPU throttling, memory, restarts and user-facing service indicators, then compare with the prior version under similar load. Roll back through the Deployment source if latency, eviction or OOM behavior worsens. Make sure the cluster has enough surge capacity for the rollout itself. If a namespace has a ResourceQuota or LimitRange, inspect it before interpreting admission errors; policies can inject defaults, reject out-of-range values or cap aggregate requests.

Do not use `kubectl top` as the only sizing method, and do not equate current usage with future capacity. Requests influence bin packing and the HPA's utilization calculations when configured; changing requests can therefore change autoscaling behavior even if actual work does not change. If HPA scales on CPU utilization relative to request, raising the request lowers reported utilization for the same CPU consumption. Coordinate resource updates with the autoscaling target and verify replica behavior. [Chapter 117](../12-kubernetes-production-engineering/117-horizontal-vertical-and-node-autoscaling.md) covers autoscaling and should be read before changing a workload with an HPA.

For accelerator and other extended resources, ordinary CPU/memory reasoning is incomplete. Device plugins expose discrete resources that generally cannot be overcommitted, and device placement/health introduces hardware-specific concerns. Use integer quantities for extended resources and consult the vendor and Kubernetes device documentation. A request for an unavailable GPU can keep a Pod Pending even if CPU and memory are plentiful.

## Exercises and answer guidance

1. A Pod requests 1 CPU and has a 2 CPU limit. Can the scheduler place it only on a node with 2 free CPUs? The scheduler accounts for the 1 CPU request; the runtime limit is not the placement request, though other constraints and allocatable capacity still apply.
2. A container uses more CPU than its request and remains running but response latency rises under contention. What should be investigated? CPU limit throttling, node contention, request weighting and application concurrency; CPU exhaustion usually throttles rather than OOM-killing the container.
3. A Pod restarts with `OOMKilled` but the node has free memory. What is a likely cause? Its container exceeded its cgroup memory limit; inspect the limit, peak working set and transient allocation behavior.
4. A Pod is Pending with `Insufficient memory`. Should its memory limit be raised? Not necessarily. The scheduler evaluates the request against allocatable memory; inspect request, node accounting, quotas and placement constraints.
5. An HPA targets 70% CPU utilization and the CPU request doubles. What can happen to scaling at the same workload? Reported utilization relative to request falls, potentially delaying scale-out; validate autoscaler behavior with the new request.

Review questions: what do requests and limits control, why does CPU-limit pressure differ from memory-limit pressure, how do QoS and node pressure affect eviction, and what evidence is required before right-sizing?

## Verification and primary sources

Official Kubernetes resource-management, scheduler, node-pressure, affinity and taint documentation was inspected on 2026-10-04. Resource manifests and commands are illustrative; no workload, limit, node or quota was changed, and no live metric was queried. `kubectl top` requires an installed metrics API. Static checks do not prove scheduler fit, CPU performance, memory peaks, eviction order, QoS behavior under pressure or application SLO impact.

Primary references: [resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/), [assigning Pods to nodes](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/), [node-pressure eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/), [taints and tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/), and [limit ranges](https://kubernetes.io/docs/concepts/policy/limit-range/).
