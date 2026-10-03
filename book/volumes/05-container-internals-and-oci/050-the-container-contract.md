---
book: The Complete DevOps Engineering Book
volume: 5
volume_title: "Container Internals and OCI"
chapter: 50
title: "The Container Contract"
slug: the-container-contract
status: draft
summary: ../../_ai/chapter-summaries/050-the-container-contract.md
---

# Chapter 50 — The Container Contract

A container image is a packaged filesystem and execution description. A container is one execution of that image with a process, environment, resource limits, network attachments, mounts and a writable layer. The distinction matters operationally: replacing a container discards its writable layer, while data in a mounted volume can survive. Chapter 49 explained how an image reaches a host; this chapter describes the application contract that lets an orchestrator or operator replace an instance without losing service behavior or durable data.

DispatchDesk is a small fictional ticket service. We will treat its process as an HTTP server that reads configuration at startup, writes request and diagnostic logs to standard output and standard error, handles termination signals, and stores durable records in PostgreSQL. Its local cache may be Redis, but losing that cache does not lose a ticket. These choices define behavior independently of Docker, Podman or a later scheduler.

## Signals, logs and configuration

The container runtime starts a process and eventually asks it to stop. In a Linux container, the process selected as PID 1 has special responsibilities: it must receive termination signals and reap child processes. If a shell script becomes PID 1 and starts an application without replacing itself, the signal can stop at the shell while the child continues. The runtime waits for its grace period and may then forcefully kill the process. A clean application should respond to `SIGTERM`, stop accepting new work, finish or cancel in-flight requests within a bounded interval, close dependencies and exit. A supervisor or init process can help when an image intentionally runs multiple processes, but adding one does not remove the need for a defined shutdown policy.

Use `exec` in a simple shell entrypoint so the application replaces the shell and receives the signal directly:

```sh
#!/bin/sh
set -eu

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL is required" >&2
  exit 64
fi

exec /usr/local/bin/dispatchdesk serve --listen "${LISTEN_ADDR:-0.0.0.0:8080}"
```

The script checks a required setting, chooses a default listen address and then uses `exec`. The application still needs to implement graceful termination. A container stop timeout should be longer than the application's normal shutdown bound and shorter than the deployment system's rollout deadline. If a request can run for minutes, define what happens at the deadline: finish, return a retryable failure, or persist work to a queue before acknowledging it. Chapter 74 covers graceful application shutdown in more depth.

Write operational messages to standard output and errors to standard error. The engine can capture these streams and expose them through `docker logs` or an equivalent interface, while a host or platform logging agent forwards them to durable storage. A file written only inside the container's writable layer disappears when that instance is removed and may not be collected at all. If an application needs structured logs, include stable fields such as timestamp, severity, service, environment, request identifier and trace identifier. Do not emit passwords, access tokens, session cookies, private keys or full sensitive request bodies. Logging policy, retention and alerting are platform concerns; the application supplies useful, safe events.

Configuration should enter through an explicit boundary. Non-secret settings such as listen address, feature mode, timeout and dependency endpoint can be environment variables or mounted configuration files. Secret values should come from the platform's secret mechanism, with narrow read access and a rotation process. An environment variable is not secret storage by itself: it can appear in process inspection, crash reports or diagnostic bundles. Avoid baking environment-specific values and credentials into image layers. The same digest should be usable in test and production, with deployment configuration supplying the environment's differences.

Validate configuration at startup and fail clearly before accepting traffic. Silently substituting an unsafe default for a missing database credential turns a deployment error into an ambiguous outage. Conversely, do not require every downstream dependency to be available before a process can start if the service can become ready later. Separate process liveness from readiness: liveness answers whether the process can make progress or should be restarted; readiness answers whether it can safely receive new requests. A transient database interruption may make an instance unready without meaning that restarting it will help.

## Ephemeral execution and durable state

Treat a container's writable layer as disposable. It is useful for temporary files, caches and runtime artifacts, but an operator should be able to remove an instance and start a replacement from the same image and declared configuration. If a process writes the only copy of an uploaded file or database record into that layer, replacement destroys user data. Store durable state in a database, object store, queue or explicitly managed persistent volume. Make backup and restore ownership clear; a persistent disk is not a backup.

A useful boundary for DispatchDesk is:

| Data | Owner | Expected lifetime | Recovery source |
| --- | --- | --- | --- |
| Process memory and temporary request buffers | One process | Until exit | Recompute or retry request |
| Compiled assets and application code | Image digest | Release lifetime | Registry and build records |
| Ticket records | PostgreSQL | Business retention period | Database backup and transaction recovery |
| Search or hot ticket cache | Redis | Until eviction or rebuild | PostgreSQL or cache repopulation |
| Access and audit events | Central logging system | Defined by policy | Replicated log storage |

This table is more than an architecture diagram. It identifies which failure loses information and which team restores it. The Redis cache can be dropped during a migration if the application can regenerate entries. PostgreSQL cannot be treated the same way; its backup cadence, restore point objective and tested recovery procedure must match the business requirement. Chapters 36 and 37 discuss those data services and their backups.

Use mounts deliberately. A read-only bind mount is appropriate for configuration that the process should consume but never rewrite. A named volume is appropriate for an engine-managed data directory when the engine is the chosen storage owner. A host path gives an operator direct filesystem control, but it couples deployment to host layout, ownership, labels and backup policy. On SELinux systems, labeling rules also matter; disabling enforcement to make a mount work removes a protection instead of correcting the mount. Chapter 45 explains container storage boundaries.

Every persisted file has an ownership and permission model. A non-root process may be unable to write a newly mounted directory, or a container UID may map to a different host identity in rootless mode. Decide which UID and group owns files, provision that identity and verify access in the target engine. Do not respond by running the application as root or opening the directory to every user without considering the threat. Mount only paths the container requires, and make configuration and code mounts read-only wherever the application does not need to write.

## Designing an application that restarts cleanly

A replacement is ordinary, not exceptional. It can follow a deployment, node reboot, health failure, resource limit or host maintenance. The application should therefore be safe to start more than once and safe to stop at any time. Avoid local singleton locks as the only protection against duplicate scheduled work. Use a database constraint, lease or queue ownership protocol when two replicas could process the same item. Make migrations compatible with a rolling window where old and new application versions can overlap: add an optional field first, deploy code that understands it, backfill, then remove obsolete behavior in a later release.

Retries need bounded timeouts and jitter. If every new process retries a failed database connection at the same fixed interval, a recovering database can be overwhelmed by a synchronized surge. Back off, cap the delay, add randomization and expose retry counts. Distinguish a retryable network interruption from invalid credentials or an incompatible schema; endless retries do not repair a permanent configuration error. A process should export enough health evidence to let an operator distinguish startup, readiness, dependency and request failures without exposing secret configuration.

Before making an image a deployment unit, answer these questions in a short runtime contract:

1. Which executable starts, and which user runs it?
2. Which signals does it handle, and how long may shutdown take?
3. Which port or socket does it listen on, and what readiness evidence does it provide?
4. Which settings are required, which have safe defaults, and where do secrets come from?
5. Which paths are temporary, and which state is stored outside the container?
6. What happens when each dependency is unavailable during startup and during normal work?
7. What evidence appears in logs and metrics, and how are sensitive values excluded?

These answers let Docker, Podman and later platforms supervise the same application rather than forcing each runtime to invent recovery behavior. The image remains an immutable release artifact; process state is replaceable; data ownership and recovery are explicit.

## Exercises and review questions

1. In the shell entrypoint above, what behavior changes if `exec` is removed? How would you test signal delivery and shutdown time in a disposable environment?
2. Classify a generated thumbnail, a ticket record, an access log and a compiled binary by owner and recovery source.
3. A new container starts but cannot write to its mounted upload directory. List the identity, mount and SELinux facts you would inspect before changing permissions.
4. Why can a failed database readiness probe justify removing an instance from traffic without restarting it?
5. Design a rolling schema change that remains compatible while two application versions run concurrently.

## Sources and verification

The [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec), Docker's [container lifecycle](https://docs.docker.com/engine/containers/run/) and [logging](https://docs.docker.com/engine/logging/) documentation, and systemd's [`KillSignal` and `TimeoutStopSec` documentation](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) were inspected on 2026-10-02. The example entrypoint was reviewed as text but not run against a DispatchDesk binary. Application signal handling, health endpoints, mount behavior and logging integrations depend on the application's implementation and runtime configuration.
