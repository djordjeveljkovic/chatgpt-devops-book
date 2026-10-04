---
book: The Complete DevOps Engineering Book
volume: 12
volume_title: "Kubernetes Production Engineering"
chapter: 117
title: "Horizontal, Vertical and Node Autoscaling"
slug: horizontal-vertical-and-node-autoscaling
status: complete
summary: ../../_ai/chapter-summaries/117-horizontal-vertical-and-node-autoscaling.md
---

# Chapter 117 — Horizontal, Vertical and Node Autoscaling

## Three different scaling loops

Autoscaling is not a single control. Horizontal Pod Autoscaling (HPA) changes a workload's replica count. Vertical Pod Autoscaling (VPA) recommends or changes resource requests for Pods, depending on the installed implementation and policy. Node autoscaling adds or removes worker capacity to satisfy schedulable demand. These loops observe different signals and act on different objects. They must be designed together: an HPA can request more Pods while node capacity remains fixed, and a node autoscaler cannot help if admitted Pods cannot fit available node shapes because of affinity, resources or storage topology. A namespace `ResourceQuota` can instead reject Pod creation at admission, while a provider or node-pool quota can prevent new worker provisioning for already Pending Pods; inspect the correct layer.

Scaling starts with a bottleneck and a service objective. More replicas can improve throughput for stateless work that partitions requests, but do not fix a saturated shared database, serial queue consumer, connection pool limit or hot key. More CPU can reduce compute latency but not increase a dependency's connection limit. More nodes can provide scheduler capacity but may not arrive before a short traffic spike has passed. Identify the constrained resource, scaling signal, startup time, warm-up time, maximum safe capacity and scale-down safety before enabling a controller.

The HPA is part of Kubernetes' autoscaling API and periodically adjusts the scale of a target workload such as a Deployment or StatefulSet. The current stable API is `autoscaling/v2`; it can use resource, custom and external metrics subject to the corresponding metrics APIs and adapters being available. The controller computes a replica recommendation from the relation between current and target metrics, then applies bounds and behavior policies. Missing metrics, not-yet-ready Pods, stabilization and scaling policies affect the result. HPA is a feedback controller, not a direct reaction to each request. Read the Kubernetes [HPA guide](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/) and current API reference for the installed version.

For CPU or memory utilization targets, resource requests matter because utilization is calculated relative to requests. If requests are absent or unrealistic, the metric may be unavailable or misleading. CPU utilization can lag a burst and include startup work; memory often does not fall when demand drops and may indicate a leak rather than useful capacity. Queue depth, request concurrency, latency or other service-specific signals may better reflect demand, but custom and external metrics require adapters, permissions, ownership and alerting. Multiple HPA metrics can produce different replica recommendations; the controller uses the highest recommendation subject to configured limits. Choose a metric that tracks user demand and can be observed reliably under failure.

## Horizontal and vertical tradeoffs

Horizontal scaling adds replicas. It works best when the workload can serve requests in parallel, new replicas start quickly, and dependencies have capacity to handle additional concurrency. Define `minReplicas` from availability needs and `maxReplicas` from a tested service and dependency limit. Configure scale-up behavior to respond quickly enough for the workload's demand curve and scale-down behavior to avoid oscillation or premature removal. A high maximum can amplify an incident by overwhelming a database or external API. Coordinate HPA changes with queue, connection pool and rate limits.

Readiness and startup affect scaling. A new Pod may take time to pull an image, warm caches, load models, join a cluster or pass health checks. If metrics from a new Pod are included too early, the HPA can overreact or suppress the next scale-up. A startup probe and readiness signal should reflect when the Pod can actually serve. Test cold-start time at peak load. For batch systems, define whether scale follows queue depth, oldest-message age or processing throughput, and ensure the minimum replica count can prevent unbounded backlog.

An HPA manages the scale target, so avoid separately setting or applying `.spec.replicas` in a way that competes with it. A later manifest apply can overwrite a manually changed replica count or create confusing ownership. Configure the HPA bounds and let the controller own the scale subresource. Observe desired and current replicas, metric values, conditions and events during a rollout. If metrics disappear, inspect API registration, adapter health and metric labels before replacing autoscaler objects.

Vertical Pod Autoscaling can estimate requests from observed consumption and configured bounds. It is commonly installed as an add-on with a recommender, updater and admission component; it is not guaranteed to be present in every cluster. Verify its version, API, metrics source and update modes. Automatic changes can restart or resize Pods and alter scheduling, so begin with recommendation-only observation, compare recommendations with workload behavior and deploy controlled policies. Define minimum and maximum values, which containers and resources may change, and who approves updates. Do not let HPA and VPA independently control the same CPU or memory signal without an explicit supported configuration; their feedback loops can conflict. Kubernetes' [VPA guide](https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/) describes component and update behavior, which changes across VPA versions.

Requests and limits are different controls. Requests drive scheduling and are central to utilization-based HPA decisions; limits constrain runtime use according to Kubernetes resource semantics. A VPA recommendation that raises requests can make Pods unschedulable if the cluster lacks capacity. A recommendation that raises CPU limits can alter throttling behavior; changing memory limits can change OOM risk. Review resource policies and `LimitRange` constraints alongside autoscaler output. [Chapter 114](114-csi-and-production-storage.md) covers storage topology as another scheduling constraint. [Chapter 116](116-placement-disruption-and-availability.md) covers placement and disruption effects; a request change can shift replica distribution or interfere with maintenance headroom.

## Node capacity and feedback

Node autoscaling is usually provided by a cluster add-on or cloud integration, not by the HPA itself. It reacts to unschedulable Pods or other configured demand and selects a node group or machine type according to its implementation. It may take minutes for quota checks, provisioning, boot, node registration, CNI initialization and image pulls. It may also consolidate or remove nodes when utilization permits, subject to disruption constraints. Confirm the provider's supported node types, scale-from-zero behavior, maximums, quotas, upgrade behavior and consolidation policy. Kubernetes' [node autoscaling overview](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/) explains the integration landscape but does not guarantee one implementation's behavior.

For predictable scheduling, the Pod request vector must fit an available node after system reservations and daemon workloads. A Pod that requests an unsupported GPU, architecture, zone or volume topology may remain pending even while a node autoscaler is healthy. Taints, affinity, topology spread and PVC binding can limit eligible capacity. A provider or node-pool quota may prevent the autoscaler from provisioning a matching node; this differs from a namespace `ResourceQuota`, which can reject creation of the Pod before it is persisted. A cluster autoscaler can add only node shapes that match its configuration and provider limits. Include Pod disruption budgets and termination grace periods in node scale-down behavior; a node that cannot safely evict workloads may remain even when it appears lightly used.

The three loops can form a delayed feedback chain: traffic rises; HPA increases replica demand; scheduler marks some Pods Pending; node autoscaler requests workers; workers boot and register; Pods start and become Ready; HPA observes changed metrics; later, scale-down controllers remove surplus Pods and nodes. Dashboards should show each transition, not just final replica counts. Track HPA desired/current replicas and metric status, pending Pod age and scheduling reasons, node provisioning and quota errors, node readiness, saturation, user latency, queue lag and cost. Alert on the time a service remains below required capacity, not every transient pending Pod.

DispatchDesk's order API experiences a morning traffic peak and autoscaling does not meet its latency objective. The HPA uses a request-concurrency metric, which rises until its `maxReplicas` is reached, while database connections saturate before CPU reaches its target. Several new Pods also remain Pending because their memory requests do not fit the configured node types; the node autoscaler cannot satisfy one Pod affinity rule selecting an obsolete label. The team preserves request and metric evidence, checks HPA conditions, scheduler events, node limits and database pool behavior, then updates the workload and its scaling envelope in a canary. It tests cold starts, downstream connection capacity and node provisioning delay before raising the production maximum. Simply increasing `maxReplicas` would have increased database pressure without fixing eligible capacity.

## Observe and troubleshoot safely

Use read-only status queries from an authorized, verified kubeconfig context:

```bash
kubectl --context kind-dispatchdesk --namespace production get hpa
kubectl --context kind-dispatchdesk --namespace production describe hpa dispatchdesk-api
kubectl --context kind-dispatchdesk --namespace production get deployment dispatchdesk-api
kubectl --context kind-dispatchdesk --namespace production get pods -o wide
kubectl --context kind-dispatchdesk get nodes
kubectl --context kind-dispatchdesk --namespace production get events --sort-by=.lastTimestamp
```

The context name is illustrative; verify endpoint and account. HPA status and events can reveal missing metrics, bounds and desired replica count. Deployment and Pod status show rollout and scheduling state. The core `kubectl top` command may help when a metrics server is installed, but its values are sampled resource metrics rather than a billing or long-term monitoring source. VPA resources and node autoscaler events vary by installed add-on and distribution. Do not infer that a scaling controller is healthy from one object being present; inspect the relevant metrics API, controller conditions, events and provider-side provisioning evidence.

When scaling fails, walk the control loop in order. Is the demand metric present and moving? Does the HPA have permission and a valid target? Is desired replica count above the target's current count? Did Pod admission succeed, or did a namespace quota reject creation? For persisted Pending Pods, can the scheduler place them with their requests, labels, taints and PVC topology? If Pods remain Pending, does the node autoscaler recognize the reason and have a compatible pool, provider quota and subnet capacity? Once nodes register, can images pull and health checks pass? Finally, can downstream dependencies accept the increased load? Use timestamps to distinguish a slow but progressing scale-out from a permanent constraint. Test scale-in separately; graceful shutdown, connection draining, queue handoff, PDBs and storage detach can make it unsafe.

Do not delete HPAs, relax all scheduling constraints, raise every maximum or manually scale while a controller owns the replica count as first-line diagnosis. Such changes can obscure the signal or create a competing control loop. If emergency manual capacity is needed, coordinate with the service owner, know how the controller will reconcile it, apply a temporary bounded change and document the return path. After resolution, test both scale directions under a representative load and record time-to-capacity, maximum sustainable throughput, dependency headroom and cost.

## Exercises and answer guidance

1. HPA desired replicas increase, but Pods remain Pending. What should be investigated? Scheduler events, requests and limits, node shapes/quota, taints/affinity/topology, storage and autoscaler recognition; replica demand is not schedulable capacity.
2. CPU utilization is low while request latency and queue depth rise. Is CPU HPA necessarily the right metric? No. Find the bottleneck and use a signal that tracks demand or service health, with a safe dependency capacity bound.
3. A VPA recommendation raises Pod requests and replicas become unschedulable. What interacted? Resource rightsizing changed scheduler demand; node capacity, HPA, constraints and VPA update policy must be planned together.
4. A team raises `maxReplicas` after a database saturation incident. What risk does this create? More API Pods can increase connections and worsen the bottleneck; test service and downstream limits before expanding the bound.
5. Node autoscaling takes longer than the traffic burst. What options should be evaluated? Warm minimum capacity, faster startup/image paths, predictive or demand-aware scaling, queue buffering and application SLO tradeoffs; validate cost and failure behavior.

Review questions: how do HPA, VPA and node autoscaling differ, why do requests affect both scheduling and CPU utilization, what prevents a requested replica from becoming Ready, and which limits protect downstream systems?

## Verification and primary sources

Official Kubernetes HPA, VPA, node autoscaling and Deployment documentation was inspected on 2026-10-04. The commands are read-only examples and were not run against a cluster. No HPA, VPA, workload, node group, quota or metric adapter was changed. Static checks cannot prove metric quality, controller version compatibility, provider provisioning time, peak capacity, application behavior or dependency limits.

Primary references: [Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/), [Vertical Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/), [Node Autoscaling](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/), [Autoscaling Workloads](https://kubernetes.io/docs/concepts/workloads/autoscaling/), and [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).
