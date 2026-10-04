# Independent review — Chapter 115

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 81955c2913290f7f156d01f495a5aa43f6bcda9378de751efb45e2c781138e92

## Findings

No material findings. Fresh review confirms the ConfigMap authorization check now explicitly selects production namespace, independently of the impersonated ServiceAccount name. Pod-level automount precedence is also explicitly stated, resolving the optional note.

## Scope and dated primary evidence

Read complete current body, summary, brief, authoring guide and relevant prerequisites. Coverage includes role/subject/binding scope, projected and external identities, credential reduction, diagnosis and answer guidance. YAML Role/ServiceAccount/RoleBinding is internally consistent and illustrative, with no apply instruction; named ConfigMap get is correctly restricted, and lack of automatically mounted credentials is disclosed. ResourceNames list/watch caveat, workload-creation escalation, Secret reads, namespace weakness, impersonation, hostPath and kubelet-proxy risks are sound. Other get/describe and Secret authorization commands have correct scope and avoid dumping values. Authorization checks do not persist resource changes but invoke review APIs, so “read-only” denotes no workload/configuration mutation. Authentication/network access is correctly distinguished from authorization success. No fixed provider federation configuration or distro installation command is supplied.

Official primary sources inspected 2026-10-04: [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) supports namespace/cluster bindings, named resource rules and escalation restrictions; [RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/) supports workload/Secret, nodes/proxy and hostPath escalation; [kubectl auth can-i](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/) explicitly distinguishes impersonated account namespace from request namespace in examples and supports the corrected namespace targeting; [ServiceAccount configuration](https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/) documents Pod automount precedence and projected tokens; [projected volumes](https://kubernetes.io/docs/concepts/storage/projected-volumes/) supports audience/expiry/rotation and subPath non-update caveat. Summary agrees with actual evidence limits. API-token federation remains intentionally provider-specific and requires target issuer/audience/trust validation rather than implying tokens automatically grant cloud access.

## Validation and limits

`python tools/check_book.py --chapters 115-116` passed on 2026-10-04: two draft chapters, two shell syntax blocks, one YAML parsing block and 1,382 global local-link checks; no errors/warnings. Hash computed with tools.promote_reviewed.body_hash. Static checks establish syntax/parsing and local links only. No cluster/API query, manifest application, storage operation, token generation, impersonation, identity-provider exchange or provider action occurred. No selected driver/controller/backend, OS matrix, real authorization, data recovery, performance or external federation was tested. Primary sources were inspected selectively rather than exhaustive external-link or deployment validation. Only separate review records were written.

Verdict: approved
