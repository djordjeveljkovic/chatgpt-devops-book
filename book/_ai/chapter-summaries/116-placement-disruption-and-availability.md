# Chapter 116 continuation

Status: complete

## Written material
Failure domains and scheduler placement; affinity and topology spread; readiness/liveness/startup probes; PDB scope and limits; rollout and maintenance capacity; DispatchDesk drain stall; read-only diagnostics and exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Failure domain, node and Pod affinity, topology spread, taint/toleration, readiness, PDB, Eviction API, allowed disruptions, rollout surge/unavailability.

## Examples and cross-references
DispatchDesk zone-capacity and node-image drain scenario; read-only placement and PDB inspection; links to Chapters 114 and 117.

## Open threads
Validate workload-specific probes, topology and PDB choices in a real cluster before adoption; no cluster testing performed.

## Verification
Scoped checker and local-link validation pending; official Kubernetes placement and disruption docs inspected 2026-10-04.
