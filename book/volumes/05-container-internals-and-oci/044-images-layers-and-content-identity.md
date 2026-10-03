---
book: The Complete DevOps Engineering Book
volume: 5
volume_title: "Container Internals and OCI"
chapter: 44
title: "Images, Layers and Content Identity"
slug: images-layers-and-content-identity
status: complete
summary: ../../_ai/chapter-summaries/044-images-layers-and-content-identity.md
---

# Chapter 44 — Images, Layers and Content Identity

## Separate a name from the bytes

An image tag such as `dispatchdesk:stable` is a human-readable name that a registry or local engine can update to refer to different content. A digest identifies bytes by a content hash. If Harbor deploys a verified image digest, it can ask whether every host received the same manifest content. If it deploys a mutable tag, the answer may change between pull times.

Digest identity does not establish who built the image, whether its inputs were trustworthy, or whether the program is safe. Those require provenance, source review, build controls, vulnerability response and signature or policy checks. A hash helps detect content changes relative to a trusted digest; it does not make the digest trustworthy by itself.

The Open Container Initiative (OCI) image format describes an image manifest, optional image index, configuration and filesystem layers. A manifest identifies the image configuration and ordered layer descriptors by media type, digest and size. An image index can point to different platform-specific manifests, such as a Linux image for arm64 and another for amd64. A deployment must know whether the recorded digest refers to the multi-platform index or a platform-specific manifest, and which platform the host selects.

## Understand the layer stack

Each filesystem layer is a changeset. Applying layers in order to an empty directory produces the image's merged root filesystem. A layer can add or replace files, change metadata or represent deletion of a prior path using a whiteout marker. The runtime presents the resulting tree as one filesystem view. Image configuration is separate from the filesystem changes: it includes defaults such as entry point, arguments, environment, working directory and user metadata.

Layer reuse can reduce transfer and storage when several images share identical base content. It does not mean the image is small at runtime: files in lower layers still occupy storage, and a file later deleted by a whiteout remains present in an earlier layer's bytes. A build that adds a large archive and removes it in a later instruction may still distribute the large archive. Arrange build steps so unnecessary material does not enter a committed layer, and use multi-stage builds when build tools should not be in the runtime image.

Layer boundaries also affect build caching. If an earlier layer changes, later dependent steps may need rebuilding. Stable, infrequently changed dependencies can be separated from application source to improve reuse, but build-cache correctness depends on declaring inputs and invalidating when they change. A cache is a speed mechanism, not a reliable record of what source or credentials produced an artifact. [Chapter 54](../06-docker-in-practice/054-buildkit-caching-and-multi-stage-builds.md) covers build behavior.

## Read image identity carefully

Several identifiers are easy to confuse:

| Identifier | What it identifies | What it does not prove |
|---|---|---|
| Tag, such as `:1.8.2` | A name resolved by a registry or local engine | Immutable content or publisher identity |
| Image configuration ID | The image configuration and its root filesystem diff identity under the image model | The registry manifest chosen for a specific platform |
| Layer digest | A specific encoded layer blob referenced by a descriptor | The complete image or its source history |
| Manifest digest | A specific manifest object and its referenced config/layers | Signature validity, publisher, or that a host runs it |
| Index digest | A multi-platform index selecting one or more platform manifests | Which platform variant a host selected without platform context |

Digest calculation includes exact bytes. Recompressing a layer can change the descriptor digest even if its unpacked files are equivalent. OCI distinguishes a layer DiffID over uncompressed layer content from a descriptor digest over the referenced blob representation. This is why two tools can produce semantically similar filesystems with different image digests. Reproducible builds seek the same outputs from controlled inputs; image digest verification checks the identity of one output.

For a release, record the repository name, manifest or index digest, selected platform, source revision, build pipeline run and provenance evidence together. Deploy by digest where supported. Keep the tag as a useful label for people, not as the only release identity. When promoting across environments, move or copy the artifact without rebuilding it, then verify that the destination digest is the intended one. [Chapter 59](../06-docker-in-practice/059-publishing-and-promoting-images.md) develops this process.

## A small inspection model

When examining an OCI image layout or registry manifest, answer these questions in order:

1. Is this a manifest or a multi-platform index?
2. Which operating system and architecture does each selected manifest describe?
3. Which config digest and ordered layer descriptors does the manifest reference?
4. Does the recorded digest match the bytes retrieved from the trusted registry endpoint?
5. What evidence binds the digest to the reviewed source and build process?
6. What runtime configuration, mounts, user, capabilities and limits will the engine apply?

An image archive can be inspected without starting its entry point, but archive inspection does not prove runtime behavior. Treat metadata as input to deployment review. An image can request a default user or expose a port as metadata; the engine's actual run configuration and host policy determine effective identity and network publication. The container process still has the host-kernel boundaries described in Chapters 41–43.

## Supply-chain and cleanup implications

Image layers can preserve secrets even if a later layer deletes the file. Do not copy credentials into build context or an image layer and rely on deletion in a subsequent step. Use a build-secret mechanism that exposes a secret only to the step that requires it, and verify that build logs and caches do not retain it. The final artifact should contain only runtime dependencies and necessary files.

Registry cleanup should follow retention policy. Deleting a tag can remove a human alias while content remains referenced by another tag, index or deployment. Deleting content-addressed objects can break rollback or a still-running host that has not pulled its replacement. Record deployed digests, retain the required rollback set and understand registry garbage-collection behavior before pruning.

## Exercises and review questions

1. Explain why a tag can point to different image bytes next week while a digest remains content-addressed.
2. A multi-platform tag resolves to an index. What extra evidence is needed to confirm the arm64 server runs the intended arm64 manifest?
3. A build copies a private key into one layer and removes it in a later layer. Why can the key remain recoverable from the image?
4. A release manifest digest differs after copying to a registry. Which content and metadata should be compared before deployment?
5. What should be recorded to connect a running DispatchDesk image to reviewed source code?

**Answer guidance:** For exercise 1, a tag is a mutable name that a publisher can move; a digest is computed over exact bytes, so changing those bytes produces a different digest. For exercise 2, record the index digest, the selected `linux/arm64` child manifest digest, platform/variant and runtime-reported image identity; confirm the child descriptor is referenced by the index. For exercise 3, image layers are separate content-addressed changesets, so deleting a secret in a later layer hides it in the merged filesystem but leaves its bytes in the earlier layer. Rebuild without the secret and rotate it. For exercise 4, compare source and destination index and child-manifest descriptors, config digests, layer digests/sizes and media types; a conversion or recompression can change representations, so require a documented equivalence and revalidate signatures/provenance instead of assuming the old digest applies. For exercise 5, retain the reviewed commit, build inputs and builder/pipeline identity, base-image digests, target platform, provenance/signature, promoted manifest or index digest, deployment reference and runtime-resolved identity.

Image layers make distribution efficient and content hashes make artifacts addressable, but trusted delivery needs evidence that connects bytes to source and policy. Next, [Container Filesystems and Storage](045-container-filesystems-and-storage.md) follows writes from the image's read-only layers to mutable container and persistent storage.

## Sources and verification

The OCI [Image Specification](https://raw.githubusercontent.com/opencontainers/image-spec/main/spec.md), [manifest](https://raw.githubusercontent.com/opencontainers/image-spec/main/manifest.md), [configuration](https://raw.githubusercontent.com/opencontainers/image-spec/main/config.md) and [layer](https://raw.githubusercontent.com/opencontainers/image-spec/main/layer.md) specifications were inspected on 2026-10-04. This chapter contains no registry push, image build or platform-selection result from an executed container.
