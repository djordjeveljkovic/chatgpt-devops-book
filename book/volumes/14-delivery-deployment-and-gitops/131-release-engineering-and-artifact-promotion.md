---
book: The Complete DevOps Engineering Book
volume: 14
volume_title: "Delivery, Deployment and GitOps"
chapter: 131
title: "Release Engineering and Artifact Promotion"
slug: release-engineering-and-artifact-promotion
status: complete
summary: ../../_ai/chapter-summaries/131-release-engineering-and-artifact-promotion.md
---

# Chapter 131 — Release Engineering and Artifact Promotion

## Why this matters

A deployment pipeline can pass every test and still release the wrong thing. A later job might rebuild from a moving base-image tag, resolve a newer dependency, use a different compiler, or run a workflow from a different commit. A green test then describes one set of bytes while production receives another. Release engineering closes that gap: it gives a tested artifact an identity, records the evidence and decisions attached to that identity, and moves the same artifact through the environments where it will run.

The governing rule is simple: build once, then promote. Build once means that an artifact selected for release is created by a defined build process from an identified source revision and inputs. Promote means that environments receive that artifact, identified by a content digest, after the required policy checks pass. Promotion does not mean “run the build again with a production tag.” A rebuild may produce different bytes even when the source commit is unchanged.

This chapter focuses on container images because DispatchDesk uses them in later deployment examples. The same reasoning applies to packages, binaries, static bundles, database migration packages, and signed firmware. [Chapter 129](../13-continuous-integration-platforms/129-artifacts-caches-and-build-reproducibility.md) explains caches, reproducible builds, and provenance; this chapter uses those ideas to define a release decision. [Chapter 130](../13-continuous-integration-platforms/130-ci-incidents-and-platform-comparison.md) covers pipeline incidents that can invalidate its assumptions. [Chapter 123](../13-continuous-integration-platforms/123-github-actions-runners-and-security.md) discusses runner trust and credential scope, which also apply to release jobs. The next chapters apply the release identity to a VPS and then to AWS.

## Build once and define release identity

A Git commit is an important input, but it is not the release artifact. It identifies source history; it does not identify the image manifest that a registry serves. A useful release record links several identities and evidence items:

| Field | What it establishes |
|---|---|
| Source revision | The repository and immutable commit that supplied the source |
| Build definition | The workflow, build configuration, and builder identity |
| Artifact reference | Registry and repository plus a manifest digest |
| Test evidence | Which checks ran against the candidate and their results |
| Supply-chain evidence | Provenance, signature, SBOM, and verification result where required |
| Release decision | Who or what approved promotion, when, under which policy |
| Deployment configuration | The environment-specific settings selected separately from the artifact |

For a multi-platform image, the deployable reference is usually the image-index digest, which identifies the index and its platform-specific manifests. Pinning only one architecture’s child digest can fail on another node architecture. A tag such as `1.8.0` or `production` is a convenient name that a registry can associate with a manifest; it is not a content identity. Tags can be moved unless the registry enforces immutability. OCI descriptors express content by digest, and the OCI distribution model permits one manifest digest to have zero, one, or multiple tags. This is why a human release label can be useful alongside a digest, but should not replace it ([OCI descriptors](https://specs.opencontainers.org/image-spec/descriptor/), [OCI distribution specification](https://specs.opencontainers.org/distribution-spec/)).

Suppose DispatchDesk builds commit `9f…` and publishes `registry.example.net/dispatchdesk/api:build-9f…`. CI should capture the digest returned by the registry after the push, then test and scan that digest. A tag derived from a commit is helpful for finding the candidate, but is still a tag. Record the actual digest, for example as the illustrative shape `registry.example.net/dispatchdesk/api@sha256:<64-hex-digest>`. The angle-bracket text is a placeholder, not a usable digest. Never copy an invented or truncated digest into deployment configuration.

Build inputs matter as much as the label. A useful build record describes the source commit, build workflow revision, target platforms, builder, dependency lockfiles, and relevant parameters. Pin action and base-image inputs according to the project’s dependency policy. A build can be deterministic without being hermetic, and a digest proves which bytes were selected without proving that those bytes are safe. Provenance helps connect an artifact to its build process; it does not certify the source as benign. SLSA recommends checking the signature and comparing provenance fields such as builder identity and build parameters against consumer expectations ([SLSA verification guidance](https://slsa.dev/spec/v1.2/verifying-artifacts)).

## Environment gates and evidence

Environments differ in authority and consequence. A pull-request test environment may accept untrusted code with restricted credentials. A staging deployment may use realistic configuration and synthetic data. Production may need an approver, a maintenance window, a health check, and a rollback path. Model those differences as gates around the artifact, not as reasons to rebuild it.

The evidence policy should say what must be true before promotion. For example, a DispatchDesk policy might require all of these:

1. The candidate came from the protected default branch after required reviews.
2. Unit, integration, and contract tests passed for the candidate digest, not a separately rebuilt image.
3. Vulnerability results are recent enough for the release decision and meet the organization’s severity and exception rules.
4. Provenance identifies an accepted builder and source commit; the signature verifies; the artifact digest in the statement matches the candidate.
5. A human approves production promotion for a high-impact release, and the approval is associated with the exact digest.
6. The production configuration is reviewed, versioned, and compatible with this application release.

These controls are policy choices, not universal guarantees. A team may choose a different approval model for a low-risk internal service. It should still make the identity of the tested artifact unambiguous and keep a record of which checks were required. A missing or unverifiable statement should fail closed when provenance is mandatory; when it is optional, the release record should say so instead of silently treating absence as success.

Keep environment-specific values outside the image. The image contains application code and runtime dependencies; it should not embed production passwords, private keys, customer data, or environment URLs as build-time secrets. Inject configuration at deployment through the platform’s controlled mechanism. This lets staging and production run the same bits while retaining separate access boundaries. It also avoids one rebuild per environment, which would break artifact identity.

Testing “the same artifact” requires care. If CI tests a local image before publishing and later pushes a newly built image, those are different operations with a gap between them. Prefer publishing a uniquely named candidate, resolving its digest, and running tests against that registry reference. If the pipeline uses a registry mirror or copies between registries, verify the destination digest and preserve the multi-platform index. Some copy or conversion operations change the manifest representation and therefore its digest. A changed digest means the reference is different; investigate whether the bytes and platform selection remain equivalent, then attach new verification evidence to the destination identity. Do not assume a successful copy proves byte-for-byte identity.

## Promoting a tested image

For a simple organization with one registry, promotion can add a human-readable release tag to an already-tested digest while deployments remain pinned to the digest. Across registries, promotion may copy an image from a candidate repository into a production repository. The copy job needs read access to the source and narrowly scoped write access to the destination. It should not execute pull-request code with production registry credentials. Chapter 123 discusses runner trust and credential scope; apply those boundaries to release jobs as well.

The following Bash fragment illustrates copying a multi-platform image to a release tag while requiring the copy tool to preserve the digest. Run it in a trusted release job with `skopeo` installed, source and destination registry authentication already configured in its protected credential store, and write permission limited to the release repository. The variables are supplied by protected pipeline inputs; the example does not include credentials.

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${REGISTRY:?Set the registry hostname, for example registry.example.net}"
: "${REPOSITORY:?Set the image repository, for example dispatchdesk/api}"
: "${SOURCE_DIGEST:?Set the tested sha256 digest returned by the registry}"
: "${RELEASE_TAG:?Set the approved release tag, for example 1.8.0}"

if [[ ! "$SOURCE_DIGEST" =~ ^sha256:[0-9a-f]{64}$ ]]; then
  printf 'SOURCE_DIGEST must be sha256 followed by 64 lowercase hex characters\n' >&2
  exit 2
fi

digest_file="$(mktemp)"
trap 'rm -f "$digest_file"' EXIT

skopeo copy --all --preserve-digests --digestfile "$digest_file" \
  "docker://${REGISTRY}/${REPOSITORY}@${SOURCE_DIGEST}" \
  "docker://${REGISTRY}/${REPOSITORY}:${RELEASE_TAG}"

copied_digest="$(<"$digest_file")"
if [[ "$copied_digest" != "$SOURCE_DIGEST" ]]; then
  printf 'Destination digest differs; stop and investigate\n' >&2
  exit 1
fi
printf 'Promoted %s:%s at %s\n' "$REPOSITORY" "$RELEASE_TAG" "$copied_digest"
```

The example treats the registry host and repository as protected configuration, the digest as the result of earlier candidate testing, and the release tag as an approved input. The digest validation prevents malformed references; it does not prove that the digest passed policy. The `--all` option requests the full image list, including a multi-platform index, rather than only the current machine’s architecture. `--preserve-digests` makes the copy fail if the destination representation cannot keep the source digest. The digest file is a temporary output removed when the shell exits. A forced termination such as `SIGKILL`, host loss, or abrupt runner teardown can bypass cleanup, so the file contains only a digest and the runner should clean temporary storage between jobs. Skopeo also applies the configured image trust policy; the release workflow must configure that policy deliberately. Review the installed Skopeo version’s manual before adapting flags, because the command has no effect until it contacts the registries ([Skopeo copy reference](https://github.com/containers/skopeo/blob/main/docs/skopeo-copy.1.md)).

An exact-digest copy can fail for legitimate reasons: the destination registry may not support the same manifest media type, the release job may lack source-read or destination-write permission, or an architecture manifest may be missing. Do not remove `--preserve-digests` just to get a green job. First determine whether conversion is an accepted policy. If conversion is needed, treat the destination manifest as a new artifact identity: capture its digest, verify its platform list and content, rerun required checks or establish an approved equivalence process, and create or verify provenance for the destination artifact. If the candidate index was accidentally copied as a single-platform image, halt promotion; developers and production hosts on another architecture may pull an incomplete release.

After promotion, deploy by digest, not by resolving the tag at deployment time. Keep the release tag for people and release notes. A deployment record should retain the exact digest, source commit, configuration revision, and gate results. Then Chapter 132 can deploy that identity to a host; later chapters apply it to cloud and orchestrated rollouts.

## Failure, diagnosis, and recovery

Consider this incident: staging passes against digest A. A release job rebuilds the same commit using a mutable `runtime:stable` base image, yielding digest B, then publishes B as `1.8.0`. Production reports a startup failure that staging did not reproduce. The team initially sees the same source commit and assumes it tested the release. The error is in the release contract: commit equality was mistaken for artifact equality.

Contain the impact by stopping further rollout and recording which digest each environment actually ran. Query the registry and deployment history; do not infer identity from the tag’s current value. Compare the release job’s build record to the staging candidate: source commit, builder, base-image digest, target platform, and final manifest digest. If B is the production artifact, roll back to the last known-good digest that remains available and whose configuration is compatible. Re-run smoke tests and health checks against that exact reference, then confirm the environment is serving it. Do not overwrite a tag and assume already-running hosts changed; they may have pulled a different manifest earlier or may never pull again.

Prevent recurrence by making the release job consume the candidate digest instead of invoking the build, and make the promotion record fail when the destination identity is unexpected. If a mutable tag was overwritten, restore a human tag only after verifying the intended digest and checking the registry’s retention and immutability controls. Preserve the incident evidence and determine whether the rebuild was merely different or also introduced malicious or vulnerable content. A digest comparison diagnoses identity drift; it does not diagnose safety.

Another common failure is provenance that verifies cryptographically but describes an unexpected repository, workflow, or builder. Signature validity establishes that signed data was not altered and that a signing identity can be checked; it does not make that identity acceptable. Define the expected repository, branch or source ref, builder identity, and subject digest before verification. GitHub’s artifact-attestation documentation makes the same distinction: attestations link an artifact to its source and build instructions, but consumers still set policy and evaluate the software ([GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations)).

## Exercises

1. A deployment manifest names `dispatchdesk/api:1.8.0`. Explain why this is insufficient to establish what bytes ran. What should the release record store?
2. A GitLab job tests an image built from a commit, then the production job rebuilds that commit and deploys the new tag. Redesign the handoff so production receives the tested candidate.
3. Your destination registry rejects `--preserve-digests`. List the facts to inspect before deciding whether to convert the manifest. What new evidence would the converted artifact require?
4. A multi-architecture release job copies only the runner’s `linux/amd64` image. What may happen when an ARM64 production node pulls the release tag, and how should the copy and validation policy change?
5. A valid provenance signature identifies a builder workflow from an unprotected branch. Which checks should block promotion even though signature verification passed?

### Answer guidance

1. A tag is a mutable name. Store the registry repository and immutable manifest or index digest, plus source commit, build identity, tests, supply-chain evidence, release decision, and deployment configuration revision.
2. Publish a uniquely identified candidate, capture the registry digest, run tests against that digest, then pass the digest to the protected promotion job. The production job only copies or tags that image and confirms the resulting identity; it does not rebuild source.
3. Check media type, source and destination manifest/index digests, platform descriptors, registry support, copy-tool version, and whether the organization’s policy permits representation changes. A converted artifact has a new identity and needs its resulting digest recorded, platforms inspected, required scans/tests rerun or an explicitly approved equivalence check, and provenance/signature policy satisfied for that identity.
4. The copy may produce a single-platform AMD64 manifest instead of preserving the candidate's multi-platform index, so ARM64 nodes may fail to pull or may not receive the intended platform image. Copy the full image list and index, inspect its platform descriptors, and verify the destination digest before release.
5. Compare the attested repository, source ref, workflow, builder identity, and artifact subject digest to the organization’s expected values. A valid signature from an untrusted build context is not an acceptable release.

## Review questions

- Why is “same commit” weaker than “same artifact” as a deployment guarantee?
- What does a content digest establish, and what security questions does it leave open?
- When should a registry copy be treated as creating a new release identity?
- Why should environment configuration and secrets stay separate from the image?
- What is the difference between verifying a provenance signature and accepting the provenance under policy?

## Takeaways

- Build the release candidate once and record its registry digest; run release gates against that identity.
- Promote a tested artifact through environments, and record every expected identity change explicitly.
- Use tags for people and workflow convenience, while deployments refer to digests.
- Verify provenance against a trusted builder and expected source, workflow, and artifact subject; a valid signature alone does not approve a release.
- Keep runtime configuration separate from image contents and make rollback point to a retained known-good digest.

## Further reading

- [OCI Image and Distribution specifications](https://specs.opencontainers.org/image-spec/descriptor/)
- [SLSA verification guidance](https://slsa.dev/spec/v1.2/verifying-artifacts)
- [Skopeo copy reference](https://github.com/containers/skopeo/blob/main/docs/skopeo-copy.1.md)
- [GitHub artifact attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations)
- [Docker image validation policies](https://docs.docker.com/build/policies/validate-images/)

Sources reviewed 2026-10-04. Examples are illustrative; no image build, registry copy, provenance verification, or deployment was executed.
