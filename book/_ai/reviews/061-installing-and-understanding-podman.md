# Independent review — Chapter 61

Reviewer: review_volume3_021_025 (independent Volume 7 assignment)
Date: 2026-10-04
Reviewed body SHA256: 401c3773c44ff4b3a8def38bf69e52ca5d0b117f2551c4d10b4ac6d7e9d91416

## Scope and findings

Read AI_AUTHORING_GUIDE.md, chapter brief, manuscript and compact summary, and prerequisite/canonical context in Chapters 60, 47 and preceding assigned chapters. Reviewed exact examples, version claims, distro boundaries, rootless identity/storage, safety, recovery evidence, prose, local links and required exercises/guidance/takeaways. Quadlet configuration is deferred to Chapter 66 and is outside this five-chapter review.

Checked separate Ubuntu/Fedora/RHEL installation procedures and entitlement, rootless/rootful stores, --remote=false override, API socket authority, machine versus host paths, executable versus engine acceptance and vendor rollback/data compatibility. Failure scenarios preserve identity before recreation. Assessment guidance and takeaways are complete. No material findings.

## Primary-source evidence

Official upstream stable documentation inspected during this review (2026-10-03–04):

- [installation](https://podman.io/docs/installation).
- [podman.1.html](https://docs.podman.io/en/stable/markdown/podman.1.html).
- [podman-info.1.html](https://docs.podman.io/en/stable/markdown/podman-info.1.html).
- [podman-system-service.1.html](https://docs.podman.io/en/stable/markdown/podman-system-service.1.html).

## Verification and limits

`python3 tools/check_book.py --chapters 61-65` passed: 23 shell syntax checks, 1 YAML parse and 1,333 global local links; no errors or warnings. These establish syntax/local linkage, not Podman runtime, Kubernetes API validation or registry image content.

Attempted local `podman --version` and `podman --remote=false info`: both failed during configuration initialization with `mkdir /run/user/1001/libpod: read-only file system`. No engine version or working namespace/runtime can be inferred from that attempt. The authoring baseline reports 6.1.2; this review independently verified stable documented semantics, not execution on that version. No image pull, container/pod creation, ownership/relabel mutation, network allocation, kube playback, runtime HTTP exchange, systemd activation, package install or live restore performed. Ubuntu 24.04/Fedora 44/RHEL 9/10 VM matrix remains untested.

Summaries accurately retain draft status and unperformed runtime checks; they do not claim executed deployments. Optional low findings do not block approval.

Verdict: approved
