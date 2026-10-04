# Chapter 174 continuation

Status: complete

## Written material
API authentication/authorization/admission boundaries; namespace-scoped RBAC and workload-creation risk; Pod Security Admission; NetworkPolicy implementation and additive semantics; cluster threat review and recovery.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Authentication versus authorization versus admission; Role/RoleBinding; indirect Secret access through workload creation; Pod Security Admission; ingress/egress isolation; additive NetworkPolicies; audit evidence limits.

## Examples and cross-references
DispatchDesk observer Role/RoleBinding, Pod Security namespace labels, deny policy, and unauthorized workload/secret-mount incident. Links to Chapters 173 and 175.

## Open threads
No unresolved material findings; bounded precision changes awaiting hash refresh. No live cluster validation performed.

## Verification
Independent review approved the technical content and recorded three precision notes, now addressed. Focused checker passed three YAML checks, two shell checks and 1,473 local links without warnings or errors. Kubernetes primary references checked on 2026-10-04. No live cluster, identity provider, CNI, admission policy, audit backend, etcd, secret rotation or incident response exercised.
