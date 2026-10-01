---
book: The Complete DevOps Engineering Book
volume: 2
volume_title: "Linux and Automation"
chapter: 16
title: "Systemd and Service Lifecycles"
slug: systemd-and-service-lifecycles
status: complete
summary: ../../_ai/chapter-summaries/016-systemd-and-service-lifecycles.md
---

# Chapter 16 — Systemd and Service Lifecycles

## Why this matters

Harbor's first worker ran in a terminal. It disappeared after a disconnect, and nobody knew whether the missing notifications reflected a dead process or a provider failure. Starting it again restored activity, but left the underlying lifecycle undocumented. A supervisor makes process ownership, restart decisions, logs, and shutdown behavior explicit.

Systemd is the service manager used by the Ubuntu, Fedora, and RHEL baselines in this book. It can start processes during boot, monitor them, group their descendants, and apply an execution environment. It cannot infer that DispatchDesk has committed an order correctly or delivered a notification once. The service manager owns process lifecycle; the application owns business correctness.

## Units describe managed resources

A unit is a configuration object. Service units describe supervised commands; socket, timer, mount, and target units describe other resources and coordination. A target groups units rather than necessarily representing a process. The `.service` suffix identifies the examples here.

System units and user units belong to different managers. A system unit may run with a dedicated service identity selected by `User=`. A user unit runs in that user's manager and should be controlled with `systemctl --user`. Confusing these scopes produces misleading results: the same short unit name can exist in both. User-manager availability after logout depends on the host's session and lingering configuration; do not assume a user unit is a boot-persistent production deployment.

Administrative system units commonly live under `/etc/systemd/system`; vendor units live in distribution-managed directories. Inspect `systemctl cat` and the reported fragment path instead of guessing the vendor path. Keep custom configuration in supported overrides rather than editing a packaged file that an upgrade may replace.

A service's active state describes the manager's lifecycle view. A long-running process can be active while unable to accept orders. A completed oneshot can be inactive after succeeding, or remain logically active when configured accordingly. Read the unit type, result, and main-process information together. [Upstream systemd service manual](https://man7.org/linux/man-pages/man5/systemd.service.5.html).

## A minimal, complete lifecycle lab

Use this lab on a disposable Linux VM with a working user systemd manager. It launches only a foreground sleep process and demonstrates ownership without pretending to run DispatchDesk. Confirm that `command -v sleep` resolves to `/usr/bin/sleep` on that VM; substitute its actual absolute path if necessary.

Create `~/.config/systemd/user/dispatchdesk-lifecycle-lab.service` with this inline content:

```ini
[Unit]
Description=DispatchDesk lifecycle practice

[Service]
Type=exec
ExecStart=/usr/bin/sleep infinity
Restart=on-failure
RestartSec=3s
TimeoutStopSec=10s
```

The unit has no installation section because this lab is started explicitly and is not enabled at login or boot. `Type=exec` gives the manager a startup boundary at successful execution of the command. That catches some setup failures more accurately than treating creation of the process alone as startup; it still does not signal application readiness. A program implementing the notification protocol can use `Type=notify`, but selecting that type without implementing the protocol makes startup wait for a message that never arrives.

With the file created in the intended user configuration directory, run:

```bash
systemd-analyze --user verify "$HOME/.config/systemd/user/dispatchdesk-lifecycle-lab.service"
systemctl --user daemon-reload
systemctl --user start dispatchdesk-lifecycle-lab.service
systemctl --user status dispatchdesk-lifecycle-lab.service --no-pager
systemctl --user show dispatchdesk-lifecycle-lab.service -p MainPID -p ActiveState -p SubState -p Result
systemctl --user stop dispatchdesk-lifecycle-lab.service
systemctl --user is-active dispatchdesk-lifecycle-lab.service
```

The final command should report inactive and return nonzero after a successful stop; interpret it as an assertion about state, not a failed stop operation. Verification checks configuration and detectable dependencies, not the whole runtime behavior. If the user bus is unavailable, resolve the VM/session setup rather than mixing in system-manager commands.

Remove only the specific lab unit file after stopping it, then reload the user manager. Do not remove the entire user unit directory, which may contain unrelated services. The author successfully verified the extracted practice unit with systemd-analyze 262 outside sandbox restrictions; the full manager lifecycle remains a reader VM exercise.

## Ordering is not readiness

`After=` establishes ordering between units involved in a transaction. It does not itself pull another unit into that transaction. `Wants=` requests a dependency with comparatively weak coupling; `Requires=` provides stronger dependency relationships, but it still needs suitable ordering when sequence matters. More dependencies are not automatically safer: unnecessary coupling can make an unrelated failure prevent useful work.

A network-online target is a boot coordination point, not a promise that a remote database or provider remains reachable forever. A DispatchDesk worker needs bounded retries and clear failure reporting when dependencies disappear after startup. A unit dependency cannot replace those runtime behaviors.

Similarly, ordering a client after a `Type=exec` server means its executable was launched, not that its listening socket and durable store are ready. Prefer an application readiness protocol or an explicit bounded check designed for the dependent interaction. Do not add arbitrary sleeps to hide initialization uncertainty. Boot speed and load will eventually defeat an assumed delay.

## Express the execution contract

A production unit should describe the runtime identity, working directory, program, configuration, mutable state, and stop policy. The following is a design example for a later foreground DispatchDesk runtime, not a runnable extension of Chapter 10's one-shot CLI. It assumes an administrator has created the `dispatchdesk` account, deployed `/opt/dispatchdesk/current/service.py` and its interpreter, and defined the application's data-path option.

```ini
[Unit]
Description=DispatchDesk order service

[Service]
Type=exec
User=dispatchdesk
Group=dispatchdesk
WorkingDirectory=/opt/dispatchdesk/current
ExecStart=/usr/bin/python3 -u /opt/dispatchdesk/current/service.py --data-dir /var/lib/dispatchdesk
StateDirectory=dispatchdesk
StateDirectoryMode=0750
UMask=0027
Restart=on-failure
RestartSec=5s
TimeoutStopSec=45s
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes

[Install]
WantedBy=multi-user.target
```

`StateDirectory=` arranges a designated persistent state location under the system manager's state hierarchy and accounts for its access under filesystem protection. Validate its actual ownership and access on the host, including mandatory policy. The application reads executable release content but writes its state elsewhere, matching Chapter 14's design. Its foreground process gives the manager a direct lifecycle owner.

The hardening options restrict the environment. They can also reveal undeclared requirements, such as an application writing beside its executable or relying on a file in a home directory. Test intended operations and recovery under the same settings; adding restrictions without testing is not proof of secure operation. The current upstream manual includes newer features than some baseline packages, so check `systemd --version` and the host's installed manuals when extending this deliberately conservative example. [Execution environment and directory options](https://man7.org/linux/man-pages/man5/systemd.exec.5.html).

`ExecStart=` is not an arbitrary interactive-shell command line. Shell pipelines and redirections require an explicitly invoked shell, bringing quoting and signal ownership back into the design. Prefer direct execution when possible. Do not embed credentials in unit arguments or assume the unit file is a secret store. Later secrets chapters develop protected delivery; this example has no secret values.

## Restart policy must support recovery

`Restart=on-failure` requests restart for failures recognized by the manager; it does not validate the data or classify every business error. A clean application exit may not trigger that policy. An explicit stop does not behave like an accidental failure requiring immediate resurrection. Choose restart behavior around the program's exit contract.

`RestartSec=` spaces restarts. Start-rate limiting can eventually prevent repeated starts after a rapid failure loop. Inspect the error that caused the loop before clearing the failed state. A missing configuration file, corrupt store, or denied directory will not be repaired by faster restarts.

Shutdown uses the unit's process-management policy and timeout. The application must respond to termination with the bounded drain described in Chapter 15. After the deadline, forced termination may occur according to configuration; external notification outcomes can remain ambiguous. Do not use a timeout that contradicts request/dependency deadlines, and do not promise cleanup on forced termination.

## Read logs and effective configuration

For a managed system service, useful read-only observations include:

```bash
systemctl cat dispatchdesk.service
systemctl show dispatchdesk.service -p FragmentPath -p DropInPaths -p MainPID -p Result -p ExecMainStatus
journalctl -u dispatchdesk.service --since '30 minutes ago' --no-pager
```

Run these only on a host where the named service exists and you have authorized read access. Logs may contain restricted identifiers; share a sanitized incident extract rather than an entire journal. Unit filtering identifies lifecycle context, while a bounded interval keeps evidence relevant. Add boot selection when investigating an earlier boot. Journal retention is a host configuration, so absence of old records is not proof that nothing happened. [Journal query manual](https://man7.org/linux/man-pages/man1/journalctl.1.html).

`systemctl edit dispatchdesk.service` can create a supported drop-in for an administrative override. Inspect the merged configuration afterward. Replacing an existing `ExecStart=` often requires clearing the prior list before setting a replacement, so follow the directive's documented merge behavior. A small override can have a large effect; store its intended content in the deployment's reviewable configuration.

`daemon-reload` asks the manager to reread unit configuration. It does not itself restart the application. `reload` requests the service's implemented reload behavior; not every service supports it. `restart` changes its process lifetime. Verify which layer a proposed configuration change affects before choosing an operation. [Systemctl command semantics](https://man7.org/linux/man-pages/man1/systemctl.1.html).

## Recover a restart loop

Harbor deploys a new release, then observes repeated starts followed by failure. Capture unit status, result, recent journal entries, and the effective command. The journal reports the interpreter launched successfully but the application cannot find its configuration. That distinguishes a program setup failure from a missing executable and from an unreachable provider.

The new unit override changed `WorkingDirectory=` while the application still resolved a relative configuration path. Restore the known configuration contract through an explicit absolute path or a reviewed working-directory correction. Validate the merged unit, reload the manager if unit content changed, and deliberately restart only this service. If start limiting was reached, clear the relevant failed state as part of that recovery after correcting the cause.

Then verify process stability and application behavior separately. Check `/healthz`, `/readyz`, a controlled order acceptance, paired durable notification intent, and worker progress using the appropriate later runtime tests. A green `systemctl` state establishes process lifecycle only. Retain the previous release and its unit configuration until rollback risks, especially data compatibility, are understood.

## Exercises and takeaways

1. Run the user-unit lab in a disposable VM. Explain why it needs no `enable` operation. Guidance: explicit start exercises lifecycle; enabling arranges activation through installation relationships.
2. Explain why `After=database.service` alone does not establish a ready database. Guidance: ordering and dependency inclusion differ, and readiness depends on the database's startup protocol.
3. A unit file changes but its process continues unchanged after daemon-reload. Is that surprising? Guidance: rereading manager configuration is distinct from restarting a running program.
4. Plan a restart-loop investigation without changing restart intervals first. Guidance: effective command/context, result, journal interval, and application exit contract should reveal the failing requirement.

A supervised service is a documented process contract. Keep ownership direct, distinguish startup from readiness, and align restart and stop behavior with durable recovery. Continue to [Chapter 17](017-packages-and-linux-distributions.md) for the provenance and upgrade workflow behind the interpreter and other deployed dependencies.
