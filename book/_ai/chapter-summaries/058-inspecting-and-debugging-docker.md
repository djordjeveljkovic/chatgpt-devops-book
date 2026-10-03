# Chapter 58 continuation

Status: complete; independently reviewed and approved.

## Written material
Compose logs/ps and targeted inspect/exec/stats/events; host process, journal and storage correlation; rootful/remote/rootless/Desktop execution boundaries; controlled crashing-container lab with exit-state diagnosis, recovery and scoped cleanup; exercises and answers.

## Concepts and terminology
Logging driver, container state/exit code/OOM flag/restart count, live `exec`, resource sample, bounded event buffer, daemon context, host PID, recovery evidence.

## Examples and cross-references
Uses Chapter 57 Compose service `api` and named Alpine crash lab. Compose commands run from same project directory/context; examples state one API instance. Host `df`/journal require local rootful Engine. Event history bounded by `--until`; live stream can be stopped with Ctrl-C. Links to chapters 16, 57, 60 and 141.

## Open threads
No unresolved review findings. No Docker runtime test or actual diagnostic samples.

## Exact next section
None. Continue with Chapter 59.

## Verification
Docker logs/inspect/exec/stats/events, logging driver and state docs inspected 2026-10-03. Independent reviewer `review_055` approved body SHA256 `43a63decedd274b5311f9b580644e3879e6b4aa366398c7604b2f852094c6d44`; ten shell syntax blocks and local links passed. No runtime checks.
