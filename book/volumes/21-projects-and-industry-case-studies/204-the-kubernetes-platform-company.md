---
book: The Complete DevOps Engineering Book
volume: 21
volume_title: "Projects and Industry Case Studies"
chapter: 204
title: "The Kubernetes Platform Company"
slug: the-kubernetes-platform-company
status: complete
summary: ../../_ai/chapter-summaries/204-the-kubernetes-platform-company.md
---

# Chapter 204 — The Kubernetes Platform Company

**Section outline:** several teams and deployment requirements; shared platform and workload isolation; why Kubernetes becomes justified.

## Identify the coordination problem

DispatchDesk now has six product teams releasing APIs, workers and scheduled tasks. Teams repeatedly build deployment workflows, struggle with inconsistent observability and compete for a shared environment. The platform team proposes Kubernetes. This time the decision is supported by multiple workload and team needs, but the cluster is not the goal: reducing release coordination and providing safe, reusable operations is.

Inventory workloads and classify requirements: stateless API, queue worker, scheduled job, stateful database dependency, public exposure, secrets, CPU/memory envelope, availability objective, data sensitivity and owner. Decide which workloads belong in the shared cluster and which remain managed services or external systems. A cluster does not require every service to run inside it. Managed databases and object storage can be better operated outside the cluster.

Define organizational ownership. The platform team owns cluster lifecycle, node capacity, network and admission policy, base observability, upgrades, supported deployment paths and cluster incident response. Product teams own application behavior, service SLOs, resource requests, release and runtime troubleshooting. A shared on-call model and escalation path prevent the platform team from becoming a ticket queue for every application problem.

## Build shared paths and isolation

Create separate environments or clusters according to fault, security, compliance and blast-radius needs. Namespaces organize workloads but do not alone establish a complete security boundary. Combine scoped RBAC, network policy, admission controls, resource quotas/limits, workload identity, secret handling and node isolation where risk warrants it. Restrict privileged workloads and cluster-wide permissions; audit the exceptions. Chapter 103 covers Pods and application lifecycles; Chapters 107–120 cover production cluster mechanics.

Provide a versioned service template that encodes supported labels, health semantics, resource requests, security context, telemetry and deployment ownership. Let teams configure only reviewed fields. The platform path should validate requests early and surface actionable errors. It must not claim the template authenticates owner identity or image provenance unless those are enforced by trusted mechanisms. For custom workloads, publish an exception and support path with explicit responsibilities.

Use GitOps or another single deployment authority per resource. Keep configuration and secrets in appropriate stores, protect reconciliation credentials, and test drift and rollback behavior. A UI can improve discovery, but its existence is not platform value. Measure time to a working service, successful changes, incident handoffs, support interrupts, upgrade adoption and platform reliability. Include the platform's own SLOs and recovery plan.

## Prove the value and operating capacity

The first rollout begins with low-risk stateless services. The team tests node loss, upgrade, image pull failure, secret rotation, namespace quota exhaustion, DNS failure and cluster API unavailability. It checks which services remain available when control-plane operations stop and which deployments must wait. It performs a restore of platform configuration and documents how to rebuild the cluster rather than assuming the cluster is its own backup.

After several months, teams deploy independently and share consistent signals; platform pager load remains within staffed capacity. A stateful workload stays on RDS because the platform team does not yet have an equal recovery offer for database operations. The architecture includes Kubernetes where the repeated scheduling and deployment needs justify it, and retains managed services where their contract is stronger.

Cluster upgrades illustrate the platform product's recurring work. The platform team pins supported Kubernetes and add-on versions, tests an upgrade in a representative environment, checks deprecated APIs and workload disruption budgets, then upgrades a canary node pool before expanding. Product teams receive a compatibility window and a clear owner for remediation. The platform publishes supported versions and an end-of-support date rather than silently changing every workload. If an upgrade fails, the team needs a supported reversal or forward-repair plan; control-plane rollback may not be available for every provider/version. Measure upgrade completion and workload impact, not simply whether the API server reports a new version.

 The operating model is part of the adoption gate. Product engineers practice diagnosing a rejected Pod, failed image pull and bad rollout, while the platform team practices node replacement and control-plane escalation. The cluster is accepted only when teams can locate the right owner quickly and understand which symptoms belong to the application, shared platform or cloud provider.

Exercises:

1. A namespace has a separate quota but any developer can create privileged Pods. What isolation remains absent?
2. A cluster API outage stops deployments, but existing Pods keep serving. How should this degraded state be documented?
3. Teams adopt a template but routinely edit generated resources after deployment. Which product contract may be failing?
4. A database team asks to move its stateful workload into Kubernetes. Which operation evidence is needed?

Answer guidance: quota limits resource consumption but not privilege, host access or cross-namespace/network access; enforce RBAC, admission, policy and isolation. Distinguish data-plane serving from control-plane management and define recovery/rollout implications. Investigate missing flexibility, poor defaults, ownership conflict or absent update path; measure user task completion and support cost. Demonstrate backup/restore, storage semantics, failover, upgrade, security, on-call expertise and comparative cost against managed RDS.

Review questions:

- What repeated team problem makes a shared cluster valuable?
- Which isolation layers are needed beyond namespaces?
- How are platform and application ownership divided?
- What operational tests should gate broad workload adoption?

Takeaways:

- Kubernetes is justified by workload and team needs, not by service count alone.
- A platform product includes ownership, policy, support, upgrades and recovery.
- Namespaces are one organization mechanism within a broader isolation design.
- Keep workloads outside the cluster when another service offers a better operating contract.

## Sources checked 2026-10-04

- [Kubernetes multi-tenancy](https://kubernetes.io/docs/concepts/security/multi-tenancy/) and [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) — shared-cluster risks and authorization.
- [Kubernetes network policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) and [Pod security standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) — workload controls.
- Chapters 192–194 and 103–120 — platform paths, tenant isolation, mesh and cluster operation.

DispatchDesk's organization and results are fictional. No cluster was deployed or tested.
