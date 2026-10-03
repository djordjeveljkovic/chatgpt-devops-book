---
book: The Complete DevOps Engineering Book
volume: 5
volume_title: "Container Internals and OCI"
chapter: 49
title: "Registries and Image Distribution"
slug: registries-and-image-distribution
status: complete
summary: ../../_ai/chapter-summaries/049-registries-and-image-distribution.md
---

# Chapter 49 — Registries and Image Distribution

## A registry distributes named content

A container registry stores image manifests, indexes and layer blobs so clients can pull or push content. A repository groups related content under a registry host and namespace. A tag is a mutable human label; a digest identifies a specific content object. The registry handles distribution and authorization, while the deployment process decides which digest is approved to run.

OCI's Distribution Specification defines an HTTP API for discovering and transferring content. It builds on the registry protocol used by Docker-compatible tools. A client can request a manifest by tag or digest, receive descriptors for required blobs, and download missing layers. Efficient clients reuse layer content already present in local storage. Pulling an image does not start its application; the engine later creates and launches a container from the selected platform-specific manifest.

Public and private registries have different access and operational policies. A public image may still require authentication for rate limits or organizational policy. A private registry requires an identity with access to the requested repository. A pull-only deployment credential should not be able to push or delete production artifacts. CI publishing identities need scoped write access and should not be reused as runtime credentials.

## Authenticate without leaking credentials

Registry authentication often uses a challenge flow: the registry requests authorization, a trusted token service issues a scoped bearer token, and the client retries the operation. The token's scope should match the repository and action. Protect it like a password while it is valid. Use TLS with certificate validation so credentials and image content are protected in transit and the client knows which registry endpoint it reached.

An interactive Docker login to a private registry can prompt for an access token without placing the token in shell history:

```bash
docker login registry.example.net --username harbor-deployer
```

The hostname is fictional and is not contacted by this book check. Authenticate only to the intended registry. Docker may store credentials using a configured credential helper or operating-system credential store. Without a helper, some Docker installations store an encoded credential in the client configuration file; base64 encoding is not encryption. Restrict access to the config directory, avoid committing it, and log out or rotate credentials when the operator or workload no longer needs them. Podman has its own auth-file behavior; check its current manual and storage permissions.

Automation should read a short-lived, narrowly scoped token from its secret manager and pipe it to the CLI's standard input using the documented `--password-stdin` flow. Do not put tokens in command-line arguments, Dockerfiles, build arguments, process listings or logs. On a shared CI runner, ensure the runner's engine credentials cannot be read by unrelated jobs. Separate pull-only deployment credentials from push-capable build credentials.

## Pull an exact release artifact

For a production rollout, resolve and approve the image digest during the build and promotion process, then pull by digest. The following is a template; replace the digest with the verified manifest or index digest recorded by that process:

```bash
image_ref='registry.example.net/harbor/dispatchdesk@sha256:REPLACE_WITH_VERIFIED_DIGEST'
docker image pull "$image_ref"
docker image inspect "$image_ref" --format '{{.Id}} {{.Os}}/{{.Architecture}}'
```

The pull selects exact manifest content rather than resolving a moving tag at deployment time. If the digest identifies a multi-platform index, the engine selects the child manifest matching the host platform. Record the platform and selected manifest as well as the index digest when incident analysis requires exact deployed bytes. The local image `.Id` commonly describes the image configuration and is not necessarily the registry manifest digest. Do not mistake one identifier for another.

An image pull can fail because DNS cannot resolve the registry, TLS validation fails, authentication is missing, repository scope is denied, the manifest has no matching platform, or a layer transfer is interrupted. Diagnose each boundary from client output and engine logs. A certificate failure should be repaired by using the correct trust chain and hostname, not by marking a production registry as insecure. In the documented bearer-token flow, an initial HTTP 401 with `WWW-Authenticate` is the normal challenge that tells the client how to request a scoped token; a 401 that persists after the client obtains and presents that token suggests an authentication/token problem. A 403 commonly indicates authorization or scope denial, but registries can vary in how they report private-resource failures.

## Manage repository and retention boundaries

Use fully qualified image references in automation so the intended registry and namespace are explicit. A short name such as `dispatchdesk:latest` may resolve through engine-specific search registries or a default public registry. This can produce a different image than intended and complicate audit evidence. Configure approved registries and mirrors through the engine's supported policy, and verify that a mirror preserves trust and digest identity.

Retain every digest still used by a deployment or required rollback. A tag can move or be deleted while an image digest remains in storage; registry cleanup policies may remove untagged content after a configured period. Document how tags are assigned, whether they can be overwritten, who can delete manifests and how replication behaves across regions. Validate retention against release and incident-recovery windows before enabling automated garbage collection.

Registry availability and download quotas are production dependencies. Mirror approved base images where policy permits, use pull-through caches when the workload and registry support them, and monitor authentication failures, rate limits, latency and storage capacity. A cache improves availability only for content it has already retained; it does not make a new release available if the upstream is unreachable. Keep the verified artifact available in an alternate approved path for recovery when the primary registry is unavailable.

Signing and provenance systems attach trust evidence to image content, often keyed to a digest. Verify the signature or attestation against an independently managed identity and policy before deployment. A signature says that a particular key or identity signed a statement; policy determines whether that signer and statement are acceptable. If an image is rebuilt or transformed, its digest changes and the associated evidence must be checked again. Chapter 59 covers artifact promotion and evidence across environments.

## Debug distribution failures safely

If a pull says “not found,” confirm the fully qualified registry, namespace, repository and digest. Some registries avoid revealing whether an unauthorized private repository exists, so an authorization failure may look like absence. A successful `docker login` authenticates the supplied identity to the registry and stores or retrieves its credentials using the configured helper or client mechanism. That identity may still lack authorization for a particular repository, action or tag; inspect its scope and the identity used by the engine.

If a deployment unexpectedly runs older code, compare the requested reference, resolved manifest digest, selected platform, node-local cache and runtime's actual image ID. Tags may point to different digests on different hosts. Record the digest at build, promotion, deployment and runtime inspection points so the mismatch can be located.

If registry credentials leak, revoke them at the issuing authority, remove them from runner or operator stores, review access logs, rotate dependent secrets and rebuild any image that could contain the credential in a layer. Deleting the exposed tag alone does not revoke a token or erase already pulled content.

## Exercises and review questions

1. Why does `docker login` success not prove that a pull-only identity can access a specific private repository?
2. Explain the difference between a mutable tag, an image index digest, a platform manifest digest and a local image config ID.
3. A CI job can push and delete every production image but only needs to publish one build. Which identity scope should be reduced?
4. What happens to availability when a registry is down and a node has never pulled the requested digest?
5. Design a rollback retention rule that protects deployed digests without keeping every experimental build forever.

**Answer guidance:** For exercise 1, login establishes the registry identity, but repository pull authorization is a separate scoped decision; verify the identity has read access to that exact repository and action. For exercise 2, distinguish the mutable human tag, top-level index digest, platform-specific child manifest digest and local image configuration ID; record the selected child for the target platform. For exercise 3, use a short-lived identity scoped to push the intended repository/build and deny production deletion or unrelated repositories; separate promotion/deployment credentials. For exercise 4, the node cannot fetch uncached content until the registry or an approved mirror/cache becomes reachable, so maintain an already-pulled rollback digest or alternate approved artifact path. For exercise 5, retain all currently deployed digests plus the tested rollback window and release evidence, and remove only artifacts proven outside deployment/retention references under a reviewed cleanup policy.

Registries distribute content and enforce access; a secure release process binds an approved digest to trusted source and build evidence. The next chapter defines the container contract that application teams should keep stable across Docker, Podman and production platforms.

## Sources and verification

The OCI [Distribution Specification](https://specs.opencontainers.org/distribution-spec/), Docker [`login`](https://docs.docker.com/reference/cli/docker/login/), [registry authentication](https://docs.docker.com/reference/api/registry/auth/) and [credential configuration](https://docs.docker.com/reference/cli/docker/) documentation were inspected on 2026-10-04. The login and pull examples use fictional values and were not run. Registry-specific quotas, retention, credential helpers and policy vary by provider and client version.
