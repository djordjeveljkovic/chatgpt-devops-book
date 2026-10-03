---
book: The Complete DevOps Engineering Book
volume: 7
volume_title: "Podman and the Rootless Host"
chapter: 70
title: "Podman Host Operations and Incidents"
slug: podman-host-operations-and-incidents
status: complete
summary: ../../_ai/chapter-summaries/070-podman-host-operations-and-incidents.md
---

# Chapter 70 — Podman Host Operations and Incidents

## Storage, upgrades and resource pressure

DispatchDesk's fictional VPS team now has a rootless service declaration and a tested HTTP path. The next question is whether an on-call engineer can recover it after disk pressure, a failed package upgrade or expired registry credentials. Rootless ownership distributes engine state across accounts, so host-wide incident response needs an account-aware inventory rather than one administrator's `podman ps` output.

Read [migration acceptance](069-migrating-docker-workflows-to-podman.md), [Quadlet](066-quadlet-and-systemd-integration.md), [server backups](../04-vps-and-server-operations/037-server-backups-and-restore.md) and [host capacity](../04-vps-and-server-operations/040-vps-incidents-and-capacity.md). Commands here run locally on the relevant Linux host as the owning ordinary service account unless `sudo` marks administrator access. Read-only inspection is shown before any recovery change. Examples using `dd-http-66` require Chapter 66's fixture to be currently installed; otherwise substitute a deliberately identified owned service in prose, not an unknown name.

Start with identity, engine and storage inventory:

```bash
id
podman --remote=false info
podman --remote=false system df --verbose
podman --remote=false ps --all
podman --remote=false volume ls
```

`system df` reports engine-account usage by object category; its reclaimable estimates are not a guarantee that a particular deletion will free that many physical bytes. Shared layers and backing filesystem behavior affect the result. Compare it with host filesystem capacity using the effective graph root:

```bash
graph_root=$(podman --remote=false info --format '{{.Store.GraphRoot}}')
findmnt -T "$graph_root"
df -h "$graph_root"
df -i "$graph_root"
```

The variable is obtained from the selected engine, not a guessed home-directory path. `findmnt` identifies the backing mount; `df -h` checks byte capacity and `df -i` checks inode capacity. Rootless storage may live on the same filesystem as home data, while application bind mounts and journals can live elsewhere. Check those actual paths separately. A full `/var/tmp` can also disrupt downloads even when the graph root has space.

Monitor disk usage over time, inode growth, journal retention, container count, image growth and application data. Rootless accounts can each hold duplicate image caches. Per-account usage is useful for ownership; host aggregate capacity determines whether another deployment can proceed. Build caches and old releases need a retention policy that preserves rollback artifacts without accumulating indefinitely.

Do not make `podman system prune --all --volumes` the default response to pressure. Prune can remove stopped containers, unused networks and images according to flags; volumes require explicit handling and may contain valuable data even when no running container references them. The [prune manual](https://docs.podman.io/en/stable/markdown/podman-system-prune.1.html) is the authority for the installed release. An “unused” volume can be the only copy of yesterday's stopped database.

Prefer scoped deletion after documenting ownership and backup status. Preserve failed-container logs and configuration before removing their objects. Verify filesystem capacity afterward; deleted-but-open files can remain allocated until the owning process closes them. Investigate that host condition with appropriate administrator diagnostics rather than repeatedly pruning different accounts.

## Upgrades and rollback boundaries

Ubuntu APT and Fedora/RHEL DNF updates can change Podman, runtime, networking helpers and policy packages together. Review the planned transaction and vendor notes. RHEL support streams and backports differ from Fedora's release cadence; a newer upstream feature is not a reason to add unsupported repositories to a stable production host.

Take a tested application-consistent backup, record current package versions, engine info, account/subordinate allocations, declarative source, image digest and data location. Use a disposable canary with representative storage and networking before updating the fleet. Test start, stop, boot and restore after the upgrade. A running process that survived package replacement has not proved that the next recreated container will work.

An engine upgrade may require state migration. `podman system migrate` is an explicit maintenance operation and can stop containers, including the rootless namespace keeper. The [migration manual](https://docs.podman.io/en/stable/markdown/podman-system-migrate.1.html) describes its consequences. Reserve it for the documented case under a planned maintenance procedure, not an automatic command after every package update.

Rollback has two distinct layers: application release rollback and host engine rollback. Restoring the prior digest/configuration may repair an application regression. Downgrading an engine can encounter storage/database compatibility constraints. Follow vendor-supported recovery instead of assuming an old binary reads newly migrated state. Preserve clean application backups so host recreation remains possible if an in-place downgrade is unsupported.

Podman auto-update is another lifecycle choice. The [auto-update manual](https://docs.podman.io/en/stable/markdown/podman-auto-update.1.html) describes policies and systemd integration. An automatically tracked tag is not equivalent to an explicitly approved digest release. Startup success does not prove schema compatibility or business correctness. Choose automation only with appropriate acceptance, readiness notification, rollback limits and a defined owner for failed updates.

## Service recovery and registry failures

For the Chapter 66 fixture, gather bounded supervisor and application evidence before changing state:

```bash
systemctl --user status dd-http-66.service
systemctl --user cat dd-http-66.service
journalctl --user -u dd-http-66.service --since '30 minutes ago' --no-pager
podman --remote=false inspect dd-http-66
podman --remote=false logs --timestamps --tail 100 dd-http-66
podman --remote=false events --since 30m --stream=false
```

The [events reference](https://docs.podman.io/en/stable/markdown/podman-events.1.html) explains event recording. Retention/backend configuration determines how much history is available. Service failure before container creation can leave no container to inspect, so a missing object and an informative systemd journal are compatible observations. Preserve the first failure instead of letting repeated retries obscure it.

Classify registry failures by stage. DNS errors concern resolution; connection timeouts concern routing, proxy or service availability; certificate errors concern trust, hostname and time; unauthorized errors concern credentials and repository permissions; missing manifests concern image reference or platform. A private registry can return intentionally ambiguous errors, so compare authorized repository access without publishing tokens in logs. Do not set TLS verification false as a general recovery action.

A common incident occurs after reboot: an interactive pull worked yesterday, but the service cannot authenticate today. Linux Podman's default authentication file can live under the user's runtime directory, which is not a durable credential store across reboot. The [login manual](https://docs.podman.io/en/stable/markdown/podman-login.1.html) documents file selection and explicit `--authfile` behavior.

For an approved private registry, select a persistent account-owned auth file and configure the service to use that exact path. The following is a reader procedure; replace the value with the actual trusted registry hostname before use:

```bash
registry_host='registry.example.org'
install -d -m 700 "$HOME/.config/containers"
podman --remote=false login \
  --authfile "$HOME/.config/containers/registry-auth.json" "$registry_host"
chmod 600 "$HOME/.config/containers/registry-auth.json"
```

The example hostname is reserved and not a working registry. Interactive login avoids putting a password directly in shell history or process arguments; organizational token delivery may instead require an approved secret mechanism. The auth file is sensitive encoded credential material, not encryption. Use scoped credentials, protect the account and document rotation. Do not print or commit its contents.

In the Quadlet source, add `Environment=REGISTRY_AUTH_FILE=%h/.config/containers/registry-auth.json` to its `[Service]` section. This sets the environment of the host Podman process; placing an application environment value in `[Container]` would target the wrong process. Podman login and image operations support `REGISTRY_AUTH_FILE` as documented. Inspect the generated service and effective environment to verify the realized path. Test the exact approved private image under the same account and auth selection, then reload/restart the service after repairing the cause. Increasing the timeout cannot restore expired permissions.

## Resource pressure and recovery sequence

A rootless service can exhaust its container limit, the account's parent cgroup, or the host. Observe all applicable boundaries:

```bash
podman --remote=false stats --no-stream
free -h
vmstat 1 5
sudo journalctl -k --since '30 minutes ago' --no-pager
```

The [stats manual](https://docs.podman.io/en/stable/markdown/podman-stats.1.html) documents metrics and rootless limitations. Empty or unavailable network counters under a particular rootless setup do not mean zero traffic. `free` and `vmstat` describe the host; they do not directly reveal a particular container's effective limit. Inspect container configuration and actual cgroup hierarchy when limit behavior matters.

An exit code alone does not establish an OOM kill. Correlate workload state, kernel/cgroup evidence and timestamps. A process can also be deliberately killed or exceed another limit. If a fixed memory limit is repeatedly reached, compare application working set, leaks, concurrency and parent pressure before raising it. More memory may be the right capacity decision, but it should not hide an unbounded queue or a leak.

For a registry outage, avoid restarting otherwise healthy cached workloads unnecessarily. Preserve the approved local artifact and separate image availability from running-service health. For a full disk, stop nonessential growth, reclaim only verified disposable objects, restore headroom and check data consistency before reopening writes. For corrupted application data, recreate containers only after the database-specific restore procedure; engine recreation cannot repair records.

Recovery succeeds when the original user-visible operation works, the supervisor remains stable and durable data is verified. Record residual risk, such as unavailable rollback images or a temporary capacity margin. A green `systemctl` status is one item of evidence, not the whole outcome.

## Operating a fleet of rootless hosts

Rootless fleets need a host-account-service map: numeric UID/GID, subordinate allocation, linger policy, graph root, application data path, security model, approved package source/version, Quadlet source revision, image digest and credential rotation owner. Central automation should target explicit accounts and local/remote contexts, not rely on the coordinator's interactive environment.

Canary changes by workload class. A stateless worker, attachment writer and database-bearing host exercise different risks. Test Ubuntu and Fedora/RHEL paths independently where both are supported. Preserve rollback instructions and backups outside the host being changed. If remote rootless administration is used, protect SSH access and engine sockets according to the account's full authority.

Monitoring labels should include host and service identity without exposing credentials. Collect application SLIs, host capacity, supervisor restart activity and backup/restore age. Avoid defining health solely as the count of running containers. A host can run every container while DispatchDesk cannot commit a request because its database is unavailable.

The next volume introduces [declarative infrastructure](../08-infrastructure-as-code/071-declarative-infrastructure-and-reconciliation.md). Keep this volume's rootless acceptance sheet as input: account identity, storage, security and lifecycle are requirements automation must preserve, not details to discard when YAML generation becomes convenient.

## Exercises and review questions

1. Disk space is low but engine reclaimable usage is small. **Guidance:** inspect backing filesystems, inodes, app data, journals, download temp space and deleted-open files under appropriate authority.
2. Pull works before reboot and authentication fails after reboot. **Guidance:** compare runtime versus persistent auth paths, service account, exact image permissions and generated host-process environment setting.
3. A process exits 137. Is OOM proved? **Guidance:** correlate kernel/cgroup evidence, timing and possible deliberate signals.
4. Design a canary upgrade acceptance sheet. **Guidance:** package/engine evidence, ownership/labels, network/DNS, start/stop/boot, restored data, readiness and rollback boundaries.

## Takeaways and further reading

Rootless operations depend on explicit account identity and tested host recovery. Preserve evidence before deletion, distinguish artifact availability from service health, and treat engine migrations as maintenance changes.

Primary Podman system-df, prune, migrate, events, login, stats and auto-update documentation was inspected 2026-10-03. No prune, upgrade, credential creation, service restart, host change or incident recovery was executed by the author.
