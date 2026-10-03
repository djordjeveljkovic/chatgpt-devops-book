# Chapter 56 continuation

Status: complete; independent review approved.

## Written material
Volumes versus bind mounts; daemon host/context; volume copy/obscuring behavior; ownership and user mapping; SELinux `:Z` and `:z` bind labeling; marker-based persistence, archive, isolated restore and content verification; database backup consistency; replacement failure diagnosis; exercises and answer guidance.

## Concepts and terminology
Named and anonymous volumes, bind mount, daemon host, container writable layer, `volume-nocopy`, UID/GID mapping, SELinux labels, logical database dump, base backup, WAL archiving, application-consistent recovery.

## Examples and cross-references
Named-volume lab seeds marker, removes/replaces container, reads marker, archives to host bind mount, restores into a fresh separate volume and compares contents. Includes SELinux variants on dedicated paths. Links to chapters 36, 37, 45, 55 and 57.

## Open threads
No material review findings. No Docker/database runtime test; tar archive is explicitly not a PostgreSQL backup.

## Exact next section
None. Continue with Chapter 57.

## Verification
Docker storage/volume/bind mount/prune and PostgreSQL 18 backup docs inspected 2026-10-03. Full book checker passed, and reviewer reran nine shell blocks and links. Independent reviewer `review_054` approved body SHA256 `2cde41b90a0d80958e6d9a7f5a36e6eade187289cca197d1fa5f2688c513588c`; Docker/database/archive operations were not executed.
