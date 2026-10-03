---
book: The Complete DevOps Engineering Book
volume: 7
volume_title: "Podman and the Rootless Host"
chapter: 64
title: "Podman Networking and Ports"
slug: podman-networking-and-ports
status: complete
summary: ../../_ai/chapter-summaries/064-podman-networking-and-ports.md
---

# Chapter 64 — Podman Networking and Ports

## Network backends and rootless forwarding

DispatchDesk's fictional VPS deployment uses a host reverse proxy to terminate TLS and forward to a loopback HTTP port. Its database should be reachable from the application, not from arbitrary internet clients. Those requirements create two different network paths: host-to-service publication and service-to-service communication. A successful image pull tests neither path.

Complete [identity and ownership](063-rootless-identity-and-volume-ownership.md) first. Use a disposable local Linux host, the same ordinary Podman account, registry access, `curl` and a free TCP port 8089. Commands below do not change host firewall rules. [Network troubleshooting](../03-networking-and-traffic/030-network-troubleshooting-in-layers.md) explains the underlying layer-by-layer method; this chapter applies it to Podman's boundaries.

Start by recording effective configuration:

```bash
podman --remote=false info
podman --remote=false network ls
```

Distinguish the network configuration backend from rootless packet forwarding. Netavark configures Podman networks; Aardvark supplies DNS for supported networks. Rootless standalone networking can use pasta, while older packages or configurations may use slirp4netns. A named rootless bridge has a different forwarding path from standalone pasta. Changing one setting does not prove every existing container has adopted it.

The stable manual inspected 2026-10-03 documents pasta as the current rootless default. Treat that as a documentation assumption, not a declaration about every Ubuntu or RHEL package. Upgrades, vendor backports and existing configuration can preserve other choices. Source-address visibility, IPv6, host reachability and forwarding performance deserve tests under the actual selected mode. If DispatchDesk uses client IP for rate limiting, verify the end-to-end proxy trust contract instead of accepting whichever address the container happens to see.

Rootless processes cannot simply administer the host's bridge and firewall as root. Helpers and namespace boundaries make the requested topology possible within their supported constraints. This is why a diagram showing only a bridge can omit the failure point that matters. Record the host listener, forwarding helper, container namespace and application listener separately.

Host networking removes a namespace boundary and changes available host service access. It is a deliberate architectural choice, not a universal fix for failed publication. Low-numbered host ports may require host policy changes; use unprivileged loopback ports behind the existing reverse proxy rather than expanding privileges to obtain port 80.

## Name resolution and port reachability

Create a user-defined network and a service on it. The names are chapter-specific so cleanup stays bounded:

```bash
podman --remote=false network create dd-net-64
podman --remote=false network inspect dd-net-64
podman --remote=false run --detach --name dd-web-64 \
  --network dd-net-64 --network-alias web \
  --publish 127.0.0.1:8089:80 \
  docker.io/library/nginx:alpine
podman --remote=false port dd-web-64
curl --fail --show-error --max-time 5 http://127.0.0.1:8089/
podman --remote=false run --rm --network dd-net-64 \
  docker.io/library/busybox:1.37 \
  wget -T 5 -q -O - http://web:80/
```

`network create` allocates a named network under this account's engine. Inspect its backend-reported configuration and DNS setting before assuming name resolution works. `--network-alias web` provides a network-scoped service name where network DNS is enabled. The disposable BusyBox client joins that network and requests the service's container port directly. It does not use host port 8089.

The two probes establish different evidence. Host `curl` exercises loopback publication. BusyBox `wget` exercises container-network name resolution and connectivity. If the first succeeds and the second fails, investigate DNS/network membership rather than the host's TLS proxy. If the second succeeds and the first fails, inspect the host listener and publication. Both succeeding still leaves public TLS routing, certificate validation and application readiness untested.

A service name on this network is not automatically an internet DNS record or a hostname resolvable by the host. Likewise, `localhost` inside the client container points to that client's own network namespace. Use `web:80` here, not `localhost:8089`. In a pod, shared networking changes that relationship; Chapter 65 develops that case.

An image's `EXPOSE` metadata does not itself request this specific host publication. Declare the mapping and verify it. The `127.0.0.1` binding restricts this example to IPv4 loopback on the execution host. It does not automatically create an IPv6 listener. A reverse proxy configured for `::1` can therefore fail while the shown IPv4 probe succeeds. Match proxy upstream address family and publication explicitly.

Do not infer external accessibility solely from a successful local probe. Public routing additionally depends on host firewall, provider firewall/security policy and the edge listener. Ubuntu UFW and Fedora/RHEL firewalld have different management interfaces, and neither should be manipulated speculatively from this rootless lab. Consult [firewall policy](../03-networking-and-traffic/027-firewalls-and-network-policy.md), inspect actual traffic paths, and test from an authorized external client when the design requires it.

## Diagnosing a network mismatch

Create a deliberate mismatch: launch the client without attaching it to `dd-net-64`.

```bash
podman --remote=false run --rm docker.io/library/busybox:1.37 \
  wget -T 5 -q -O - http://web:80/
podman --remote=false inspect dd-web-64
podman --remote=false network inspect dd-net-64
podman --remote=false logs --tail 50 dd-web-64
```

The expected failure is that `web` cannot resolve or reach this network-scoped service from an unrelated network. The exact error depends on DNS configuration; a host environment that also defines `web` may resolve somewhere else, which is why names and addresses must be checked together. Recover by using the intended network and repeating the same bounded request. Do not add arbitrary public DNS records for an internal alias.

If name resolution succeeds but the connection fails, confirm the returned address belongs to the current service, the client is attached to the right network and the application listens on port 80. Preserve the failing destination and timestamp. A stale address from an earlier object can make DNS look healthy while directing traffic to the wrong instance. Avoid building operational automation around a dynamically assigned container IP when a supported service alias is available.

If traffic reaches the application but returns 502 from the host reverse proxy, the engine may be functioning correctly. Inspect the proxy's configured upstream, scheme and address family. For example, `https://127.0.0.1:8089` is wrong for this plain-HTTP fixture. A TLS failure on that connection should not be diagnosed by opening additional firewall ports.

When a rootless workload needs host services, verify the installed version's `host.containers.internal` behavior and actual generated hosts file. The alias is not a promise that every host-only listener is reachable under every mode. A container trying `127.0.0.1:5432` addresses itself unless it shares the host network namespace. Prefer an explicit supported path with authentication and a narrow listener instead of broadly exposing the database.

Measure source addresses under the selected path. Named rootless bridge forwarding may rewrite them differently from pasta. A reverse proxy can send a trusted forwarded address header, but the application must only trust headers from the approved proxy path. An internet client can fabricate those headers when direct access remains available. Engine networking and application security must agree on the boundary.

For intermittent failures, collect application latency, CPU pressure, forwarding helper state, connection errors and DNS timing before blaming the network backend. A saturated application backlog can resemble a packet loss problem. A service that occasionally returns late still needs a bounded probe and timestamp correlation, not just a single successful ping. ICMP permission differences also make ping a poor substitute for the actual HTTP request.

## Design and recovery choices

The fictional VPS team keeps one externally reachable reverse proxy and loopback-only application publication. That suits a small single-host service and makes its exposure easy to audit. The fictional Kubernetes team will later use service objects and cluster policy; importing its assumptions into this host would add complexity without providing a scheduler. The fictional managed-cloud team may delegate ingress to a provider and must verify that provider's own contract.

Before a networking backend change, inventory container networks, publications, DNS aliases and clients. Recreate bounded test objects under the new configuration, then verify both ingress and internal paths. Existing objects can retain configuration from creation time. Do not delete all network metadata to force a change on a live host. A rollback needs the old configuration and a recreate plan, and persistent data must remain outside the replaced containers.

Clean up only this fixture after collecting evidence:

```bash
podman --remote=false stop --time 10 dd-web-64
podman --remote=false rm dd-web-64
podman --remote=false network rm dd-net-64
```

Network removal should refuse when active endpoints still depend on it. Investigate that refusal instead of forcing deletion; it may expose an unexpected dependency. The images can remain cached for later chapters.

## Exercises and review questions

1. Build a four-row matrix for host probe and container probe success/failure. **Guidance:** isolate publication, DNS/network membership, application binding and common application failure rather than assigning every failure to a firewall.
2. Explain why `localhost:8089` is wrong in the BusyBox client. **Guidance:** its loopback belongs to its own namespace; the service's network endpoint is `web:80`.
3. A proxy uses IPv6 loopback and the lab uses IPv4. How do you verify the mismatch? **Guidance:** inspect listener addresses and probe the configured upstream explicitly.
4. Plan a rootless backend upgrade for a service using client IP for abuse controls. **Guidance:** compare observed addresses and trusted proxy headers across paths before and after recreation, including rollback.

## Takeaways and further reading

Test the requested traffic path, not a nearby substitute. Network backend, rootless forwarding, service DNS and application binding are distinct operational facts. Continue with [pods and Kubernetes YAML](065-podman-pods-and-kubernetes-yaml.md).

The [network-create manual](https://docs.podman.io/en/stable/markdown/podman-network-create.1.html) and upstream Podman run networking reference were inspected 2026-10-03. No network or firewall change, HTTP probe or container execution was performed by the author.
