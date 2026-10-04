---
book: The Complete DevOps Engineering Book
volume: 12
volume_title: "Kubernetes Production Engineering"
chapter: 111
title: "Cluster Provisioning and Ownership"
slug: cluster-provisioning-and-ownership
status: complete
summary: ../../_ai/chapter-summaries/111-cluster-provisioning-and-ownership.md
---

# Chapter 111 — Cluster Provisioning and Ownership

## Managed and self-managed responsibilities

A Kubernetes cluster is a long-lived production platform with an API, control plane, worker capacity, network and storage integrations, identities, add-ons, upgrade path and recovery plan. Choosing a service or installer does not make those responsibilities disappear. It changes who performs each task and which controls remain available to the workload team. Before creating a cluster, identify the service owner, the operational team and the evidence each team needs to accept its part of the system.

A managed control plane reduces work such as operating API server instances and the control-plane datastore. In Amazon EKS standard mode, AWS operates the Kubernetes control plane, while customers still configure access, network integration, worker capacity, workloads and their security. EKS Auto Mode shifts additional node and infrastructure tasks to AWS. Azure AKS also operates the control plane, while customers still configure and schedule many cluster, node and workload tasks. The precise boundary depends on the selected provider mode, node type, optional integrations and current service policy. Treat a provider's current responsibility documentation and service contract as part of the design; do not generalize one product's boundary to every Kubernetes service. See [EKS security responsibilities](https://docs.aws.amazon.com/eks/latest/userguide/security.html), [EKS deployment options](https://docs.aws.amazon.com/eks/latest/userguide/eks-deployment-options.html), and [AKS shared responsibility](https://learn.microsoft.com/en-us/azure/aks/support-policies).

Self-managed Kubernetes, whether on company-owned hardware or virtual machines, assigns more direct duties to the platform team. Someone must provision and patch operating systems, run the API server and controllers, protect and back up etcd, handle control-plane certificates, maintain the container runtime and CNI, observe capacity and recover failed control-plane members. A one-machine control plane is not highly available. High availability requires a topology designed for failure domains, redundant control-plane components and datastore quorum, along with a working API endpoint, network paths and tested recovery. A managed service hides some implementation work but still leaves customer work such as access governance, node maintenance, add-on configuration, cluster upgrades, workload data recovery and incident coordination.

Use a responsibility matrix before approving a production cluster. A common starting point is:

| Area | Managed control plane | Self-managed control plane | Evidence and owner |
|---|---|---|---|
| API server and control-plane datastore | Provider operates core service; customer configures access and integrations | Platform team patches, monitors, backs up and restores components | Service contract or runbook; named platform owner |
| Worker nodes and OS | Depends on managed node mode; customer may still select images and schedule updates | Platform team patches OS, kubelet and runtime | Node image policy, maintenance schedule, drain/recovery procedure |
| Network, DNS and storage | Provider may offer integrations; customer selects/configures and validates workload paths | Platform team installs and operates CNI, DNS and storage integrations | Tested service paths, CIDRs, plugin owner, storage restore evidence |
| Identity and authorization | Provider exposes identity integration; customer assigns cloud/Kubernetes roles | Platform team operates identity integration and RBAC | Break-glass test, least-privilege review, audit trail |
| Version upgrades and add-ons | Provider supports versions and mechanisms; customer schedules and sequences work | Platform team plans and executes the full control-plane/node/add-on sequence | Supported-version calendar, canary evidence, rollback/recovery plan |
| Applications and data | Customer responsibility in either model | Customer responsibility in either model | SLOs, backup tests, incident ownership and recovery objectives |

This table is a prompt, not a provider contract. For example, an EKS standard cluster and EKS Auto Mode have different infrastructure boundaries; AKS node OS patching can require customer scheduling even though the control plane is managed. A provider can operate a control plane while a customer owns the cluster's security groups, identities, add-on policy and application data. Record who pages whom when API access fails, a node image is vulnerable, storage cannot attach, or an upgrade stalls. A task without a named owner is a future incident.

## kubeadm, bootstrap and maintenance

`kubeadm` is a tool for bootstrapping and upgrading Kubernetes clusters; it is not a complete production platform, cloud integration or operations team. It helps establish control-plane and node configuration, but operators still provide hosts, load balancing, a container runtime, CNI, DNS and any storage/cloud integrations. The Kubernetes project documents both stacked-etcd and external-etcd high-availability topologies. Stacked etcd is simpler but couples datastore members to control-plane hosts; external etcd adds infrastructure and a separate quorum to operate. Select a topology from failure and recovery requirements, then test the loss of a host and datastore member before declaring it highly available. The upstream [kubeadm HA guide](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/) explicitly does not cover cloud-provider setup; use the provider's own instructions for cloud load balancers, storage and control-plane integrations. The official [production environment guide](https://kubernetes.io/docs/setup/production-environment/) provides broader context.

Bootstrap is a dependency sequence, not a single command. The team first prepares supported hosts, routes and firewall rules; installs a compatible container runtime and versioned Kubernetes tools; initializes control-plane configuration and certificates; brings up the chosen CNI; validates cluster DNS and node readiness; then joins additional control-plane and worker nodes. The [kubectl object and diagnostic workflow in Chapter 110](../11-kubernetes-foundations/110-kubectl-diagnostics-and-api-objects.md) helps verify API objects, but a successful `kubectl get nodes` is not proof that production workloads can resolve services, attach storage, authenticate, reach the API or survive a zone failure. Network plugins, cloud controllers and storage provisioners have their own version matrix and operational instructions.

Installation and service management differ across Linux distributions. Package repository configuration, package manager commands, system paths and security controls are not interchangeable between Ubuntu and Fedora/RHEL. Follow the supported installation instructions for the exact distribution and Kubernetes release, and keep the package versions aligned with the cluster's version-skew policy. Avoid mixing upstream instructions with an enterprise distribution's lifecycle or support contract without checking both. This chapter focuses on ownership and sequence; the Linux-specific package procedures belong in the platform build and should be tested for every supported Ubuntu and Fedora/RHEL target.

Maintenance should be a recurring engineering task. Track each control-plane, kubelet, runtime, CNI, CoreDNS, kube-proxy or provider add-on version against its supported window. Upgrade one supported step at a time where required; test deprecated APIs and admission policies before production; verify version skew; stage a canary; preserve capacity for disruption budgets; then update nodes and add-ons in their supported order. A provider-managed control plane may still require the customer to initiate a version update or replace node groups. With kubeadm, the operator sequences control-plane and worker upgrades, drains nodes, updates binaries and checks health. Follow the selected version's official procedure because exact package names, flags and supported skew change over time. See [kubeadm upgrades](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/) and [EKS version upgrades](https://docs.aws.amazon.com/eks/latest/userguide/update-cluster.html).

Back up the Kubernetes API state and application data according to their distinct recovery needs. An etcd backup is not a database backup for an application running in the cluster. A successful snapshot is not evidence that the team can restore into a clean environment, recover encryption keys or reconnect storage. Define recovery objectives, retention, access to backup copies and a restore exercise. [Chapter 120](../12-kubernetes-production-engineering/120-upgrades-etcd-and-cluster-recovery.md) covers etcd and cluster recovery; [Chapter 186](../19-site-reliability-and-recovery/186-backup-engineering.md) covers workload backup engineering. For managed services, read what the provider backs up and which recovery actions remain the customer's job; do not infer application data protection from control-plane availability.

## A production cluster responsibility checklist

DispatchDesk's platform team proposes a production cluster because several services now require independent deployment windows. The first proposal assumes that selecting a managed Kubernetes service means the provider patches every node, upgrades add-ons, configures private access and restores application databases. The assumption is false. During a tabletop review, the owner matrix shows that the selected mode operates the control plane but leaves customer actions for node updates, network configuration, IAM/RBAC, workload observability, PVC backup and version scheduling. The recovery is to assign an owner and verifiable evidence to every retained duty before the first production workload is admitted.

The checklist should capture decisions rather than copy generic “best practice” values:

1. **Purpose and failure budget:** Which workloads belong here, what can be unavailable during maintenance, and what recovery time and data loss are acceptable? If a workload cannot tolerate cluster maintenance or shares no operational boundary, compare a managed service, VM deployment or separate cluster before committing.
2. **Service boundary:** Record provider and service mode, control-plane scope, node type, supported versions, service limits, maintenance options and tasks the customer initiates. Link to the provider's current service-specific responsibility page.
3. **Identity and API access:** Name cluster administrators and workload owners, specify human and workload authentication, RBAC boundaries, audit logs, private/public API exposure and a tested break-glass path. Avoid a shared administrator kubeconfig as the routine access model.
4. **Network and add-ons:** Document control-plane/node paths, Pod and Service CIDRs, DNS, ingress/gateway implementation, CNI, policy enforcement and egress. Record owner and compatibility source for every add-on; test a workload request across the same path users will take.
5. **Capacity and storage:** Define node pool or worker failure-domain placement, Pod requests, autoscaling boundaries, upgrade surge capacity, storage classes, encryption and volume topology. Identify who tests snapshots and application restore, and how a full or detached volume is handled.
6. **Operations and recovery:** Assign alert routing, on-call, API/node failure playbooks, cluster and data backup schedules, upgrade calendar, node image process, certificate responsibilities, and restore/failover tests. Write down how platform and application teams coordinate during a shared outage.
7. **Exit and change control:** Preserve cluster configuration as reviewed source, record versions and identity dependencies, and define how workloads/data move if the provider or topology no longer fits. Treat control-plane recreation and application migration as separate plans.

Review observable evidence through a client already configured for the intended cluster. The following commands are reads; run them only from an authorized administrative environment. Replace the illustrative `dispatchdesk-prod` context with the locally configured context whose API endpoint and cloud account/project you have verified. Do not publish full object data without review:

```bash
kubectl --context dispatchdesk-prod version
kubectl --context dispatchdesk-prod get nodes -o wide
kubectl --context dispatchdesk-prod cluster-info
```

The explicit context flag pins each API read, but a familiar context name is not proof of account or cluster identity. Before running them, inspect the locally configured context and compare its API endpoint and cloud account/project through the provider console or approved inventory. `kubectl version` shows client and server versions; `get nodes` shows node readiness, version, roles and placement; `cluster-info` reports API and core service endpoints available to that client. These reads do not establish control-plane high availability, backup recovery, security configuration, user traffic health or provider responsibility. For self-managed clusters, inspect the control-plane and etcd topology through the approved runbooks; do not run broad host commands on a production control plane without authorization.

If a production incident exposes a gap, such as every worker group still on an unsupported image while the team believed the provider would update it, first identify the chosen service mode and compare the node-group lifecycle policy with the responsibility matrix. Preserve current workload health and upgrade evidence. Assign the customer-side node-image update, test it in a canary group, drain within Pod disruption constraints, and verify critical workloads and add-ons before retiring the old group. If the control plane itself is unhealthy, escalate through the provider's support boundary or the self-managed control-plane recovery plan; changing application Pods cannot repair an unavailable API. Record the corrected owner and deadline so the same assumption does not recur.

## Exercises and answer guidance

1. A managed provider operates the control plane. Who owns application database restore? The application/service owner unless the specific managed data service contract says otherwise; control-plane backup is not workload data backup.
2. A team has three kubeadm control-plane VMs in one rack and calls the cluster highly available. What should be challenged? Failure-domain diversity, etcd quorum, API endpoint, network, power and restore procedures; three hosts in one shared failure domain do not provide the intended resilience.
3. `kubectl get nodes` shows every node Ready. Does that prove a new Pod can use storage and reach an external dependency? No. Test scheduling, CNI/DNS, network policy, storage provisioning/attach, identity and the actual application path.
4. A managed service offers a new Kubernetes minor version. Can the platform team assume the provider will update worker nodes at the same time? No. Inspect that service mode's version and node lifecycle contract, schedule the customer-side data-plane/add-on work and verify version skew.
5. The platform team has an etcd backup but has never restored it and has no application database backup. Is recovery proven? No. Test control-plane restoration and workload data restoration separately, including credentials, encryption keys and required infrastructure.

Review questions: which responsibilities change with the cluster operating model, what does `kubeadm` provide and leave to operators, what evidence demonstrates production readiness, and how are cluster recovery and application data recovery distinguished?

## Verification and primary sources

Official Kubernetes production, kubeadm HA and upgrade documentation and current Amazon EKS/AKS responsibility pages were inspected on 2026-10-04. This chapter gives no provisioning commands and creates no infrastructure. The `kubectl` examples are read-only and were not run against a cluster. Service responsibility varies by provider, selected mode and current contract; no provider SLA, cost, version availability or recovery guarantee is inferred. Static checks do not establish cluster resilience, node support, network policy, identity, storage, backup restoration or an operational team's ability to recover.

Primary references: [Kubernetes production environment](https://kubernetes.io/docs/setup/production-environment/), [kubeadm high availability](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/), [kubeadm upgrade](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/), [Amazon EKS security](https://docs.aws.amazon.com/eks/latest/userguide/security.html), [Amazon EKS deployment options](https://docs.aws.amazon.com/eks/latest/userguide/eks-deployment-options.html), and [AKS support policies](https://learn.microsoft.com/en-us/azure/aks/support-policies).
