---
book: The Complete DevOps Engineering Book
volume: 5
volume_title: "Container Internals and OCI"
chapter: 50
title: "The Container Contract"
slug: the-container-contract
status: complete
summary: ../../_ai/chapter-summaries/050-the-container-contract.md
---

# Chapter 50 — The Container Contract

A container image is a packaged filesystem and execution description. A container is one execution of that image with a process, environment, resource limits, network attachments, mounts and a writable layer. The distinction matters operationally: replacing a container discards its writable layer, while data in a mounted volume can survive. [Chapter 49](049-registries-and-image-distribution.md) explained how an image reaches a host; this chapter describes the application contract that lets an orchestrator or operator replace an instance without losing service behavior or durable data.

DispatchDesk is a small fictional ticket service. We will treat its process as an HTTP server that reads configuration at startup, writes request and diagnostic logs to standard output and standard error, handles termination signals, and stores durable records in PostgreSQL. Its local cache may be Redis, but losing that cache does not lose a ticket. These choices define behavior independently of Docker, Podman or a later scheduler.

## Signals, logs and configuration

The container runtime starts a process and eventually asks it to stop. In a Linux container, the process selected as PID 1 has special responsibilities: it must receive termination signals and reap child processes. If a shell script becomes PID 1 and starts an application without replacing itself, the signal can stop at the shell while the child continues. The runtime waits for its grace period and may then forcefully kill the process. A clean application should respond to `SIGTERM`, stop accepting new work, finish or cancel in-flight requests within a bounded interval, close dependencies and exit. A supervisor or init process can help when an image intentionally runs multiple processes, but adding one does not remove the need for a defined shutdown policy.

Use `exec` in a simple shell entrypoint so the application replaces the shell and receives the signal directly. This generic wrapper runs the command supplied by the image's `CMD` or the container operator; it does not assume a DispatchDesk binary exists:

```sh
#!/bin/sh
set -eu

if [ "$#" -eq 0 ]; then
  echo "no application command supplied" >&2
  exit 64
fi

exec "$@"
```

The script rejects an empty command and then replaces itself with the configured process. Application settings and signal behavior remain the application's responsibility. A container stop timeout should be longer than the application's normal shutdown bound and shorter than the deployment system's rollout deadline. If a request can run for minutes, define what happens at the deadline: finish, return a retryable failure, or persist work to a queue before acknowledging it. [Chapter 107](../11-kubernetes-foundations/107-probes-and-graceful-termination.md) discusses Kubernetes probes and termination behavior.

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

This table is more than an architecture diagram. It identifies which failure loses information and which team restores it. The Redis cache can be dropped during a migration if the application can regenerate entries. PostgreSQL cannot be treated the same way; its backup cadence, restore point objective and tested recovery procedure must match the business requirement. [Chapters 36](../04-vps-and-server-operations/036-database-and-cache-operations-on-one-host.md) and [37](../04-vps-and-server-operations/037-server-backups-and-restore.md) discuss those data services and their backups.

Use mounts deliberately. A read-only bind mount is appropriate for configuration that the process should consume but never rewrite. A named volume is appropriate for an engine-managed data directory when the engine is the chosen storage owner. A host path gives an operator direct filesystem control, but it couples deployment to host layout, ownership, labels and backup policy. On Fedora/RHEL, SELinux labels are a separate access control from Unix owner/group/mode; on Ubuntu, an AppArmor profile can restrict operations even when DAC checks pass. Check the effective container identity, numeric host ownership, mount source and target, and the relevant policy denial before changing permissions. [Chapter 45](045-container-filesystems-and-storage.md) explains container storage boundaries, [Chapter 47](047-rootless-containers-and-user-mapping.md) covers UID/GID mappings, and [Chapter 48](048-capabilities-and-security-boundaries.md) covers container security boundaries.

Every persisted file has an ownership and permission model. A non-root process may be unable to write a newly mounted directory, or a container UID may map to a different host identity in rootless mode. Decide which UID and group owns files, provision that identity and verify access in the target engine. Do not respond by running the application as root or opening the directory to every user without considering the threat. Mount only paths the container requires, and make configuration and code mounts read-only wherever the application does not need to write.

## Observe a graceful stop and a forced deadline

This small Python process demonstrates direct signal handling and a bounded shutdown delay. It has no database, HTTP listener or customer data. Run the exercise on a disposable Linux Docker host, as an operator authorized to use the selected local daemon, from an empty lab directory. Save these files there.

`entrypoint.sh`:

```sh
#!/bin/sh
set -eu

if [ "$#" -eq 0 ]; then
  echo "no application command supplied" >&2
  exit 64
fi

exec "$@"
```

`app.py`:

```python
import os
import signal
import time


shutdown_delay = float(os.environ.get("SHUTDOWN_DELAY_SECONDS", "1.5"))


def handle_stop(signum, _frame):
    print(f"received {signal.Signals(signum).name}; draining", flush=True)
    time.sleep(shutdown_delay)
    print("shutdown complete", flush=True)
    raise SystemExit(0)


signal.signal(signal.SIGTERM, handle_stop)
print(f"started as pid {os.getpid()}", flush=True)
while True:
    time.sleep(60)
```

`Dockerfile`:

```dockerfile
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
COPY entrypoint.sh /entrypoint.sh
COPY app.py /app.py
RUN chmod 0555 /entrypoint.sh
STOPSIGNAL SIGTERM
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "/app.py"]
```

The exec-form entrypoint starts the wrapper as the initial process, then `exec` replaces it with Python. Confirm the files are in the current build context and build a learning image:

```bash
docker build --tag dispatchdesk-contract-lab:dev .
```

The Dockerfile uses the current Python 3.12 slim tag as a mutable example. A production image should use an approved base image and record its digest, as discussed in [Chapter 44](044-images-layers-and-content-identity.md). Build requires access to the selected local daemon and registry if the base is not cached. No port or persistent volume is created. The app handles `SIGTERM` by recording the signal, waiting to represent in-flight work, and exiting zero; it does not demonstrate real request draining.

Start a container with a five-second stop timeout and a 1.5-second synthetic drain. The detached CLI can return before the process installs its signal handler, so the bounded helper waits for the application's `started as pid 1` log line before sending a stop signal. This lab assumes the daemon's logging driver makes recent logs readable through `docker logs`.

```bash
wait_for_started() {
  _lab_container_name=$1
  _lab_start_attempt=0
  while [ "$_lab_start_attempt" -lt 20 ]; do
    if docker logs "$_lab_container_name" 2>&1 | grep -q 'started as pid 1'; then
      return 0
    fi
    _lab_running=$(docker inspect --format '{{.State.Running}}' \
      "$_lab_container_name" 2>/dev/null) || _lab_running=false
    if [ "$_lab_running" != true ]; then
      break
    fi
    _lab_start_attempt=$((_lab_start_attempt + 1))
    sleep 0.25
  done
  docker inspect "$_lab_container_name" \
    --format 'status={{.State.Status}} exit={{.State.ExitCode}} error={{.State.Error}}' || true
  docker logs --timestamps "$_lab_container_name" || true
  return 1
}

docker run --detach --name dispatchdesk-stop-ok \
  --stop-timeout 5 \
  --env SHUTDOWN_DELAY_SECONDS=1.5 \
  dispatchdesk-contract-lab:dev
wait_for_started dispatchdesk-stop-ok || exit 1
docker exec dispatchdesk-stop-ok python -c \
  'print(open("/proc/1/cmdline", "rb").read().decode().replace(chr(0), " "))'
time docker stop --timeout 5 dispatchdesk-stop-ok
docker inspect dispatchdesk-stop-ok \
  --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}'
docker logs --timestamps dispatchdesk-stop-ok
docker run --detach --name dispatchdesk-stop-too-short \
  --stop-timeout 1 \
  --env SHUTDOWN_DELAY_SECONDS=4 \
  dispatchdesk-contract-lab:dev
wait_for_started dispatchdesk-stop-too-short || exit 1
time docker stop --timeout 1 dispatchdesk-stop-too-short
docker inspect dispatchdesk-stop-too-short \
  --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}}'
docker logs --timestamps dispatchdesk-stop-too-short
```

The first run starts a background container and the helper polls for up to five seconds. If it cannot see the startup marker or the container stops, it prints state and logs, then the script exits before signaling it. Once ready, `docker exec` reads PID 1's command line and should show Python as the final process, not a shell wrapper. `docker stop --timeout 5` sends the container's configured stop signal, `SIGTERM` here, and waits up to five seconds. The shell's `time` reports what this disposable run took on the target host; do not treat it as a benchmark. Expected evidence is an exited state with code 0, `oom=false`, and logs ending in `shutdown complete`.

The second run uses the same helper to eliminate the startup race, then deliberately sets a deadline shorter than the four-second synthetic drain. The process begins draining but cannot finish inside the one-second grace period, so the daemon sends `SIGKILL`. The expected exit code is 137 in this controlled case, and the completion message should be absent. An exit code of 137 alone is not proof of a stop-timeout cause in an incident: a manual kill or daemon disruption can produce the same code. Correlate stop events, timestamps, configured timeout and OOM state. Docker's default stop timeout for Linux containers is ten seconds when neither the container nor daemon supplies another value, but an application's contract should set a bound that fits its work and deployment deadline. If normal production work often exceeds the deadline, change the application shutdown bound or deployment policy based on measured in-flight work; increasing the timeout without regard to rollout deadlines can merely delay a stuck deployment.

This lab demonstrates what happens when a known process receives a signal and a known deadline. It does not prove every image uses `SIGTERM`: an image can declare a different `STOPSIGNAL`, and an operator can override it with `--stop-signal`. Inspect `.Config.StopSignal` and the deployment command before assuming the signal. A shell wrapper that omits `exec` may remain PID 1 and fail to forward signals to its child; an init process can reap children, but the application's shutdown semantics still need to be tested. Linux gives PID 1 special signal behavior, so a process must handle the termination signal it is expected to receive.

When the evidence is recorded, remove only these stopped lab containers and optionally the local image:

```bash
docker rm dispatchdesk-stop-ok dispatchdesk-stop-too-short
docker image rm dispatchdesk-contract-lab:dev
```

Removal discards each container's metadata and writable layer. The image removal fails harmlessly if another local object still references it; do not force deletion of shared images just to clean this exercise.

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

1. In the shell entrypoint above, what behavior changes if `exec` is removed? How does the graceful-stop lab establish the actual PID 1 process, signal received and deadline outcome?
2. Classify a generated thumbnail, a ticket record, an access log and a compiled binary by owner and recovery source.
3. A new container starts but cannot write to its mounted upload directory. List the UID/GID, rootless mapping, mount source/target, Unix mode, SELinux or AppArmor evidence you would inspect before changing access controls.
4. Why can a failed database readiness probe justify removing an instance from traffic without restarting it?
5. Design a rolling schema change that remains compatible while two application versions run concurrently.

### Answer guidance

1. Without `exec`, the shell can remain PID 1 and may not forward the runtime's signal to its child. Inspect `/proc/1/cmdline`, capture logs and state, then compare a stop timeout longer than the app's normal measured shutdown with one deliberately too short. A 137 exit alone does not identify the cause; correlate events, OOM state and timing.
2. A thumbnail is derived and can be rebuilt from the source image; a ticket record is authoritative PostgreSQL data backed up through a tested database procedure; access logs belong to a managed logging system with a retention policy; compiled binaries belong to the reviewed image digest/build record.
3. Check the process's numeric UID/GID, the volume or bind source, target path, mount mode, directory owner/group/mode, and any rootless user mapping. Then check Fedora/RHEL SELinux labels and AVC denials or Ubuntu AppArmor profile denials separately. Correct only the narrow missing ownership or policy rule; do not disable enforcement or use world-writable permissions as a shortcut.
4. Readiness decides whether an instance should receive new traffic. Restarting a healthy process that cannot reach an unavailable database does not make the dependency available; a restart loop can add reconnect load while the database remains down.
5. Expand/backfill/contract: add an optional compatible column or representation, deploy code that can read old and new formats and writes the new form, backfill existing rows, verify all readers/writers have moved, then remove the old schema/behavior in a later release.

## Sources and verification

The [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec), Docker's [container lifecycle](https://docs.docker.com/engine/containers/run/), [`docker stop`](https://docs.docker.com/reference/cli/docker/container/stop/) and [logging](https://docs.docker.com/engine/logging/) documentation were inspected on 2026-10-03. The linked systemd [`TimeoutStopSec`](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) and [`KillSignal`](https://www.freedesktop.org/software/systemd/man/latest/systemd.kill.html) pages are separate directives and are not used as evidence for Docker behavior; the documentation host returned HTTP 403 during this authoring pass. Canonical storage/identity/security chapters were also consulted. The generic entrypoint and Python lab files are complete examples but were reviewed statically, not built or run. Runtime signal handling, health endpoints, mount behavior and logging integrations depend on the application and configuration. The lab uses a synthetic shutdown delay and does not claim a real service drain measurement.
