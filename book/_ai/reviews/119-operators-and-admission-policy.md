# Independent review — Chapter 119

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 874ffb7a887d2fd183db99ca2462ce27257ae3c13406614b7b8cc53230750adf

## Findings

No material findings. Fresh re-review confirms CRD deletion deletes stored instances and the API endpoint, recreation does not restore them, and operator-only removal can leave unreconciled objects. Export/migration, external cleanup, finalizers and owned-resource impact are explicitly required before either action.

## Scope and dated primary evidence

Read full body, summary, SKELETON brief, authoring guide and Chapter 118 prerequisite. Custom API/controller contracts, admission lifecycle/ownership and operator selection cover the brief. Fictional operator evaluation is clearly illustrative, with staging failure/restore acceptance and constrained admission rollout. Exercises have answers and operational review questions. Six kubectl queries are valid read-only inspections: CRDs, cluster RBAC and admission configuration are cluster scoped; workload/RBAC/Event reads explicitly select production namespace. Every command pins context; unavailable version-sensitive APIs and observational limits are stated. No install/apply/delete, disabling enforcement, removing finalizer or dumping Secret values is instructed as diagnosis. No Linux host commands require distro variants.

Primary official sources inspected 2026-10-04: [Operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/) supports domain-specific controllers without universal backup/recovery guarantees; [CRD task](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/) explicitly documents stored-instance deletion and empty recreation, supporting the corrected distinction; [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/) supports enforce/warn/audit distinctions and Pod versus workload template behavior; [ValidatingAdmissionPolicy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/) supports CEL, policy plus binding, Deny/Warn incompatibility and scoped match behavior; [Dynamic Admission Control](https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/) supports mutation/validation stages, TLS/timeouts and invocation failurePolicy versus intentional denial. Current conceptual claims are otherwise sound, including warning/audit staging, runtime-enforcement limits, controller status limitations and webhook recovery dependencies. Summary accurately states lack of live/operator-specific validation.

## Validation and limits

`python tools/check_book.py --chapters 119-120` passed on 2026-10-04: two draft chapters, two shell syntax blocks and 1,389 global local-link checks; no errors/warnings. Body hash computed using tools.promote_reviewed.body_hash. No cluster/API queries, CRD/operator changes, policy/CEL execution, webhook requests, namespace-label changes, restore or deletion occurred. No selected operator/version, installed API baseline, Ubuntu/Fedora/RHEL matrix, exception scope, actual failurePolicy, reconciliation, stored-version conversion, support contract or recovery was tested. Documentation/static analysis does not establish deployment behavior or exhaustively verify external links. Only this separate review record was written.

Verdict: approved
