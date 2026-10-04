# Independent review — Chapter 174

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 7dfdbdf8b56f771ecf9e11947d7acd11d6b52c2b068159842c5ed20e49f6d045

## Scope and findings

Read complete body/summary, assigned brief and guide, with Chapter 173 prerequisite context. Reviewed RBAC APIs/YAML, indirect workload privilege, service-account credentials, Pod Security label strategy, NetworkPolicy/CNI semantics, inspection commands, incident/recovery and assessment. No material technical finding; approved.

The Role/RoleBinding use correct API group, namespaced metadata, Group subject and roleRef. Core pods/services/endpoints read verbs do not include exec/port-forward, Secret access or workload creation. Group mapping must match actual authentication and pod read access can disclose specification metadata. Impersonation permissions are correctly distinguished from a denied target operation; actual group/principal acceptance testing is required. Creation of pods/controllers can indirectly access Secrets/PVCs or stronger service accounts; direct Secret-get denial is not misrepresented as full protection. Namespace-scoped bindings, cluster-wide duties and wildcard/custom-resource expansion remain separate.

Pod Security labels have correct modes/levels/version keys. Baseline enforcement plus restricted audit/warn is correctly described as staging, not restricted enforcement. v1.34 is illustrative and intentionally replaceable, not a current-release claim. Admission Pod fields are distinct from image trust, RBAC and secret authorization. Version revision follows target support/testing. Default-deny policy uses valid networking.k8s.io/v1 with empty podSelector and both policyTypes; omitted allow rules isolate the namespace's selected pods in both directions under a supporting plugin. Additive allowances and required DNS/peer exceptions are accurately stated. It is not promised to supply layer-7 or universal host/control-plane isolation. Plugin enforcement must be observed, not inferred from object creation.

Node pools/namespaces are qualified isolation choices, not hard hostile-tenancy guarantees. Encryption at rest does not deny authorized plaintext reads or replace backup protection. Audit/event retention limits and effective policy editing privileges are visible. Incident reasoning connects broad identity, workload creation, Secret mount and data network access; containment preserves evidence unless immediate harm demands isolation. Credential rotation, trusted workload rebuild, customer reconciliation and possible control-plane trust repair are distinct recovery duties. Exercises/questions/takeaways and linked prerequisites are complete; no live configuration result is invented.

Low optional precision observations:

- RBAC can-i example: --as alone does not reproduce the real reader's identity-provider groups. Add that explicit note or a controlled --as-group example with required group impersonation rights. Current surrounding actual-group/test-account caveat already limits acceptance appropriately.
- NetworkPolicy discussion: briefly mention traffic to/from a pod's own node and hostNetwork/plugin-specific behavior as exceptions to interpreting default-deny as a universal packet firewall. Existing plugin/host-control scope prevents a material universal-isolation claim.
- Pod Security rollout: note namespace-label changes do not evict existing violating Pods; enforcement affects subsequent admitted Pod operations. Existing canary/inventory guidance is sound.

## Primary evidence checked 2026-10-04

- [Kubernetes RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/): least privilege, workload creation escalation and token/policy boundaries.
- [Namespace Pod Security enforcement](https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/) and [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/): label modes/version pinning and checks by admission scope.
- [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/): plugin requirement, additive directional isolation, allow-rule and enforcement limitations.

## Validation and limits

`python3 tools/check_book.py --chapters 174-174` passed three YAML checks, two shell syntax checks and 1,473 global local links without warnings/errors. Exact stripped-front-matter body hash calculated using `tools.promote_reviewed.body_hash`. YAML and API/flag semantics inspected statically; no server-side admission/schema/authorization or cluster operation executed. No actual identity-provider group mapping, Pod Security transition, CNI allowed/denied connection, audit backend, etcd encryption, secret rotation or incident recovery tested. No Kubernetes/CNI/node OS/version matrix tested. Current references do not prove effective deployed policy or incident scope. Only this review record written.

## Bounded correction refresh — 2026-10-04

Impersonated-user versus actual provider groups and NetworkPolicy node/localhost/hostNetwork qualifications are resolved. The Pod Security paragraph and answer guidance introduce an inaccurate dry-run scope: a namespace-label server-side dry run examines existing Pods, not every controller Pod template. Further, update templates and roll out/recreate their Pods rather than instructing operators to recreate the controllers themselves. Medium finding at Pod Security paragraph and exercise answer guidance: distinguish namespace-label dry-run warnings for existing Pods from separate intended-template admission tests, and use rollout/recreated Pods wording. The earlier admission-only/non-eviction correction is otherwise sound.

Current body hash: 3e872e6729560a73158b0ecc3e6063cb3ef856e748c86b39c55fbe333e4be5dd. Focused 174-175 checker passed three YAML/two shell checks and 1,473 links without warnings/errors. Earlier runtime limits remain. Only this review record updated.

## Final bounded correction refresh — 2026-10-04

All earlier precision findings now resolved. Namespace-label dry run is accurately restricted to existing Pods; dormant controller templates receive separate intended-level staging validation. Updated templates are rolled out to replace Pods rather than deleting/recreating controllers. Admission/non-eviction, identity-provider group and NetworkPolicy exception boundaries remain accurate. Summary reflects current content and revising state. No material issue remains.

Fresh body SHA256: 7dfdbdf8b56f771ecf9e11947d7acd11d6b52c2b068159842c5ed20e49f6d045. Focused `python3 tools/check_book.py --chapters 174-175` passed three YAML checks, two shell checks and 1,476 local links without warnings/errors. Earlier full assessment/primary evidence and nonexecution limits remain applicable. Only this review record updated.

Verdict: approved
