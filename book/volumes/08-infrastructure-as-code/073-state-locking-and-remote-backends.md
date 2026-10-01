---
book: The Complete DevOps Engineering Book
volume: 8
volume_title: "Infrastructure as Code"
chapter: 73
title: "State, Locking and Remote Backends"
slug: state-locking-and-remote-backends
status: complete
summary: ../../_ai/chapter-summaries/073-state-locking-and-remote-backends.md
---

# Chapter 73 — State, Locking and Remote Backends

## Resource identity and state sensitivity

DispatchDesk's team has source code for a network and a database. After a successful apply, the cloud has objects with generated identifiers. The infrastructure engine needs a durable association between its configuration addresses and those remote identities. State is that operational record. It also holds information used during planning and may hold sensitive resource attributes. Losing source and losing state are different incidents: source describes intent; state helps identify which existing objects the engine manages.

A resource address such as `module.orders.aws_db_instance.primary` is an identity inside the configuration, while a cloud identifier names an object in the provider's system. Changing a local name without describing the intended move can make an engine interpret an old address as removed and a new one as missing. That can produce deletion and creation instead of a harmless rename. [Safe refactoring](075-import-drift-and-safe-refactoring.md) owns the detailed move/import procedure. Here, understand why treating state as disposable cache is dangerous.

State is not an application backup. It may identify a PostgreSQL database without containing the orders stored in it. Conversely, an application backup does not reconstruct the ownership relationships that infrastructure planning uses. A recovery plan must preserve both, with their different confidentiality, retention, and recovery needs. DispatchDesk's database restoration procedure belongs to [managed database operations](../10-aws-production-services/095-rds-and-managed-database-operations.md) and [backup engineering](../19-site-reliability-and-recovery/186-backup-engineering.md).

Do not commit state to a source repository. Access to repository history is often broader and lasts longer than access to production infrastructure. Deleting a secret-bearing file in a later commit does not remove its historical copies. The same concern applies to saved plans, exported JSON, debug logs, terminal recordings, and attachments to support tickets. Marking a value sensitive controls presentation in some interfaces; it is not a storage encryption policy.

State access is privileged operational access. An engineer who can read a state snapshot may learn passwords, connection strings, resource names, or network details. An engineer who can overwrite it can influence the next plan's understanding of ownership. Separate read and write authority where the backend permits it. Audit administrative actions, restrict the recovery location, and document who can perform a restore during an incident.

## Remote state and concurrent changes

A local state file can serve a single-person disposable lab. It becomes fragile when two engineers clone the repository and each obtains a different copy. The repository then contains common intent but the operators have divergent operational records. A remote backend provides a shared state location. It still needs authentication, appropriate access policy, durable storage, and a concurrency mechanism. “Remote” by itself does not establish all four.

A state lock serializes operations that could otherwise write conflicting views. It is not a lock on the cloud account, a deployment freeze, or a mechanism that prevents somebody using the console. It also does not guarantee application availability. Terraform uses supported backend locking during operations that may write state and stops if acquisition fails. The [official locking documentation](https://developer.hashicorp.com/terraform/language/state/locking) explains this behavior and warns against bypassing it.

For the AWS company's Terraform backend, the following is a complete backend declaration placed inside the root module's `terraform` block, or in a separate `backend.tf` with that block. It assumes an already provisioned private bucket, bucket versioning, appropriate encryption/access policy, and a Terraform executable supporting the documented S3 lockfile option. Replace the bucket with the actual approved bucket name before running initialization. This example does not create the bucket:

```hcl
terraform {
  backend "s3" {
    bucket       = "replace-with-approved-state-bucket"
    key          = "dispatchdesk/staging/terraform.tfstate"
    region       = "eu-central-1"
    encrypt      = true
    use_lockfile = true
  }
}
```

The key separates this environment's state object from other roots. The selected region is an example, not a mandate. S3 locking is opt-in; the official backend documentation inspected for this chapter marks DynamoDB-based locking deprecated. The executing identity needs scoped state-object access and the documented read/write/delete permissions on the lock object. Check the exact policy requirements and feature support against the chosen executable. OpenTofu's backend behavior must be checked separately; this is not a universal interchangeable backend recipe. [Terraform S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3) is the authoritative reference.

The credentials used by the backend and the credentials used by a resource provider are separate concerns even when an organization supplies both through one session. Initialization can fail to read state before a provider ever attempts a resource operation. Diagnose that distinction. The prerequisite for this AWS example is a verified short-lived CLI/session identity described in [AWS identity sessions](../09-aws-foundations/082-aws-cli-and-identity-sessions.md), plus explicit permission to the approved bucket and encryption key where applicable.

Creating the backend's storage involves billable storage, request, and possibly key-management operations. Prices depend on region and configuration; estimate them from current AWS pricing instead of assuming a free tier. Do not destroy the bucket as part of routine application teardown. Retain state versions according to a documented recovery and data policy; destroying backend history can turn a small cleanup mistake into an unrecoverable ownership incident.

## Migrating without losing the record

A backend migration is an operational change with a maintenance owner. Stop competing automation, identify the current backend and workspace, and produce a restricted backup. Run these commands as the ordinary operator user in the initialized root module directory. They are the same on Ubuntu and Fedora/RHEL; the user needs CLI and backend permissions, not sudo:

```bash
umask 077
terraform state pull > before-migration.tfstate
terraform state list
```

`umask 077` limits permissions on newly created files in this shell. Redirection creates the snapshot file; `state pull` retrieves the current backend's state. Treat the result as sensitive and verify that the command succeeded before relying on the file. The CLI may normalize state representation, so the snapshot is a tool-produced export rather than a promise of a byte-identical object copy. `state list` provides an address inventory for comparison after migration. [State pull documentation](https://developer.hashicorp.com/terraform/cli/commands/state/pull) describes the command.

Only after recording the source should the team add the destination backend configuration and run:

```bash
terraform init -migrate-state
terraform state list
terraform plan -input=false -lock-timeout=60s
```

`-migrate-state` requests copying state to the new backend and may ask for confirmation. Read the proposed source and destination carefully. `-reconfigure` has a different purpose: it changes local backend initialization without asking the tool to migrate the previous state. Substituting it here can leave the new destination empty while old resources remain managed by the old state location. The final plan waits up to sixty seconds for a lock instead of failing immediately on a transient competing operation. A no-change plan and matching inventory support the migration; they do not prove that every application dependency works.

A production migration also verifies access from the CI execution identity, not only the engineer's laptop. A configuration that works with broad personal permissions can fail when the next release uses a restricted role. Keep source and destination backups until the recovery window has passed. Securely dispose of local copies according to the organization's data policy. Do not leave a sensitive export in a build workspace whose artifact collector uploads every file.

## Recovering a failed state operation

At 14:00, a CI job loses its runner while holding a state lock. At 14:05, a developer sees a lock error and wants to remove the lock. The first question is whether an executor is still active. A lost web connection is not proof that the remote process stopped. Check the CI job, agent, run identifier, and backend lock information; contact the operation's owner. Stop new writers while establishing the facts.

If the lock belongs to your definitively terminated operation and automatic release failed, the tool's recovery command uses the actual lock identifier from the diagnostic:

```bash
terraform force-unlock ACTUAL_LOCK_ID_FROM_DIAGNOSTIC
```

The argument is an explanatory placeholder; replace it with the observed identifier. This command changes locking state and does not roll back infrastructure. Keep its confirmation prompt. Do not add `-force` to a routine runbook simply to make it unattended. Releasing an active lock can permit concurrent writers, which is precisely the failure the lock prevents. [Force-unlock reference](https://developer.hashicorp.com/terraform/cli/commands/force-unlock) specifies the command.

After release, generate a new plan and inspect remote inventory. The interrupted operation may have created an object before recording all results. Conversely, it may have recorded a completed operation before the runner disappeared. Recovery requires reconciling actual objects with the latest durable state, not assuming the last terminal message tells the whole story. Preserve the failed run's logs and identifiers so import or other repair has evidence.

A write failure deserves different handling from a stale lock. If an apply changed infrastructure but could not persist state, protect any recovery state file named by the diagnostic, freeze writers, and repair backend access. Do not immediately reapply from an older snapshot: it can repeat operations or propose unintended replacements. Escalate to the documented recovery procedure for the exact tool/backend version. Manual state replacement is a controlled incident action, not an ordinary retry flag.

Restoring an older state version can recover lost ownership information, but it also rewinds the tool's knowledge. Objects created after that version still exist remotely. Compare the restored snapshot's inventory with provider inventory and audit records before applying. Version history makes recovery possible; it does not decide which version is correct. [Infrastructure disaster recovery](080-infrastructure-lifecycle-and-disaster-recovery.md) expands the bootstrap and reconstruction sequence.

## Boundaries and operational decisions

One giant state file makes it easy to reference resources but enlarges the permission and failure scope of each operation. Many tiny files reduce scope but multiply coordination, dependency publication, and recovery procedures. Split state along stable ownership and lifecycle boundaries. A shared network can have a different change cadence from DispatchDesk's application pool; a database can require a different deletion policy from disposable test capacity. Do not split every resource merely to reduce a count.

Remote-state consumers can also expand confidentiality exposure. If a consumer's mechanism requires reading an entire state snapshot to obtain one output, granting that access may reveal more than intended. Publish narrowly scoped connection metadata through an appropriate service when the trust boundary requires it. Avoid treating internal output names as an accidental public API without documenting their stability.

For the VPS company, a hosted backend with simple controls can be preferable to operating storage infrastructure solely for a few resources. The AWS company can use a separately administered AWS backend. The Kubernetes company should avoid storing its only cluster-recovery record inside the cluster that the record is needed to rebuild. The choice is governed by recovery access, operational skill, and trust boundaries, not team size alone.

## Exercises and answer guidance

1. A pipeline can read the state object but cannot delete the lock object. What failure might follow? Lock release can fail even though state access works; verify the exact backend lock-object permissions before changing any resource-provider role.
2. Why can restoring yesterday's state produce a dangerous plan? It lacks knowledge of later objects or changes. Reconcile inventory and audit history before applying.
3. Two roots use the same bucket and key by mistake. What is the correction? Freeze writers, identify actual ownership and latest trustworthy snapshots, then separate keys through a controlled migration. Merely renaming a local directory does not change backend identity.

Review questions: Why is state sensitive? What does a lock protect? What is the difference between migration and reconfiguration? Why should backend storage outlive application teardown?

Reliable state operations depend on durable identity records, one active writer, restricted exports, and a rehearsed recovery path that remains accessible when the managed environment is unavailable.

## Sources and verification

Terraform locking, S3 backend, state pull, and force-unlock primary documentation linked above was inspected 2026-10-01. S3 lockfile configuration reflects that documented Terraform interface; readers must verify their selected tool/version. No CLI exists on the authoring PATH, so migration, locking, IAM, and cloud behavior were not executed. No account resources or billable operations were created.
