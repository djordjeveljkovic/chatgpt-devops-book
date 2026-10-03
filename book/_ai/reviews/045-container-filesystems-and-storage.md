# Independent re-review — Chapter 45

Reviewer: review_volume3_021_025 (independent Volume5 correction review)
Date: 2026-10-04
Reviewed body SHA256: 81d41449bb59e5c576bb81603c6c6aa312e52ba521ef5572ca381de1adba8b3d

## Current scope and findings

Re-read the complete current manuscript body against the recorded findings. All five exercises now have correct guidance. Optional findings are resolved too: tmpfs swap persistence and secret implications are explicit; host capacity observations must run on the daemon host for remote Docker. Published pending-review text is removed. No unresolved material findings or new material issue found. This fresh approval covers only the body hash above.

## Fresh validation and limits

`python3 tools/check_book.py --chapters 41-45` passed on 2026-10-04: five drafts, 6 shell syntax blocks and 1,336 global local links; no errors or warnings. No runtime, resource-pressure/OOM, image-build/promotion, storage migration, distro VM matrix or live recovery executed in this correction review. No new external-source inspection; the primary-source evidence from the initial review below remains applicable. Only these five review records changed.

## Initial primary-source and execution evidence retained

Inspected on 2026-10-04:

- [overlayfs.html](https://docs.kernel.org/filesystems/overlayfs.html).
- [Official documentation](https://docs.docker.com/engine/storage/containerd/).

OCI specification landing pages exposed only navigation in the browser extraction, so the corresponding official upstream GitHub specification text was read where relevant. Docker documentation confirms Engine29.0+ fresh-install containerd-store default and upgraded-install legacy behavior. Kernel cgroup documentation explicitly states oom_kill counts member processes killed by any OOM killer.

## Verification and limits

`python3 tools/check_book.py --chapters 41-45` passed: five drafts, 6 shell syntax blocks and 1,333 global local links; no errors or warnings. Docker unavailable, so no inspect template run or engine/backend capacity verified. No mount, volume, migration, prune or storage modification performed.

No Ubuntu/Fedora/RHEL VM matrix, container-runtime launch, isolation escape/security test, cgroup load/OOM experiment, production recovery or external service change performed. Linux fundamentals are not claimed to have been validated on every kernel/runtime. Summaries honestly report draft status and nonexecution; their continuation state should be refreshed by the author/coordinator after findings are resolved. Only separate review records were edited.

Verdict: approved
