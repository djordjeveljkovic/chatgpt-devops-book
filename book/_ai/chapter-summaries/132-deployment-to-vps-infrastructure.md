# Chapter 132 continuation

Status: complete

## Written material

Single-host production deployment reasoning; assumed Ubuntu/Fedora/RHEL-compatible systemd host; dedicated SSH deployment boundary and effective-config cautions; immutable release directory layout; Ubuntu apt and Fedora/RHEL-compatible dnf install examples; separate AppArmor/SELinux diagnostics; systemd unit and validation/start/status commands; archive transfer/install, permissions, same-filesystem atomic active-symlink switch, restart and local/proxy health checks; incident diagnosis, rollback and data/schema limitations; exercises, answer guidance, review questions and takeaways.

## Concepts and terminology

Deployment identity, dedicated deployment identity, release directory, shared state, service account, systemd unit, atomic directory-entry replacement, health check, rollback target, expand-and-contract migration.

## Examples and cross-references

Fictional DispatchDesk Linux binary at `/srv/dispatchdesk`, served by `dispatchdesk-api.service` on loopback. Links to Chapters 131 and 136. VPS provider, reverse proxy, systemd unit behavior and application endpoints are assumptions for the example.

## Open threads

Independent reviewer approved the corrected body hash; systemd EnvironmentFile behavior is consistent throughout, stale candidate links are diagnosed, and concurrent promotions are serialized. No server, SSH configuration, archive, unit, service, proxy or network path was executed.

## Exact next section

None. Independently approved; continue to the next unfinished chapter.

## Verification

OpenSSH, systemd service, Linux rename semantics and distro package-manager behavior checked against primary documentation 2026-10-04. `python3 tools/check_book.py --chapters 132-132` passed: four shell syntax checks and 1,406 global local links; no errors or warnings. `git diff --check` passed. Static validation does not test deployment or rollback behavior.
