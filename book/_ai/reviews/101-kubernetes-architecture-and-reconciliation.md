# Independent review — Chapter 101

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 922f28e4fc369c7bd6c13417beb7a78cdc056b18904449d4d8bc89b930c5666d

## Findings

No unresolved findings. Fresh independent review of the complete corrected current body confirms ReplicaSet count/template behavior and possible persistence of direct Pod image edits, including mixed-image implications and replacement behavior. Exercise 3 now correctly rejects automatic reversion. The scheduling example consistently uses 500m; the image placeholder occupies @sha256 syntax and explicitly requires replacing the full reference with a verified repository/digest.

## Scope and dated primary evidence

Fresh pass read the current corrected body against the prior findings; earlier scope: read the authoring guide, assigned SKELETON brief, complete current Chapter 101 body and summary, Chapter 100 prerequisite summary and relevant Chapters 46/94 summaries. The brief's architecture, node/runtime and desired-state-transition topics are covered. Exercises have answer guidance; recovery discussion distinguishes fixing requests/capacity from deleting owned Pods. The summary accurately records the illustrative/unexecuted scope. Prerequisite manuscripts were not re-reviewed.

Inspected official Kubernetes documentation on 2026-10-04:

- [Cluster architecture](https://kubernetes.io/docs/concepts/architecture/) supports API server, etcd, scheduler, controllers and node-agent responsibilities. API acceptance versus workload readiness and managed-service ownership are explained coherently.
- [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/) explains matching ownership/count and creation from a template, and explicitly says adopted existing Pods are not made to match a changed template. This supports the corrected count/template explanation.
- [Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) documents rollout on a changed Deployment Pod template and selector/template-label consistency. Parent/source-of-truth updates are the correct durable procedure; a child edit is not itself a parent rollout trigger.
- [Pods](https://kubernetes.io/docs/concepts/workloads/pods/) describes update constraints and replacement, rather than a universal child-field reversion loop.
- [kubectl get](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_get/) documents the resource/name, namespace, label selector, wide output and JSONPath sort options used here.
- [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/) supports describe/event investigation and insufficient schedulable resource diagnosis.

Exact kubectl commands are read-only. current-context reads local configuration; cluster-info and resource/event reads require configured credentials, connectivity and appropriate permissions. The authorized-workstation context is stated and the Pending Pod placeholder is explained. Existing labels must actually match the deployment for the listed selectors to show intended objects. Nodes are cluster-scoped; the production namespace is explicit for workload/events. No host package, unit, AppArmor or SELinux changes occur, so prepared Ubuntu and Fedora/RHEL clients use the same commands. CNI/Service-routing/CSI distinctions, CRI versus OCI link, scheduling versus startup, finite event history and control-plane interruption qualifications are sound. This is not an exhaustive audit of external links or version-specific networking implementations.

## Validation and limits

`python tools/check_book.py --chapters 101-102` passed on 2026-10-04: two draft chapters, one YAML parsing check, six shell syntax blocks and 1,351 global local-link checks; no errors or warnings. YAML parsing is not Kubernetes schema/admission validation. No kubectl command contacted a cluster, no object was applied/scaled/patched/deleted, and no node, runtime, etcd, API server, scheduler, controller, CNI/CSI component or application recovery was exercised. No installed client/server version, RBAC grant, timing, capacity, availability or live distro matrix was verified. Primary documentation establishes documented mechanisms, not runtime evidence. Only this separate body-hash-bound review record was written; chapter, summary and shared state were unchanged.

Verdict: approved
