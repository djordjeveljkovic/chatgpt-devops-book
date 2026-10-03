# Independent review — Chapter 24

Reviewer: review_volume3_021_025 (independent reviewer)
Date: 2026-10-03
Reviewed body SHA256: e18a624be423bafe0bb68517a223f267b68f9593d2cfe54840df0f491a8d7f5d

## Scope and findings

Read AI_AUTHORING_GUIDE.md, PROGRESS.md, BASELINE.md, manifest record, skeleton brief, manuscript, chapter summary and prerequisite summary/manuscript context.

Inspected safe/idempotent method semantics, status and header boundaries, HTTP/1.1 framing, proxy header trust, hop deadlines, durable order versus lab response, curl flags/timing/address override and secret handling. The one-connection lifecycle and need to restart before each curl are explicit. Exercises and takeaways meet the brief. No material finding.

- Low, “A complete local HTTP lab”, first paragraph: “requires Python 3.14” is unnecessarily restrictive for APIs used here and exceeds the default Python on several book baselines. Prefer “Python 3; tested with 3.14” or explain installation.
- Low, same section, HTTPServer lifecycle: server.timeout bounds waiting to accept a request, not an already accepted client that stalls its headers/body. The text accurately calls it an accept timeout and provides Ctrl-C cleanup; optionally set accepted-socket timeouts to improve robustness of this loopback learning server.

## Dated primary-source evidence

Inspected on 2026-10-03:

- [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html).
- [Python http.server](https://docs.python.org/3/library/http.server.html).
- [curl manual](https://curl.se/docs/manpage.html).

## Verification and limits

Measured tools: Python 3.14.7, curl 8.22.0, OpenSSL 3.6.4.

Executed the unchanged extracted HTTP server separately for each curl request: /healthz 200, /missing 404, POST /orders 202, expected bodies, curl exit 0 and server exit 0. Temporary files removed. No public exposure, TLS, proxy or durable order processing tested.

`python3 tools/check_book.py --chapters 21-25` passed: 14 shell syntax blocks, 3 Python syntax blocks and 1,294 global local links; no errors or warnings. This does not prove external-link longevity or Linux baseline runtime equivalence. No Ubuntu/Fedora/RHEL VM matrix or production recovery was tested. Optional low findings above do not block approval.

Verdict: approved
