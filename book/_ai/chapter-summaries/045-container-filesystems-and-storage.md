# Chapter 45 continuation

Status: complete

## Written material
Image lower layers and writable layer; OverlayFS copy-up; mounts lifecycle comparison; durable database ownership; volume inspection/capacity; migration and deletion cautions; exercises and answer guidance.

## Concepts and terminology
OverlayFS, lower/upper layer, whiteout, copy-on-write, named volume, bind mount, tmpfs, network filesystem, containerd snapshotter, storage root.

## Examples and cross-references
Read-only Docker inspect templates and host findmnt/df commands for an authorized test container; host filesystem checks must run on the remote daemon host when applicable. Explicitly notes tmpfs pages may be swapped and Docker Engine 29's containerd image-store default for fresh installs is version-sensitive. Links chapters 36–37, 41, 44, 46, 51, 56.

## Open threads
No engine inspected or storage modified; engine storage details vary. Database backup/restore remains database-specific. Fresh independent review approved against the current body hash.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Book shell syntax and local links checked. Kernel OverlayFS, Docker storage driver/volume/current storage docs and OCI specs inspected 2026-10-04.
