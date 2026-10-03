# Chapter 92 continuation

Status: complete

## Written material
Registry token/repository permission/digest boundaries; basic versus enhanced scanning; review-only lifecycle policy; existing image input/new immutable ECR repo/temporary Podman auth/push digest/compare/pinned pull/optional scan/preview/delete; rebuilt-artifact recovery; exercises and answer guidance.

## Concepts and terminology
Local imageID versus registrymanifestdigest/index, immutability/exclusion modes, scanstatus not zerofindings, untagged digest retention, exactartifact promotion.

## Examples and cross-references
Previously approved local single-platform image required, not rebuilt here. UUID fresh repo, returned URI and digest; no invented IDs. Billable registry costs and credential teardown. Local policy, digest and credentials live in a fresh private directory with scoped cleanup. Links 59, 61 and 82.

## Open threads
Fresh independent review required; all AWS, Podman, registry, scan and policy integrations unrun.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Primary ECR/CLI/Podman docs inspected2026-10-01. Validation92-92 passed JSON1/shell4/global links after correcting061 filename. Authfile uses a fresh protected directory with initially absent auth.json. No cloud or container execution performed.
