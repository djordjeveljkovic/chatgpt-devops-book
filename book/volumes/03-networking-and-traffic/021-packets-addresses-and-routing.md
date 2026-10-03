---
book: The Complete DevOps Engineering Book
volume: 3
volume_title: "Networking and Traffic"
chapter: 21
title: "Packets, Addresses and Routing"
slug: packets-addresses-and-routing
status: complete
summary: ../../_ai/chapter-summaries/021-packets-addresses-and-routing.md
---

# Chapter 21 — Packets, Addresses and Routing

## Why this matters

Harbor's DispatchDesk API can answer a request on its own host, yet its notification worker cannot reach a provider. Restarting the API changes nothing. Before investigating application code, the team needs to establish which destination address it attempted, which interface carried the packet, which source address it used, and whether replies could return. A network failure is a claim about a path, not a diagnosis.

This chapter starts with a single Linux host and an ordinary routed IP network. It builds on [Chapter 20](../02-linux-and-automation/020-scheduling-and-resource-limits.md). It does not require an existing DispatchDesk deployment. The private addresses below describe a fictional lab; substitute an approved destination from your own environment when running host observations. Internet connectivity, DNS resolution, transport establishment and application success are separate pieces of evidence.

## Interfaces, addresses and subnets

An interface is a kernel object through which network traffic can pass. It might represent a physical Ethernet adapter, Wi-Fi, a virtual bridge, a tunnel or loopback. An interface name such as `enp1s0` identifies that object on a particular host. It is not an address, and copying a name from another server does not make it exist locally. Administrative state and carrier state differ: an enabled physical adapter can still lack a connected cable. [Linux interface manual](https://man7.org/linux/man-pages/man8/ip-link.8.html).

An IP address identifies a location within an address family and routing context. A host can have several addresses on one interface and several interfaces at once. `127.0.0.1` and `::1` refer to loopback within the current network namespace. A service bound only to loopback is unavailable through another host's network interface. A wildcard listener is a binding choice, not proof that external packets can traverse every intervening policy.

A prefix length tells you how many leading address bits identify a network. In the fictional `10.42.8.20/24`, the first 24 bits select `10.42.8.0/24`; the last eight identify an address within it. A `/25` divides that space into two smaller ranges. Comparing decimal text prefixes is unreliable: `10.42.8.130` lies outside `10.42.8.0/25` despite sharing its first three octets. CIDR prefixes express address blocks and support aggregation. [CIDR specification](https://www.rfc-editor.org/rfc/rfc4632.html).

Address ownership and route selection are related but distinct. Configuring an address commonly creates a connected route for its prefix. A route can also refer to a network for which the host has no local address, using a reachable router as the next hop. A private address is not inherently unreachable within your organization; private networks can be routed over provider networks or VPNs. Conversely, merely selecting private space does not establish access controls or encryption.

IPv6 uses 128-bit addresses and supports several scopes. A link-local address such as `fe80::1` needs an interface context when multiple links are possible. IPv6 Neighbor Discovery performs functions that IPv4 commonly handles through ARP; disabling all ICMPv6 can break ordinary network operation. IPv6 routers do not fragment forwarded packets. Path MTU handling therefore matters when tunnels reduce the available packet size. [IPv6 specification](https://www.rfc-editor.org/rfc/rfc8200.html).

The maximum transmission unit, or MTU, limits the packet size an interface can carry at the IP layer. A tunnel adds headers and can reduce the size available to its inner packet. If small probes work but larger exchanges stall, investigate packet-size evidence and necessary control messages. Do not jump from that pattern to a global MTU change without locating the affected path.

## Routing tables and packet paths

Imagine an API host with address `10.42.8.20/24`, a router at `10.42.8.1`, and a database at `10.42.9.30`. The database lies outside the host's directly connected prefix. A route can send that destination through the router; the router then makes its own forwarding decision. A default route supplies a fallback for destinations lacking a more specific match.

Within an applicable routing table, a longer matching prefix takes precedence over a shorter one. Thus a `/24` route can steer a database subnet differently from a `/0` default. Metrics distinguish competing routes where their other selection criteria permit it; a low default-route metric does not override a more specific route. Linux can also select tables through policy rules, using criteria such as source address or packet mark. Reading only the main table can miss the decision relevant to a multi-interface host. [Routing manual](https://man7.org/linux/man-pages/man8/ip-route.8.html).

On an Ethernet link, sending an IP packet requires a link-layer destination. For an on-link destination, the host resolves that destination's neighbor address. For an off-link destination, it resolves the next-hop router instead. An ARP lookup for the remote database on the API's link can indicate an incorrect prefix or route. A neighbor entry describes the adjacent link, not the entire Internet path. [Neighbor-table manual](https://man7.org/linux/man-pages/man8/ip-neighbour.8.html).

Every reply needs a route too. A request may reach a database whose response leaves through an unexpected router. A stateful firewall can then reject traffic it did not see established. NAT can further change the addresses visible at different observation points; [Chapter 28](028-nat-proxies-and-connection-tracking.md) develops that boundary. Draw forward and return paths separately whenever several interfaces, VPNs or provider networks are involved.

## Inspect the host before changing it

Run these observations as your ordinary user on the Linux host where the failing process runs. They do not modify network configuration. The working directory does not matter. Install missing tools through your distribution's configured repositories: Ubuntu packages the utility as `iproute2`; Fedora and subscribed RHEL systems use package `iproute`. Package installation needs administrative privileges, but the observations themselves generally do not.

```bash
ip -Version
ip -brief link show
ip -brief address show
ip -4 route show
ip -6 route show
ip rule show
ip neigh show
```

`-brief` makes interface output compact. `-4` and `-6` isolate the address families. Record addresses, prefixes, interface states and routes together. Preserve command errors too: a restricted container or sandbox may deny netlink access, so absence of output is not evidence that the host has no routes.

For an approved real destination, replace this fictional database address and ask the kernel to resolve the route:

```bash
ip -4 route get 10.42.9.30
```

This lookup does not send a probe. Read its chosen device, next hop and source address. The result can expose a mistaken VPN route or an unexpected source address, but it does not establish remote reachability. If the application binds a particular source address, reproduce that condition with the route command's `from` selector after confirming the address belongs to this host.

The following is illustrative output for the fictional topology, not a result measured on the author's machine:

```console
10.42.9.30 via 10.42.8.1 dev enp1s0 src 10.42.8.20
```

A correct-looking lookup narrows the investigation to later boundaries. It does not prove that the router forwards, the provider permits the traffic, or the remote listener exists.

## A subnet calculation lab

On any Linux host with Python 3, run this complete program as an ordinary user. It changes no host configuration and needs no network access. The standard `ipaddress` library validates networks and checks membership; `strict=True` rejects a network definition with host bits set. [Python address-library reference](https://docs.python.org/3/library/ipaddress.html).

```python
from ipaddress import ip_address, ip_network

api_network = ip_network("10.42.8.0/24", strict=True)
for candidate in ("10.42.8.20", "10.42.8.130", "10.42.9.30"):
    address = ip_address(candidate)
    print(address, "on-link by configured prefix:", address in api_network)

for subnet in api_network.subnets(new_prefix=25):
    print("subnet:", subnet, "addresses:", subnet.num_addresses)
```

Expect the two `10.42.8` addresses to pass membership and the database address to fail. Both `/25` subnets contain 128 addresses. That count includes all numerical addresses; it is not a provider's usable-host guarantee. Providers can reserve addresses, and IPv4 subnet conventions depend on the prefix and link type. Never derive a cloud capacity promise from arithmetic alone.

Change the API network to `10.42.8.0/25` and run again. The `.130` result changes. This reproduces the reasoning behind a prefix incident without disrupting a real interface. Cleanup consists only of removing the lab file if you saved one.

## Diagnosing an unreachable destination

Harbor changes the API's private prefix from `/24` to `/16` by mistake. Its database remains at `10.42.9.30` behind the router. The host now considers that database on-link and tries to resolve it locally instead of sending through the gateway. No database process restart can repair that path.

Investigate from the worker's actual execution environment. First confirm its configured destination is correct. Then compare address/prefix observations against the approved network design and run the destination route lookup. Inspect neighbors on the selected link. An unresolved neighbor plus an unexpected direct route supports the prefix hypothesis; it does not prove it by itself, because a disconnected link or missing adjacent host can produce similar neighbor evidence.

Check the network manager's persistent settings and any recent change. After confirming the incorrect prefix, restore the approved value through the owning manager. Use console access and a tested rollback path for remote changes. Recheck the route and neighbor behavior, then verify a connection to the database's actual port. Finally run an application operation whose result can be observed without creating duplicate orders. An ICMP echo response would still be weaker evidence than the worker's successful database exchange.

A timeout alone cannot distinguish a silent firewall drop, broken return route, offline host or congestion. A local “network unreachable” error suggests a local routing decision; a received ICMP error adds evidence from another node. Record the exact error and observation point instead of flattening every failure into “the network is down.” Later chapters add transport and packet-capture evidence.

## Persistent configuration and recovery

An `ip` mutation affects running kernel state; it does not automatically update the manager that reconstructs the network at boot or lease renewal. An emergency route can disappear later, or the manager can overwrite it. Recovery is complete only when the intended persistent configuration and runtime state agree.

On Ubuntu installations managed by Netplan, inspect the YAML under `/etc/netplan/` and identify its renderer. NetworkManager and systemd-networkd are different back ends. Cloud images may have provider or cloud-init ownership of these files. Netplan can represent static addresses and routes, but replacing the directory with a tutorial example can remove necessary provider settings. [Netplan configuration examples](https://netplan.readthedocs.io/en/stable/examples/).

On Fedora and RHEL hosts using NetworkManager, identify the active connection profile before editing. These ordinary-user observations distinguish saved profiles from attached devices:

```bash
nmcli connection show --active
nmcli device status
```

A profile name need not equal an interface name. Inspect its address, route and automatic-configuration settings before planning a change. Activating a changed profile can interrupt remote access; arrange console recovery and restore the exact saved profile when necessary. RHEL repository access and packaged versions depend on its subscription and release. The shared CLI does not make Fedora's package baseline identical to RHEL's. [NetworkManager CLI reference](https://networkmanager.dev/docs/api/latest/nmcli.html).

For Harbor, one documented private route and an accurate prefix are preferable to accumulating ad hoc routes after each incident. As additional hosts and VPNs arrive, record who owns each subnet, which paths carry management traffic, and which return routes are required. A diagram that includes addresses, prefixes and gateways is more actionable than a box labeled “network.”

## Exercises, review questions and takeaways

1. Run the arithmetic lab with both prefixes. Explain why `.130` changes membership while `.20` does not. Guidance: compare the boundary at 128, not the dotted text alone.
2. Inspect an approved destination with `ip route get`. Which parts describe local selection, and which parts remain unproven? Guidance: the source, device and next hop are local evidence; remote forwarding and application health require later checks.
3. Draw the database request and return paths for the fictional topology. Guidance: include the database's gateway and identify where a stateful policy could see only one direction.
4. Explain why a runtime route repair disappears after reboot. Guidance: inspect the owning persistent manager rather than assuming the kernel writes its changes back to configuration.

Review questions: How does a prefix differ from an interface? Which neighbor is resolved for an off-link destination? Why can IPv4 success coexist with IPv6 failure? A sound answer distinguishes addressing, route selection, adjacent-link delivery and address-family-specific paths.

Record the path before repairing it, restore the configuration at its owning layer, and verify the workload after the route is corrected. Continue to [Chapter 22](022-tcp-udp-and-connections.md) for the connection evidence that IP reachability alone cannot supply.
