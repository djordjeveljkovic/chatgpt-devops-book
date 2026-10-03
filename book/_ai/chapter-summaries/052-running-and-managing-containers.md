# Chapter 52 — Running and Managing Containers

Status: complete

## Written material
Run/create/start/stop/remove lifecycle; local-host HTTP example, inspection and diagnostics; names, port publication and restart policy; scoped cleanup, five exercises and answer guidance.

## Concepts and terminology
Container lifecycle, host/container port mapping, Engine 28.0.0 loopback boundary, restart policy, writable layer, anonymous and named volume cleanup, and image cache distinction.

## Examples and cross-references
Nginx learning container published only on the disposable test host loopback at port 18080. Requires an authorized local Docker Engine context and Engine 28.0.0 or newer for the stated bridge-network localhost isolation. Commands are reader-run, not executed. Relative links to prerequisite Chapter 51 and canonical Chapters 49 and 50.

## Open threads
No local Docker daemon; network and firewall behavior depends on host configuration. `nginx:alpine` is a mutable learning tag only. No runtime test was performed; approval is based on documentation and static checks.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Docker official run/restart/inspect/logs/firewall/port-publishing docs inspected 2026-10-02. Independent review approved body SHA256 `c79c14577452ee7c49122e0441654316f074a17ffb59df66cbf38c7b68036272`. Chapter 51–52 check passed 12 shell syntax checks and 1,274 local links; full check passed 296 shell, 35 Python, 25 YAML, 2 Go, 11 JSON and 2 JavaScript checks plus 1,274 local links, with no errors or warnings. No Docker daemon, container, network or firewall operation was run.
