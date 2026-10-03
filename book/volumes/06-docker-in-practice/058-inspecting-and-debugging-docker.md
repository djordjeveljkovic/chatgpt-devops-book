---
book: The Complete DevOps Engineering Book
volume: 6
volume_title: "Docker in Practice"
chapter: 58
title: "Inspecting and Debugging Docker"
slug: inspecting-and-debugging-docker
status: complete
summary: ../../_ai/chapter-summaries/058-inspecting-and-debugging-docker.md
---

# Chapter 58 — Inspecting and Debugging Docker

When a container exits, “it is down” names a symptom, not a cause. A useful diagnosis combines application output, container state, process and resource evidence, daemon events, and the host's view. Each command answers a different question. Reading logs cannot show whether a host port was published; `docker inspect` cannot prove a customer request succeeded; CPU statistics do not reveal application intent. Capture evidence before deleting a failed container or changing its configuration.

Assume a Linux Docker Engine on a disposable host and an authorized local daemon context. The commands below inspect Docker and host state; they do not provision infrastructure. With a remote context, Docker commands query the remote daemon, and host commands must run on that daemon's machine to provide correlated evidence. Docker Desktop and rootless Engine add VM or user-service boundaries, so do not treat the CLI workstation's host processes as the container host. See [Chapter 57](057-docker-compose-for-multi-service-applications.md) for Compose services and dependencies. Commands against that Compose project must run from the same project directory and use the same context as `docker compose up`.

## Logs, exec, inspect, stats and events

Container logs normally represent the process's standard output and standard error as exposed by the configured logging driver. Applications that write important diagnostics only to a file inside the container may not show them in `docker logs`. Start with bounded output and timestamps:

```bash
docker compose ps --all api
docker compose logs --timestamps --tail 100 api
```

The Compose `--all` option includes stopped containers, so these commands can find a failed service instance that no longer appears in the default running-only list. `--timestamps` adds Docker's timestamp to each record; `--tail 100` limits output to the latest hundred lines. Logs can contain tokens, personal data, SQL values or internal topology. Inspect and share them under the system's access and retention rules, and redact before attaching them to tickets. If output is empty or unavailable, inspect the logging driver and application logging destination rather than concluding that the process emitted nothing.

Use `docker inspect` to query configuration and state structured by the daemon. The Chapter 57 lab creates one API container per project. If a service has been scaled, select one ID from `docker compose ps --all --quiet api` and inspect that ID rather than passing multiple newline-separated IDs through the variable below. A focused template is easier to read than dumping the complete object:

```bash
api_container=$(docker compose ps --all --quiet api)
if [ -z "$api_container" ]; then
  printf '%s\n' 'No API container exists in this Compose project' >&2
  exit 1
fi
docker inspect "$api_container" \
  --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}} restarts={{.RestartCount}} error={{.State.Error}}'
docker inspect "$api_container" \
  --format 'image={{.Config.Image}} user={{.Config.User}} ports={{json .NetworkSettings.Ports}} mounts={{json .Mounts}}'
```

Replace the name with the actual object. The first template exposes lifecycle evidence: state, last exit code, whether the daemon marked it OOM-killed and restart count. The second displays selected configuration, including image reference, configured user, ports and mounts. These are configured/observed daemon values, not proof that a dependency accepted a request or that the image tag still resolves to the same bytes. Full inspect output can reveal environment variables and mount paths, so avoid indiscriminate publication.

`docker exec` runs a new process inside a running container; it cannot diagnose a container whose PID 1 has exited. Use it for a narrow check, not as an unrecorded repair shell:

```bash
docker compose exec api id
docker compose exec api sh -c 'test -r /app/app.py && printf "%s\n" readable'
```

The executable must exist in the image, and the command inherits the container's user and working directory unless flags override them. Minimal images may have no shell, `ps`, `curl` or package manager. Avoid installing packages into a live container to make the debug command work; that produces a change that disappears on replacement and is absent from the image definition. For a stopped container, inspect its state and logs, then reproduce the problem from its declared image and configuration in a controlled environment.

`docker stats --no-stream` samples resource use without leaving a streaming terminal open. The Chapter 57 lab runs one API container; if the service has been scaled, inspect one selected container ID at a time:

```bash
docker stats --no-stream "$(docker compose ps --quiet api)"
```

CPU, memory, network I/O, block I/O and process counts help test a hypothesis such as a memory limit being reached or traffic stopping. A sample is not a trend, profile or service-level objective. Values are interpreted through host and cgroup behavior, including platform and Engine differences. Compare repeated samples with application latency, request volume and host metrics before attributing a symptom. A stopped container has no live resource sample to read.

Docker events provide a time-ordered stream of object lifecycle changes, including start, die, health status and OOM events. A filtered look-back helps correlate a recent failure:

```bash
events_until=$(date -u +%Y-%m-%dT%H:%M:%SZ)
docker events --since 10m --until "$events_until" \
  --filter "container=$(docker compose ps --all --quiet api)"
```

The timestamp captures the current CLI-host time in UTC and bounds the query; Docker interprets event times relative to the client. Confirm the host clock and context. For a live stream while reproducing a transient failure, omit `--until` in one terminal and press Ctrl-C after capturing the event. Events are a short operational history, not a durable audit log; Docker retains only a limited recent event buffer. Send required evidence to a durable event or observability system. Event absence does not prove that an action did not occur if the time window, context or buffer is wrong.

## Correlate container and host evidence

For a running container, `docker top` displays processes from the daemon's perspective and `docker inspect` exposes the init process identifier. On a rootful Linux Engine, that PID can be correlated with the host process table:

```bash
docker top "$(docker compose ps --quiet api)"
container_pid=$(docker inspect --format '{{.State.Pid}}' "$(docker compose ps --quiet api)")
if [ "$container_pid" -gt 0 ]; then
  ps -o pid,ppid,user,stat,etime,args -p "$container_pid"
fi
```

The variable is assigned from the container's current state; a stopped container normally has PID 0, so the conditional skips host process lookup. The daemon's `docker top` output and host `ps` help correlate process identity, owner and elapsed time, but the host may display namespace-translated IDs and cgroup details differently. With rootless Docker or Docker Desktop, identify the daemon's actual host/VM and the operator's permissions before comparing process IDs.

Check host-level daemon and storage evidence separately. Run this block in a shell on the daemon host itself, with a local context to its rootful Docker Engine; do not pass a remote daemon's data-root path to the CLI workstation's `df`. On Ubuntu and Fedora/RHEL hosts using systemd, these read-only commands show recent daemon messages and the filesystem containing Docker's data root:

```bash
sudo journalctl -u docker.service --since '15 minutes ago' --no-pager
docker info --format '{{.DockerRootDir}}'
df -h "$(docker info --format '{{.DockerRootDir}}')"
```

The first command reads the system service journal and may require administrator privileges; it does not inspect application logs. On Ubuntu and Fedora/RHEL where Docker Engine is installed as a system service, the unit is normally `docker.service`; verify the installed package's service name. Rootless Engine logs belong to the user's service manager, and Docker Desktop logs are in its diagnostic environment. `df` reports filesystem capacity for the daemon's data root; also monitor inodes, image/layer growth, volumes and log storage. A full host filesystem can cause unrelated failures across containers.

Compare the same incident window across layers: request errors and latency from the application; container stdout/stderr and health status; dependency logs; daemon lifecycle events; host CPU, memory, disk and network; then upstream load balancer or firewall evidence. Normalize timestamps and record the daemon context. A successful local `curl` to a published port establishes one path from that machine only. For end-to-end troubleshooting, correlate a request ID or job ID across the API, queue, worker and database rather than matching events only by approximate minute.

## Diagnose and recover a crashing container

Create a controlled failure in a disposable daemon. The shell command deliberately exits with status 42 after writing a diagnostic line to standard error. The container is not launched with `--rm`, so the stopped object remains available for inspection. The command returns nonzero by design; run it separately from automation that uses `set -e`:

```bash
docker run --name dispatchdesk-crash-lab alpine:3.20 \
  sh -c 'printf "%s\n" "configuration file missing" >&2; exit 42'
```

The learning tag may change and is not a production image pin. This command creates a named container, pulls the image if necessary, runs one process and leaves the stopped container record and writable layer. It does not change a named volume or publish a port. A repeated run with the same name fails until the earlier lab container is removed; inspect ownership before cleanup.

Read its logs, structured state and recent lifecycle events:

```bash
docker logs --timestamps dispatchdesk-crash-lab
docker inspect dispatchdesk-crash-lab \
  --format 'status={{.State.Status}} exit={{.State.ExitCode}} oom={{.State.OOMKilled}} error={{.State.Error}}'
events_until=$(date -u +%Y-%m-%dT%H:%M:%SZ)
docker events --since 5m --until "$events_until" \
  --filter container=dispatchdesk-crash-lab
```

Expected evidence is the message `configuration file missing`, an exited status, exit code 42, and a `die` event if it remains in the daemon's recent event window. No output is claimed as measured. In an actual incident, exit status narrows the diagnosis but rarely explains it alone: the application may return its own code, a signal may terminate it, the kernel may kill it for memory, or an entrypoint may reject configuration before the app starts.

Suppose the production API crashes after a deploy. Preserve the container name/ID, image digest, creation/start timestamps, exit and OOM state, restart count, logs, inspect output, health state, mount list, published ports, daemon events and corresponding host metrics. Compare the failing instance with the last known good deployment: environment/config source (without exposing values), command and arguments, image identity, permissions, dependencies and resource limits. A health check failure while PID 1 remains alive differs from an exited primary process. A restart policy can obscure the initial failure by repeatedly replacing process state; bounded logs and events are especially useful.

Choose recovery after finding a plausible cause. If the image or configuration revision is wrong, roll back to a verified compatible revision using the deployment process. If a secret expired, rotate through its owner and update dependents; do not print it to prove it exists. If disk or memory pressure caused the exit, measure the limiting resource and reduce load or restore capacity before restarting. If a required mount is empty, verify daemon context, volume identity and backup before touching data. Avoid `docker commit` as an incident patch: it captures an ad hoc writable layer, omits a reproducible source change and can preserve secrets or transient state. Record the evidence and recovery decision, then create a corrected image/configuration through version control.

After the cause is corrected, start or recreate only the intended service, then verify the expected health signal and a real application request. Observe logs and metrics through the normal error budget window, and confirm that retries are not masking a continuing failure. Preserve the failed container until evidence is collected when policy permits; then remove only that lab or incident object. If diagnostic evidence is needed for a security or reliability review, retain it in the approved incident record before cleanup. Once the disposable lab evidence is no longer needed, remove only its named container:

```bash
docker rm dispatchdesk-crash-lab
```

The container is stopped, so no force option is needed. This removes its metadata and writable layer, not the downloaded Alpine image.

## Exercises and review questions

1. `docker logs` returns no useful text for a stopped container. Which configuration and state checks distinguish “application emitted nothing” from “the logging path is unavailable”?
2. Why is `docker exec` unavailable after PID 1 has exited? What evidence can be collected instead?
3. Container memory is high in one `docker stats` sample. What evidence is needed before deciding that memory caused the incident?
4. The container is healthy but customers receive errors from an upstream load balancer. Which boundaries must be tested outside the container health check?
5. After a redeploy, an API crash loop begins. Which evidence should be preserved before removing containers or changing configuration?
6. Why do daemon events and container-local logs not constitute a complete durable audit record?

### Answer guidance

1. Inspect the logging driver and container state, check the application's configured output destination, and verify that the command queries the correct daemon/context. A `none` log driver or unsupported remote driver behavior can affect retrieval.
2. `exec` starts a new process only while the primary container process is running. For an exited container, inspect exit/OOM state, logs, image/configuration and events; reproduce from the declared configuration if more investigation is needed.
3. Compare repeated samples, configured limits, cgroup/host memory and OOM events with application metrics, traffic, restart timestamps and host pressure. A sample is correlation evidence, not proof of cause.
4. Check host publication and bind address, host firewall, routes, upstream listener/health policy and external network controls from the correct execution host. The container check covers only its configured probe path.
5. Capture object identity, image digest, timestamps, exit code, OOM flag, restart count, logs, inspect state, event window, mounts, effective command/config source and matching host/dependency evidence. Protect secrets in logs and inspect output.
6. Events are a bounded recent buffer and container logs depend on the configured logging driver and retention. Send required records to a durable, access-controlled observability or audit system.

## Takeaways

- Logs, inspect, exec, stats and events answer different diagnostic questions.
- Query the intended daemon context and correlate timestamps across container, host, dependency and upstream evidence.
- Preserve exit state, logs, image identity, configuration references, mounts and event windows before destructive cleanup.
- Resource samples and health checks are bounded observations, not proof of the cause or business outcome.
- Reproduce and fix failures in declared image/configuration inputs; avoid undocumented patches to a live or stopped writable layer.
- Validate the recovery with application behavior and observe for recurrence.

## Further reading

- [Docker Compose for Multi-service Applications](057-docker-compose-for-multi-service-applications.md) — dependencies, health checks and project identity.
- [Docker Production Operations](060-docker-production-operations.md) — daemon logging, limits and ongoing recovery controls.
- [Systemd and Service Lifecycles](../02-linux-and-automation/016-systemd-and-service-lifecycles.md) — host service logs and process management.
- [Observability from Questions to Evidence](../15-observability-and-telemetry/141-observability-from-questions-to-evidence.md) — durable service-level signals and objectives.

## Sources and verification

Docker's official [`docker logs`](https://docs.docker.com/reference/cli/docker/container/logs/), [`docker inspect`](https://docs.docker.com/reference/cli/docker/container/inspect/), [`docker exec`](https://docs.docker.com/reference/cli/docker/container/exec/), [`docker stats`](https://docs.docker.com/reference/cli/docker/container/stats/), [system events](https://docs.docker.com/reference/cli/docker/system/events/), [logging drivers](https://docs.docker.com/engine/logging/configure/) and [container state](https://docs.docker.com/engine/containers/runmetrics/) documentation were inspected on 2026-10-03. Behavior is scoped to the selected Docker Engine and logging driver; rootless/Desktop process and journal paths differ. Commands and code blocks were statically checked but not run because this workspace has no Docker daemon. No crash, log record, resource sample or recovery is claimed as runtime evidence.
