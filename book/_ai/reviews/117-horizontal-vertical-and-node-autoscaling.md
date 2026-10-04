# Independent review — Chapter 117

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 14c9ba0ebad92ad82f1533558443a5fc0c1f041e84ea897fb0ca990f0c4aa3b8

## Findings

No material findings. Fresh re-review confirms namespace ResourceQuota admission failure, persisted Pending Pod scheduler constraints and provider/node-pool provisioning quotas are explicitly separated throughout diagnosis. The DispatchDesk scenario now identifies request concurrency as the HPA demand metric, explaining scaling even below CPU target.

## Scope and dated primary evidence

Read complete body, summary, brief, authoring guide and Chapter 116 prerequisite. Metrics/feedback/boundaries, HPA/VPA/node capacity and unschedulable diagnosis cover the brief; stabilization and oscillation receive conceptual treatment rather than a measured reproduction. Exercises have answer guidance and maintenance/emergency actions include bounded ownership and return paths. Six kubectl queries are valid observational reads with explicit context, production namespace for workload/HPA/Event objects and cluster scope for Nodes. No scaling, add-on installation or billable provisioning command is supplied. Output/runtime assumptions and no-live-test claims are explicit. No Linux host command requires a distro split; add-on/provider differences are qualified.

Official sources inspected 2026-10-04: [HPA](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/) supports autoscaling/v2, metrics APIs/adapters, requests-relative utilization, highest recommendation among multiple metrics, readiness/missing-metric adjustments and scale stabilization. [VPA](https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/) supports add-on components, recommendations/update policy, version-sensitive in-place/recreate modes and resource policy/limit interaction. [Node autoscaling](https://kubernetes.io/docs/concepts/cluster-administration/node-autoscaling/) supports implementation-dependent provisioning/consolidation and scheduling-based capacity demand. [ResourceQuota](https://kubernetes.io/docs/concepts/policy/resource-quotas/) documents admission rejection and workload-controller inability to create additional Pods, supporting the corrected diagnostic distinction. Requests/limits distinctions and feedback conflicts are otherwise correct. The summary matches the body and no implementation timings or tested throughput are fabricated.

## Validation and limits

`python tools/check_book.py --chapters 117-118` passed on 2026-10-04: two draft chapters, two shell syntax blocks and 1,384 global local-link checks; no errors/warnings. Exact body hash computed using tools.promote_reviewed.body_hash. No API queries, scaling, metrics adapter/VPA installation, node/provider operation, admission test, load test or scale-in recovery rehearsal occurred. No installed autoscaler/version, Ubuntu/Fedora/RHEL matrix, metric quality, provider quota/delay, cost, throughput, dependency headroom or live reconciliation was tested. Documentation/static evidence establishes mechanism rather than measured capacity or exhaustive external-link verification. Only this separate review record was written.

Verdict: approved
