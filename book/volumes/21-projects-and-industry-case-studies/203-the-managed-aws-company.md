---
book: The Complete DevOps Engineering Book
volume: 21
volume_title: "Projects and Industry Case Studies"
chapter: 203
title: "The Managed AWS Company"
slug: the-managed-aws-company
status: complete
summary: ../../_ai/chapter-summaries/203-the-managed-aws-company.md
---

# Chapter 203 — The Managed AWS Company

**Section outline:** ECS, queues and managed persistence; team capacity and service boundaries; a growth-driven architecture change.

## Move responsibility with a clear contract

DispatchDesk has a small platform team and now operates a managed AWS environment. It deploys an API and worker to Amazon ECS, stores relational state in Amazon RDS for PostgreSQL, places documents in S3, and uses a managed queue for asynchronous email and import tasks. The architecture uses managed components to reduce host maintenance; the product team still owns data correctness, workload configuration, IAM policy, deployments, alarms, recovery and cost.

Map each request from public entry through load balancer, task, database or queue, and external provider. Define which identity each task assumes and scope permissions to the operations it needs. Keep database credentials out of images and logs; rotate them and test connection-pool recovery. Bucket and queue policies should state who can read, write, delete and administer. Use private network paths where required, but retain explicit identity checks. Chapters 083–089 and 091–100 cover these service controls in detail.

For asynchronous work, define message visibility, retry count, poison-message handling, idempotency, ordering needs and retention. A queue improves buffering and workload isolation; it does not guarantee exactly-once business effects. The worker records a durable result keyed to the order/event identity before acknowledging completion. A dead-letter queue is monitored and has an owned replay procedure, not a disposal bin.

## Split by responsibility rather than service fashion

One application team owns order APIs and persistence; a small operations group supports the shared account, network and deployment path. As service ownership grows, the team separates the import worker because it has a distinct throughput profile and can be scaled from queue depth. The boundary comes with a versioned message contract, data authority and on-call responsibility. The team avoids splitting order and billing just to match a diagram: they share transaction invariants and still change together.

Use infrastructure as code for account, network, IAM, service definitions, alarms and managed data resources. Review plans, protect state, and separate production credentials from pull-request validation. Promote the same immutable image digest from test to production; environment configuration changes independently but remains versioned. Add rollout alarms for successful order creation and queue age, not only task health. A task can be healthy while it cannot reach the database or complete work.

## Change architecture from observed pain

A regional event exposes that imports can fill the primary queue and delay transactional notifications. The team separates queues by priority, applies per-queue concurrency, and reserves database connection capacity. It evaluates a read replica for reporting, but rejects using a lagging replica for financial decisions without an explicit stale-read contract. It adds a tested backup and recovery procedure for RDS plus independent object protections; managed backups reduce operational work but do not prove application restore completeness.

The team reviews service ownership as it adds developers. It writes a small platform contract: supported languages, log/trace fields, image identity, deployment method, SLOs and escalation. That shared contract supports different implementations without claiming all products have the same runtime needs. Multi-account growth is considered for security and billing boundaries, with centralized logging and emergency access designed before accounts proliferate.

The account foundation matters as the number of services grows. Separate production from development by account or another enforceable boundary, establish an organization-level audit trail, and prevent application roles from changing foundational controls. Use short-lived workload credentials where supported. A deployment role should be unable to grant itself broader IAM permissions or disable audit collection. Cross-account access requires an explicit trust relationship and a test showing the intended principal can perform only its assigned actions. Keep emergency access distinct and reviewed. These controls make future team autonomy possible without treating a shared account administrator as the everyday deployment mechanism.

 The team reviews cloud spend monthly by service and environment, explains shared network and observability charges, and sets alerts for unexpected growth. It keeps infrastructure state and audit evidence recoverable if the deployment system fails. Managed components change the failure mode and skill profile; they do not make the architecture ownerless.

 Teams also define a service retirement process for temporary resources and old environments, with a human owner for data deletion and billing closure. Cost alerts alone cannot tell whether an unusual spike is legitimate demand or runaway work; correlate them with deployment, traffic and queue activity before taking action.

Exercises:

1. The queue reports successful delivery, but customers receive duplicate emails after worker retries. What business invariant is missing?
2. Task health checks pass while order creation fails from database connection exhaustion. Which signals and limits should be added?
3. A managed backup restores the database, but uploaded documents are absent. How was recovery scope incomplete?
4. The team proposes a service split around every database table. Which evidence should govern boundaries?

Answer guidance: idempotent effects and a durable processed-event key are missing; retries may repeat a side effect after ambiguous acknowledgement. Add transaction success, connection utilization/waits, pool bounds, queue age and dependency alarms; coordinate app concurrency with database capacity. Include object data, metadata, keys and cross-reference integrity in backup scope and test a representative workflow. Use domain coherence, change coupling, data ownership, scaling/security needs and ability to operate an independent service.

Review questions:

- Which responsibilities remain with a team using managed cloud services?
- Why do queues need explicit idempotency and replay ownership?
- How should teams choose a service boundary and own its data?
- What does a complete recovery test include across managed services?

Takeaways:

- Managed services reduce selected infrastructure work while preserving application ownership.
- Specify identity, queue, data and recovery contracts across service boundaries.
- Scale workers and database concurrency from measured demand and business priority.
- Reuse a platform contract while letting workloads choose appropriate implementation details.

## Sources checked 2026-10-04

- [Amazon ECS documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html), [Amazon RDS for PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html), [Amazon SQS](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html) and [Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html) — service behaviors and operations.
- Chapters 092–100 and 186–190 — artifact promotion, AWS services, recovery and reliability.

AWS architecture and incidents are fictional. No AWS resources were created or tested.
