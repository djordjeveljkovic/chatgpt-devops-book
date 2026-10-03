# Chapter 30 continuation

Status: complete

## Written material
Request-scoped evidence capture; local, route, resolver, socket and application observations; bounded tracepath/mtr/tcpdump usage; probe-vs-data-path and latency interpretation; end-to-end fictional incident; verified recovery and incident improvement; exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Observation point, network namespace, system resolver, stage timing, route lookup, ICMP probe, packet capture drops, tail latency, correlation/request ID, evidence limits.

## Examples and cross-references
Read-only Linux commands using documented/fictitious endpoints; network probes and tcpdump commands require authorization and can generate packets. Chapter 30 is explicitly illustrative, with no measured results claimed. Links across networking chapters and Volume 4.

## Open threads
Independent review found no material issue. Optional usability improvement: state distribution-specific install prerequisites or a canonical reference for `tracepath`, `mtr` and `tcpdump`. No remote probes or production capture run; `mtr` is not installed and tracepath was not run. Capture flags checked against tcpdump manual, but packet visibility depends on host and permissions.

## Verification
Inspected tracepath and tcpdump manuals, the MTR upstream manual and RFC 2330 on measurement limits on 2026-10-02. Environment has tcpdump 4.99.7 and tracepath; mtr is absent. No command targeting an external network was run. Chapter's inline HAProxy configuration remains unparsed.
