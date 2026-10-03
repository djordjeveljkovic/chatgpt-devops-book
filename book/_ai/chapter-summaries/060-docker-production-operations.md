# Chapter 60 — Docker Production Operations

Status: complete

## Written material
Daemon/host capacity and journal checks, including separate Engine 29+ containerd storage roots; rootful Linux daemon log-rotation strategy with `dockerd --validate`, startup-flag and per-container checks, staged config rollout and rollback; disk inventory and prune impact; health checks, resource limits, swap caveat and restart behavior; production deployment review matrix; patch failure scenario; exercises, answer guidance and takeaways.

## Concepts and terminology
Docker daemon host/context, `DockerRootDir`, containerd image store/root, logging driver and per-container override, log rotation, systemd maintenance window, disk/inode pressure, health state, hard memory/CPU/PID limits and swap, restart policy, prune scope and rollback digest.

## Examples and cross-references
Read-only `docker info`, `docker system df`, host `df`/journal checks for Docker and separate containerd roots; illustrative `daemon.json` using local logs; daemon-file validation, unit flag inspection, per-container effective log configuration; bounded resource settings and deployment review for DispatchDesk. No Docker host, daemon or service change was performed. Relative links to chapters 45, 51, 56–59 and 141.

## Open threads
Independent reviewer approved body SHA256 `45352d85459b17d802492a780851da0e794cfd995b9b1ef674c9143ce5a2507a`. No Docker daemon, host restart, service deployment, prune, or resource load test was run.

## Exact next section
None. Volume 6, Chapters 51–60, is complete and approved; next resume from the earliest unfinished dependency in `PROGRESS.md`.

## Verification
Docker official daemon configuration/validation, logging configuration/local driver, containerd image-store defaults and paths, resource constraints, restart policy, system disk usage and prune documentation inspected 2026-10-03. Independent review passed eight shell syntax blocks, one JSON parse and 1,294 local links. Full checker passed 220 chapter records, 309 shell, 35 Python, 26 YAML, 2 Go, 12 JSON, 2 JavaScript syntax/parsing checks and 1,294 local links, with no errors or warnings. Static checks do not validate host service impact, log capacity, limit values or recovery behavior.
