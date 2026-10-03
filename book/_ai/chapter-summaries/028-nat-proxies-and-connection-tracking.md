# Chapter 28 continuation

Status: complete

## Written material
Source/destination NAT and translation state; forward/reverse proxy distinctions; source attribution through translation; conntrack and source-port capacity observation; measured exhaustion diagnosis and recovery; exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
SNAT, DNAT, masquerade, original/translated tuple, stateful connection tracking, forward/reverse proxy, conntrack entry and insert failure, ephemeral source port, flow churn.

## Examples and cross-references
Read-only conntrack, sysctl/proc and socket observations. No rule mutation or conntrack flush. Links to Chapters 22, 27 and 29; RFC 7239 for forwarded HTTP metadata.

## Open threads
Independent review found no material issue. Optional usability improvement: state distribution package names (`conntrack` on Ubuntu; `conntrack-tools` on Fedora, while preserving RHEL release/repository caveats). The utility is absent, and no NAT topology or kernel state changed.

## Verification
Inspected netfilter nftables NAT guide, conntrack-tools manual, Linux kernel conntrack sysctl documentation and RFC 7239 on 2026-10-02. `conntrack -V` confirmed the utility is not installed; no live conntrack counter is asserted. Source-port and tracking commands are observational only.
