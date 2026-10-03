---
book: The Complete DevOps Engineering Book
volume: 3
volume_title: "Networking and Traffic"
chapter: 28
title: "NAT, Proxies and Connection Tracking"
slug: nat-proxies-and-connection-tracking
status: complete
summary: ../../_ai/chapter-summaries/028-nat-proxies-and-connection-tracking.md
---

# Chapter 28 — NAT, Proxies and Connection Tracking

## Why this matters

A Harbor worker can connect to the Internet from its private network even though it has no public address. A translation gateway changes the packet's source address and remembers the flow so replies can return. During a provider outage, many short-lived connections fail and new ones cannot obtain a translation entry or source port. Looking only at the application's private IP hides the shared egress boundary.

This chapter distinguishes packet translation from application proxies and follows the state that supports a connection. It builds on [Chapter 27](027-firewalls-and-network-policy.md) and [Chapter 22](022-tcp-udp-and-connections.md). Diagnostic commands are observational; do not clear connection-tracking state or change NAT rules to see whether an incident disappears.

## Translation and return paths

Network address translation (NAT) rewrites packet addresses and, for port translation, transport ports. Source NAT changes the source as traffic leaves a network, often so private hosts share a routable egress address. Destination NAT changes the destination, often to publish an internal service behind a public address. Masquerading is a source-NAT mode that chooses an address from an outgoing interface. The routing, translation rule and firewall policy must agree in both directions. [nftables NAT documentation](https://wiki.nftables.org/wiki-nftables/index.php/Performing_Network_Address_Translation_(NAT)).

A stateful NAT gateway records the original and translated flow tuples. When a reply arrives, connection state lets the gateway reverse the relevant translation. This is why an outbound packet can return through the same gateway even though the remote peer never saw the private source address. A route that sends the reply through a different node can break the mapping or be rejected by stateful policy. Active-active gateways need a design for sharing, synchronizing or deliberately partitioning flow state.

NAT does not encrypt traffic or authenticate a peer. It is not an access-control policy: publishing a port with destination translation still requires an explicit firewall decision and a protected service. A private address does not guarantee isolation from other private networks. Use routing and policy to define reachability, and TLS or another authenticated protocol for confidentiality and identity.

Address translation also complicates attribution. An application log may contain a container or private address while an external service records the gateway's public address. Preserve request identifiers and the translation boundary when correlating evidence. Port translation can allow many internal flows to share one address, but available source ports and tracking resources are finite.

## Forward and reverse proxies

A forward proxy receives requests from clients and makes outbound requests on their behalf. It can enforce egress policy, cache content, inspect traffic or provide an audit point. Clients must be configured to use it, and DNS can occur on either the client or proxy depending on proxy protocol and implementation. A policy that allows the client to reach the proxy does not necessarily allow the proxy to reach the destination.

A reverse proxy sits in front of servers and accepts client traffic on their behalf. It can terminate TLS, route by host or path, enforce limits and balance requests across backends. The client has a connection to the proxy, and the proxy has a separate upstream connection. A healthy client-facing socket therefore says nothing conclusive about backend connectivity. See [Chapter 29](029-load-balancers-and-traffic-distribution.md) for traffic distribution and health checks.

An HTTP proxy understands application messages; a NAT gateway rewrites packet headers without interpreting an HTTP request. A transparent proxy may intercept traffic without explicit client configuration, but the underlying routing and policy remain part of its operation. Some systems combine proxying and NAT, so identify which component terminated or transformed each connection before explaining an observed address.

Forwarded client-address headers can preserve identity through a reverse proxy, but they are trustworthy only when inserted or sanitized by a known proxy. An arbitrary client can send the same header. Restrict direct backend access and configure an explicit trusted-proxy list before an application relies on forwarded address data. [Forwarded header standard](https://www.rfc-editor.org/rfc/rfc7239.html).

## Conntrack and ephemeral ports

Linux connection tracking (conntrack) associates packets with stateful flows. Netfilter can use this state for firewall decisions and NAT mapping. Inspect the aggregate counters with tools available on the host:

```bash
sudo conntrack -S
cat /proc/sys/net/netfilter/nf_conntrack_count
cat /proc/sys/net/netfilter/nf_conntrack_max
```

`conntrack -S` reports per-CPU statistics, including insert failures and early drops on supported versions. The proc files report the current number of tracked entries and configured maximum when that kernel module and proc interface are present. Missing files do not prove there is no stateful gateway; the host may not load the feature or may be observed from a container namespace. The `conntrack` utility comes from `conntrack-tools` where available; Ubuntu, Fedora and RHEL package availability and privileges vary. Read the installed tool's manual before interpreting fields. [conntrack-tools manual](https://conntrack-tools.netfilter.org/manual.html).

A counter near its limit is a warning signal, not a full diagnosis. Compare the count's rate and duration, connection lifetimes, insert-failure counters, traffic volume and application errors. Long-lived legitimate flows can consume state; abandoned UDP flows and aggressive retry loops can also accumulate entries. Increasing the maximum can consume more kernel memory and postpone the same leak or burst.

Outbound clients select ephemeral source ports for TCP and UDP flows. Inspect the configured range and current socket state:

```bash
cat /proc/sys/net/ipv4/ip_local_port_range
ss -tan state time-wait
ss -s
```

A client behind a shared NAT may compete for translated port mappings under the gateway's allocation rules, even if the client itself has unused local ports. Repeated short-lived connections to one destination can create pressure and TIME-WAIT state. Connection pooling can reduce churn when the application can safely reuse sessions. Tune retries, pool sizes, idle timeouts and destination concurrency from measurements instead of copying a global range change.

A proxy can shift the bottleneck: many clients may share one proxy's upstream address and port space. Scale or partitioning decisions should consider concurrent flow counts, backend connection reuse, NAT allocation and provider limits. Network address count alone does not predict sustainable request throughput.

## Diagnose exhaustion and restore service

Summit workers suddenly report connection timeouts to a provider. Their local route remains correct. Compare connection failures by destination, source host and time; inspect socket states and connection-creation rates; examine the host's conntrack counters if it performs tracking; and check the provider NAT gateway's own flow or port-allocation metrics. Distinguish a local ephemeral-port shortage, kernel conntrack pressure, gateway translation exhaustion, provider rate limit and remote refusal. Each happens at a different boundary.

Contain retry amplification first. Reduce or pause nonessential new work while preserving queued notification intent. Compare one controlled connection from a low-volume host with a busy worker, and record the source address seen by the provider if available. Inspect whether long-lived or leaked connections consume capacity, whether idle sessions expire at one layer but remain pooled at another, and whether an upstream proxy or NAT gateway is shared across unrelated services.

Restore service by correcting the responsible limit or leak with a measured change. If an application fails to close responses, fix its resource lifecycle and verify repeated failures no longer accumulate sockets. If a NAT gateway's allocation is exhausted by legitimate concurrency, reduce churn through pooling or add capacity using the provider's supported design. If conntrack insert failures are confirmed, document the memory consequence before changing its maximum and verify the rate falls. Clearing all conntrack entries can terminate active sessions and break NAT mappings; it is not routine cleanup.

After recovery, confirm new connections progress, existing work drains, and queued notifications reconcile without duplicate effects. Compare the same counters through the next normal traffic peak. A quiet graph immediately after suppressing all traffic is not proof that capacity is adequate.

## Exercises, review questions and takeaways

1. Draw a worker-to-provider flow through source NAT. Guidance: label the original tuple, translated tuple, tracking state and return route.
2. Explain why a reverse proxy can answer while its application backend is unreachable. Guidance: separate the client-to-proxy connection from the proxy-to-backend connection.
3. A conntrack count approaches its maximum while insert failures remain zero. What additional evidence is needed? Guidance: inspect trends, rates, entry lifetimes, errors and workload; one snapshot is not causal evidence.
4. Compare adding another public egress address with reducing connection churn. Guidance: test whether port allocation or application connection lifecycle is the limiting factor and include policy/attribution consequences.

Review questions: What does NAT fail to provide as a security property? Which side resolves a hostname when using a forward proxy? Why can an app's local port range differ from a shared NAT's remaining mappings? Good answers follow both address transformations and ownership boundaries.

Trace translation and proxy boundaries separately, then correlate their state with application connection behavior. Change capacity only after locating the exhausted resource. Continue to [Chapter 29](029-load-balancers-and-traffic-distribution.md) to distribute requests while observing each backend path.
