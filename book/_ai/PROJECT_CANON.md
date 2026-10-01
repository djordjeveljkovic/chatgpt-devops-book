# DispatchDesk continuity and example contracts

This is a fictional teaching project. All traffic, staffing and budget figures below are scenario assumptions, never measured results or facts about a real company. Change an assumption explicitly before changing the architecture.

## Product and first deployment

DispatchDesk accepts orders, records them and sends notifications. The first team has two developers who share operations. Its first release runs on one Linux VPS. Users need a responsive order acknowledgment and eventual notification, not an elaborate microservice estate.

Initial learning scenario, established in Chapter 002: one order request per second typically, ten at peak, with payloads bounded to 64 KiB. Later growth scenarios can move to tens or hundreds of requests per second, a larger database and notification bursts; label that change explicitly. Third-party notification outages are expected. A later example target can be 99.5% monthly availability for order acceptance, with notification delay measured separately; introduce a target before treating it as a requirement. These are scenario assumptions, not measured results or universally appropriate values. Clarify whether planned maintenance consumes the budget.

Start with a single API process and durable persistence; introduce PostgreSQL and a worker as concurrency and asynchronous work become relevant. Redis is optional and derived state unless a chapter explicitly defines a different authority contract. Durable order and notification intent belongs in the database or a deliberately durable broker, not an accidentally persistent cache.

## Consistent interfaces

- HTTP service examples listen on unprivileged container port 8080 unless the runtime specifically requires another port. Published host ports and reverse proxies are explicit.
- `GET /healthz`: the process can respond. Do not make it depend on every downstream service.
- `GET /readyz`: the process can safely accept the type of work routed to it; define the dependency policy for that service.
- `POST /orders`: accept an order with a caller-supplied idempotency key when retries become part of the example. Persist the order and notification intent before acknowledging accepted work.
- `GET /orders/{id}`: show observable order state without exposing another tenant's data.
- Worker examples process notification intent with explicit acknowledgment, retry and duplicate-effect behavior. Graceful shutdown stops accepting new work and handles an in-flight item under a documented deadline.
- Configuration names: `PORT`, `DATABASE_URL`, `REDIS_URL`, `LOG_LEVEL`; add specific variables locally when needed. Never put real credentials in code or logs.
- Metrics and traces use bounded route templates, operation names and status labels. Order IDs belong in controlled logs/traces when appropriate, never unbounded Prometheus labels.

These contracts keep chapters coherent. Each practical snippet must still show its own setup; do not imply that an earlier chapter silently created files, accounts or infrastructure.

## Alternative company paths

**Harbor, the VPS company:** a small team, predictable regional traffic and a tight cash budget. It improves inefficient queries and resizes its VPS before adding hosts. It eventually separates database hosting or adds an application replica when evidence justifies that change. Losing one host must have an explicit recovery procedure. Kubernetes is delayed because its staffing and maintenance cost exceeds the current benefit.

**Summit, the managed AWS company:** a growing product team, bursty traffic and limited database/cluster operations capacity. It favors RDS, SQS and ECS/Fargate where service contracts fit. Discuss IAM, networking, quotas, bills and provider dependencies alongside reduced host maintenance. It can scale workers independently of request-serving capacity.

**Atlas, the platform company:** several application teams with different runtimes, many independently deployed services and explicit isolation/governance requirements. A platform team adopts Kubernetes when a shared workload API and operational expertise justify the cost. Managed services can remain outside the cluster; Kubernetes is not an argument to operate every database internally.

These are concurrent alternatives, not a universal maturity ladder. Use the same product capability and comparable assumptions when comparing them. Change traffic, reliability, staffing or tenancy requirements explicitly so a decision has a visible cause.

## Runtime examples

Python, PHP, Go and JavaScript examples demonstrate process supervision, configuration, signals, concurrency, connection pools, startup/readiness and telemetry. Keep code small and complete enough for its stated purpose. Do not silently claim that a language's development server is a production deployment. Explain PHP-FPM/proxy boundaries and managed-runtime worker behavior where relevant.

## Real-company cases

Keep real documented systems separate from this fictional project. Cite source publication date and organizational boundary. Older Netflix container publications teach historical design decisions; they do not establish its current entire deployment stack. Uber's 2026 monitoring publication describes corporate-network observability. Google SRE publications describe practices under Google's constraints; explain what can be adapted by smaller teams.
