# Chapter 24 continuation

Status: draft

## Written material
HTTP method semantics and status/header interpretation; HTTP/1.1 framing and connection reuse; reverse-proxy trust and timeout boundaries; complete loopback-only Python server and curl commands; timing output; request failure diagnosis and exercises.

## Exact next section
Independent technical and editorial review.

## Concepts and terminology
Safe/idempotent method, status, content type/length, hop, reverse proxy, forwarded header trust, connect/transfer deadline, request ID, durable idempotency result.

## Examples and cross-references
Python 3.14 standard-library server binds only to `127.0.0.1:18081`; provides `/healthz`, `/orders` and one-request-per-accepted-connection lab behavior. Order response is explicitly non-persistent and non-production. Curl examples show health, missing path, order acceptance and timing. Links to Chapters 22, 23, 25 and relevant later chapters.

## Open threads
Independent review; run exact local HTTP examples if socket permissions permit; validate `http.server` lifecycle and curl flags against installed versions. No TLS, public reverse proxy or durable order flow tested.

## Verification
Inspected RFC 9110 and RFC 9112, curl manual, Python 3.14 `http.server` and `urllib` references on 2026-10-02. Python syntax to be checked; exact `/healthz`, missing-path and `/orders` exchanges executed outside the sandbox with curl 8.22.0 and Python 3.14.7; observed HTTP 200, 404 and 202 with the expected bodies, and verified the server exited with port 18081 no longer listening. No TLS, public reverse proxy or durable order flow tested.
