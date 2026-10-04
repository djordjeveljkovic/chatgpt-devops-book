---
book: The Complete DevOps Engineering Book
volume: 18
volume_title: "Security and Software Supply Chains"
chapter: 174
title: "Kubernetes Security Boundaries"
slug: kubernetes-security-boundaries
status: complete
summary: ../../_ai/chapter-summaries/174-kubernetes-security-boundaries.md
---

# Chapter 174 — Kubernetes Security Boundaries

**Section outline:** limit API identities and workload authority; enforce workload and network policy at the right boundaries; inspect a fictional cluster incident through access, policy and audit evidence.

## API access, workload policy and tenancy

Kubernetes security is distributed across the API server, identity provider, admission controls, workload specification, node, network implementation and storage. A namespace helps organize objects and scope some policies; it is not by itself a hard security boundary between mutually hostile workloads. A cluster operator must know which control plane and network implementation enforce the intended policy. [Chapter 173](173-container-security-in-practice.md) covers container runtime identity and privilege, while [Chapter 175](175-secrets-and-credential-rotation.md) covers secret lifecycle in depth.

Start with the Kubernetes API as a powerful control surface. Authentication answers who made a request; authorization determines whether that identity can perform the requested verb on a resource; admission can reject or mutate an otherwise authorized request. A workload's service account token is also an API credential, not merely a pod metadata field. Do not grant application service accounts broad cluster permissions for convenience. Set `automountServiceAccountToken: false` for workloads that do not call the Kubernetes API, and give a workload a dedicated service account and namespaced Role only when the API is part of its job.

Workload creation itself can convey indirect access. A user who can create Pods or workload controllers in a namespace may be able to mount namespace Secrets or ConfigMaps into a pod they control, run code under a powerful service account, or use a PVC. Kubernetes RBAC guidance calls out workload-creation privileges as a privilege-escalation path. A policy review that sees “cannot get secrets” can still miss that the same user can create a pod which reads them. Check verbs together with the resources and the workload's effective service account, admission rules, volumes and node placement.

Keep human and automation identities separate. Prefer group-based role bindings from the cluster's identity provider over shared long-lived administrator kubeconfigs. Use namespace `RoleBinding` for namespaced access when possible; reserve `ClusterRoleBinding` and `cluster-admin` for operators with a specific cluster-wide duty. Avoid wildcard verbs/resources, and recheck custom-resource permissions when new APIs or operators are installed. A new resource type can make an old wildcard grant more powerful. Remove departed user bindings and stale service accounts, and review access periodically.

Here is a deliberately limited viewer role for the fictional `dispatchdesk` namespace. It grants read access to selected core workload and service discovery objects, and binds that role to an identity-provider group. It does not grant Pod creation, Secret access, exec, port-forward or cluster-scoped permissions:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: dispatchdesk-observer
  namespace: dispatchdesk
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "endpoints"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dispatchdesk-observers
  namespace: dispatchdesk
subjects:
  - kind: Group
    name: dispatchdesk-readers
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: dispatchdesk-observer
  apiGroup: rbac.authorization.k8s.io
```

The API group for core resources is the empty string. `RoleBinding` keeps these permissions in `dispatchdesk`; the referenced Group name must match the authenticated identity provider's group claim. Listing pods reveals workload metadata and specifications, so even read access should be granted to people who need it. Apply this file with `kubectl apply -f` only after confirming cluster context, namespace and review. Inspect the resulting bindings and test intended and denied actions:

```bash
kubectl auth can-i --list -n dispatchdesk
kubectl get role,rolebinding -n dispatchdesk
kubectl auth can-i create pods -n dispatchdesk --as=reader@example.invalid
```

The first command asks the API to evaluate the current identity's permissions in a namespace. The second reads the namespaced authorization objects. The third tests an impersonated user; it succeeds only if the caller is allowed to impersonate that user, so failure can mean missing impersonation rights rather than a workload permission result. `--as` does not log in through the configured identity provider or automatically reproduce its group claims. Test the actual group binding with a controlled provider-backed account, then check both allowed and denied operations. A YAML manifest describes desired authorization; these commands inspect API state and an authorization decision, not whether every external identity provider maps claims as expected.

## Pod Security and network controls

Pod Security Admission enforces the built-in Pod Security Standards at namespace boundaries. The `privileged`, `baseline` and `restricted` levels are cumulative choices with different compatibility costs. Restricted is appropriate for many application namespaces, but a Pod that needs host access, added capabilities or unusual volume types may be rejected. Do not label a namespace without first inventorying existing workloads and exceptions. Start with audit and warning, fix manifests, then enforce a version-pinned policy when the namespace is ready.

This example shows the namespace labels for a staged rollout. The version is illustrative: replace `v1.34` with the Kubernetes minor version chosen for the cluster. Pinning makes the standard's interpretation stable across control-plane upgrades; teams should intentionally revise it as they test a newer standard.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: dispatchdesk
  labels:
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/audit-version: v1.34
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/warn-version: v1.34
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/enforce-version: v1.34
```

Audit and warning labels surface violations while baseline is enforced. Before enforcement, use server-side dry run with the intended namespace-label change to receive warnings about existing Pods. That check does not inspect every dormant Deployment, Job or CronJob template. Validate rendered Pod templates in a staging namespace with the intended admission level, then update production templates and roll out their controllers so new Pods are admitted under the new policy. Enforcing a stricter label rejects future Pod admissions; it does not evict or repair Pods that are already running. After existing workloads satisfy restricted policy and a test rollout confirms expected behavior, change `enforce` to `restricted`. A policy version is independent of the cluster's available API version; check the target cluster and its Kubernetes documentation before applying. Pod Security Admission does not replace controls for RBAC, node access, image source, network reachability, secret use or host-level configuration. It checks Pod security fields at admission; it cannot prove an image is safe or an application has correct authorization.

NetworkPolicy restricts layer 3/4 traffic for selected pods, but only if the cluster's network plugin enforces the API. An API object can exist and show as applied while a plugin without support ignores its effect. Policies are additive: if multiple policies select a pod, allowed traffic is their union. Pods are non-isolated by default in a direction until a policy selects them for that direction. A default-deny egress policy also blocks DNS unless DNS traffic is separately allowed. NetworkPolicy cannot block a Pod's localhost traffic or traffic from its resident node; behavior for `hostNetwork` Pods is undefined and commonly follows node-IP behavior. Use host firewall, node or admission controls for those paths. These semantics make a policy rollout a connectivity change that needs tests for required clients, health checks, DNS and provider endpoints.

The following namespace-wide deny is a starting point for a carefully staged environment, not a complete production policy:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: dispatchdesk
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

It isolates every pod in the namespace for both ingress and egress. It does not provide allow rules, so DNS lookups, API calls, metrics scraping and service-to-service requests may stop. Before applying, map the actual traffic flows and add narrow policies for required peers and ports. NetworkPolicy does not express application-layer identities, URLs or all external policy needs; use egress gateways, cloud firewalls or service-mesh controls when the threat model requires those attributes. Verify the plugin with a test workload by attempting both allowed and denied flows, and record observed results. Reading back YAML is not enforcement evidence.

Treat namespaces as an administrative unit, not the only tenancy control. For teams with different trust levels, combine namespace-specific RBAC, admission policy, quotas, network segmentation, dedicated node pools where needed, and controls on who can edit policy. A team that can change its own NetworkPolicy or remove the Pod Security labels may undo those boundaries. Restrict namespace labels and policy objects through RBAC and admission rules. Workloads that handle secrets or public traffic may warrant stronger isolation than a namespace default, including separate nodes or clusters when the residual risk justifies the operational cost.

The API server and etcd deserve special attention. Restrict network access to the API endpoint and etcd; protect API authentication material; enable audit logging with an appropriate retention and access policy; and configure encryption at rest for Secrets when required by the data threat model. Encryption at rest protects stored object representation, but an authorized API reader or a pod mounting the Secret can still obtain plaintext. Backups must be protected separately. Audit logs can show API actions, but they need reliable timestamps, durable restricted storage and a response process to be useful during an investigation.

## A cluster threat and permissions review

DispatchDesk has separate namespaces for `dispatchdesk`, `monitoring` and `platform`. A developer receives a namespaced “deploy” role to update the app. Later, a pipeline identity is mistakenly bound to a broad ClusterRole so it can inspect a custom rollout resource. A malicious change uses that identity to create a pod in the application namespace, mounts a database Secret, and reaches the database over unrestricted east-west traffic. The original assumption was that namespace separation and absence of direct Secret `get` permission made the application boundary safe. Workload creation, service-account selection, admission and network access were never reviewed together.

Respond by freezing new deployments from the affected identity and preserving API audit logs, binding changes, admission events and controller records. Revoke or narrow the broad binding after confirming an alternate administrator path. Rotate credentials the malicious pod could read; removing the Pod is not credential rotation. Inspect service accounts, RoleBindings, ClusterRoleBindings, pods, volumes, image digests and network policies in affected namespaces. Determine whether the pod ran, which node it used, whether it could reach data services, and which external credentials it mounted. Contain only after preserving enough evidence to reconstruct the access path, unless active harm requires immediate isolation.

The team then compares intended access with live API state. An operator can inspect all-role bindings, but command output must be scoped and protected because it may include sensitive names or configuration:

```bash
kubectl get rolebindings,clusterrolebindings -A -o wide
kubectl get pods,serviceaccounts,networkpolicies -n dispatchdesk
kubectl get namespace dispatchdesk --show-labels
kubectl get events -n dispatchdesk --sort-by=.metadata.creationTimestamp
```

These are read-only API queries; the events list is best-effort evidence with retention and ordering behavior determined by cluster configuration. Compare the manifests with version control, then review audit records for who created the binding and pod, which identity performed each request, and whether any reads or exec operations followed. Test RBAC decisions for the actual pipeline principal and application service accounts. Inspect admission warnings/denials and the network plugin's enforcement evidence. If audit policy omitted relevant request bodies or logs have expired, say what cannot be established; absence of a retained event is not proof the action never occurred.

Recovery begins from a known-good policy and credential state. Remove unauthorized access paths, rotate exposed secrets and tokens, patch the identity binding, add a default-deny network policy with explicitly tested exceptions, and stage restricted Pod Security enforcement. Rebuild affected workloads from trusted images and redeploy only after policy tests pass. Reconcile database and customer state with application owners. Record the incident timeline, evidence sources, containment decisions, residual uncertainty and a follow-up owner for each policy gap. If the threat includes control-plane compromise or etcd write access, a namespace-level cleanup is insufficient; engage the cluster owner and rebuild or restore control-plane trust according to the cluster recovery plan.

Exercises:

1. A service account has no `get secrets` verb but can create deployments in a namespace containing database credentials. Explain the indirect risk and name two controls that can reduce it.
2. A default-deny egress policy is applied and the application can no longer resolve its database service. What assumptions about DNS and NetworkPolicy enforcement should be checked first?
3. A namespace has Pod Security audit and warning at `restricted`, but enforce remains `baseline`. What evidence is needed before moving enforce to restricted, and how should the standard version be selected?

Answer guidance: a workload creator can create a pod that mounts a namespace Secret or select a powerful service account unless admission and other controls prevent it. Restrict workload creation, disable unnecessary service-account token mounting, scope permissions, enforce Pod Security and protect Secret volume access through admission/RBAC. Check that the CNI enforces NetworkPolicy, inspect whether the pod is isolated for egress, and allow DNS to the actual cluster resolver before testing the database path. Review namespace-label dry-run warnings for existing Pods, validate dormant templates in a staging namespace, fix or document exceptions, canary the policy, then pin the standard to a version matching the target cluster's minor release. Update controller templates and roll them out so the replacement Pods receive admission checks.

Review questions:

- Why can permission to create Pods be more powerful than permission to read a Secret directly?
- What do Pod Security Admission and NetworkPolicy each enforce, and what do they leave to other controls?
- Which kinds of evidence establish that a declared cluster policy is enforced at runtime?

Takeaways:

- Treat API identities and workload creation as privileged control paths; scope permissions by namespace and function.
- Use Pod Security Admission and NetworkPolicy with staged rollout, version awareness and confirmed implementation support.
- Namespace boundaries need protection against users who can edit their own policies or select powerful service accounts.
- Preserve API, admission and network evidence during response, then rotate exposed credentials and recover from trusted policy.

## Sources checked 2026-10-04

- [Kubernetes RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) — least privilege, workload creation risks, service-account tokens and periodic review.
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) and [namespace enforcement](https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/) — policy levels, label enforcement, audit/warn rollout and version labels.
- [Kubernetes NetworkPolicies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) — implementation requirement, isolation semantics, additive rules and DNS implications.
- [Securing a cluster](https://kubernetes.io/docs/tasks/administer-cluster/securing-a-cluster/) — API access, audit, etcd and encryption-at-rest context.
- [Kubernetes security checklist](https://kubernetes.io/docs/concepts/security/security-checklist/) — current security review areas and version considerations.

The commands and manifests are documentation examples checked against Kubernetes documentation on the listed date. No live cluster, API identity provider, CNI enforcement, admission policy, audit backend, etcd, secret rotation or incident response was exercised.
