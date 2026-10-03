# Independent review — Chapter 23

Reviewer: review_volume3_021_025 (independent reviewer)
Date: 2026-10-03
Reviewed body SHA256: 5621e0b3286ad10c5a4bf8b70dbd3dba1fa9236c145d5501372a028aa6815573

## Scope and findings

Read AI_AUTHORING_GUIDE.md, PROGRESS.md, BASELINE.md, manifest record, skeleton brief, manuscript, chapter summary and prerequisite summary/manuscript context.

Inspected stub/NSS versus dig boundaries, authority/delegation/glue, record semantics, positive and negative cache behavior, TTL cutover timing, DNSSEC limitations, split-horizon and per-link resolver differences, documentation addresses and reversible service overlap. Required assessment guidance is present. No material finding.

- Low, “Inspect the actual resolver path”, before the first dig block: add package prerequisites (Ubuntu dnsutils/bind9-dnsutils; Fedora/RHEL bind-utils) for readers whose hosts lack dig. This is a usability improvement; it does not invalidate DNS reasoning or the commands.

## Dated primary-source evidence

Inspected on 2026-10-03:

- [BIND dig reference](https://bind9.readthedocs.io/en/latest/manpages.html#dig-dns-lookup-utility).
- [RFC 2308](https://www.rfc-editor.org/rfc/rfc2308.html).

## Verification and limits

Documentation and static review only for resolver queries. No external DNS queries, record changes, cache flushes or VPN changes performed. Application-specific caches and distributions were not exercised.

`python3 tools/check_book.py --chapters 21-25` passed: 14 shell syntax blocks, 3 Python syntax blocks and 1,294 global local links; no errors or warnings. This does not prove external-link longevity or Linux baseline runtime equivalence. No Ubuntu/Fedora/RHEL VM matrix or production recovery was tested. Optional low findings above do not block approval.

Verdict: approved
