# Chapter 21 continuation

Status: draft

## Written material
Interfaces and link state; IPv4/IPv6 prefixes; CIDR membership; MTU and IPv6 control traffic; longest-prefix and policy routing; next-hop neighbor resolution; forward/return paths; read-only `ip` observations; Python subnet calculation lab; Harbor prefix fault diagnosis; Netplan and NetworkManager ownership; recovery and exercises.

## Exact next section
Independent technical and editorial review.

## Concepts and terminology
Interface, administrative/carrier state, prefix, CIDR, MTU, connected/default/more-specific route, metric, policy-routing rule, next hop, neighbor entry, source address and return path.

## Examples and cross-references
Fictional `10.42.8.0/24` API subnet and `10.42.9.30` database; Python `ipaddress` lab; `ip route get` and interface observations. Links to Chapters 20, 22, 28 and Volume 3. Examples do not change host configuration.

## Open threads
Independent review; no live Ubuntu, Fedora or RHEL configuration was changed. Check each package name and persistent manager instructions during review.

## Verification
Inspected upstream iproute2 `ip-link`, `ip-address`, `ip-route` and `ip-neighbour` manuals; Netplan examples; NetworkManager CLI reference; Python 3.14 `ipaddress`; RFC 4632 and RFC 8200 on 2026-10-02. Python subnet example executed with Python 3.14.7 and produced the expected membership and `/25` results. Read-only `ip address`, IPv4/IPv6 routes and `ss -ltn` executed on iproute2 7.2.0 outside sandbox; sandbox lacked netlink access. No actual route or interface was modified. No cloud path tested.
