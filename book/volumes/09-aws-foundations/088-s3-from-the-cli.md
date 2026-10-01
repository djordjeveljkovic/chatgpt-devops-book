---
book: The Complete DevOps Engineering Book
volume: 9
volume_title: "AWS Foundations"
chapter: 88
title: "S3 from the CLI"
slug: s3-from-the-cli
status: complete
summary: ../../_ai/chapter-summaries/088-s3-from-the-cli.md
---

# Chapter 88 — S3 from the CLI

## Buckets, objects and access controls

Summit publishes DispatchDesk release artifacts to S3 so deployment workers can retrieve a specific approved artifact independently of the build machine. That design needs more than a successful upload: the release record must identify the exact bytes and object version, readers need narrowly scoped access, and retention must preserve rollback artifacts. Harbor can use a simpler artifact repository or host copy, while Atlas may retrieve OCI images from a registry. S3 is an object interface, not a mandatory waypoint for every deployment.

A bucket supplies a service namespace and configuration boundary. An object has a key, data and metadata; a versioned object also has a version identifier. A slash in a key supports prefix organization rather than creating a POSIX directory. `releases/dispatchdesk/build-42.tar` is one complete key. Renaming a local directory does not rename its uploaded objects. Case, leading slashes and accidental whitespace can produce different keys that look similar in a dashboard.

Use an approved general-purpose bucket for this chapter. Bucket namespace choices and specialized bucket types have service-specific behavior; do not assume one naming rule or operation applies to every S3 offering. [AWS's security guidance](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html) covers current bucket ownership, policy and protection decisions. Keep release objects private, retain public-access controls, and use IAM roles or temporary operator authentication. An artifact repository containing only nonsecret binaries can still supply privileged code to production.

Apply [IAM policy reasoning](083-iam-policies-and-least-privilege.md) to separate bucket actions from object actions. Listing a prefix and reading an object are different permissions. Version-specific reads additionally require the appropriate version access. SSE-KMS objects add key authorization. Never make a bucket public to diagnose a denied deployment download. First establish the effective caller, bucket, exact key, version and encryption requirements; access denial is not evidence that the object is absent.

The high-level `aws s3` commands suit copy and sync workflows. `aws s3api` exposes individual service operations and metadata needed here. A synchronization command with deletion enabled can turn a local missing file into a remote deletion. Its preview is useful, but it does not replace review of the destination and scope. For the small lab below, use exact key operations so cleanup cannot accidentally target an entire release prefix.

## Versioning, lifecycle and multipart upload

Versioning preserves separate variants when a key is overwritten. A simple delete in a versioning-enabled bucket ordinarily creates a delete marker; an older version may still be retrievable. Deleting a specified version permanently removes that version. [The versioning guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html) explains enabled, suspended and initially unversioned states. Suspending versioning does not convert the bucket back to its original unversioned state or remove historical versions.

A release record should contain bucket, key, version ID, artifact checksum, build provenance and approval. Versioning alone does not establish which artifact is approved. If a deployment asks for the current version of a mutable key such as `latest.tar`, a later write changes what it receives. Prefer immutable release keys and retain version IDs when versioning is enabled. A cryptographic checksum verifies bytes relative to the expected digest; it does not identify who authorized them unless the expected digest comes from a trusted release record.

Retention is a policy decision before it becomes a lifecycle rule. The fictional example below describes an expendable `temporary-labs/` prefix: current objects expire after seven days, noncurrent versions after two days, and incomplete multipart uploads after one day. Those are arbitrary lab retention assumptions, unsuitable for production release rollback or customer records without a separate requirement. Save this as `lab-lifecycle.json` for review, not automatic application:

```json
{
  "Rules": [
    {
      "ID": "temporary-lab-retention",
      "Status": "Enabled",
      "Filter": {"Prefix": "temporary-labs/"},
      "Expiration": {"Days": 7},
      "NoncurrentVersionExpiration": {"NoncurrentDays": 2},
      "AbortIncompleteMultipartUpload": {"DaysAfterInitiation": 1}
    }
  ]
}
```

Expiration and noncurrent expiration address different retained objects. Lifecycle processing is asynchronous and is not a deterministic immediate-cleanup script. [AWS's lifecycle examples](https://docs.aws.amazon.com/AmazonS3/latest/userguide/lifecycle-configuration-examples.html) explain the separate actions. A bucket lifecycle update replaces the configuration supplied through that API; a single-rule file must not silently discard other owners' rules. The owning infrastructure definition should merge reviewed requirements and preserve the complete intended configuration. Removing a rule later cannot undelete a version it already removed.

Multipart upload divides a larger object into parts, permits retrying individual parts, and completes them into an object. Failed or abandoned uploads can retain billable parts until explicitly aborted or cleaned by the intended policy. ETags are not universal whole-file MD5 digests, particularly across multipart and encryption cases. Follow [AWS's multipart guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html) for part and checksum requirements. Small files below use single `put-object` requests, avoiding fabricated multipart thresholds or performance guarantees.

## A version-pinned upload workflow

Run this optional lab from an ordinary Bash workstation user with Python 3 and AWS CLI v2. Ubuntu 24.04 LTS, Fedora 44 and RHEL 9 use the same API commands; Python installation follows the distribution baseline. Use an existing private, versioning-enabled, general-purpose sandbox bucket and an approved expendable prefix. Complete the account preflight in [Chapter 82](082-aws-cli-and-identity-sessions.md), verify bucket ownership and region with its administrator, and authorize put/get-version/list-versions/delete-version for the selected lab key. Required bucket configuration reads are separate permissions.

This creates two billable object versions and makes requests; review [S3 pricing](https://aws.amazon.com/s3/pricing/) and any KMS charges. The lab does not create or change a bucket, encryption policy, lifecycle policy or public access setting. The bucket's approved encryption configuration must accept these requests. No cloud upload was executed during authoring.

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Verified versioning-enabled sandbox bucket: ' lab_bucket
: "${lab_bucket:?bucket required}"
lab_status=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager s3api get-bucket-versioning --bucket "$lab_bucket"   --query 'Status' --output text)
if [ "$lab_status" != Enabled ]; then
  printf 'Stop: this lab requires enabled versioning.\n' >&2
  exit 1
fi
lab_suffix=$(python3 -c 'import uuid; print(uuid.uuid4().hex)')
lab_key="temporary-labs/$lab_suffix/artifact.txt"
printf 'Record bucket/key: %s %s\n' "$lab_bucket" "$lab_key"
printf 'DispatchDesk lab artifact revision one\n' > artifact.txt
lab_version_one=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager s3api put-object --bucket "$lab_bucket"   --key "$lab_key" --body artifact.txt --checksum-algorithm SHA256   --query 'VersionId' --output text)
printf 'Record version one: %s\n' "$lab_version_one"
cp -- artifact.txt expected-one.txt
printf 'DispatchDesk lab artifact revision two\n' > artifact.txt
lab_version_two=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager s3api put-object --bucket "$lab_bucket"   --key "$lab_key" --body artifact.txt --checksum-algorithm SHA256   --query 'VersionId' --output text)
printf 'Record version two: %s\n' "$lab_version_two"
case "$lab_version_one:$lab_version_two" in
  *None*|*null*) printf 'Stop: missing expected version IDs.\n' >&2; exit 1 ;;
esac
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   s3api get-object --bucket "$lab_bucket" --key "$lab_key"   --version-id "$lab_version_one" downloaded-one.txt
cmp -- expected-one.txt downloaded-one.txt
```

The UUID creates a distinct lab key without pretending collision prevention is an authorization control. Record the key and returned version IDs immediately. `--body` reads the local file; `--checksum-algorithm SHA256` requests the documented upload checksum mechanism. `--query VersionId` captures identity rather than an ETag approximation. The second upload uses the same key, creating a new version. The explicit version read must return the first bytes, which `cmp` checks exactly; successful comparison produces no output. This is expected behavior, not measured cloud evidence.

The version-ID guard stops if output lacks the expected identifiers, but uploads may already exist. It does not roll them back. Inventory the exact recorded key and inspect versions before recovery. The simplistic string guard is a lab precondition check, not a general parser for arbitrary production metadata. Production automation should store and validate structured responses together with its release record.

Inspect all versions and delete only those created here:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   s3api list-object-versions --bucket "$lab_bucket"   --prefix "$lab_key" --output json
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   s3api delete-object --bucket "$lab_bucket" --key "$lab_key"   --version-id "$lab_version_two"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   s3api delete-object --bucket "$lab_bucket" --key "$lab_key"   --version-id "$lab_version_one"
rm -- artifact.txt expected-one.txt downloaded-one.txt
```

Compare exact keys in the listing because a prefix can match longer keys too. Version-specific deletion is permanent and avoids deliberately adding a delete marker. Rerun the listing to confirm the created versions are gone; access denial or retention blocking is not successful cleanup. Do not remove unfamiliar versions, bucket configuration or the bucket itself. Partial upload failures need the same exact-key inventory procedure, with cleanup ownership retained until costs and resources are resolved.

## Missing artifact, surviving versions

Suppose a release worker reports that `releases/current.tar` is missing after an operator ran an unqualified delete. The mistaken conclusion is that versioning failed because an ordinary get cannot find the object. Inspect the exact bucket and key using version-aware inventory, including delete markers. If a marker is current and the approved version survives, retrieve that explicit version, verify its trusted checksum and provenance, and use it through the release workflow. Do not promote the most recently listed version merely because it downloads.

If the version was permanently deleted by a lifecycle rule or authorized version deletion, versioning cannot recreate its bytes. Retrieve an independently retained artifact or reproduce the build under the established reproducibility requirements. Investigate which identity changed the object or retention policy and whether the approved rollback window was accurately encoded. Recovery includes fixing mutable deployment references and retention decisions so the same operational sequence does not repeat.

## Exercises and answer guidance

1. Does deleting a key in an enabled-versioning bucket necessarily remove all bytes? No; inspect versions and delete markers. Explicit version deletion has different semantics.
2. Why does this lab retrieve version one after writing version two? It demonstrates that the release identity can remain fixed while the key's current version changes.
3. Is an ETag always a whole-file MD5 checksum? No. Use the appropriate checksum mechanism and trusted artifact digest rather than that assumption.
4. Can a one-rule lifecycle file be safely applied to a shared bucket? Only after reviewing the entire intended configuration and ownership; blindly replacing configuration can discard unrelated retention rules.

Review questions: which exact artifact was approved, who can overwrite or delete it, what restores it during the rollback window, and which retained versions or upload parts incur charges?

## Verification and primary sources

Official S3 and CLI documentation was inspected on 2026-10-01. Examples assume AWS CLI v2 and an existing general-purpose bucket with enabled versioning. No upload, download, lifecycle application, public-access change or version deletion was executed. Syntax and JSON parsing cannot establish bucket policy, checksum interoperability or cloud retention behavior.

Operation references: [put-object](https://docs.aws.amazon.com/cli/latest/reference/s3api/put-object.html), [get-object](https://docs.aws.amazon.com/cli/latest/reference/s3api/get-object.html), [get-bucket-versioning](https://docs.aws.amazon.com/cli/latest/reference/s3api/get-bucket-versioning.html), [list-object-versions](https://docs.aws.amazon.com/cli/latest/reference/s3api/list-object-versions.html), [delete-object](https://docs.aws.amazon.com/cli/latest/reference/s3api/delete-object.html), and [lifecycle configuration API](https://docs.aws.amazon.com/cli/latest/reference/s3api/put-bucket-lifecycle-configuration.html).
