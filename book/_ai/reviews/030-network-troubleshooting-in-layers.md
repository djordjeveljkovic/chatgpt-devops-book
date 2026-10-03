# Independent review — Chapter 30

Reviewer: review_volume3_026_030
Date: 2026-10-03
Reviewed body SHA256: 30d5406647be2a719e942a2e866ff9403e5ba25b7df392d6eb1d78da9a7d3db1

## Findings

No unresolved material finding.

- Low — manuscript “Use tcpdump, tracepath and mtr carefully”: add distribution-specific installation prerequisites or a canonical reference for the newly introduced tools. Their absence is disclosed in the summary and behavior is qualified, so this is a usability improvement rather than a correctness blocker.

## Inspection and evidence

Read the complete manuscript, its brief/manifest/summary, prerequisite Chapter 29, and routing/transport/DNS/HTTP/TLS summaries. Checked execution namespace, NSS versus DNS-tool path, hypothetical route lookup, bounded probes, capture point/filter, ICMP response versus forwarded loss, offloading/asymmetric-path cautions, capture drop evidence, reused-connection timing and request-correlated pool saturation. Recovery repeats the affected operation, examines original load and reconciles ambiguous order outcomes. The fictional incident is explicitly illustrative; exercises and review questions include guidance and a final takeaway.

On 2026-10-03 inspected [tracepath manual](https://man7.org/linux/man-pages/man8/tracepath.8.html), [MTR upstream manual](https://github.com/traviscross/mtr/blob/master/man/mtr.8.in), [tcpdump upstream manual source](https://raw.githubusercontent.com/the-tcpdump-group/tcpdump/master/tcpdump.1.in) and [RFC 2330](https://www.rfc-editor.org/rfc/rfc2330.html). These support flag meanings and measurement limitations. Installed tracepath reports iputils 20250605; tcpdump is 4.99.7/libpcap 1.11.0. Compiled the exact capture filter using `tcpdump -d 'host 10.42.8.21 and tcp port 8080'`: exit 0 and 17 filter instructions, without starting a capture. MTR is unavailable. No outbound probe was executed.

## Verification and limits

Reviewer ran `python tools/check_book.py --chapters 26-30` on 2026-10-03: five manuscript checks, 16 shell syntax blocks, 1,294 global local-link checks; no errors or warnings. This validates syntax and local references, not operational semantics. External documentation retrieval is evidence only for the sources explicitly listed above, not an exhaustive external-link availability check. No host firewall, SSH daemon, remote system, NAT state, provider, load-balancer listener or production traffic was changed. HAProxy, UFW, firewalld, conntrack and MTR are unavailable in this environment; no HAProxy parser run, live SSH/tunnel, connection exhaustion, capture or distro matrix execution is claimed. Manuscripts/summaries/shared state were not edited by this reviewer.

Verdict: approved
