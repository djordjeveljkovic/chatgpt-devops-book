# Chapter 28 continuation

Status: draft

## Written material
Source/destination NAT and translation state; forward/reverse proxy distinctions; source attribution through translation; conntrack and source-port capacity observation; measured exhaustion diagnosis and recovery; exercises.

## Exact next section
Independent technical and editorial review.

## Concepts and terminology
SNAT, DNAT, masquerade, original/translated tuple, stateful connection tracking, forward/reverse proxy, conntrack entry and insert failure, ephemeral source port, flow churn.

## Examples and cross-references
Read-only conntrack, sysctl/proc and socket observations. No rule mutation or conntrack flush. Links to Chapters 22, 27 and 29; RFC 7239 for forwarded HTTP metadata.

## Open threads
Independent review; `conntrack` utility absent, no NAT topology or kernel state changed. Verify exact package name for each target distribution and tool output semantics.

## Verification
Inspected netfilter nftables NAT guide, conntrack-tools manual, Linux kernel conntrack sysctl documentation and RFC 7239 on 2026-10-02. `conntrack -V` confirmed the utility is not installed; no live conntrack counter is asserted. Source-port and tracking commands are observational only.
