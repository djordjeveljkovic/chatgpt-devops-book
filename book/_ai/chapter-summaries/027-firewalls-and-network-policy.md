# Chapter 27 continuation

Status: complete

## Written material
Host/network policy layers; state tracking and rule placement; inspection through nftables, UFW and firewalld; manager-specific runtime/permanent workflows; safe source-scoped SSH access change and rollback; path diagnosis; exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Stateful/stateless filter, hook, chain/rule ordering, zone, source prefix, runtime and permanent state, host/provider policy, conntrack.

## Examples and cross-references
Inspection commands are read-only. UFW and firewalld change commands are explicitly marked as live policy changes requiring host-specific validation and recovery path. Management subnet is fictional. Links to Chapters 22, 26 and 28.

## Open threads
Independent review; no host firewall state changed. `ufw` unavailable in environment, and nftables/firewalld live policy not altered. Review distro-specific examples and remote rollback sequence.

## Verification
Inspected Ubuntu Server firewall guide, firewalld `firewall-cmd` and runtime/permanent docs and nftables project guide on 2026-10-02. `ufw --version` confirmed the utility is absent. No policy changes were run. Examples retain the distinction between runtime and permanent state.
