---
book: The Complete DevOps Engineering Book
volume: 12
volume_title: "Kubernetes Production Engineering"
chapter: 115
title: "RBAC and Workload Identity"
slug: rbac-and-workload-identity
status: complete
summary: ../../_ai/chapter-summaries/115-rbac-and-workload-identity.md
---

# Chapter 115 — RBAC and Workload Identity

## Identity, authentication and authorization

Kubernetes access has two separate questions: who is making a request, and what may that identity do? Authentication establishes a username, groups or service account for an API request. Authorization evaluates that identity and request against configured policy. A successful login does not imply permission to read an object, and a well-scoped Role cannot compensate for a credential that is broadly distributed or never expires. Production access design covers human identity, automation, workload identity, credential lifetime, authorization, audit and revocation together.

Kubernetes user identities are generally supplied by an external authentication mechanism; the API server treats them as identity data rather than requiring a built-in user object. ServiceAccounts are namespaced Kubernetes objects intended for workloads and automation. Every namespace has a `default` ServiceAccount, and a Pod without an explicit service account uses it. A ServiceAccount name alone has no special privilege; the effective access comes from bindings and other authorization mechanisms. Create distinct workload identities instead of relying on the default account, and grant each only the API access it needs. See Kubernetes [ServiceAccounts](https://kubernetes.io/docs/concepts/security/service-accounts/) and [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/).

Role-based access control (RBAC) evaluates API groups, resources, subresources, verbs and sometimes resource names. A `Role` grants permissions within one namespace; a `RoleBinding` attaches a Role or ClusterRole to subjects in that namespace. A `ClusterRole` can describe cluster-scoped permissions or reusable namespaced permissions, and a `ClusterRoleBinding` grants its rules across the cluster. Prefer namespace-scoped bindings where they fit. A RoleBinding to a ClusterRole still grants within the RoleBinding's namespace; a ClusterRoleBinding grants cluster-wide access to the ClusterRole's rules. Review the subject, referenced role and scope together.

RBAC verbs describe API operations, not safe intentions. `get`, `list` and `watch` on Secrets can reveal secret data; `nodes/proxy` access can reach kubelet APIs and is not a harmless read permission. Permission to create Pods or workloads can allow a principal to use any ServiceAccount in that namespace and mount many Secrets or ConfigMaps accessible there. A namespace is useful for organization and policy, but it is a weak boundary between mutually untrusted tenants unless admission, Pod security, network policy, storage and other controls reinforce it. [Chapter 112](112-cluster-networking-and-cni.md) discusses NetworkPolicy; avoid treating a namespace boundary as a substitute for authorization. Avoid wildcard verbs/resources and broad `cluster-admin` grants. The Kubernetes [RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) describes privilege escalation paths that ordinary role reviews can miss.

## Design permissions around operations

Start from the action an identity must perform, not from a role name such as "developer" or "viewer." List API objects, verbs, namespace scope, frequency and operational purpose. A human who views Deployments may not need to read Secrets. A release controller that patches a Deployment may not need permission to create Pods, read all ConfigMaps or change its Role. A metrics reader may need selected API discovery, but should not receive wildcard access to future custom resources.

The following is a review example for a controller that reads a named ConfigMap in the `production` namespace. It does not grant Secret access or workload mutation:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: dispatchdesk-config-reader
  namespace: production
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  resourceNames: ["dispatchdesk-settings"]
  verbs: ["get"]
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: dispatchdesk-api
  namespace: production
automountServiceAccountToken: false
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dispatchdesk-config-reader
  namespace: production
subjects:
- kind: ServiceAccount
  name: dispatchdesk-api
  namespace: production
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: dispatchdesk-config-reader
```

This manifest illustrates object relationships; it is not an instruction to apply to a live cluster. The example's `automountServiceAccountToken: false` prevents automatic API token mounting for Pods using that service account unless a Pod-level setting overrides it. If the workload needs the Kubernetes API, explicitly design its token flow and permissions rather than disabling the token and assuming access will work. Test the exact identity and request in a disposable environment before release. For a controller that watches many dynamically named objects, `resourceNames` may not fit its list/watch pattern; design the minimum permissions required by the client's API behavior and verify them with the controller's official instructions.

Review escalation-sensitive capabilities carefully. Permissions to create or bind roles, impersonate identities, approve client certificate requests, create ServiceAccount tokens, modify admission webhooks, patch namespace labels or access the kubelet proxy can grant much broader power than their names suggest. Permission to create arbitrary PersistentVolumes may expose host files through `hostPath`. Treat permission reviews as analysis of reachable effects, not just a count of verbs. [Chapter 119](119-operators-and-admission-policy.md) covers admission controls that can reinforce workload boundaries. Separate cluster administration from routine deployment, require a controlled break-glass path and audit its use.

Human access should use the organization's identity provider and short-lived authentication where supported by the Kubernetes distribution. Avoid shared kubeconfigs and long-lived client credentials because attribution and revocation become difficult. Separate read, deploy and administrative identities; require stronger approval for cluster-wide changes; and make offboarding remove both identity-provider membership and any remaining cluster bindings. Review effective access periodically and after team, namespace or service ownership changes. Preserve audit records for authentication, authorization denials and privileged operations.

## Workload tokens and external services

By default, Kubernetes makes ServiceAccount credentials available to Pods. Workloads that do not call the API should opt out of automatic token mounting at the Pod or ServiceAccount level. A workload that does need API access should use a dedicated ServiceAccount with minimal RBAC. Avoid copying a static ServiceAccount token into a Secret or image. Modern projected ServiceAccount tokens are short-lived and can be rotated by kubelet; they carry an audience and can be bound to an object. Consumers must validate the intended audience and expiry. A projected token mounted through `subPath` does not receive updates, so use a regular projected volume mount when rotation is expected. See the Kubernetes [projected volume guide](https://kubernetes.io/docs/concepts/storage/projected-volumes/) and ServiceAccount token guidance.

A Kubernetes ServiceAccount token is not automatically a cloud-provider credential. Cloud workload identity typically uses federation: a cloud identity provider trusts signed cluster tokens with a specific issuer, audience and subject, then grants an external role. The exact annotations, webhooks, token exchange, trust policy and supported audiences are provider-specific. Configure the narrowest subject and resource scope, keep the cluster issuer and provider trust relationship current, and monitor failed exchanges. Do not place cloud access keys in Pod environment variables as a shortcut. Verify the provider's current official workload-identity documentation and test that a Pod with the intended identity can access only the required resource.

When a workload serves multiple environments, do not reuse one high-privilege ServiceAccount across namespaces or clusters without a specific trust design. Keep identity claims stable and explicit, and ensure a compromised Pod cannot mint or read credentials for unrelated workloads. Token requests and impersonation are privileged operations. Be especially careful with controllers that can create Pods: unless admission and identity controls constrain the workload, Pod creation may provide access to another account's mounted token and namespace resources.

DispatchDesk's report processor needs to read one configuration object and publish status updates to its own Deployment. An initial permission request asks for `cluster-admin` because an engineer used an administrator kubeconfig during development. The platform team maps the actual API calls, assigns a dedicated ServiceAccount, scopes configuration access to the required namespace and grants only the necessary workload update. It disables token automount if the processor does not need Kubernetes API calls directly, and uses a separate federation path for its object-storage access. The team tests both expected success and denied access to a Secret, another namespace and an unrelated cloud bucket. The denied cases matter: a system that performs its task but can also reach unrelated data has not met least privilege.

## Inspect and test effective access

Review Role and ClusterRole rules together with all bindings and subjects. Use an authorized context and avoid commands that dump Secret values. The following inspections are read-only:

```bash
kubectl --context kind-dispatchdesk --namespace production get serviceaccounts,roles,rolebindings
kubectl --context kind-dispatchdesk get clusterroles,clusterrolebindings
kubectl --context kind-dispatchdesk --namespace production describe role dispatchdesk-config-reader
kubectl --context kind-dispatchdesk --namespace production describe rolebinding dispatchdesk-config-reader
kubectl --context kind-dispatchdesk --namespace production auth can-i get configmap/dispatchdesk-settings \
  --as=system:serviceaccount:production:dispatchdesk-api
kubectl --context kind-dispatchdesk --namespace production auth can-i get secrets \
  --as=system:serviceaccount:production:dispatchdesk-api
```

Replace the illustrative context with a verified local target. `kubectl auth can-i --as` requires the caller to be authorized to impersonate the tested identity; a denial may reflect missing impersonation permission rather than the target's effective access. An affirmative answer evaluates authorization for that request but does not prove the application can authenticate, reach the API, or use a credential securely. Inspect the full subject set and role rules; a ServiceAccount may receive permissions through multiple bindings, including cluster-wide bindings. Avoid `get secrets -o yaml` during routine review because it exposes secret contents.

During a production access incident, identify the exact caller, API server, namespace, verb, resource and timestamp from audit evidence. Check whether authentication succeeded, then examine the authorization decision and all applicable bindings. A `Forbidden` response differs from a network timeout or invalid token. If credentials may be exposed, revoke the trust or binding and rotate external credentials using the provider procedure; deleting a Pod does not necessarily revoke every credential copied elsewhere. If a workload unexpectedly reads a Secret, investigate its effective RBAC, ability to create Pods, mounted service accounts and admission controls. Preserve relevant audit evidence before removing objects, then test both the repaired operation and previously reachable unauthorized paths.

## Exercises and answer guidance

1. A user can create Deployments in a namespace but cannot get Secrets. Is Secret access impossible? No. Workload creation can let the user run a Pod as another ServiceAccount and mount namespace Secrets. Treat deployment rights as powerful and enforce workload/admission boundaries.
2. A service account has no direct RoleBinding but can list cluster resources. What should be checked? ClusterRoleBindings and all bindings for its groups/identity, plus non-RBAC authorization mechanisms and the actual authenticated identity.
3. A Pod does not use the Kubernetes API. What should its token policy be? Disable automatic token mounting and test that the application still works; use an explicit projected token only if there is a documented API or federation requirement.
4. `kubectl auth can-i` returns no while impersonating a ServiceAccount. Does that prove the workload cannot perform the operation? Not necessarily. The inspecting caller may lack impersonation rights, the cluster may use other authorization mechanisms, or the test identity may not match the Pod's actual service account. Correlate with bindings and authorized audit/testing.
5. A token issued for the API server is presented to an unrelated external service. What should the receiver enforce? Its expected issuer, audience, subject, signature, expiry and trust policy; do not accept a token solely because it is a valid JWT.

Review questions: how do authentication and authorization differ, how do RoleBinding and ClusterRoleBinding scope access, why can workload creation imply Secret access, and how do short-lived tokens and workload federation reduce credential exposure?

## Verification and primary sources

Official Kubernetes RBAC, ServiceAccount, projected token and security guidance was inspected on 2026-10-04. The manifest is illustrative and was not applied. The `kubectl` examples are read-only and were not run against a cluster. No identity provider, cloud trust, token, role, binding, workload or Secret was modified or queried for contents. Static checks cannot prove effective access in a particular cluster, provider federation configuration, authentication strength, audit completeness or incident revocation behavior.

Primary references: [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/), [RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/), [ServiceAccounts](https://kubernetes.io/docs/concepts/security/service-accounts/), [projected volumes](https://kubernetes.io/docs/concepts/storage/projected-volumes/), [configure ServiceAccounts for Pods](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/), and [application security checklist](https://kubernetes.io/docs/concepts/security/application-security-checklist/).
