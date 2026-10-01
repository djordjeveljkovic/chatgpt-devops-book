---
book: The Complete DevOps Engineering Book
volume: 22
volume_title: "Operational Reference"
chapter: 219
title: "Compatibility Matrix and Glossary"
slug: compatibility-matrix-and-glossary
status: complete
summary: ../../_ai/chapter-summaries/219-compatibility-matrix-and-glossary.md
---

# Chapter 219 — Compatibility Matrix and Glossary

Compatibility is a relationship between components and a particular workload. A command parsing successfully on a laptop does not establish that a provider, cluster, service manager and application will behave correctly together. Use this chapter to describe your actual environment and translate terminology; use the canonical chapter for the mechanism or installation procedure.

The book's writing baseline is2026-10-01. Ubuntu24.04LTS, Fedora Server44 and RHEL9 provide its main distribution examples, with Ubuntu26.04 and RHEL10 differences identified where relevant. These are teaching baselines, not a promise that every future reader will have the same packages or support entitlement. Check [Canonical's lifecycle table](https://ubuntu.com/about/release-cycle), [Fedora's official Server download](https://fedoraproject.org/server/download/) and [Red Hat's lifecycle policy](https://access.redhat.com/support/policy/updates/errata) before selecting a new production host. RHEL major, minor and Application Stream support are separate questions.

## Distribution and execution matrix

| Area | Ubuntu baseline | Fedora/RHEL baseline | Portable question |
|---|---|---|---|
| OS identity | Inspect `/etc/os-release`; record24.04 versus26.04 | Record Fedora release or exact RHEL major/minor | Which distribution and package repository actually supplied this component? |
| Packages | APT/dpkg workflows | DNF/RPM workflows; RHEL subscription/repository access matters | Is the package maintained by this vendor, upstream or a third party? |
| Service manager | systemd on the selected server installation | systemd on the selected server installation | Does the installed version support the directive, and is this the system or user manager? |
| Mandatory access control | Applicable AppArmor policy/configuration | SELinux policy/configuration on enforcing hosts | Which profile/domain and denial explain this process's access? |
| Firewall | Inspect the active backend and manager; UFW may be used | Inspect firewalld/nftables and installation policy | Which owner manages the rule set, including container-generated rules? |
| Container runtime | Engine from deliberately chosen repository | Engine from deliberately chosen repository | Which engine version, OCI runtime, rootless mode and cgroup delegation are active? |
| SSH administration | OpenSSH behavior plus distribution configuration | OpenSSH behavior plus distribution configuration | Which effective config and authentication path are in use? |
| Cloud image | Provider-built Ubuntu image with its bootstrap defaults | Fedora/RHEL image with provider defaults and possible entitlement requirements | Which login user, architecture, image lineage and bootstrap mechanism apply? |

Do not translate a tutorial by replacing `apt` with `dnf` alone. Package names, repository signing, enabled services and policy labels can differ. A default from one image is not necessarily the default of another vendor's image with the same distribution name. Red Hat's [SELinux introduction](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/getting-started-with-selinux_using-selinux) explains its separate access-control role. Disabling enforcement to make a mount work discards diagnostic evidence about the failing boundary.

Docker publishes a supported Ubuntu installation path with repository/package instructions and firewall considerations. The [Docker Ubuntu installation guide](https://docs.docker.com/engine/install/ubuntu/) should govern that setup; distro packages and Docker's own packages are not an implicit interchangeable set. Equivalent Fedora/RHEL instructions require their own source and support assessment in the Docker volume.

## Component compatibility matrix

| Pair | What must agree | Common mistaken inference |
|---|---|---|
| Container image and node | CPU architecture, executable ABI, required kernel/runtime features and configuration | OCI packaging means any binary runs on every node. |
| Host and rootless runtime | User mappings, cgroup support/delegation, network helper and mount/security behavior | A nonroot engine can enforce every resource option on every host. |
| Docker CLI and daemon | Endpoint, supported API behavior and relevant server features | Updating the client updated the server. |
| Podman local/remote workflow | Client/server behavior and platform-specific available options | A local Linux storage/namespace command works through a remote macOS client. |
| Compose and engine/provider | Exact Compose implementation, supported specification features and networking behavior | Compatible container images imply identical Compose orchestration. |
| Kubernetes components | Official skew policy plus provider/add-on restrictions | All components permit the same version gap. |
| Kubernetes manifest and cluster | Served API versions, installed CRDs/controllers and admission policy | Valid YAML means the cluster understands or permits the resource. |
| IaC engine and provider/backend | CLI version, provider constraints/lock file, state schema, backend options and permissions | Terraform and OpenTofu remain identical forever. |
| Jenkins and Java/plugins | Controller/agent Java requirements and tested plugin combination | Any installed Java lets a current Jenkins package run. |
| Telemetry producer/collector/backend | Protocol, encoding, authentication, supported signals and configuration schema | An OTLP receiver automatically sends data to every desired storage system. |
| Application and data | Schema/message compatibility during mixed-version deployment and rollback | Reverting an image reverts committed database changes. |

The Kubernetes [version skew policy](https://kubernetes.io/releases/version-skew-policy/) distinguishes components: `kubectl` is supported within one minor version of the API server, while kubelet has a different older-version allowance and must not be newer than the API server. Highly available API servers and managed providers can narrow the permissible range. Check the actual target versions and provider upgrade path; a single “Kubernetes version” does not describe the whole cluster.

For S3 state, current [Terraform backend documentation](https://developer.hashicorp.com/terraform/language/backend/s3) documents `use_lockfile` and deprecates DynamoDB locking. Current [OpenTofu backend documentation](https://opentofu.org/docs/language/settings/backends/s3/) separately documents S3 lock files and DynamoDB-to-S3 migration. The availability of an option in current docs does not establish support in an older installed binary. Migrating locking requires coordinating every writer so an old client cannot take a different lock against the same state.

## Maintenance changes that alter old tutorials

| Item | Inspected situation at the writing baseline | Reader action |
|---|---|---|
| Community ingress-nginx | Retirement announced for March2026 | Evaluate a maintained controller/Gateway implementation and an explicit migration path. |
| Promtail | End of life March2,2026 | Use the maintained collector path taught here, including Alloy; verify migrated parsing/labels/checkpoints. |
| Jenkins package setup | Current Linux instructions include Java21 and updated signing instructions | Use current official installation docs and validate plugin/agent requirements. |
| Podman rootless networking | Behavior depends on installed release; contemporary networking differs from older slirp4netns tutorials | Inspect the actual backend/helper rather than copying historic defaults. |
| Terraform S3 lock configuration | DynamoDB path is deprecated in current docs | Verify engine support and migrate locking with coordinated writers and scoped permissions. |

These are specific maintenance facts, not a general claim that older infrastructure fails on the date a project retires. Retirement changes support and remediation options. Sources: [Ingress NGINX statement](https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/), [Promtail-to-Alloy migration](https://grafana.com/docs/alloy/latest/set-up/migrate/from-promtail/), [Jenkins Linux installation](https://www.jenkins.io/doc/book/installing/linux/) and [Podman network reference](https://docs.podman.io/en/latest/markdown/podman-network.1.html). Ingress NGINX's retirement is distinct from Nginx itself or separately maintained vendors' controllers.

## Glossary of boundaries

These concise definitions are navigational aids written for this book. Where a product uses a term differently, prefer its documented contract.

| Term | Meaning and boundary |
|---|---|
| DevOps | Engineering practice connecting development and operation through shared outcomes and feedback; not a synonym for a single tool. |
| SRE | Reliability engineering using explicit objectives and engineering methods to manage operational work and risk. |
| Platform engineering | Building and operating useful shared capabilities for internal users, with product ownership and feedback. |
| Desired state | Declared target configuration; it can be wrong even when a controller faithfully implements it. |
| Reconciliation | Comparing observations with desired state and acting to reduce differences; convergence may be delayed or impossible. |
| Drift | Observed divergence from the managed expectation; distinguish intentional emergency changes from unnoticed changes. |
| Idempotence | Repeating an operation preserves its intended effect under stated assumptions; it does not imply zero side effects in every external system. |
| Immutable artifact | Content-addressed release material that is promoted without being rebuilt or modified. Its configuration and data remain separate. |
| Image | Packaged filesystem and execution metadata; different from a running process or a persistent database. |
| Container | A runtime object and isolated process environment created from an image and configuration. |
| OCI | Specifications for container image/runtime/distribution interoperability; not a universal orchestration standard. |
| Namespace | Linux isolation mechanism, or Kubernetes object scope, depending on context. These are different abstractions. |
| cgroup | Kernel mechanism grouping processes for resource control/accounting; availability and delegation affect enforcement. |
| Rootless | Runtime operated without host-root privileges, commonly using user namespaces; not proof that every workload access is safe. |
| Volume | Persistent or externally managed mounted storage in a container context; lifecycle depends on the implementation. |
| Registry | Service distributing image/artifact content and metadata; authentication does not itself establish artifact trust. |
| Digest | Content hash identifier; distinct from a mutable friendly tag and from signature/provenance verification. |
| Pod | Kubernetes scheduling unit containing related containers; its lifecycle and storage differ from a VM. |
| Deployment | Kubernetes controller for replicated workloads, or a general release operation; qualify the meaning. |
| Service | Kubernetes network abstraction, systemd unit concept, or customer-facing capability; context matters. |
| Ingress/Gateway | Kubernetes traffic-routing API abstractions that need an implementing controller; YAML alone forwards no packets. |
| Readiness | Policy for accepting work in the current state; not identical to process liveness. |
| Liveness | Whether the process satisfies the selected alive criterion; a failed dependency need not justify restarting it. |
| IAM principal | Identity making an authorization request; evaluated with applicable policies and contextual controls. |
| Availability Zone | Provider failure-domain construct within a region; using several still requires a working failover design. |
| Region | Geographic provider service scope with its own features, quotas and failure considerations. |
| CI | Automated integration feedback, usually building/testing changes; successful CI is not proof of production readiness. |
| Continuous delivery | Keeping changes ready for release through a repeatable process, potentially with an explicit release gate. |
| Continuous deployment | Automatically releasing qualifying changes through the defined production process. |
| GitOps | Reconciliation using versioned declarative configuration and a controller workflow; source approval and controller access remain essential. |
| Artifact | Output retained for a defined use; a deployable artifact needs identity, provenance and custody. |
| Cache | Reusable acceleration data whose correctness assumptions and invalidation must be understood. |
| SLI | Measured service indicator with a defined population and observation method. |
| SLO | Target for an SLI over a stated window; request fractions and time-based availability are different definitions. |
| Error budget | Allowed objective shortfall over the defined window, used with a policy for engineering decisions. |
| Cardinality | Number of distinct label combinations/series; per-request metric identifiers can make it unbounded. |
| Trace/span | Correlated operation history and its timed components; sampling means it may not be a complete ledger. |
| Vertical scaling | Increasing resources of an instance, with limits and possible interruption. |
| Horizontal scaling | Increasing instance count, requiring work distribution and shared-state/dependency planning. |
| Saturation | A resource or service approaching a limiting capacity, often visible through queueing/waits rather than utilization alone. |
| Backpressure | Limiting upstream admission or production to keep downstream demand within a workable contract. |
| Retry budget | Bounded extra attempts/time that prevent recovery traffic from overwhelming a dependency. |
| RPO | Maximum acceptable loss expressed relative to recovery point; backup frequency alone does not prove it. |
| RTO | Target time to restore the specified service after an event; includes dependencies and validation. |
| Backup | Recoverable retained data/configuration with an established restoration path; a copied file without verification is weak evidence. |
| Failover | Moving service responsibility to another path or instance; requires fencing and data/traffic correctness where applicable. |
| Rollback | Returning to a previous compatible application/configuration state; data changes may require forward repair instead. |
| Blast radius | Population and resources a fault or change can affect under the actual dependency and permission model. |
| Toil | Repetitive operational work that can be reduced through engineering; automation still needs ownership and maintenance. |

## Keep a compatibility record that can be updated

For each environment retain the actual OS/kernel/architecture, tool client/server versions, repository origins, manifests, provider lock files, controllers/CRDs, service-manager/security modes and application-data versions. Add a checked date and evidence category: documentation inspected, parser accepted, disposable local execution, staging integration or production observation. A missing category is a missing test, not an invitation to invent a successful one.

When an upgrade is proposed, ask which contract changes, who owns each side, which behavior can be rehearsed and what fallback remains compatible with the new data. Summit may delegate parts of patching to managed AWS services but still owns configuration, client compatibility and recovery. Atlas needs add-on/controller tests as well as the Kubernetes upgrade path. Harbor needs host/runtime/security-policy checks even without a cluster.

As a drill, diagnose “valid YAML rejected by the cluster.” Good answers distinguish parsing from a served API, installed CRD, admission decision and authorization. Then diagnose “new image fails only on one host”: compare architecture/runtime/security/mount and configuration evidence before blaming the image. Record the minimum compatibility evidence needed to authorize each repair.

The matrices summarize inspected primary documentation and explicit teaching choices as of2026-10-01. They are not a certified integration matrix. Chapter-specific verification records distinguish tools actually measured or executed from unavailable Docker, AWS, Kubernetes and provider integrations on the writing host.
