---
book: The Complete DevOps Engineering Book
volume: 3
volume_title: "Networking and Traffic"
chapter: 29
title: "Load Balancers and Traffic Distribution"
slug: load-balancers-and-traffic-distribution
status: draft
summary: ../../_ai/chapter-summaries/029-load-balancers-and-traffic-distribution.md
---

# Chapter 29 — Load Balancers and Traffic Distribution

## Why this matters

Harbor adds a second DispatchDesk API instance to handle peak traffic. Both processes pass local health checks, but one receives nearly all requests while the other stays idle. A load balancer can distribute new connections or application requests, yet its behavior depends on protocol, algorithm, persistence settings, health checks and connection lifetime. Adding a second server does not by itself create usable capacity or availability.

This chapter compares layer four and layer seven balancing, health policy, connection draining and algorithms. It builds on proxies and translation in [Chapter 28](028-nat-proxies-and-connection-tracking.md), and on HTTP behavior in [Chapter 24](024-http-and-api-traffic.md). The examples use fictional addresses and are not an instruction to expose a listener publicly.

## Layer four and layer seven routing

A layer-four load balancer makes decisions using transport metadata such as protocol, address and port. It can distribute TCP connections without interpreting HTTP paths or responses. One client connection generally maps to a backend connection or stream for its lifetime. A long-lived connection can therefore keep traffic on one server even while new connections are balanced evenly. TCP balancing fits protocols the balancer does not need to understand, including database protocols, when the service's own semantics permit it.

A layer-seven HTTP balancer parses HTTP and can route by host, path, header or other request properties. It may terminate TLS, authenticate or filter requests, enforce body limits, and reuse upstream connections. It can make per-request decisions on a persistent client connection, depending on protocol and configuration. That capability adds application-specific policy and parsing work; it also creates another service endpoint whose certificates, timeouts and logs must be operated.

A direct server return design can let a layer-four director choose a backend while response packets bypass it. This can reduce load on the director, but it requires deliberate address advertisement and routing symmetry. It complicates source identity and troubleshooting. Treat it as a distinct network design, not a toggle that preserves every proxy property.

Cloud load balancers add managed health checks, listeners, target groups and service-specific behaviors. Their source addresses, proxy-protocol support, idle timeouts, health thresholds and cross-zone rules vary. Check current provider documentation and costs before adopting exact settings. The service still needs healthy backends, safe migrations and an incident path that understands the managed boundary.

## Health checks and connection draining

A health check asks whether a backend should receive new work. A TCP connect check proves that a transport endpoint accepted a connection. An HTTP readiness check can test that the application is ready to accept a request, but only the dependencies appropriate to that readiness contract. Keep process liveness separate from readiness: restarting a healthy process because the database is temporarily unavailable can multiply an outage.

A check that depends on every downstream system can eject all backends when a shared dependency fails. Removing unhealthy instances may protect the remaining service, but it cannot restore a database that all instances share. Decide which requests the instance can safely serve and which dependency failures should stop new work. Include hysteresis: consecutive-failure and recovery thresholds reduce flapping, while check intervals and timeouts determine how quickly the balancer reacts. Aggressive probing can itself add load during an outage.

During deployment or host maintenance, draining stops assigning new work to a backend while allowing existing connections or requests to finish where supported. The drain deadline must fit application shutdown behavior, client keep-alives, streaming requests, queue consumers and database transactions. A balancer's “drain complete” signal does not guarantee that an asynchronous job has committed or that an order can never be retried. Reconcile application state before terminating a backend with uncertain work.

Session affinity sends a client repeatedly to one backend using a cookie or source-based mapping. It can hide missing shared state and make load uneven. Before enabling stickiness, define what state requires it and whether it can instead be stored in a shared durable service. Affinity can also be disrupted by NAT, address changes, backend removal or expiration.

## Choose an algorithm for the workload

Round robin works well when backends have similar capacity and requests have similar duration; each new assignment rotates through eligible servers. Weighted round robin gives a larger share to servers with more configured capacity, but weights need measurement and maintenance. Least connections can help when connections are long-lived and connection count approximates work; it can mislead when a small number of connections create disproportionate CPU or database load. Source hashing can preserve locality but makes uneven source populations and backend changes visible as skew. Power-of-two choices and random methods are implementation-specific options whose exact behavior should be verified in the chosen balancer.

An algorithm distributes a unit defined by the product. Layer-four balancing distributes connections. Layer-seven balancing may distribute requests while reusing upstream connections. Neither equal request counts nor equal connection counts guarantee equal CPU, latency, memory or database work. Observe backend request rate, queue depth, duration, errors and resource consumption alongside the policy.

Before adding capacity, check whether the bottleneck is in the application, database pool, network path or balancer itself. A balancing change that overloads a shared database can reduce overall success. Limit per-backend concurrency and set queue behavior so overload is visible rather than hidden behind requests that wait indefinitely.

## A DispatchDesk balancing configuration

This illustrative HAProxy configuration accepts HTTP on port 8080 and checks a readiness path on two fictional API backends. Save it only as a reviewed configuration artifact; do not start it on a production host without providing the intended listener, network rules, logging, timeouts, TLS policy and tested backend addresses. HAProxy directives change across releases, so validate with the exact installed version before deployment.

```haproxy
global
    maxconn 2048

defaults
    mode http
    timeout connect 2s
    timeout client 15s
    timeout server 15s

frontend dispatchdesk_api
    bind 127.0.0.1:8080
    default_backend dispatchdesk_nodes

backend dispatchdesk_nodes
    balance roundrobin
    option httpchk
    http-check send meth GET uri /readyz ver HTTP/1.1 hdr Host dispatchdesk.internal
    http-check expect status 200
    server api_a 10.42.8.21:8080 check inter 2s fall 3 rise 2
    server api_b 10.42.8.22:8080 check inter 2s fall 3 rise 2
```

The listener is bound to loopback so this fragment cannot expose a public service by itself. The fictional backends use the project's port 8080 convention. Health succeeds only for an HTTP 200 from `/readyz`, with three consecutive failures to mark a server down and two successes to restore it. A real readiness endpoint should have an explicit dependency policy and the check's `Host` value must match the application's routing. The request and response timeouts bound different legs; choose them using observed latency distributions and the client deadline.

HAProxy documentation describes the available balancing algorithms and health-check behavior; defaults vary by version, so set the intended policy explicitly. [HAProxy 3.2 configuration manual](https://docs.haproxy.org/3.2/configuration.html), [backend algorithms](https://www.haproxy.com/documentation/haproxy-configuration-tutorials/proxying-essentials/configuration-basics/backends/) and [health checks](https://www.haproxy.com/documentation/haproxy-configuration-tutorials/reliability/health-checks/).

## Diagnose uneven traffic and restore service

The second Harbor backend remains idle. First confirm the balancer's target membership and current health status. Verify that each target is reachable from the balancer and that its readiness response, path, host header and expected status match the check. Look at backend request counts, connection duration, affinity cookies, hashing keys and current connection reuse. Compare observations over a window long enough to account for keep-alive connections; an instantaneous count can mislead.

Suppose one backend has an old readiness route that returns 404 while its `/healthz` returns 200. The process is alive but fails the balancer's readiness contract, so it is correctly excluded. Align the readiness route and health policy, deploy to one backend first, and check it becomes healthy before changing the rest. If all targets fail because readiness includes a shared database that is down, contain writes and restore the shared dependency rather than repeatedly restarting every API process.

If one backend is overloaded despite even request counts, compare request costs, tail latency, in-flight work and database-pool waits. Apply a controlled weight or concurrency limit only after finding what differs. Drain one backend to test behavior before maintenance, and verify that active requests complete or have a safe retry path before shutdown.

## Exercises, review questions and takeaways

1. Compare a layer-four TCP check with an HTTP readiness check. Guidance: name the endpoint and evidence each one proves, and what it leaves untested.
2. Choose an algorithm for short API calls, long-lived database sessions and skewed request costs. Guidance: first define whether assignments are connections or requests and which measured resource best approximates work.
3. Design a backend drain deadline. Guidance: account for request, keep-alive, streaming, application shutdown and uncertainty about committed writes.
4. Diagnose one idle backend. Guidance: inspect check response, persistence, hashing, long-lived connections and observed request windows.

Review questions: What does a `200` health check prove? Why can equal connection counts overload one backend? What happens to a request during a drain? Good answers refer to the check contract, assignment unit and application work lifecycle.

Balance the work unit the balancer actually understands, then measure the work the application must finish. Continue to [Chapter 30](030-network-troubleshooting-in-layers.md) for a disciplined path investigation across these components.
