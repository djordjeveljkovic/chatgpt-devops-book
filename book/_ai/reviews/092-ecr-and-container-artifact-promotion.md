# Independent re-review — Chapter 92

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 4fb2bfe98a9868638cdc66f0de7149272be3100cf21ea6af5dc17cff21209e2c

## Scope and findings

Freshly read the corrected current manuscript against the prior working-directory/cleanup finding. This re-review covers the directory/file ownership correction and the unchanged surrounding commands for regressions; it retains the original dated source evidence below.

The material finding is resolved. Setup now uses mktemp to create a fresh private directory, enters it under set-e, captures its absolute path and writes the supplied complete retention JSON there. Later instructions require the same shell/directory, isolating digest output and named-file cleanup. Teardown removes only lab-created files and uses nonrecursive rmdir, preserving unexpected remaining content. The separate protected credential directory remains appropriate. No remaining material finding.

## Dated primary-source evidence

Inspected on 2026-10-04:

- [ECR authentication](https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html): IAM token scope, AWS username and password-stdin login relationship.
- [Tag mutability](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-tag-mutability.html): IMMUTABLE and exclusion modes. Its introductory statement about all tags conflicts with its newer exclusion sections; the manuscript correctly acknowledges the modes.
- [Repository policies](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-policies.html): resource/identity permission boundaries.
- [Image scanning](https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-scanning.html): OS-only basic versus enhanced language/continuous capabilities, and current basic results through DescribeImageScanFindings.
- [Lifecycle policies](https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html): preview, untagged selection, imageCountMoreThan ordering and manifest-list reference constraints.
- [create-repository](https://docs.aws.amazon.com/cli/latest/reference/ecr/create-repository.html), [describe-images](https://docs.aws.amazon.com/cli/latest/reference/ecr/describe-images.html), [describe-image-scan-findings](https://docs.aws.amazon.com/cli/latest/reference/ecr/describe-image-scan-findings.html), [start-lifecycle-policy-preview](https://docs.aws.amazon.com/cli/latest/reference/ecr/start-lifecycle-policy-preview.html), [delete-repository](https://docs.aws.amazon.com/cli/latest/reference/ecr/delete-repository.html): flags, identifiers, response fields and force-delete semantics.
- [Podman login](https://docs.podman.io/en/latest/markdown/podman-login.1.html), [push](https://docs.podman.io/en/latest/markdown/podman-push.1.html), [untag](https://docs.podman.io/en/latest/markdown/podman-untag.1.html): authfile/password-stdin/TLS behavior, resulting-image digestfile and selective local-name removal.

## Validation and limits

`python3 tools/check_book.py --chapters 92-92` passed: 5 shell syntax blocks and 1,336 global local links; no errors/warnings. Executed only the extracted local setup block in a subprocess: directory creation, cd and here-document succeeded, directory mode was 700, Python json.tool accepted lab-retention.json, and removal of that file plus empty-directory rmdir succeeded. The scoped checker does not itself parse JSON embedded inside a shell here-document; this separate check covered that JSON.

No AWS API call, token/login, repository creation/deletion, Podman image operation, scan, preview, cross-account copy or deployment executed. No OS runtime matrix or pricing estimate performed. Existing primary-source comparison remains documentation evidence, not registry interoperability or recovery evidence. Only this review record changed; chapter and summary were not edited.

Verdict: approved
