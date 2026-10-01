---
book: The Complete DevOps Engineering Book
volume: 22
volume_title: "Operational Reference"
chapter: 212
title: "Networking and VPS Diagnostic Reference"
slug: networking-and-vps-diagnostic-reference
status: complete
summary: ../../_ai/chapter-summaries/212-networking-and-vps-diagnostic-reference.md
---

# Chapter 212 — Networking and VPS Diagnostic Reference

Use this reference to choose the next observation in a network or VPS incident. The packet and protocol mechanisms belong to [Volume 3](../03-networking-and-traffic/README.md); host provisioning, proxying and recovery belong to [Volume 4](../04-vps-and-server-operations/README.md). Work from the affected user's path toward the service. A successful connection from the server to itself does not reproduce a remote customer's route.

Before testing, write down the client location, destination name, address family, port, time window and reported symptom. Use an authorized diagnostic host and replace illustrative names with the intended endpoint. Run a small number of bounded requests; diagnosis does not require an accidental load test. Examples assume Linux with iproute2, curl and OpenSSL. `dig` comes from the distribution's DNS utility package; Ubuntu commonly uses `dnsutils`, while Fedora/RHEL use `bind-utils`. Verify the package on the selected release.

## Name resolution and address selection

```bash
book_host='orders.example.invalid'
getent ahosts "$book_host"
dig "$book_host" A +noall +answer +comments
dig "$book_host" AAAA +noall +answer +comments
```

The `.invalid` name deliberately does not identify a real service; replace it before a practical test. `getent ahosts` follows the host's configured name-service mechanisms, which can include local hosts files as well as DNS. `dig` queries DNS and is useful for separating that path from application/system resolution. `A` requests IPv4 records and `AAAA` requests IPv6 records. `+noall` clears ordinary output sections; `+answer` restores answers and `+comments` restores information such as the response status. An empty answer is not automatically NXDOMAIN: inspect the status and authority context when needed.

Compare the resolver used by the failing application with the resolver used by your test. An authoritative server can contain the new record while a recursive resolver still has a valid cached old answer. A negative answer can also be cached. Querying one public resolver is useful evidence about that resolver, not proof of what every user receives. Follow [DNS from Resolver to Authority](../03-networking-and-traffic/023-dns-from-resolver-to-authority.md) for cache and delegation diagnosis. ISC's [BIND resources](https://www.isc.org/bind/) lead to the utility reference for the installed version.

If a service publishes both address families, test both deliberately. `curl -4` and `curl -6` restrict address-family selection. An IPv6 failure can be hidden by a client's successful IPv4 fallback, while another client waits longer or uses a different path. Record the selected address rather than treating the hostname as one immutable destination.

## Local interfaces, routes and listeners

| Command | Interpretation and boundary |
|---|---|
| `ip -brief address` | Show interfaces and assigned addresses compactly. This says nothing by itself about a remote route or firewall. |
| `ip route show` | Show the main routing table. Policy routing can involve additional rules and tables. |
| `ip rule show` | Inspect route-selection rules when source addresses, marks or multiple uplinks matter. |
| `ip route get DESTINATION_IP` | Ask the kernel how it would route to this address, including selected source/interface. It is a route calculation, not a successful packet exchange. |
| `ss -lnt` | Show listening TCP sockets numerically. `-l` selects listeners, `-n` avoids name resolution and `-t` selects TCP. |
| `sudo ss -lntp` | Add process information with `-p`; sufficient privileges may be needed to see another account's ownership. |
| `ss -tan` | Show TCP sockets across states using `-a`, numerically using `-n`. Large connection counts need state and workload interpretation. |

Use a verified numeric address in place of `DESTINATION_IP`; the table is command notation, not a ready-made probe of a particular server. [Packets, Addresses and Routing](../03-networking-and-traffic/021-packets-addresses-and-routing.md) explains route precedence and [TCP, UDP and Connections](../03-networking-and-traffic/022-tcp-udp-and-connections.md) explains socket states.

A process listening on `127.0.0.1:8080` is available only through loopback in that network namespace. Publishing a firewall rule cannot make it listen on an external address. Conversely, a listener on an external address does not prove that a cloud security group or intermediate policy admits traffic. Container network namespaces add another location: inspect the listener where the application actually runs and the host-side publication separately.

Do not equate every TIME_WAIT socket with a leak. It can be expected connection lifecycle behavior. Determine connection creation rate, destination patterns, port allocation and whether requests actually fail. A high established count can be legitimate long-lived traffic or stuck work; its interpretation depends on the workload and timeout contract.

## HTTP evidence with curl

After replacing the host name, this bounded GET checks the selected readiness endpoint:

```bash
curl --silent --show-error --fail-with-body \
  --connect-timeout 3 --max-time 10 \
  "https://$book_host/readyz"
```

`--silent` suppresses the progress meter and `--show-error` preserves transfer errors. `--fail-with-body` returns an error for HTTP failures while retaining a useful response body; verify the installed curl supports it. `--connect-timeout` bounds connection establishment and `--max-time` bounds the complete transfer. An HTTP error response is different evidence from DNS failure or a TLS-verification failure. A readiness response is still not a complete order-acceptance and notification test.

For timing without dumping a large response:

```bash
curl --silent --show-error --output /dev/null \
  --connect-timeout 3 --max-time 10 \
  --write-out 'code=%{response_code} dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} first_byte=%{time_starttransfer} total=%{time_total}\n' \
  "https://$book_host/readyz"
```

The write-out fields are cumulative timestamps within this transfer, not independent additive stage durations. For a simple fresh HTTPS connection, differences can help localize name lookup, connection and TLS work; reused connections, redirects and protocol behavior require care. `time_starttransfer` includes upstream and application work before the first response byte. This command intentionally does not add `--fail`, so the status is visible even when HTTP reports an error; automation must check both the transport exit and response code according to its purpose. The [curl manual](https://curl.se/docs/manpage.html) defines the fields and flags.

Use `--verbose` for a controlled investigation when headers and handshake details are needed. Its output can contain authorization or cookie data, so save only the relevant sanitized evidence in a shared incident record. `--head` asks for HEAD; it does not prove the same behavior as a GET or an authenticated order POST. Avoid using arbitrary request methods merely to silence an inconvenient symptom.

To test one selected backend address while retaining the hostname for HTTPS routing and certificate checks:

```bash
book_ip='192.0.2.10'
curl --silent --show-error --fail-with-body \
  --resolve "$book_host:443:$book_ip" \
  --connect-timeout 3 --max-time 10 "https://$book_host/readyz"
```

The numeric address is documentation-only and must also be replaced. `--resolve` supplies a mapping for the specified host/port without editing global DNS. The URL still provides the HTTP name and TLS server name. This is useful when comparing an old and new backend during a DNS change. It can intentionally bypass a normal frontend, so describe that altered path before interpreting the result.

## TLS and certificate diagnosis

For the actual endpoint:

```bash
openssl s_client -connect "$book_host:443" -servername "$book_host" \
  -verify_hostname "$book_host" -verify_return_error -brief </dev/null
```

`-connect` chooses the TCP endpoint, `-servername` sends the intended TLS SNI name, and `-verify_hostname` checks the expected certificate identity. `-verify_return_error` makes certificate verification failure stop the test rather than letting an interactive diagnostic session proceed past it. `-brief` reduces output; input from `/dev/null` prevents an interactive application conversation. Trust still depends on the configured CA sources. The [OpenSSL s_client reference](https://docs.openssl.org/3.5/man1/openssl-s_client/) explains its diagnostic behavior.

If the service uses an internal CA, supply the approved CA material through the documented verification option instead of disabling verification. For a local certificate file, `openssl x509 -in ./server.crt -noout -dates -subject -issuer` inspects dates and identity metadata; it does not verify that the remote listener serves this file or that its private key matches. Compare the actual served chain and deployment configuration. See [TLS, Certificates and Trust](../03-networking-and-traffic/025-tls-certificates-and-trust.md).

An expired certificate, wrong server name, missing intermediate and unreachable TCP endpoint are different problems. `curl --insecure` hides a verification boundary and can make an unsafe endpoint appear healthy. A temporary diagnostic comparison, if justified, must remain clearly separate from the operational fix and should not become a deployed client option.

## Packet capture and path observations

A capture must be scoped to authorized traffic and handled as potentially sensitive evidence:

```bash
sudo tcpdump -ni any -c 50 'tcp port 443'
```

`-n` suppresses address/name resolution, `-i any` selects available interfaces through the platform's aggregate capture device, and `-c 50` bounds packets. The quoted filter reaches tcpdump intact. This can confirm SYNs, retransmissions and connection closure, but encrypted payload contents remain unavailable without a separate legitimate decoding context. Capture at the right namespace and interface; an application-container capture and a VPS-host capture can see different paths.

`tracepath DESTINATION_IP` can help reveal path and MTU behavior; `mtr` can sample hop responses over time when installed. Intermediate routers may limit diagnostic responses while forwarding application traffic normally. Loss reported at one hop that does not continue at later hops is not sufficient proof of customer packet loss. [Network Troubleshooting in Layers](../03-networking-and-traffic/030-network-troubleshooting-in-layers.md) explains these limits.

## A VPS decision route

| Symptom | Next useful evidence |
|---|---|
| Name does not resolve | System resolver result, DNS status, delegation and cache state |
| Connection refused | Correct destination, listener address/port and active reject policy |
| Connection times out | Route, filtering, return path, destination state and bounded capture |
| TLS fails | Served chain, expected name, validity period, trust store and handshake result |
| HTTP 502/504 | Proxy upstream selection, backend listener, timeouts and dependency latency |
| Requests fail under load | Queueing, connection pools, CPU/memory/I/O pressure and rate of new connections |
| Local check passes; remote check fails | Difference in name, address family, routing, frontend policy or client identity |

For a bad deployment, inspect `systemctl status` and the current-boot journal using [Chapter 211](211-linux-and-shell-command-reference.md). Verify disk/inode capacity before repeatedly restarting a service that cannot write state. A proxy reload does not repair an unavailable database, and opening more firewall rules does not fix an application bound to the wrong interface.

Review drill: new certificates were installed, local HTTP works, and remote HTTPS fails. Confirm the remote endpoint and certificate actually served; then compare the SNI name, verification result and proxy listener. Do not start with a host-wide firewall flush. After a targeted repair, repeat the original client path and an authorized application journey, recording the time and active release.

## Verification

Written on 2026-10-01. Installed curl and OpenSSL s_client help were inspected; their official manuals were consulted where available. iproute2, dig, tcpdump and tracepath executables are present, but no packet capture, external probe, TLS handshake, firewall or service change was executed for this reference. The reserved names/addresses are illustrative and intentionally require replacement. Shell syntax and local links are checked separately from live network outcomes.
