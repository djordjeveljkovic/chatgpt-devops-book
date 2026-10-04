# Chapter 114 continuation

Status: complete

## Written material
CSI driver boundaries and capabilities; PV/PVC/StorageClass lifecycle; access modes, topology and delayed binding; reclaim, performance, capacity and expansion; snapshot consistency and restore; DispatchDesk storage incident; read-only diagnostics and exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
CSI, PV, PVC, StorageClass, access mode, topology, WaitForFirstConsumer, reclaim policy, VolumeSnapshot, VolumeSnapshotContent, VolumeSnapshotClass.

## Examples and cross-references
DispatchDesk database volume attachment and incomplete snapshot recovery scenario; read-only `kubectl` queries; links to Chapters 120 and 186.

## Open threads
Verify current driver-specific access, topology, expansion and snapshot claims during review; no cluster or backend test performed.

## Verification
Scoped static checker and local links pending; official Kubernetes storage and CSI references inspected 2026-10-04.
