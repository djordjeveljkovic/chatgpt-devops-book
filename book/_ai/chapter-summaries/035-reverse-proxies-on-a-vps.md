# Chapter 35 continuation

Status: draft; independent review pending.

## Written material
Nginx single-upstream HTTP example; proxy headers and trust boundaries; body and timeout semantics; syntax/reload and local/external path checks; TLS handling considerations; buffering, multiple hosts, diagnostics and exercises.

## Concepts and terminology
Reverse proxy, upstream, forwarded-header trust, request-body limit, connect/send/read inactivity timeout, buffering, virtual host, TLS termination.

## Examples and cross-references
Example forwards to 127.0.0.1:8080 and uses fictional orders.example.test; 64 KiB limit from Chapter 10 contract. Chapter 34 supplies local service. Links to chapters 27, 29, 30 and 36. Nginx configuration is illustrative and package paths vary.

## Open threads
No real Nginx package, certificate, DNS, provider firewall, application or external route tested. Add concrete TLS server block only after book's cert lifecycle direction is confirmed. Independent review pending.

## Exact next section
None. Begin Chapter 37, then request independent review before claiming completion.

## Verification
Book checker passed chapter-specific syntax and links. The Nginx config was not validated with nginx -t against an installed package. Official Nginx proxy and upstream documentation inspected 2026-10-02.
