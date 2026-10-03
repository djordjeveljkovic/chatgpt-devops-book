---
book: The Complete DevOps Engineering Book
volume: 10
volume_title: "AWS Production Services"
chapter: 94
title: "EKS and AWS Integration"
slug: eks-and-aws-integration
status: complete
summary: ../../_ai/chapter-summaries/094-eks-and-aws-integration.md
---

# Chapter 94 — EKS and AWS Integration

## Managed control plane and worker ownership

Amazon EKS runs a managed Kubernetes control plane for a cluster. AWS operates its control-plane infrastructure, including the API server and etcd, while the customer chooses versions, configures access, connects the cluster to a VPC and operates workloads and integrations. The worker plane still needs compute: managed node groups, Fargate profiles or another supported capacity model each place different operational work with the team. “Managed Kubernetes” does not mean that AWS deploys DispatchDesk, chooses its resource requests, repairs a bad rollout or establishes that an order was durably accepted.

Use Kubernetes when its API, ecosystem, portability or team operating model justifies its wider set of objects and controllers. If a team needs a small number of AWS-native services and does not need the Kubernetes abstraction, ECS may have a smaller operational surface. The comparison is about system ownership, team experience, workload shape, guardrails and cost evidence; neither platform is a universal next step after containers.

The shared-responsibility boundary changes which component the team diagnoses, not whether diagnosis is needed:

| Area | AWS operates or supplies | The team still owns |
|---|---|---|
| Control plane | Managed Kubernetes API and control-plane infrastructure | Version selection, cluster endpoint access, authentication and Kubernetes authorization policy |
| Compute | Managed node-group control operations or Fargate task hosts | Workload requests, placement, capacity choices, node-group configuration and application availability |
| Networking | VPC and EKS integration points | Address capacity, routes, security groups, CNI/add-on configuration, policies and ingress reachability |
| Identity | IAM, EKS authentication integrations and available workload-identity mechanisms | Least-privilege roles, cluster access grants, service accounts and audit of effective permissions |
| Storage | AWS volume/file services and CSI integration options | Storage classes, topology, backup/restore, data lifecycle and application consistency |
| Application | Underlying AWS services | Image identity, Kubernetes manifests, probes, rollout safety, secrets, logs, metrics and incident response |

AWS documents the EKS control-plane portion of this boundary in its [security and shared-responsibility guide](https://docs.aws.amazon.com/eks/latest/userguide/security.html). Control plane health is one input. Node readiness, pod scheduling, CNI state, add-on version and application behavior remain separate evidence.

## Identity, networking and storage integrations

There are two identity questions. First, which AWS principal can call EKS APIs and authenticate to the Kubernetes API? EKS access entries connect an IAM principal to cluster access; Kubernetes RBAC or an associated EKS access policy then determines Kubernetes permissions. An IAM policy that permits `eks:DescribeCluster` does not by itself grant permission to list every Kubernetes Secret. AWS now marks the legacy `aws-auth` ConfigMap method as deprecated, but existing clusters may depend on it. Inspect authentication mode and current mappings before migration: enabling access entries is a cluster configuration change, and `API_AND_CONFIG_MAP` keeps two separate sources whose precedence matters. Avoid solving an access failure with an administrator-wide binding. See [EKS access-entry behavior](https://docs.aws.amazon.com/eks/latest/userguide/grant-k8s-access.html).

Second, what AWS permissions should a workload running in a Pod receive? Do not give every Pod the node's broad IAM role. EKS supports IAM Roles for Service Accounts (IRSA) and EKS Pod Identity, with different prerequisites and portability properties. Pod Identity uses an EKS agent and EKS-managed associations; IRSA relies on the cluster's OIDC identity provider and web-identity role assumption. AWS currently recommends Pod Identity where it fits, but SDK support, cluster model, cross-account access, audit and operational standards can affect the choice. Select one deliberately and keep its role limited to the specific AWS API and resource needed. See the official [workload identity comparison](https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html).

EKS networking is also a layered responsibility. Cluster creation requires subnets across multiple Availability Zones; control-plane communications, Pods, Services and an ingress controller or load-balancer integration then add distinct paths to inspect. In the Amazon VPC CNI model, Pod addresses use VPC networking and consume address capacity from the node subnets. A cluster with enough node CPU can still fail to bring Pods into useful service because an address cannot be allocated, a security rule blocks traffic, or an IP target cannot be registered. [EKS VPC and subnet requirements](https://docs.aws.amazon.com/eks/latest/userguide/network-reqs.html) include address availability and subnet topology; the [VPC CNI guide](https://docs.aws.amazon.com/eks/latest/best-practices/vpc-cni.html) explains Pod address assignment.

Storage has a similar control-plane/data-plane split. The EBS CSI driver can provision block volumes for Pods on supported EC2 node setups, but it cannot mount EBS volumes to Fargate Pods. The team still decides access mode, storage class, snapshot policy, restore test and which availability-zone topology is acceptable. An EBS volume is tied to an Availability Zone; a replacement Pod constrained elsewhere may not attach it. A persistent volume claim protects lifecycle from a Pod restart, but it is not a backup and does not make writes transactionally safe. Shared file storage such as EFS has different throughput, latency, security and consistency trade-offs. Treat stateful data separately from replaceable Pods and test recovery using the database's own process. See [EBS CSI support and limitations](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html).

## An EKS operational responsibility map

This read-only inventory helps answer “which layer owns the failure?” It inspects an existing authorized cluster; it does not create or modify EKS resources. Run with AWS CLI v2, `kubectl`, and a configured identity on an Ubuntu 24.04 LTS, Fedora 44 or RHEL 9 workstation. Complete [Chapter 82's AWS account preflight](../09-aws-foundations/082-aws-cli-and-identity-sessions.md), then record the intended profile, account and region. The Kubernetes context must name the same intended cluster. `kubectl` output can expose workload names and node addresses, so store it under the team's access and retention policy.

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Expected AWS account ID: ' lab_expected_account
read -r -p 'Existing EKS cluster name: ' lab_cluster
lab_actual_account=$(aws --profile "$lab_profile" --region "$lab_region" \
  --no-cli-pager sts get-caller-identity --query Account --output text)
[[ "$lab_actual_account" == "$lab_expected_account" ]] || {
  printf 'Profile resolved to account %s, not expected account %s\n' \
    "$lab_actual_account" "$lab_expected_account" >&2
  exit 1
}
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  eks describe-cluster --name "$lab_cluster" \
  --query 'cluster.{status:status,version:version,endpoint:endpoint,auth:accessConfig.authenticationMode,subnets:resourcesVpcConfig.subnetIds,clusterSecurityGroup:resourcesVpcConfig.clusterSecurityGroupId}'
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  eks list-addons --cluster-name "$lab_cluster"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  eks list-access-entries --cluster-name "$lab_cluster"
```

The three AWS calls describe state and do not update `kubeconfig`. Before using `kubectl`, inspect the current local context and confirm it matches the cluster you intended:

```bash
kubectl config current-context
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'
```

Compare the selected context's API server URL with the `endpoint` returned by `describe-cluster`. If they differ, stop before querying Kubernetes resources; identify the approved context without changing it. After confirming the endpoint and authorization, inspect the cluster:

```bash
kubectl auth can-i get nodes
kubectl get nodes -o wide
kubectl get pods --all-namespaces -o wide
kubectl get events --all-namespaces --sort-by=.metadata.creationTimestamp
```

`kubectl auth can-i` checks the current caller's effective Kubernetes authorization for that verb and resource; it does not grant access or prove permission to read other objects. Cluster API authentication and Kubernetes authorization are separate from AWS IAM permission to describe the cluster. `list-access-entries` applies only when the cluster authentication mode includes the EKS API; a denied or unsupported call is not evidence that the cluster has no mappings. Omit commands that reveal workloads or addresses if the caller is not authorized to view them.

Consider a Deployment whose new Pods have not become useful while existing nodes show CPU and memory headroom. First distinguish scheduler placement from startup. A Pod with no assigned node and an `Unschedulable` event points toward resource requests, taints, affinity, topology or volume binding. A Pod assigned to a node but stuck creating its sandbox can point toward CNI address allocation or networking; `ImagePullBackOff` instead points toward image identity, authorization or route/endpoint access. Use `kubectl describe pod` events and its assigned-node field to determine which phase failed. For a CNI allocation error, inspect node and subnet address capacity, VPC CNI add-on health/configuration and the node role's permitted CNI behavior. Do not edit CNI settings or broaden IAM policies based on a generic Pending phase. The recovery owner may need to add eligible subnet capacity, correct the supported CNI configuration or reduce unnecessary Pod address demand, then verify a newly running Pod and its actual service path.

For an application that can reach AWS but receives `AccessDenied`, check the Pod's service account, identity association/trust, projected credential path, role session and exact denied action/resource. Compare the intended workload role with the node role and confirm which one the AWS SDK actually resolved. A successful `kubectl get pods` proves nothing about the Pod's S3 permission. Rotate or change the intended role through the owner, then verify the single required action without granting administrator access. Preserve audit events and application logs before concluding that a network error is IAM-related.

When a workload reports `Ready` but customers still see errors, inspect the Deployment's revision and rollout status, Pod readiness condition, Service selectors/endpoints and ingress/load-balancer target health. Then run a safe synthetic request and inspect the durable database or queue result. Kubernetes readiness controls traffic according to a probe; it does not certify business correctness. The process/container baseline in [Chapter 41](../05-container-internals-and-oci/041-containers-are-isolated-processes.md) and probe behavior in [Chapter 107](../11-kubernetes-foundations/107-probes-and-graceful-termination.md) own the deeper workload and readiness details.

## Exercises and answer guidance

1. AWS reports the EKS cluster `ACTIVE`, but no API Pods schedule. Inspect nodes, namespace events, resource requests, taints and CNI address availability; cluster status covers the managed control plane, not workload capacity.
2. An engineer can call `DescribeCluster` but receives Kubernetes `Forbidden` for a Deployment. Check EKS authentication mode/access entry and Kubernetes authorization separately from AWS API permissions.
3. A Pod has access to S3 through its node role. Why replace that setup? A workload-specific role narrows credentials and blast radius; verify the selected Pod identity mechanism before detaching node permissions that infrastructure add-ons need.
4. A PVC is bound and an application writes successfully. Is recovery proven? No. Verify snapshots or backups, restore them into an isolated target, and validate database consistency and application recovery.

Review questions: who operates the control plane, which role authenticates a human, which identity reaches AWS from a Pod, what limits Pod network growth, and what proves durable application behavior?

## Verification and primary sources

AWS EKS shared-responsibility, cluster networking, VPC CNI, access-entry and workload identity documentation was inspected on 2026-10-04. The commands are read-only inventory and authorization checks; no AWS identity/API call, kubeconfig update, Kubernetes object read/write, node change, CNI change, volume provisioning or cluster operation was executed during authoring. Syntax and links cannot establish the target account, effective RBAC, cluster readiness, Pod reachability, storage recovery or business correctness.

Primary references: [EKS security and shared responsibility](https://docs.aws.amazon.com/eks/latest/userguide/security.html), [EKS network requirements](https://docs.aws.amazon.com/eks/latest/userguide/network-reqs.html), [VPC CNI guide](https://docs.aws.amazon.com/eks/latest/best-practices/vpc-cni.html), [EKS workload identity comparison](https://docs.aws.amazon.com/eks/latest/userguide/service-accounts.html), [access entries and legacy authentication](https://docs.aws.amazon.com/eks/latest/userguide/grant-k8s-access.html), [EBS CSI support and limitations](https://docs.aws.amazon.com/eks/latest/userguide/ebs-csi.html) and [AWS CLI describe-cluster](https://docs.aws.amazon.com/cli/latest/reference/eks/describe-cluster.html).
