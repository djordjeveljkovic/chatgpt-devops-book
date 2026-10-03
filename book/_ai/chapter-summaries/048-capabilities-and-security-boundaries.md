# Chapter 48 continuation

Status: draft; independent review pending.

## Written material
Linux capability boundaries; restrictive Docker launch template; read-only/root/volume trade-offs; seccomp and LSM layers; engine socket authority; denial diagnosis and exercises.

## Concepts and terminology
Capability sets, CAP_NET_BIND_SERVICE, CAP_SYS_ADMIN, seccomp allowlist, no-new-privileges, read-only rootfs, AppArmor, SELinux, engine socket.

## Examples and cross-references
Illustrative `docker run` template with `--user`, all caps dropped, no-new-privileges and bounded tmpfs; image placeholder, not executed. Links chapters 14, 32, 41–47 and 49.

## Open threads
Actual application writable paths and capability needs unverified; Docker defaults version-specific. Independent review pending.

## Exact next section
None. Begin Chapter 50, then request independent review before claiming completion.

## Verification
Shell syntax and local links checked. Linux capabilities, kernel seccomp, Docker seccomp/security primary documentation inspected 2026-10-02.
