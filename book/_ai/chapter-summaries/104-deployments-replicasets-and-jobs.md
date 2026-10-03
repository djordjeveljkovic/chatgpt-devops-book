# Chapter 104 continuation

Status: complete

## Written material
Deployment/ReplicaSet ownership; selector/template rules; rollout capacity and terminating-Pod overlap; explicit rollback and cleanup commands; Job completion/retries/idempotency; CronJob scheduling/overlap/missed runs; exercises with answer guidance.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Deployment, ReplicaSet, selector, Pod template, rolling update, maxSurge/maxUnavailable, revision, rollback, Job, completion, parallelism, backoffLimit, CronJob concurrencyPolicy.

## Examples and cross-references
DispatchDesk Deployment excerpt and explicit local namespace/apply, rollout inspection, rollback and cleanup commands; direct links to Chapters 103 and 107. Manifest uses placeholder digest; no cluster actions executed.

## Open threads
None known. Cluster capacity, installed client/server versions and application semantics remain environment-specific as described in the chapter.

## Verification
Official Kubernetes controller documentation inspected 2026-10-04. Scoped YAML, shell and link checks passed. No cluster workload or batch process created or changed.
