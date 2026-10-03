# Chapter 23 continuation

Status: complete

## Written material
Stub, recursive and authoritative resolution; zones and delegation/glue; record types; DNS transport and DNSSEC boundaries; positive/negative caching and TTL timing; local system resolver inspection; `dig` query interpretation; direct resolver/authority/trace comparison; stale-answer diagnosis; reversible cutover; exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Stub resolver, NSS, recursive resolver, authoritative server, zone, delegation, glue, RR/TTL, A/AAAA/CNAME/MX/NS/SOA, NXDOMAIN, NODATA, negative caching, DNSSEC validation, split-horizon, active connection.

## Examples and cross-references
Read-only `getent`, `resolvectl`, `dig` examples use fictional hostnames or public `example.com`; direct internal resolver example uses RFC documentation address only as placeholder. Links to Chapters 22 and 24. No record mutation or cache flush.

## Open threads
Independent review found no material issue. An optional usability improvement remains: state distro-specific `dig` package prerequisites (Ubuntu `dnsutils`/`bind9-dnsutils`; Fedora/RHEL `bind-utils`). `dig` commands were not executed because sandbox networking blocks sockets; no system-specific resolver or DNSSEC runtime was tested.

## Verification
Inspected RFC 1034, RFC 1035, RFC 2308, RFC 4033, Linux `resolv.conf` and `resolvectl` manuals and BIND `dig` reference on 2026-10-02. `dig -v` attempted in sandbox and reported that it could not open networking sockets; no live DNS query result is asserted. All nameserver addresses in the fictional examples are documentation-only or explicitly marked for substitution.
