# Independent review — Chapter 68

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: c29358e8f72ad77707d24d24433f1bc1e412363beca26d9d55aa98217afda17f

## Findings, inspection and dated evidence

No unresolved material finding. Re-reviewed the current Chapter 68 body on 2026-10-04 after the permission repair. Fixture creation now explicitly applies `chmod 0644 message.txt`, and the new explanation states that COPY preserves source permissions while runtime UID 65532 needs read access. This resolves the inherited-umask reproducibility finding without broadening the private directory or any real secret. In a disposable temporary directory, created the exact fixture under umask 077 and applied the exact chmod: observed mode 0644 with the other-read bit enabled, which allows UID 65532 to read the root-owned copied file under ordinary DAC. This is file-mode evidence, not container runtime acceptance.

The build/working-container versus runtime distinction, compatible account storage, transport prefixes, manifest/index/platform scope, narrow hash checker, immutable input discipline, offline transfer, trust gates, failure diagnosis and cleanup are sound. Installation commands distinguish Ubuntu and Fedora/subscribed RHEL prerequisites. Exercises supply guidance and takeaways.

Primary evidence: [Buildah build](https://github.com/containers/buildah/blob/main/docs/buildah-build.1.md), [Buildah rmi](https://github.com/containers/buildah/blob/main/docs/buildah-rmi.1.md), Skopeo [inspect](https://github.com/containers/skopeo/blob/main/docs/skopeo-inspect.1.md) and [copy](https://github.com/containers/skopeo/blob/main/docs/skopeo-copy.1.md), [containers transports](https://github.com/containers/image/blob/main/docs/containers-transports.5.md), and [Dockerfile COPY reference](https://docs.docker.com/reference/dockerfile/#copy), inspected on 2026-10-03/04. COPY's preservation of source-file permissions establishes the reason for the now-resolved finding. Independently compiled the exact embedded Python here-document without executing it. In a disposable temporary directory, the exact fixture file content created under umask 077 had mode 0600 and no other-read bit; removed the temporary tree. This demonstrates source mode only, not a built-image runtime result.

## Repair validation

Re-ran `python tools/check_book.py --chapters 68-68`: one draft, nine shell syntax blocks and 1,333 global local-link checks; no errors or warnings.

## Scope and validation limits

Read the authoring guide, assigned SKELETON brief and manuscript/summary, and prerequisite/rootless account summaries 61–65; checked the complete five-chapter sequence together and relevant canonical links. Summaries accurately distinguish static checks from unperformed runtime acceptance. `python tools/check_book.py --chapters 66-70` passed five drafts, 30 shell syntax checks, one YAML parse and 1,333 global local-link checks, with no errors or warnings. The embedded Python was separately compiled in this review. Static checking cannot establish runtime semantics or external-link uptime. Successfully retrieved primary sources are listed above; no exhaustive external-link availability audit is claimed.

Podman is installed but ordinary `podman --version` failed before reporting a version because the default runtime state path is read-only in this sandbox. The independent Quadlet binary reports 6.1.2 and can generate text in an isolated dry-run. Buildah and Skopeo are unavailable. No installed account configuration, systemd service, linger setting, container store, image, registry credential, host policy, network listener, engine socket, image build/copy, service boot or restore test was changed/executed. No runtime Ubuntu/Fedora/RHEL matrix was tested. Reviewer edited only separate review records; no manuscripts, summaries or shared metadata were changed.

Verdict: approved
