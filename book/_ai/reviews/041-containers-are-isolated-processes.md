# Independent re-review — Chapter 41

Reviewer: review_volume3_021_025 (independent Volume5 correction review)
Date: 2026-10-04
Reviewed body SHA256: 60c891548bb571ff08ebdb6e405c7546196dd19d4a16d80c7bd4028b288ee137

## Current scope and findings

Re-read the complete current manuscript body against the recorded findings. All four exercises now have correct guidance, including shared-kernel failures, independent durable authority, combined controls and isolated shutdown/order-intent reconciliation. Published pending-review text is removed. No unresolved material findings or new material issue found. This fresh approval covers only the body hash above.

## Fresh validation and limits

`python3 tools/check_book.py --chapters 41-45` passed on 2026-10-04: five drafts, 6 shell syntax blocks and 1,336 global local links; no errors or warnings. No runtime, resource-pressure/OOM, image-build/promotion, storage migration, distro VM matrix or live recovery executed in this correction review. No new external-source inspection; the primary-source evidence from the initial review below remains applicable. Only these five review records changed.

## Initial primary-source and execution evidence retained

Inspected on 2026-10-04:

- [config-linux.md](https://raw.githubusercontent.com/opencontainers/runtime-spec/main/config-linux.md).

OCI specification landing pages exposed only navigation in the browser extraction, so the corresponding official upstream GitHub specification text was read where relevant. Docker documentation confirms Engine29.0+ fresh-install containerd-store default and upgraded-install legacy behavior. Kernel cgroup documentation explicitly states oom_kill counts member processes killed by any OOM killer.

## Verification and limits

`python3 tools/check_book.py --chapters 41-45` passed: five drafts, 6 shell syntax blocks and 1,333 global local links; no errors or warnings. Executed the exact shell-context snippet: PID2, readable PID/mount/network namespace handles and one 0:: cgroup membership line. This is evidence for the reviewer shell context only, not host initial-namespace or a launched container.

No Ubuntu/Fedora/RHEL VM matrix, container-runtime launch, isolation escape/security test, cgroup load/OOM experiment, production recovery or external service change performed. Linux fundamentals are not claimed to have been validated on every kernel/runtime. Summaries honestly report draft status and nonexecution; their continuation state should be refreshed by the author/coordinator after findings are resolved. Only separate review records were edited.

Verdict: approved
