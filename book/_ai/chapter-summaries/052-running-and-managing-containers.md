# Chapter 52 continuation

Status: draft; independent review pending.

## Written material
Run/create/start/stop/remove lifecycle; isolated HTTP example, inspection and diagnostics; names, port publication and restart policy; scoped cleanup and exercises.

## Concepts and terminology
Container lifecycle, host/container port mapping, loopback binding, restart policy, writable layer and image cache distinction.

## Examples and cross-references
Nginx learning container published only on test host loopback at port 18080. Commands are reader-run, not executed. Links chapters 49 and 50.

## Open threads
No local Docker daemon; network and firewall behavior depends on host configuration. `nginx:alpine` is a mutable learning tag only. Independent review pending.

## Exact next section
None. Begin Chapter 53 on Dockerfiles and build contexts.

## Verification
Docker official run/restart/inspect/logs/firewall docs inspected 2026-10-02. Book syntax and link checks pending.
