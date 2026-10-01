---
book: The Complete DevOps Engineering Book
volume: 10
volume_title: "AWS Production Services"
chapter: 92
title: "ECR and Container Artifact Promotion"
slug: ecr-and-container-artifact-promotion
status: draft
summary: ../../_ai/chapter-summaries/092-ecr-and-container-artifact-promotion.md
---

# Chapter 92 — ECR and Container Artifact Promotion

## Repository permissions and image identity

A release should move the artifact that passed validation, rather than rebuild it independently for each environment. Summit uses ECR to store DispatchDesk container images for ECS. Atlas can use ECR or another suitable OCI registry for Kubernetes. Harbor can deploy a conventional artifact or use a container registry without adopting an AWS compute platform. Registry choice follows authentication, placement, retention and operational requirements, not a requirement that every company use the same service.

Read [image publication and promotion](../06-docker-in-practice/059-publishing-and-promoting-images.md) for OCI image identity. An image tag is a name associated with registry content. A digest identifies a particular manifest or index. A local image ID is not necessarily the digest of the manifest uploaded to a registry. Compression, media-type conversion and a multi-platform index can change what identity is relevant. Record the digest observed at the destination and deploy that exact registry reference.

ECR separates AWS API authentication from the container client's registry login. The principal obtaining a registry token must have the required token permission; repository operations additionally need their own allowed actions. A successful login does not prove permission to push a particular repository. [ECR authentication documentation](https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html) describes the token and its scope. Pass the password through standard input, protect the local authentication file, and never print it to a build log.

Use an immutable repository for ordinary release tags in this example. ECR also supports mutability modes with exclusions; inspect actual repository settings rather than assuming every tag is protected. [Tag-mutability documentation](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-tag-mutability.html) shows the interfaces. Immutability prevents a tag overwrite under the chosen mode, but it does not prove who approved its first image or prevent an authorized deletion. Deployment approval should bind to digest and provenance independently.

Reader and publisher permissions should differ. A deployer commonly needs image and layer retrieval plus authentication, while a builder needs layer upload and image publication. Neither role needs repository deletion merely to deploy. Cross-account pull requires the appropriate calling identity permissions and repository policy, with any encryption and service requirements also considered. [Repository-policy examples](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-policy-examples.html) provide the exact action relationships. Limit trusted principals to the intended accounts or roles rather than opening the repository broadly to fix an access error.

## Scanning, retention and cross-account access

A scan evaluates supported packages against a vulnerability knowledge base. It is not an application test, a signature verification or an assurance that arbitrary code is safe. Basic ECR scanning and enhanced Inspector scanning have different coverage and lifecycle behavior. [The scanning guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning.html) describes operating-system coverage for basic scanning and additional language-package/continuous capabilities for enhanced scanning. Choose the registry configuration deliberately and review costs before changing it.

Current basic scanning results must be read through `DescribeImageScanFindings`; do not rely on older tutorials that gate releases on `DescribeImages` summary fields. Track scan status, digest, completion/freshness, supported coverage and findings. A missing result, unsupported image or in-progress scan must not silently become “zero vulnerabilities.” Decide how severity, exploitability, reachable functionality, exceptions and remediation deadlines affect promotion. An exception needs an owner and expiry so it does not become a permanent bypass.

Retention must preserve deployed and rollback digests. An image can become untagged yet remain referenced by a running deployment or its rollback record. Deleting every untagged image is therefore not automatically safe. Compare registry candidates against live deployment and retained release inventories, including multi-platform references and associated evidence. Storage cost is real, but a failed recovery due to deleted artifacts can be more expensive than retaining the approved rollback window.

For a dedicated expendable repository, this complete review-only `lab-retention.json` policy would retain the newest three untagged images and expire older untagged candidates:

```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "Review-only expendable untagged lab retention",
      "selection": {
        "tagStatus": "untagged",
        "countType": "imageCountMoreThan",
        "countNumber": 3
      },
      "action": {"type": "expire"}
    }
  ]
}
```

Three is an arbitrary lab count, not a production release policy. Preview it before application, inspect selected digests and compare with the required retention set. [Lifecycle-policy documentation](https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html) explains evaluation and reference constraints. This chapter previews but does not apply this policy. A preview success is useful only if its status is complete and its population matches the current intended repository; images can change after the preview.

Cross-account promotion can mean authorizing a deployment role to pull the same source image, or copying an approved image to a destination registry under separate ownership. Retagging in one repository does not create a second independently governed artifact store. If copying is required, retain manifests and platform content and verify destination identity rather than assuming a human-readable tag preserved it. Record the policy and account boundary as part of release evidence.

## Publish and record a digest

The optional lab creates a new dedicated ECR repository, uploads an already built single-platform image using rootless Podman, captures its destination digest and retrieves it by that digest. It creates no compute deployment. You must already have a nonsecret, approved local image and its source/build evidence from the container chapters. This chapter does not rebuild DispatchDesk or pretend an image tag is a complete application implementation.

Run from an ordinary Bash workstation user with AWS CLI v2, Python 3 and a working rootless Podman installation. Ubuntu 24.04 LTS, Fedora 44 and RHEL 9 use the same AWS commands; use [Podman installation](../07-podman-and-the-rootless-host/061-installing-and-understanding-podman.md) for host-specific runtime prerequisites. On an approved Docker workstation, the corresponding login/tag/push/pull operations can implement the same registry protocol, but credential-file flags differ; do not paste Podman's `--authfile` into Docker commands.

Complete [Chapter 82's account preflight](../09-aws-foundations/082-aws-cli-and-identity-sessions.md). Required permissions cover repository creation/inspection/deletion, authentication and image/layer publication/retrieval; optional scans/previews need additional operations. Review [ECR pricing](https://aws.amazon.com/ecr/pricing/) and chosen scan/encryption features. Image storage, transfer and scanning can incur costs. Establish teardown ownership before pushing. No AWS or registry operations were executed during authoring.

```bash
set -euo pipefail
umask 077
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Approved existing local single-platform image reference: ' lab_source
: "${lab_source:?local image required}"
podman image inspect "$lab_source"
lab_suffix=$(python3 -c 'import uuid; print(uuid.uuid4().hex)')
lab_repository="dispatchdesk-lab-$lab_suffix"
lab_uri=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager ecr create-repository --repository-name "$lab_repository"   --image-tag-mutability IMMUTABLE   --tags Key=Project,Value=DispatchDesk Key=Purpose,Value=temporary-lab   --query 'repository.repositoryUri' --output text)
printf 'Record repository/URI: %s %s\n' "$lab_repository" "$lab_uri"
lab_registry=${lab_uri%%/*}
lab_auth_dir=$(mktemp -d)
lab_auth="$lab_auth_dir/auth.json"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ecr get-login-password |
  podman login --tls-verify=true --authfile "$lab_auth"     --username AWS --password-stdin "$lab_registry"
lab_tag=approved-lab
podman tag "$lab_source" "$lab_uri:$lab_tag"
podman push --tls-verify=true --authfile "$lab_auth"   --digestfile lab-pushed-digest.txt "$lab_uri:$lab_tag"
lab_digest=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager ecr describe-images --repository-name "$lab_repository"   --image-ids "imageTag=$lab_tag"   --query 'imageDetails[0].imageDigest' --output text)
printf 'Record immutable destination: %s@%s\n' "$lab_uri" "$lab_digest"
test "$lab_digest" = "$(cat lab-pushed-digest.txt)"
podman pull --tls-verify=true --authfile "$lab_auth" "$lab_uri@$lab_digest"
```

The repository URI comes from AWS rather than a hard-coded account/partition hostname. The shell's prefix operation extracts its registry component. A UUID makes this a fresh lab repository; if creation nevertheless conflicts, inspect ownership rather than deleting an existing repository. The inspection of the local source should confirm its intended architecture and identity before publication.

`--authfile` confines the registry credential to a temporary file; `--password-stdin` avoids placing it in process arguments. Explicit TLS verification prevents an insecure local registry configuration from weakening this request. `pipefail` makes a failed token-producing stage visible even if the consumer's behavior is misleading. Login can still leave a credential file after later failure, so keep its path for cleanup and never upload it as an artifact.

The push writes the resulting destination digest to a file. `describe-images` looks up the exact tag in the exact repository; the equality check compares two observations of the uploaded manifest. Failure requires inspecting upload/conversion and registry identity, not editing the expected digest until the check passes. Pulling the explicit digest establishes retrieval of that identity, but this lab does not run it or prove business behavior. For a multi-platform release, publish and verify the intended index and child manifests through the corresponding workflow rather than pushing one local platform and calling it the whole release.

If this sandbox registry is configured for basic scanning and permits a manual scan, use the exact digest:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ecr start-image-scan --repository-name "$lab_repository"   --image-id "imageDigest=$lab_digest"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ecr describe-image-scan-findings --repository-name "$lab_repository"   --image-id "imageDigest=$lab_digest" --output json
```

A scan is asynchronous. Inspect its status and repeat bounded observation until the documented terminal result, rather than interpreting an immediate incomplete response as a clean image. For enhanced scanning, inspect its configured Inspector integration and findings instead of forcing this manual-basic workflow. Do not switch a shared registry's scan type for a lab. Existing scan history and coverage are operational inputs.

Preview the reviewed retention file without applying expiration:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ecr start-lifecycle-policy-preview --repository-name "$lab_repository"   --lifecycle-policy-text file://lab-retention.json
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ecr get-lifecycle-policy-preview --repository-name "$lab_repository"   --output json
```

A repository containing only the tagged lab image should not supply an eligible untagged candidate for this rule. That limited result does not prove a production repository's retention safety. Inspect the preview status and pagination when there are more images.

Remove only the fresh lab repository after confirming no deployment references it:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ecr delete-repository --repository-name "$lab_repository" --force
podman untag "$lab_source" "$lab_uri:$lab_tag"
rm -f -- "$lab_auth" lab-pushed-digest.txt lab-retention.json
rmdir -- "$lab_auth_dir"
```

`--force` permanently removes the repository and its images; it is appropriate only for this recorded expendable repository. Confirm absence through inventory in the original account/region. Local untagging removes the lab name while retaining the original source reference; pulled content may remain in local image storage under digest identity, so inspect it before any further removal. Do not prune unrelated images or credential stores. Partial failures retain cleanup responsibility for both cloud repository and local authentication file.

## A promotion that changed the artifact

Suppose staging passed on one image, then production used a rebuilt image with the same human release label. The rebuild resolved updated base content and dependencies; production's failing digest differs from staging. The incorrect assumption is that identical labels imply identical artifacts. Capture both destination digests, build inputs and deployment records. Route rollback through the retained approved digest and compatible configuration, then validate readiness and order/intent behavior.

The durable repair promotes the already validated artifact and binds approval to its digest and provenance. If a registry conversion or destination copy changes identity, validate and record that destination artifact before approving it. Scanning is another evidence input attached to the precise digest, not a substitute for this relationship. A release is reviewable when its source, build, registry identity, tests and deployment all refer to the intended artifact.

## Exercises and answer guidance

1. Registry login succeeds but push is denied. What remains unproven? Repository publication permissions and the target scope; authentication is a separate boundary.
2. Basic scan summary fields are absent from `describe-images`. Does that imply zero findings? No. Use the documented findings API and inspect scan status/coverage.
3. Why can untagged-image expiration break rollback? Deployments can reference digests directly even after tags disappear.
4. A source image ID differs from the pushed manifest digest. Is corruption established? No. They identify different objects; inspect destination manifest identity and expected conversion/platform behavior.

Review questions: which digest passed validation, who can publish/delete it, which scanning coverage was evaluated, and which retention policy preserves the rollback requirement?

## Verification and primary sources

Official ECR, CLI and Podman documentation was inspected on 2026-10-01. No repository, authentication token, image push/pull, scan, preview or deletion was executed. No invented digest is supplied. AWS CLI v2 and the documented Podman flag interfaces are assumptions to verify on the actual workstation; local syntax checks do not establish registry interoperability.

Operation references: [create-repository](https://docs.aws.amazon.com/cli/latest/reference/ecr/create-repository.html), [describe-images](https://docs.aws.amazon.com/cli/latest/reference/ecr/describe-images.html), [scan start](https://docs.aws.amazon.com/cli/latest/reference/ecr/start-image-scan.html), [scan findings](https://docs.aws.amazon.com/cli/latest/reference/ecr/describe-image-scan-findings.html), [lifecycle preview](https://docs.aws.amazon.com/cli/latest/reference/ecr/start-lifecycle-policy-preview.html), [repository deletion](https://docs.aws.amazon.com/cli/latest/reference/ecr/delete-repository.html), [Podman login](https://docs.podman.io/en/latest/markdown/podman-login.1.html), and [Podman push](https://docs.podman.io/en/latest/markdown/podman-push.1.html).
