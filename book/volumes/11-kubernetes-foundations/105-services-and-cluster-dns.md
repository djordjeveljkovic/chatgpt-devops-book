---
book: The Complete DevOps Engineering Book
volume: 11
volume_title: "Kubernetes Foundations"
chapter: 105
title: "Services and Cluster DNS"
slug: services-and-cluster-dns
status: complete
summary: ../../_ai/chapter-summaries/105-services-and-cluster-dns.md
---

# Chapter 105 — Services and Cluster DNS

## Selectors, endpoints and virtual addresses

A Pod IP is a moving implementation detail. A replacement Pod can have a different address, and callers should not need to watch a Deployment rollout to find the current replicas. A Kubernetes Service gives a stable name and, for most service types, a stable virtual IP that routes connections to a changing set of backends. The EndpointSlice controller watches Pods selected by a Service and publishes matching backend information through EndpointSlices. A Service expresses discovery and routing intent; it does not start Pods or verify that an application returns correct responses.

The following Service targets the HTTP port declared by the Chapter 104 DispatchDesk Deployment. Save it as `service.yaml` and apply it in the same namespace as that Deployment:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: dispatchdesk-api
  namespace: production
  labels:
    app.kubernetes.io/name: dispatchdesk
    app.kubernetes.io/component: api
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: dispatchdesk
    app.kubernetes.io/component: api
  ports:
    - name: http
      protocol: TCP
      port: 80
      targetPort: http
```

`port` is the port clients use on the Service; `targetPort` is the backend Pod port. A named `targetPort` resolves to the matching named container port, so the Deployment labels its API port `http` and declares 8080. The Service listens on port 80 and forwards to each selected Pod's 8080. If `targetPort` is omitted it defaults to `port`. Using names can make a backend port change clearer, but the name must exist on the Pods. TCP is the default protocol, shown explicitly here.

The selector is a conjunction: a Pod must carry both labels to be selected. A typo, wrong namespace, or labels that differ from the Deployment template can leave the Service with no backends. Labels are not exclusive ownership claims; two Services can select the same Pod set, intentionally or by mistake. Keep selectors narrow, stable and aligned with the workload template. Avoid changing a live selector casually because that can redirect traffic immediately.

Kubernetes normally creates one or more EndpointSlices for a Service with a selector. They contain the addresses, ports and conditions for backend endpoints and may split a large set across multiple slices. Inspect the whole set by label, rather than assuming a Service maps to one legacy Endpoints object:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  get service dispatchdesk-api -o wide
kubectl --context kind-dispatchdesk --namespace production \
  get endpointslices -l kubernetes.io/service-name=dispatchdesk-api -o wide
kubectl --context kind-dispatchdesk --namespace production \
  get pods -l app.kubernetes.io/name=dispatchdesk,app.kubernetes.io/component=api \
  --show-labels -o wide
```

These commands read the Service address and port, its slices, and Pods matching the selector. EndpointSlice endpoint conditions can distinguish ready, serving and terminating endpoints; a Pod can match labels yet not be eligible for normal traffic because it is not ready. Review every slice and its conditions when diagnosing a partial backend set. Kubernetes has deprecated the older Endpoints API beginning with v1.33; new tooling should use EndpointSlices. See [Services](https://kubernetes.io/docs/concepts/services-networking/service/) and [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/).

For a normal `ClusterIP` Service, the virtual address is available inside the cluster. The data plane implementation, often kube-proxy but sometimes integrated into a network implementation, directs connections toward eligible backends. The Service's virtual IP is not a Pod address and usually cannot be reached from an arbitrary laptop. `type: NodePort` exposes a port on nodes, while `type: LoadBalancer` asks an implementation or cloud integration to provision an external load balancer; those choices introduce network exposure, cost and provider-specific behavior. A local kind cluster's Service does not automatically become internet-accessible by changing the type. Use Ingress or Gateway API for HTTP entry routing when an implementation is installed; neither is a replacement for the Service that selects backends.

Some systems need to route to endpoints outside Kubernetes. A Service without a selector can be associated with manually managed EndpointSlices; Kubernetes does not populate them from Pods automatically. This makes ownership and endpoint lifecycle the operator's responsibility. Do not copy Pod IPs into a hand-maintained slice as a shortcut for ordinary workload discovery. `ExternalName` is another special case: it returns a DNS CNAME for an external name and does not proxy traffic or create a virtual IP. A headless Service (`clusterIP: None`) has no virtual IP; DNS can return backend Pod addresses directly. Clients then need to handle address-set changes and connection selection themselves.

## Discovery and connection paths

Pods normally use cluster DNS to resolve Service names. A client in the same namespace can usually connect to `dispatchdesk-api`; the namespace-qualified form is `dispatchdesk-api.production`, and the fully qualified form includes `svc.<cluster-domain>`, commonly `dispatchdesk-api.production.svc.cluster.local`. The cluster domain can be configured differently, so do not hard-code `cluster.local` into application assumptions without checking the cluster. A short name is convenient within one namespace but can resolve unexpectedly if the application moves to another namespace. For cross-namespace configuration, use at least `service.namespace` and make the namespace explicit.

The resulting DNS answer for a regular ClusterIP Service is the Service's virtual IP, not a list of Pods. DNS resolution and connection success are separate steps: a name can resolve while the Service has no usable backends, or the destination process can refuse connections on the expected port. Headless Services differ because their DNS answers can contain endpoint addresses. SRV records can publish a port for a named Service port when a client uses them; most application clients instead configure a host and port directly.

The cluster DNS add-on, commonly CoreDNS, watches Kubernetes objects and answers queries from Pods. Pod DNS configuration usually includes a nameserver and search suffixes for its namespace and cluster domain. This allows short names to work but can add DNS queries when a name has multiple dots, depending on resolver settings such as `ndots`. Very long or incorrectly constructed names can be affected by search expansion and resolver behavior. Use a fully qualified name ending in a dot only when the client library's interpretation is understood; do not append a dot blindly to application configuration.

Older applications sometimes consume Service environment variables that kubelet adds when a Pod starts. That mechanism has an ordering constraint: the Service needs to exist before the client Pod is created for those variables to be populated. DNS discovery avoids that creation-order dependency and is generally the more flexible choice. Environment variables are also a snapshot for that Pod, while DNS can reflect Service address changes subject to client caching. Neither mechanism guarantees existing TCP connections will be moved when backends change.

From a workstation, `kubectl --context kind-dispatchdesk --namespace production port-forward service/dispatchdesk-api 18080:80` can be a useful diagnostic tunnel to a selected backend when the Service has a selector. It is not the Service's normal network path and does not demonstrate cluster DNS, client routing, load balancing, firewall policy or external reachability. To test the actual in-cluster path, run a client Pod in the cluster and connect by Service name. For application traffic, inspect the source and destination namespaces, DNS result, Service port, endpoint port, network policies and the server's listening socket as separate layers.

## Debugging a Service with no working backend

Suppose a rollout completed and the API Pods report Ready, but DispatchDesk cannot connect to `dispatchdesk-api.production`. The useful question is not simply whether the Service object exists. Trace the path in order: workload labels, Service selector, EndpointSlices and readiness conditions, Service port mapping, DNS, network policy, then process listener and application behavior. Each check narrows a different class of failure.

For a disposable Chapter 102 local cluster, apply the Service from the repository root after the Chapter 104 Deployment has been applied in `production`:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  apply -f service.yaml
kubectl --context kind-dispatchdesk --namespace production \
  get service dispatchdesk-api -o yaml
kubectl --context kind-dispatchdesk --namespace production \
  get endpointslices -l kubernetes.io/service-name=dispatchdesk-api -o yaml
```

`apply` changes the selected cluster; the other commands inspect the configuration and generated backends. If the EndpointSlice query returns no objects or no addresses, compare the exact Service selector with live Pod labels. Then inspect readiness, rollout state and events. A matching but unready Pod may be excluded from traffic; a matching ready Pod can still have an application that is broken. Do not remove readiness checks just to populate a slice: first establish that the application can serve requests correctly.

Next check that the Service's `port` and `targetPort` agree with the intended client and Pod listener. A named `targetPort` that does not resolve, or a numeric target port that differs from the actual listening socket, produces a backend path that cannot complete a connection. `containerPort` in a Pod spec is metadata; it does not open a socket. If DNS fails, first compare same-namespace, namespace-qualified and fully qualified lookups from a Pod. If all Service lookups fail, test a known built-in name such as `kubernetes.default.svc` from the same client Pod to separate general cluster DNS failure from one Service's record. Check the Pod's `/etc/resolv.conf`, the DNS Service and its EndpointSlices before changing CoreDNS settings.

For example, a temporary diagnostic Pod based on BusyBox can issue a DNS query from within the cluster. This creates a Pod and consumes local resources; use the Chapter 102 disposable context and remove it afterward. The tag below is illustrative, not a pinned production image:

```bash
kubectl --context kind-dispatchdesk --namespace production run dns-check \
  --image=busybox:1.36.1 --restart=Never --command -- sleep 300
kubectl --context kind-dispatchdesk --namespace production \
  wait --for=condition=Ready pod/dns-check --timeout=60s
kubectl --context kind-dispatchdesk --namespace production \
  exec dns-check -- nslookup dispatchdesk-api.production.svc.cluster.local
kubectl --context kind-dispatchdesk --namespace production \
  exec dns-check -- nslookup kubernetes.default.svc
kubectl --context kind-dispatchdesk --namespace production delete pod dns-check
```

If a diagnostic Pod with that name already exists, inspect it and choose another name rather than deleting an unknown workload. The bounded wait gives the image time to pull and the Pod time to become Ready. If it times out, inspect the Pod and events before interpreting a failed exec as a DNS problem. `nslookup` verifies name resolution from that Pod; it does not establish that TCP traffic is allowed or the application responds. A stricter lab image should be pinned by verified digest, and production debugging should use an approved image and workload rather than a temporary ad hoc Pod. NetworkPolicy can block traffic even when DNS and EndpointSlices look correct. Finally check application logs, the container's configured port and actual listener. Restore the intended selector or port only after collecting the evidence that identified the mismatch.

Cleanup is part of the diagnostic procedure. If the Service was created only for the lab, remove it and verify that the temporary Pod is gone. Deleting the Service removes its stable name and virtual IP, so do not use the cleanup command against a shared or production Service:

```bash
kubectl --context kind-dispatchdesk --namespace production delete service dispatchdesk-api
kubectl --context kind-dispatchdesk --namespace production get pods
```

In a real incident, recovery might mean correcting the selector, aligning the port, repairing a readiness failure, allowing the required network path, or fixing CoreDNS. Apply the correction through the source of truth, then verify EndpointSlice conditions and make a request from the same network location as the affected client. A successful DNS query proves only DNS; a successful TCP connect proves only the path to a listener; an application-level check must verify the response the client requires. This layered evidence avoids treating a healthy control-plane object as proof of working user traffic.

## Exercises and answer guidance

1. A Service exists and resolves to a ClusterIP, but its EndpointSlices contain no endpoints. What should be compared first? Compare the Service selector to Pod labels in the same namespace, then examine readiness and EndpointSlice conditions.
2. A client Pod in `analytics` cannot resolve the short name `dispatchdesk-api`, while a Pod in `production` can. What name should the cross-namespace client use? Use `dispatchdesk-api.production` or a fully qualified Service name, subject to the cluster domain.
3. A Service has one ready endpoint and DNS returns the correct ClusterIP, but requests time out. Name three remaining layers to inspect. Network policy/routing, Service port-to-targetPort mapping, and the process listener/application behavior are all candidates.
4. Does a `containerPort: 8080` declaration prove the process listens on 8080? No. It is metadata; inspect process configuration or test the listener.
5. A headless Service resolves directly to three Pod addresses. What must the client or application consider? It must handle endpoint churn and choose/retry connections because the Service does not provide a virtual IP proxy/load-balancing path.

Review questions: how does a Service selector become backend addresses, why are EndpointSlices preferable to the deprecated Endpoints API, what distinction exists between DNS success and application reachability, and which discovery form fits each client namespace and workload?

## Verification and primary sources

Official Kubernetes Service, EndpointSlice, DNS and Service debugging documentation was inspected on 2026-10-04. YAML and shell examples are illustrative; no Service, diagnostic Pod, network request or cluster query was executed. BusyBox is shown with a mutable example tag. Static checks do not prove cluster DNS configuration, network policy, EndpointSlice readiness, port reachability, image availability or application health.

Primary references: [Services](https://kubernetes.io/docs/concepts/services-networking/service/), [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/), [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/), and [Debugging Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/).
