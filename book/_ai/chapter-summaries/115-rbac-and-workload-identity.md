# Chapter 115 continuation

Status: complete

## Written material
Authentication versus authorization; RBAC scope and privilege-escalation risks; least-privilege example manifest; human, ServiceAccount and federated workload identity; short-lived projected tokens; read-only effective-access checks; DispatchDesk incident and exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
ServiceAccount, Role, ClusterRole, RoleBinding, ClusterRoleBinding, projected token, audience, federation, impersonation, least privilege.

## Examples and cross-references
DispatchDesk report processor permissions and cloud object-storage identity; read-only `kubectl` inspection and authorization queries; links to Chapters 112 and 119.

## Open threads
Check exact identity-provider federation behavior against provider documentation during review; no live identity or API test performed.

## Verification
Scoped checker and local-link validation pending; official Kubernetes security and identity docs inspected 2026-10-04.
