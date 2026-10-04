---
book: The Complete DevOps Engineering Book
volume: 12
volume_title: "Kubernetes Production Engineering"
chapter: 119
title: "Operators and Admission Policy"
slug: operators-and-admission-policy
status: complete
summary: ../../_ai/chapter-summaries/119-operators-and-admission-policy.md
---

# Chapter 119 — Operators and Admission Policy

## Custom resources and controller contracts

Kubernetes controllers continuously compare desired state with observed state and take action to reduce the difference. A Deployment controller creates and replaces Pods until the workload matches its specification. An operator applies this controller pattern to a domain-specific application or service: a custom resource represents the desired state, and one or more controllers implement the operational knowledge needed to realize it. An operator may install, configure, upgrade, back up or recover software, but its capabilities and guarantees are specific to that implementation. Installing one adds code, permissions, dependencies and operational ownership to the cluster.

A CustomResourceDefinition (CRD) extends the Kubernetes API with a new kind and schema. Custom resources are stored and served by the API server; by themselves, they do not perform actions. A controller watches those objects and related resources, reconciles them and reports status. The API spec should describe user intent; controller-owned status should report observed state and conditions. A status such as `Ready=True` is only as meaningful as the operator's contract and probes. Check how the controller defines readiness, what it verifies, how it handles partial failure and how it retries. Kubernetes' [custom resource guide](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/) explains the API and controller model.

Read the custom API before adopting it. Understand namespaced versus cluster scope, schema validation, defaulting, version conversion, deprecation, status fields, finalizers, ownership references and supported upgrade paths. A CRD can persist data in the cluster's API datastore, so unbounded or high-frequency application data does not belong in custom resources. A finalizer can delay deletion while a controller performs cleanup; if the controller is unavailable, deletion can remain pending. Uninstalling only the operator can leave custom resources and managed resources without a reconciler. Deleting the CRD deletes its stored custom-resource instances and removes that API endpoint; recreating the CRD does not restore those objects. Before either action, follow the vendor's uninstall procedure, export or migrate any required state, understand external cleanup and verify the impact of finalizers and owned resources.

An operator's permissions define its reach. Inspect the ServiceAccount, Roles, ClusterRoles and bindings it installs. A cluster-scoped controller that can read Secrets or create arbitrary workloads has a large blast radius if compromised. [Chapter 115](115-rbac-and-workload-identity.md) covers workload identity and privilege review. Check the operator's image provenance, release process, supported Kubernetes versions, multi-tenant assumptions, upgrade instructions, backup and restore behavior, metrics and incident owner. Confirm which tasks are automated and which still require an administrator. A project that calls itself an operator does not automatically provide safe upgrades, tested restore or a vendor support contract.

## Admission and policy lifecycle

Admission control evaluates API requests after authentication and authorization and before accepted objects are stored. Mutating admission can change an object, often to apply defaults; validating admission can reject a request that violates policy. Built-in admission plugins, ValidatingAdmissionPolicy (VAP) using CEL, and dynamic admission webhooks have different capabilities and failure modes. Choose the simplest mechanism that expresses the required policy. Admission policy evaluates API writes; it does not continuously audit existing objects or replace runtime enforcement.

Pod Security Admission (PSA) is built in and enforces the Pod Security Standards at namespace scope. Its `enforce` mode rejects non-compliant Pods, while `warn` surfaces client warnings and `audit` records audit annotations without blocking. Namespace labels can pin a policy level and version. A phased rollout can first observe `warn`/`audit` results, remediate workloads and then enable `enforce`. Pod template warnings and enforcement are not identical: the enforcing check applies to the resulting Pod, while audit and warning modes also help identify violations in workload resources. Review exemptions carefully and document the owner and reason. See Kubernetes [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/) and [enforcement guidance](https://kubernetes.io/docs/setup/best-practices/enforcing-pod-security-standards/).

VAP lets cluster administrators express validation in CEL and bind a policy to selected requests. The policy defines match conditions and validations; a binding selects where it applies and chooses actions such as `Deny`, `Warn` or `Audit`. These actions have distinct effects, and `Deny` and `Warn` cannot be combined in the same binding. A policy may be scoped by resource, namespace selector, operation and other match rules. Test CEL behavior against representative objects, missing or null fields, updates and controller-generated resources. A policy that selects too broadly or evaluates an absent field incorrectly can block platform operations as well as application releases. Use warnings and audit data to learn the impact before enforcement, while recognizing that dry-run and test tooling must exercise the same match logic and policy version as production.

Admission webhooks provide external mutation or validation code and can perform checks beyond CEL, including calls to other systems. That flexibility introduces a network dependency on API writes. Review service availability, TLS trust, request timeout, API version compatibility, scope, side effects, re-entrancy and failure policy. A webhook with `failurePolicy: Fail` can reject matching requests when it is unavailable; `Ignore` can allow requests to continue when invocation fails, but a deliberate rejection returned by a reachable webhook still denies the request. A safe design often keeps mutation simple and validates the final object after mutation. Exclude dependent system components or namespaces when appropriate so an admission controller does not block the components it needs to recover. Kubernetes documents [dynamic admission control](https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/) and [webhook good practices](https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/).

Policy should encode a clear operational requirement, not every preference. For example, requiring a non-root security context may be appropriate for a workload namespace, but platform agents may require explicit exceptions. A rule that requires an image digest can improve immutability, but the image delivery system must reliably provide and update digests. A blanket rule rejecting all host access could block a legitimate node component if it is selected accidentally. Keep policy authorship and exception approval separate where risk warrants, version policies in source control, test them during Kubernetes upgrades and monitor denial volume and failure metrics.

## Decide whether an operator is justified

An operator is useful when the application has recurring lifecycle tasks that benefit from a declarative API and require domain knowledge: managing a replicated database, coordinating backups, handling failover or upgrading a multi-component system. It may be unnecessary when a Deployment, StatefulSet, Job, Helm chart, Kustomize overlay or managed service already covers the lifecycle with simpler ownership. Kubernetes recommends considering a standalone API when the workload is not naturally declarative, requires high-throughput data handling or needs synchronous transactional operations rather than desired-state reconciliation. See the Kubernetes [Operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/) and [custom resource design guidance](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/).

Compare the operator's value with its ongoing cost: control-plane API load, CRD lifecycle and conversions, controller capacity, permissions, webhook availability, backup coordination and on-call learning. Ask how it behaves when the API server, storage, cloud provider or one managed Pod is unavailable. Determine how upgrades preserve backward compatibility and whether the controller requires ordered upgrades. [Chapter 118](118-helm-and-kustomize.md) covers release packaging and rollback limits; [Chapter 120](120-upgrades-etcd-and-cluster-recovery.md) covers cluster recovery. Test restore and operator removal in an isolated environment. A healthy controller Pod does not prove that custom resources reconcile correctly or that the application is recoverable.

DispatchDesk considers an operator for its stateful reporting database because manual failover has become error-prone. The platform team compares the operator's supported database versions, backup and restore contract, storage integration, CRD upgrade path, RBAC and support ownership with a managed database service and the current runbooks. In a staging cluster, it tests a controller restart, failed replica, storage detach and restore from backup, and records which actions require a human. The operator is selected only after application owners can inspect its status, understand its failure behavior and execute recovery without depending on undocumented controller internals. A second proposal to install a custom webhook that rejects all privileged Pods is deferred until the team can scope exemptions and stage enforcement; the built-in PSA warn/audit modes provide earlier evidence with fewer moving parts.

## Inspect controllers and policy state

Read-only queries can show which APIs and controllers exist and how they report status:

```bash
kubectl --context kind-dispatchdesk get crds
kubectl --context kind-dispatchdesk --namespace production get deploy,serviceaccounts,roles,rolebindings
kubectl --context kind-dispatchdesk get clusterroles,clusterrolebindings
kubectl --context kind-dispatchdesk get validatingadmissionpolicies,validatingadmissionpolicybindings
kubectl --context kind-dispatchdesk get validatingwebhookconfigurations,mutatingwebhookconfigurations
kubectl --context kind-dispatchdesk --namespace production get events --sort-by=.lastTimestamp
```

Replace the illustrative context only after checking its API endpoint and account. Some resources may be unavailable on older or differently configured clusters; CRDs and custom resources vary by operator. These queries do not reveal all controller effects, external dependencies, stored application data or effective webhook reachability. Do not dump Secret contents while inspecting controller credentials. Review events and audit logs for the exact admission decision; denial messages and warning headers may identify the policy or webhook responsible.

If a new workload is rejected, preserve the exact request, namespace, user, operation and API response. Determine whether the rejection came from PSA, a VAP binding, an admission webhook, API validation or authorization. Compare the object to the policy version and match scope, then test a narrow compliant change. Do not disable all admission checks to make a release succeed. If a webhook is unavailable and its failure policy blocks writes, restore its service or follow a reviewed, time-bounded recovery procedure that preserves intended enforcement. If an operator resource is stuck, inspect its generation, status conditions, events, controller logs and managed-resource ownership. Avoid removing finalizers or deleting CRDs as shortcuts; first determine which cleanup or recovery action they protect.

## Exercises and answer guidance

1. A CRD is installed, but creating a custom resource does not create any Pods. Is the API broken? Not necessarily. A CRD stores and serves objects; a controller must watch and reconcile them.
2. An operator reports `Ready=True`. Does that prove a database backup can be restored? No. Inspect the operator's documented condition contract and perform an isolated restore and application validation.
3. A VAP has a valid CEL expression but no matching binding. Is it enforced? No. The policy and binding together determine where and how validation applies.
4. A webhook has `failurePolicy: Ignore`, but a matching request still receives a denial. How can that happen? The webhook may have been reached and deliberately returned `allowed: false`; failure policy applies to invocation errors, not successful policy rejection.
5. A cluster upgrade team plans to delete an operator's CRD before uninstalling its controller. What must be considered? Whether custom objects and managed resources need migration or cleanup, finalizers and stored versions, controller responsibilities and backup/restore evidence.

Review questions: what turns a custom resource into a declarative API, what is the operational contract of an operator, how do PSA/VAP/webhooks differ, and how should policy move from observation to enforcement?

## Verification and primary sources

Official Kubernetes custom resource, operator, PSA, VAP and admission webhook documentation was inspected on 2026-10-04. The commands are read-only examples and were not run against a cluster. No CRD, operator, policy, webhook, namespace label or workload was installed or changed. Static checks cannot establish an operator's support contract, reconciliation correctness, webhook availability, policy coverage, exception safety or recovery capability.

Primary references: [Custom Resources](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/), [Operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/), [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/), [Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/), [Dynamic Admission Control](https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/), and [Admission Webhook Good Practices](https://kubernetes.io/docs/concepts/cluster-administration/admission-webhooks-good-practices/).
