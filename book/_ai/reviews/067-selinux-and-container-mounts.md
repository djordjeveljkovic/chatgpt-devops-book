# Independent review — Chapter 67

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: a9b0282077a98c4913cd32ba85c201e709063edd2d0b2a5115e3012f0b2e6d78

## Findings, inspection and dated evidence

No unresolved material finding. Reviewed private versus shared categories, pod security-label boundary, DAC/mapping versus mandatory policy, dedicated-path relabel safety, enforcing-host prerequisite, AVC time/path/context correlation, no blanket audit2allow or privileged repair, restore label behavior, AppArmor distinction and cleanup. The rootless container-root lab correctly matches the account-owned source's ordinary identity while leaving SELinux as a separate question. An unrelabeled home source is described as a possible denial, not a guaranteed result. Explicit Ubuntu versus Fedora/RHEL target paths and honest policy-specific limits are present. Exercises have guidance and the recovery explains competing private relabeling.

Primary evidence: [Podman run labeling manual](https://docs.podman.io/en/stable/markdown/podman-run.1.html), [container-selinux policy manual](https://github.com/containers/container-selinux/blob/main/container_selinux.8), [RHEL 9 SELinux troubleshooting](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/troubleshooting-problems-related-to-selinux_using-selinux) and [Ubuntu AppArmor guide](https://ubuntu.com/server/docs/how-to/security/apparmor/), inspected on 2026-10-03/04. These support Z/z semantics, label changes persisting after object removal and distinct mandatory-security models. No enforcement-mode, label, profile, host directory or container mount mutation was performed.

## Scope and validation limits

Read the authoring guide, assigned SKELETON brief and manuscript/summary, and prerequisite/rootless account summaries 61–65; checked the complete five-chapter sequence together and relevant canonical links. Summaries accurately distinguish static checks from unperformed runtime acceptance. `python tools/check_book.py --chapters 66-70` passed five drafts, 30 shell syntax checks, one YAML parse and 1,333 global local-link checks, with no errors or warnings. The embedded Python was separately compiled in this review. Static checking cannot establish runtime semantics or external-link uptime. Successfully retrieved primary sources are listed above; no exhaustive external-link availability audit is claimed.

Podman is installed but ordinary `podman --version` failed before reporting a version because the default runtime state path is read-only in this sandbox. The independent Quadlet binary reports 6.1.2 and can generate text in an isolated dry-run. Buildah and Skopeo are unavailable. No installed account configuration, systemd service, linger setting, container store, image, registry credential, host policy, network listener, engine socket, image build/copy, service boot or restore test was changed/executed. No runtime Ubuntu/Fedora/RHEL matrix was tested. Reviewer edited only separate review records; no manuscripts, summaries or shared metadata were changed.

Verdict: approved
