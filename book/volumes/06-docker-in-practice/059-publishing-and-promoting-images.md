---
book: The Complete DevOps Engineering Book
volume: 6
volume_title: "Docker in Practice"
chapter: 59
title: "Publishing and Promoting Images"
slug: publishing-and-promoting-images
status: complete
summary: ../../_ai/chapter-summaries/059-publishing-and-promoting-images.md
---

# Chapter 59 — Publishing and Promoting Images

Building an image is only one step in releasing a service. A deployment system needs to retrieve the same tested artifact in each environment, identify exactly which bytes it selected, and keep the credentials used to publish separate from credentials used to run the workload. A tag gives an image a human-readable name. A digest identifies a manifest by content. Treating those references as interchangeable is a common source of “works in staging, differs in production” failures.

This chapter uses a fictional private registry at `registry.example.internal` and DispatchDesk's API image. Replace the hostname, repository, namespace and credentials with values approved for your organization. Do not push example content to a public registry. The build context and Dockerfile follow [Chapter 53](053-dockerfiles-and-build-contexts.md); cache and multi-platform build concerns are covered in [Chapter 54](054-buildkit-caching-and-multi-stage-builds.md), and diagnosis of failed containers is in [Chapter 58](058-inspecting-and-debugging-docker.md).

## Registry login, tagging and digest identity

A registry stores image manifests and their referenced configuration and layers. It may serve tags, digests, or both. The registry hostname is part of the image name: `registry.example.internal/dispatchdesk/api:...` identifies a repository on that registry. A bare name such as `dispatchdesk/api` ordinarily refers to Docker Hub, which is not the private destination intended here. Confirm the registry's TLS, access policy, retention rules, namespace and region before publishing. A registry outage or quota limit can block a release even when the local build succeeded.

Use a short-lived, least-privilege publishing identity. For a human operator, configure Docker's credential helper and authenticate interactively:

```bash
docker login registry.example.internal
```

The command prompts for credentials or uses the configured helper. In automation, obtain a short-lived token from the CI platform's approved identity integration and pass it through standard input rather than a command-line argument:

```bash
printf '%s' "$REGISTRY_TOKEN" |
  docker login registry.example.internal \
    --username "$REGISTRY_USER" \
    --password-stdin
```

`REGISTRY_TOKEN` and `REGISTRY_USER` must be injected by the CI secret or workload-identity mechanism, not committed in a file or echoed to logs. Do not enable shell tracing around credentials. The Docker CLI may store credentials in its configuration or credential helper; use an isolated CI configuration directory and remove it at job cleanup when the runner is persistent. Removing the directory alone does not erase credentials held by an external helper; run the helper-aware `docker logout registry.example.internal` and revoke the short-lived token or identity grant according to the CI provider's cleanup procedure. A successful login proves only that the credential was accepted, not that it has the intended repository scope or that the image passed review. Prefer separate pull-only runtime credentials and publish credentials that can write only to the required repository.

Tags are mutable names unless the registry enforces immutability. Teams commonly use a commit identifier for a build, a semantic version for a release, and a channel tag such as `production` for convenience. The channel tag can be moved; it is not a durable audit record. A digest such as `registry.example.internal/dispatchdesk/api@sha256:…` names a specific manifest. Record and deploy the digest that the registry reports after publication. Do not copy a fabricated digest into configuration: obtain the real value from the registry and verify it in the release record.

## Build once, then promote

The build should happen once for a source revision and target platform set. Run the build from a clean checkout and an explicitly selected context. This example assumes a CI job has set `GIT_SHA` to the full source revision, and `BUILD_CONTEXT` to the directory containing the Chapter 53 Dockerfile and ignore file. Validate both before constructing the tag:

```bash
case "${GIT_SHA:-}" in
  *[!0-9a-f]*|'') printf '%s\n' 'GIT_SHA must contain lowercase hexadecimal characters' >&2; exit 2 ;;
esac
if [ "${#GIT_SHA}" -ne 40 ]; then
  printf '%s\n' 'GIT_SHA must be a full 40-character commit ID' >&2
  exit 2
fi
if [ ! -f "$BUILD_CONTEXT/Dockerfile" ]; then
  printf '%s\n' 'BUILD_CONTEXT must contain the reviewed Dockerfile' >&2
  exit 2
fi

image=registry.example.internal/dispatchdesk/api
build_tag="git-$GIT_SHA"
docker build --pull --tag "$image:$build_tag" "$BUILD_CONTEXT"
docker image inspect "$image:$build_tag" \
  --format 'id={{.Id}} tags={{json .RepoTags}}'
docker image push "$image:$build_tag"
```

The `case` rejects empty or non-hexadecimal revisions, and the length check requires a full commit ID rather than an ambiguous prefix. The context check catches a common CI working-directory error before Docker sends files to the builder. `--pull` checks for an updated base image; for strict reproducibility, the Dockerfile should pin base images by digest and dependencies should use lockfiles as discussed in Chapters 49 and 53. A Docker build can still differ because of platform, builder version, build arguments or network-fetched inputs, so record those inputs with the build. The local image ID shown by `docker image inspect` is useful evidence, but the registry manifest digest is the deployment reference.

After the push, inspect what the registry serves:

```bash
docker buildx imagetools inspect "$image:$build_tag"
```

Record the top-level digest and the platform manifests shown in the output. Multi-platform images can have a top-level image index pointing to separate per-platform manifests; a digest for one platform is not necessarily the index digest selected by a multi-platform tag. When an expected architecture is absent, stop promotion and rebuild for the required platforms using the reviewed build process. Do not silently substitute a developer's local image.

Promotion means making the same reviewed build available under a release reference and deploying the verified digest. It does not mean rebuilding with a different Dockerfile, secret, dependency resolution or base image for each environment. Registry tooling can copy or create tags from an existing digest, but media-type conversion or registry behavior may produce a different top-level digest. Inspect the destination after any copy and record its resulting digest; compare platform manifests and image configuration before claiming byte identity. Use a registry-native promotion operation when available, because it can avoid downloading layers through an operator workstation and retain registry-side provenance.

For a registry that supports Docker Buildx imagetools, a source digest can be referenced while creating release tags. `imagetools create` defaults to `--prefer-index=true`: when its single source is already a manifest list or index, Buildx copies that index; when the source is one ordinary platform manifest, it wraps that manifest in a new index. Use `--prefer-index=false` when preserving an ordinary manifest is required and supported by the installed Buildx version. The output digest can therefore change even when the referenced platform image content is unchanged; inspect the destination and compare the platform manifests before release.

```bash
source_digest=sha256:REPLACE_WITH_DIGEST_REPORTED_BY_SOURCE_REGISTRY
docker buildx imagetools create \
  --tag "$image:1.4.0" \
  --tag "$image:production" \
  "$image@$source_digest"
docker buildx imagetools inspect "$image:1.4.0"
```

Replace the placeholder with the real digest captured from the preceding registry inspection; the command is intentionally not copy-and-paste ready until that evidence exists. `1.4.0` is a fictional release version. Apply registry tag immutability to version tags where supported, and restrict who may move mutable channel tags. Confirm the post-promotion digest and platform list. If the registry reports a new top-level digest, compare the source and destination manifests and configurations before deployment. A tag alone is not proof that the release is the intended artifact.

The deployment manifest should prefer a digest-qualified reference when the platform supports it:

```yaml
image: registry.example.internal/dispatchdesk/api@sha256:REPLACE_WITH_VERIFIED_RELEASE_DIGEST
```

Keep the human release version in the deployment metadata or release record as well. That record should link the source commit, build job, builder/platform inputs, published tag, verified digest, approval, vulnerability and policy results, and the deployment change. A rollback then selects a known prior digest instead of hoping that a mutable `previous` tag still points to the same content.

## Releasing a versioned service

Suppose DispatchDesk version 1.4.0 fixes a request-timeout bug. The team builds one candidate from a reviewed commit, publishes it to the private registry, runs image and application checks against that exact candidate digest, then authorizes the release. Staging and production deploy the approved digest; environment-specific configuration arrives through the deployment system, not by rebuilding the image with secrets baked into a layer. A staging success is evidence about that digest and staging configuration, not proof that production's credentials, database or firewall are correct.

Before promotion, check that the candidate repository is the intended registry, the tag points to a digest, all required architectures exist, the image starts under the expected user, and vulnerability/licensing/signature policies passed for the exact digest. The policy owner defines acceptable findings and exception expiry; a scanner's “no critical findings” summary does not prove that an image is safe or that its software inventory is complete. Signatures, attestations and provenance can strengthen the chain of evidence, but verify the signing identity and policy rather than treating their presence as automatic trust.

If a push reports success but the tag cannot be pulled, separate authentication, authorization, naming, network and retention failures. Confirm the registry host and repository path, inspect the exact tag, attempt a pull using a read-only deployment identity, and compare the returned digest with the release record. A successful publisher login with a failed pull can indicate separate permissions or an incorrect namespace. If a tag unexpectedly resolves to a new digest, freeze deployment, preserve current references and audit who can write that tag before changing production. Do not force-push an older image over a tag until the registry's immutability and rollback procedures are understood.

For cleanup, remove only local candidate tags after the registry and deployment references are confirmed. Local deletion does not delete the remote registry object; registry retention and garbage collection are separate administrative operations. Avoid deleting a digest while another tag, deployment or rollback record still depends on it. Keep release digests available for the organization's rollback and incident-retention period.

## Exercises and review questions

1. What is the difference between a mutable tag and a digest-qualified image reference? Which should a production deployment record use, and why?
2. A developer logs into the registry successfully but the CI push is denied. List checks that distinguish bad credentials from missing repository permission or a wrong image name.
3. A multi-platform candidate has an `amd64` manifest but no `arm64` manifest. What evidence should block promotion, and what should the build owner do?
4. A release tag points to a different digest after promotion. What do you compare before deploying, and when should promotion stop?
5. Why should staging and production deploy the same image digest while using different configuration and secrets?

### Answer guidance

1. A tag is a human-readable pointer whose target can change; a digest identifies manifest content. Record the version for people, but deploy and audit the verified digest so the selected artifact is unambiguous.
2. Check the registry hostname and namespace in the image reference, the CI identity/token expiry, repository write scope, credential helper/config context, and registry audit response. Successful authentication does not imply push authorization.
3. The registry index/platform list is evidence that the required architecture is missing. Stop promotion and rebuild the same reviewed source for the approved platform set; do not substitute a workstation-built image.
4. Compare source and destination top-level manifests, per-platform manifest digests, image configuration and layer descriptors. Pause promotion if the approved content cannot be tied to the destination digest; investigate registry conversion or tag mutation before deployment.
5. A common digest keeps software content consistent across environments, while external configuration supplies environment-specific endpoints and credentials. Rebuilding per environment would create unreviewed artifact differences and can accidentally embed secrets.

## Takeaways

- Authenticate with scoped, short-lived credentials and keep publish access separate from runtime pull access.
- Tags support human workflows but can move; record the registry digest and platform set for each release.
- Build a candidate once from reviewed source, test that exact artifact, and promote it without an environment-specific rebuild.
- Verify the destination after registry promotion because copying or media conversion may change the top-level digest.
- Deploy digest-qualified references and retain release evidence and prior digests for rollback.

## Further reading

- [Registries and Image Distribution](../05-container-internals-and-oci/049-registries-and-image-distribution.md) — registry namespaces, artifact identity and distribution.
- [BuildKit, Caching and Multi-stage Builds](054-buildkit-caching-and-multi-stage-builds.md) — build inputs, cache scope and multi-platform output.
- [Inspecting and Debugging Docker](058-inspecting-and-debugging-docker.md) — diagnose an image that fails after deployment.
- [Release Engineering and Artifact Promotion](../14-delivery-deployment-and-gitops/131-release-engineering-and-artifact-promotion.md) — approvals and release records across environments.

## Sources and verification

Docker's official [`docker login`](https://docs.docker.com/reference/cli/docker/login/), [`docker image push`](https://docs.docker.com/reference/cli/docker/image/push/), [`docker image tag`](https://docs.docker.com/reference/cli/docker/image/tag/), [Buildx `imagetools inspect`](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/), [Buildx `imagetools create`](https://docs.docker.com/reference/cli/docker/buildx/imagetools/create/) and [Docker Hub immutable tags](https://docs.docker.com/docker-hub/repos/manage/hub-images/immutable-tags/) documentation were inspected on 2026-10-03. The registry hostname, credentials, release version and digest are examples; no registry push, authentication, image build or deployment was performed. Shell and local links will be checked statically; that does not validate a registry's actual authorization, retention or promotion behavior.
