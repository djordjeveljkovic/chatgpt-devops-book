# The Complete DevOps Engineering Book — Detailed Skeleton

## Authoritative teaching brief

Teach requirements → constraints → alternatives → decision → commands/configuration → mechanism → evidence → failure → recovery → scaling. The audience progresses from a novice to an engineer who can reason about unfamiliar production problems. Senior readers should gain diagnostic references and alternative designs. This is an engineering book, not a list of commands.

English; Markdown and complete inline examples; equal Ubuntu and Fedora/RHEL coverage. Do not force Kubernetes, microservices or horizontal scaling onto a problem that does not justify them. Examples must distinguish fictional organizations from dated, attributed company publications.

## Chapter contract

Each chapter includes purpose and prerequisites, a mental model, the ordered subject sections below, a small practical example, command explanations, a realistic failure/diagnosis/recovery scenario, engineering tradeoffs, exercises with answer guidance, review questions, concise takeaways and primary sources. Adapt headings to the subject; do not repeat boilerplate prose. For each command state execution context, arguments/flags, purpose, expected outcome, state changes, errors and verification; include rollback/cleanup where relevant.

Substantial chapters normally need roughly 1,500–3,000 words, sometimes more. References may be shorter. Depth and examples determine length; word counts are diagnostic, not a substitute for editorial judgment. All important commands and complete files stay inline in the book rather than in companion lab directories.

## Project continuity

DispatchDesk accepts orders and sends notifications. Start with one process and a local database. Add a worker, PostgreSQL, Redis, monitoring and release automation as constraints appear. The VPS company values low cost and a small operational footprint; the AWS company favors managed services and ECS; the platform company eventually needs Kubernetes for several teams. Record assumptions and decision changes rather than implying that these routes are stages every organization must follow. Use Python, PHP, Go and JavaScript examples when their lifecycle, concurrency or deployment differences matter.

## Progress and agent protocol

Read AI_AUTHORING_GUIDE.md and PROGRESS.md before writing. Read the target chapter summary and its brief below. Use gpt-6.1-sol with low reasoning for writing and independent review agents. Workers own disjoint chapters; only the coordinator updates shared state and indexes. Save a factual summary at each substantial boundary. Never restart completed material or label a placeholder, unreviewed draft or untested integration as complete.

## Canonical topic ownership

Linux primitives belong to Volume 2; packet and protocol explanations to Volume 3; host operations to Volume 4; container internals to Volume 5; tool-specific behavior to Volumes 6–7; IaC semantics to Volume 8; AWS basics to Volume 9; Kubernetes reconciliation to Volume 11; CI trust to Volume 13; release compatibility to Volume 14; telemetry semantics to Volume 15; scaling mathematics to Volume 16; delivery/consistency contracts to Volume 17; security control selection to Volume 18; SLO and recovery objectives to Volume 19. Cross-reference the owning chapter instead of re-explaining it.

## Complete chapter briefs

## Volume 1 — Engineering Mental Models

### 001. What DevOps Engineers Actually Own

- Chapter: [book/volumes/01-engineering-mental-models/001-what-devops-engineers-actually-own.md](book/volumes/01-engineering-mental-models/001-what-devops-engineers-actually-own.md). Prerequisite: No prior knowledge assumed; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Service lifecycle and responsibility; DevOps, operations, platform engineering and SRE; From a ticket to an operating outcome.
- Outcome: explain and apply what devops engineers actually own, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make from a ticket to an operating outcome concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 002. Requirements Before Tools

- Chapter: [book/volumes/01-engineering-mental-models/002-requirements-before-tools.md](book/volumes/01-engineering-mental-models/002-requirements-before-tools.md). Prerequisite: Chapter 1; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Functional and operational requirements; Constraints and measurable acceptance; Writing a service charter.
- Outcome: explain and apply requirements before tools, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make writing a service charter concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 003. How Computers Execute Services

- Chapter: [book/volumes/01-engineering-mental-models/003-how-computers-execute-services.md](book/volumes/01-engineering-mental-models/003-how-computers-execute-services.md). Prerequisite: Chapter 2; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: CPU, memory, storage and networks; Processes, kernels and system calls; Following one request through a machine.
- Outcome: explain and apply how computers execute services, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make following one request through a machine concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 004. Reliability and Risk

- Chapter: [book/volumes/01-engineering-mental-models/004-reliability-and-risk.md](book/volumes/01-engineering-mental-models/004-reliability-and-risk.md). Prerequisite: Chapter 3; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Availability, durability and correctness; Failure domains and correlated failure; Choosing an acceptable risk budget.
- Outcome: explain and apply reliability and risk, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing an acceptable risk budget concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 005. Architecture as Tradeoffs

- Chapter: [book/volumes/01-engineering-mental-models/005-architecture-as-tradeoffs.md](book/volumes/01-engineering-mental-models/005-architecture-as-tradeoffs.md). Prerequisite: Chapter 4; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Quality attributes and competing objectives; Reversibility and decision records; Comparing three viable architectures.
- Outcome: explain and apply architecture as tradeoffs, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make comparing three viable architectures concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 006. Environments and Reproducibility

- Chapter: [book/volumes/01-engineering-mental-models/006-environments-and-reproducibility.md](book/volumes/01-engineering-mental-models/006-environments-and-reproducibility.md). Prerequisite: Chapter 5; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Development, staging and production; Configuration and artifact identity; Preventing environment drift.
- Outcome: explain and apply environments and reproducibility, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make preventing environment drift concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 007. Learning to Investigate

- Chapter: [book/volumes/01-engineering-mental-models/007-learning-to-investigate.md](book/volumes/01-engineering-mental-models/007-learning-to-investigate.md). Prerequisite: Chapter 6; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Observation, hypotheses and experiments; Evidence quality and uncertainty; A disciplined troubleshooting notebook.
- Outcome: explain and apply learning to investigate, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a disciplined troubleshooting notebook concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 008. Working Safely at the CLI

- Chapter: [book/volumes/01-engineering-mental-models/008-working-safely-at-the-cli.md](book/volumes/01-engineering-mental-models/008-working-safely-at-the-cli.md). Prerequisite: Chapter 7; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Execution context and privileges; Read, change, verify and recover; Recognizing destructive and costly commands.
- Outcome: explain and apply working safely at the cli, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make recognizing destructive and costly commands concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 009. Teams, Ownership and Operational Work

- Chapter: [book/volumes/01-engineering-mental-models/009-teams-ownership-and-operational-work.md](book/volumes/01-engineering-mental-models/009-teams-ownership-and-operational-work.md). Prerequisite: Chapter 8; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Service ownership and handoffs; Toil, collaboration and documentation; A practical operational readiness review.
- Outcome: explain and apply teams, ownership and operational work, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a practical operational readiness review concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 010. The DispatchDesk Project Begins

- Chapter: [book/volumes/01-engineering-mental-models/010-the-dispatchdesk-project-begins.md](book/volumes/01-engineering-mental-models/010-the-dispatchdesk-project-begins.md). Prerequisite: Chapter 9; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: A small order and notification product; Workload, budget and reliability assumptions; Three companies with different constraints.
- Outcome: explain and apply the dispatchdesk project begins, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make three companies with different constraints concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 2 — Linux and Automation

### 011. The Shell and Command Execution

- Chapter: [book/volumes/02-linux-and-automation/011-the-shell-and-command-execution.md](book/volumes/02-linux-and-automation/011-the-shell-and-command-execution.md). Prerequisite: Chapter 10; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Arguments, quoting and expansion; Environment, exit codes and PATH; Tracing a command without leaking secrets.
- Outcome: explain and apply the shell and command execution, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make tracing a command without leaking secrets concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 012. Files, Paths and Filesystem Tools

- Chapter: [book/volumes/02-linux-and-automation/012-files-paths-and-filesystem-tools.md](book/volumes/02-linux-and-automation/012-files-paths-and-filesystem-tools.md). Prerequisite: Chapter 11; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Paths, inodes and directory entries; Finding and inspecting files; Safe copy, move and deletion workflows.
- Outcome: explain and apply files, paths and filesystem tools, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make safe copy, move and deletion workflows concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 013. Text Processing and Pipelines

- Chapter: [book/volumes/02-linux-and-automation/013-text-processing-and-pipelines.md](book/volumes/02-linux-and-automation/013-text-processing-and-pipelines.md). Prerequisite: Chapter 12; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Streams, redirection and pipes; Searching and transforming structured text; Building a useful diagnostic pipeline.
- Outcome: explain and apply text processing and pipelines, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make building a useful diagnostic pipeline concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 014. Users, Groups and Permissions

- Chapter: [book/volumes/02-linux-and-automation/014-users-groups-and-permissions.md](book/volumes/02-linux-and-automation/014-users-groups-and-permissions.md). Prerequisite: Chapter 13; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Ownership, modes and ACLs; sudo and privilege boundaries; Diagnosing permission denied.
- Outcome: explain and apply users, groups and permissions, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing permission denied concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 015. Processes, Signals and Jobs

- Chapter: [book/volumes/02-linux-and-automation/015-processes-signals-and-jobs.md](book/volumes/02-linux-and-automation/015-processes-signals-and-jobs.md). Prerequisite: Chapter 14; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Process trees and descriptors; Signals and exit behavior; Stopping a stuck service gracefully.
- Outcome: explain and apply processes, signals and jobs, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make stopping a stuck service gracefully concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 016. Systemd and Service Lifecycles

- Chapter: [book/volumes/02-linux-and-automation/016-systemd-and-service-lifecycles.md](book/volumes/02-linux-and-automation/016-systemd-and-service-lifecycles.md). Prerequisite: Chapter 15; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Units, dependencies and restart policy; Journal and unit overrides; Operating a supervised service.
- Outcome: explain and apply systemd and service lifecycles, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make operating a supervised service concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 017. Packages and Linux Distributions

- Chapter: [book/volumes/02-linux-and-automation/017-packages-and-linux-distributions.md](book/volumes/02-linux-and-automation/017-packages-and-linux-distributions.md). Prerequisite: Chapter 16; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: apt, dnf and package provenance; Ubuntu and Fedora/RHEL release differences; Installing and upgrading reproducibly.
- Outcome: explain and apply packages and linux distributions, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make installing and upgrading reproducibly concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 018. Shell Automation That Survives Failure

- Chapter: [book/volumes/02-linux-and-automation/018-shell-automation-that-survives-failure.md](book/volumes/02-linux-and-automation/018-shell-automation-that-survives-failure.md). Prerequisite: Chapter 17; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Input validation and quoting; Idempotency, traps and temporary files; A restartable maintenance script.
- Outcome: explain and apply shell automation that survives failure, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a restartable maintenance script concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 019. Git for Operational Changes

- Chapter: [book/volumes/02-linux-and-automation/019-git-for-operational-changes.md](book/volumes/02-linux-and-automation/019-git-for-operational-changes.md). Prerequisite: Chapter 18; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Commits, branches and review; Reverting and resolving conflicts; Managing infrastructure changes as code.
- Outcome: explain and apply git for operational changes, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make managing infrastructure changes as code concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 020. Scheduling and Resource Limits

- Chapter: [book/volumes/02-linux-and-automation/020-scheduling-and-resource-limits.md](book/volumes/02-linux-and-automation/020-scheduling-and-resource-limits.md). Prerequisite: Chapter 19; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Timers, cron and time zones; File descriptors and process limits; Preventing overlapping scheduled jobs.
- Outcome: explain and apply scheduling and resource limits, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make preventing overlapping scheduled jobs concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 3 — Networking and Traffic

### 021. Packets, Addresses and Routing

- Chapter: [book/volumes/03-networking-and-traffic/021-packets-addresses-and-routing.md](book/volumes/03-networking-and-traffic/021-packets-addresses-and-routing.md). Prerequisite: Chapter 20; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Interfaces, addresses and subnets; Routing tables and packet paths; Diagnosing an unreachable destination.
- Outcome: explain and apply packets, addresses and routing, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing an unreachable destination concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 022. TCP, UDP and Connections

- Chapter: [book/volumes/03-networking-and-traffic/022-tcp-udp-and-connections.md](book/volumes/03-networking-and-traffic/022-tcp-udp-and-connections.md). Prerequisite: Chapter 21; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Handshakes, retransmission and ports; Connection state and timeouts; Using ss and packet capture.
- Outcome: explain and apply tcp, udp and connections, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make using ss and packet capture concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 023. DNS from Resolver to Authority

- Chapter: [book/volumes/03-networking-and-traffic/023-dns-from-resolver-to-authority.md](book/volumes/03-networking-and-traffic/023-dns-from-resolver-to-authority.md). Prerequisite: Chapter 22; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Recursive and authoritative resolution; Caching, TTL and negative responses; Debugging a failed DNS change.
- Outcome: explain and apply dns from resolver to authority, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make debugging a failed dns change concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 024. HTTP and API Traffic

- Chapter: [book/volumes/03-networking-and-traffic/024-http-and-api-traffic.md](book/volumes/03-networking-and-traffic/024-http-and-api-traffic.md). Prerequisite: Chapter 23; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Methods, status and headers; Persistent connections and proxy boundaries; Following a request with curl.
- Outcome: explain and apply http and api traffic, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make following a request with curl concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 025. TLS, Certificates and Trust

- Chapter: [book/volumes/03-networking-and-traffic/025-tls-certificates-and-trust.md](book/volumes/03-networking-and-traffic/025-tls-certificates-and-trust.md). Prerequisite: Chapter 24; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Certificate chains and names; Issuance, renewal and termination; Diagnosing TLS with openssl.
- Outcome: explain and apply tls, certificates and trust, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing tls with openssl concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 026. SSH and Remote Administration

- Chapter: [book/volumes/03-networking-and-traffic/026-ssh-and-remote-administration.md](book/volumes/03-networking-and-traffic/026-ssh-and-remote-administration.md). Prerequisite: Chapter 25; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Keys, agents and host verification; Bastions, tunnels and connection reuse; A reliable remote maintenance session.
- Outcome: explain and apply ssh and remote administration, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a reliable remote maintenance session concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 027. Firewalls and Network Policy

- Chapter: [book/volumes/03-networking-and-traffic/027-firewalls-and-network-policy.md](book/volumes/03-networking-and-traffic/027-firewalls-and-network-policy.md). Prerequisite: Chapter 26; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Stateful filtering and rule ordering; nftables, ufw and firewalld; Changing access without losing SSH.
- Outcome: explain and apply firewalls and network policy, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make changing access without losing ssh concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 028. NAT, Proxies and Connection Tracking

- Chapter: [book/volumes/03-networking-and-traffic/028-nat-proxies-and-connection-tracking.md](book/volumes/03-networking-and-traffic/028-nat-proxies-and-connection-tracking.md). Prerequisite: Chapter 27; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Translation and return paths; Forward and reverse proxies; Finding conntrack and ephemeral-port exhaustion.
- Outcome: explain and apply nat, proxies and connection tracking, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make finding conntrack and ephemeral-port exhaustion concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 029. Load Balancers and Traffic Distribution

- Chapter: [book/volumes/03-networking-and-traffic/029-load-balancers-and-traffic-distribution.md](book/volumes/03-networking-and-traffic/029-load-balancers-and-traffic-distribution.md). Prerequisite: Chapter 28; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Layer four and layer seven routing; Health checks and connection draining; Choosing an algorithm and failure behavior.
- Outcome: explain and apply load balancers and traffic distribution, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing an algorithm and failure behavior concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 030. Network Troubleshooting in Layers

- Chapter: [book/volumes/03-networking-and-traffic/030-network-troubleshooting-in-layers.md](book/volumes/03-networking-and-traffic/030-network-troubleshooting-in-layers.md). Prerequisite: Chapter 29; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Local, route, name and application evidence; tcpdump, tracepath and mtr; Separating packet loss from application latency.
- Outcome: explain and apply network troubleshooting in layers, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make separating packet loss from application latency concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 4 — VPS and Server Operations

### 031. Choosing and Provisioning a VPS

- Chapter: [book/volumes/04-vps-and-server-operations/031-choosing-and-provisioning-a-vps.md](book/volumes/04-vps-and-server-operations/031-choosing-and-provisioning-a-vps.md). Prerequisite: Chapter 30; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Sizing, regions and provider constraints; Images, SSH access and cloud-init; An auditable first-server build.
- Outcome: explain and apply choosing and provisioning a vps, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make an auditable first-server build concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 032. Host Hardening and Access

- Chapter: [book/volumes/04-vps-and-server-operations/032-host-hardening-and-access.md](book/volumes/04-vps-and-server-operations/032-host-hardening-and-access.md). Prerequisite: Chapter 31; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Administrative identities and updates; Exposure reduction and recovery access; An Ubuntu and Fedora/RHEL baseline.
- Outcome: explain and apply host hardening and access, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make an ubuntu and fedora/rhel baseline concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 033. Disks, Filesystems and Mounts

- Chapter: [book/volumes/04-vps-and-server-operations/033-disks-filesystems-and-mounts.md](book/volumes/04-vps-and-server-operations/033-disks-filesystems-and-mounts.md). Prerequisite: Chapter 32; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Block devices, partitions and filesystems; Persistent mounts and growth; Diagnosing full disks and inodes.
- Outcome: explain and apply disks, filesystems and mounts, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing full disks and inodes concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 034. Deploying a Service with Systemd

- Chapter: [book/volumes/04-vps-and-server-operations/034-deploying-a-service-with-systemd.md](book/volumes/04-vps-and-server-operations/034-deploying-a-service-with-systemd.md). Prerequisite: Chapter 33; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Users, working directories and configuration; Release directories and service units; Deploying DispatchDesk without containers.
- Outcome: explain and apply deploying a service with systemd, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make deploying dispatchdesk without containers concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 035. Reverse Proxies on a VPS

- Chapter: [book/volumes/04-vps-and-server-operations/035-reverse-proxies-on-a-vps.md](book/volumes/04-vps-and-server-operations/035-reverse-proxies-on-a-vps.md). Prerequisite: Chapter 34; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Nginx routing and upstreams; TLS, buffering and timeout boundaries; Serving multiple applications safely.
- Outcome: explain and apply reverse proxies on a vps, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make serving multiple applications safely concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 036. Database and Cache Operations on One Host

- Chapter: [book/volumes/04-vps-and-server-operations/036-database-and-cache-operations-on-one-host.md](book/volumes/04-vps-and-server-operations/036-database-and-cache-operations-on-one-host.md). Prerequisite: Chapter 35; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: PostgreSQL and Redis resource competition; Persistence, access and maintenance; Avoiding accidental public exposure.
- Outcome: explain and apply database and cache operations on one host, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make avoiding accidental public exposure concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 037. Server Backups and Restore

- Chapter: [book/volumes/04-vps-and-server-operations/037-server-backups-and-restore.md](book/volumes/04-vps-and-server-operations/037-server-backups-and-restore.md). Prerequisite: Chapter 36; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Files, databases and configuration scope; Retention, encryption and consistency; Restoring into an isolated server.
- Outcome: explain and apply server backups and restore, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make restoring into an isolated server concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 038. Patching and Maintenance Windows

- Chapter: [book/volumes/04-vps-and-server-operations/038-patching-and-maintenance-windows.md](book/volumes/04-vps-and-server-operations/038-patching-and-maintenance-windows.md). Prerequisite: Chapter 37; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Package and kernel updates; Drain, restart and smoke checks; Recovering from a bad host update.
- Outcome: explain and apply patching and maintenance windows, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make recovering from a bad host update concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 039. Adding a Second Server

- Chapter: [book/volumes/04-vps-and-server-operations/039-adding-a-second-server.md](book/volumes/04-vps-and-server-operations/039-adding-a-second-server.md). Prerequisite: Chapter 38; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Shared state and traffic distribution; Configuration consistency and failure domains; Moving from one machine to two.
- Outcome: explain and apply adding a second server, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make moving from one machine to two concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 040. VPS Incidents and Capacity

- Chapter: [book/volumes/04-vps-and-server-operations/040-vps-incidents-and-capacity.md](book/volumes/04-vps-and-server-operations/040-vps-incidents-and-capacity.md). Prerequisite: Chapter 39; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: CPU, memory, disk and network evidence; Provider limits and noisy neighbors; Deciding whether to resize or redesign.
- Outcome: explain and apply vps incidents and capacity, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make deciding whether to resize or redesign concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 5 — Container Internals and OCI

### 041. Containers Are Isolated Processes

- Chapter: [book/volumes/05-container-internals-and-oci/041-containers-are-isolated-processes.md](book/volumes/05-container-internals-and-oci/041-containers-are-isolated-processes.md). Prerequisite: Chapter 40; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Process isolation versus virtual machines; Host-kernel dependencies and limits; Inspecting a running container from the host.
- Outcome: explain and apply containers are isolated processes, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make inspecting a running container from the host concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 042. Linux Namespaces

- Chapter: [book/volumes/05-container-internals-and-oci/042-linux-namespaces.md](book/volumes/05-container-internals-and-oci/042-linux-namespaces.md). Prerequisite: Chapter 41; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: PID, mount, network and user views; Namespace boundaries and inspection; Explaining container-visible resources.
- Outcome: explain and apply linux namespaces, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make explaining container-visible resources concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 043. Cgroups and Resource Accounting

- Chapter: [book/volumes/05-container-internals-and-oci/043-cgroups-and-resource-accounting.md](book/volumes/05-container-internals-and-oci/043-cgroups-and-resource-accounting.md). Prerequisite: Chapter 42; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: CPU, memory and I/O controls; Limits, pressure and OOM behavior; Reading resource evidence rather than guesses.
- Outcome: explain and apply cgroups and resource accounting, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make reading resource evidence rather than guesses concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 044. Images, Layers and Content Identity

- Chapter: [book/volumes/05-container-internals-and-oci/044-images-layers-and-content-identity.md](book/volumes/05-container-internals-and-oci/044-images-layers-and-content-identity.md). Prerequisite: Chapter 43; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: OCI image structure and manifests; Tags, digests and multi-platform images; Tracing an image from registry to runtime.
- Outcome: explain and apply images, layers and content identity, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make tracing an image from registry to runtime concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 045. Container Filesystems and Storage

- Chapter: [book/volumes/05-container-internals-and-oci/045-container-filesystems-and-storage.md](book/volumes/05-container-internals-and-oci/045-container-filesystems-and-storage.md). Prerequisite: Chapter 44; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Read-only layers and writable state; Overlay behavior and mounts; Finding unexpected disk growth.
- Outcome: explain and apply container filesystems and storage, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make finding unexpected disk growth concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 046. OCI Runtimes and Container Engines

- Chapter: [book/volumes/05-container-internals-and-oci/046-oci-runtimes-and-container-engines.md](book/volumes/05-container-internals-and-oci/046-oci-runtimes-and-container-engines.md). Prerequisite: Chapter 45; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Engine, runtime and kernel responsibilities; containerd, CRI-O, runc and crun; Following a container start.
- Outcome: explain and apply oci runtimes and container engines, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make following a container start concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 047. Rootless Containers and User Mapping

- Chapter: [book/volumes/05-container-internals-and-oci/047-rootless-containers-and-user-mapping.md](book/volumes/05-container-internals-and-oci/047-rootless-containers-and-user-mapping.md). Prerequisite: Chapter 46; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: User namespaces and subordinate IDs; Privileges, networking and storage limitations; Explaining root inside a rootless container.
- Outcome: explain and apply rootless containers and user mapping, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make explaining root inside a rootless container concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 048. Capabilities and Security Boundaries

- Chapter: [book/volumes/05-container-internals-and-oci/048-capabilities-and-security-boundaries.md](book/volumes/05-container-internals-and-oci/048-capabilities-and-security-boundaries.md). Prerequisite: Chapter 47; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Capabilities, seccomp and LSMs; AppArmor, SELinux and device access; Reducing privilege for a real workload.
- Outcome: explain and apply capabilities and security boundaries, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make reducing privilege for a real workload concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 049. Registries and Image Distribution

- Chapter: [book/volumes/05-container-internals-and-oci/049-registries-and-image-distribution.md](book/volumes/05-container-internals-and-oci/049-registries-and-image-distribution.md). Prerequisite: Chapter 48; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Authentication, manifests and blobs; Caching, retention and availability; Diagnosing pull and platform errors.
- Outcome: explain and apply registries and image distribution, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing pull and platform errors concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 050. The Container Contract

- Chapter: [book/volumes/05-container-internals-and-oci/050-the-container-contract.md](book/volumes/05-container-internals-and-oci/050-the-container-contract.md). Prerequisite: Chapter 49; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Signals, logs and configuration; Ephemeral execution and durable state; Designing an application that restarts cleanly.
- Outcome: explain and apply the container contract, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make designing an application that restarts cleanly concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 6 — Docker in Practice

### 051. Installing and Inspecting Docker

- Chapter: [book/volumes/06-docker-in-practice/051-installing-and-inspecting-docker.md](book/volumes/06-docker-in-practice/051-installing-and-inspecting-docker.md). Prerequisite: Chapter 50; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Engine installation on both Linux families; Daemon access and privilege; Verifying client, server and context.
- Outcome: explain and apply installing and inspecting docker, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make verifying client, server and context concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 052. Running and Managing Containers

- Chapter: [book/volumes/06-docker-in-practice/052-running-and-managing-containers.md](book/volumes/06-docker-in-practice/052-running-and-managing-containers.md). Prerequisite: Chapter 51; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: run, create, start, stop and remove; Names, ports and restart policy; Operating a small HTTP container.
- Outcome: explain and apply running and managing containers, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make operating a small http container concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 053. Dockerfiles and Build Contexts

- Chapter: [book/volumes/06-docker-in-practice/053-dockerfiles-and-build-contexts.md](book/volumes/06-docker-in-practice/053-dockerfiles-and-build-contexts.md). Prerequisite: Chapter 52; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Instructions, context and ignore rules; Layers and reproducible dependency installation; Building a useful application image.
- Outcome: explain and apply dockerfiles and build contexts, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make building a useful application image concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 054. BuildKit, Caching and Multi-stage Builds

- Chapter: [book/volumes/06-docker-in-practice/054-buildkit-caching-and-multi-stage-builds.md](book/volumes/06-docker-in-practice/054-buildkit-caching-and-multi-stage-builds.md). Prerequisite: Chapter 53; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Cache invalidation and dependency ordering; Build secrets and multi-stage boundaries; Reducing rebuild time and image size.
- Outcome: explain and apply buildkit, caching and multi-stage builds, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make reducing rebuild time and image size concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 055. Docker Networking

- Chapter: [book/volumes/06-docker-in-practice/055-docker-networking.md](book/volumes/06-docker-in-practice/055-docker-networking.md). Prerequisite: Chapter 54; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Bridge, host and user-defined networks; Service naming and published ports; Debugging communication between containers.
- Outcome: explain and apply docker networking, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make debugging communication between containers concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 056. Docker Volumes and Persistent Data

- Chapter: [book/volumes/06-docker-in-practice/056-docker-volumes-and-persistent-data.md](book/volumes/06-docker-in-practice/056-docker-volumes-and-persistent-data.md). Prerequisite: Chapter 55; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Volumes, bind mounts and ownership; Backup and database consistency; Surviving container replacement.
- Outcome: explain and apply docker volumes and persistent data, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make surviving container replacement concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 057. Docker Compose for Multi-service Applications

- Chapter: [book/volumes/06-docker-in-practice/057-docker-compose-for-multi-service-applications.md](book/volumes/06-docker-in-practice/057-docker-compose-for-multi-service-applications.md). Prerequisite: Chapter 56; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Services, networks and configuration; Dependencies and readiness; An API, worker, PostgreSQL and Redis stack.
- Outcome: explain and apply docker compose for multi-service applications, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make an api, worker, postgresql and redis stack concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 058. Inspecting and Debugging Docker

- Chapter: [book/volumes/06-docker-in-practice/058-inspecting-and-debugging-docker.md](book/volumes/06-docker-in-practice/058-inspecting-and-debugging-docker.md). Prerequisite: Chapter 57; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: logs, exec, inspect, stats and events; Host and container evidence correlation; Diagnosing a crashing application.
- Outcome: explain and apply inspecting and debugging docker, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing a crashing application concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 059. Publishing and Promoting Images

- Chapter: [book/volumes/06-docker-in-practice/059-publishing-and-promoting-images.md](book/volumes/06-docker-in-practice/059-publishing-and-promoting-images.md). Prerequisite: Chapter 58; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Registry login, tagging and digest identity; Build once and promote; Releasing a versioned service.
- Outcome: explain and apply publishing and promoting images, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make releasing a versioned service concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 060. Docker Production Operations

- Chapter: [book/volumes/06-docker-in-practice/060-docker-production-operations.md](book/volumes/06-docker-in-practice/060-docker-production-operations.md). Prerequisite: Chapter 59; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Daemon maintenance and log rotation; Health, resource limits and recovery; A production deployment review.
- Outcome: explain and apply docker production operations, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a production deployment review concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 7 — Podman and the Rootless Host

### 061. Installing and Understanding Podman

- Chapter: [book/volumes/07-podman-and-the-rootless-host/061-installing-and-understanding-podman.md](book/volumes/07-podman-and-the-rootless-host/061-installing-and-understanding-podman.md). Prerequisite: Chapter 60; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Installation and version inspection; Local and remote execution; Comparing daemonless operation with Docker.
- Outcome: explain and apply installing and understanding podman, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make comparing daemonless operation with docker concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 062. The Podman Container Lifecycle

- Chapter: [book/volumes/07-podman-and-the-rootless-host/062-the-podman-container-lifecycle.md](book/volumes/07-podman-and-the-rootless-host/062-the-podman-container-lifecycle.md). Prerequisite: Chapter 61; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: run, inspect, exec, logs and cleanup; Rootless versus rootful state; Operating an HTTP service.
- Outcome: explain and apply the podman container lifecycle, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make operating an http service concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 063. Rootless Identity and Volume Ownership

- Chapter: [book/volumes/07-podman-and-the-rootless-host/063-rootless-identity-and-volume-ownership.md](book/volumes/07-podman-and-the-rootless-host/063-rootless-identity-and-volume-ownership.md). Prerequisite: Chapter 62; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Subordinate IDs and mappings; keep-id, unshare and file ownership; Repairing persistent-volume access.
- Outcome: explain and apply rootless identity and volume ownership, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make repairing persistent-volume access concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 064. Podman Networking and Ports

- Chapter: [book/volumes/07-podman-and-the-rootless-host/064-podman-networking-and-ports.md](book/volumes/07-podman-and-the-rootless-host/064-podman-networking-and-ports.md). Prerequisite: Chapter 63; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Network backends and rootless forwarding; Name resolution and port reachability; Diagnosing a network mismatch.
- Outcome: explain and apply podman networking and ports, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing a network mismatch concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 065. Podman Pods and Kubernetes YAML

- Chapter: [book/volumes/07-podman-and-the-rootless-host/065-podman-pods-and-kubernetes-yaml.md](book/volumes/07-podman-and-the-rootless-host/065-podman-pods-and-kubernetes-yaml.md). Prerequisite: Chapter 64; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Shared namespaces and pod membership; generate kube and play kube boundaries; Moving a small pod between environments.
- Outcome: explain and apply podman pods and kubernetes yaml, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make moving a small pod between environments concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 066. Quadlet and Systemd Integration

- Chapter: [book/volumes/07-podman-and-the-rootless-host/066-quadlet-and-systemd-integration.md](book/volumes/07-podman-and-the-rootless-host/066-quadlet-and-systemd-integration.md). Prerequisite: Chapter 65; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Declarative units and generated services; User services, lingering and startup; Running a durable rootless service.
- Outcome: explain and apply quadlet and systemd integration, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make running a durable rootless service concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 067. SELinux and Container Mounts

- Chapter: [book/volumes/07-podman-and-the-rootless-host/067-selinux-and-container-mounts.md](book/volumes/07-podman-and-the-rootless-host/067-selinux-and-container-mounts.md). Prerequisite: Chapter 66; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Labels, shared and private relabeling; Diagnosing AVC denials; Fixing mounts without disabling policy.
- Outcome: explain and apply selinux and container mounts, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make fixing mounts without disabling policy concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 068. Buildah and Skopeo Workflows

- Chapter: [book/volumes/07-podman-and-the-rootless-host/068-buildah-and-skopeo-workflows.md](book/volumes/07-podman-and-the-rootless-host/068-buildah-and-skopeo-workflows.md). Prerequisite: Chapter 67; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Building OCI images with Buildah; Inspecting and copying images with Skopeo; A registry-independent image workflow.
- Outcome: explain and apply buildah and skopeo workflows, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a registry-independent image workflow concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 069. Migrating Docker Workflows to Podman

- Chapter: [book/volumes/07-podman-and-the-rootless-host/069-migrating-docker-workflows-to-podman.md](book/volumes/07-podman-and-the-rootless-host/069-migrating-docker-workflows-to-podman.md). Prerequisite: Chapter 68; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Compatible commands and behavioral differences; Compose providers and socket compatibility; A measured migration checklist.
- Outcome: explain and apply migrating docker workflows to podman, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a measured migration checklist concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 070. Podman Host Operations and Incidents

- Chapter: [book/volumes/07-podman-and-the-rootless-host/070-podman-host-operations-and-incidents.md](book/volumes/07-podman-and-the-rootless-host/070-podman-host-operations-and-incidents.md). Prerequisite: Chapter 69; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Storage, upgrades and resource pressure; Service recovery and registry failures; Operating a fleet of rootless hosts.
- Outcome: explain and apply podman host operations and incidents, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make operating a fleet of rootless hosts concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 8 — Infrastructure as Code

### 071. Declarative Infrastructure and Reconciliation

- Chapter: [book/volumes/08-infrastructure-as-code/071-declarative-infrastructure-and-reconciliation.md](book/volumes/08-infrastructure-as-code/071-declarative-infrastructure-and-reconciliation.md). Prerequisite: Chapter 70; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Desired state and dependency graphs; Idempotency and ownership; Comparing scripts with declarative tools.
- Outcome: explain and apply declarative infrastructure and reconciliation, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make comparing scripts with declarative tools concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 072. Terraform and OpenTofu CLI Foundations

- Chapter: [book/volumes/08-infrastructure-as-code/072-terraform-and-opentofu-cli-foundations.md](book/volumes/08-infrastructure-as-code/072-terraform-and-opentofu-cli-foundations.md). Prerequisite: Chapter 71; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Providers, resources and variables; init, validate, plan and apply; A reviewed infrastructure change.
- Outcome: explain and apply terraform and opentofu cli foundations, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a reviewed infrastructure change concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 073. State, Locking and Remote Backends

- Chapter: [book/volumes/08-infrastructure-as-code/073-state-locking-and-remote-backends.md](book/volumes/08-infrastructure-as-code/073-state-locking-and-remote-backends.md). Prerequisite: Chapter 72; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Resource identity and state sensitivity; Remote state and concurrent changes; Recovering a failed state operation.
- Outcome: explain and apply state, locking and remote backends, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make recovering a failed state operation concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 074. Modules and Infrastructure Boundaries

- Chapter: [book/volumes/08-infrastructure-as-code/074-modules-and-infrastructure-boundaries.md](book/volumes/08-infrastructure-as-code/074-modules-and-infrastructure-boundaries.md). Prerequisite: Chapter 73; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Inputs, outputs and composition; Environment and ownership boundaries; Designing a reusable network module.
- Outcome: explain and apply modules and infrastructure boundaries, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make designing a reusable network module concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 075. Import, Drift and Safe Refactoring

- Chapter: [book/volumes/08-infrastructure-as-code/075-import-drift-and-safe-refactoring.md](book/volumes/08-infrastructure-as-code/075-import-drift-and-safe-refactoring.md). Prerequisite: Chapter 74; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Discovery and import workflows; Address changes and replacement risk; Adopting existing infrastructure safely.
- Outcome: explain and apply import, drift and safe refactoring, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make adopting existing infrastructure safely concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 076. Testing and Policy for Infrastructure

- Chapter: [book/volumes/08-infrastructure-as-code/076-testing-and-policy-for-infrastructure.md](book/volumes/08-infrastructure-as-code/076-testing-and-policy-for-infrastructure.md). Prerequisite: Chapter 75; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Validation, plans and integration checks; Policy gates and change review; Checking an infrastructure pull request.
- Outcome: explain and apply testing and policy for infrastructure, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make checking an infrastructure pull request concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 077. Ansible Inventory and Playbooks

- Chapter: [book/volumes/08-infrastructure-as-code/077-ansible-inventory-and-playbooks.md](book/volumes/08-infrastructure-as-code/077-ansible-inventory-and-playbooks.md). Prerequisite: Chapter 76; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Inventory, modules and tasks; Privilege, handlers and idempotency; Configuring Ubuntu and Fedora/RHEL hosts.
- Outcome: explain and apply ansible inventory and playbooks, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make configuring ubuntu and fedora/rhel hosts concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 078. Ansible Roles and Secret Handling

- Chapter: [book/volumes/08-infrastructure-as-code/078-ansible-roles-and-secret-handling.md](book/volumes/08-infrastructure-as-code/078-ansible-roles-and-secret-handling.md). Prerequisite: Chapter 77; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Reusable roles and collections; Vault and external secret references; Operating a multi-host deployment.
- Outcome: explain and apply ansible roles and secret handling, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make operating a multi-host deployment concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 079. Cloud-init and CloudFormation

- Chapter: [book/volumes/08-infrastructure-as-code/079-cloud-init-and-cloudformation.md](book/volumes/08-infrastructure-as-code/079-cloud-init-and-cloudformation.md). Prerequisite: Chapter 78; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: First-boot configuration and image boundaries; AWS stacks, change sets and drift; Choosing the right provisioning layer.
- Outcome: explain and apply cloud-init and cloudformation, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing the right provisioning layer concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 080. Infrastructure Lifecycle and Disaster Recovery

- Chapter: [book/volumes/08-infrastructure-as-code/080-infrastructure-lifecycle-and-disaster-recovery.md](book/volumes/08-infrastructure-as-code/080-infrastructure-lifecycle-and-disaster-recovery.md). Prerequisite: Chapter 79; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Bootstrap dependencies and break-glass access; State recovery and teardown; Rebuilding a lost environment.
- Outcome: explain and apply infrastructure lifecycle and disaster recovery, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make rebuilding a lost environment concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 9 — AWS Foundations

### 081. AWS Accounts, Regions and Responsibility

- Chapter: [book/volumes/09-aws-foundations/081-aws-accounts-regions-and-responsibility.md](book/volumes/09-aws-foundations/081-aws-accounts-regions-and-responsibility.md). Prerequisite: Chapter 80; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Accounts, organizations and environments; Regions, zones and service boundaries; A usable account layout.
- Outcome: explain and apply aws accounts, regions and responsibility, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a usable account layout concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 082. AWS CLI and Identity Sessions

- Chapter: [book/volumes/09-aws-foundations/082-aws-cli-and-identity-sessions.md](book/volumes/09-aws-foundations/082-aws-cli-and-identity-sessions.md). Prerequisite: Chapter 81; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Profiles, regions and output formats; SSO, role sessions and credential precedence; Verifying identity before a command.
- Outcome: explain and apply aws cli and identity sessions, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make verifying identity before a command concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 083. IAM Policies and Least Privilege

- Chapter: [book/volumes/09-aws-foundations/083-iam-policies-and-least-privilege.md](book/volumes/09-aws-foundations/083-iam-policies-and-least-privilege.md). Prerequisite: Chapter 82; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Actions, resources and conditions; Role trust and permission evaluation; Debugging an access-denied response.
- Outcome: explain and apply iam policies and least privilege, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make debugging an access-denied response concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 084. VPC, Subnets and Routes

- Chapter: [book/volumes/09-aws-foundations/084-vpc-subnets-and-routes.md](book/volumes/09-aws-foundations/084-vpc-subnets-and-routes.md). Prerequisite: Chapter 83; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Address design and routing; Internet access, NAT and endpoints; Tracing traffic through an AWS network.
- Outcome: explain and apply vpc, subnets and routes, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make tracing traffic through an aws network concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 085. Security Groups and Network ACLs

- Chapter: [book/volumes/09-aws-foundations/085-security-groups-and-network-acls.md](book/volumes/09-aws-foundations/085-security-groups-and-network-acls.md). Prerequisite: Chapter 84; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Stateful and stateless boundaries; Ingress, egress and service exposure; A private database connectivity investigation.
- Outcome: explain and apply security groups and network acls, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a private database connectivity investigation concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 086. EC2 and Instance Lifecycle

- Chapter: [book/volumes/09-aws-foundations/086-ec2-and-instance-lifecycle.md](book/volumes/09-aws-foundations/086-ec2-and-instance-lifecycle.md). Prerequisite: Chapter 85; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Images, instance types and metadata; SSH, Systems Manager and instance profiles; Provisioning and replacing a server.
- Outcome: explain and apply ec2 and instance lifecycle, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make provisioning and replacing a server concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 087. EBS and Cloud Storage Choices

- Chapter: [book/volumes/09-aws-foundations/087-ebs-and-cloud-storage-choices.md](book/volumes/09-aws-foundations/087-ebs-and-cloud-storage-choices.md). Prerequisite: Chapter 86; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Block, file and object semantics; Snapshots, performance and encryption; Choosing storage for an application.
- Outcome: explain and apply ebs and cloud storage choices, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing storage for an application concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 088. S3 from the CLI

- Chapter: [book/volumes/09-aws-foundations/088-s3-from-the-cli.md](book/volumes/09-aws-foundations/088-s3-from-the-cli.md). Prerequisite: Chapter 87; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Buckets, objects and access controls; Versioning, lifecycle and multipart upload; Operating an upload and retention workflow.
- Outcome: explain and apply s3 from the cli, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make operating an upload and retention workflow concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 089. Route 53, Certificates and Load Balancers

- Chapter: [book/volumes/09-aws-foundations/089-route-53-certificates-and-load-balancers.md](book/volumes/09-aws-foundations/089-route-53-certificates-and-load-balancers.md). Prerequisite: Chapter 88; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: DNS records and routing policies; ACM and load-balancer integration; Publishing a secure endpoint.
- Outcome: explain and apply route 53, certificates and load balancers, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make publishing a secure endpoint concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 090. AWS Budgets, Tags and Inventory

- Chapter: [book/volumes/09-aws-foundations/090-aws-budgets-tags-and-inventory.md](book/volumes/09-aws-foundations/090-aws-budgets-tags-and-inventory.md). Prerequisite: Chapter 89; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Ownership and allocation tags; Budgets, quotas and billing evidence; Finding forgotten resources before cleanup.
- Outcome: explain and apply aws budgets, tags and inventory, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make finding forgotten resources before cleanup concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 10 — AWS Production Services

### 091. EC2 Auto Scaling and Launch Templates

- Chapter: [book/volumes/10-aws-production-services/091-ec2-auto-scaling-and-launch-templates.md](book/volumes/10-aws-production-services/091-ec2-auto-scaling-and-launch-templates.md). Prerequisite: Chapter 90; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Immutable launches and capacity policy; Health, draining and replacement; Scaling a host-based service.
- Outcome: explain and apply ec2 auto scaling and launch templates, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make scaling a host-based service concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 092. ECR and Container Artifact Promotion

- Chapter: [book/volumes/10-aws-production-services/092-ecr-and-container-artifact-promotion.md](book/volumes/10-aws-production-services/092-ecr-and-container-artifact-promotion.md). Prerequisite: Chapter 91; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Repository permissions and image identity; Scanning, retention and cross-account access; Publishing a release by digest.
- Outcome: explain and apply ecr and container artifact promotion, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make publishing a release by digest concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 093. ECS and Fargate Services

- Chapter: [book/volumes/10-aws-production-services/093-ecs-and-fargate-services.md](book/volumes/10-aws-production-services/093-ecs-and-fargate-services.md). Prerequisite: Chapter 92; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Tasks, services and capacity; Networking, IAM and deployment health; Deploying an API and background worker.
- Outcome: explain and apply ecs and fargate services, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make deploying an api and background worker concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 094. EKS and AWS Integration

- Chapter: [book/volumes/10-aws-production-services/094-eks-and-aws-integration.md](book/volumes/10-aws-production-services/094-eks-and-aws-integration.md). Prerequisite: Chapter 93; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Managed control plane and worker ownership; Identity, networking and storage integrations; An EKS operational responsibility map.
- Outcome: explain and apply eks and aws integration, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make an eks operational responsibility map concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 095. RDS and Managed Database Operations

- Chapter: [book/volumes/10-aws-production-services/095-rds-and-managed-database-operations.md](book/volumes/10-aws-production-services/095-rds-and-managed-database-operations.md). Prerequisite: Chapter 94; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Availability, maintenance and connections; Backups, replicas and recovery; Diagnosing database saturation.
- Outcome: explain and apply rds and managed database operations, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing database saturation concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 096. ElastiCache and Managed Caching

- Chapter: [book/volumes/10-aws-production-services/096-elasticache-and-managed-caching.md](book/volumes/10-aws-production-services/096-elasticache-and-managed-caching.md). Prerequisite: Chapter 95; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Cache authority and eviction; Failover, connections and access; Designing for a cache outage.
- Outcome: explain and apply elasticache and managed caching, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make designing for a cache outage concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 097. SQS, SNS and EventBridge

- Chapter: [book/volumes/10-aws-production-services/097-sqs-sns-and-eventbridge.md](book/volumes/10-aws-production-services/097-sqs-sns-and-eventbridge.md). Prerequisite: Chapter 96; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Queue, fanout and routing semantics; Visibility, retries and dead letters; Operating a notification pipeline.
- Outcome: explain and apply sqs, sns and eventbridge, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make operating a notification pipeline concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 098. Lambda and Serverless Tradeoffs

- Chapter: [book/volumes/10-aws-production-services/098-lambda-and-serverless-tradeoffs.md](book/volumes/10-aws-production-services/098-lambda-and-serverless-tradeoffs.md). Prerequisite: Chapter 97; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Execution lifecycle and concurrency; Retries, packaging and observability; Choosing a small event-driven task.
- Outcome: explain and apply lambda and serverless tradeoffs, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing a small event-driven task concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 099. CloudFront and Edge Delivery

- Chapter: [book/volumes/10-aws-production-services/099-cloudfront-and-edge-delivery.md](book/volumes/10-aws-production-services/099-cloudfront-and-edge-delivery.md). Prerequisite: Chapter 98; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Origins, caching and invalidation; Headers, authorization and dynamic content; Reducing origin load without stale-data surprises.
- Outcome: explain and apply cloudfront and edge delivery, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make reducing origin load without stale-data surprises concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 100. Secrets, CloudWatch and Cloud Resilience

- Chapter: [book/volumes/10-aws-production-services/100-secrets-cloudwatch-and-cloud-resilience.md](book/volumes/10-aws-production-services/100-secrets-cloudwatch-and-cloud-resilience.md). Prerequisite: Chapter 99; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: KMS, Secrets Manager and rotation; Logs, metrics and managed alarms; A multi-zone recovery and cost review.
- Outcome: explain and apply secrets, cloudwatch and cloud resilience, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a multi-zone recovery and cost review concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 11 — Kubernetes Foundations

### 101. Kubernetes Architecture and Reconciliation

- Chapter: [book/volumes/11-kubernetes-foundations/101-kubernetes-architecture-and-reconciliation.md](book/volumes/11-kubernetes-foundations/101-kubernetes-architecture-and-reconciliation.md). Prerequisite: Chapter 100; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: API server, controllers and etcd; Nodes, kubelet and container runtime; Following a desired-state change.
- Outcome: explain and apply kubernetes architecture and reconciliation, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make following a desired-state change concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 102. Local Clusters and kubectl Contexts

- Chapter: [book/volumes/11-kubernetes-foundations/102-local-clusters-and-kubectl-contexts.md](book/volumes/11-kubernetes-foundations/102-local-clusters-and-kubectl-contexts.md). Prerequisite: Chapter 101; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: kind, minikube and environment prerequisites; Contexts, namespaces and access; Avoiding a command against the wrong cluster.
- Outcome: explain and apply local clusters and kubectl contexts, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make avoiding a command against the wrong cluster concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 103. Pods and Application Lifecycles

- Chapter: [book/volumes/11-kubernetes-foundations/103-pods-and-application-lifecycles.md](book/volumes/11-kubernetes-foundations/103-pods-and-application-lifecycles.md). Prerequisite: Chapter 102; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Pod identity and container restart; Init containers and lifecycle hooks; Deploying and inspecting a small service.
- Outcome: explain and apply pods and application lifecycles, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make deploying and inspecting a small service concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 104. Deployments, ReplicaSets and Jobs

- Chapter: [book/volumes/11-kubernetes-foundations/104-deployments-replicasets-and-jobs.md](book/volumes/11-kubernetes-foundations/104-deployments-replicasets-and-jobs.md). Prerequisite: Chapter 103; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Controllers and ownership; Rollouts, Jobs and CronJobs; Choosing a workload controller.
- Outcome: explain and apply deployments, replicasets and jobs, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing a workload controller concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 105. Services and Cluster DNS

- Chapter: [book/volumes/11-kubernetes-foundations/105-services-and-cluster-dns.md](book/volumes/11-kubernetes-foundations/105-services-and-cluster-dns.md). Prerequisite: Chapter 104; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Selectors, endpoints and virtual addresses; Discovery and connection paths; Debugging a Service with no working backend.
- Outcome: explain and apply services and cluster dns, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make debugging a service with no working backend concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 106. ConfigMaps, Secrets and Configuration

- Chapter: [book/volumes/11-kubernetes-foundations/106-configmaps-secrets-and-configuration.md](book/volumes/11-kubernetes-foundations/106-configmaps-secrets-and-configuration.md). Prerequisite: Chapter 105; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Configuration injection and updates; Secret boundaries and application reload; Changing configuration predictably.
- Outcome: explain and apply configmaps, secrets and configuration, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make changing configuration predictably concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 107. Probes and Graceful Termination

- Chapter: [book/volumes/11-kubernetes-foundations/107-probes-and-graceful-termination.md](book/volumes/11-kubernetes-foundations/107-probes-and-graceful-termination.md). Prerequisite: Chapter 106; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Startup, readiness and liveness; Termination and traffic draining; Preventing probe-driven restart loops.
- Outcome: explain and apply probes and graceful termination, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make preventing probe-driven restart loops concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 108. Resource Requests, Limits and Scheduling

- Chapter: [book/volumes/11-kubernetes-foundations/108-resource-requests-limits-and-scheduling.md](book/volumes/11-kubernetes-foundations/108-resource-requests-limits-and-scheduling.md). Prerequisite: Chapter 107; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Scheduling and runtime enforcement; CPU throttling and memory exhaustion; Right-sizing a workload from evidence.
- Outcome: explain and apply resource requests, limits and scheduling, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make right-sizing a workload from evidence concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 109. Persistent Volumes and Stateful Workloads

- Chapter: [book/volumes/11-kubernetes-foundations/109-persistent-volumes-and-stateful-workloads.md](book/volumes/11-kubernetes-foundations/109-persistent-volumes-and-stateful-workloads.md). Prerequisite: Chapter 108; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Claims, classes and binding; StatefulSets and storage lifecycle; Replacing a Pod without losing data.
- Outcome: explain and apply persistent volumes and stateful workloads, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make replacing a pod without losing data concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 110. kubectl Diagnostics and API Objects

- Chapter: [book/volumes/11-kubernetes-foundations/110-kubectl-diagnostics-and-api-objects.md](book/volumes/11-kubernetes-foundations/110-kubectl-diagnostics-and-api-objects.md). Prerequisite: Chapter 109; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: get, describe, logs, exec and events; Object fields, labels and selectors; A first Kubernetes incident investigation.
- Outcome: explain and apply kubectl diagnostics and api objects, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a first kubernetes incident investigation concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 12 — Kubernetes Production Engineering

### 111. Cluster Provisioning and Ownership

- Chapter: [book/volumes/12-kubernetes-production-engineering/111-cluster-provisioning-and-ownership.md](book/volumes/12-kubernetes-production-engineering/111-cluster-provisioning-and-ownership.md). Prerequisite: Chapter 110; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Managed and self-managed responsibilities; kubeadm, bootstrap and maintenance; A production cluster responsibility checklist.
- Outcome: explain and apply cluster provisioning and ownership, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a production cluster responsibility checklist concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 112. Cluster Networking and CNI

- Chapter: [book/volumes/12-kubernetes-production-engineering/112-cluster-networking-and-cni.md](book/volumes/12-kubernetes-production-engineering/112-cluster-networking-and-cni.md). Prerequisite: Chapter 111; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Pod routing and network implementation; Network policies and reachability; Diagnosing cross-node packet paths.
- Outcome: explain and apply cluster networking and cni, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing cross-node packet paths concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 113. Ingress and Gateway API

- Chapter: [book/volumes/12-kubernetes-production-engineering/113-ingress-and-gateway-api.md](book/volumes/12-kubernetes-production-engineering/113-ingress-and-gateway-api.md). Prerequisite: Chapter 112; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: HTTP routing and controller ownership; TLS, ingress classes and Gateway resources; Publishing services with a supported controller.
- Outcome: explain and apply ingress and gateway api, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make publishing services with a supported controller concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 114. CSI and Production Storage

- Chapter: [book/volumes/12-kubernetes-production-engineering/114-csi-and-production-storage.md](book/volumes/12-kubernetes-production-engineering/114-csi-and-production-storage.md). Prerequisite: Chapter 113; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Drivers, snapshots and topology; Access modes, recovery and expansion; Diagnosing a volume that will not attach.
- Outcome: explain and apply csi and production storage, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing a volume that will not attach concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 115. RBAC and Workload Identity

- Chapter: [book/volumes/12-kubernetes-production-engineering/115-rbac-and-workload-identity.md](book/volumes/12-kubernetes-production-engineering/115-rbac-and-workload-identity.md). Prerequisite: Chapter 114; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Subjects, roles and bindings; Service accounts and external identity; Reducing deployment credentials.
- Outcome: explain and apply rbac and workload identity, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make reducing deployment credentials concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 116. Placement, Disruption and Availability

- Chapter: [book/volumes/12-kubernetes-production-engineering/116-placement-disruption-and-availability.md](book/volumes/12-kubernetes-production-engineering/116-placement-disruption-and-availability.md). Prerequisite: Chapter 115; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Affinity, taints and topology spreading; Disruption budgets and maintenance; Draining nodes without false availability claims.
- Outcome: explain and apply placement, disruption and availability, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make draining nodes without false availability claims concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 117. Horizontal, Vertical and Node Autoscaling

- Chapter: [book/volumes/12-kubernetes-production-engineering/117-horizontal-vertical-and-node-autoscaling.md](book/volumes/12-kubernetes-production-engineering/117-horizontal-vertical-and-node-autoscaling.md). Prerequisite: Chapter 116; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Metrics, feedback and scaling boundaries; HPA, VPA and node capacity; Diagnosing oscillation and unschedulable Pods.
- Outcome: explain and apply horizontal, vertical and node autoscaling, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing oscillation and unschedulable pods concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 118. Helm and Kustomize

- Chapter: [book/volumes/12-kubernetes-production-engineering/118-helm-and-kustomize.md](book/volumes/12-kubernetes-production-engineering/118-helm-and-kustomize.md). Prerequisite: Chapter 117; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Packages, templates and overlays; Values, rendered manifests and release state; Reviewing deployment customization.
- Outcome: explain and apply helm and kustomize, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make reviewing deployment customization concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 119. Operators and Admission Policy

- Chapter: [book/volumes/12-kubernetes-production-engineering/119-operators-and-admission-policy.md](book/volumes/12-kubernetes-production-engineering/119-operators-and-admission-policy.md). Prerequisite: Chapter 118; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Custom resources and controller contracts; Admission, policy and lifecycle ownership; Deciding whether an operator is justified.
- Outcome: explain and apply operators and admission policy, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make deciding whether an operator is justified concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 120. Upgrades, etcd and Cluster Recovery

- Chapter: [book/volumes/12-kubernetes-production-engineering/120-upgrades-etcd-and-cluster-recovery.md](book/volumes/12-kubernetes-production-engineering/120-upgrades-etcd-and-cluster-recovery.md). Prerequisite: Chapter 119; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Version skew and staged upgrades; Control-plane backup and recovery; A failed-upgrade and restore scenario.
- Outcome: explain and apply upgrades, etcd and cluster recovery, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a failed-upgrade and restore scenario concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 13 — Continuous Integration Platforms

### 121. CI Architecture and Trust Boundaries

- Chapter: [book/volumes/13-continuous-integration-platforms/121-ci-architecture-and-trust-boundaries.md](book/volumes/13-continuous-integration-platforms/121-ci-architecture-and-trust-boundaries.md). Prerequisite: Chapter 120; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Events, workers and pipeline graphs; Untrusted code and credential exposure; Designing an artifact-producing pipeline.
- Outcome: explain and apply ci architecture and trust boundaries, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make designing an artifact-producing pipeline concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 122. GitHub Actions Workflows

- Chapter: [book/volumes/13-continuous-integration-platforms/122-github-actions-workflows.md](book/volumes/13-continuous-integration-platforms/122-github-actions-workflows.md). Prerequisite: Chapter 121; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Events, jobs, steps and expressions; Reusable workflows and matrices; A multi-language test workflow.
- Outcome: explain and apply github actions workflows, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a multi-language test workflow concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 123. GitHub Actions Runners and Security

- Chapter: [book/volumes/13-continuous-integration-platforms/123-github-actions-runners-and-security.md](book/volumes/13-continuous-integration-platforms/123-github-actions-runners-and-security.md). Prerequisite: Chapter 122; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Hosted and self-hosted execution; Permissions, OIDC and action pinning; Hardening a deployment workflow.
- Outcome: explain and apply github actions runners and security, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make hardening a deployment workflow concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 124. GitLab CI Pipeline Design

- Chapter: [book/volumes/13-continuous-integration-platforms/124-gitlab-ci-pipeline-design.md](book/volumes/13-continuous-integration-platforms/124-gitlab-ci-pipeline-design.md). Prerequisite: Chapter 123; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Stages, jobs, rules and includes; Artifacts, dependencies and environments; A merge-request and release pipeline.
- Outcome: explain and apply gitlab ci pipeline design, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a merge-request and release pipeline concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 125. GitLab Runners and Credentials

- Chapter: [book/volumes/13-continuous-integration-platforms/125-gitlab-runners-and-credentials.md](book/volumes/13-continuous-integration-platforms/125-gitlab-runners-and-credentials.md). Prerequisite: Chapter 124; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Executor choices and runner isolation; Protected variables and federated identity; Operating runners without cross-job leakage.
- Outcome: explain and apply gitlab runners and credentials, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make operating runners without cross-job leakage concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 126. Jenkins Controllers and Agents

- Chapter: [book/volumes/13-continuous-integration-platforms/126-jenkins-controllers-and-agents.md](book/volumes/13-continuous-integration-platforms/126-jenkins-controllers-and-agents.md). Prerequisite: Chapter 125; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Controller duties and agent execution; Plugins, credentials and lifecycle; Installing and securing a Jenkins service.
- Outcome: explain and apply jenkins controllers and agents, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make installing and securing a jenkins service concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 127. Jenkins Declarative Pipelines

- Chapter: [book/volumes/13-continuous-integration-platforms/127-jenkins-declarative-pipelines.md](book/volumes/13-continuous-integration-platforms/127-jenkins-declarative-pipelines.md). Prerequisite: Chapter 126; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Jenkinsfile, stages and post actions; Shared libraries and controlled reuse; A build, test and publish pipeline.
- Outcome: explain and apply jenkins declarative pipelines, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a build, test and publish pipeline concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 128. Tests, Quality Gates and Feedback

- Chapter: [book/volumes/13-continuous-integration-platforms/128-tests-quality-gates-and-feedback.md](book/volumes/13-continuous-integration-platforms/128-tests-quality-gates-and-feedback.md). Prerequisite: Chapter 127; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Unit, integration and contract boundaries; Security scans and useful gates; Balancing confidence with pipeline duration.
- Outcome: explain and apply tests, quality gates and feedback, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make balancing confidence with pipeline duration concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 129. Artifacts, Caches and Build Reproducibility

- Chapter: [book/volumes/13-continuous-integration-platforms/129-artifacts-caches-and-build-reproducibility.md](book/volumes/13-continuous-integration-platforms/129-artifacts-caches-and-build-reproducibility.md). Prerequisite: Chapter 128; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Artifacts versus disposable caches; Dependency integrity and reproducible inputs; Tracking one artifact through a pipeline.
- Outcome: explain and apply artifacts, caches and build reproducibility, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make tracking one artifact through a pipeline concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 130. CI Incidents and Platform Comparison

- Chapter: [book/volumes/13-continuous-integration-platforms/130-ci-incidents-and-platform-comparison.md](book/volumes/13-continuous-integration-platforms/130-ci-incidents-and-platform-comparison.md). Prerequisite: Chapter 129; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Queueing, flaky jobs and worker pressure; GitHub, GitLab and Jenkins tradeoffs; Diagnosing a compromised or stalled pipeline.
- Outcome: explain and apply ci incidents and platform comparison, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing a compromised or stalled pipeline concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 14 — Delivery, Deployment and GitOps

### 131. Release Engineering and Artifact Promotion

- Chapter: [book/volumes/14-delivery-deployment-and-gitops/131-release-engineering-and-artifact-promotion.md](book/volumes/14-delivery-deployment-and-gitops/131-release-engineering-and-artifact-promotion.md). Prerequisite: Chapter 130; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Build once and release identity; Environment gates and evidence; Promoting a tested image.
- Outcome: explain and apply release engineering and artifact promotion, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make promoting a tested image concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 132. Deployment to VPS Infrastructure

- Chapter: [book/volumes/14-delivery-deployment-and-gitops/132-deployment-to-vps-infrastructure.md](book/volumes/14-delivery-deployment-and-gitops/132-deployment-to-vps-infrastructure.md). Prerequisite: Chapter 131; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: SSH boundaries and release directories; Health checks and atomic switches; A reversible single-host deployment.
- Outcome: explain and apply deployment to vps infrastructure, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a reversible single-host deployment concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 133. Container Deployment to AWS

- Chapter: [book/volumes/14-delivery-deployment-and-gitops/133-container-deployment-to-aws.md](book/volumes/14-delivery-deployment-and-gitops/133-container-deployment-to-aws.md). Prerequisite: Chapter 132; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: ECS task revisions and service updates; EKS manifests and release evidence; A staged cloud deployment.
- Outcome: explain and apply container deployment to aws, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a staged cloud deployment concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 134. Rolling Updates and Blue Green

- Chapter: [book/volumes/14-delivery-deployment-and-gitops/134-rolling-updates-and-blue-green.md](book/volumes/14-delivery-deployment-and-gitops/134-rolling-updates-and-blue-green.md). Prerequisite: Chapter 133; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Mixed versions and traffic switching; Capacity headroom and session state; Choosing a release strategy.
- Outcome: explain and apply rolling updates and blue green, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing a release strategy concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 135. Canary Releases and Feature Flags

- Chapter: [book/volumes/14-delivery-deployment-and-gitops/135-canary-releases-and-feature-flags.md](book/volumes/14-delivery-deployment-and-gitops/135-canary-releases-and-feature-flags.md). Prerequisite: Chapter 134; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Cohorts, metrics and decision windows; Flag lifecycle and rollback control; Stopping a harmful release early.
- Outcome: explain and apply canary releases and feature flags, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make stopping a harmful release early concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 136. Database and Message Compatibility

- Chapter: [book/volumes/14-delivery-deployment-and-gitops/136-database-and-message-compatibility.md](book/volumes/14-delivery-deployment-and-gitops/136-database-and-message-compatibility.md). Prerequisite: Chapter 135; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Expand-and-contract schema changes; Backfills and mixed-version messages; Releasing without breaking old workers.
- Outcome: explain and apply database and message compatibility, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make releasing without breaking old workers concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 137. GitOps Principles and Reconciliation

- Chapter: [book/volumes/14-delivery-deployment-and-gitops/137-gitops-principles-and-reconciliation.md](book/volumes/14-delivery-deployment-and-gitops/137-gitops-principles-and-reconciliation.md). Prerequisite: Chapter 136; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Git state, controllers and drift; Promotion and secret boundaries; Separating build from deployment authority.
- Outcome: explain and apply gitops principles and reconciliation, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make separating build from deployment authority concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 138. Argo CD in Practice

- Chapter: [book/volumes/14-delivery-deployment-and-gitops/138-argo-cd-in-practice.md](book/volumes/14-delivery-deployment-and-gitops/138-argo-cd-in-practice.md). Prerequisite: Chapter 137; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Applications, sync and health; Projects, permissions and rollback behavior; Operating an application through Argo CD.
- Outcome: explain and apply argo cd in practice, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make operating an application through argo cd concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 139. Flux in Practice

- Chapter: [book/volumes/14-delivery-deployment-and-gitops/139-flux-in-practice.md](book/volumes/14-delivery-deployment-and-gitops/139-flux-in-practice.md). Prerequisite: Chapter 138; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Sources, reconciliation and dependencies; Image automation and environment changes; Operating a comparable Flux deployment.
- Outcome: explain and apply flux in practice, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make operating a comparable flux deployment concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 140. Rollback, Roll Forward and Release Incidents

- Chapter: [book/volumes/14-delivery-deployment-and-gitops/140-rollback-roll-forward-and-release-incidents.md](book/volumes/14-delivery-deployment-and-gitops/140-rollback-roll-forward-and-release-incidents.md). Prerequisite: Chapter 139; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Application, data and infrastructure boundaries; Unknown completion and recovery decisions; A failed-release investigation.
- Outcome: explain and apply rollback, roll forward and release incidents, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a failed-release investigation concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 15 — Observability and Telemetry

### 141. Observability from Questions to Evidence

- Chapter: [book/volumes/15-observability-and-telemetry/141-observability-from-questions-to-evidence.md](book/volumes/15-observability-and-telemetry/141-observability-from-questions-to-evidence.md). Prerequisite: Chapter 140; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Metrics, logs, traces and profiles; User impact and service boundaries; Instrumenting a meaningful request path.
- Outcome: explain and apply observability from questions to evidence, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make instrumenting a meaningful request path concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 142. Prometheus and Exporters

- Chapter: [book/volumes/15-observability-and-telemetry/142-prometheus-and-exporters.md](book/volumes/15-observability-and-telemetry/142-prometheus-and-exporters.md). Prerequisite: Chapter 141; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Scrapes, labels and time series; Exporters, discovery and retention; Monitoring hosts and application services.
- Outcome: explain and apply prometheus and exporters, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make monitoring hosts and application services concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 143. PromQL for Operational Questions

- Chapter: [book/volumes/15-observability-and-telemetry/143-promql-for-operational-questions.md](book/volumes/15-observability-and-telemetry/143-promql-for-operational-questions.md). Prerequisite: Chapter 142; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Counters, gauges, rates and histograms; Aggregation and missing series; Investigating latency and error rates.
- Outcome: explain and apply promql for operational questions, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make investigating latency and error rates concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 144. Grafana Dashboards and Provisioning

- Chapter: [book/volumes/15-observability-and-telemetry/144-grafana-dashboards-and-provisioning.md](book/volumes/15-observability-and-telemetry/144-grafana-dashboards-and-provisioning.md). Prerequisite: Chapter 143; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Data sources, queries and panels; Variables, provisioning and access; A dashboard that supports diagnosis.
- Outcome: explain and apply grafana dashboards and provisioning, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a dashboard that supports diagnosis concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 145. Alertmanager and Actionable Alerts

- Chapter: [book/volumes/15-observability-and-telemetry/145-alertmanager-and-actionable-alerts.md](book/volumes/15-observability-and-telemetry/145-alertmanager-and-actionable-alerts.md). Prerequisite: Chapter 144; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Grouping, routing and inhibition; Ownership and alert fatigue; Paging on service impact.
- Outcome: explain and apply alertmanager and actionable alerts, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make paging on service impact concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 146. Logs with Journald and Loki

- Chapter: [book/volumes/15-observability-and-telemetry/146-logs-with-journald-and-loki.md](book/volumes/15-observability-and-telemetry/146-logs-with-journald-and-loki.md). Prerequisite: Chapter 145; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Structured events and correlation; Collection, labels and retention; Following an error across services.
- Outcome: explain and apply logs with journald and loki, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make following an error across services concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 147. OpenTelemetry Instrumentation and Collectors

- Chapter: [book/volumes/15-observability-and-telemetry/147-opentelemetry-instrumentation-and-collectors.md](book/volumes/15-observability-and-telemetry/147-opentelemetry-instrumentation-and-collectors.md). Prerequisite: Chapter 146; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Context propagation and signals; Collector pipelines and sampling; Tracing a multi-language request.
- Outcome: explain and apply opentelemetry instrumentation and collectors, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make tracing a multi-language request concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 148. Tempo, Jaeger and Trace Investigation

- Chapter: [book/volumes/15-observability-and-telemetry/148-tempo-jaeger-and-trace-investigation.md](book/volumes/15-observability-and-telemetry/148-tempo-jaeger-and-trace-investigation.md). Prerequisite: Chapter 147; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Spans, parent relationships and timing; Sampling limits and backend choices; Finding a slow downstream dependency.
- Outcome: explain and apply tempo, jaeger and trace investigation, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make finding a slow downstream dependency concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 149. Elastic, OpenSearch and CloudWatch

- Chapter: [book/volumes/15-observability-and-telemetry/149-elastic-opensearch-and-cloudwatch.md](book/volumes/15-observability-and-telemetry/149-elastic-opensearch-and-cloudwatch.md). Prerequisite: Chapter 148; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Search-oriented log workflows; Managed telemetry and query costs; Choosing a telemetry backend.
- Outcome: explain and apply elastic, opensearch and cloudwatch, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing a telemetry backend concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 150. Observability at Scale

- Chapter: [book/volumes/15-observability-and-telemetry/150-observability-at-scale.md](book/volumes/15-observability-and-telemetry/150-observability-at-scale.md). Prerequisite: Chapter 149; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Cardinality, storage and ingestion budgets; SLO dashboards and telemetry outages; A capacity review for the monitoring system.
- Outcome: explain and apply observability at scale, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a capacity review for the monitoring system concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 16 — Performance and Capacity Engineering

### 151. Workload Models and Measurement

- Chapter: [book/volumes/16-performance-and-capacity-engineering/151-workload-models-and-measurement.md](book/volumes/16-performance-and-capacity-engineering/151-workload-models-and-measurement.md). Prerequisite: Chapter 150; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Arrival rates, concurrency and service time; Percentiles and representative workloads; Writing a load-test charter.
- Outcome: explain and apply workload models and measurement, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make writing a load-test charter concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 152. CPU, Memory and Scheduler Diagnosis

- Chapter: [book/volumes/16-performance-and-capacity-engineering/152-cpu-memory-and-scheduler-diagnosis.md](book/volumes/16-performance-and-capacity-engineering/152-cpu-memory-and-scheduler-diagnosis.md). Prerequisite: Chapter 151; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Utilization, contention and pressure; Profiling and working-set evidence; Distinguishing CPU saturation from waiting.
- Outcome: explain and apply cpu, memory and scheduler diagnosis, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make distinguishing cpu saturation from waiting concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 153. Disk, Network and Connection Bottlenecks

- Chapter: [book/volumes/16-performance-and-capacity-engineering/153-disk-network-and-connection-bottlenecks.md](book/volumes/16-performance-and-capacity-engineering/153-disk-network-and-connection-bottlenecks.md). Prerequisite: Chapter 152; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Latency, bandwidth, queues and IOPS; Connection pools and file descriptors; Finding a shared resource ceiling.
- Outcome: explain and apply disk, network and connection bottlenecks, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make finding a shared resource ceiling concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 154. Load Testing with k6 and Locust

- Chapter: [book/volumes/16-performance-and-capacity-engineering/154-load-testing-with-k6-and-locust.md](book/volumes/16-performance-and-capacity-engineering/154-load-testing-with-k6-and-locust.md). Prerequisite: Chapter 153; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Open and closed workload models; Warmup, test data and correctness; A staged DispatchDesk load experiment.
- Outcome: explain and apply load testing with k6 and locust, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a staged dispatchdesk load experiment concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 155. Vertical Scaling Decisions

- Chapter: [book/volumes/16-performance-and-capacity-engineering/155-vertical-scaling-decisions.md](book/volumes/16-performance-and-capacity-engineering/155-vertical-scaling-decisions.md). Prerequisite: Chapter 154; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Headroom, larger machines and limits; Downtime, cost and diminishing returns; A measured VPS resize decision.
- Outcome: explain and apply vertical scaling decisions, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a measured vps resize decision concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 156. Horizontal Scaling Decisions

- Chapter: [book/volumes/16-performance-and-capacity-engineering/156-horizontal-scaling-decisions.md](book/volumes/16-performance-and-capacity-engineering/156-horizontal-scaling-decisions.md). Prerequisite: Chapter 155; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Stateless work and shared state; Coordination, partitioning and balancing; Adding replicas without multiplying a bottleneck.
- Outcome: explain and apply horizontal scaling decisions, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make adding replicas without multiplying a bottleneck concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 157. Autoscaling as a Feedback System

- Chapter: [book/volumes/16-performance-and-capacity-engineering/157-autoscaling-as-a-feedback-system.md](book/volumes/16-performance-and-capacity-engineering/157-autoscaling-as-a-feedback-system.md). Prerequisite: Chapter 156; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Signals, delay and stabilization; Cold starts, floors and ceilings; Preventing scaling oscillation.
- Outcome: explain and apply autoscaling as a feedback system, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make preventing scaling oscillation concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 158. Capacity Planning and Forecasting

- Chapter: [book/volumes/16-performance-and-capacity-engineering/158-capacity-planning-and-forecasting.md](book/volumes/16-performance-and-capacity-engineering/158-capacity-planning-and-forecasting.md). Prerequisite: Chapter 157; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Growth, seasonality and failure reserve; Quotas and lead times; Estimating capacity with uncertainty.
- Outcome: explain and apply capacity planning and forecasting, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make estimating capacity with uncertainty concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 159. Caching, Batching and Efficiency

- Chapter: [book/volumes/16-performance-and-capacity-engineering/159-caching-batching-and-efficiency.md](book/volumes/16-performance-and-capacity-engineering/159-caching-batching-and-efficiency.md). Prerequisite: Chapter 158; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Reuse, locality and amortized cost; Freshness and batch latency; Reducing work before adding machines.
- Outcome: explain and apply caching, batching and efficiency, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make reducing work before adding machines concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 160. Cost and Performance Tradeoffs

- Chapter: [book/volumes/16-performance-and-capacity-engineering/160-cost-and-performance-tradeoffs.md](book/volumes/16-performance-and-capacity-engineering/160-cost-and-performance-tradeoffs.md). Prerequisite: Chapter 159; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Unit economics and total ownership; Spot capacity, commitments and architecture; Comparing three scaling proposals.
- Outcome: explain and apply cost and performance tradeoffs, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make comparing three scaling proposals concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 17 — Distributed Systems and Data Operations

### 161. Partial Failure and Timeouts

- Chapter: [book/volumes/17-distributed-systems-and-data-operations/161-partial-failure-and-timeouts.md](book/volumes/17-distributed-systems-and-data-operations/161-partial-failure-and-timeouts.md). Prerequisite: Chapter 160; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Independent failure and uncertain outcomes; Timeout budgets and cancellation; Following a request that may have succeeded.
- Outcome: explain and apply partial failure and timeouts, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make following a request that may have succeeded concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 162. Retries, Idempotency and Backoff

- Chapter: [book/volumes/17-distributed-systems-and-data-operations/162-retries-idempotency-and-backoff.md](book/volumes/17-distributed-systems-and-data-operations/162-retries-idempotency-and-backoff.md). Prerequisite: Chapter 161; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Duplicate work and retry storms; Idempotency keys and jitter; A reliable worker retry contract.
- Outcome: explain and apply retries, idempotency and backoff, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a reliable worker retry contract concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 163. Queues and Backpressure

- Chapter: [book/volumes/17-distributed-systems-and-data-operations/163-queues-and-backpressure.md](book/volumes/17-distributed-systems-and-data-operations/163-queues-and-backpressure.md). Prerequisite: Chapter 162; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Producer and consumer rates; Leases, dead letters and flow control; Recovering a growing work backlog.
- Outcome: explain and apply queues and backpressure, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make recovering a growing work backlog concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 164. Database Connections and Concurrency

- Chapter: [book/volumes/17-distributed-systems-and-data-operations/164-database-connections-and-concurrency.md](book/volumes/17-distributed-systems-and-data-operations/164-database-connections-and-concurrency.md). Prerequisite: Chapter 163; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Pools, locks and transaction boundaries; Contention and isolation; Diagnosing a database-backed service.
- Outcome: explain and apply database connections and concurrency, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make diagnosing a database-backed service concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 165. Replication and Failover

- Chapter: [book/volumes/17-distributed-systems-and-data-operations/165-replication-and-failover.md](book/volumes/17-distributed-systems-and-data-operations/165-replication-and-failover.md). Prerequisite: Chapter 164; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Replication lag and durability; Leader authority and fencing; Avoiding split-brain recovery.
- Outcome: explain and apply replication and failover, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make avoiding split-brain recovery concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 166. Consistency and Consensus Concepts

- Chapter: [book/volumes/17-distributed-systems-and-data-operations/166-consistency-and-consensus-concepts.md](book/volumes/17-distributed-systems-and-data-operations/166-consistency-and-consensus-concepts.md). Prerequisite: Chapter 165; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Ordering, quorums and partitions; Consistency contracts and operational limits; Reasoning about a coordination service.
- Outcome: explain and apply consistency and consensus concepts, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make reasoning about a coordination service concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 167. Cache Design and Invalidation

- Chapter: [book/volumes/17-distributed-systems-and-data-operations/167-cache-design-and-invalidation.md](book/volumes/17-distributed-systems-and-data-operations/167-cache-design-and-invalidation.md). Prerequisite: Chapter 166; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Source of truth and derived state; Stampedes, expiration and outage behavior; A controlled cache-failure experiment.
- Outcome: explain and apply cache design and invalidation, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a controlled cache-failure experiment concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 168. Database Scaling and Partitioning

- Chapter: [book/volumes/17-distributed-systems-and-data-operations/168-database-scaling-and-partitioning.md](book/volumes/17-distributed-systems-and-data-operations/168-database-scaling-and-partitioning.md). Prerequisite: Chapter 167; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Indexes, read replicas and sharding; Hot keys and cross-partition work; Choosing a data scaling path.
- Outcome: explain and apply database scaling and partitioning, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing a data scaling path concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 169. Messaging and Event-driven Architecture

- Chapter: [book/volumes/17-distributed-systems-and-data-operations/169-messaging-and-event-driven-architecture.md](book/volumes/17-distributed-systems-and-data-operations/169-messaging-and-event-driven-architecture.md). Prerequisite: Chapter 168; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Events, commands and delivery semantics; Outbox, ordering and schema evolution; Connecting order processing to notifications.
- Outcome: explain and apply messaging and event-driven architecture, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make connecting order processing to notifications concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 170. Stateful Recovery and Data Migration

- Chapter: [book/volumes/17-distributed-systems-and-data-operations/170-stateful-recovery-and-data-migration.md](book/volumes/17-distributed-systems-and-data-operations/170-stateful-recovery-and-data-migration.md). Prerequisite: Chapter 169; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Backfill, reconciliation and authority; Cutover and recovery evidence; Migrating a live data boundary.
- Outcome: explain and apply stateful recovery and data migration, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make migrating a live data boundary concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 18 — Security and Software Supply Chains

### 171. Threat Modeling for Operators

- Chapter: [book/volumes/18-security-and-software-supply-chains/171-threat-modeling-for-operators.md](book/volumes/18-security-and-software-supply-chains/171-threat-modeling-for-operators.md). Prerequisite: Chapter 170; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Assets, identities and trust boundaries; Abuse paths and practical controls; Threat modeling DispatchDesk.
- Outcome: explain and apply threat modeling for operators, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make threat modeling dispatchdesk concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 172. Host Security and Patch Management

- Chapter: [book/volumes/18-security-and-software-supply-chains/172-host-security-and-patch-management.md](book/volumes/18-security-and-software-supply-chains/172-host-security-and-patch-management.md). Prerequisite: Chapter 171; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Access, packages and attack surface; Ubuntu and Fedora/RHEL hardening differences; A defensible host-maintenance process.
- Outcome: explain and apply host security and patch management, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a defensible host-maintenance process concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 173. Container Security in Practice

- Chapter: [book/volumes/18-security-and-software-supply-chains/173-container-security-in-practice.md](book/volumes/18-security-and-software-supply-chains/173-container-security-in-practice.md). Prerequisite: Chapter 172; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Image content and runtime privilege; Rootless operation and workload isolation; Reviewing a container security posture.
- Outcome: explain and apply container security in practice, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make reviewing a container security posture concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 174. Kubernetes Security Boundaries

- Chapter: [book/volumes/18-security-and-software-supply-chains/174-kubernetes-security-boundaries.md](book/volumes/18-security-and-software-supply-chains/174-kubernetes-security-boundaries.md). Prerequisite: Chapter 173; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: API access, workload policy and tenancy; Pod Security and network controls; A cluster threat and permissions review.
- Outcome: explain and apply kubernetes security boundaries, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a cluster threat and permissions review concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 175. Secrets and Credential Rotation

- Chapter: [book/volumes/18-security-and-software-supply-chains/175-secrets-and-credential-rotation.md](book/volumes/18-security-and-software-supply-chains/175-secrets-and-credential-rotation.md). Prerequisite: Chapter 174; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Secret distribution and lifecycle; Vault, cloud secrets and rotation; Recovering from a leaked credential.
- Outcome: explain and apply secrets and credential rotation, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make recovering from a leaked credential concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 176. Federation, OIDC and Short-lived Identity

- Chapter: [book/volumes/18-security-and-software-supply-chains/176-federation-oidc-and-short-lived-identity.md](book/volumes/18-security-and-software-supply-chains/176-federation-oidc-and-short-lived-identity.md). Prerequisite: Chapter 175; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Trust claims and audience boundaries; CI and workload federation; Replacing static cloud keys.
- Outcome: explain and apply federation, oidc and short-lived identity, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make replacing static cloud keys concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 177. Vulnerability Scanning and SBOMs

- Chapter: [book/volumes/18-security-and-software-supply-chains/177-vulnerability-scanning-and-sboms.md](book/volumes/18-security-and-software-supply-chains/177-vulnerability-scanning-and-sboms.md). Prerequisite: Chapter 176; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Package inventory and vulnerability evidence; Trivy, Grype and SBOM workflows; Prioritizing fixes by exposure and impact.
- Outcome: explain and apply vulnerability scanning and sboms, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make prioritizing fixes by exposure and impact concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 178. Artifact Signing and Provenance

- Chapter: [book/volumes/18-security-and-software-supply-chains/178-artifact-signing-and-provenance.md](book/volumes/18-security-and-software-supply-chains/178-artifact-signing-and-provenance.md). Prerequisite: Chapter 177; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Signatures, attestations and trust roots; Cosign and provenance verification; Verifying an artifact before deployment.
- Outcome: explain and apply artifact signing and provenance, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make verifying an artifact before deployment concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 179. Policy, Audit and Compliance Evidence

- Chapter: [book/volumes/18-security-and-software-supply-chains/179-policy-audit-and-compliance-evidence.md](book/volumes/18-security-and-software-supply-chains/179-policy-audit-and-compliance-evidence.md). Prerequisite: Chapter 178; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Policies as explicit controls; OPA and admission evidence; A reviewable release approval record.
- Outcome: explain and apply policy, audit and compliance evidence, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a reviewable release approval record concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 180. Security Incidents and Containment

- Chapter: [book/volumes/18-security-and-software-supply-chains/180-security-incidents-and-containment.md](book/volumes/18-security-and-software-supply-chains/180-security-incidents-and-containment.md). Prerequisite: Chapter 179; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Evidence preservation and isolation; Credential revocation and clean rebuild; A compromised-runner response.
- Outcome: explain and apply security incidents and containment, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a compromised-runner response concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 19 — Site Reliability and Recovery

### 181. SLIs, SLOs and Error Budgets

- Chapter: [book/volumes/19-site-reliability-and-recovery/181-slis-slos-and-error-budgets.md](book/volumes/19-site-reliability-and-recovery/181-slis-slos-and-error-budgets.md). Prerequisite: Chapter 180; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: User journeys and measurement windows; Targets and release decisions; Defining a useful service objective.
- Outcome: explain and apply slis, slos and error budgets, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make defining a useful service objective concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 182. On-call and Operational Readiness

- Chapter: [book/volumes/19-site-reliability-and-recovery/182-on-call-and-operational-readiness.md](book/volumes/19-site-reliability-and-recovery/182-on-call-and-operational-readiness.md). Prerequisite: Chapter 181; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Ownership, escalation and handoff; Runbooks and response authority; Preparing a team for production responsibility.
- Outcome: explain and apply on-call and operational readiness, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make preparing a team for production responsibility concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 183. Incident Command and Communication

- Chapter: [book/volumes/19-site-reliability-and-recovery/183-incident-command-and-communication.md](book/volumes/19-site-reliability-and-recovery/183-incident-command-and-communication.md). Prerequisite: Chapter 182; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Declaration, roles and updates; Stabilization and uncertainty; Running a coordinated outage response.
- Outcome: explain and apply incident command and communication, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make running a coordinated outage response concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 184. Troubleshooting Under Pressure

- Chapter: [book/volumes/19-site-reliability-and-recovery/184-troubleshooting-under-pressure.md](book/volumes/19-site-reliability-and-recovery/184-troubleshooting-under-pressure.md). Prerequisite: Chapter 183; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Hypotheses, timelines and safe experiments; Mitigation versus causal explanation; An outage investigation with incomplete evidence.
- Outcome: explain and apply troubleshooting under pressure, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make an outage investigation with incomplete evidence concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 185. Postmortems and Corrective Actions

- Chapter: [book/volumes/19-site-reliability-and-recovery/185-postmortems-and-corrective-actions.md](book/volumes/19-site-reliability-and-recovery/185-postmortems-and-corrective-actions.md). Prerequisite: Chapter 184; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Contributing factors and evidence; Action ownership and effectiveness; Turning an incident into engineering work.
- Outcome: explain and apply postmortems and corrective actions, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make turning an incident into engineering work concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 186. Backup Engineering

- Chapter: [book/volumes/19-site-reliability-and-recovery/186-backup-engineering.md](book/volumes/19-site-reliability-and-recovery/186-backup-engineering.md). Prerequisite: Chapter 185; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Consistency, retention and encryption; Independent copies and restore evidence; Testing database and object restoration.
- Outcome: explain and apply backup engineering, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make testing database and object restoration concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 187. Disaster Recovery and Failback

- Chapter: [book/volumes/19-site-reliability-and-recovery/187-disaster-recovery-and-failback.md](book/volumes/19-site-reliability-and-recovery/187-disaster-recovery-and-failback.md). Prerequisite: Chapter 186; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: RPO, RTO and dependency recovery; Failover authority and return to normal; A regional-loss recovery plan.
- Outcome: explain and apply disaster recovery and failback, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a regional-loss recovery plan concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 188. Chaos and Resilience Experiments

- Chapter: [book/volumes/19-site-reliability-and-recovery/188-chaos-and-resilience-experiments.md](book/volumes/19-site-reliability-and-recovery/188-chaos-and-resilience-experiments.md). Prerequisite: Chapter 187; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Hypotheses, blast radius and stop conditions; Fault injection and recovery evidence; A bounded service failure experiment.
- Outcome: explain and apply chaos and resilience experiments, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a bounded service failure experiment concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 189. Reliability Testing and Game Days

- Chapter: [book/volumes/19-site-reliability-and-recovery/189-reliability-testing-and-game-days.md](book/volumes/19-site-reliability-and-recovery/189-reliability-testing-and-game-days.md). Prerequisite: Chapter 188; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Load, fault and recovery combinations; Tabletop and technical exercises; A rehearsal before a major launch.
- Outcome: explain and apply reliability testing and game days, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a rehearsal before a major launch concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 190. Reducing Toil and Improving Operations

- Chapter: [book/volumes/19-site-reliability-and-recovery/190-reducing-toil-and-improving-operations.md](book/volumes/19-site-reliability-and-recovery/190-reducing-toil-and-improving-operations.md). Prerequisite: Chapter 189; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Manual work and recurring failure; Automation, guardrails and maintenance; A reliability improvement roadmap.
- Outcome: explain and apply reducing toil and improving operations, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a reliability improvement roadmap concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 20 — Architecture and Platform Engineering

### 191. Monoliths, Services and Organizational Boundaries

- Chapter: [book/volumes/20-architecture-and-platform-engineering/191-monoliths-services-and-organizational-boundaries.md](book/volumes/20-architecture-and-platform-engineering/191-monoliths-services-and-organizational-boundaries.md). Prerequisite: Chapter 190; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Deployment and ownership boundaries; Coupling and operational overhead; Choosing a service extraction.
- Outcome: explain and apply monoliths, services and organizational boundaries, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing a service extraction concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 192. Platform Teams and Developer Experience

- Chapter: [book/volumes/20-architecture-and-platform-engineering/192-platform-teams-and-developer-experience.md](book/volumes/20-architecture-and-platform-engineering/192-platform-teams-and-developer-experience.md). Prerequisite: Chapter 191; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Internal customers and product thinking; Golden paths and escape hatches; A small useful deployment platform.
- Outcome: explain and apply platform teams and developer experience, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a small useful deployment platform concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 193. Multi-tenancy and Isolation

- Chapter: [book/volumes/20-architecture-and-platform-engineering/193-multi-tenancy-and-isolation.md](book/volumes/20-architecture-and-platform-engineering/193-multi-tenancy-and-isolation.md). Prerequisite: Chapter 192; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Shared, pooled and dedicated resources; Noisy neighbors and authorization; Choosing an isolation boundary.
- Outcome: explain and apply multi-tenancy and isolation, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing an isolation boundary concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 194. Service Meshes and Traffic Policy

- Chapter: [book/volumes/20-architecture-and-platform-engineering/194-service-meshes-and-traffic-policy.md](book/volumes/20-architecture-and-platform-engineering/194-service-meshes-and-traffic-policy.md). Prerequisite: Chapter 193; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Identity, routing and telemetry; Sidecar and ambient tradeoffs; Deciding whether a mesh earns its cost.
- Outcome: explain and apply service meshes and traffic policy, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make deciding whether a mesh earns its cost concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 195. Multi-zone and Multi-region Architecture

- Chapter: [book/volumes/20-architecture-and-platform-engineering/195-multi-zone-and-multi-region-architecture.md](book/volumes/20-architecture-and-platform-engineering/195-multi-zone-and-multi-region-architecture.md). Prerequisite: Chapter 194; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Latency, authority and failure domains; Active-passive and active-active designs; A regional architecture review.
- Outcome: explain and apply multi-zone and multi-region architecture, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a regional architecture review concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 196. Hybrid and Restricted Environments

- Chapter: [book/volumes/20-architecture-and-platform-engineering/196-hybrid-and-restricted-environments.md](book/volumes/20-architecture-and-platform-engineering/196-hybrid-and-restricted-environments.md). Prerequisite: Chapter 195; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Connectivity, mirrors and artifact trust; Air-gapped updates and operational access; Operating with limited external dependencies.
- Outcome: explain and apply hybrid and restricted environments, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make operating with limited external dependencies concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 197. Legacy Infrastructure Modernization

- Chapter: [book/volumes/20-architecture-and-platform-engineering/197-legacy-infrastructure-modernization.md](book/volumes/20-architecture-and-platform-engineering/197-legacy-infrastructure-modernization.md). Prerequisite: Chapter 196; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Inventory, constraints and behavior; Incremental migration and reversibility; Replacing a fragile deployment process.
- Outcome: explain and apply legacy infrastructure modernization, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make replacing a fragile deployment process concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 198. Architecture Reviews and Decision Records

- Chapter: [book/volumes/20-architecture-and-platform-engineering/198-architecture-reviews-and-decision-records.md](book/volumes/20-architecture-and-platform-engineering/198-architecture-reviews-and-decision-records.md). Prerequisite: Chapter 197; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Requirements, alternatives and evidence; Assumptions and reversal triggers; Reviewing a production proposal.
- Outcome: explain and apply architecture reviews and decision records, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make reviewing a production proposal concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 199. FinOps and Engineering Economics

- Chapter: [book/volumes/20-architecture-and-platform-engineering/199-finops-and-engineering-economics.md](book/volumes/20-architecture-and-platform-engineering/199-finops-and-engineering-economics.md). Prerequisite: Chapter 198; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Ownership, allocation and unit cost; Forecasts and optimization evidence; Choosing between labor and cloud spend.
- Outcome: explain and apply finops and engineering economics, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make choosing between labor and cloud spend concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 200. Senior Engineering Judgment

- Chapter: [book/volumes/20-architecture-and-platform-engineering/200-senior-engineering-judgment.md](book/volumes/20-architecture-and-platform-engineering/200-senior-engineering-judgment.md). Prerequisite: Chapter 199; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Uncertainty, prioritization and communication; Simple designs and justified complexity; Mentoring through a difficult operational decision.
- Outcome: explain and apply senior engineering judgment, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make mentoring through a difficult operational decision concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 21 — Projects and Industry Case Studies

### 201. DispatchDesk on a Single VPS

- Chapter: [book/volumes/21-projects-and-industry-case-studies/201-dispatchdesk-on-a-single-vps.md](book/volumes/21-projects-and-industry-case-studies/201-dispatchdesk-on-a-single-vps.md). Prerequisite: Chapter 200; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Initial workload and operational contract; Native services and first release; A first failure and measured improvement.
- Outcome: explain and apply dispatchdesk on a single vps, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a first failure and measured improvement concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 202. The VPS Company Scales Carefully

- Chapter: [book/volumes/21-projects-and-industry-case-studies/202-the-vps-company-scales-carefully.md](book/volumes/21-projects-and-industry-case-studies/202-the-vps-company-scales-carefully.md). Prerequisite: Chapter 201; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Vertical growth and resource evidence; Second host and managed database choices; Why the team delays Kubernetes.
- Outcome: explain and apply the vps company scales carefully, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make why the team delays kubernetes concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 203. The Managed AWS Company

- Chapter: [book/volumes/21-projects-and-industry-case-studies/203-the-managed-aws-company.md](book/volumes/21-projects-and-industry-case-studies/203-the-managed-aws-company.md). Prerequisite: Chapter 202; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: ECS, queues and managed persistence; Team capacity and service boundaries; A growth-driven architecture change.
- Outcome: explain and apply the managed aws company, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a growth-driven architecture change concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 204. The Kubernetes Platform Company

- Chapter: [book/volumes/21-projects-and-industry-case-studies/204-the-kubernetes-platform-company.md](book/volumes/21-projects-and-industry-case-studies/204-the-kubernetes-platform-company.md). Prerequisite: Chapter 203; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Several teams and deployment requirements; Shared platform and workload isolation; Why Kubernetes becomes justified.
- Outcome: explain and apply the kubernetes platform company, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make why kubernetes becomes justified concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 205. Multi-language Services in Production

- Chapter: [book/volumes/21-projects-and-industry-case-studies/205-multi-language-services-in-production.md](book/volumes/21-projects-and-industry-case-studies/205-multi-language-services-in-production.md). Prerequisite: Chapter 204; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Python, PHP, Go and JavaScript lifecycles; Signals, health, concurrency and telemetry; Comparable deployment contracts across runtimes.
- Outcome: explain and apply multi-language services in production, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make comparable deployment contracts across runtimes concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 206. Three Pipelines for One Release Contract

- Chapter: [book/volumes/21-projects-and-industry-case-studies/206-three-pipelines-for-one-release-contract.md](book/volumes/21-projects-and-industry-case-studies/206-three-pipelines-for-one-release-contract.md). Prerequisite: Chapter 205; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: GitHub Actions implementation; GitLab CI and Jenkins implementations; Comparing evidence, credentials and recovery.
- Outcome: explain and apply three pipelines for one release contract, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make comparing evidence, credentials and recovery concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 207. An End-to-end Observability Investigation

- Chapter: [book/volumes/21-projects-and-industry-case-studies/207-an-end-to-end-observability-investigation.md](book/volumes/21-projects-and-industry-case-studies/207-an-end-to-end-observability-investigation.md). Prerequisite: Chapter 206; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Instrumentation and user symptoms; Metrics, logs and traces; A slow-order incident and resolution.
- Outcome: explain and apply an end-to-end observability investigation, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a slow-order incident and resolution concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 208. Google SRE Practices in Context

- Chapter: [book/volumes/21-projects-and-industry-case-studies/208-google-sre-practices-in-context.md](book/volumes/21-projects-and-industry-case-studies/208-google-sre-practices-in-context.md). Prerequisite: Chapter 207; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Published reliability and release practices; Constraints behind organizational choices; What a smaller team can reuse.
- Outcome: explain and apply google sre practices in context, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make what a smaller team can reuse concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 209. Netflix Container and Delivery Evolution

- Chapter: [book/volumes/21-projects-and-industry-case-studies/209-netflix-container-and-delivery-evolution.md](book/volumes/21-projects-and-industry-case-studies/209-netflix-container-and-delivery-evolution.md). Prerequisite: Chapter 208; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Dated container and delivery publications; Platform decisions and migration context; Lessons without copying an entire stack.
- Outcome: explain and apply netflix container and delivery evolution, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make lessons without copying an entire stack concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 210. Uber Observability and Alternative Growth Paths

- Chapter: [book/volumes/21-projects-and-industry-case-studies/210-uber-observability-and-alternative-growth-paths.md](book/volumes/21-projects-and-industry-case-studies/210-uber-observability-and-alternative-growth-paths.md). Prerequisite: Chapter 209; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Documented observability case studies; Historical scope and architecture constraints; Comparing real evidence with fictional company decisions.
- Outcome: explain and apply uber observability and alternative growth paths, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make comparing real evidence with fictional company decisions concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

## Volume 22 — Operational Reference

### 211. Linux and Shell Command Reference

- Chapter: [book/volumes/22-operational-reference/211-linux-and-shell-command-reference.md](book/volumes/22-operational-reference/211-linux-and-shell-command-reference.md). Prerequisite: Chapter 210; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Inspection, files, processes and services; Arguments, outcomes and failure clues; Links to canonical explanations.
- Outcome: explain and apply linux and shell command reference, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make links to canonical explanations concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 212. Networking and VPS Diagnostic Reference

- Chapter: [book/volumes/22-operational-reference/212-networking-and-vps-diagnostic-reference.md](book/volumes/22-operational-reference/212-networking-and-vps-diagnostic-reference.md). Prerequisite: Chapter 211; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: DNS, TLS, routing and sockets; Layered diagnostic decision trees; A quick incident evidence checklist.
- Outcome: explain and apply networking and vps diagnostic reference, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a quick incident evidence checklist concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 213. Docker and Podman Command Reference

- Chapter: [book/volumes/22-operational-reference/213-docker-and-podman-command-reference.md](book/volumes/22-operational-reference/213-docker-and-podman-command-reference.md). Prerequisite: Chapter 212; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Lifecycle, images, storage and networks; Compatibility and rootless differences; Command-to-chapter lookup.
- Outcome: explain and apply docker and podman command reference, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make command-to-chapter lookup concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 214. Kubernetes Command and Object Reference

- Chapter: [book/volumes/22-operational-reference/214-kubernetes-command-and-object-reference.md](book/volumes/22-operational-reference/214-kubernetes-command-and-object-reference.md). Prerequisite: Chapter 213; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: kubectl inspection and change commands; Objects, ownership and common symptoms; Safe context and rollout checks.
- Outcome: explain and apply kubernetes command and object reference, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make safe context and rollout checks concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 215. AWS CLI Operational Reference

- Chapter: [book/volumes/22-operational-reference/215-aws-cli-operational-reference.md](book/volumes/22-operational-reference/215-aws-cli-operational-reference.md). Prerequisite: Chapter 214; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Identity, networking, compute and data commands; Pagination, queries and permissions; Cost-aware resource inspection.
- Outcome: explain and apply aws cli operational reference, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make cost-aware resource inspection concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 216. Infrastructure and Pipeline Reference

- Chapter: [book/volumes/22-operational-reference/216-infrastructure-and-pipeline-reference.md](book/volumes/22-operational-reference/216-infrastructure-and-pipeline-reference.md). Prerequisite: Chapter 215; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Terraform, OpenTofu and Ansible workflows; GitHub, GitLab and Jenkins release checks; Change and credential checklists.
- Outcome: explain and apply infrastructure and pipeline reference, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make change and credential checklists concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 217. Scaling and Architecture Decision Tables

- Chapter: [book/volumes/22-operational-reference/217-scaling-and-architecture-decision-tables.md](book/volumes/22-operational-reference/217-scaling-and-architecture-decision-tables.md). Prerequisite: Chapter 216; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Vertical, horizontal and efficiency options; Data, tenancy and regional tradeoffs; Evidence needed before a scaling decision.
- Outcome: explain and apply scaling and architecture decision tables, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make evidence needed before a scaling decision concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 218. Observability and Incident Runbooks

- Chapter: [book/volumes/22-operational-reference/218-observability-and-incident-runbooks.md](book/volumes/22-operational-reference/218-observability-and-incident-runbooks.md). Prerequisite: Chapter 217; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Metrics, logs, traces and alert symptoms; First-response and handoff templates; An evidence-based diagnostic index.
- Outcome: explain and apply observability and incident runbooks, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make an evidence-based diagnostic index concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 219. Compatibility Matrix and Glossary

- Chapter: [book/volumes/22-operational-reference/219-compatibility-matrix-and-glossary.md](book/volumes/22-operational-reference/219-compatibility-matrix-and-glossary.md). Prerequisite: Chapter 218; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Supported baselines and provider differences; Terms, abbreviations and conceptual boundaries; A maintenance and verification ledger.
- Outcome: explain and apply compatibility matrix and glossary, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a maintenance and verification ledger concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

### 220. Production Readiness and Recovery Checklists

- Chapter: [book/volumes/22-operational-reference/220-production-readiness-and-recovery-checklists.md](book/volumes/22-operational-reference/220-production-readiness-and-recovery-checklists.md). Prerequisite: Chapter 219; consult canonical-topic chapters for deeper dependencies.
- Ordered core sections: Release, security and ownership evidence; Backup, failover and rollback readiness; A final service review.
- Outcome: explain and apply production readiness and recovery checklists, recognize its operational limits, and justify a decision under stated constraints.
- Example and failure brief: make a final service review concrete with realistic inputs, inspectable evidence, a failed assumption, diagnosis and recovery.
- Verification and assessment: use primary documentation for exact behavior; record tested versions, distinguish illustrative output, add focused exercises and answer guidance.

