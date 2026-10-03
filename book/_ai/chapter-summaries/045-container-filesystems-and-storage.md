# Chapter 45 continuation

Status: draft; independent review pending.

## Written material
Image lower layers and writable layer; OverlayFS copy-up; mounts lifecycle comparison; durable database ownership; volume inspection/capacity; migration and deletion cautions; exercises.

## Concepts and terminology
OverlayFS, lower/upper layer, whiteout, copy-on-write, named volume, bind mount, tmpfs, network filesystem, containerd snapshotter, storage root.

## Examples and cross-references
Read-only Docker inspect templates and host findmnt/df commands for an authorized test container. Explicitly covers Docker Engine 29 containerd image-store default for fresh installs; version-sensitive. Links chapters 36–37, 41, 44, 46, 51, 56.

## Open threads
No engine inspected or storage modified; engine storage details vary. Database backup/restore remains database-specific. Independent review pending.

## Exact next section
None. Begin Chapter 47, then request independent review before claiming completion.

## Verification
Book shell syntax and local links checked. Kernel OverlayFS, Docker storage driver/volume/current storage docs and OCI specs inspected 2026-10-02.
