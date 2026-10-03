---
book: The Complete DevOps Engineering Book
volume: 7
volume_title: "Podman and the Rootless Host"
chapter: 66
title: "Quadlet and Systemd Integration"
slug: quadlet-and-systemd-integration
status: complete
summary: ../../_ai/chapter-summaries/066-quadlet-and-systemd-integration.md
---

# Chapter 66 — Quadlet and Systemd Integration

## Declarative units and generated services

A container that responds to HTTP after an interactive `run` has passed one useful test. DispatchDesk needs a stronger contract: start without a human login, restart under a defined policy, stop cleanly, and provide an inspectable release configuration. Quadlet translates container declarations into systemd services so the existing host supervisor owns that lifecycle.

Read [systemd lifecycles](../02-linux-and-automation/016-systemd-and-service-lifecycles.md) and [Podman pods](065-podman-pods-and-kubernetes-yaml.md) first. This fixture runs on a disposable Linux host as one ordinary account with a working systemd user manager, cgroup v2, Podman Quadlet support, registry access, `curl`, and free TCP port 8091. Check `podman info` and the installed `podman-systemd.unit` manual. Ubuntu 24.04 packages and vendor-maintained RHEL builds may support fewer Quadlet keys than upstream stable documentation. Fedora availability does not establish RHEL feature support.

The source file goes in a rootless search path such as `~/.config/containers/systemd/`. A `.container` source is read by the generator during manager startup or daemon reload, producing a corresponding `.service`. The generated service is an implementation artifact; edit the source rather than modifying temporary generated output. Source-controlled files should record approved image identity, ports, mounts and resource policy.

Create the directory as the owning account:

```bash
mkdir -p "$HOME/.config/containers/systemd"
```

Save this complete fixture as `~/.config/containers/systemd/dd-http-66.container`:

```ini
[Unit]
Description=DispatchDesk HTTP transport fixture
StartLimitIntervalSec=60
StartLimitBurst=5

[Container]
Image=docker.io/library/nginx:alpine
ContainerName=dd-http-66
PublishPort=127.0.0.1:8091:80
LogDriver=journald
StopTimeout=10

[Service]
Restart=on-failure
RestartSec=3
TimeoutStartSec=180
TimeoutStopSec=30

[Install]
WantedBy=default.target
```

This intentionally small service exposes the same transport fixture as Chapter 62. It contains no business data or database. `ContainerName` makes inspection predictable. The loopback publication keeps the listener local to the host. Journald provides a host-managed log destination. The restart delay and start limit bound a rapid failure loop. The stop timeout gives the application ten seconds while the surrounding service timeout leaves additional room for engine cleanup. Measure those intervals for the real application rather than copying them as universal production values.

`TimeoutStartSec` accommodates an initial image pull, but it does not turn a registry outage into successful startup. For a production digest-pinned release, pre-pull during an approved deployment step and verify image availability under the service account. A mutable tag is appropriate only for this disposable fixture; replace it with the measured approved reference when constructing the real DispatchDesk unit.

The [Quadlet documentation](https://docs.podman.io/en/stable/markdown/podman-systemd.unit.5.html) defines the generator, search paths and install behavior. In particular, boot activation comes from the source's `[Install]` section; do not assume a generated service can be enabled like a persistent handwritten unit. Inspect the generated file before starting it.

```bash
systemctl --user daemon-reload
systemctl --user cat dd-http-66.service
systemctl --user start dd-http-66.service
systemctl --user status dd-http-66.service
podman --remote=false inspect dd-http-66
curl --fail --show-error --max-time 5 http://127.0.0.1:8091/
```

`daemon-reload` reruns generators and reloads unit definitions. It does not necessarily restart an already-running container with changed settings. `cat` shows the realized service and drop-ins. `start` changes runtime state. Status, inspect output and HTTP acceptance provide three different observations: supervisor state, container configuration and client-visible behavior.

## User services, lingering and startup

A rootless Quadlet belongs to the user manager. Adding `[Service] User=somebody` to a rootful Quadlet does not reproduce that supported rootless arrangement. The source location, manager and account environment establish the engine identity. Keep administrator commands and user service commands separate so operators do not accidentally inspect another store.

For unattended startup, an administrator can enable lingering for the dedicated account. On the disposable host, the following enables it for the current owning account through authorized sudo:

```bash
sudo loginctl enable-linger "$(id -un)"
loginctl show-user "$(id -un)" -p Linger
```

Lingering keeps the account's user manager available outside interactive sessions and permits startup at boot. This is a persistent host change. In production it belongs in account provisioning policy, with ownership, resource limits and monitoring. Record whether it was enabled before the lab so teardown does not disable an existing service account's legitimate setting.

A successful start during login does not establish logout or reboot acceptance. Test both on the disposable host, from another authorized session that can observe the listener and service state. Reboot interrupts every workload on that host and should be performed only in a planned test or maintenance window. Before reboot, record the source file, image availability, manager activation and health probe. After reboot, verify the service without relying on a new login to start it.

The user's encrypted home or delayed filesystem mount can create a separate boot dependency. Lingering does not make unavailable source files, image storage or credentials magically accessible. Design startup around storage that exists when the manager starts. The administrator must also decide how user resource limits interact with container limits; all services under that account can share a constrained parent slice.

User units cannot simply wait on system units as if both lived in one manager. Current Quadlet can add its own network readiness integration, but releases differ. Inspect the generated dependencies on your host. Network-online ordering still does not prove that a private registry, DNS server or application database is reachable. Applications need bounded dependency retries and readiness semantics.

## Running a durable rootless service

The fixture has one lifecycle owner: systemd. Use `systemctl --user` to stop, restart and inspect it. A manual `podman stop` can make the service manager observe failure and apply its restart policy. A second competing restart mechanism can produce confusing behavior. Express restart intent at the selected supervisor and test the consequence of process failure separately from an operator-requested stop.

Observe logs and realized state:

```bash
journalctl --user -u dd-http-66.service --since '15 minutes ago' --no-pager
podman --remote=false logs --timestamps --tail 50 dd-http-66
systemctl --user show dd-http-66.service -p ActiveState -p SubState -p NRestarts
```

Supervisor messages show generator/startup failures and restart activity; application output shows what the workload emitted. Journal access and retention depend on host configuration. Ensure operations staff can obtain the needed evidence without granting broad engine control. Monitor HTTP readiness separately from the service's active state: the runtime can notify systemd of startup before application dependencies become ready.

For a release change, preserve the previous source and digest. Update the intended source, reload the manager, inspect the generated changes, then restart during the planned deployment window. Probe the actual upstream path used by the reverse proxy and observe error rates. If acceptance fails, restore the previous source, reload and restart. Persistent state and schema compatibility must be assessed before image rollback; this fixture has none, but DispatchDesk will.

Health-check-triggered restart should be chosen carefully. Restarting on every transient database outage can amplify a shared dependency failure. A readiness check can withdraw traffic while the process continues recovering. A liveness check should detect a condition that restart can plausibly repair. These are application policy decisions, not defaults that Quadlet can infer from a URL.

## Failed generation and recovery

Suppose `systemctl --user start` says the unit does not exist. The failed assumption is that placing a source file always creates a valid generated unit. Inspect the filename and search path, reload, check generator diagnostics and confirm key support in the installed version. Current upstream documentation offers generator dry-run and `systemd-analyze --generators=true` verification; the binary location and options depend on packaging. Use the documented packaged path rather than assuming `/usr/lib` and `/usr/libexec` are interchangeable.

If the source uses a key introduced after the distribution's package, select a supported declaration or upgrade through an approved vendor path. Do not paste raw `PodmanArgs` around every rejected key without checking whether that bypass changes supervision semantics. If the service starts and fails repeatedly, inspect the first error and start-limit state. Repair the cause, then use `systemctl --user reset-failed dd-http-66.service` if the start limit prevents the deliberate retry.

If a pull times out, distinguish authentication/TLS/DNS from a legitimately slow transfer. Increasing startup timeout may fit a measured download; it does not repair missing credentials. If it works interactively but not at boot, compare service account environment, persistent auth location and filesystem availability. Chapter 70 develops that incident.

For lab cleanup:

```bash
systemctl --user stop dd-http-66.service
rm -- "$HOME/.config/containers/systemd/dd-http-66.container"
systemctl --user daemon-reload
```

Inspect remaining objects if cleanup differs from expected generator behavior. Disable lingering only if this lab enabled it and the account has no other unattended services; that is an administrator policy decision, not automatic cleanup.

## Exercises and review questions

1. Explain source versus generated service. **Guidance:** edit `.container`, reload to regenerate, inspect `.service`; a reload alone does not apply changed runtime configuration to an existing process.
2. Design logout and boot acceptance. **Guidance:** observe from another session and verify startup before a new workload-account login can influence it.
3. A unit is active but HTTP readiness fails. What was actually established? **Guidance:** supervisor lifecycle state, not application dependency readiness.
4. A unit disappeared after adding a key from an online example. **Guidance:** generator diagnostics, installed version/key support and source search path come before runtime diagnosis.

## Takeaways and further reading

A durable rootless service needs a declared lifecycle, the correct user manager and tested startup outside login sessions. Keep one supervisor responsible for restart. Continue with [SELinux mounts](067-selinux-and-container-mounts.md).

Quadlet primary documentation was inspected 2026-10-03. The systemd rendered manual returned HTTP 403; the official [loginctl source manual](https://raw.githubusercontent.com/systemd/systemd/main/man/loginctl.xml) was inspected as the primary-source fallback for linger behavior. Consult the installed manual for your packaged release. No source file was installed, service activated or host rebooted by the author.
