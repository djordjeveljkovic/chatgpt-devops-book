---
book: The Complete DevOps Engineering Book
volume: 3
volume_title: "Networking and Traffic"
chapter: 30
title: "Network Troubleshooting in Layers"
slug: network-troubleshooting-in-layers
status: draft
summary: ../../_ai/chapter-summaries/030-network-troubleshooting-in-layers.md
---

# Chapter 30 — Network Troubleshooting in Layers

## Why this matters

DispatchDesk users report slow order submissions, and one dashboard shows packet loss. Harbor's team sees a route to the API and a healthy backend. Several people prepare unrelated changes: restart the load balancer, flush DNS and open a firewall port. None has yet established which request failed or which path it took.

Troubleshooting works best when each observation answers a specific question and preserves the boundary it measured. This chapter assembles the preceding networking tools into an investigation that starts with the user-visible symptom and follows one request through local configuration, routing, DNS, transport, TLS, HTTP, proxies and backend behavior. It is a method for reducing uncertainty, not a checklist that every incident must execute in full.

## Collect local, route, name and application evidence

Start with a concrete report: affected user, operation, time interval, source network, destination name, response or error, request identifier and whether retries succeeded. Compare one failing operation with a known-good one from the same client path. Avoid collecting a broad packet trace before the question and capture point are clear.

Establish the local context on the host or container that made the request. Record the execution identity, network namespace, configured proxy, resolver path and destination port. A host's working DNS or route does not prove a container uses the same configuration. Capture the relevant read-only state before changing it:

```bash
ip -brief address show
ip rule show
ip route get 10.42.8.21
getent ahosts api.example.com
ss -tan state established
```

The destination IP is a fictional value in this example; replace it only after resolving an approved service name through the affected client's normal resolver path. `ip route get` answers how the local kernel would route that address. `getent` follows the system name-service path. `ss` snapshots TCP sockets in the current host/network namespace, subject to permission. None makes an HTTP request.

Record DNS answers and TTLs from the same resolver path as the process. Compare A and AAAA results, proxy settings and the actual remote endpoint selected by the client. The name in a URL, the address selected, the route source address and the server certificate hostname are related but distinct. A direct test to an IP can isolate one layer only when it preserves the intended HTTP host and TLS SNI as described in Chapters 24 and 25.

Use a bounded application probe whose method is safe and whose effect is known. Capture status, connection and total duration separately. Correlate a request ID through load-balancer access logs, application logs, database waits and notification state. A process restart changes several observations at once and can erase evidence, so prefer one hypothesis-driven change after recording the initial state.

## Use tcpdump, tracepath and mtr carefully

`tracepath` can discover hop behavior and path-MTU clues without superuser privileges on common Linux installations. It sends network probes that some networks suppress or deprioritize. Use it against an authorized destination and keep the hop limit bounded:

```bash
tracepath -n -m 8 api.example.com
```

`-n` avoids reverse-name lookups that add delay and separate DNS noise; `-m 8` bounds the maximum hops in this example. A missing response at an intermediate hop does not prove the router drops forwarded application traffic. ICMP responses can be filtered or rate-limited even while packets continue toward the destination. `tracepath` behavior and privileges depend on platform/kernel configuration. [tracepath manual](https://man7.org/linux/man-pages/man8/tracepath.8.html).

`mtr` combines repeated path probes and can show change over time. One bounded report is:

```bash
mtr --report --no-dns --report-cycles 5 api.example.com
```

`--report` prints and exits, `--no-dns` avoids reverse-name lookups, and `--report-cycles 5` limits this run to five probe cycles. MTR can use different probe methods depending on permissions, flags and build. Its results are probe metrics with method and observation limits, not necessarily the application's exact TCP or HTTP path; see the [IP performance measurement framework](https://www.rfc-editor.org/rfc/rfc2330.html). Ask the network owner before running sustained probes against sensitive infrastructure. [MTR upstream manual](https://github.com/traviscross/mtr/blob/master/man/mtr.8.in).

A short packet capture at the correct interface can prove whether a specific packet reached that observation point or a reply left it. On an authorized Linux host, this command bounds capture duration and number of matching packets:

```bash
sudo timeout 15s tcpdump -i any -nn -c 20 'host 10.42.8.21 and tcp port 8080'
```

Replace the fictional target and port with the expected peer. `-i any` observes eligible interfaces in the current network namespace; capture-link details differ from selecting a physical device. `-nn` leaves addresses and ports numeric, `-c 20` stops after twenty matching packets, and `timeout` bounds a quiet capture. Packet capture may require privilege and can expose payload data. The filter narrows volume but does not guarantee a safe data classification. Avoid writing a capture file unless needed, protect it, and remove it under the approved retention process.

Use packet evidence to ask whether the request, handshake, retransmission or response crossed a particular boundary. A trace at the client cannot show what happened behind a cloud load balancer. Capture the same flow on both sides of a suspected boundary if the responsible owner permits it. Account for NAT, proxy termination, offloading and asymmetric paths before comparing addresses and checksums.

## Separate packet loss from application latency

End-to-end latency contains name resolution, connection setup, TLS negotiation, request transfer, queueing, server execution and response transfer. A high HTTP total with a normal TCP connect time points toward a later phase, but timer definitions and connection reuse matter. For reused HTTP connections, a new DNS lookup or handshake may not occur at all. Compare per-request timing fields and server-side spans rather than treating one number as the whole path.

Packet loss inferred from ping or MTR is not automatically application packet loss. Routers often process their own probe responses differently from transit packets. Consider the final destination result and compare measurements from both ends. If one intermediate hop reports loss but all later hops and the endpoint do not, that hop may simply rate-limit replies. If loss begins at one point and persists through the destination under matching probe conditions, a path issue becomes more plausible, but still needs confirmation on the service flow.

Application latency can rise without packet loss when a worker queue grows, a database pool is saturated, a shared dependency slows, CPU is throttled or the load balancer repeatedly selects a slow target. Conversely, retransmission can increase tail latency while average request counts appear stable. Compare percentiles, errors, saturation, queue depth and target-specific behavior over the same time window.

A packet capture itself can drop packets under high load. Record tcpdump's captured and kernel-dropped counts when it exits. A quiet filtered capture may mean the packet never arrived, the filter or interface was wrong, or packets were lost before userspace. Validate the filter with a controlled flow where possible before drawing a negative conclusion.

## A layered DispatchDesk investigation

During a deploy, 5% of Harbor's order requests take ten seconds and return `504`. The balancer reports both API nodes healthy; service CPU is normal. The team chooses one affected client request ID and establishes its timestamp, client region and URL. The client trace shows DNS completed, TCP and TLS connected quickly, and the HTTP response came from the reverse proxy after the upstream timeout.

The balancer logs show that the affected request went to `api_b`. Both readiness checks return `200`, so basic readiness does not reveal the defect. Application traces show the request waits on a database pool before issuing a query. `api_a` has free pool capacity; `api_b` has an elevated active-connection count after the deploy. The deployment changed a pool setting on only one node. Packet-loss probes do not correlate with the failures, and a short permitted capture confirms the proxy's upstream TCP connection was established. This points to application-side pool saturation rather than a missing route.

The responders pause further rollout, reduce incoming work through the established backpressure control, and restore the last known-good pool setting on the affected node. They drain that node, allow in-flight orders to finish under a deadline, then re-enable it after request latency and pool wait return to the expected range. They reconcile orders whose client received a timeout because the server may have committed them before the proxy response expired. They do not ask clients to replay each request blindly.

This is an illustrative incident, not measured system output. Its value is the sequence of discriminating observations: client timing identified a proxy response, a request ID connected it to one backend, the database pool wait located the stall, and a staged rollback restored capacity. Each observation reduced the set of plausible causes before a change was made.

## Close the incident with verified recovery

Recovery requires more than a green health probe. Repeat the original safe request from the affected client path, compare status and latency, and confirm the specific backend and dependency have recovered. Reconcile any request whose outcome was ambiguous. Observe the service long enough to include the traffic level that exposed the fault.

Record the hypothesis, observations, changes and limits of the evidence. If a route, firewall or DNS record changed, verify its persistent owner and rollback state. If a load-balancer setting changed, inspect runtime and saved configuration. If the capture or probe lacked visibility into a provider boundary, state that limitation instead of claiming the entire path was proved.

Turn the incident into an actionable improvement: a targeted alert for pool wait, a staged configuration validation, a dashboard linking request IDs to backend names, or a runbook that names the correct owner. Avoid a generic action such as “improve monitoring” that provides no trigger or observable completion. A successful diagnosis should make the next similar failure faster to distinguish.

## Exercises, review questions and takeaways

1. A middle MTR hop shows 30% loss, while the final destination shows no loss. What does this prove? Guidance: it shows probe responses differed at that hop; it does not establish transit loss to the endpoint.
2. A user request has a fast TCP connect but slow total response. Which evidence helps locate the time? Guidance: compare TLS, proxy, application and dependency spans, accounting for reused connections.
3. Design a safe packet capture. Guidance: specify owner approval, observation point, interface, endpoint, port, packet/time limits, sensitive-data handling and cleanup.
4. A `504` follows a server-side order commit. How should the client retry? Guidance: reconcile operation state and use the service's durable idempotency contract before repeating a side effect.

Review questions: Which command follows the system name-service path? Why can an intermediate hop suppress probes but forward application packets? Which measurements identify proxy time versus database-pool wait? Answer with the observation source and its limits.

Follow one request through the actual client path, distinguish each protocol boundary, and change only the layer supported by the evidence. Continue to [Volume 4](../04-vps-and-server-operations/README.md) to apply these methods to server operations.
