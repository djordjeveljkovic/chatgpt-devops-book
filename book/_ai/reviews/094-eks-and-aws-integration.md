# Independent re-review — Chapter 94

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 320a33806693d6cf116aaf08167424e3c45afedfdfd39e6c345e6390f636492e

## Scope and findings

Freshly read the corrected operational sections and current body against both prior low findings, checking surrounding examples for regressions. Endpoint-selection guidance is resolved: the local kubeconfig block is separate from resource reads, with an explicit stop condition on endpoint mismatch between them. The detailed diagnosis now correctly separates unassigned/Unschedulable placement from assigned-node sandbox/CNI startup and ImagePullBackOff, with phase-specific recovery evidence.

Final wording rechecked on2026-10-04: the networking overview now says “fail to bring Pods into useful service”, resolving the remaining optional terminology finding. No material or remaining optional finding. This additional review covers only that final wording correction; the prior scoped validation and source limits below remain applicable.

## Dated primary-source evidence

Inspected on2026-10-04:

- [EKS security](https://docs.aws.amazon.com/eks/latest/userguide/security.html): managed-control-plane/shared-responsibility boundary.
- [Access integrations](https://docs.aws.amazon.com/eks/latest/userguide/grant-k8s-access.html), [legacy aws-auth](https://docs.aws.amazon.com/eks/latest/userguide/auth-configmap.html): IAM authentication, distinct Kubernetes permissions, authentication modes and deprecation.
- [Workload identity comparison](https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html): IRSA versus EKS-only Pod Identity and qualified AWS recommendation.
- [VPC requirements](https://docs.aws.amazon.com/eks/latest/userguide/network-reqs.html), [VPC CNI](https://docs.aws.amazon.com/eks/latest/best-practices/vpc-cni.html): multi-AZ subnets, address capacity and Pod address assignment.
- [EBS CSI](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html): supported compute boundaries, including inability to mount EBS to Fargate Pods.
- [describe-cluster](https://docs.aws.amazon.com/cli/latest/reference/eks/describe-cluster.html), [list-access-entries](https://docs.aws.amazon.com/cli/latest/reference/eks/list-access-entries.html): read-only operation inputs/response fields and access-entry inventory.
- [kubectl auth can-i](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_auth/kubectl_auth_can-i/): permission-check semantics for specified verb/resource.

## Validation and limits

`python3 tools/check_book.py --chapters 94-94` passed:3 shell syntax blocks and1,341 global local links; no errors/warnings. Source evidence above is retained from the original review; no new service-specific assertion required another source lookup. No AWS identity/API call, kubeconfig inspection/update, Kubernetes object read/write, auth check, node/CNI change, storage operation or workload probe executed. No OS/cluster-version matrix or recovery test performed. Syntax/source review cannot establish actual context, permissions, allocation, readiness or durability. Only this review record changed; chapter and summary were not edited.

Verdict: approved
