# Chapter 131 continuation

Status: complete

## Written material

Why release engineering closes the gap between tested and deployed bytes; build-once/promote model; release identity record; source, builder, digest, test, provenance, decision and configuration evidence; tag versus digest and multi-platform OCI index distinction; environment-specific gates; provenance limits; protected credentials; artifact testing and cross-registry identity changes; Bash/Skopeo example for digest-preserving multi-platform promotion; diagnosis and recovery for rebuild drift and untrusted provenance; exercises with answer guidance; review questions and takeaways.

## Concepts and terminology

Release candidate, promotion, release identity, registry manifest/index digest, multi-platform image, mutable tag, artifact provenance, policy gate, destination identity, rollback digest.

## Examples and cross-references

DispatchDesk API candidate promoted to a release tag with Skopeo `--all` and `--preserve-digests`; illustrative build-once workflow and rebuild-drift incident. Relative links to Chapters 123, 129 and 130; forward connection to deployment chapters 132–133.

## Open threads

Independent review approved the final body hash; the three optional editorial findings were resolved. No registry, image build, signature verification, CI provider, or deployment was executed.

## Exact next section

None. Independently approved; continue to the next unfinished chapter.

## Verification

Official OCI, SLSA v1.2, Skopeo, GitHub artifact-attestation and Docker policy documentation inspected 2026-10-04. `python3 tools/check_book.py --chapters 131-131` passed with one shell syntax check and 1,403 global local links; `git diff --check` passed. Static checks do not establish command behavior against a live registry.
