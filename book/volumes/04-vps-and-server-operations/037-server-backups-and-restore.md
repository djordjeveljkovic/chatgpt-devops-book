---
book: The Complete DevOps Engineering Book
volume: 4
volume_title: "VPS and Server Operations"
chapter: 37
title: "Server Backups and Restore"
slug: server-backups-and-restore
status: draft
summary: ../../_ai/chapter-summaries/037-server-backups-and-restore.md
---

# Chapter 37 — Server Backups and Restore

## Recovery starts with a promise

A backup matters only if it contains the required data, survives the failure it is meant to address, and can be restored within the agreed time. A green job status is evidence that a program completed; it does not prove that the right files were selected, that database transactions are consistent, that credentials remain available, or that a replacement host can serve work again.

Harbor's DispatchDesk VPS stores application code, operating-system configuration, secrets, logs and order data. Those assets have different recovery paths. A replacement VPS can be reprovisioned from documented configuration and trusted artifacts. PostgreSQL needs a database-consistent backup and restore process, described in [Chapter 36](036-database-and-cache-operations-on-one-host.md). Redis can be rebuilt if it remains only a derived cache. The backup plan should identify each source of truth, its recovery point objective (RPO), its recovery time objective (RTO), the accountable owner and the test that proves recovery.

For example, an RPO of one hour means the team is willing to lose at most one hour of committed changes under the defined failure; an RTO of four hours means service should be restored within four hours of the incident start. These are targets to test, not guarantees produced by selecting a backup frequency. Include detection, access recovery, host provisioning, data transfer, validation, DNS or traffic switching and operator availability in the elapsed time.

## Separate reproducible host state from durable data

Keep a record of the operating-system image, package inventory, configuration management revision, service unit, firewall policy, application artifact digest, database version and storage layout. The configuration repository must not contain plaintext production credentials. Store secrets separately with restricted access and a tested rotation path. A provider image or snapshot can shorten replacement time, but it may preserve a compromised host, depend on the same account or region, and fail to capture application-consistent database state. It is one recovery input, not the whole plan.

Use a backup destination outside the host's ordinary failure boundary. Off-host means a stolen credential or operator command on the VPS cannot silently erase every copy. Separate credentials and administrative roles, use encryption, restrict repository write and deletion access, and consider immutable retention controls where the chosen storage supports them. Keep the recovery credential and encryption key available through a separate, controlled procedure. An encrypted repository whose password is lost is not a useful recovery copy.

Restic is one example of a client-side encrypted file-backup tool. It can write to local or remote backends, but the backend's durability, account security, lifecycle rules, billing and region remain the operator's responsibility. Pin and test a supported version and backend configuration. Do not assume a local repository on the same VPS protects against VPS or disk loss.

The following shell fragment assumes an already initialized remote repository, a restricted password file, and a reviewed Restic installation. It backs up configuration and immutable releases, not the live PostgreSQL data directory. Adapt paths to the target host. Avoid `set -x` because tracing can expose credentials and repository details.

```bash
set -eu
umask 077
export RESTIC_REPOSITORY='sftp:backup-user@backup.example.net:/srv/restic/dispatchdesk'
export RESTIC_PASSWORD_FILE='/etc/dispatchdesk/restic-password'

restic snapshots --latest 1
restic backup \
  --host harbor-dispatchdesk \
  --tag host-config-and-releases \
  /etc/dispatchdesk \
  /etc/systemd/system/dispatchdesk.service \
  /srv/dispatchdesk/releases
restic check
```

The repository address is fictional and contains no password. Set up the SFTP account and key through the provider's supported process, restrict it to the required repository, and verify host-key identity. The password file must be readable only by the intended backup identity and included in a separately protected recovery procedure; do not casually include it in its own repository. For a production scheduled job, provide repository variables through a restricted service environment and alert on nonzero exit, missed schedules and stale snapshots. The `snapshots` line is an inspection command; it is not a retention policy. Apply retention only after deciding what recovery dates must remain and testing the effect in the selected repository.

Back up active data using its consistency mechanism. PostgreSQL's logical dump, base backup and continuous-archive methods have different recovery properties. An ordinary file walk over a running database directory can capture files from different moments and is not a supported substitute. A filesystem or provider snapshot is valid only when the database and storage procedure make it consistent, including write-ahead logs. SQLite also has online backup mechanisms; copying only the main database file while it is being written can miss journal or WAL state. Either coordinate an application-safe snapshot, stop the writer in a controlled window, or use the database's supported backup tool.

## Restore to an isolated destination

A restore rehearsal should not overwrite production. Select a known snapshot, verify its host and timestamp, and restore into a new empty directory with enough space. The Restic password and backend credentials must come from the recovery procedure, not from memory or a shell command saved in a ticket.

```bash
set -eu
umask 077
export RESTIC_REPOSITORY='sftp:backup-user@backup.example.net:/srv/restic/dispatchdesk'
export RESTIC_PASSWORD_FILE='/etc/dispatchdesk/restic-password'

restic snapshots --host harbor-dispatchdesk
restore_dir=$(mktemp -d)
restic restore SNAPSHOT_ID --target "$restore_dir"
find "$restore_dir" -maxdepth 5 -type f -print
```

Replace `SNAPSHOT_ID` only after reviewing the snapshot listing. Restic recreates the paths recorded in the snapshot under the target directory. Inspect the resulting tree, compare expected configuration and release files, verify checksums where recorded, and confirm permissions and ownership requirements before using anything. Never point this isolated rehearsal at `/` or the live application's release path. The `find` command is an inventory, not proof of file correctness.

For a full application recovery, provision a clean replacement host, apply its hardening baseline, restore configuration through a controlled secret path, deploy the verified artifact, restore PostgreSQL with the chosen procedure and verify the application against the restored data. Keep the replacement isolated from real customers and external notification providers until validation is complete. Synthetic checks should confirm that accepted orders and notification intents remain paired, readiness behaves correctly and the restored service can start. Then measure elapsed time and compare actual recovery point with RPO and RTO. Document every manual action that consumed time.

Do not use an in-place restore as the first test. A restore may overwrite current files, and interruption can leave a mixed state. If production data must be restored, first capture current state where feasible, stop or drain writers, preserve evidence, get the incident owner's approval under the recovery procedure, and follow the database-specific runbook. Avoid broad restore deletion options unless the exact deletion set has been reviewed and tested.

## Retention, integrity and access

Define retention around business requirements, legal obligations, recovery scenarios and cost. More snapshots do not help if all credentials have broad delete access. Monitor repository growth, failed reads, last successful snapshot age and remaining backend capacity. Periodically verify repository metadata and read data according to the tool's documented integrity check. A checksum detects some corruption; it does not prove semantic application consistency. Keep at least one recovery path independent from the source host's administrative credentials.

Backups can contain customer data, secrets, encryption keys and security configuration. Encrypt in transit and at rest, restrict operators, audit reads and deletion, and set retention that accounts for sensitive-data removal requirements. Encryption does not prevent an authorized repository user from deleting encrypted objects. Test credential rotation and recovery after the original operator is unavailable. Protect the backup control plane as carefully as the production host.

## Diagnose a failed recovery path

If a scheduled backup is missing, check the timer or scheduler, service exit code, network path, repository credentials, destination capacity and logs. Distinguish a backup that never started from one that could not read files or could not finalize its snapshot. Do not suppress a nonzero result to keep an alert quiet. If repository integrity checks fail, stop pruning and preserve the repository for investigation; follow the backup tool's repair procedure on a safe copy.

If a restore is slow, record data volume, backend throughput, host provisioning duration and validation steps. Increasing parallelism may compete with the production service or provider quotas. If files restore but the application fails, identify missing runtime packages, secrets, schema compatibility or ownership. Correct the recovery record and rehearse again. A failed exercise is valuable evidence only when it changes the recovery plan.

## Exercises and review questions

1. Write a recovery table for application code, operating-system configuration, secrets, PostgreSQL orders and Redis cache. Give each an RPO, RTO, owner and verification step.
2. What failure does a provider disk snapshot survive? Which account, region, database consistency and encryption-key risks remain?
3. Restore one non-sensitive sample directory from a disposable Restic repository into a temporary path. Verify file contents and capture the duration. Do not use a production repository for the exercise.
4. Your database snapshot is recent but the decryption password is unavailable. How should the recovery plan detect and prevent this failure?

The test of a backup is a controlled restore with the application-level invariants checked. Continue to [Patching and Maintenance Windows](038-patching-and-maintenance-windows.md), where preserving a recoverable baseline makes routine change safer.

## Sources and verification

Restic 0.19.1's official [backup](https://restic.readthedocs.io/en/stable/040_backup.html), [restore](https://restic.readthedocs.io/en/stable/050_restore.html), [repository check](https://restic.readthedocs.io/en/stable/045_working_with_repos.html) and [quickstart](https://restic.readthedocs.io/en/stable/010_introduction.html) documentation was inspected on 2026-10-02. PostgreSQL backup and SQLite online-backup boundaries are covered in Chapter 36 and its primary-source links. This chapter's shell samples passed syntax checks, but Restic, an SFTP backend, database restore and replacement-host recovery were not run. Independent review is pending.
