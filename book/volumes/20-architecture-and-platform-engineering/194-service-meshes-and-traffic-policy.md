---
book: The Complete DevOps Engineering Book
volume: 20
volume_title: "Architecture and Platform Engineering"
chapter: 194
title: "Service Meshes and Traffic Policy"
slug: service-meshes-and-traffic-policy
status: draft
summary: ../../_ai/chapter-summaries/194-service-meshes-and-traffic-policy.md
---

# Chapter 194 — Service Meshes and Traffic Policy

A service mesh can centralize workload identity, encrypted service-to-service transport, and selected traffic policy across many workloads. It also adds proxies or node-level dataplane components, a control plane, certificate lifecycle, new traffic paths and another source of latency and failure. The design decision is whether those shared capabilities solve a repeated problem worth operating.

For DispatchDesk, an API may call a notification worker and database. The mesh can authenticate one workload identity to another and supply transport telemetry. It cannot infer that an order is durably accepted, determine the customer's tenant authorization or make a provider retry safe. Those remain application and data contracts.

Harbor's two developers might implement a small number of authenticated service links using existing host/proxy controls without a mesh. Summit may receive useful defaults from its managed service platform and should evaluate feature/operating cost there. Atlas could have enough teams and service-to-service edges to justify shared policy, if platform owners can diagnose and upgrade it. Product selection follows the requirement and operation model, not the number of microservices alone.

## State the repeated requirement

Before choosing a mesh, identify the actual repeated need and evidence:

| Need | Mesh contribution to assess | Separate work that remains |
|---|---|---|
| Workload identity | Issue and validate mesh identities for participating workloads | Human/API identity, application authorization and trust-domain governance. |
| Encrypted in-mesh transport | Automate workload certificate exchange and transport protection | Gateway/client TLS, excluded traffic, external dependencies and end-to-end data protection. |
| Caller-specific network policy | Match authenticated workload identity to traffic policy | Tenant and user authorization inside the application. |
| Common traffic controls | Apply routing/timeouts/retries/telemetry from a shared control interface | Retry semantics, deadlines and application-level correctness. |
| Service communication visibility | Observe participating network operations | Business outcomes, telemetry access/cost and requests outside the mesh. |

Make each requirement testable. “Need mTLS” means define which workload pairs must authenticate, which transitions may carry plaintext, how mixed versions are handled and how the result is observed. “Need uniform retries” requires identifying idempotent operations and end-to-end deadlines. A policy that retries order creation can duplicate state unless the application contract prevents it.

Map current traffic by source identity, destination, protocol and ownership. Kubernetes labels that select a workload are mutable configuration; verify which release/controller owns them. Classify HTTP versus opaque TCP because L7 path/method rules require a proxy that can interpret the protocol. A mesh sidecar cannot infer HTTP semantics in an encrypted opaque tunnel without the necessary protocol context.

## Compare data-plane modes by operations

Istio's current documentation describes both sidecar and ambient modes; see [the mode comparison](https://istio.io/latest/docs/overview/dataplane-modes/). Details vary by exact release and platform. The distinction is not “old versus free.”

| Concern | Sidecar mode | Ambient mode |
|---|---|---|
| Workload dataplane | Proxy runs alongside each enrolled workload | Node-level ztunnel provides core L4 functions; optional waypoint proxies add L7 processing. |
| Resource/lifecycle | Per-workload proxy uses pod resources and joins its lifecycle | Node/waypoint components have separate ownership, capacity and lifecycle. |
| Enrollment | Injection/restart/version compatibility must be checked for each workload class | Node redirection and ambient enrollment must be verified; waypoint association governs selected L7 paths. |
| Protocol capabilities | Sidecar handles configured L4/L7 traffic through its proxy | Core ambient handles selected L4 capabilities; L7 capabilities need the appropriate waypoint path. |
| Troubleshooting | Compare app container and sidecar config/logs/counters | Inspect node tunnel, waypoint presence/routes and policy path separately. |
| Failure domain | An individual proxy can affect that workload, while control-plane config affects many | Node dataplane disruption can affect many colocated workloads; waypoint outage can affect its routed features. |

Assess installed-version support, resource use, upgrade strategy, network plugin and workload/security restrictions. Do not place a mixed set of proxy versions into production solely because the same CLI accepted all resources. An architectural decision record should name the supported mode and a tested migration/fallback path.

## Identity, encryption and authorization are distinct

Mutual TLS authenticates workload peers and protects their transport within its scope. It does not prove that a human caller may read a specific order. Likewise an HTTP authorization policy at the mesh can constrain which service account may call `POST /orders`; the API still needs to authorize the end-user, tenant and business operation.

The following scoped Istio resources are complete examples for a **staging** namespace named `dispatchdesk-mesh`. They assume both API and client workloads are already enrolled in the same Istio control plane, that their Pods carry the shown labels and that the workload port uses HTTP as expected by the policy. `cluster.local` is the usual example trust domain in upstream documentation; substitute the actual trust domain and inspect issued identities before applying.

```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: dispatchdesk-api-require-mtls
  namespace: dispatchdesk-mesh
spec:
  selector:
    matchLabels:
      app: dispatchdesk-api
  mtls:
    mode: STRICT
---
apiVersion: security.istio.io/v1
kind: AuthorizationPolicy
metadata:
  name: dispatchdesk-api-callers
  namespace: dispatchdesk-mesh
spec:
  selector:
    matchLabels:
      app: dispatchdesk-api
  action: ALLOW
  rules:
    - from:
        - source:
            principals:
              - cluster.local/ns/dispatchdesk-mesh/sa/dispatchdesk-client
      to:
        - operation:
            methods: ["GET", "POST"]
            paths: ["/orders", "/orders/*"]
```

With an ALLOW policy selecting the API, requests that match no rule are denied by that policy. It intentionally permits only the client service account's listed operations. This can block health probes, ingress or other legitimate callers if they use a different identity/path. Inventory and explicitly model those paths before enforcement. A missing service account credential, different trust domain or unenrolled source may present no matching principal and be denied.

Istio documents `STRICT` and peer policy scope in [PeerAuthentication](https://istio.io/latest/docs/reference/config/security/peer_authentication/) and workload principals/ALLOW matching in [AuthorizationPolicy](https://istio.io/latest/docs/reference/config/security/authorization-policy/). The stable API group is shown in the upstream examples for the inspected version; confirm installed CRDs and control-plane compatibility first.

## Validate the path before enforcing it

Review the current context and exact targets with the cluster-owner's change procedure. These commands are read-only or local analysis; the final `apply` changes staging policy and should occur only after its intended namespace state and object ownership are recorded.

```bash
kubectl config current-context
kubectl get namespace dispatchdesk-mesh
kubectl get pods -n dispatchdesk-mesh -o wide
kubectl get peerauthentication,authorizationpolicy -n dispatchdesk-mesh
istioctl version --context=mesh-staging
istioctl analyze --context=mesh-staging --namespace=dispatchdesk-mesh policy.yaml
```

The `analyze` command evaluates local manifests and, by default, can compare with cluster state. For fully local analysis, Istio documents `--use-kube=false`, but the local file set must be self-contained. Neither mode proves actual dataplane delivery or enforcement. It can identify selected configuration inconsistencies. See [istioctl analyze](https://istio.io/latest/docs/ops/diagnostic-tools/istioctl-analyze/).

Before applying, check whether either named object already exists and whether it is owned by GitOps or another manager. Do not overwrite existing production policy from a scratch file. For an owned staging change, render/review and apply through the designated controller; direct operation may conflict with reconciliation. Following the correct change path, a possible explicit command is:

```bash
kubectl apply --context=mesh-staging --namespace=dispatchdesk-mesh -f policy.yaml
kubectl get peerauthentication,authorizationpolicy -n dispatchdesk-mesh -o yaml
```

The first command creates or changes live policy. The second reads persisted API objects; neither demonstrates observed encrypted traffic or expected allow/deny results. Use an authorized client Pod with the intended service account to call the API, then a separately authorized test identity for a denial case. Confirm the application result and mesh authorization counters/logs. Reproduce with a real known record only in a test environment, and avoid creating an order merely to test a route.

## Troubleshoot evidence in order

| Symptom | First discriminating evidence | Interpretation |
|---|---|---|
| Client cannot resolve API name | Kubernetes Service, DNS and endpoint readiness | Mesh identity policy is not the first assumption if routing never resolves. |
| Plaintext connection refused after STRICT | Source enrollment/identity and destination proxy status | Expected if a required peer bypasses mesh encryption; validate migration scope. |
| Authenticated client gets mesh denial | Peer principal, selected labels, actual method/path and policy attachment | Check identity/trust-domain/config before widening the rule. |
| Traffic bypasses expected waypoint | Target type/label, waypoint status, service versus pod address and applicable AuthorizationPolicy | A label expressing waypoint intent alone does not prove L7 enforcement. |
| Mesh telemetry healthy while orders fail | Application state, database, queue and customer result | Transport policy does not establish durable business outcome. |
| Tail latency rises after enrollment | Per-proxy queue/CPU, route retries, app waits and dependency saturation | Mesh overhead and retry amplification are separate hypotheses to measure. |
| Configuration exists but endpoint has old policy | Control-plane sync, proxy config and reconciliation ownership | API persistence is not dataplane convergence. |

Istio's current [waypoint guidance](https://istio.io/latest/docs/ambient/usage/waypoint/) includes a subtle security condition: a waypoint label alone does not necessarily force traffic through that proxy if the waypoint is absent or the traffic type does not match. If L7 enforcement is a security requirement, require the expected waypoint identity at the workload and test direct-workload paths. This is a good example of why “configuration present” is weaker evidence than a negative bypass test.

For sidecar workloads, `istioctl proxy-status` and `istioctl proxy-config` provide proxy synchronization/configuration views. First find the actual API Pod and verify it has the expected proxy; then inspect its listeners/routes/clusters using that Pod identity and selected context. Ambient debugging follows its own ztunnel/waypoint diagnostics. A command reporting synchronized config still does not test a real request.

## Rollout, failure and recovery

Stage policy in a bounded namespace/workload class. Record baseline callers and status, apply a narrowly targeted policy, test each required caller and an unauthorized one, then widen only after owners accept the evidence. Monitor denied traffic, latency, application outcomes and proxy resources across a workload restart and control-plane update. Treat `PERMISSIVE` as a temporary migration mode with named exit conditions, not a permanent substitute for knowing which clients remain plaintext.

An overly broad STRICT policy can isolate a nonmesh peer. A wide ALLOW policy can defeat least privilege. A mis-selected label can apply to zero workloads while producing a reassuringly successful API update. Preserve the prior policy and identify GitOps/controller ownership before rollback. Removing a new policy may restore the prior API object but does not necessarily restore a prior traffic mode if other root/namespace/workload policy remains. Verify observed connectivity and state after recovery.

Every proxy and policy adds resource, version-skew and investigation overhead. Put application, sidecar/node tunnel and waypoint capacity in the connection budget. Mesh retries multiply application retries; ensure one overall deadline and operation idempotency. Security policy should fail in a way the organization understands under control-plane or dataplane loss; document whether existing connections continue and what new connections do for the selected mode/version.

## Exercises and decision record

1. An API ALLOW policy breaks an ingress health check. Identify the source identity and operation, add the smallest justified exception and keep an unauthorized client denied. Do not solve it by allowing every principal.
2. An ambient namespace label exists, but a direct Pod-IP request reaches the workload without the expected L7 policy. Explain the missing waypoint/enforcement path and test a direct route.
3. Explain why mTLS succeeds while a user from another tenant still must be rejected by the application. Name the workload and user identities separately.
4. Decide whether Harbor needs a service mesh for one API and one worker. A complete decision compares its explicit trust/operations need with a maintained reverse proxy or direct workload configuration, then counts control-plane/diagnostic work.

Record the capability being standardized, mode/version/provider, identity trust domain, included/excluded workload classes, policy owner, failure behavior, baseline tests, rollout/rollback steps, resource impact and a reconsideration trigger. Primary Istio/Kubernetes sources were inspected on2026-10-01. Policy was syntax parsed only; no cluster resources, mesh installation or workload traffic was changed or tested for this chapter.
