---
book: The Complete DevOps Engineering Book
volume: 3
volume_title: "Networking and Traffic"
chapter: 23
title: "DNS from Resolver to Authority"
slug: dns-from-resolver-to-authority
status: draft
summary: ../../_ai/chapter-summaries/023-dns-from-resolver-to-authority.md
---

# Chapter 23 — DNS from Resolver to Authority

## Why this matters

Harbor changes the address of its DispatchDesk API during a migration. Some clients reach the new host, others continue using the old one, and a local `dig` result appears to contradict the browser. Several DNS layers can answer the same question from different caches, and a process may use a local hosts file or resolver service before it sends any DNS packet. A name lookup is a path through configured authorities and caches, not a single global read.

This chapter follows the name from an application toward authoritative data, then investigates a failed change. [Chapter 22](022-tcp-udp-and-connections.md) covers the transport exchanges used by ordinary DNS. The examples query public names for read-only diagnostics; substitute your organization's approved nameserver for internal domains. Do not send confidential internal names to a public resolver.

## Recursive and authoritative resolution

An application commonly asks a stub resolver to turn a hostname into one or more resource records. The stub follows the host's resolver configuration, which may point at a local caching service, a VPN-provided resolver or a network gateway. That recursive resolver performs the work needed to answer the client's question and normally caches records. A recursive resolver's response is not necessarily fetched fresh from the zone's authoritative servers on every query.

DNS is a distributed hierarchy. A resolver that needs an uncached answer can begin with root-server information, follow a referral to the relevant top-level domain, then follow another referral toward the domain's authoritative nameservers. Each referral directs the resolver deeper into the namespace. The final authoritative server answers from its configured zone data. Root and TLD servers do not contain every website's address. [DNS concepts and delegation](https://www.rfc-editor.org/rfc/rfc1034.html).

A zone is an administrative portion of the namespace. A delegation transfers authority for a child zone to named authoritative servers. At the parent, NS records identify those nameservers. When a nameserver's hostname is inside the child zone it serves, glue address records at the parent can break the bootstrap dependency. Delegation data and child-zone data are related but separate; they can disagree during a change.

A resource record has a name, type, class, TTL and type-specific data. `A` records return IPv4 addresses; `AAAA` records return IPv6 addresses. `CNAME` records alias one DNS name to another and can require additional resolution. An `MX` record describes mail routing, not the address of a web API. DNS name resolution does not select the application's TCP port; URI and client configuration supply that separately.

There are different ways to ask questions. `dig` sends DNS questions to a configured or explicit DNS server. It is useful for inspecting record types and authority fields. Normal application lookup may also use `/etc/hosts`, NSS modules, a language runtime cache, service discovery, or a proxy. Therefore a successful `dig` query does not prove the application used that same answer. Conversely, a hosts-file entry can make the application succeed while DNS itself is broken.

DNS usually uses UDP, and also uses TCP when response size, truncation, or protocol requirements call for it. TCP is a normal DNS transport, not proof of a zone transfer. Firewalls and middleboxes must allow the actual resolver traffic required by the design. DNSSEC adds data-origin authentication and integrity validation to the DNS hierarchy; it does not encrypt ordinary DNS queries. Trust depends on the validating resolver and how clients use its validation results. [DNSSEC overview](https://www.rfc-editor.org/rfc/rfc4033.html).

## Caching, TTL and negative responses

An authoritative answer's TTL indicates how long a cache may retain that record before it should refresh it. A recursive resolver may return the remaining cached lifetime, so two answers observed at different times can show different TTLs while representing the same underlying record. A lower TTL helps shorten cache persistence only after the lower value has propagated; it cannot recall answers already cached under a longer earlier TTL.

Caches exist at recursive resolvers, local stub services, application runtimes, language libraries and sometimes proxies. A browser can therefore behave differently from a fresh `dig` query. Local caches may need no explicit flush if their remaining TTL naturally expires. Clearing a resolver cache changes only that cache; it cannot clear a remote resolver or a running process's private cache.

Negative answers are cached too. `NXDOMAIN` says the queried name does not exist according to the responding authority; `NOERROR` with no record of the requested type can mean the name exists but has no such record. This is often called NODATA. These conditions have different repair implications. Negative caching uses information from the zone's SOA and is bounded according to DNS negative-caching rules. A name created after a cached negative answer can remain unavailable until that negative entry expires. [Negative DNS caching specification](https://www.rfc-editor.org/rfc/rfc2308.html).

A TTL is not a synchronized global expiration moment. Recursive resolvers refresh independently, can be unavailable, or can implement stale-answer behavior under their policy. Clients may keep using an address for the lifetime of a connection long after DNS has changed. A DNS cutover thus needs both a record plan and a connection/drain plan.

## Inspect the actual resolver path

Start on the Linux host where the affected application runs. The following commands do not change configuration. They expose the local resolver setup and query record types:

```bash
cat /etc/resolv.conf
getent ahosts api.example.com
resolvectl status
resolvectl query api.example.com
```

Use the commands supported by the host. `getent` asks through the system name-service path and is useful for approximating a typical libc application lookup. `resolvectl` is available only where systemd-resolved is installed and integrated; it can show per-link DNS state. `/etc/resolv.conf` may be a generated symlink to a local stub rather than the upstream recursive server. Do not edit it directly until you identify its owner. [Resolver file behavior](https://man7.org/linux/man-pages/man5/resolv.conf.5.html) and [resolvectl manual](https://man7.org/linux/man-pages/man1/resolvectl.1.html).

On an Ubuntu host using Netplan and systemd-resolved, inspect both the network manager's nameserver inputs and the resolver's active per-link state. On Fedora or RHEL using NetworkManager, inspect active connection profiles and `nmcli device show` for DNS-related properties. VPN profiles can install route-specific domains and nameservers. A global query that succeeds through Wi-Fi does not prove the internal suffix routes to the VPN resolver. RHEL repository availability and tools depend on its subscribed release.

Use `dig` to ask an explicit question. These commands query your configured resolver for public example data; the exact addresses and TTLs change and are not part of the lesson:

```bash
dig example.com. A
dig example.com. AAAA
dig example.com. NS
dig example.com. SOA
dig example.com. A +noall +answer
```

The trailing dot makes the DNS name absolute and avoids appending a search suffix. The final form limits the display to answer records. Read the status, query section, answer and authority section. An empty answer alone is ambiguous until you inspect the response code and authority data. For a domain you own, query its actual name and record type rather than copying `example.com` results into a production decision.

Ask a specific recursive server by passing its address after `@`:

```bash
dig @192.0.2.53 api.internal.example. A
```

`192.0.2.53` is reserved for documentation and will not be your real resolver. Substitute a server you are authorized to query. Compare that result with the default path. An explicit server query bypasses some local resolver-selection logic, so it answers a narrower question.

`dig +trace example.com. A` asks the tool to follow delegation from the root using iterative queries. It can reveal a broken delegation chain, but it contacts multiple external servers directly and may fail where egress DNS is restricted. It does not reproduce a normal client's recursive path or prove that a configured recursive resolver works. Treat the command as a deliberate diagnostic with the organization's network policy in mind. `+dnssec` requests DNSSEC-related records; the flag alone does not prove that your local resolver validated a signature.

## A DNS investigation with dig

Assume the current authoritative answer for Harbor's API is `203.0.113.40`, and the proposed new address is `203.0.113.55`. Those documentation-only addresses illustrate the scenario; they are not routable service endpoints. First query the current record through the application's configured recursive path. Record the time, resolver address, answer, TTL, status and whether the application has its own cache.

Then ask the authoritative nameserver directly. Find the zone's NS records, obtain a nameserver address, and query that server for the record. Direct authoritative queries distinguish stale recursive cache from current zone data. They do not prove the parent delegation points to that authority; `+trace` or explicit parent and child queries can examine that separate link. A disagreement between parent delegation and child NS records can create resolver-dependent failures.

Compare A and AAAA records independently. A correct IPv4 answer does not imply IPv6 is correct. Some clients race both address families or select one based on connection results, as discussed in [Chapter 22](022-tcp-udp-and-connections.md). Test the chosen address from the same network and runtime context as the failing process. DNS output identifies candidate addresses, not reachability or application health.

An investigative record should preserve the full response code. `SERVFAIL` often means the recursive resolver could not complete or validate resolution; it does not identify which upstream step failed. `REFUSED` indicates the server declined the query under its policy. `NXDOMAIN` and NODATA are meaningful negative responses. A timeout can be packet loss, firewall policy, a silent server, or a broken return path. Compare the same query against another authorized resolver only when policy allows, and preserve where each answer came from.

## Debugging a failed DNS change

Harbor updates its API record, and one worker still connects to the old address. Check the worker's effective hostname and resolver configuration first. Resolve through the system lookup path used by that worker, then query the configured recursive server with `dig`, and finally query the authority. The pattern matters: if authority is current but recursion is old, a cache or delegation path is likely; if recursion is current but the worker is old, investigate application caching, connection pools, proxies or a different hostname.

Inspect all records involved in the application path, including CNAME targets, A and AAAA answers, split-horizon views, and per-link DNS routing. Confirm that the new endpoint accepts the expected transport and application protocol from the worker's actual network. A correct DNS record can direct clients to an unreachable host, so the answer alone is not successful recovery.

Do not flush every cache as the first repair. It can increase query load and erase useful evidence while leaving the cause intact. Record before-and-after answers and TTLs. Restart an application only if its own cache or connection lifecycle requires it, and establish how pending work will be retried safely before recycling workers.

## Plan a reversible cutover

For a planned endpoint migration, lower the relevant TTL in advance and wait at least the previous TTL before the cutover. The required wait can be longer when resolver behavior is unknown or a provider has documented propagation delays. Prepare and validate the destination before publishing it; DNS does not make an unready endpoint safe. During transition, both destinations may need to serve requests.

Change the record through the authoritative provider's supported control plane, then query the authority and several representative recursive resolvers. Monitor request rate and errors at old and new endpoints. Keep the old endpoint available through the plausible cache and active-connection tail. If failure criteria are met, restore the old record and leave both endpoints ready while caches converge. Raising TTL after stable cutover can reduce later query volume, but only after operational evidence supports it.

A low TTL does not guarantee instant worldwide cutover. Some clients cache beyond policy, established connections persist, and negative answers can outlive a newly created record. Make rollback mean “old service can still safely handle the work,” not merely “the DNS record was edited back.”

## Exercises, review questions and takeaways

1. Compare `getent ahosts` with `dig` for a hostname intentionally present in `/etc/hosts`. Guidance: the system lookup path can find a local entry without querying DNS; note the response source rather than assuming both tools share it.
2. Query an existing name for an absent record type and compare it with an invented `.invalid` name. Guidance: distinguish NODATA from NXDOMAIN by status and authority sections.
3. Design a safe address cutover. Guidance: account for the old TTL, authoritative readiness, separate A/AAAA records, active connections, monitoring and rollback capacity.
4. Explain why flushing the local cache does not fix an old answer held by a recursive resolver. Guidance: identify each independent cache boundary.

Review questions: What is the difference between recursive and authoritative service? Why can lowering TTL today fail to shorten a cache populated yesterday? What does `dig` test that `getent` may not? Good answers name the resolver path and observation point.

Preserve the answering resolver, status and TTL alongside each observation. Repair the layer that supplied the stale or incorrect data, then test the application path. Continue to [Chapter 24](024-http-and-api-traffic.md) to follow the request after its name becomes an address.
