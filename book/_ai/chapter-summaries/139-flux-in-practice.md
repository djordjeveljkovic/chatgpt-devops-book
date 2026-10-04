# Chapter 139 continuation

Status: complete

## Written material
Flux Toolkit source and apply controllers; GitRepository and Flux Kustomization; bootstrap and ownership; multi-tenant security and impersonation; source credentials and SOPS boundaries; read-only diagnosis and suspension; prune/garbage collection; exercises, answer guidance, review questions and takeaways.

## Concepts and terminology
source-controller artifact; kustomize-controller; helm-controller; GitRepository; Flux Kustomization vs Kustomize file; dependsOn; health/readiness; service-account impersonation; suspension; pruning.

## Examples and cross-references
Illustrative publicly readable GitRepository (with private-source `secretRef` guidance) and conservative staging Kustomization; `kubectl` status/describe inspection. Links to Chapters 136–138, 140, and OpenGitOps.

## Open threads
Independent review approved the final body hash. Flux install, source fetch, tenant impersonation, and cluster behavior were not exercised.

## Verification
Body is 2,109 words. Flux official docs checked 2026-10-04; Flux components and cluster behavior were not exercised. Focused `python3 tools/check_book.py --chapters 137-139` passed with YAML 4, shell 3, and 1,440 local links; no warnings/errors. Static validation does not test rendering or cluster semantics.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.
