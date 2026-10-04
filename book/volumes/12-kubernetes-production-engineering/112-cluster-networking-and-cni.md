---
book: The Complete DevOps Engineering Book
volume: 12
volume_title: "Kubernetes Production Engineering"
chapter: 112
title: "Cluster Networking and CNI"
slug: cluster-networking-and-cni
status: complete
summary: ../../_ai/chapter-summaries/112-cluster-networking-and-cni.md
---

# Chapter 112 — Cluster Networking and CNI

## Pod routing and network implementation

Kubernetes networking has several paths that look similar to an application but are implemented by different components. Containers in one Pod share a network namespace and can use `localhost`. Pod-to-Pod communication uses the cluster's Pod network. Pod-to-Service traffic uses a stable Service address or name and a service-routing implementation. Traffic from outside the cluster enters through a separate path such as a load balancer, Ingress or Gateway. When an API call succeeds but an application connection fails, identify which path is broken before changing routes or firewall rules.

The Kubernetes network model expects every Pod to have a cluster-reachable IP and permits Pods to communicate with each other without address translation between Pod IPs, subject to network policy and implementation. Nodes have their own addresses, and Services have virtual addresses from a separate range. Plan Pod and Service ranges alongside node subnets, connected VPCs, office networks, VPNs, peered clusters and external dependencies so that addresses do not collide where routes must interoperate. Some CNIs allocate Pod IPs from the same VPC subnets used by nodes, while others use a distinct Pod CIDR with overlay or routed paths; follow the chosen implementation's allocation and routing model. If `10.0.0.0/8` is already used by a corporate network and a cluster independently allocates an overlapping Pod range, routing can become ambiguous when traffic leaves or crosses a boundary. Choose ranges from an inventory, not from a copied example.

The Container Network Interface (CNI) is the common plugin interface used by container runtimes to configure Pod networking. The CNI plugin or broader network implementation allocates Pod addresses, configures interfaces and routes, and may implement network policy, encryption, observability or service routing. Kubernetes defines APIs and behavior expectations, but it does not supply every network implementation itself. A cluster can use an overlay that encapsulates Pod packets between nodes, a routed Pod network that advertises Pod CIDRs, or a provider-integrated design. Each has different dependencies on node routes, security rules, MTU, IP capacity and operations. A plugin may also replace kube-proxy for Service traffic; inspect the installed architecture rather than assuming every cluster has the same agents. Read the Kubernetes [network model](https://kubernetes.io/docs/concepts/cluster-administration/networking/), [network plugin requirements](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/) and the selected implementation's support matrix.

Capacity planning includes addresses. Some network implementations allocate Pod IPs from a per-node block or from a cloud subnet, so a node's practical Pod density can be limited by available addresses before CPU or memory is exhausted. Dual-stack clusters need compatible Pod, Service and node families with matching primary-family configuration. A design that works in IPv4 can fail when an IPv6 route, firewall or client assumption is missing. Record subnet sizes, reserved addresses, allocation behavior, node limits and expansion path alongside compute capacity.

MTU is the maximum packet size that a link can carry without fragmentation. Encapsulation adds headers, reducing the usable inner-packet size on an overlay path. If the node or CNI MTU is inconsistent with the underlying path, small health checks may succeed while larger TLS or API responses stall or fragment. Diagnose MTU only after confirming source/destination addresses, routes and packet loss; do not lower it arbitrarily because that can reduce throughput. Use the network implementation's documented calculation and test from Pods across the relevant nodes and tunnels.

Services do not create a physical listener on each Pod. A `ClusterIP` is a virtual address whose packets are directed to eligible endpoints through kube-proxy or an alternative service implementation. DNS usually resolves the Service name to that virtual address; EndpointSlices describe the backing endpoints. A headless Service resolves to endpoint IPs instead. [Chapter 105](../11-kubernetes-foundations/105-services-and-cluster-dns.md) covers selectors, DNS and service troubleshooting. Debug Service discovery separately from raw Pod-to-Pod routing: a healthy Service object cannot make an unreachable Pod network work, and a reachable Pod IP does not prove that the Service selector, port mapping or readiness state is correct.

## Network policies and reachability

NetworkPolicy is an API for selecting Pods and describing allowed ingress and egress traffic. In a namespace with no applicable policy, Kubernetes' standard behavior is to allow all ingress and egress. A policy isolates selected Pods for the directions it declares and allows matching traffic; multiple applicable policies combine additively. The API expresses allow rules rather than a general explicit-deny ordering system. A policy is effective only if the network implementation enforces NetworkPolicy. Creating a policy object on a cluster whose CNI does not enforce it can leave traffic behavior unchanged, so verify support and test actual paths.

An ingress policy selects destination Pods, then permits traffic from matching Pod/namespace selectors or IP blocks on specified ports. An egress policy selects source Pods and permits destinations and ports. A default-deny egress policy also blocks DNS unless a separate rule allows the cluster DNS path. The DNS Service's labels and namespace can vary by distribution; inspect the actual DNS Pods and policy support before writing a rule. NetworkPolicy is not a replacement for cloud firewalls, node security groups, external firewalls, service authentication or application authorization. It controls Pod traffic at the layer supported by the network implementation; host traffic and some special paths have distinct behavior. See the official [NetworkPolicy reference](https://kubernetes.io/docs/concepts/services-networking/network-policies/).

For DispatchDesk, imagine the API Pods need inbound HTTP from the edge gateway and outbound database connections plus cluster DNS. A default-deny rule without corresponding allow rules can make the API appear unhealthy in several different ways: readiness may fail because it cannot reach its database; name lookups may time out because DNS egress is denied; or client traffic may never reach the backend. Define required flows from observed application behavior, not from a broad `allow-all` exception. Validate the path from both ends and keep a documented owner for each policy and its required peers.

NetworkPolicy selectors are namespace-scoped for the selected Pods. A namespace selector and a Pod selector in the same peer object are combined with AND: the peer must be a Pod matching the labels in a namespace that also matches. Separate peer list entries act as alternatives. `ipBlock` rules describe CIDRs and exceptions, but Pod IPs can change; use stable labels for in-cluster workload identities where possible. Policy order is not a priority mechanism: allowed flows from any applicable policy are combined. Do not rely on two policies where one is intended to override another.

Test representative traffic after policy changes. Check DNS lookup, TCP connection, TLS handshake and application response as distinct stages. A `curl` failure can mean name resolution, routing, policy, listener, TLS or HTTP behavior; record which stage completed. Test both ingress and egress, same-node and cross-node placement, IPv4 and IPv6 if enabled, and paths through Services as well as direct Pod IPs when the application uses both. A temporary client Pod is a cluster mutation and may require approval; use an approved diagnostic image and clean it up after recording evidence.

## Diagnosing cross-node packet paths

DispatchDesk has two ready API replicas and an internal Service. One client Pod can reach an API Pod on the same node but times out when the selected backend is on another node. The initial assumption is that the application process is broken, so the team restarts it. That does not change the node-to-node path. Because behavior varies with placement, compare the Pod IPs and node names, test the same port from clients on each side, and inspect the network implementation and infrastructure path between those nodes.

From an authorized administrative workstation with the intended kubeconfig, start with read-only API evidence:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  get pods -l app.kubernetes.io/name=dispatchdesk -o wide
kubectl --context kind-dispatchdesk \
  get nodes -o wide
kubectl --context kind-dispatchdesk --namespace production \
  get networkpolicies
kubectl --context kind-dispatchdesk --namespace production \
  get endpointslices -l kubernetes.io/service-name=dispatchdesk-api -o yaml
kubectl --context kind-dispatchdesk --namespace kube-system \
  get pods -o wide
```

These reads relate Pod IPs to nodes, show namespace policy objects, list Service endpoints and locate system Pods. The kube-system label and component names vary by CNI and cluster distribution; identify the installed plugin from cluster documentation or node configuration rather than assuming a DaemonSet name. EndpointSlice membership does not prove packet delivery. NetworkPolicy objects do not prove enforcement or a specific flow decision. Do not share full output if it contains internal addresses or sensitive annotations.

Follow the path in layers. First verify the source and destination Pod are Ready, are listening on the expected port, and belong to the expected namespaces and network-policy selectors. Then check whether the client resolves the Service name to the expected address and whether the Service has ready endpoints. If a direct Pod-IP test works but Service access fails, investigate Service port/targetPort, endpoint conditions and the service proxy implementation. If same-node direct Pod traffic works but cross-node direct Pod traffic fails, inspect the CNI's node agents, Pod CIDR allocation, node routes, encapsulation protocol, firewall/security-group rules and MTU. The exact ports and protocols depend on the selected CNI; use that vendor's documentation and the infrastructure team's approved rule inventory, not a generic port list.

Use packet captures or CNI observability only under the platform's access procedure. A capture on the source Pod interface, host veth, node tunnel and destination interface can show where packets stop, but requires node privileges and may contain customer data. Record timestamps, 5-tuples and relevant node/Pod identities; mask payloads. Check CNI agent logs and node conditions alongside the packet path. If a policy denies traffic, confirm which policy selected the Pod and which allowed peer/port is missing. If the route or firewall blocks the path, identify the exact node pair, protocol and direction before changing rules.

Recovery depends on the failed layer. For a policy error, apply a reviewed least-privilege rule and verify DNS plus application traffic from the intended client. For a node route, address allocation or firewall issue, coordinate the CNI and infrastructure owners and stage the change on a canary node pair; a rule that enables one path can expose every Pod on a subnet if scoped too broadly. For MTU mismatch, use the implementation's documented value and verify large packets and TLS traffic after the change. Confirm that both same-node and cross-node paths work, then check Service requests and user-facing errors. Avoid repeatedly restarting Pods when placement-specific evidence points to the node network.

Network failures can be asymmetric. Ingress may reach the Pod while the response route is missing; egress may reach a dependency from one zone only; policy may allow requests but not a required callback. Exercise both request and response paths and compare source identity as observed by the destination. NAT, external traffic policy, node SNAT and service-mesh sidecars can alter the source address or connection path. Document the actual path for every supported traffic direction.

## Exercises and answer guidance

1. Two Pods on one node communicate, but direct Pod-IP traffic fails across nodes. What should be investigated before restarting the application? CNI node agents, route/encapsulation path, firewall protocols, CIDR allocation, MTU and node conditions; first confirm application listeners and policy selectors.
2. NetworkPolicy objects exist, but a supposedly denied connection still succeeds. What does that suggest? The installed network implementation may not enforce NetworkPolicy, the Pod may not be selected, another policy may allow the flow, or the tested path may bypass expected enforcement.
3. A default-deny egress policy causes API health checks and DNS lookups to fail. Why can both symptoms appear? The policy may block database egress and DNS egress; allow required peers and DNS explicitly, then test each path separately.
4. A Service resolves to a ClusterIP and an EndpointSlice lists a ready Pod, but the client cannot connect. What has been established, and what remains? Discovery and control-plane endpoint membership are established; packet path, policy enforcement, target port, listener and application behavior remain to test.
5. A cross-node overlay has intermittent TLS stalls while small probes work. What additional hypothesis should be checked? MTU or path-MTU behavior, alongside loss and retransmission; validate with the CNI's documented settings and a controlled large-packet/application test.

Review questions: which component provides the Pod network, how does Service routing differ from Pod routing, how do ingress and egress policies combine, and what placement-dependent evidence narrows a cross-node failure?

## Verification and primary sources

Official Kubernetes cluster networking, network plugin, NetworkPolicy and Service documentation was inspected on 2026-10-04. Commands are read-only and target the disposable `kind-dispatchdesk` context; no packet capture, policy, CNI configuration, node route or cluster resource was changed. No Pod traffic was tested. Static checks do not prove CNI enforcement, routes, firewall rules, MTU, address capacity, dual-stack operation, service-proxy behavior or application reachability.

Primary references: [Cluster Networking](https://kubernetes.io/docs/concepts/cluster-administration/networking/), [Network Plugins](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/), [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/), [Services](https://kubernetes.io/docs/concepts/services-networking/service/), and [Virtual IPs and Service Proxies](https://kubernetes.io/docs/reference/networking/virtual-ips/).
