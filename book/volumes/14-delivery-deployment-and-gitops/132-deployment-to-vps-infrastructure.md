---
book: The Complete DevOps Engineering Book
volume: 14
volume_title: "Delivery, Deployment and GitOps"
chapter: 132
title: "Deployment to VPS Infrastructure"
slug: deployment-to-vps-infrastructure
status: complete
summary: ../../_ai/chapter-summaries/132-deployment-to-vps-infrastructure.md
---

# Chapter 132 — Deployment to VPS Infrastructure

## Why a single-host release still needs engineering

A virtual private server can be a sound first production platform for a small service. It is familiar, inexpensive to understand, and gives a team direct control over the operating system. Its simplicity does not remove release risks. A deployment that copies files over the live application, restarts it halfway through, or loses the previous version during cleanup can turn a routine change into an outage. A safe VPS process treats the host as a production system with an explicit access boundary, immutable release directories, health evidence, and a recovery path.

This chapter takes the image digest and release identity from [Chapter 131](131-release-engineering-and-artifact-promotion.md) and applies the same principle to a single VPS. The host receives one identified release, unpacks or installs it into a versioned directory, then switches the service to that release. Environment configuration stays outside the release. Chapter 136 will cover a key limit: restoring application code does not automatically reverse a database change.

The examples use a fictional DispatchDesk API installed as a Linux binary and served by systemd. The assumed host is Ubuntu Server or Fedora Server/RHEL-compatible Linux, with systemd, an existing non-root SSH account named `releasebot`, an application account named `dispatchdesk`, and a separately configured reverse proxy. Fedora and RHEL are not interchangeable for package support and subscriptions, but the commands below use systemd and GNU coreutils shared by the stated targets. The machine’s firewall permits only the proxy’s public listener; the API binds to loopback. These are starting assumptions, not steps that provision a new VPS.

## SSH boundaries and release directories

The deployment identity should have only the access needed to place a release and request a controlled service restart. Do not deploy from a personal laptop key copied into CI, share the root SSH key, or run the application as the SSH user. Use a dedicated key or short-lived SSH credential held by the trusted release job, pin the server host key through a managed known-hosts value, and scope the account to the intended server. Disable SSH agent forwarding and interactive shell access for automation when the operational model supports it. On the server, retain an administrative recovery path before changing SSH settings, and test configuration in a second session before ending the working session.

The OpenSSH server supports controls such as `AllowUsers`, `AllowGroups`, `PermitRootLogin`, and `PasswordAuthentication`, but their effective behavior depends on the full configuration, included files, and distribution defaults. Inspect the installed server’s effective configuration and test the intended account before tightening policy. Do not paste a generic hardening file over `/etc/ssh/sshd_config`; a lockout can remove the only recovery path. Restrict network access to the SSH port through the provider firewall and host firewall, and keep access logs available. Public-key authentication is an authentication method, not an authorization model: the account still needs filesystem and service permissions appropriate to deployment ([OpenSSH `sshd_config`](https://man.openbsd.org/sshd_config.5)).

Use a layout that keeps each release separate from mutable state:

```text
/srv/dispatchdesk/
├── current -> releases/2026-10-04T120000Z-9fabc123
├── releases/
│   ├── 2026-10-04T120000Z-9fabc123/
│   └── 2026-10-03T171500Z-812def45/
└── shared/
    └── uploads/
/etc/dispatchdesk/api.env
```

The directory names are illustrative release identifiers, not measured build IDs. The deploy account can create release content and update the `current` link. The `dispatchdesk` service account can read and execute the selected release but cannot modify it. The environment file and persistent uploads are outside versioned release directories, so switching versions does not erase runtime data or expose secrets through an artifact. On real systems, check every parent directory’s ownership and permissions; an unprivileged writer must not be able to replace a parent symlink and redirect privileged operations.

Install host packages through the distribution’s package manager, not by running an unverified install script from a pipeline. If the deployment host needs transfer and health-check tools, Ubuntu uses `apt` while Fedora and RHEL-compatible systems use `dnf` (RHEL may require an entitled repository):

```bash
# Ubuntu Server; run interactively as an administrator.
sudo apt-get update
sudo apt-get install --yes rsync curl

# Fedora Server or an entitled RHEL-compatible host.
sudo dnf install --assumeyes rsync curl
```

Check package availability for the image and release you operate; these commands intentionally do not change the SSH daemon or firewall. Create service and deployment users through the host’s approved account-management process. Keep secrets in a root-readable environment file or a dedicated secret service. On Ubuntu, AppArmor may constrain the service; Fedora and RHEL commonly enforce SELinux. If an access denial follows a path or unit change, inspect the relevant audit evidence and correct the profile or file label. Do not solve a path problem by disabling mandatory access control.

## Define a systemd service contract

A system service makes process ownership, working directory, restart behavior, and logs explicit. This illustrative unit assumes the release contains `bin/dispatchdesk-api`, which consumes configuration variables supplied by systemd, listens on `127.0.0.1:8080`, and exposes `/healthz`. Those are fictional application interfaces. Create `/etc/systemd/system/dispatchdesk-api.service` as root with contents like:

```ini
[Unit]
Description=DispatchDesk API
After=network.target

[Service]
Type=simple
User=dispatchdesk
Group=dispatchdesk
WorkingDirectory=/srv/dispatchdesk/current
EnvironmentFile=/etc/dispatchdesk/api.env
ExecStart=/srv/dispatchdesk/current/bin/dispatchdesk-api
Restart=on-failure
RestartSec=3s
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

`User` and `Group` keep the process away from root privileges. `WorkingDirectory` gives the binary a predictable base for relative paths; the application should still use explicit paths for persistent data. The system service manager reads `EnvironmentFile` and supplies its variables to the process environment before starting the unprivileged service user. The application consumes the variables; it does not need direct permission to open the environment file. Store secrets in a root-owned file with permissions that allow the manager to read it, and keep the service account from reading it directly unless the application has a separate, explicit file-based configuration design. `Restart=on-failure` asks systemd to restart a process that exits unsuccessfully; it does not make a broken application healthy. `NoNewPrivileges` and `PrivateTmp` are useful restrictions, not a complete sandbox, and should be tested with the application’s needs.

After saving the unit, inspect it and ask systemd to reload unit definitions. Enable startup at boot and start it only after the first release and environment file exist:

```bash
sudo systemd-analyze verify /etc/systemd/system/dispatchdesk-api.service
sudo systemctl daemon-reload
sudo systemctl enable dispatchdesk-api.service
sudo systemctl start dispatchdesk-api.service
sudo systemctl status --no-pager dispatchdesk-api.service
sudo journalctl -u dispatchdesk-api.service --since '10 minutes ago' --no-pager
```

`systemd-analyze verify` can catch many unit syntax and dependency problems but does not validate application behavior. `enable` creates boot-time activation links; `start` launches now. `status` and `journalctl` provide evidence from systemd, not an end-to-end check through the public proxy. Ubuntu and Fedora/RHEL both use systemd commands here; their package versions, SELinux/AppArmor policy, filesystem layout, and provider firewall controls may differ. The `systemd.service` manual describes service process supervision and its limits ([systemd service documentation](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)).

## Install a release and switch atomically

The release job should fetch or transfer the exact artifact selected in Chapter 131. Do not check out source and compile on the production host: it expands the production trust boundary and makes the host’s compiler, dependencies, and mutable package state part of the build. If the application is delivered as an archive, verify its recorded checksum or signature before extraction. The archive must not contain absolute paths, `..` traversal entries, devices, or unexpected symlinks. Place the extracted content in a new, uniquely named release directory, then set ownership and restrictive modes before activation.

Assume a trusted CI runner has authenticated to `releasebot@vps.example.net`, verified the host key, and downloaded an approved archive as `dispatchdesk-api.tar.gz`. It transfers the archive to a staging path. On the host, a tightly controlled deployment command validates and unpacks it; the following example shows the critical filesystem operations for an administrator-run session, not a complete archive-validation tool:

```bash
set -euo pipefail

release_id='2026-10-04T120000Z-9fabc123'
release_root='/srv/dispatchdesk/releases'
release_path="${release_root}/${release_id}"
current_link='/srv/dispatchdesk/current'
candidate_link='/srv/dispatchdesk/current.next'
archive='/var/tmp/dispatchdesk-api.tar.gz'

test ! -e "$release_path"
if [[ -e "$candidate_link" || -L "$candidate_link" ]]; then
  printf 'Candidate link already exists; inspect it before retrying\n' >&2
  exit 1
fi
install -d -o root -g dispatchdesk -m 0750 "$release_path"
tar --extract --gzip --file "$archive" --directory "$release_path" \
  --no-same-owner --no-same-permissions
chown -R root:dispatchdesk "$release_path"
find "$release_path" -type d -exec chmod 0750 {} +
find "$release_path" -type f -exec chmod 0640 {} +
chmod 0750 "$release_path/bin/dispatchdesk-api"

ln -s "releases/${release_id}" "$candidate_link"
mv -Tf "$candidate_link" "$current_link"
systemctl restart dispatchdesk-api.service
```

In production, have a root-owned wrapper validate the release identifier, verify the archive’s trusted checksum or signature, reject unsafe archive members, and accept only an approved artifact. Do not give `releasebot` arbitrary root access to `tar`, `find`, or a shell. The example’s `tar` flags avoid preserving archive ownership and permissions, but they do not make an untrusted archive safe. Configure a per-service release lock or CI concurrency group so two promotions cannot race over `current.next`. If a prior attempt left that link behind, inspect its target and remove it only after confirming it points within the known release tree; do not automatically follow or overwrite an unexpected symlink. The selected path is under the service’s release tree; the candidate link and current link are in the same directory and filesystem. `mv -T` is a GNU coreutils option available on the target GNU/Linux distributions. Renaming the candidate symlink over the old symlink is atomic at the directory-entry level when it is on the same filesystem: readers see the old link or the new one, not a missing `current` path. Atomic pointer replacement does not make process restart, database migration, or the full deployment transaction atomic ([Linux `rename(2)`](https://man7.org/linux/man-pages/man2/rename.2.html)).

Before sending traffic, inspect the service and check the local health endpoint using the host’s expected service identity and proxy route:

```bash
systemctl is-active --quiet dispatchdesk-api.service
curl --fail --silent --show-error http://127.0.0.1:8080/healthz
```

The example assumes the endpoint is implemented and that the operator has permission to query systemd. A process can be active while returning a failing health response; both checks matter. Also make a request through the reverse proxy and verify the reported release identity if the application safely exposes one. Treat response samples as evidence from the current request, not proof that every user path works. Only after those checks pass should the release job declare the deployment successful and retain its release record.

## Failure diagnosis, rollback, and limits

If the process fails to start, first stop rollout. Read `systemctl status` and the service journal, verify the `current` target, inspect ownership and executable mode, and confirm that the environment file exists with the expected permissions. A missing shared library, incompatible configuration, or denied file access may look like an application defect. On Fedora/RHEL, check recent SELinux AVC records when audit tooling is present; on Ubuntu, inspect AppArmor status and kernel/audit logs. Restore the intended security policy and relabel only the affected path where appropriate. Do not recursively make the tree world-writable or turn off SELinux/AppArmor to make the service start.

For a code-only failure, point `current` back to the previous retained release using the same candidate-link-and-rename operation, restart the service, then repeat the local and proxy health checks. Keep enough old releases and disk capacity for the recovery window, but remove them only after the deployment has been stable and the rollback target is known. Keep the release directory immutable after activation; operators should not hot-edit a file because doing so makes its recorded identity false.

A symlink rollback restores application files, not external state. It does not undo a database migration, message format change, or a request already processed by the failed version. Use backward-compatible expand-and-contract schema changes, preserve a backup plan, and make rollback a tested release procedure rather than an assumption. If the candidate is incompatible with the current schema, do not restart the old binary until compatibility is assessed. A single VPS also remains one failure domain: a kernel issue, disk loss, provider outage, or damaged host can make every release unavailable. Host snapshots and backups are recovery inputs, not substitutes for tested restore procedures.

## Exercises

1. A deployment account can log in as root and run arbitrary commands. Redesign the access boundary so a trusted release job can publish a release and restart only the DispatchDesk service.
2. During rollout, `systemctl is-active` reports active but the health endpoint returns HTTP 500. What evidence do you inspect, and when is the deployment considered successful?
3. After a restart, systemd reports that it could not load `/etc/dispatchdesk/api.env`, or the process starts but reports that a required setting is absent. How do you distinguish a manager read failure from an application configuration failure without exposing secret values?
4. A symlink switch and restart succeed, but the service fails because a migration removed a column expected by the old binary. Why is switching the link back insufficient, and what compatibility approach avoids this rollback trap?
5. Why must the staging link and `current` link be on the same filesystem for the illustrated atomic replacement? What does the atomic rename guarantee, and what does it not guarantee?

### Answer guidance

1. Use a dedicated SSH identity and non-root account, pin the host key, and transfer only a verified artifact. Give that account a narrowly scoped deployment interface or root-owned wrapper and only the service restart permission required. Keep the application process under its own unprivileged service account. Test administrative recovery before altering SSH policy.
2. Inspect the unit state, recent journal, current symlink, application logs and configuration, then query the endpoint locally and through the proxy. The release is not successful until the agreed health checks pass. An active process only proves systemd sees a running process.
3. For a systemd environment-file load failure, inspect the unit state and journal, then check that the path exists and the service manager can traverse parent directories and read the root-owned file. For an application-reported missing setting, confirm that the unit references the intended file, reload unit configuration if it changed, restart, and inspect safe application diagnostics that report key presence without printing secret values. This example does not require the service account to open `api.env`. If the application instead reads a file directly, design a separate restricted ownership/group mode for that file. In either case inspect audit/kernel denial evidence and correct the specific owner/mode or platform policy; do not broaden permissions indiscriminately or disable mandatory controls.
4. The database is shared external state; changing code does not restore the removed column. Use additive migrations, deploy code that tolerates both old and new schemas, migrate data, and remove obsolete schema only after old versions are out of service.
5. A same-filesystem rename can replace the directory entry atomically; a cross-filesystem move becomes copy-and-delete and can expose intermediate state or fail with a cross-device error. The rename protects observers from seeing a missing pointer. It does not guarantee the restarted process is healthy, revert data, or make proxy traffic and database changes atomic.

## Review questions

- Which host responsibilities are trusted to the release job, and which remain under administrator control?
- Why should the deployment user, service user, and root have separate roles?
- What is the distinction between an atomic symlink switch and an atomic application release?
- Which evidence proves that a new release is healthy from the host and from a client path?
- Which changes cannot be reversed by restoring the previous application directory?

## Takeaways

- Give deployment automation a dedicated, narrow SSH identity and preserve an administrative recovery path.
- Install each artifact into a new release directory; keep secrets and persistent state outside it.
- Run the application as its own unprivileged systemd service and validate both process and request health.
- Use a same-filesystem atomic symlink replacement for the active release pointer, then restart and verify.
- Rollback restores application files only; schema, messages, and external side effects need their own compatibility and recovery plan.

## Further reading

- [OpenSSH server configuration](https://man.openbsd.org/sshd_config.5)
- [systemd service units](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)
- [Linux rename semantics](https://man7.org/linux/man-pages/man2/rename.2.html)
- [Chapter 131 — Release Engineering and Artifact Promotion](131-release-engineering-and-artifact-promotion.md)
- [Chapter 136 — Database and Message Compatibility](136-database-and-message-compatibility.md)

Sources reviewed 2026-10-04. Commands and systemd unit are illustrative; no VPS, SSH server, archive, systemd service, or network path was modified or tested.
