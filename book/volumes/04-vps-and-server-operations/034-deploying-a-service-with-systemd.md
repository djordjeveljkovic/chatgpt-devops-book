---
book: The Complete DevOps Engineering Book
volume: 4
volume_title: "VPS and Server Operations"
chapter: 34
title: "Deploying a Service with Systemd"
slug: deploying-a-service-with-systemd
status: draft
summary: ../../_ai/chapter-summaries/034-deploying-a-service-with-systemd.md
---

# Chapter 34 — Deploying a Service with Systemd

## Why this matters

An application that works in an interactive shell can fail after logout or reboot. It may inherit a developer's working directory, environment, credentials and terminal behavior. A service manager gives the process an explicit identity, start command, filesystem view, restart policy and place in the boot and shutdown sequence. Those settings become part of the application deployment and need the same review as code.

This chapter deploys a small Harbor instance of DispatchDesk as a conventional Python service on the VPS from Chapters 31–33. The application is assumed to implement the project contract from [Chapter 10](../01-engineering-mental-models/010-the-dispatchdesk-project-begins.md): HTTP on `127.0.0.1:8080`, order acceptance that durably pairs an order with notification intent, and `/healthz` and `/readyz` endpoints with distinct meanings. The snippets configure a deployment boundary; they do not create that HTTP implementation. Keep the service private until the proxy in Chapter 35 is configured.

## Separate releases, configuration and state

Use distinct paths so an upgrade does not overwrite the database or secret configuration. This example uses a deployment account to place immutable releases and a runtime account to execute them. The runtime does not own the release tree. Create accounts and directories using the distribution's approved provisioning method; package names and service account defaults differ between Ubuntu, Fedora and RHEL.

```text
/srv/dispatchdesk/releases/2026-10-02.1/   application code and virtual environment
/srv/dispatchdesk/current                  symlink to the selected release
/etc/dispatchdesk/dispatchdesk.env          restricted runtime configuration
/var/lib/dispatchdesk/                      durable mutable application state
```

The directory name is an example release identifier, not a guarantee that a build came from a trusted source. Record the source revision, build inputs and artifact digest alongside a real release. Do not put secrets in the release tree, shell history or a world-readable file. Limit access to `/etc/dispatchdesk/dispatchdesk.env` to administrators and the service's intended reader. A systemd environment file is configuration, not a secret vault: privileged users can inspect process state and files, and crash diagnostics may expose environment values.

Create a service identity with no interactive login and no writable home if the application does not need one. The service requires read and execute access to its release, read access to its configuration and write access to its state directory. Grant only those rights. An SQLite deployment also needs directory-level write access for journal or WAL sidecar files. If PostgreSQL is chosen later, the application should receive a database role, not ownership of the database server's data directory.

Before enabling a unit, verify all three paths, their owners and modes, and that the exact interpreter and application command work as the service identity. A successful command in an administrator's shell proves little about the service's permissions. SELinux or AppArmor may deny access even when Unix mode bits appear correct; inspect the relevant audit trail and policy rather than disabling confinement.

## Define the process contract

Install a unit such as `/etc/systemd/system/dispatchdesk.service`. This illustrative unit uses a virtual environment already present in the selected release. It assumes the application supports a foreground HTTP server and reads `PORT` and `DISPATCHDESK_DATA_DIR`. Adapt variable names to the actual application; systemd cannot make an application honor a setting it does not implement.

```ini
[Unit]
Description=DispatchDesk order service
After=network.target

[Service]
Type=exec
User=dispatchdesk
Group=dispatchdesk
WorkingDirectory=/srv/dispatchdesk/current
EnvironmentFile=/etc/dispatchdesk/dispatchdesk.env
Environment=PORT=8080
Environment=DISPATCHDESK_DATA_DIR=/var/lib/dispatchdesk
ExecStart=/srv/dispatchdesk/current/.venv/bin/python -m dispatchdesk
Restart=on-failure
RestartSec=3s
TimeoutStopSec=30s
UMask=0027
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
ReadWritePaths=/var/lib/dispatchdesk

[Install]
WantedBy=multi-user.target
```

`Type=exec` reports a failure if systemd cannot execute the configured program. `ExecStart` names the foreground process directly; do not put `&`, shell expansions or a shell pipeline there. If a wrapper is required, make it an audited executable with a defined exit status and signal behavior. `Restart=on-failure` can recover from a crash, but a loop that fails every three seconds is not healthy recovery. Monitor repeated starts and fix the underlying cause. A restart policy cannot repair bad configuration or preserve work held only in memory.

The unit's filesystem settings reduce accidental access, but are not a substitute for correct ownership or a security review. `ProtectSystem=strict` makes most of the filesystem read-only from the service's view; `ReadWritePaths` grants a writable state path. Test such restrictions against the real application, including temporary files, certificate access, DNS, database sockets and runtime libraries. Sandboxing options vary by systemd version and kernel. Check `systemd-analyze security dispatchdesk.service` as an inspection aid, not as a proof or a score to optimize blindly.

There is intentionally no `After=postgresql.service` dependency here. Starting after a unit does not by itself establish application readiness, and a separate database unit name varies by distribution and installation. The application needs bounded connection attempts and a clear readiness policy. If the service is deliberately coupled to a local mount or another local unit, encode the actual dependency and verify boot and recovery ordering. Do not make `/readyz` succeed merely because the process exists.

## Install, inspect and operate the unit

After placing the unit and preparing paths, ask systemd to reload definitions, then inspect before starting it:

```bash
sudo systemd-analyze verify /etc/systemd/system/dispatchdesk.service
sudo systemctl daemon-reload
sudo systemctl cat dispatchdesk.service
sudo systemctl enable --now dispatchdesk.service
sudo systemctl status --no-pager dispatchdesk.service
sudo journalctl -u dispatchdesk.service -b --no-pager -n 80
```

`systemd-analyze verify` catches some unit syntax and dependency problems; it does not validate Python imports, permissions, database schema or business behavior. `enable --now` both starts the current instance and arranges a start at the configured boot target. Read status and logs rather than treating a zero command status as the only evidence. Journal access is governed by host policy; redact credentials, customer data and tokens before sharing excerpts.

Check the local listener and application endpoints from the host:

```bash
sudo ss -ltnp
curl --fail --show-error http://127.0.0.1:8080/healthz
curl --fail --show-error http://127.0.0.1:8080/readyz
```

Confirm the listener is loopback-only for this deployment. `healthz` should indicate whether the process can respond; `readyz` should reflect whether it can safely accept routed orders under the documented dependency and drain policy. A 200 response from both endpoints does not prove an order is durable. Send a synthetic order only in a test environment, retrieve it in a separate request, and confirm its notification intent exists. Avoid using real customer data for a deployment smoke test.

When changing a unit, run `systemd-analyze verify` again, reload systemd, and restart only when the change requires it. When changing application code, deploy a new release path and deliberately update the `current` symlink. A simple release switch might look like this:

```bash
sudo ln -s /srv/dispatchdesk/releases/2026-10-02.2 /srv/dispatchdesk/current.next
sudo mv -Tf /srv/dispatchdesk/current.next /srv/dispatchdesk/current
sudo systemctl restart dispatchdesk.service
sudo systemctl status --no-pager dispatchdesk.service
```

The rename is atomic on the same filesystem, but the overall deployment is not a transaction: the new process can fail after the pointer changes. Preserve the previous release, verify application readiness and business behavior, and define how to roll back code and compatible configuration. A database migration may be irreversible or incompatible with the previous version. Keep schema evolution backward compatible through the rollout or have a tested restore plan. Do not delete the previous release or database as part of a generic cleanup command.

## Shutdown is part of correctness

Systemd normally signals the service process to stop and waits up to `TimeoutStopSec`. The application must handle its termination signal, stop accepting new work, finish or safely release in-flight acceptance transactions, stop claiming new notification work and exit within the bound. If it ignores the signal, systemd may eventually terminate it forcibly. A process restart can recover durable pending intent only if the program records ownership and retries safely.

The database commit and the HTTP response can still be separated by a network failure. The server might commit the order and lose its response before the caller receives it. The caller may retry. A production acceptance endpoint needs the idempotency contract developed later in the book; the simple chapter 10 CLI is not sufficient. Process supervision controls process lifetime but cannot infer whether an external provider sent a notification. Preserve stable intent and use reconciliation for uncertain outcomes.

## Diagnose failures at the owning layer

If the unit reports `203/EXEC`, verify the executable path, interpreter permissions, mount options and parent directory traversal rights. If it exits immediately, inspect the journal for import, configuration and database errors. If it starts but cannot bind, another process may own port 8080; identify that listener rather than killing it by name. If it can bind but the proxy later fails, compare listener address, firewall policy and proxy upstream. If the service gets permission denied on state, inspect every directory component and security-module denials before broadening access.

A restart count that rises after each release suggests a bad artifact or incompatible configuration. Restore the known-good release pointer and restart, then preserve logs and identify the failing change. A successful restart is not a rollback if a schema migration already altered data. Record the release ID, unit version, schema version and recovery action together.

## Exercises and review questions

1. Inspect a service unit from a disposable host. Which identity runs it, what can it write, where does it log and what does its restart policy do?
2. Design a graceful shutdown sequence for a request that has committed an order but has not yet returned its HTTP response. Which retry behavior makes the outcome safe?
3. Propose a release rollback where the new binary expects a new database column. Guidance: identify whether the schema change is backward compatible and what evidence is needed before switching code back.

The key questions are whether the unit has explicit inputs, whether runtime access is limited to required paths, whether readiness measures useful capability, and whether shutdown preserves durable work. Next, [Reverse Proxies on a VPS](035-reverse-proxies-on-a-vps.md) places a public HTTP boundary in front of this private service.

## Sources and verification

The upstream [`systemd.service`](https://man7.org/linux/man-pages/man5/systemd.service.5.html), [`systemd.exec`](https://man7.org/linux/man-pages/man5/systemd.exec.5.html) and [`systemd-analyze`](https://man7.org/linux/man-pages/man1/systemd-analyze.1.html) manuals and the host's installed unit manuals were inspected on 2026-10-02. The example unit is a template and was syntax-reviewed, but not installed or started on a production host; the application interface names are assumptions from the DispatchDesk contract and must be matched to a concrete implementation. No database migration, customer request or provider notification was run. Independent review is pending.
