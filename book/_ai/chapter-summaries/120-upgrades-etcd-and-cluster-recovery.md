# Chapter 120 continuation

Status: complete

## Written material
Version-skew and staged upgrade planning; kubeadm versus managed process; etcd responsibility and sensitive snapshots; quorum repair versus disaster restore; application data recovery; DispatchDesk upgrade incident; read-only checks and rehearsals.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Version skew, etcd quorum, API-state snapshot, disaster restore, CRD/API compatibility, recovery point and recovery time.

## Examples and cross-references
DispatchDesk kubeadm upgrade with a failed etcd member that retains quorum; read-only API baseline; links to Chapters 114 and 186.

## Open threads
Validate exact restore and upgrade procedures against target Kubernetes, etcd and provider versions before execution; no cluster operation performed.

## Verification
Scoped checker and local-link validation pending; official Kubernetes and etcd documentation inspected 2026-10-04.
