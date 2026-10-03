# Independent review — Chapter 104

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 7741b3cae797dcd2417b6b2039f67d0554179dbfb429bb64253888142a91f950

## Findings

No unresolved findings. Fresh independent re-review confirms rollback now explicitly targets kind-dispatchdesk/production and checks rollout status with a bounded timeout; both maxSurge passages explain terminating-Pod overlap and its capacity implications; lab cleanup deletes only the owned Deployment and conditions namespace deletion on exclusive lab ownership and absence of other resources. Source and execution limits from the prior review remain applicable.

## Inspection and dated primary evidence

Read the full current chapter and summary, SKELETON brief and previously read authoring guide. Chapter 103 prerequisite was independently reviewed immediately before this assignment; context fundamentals from Chapters 101/102 are established. The brief's controller selection, rollout and batch semantics are covered with exercises and appropriate answer guidance. YAML selector/template labels match, digest placeholder is explicit, namespace creation exists and already-existing namespace behavior is explained. The summary accurately states fragment/nonexecution scope; its Chapter 103 cross-link claim refers to a dependency rather than an actual relative body link.

Retrieved official Kubernetes [Deployment documentation](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/) and [CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) on 2026-10-04. Deployment documentation supports rolling strategy, template-triggered revisions, unchanged scaling revisions, rollout history/undo and migration rollback limits; it also documents terminating-Pod overlap beyond nominal surge. Job documentation supports completions/parallelism, Never versus OnFailure, backoff/deadline and duplicate task starts even for a single completion. CronJob documentation supports concurrency-policy scope, Forbid missed runs, Replace behavior, time-zone version applicability, approximate scheduling and required idempotency. No exactly-once or unlimited backlog guarantee is asserted. ReplicaSet ownership/selector details were checked against the official source in the immediately preceding Chapter 101 review. Attempt to retrieve the generated kubectl rollout undo reference returned an internal retrieval error; Deployment documentation provides primary evidence for undo behavior, and context/namespace targeting follows Kubernetes client configuration reviewed in Chapter 102.

The fixed three-replica/maxUnavailable 0/maxSurge 1 policy is valid and can stall when new Pods cannot schedule/become available. No readiness probe is in this teaching fragment; text explicitly requires production probes and the failed-readiness scenario concerns a later configured release. rollout status uses a bounded 120-second observation timeout, not a deployment rollback or readiness guarantee. Read selectors can include multiple components/workloads, which is useful inventory but not proof of ownerReferences. Bash commands use valid context/namespace/name and selector syntax including the corrected explicit rollback target. Ubuntu/Fedora/RHEL prepared kubectl clients use the same API commands; no distro-specific host changes are prescribed. No fabricated measured output appears.

## Validation and limits

`python tools/check_book.py --chapters 104-105` passed on 2026-10-04: two draft chapters, two YAML parsing checks, eight shell syntax blocks, 1,355 global local-link checks; no errors or warnings. Syntax/YAML parsing is not Kubernetes schema/admission validation. No kubectl command contacted a cluster; no namespace, Deployment, ReplicaSet, Pod, Job or CronJob was created/queried/modified/deleted. No rollout/rollback, image pull, scheduler/capacity, retry/duplicate-effect, schedule or application/data recovery behavior was executed. No installed client/server version, real credentials/RBAC or distro matrix was tested. Retrieved sources support documented behavior rather than runtime guarantees and are not an exhaustive external-link audit. Only this review record was written.

Verdict: approved
