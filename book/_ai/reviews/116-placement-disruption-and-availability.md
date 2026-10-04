# Independent review — Chapter 116

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 0f9da90aa57f856d8f89d55c42d380b7b930d38bf3377e27783959f69e8da092

## Findings

No material findings. Re-review confirms the scenario now explicitly has one already-unready selected replica, leaving two healthy Pods at minAvailable 2 and zero eviction allowance. ResourceQuota admission rejection is now explicitly distinguished from a persisted Pending Pod's scheduler constraints. The preceding broad quota wording would be clearer if restricted to provider capacity quota, but the immediately following explanation prevents the earlier technical ambiguity.

Low optional — the --force warning can explicitly distinguish unmanaged-Pod handling from --disable-eviction, which bypasses PDB. No supplied drain command performs either action.

## Scope and dated primary evidence

Read full current body, summary, SKELETON brief, authoring guide and relevant approved prerequisites. Placement/affinity/taints, disruption budgets/maintenance and diagnosis cover the assigned structure. Exercises contain answer guidance. The five diagnostic queries are correctly context pinned; workload/PDB/Event queries are production-scoped and Nodes are cluster-scoped. Zone label display syntax is valid. Commands do not drain, delete, apply or modify cluster state, and sensitive output/expired Event limits are disclosed. Hard/soft placement, toleration permission versus attraction, PDB versus rolling update, involuntary disruption, unhealthy eviction choices and resource/topology capacity boundaries are otherwise technically sound. Probe distinctions are conceptual and no numerical timing guarantee appears. No Ubuntu/Fedora/RHEL package or host commands require a distro variant; provider labels/failure domains remain conditional. Summary accurately records no runtime tests.

Official primary sources inspected on 2026-10-04: [Disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/) supports Eviction API budget scope and direct deletion/rolling update exclusions; [PDB configuration](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) supports healthy-count allowance calculation and unhealthyPodEvictionPolicy; [topology spread](https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/) supports scheduling/balance constraints and feasible-domain limits; [ResourceQuota](https://kubernetes.io/docs/concepts/policy/resource-quotas/) distinguishes admission rejection; [kubectl drain](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_drain/) distinguishes --force from --disable-eviction and node maintenance behavior.

## Validation and limits

`python tools/check_book.py --chapters 116-117` passed on 2026-10-04: two draft chapters, two shell syntax blocks and 1,384 global local-link checks; no errors/warnings. Body hash computed using tools.promote_reviewed.body_hash. No live API commands, drain, eviction, workload/controller change, node operation, autoscaler/provider request or traffic test occurred. No actual topology labels, scheduler/plugin version, OS matrix, spare capacity, probe quality, PDB health status, SLO or recovery duration was validated. Documentation/static analysis does not establish live safe maintenance. Only this separate review record was written.

Verdict: approved
