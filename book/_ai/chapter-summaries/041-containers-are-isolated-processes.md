# Chapter 41 continuation

Status: draft; independent review pending.

## Written material
Container process model; OCI/runtime/engine/orchestrator layers; runtime assembly and PID 1 lifecycle; isolation limitations; process namespace inspection; DispatchDesk consequences and exercises.

## Concepts and terminology
Container vs VM, OCI image/runtime specs, foreground process, writable layer, PID 1, namespace, cgroup, mount, capability, published port, durable external state.

## Examples and cross-references
Read-only /proc namespace and cgroup inspection of current shell. Later inspect known test container. DispatchDesk state remains durable/external. Links chapters 10, 42–43, 45, 48, 55 and 56.

## Open threads
No container runtime used or runtime isolation claim tested. Runtime and host configurations differ. Independent review pending.

## Exact next section
None. Begin Chapter 42, then request independent review before claiming completion.

## Verification
Shell syntax and local links checked. OCI Runtime Spec and Linux config pages inspected 2026-10-02.
