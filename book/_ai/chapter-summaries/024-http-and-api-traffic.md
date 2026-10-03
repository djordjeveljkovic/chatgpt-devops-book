# Chapter 24 continuation

Status: complete

## Written material
HTTP method semantics and status/header interpretation; HTTP/1.1 framing and connection reuse; reverse-proxy trust and timeout boundaries; complete loopback-only Python server and curl commands; timing output; request failure diagnosis and exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Safe/idempotent method, status, content type/length, hop, reverse proxy, forwarded header trust, connect/transfer deadline, request ID, durable idempotency result.

## Examples and cross-references
Python 3.14 standard-library server binds only to `127.0.0.1:18081`; provides `/healthz`, `/orders` and one-request-per-accepted-connection lab behavior. Order response is explicitly non-persistent and non-production. Curl examples show health, missing path, order acceptance and timing. Links to Chapters 22, 23, 25 and relevant later chapters.

## Open threads
Independent review found no material issue. Optional improvements remain: avoid requiring Python 3.14 for APIs available in earlier Python 3 releases and set accepted-socket timeouts if hardening the learning server against stalled clients. Local HTTP exchanges were executed; no TLS, public reverse proxy or durable order flow was tested.

## Verification
Inspected RFC 9110 and RFC 9112, curl manual, Python 3.14 `http.server` and `urllib` references on 2026-10-02. Python syntax and all local examples passed the chapter checker. Exact `/healthz`, missing-path and `/orders` exchanges executed outside the sandbox with curl 8.22.0 and Python 3.14.7; observed HTTP 200, 404 and 202 with expected bodies, and verified the server exited with port 18081 no longer listening. No TLS, public reverse proxy or durable order flow tested.
