# Independent review — Chapter 22

Reviewer: review_volume3_021_025 (independent reviewer)
Date: 2026-10-03
Reviewed body SHA256: 4ac7e02dea1446c0802e9dce18c7479d64115d94b8a5f913571bd18a53a10a3c

## Scope and findings

Read AI_AUTHORING_GUIDE.md, PROGRESS.md, BASELINE.md, manifest record, skeleton brief, manuscript, chapter summary and prerequisite summary/manuscript context.

Inspected TCP stream framing, UDP delivery caveats, socket states and queue context, dual-stack uncertainty, timeout stage separation, ss flags/filters, loopback scope, capture filter/count and GNU timeout behavior. Recovery distinguishes rejecting endpoint from process ownership and durable outcomes. Exercises, guidance and takeaways meet the brief. No material finding.

## Dated primary-source evidence

Inspected on 2026-10-03:

- [RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html).
- [Python socket API](https://docs.python.org/3/library/socket.html).
- [ss manual](https://man7.org/linux/man-pages/man8/ss.8.html).

## Verification and limits

Measured tools: Python 3.14.7, curl 8.22.0, OpenSSL 3.6.4.

Independently executed extracted unchanged TCP and UDP server/client programs in temporary files. Both clients returned response: ack with exit 0; both one-exchange servers exited 0. Sandbox socket creation first returned PermissionError; approved execution outside that restriction permitted only disposable loopback tests. No packet capture or remote connectivity tested.

`python3 tools/check_book.py --chapters 21-25` passed: 14 shell syntax blocks, 3 Python syntax blocks and 1,294 global local links; no errors or warnings. This does not prove external-link longevity or Linux baseline runtime equivalence. No Ubuntu/Fedora/RHEL VM matrix or production recovery was tested. Optional low findings above do not block approval.

Verdict: approved
