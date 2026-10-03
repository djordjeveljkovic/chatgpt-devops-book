---
book: The Complete DevOps Engineering Book
volume: 7
volume_title: "Podman and the Rootless Host"
chapter: 68
title: "Buildah and Skopeo Workflows"
slug: buildah-and-skopeo-workflows
status: complete
summary: ../../_ai/chapter-summaries/068-buildah-and-skopeo-workflows.md
---

# Chapter 68 — Buildah and Skopeo Workflows

## Building OCI images with Buildah

DispatchDesk wants to build an image in one environment and deploy it in another without depending on a permanently running Docker daemon. Buildah constructs container images; Skopeo inspects and transfers image artifacts through explicit transports. These tools separate artifact production from running a service. They do not eliminate supply-chain review, registry authentication or platform compatibility.

Read [image identity](../05-container-internals-and-oci/044-images-layers-and-content-identity.md), [publishing and promotion](../06-docker-in-practice/059-publishing-and-promoting-images.md), and [SELinux mounts](067-selinux-and-container-mounts.md) first. The lab runs on a disposable local Linux host as one ordinary account with working rootless namespaces/storage, registry access, Buildah, Skopeo, Podman, `jq` and Python 3. It creates no cloud resources or production registry content.

Administrators install the tools using their supported repositories. On Ubuntu 24.04 LTS:

```bash
sudo apt-get update
sudo apt-get install buildah skopeo jq
```

On Fedora 44, or separately on subscribed supported RHEL 9/10 with container-tool packages available:

```bash
sudo dnf install buildah skopeo jq
```

Do not infer matching versions from matching package names. Inspect each executable and record it with the build evidence:

```bash
buildah --version
skopeo --version
podman --version
```

Buildah and Podman can share image storage when used by the same account under compatible storage configuration. They do not share the meaning of their working/running container objects. A Buildah working container is a construction workspace, not a systemd-managed application service. Skopeo's `containers-storage:` transport must also address the intended compatible local store; rootful invocation or environment overrides can select another store.

Create a new dedicated working directory and stop if it already exists:

```bash
mkdir -m 700 "$HOME/dd-artifact-68"
cd "$HOME/dd-artifact-68"
printf 'DispatchDesk artifact fixture\n' > message.txt
chmod 0644 message.txt
```

The explicit mode makes the non-sensitive fixture readable by the image's UID 65532 even when the host account uses a restrictive umask such as 077. `COPY` preserves source permissions, so relying on the caller's umask could leave the image process unable to read its input.

Save this complete `Containerfile`:

```dockerfile
FROM docker.io/library/busybox:1.37
COPY message.txt /message.txt
USER 65532:65532
ENTRYPOINT ["cat", "/message.txt"]
```

This is a deliberately tiny artifact fixture. It demonstrates copied content, a non-root container process and an exec-form entrypoint. It does not implement the DispatchDesk application. The base tag is mutable, so production builds should resolve and record a verified base digest. Build contexts must exclude credentials and unnecessary files; the context directory here contains only the fixture inputs and subsequent evidence files.

```bash
buildah build --format oci --tag localhost/dd-artifact-68:lab \
  --file Containerfile .
podman --remote=false image inspect localhost/dd-artifact-68:lab
podman --remote=false run --rm localhost/dd-artifact-68:lab
```

The final dot supplies the build context. `--file` selects the recipe, `--tag` assigns a local reference and `--format oci` requests OCI image formatting. The [Buildah build manual](https://github.com/containers/buildah/blob/main/docs/buildah-build.1.md) documents its supported flags. Successful runtime acceptance should print the copied fixture text and exit successfully. These are expected observations, not author-measured results.

The build is simple enough that application compilation cannot obscure artifact transfer. For a real Go, Python or Node.js service, keep the existing application contract and build tests from the Docker volume. Changing the builder does not justify replacing language dependency locks or approved test gates. A reproducible recipe can still produce different output if it downloads mutable dependencies or includes timestamps; record inputs and compare artifacts rather than calling every Containerfile build reproducible.

## Inspecting and copying images with Skopeo

Skopeo identifies sources and destinations by transport. A remote registry uses `docker://`; a local OCI layout uses `oci:`; the local container store uses `containers-storage:`. The spelling expresses where content comes from. A registry reference without a transport is not interchangeable with a host path.

Inspect a remote base without starting its container:

```bash
skopeo inspect docker://docker.io/library/busybox:1.37 > base-inspect.json
skopeo inspect --raw docker://docker.io/library/busybox:1.37 > base-manifest.json
jq '{Name, Digest, Architecture, Os}' base-inspect.json
```

Ordinary inspection provides selected image metadata; raw inspection returns manifest content. For a multi-platform tag, understand whether you are recording an index or a selected platform image. The [Skopeo inspect manual](https://github.com/containers/skopeo/blob/main/docs/skopeo-inspect.1.md) explains platform selection and raw output. The remote tag can change between two requests, so a production evidence procedure should resolve one immutable reference and inspect that reference thereafter.

Copy the newly built local fixture to an OCI layout:

```bash
skopeo copy containers-storage:localhost/dd-artifact-68:lab \
  oci:dd-layout:lab
skopeo inspect oci:dd-layout:lab > layout-inspect.json
python3 - <<'CHECK'
import hashlib
import json
from pathlib import Path
root = Path('dd-layout')
index = json.loads((root / 'index.json').read_text())
assert index['schemaVersion'] == 2
for descriptor in index['manifests']:
    algorithm, digest = descriptor['digest'].split(':', 1)
    assert algorithm == 'sha256'
    data = (root / 'blobs' / algorithm / digest).read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest
print('Top-level manifest descriptors match local blob bytes')
CHECK
```

The layout directory contains content-addressed blobs and an index. The short Python check verifies each top-level descriptor against its corresponding local manifest blob; it does not recursively validate every layer, establish signature trust, or certify application behavior. Its deliberately narrow message prevents a hash comparison from being mistaken for a complete supply-chain check.

## A registry-independent image workflow

An OCI layout lets this fixture cross a controlled boundary without publishing it to a registry. On this same lab host, import it under a second local name and run that name:

```bash
skopeo copy oci:dd-layout:lab \
  containers-storage:localhost/dd-artifact-68:imported
podman --remote=false image inspect localhost/dd-artifact-68:imported
podman --remote=false run --rm localhost/dd-artifact-68:imported
```

For another host, transfer the complete layout through an approved authenticated channel, verify its transport integrity, inspect descriptors there, and import using that host's owning account. The destination needs a compatible architecture and supported store. A file copied successfully does not establish that its image can run on that machine.

This fixture contains one built platform. Copying a multi-platform index has different requirements. Skopeo's `--all` option is relevant when preserving every image in a list; confirm source and destination support. Its [copy manual](https://github.com/containers/skopeo/blob/main/docs/skopeo-copy.1.md) also documents digest-preservation and format options. Do not apply `--all` to a single-platform fixture and claim that additional architectures were built.

If a transfer performs manifest-format conversion or recompression, the destination's manifest digest may differ while the executable content is related. Decide whether exact digest preservation is required, use a supported preservation option when appropriate, and inspect destination identity after copying. A tag with the same spelling in two registries is not proof of byte-identical manifests. Promotion evidence should connect source digest, destination digest, platform and verification result explicitly.

Skopeo does not scan images merely by copying them. Keep signature verification, vulnerability assessment, provenance and deployment approval as separate gates. A content hash detects changed bytes; it does not tell you whether the approved author produced those bytes or whether they contain a vulnerable dependency. Offline transfer must carry the relevant evidence and trust policy, not only the layers.

## Failure, diagnosis and recovery

Suppose Skopeo cannot find `localhost/dd-artifact-68:lab` in `containers-storage:` after Buildah reports success. First compare account, privilege, storage configuration and the exact name. A rootful Skopeo command may address another store. Buildah's working-container name is also not the image tag. Inspect Buildah images and Podman images under the intended account before rebuilding.

Suppose a build works on a developer machine but fails in a CI container with an operation-not-permitted error. Determine the denied stage: user namespace setup, storage mounts, a `RUN` instruction or cgroup access. An outer container's security restrictions can prevent nested rootless builds. Blindly switching the runner to privileged mode changes a major security boundary. Select an approved runner/build isolation design with the necessary documented capabilities and verify its threat model.

Suppose the destination rejects a manifest format. Preserve the source artifact and error, inspect destination supported formats and choose an approved conversion strategy. Then record its new digest and repeat runtime acceptance. Do not disable TLS verification to diagnose a format error: certificate verification and manifest support are independent layers.

Suppose a copied image prints old text. Compare the actual local tag, image ID, layout reference and destination inspection. A rebuild can move a tag while a prior OCI layout still contains the earlier artifact. Immutable release records prevent a later tag from rewriting what an incident report claims was deployed.

## Cleanup and assessment

After retaining evidence elsewhere if needed, remove only the two fixture tags and the dedicated directory. Check for collisions with other exercises first. `buildah rmi` removes image references/content subject to its usage constraints; do not use a global “all” option.

```bash
buildah rmi localhost/dd-artifact-68:lab
podman --remote=false image rm localhost/dd-artifact-68:imported
cd "$HOME"
rm -r -- "$HOME/dd-artifact-68"
```

The final command recursively deletes the dedicated lab tree, including copied artifact blobs and evidence files. It is destructive and appropriate only after confirming that exact directory contains this disposable exercise.

## Exercises and review questions

1. Explain why a successful OCI layout copy does not prove a production image is trusted. **Guidance:** bytes, signatures/provenance, vulnerabilities, application tests and approval answer different questions.
2. Extend the Python checker conceptually to recurse through manifest layer/config descriptors. **Guidance:** hash each referenced blob, verify sizes, distinguish indexes from manifests, and reject missing content; this still is not signature trust.
3. A multi-platform tag becomes one platform after copying. **Guidance:** inspect index/platform selection and whether `--all` was required and supported.
4. Buildah sees an image but rootful Skopeo does not. **Guidance:** account and storage selection come before image reconstruction.

## Takeaways and further reading

Keep artifact building, transfer, identity and runtime acceptance distinct. Transport prefixes and verified digests make the boundary inspectable. Continue with [Docker migration](069-migrating-docker-workflows-to-podman.md).

Buildah build/rmi and Skopeo inspect/copy primary manuals were inspected 2026-10-03. No package installation, image build, copy, registry interaction or fixture execution was performed by the author.
