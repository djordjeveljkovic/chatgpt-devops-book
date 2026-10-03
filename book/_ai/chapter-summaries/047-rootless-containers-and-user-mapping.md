# Chapter 47 continuation

Status: draft; independent review pending.

## Written material
Rootless vs rootful/userns-remap distinctions; subordinate UID/GID maps; host permissions and bind mounts; rootless storage/network/systemd constraints; validation checklist and exercises.

## Concepts and terminology
User namespace, UID/GID map, subordinate ID ranges, rootless engine, userns-remap, rootless storage/network, user systemd manager/linger.

## Examples and cross-references
Read-only `id` and `/proc/self/{uid,gid}_map`. Illustrative mapping numbers; no subuid ranges changed. Links chapters 42–46 and 48.

## Open threads
Kernel, filesystem, network backend and engine-version support vary. No rootless engine run. Independent review pending.

## Exact next section
None. Begin Chapter 50, then request independent review before claiming completion.

## Verification
Shell syntax and local links checked. Linux user namespace, Docker rootless/remap and Podman docs inspected 2026-10-02.
