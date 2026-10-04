---
book: The Complete DevOps Engineering Book
volume: 16
volume_title: "Performance and Capacity Engineering"
chapter: 157
title: "Autoscaling as a Feedback System"
slug: autoscaling-as-a-feedback-system
status: complete
summary: ../../_ai/chapter-summaries/157-autoscaling-as-a-feedback-system.md
---

# Chapter 157 — Autoscaling as a Feedback System

**Section outline:** model feedback delay; choose actionable signals; simulate a delayed controller; configure bounded Kubernetes and ECS examples; diagnose oscillation and stalled growth.

## Scaling reacts after demand has already changed

An autoscaler observes a signal, computes a desired capacity, requests a change, and waits for usable capacity. The observation may already be old. Provisioning, image download, application initialization and routing add more delay. This is a feedback system acting on delayed evidence, not an instantaneous capacity guarantee.

[Horizontal scaling](156-horizontal-scaling-decisions.md) established the application and shared-resource prerequisites. Automating replica count does not remove them. Summit can use ECS service scaling because its tasks are replaceable and its database and notification queues have explicit budgets. Atlas can use Kubernetes autoscaling within its platform's metrics and scheduling contracts. Harbor may reasonably keep a fixed VPS allocation, schedule predictable background work and resize deliberately. Automation must earn its operational complexity.

Consider a hypothetical burst from twelve to forty-eight attempts per second. Four ready replicas each sustain six attempts per second within the chosen performance boundary. For ninety seconds, existing capacity is twenty-four attempts per second while new replicas become ready. If the system queues all excess work, the backlog can grow by roughly2160attempts during that interval. If it rejects excess requests, the user sees those rejections instead. A later increase cannot undo either the delay already experienced or the rejected attempts. Client retries can add work at precisely the wrong time.

Reserve capacity, scheduled preparation and bounded admission can protect the response deadline while reactive scaling catches up. A queue is appropriate when the business permits deferred work, such as notification delivery. It is not permission to acknowledge an order before its durable state and notification intent are recorded.

## Choose a signal that changes when capacity changes

A useful target signal has a predictable relationship to capacity. Per-replica CPU can work for CPU-bound requests when added replicas receive work and shared dependencies remain healthy. Requests per ready target can work when request costs are sufficiently stable. Queue backlog per worker can help independent consumers, especially when accompanied by oldest-job age and completion rate. A raw total backlog does not naturally halve when the worker count doubles; the policy must interpret it appropriately.

Latency is a customer-facing boundary and an essential outcome metric, but it can be a dangerous sole control signal. Latency rises because of database locks, failed dependencies, overload, cold caches and network faults as well as insufficient replicas. Adding API processes during a database connection crisis can increase latency further. A controller needs a plausible corrective action, not simply a bad number.

For queue workers, measure service time by job class. If one worker completes five ordinary notifications per second, then a backlog of1000with continuing arrivals of20persecond requires more than four workers to drain. At six workers the theoretical excess completion capacity is ten per second, giving a100-second drain time under stable assumptions. Provider rate limits and slow job classes can invalidate that arithmetic. Oldest-job age tells the operator whether the customer's deadline is being missed even when aggregate backlog falls.

Avoid targeting memory usage blindly when the workload retains cache: adding workers can create more independent caches and increase total memory rather than reduce the observed fraction. A memory leak can repeatedly trigger scaling without recovering the leaking processes. Reject labels with unbounded customer or order values in the scaling signal, just as in ordinary metrics.

## A complete local delayed-controller model

Save the following as `autoscale_model.py` and run `python3 autoscale_model.py` as an ordinary user on Ubuntu, Fedora or RHEL. It uses only Python's standard library. The model makes assumptions visible: ten-second time steps, sixty-second startup, a sixty-second downscale hold and a six-replica ceiling. It queues excess work and omits failures, routing skew and service-time variation. It is a teaching simulation, not a prediction of ECS or Kubernetes internals.

```python
import math

step = 10
ready = 2
pending = []
backlog = 0.0
capacity_per_replica = 6.0
minimum, maximum = 2, 6
last_scale_up = -1000

for now in range(0, 241, step):
    arrivals_per_second = 30.0 if 40 <= now < 140 else 8.0
    newly_ready = sum(count for when, count in pending if when <= now)
    pending = [(when, count) for when, count in pending if when > now]
    ready += newly_ready
    arriving = arrivals_per_second * step
    completed = min(backlog + arriving,
                    ready * capacity_per_replica * step)
    backlog = backlog + arriving - completed
    desired = math.ceil((arrivals_per_second + backlog / 60.0) /
                        capacity_per_replica)
    desired = max(minimum, min(maximum, desired))
    requested = ready + sum(count for _, count in pending)
    if desired > requested:
        pending.append((now + 60, desired - requested))
        last_scale_up = now
    elif desired < ready and now - last_scale_up >= 60:
        # Remove at most one ready replica per observation.
        ready -= 1
    print(f"t={now:3d}s ready={ready} requested={requested} "
          f"backlog={backlog:.0f} desired={desired}")
```

The printed values are generated by the reader's run; none are presented here as measured platform output. The capacity used for a time step is the ready count before its final downscale action, so the row reports the next ready allocation rather than pretending a removal affected already completed work. The `requested` variable captures the count before this step's new action. These choices matter when interpreting a simulation.

Change startup delay to120seconds in the `pending.append` expression. The same replica ceiling can still be sufficient in steady state while the transient backlog becomes unacceptable. Then change the maximum to four: capacity stays below the burst's arrival rate until demand falls. A controller can be functioning perfectly while its ceiling makes the business target impossible. Delete the local simulation file after the experiment if it is no longer needed; it changes no infrastructure.

## Atlas: configure behavior without hiding prerequisites

The following complete HPA object illustrates a bounded CPU policy for an **existing** Atlas staging Deployment named `dispatchdesk-api` in namespace `dispatchdesk-staging`. The cluster must expose resource metrics, support `autoscaling/v2`, and permit this object. Every relevant application container needs a CPU request for the utilization calculation, and the deployment's images, readiness, database pools and replica budget must already be valid. This object does not supply those prerequisites or create the application.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dispatchdesk-api
  namespace: dispatchdesk-staging
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dispatchdesk-api
  minReplicas: 2
  maxReplicas: 6
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 65
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Pods
          value: 1
          periodSeconds: 60
```

This manifest uses the Pod-level CPU resource metric, so CPU requests must be set for every container in each measured Pod. A sidecar's usage and request contribute to aggregate utilization; an unrequested container can leave Pod CPU utilization undefined, so the HPA will not scale on that metric. When the application container should drive scaling independently, Kubernetes offers `ContainerResource` metrics in supported releases; verify API support before changing the metric type. The sixty-five-percent target is relative to CPU requests, not host CPU capacity or necessarily the container's limit. The explicit replica boundaries must fit database connections and node capacity. The policies constrain changes; they do not promise a usable new pod in sixty seconds. The [official HPA documentation](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/) explains metric handling and downscale stabilization. The example avoids newer optional tolerance and scale-to-zero fields to keep its compatibility assumptions narrower; confirm the server's API schema rather than relying on a current webpage for an older cluster.

Here the 300-second downscale stabilization window uses the highest desired replica recommendation from the preceding five minutes, preventing a brief low signal from immediately removing capacity. The `Pods` policy's `periodSeconds: 60` limits removal to one pod over its rolling one-minute policy window. This is separate from the stabilization window. If multiple policies are configured for one direction, Kubernetes defaults to the policy that permits the largest change unless `selectPolicy` overrides it. Scale-up here has no stabilization delay but remains limited to two pod additions per one-minute window.

Use these commands only from an authorized operator workstation with an existing staging kubeconfig. They are distribution-neutral; installation of kubectl and cluster access follows the book's Kubernetes prerequisites. Save the YAML as `hpa.yaml`.

```bash
kubectl config current-context
kubectl -n dispatchdesk-staging get deployment dispatchdesk-api
kubectl -n dispatchdesk-staging get hpa dispatchdesk-api
```

Inspect the context and existing object before proceeding. If an HPA already exists, review its ownership and preserve its desired configuration; do not overwrite another controller's policy. In a lab where the target exists and no HPA with this name exists, preview then apply the example:

```bash
kubectl apply --dry-run=server -f hpa.yaml
kubectl apply -f hpa.yaml
kubectl -n dispatchdesk-staging describe hpa dispatchdesk-api
kubectl -n dispatchdesk-staging get pods
```

Server dry-run asks the API server to validate without persisting this object; it is not a load test and cannot establish useful metrics. Applying changes a live staging controller. `describe` exposes conditions, target metrics and events; compare desired replicas with actual ready pods. An unknown metric or a failure condition needs diagnosis. Cleanup for a newly created lab HPA is `kubectl -n dispatchdesk-staging delete hpa dispatchdesk-api`; deleting it stops that controller and does not automatically return the Deployment to its former replica count. Restore the prior desired count through the team's owning deployment mechanism after checking load and readiness.

## Summit: the same reasoning with different mechanisms

ECS service autoscaling changes desired task count through Application Auto Scaling. Summit must distinguish requested tasks from running healthy tasks, and account for deployment behavior and capacity availability. Its target-tracking policy should use a signal whose relationship to task count makes sense. The inspected [ECS service scaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html) and [target-tracking](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-autoscaling-targettracking.html) documentation describe cooldown and deployment interaction; exact account-specific setup belongs to Summit's existing service configuration.

A task floor protects known startup delay and minimum failure tolerance. A ceiling protects spending and downstream resources but also defines a possible overload state that needs an alert and admission policy. Scheduled scaling can prepare for a known campaign, while reactive scaling covers uncertainty. Neither should be treated as a substitute for provider quotas, image availability or database reserve.

## Diagnose oscillation and stalled growth

Oscillation can appear as task count repeatedly rising, then falling as new capacity lowers the average signal, then rising again after removed capacity drives it up. Correlate recommendation timestamps, ready count, request arrival, startup duration and cache warmup. A downscale hold and a bounded removal rate can reduce churn. Increasing the hold alone does not fix a noisy metric, a leak or a permanently saturated dependency.

Stalled growth looks different: desired replicas rise while ready capacity remains unchanged. Inspect pending scheduling, quotas, image pulls, startup failures, readiness and metrics freshness. A controller action is not delivery of capacity. Recovery might temporarily cap admission, retain a known good floor, correct startup or quota constraints, and wait for verified ready capacity. Avoid manual replica edits that immediately fight the still-active controller; use the platform's supported policy pause or change process and record how automation will resume.

## Exercises and answer guidance

A worker backlog is shrinking, but oldest-job age continues increasing. What could explain this? Newer easy jobs may dominate completions while older expensive or repeatedly failing jobs remain. Inspect age by bounded job class and ownership; aggregate depth alone hides the deadline violation.

A CPU HPA shows sixty-five percent utilization, yet host CPU is low. Explain the denominator. HPA utilization is tied to declared requests; it is not a host-capacity fraction. Verify requests and the workload's measured demand before changing the target.

An autoscaler requests six replicas but only two are ready during a surge. Name the immediate business protection and the diagnosis. Bounded admission or agreed queueing protects the service while the team inspects scheduling, startup, quotas and readiness. Raising the maximum without understanding readiness does not supply capacity.

## Takeaways and verification

Autoscaling succeeds when signals represent correctable demand, startup delay fits the customer deadline, and floors and ceilings match shared-resource budgets. Observe ready capacity and customer outcomes alongside recommendations. Official Kubernetes and AWS documentation was inspected on 2026-10-04. YAML and simulation are inline; no HPA application, ECS policy change, cluster load test or cloud scaling operation was executed while authoring.
