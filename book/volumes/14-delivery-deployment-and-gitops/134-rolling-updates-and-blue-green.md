---
book: The Complete DevOps Engineering Book
volume: 14
volume_title: "Delivery, Deployment and GitOps"
chapter: 134
title: "Rolling Updates and Blue Green"
slug: rolling-updates-and-blue-green
status: complete
summary: ../../_ai/chapter-summaries/134-rolling-updates-and-blue-green.md
---

# Chapter 134 — Rolling Updates and Blue Green

## Why release shape affects reliability

A new version rarely replaces an old one at a single instant. During a release, some requests may reach old code, others new code, and traffic routers may observe health at a different pace from application users. The release strategy defines how that overlap happens, how much capacity it needs, what evidence permits traffic to move, and what recovery means. Selecting “rolling” or “blue/green” without checking session state, database compatibility, capacity, and health signals can leave a deployment technically complete while users experience failures.

This chapter builds on the ECS and EKS deployment paths in [Chapter 133](133-container-deployment-to-aws.md). A rolling update gradually replaces instances or Pods under one service identity. Blue/green keeps a current environment (blue) serving while a candidate environment (green) starts alongside it; traffic is directed to green only after checks. The terms describe patterns, and a platform’s implementation has its own controller, routing, health, and rollback semantics. For example, ECS exposes several service strategies, while a Kubernetes Deployment natively performs a rolling update; Kubernetes blue/green behavior is composed from workload objects and traffic routing rather than selected by a Deployment strategy enum ([ECS deployment strategies](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_service-options.html), [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)).

## Mixed versions and traffic switching

In a rolling release, the controller starts a replacement, waits for its readiness criteria, and then terminates or removes an old instance according to its availability settings. The old and new versions coexist for some interval. A Kubernetes Deployment expresses that overlap through `maxUnavailable` and `maxSurge`; an ECS service has minimum and maximum healthy task percentages; a VPS deployment in [Chapter 132](132-deployment-to-vps-infrastructure.md) switches one host’s release pointer and restarts the process. Those controls have different implementation details, but all ask how much old and new capacity can run together and how much capacity may be unavailable.

The overlap imposes a compatibility contract. Requests, sessions, events, database rows, and messages may be created by one version and consumed by the other. If DispatchDesk version A writes a queue message that version B cannot parse, a rolling deployment can fail even when both containers are healthy. Similarly, new code can read a column added by a migration while old code continues to run; removing an old column during that overlap can break the remaining old instances. Plan for mixed versions as a normal deployment state, not an unlikely edge case. Chapter 136 develops expand-and-contract database and message compatibility in detail.

A readiness check should answer whether a particular instance can serve the traffic it is about to receive. It may verify that the process is responsive and has its required local initialization complete. If every instance’s readiness check requires a shared dependency to be fully healthy, a brief dependency issue can remove all targets simultaneously. Conversely, a shallow check that only returns HTTP 200 may mark an instance ready before it can process orders. Pair readiness with a separate synthetic business operation, and ensure that removing one target leaves enough healthy capacity to meet the service objective.

Blue/green changes the topology during release. Green is deployed independently and is not initially given normal production traffic. Operators or an automated controller can send test traffic to green, verify health and representative behavior, and then switch traffic. Routing can use a load-balancer listener, service mesh, reverse proxy, or another supported mechanism. Do not assume DNS changes are instantaneous or atomic: client and resolver caches can preserve old answers. A load balancer can direct new connections while established connections and sticky sessions remain on blue. Plan how long blue remains available and how session state behaves after the switch.

Kubernetes does not make a selector swap into a complete blue/green safety system. A common pattern runs two Deployments with distinct labels and uses a Service selector or an ingress/controller routing rule to choose the active version. Before changing that route, check that green Pods are ready, the endpoints match the intended labels, the load balancer has registered healthy targets, and the service has enough capacity. Retain a known way to route back to blue. For GitOps-managed resources, change the declarative source and let the reconciler apply it; manually switching a selector can be reverted or leave source and cluster out of sync. [Chapter 137](137-gitops-principles-and-reconciliation.md) covers reconciliation.

Blue/green can provide a fast traffic reversal while both versions remain available, but it is not a universal zero-downtime guarantee. A failed database migration, incompatible shared cache, side effect emitted by green, or external schema change may persist after routing returns to blue. Blue and green may also share a database or queue, so writes from green are not erased by changing the listener. Distinguish traffic rollback (route users to blue) from application rollback (restore its configuration) and data recovery (repair or restore state). The rollback procedure should state what each action changes and what it cannot undo.

## Capacity headroom and session state

Rolling updates usually need less duplicate capacity than a full blue/green deployment, but “less” does not mean none. A surge setting can require additional Pods, IP addresses, CPU and memory. An ECS deployment maximum can require spare task capacity or room in private subnets. If a cluster autoscaler needs several minutes to add nodes, a tight rollout deadline may expire before capacity arrives. Reducing the rollout’s availability floor to force progress can turn a capacity problem into an outage. Inspect pending tasks or Pods, subnet address capacity, quotas, scheduler events and resource requests first.

Blue/green generally requires the candidate environment to run alongside production long enough for validation and traffic shifting. That can double part of the compute footprint, and may also temporarily double database connections, background consumers, scheduled jobs, or third-party requests. Do not let both API versions process the same queue unless the consumer behavior is safe under overlap. Some workloads should scale green workers to zero until cutover, then drain blue; other workloads need a controlled handoff and idempotent processing. Estimate both resource cost and external side-effect risk before choosing the pattern.

Stateful sessions complicate both strategies. If user session state lives only in a process’s memory, rolling replacement can log a user out when a request reaches a different replica. Blue/green can strand sessions on blue after cutover or create a second incompatible session store. Prefer a shared, version-compatible session system where its operational and security properties fit; otherwise document affinity and drain behavior. Sticky sessions can reduce cross-version exposure but are not durable state and can concentrate load.

Monitor the transition at several layers. Record the candidate version and image digest, number of desired and ready instances, load-balancer target health, error rate, latency distribution, saturation, dependency errors, and synthetic transaction result. Define a hold period that allows the important failure signals to surface, including delayed queue processing and scheduled jobs. A rollout controller may automatically roll back when startup or health checks fail, but a green metric does not guarantee business correctness. Assign an operator to watch the release and make the stop/continue decision when the system cannot make it safely.

## Choosing a release strategy

Use a rolling update when versions can coexist safely, the service has enough steady capacity to preserve its availability floor, and replacing instances gradually matches the failure impact you can accept. It is operationally efficient and works naturally with ECS rolling deployments and Kubernetes Deployments. Recovery may take time because the controller has to replace tasks or Pods again; keep the prior task definition, image digest, manifest or release package available. Configure the controller’s rollback behavior, but do not treat an automatic state transition as your final health check.

Use blue/green when the system can afford parallel capacity and benefits from testing the new version on an isolated target before routing normal traffic. It is useful when a rapid route reversal matters, a canary or test listener is available, or the team needs a clean comparison between old and new pools. It requires explicit traffic management, duplicate-environment configuration, and a plan for shared state. ECS blue/green, linear, and canary strategies have AWS-specific load-balancer and permission requirements; Kubernetes implementations depend on the ingress, service mesh, or controller selected. Verify the exact strategy supported by the chosen service and controller rather than copying a generic diagram into production ([ECS traffic-shift workflow](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/blue-green-deployment-how-it-works.html)).

For DispatchDesk, assume the API is stateless, has three replicas, and uses a compatible database migration. A rolling update fits if the cluster has one surge slot and its requests leave enough capacity to run three ready instances while replacements start. If the change touches a new request path and the team wants a low-risk test against production-like traffic, blue/green can run the green API with a test listener, synthetic orders, and a short observation window before production cutover. The new API must not send irreversible customer notifications during test traffic. If the team cannot isolate side effects or provision extra capacity, a controlled rolling release with a feature flag may be safer and simpler.

## Failure diagnosis and recovery

During a DispatchDesk rolling update configured with `maxUnavailable: 1`, new Pods remain Pending while one old Pod has already terminated. The assumption “the controller will preserve the full replica count” was false: this setting explicitly permits one replica to be unavailable during a Deployment rollout. Inspect Deployment conditions and events, requests, node allocatable resources, and actual Ready counts. If the pending Pod's memory request exceeds available schedulable memory, adding time to the rollout deadline will not create capacity. A PodDisruptionBudget does not constrain a Deployment rolling update; it applies to supported voluntary eviction workflows such as node drains. Stop further promotion, restore the previous template if the rollout has affected service, and add or free capacity before retrying. Verify live endpoints and a synthetic order after recovery.

In a blue/green release, the green target group is healthy but the first production requests fail with authorization errors. Health probes exercised only a public endpoint that did not require the production identity. Stop traffic shifting and route back to blue while it remains available. Compare the two environments’ runtime roles, secret references, and downstream access; then test a production-equivalent request against green before another cutover. Do not infer green’s correctness from target health alone.

If rollback causes errors, ask whether the old version can still read data written by green and whether jobs or messages were processed during the overlap. Freeze incompatible writes only if the application’s recovery plan defines a safe procedure. Preserve deployment events, route weights, version identity, and relevant request IDs. Repair-forward may be safer than another binary rollback when external state has changed. The team should document the point beyond which returning traffic to blue is no longer a valid recovery action.

## Exercises

1. A rolling update has two old and one new healthy replicas. The new version changes a message field that old workers do not recognize. Why is healthy routing not sufficient to proceed?
2. A blue/green cutover is reversed, but users continue to see failures. List three state or routing reasons why the route change may not restore the old behavior immediately.
3. Your Kubernetes rollout cannot schedule its one surge Pod. What evidence should you gather before changing `maxUnavailable`, and does a PodDisruptionBudget control the Deployment's rolling update?
4. DispatchDesk’s API and queue consumer share an image. What additional controls are needed before running blue and green consumer pools at the same time?
5. Choose a strategy for a low-risk static web service and for a payment API requiring preproduction traffic validation. Explain the constraints that drive each choice.

### Answer guidance

1. During overlap, old workers may consume messages written by new code. Verify backward and forward message compatibility or stage the protocol change so both versions can handle the transition. Readiness only reports the health signal configured for a Pod; it does not prove that mixed versions agree on a message schema.
2. Existing connections or sticky sessions can remain on green; DNS or client caches can delay route changes; shared database/cache state or side effects can persist after traffic returns. Confirm actual routing and workload version, then inspect shared-state compatibility and synthetic behavior.
3. Inspect pending-Pod events, requests versus allocatable capacity, quotas, taints/affinity, subnet/IP constraints, and autoscaler delay. `maxUnavailable` and `maxSurge` control the Deployment rollout; a PodDisruptionBudget does not block or repair that rolling update, though it can matter for a concurrent node drain. Decide whether to add capacity or revise the availability target from evidence and service objectives, not to force a green status.
4. Confirm duplicate consumers cannot process a message twice or violate ordering, use idempotent handlers, control which pool receives work, and define drain/cutover behavior. Compare role permissions, concurrency and downstream limits. If these controls are absent, do not run both consumer pools against production work.
5. A static web service may use rolling when assets are immutable and old/new versions can coexist; blue/green may still fit if traffic reversal or cache validation matters and the extra environment is affordable. A payment API may justify blue/green or a controlled canary/test-traffic phase if production identity, side effects, capacity and rollback semantics are explicitly designed. The risk level alone does not select a strategy; compatibility, evidence, capacity, routing and recovery do.

## Review questions

- What kinds of work can fail when old and new application versions coexist?
- How do capacity and subnet constraints change the meaning of a surge setting?
- What additional control-plane elements make a blue/green route switch observable and reversible?
- Why is a healthy load-balancer target weaker than a successful customer transaction?
- Which shared state must remain compatible after traffic is routed back to the old version?

## Takeaways

- Rolling updates deliberately run mixed versions; design APIs, schemas, messages, and sessions for that overlap.
- Blue/green offers a separate candidate pool and traffic switch, with extra capacity and shared-state complexity.
- Controller health and application correctness are different signals; verify a representative transaction before advancing.
- Set availability and surge controls from measured capacity and the service objective.
- A route rollback cannot reverse database writes, messages, or external side effects; define recovery boundaries before release.

## Further reading

- [Chapter 132 — Deployment to VPS Infrastructure](132-deployment-to-vps-infrastructure.md)
- [Chapter 133 — Container Deployment to AWS](133-container-deployment-to-aws.md)
- [Chapter 136 — Database and Message Compatibility](136-database-and-message-compatibility.md)
- [Amazon ECS deployment strategies](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_service-options.html)
- [Amazon ECS blue/green deployment workflow](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/blue-green-deployment-how-it-works.html)
- [Kubernetes Deployment updates](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Pod disruptions and disruption budgets](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)
- [Kubernetes rolling update procedure](https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/)

Sources reviewed 2026-10-04. No ECS deployment, Kubernetes rollout, traffic switch, load test, or database operation was executed.
