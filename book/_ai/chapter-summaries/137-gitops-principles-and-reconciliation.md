# Chapter 137 continuation

Status: complete

## Written material
Why this matters; Git state, controllers and drift; promotion and secret boundaries; separating build from deployment authority; drift investigation procedure; exercises with answer guidance; review questions; takeaways; references.

## Concepts and terminology
OpenGitOps principles; desired and observed state; pull-based agent; reconciliation loop; drift; environment promotion; build/deploy authority boundary; secret reference and external secret source; pruning.

## Examples and cross-references
DispatchDesk image digest promoted to staging then production; illustrative Kubernetes Deployment secret reference; read-only `kubectl` investigation of desired/ready replicas and image. Links to Chapters 131–133, 136, 138–140.

## Open threads
Independent review approved the body hash. No live GitOps controller or cluster behavior was exercised.

## Verification
Chapter body is 2,818 words. `python3 tools/check_book.py --chapters 137-140` passed one YAML and shell example plus 1,443 local links with no warnings/errors. Primary documentation checked 2026-10-04: OpenGitOps Principles/Glossary v1.0.0; Kubernetes Controllers, Secrets, Secret good practices, and RBAC good practices. No cluster/controller was exercised.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.
