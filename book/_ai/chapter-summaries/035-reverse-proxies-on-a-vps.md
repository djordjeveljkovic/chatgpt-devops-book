# Chapter 35 continuation

Status: complete

## Written material
Nginx single-upstream HTTP example with a rejecting default host; Ubuntu and Fedora/RHEL install/include paths; proxy headers and trust boundaries; body and timeout semantics; syntax/start/reload and local/external path checks; SELinux proxy-connect diagnosis and rollback; TLS handling considerations; buffering, multiple hosts, diagnostics and answer-guided exercises.

## Concepts and terminology
Reverse proxy, upstream, forwarded-header trust, request-body limit, connect/send/read inactivity timeout, buffering, virtual host, TLS termination.

## Examples and cross-references
Example forwards to 127.0.0.1:8080 and uses fictional orders.example.test; 64 KiB limit from Chapter 10 contract. Chapter 34 supplies local service. Links to chapters 27, 29, 30 and 36. Nginx configuration is illustrative and package paths vary.

## Open threads
No real Nginx package, certificate, DNS, provider firewall, application or external route tested. Add concrete TLS server block only after book's cert lifecycle direction is confirmed.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
The Nginx config was not validated with `nginx -t` against an installed package. Official Nginx proxy/upstream and Red Hat RHEL 9 reverse-proxy documentation inspected 2026-10-04. Scoped and full book syntax/link checks passed on 2026-10-04.
