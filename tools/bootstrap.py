"""Create the initial book structure; existing chapters are never overwritten."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
# Each chapter has a title and three deliberately distinct teaching sections.
VOLUMES = [
('Engineering Mental Models', '''
What DevOps Engineers Actually Own|Service lifecycle and responsibility|DevOps, operations, platform engineering and SRE|From a ticket to an operating outcome
Requirements Before Tools|Functional and operational requirements|Constraints and measurable acceptance|Writing a service charter
How Computers Execute Services|CPU, memory, storage and networks|Processes, kernels and system calls|Following one request through a machine
Reliability and Risk|Availability, durability and correctness|Failure domains and correlated failure|Choosing an acceptable risk budget
Architecture as Tradeoffs|Quality attributes and competing objectives|Reversibility and decision records|Comparing three viable architectures
Environments and Reproducibility|Development, staging and production|Configuration and artifact identity|Preventing environment drift
Learning to Investigate|Observation, hypotheses and experiments|Evidence quality and uncertainty|A disciplined troubleshooting notebook
Working Safely at the CLI|Execution context and privileges|Read, change, verify and recover|Recognizing destructive and costly commands
Teams, Ownership and Operational Work|Service ownership and handoffs|Toil, collaboration and documentation|A practical operational readiness review
The DispatchDesk Project Begins|A small order and notification product|Workload, budget and reliability assumptions|Three companies with different constraints
'''),
('Linux and Automation', '''
The Shell and Command Execution|Arguments, quoting and expansion|Environment, exit codes and PATH|Tracing a command without leaking secrets
Files, Paths and Filesystem Tools|Paths, inodes and directory entries|Finding and inspecting files|Safe copy, move and deletion workflows
Text Processing and Pipelines|Streams, redirection and pipes|Searching and transforming structured text|Building a useful diagnostic pipeline
Users, Groups and Permissions|Ownership, modes and ACLs|sudo and privilege boundaries|Diagnosing permission denied
Processes, Signals and Jobs|Process trees and descriptors|Signals and exit behavior|Stopping a stuck service gracefully
Systemd and Service Lifecycles|Units, dependencies and restart policy|Journal and unit overrides|Operating a supervised service
Packages and Linux Distributions|apt, dnf and package provenance|Ubuntu and Fedora/RHEL release differences|Installing and upgrading reproducibly
Shell Automation That Survives Failure|Input validation and quoting|Idempotency, traps and temporary files|A restartable maintenance script
Git for Operational Changes|Commits, branches and review|Reverting and resolving conflicts|Managing infrastructure changes as code
Scheduling and Resource Limits|Timers, cron and time zones|File descriptors and process limits|Preventing overlapping scheduled jobs
'''),
('Networking and Traffic', '''
Packets, Addresses and Routing|Interfaces, addresses and subnets|Routing tables and packet paths|Diagnosing an unreachable destination
TCP, UDP and Connections|Handshakes, retransmission and ports|Connection state and timeouts|Using ss and packet capture
DNS from Resolver to Authority|Recursive and authoritative resolution|Caching, TTL and negative responses|Debugging a failed DNS change
HTTP and API Traffic|Methods, status and headers|Persistent connections and proxy boundaries|Following a request with curl
TLS, Certificates and Trust|Certificate chains and names|Issuance, renewal and termination|Diagnosing TLS with openssl
SSH and Remote Administration|Keys, agents and host verification|Bastions, tunnels and connection reuse|A reliable remote maintenance session
Firewalls and Network Policy|Stateful filtering and rule ordering|nftables, ufw and firewalld|Changing access without losing SSH
NAT, Proxies and Connection Tracking|Translation and return paths|Forward and reverse proxies|Finding conntrack and ephemeral-port exhaustion
Load Balancers and Traffic Distribution|Layer four and layer seven routing|Health checks and connection draining|Choosing an algorithm and failure behavior
Network Troubleshooting in Layers|Local, route, name and application evidence|tcpdump, tracepath and mtr|Separating packet loss from application latency
'''),
('VPS and Server Operations', '''
Choosing and Provisioning a VPS|Sizing, regions and provider constraints|Images, SSH access and cloud-init|An auditable first-server build
Host Hardening and Access|Administrative identities and updates|Exposure reduction and recovery access|An Ubuntu and Fedora/RHEL baseline
Disks, Filesystems and Mounts|Block devices, partitions and filesystems|Persistent mounts and growth|Diagnosing full disks and inodes
Deploying a Service with Systemd|Users, working directories and configuration|Release directories and service units|Deploying DispatchDesk without containers
Reverse Proxies on a VPS|Nginx routing and upstreams|TLS, buffering and timeout boundaries|Serving multiple applications safely
Database and Cache Operations on One Host|PostgreSQL and Redis resource competition|Persistence, access and maintenance|Avoiding accidental public exposure
Server Backups and Restore|Files, databases and configuration scope|Retention, encryption and consistency|Restoring into an isolated server
Patching and Maintenance Windows|Package and kernel updates|Drain, restart and smoke checks|Recovering from a bad host update
Adding a Second Server|Shared state and traffic distribution|Configuration consistency and failure domains|Moving from one machine to two
VPS Incidents and Capacity|CPU, memory, disk and network evidence|Provider limits and noisy neighbors|Deciding whether to resize or redesign
'''),
('Container Internals and OCI', '''
Containers Are Isolated Processes|Process isolation versus virtual machines|Host-kernel dependencies and limits|Inspecting a running container from the host
Linux Namespaces|PID, mount, network and user views|Namespace boundaries and inspection|Explaining container-visible resources
Cgroups and Resource Accounting|CPU, memory and I/O controls|Limits, pressure and OOM behavior|Reading resource evidence rather than guesses
Images, Layers and Content Identity|OCI image structure and manifests|Tags, digests and multi-platform images|Tracing an image from registry to runtime
Container Filesystems and Storage|Read-only layers and writable state|Overlay behavior and mounts|Finding unexpected disk growth
OCI Runtimes and Container Engines|Engine, runtime and kernel responsibilities|containerd, CRI-O, runc and crun|Following a container start
Rootless Containers and User Mapping|User namespaces and subordinate IDs|Privileges, networking and storage limitations|Explaining root inside a rootless container
Capabilities and Security Boundaries|Capabilities, seccomp and LSMs|AppArmor, SELinux and device access|Reducing privilege for a real workload
Registries and Image Distribution|Authentication, manifests and blobs|Caching, retention and availability|Diagnosing pull and platform errors
The Container Contract|Signals, logs and configuration|Ephemeral execution and durable state|Designing an application that restarts cleanly
'''),
('Docker in Practice', '''
Installing and Inspecting Docker|Engine installation on both Linux families|Daemon access and privilege|Verifying client, server and context
Running and Managing Containers|run, create, start, stop and remove|Names, ports and restart policy|Operating a small HTTP container
Dockerfiles and Build Contexts|Instructions, context and ignore rules|Layers and reproducible dependency installation|Building a useful application image
BuildKit, Caching and Multi-stage Builds|Cache invalidation and dependency ordering|Build secrets and multi-stage boundaries|Reducing rebuild time and image size
Docker Networking|Bridge, host and user-defined networks|Service naming and published ports|Debugging communication between containers
Docker Volumes and Persistent Data|Volumes, bind mounts and ownership|Backup and database consistency|Surviving container replacement
Docker Compose for Multi-service Applications|Services, networks and configuration|Dependencies and readiness|An API, worker, PostgreSQL and Redis stack
Inspecting and Debugging Docker|logs, exec, inspect, stats and events|Host and container evidence correlation|Diagnosing a crashing application
Publishing and Promoting Images|Registry login, tagging and digest identity|Build once and promote|Releasing a versioned service
Docker Production Operations|Daemon maintenance and log rotation|Health, resource limits and recovery|A production deployment review
'''),
('Podman and the Rootless Host', '''
Installing and Understanding Podman|Installation and version inspection|Local and remote execution|Comparing daemonless operation with Docker
The Podman Container Lifecycle|run, inspect, exec, logs and cleanup|Rootless versus rootful state|Operating an HTTP service
Rootless Identity and Volume Ownership|Subordinate IDs and mappings|keep-id, unshare and file ownership|Repairing persistent-volume access
Podman Networking and Ports|Network backends and rootless forwarding|Name resolution and port reachability|Diagnosing a network mismatch
Podman Pods and Kubernetes YAML|Shared namespaces and pod membership|generate kube and play kube boundaries|Moving a small pod between environments
Quadlet and Systemd Integration|Declarative units and generated services|User services, lingering and startup|Running a durable rootless service
SELinux and Container Mounts|Labels, shared and private relabeling|Diagnosing AVC denials|Fixing mounts without disabling policy
Buildah and Skopeo Workflows|Building OCI images with Buildah|Inspecting and copying images with Skopeo|A registry-independent image workflow
Migrating Docker Workflows to Podman|Compatible commands and behavioral differences|Compose providers and socket compatibility|A measured migration checklist
Podman Host Operations and Incidents|Storage, upgrades and resource pressure|Service recovery and registry failures|Operating a fleet of rootless hosts
'''),
('Infrastructure as Code', '''
Declarative Infrastructure and Reconciliation|Desired state and dependency graphs|Idempotency and ownership|Comparing scripts with declarative tools
Terraform and OpenTofu CLI Foundations|Providers, resources and variables|init, validate, plan and apply|A reviewed infrastructure change
State, Locking and Remote Backends|Resource identity and state sensitivity|Remote state and concurrent changes|Recovering a failed state operation
Modules and Infrastructure Boundaries|Inputs, outputs and composition|Environment and ownership boundaries|Designing a reusable network module
Import, Drift and Safe Refactoring|Discovery and import workflows|Address changes and replacement risk|Adopting existing infrastructure safely
Testing and Policy for Infrastructure|Validation, plans and integration checks|Policy gates and change review|Checking an infrastructure pull request
Ansible Inventory and Playbooks|Inventory, modules and tasks|Privilege, handlers and idempotency|Configuring Ubuntu and Fedora/RHEL hosts
Ansible Roles and Secret Handling|Reusable roles and collections|Vault and external secret references|Operating a multi-host deployment
Cloud-init and CloudFormation|First-boot configuration and image boundaries|AWS stacks, change sets and drift|Choosing the right provisioning layer
Infrastructure Lifecycle and Disaster Recovery|Bootstrap dependencies and break-glass access|State recovery and teardown|Rebuilding a lost environment
'''),
('AWS Foundations', '''
AWS Accounts, Regions and Responsibility|Accounts, organizations and environments|Regions, zones and service boundaries|A usable account layout
AWS CLI and Identity Sessions|Profiles, regions and output formats|SSO, role sessions and credential precedence|Verifying identity before a command
IAM Policies and Least Privilege|Actions, resources and conditions|Role trust and permission evaluation|Debugging an access-denied response
VPC, Subnets and Routes|Address design and routing|Internet access, NAT and endpoints|Tracing traffic through an AWS network
Security Groups and Network ACLs|Stateful and stateless boundaries|Ingress, egress and service exposure|A private database connectivity investigation
EC2 and Instance Lifecycle|Images, instance types and metadata|SSH, Systems Manager and instance profiles|Provisioning and replacing a server
EBS and Cloud Storage Choices|Block, file and object semantics|Snapshots, performance and encryption|Choosing storage for an application
S3 from the CLI|Buckets, objects and access controls|Versioning, lifecycle and multipart upload|Operating an upload and retention workflow
Route 53, Certificates and Load Balancers|DNS records and routing policies|ACM and load-balancer integration|Publishing a secure endpoint
AWS Budgets, Tags and Inventory|Ownership and allocation tags|Budgets, quotas and billing evidence|Finding forgotten resources before cleanup
'''),
('AWS Production Services', '''
EC2 Auto Scaling and Launch Templates|Immutable launches and capacity policy|Health, draining and replacement|Scaling a host-based service
ECR and Container Artifact Promotion|Repository permissions and image identity|Scanning, retention and cross-account access|Publishing a release by digest
ECS and Fargate Services|Tasks, services and capacity|Networking, IAM and deployment health|Deploying an API and background worker
EKS and AWS Integration|Managed control plane and worker ownership|Identity, networking and storage integrations|An EKS operational responsibility map
RDS and Managed Database Operations|Availability, maintenance and connections|Backups, replicas and recovery|Diagnosing database saturation
ElastiCache and Managed Caching|Cache authority and eviction|Failover, connections and access|Designing for a cache outage
SQS, SNS and EventBridge|Queue, fanout and routing semantics|Visibility, retries and dead letters|Operating a notification pipeline
Lambda and Serverless Tradeoffs|Execution lifecycle and concurrency|Retries, packaging and observability|Choosing a small event-driven task
CloudFront and Edge Delivery|Origins, caching and invalidation|Headers, authorization and dynamic content|Reducing origin load without stale-data surprises
Secrets, CloudWatch and Cloud Resilience|KMS, Secrets Manager and rotation|Logs, metrics and managed alarms|A multi-zone recovery and cost review
'''),
('Kubernetes Foundations', '''
Kubernetes Architecture and Reconciliation|API server, controllers and etcd|Nodes, kubelet and container runtime|Following a desired-state change
Local Clusters and kubectl Contexts|kind, minikube and environment prerequisites|Contexts, namespaces and access|Avoiding a command against the wrong cluster
Pods and Application Lifecycles|Pod identity and container restart|Init containers and lifecycle hooks|Deploying and inspecting a small service
Deployments, ReplicaSets and Jobs|Controllers and ownership|Rollouts, Jobs and CronJobs|Choosing a workload controller
Services and Cluster DNS|Selectors, endpoints and virtual addresses|Discovery and connection paths|Debugging a Service with no working backend
ConfigMaps, Secrets and Configuration|Configuration injection and updates|Secret boundaries and application reload|Changing configuration predictably
Probes and Graceful Termination|Startup, readiness and liveness|Termination and traffic draining|Preventing probe-driven restart loops
Resource Requests, Limits and Scheduling|Scheduling and runtime enforcement|CPU throttling and memory exhaustion|Right-sizing a workload from evidence
Persistent Volumes and Stateful Workloads|Claims, classes and binding|StatefulSets and storage lifecycle|Replacing a Pod without losing data
kubectl Diagnostics and API Objects|get, describe, logs, exec and events|Object fields, labels and selectors|A first Kubernetes incident investigation
'''),
('Kubernetes Production Engineering', '''
Cluster Provisioning and Ownership|Managed and self-managed responsibilities|kubeadm, bootstrap and maintenance|A production cluster responsibility checklist
Cluster Networking and CNI|Pod routing and network implementation|Network policies and reachability|Diagnosing cross-node packet paths
Ingress and Gateway API|HTTP routing and controller ownership|TLS, ingress classes and Gateway resources|Publishing services with a supported controller
CSI and Production Storage|Drivers, snapshots and topology|Access modes, recovery and expansion|Diagnosing a volume that will not attach
RBAC and Workload Identity|Subjects, roles and bindings|Service accounts and external identity|Reducing deployment credentials
Placement, Disruption and Availability|Affinity, taints and topology spreading|Disruption budgets and maintenance|Draining nodes without false availability claims
Horizontal, Vertical and Node Autoscaling|Metrics, feedback and scaling boundaries|HPA, VPA and node capacity|Diagnosing oscillation and unschedulable Pods
Helm and Kustomize|Packages, templates and overlays|Values, rendered manifests and release state|Reviewing deployment customization
Operators and Admission Policy|Custom resources and controller contracts|Admission, policy and lifecycle ownership|Deciding whether an operator is justified
Upgrades, etcd and Cluster Recovery|Version skew and staged upgrades|Control-plane backup and recovery|A failed-upgrade and restore scenario
'''),
('Continuous Integration Platforms', '''
CI Architecture and Trust Boundaries|Events, workers and pipeline graphs|Untrusted code and credential exposure|Designing an artifact-producing pipeline
GitHub Actions Workflows|Events, jobs, steps and expressions|Reusable workflows and matrices|A multi-language test workflow
GitHub Actions Runners and Security|Hosted and self-hosted execution|Permissions, OIDC and action pinning|Hardening a deployment workflow
GitLab CI Pipeline Design|Stages, jobs, rules and includes|Artifacts, dependencies and environments|A merge-request and release pipeline
GitLab Runners and Credentials|Executor choices and runner isolation|Protected variables and federated identity|Operating runners without cross-job leakage
Jenkins Controllers and Agents|Controller duties and agent execution|Plugins, credentials and lifecycle|Installing and securing a Jenkins service
Jenkins Declarative Pipelines|Jenkinsfile, stages and post actions|Shared libraries and controlled reuse|A build, test and publish pipeline
Tests, Quality Gates and Feedback|Unit, integration and contract boundaries|Security scans and useful gates|Balancing confidence with pipeline duration
Artifacts, Caches and Build Reproducibility|Artifacts versus disposable caches|Dependency integrity and reproducible inputs|Tracking one artifact through a pipeline
CI Incidents and Platform Comparison|Queueing, flaky jobs and worker pressure|GitHub, GitLab and Jenkins tradeoffs|Diagnosing a compromised or stalled pipeline
'''),
('Delivery, Deployment and GitOps', '''
Release Engineering and Artifact Promotion|Build once and release identity|Environment gates and evidence|Promoting a tested image
Deployment to VPS Infrastructure|SSH boundaries and release directories|Health checks and atomic switches|A reversible single-host deployment
Container Deployment to AWS|ECS task revisions and service updates|EKS manifests and release evidence|A staged cloud deployment
Rolling Updates and Blue Green|Mixed versions and traffic switching|Capacity headroom and session state|Choosing a release strategy
Canary Releases and Feature Flags|Cohorts, metrics and decision windows|Flag lifecycle and rollback control|Stopping a harmful release early
Database and Message Compatibility|Expand-and-contract schema changes|Backfills and mixed-version messages|Releasing without breaking old workers
GitOps Principles and Reconciliation|Git state, controllers and drift|Promotion and secret boundaries|Separating build from deployment authority
Argo CD in Practice|Applications, sync and health|Projects, permissions and rollback behavior|Operating an application through Argo CD
Flux in Practice|Sources, reconciliation and dependencies|Image automation and environment changes|Operating a comparable Flux deployment
Rollback, Roll Forward and Release Incidents|Application, data and infrastructure boundaries|Unknown completion and recovery decisions|A failed-release investigation
'''),
('Observability and Telemetry', '''
Observability from Questions to Evidence|Metrics, logs, traces and profiles|User impact and service boundaries|Instrumenting a meaningful request path
Prometheus and Exporters|Scrapes, labels and time series|Exporters, discovery and retention|Monitoring hosts and application services
PromQL for Operational Questions|Counters, gauges, rates and histograms|Aggregation and missing series|Investigating latency and error rates
Grafana Dashboards and Provisioning|Data sources, queries and panels|Variables, provisioning and access|A dashboard that supports diagnosis
Alertmanager and Actionable Alerts|Grouping, routing and inhibition|Ownership and alert fatigue|Paging on service impact
Logs with Journald and Loki|Structured events and correlation|Collection, labels and retention|Following an error across services
OpenTelemetry Instrumentation and Collectors|Context propagation and signals|Collector pipelines and sampling|Tracing a multi-language request
Tempo, Jaeger and Trace Investigation|Spans, parent relationships and timing|Sampling limits and backend choices|Finding a slow downstream dependency
Elastic, OpenSearch and CloudWatch|Search-oriented log workflows|Managed telemetry and query costs|Choosing a telemetry backend
Observability at Scale|Cardinality, storage and ingestion budgets|SLO dashboards and telemetry outages|A capacity review for the monitoring system
'''),
('Performance and Capacity Engineering', '''
Workload Models and Measurement|Arrival rates, concurrency and service time|Percentiles and representative workloads|Writing a load-test charter
CPU, Memory and Scheduler Diagnosis|Utilization, contention and pressure|Profiling and working-set evidence|Distinguishing CPU saturation from waiting
Disk, Network and Connection Bottlenecks|Latency, bandwidth, queues and IOPS|Connection pools and file descriptors|Finding a shared resource ceiling
Load Testing with k6 and Locust|Open and closed workload models|Warmup, test data and correctness|A staged DispatchDesk load experiment
Vertical Scaling Decisions|Headroom, larger machines and limits|Downtime, cost and diminishing returns|A measured VPS resize decision
Horizontal Scaling Decisions|Stateless work and shared state|Coordination, partitioning and balancing|Adding replicas without multiplying a bottleneck
Autoscaling as a Feedback System|Signals, delay and stabilization|Cold starts, floors and ceilings|Preventing scaling oscillation
Capacity Planning and Forecasting|Growth, seasonality and failure reserve|Quotas and lead times|Estimating capacity with uncertainty
Caching, Batching and Efficiency|Reuse, locality and amortized cost|Freshness and batch latency|Reducing work before adding machines
Cost and Performance Tradeoffs|Unit economics and total ownership|Spot capacity, commitments and architecture|Comparing three scaling proposals
'''),
('Distributed Systems and Data Operations', '''
Partial Failure and Timeouts|Independent failure and uncertain outcomes|Timeout budgets and cancellation|Following a request that may have succeeded
Retries, Idempotency and Backoff|Duplicate work and retry storms|Idempotency keys and jitter|A reliable worker retry contract
Queues and Backpressure|Producer and consumer rates|Leases, dead letters and flow control|Recovering a growing work backlog
Database Connections and Concurrency|Pools, locks and transaction boundaries|Contention and isolation|Diagnosing a database-backed service
Replication and Failover|Replication lag and durability|Leader authority and fencing|Avoiding split-brain recovery
Consistency and Consensus Concepts|Ordering, quorums and partitions|Consistency contracts and operational limits|Reasoning about a coordination service
Cache Design and Invalidation|Source of truth and derived state|Stampedes, expiration and outage behavior|A controlled cache-failure experiment
Database Scaling and Partitioning|Indexes, read replicas and sharding|Hot keys and cross-partition work|Choosing a data scaling path
Messaging and Event-driven Architecture|Events, commands and delivery semantics|Outbox, ordering and schema evolution|Connecting order processing to notifications
Stateful Recovery and Data Migration|Backfill, reconciliation and authority|Cutover and recovery evidence|Migrating a live data boundary
'''),
('Security and Software Supply Chains', '''
Threat Modeling for Operators|Assets, identities and trust boundaries|Abuse paths and practical controls|Threat modeling DispatchDesk
Host Security and Patch Management|Access, packages and attack surface|Ubuntu and Fedora/RHEL hardening differences|A defensible host-maintenance process
Container Security in Practice|Image content and runtime privilege|Rootless operation and workload isolation|Reviewing a container security posture
Kubernetes Security Boundaries|API access, workload policy and tenancy|Pod Security and network controls|A cluster threat and permissions review
Secrets and Credential Rotation|Secret distribution and lifecycle|Vault, cloud secrets and rotation|Recovering from a leaked credential
Federation, OIDC and Short-lived Identity|Trust claims and audience boundaries|CI and workload federation|Replacing static cloud keys
Vulnerability Scanning and SBOMs|Package inventory and vulnerability evidence|Trivy, Grype and SBOM workflows|Prioritizing fixes by exposure and impact
Artifact Signing and Provenance|Signatures, attestations and trust roots|Cosign and provenance verification|Verifying an artifact before deployment
Policy, Audit and Compliance Evidence|Policies as explicit controls|OPA and admission evidence|A reviewable release approval record
Security Incidents and Containment|Evidence preservation and isolation|Credential revocation and clean rebuild|A compromised-runner response
'''),
('Site Reliability and Recovery', '''
SLIs, SLOs and Error Budgets|User journeys and measurement windows|Targets and release decisions|Defining a useful service objective
On-call and Operational Readiness|Ownership, escalation and handoff|Runbooks and response authority|Preparing a team for production responsibility
Incident Command and Communication|Declaration, roles and updates|Stabilization and uncertainty|Running a coordinated outage response
Troubleshooting Under Pressure|Hypotheses, timelines and safe experiments|Mitigation versus causal explanation|An outage investigation with incomplete evidence
Postmortems and Corrective Actions|Contributing factors and evidence|Action ownership and effectiveness|Turning an incident into engineering work
Backup Engineering|Consistency, retention and encryption|Independent copies and restore evidence|Testing database and object restoration
Disaster Recovery and Failback|RPO, RTO and dependency recovery|Failover authority and return to normal|A regional-loss recovery plan
Chaos and Resilience Experiments|Hypotheses, blast radius and stop conditions|Fault injection and recovery evidence|A bounded service failure experiment
Reliability Testing and Game Days|Load, fault and recovery combinations|Tabletop and technical exercises|A rehearsal before a major launch
Reducing Toil and Improving Operations|Manual work and recurring failure|Automation, guardrails and maintenance|A reliability improvement roadmap
'''),
('Architecture and Platform Engineering', '''
Monoliths, Services and Organizational Boundaries|Deployment and ownership boundaries|Coupling and operational overhead|Choosing a service extraction
Platform Teams and Developer Experience|Internal customers and product thinking|Golden paths and escape hatches|A small useful deployment platform
Multi-tenancy and Isolation|Shared, pooled and dedicated resources|Noisy neighbors and authorization|Choosing an isolation boundary
Service Meshes and Traffic Policy|Identity, routing and telemetry|Sidecar and ambient tradeoffs|Deciding whether a mesh earns its cost
Multi-zone and Multi-region Architecture|Latency, authority and failure domains|Active-passive and active-active designs|A regional architecture review
Hybrid and Restricted Environments|Connectivity, mirrors and artifact trust|Air-gapped updates and operational access|Operating with limited external dependencies
Legacy Infrastructure Modernization|Inventory, constraints and behavior|Incremental migration and reversibility|Replacing a fragile deployment process
Architecture Reviews and Decision Records|Requirements, alternatives and evidence|Assumptions and reversal triggers|Reviewing a production proposal
FinOps and Engineering Economics|Ownership, allocation and unit cost|Forecasts and optimization evidence|Choosing between labor and cloud spend
Senior Engineering Judgment|Uncertainty, prioritization and communication|Simple designs and justified complexity|Mentoring through a difficult operational decision
'''),
('Projects and Industry Case Studies', '''
DispatchDesk on a Single VPS|Initial workload and operational contract|Native services and first release|A first failure and measured improvement
The VPS Company Scales Carefully|Vertical growth and resource evidence|Second host and managed database choices|Why the team delays Kubernetes
The Managed AWS Company|ECS, queues and managed persistence|Team capacity and service boundaries|A growth-driven architecture change
The Kubernetes Platform Company|Several teams and deployment requirements|Shared platform and workload isolation|Why Kubernetes becomes justified
Multi-language Services in Production|Python, PHP, Go and JavaScript lifecycles|Signals, health, concurrency and telemetry|Comparable deployment contracts across runtimes
Three Pipelines for One Release Contract|GitHub Actions implementation|GitLab CI and Jenkins implementations|Comparing evidence, credentials and recovery
An End-to-end Observability Investigation|Instrumentation and user symptoms|Metrics, logs and traces|A slow-order incident and resolution
Google SRE Practices in Context|Published reliability and release practices|Constraints behind organizational choices|What a smaller team can reuse
Netflix Container and Delivery Evolution|Dated container and delivery publications|Platform decisions and migration context|Lessons without copying an entire stack
Uber Observability and Alternative Growth Paths|Documented observability case studies|Historical scope and architecture constraints|Comparing real evidence with fictional company decisions
'''),
('Operational Reference', '''
Linux and Shell Command Reference|Inspection, files, processes and services|Arguments, outcomes and failure clues|Links to canonical explanations
Networking and VPS Diagnostic Reference|DNS, TLS, routing and sockets|Layered diagnostic decision trees|A quick incident evidence checklist
Docker and Podman Command Reference|Lifecycle, images, storage and networks|Compatibility and rootless differences|Command-to-chapter lookup
Kubernetes Command and Object Reference|kubectl inspection and change commands|Objects, ownership and common symptoms|Safe context and rollout checks
AWS CLI Operational Reference|Identity, networking, compute and data commands|Pagination, queries and permissions|Cost-aware resource inspection
Infrastructure and Pipeline Reference|Terraform, OpenTofu and Ansible workflows|GitHub, GitLab and Jenkins release checks|Change and credential checklists
Scaling and Architecture Decision Tables|Vertical, horizontal and efficiency options|Data, tenancy and regional tradeoffs|Evidence needed before a scaling decision
Observability and Incident Runbooks|Metrics, logs, traces and alert symptoms|First-response and handoff templates|An evidence-based diagnostic index
Compatibility Matrix and Glossary|Supported baselines and provider differences|Terms, abbreviations and conceptual boundaries|A maintenance and verification ledger
Production Readiness and Recovery Checklists|Release, security and ownership evidence|Backup, failover and rollback readiness|A final service review
'''),
]

def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')

def main():
    manifest = []
    volumes = []
    for volume, (title, raw) in enumerate(VOLUMES, 1):
        vdir = f'book/volumes/{volume:02d}-{slug(title)}'
        Path(ROOT / vdir).mkdir(parents=True, exist_ok=True)
        records = []
        for line in raw.strip().splitlines():
            chapter_title, *sections = line.split('|')
            number = len(manifest) + 1
            filename = f'{number:03d}-{slug(chapter_title)}.md'
            record = dict(chapter=number, volume=volume, volume_title=title, title=chapter_title,
                          path=f'{vdir}/{filename}', summary=f'book/_ai/chapter-summaries/{filename}',
                          review=f'book/_ai/reviews/{filename}', sections=sections,
                          prerequisites=[number - 1] if number > 1 else [])
            manifest.append(record)
            records.append(record)
            path = ROOT / record['path']
            if not path.exists():
                path.write_text(frontmatter(record, 'planned') + f"\n# Chapter {number} — {chapter_title}\n\n"
                                + '> Authoring placeholder. This chapter has not been written.\n')
            summary = ROOT / record['summary']
            summary.parent.mkdir(parents=True, exist_ok=True)
            if not summary.exists():
                summary.write_text(f"# Chapter {number} continuation\n\nStatus: planned\n\n"
                                   f"## Written material\nNone.\n\n## Exact next section\nWhy this matters\n\n"
                                   '## Concepts and terminology\nNone introduced yet.\n\n'
                                   '## Examples and cross-references\nNone written yet.\n\n'
                                   '## Open threads\nWrite and independently review the chapter.\n\n'
                                   '## Verification\nNot performed.\n')
        volumes.append(dict(volume=volume, title=title, path=vdir, chapters=records))
        (ROOT / vdir / 'README.md').write_text(f'# Volume {volume} — {title}\n\n[Book index](../../README.md)\n\n'
            + '\n'.join(f"- [Chapter {r['chapter']} — {r['title']}]({Path(r['path']).name})" for r in records) + '\n')
    (ROOT / 'book/_ai/reviews').mkdir(parents=True, exist_ok=True)
    (ROOT / 'book/_ai/manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (ROOT / 'book/README.md').write_text('# The Complete DevOps Engineering Book\n\n'
        'Read in order for the novice-to-production learning path. Experienced operators can use '
        'the [reference volume](volumes/22-operational-reference/README.md) and follow its links to deeper explanations.\n\n'
        '## Volumes\n\n' + '\n'.join(f"- [Volume {v['volume']} — {v['title']}]({v['path'].removeprefix('book/')}/README.md)" for v in volumes)
        + '\n\n## Reading paths\n\n'
        '- Foundations: Volumes 1–4, followed by 5–7.\n'
        '- Cloud operations: foundations, then 8–10, 13–19.\n'
        '- Kubernetes operations: foundations and containers, then 11–19.\n'
        '- Senior reference: Volumes 16–22, following prerequisite links when needed.\n'
        '- Project journey: Volume 21 alongside the relevant explanatory chapters.\n\n'
        'Draft and review status is maintained in [PROGRESS.md](../PROGRESS.md).\n')
    skeleton = ['# The Complete DevOps Engineering Book — Detailed Skeleton', '',
        '## Authoritative teaching brief', '',
        'Teach requirements → constraints → alternatives → decision → commands/configuration → mechanism → evidence → failure → recovery → scaling. '
        'The audience progresses from a novice to an engineer who can reason about unfamiliar production problems. '
        'Senior readers should gain diagnostic references and alternative designs. This is an engineering book, not a list of commands.', '',
        'English; Markdown and complete inline examples; equal Ubuntu and Fedora/RHEL coverage. '
        'Do not force Kubernetes, microservices or horizontal scaling onto a problem that does not justify them. '
        'Examples must distinguish fictional organizations from dated, attributed company publications.', '',
        '## Chapter contract', '',
        'Each chapter includes purpose and prerequisites, a mental model, the ordered subject sections below, '
        'a small practical example, command explanations, a realistic failure/diagnosis/recovery scenario, '
        'engineering tradeoffs, exercises with answer guidance, review questions, concise takeaways and primary sources. '
        'Adapt headings to the subject; do not repeat boilerplate prose. For each command state execution context, '
        'arguments/flags, purpose, expected outcome, state changes, errors and verification; include rollback/cleanup where relevant.', '',
        'Substantial chapters normally need roughly 1,500–3,000 words, sometimes more. References may be shorter. '
        'Depth and examples determine length; word counts are diagnostic, not a substitute for editorial judgment. '
        'All important commands and complete files stay inline in the book rather than in companion lab directories.', '',
        '## Project continuity', '',
        'DispatchDesk accepts orders and sends notifications. Start with one process and a local database. '
        'Add a worker, PostgreSQL, Redis, monitoring and release automation as constraints appear. '
        'The VPS company values low cost and a small operational footprint; the AWS company favors managed services '
        'and ECS; the platform company eventually needs Kubernetes for several teams. Record assumptions and decision '
        'changes rather than implying that these routes are stages every organization must follow. '
        'Use Python, PHP, Go and JavaScript examples when their lifecycle, concurrency or deployment differences matter.', '',
        '## Progress and agent protocol', '',
        'Read AI_AUTHORING_GUIDE.md and PROGRESS.md before writing. Read the target chapter summary and its brief below. '
        'Use gpt-6.1-sol with low reasoning for writing and independent review agents. Workers own disjoint chapters; '
        'only the coordinator updates shared state and indexes. Save a factual summary at each substantial boundary. '
        'Never restart completed material or label a placeholder, unreviewed draft or untested integration as complete.', '',
        '## Canonical topic ownership', '',
        'Linux primitives belong to Volume 2; packet and protocol explanations to Volume 3; '
        'host operations to Volume 4; container internals to Volume 5; tool-specific behavior to Volumes 6–7; '
        'IaC semantics to Volume 8; AWS basics to Volume 9; Kubernetes reconciliation to Volume 11; '
        'CI trust to Volume 13; release compatibility to Volume 14; telemetry semantics to Volume 15; '
        'scaling mathematics to Volume 16; delivery/consistency contracts to Volume 17; '
        'security control selection to Volume 18; SLO and recovery objectives to Volume 19. '
        'Cross-reference the owning chapter instead of re-explaining it.', '',
        '## Complete chapter briefs', '']
    for v in volumes:
        skeleton += [f"## Volume {v['volume']} — {v['title']}", '']
        for r in v['chapters']:
            prev = f"Chapter {r['chapter']-1}" if r['chapter'] > 1 else 'No prior knowledge assumed'
            skeleton += [f"### {r['chapter']:03d}. {r['title']}", '',
                f"- Chapter: [{r['path']}]({r['path']}). Prerequisite: {prev}; consult canonical-topic chapters for deeper dependencies.",
                '- Ordered core sections: ' + '; '.join(r['sections']) + '.',
                f"- Outcome: explain and apply {r['title'].lower()}, recognize its operational limits, and justify a decision under stated constraints.",
                f"- Example and failure brief: make {r['sections'][-1].lower()} concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.",
                '- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.', '']
    (ROOT / 'SKELETON.md').write_text('\n'.join(skeleton) + '\n')

def frontmatter(r, status):
    return ('---\nbook: The Complete DevOps Engineering Book\n'
            f"volume: {r['volume']}\nvolume_title: {json.dumps(r['volume_title'])}\nchapter: {r['chapter']}\n"
            f"title: {json.dumps(r['title'])}\nslug: {slug(r['title'])}\nstatus: {status}\n"
            f"summary: ../../_ai/chapter-summaries/{Path(r['path']).name}\n---\n")

if __name__ == '__main__':
    main()
