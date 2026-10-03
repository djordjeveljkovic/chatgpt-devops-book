---
book: The Complete DevOps Engineering Book
volume: 6
volume_title: "Docker in Practice"
chapter: 60
title: "Docker Production Operations"
slug: docker-production-operations
status: complete
summary: ../../_ai/chapter-summaries/060-docker-production-operations.md
---

# Chapter 60 — Docker Production Operations

A Docker host is part of the production system. Its daemon configuration, disk capacity, patch level, log retention and recovery behavior affect every container that depends on it. A container can have a memory limit and health check while the host still fills its disk, loses its registry credentials or restarts at the wrong time. Production operations therefore combine per-container controls with host maintenance and an explicit recovery plan.

This chapter assumes a dedicated Linux Docker Engine host, an authorized operator account and a deployment managed from reviewed configuration. Docker Desktop and rootless Engine have different daemon settings and service boundaries. Commands that read Docker state use the daemon context; host service and filesystem commands must run on the machine that owns that daemon. Do not restart a shared production daemon or modify system-wide policy without an approved maintenance plan. See [Chapter 51](051-installing-and-inspecting-docker.md) for daemon access, [Chapter 57](057-docker-compose-for-multi-service-applications.md) for the DispatchDesk service stack, and [Chapter 58](058-inspecting-and-debugging-docker.md) for incident evidence.

## Daemon maintenance and log rotation

Start maintenance with capacity and version evidence from the selected production daemon:

```bash
docker context show
docker version
docker info --format 'root={{.DockerRootDir}} logging={{.LoggingDriver}} storage={{.Driver}}'
docker system df -v
```

Record the context and host with the output. If the context is remote, run filesystem and service checks on the remote daemon host, not on the CLI workstation. On Ubuntu and Fedora/RHEL systems using a rootful systemd service, an authorized operator can check the Docker data filesystem and daemon journal on that host:

```bash
data_root=$(docker info --format '{{.DockerRootDir}}')
df -h "$data_root"
df -i "$data_root"
sudo journalctl -u docker.service --since '1 hour ago' --no-pager
```

The `df` commands check byte and inode capacity for the filesystem containing Docker's data root. The journal query is read-only and may require administrator privileges. Verify the unit name and logging destination on the actual host; rootless Engine uses the user's service manager, and Docker Desktop stores daemon logs in its own VM environment. For Ubuntu and Fedora/RHEL with systemd, the daemon configuration file for a standard rootful installation is normally `/etc/docker/daemon.json`. Package installation paths, SELinux policy and service details can differ, so follow the host's distribution documentation and retain SELinux enforcement.

On fresh Docker Engine 29.0 or later installations, the containerd image store is the default. In that mode, image contents and container snapshots normally live under `/var/lib/containerd`, while volumes and other daemon data remain under Docker's data root. Setting Docker's `data-root` does not move the separate containerd directory. Inspect `docker info` for the active snapshotter and inspect the daemon and containerd service configuration on the daemon host before concluding that one filesystem check covers all container storage. For a standard system containerd installation, the default root is `/var/lib/containerd`; a custom root is configured through `/etc/containerd/config.toml`. Optional embedded-containerd mode has a different state location under Docker's data root, so account for that mode as well. Measure each actual configured storage filesystem. This version-sensitive split can otherwise fill the host root filesystem while Docker's data-root filesystem appears healthy. See [Chapter 45](../05-container-internals-and-oci/045-container-filesystems-and-storage.md) for storage fundamentals.

For a host using the separate system containerd service, inspect its effective startup configuration and default config file before checking its root filesystem:

```bash
docker info --format '{{json .DriverStatus}}'
sudo systemctl cat containerd.service
sudo sed -n '1,100p' /etc/containerd/config.toml
sudo df -h /var/lib/containerd
sudo df -i /var/lib/containerd
```

If `config.toml` sets a different `root`, or the service uses a different `--config` path, replace `/var/lib/containerd` with the configured location in both `df` commands. If the host uses embedded containerd, use the Docker data root and its configured filesystem instead. These commands read configuration and capacity; they do not change storage locations.

Container log retention is a capacity control. Docker's default `json-file` logging driver does not rotate files unless options are set; large output can consume the daemon host's disk. Docker's `local` driver rotates by default and uses a storage format intended for Docker's use. Choose a driver and retention based on whether operators need `docker logs`, a remote log platform, or both. A remote driver may introduce connectivity or back-pressure behavior; validate delivery, retention and outage handling before relying on it for incident records.

For a dedicated Engine host whose applications are compatible with the `local` logging driver, the daemon configuration can set it as the default for newly created containers:

```json
{
  "log-driver": "local",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  }
}
```

This is a complete JSON example, not a replacement file to copy over an existing daemon configuration. Merge the keys with the host's existing valid settings, keeping a single JSON object and avoiding duplicate keys. The size and file count are illustrative capacity choices: the rough per-container cap is five 10 MB files before filesystem overhead, but aggregate use depends on the number of containers and compression. Docker requires logging option values in daemon JSON to be strings. On an Engine version that supports configuration validation, validate the merged file without starting the daemon:

```bash
sudo dockerd --validate --config-file=/etc/docker/daemon.json
```

The expected result is a successful validation message and zero exit status. This checks supported file keys and values but does not prove that the systemd command line has no conflicting options or that the logging destination has enough capacity. Inspect the service's actual startup configuration as part of review:

```bash
sudo systemctl cat docker.service
```

After applying the approved change during an authorized maintenance window, confirm that the daemon is active and reports the new default:

```bash
sudo systemctl restart docker.service
sudo systemctl is-active docker.service
docker info --format '{{.LoggingDriver}}'
```

Do not run that restart on a shared production host without the change approval and workload recovery plan described above. On a canary, inspect an existing container before and after deployment-controlled recreation to detect per-container or Compose overrides:

```bash
docker inspect dispatchdesk-api-canary \
  --format 'driver={{.HostConfig.LogConfig.Type}} options={{json .HostConfig.LogConfig.Config}}'
```

Verify that the new container has the intended driver and options, and confirm log delivery and retention through the supported interface. Existing containers retain their logging configuration; recreating them through the deployment process is required to adopt a new default.

Changing daemon-wide configuration and restarting `docker.service` is an availability event. On the host, the service is controlled with systemd; use the approved change window, understand `live-restore` and networking effects, and ensure workloads can recover. Keep a known-good copy of the previous JSON and a tested rollback procedure before rollout. If the restart fails, stop further rollout, restore the prior file, inspect `journalctl -u docker.service`, validate the restored file and unit configuration, then retry the service start only under the approved recovery procedure. Verify daemon state, workload availability and port/network paths before resuming. If systemd flags conflict with the file, resolve the reviewed unit configuration conflict instead of repeatedly restarting. Do not edit Docker-managed log files directly or use an operating-system log rotator on them; configure the logging driver instead.

Disk maintenance should be driven by evidence. `docker system df -v` shows images, containers, local volumes and build cache. Remove a specifically identified unused image or build cache under an approved retention plan. `docker system prune` removes more than cache: stopped containers, unused networks, dangling images and build cache; `--all` widens image removal, and `--volumes` adds unused anonymous volumes. A volume not currently attached can still contain data someone expects to restore. Never run broad prune commands as routine cleanup on a production daemon without inventory, ownership checks and a recovery policy. For database backup and durable state, follow [Chapter 56](056-docker-volumes-and-persistent-data.md); pruning is not backup or capacity planning.

## Health, resource limits and recovery

A process being alive is different from an application being ready to serve. A Docker health check runs a command inside the container and records `starting`, `healthy` or `unhealthy` state. It can make a dependency or endpoint probe observable, but it does not automatically repair a broken service or replace an external alert. Design a check around a meaningful local condition, bound its execution time, allow a startup grace period, and avoid a probe that creates side effects or depends on a remote service whose outage would make every container appear unhealthy. See the Compose readiness pattern in [Chapter 57](057-docker-compose-for-multi-service-applications.md) and health-state inspection in [Chapter 58](058-inspecting-and-debugging-docker.md).

Resource limits turn some host capacity assumptions into enforceable boundaries. For a single-container run, an operator might set explicit memory, CPU and process limits:

```bash
docker run --detach \
  --name dispatchdesk-api-canary \
  --memory 768m \
  --cpus 1.5 \
  --pids-limit 256 \
  --restart unless-stopped \
  registry.example.internal/dispatchdesk/api@sha256:REPLACE_WITH_APPROVED_DIGEST
```

Replace the example digest with the release record's verified value from [Chapter 59](059-publishing-and-promoting-images.md). This command is illustrative; it would create a new container and could bind an application that has no port or configuration. In the real service definition, preserve its network, secrets, health check, mounts and environment configuration. `--memory` establishes a hard memory ceiling, `--cpus` limits CPU time, and `--pids-limit` bounds process count on supported Linux engines. These limits reduce specific risks but do not cap disk consumption, network traffic, all I/O, Docker daemon use, host services or aggregate load from other containers. Add storage quotas/retention and host-level monitoring where needed, and retain capacity for the operating system and daemon. If host swap is enabled, review `--memory-swap` as a separate policy; setting `--memory` alone does not necessarily prevent the container from using swap. Limits that are too low can trigger OOM kills, throttling, queue buildup or missed latency objectives. Check cgroup support with `docker info`, measure a representative load, and monitor both container and host metrics before selecting values. CPU shares are relative weight, not a hard ceiling; use the control that matches the capacity objective.

Restart policy helps a daemon recover a process after an exit, but it is not a health-based repair strategy. `unless-stopped` can bring a container back after a daemon restart unless an operator deliberately stopped it. A restart loop can repeatedly run a bad release, amplify dependency load or erase short-lived evidence. Pair restart policy with bounded alerts, clear logs, readiness checks, and a documented rollback. Avoid having both Docker restart policies and a host process manager compete to start the same container.

Recovery begins with an operator deciding whether the problem is the process, its configuration, the host or a dependency. For a crash loop, inspect the digest, exit code, OOM state, restart count, logs, events and recent host pressure before changing the service. If a release introduced the failure, roll back to the last compatible digest and configuration using the deployment controller; do not run an ad hoc `docker run` next to a managed stack. If the host disk is full, identify which images, logs, volumes or build cache consume space, then use the owning subsystem's retention procedure. Deleting a database volume may turn a capacity incident into data loss.

## A production deployment review

Before enabling a Docker service for customer traffic, review the whole deployment path:

| Area | Evidence to verify | Failure the check helps prevent |
|---|---|---|
| Artifact | Approved registry, digest, supported platforms, signature/provenance policy | Mutable tag drift or unreviewed build |
| Identity | Non-root process where practical; daemon access limited to trusted operators | Unnecessary host authority |
| Configuration | Secrets arrive through an approved mechanism; no credentials in image layers or logs | Credential disclosure during build or diagnosis |
| Networking | Only intended ports published; host firewall and upstream policy checked | Accidental external exposure |
| State | Durable data is externalized and backed up; restore has been tested | Data loss on container replacement or host failure |
| Health and recovery | Useful health signal, bounded restart behavior, rollback digest and owner | Silent failure or uncontrolled restart loop |
| Capacity | CPU, memory, process, disk and log limits align with measured demand | Noisy neighbor and disk exhaustion |
| Observability | Logs, metrics, events and alerts reach retained systems with access controls | Missing incident evidence or sensitive-data leakage |
| Maintenance | Engine patch process, config review, change window and host replacement plan | Unplanned daemon outage or inconsistent hosts |

Suppose the API canary becomes unhealthy after a daemon host is patched. First determine whether the container was recreated, what digest it runs, whether the health check fails locally, and whether the database and queue remain reachable. Compare daemon logs, service logs, host disk and memory, network mappings, image/configuration rollout history and dependency health. If only the canary fails on one host, stop further rollout and preserve its evidence. If every container on that host fails after daemon maintenance, treat the host or daemon as the likely boundary and follow the fleet's drain/replacement plan. Do not loosen all health checks or remove limits just to silence alerts; make a reversible change tied to observed evidence, then test service behavior and monitor recovery.

Exercises are review prompts, not instructions to run destructive cleanup on a production host. Practice daemon restart and rollback on a disposable host first. A single Docker host is still a single failure domain: container restart policies cannot replace host redundancy, tested backups, capacity reserves or a deploy strategy that can move work elsewhere.

## Exercises and review questions

1. `docker system df` shows low image use but the filesystem containing Docker's data root is almost full. Which measurements and owners should you investigate before deleting data?
2. A daemon logging-driver change has been merged but `docker logs` still shows old containers using the previous behavior. Explain why and describe a safe rollout.
3. A health check reports `unhealthy`, but the API process is running. What should you compare before restarting or rolling back the container?
4. A container is OOM-killed after a new resource limit is applied. Which application, container and host evidence should inform the new limit or rollback decision?
5. Why is `docker system prune --all --volumes` unsafe as a scheduled production maintenance command?
6. During an Engine patch, the daemon fails to start after a configuration update. What is the safe recovery sequence?

### Answer guidance

1. Check bytes and inodes on Docker's data-root filesystem and, when using the containerd image store with separate containerd, its configured root filesystem too. Review logs, volumes, writable layers, image/build cache and other host consumers with their owners and retention requirements. `docker system df` is not a complete host disk inventory.
2. Daemon defaults apply to newly created containers, not existing container logging configuration. Merge and validate JSON with `dockerd --validate`, inspect the unit's startup flags, schedule an approved daemon change/restart, check service state and `docker info`, recreate services through the deployment mechanism, inspect each container's effective log config, and retain rollback.
3. Inspect health-check output and timing, process state, dependency response, resource pressure, recent configuration and deployment changes, logs, events and the intended readiness contract. A running process can still be unable to serve; restarting without diagnosis may erase evidence or amplify load.
4. Correlate the configured limit and OOM state with memory use over time, cgroup and host pressure, traffic, request/job sizes, garbage collection or cache behavior, restarts and latency/errors. Restore service using the approved prior deployment or calibrated limit; do not disable the OOM killer as a default fix.
5. It can remove stopped containers, unused networks and images, build cache and unused anonymous volumes; the `--all` and `--volumes` flags widen impact. Unattached data may still be valuable, and deleting cached images can impair rollback or increase registry dependency during an incident.
6. Stop further rollout, restore the last known-good daemon configuration from the protected copy, inspect daemon journal and validation errors, then start the service using the host's normal systemd procedure. Confirm daemon health, workloads and connectivity before resuming patch rollout.

## Takeaways

- Operate the Docker daemon and its host as production dependencies; monitor disk, inodes, logs, storage and patch state.
- Configure bounded log retention, then recreate existing containers through a controlled rollout to adopt daemon defaults.
- Health checks expose a probe result; resource limits and restart policies need measured values and an application recovery plan.
- Diagnose before pruning or restarting. Broad cleanup can remove rollback artifacts or unattached data.
- Review image identity, privilege, secrets, ports, durable state, capacity, observability and rollback before customer traffic.

## Further reading

- [Inspecting and Debugging Docker](058-inspecting-and-debugging-docker.md) — correlate logs, state, events and host evidence.
- [Publishing and Promoting Images](059-publishing-and-promoting-images.md) — record and deploy approved digests.
- [Docker Volumes and Persistent Data](056-docker-volumes-and-persistent-data.md) — durability, backup and restore.
- [Observability from Questions to Evidence](../15-observability-and-telemetry/141-observability-from-questions-to-evidence.md) — alerting and retained operational evidence.
- [Systemd and Service Lifecycles](../02-linux-and-automation/016-systemd-and-service-lifecycles.md) — host service changes and rollback.

## Sources and verification

Docker's official [logging configuration](https://docs.docker.com/engine/logging/configure/), [`local` logging driver](https://docs.docker.com/engine/logging/drivers/local/), [daemon configuration](https://docs.docker.com/engine/daemon/), [`dockerd --validate`](https://docs.docker.com/reference/cli/dockerd/), [containerd image store](https://docs.docker.com/engine/storage/containerd/), [resource constraints](https://docs.docker.com/engine/containers/resource_constraints/), [restart policies](https://docs.docker.com/engine/containers/start-containers-automatically/), [`docker system df`](https://docs.docker.com/reference/cli/docker/system/df/) and [`docker system prune`](https://docs.docker.com/reference/cli/docker/system/prune/) documentation were inspected on 2026-10-03. Engine 29.0+ fresh-install storage defaults and the separate containerd root are version-sensitive; inspect the active daemon mode and config. Examples are reader-run and were not executed; this workspace has no Docker daemon. Static checks validate syntax and local links, not service availability, safe capacity values, daemon configuration on a particular distribution, or workload recovery.
