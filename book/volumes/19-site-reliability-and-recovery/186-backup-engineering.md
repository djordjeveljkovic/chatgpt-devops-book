---
book: The Complete DevOps Engineering Book
volume: 19
volume_title: "Site Reliability and Recovery"
chapter: 186
title: "Backup Engineering"
slug: backup-engineering
status: complete
summary: ../../_ai/chapter-summaries/186-backup-engineering.md
---

# Chapter 186 — Backup Engineering

**Section outline:** define recoverable state and consistent capture; protect independent copies with retention and key controls; test database and object restoration with evidence of integrity and usable recovery time.

## A successful backup job is only the start

DispatchDesk's database backup dashboard is green, but a storage administrator discovers that backups are encrypted with a key whose access role was deleted. The object bucket has versioning, yet an application bug overwrote the current records and lifecycle rules removed the old versions before the team noticed. The team has copies of data but no demonstrated path to restore a usable service.

A backup is a retained copy of state that can support recovery from a defined failure. Recoverability also depends on consistency, retention, integrity, access to encryption keys, network and compute capacity, compatible software, configuration, identities, and a procedure operators can execute. A backup job's exit status proves that the job reported success; it does not prove the copy is complete, readable, isolated from the same failure, or restorable within the required time.

## Select what to protect and how to capture it

Inventory data and configuration by owner, change rate, dependencies and consequences of loss. State which sources are authoritative and which can be rebuilt. Protect the complete recovery set: database data and transaction logs, object content and metadata, encryption keys or key-recovery procedure, infrastructure definitions, service configuration, identity and access requirements, certificates, schema and application version. Do not copy live credentials into the backup; document how to restore access using protected identity systems.

Choose a capture method compatible with the application's consistency model. A database-native dump can produce a logical export for migration or object-level recovery, but it may not contain the physical state or transaction logs needed for point-in-time recovery. A filesystem or block snapshot can capture state quickly, but related volumes may need coordinated snapshots or application quiescence to represent one consistent point. For multi-service state, use application hooks, transaction barriers or an explicit write pause when required; otherwise record the consistency limits.

PostgreSQL illustrates why the method matters. Its write-ahead log (WAL) records changes and can be archived along with a base backup for point-in-time recovery. This requires a continuous usable sequence of WAL segments from the backup start through the chosen recovery point. A logical `pg_dump` is not a substitute for that physical base-backup-plus-WAL chain. Decide whether the needed recovery unit is one database object, the whole cluster or a time-specific state, then choose and test a method that can deliver it.

Object storage versioning can preserve prior object versions after overwrites or deletes, but it is not automatically an independent backup. A privileged actor, compromised role, bad lifecycle rule or account-level failure can affect both current and retained versions. Cross-account or otherwise isolated copies, retention locks and separate administrative roles reduce shared-failure risk when configured and tested. Versioning may increase storage use and needs lifecycle rules that retain versions for the intended recovery window.

## Protect copies and operate retention

Use a recovery design with multiple copies and distinct failure domains: separate credentials or accounts, geographic placement where justified, and at least one copy resistant to ordinary deletion or modification. Immutability and object lock can protect selected versions against change for a defined retention period, but they do not prevent corruption before capture, incorrect retention choices, key loss, or reading bad data back into production. Treat immutability as one layer, not proof that the backup is correct.

Encrypt in transit and at rest with keys whose lifecycle is independent of the data copies. Document key ownership, recovery authority, rotation effects, escrow or break-glass procedure and audit trail. A backup inaccessible after key revocation is not recoverable. Conversely, a broadly accessible decryption key can make a supposedly isolated backup vulnerable to compromise. Test the least-privileged recovery identity and key access without exposing key material in logs or test reports.

Set retention from recovery needs and contractual or legal obligations. Keep enough history to detect delayed corruption, malicious deletion or ransomware that may remain unnoticed for weeks. Define expiry behavior for full backups, incrementals, snapshots and transaction logs as a compatible set; deleting a base backup or a required log segment may invalidate later recovery points. Account for time zones, lifecycle delays, versioned-object delete markers and cross-region replication lag in the operational procedure. Estimate cost using retained versions, change rate, storage class and retrieval/restore charges rather than only current data size.

Monitor backup freshness, coverage, duration, size anomalies, verification failures and copy isolation. Alert when a backup is missing or older than the permitted recovery point, when a log chain has a gap, when retention policy drifts, or when a protected copy becomes writable by the ordinary production role. Send alerts to the team that owns restoration, not only to the system that runs the job. Retain audit events and restore manifests so responders can see what was copied, when, from which source and with which software/configuration version.

## Test the restore path

A restore test should use an isolated target, a named recovery point and a versioned procedure. Record who authorized it, source backup identifiers, key and identity prerequisites, network/storage capacity, start/end times, errors, integrity checks, application checks and cleanup. Never restore over production as the first test. Protect restored data with the same access controls and retention rules as the source; test environments can contain real customer information.

Validate more than file readability. For a database, check recovery logs, expected schema/version, transaction consistency and representative application queries. For object storage, verify object counts, checksums or application-level relationships and metadata required by consumers. For a service, start a representative application version, execute a safe workflow and compare behavior with the selected recovery point. A database can start successfully while required objects, encryption keys or configuration are missing.

Measure duration by phase: locate and authorize, provision isolated resources, retrieve copies, restore data and logs, rebuild dependencies, validate, and switch traffic or declare a usable recovery environment. This makes the bottleneck visible and informs the RTO/RPO design in [Chapter 187](187-disaster-recovery-and-failback.md). A restore that took 18 hours cannot substantiate a four-hour recovery objective, even if every command eventually succeeded.

Test different failures: accidental deletion, corrupt write, lost credentials, failed primary region, incomplete log archive and a compromised production administrator. Each tests a different boundary. Restore drills can be sampled and scheduled; after changing schemas, storage policies, keys, backup tooling or provider features, repeat the tests that those changes affect. Record known limits and remediate them as reliability work.

For DispatchDesk, the team adds a separate administrative account that copies database base backups and archived WAL to an isolated backup account. The recovery plan identifies which WAL chain and target time to use and how the restore identity obtains a restricted decrypt permission. The first drill finds a missing WAL segment, so the database cannot reach the selected time. They repair the archive pipeline, alert on gaps, and repeat from a clean isolated target. Then they restore the corresponding order documents and verify database references against object metadata. The team records the achieved duration and integrity results; no claim of recovery objective compliance is made until repeated tests demonstrate it under representative capacity.

Exercises:

1. A PostgreSQL base backup is readable, but one WAL segment required for the desired recovery point is missing. What can the team restore, and what must change before claiming PITR readiness?
2. An object bucket has versioning and a lifecycle policy. Which failure modes can still make its older versions unavailable or unusable?
3. A database restore succeeds in a test but its encryption key is stored only in the production account. What recovery dependency remains untested?
4. A restore meets the data-integrity checks but takes twice the target recovery time. What evidence should be recorded and how should the objective be handled?

Answer guidance: first identify the backup method. A cleanly stopped cold backup can restore its captured state without later archived WAL; a packaged online backup includes the consistency WAL required by that backup; a raw online PostgreSQL base backup requires the WAL from backup start through backup end to become consistent. A gap after a valid backup-end point blocks recovery to later targets but does not erase the valid base state; a gap in the required start-to-end range means that raw online backup is not established as restorable. Repair monitoring/retention and test from the exact backup and continuous WAL range before claiming PITR readiness. Versioning does not isolate against privileged deletion, lifecycle expiry, account loss, key loss, corruption already captured or inaccessible copies. Test the independent key-access procedure and its required authority in the recovery environment. Record actual phase durations and scope, report the target miss and assign capacity/procedure remediation or an approved objective change; never present the successful data check as proof of time compliance.

Review questions:

- Which state must be included for a usable application recovery?
- How do database dumps, snapshots and continuous archive recovery differ?
- What threats does isolation or immutability address, and which remain?
- What evidence makes a restore test meaningful?

Takeaways:

- Select a capture and recovery method that matches consistency, recovery unit and time-point requirements.
- Keep copies, credentials, keys and administration separated enough to survive the failures you plan for.
- Monitor backup chains, freshness, retention and access; versioning alone is not independent protection.
- Restore into isolation, validate application data and measure recovery phases before making resilience claims.

## Sources checked 2026-10-04

- [PostgreSQL 18 Backup and Restore](https://www.postgresql.org/docs/current/backup.html) and [Continuous Archiving and Point-in-Time Recovery](https://www.postgresql.org/docs/current/continuous-archiving.html) — database backup methods, WAL archive continuity and recovery constraints.
- [Amazon S3 Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html) and [restoring previous versions](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RestoringPreviousVersions.html) — retained versions and recovery behavior.
- [Amazon S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) — version-bound retention protection and limitations.
- [NIST SP 800-34 Rev. 1](https://csrc.nist.gov/pubs/sp/800/34/r1/final) — contingency planning and recovery exercises.

All service data, retention settings, copy identities and timings are fictional examples. No backup, WAL archive, S3 bucket, key, restore, integrity test or production record was accessed or changed.
