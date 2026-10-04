---
book: The Complete DevOps Engineering Book
volume: 12
volume_title: "Kubernetes Production Engineering"
chapter: 113
title: "Ingress and Gateway API"
slug: ingress-and-gateway-api
status: complete
summary: ../../_ai/chapter-summaries/113-ingress-and-gateway-api.md
---

# Chapter 113 — Ingress and Gateway API

## The external request path

An application can have healthy Pods and a working ClusterIP Service while every public request fails. External traffic crosses additional boundaries: DNS, a cloud or on-premises load balancer, a Gateway or Ingress controller, a listener and route, the Service, and finally ready endpoints. Each layer has a separate owner and observable state. Troubleshooting starts by locating the first boundary where the expected request or response stops.

Kubernetes offers several ways to expose a Service. A `LoadBalancer` Service asks a supported integration to provision or attach an external load balancer for that Service. Ingress is a stable Kubernetes API for HTTP and HTTPS routing by host and path, but it requires a controller to implement the rules. Gateway API is an extensible add-on API family for infrastructure and advanced routing. The Kubernetes project has frozen the Ingress API and recommends Gateway API for new capabilities; Ingress remains supported and is not planned for removal. A platform should select an approach based on the cluster integration, required protocols and features, operational support and migration cost, rather than treating these objects as interchangeable. See the Kubernetes [Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) and [Gateway API](https://kubernetes.io/docs/concepts/services-networking/gateway/) documentation.

An Ingress object alone does not create a listener. A controller watches objects assigned to its `IngressClass`, programs a proxy or cloud load balancer and reports status according to its implementation. An Ingress rule usually identifies a host, path and Service backend; annotations and controller-specific resources may add behavior, but those extensions are not portable Kubernetes API guarantees. Verify the controller's supported version, class configuration, TLS behavior, health checks, source address handling and upgrade path. A resource accepted by the API server may still be ignored, rejected by the controller, or translated into behavior different from another implementation.

Gateway API separates infrastructure and route configuration into role-oriented resources. A `GatewayClass` describes a controller's class, a `Gateway` requests listeners and addresses, and route resources such as `HTTPRoute` attach application routing rules. This division can let a platform team own shared listeners and policy while application teams own routes in their namespaces. Cross-namespace references require explicit permission mechanisms, and the controller must support the requested attachment and route features. A Gateway API installation also requires the compatible CRDs and a controller; neither is guaranteed to exist in a cluster merely because Kubernetes supports custom resources. Read the selected controller's install and compatibility instructions before adopting it.

Gateway API has Standard and Experimental release channels, and conformance is version- and feature-specific. A controller's advertised support for one route type does not imply that it supports every optional filter or policy. Check the exact bundle version and published conformance report, then check the implementation's documentation for extended features, limits and defaults. Keep Experimental fields out of production unless the team explicitly accepts their compatibility contract. The Gateway API [versioning guide](https://gateway-api.sigs.k8s.io/docs/concepts/versioning/) and [conformance guide](https://gateway-api.sigs.k8s.io/docs/concepts/conformance/) explain these boundaries.

## Listener, route and TLS design

An external route has several names that must agree: the public DNS record, the listener hostname, the route host match, the TLS certificate names, and the backend Service and port. DNS may be managed outside Kubernetes, while a controller may publish an address in Gateway or Ingress status. An assigned address does not prove that DNS points to it or that a client can reach it. Conversely, DNS can resolve while the load balancer listener or backend is unhealthy. Record who owns DNS, certificates, public IP allocation, firewall policy, controller configuration and application route changes.

Use explicit hostnames and path semantics. Prefix matching, path rewriting, redirects and header modification can vary by API or implementation. Avoid relying on incidental controller defaults or undocumented annotations. Define whether a path is matched exactly or as a prefix, whether trailing slashes matter, and what the backend receives. Test both intended routes and nearby paths that should not match. If multiple routes can attach to a shared listener, use namespace labels, allowed route kinds and host ownership rules to constrain who can publish externally reachable paths.

TLS can terminate at an external load balancer, an ingress controller, a Gateway listener, or the application. At each termination point, decide where encryption continues, what certificate identity is checked on upstream connections, and whether the original client identity or source address is preserved. A TLS secret reference must be in an allowed namespace and supported by the controller. Certificate rotation, private key access, renewal alerts and expiry testing belong in the operating model. A successful TLS handshake at the edge does not show that the backend hop is encrypted or that the application authenticated the request. Do not place private key material in example manifests or logs.

The response path matters too. Health probes and load balancer health checks may use a different port, protocol, path or source range from user traffic. A route can be programmed while its backend Service has no ready endpoints. A backend can be healthy on its Pod IP yet fail because the Service port, target port, readiness state, policy or network path is wrong. [Chapter 105](../11-kubernetes-foundations/105-services-and-cluster-dns.md) covers Service behavior; [Chapter 112](112-cluster-networking-and-cni.md) covers Pod paths, CNI and policy. Understand whether the controller sends traffic to node ports, Pod IPs, a cloud target group or another proxy; that behavior changes source addresses, health checks, firewall requirements and failure modes.

## Operating controllers and routes

Treat an ingress or Gateway controller as a production service. It needs capacity, disruption planning, monitoring, secure administrative access, a supported upgrade process and a clear owner. Place replicas across appropriate failure domains where the implementation supports it, and confirm that the upstream load balancer can reach healthy replicas. Budget CPU and memory for connection counts, TLS handshakes and configuration churn. Controller availability is not the same as application availability: existing connections may continue during a controller outage while new configuration is not accepted, or traffic may stop depending on the data plane.

Observe both Kubernetes state and the controller's own status and telemetry. For Ingress, inspect `IngressClass`, events, controller logs, load balancer address and backend health. For Gateway API, inspect `GatewayClass`, `Gateway` and route status conditions such as acceptance and programming, along with events and implementation metrics. Conditions provide useful signals but are not end-to-end probes. They may show that a controller accepted configuration without proving external DNS, firewall reachability, TLS trust, backend readiness or a successful user request.

Use a small request matrix during rollout: correct host and path, unknown host, unknown path, valid and invalid certificate, healthy and unavailable backend, and both internal and external source locations that matter. Check redirect behavior and authentication boundaries. A canary route or controlled client can verify the data plane before DNS changes, provided it exercises the same listener and backend path. Observe latency, error rates, reset counts, certificate expiry and controller reconciliation errors. Preserve a way to return DNS or routing to the previous implementation until the new path has passed the service's acceptance checks.

DispatchDesk currently exposes its API through an Ingress controller. The platform team plans to move to Gateway API because it needs centrally owned listeners and application-owned route rules. The migration is not a YAML conversion exercise: the old controller's annotations encode rate limits, redirect rules and TLS behavior that may not have direct equivalents in the new implementation. The team inventories every public hostname, path, certificate, policy and annotation; maps each to a supported Gateway API field or controller-specific policy; and identifies behaviors that need an application or edge change. It then runs a canary hostname through the new Gateway, tests failure cases and backend identity, and only changes production DNS after the route and rollback plan are approved. Ingress remains available during the migration rather than being removed when the new controller is merely installed.

The Kubernetes project recommends Gateway API for new routing capabilities, but that recommendation does not make every installed controller or managed Kubernetes offering a drop-in replacement. Check whether the chosen provider installs the API, which controller reconciles it, what conformance version it reports, and which features require provider-specific policy. If required behavior exists only in a proprietary extension, record that dependency and migration path. For a small service needing only a stable external endpoint, `Service` of type `LoadBalancer` may be simpler than operating a shared HTTP routing layer.

## Read-only diagnostics and recovery

From an authorized administrative workstation with the intended kubeconfig, gather object and controller evidence before modifying a route:

```bash
kubectl --context kind-dispatchdesk get ingressclasses
kubectl --context kind-dispatchdesk --namespace production get ingress dispatchdesk-api -o wide
kubectl --context kind-dispatchdesk --namespace production describe ingress dispatchdesk-api
kubectl --context kind-dispatchdesk get gatewayclasses
kubectl --context kind-dispatchdesk --namespace production get gateways,httproutes
kubectl --context kind-dispatchdesk --namespace production get services,endpointslices
kubectl --context kind-dispatchdesk get events --all-namespaces --sort-by=.lastTimestamp
```

These are read-only Kubernetes API queries against the illustrative local `kind-dispatchdesk` context. Replace it only with the intended context after verifying its API endpoint and account. Some requested resources may be unavailable if their CRDs are not installed. Events are best-effort and may have aged out; controller names, namespaces, log locations and condition details depend on the implementation. Resource output can include internal addresses and annotations, so review it before sharing.

For a failing request, first reproduce with the exact hostname, path, protocol and client location. Resolve DNS and compare the address with the expected load balancer or Gateway status. Check listener and route status, host and path matches, TLS certificate identity, and whether the controller accepted and programmed the object. Then inspect Service ports and EndpointSlices for ready backends. If the backend is absent, troubleshoot selectors and readiness. If endpoints are ready but the request fails, test the backend path from an approved in-cluster client and examine policy, firewall, health-check and source-address behavior. Use controller metrics and logs to find configuration rejection, upstream connection failures, TLS errors or exhausted resources.

Do not expose a route broadly as a diagnostic shortcut. A temporary permissive host rule, public listener or firewall opening can bypass the intended security boundary and linger after the incident. Make a narrow, reviewed change with a named owner and expiry, test the precise path, and remove it after collecting evidence. If the controller is unhealthy, protect application traffic while restoring controller capacity or reverting the last route change. If DNS is wrong, correct the record with its owner and verify propagation from representative resolvers. If the backend is unhealthy, restore the application or endpoint instead of repeatedly changing edge routing. After recovery, verify TLS, host/path isolation, both request and response flows, and the observable user-facing SLI.

## Exercises and answer guidance

1. An Ingress object exists but has no external address. What should be checked? The referenced IngressClass and controller, controller events and logs, provider load balancer integration, and whether the controller publishes status; object existence alone does not provision or configure traffic.
2. A Gateway reports that a route is accepted, but clients receive connection timeouts. What remains unproven? DNS and external reachability, listener address and firewall, backend Service/endpoints, network policy and application health. Acceptance is not an end-to-end request test.
3. A controller migration reproduces paths but loses a rate limit configured through an old annotation. What is the safe response? Inventory and map behavior explicitly, identify a supported policy or application/edge implementation, test it in a canary, and preserve rollback before switching production traffic.
4. The TLS certificate is valid at the public edge. Does that establish encryption to the backend? No. Trace each TLS termination and upstream hop, and verify the backend certificate and identity policy where encryption is required.
5. A platform team wants every namespace to create arbitrary routes on a shared public listener. What should constrain that capability? Listener route-attachment rules, namespace ownership, hostnames, allowed route kinds, RBAC and implementation policy.

Review questions: what implements an Ingress object, how do Gateway API roles separate infrastructure and route ownership, what does conformance establish, and which independent layers must be verified during an external request failure?

## Verification and primary sources

Official Kubernetes Ingress and Gateway documentation and Gateway API versioning and conformance guides were inspected on 2026-10-04. The examples are read-only API queries and were not run against a cluster. No controller, CRD, route, DNS record, certificate or network resource was changed. Static checks cannot establish a controller's implementation behavior, external reachability, TLS configuration, DNS correctness, backend health or route isolation.

Primary references: [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/), [Kubernetes Gateway API](https://kubernetes.io/docs/concepts/services-networking/gateway/), [Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/), [Gateway API versioning](https://gateway-api.sigs.k8s.io/docs/concepts/versioning/), [Gateway API conformance](https://gateway-api.sigs.k8s.io/docs/concepts/conformance/), and [Gateway API implementations](https://gateway-api.sigs.k8s.io/docs/implementations/list/).
