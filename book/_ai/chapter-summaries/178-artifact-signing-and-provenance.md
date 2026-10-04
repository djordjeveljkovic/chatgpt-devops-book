# Chapter 178 continuation

Status: complete

## Written material
Drafted sections on signatures, attestations, trust roots, Cosign keyless sign/verify commands, provenance verification, deployment admission policy, fail-closed behavior, recovery and a DispatchDesk compromise scenario. Linked Chapters 176 and 177.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Artifact digest, image signature, OIDC issuer and identity, keyless signing, transparency log, attestation predicate/type, subject digest, SLSA provenance, trust root, fail-closed admission policy.

## Examples and cross-references
DispatchDesk release image tampered under mutable `stable` tag; Cosign verification pins a protected GitHub Actions workflow identity and issuer. Provenance is tied to the image subject digest and checked for source, revision, builder and build definition. Chapters 176 (workload identity) and 177 (SBOMs).

## Open threads
Fresh independent review pending after predicate selector, Cosign version and non-interactive CI prerequisites were added. No actual image, signature, attestation, registry, policy controller or deployment was tested.

## Verification
Focused `python3 tools/check_book.py --chapters 178-180` passed 3 draft records, 2 shell syntax checks and 1,482 local links with no errors/warnings before the latest edits; rerun after review fixes. Sources checked 2026-10-04: Sigstore Cosign signing, verification, attestation and CLI references; SLSA provenance v1. No Cosign CLI, OIDC, registry, signature or attestation was executed.
