# Chapter 94 continuation

Status: complete

## Written material
Managed control plane and compute ownership; ECS/EKS tradeoffs; IAM-to-Kubernetes access entries/RBAC; workload identity with Pod Identity and IRSA; VPC CNI addressing; EBS/EFS storage limits; read-only cluster responsibility map; Pending Pod, access-denied and Ready-but-failing diagnosis; exercises and answer guidance.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
EKS managed control plane, node group/Fargate profile, access entry, authentication mode, Kubernetes RBAC, Pod Identity, IRSA, VPC CNI, CSI, subnet IP capacity.

## Examples and cross-references
Read-only AWS/`kubectl` inventory of an existing cluster; verifies account and current API endpoint/context. No resource changes. Links chapters 41, 82, 93 and 107.

## Open threads
Fresh independent review required after clarifying endpoint verification order and scheduling versus post-scheduling startup failures. No AWS identity/API call, kubeconfig update, Kubernetes object read/write, node/CNI/volume change or cluster operation executed. Effective RBAC, networking, storage recovery and application behavior remain cluster-specific.

## Verification
AWS EKS security, networking, VPC CNI, access-entry, Pod Identity and EBS CSI primary documentation inspected 2026-10-04. Scoped checker passed 3 shell blocks and 1,341 local links with no errors or warnings. Syntax and links do not prove cluster access or runtime behavior.
