# Independent review — Chapter 21

Reviewer: review_volume3_021_025 (independent reviewer)
Date: 2026-10-03
Reviewed body SHA256: b0c282cfd8531aa3ff1780dfad99e11a5c785887b6696289b7c34bdcc732d58d

## Scope and findings

Read AI_AUTHORING_GUIDE.md, PROGRESS.md, BASELINE.md, manifest record, skeleton brief, manuscript, chapter summary and prerequisite summary/manuscript context.

Inspected address versus interface semantics, CIDR boundaries, longest-prefix selection with policy-table qualification, off-link neighbor selection, return-path/NAT caveats, MTU and IPv6 control traffic, package names, Netplan renderer/cloud ownership and NetworkManager profile rollback. All requested brief sections, prerequisite link, exercises with answer guidance and takeaways are present. No material finding.

## Dated primary-source evidence

Inspected on 2026-10-03:

- [ip-route manual](https://man7.org/linux/man-pages/man8/ip-route.8.html).
- [Netplan examples](https://netplan.readthedocs.io/en/stable/examples/).
- [nmcli reference](https://networkmanager.dev/docs/api/latest/nmcli.html).

## Verification and limits

Measured tools: Python 3.14.7, curl 8.22.0, OpenSSL 3.6.4.

Executed the exact ipaddress program: membership True/True/False and two 128-address /25 subnets. Compiled all Python examples. No interface, route, Netplan or NetworkManager state changed.

`python3 tools/check_book.py --chapters 21-25` passed: 14 shell syntax blocks, 3 Python syntax blocks and 1,294 global local links; no errors or warnings. This does not prove external-link longevity or Linux baseline runtime equivalence. No Ubuntu/Fedora/RHEL VM matrix or production recovery was tested. Optional low findings above do not block approval.

Verdict: approved
