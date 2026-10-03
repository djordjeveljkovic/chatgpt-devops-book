# Chapter 30 continuation

Status: draft

## Written material
Request-scoped evidence capture; local, route, resolver, socket and application observations; bounded tracepath/mtr/tcpdump usage; probe-vs-data-path and latency interpretation; end-to-end fictional incident; verified recovery and incident improvement; exercises.

## Exact next section
Independent technical and editorial review.

## Concepts and terminology
Observation point, network namespace, system resolver, stage timing, route lookup, ICMP probe, packet capture drops, tail latency, correlation/request ID, evidence limits.

## Examples and cross-references
Read-only Linux commands using documented/fictitious endpoints; network probes and tcpdump commands require authorization and can generate packets. Chapter 30 is explicitly illustrative, with no measured results claimed. Links across networking chapters and Volume 4.

## Open threads
Independent review; no remote probes or production capture run. `mtr` is not installed; tracepath syntax/probe not executed. Capture flags checked against tcpdump manual, but actual packet visibility depends on the host and permission.

## Verification
Inspected tracepath and tcpdump manuals, the MTR upstream manual and RFC 2330 on measurement limits on 2026-10-02. Environment has tcpdump 4.99.7 and tracepath; mtr is absent. No command targeting an external network was run. Chapter's inline HAProxy configuration remains unparsed.
