---
book: The Complete DevOps Engineering Book
volume: 9
volume_title: "AWS Foundations"
chapter: 87
title: "EBS and Cloud Storage Choices"
slug: ebs-and-cloud-storage-choices
status: complete
summary: ../../_ai/chapter-summaries/087-ebs-and-cloud-storage-choices.md
---

# Chapter 87 — EBS and Cloud Storage Choices

## Choose the semantics before the service

DispatchDesk stores several kinds of information: durable orders, notification intents, release artifacts, diagnostic logs, and temporary working files. Giving them all the same storage backend creates accidental coupling. Summit chooses a managed database for transactional orders, S3 for release objects, and ephemeral task space for reproducible temporary files. An EC2 diagnostic server may use EBS for its root disk without becoming the owner of application data. Harbor can use a local filesystem and database with a tested backup plan. These paths should preserve the same durability contract through different mechanisms.

Block storage presents addressable blocks. A filesystem or database decides how to organize them. EBS belongs in this category, with attachment and placement constraints described in [AWS's volume guide](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volumes.html). A volume's existence does not imply a filesystem exists, that a mount succeeded, or that the application has permission to write. Read [disks and mounts](../04-vps-and-server-operations/033-disks-filesystems-and-mounts.md) before performing guest-side storage operations. Formatting a restored volume destroys the filesystem you intended to recover.

File storage exposes shared paths and filesystem operations. EFS supplies managed NFS file storage, with regional and single-zone choices explained in [its introduction](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html). It can fit a workload that truly needs concurrent file access, but sharing a directory does not make multiple writers correct. Applications still need locking and consistency assumptions, ownership, mount availability, authentication and network access. A shared filesystem is not an automatic reason to place a conventional single-host database there.

Object storage exposes named objects through service APIs. Objects work well for immutable artifacts, exports and uploads that the application treats as whole values. Their keys and access policies differ from filesystem permissions; filesystem-like adapters can hide those differences until a workload relies on operations the adapter cannot faithfully provide. [S3 CLI operations](088-s3-from-the-cli.md) develops that interface in detail. Choose the application's required behavior first, then compare services that actually provide it.

A useful review begins with four questions. Can this data be regenerated? Must two updates commit together? How much loss can recovery tolerate? How long may recovery take? Orders and notification intents require transactional reasoning, while a build cache can usually be discarded. Avoid measuring only gigabytes: access pattern, latency, concurrency, failure placement and recovery effort can dominate capacity cost. A cheaper storage class may be unsuitable for frequently accessed operational data even when it can retain the same bytes.

## Snapshots, performance and encryption

An EBS snapshot captures volume blocks at a point in time and can produce a new volume. It is not a copy of application memory. A successful snapshot of an actively changing database may require crash recovery or may fail your application-consistency requirements. [Snapshot creation guidance](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-creating-snapshot.html) explains buffered-write limitations and recommends pausing writes or appropriate unmount/stop procedures. Coordinate database-aware backup and recovery rather than calling a storage API and assuming a transactionally coherent result.

This distinction matters for DispatchDesk's paired order and intent writes. A restore test must establish that acknowledged orders and their durable notification intent remain recoverable according to the declared recovery point. A filesystem mounting cleanly proves much less. Multi-volume applications add ordering and consistency requirements: independently capturing a data volume and a write-ahead-log volume can produce incompatible points. Use the owning database's backup method and documented storage snapshot workflow, then test restoration in an isolated environment.

Snapshots are incremental internally, but each usable snapshot can restore its represented point without an operator manually assembling a chain. Deleting an earlier snapshot is not the same as deleting all blocks needed by later snapshots. [AWS's snapshot guide](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-snapshots.html) explains retention and cost implications. The larger operational risk is often deleting the last snapshot that satisfies a required recovery point, or retaining snapshots containing sensitive records beyond the allowed retention policy.

Encryption needs a recoverable identity and key policy. EBS uses KMS keys, and key access influences creation and restoration. The [encryption guide](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-encryption.html) warns that some key authentication occurs asynchronously: an initial create response can be followed by failure. Waiting for usable state and inspecting the encryption metadata therefore matter. Backups that survive a host incident but depend on an inaccessible key do not satisfy recovery requirements. Include key ownership, deletion controls and authorized restoration roles in the backup design.

Performance is also a path rather than a single volume label. The volume's configured throughput and IOPS, instance EBS capacity, queue depth, request sizes, filesystem behavior and application access pattern can each constrain it. Restored volumes can additionally experience initialization effects; [AWS's initialization guide](https://docs.aws.amazon.com/ebs/latest/userguide/initalize-volume.html) describes the available mechanisms and their costs. Test recovery latency under representative reads, not just the volume's transition to `available`. Do not add paid acceleration features without measuring which part of recovery needs them.

## An unattached encrypted-volume lifecycle

This optional lab creates an empty encrypted EBS volume, snapshots it, creates a second volume from the snapshot, inspects metadata, and deletes all three resources. No instance attachment, formatting, filesystem data, or application is involved. Consequently, it exercises control-plane lifecycle only. It cannot prove a backup contains orders or that a restored application meets a recovery-time objective.

Use an ordinary Bash workstation account with AWS CLI v2 and the verified sandbox profile from [Chapter 82](082-aws-cli-and-identity-sessions.md). Commands are identical on Ubuntu 24.04 LTS, Fedora 44 and RHEL 9 because they call the EC2 API. Guest device naming, filesystem tools and mandatory access controls are separate distribution concerns covered in the disk chapter. Select an actual approved zone in the chosen region, and an authorized symmetric KMS key available to this account. Permissions must cover volume/snapshot operations and the necessary KMS use.

This is billable storage even when unattached. Review [EBS regional pricing](https://aws.amazon.com/ebs/pricing/) and key-related charges, set a cleanup deadline, and retain the returned identifiers. No cloud operation was executed during authoring.

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Approved zone name: ' lab_zone
read -r -p 'Approved symmetric KMS key ARN: ' lab_key
: "${lab_zone:?zone required}" "${lab_key:?key required}"
lab_volume=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager ec2 create-volume --availability-zone "$lab_zone"   --size 1 --volume-type gp3 --encrypted --kms-key-id "$lab_key"   --tag-specifications   'ResourceType=volume,Tags=[{Key=Name,Value=dispatchdesk-empty-storage-lab},{Key=Purpose,Value=temporary-lab}]'   --query 'VolumeId' --output text)
printf 'Record source volume: %s\n' "$lab_volume"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 wait volume-available --volume-ids "$lab_volume"
lab_snapshot=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager ec2 create-snapshot --volume-id "$lab_volume"   --description 'Empty encrypted lifecycle lab; no application backup'   --tag-specifications   'ResourceType=snapshot,Tags=[{Key=Purpose,Value=temporary-lab}]'   --query 'SnapshotId' --output text)
printf 'Record snapshot: %s\n' "$lab_snapshot"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 wait snapshot-completed --snapshot-ids "$lab_snapshot"
```

`--size 1` requests a one-GiB empty volume, not a one-byte object. `--volume-type gp3` chooses general-purpose SSD without prescribing production performance settings. `--encrypted` and `--kms-key-id` make the intended key choice explicit. Tags support discovery; returned IDs identify the actual resources. Waiters inspect asynchronous status and can fail after a successful create request. Preserve records and inspect the resource rather than rerunning the entire script and accumulating chargeable objects.

Create the restored volume in the same approved zone for this simple lab:

```bash
lab_restored=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager ec2 create-volume --availability-zone "$lab_zone"   --snapshot-id "$lab_snapshot" --volume-type gp3   --encrypted --kms-key-id "$lab_key"   --tag-specifications   'ResourceType=volume,Tags=[{Key=Name,Value=dispatchdesk-restored-empty-lab},{Key=Purpose,Value=temporary-lab}]'   --query 'VolumeId' --output text)
printf 'Record restored volume: %s\n' "$lab_restored"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 wait volume-available --volume-ids "$lab_restored"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 describe-volumes --volume-ids "$lab_volume" "$lab_restored"   --output json
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 describe-snapshots --snapshot-ids "$lab_snapshot" --output json
```

Inspect state, size, zone, encryption flag and key identity. The restored volume should reference the requested snapshot. These are expected relationships, not measured output from authoring. In a real restore, choose the zone containing the recovery instance and confirm attachment compatibility. A snapshot is a restoration source; it does not automatically attach a disk or switch an application's data path.

Delete only these empty lab resources after verification:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 delete-volume --volume-id "$lab_restored"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 delete-volume --volume-id "$lab_volume"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 delete-snapshot --snapshot-id "$lab_snapshot"
```

These deletions are irreversible for the named resources. For partial creation, delete only IDs that were actually returned and confirmed. A volume attached unexpectedly requires owner investigation and an authorized detach procedure; do not force detach to make a lab disappear. Retention controls may block snapshot deletion. Check the original account and region's inventory afterward, distinguish not-found from access denial, and track unresolved retained objects until their owner confirms cleanup.

## Restoring the wrong thing successfully

A realistic incident is a snapshot that completes and restores cleanly but contains yesterday's data because automation selected the wrong volume. The failure is identity selection, not snapshot availability. Capture the source volume ID, instance attachment, mount identity, application path, backup timestamp, and recovery-point requirement before creating a backup. Tags can be stale. A restored filesystem with the expected directory names can still belong to a previous deployment.

For recovery, preserve the candidate restore and original evidence. Bring up an isolated recovery environment, prevent notification delivery to real customers, and inspect the database's own recovery status and durable record checks. Compare known order IDs and backup manifests without exposing customer data in logs. If the snapshot fails the recovery point, choose an approved newer backup or the database's supported recovery path; do not promote an apparently healthy but stale database because the disk mounts.

When the correct restore is accepted, update the application data attachment through its owning configuration and retain rollback evidence according to policy. Monitor read latency, error rates and notification backlog during recovery. The final acceptance condition concerns correct service behavior and data, not merely allocated storage.

## Exercises and answer guidance

1. Can the empty-volume lab prove an order backup is good? No. It verifies resource lifecycle and metadata without any application data or consistency test.
2. What can make an encrypted snapshot unrecoverable to an operator who can list it? Missing KMS authority or unavailable key material; listing metadata is insufficient.
3. Why is formatting the restored device dangerous? It overwrites the recovered filesystem rather than making existing data readable.
4. Which storage semantics fit immutable release artifacts? Object operations usually fit; transactional order writes require a different contract and database reasoning.

Review questions: what uniquely identifies the source data, what establishes application consistency, which key enables recovery, and what evidence proves the restored service can meet its recovery objective?

## Verification and primary sources

Official EBS, EFS and EC2 CLI documentation was inspected on 2026-10-01. No volumes, snapshots, keys, filesystems or application backups were created or restored. The CLI v2 lab is intentionally unattached and empty; even a successful reader execution would not establish database recovery correctness.

Additional references: [create-volume](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-volume.html), [create-snapshot](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-snapshot.html), [snapshot-completed waiter](https://docs.aws.amazon.com/cli/latest/reference/ec2/wait/snapshot-completed.html), [delete-volume](https://docs.aws.amazon.com/cli/latest/reference/ec2/delete-volume.html), and [delete-snapshot](https://docs.aws.amazon.com/cli/latest/reference/ec2/delete-snapshot.html).
