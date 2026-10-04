---
book: The Complete DevOps Engineering Book
volume: 20
volume_title: "Architecture and Platform Engineering"
chapter: 197
title: "Legacy Infrastructure Modernization"
slug: legacy-infrastructure-modernization
status: complete
summary: ../../_ai/chapter-summaries/197-legacy-infrastructure-modernization.md
---

# Chapter 197 — Legacy Infrastructure Modernization

**Section outline:** discover the current system before choosing a target; modernize through small changes that preserve service and data; manage compatibility, rollback and retirement evidence.

## Learn the system before changing it

DispatchDesk's invoice service runs on an aging virtual machine. The only diagram is six years old; batch jobs, certificate renewal and a finance export are undocumented. A proposal to move it to Kubernetes treats the host as a package, but the real system includes its data, scheduled jobs, external integrations, operational knowledge and business timing.

Start with an inventory of processes, owners, dependencies, interfaces, data stores, backup/recovery methods, access paths, operating system and runtime versions, licenses, capacity patterns, maintenance windows and support contracts. Observe actual network and process activity where permitted, then ask users and operators to validate it. Distinguish confirmed behavior from assumptions. Record which components are unsupported, vulnerable, hard to recover or blocking change. [Chapter 141](../15-observability-and-telemetry/141-observability-from-questions-to-evidence.md) offers the evidence mindset; Chapter 186 covers recovery proof.

Define the outcome before the platform. Drivers might include security support, recovery time, release risk, scale, compliance or cost. Set acceptance measures for each: supported OS/runtime, tested restore, deployment lead time, change failure rate, batch completion deadline or reduced privileged access. “Cloud native” and “containerized” are implementation choices, not outcomes.

## Select a migration path and cutover boundary

Retain and improve when the system is stable and its risks can be managed. Rehost when moving the same workload solves a hosting constraint and the target can operate it. Replatform when a limited change improves support or operations without rewriting domain behavior. Refactor when necessary business changes justify redesign and the team can test the new behavior. Replace or retire only when data, users, integrations and legal retention are addressed. These categories help structure discussion; actual migrations can combine them.

Prefer a sequence that keeps a recoverable production path. Build deployment automation and observability around the current service first. Upgrade runtime or operating system with compatibility tests. Separate configuration from binaries. Introduce an adapter around an unstable integration. Move read-only traffic or noncritical jobs before writes. If using a strangler approach, route a clearly bounded capability through the new implementation while retaining explicit ownership of data and fallback.

Data migration is often the hardest boundary. Define source of truth, schema compatibility, backfill consistency, duplicate handling, incremental change capture, validation queries and cutover rules. Avoid uncoordinated dual writes. A shadow read can compare results but must not trigger external side effects. A rollback plan must explain which writes occurred after cutover and how they can be reconciled; switching DNS back is not data rollback.

## Make each step reversible enough

Use small batches, staged rollout and a stop condition tied to user impact. Capture a pre-change backup and prove it can restore. Keep old and new runtime dependencies available through the agreed rollback window. Check capacity and downstream limits before shifting traffic. Establish who can halt a migration, what evidence they need, and how to communicate state. A rollback can become unsafe once an irreversible schema change or external contract change is made, so plan expand-and-contract schema evolution and explicit compatibility periods.

For DispatchDesk, the team first adds a repeatable VM image build, removes a shared administrator credential and tests a restore into isolation. They instrument invoice creation and the finance export, then discover an undocumented month-end file format. A compatibility test becomes a cutover gate. They move the scheduled worker to a supported runtime while leaving the database authoritative, reconcile output for two billing cycles and only then replace the host. The team retains the original export and a tested fallback through the financial close. The gradual work resolves the support risk before any container migration is considered.

Characterization tests are especially valuable when source code is incomplete or behavior is undocumented. Capture representative inputs and outputs, including edge cases, then have the business owner confirm which behavior is contractual and which is accidental. Protect sensitive samples and avoid copying production secrets or personal data into test fixtures. A compatibility test should cover timing, ordering, encoding, rounding and failure behavior when those details affect users. If the service cannot be tested safely in isolation, create a shadow or replay method that suppresses external side effects and documents its limits.

Exercises:

1. A legacy host has no owner, but business users depend on a monthly report. What must be learned before retirement?
2. New and old services both write invoice rows during a migration. What consistency and rollback risks arise?
3. A runtime upgrade passes unit tests but misses month-end behavior. Which discovery and validation steps were absent?
4. A migration improves deployment frequency but removes the only tested restore path. How should the release be judged?

Answer guidance: identify report consumers, schedule, source data, retention, accuracy, integrations and replacement acceptance before decommissioning. Dual writes can diverge under partial failures and make rollback ambiguous; establish one writer or a deliberate change-capture/consistency scheme with reconciliation. Include representative calendar and volume cases, operator workflows and external file contracts in characterization tests. Deployment improvement does not offset unproven recovery; restore evidence is a release requirement and should be reinstated before further migration.

Review questions:

- How do you distinguish a real system dependency from an obsolete diagram?
- Which measurable business outcome justifies the chosen migration path?
- Why is data rollback different from routing rollback?
- What must remain available through the cutover and rollback window?

Takeaways:

- Discover users, interfaces, operations and recovery paths before choosing a target platform.
- Select retain, rehost, replatform, refactor, replace or retire based on measurable outcomes.
- Migrate in bounded steps with explicit data ownership, compatibility and stop conditions.
- Prove restore and reconciliation before declaring a legacy system safely replaced.

## Sources checked 2026-10-04

- [AWS Prescriptive Guidance: Migration strategies](https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-guide/migration-strategies.html) — common migration patterns and tradeoffs.
- [Microsoft Azure Cloud Adoption Framework: Rationalize](https://learn.microsoft.com/azure/cloud-adoption-framework/digital-estate/5-rs-of-rationalization) — retain, retire, rehost, replatform, refactor and other options.
- [Chapter 186 — Backup Engineering](../19-site-reliability-and-recovery/186-backup-engineering.md) — backup and restore validation.

DispatchDesk systems and migration evidence are fictional. No migration or production change was performed.
