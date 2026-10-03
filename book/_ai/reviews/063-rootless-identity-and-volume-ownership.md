# Independent review — Chapter 63

Reviewer: review_volume3_021_025 (independent Volume 7 assignment)
Date: 2026-10-04
Reviewed body SHA256: c9fd61b89aa3a0d6e59a931024e815f2772c9fae1d8d0fb5033c986c0d4e5fb1

## Scope and findings

Read AI_AUTHORING_GUIDE.md, chapter brief, manuscript and compact summary, and prerequisite/canonical context in Chapters 60, 47 and preceding assigned chapters. Reviewed exact examples, version claims, distro boundaries, rootless identity/storage, safety, recovery evidence, prose, local links and required exercises/guidance/takeaways. Quadlet configuration is deferred to Chapter 66 and is outside this five-chapter review.

Checked subordinate-range arithmetic (UID 1000→200999, UID 42→200041), UID/GID independence, default unshare map versus effective container map, keep-id process identity, fixed uid/gid override, mode-700 denied fixture caveat, :Z labeling distinct from ownership, :U real recursive mutation, rootful-only idmap qualification, mapped backup recovery and bounded cleanup. Guidance is correct and all commands have an explicit execution account and data scope. No material findings.

- Low, “Keep-id, unshare and file ownership”, first shell block: consider guarding mkdir failure explicitly (or split the create step from run). The prose already tells readers to stop on an existing data directory, but pasting the whole block otherwise continues after mkdir fails.

## Primary-source evidence

Official upstream stable documentation inspected during this review (2026-10-03–04):

- [podman-run.1.html#userns-mode](https://docs.podman.io/en/stable/markdown/podman-run.1.html#userns-mode).
- [podman-unshare.1.html](https://docs.podman.io/en/stable/markdown/podman-unshare.1.html).
- [podman-system-migrate.1.html](https://docs.podman.io/en/stable/markdown/podman-system-migrate.1.html).

## Verification and limits

`python3 tools/check_book.py --chapters 61-65` passed: 23 shell syntax checks, 1 YAML parse and 1,333 global local links; no errors or warnings. These establish syntax/local linkage, not Podman runtime, Kubernetes API validation or registry image content.

Attempted local `podman --version` and `podman --remote=false info`: both failed during configuration initialization with `mkdir /run/user/1001/libpod: read-only file system`. No engine version or working namespace/runtime can be inferred from that attempt. The authoring baseline reports 6.1.2; this review independently verified stable documented semantics, not execution on that version. No image pull, container/pod creation, ownership/relabel mutation, network allocation, kube playback, runtime HTTP exchange, systemd activation, package install or live restore performed. Ubuntu 24.04/Fedora 44/RHEL 9/10 VM matrix remains untested.

Summaries accurately retain draft status and unperformed runtime checks; they do not claim executed deployments. Optional low findings do not block approval.

Verdict: approved
