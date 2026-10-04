# Chapter 138 continuation

Status: complete

## Written material
Applications and destinations; AppProjects; automated sync/self-heal/pruning distinctions; installation and access boundaries; Git promotion path; read-only CLI inspection; failed sync/drift/deletion diagnosis; exercises, answer guidance, review questions and takeaways.

## Concepts and terminology
Application, AppProject, source revision, rendering, destination, sync status, health status, automated sync, self-heal, pruning, repository credentials, Argo CD RBAC.

## Examples and cross-references
Illustrative AppProject allowlist and staging Application with automated sync, self-heal and pruning left disabled; read-only `argocd app get`/`diff`; promotion of digest across environments. Links to Chapters 131, 136, 137, and 140.

## Open threads
Independent review approved the body hash. Argo CD deployment behavior and runtime permissions were not exercised.

## Verification
Body is 2,535 words. Argo CD stable documentation was checked 2026-10-04; implementation and runtime were not exercised. Focused `python3 tools/check_book.py --chapters 137-138` passed with YAML 3, shell 2, and 1,435 local links; no warnings/errors. Static validation does not test cluster behavior or semantics.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.
