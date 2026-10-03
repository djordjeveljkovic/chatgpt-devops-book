# Chapter 34 continuation

Status: draft; independent review pending.

## Written material
Separates release, configuration and mutable state; dedicated runtime identity; illustrative systemd unit with foreground command, environment and filesystem restrictions; install/inspect/operate/release switch; graceful shutdown and acceptance invariants; failure diagnosis; exercises.

## Concepts and terminology
Service unit, restart policy, readiness vs process state, least-privilege runtime paths, immutable release, atomic symlink switch, schema-compatible rollback, graceful drain, idempotent retry.

## Examples and cross-references
DispatchDesk assumed HTTP implementation listens at 127.0.0.1:8080 with /healthz and /readyz; HTTP program not implemented by this chapter. State path /var/lib/dispatchdesk, config /etc/dispatchdesk/dispatchdesk.env, release /srv/dispatchdesk/current. Links chapters 10, 15, 26, 31–33 and 35.

## Open threads
Match environment variable names to a concrete service before deployment; distro systemd version and SELinux/AppArmor policy differ. The sample was not installed. Independent review is pending.

## Exact next section
None. Begin Chapter 37, then request independent review before claiming completion.

## Verification
Book checker passed chapter-specific syntax and links. Systemd service, execution and systemd-analyze manuals were inspected 2026-10-02; installed service/exec manpages are available locally. A `systemd-analyze verify` attempt against a temporary root failed because the restricted environment denied user-lookup socket setup; no unit was installed or service started. No app, network listener, provider or database was started.
