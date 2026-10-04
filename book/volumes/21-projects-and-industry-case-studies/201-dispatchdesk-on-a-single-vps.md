---
book: The Complete DevOps Engineering Book
volume: 21
volume_title: "Projects and Industry Case Studies"
chapter: 201
title: "DispatchDesk on a Single VPS"
slug: dispatchdesk-on-a-single-vps
status: complete
summary: ../../_ai/chapter-summaries/201-dispatchdesk-on-a-single-vps.md
---

# Chapter 201 — DispatchDesk on a Single VPS

**Section outline:** initial workload and operational contract; native services and first release; a first failure and measured improvement.

## Start with a service contract

DispatchDesk begins as a small order-tracking product run by two engineers. A customer submits an order, staff update its status, and the service sends email notifications. The first architecture is intentionally modest: one Linux virtual private server (VPS), one application process, PostgreSQL on the same host, a reverse proxy for TLS, and an external object store for uploaded documents. The goal is to learn the workload and build safe operations, not to imitate a larger company.

Write down the operating contract before provisioning: who uses the service, when it must be available, which data is authoritative, how quickly an interruption must be repaired, how much recent data can be lost, what traffic is expected, and who responds. The team agrees on a weekday support window, a four-hour restoration target for a host loss, and a maximum one-hour order recovery point. These are initial business targets, not demonstrated results. The [SLO chapter](../19-site-reliability-and-recovery/181-slis-slos-and-error-budgets.md) later develops the measurement model.

The service's lifecycle needs a named owner even when everyone shares a small rota. Record dependencies: domain/DNS, registrar, TLS renewal, VPS access, database, object storage, mail provider, source control, package repositories and backup keys. A single-host architecture has a small bill but concentrates compute, storage and database failure. Make that limitation explicit to customers and staff.

## Build a repeatable first release

Create a least-privilege Linux account for deployment and a separate database role for the application. Keep administrator access distinct from routine application access. Configure the host firewall for required inbound traffic only; restrict database listening to local/private interfaces. Use a reverse proxy to terminate TLS and forward to an application bound to loopback. Store secrets outside source control with permissions limited to the service identity, and document rotation and recovery.

The application runs as a system service with an explicit working directory, environment file, restart policy and resource limits appropriate to the host. Use a supported runtime and package versions; log structured request and error events to the system journal or a managed log destination. Health endpoints should distinguish process liveness from ability to serve requests. Avoid exposing stack traces or secret values to clients or logs. Chapters 011–020 cover the Linux lifecycle, permissions and resource boundaries; Chapter 132 develops a VPS deployment procedure.

Automate a release that tests code, builds one immutable artifact, records its revision and deploys through a controlled path. Separate configuration from the artifact. Before changing production, verify backup freshness, disk capacity and rollback compatibility. Use a small maintenance window while the service is new; record the deployed digest and operator. A Git tag is not proof that a host runs that version; collect runtime version evidence.

For database changes, use expand-and-contract migrations: add compatible schema first, deploy code that supports old and new forms, migrate data, then remove obsolete fields after rollback is no longer needed. Take and test backups separately from the host. A local copy on the same disk does not survive host or account loss. Chapter 186 covers independent backup and restore verification.

## Respond to the first failure

In the second month, a report export fills the root filesystem. PostgreSQL begins failing writes and order updates return errors. The reverse proxy still answers a basic health check, so external uptime alone hides the degraded user outcome. The on-call engineer acknowledges the issue, checks disk and database state without deleting files blindly, disables the expensive export, expands disk capacity through the provider procedure and verifies database recovery and representative order workflows.

After service returns, the team checks whether committed transactions are present and compares export state. It retains logs and a brief timeline, identifies the unbounded temporary-file behavior, adds a disk-space alert with a clear owner and tests export cleanup with a bounded temporary directory. The incident follow-up is blameless and records what made the failure hard to detect. [Chapter 183](../19-site-reliability-and-recovery/183-incident-command-and-communication.md) covers response coordination; Chapter 185 covers post-incident learning.

The team measures request errors, successful order writes, latency, database health, disk use, backup age and restore-test results. It does not claim high availability: a host reboot interrupts the whole application. It records the evidence needed to decide whether a second host, managed database or queue is justified. Scale is a response to measured demand, risk or operating burden, not a milestone that every product must reach.

Exercises:

1. The VPS provider reports a host failure. What does the team need to restore service within four hours?
2. Disk use reaches 95%, but the API's liveness probe passes. Which signals and user journeys should guide response?
3. A schema migration succeeds, then the application rollback cannot read the new schema. How should migration sequencing change?
4. The service has no tested independent database backup. Which launch claim is unsafe?

Answer guidance: recovery access, image/configuration, database and object restore, DNS/TLS, secrets and named operators all matter; measure the restore rather than assuming provisioning time. Liveness only shows a process response; examine write/read success, latency, disk/inode use and representative transactions, then mitigate before exhaustion. Use compatible expand-and-contract changes and preserve old code compatibility until rollback ends. Do not claim a one-hour recovery point until independent backup freshness and restore integrity are demonstrated.

Review questions:

- What user and recovery contract does the first deployment promise?
- Which operational dependencies are easy to overlook on one VPS?
- Why is a passing liveness check insufficient during a disk incident?
- What evidence should trigger the next architecture investment?

Takeaways:

- A single VPS can be a reasonable first deployment when its limits and ownership are explicit.
- Build a repeatable release, least-privilege access, independent backup and tested restore path early.
- Monitor business outcomes and resource exhaustion, then use incidents to remove causes.
- Add architecture only when evidence shows which failure, load or team constraint it should solve.

## Sources checked 2026-10-04

- [Ubuntu Server documentation](https://documentation.ubuntu.com/server/) and [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html) — host and service operations.
- [PostgreSQL backup documentation](https://www.postgresql.org/docs/current/backup.html) — database protection methods.
- [Chapter 132 — Deployment to VPS Infrastructure](../14-delivery-deployment-and-gitops/132-deployment-to-vps-infrastructure.md), Chapters 181, 183, 185 and 186 — deployment, reliability and recovery.

DispatchDesk is fictional. The initial targets and incident are illustrative; no VPS, application or database was deployed.
