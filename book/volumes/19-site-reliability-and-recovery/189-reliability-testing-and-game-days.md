---
book: The Complete DevOps Engineering Book
volume: 19
volume_title: "Site Reliability and Recovery"
chapter: 189
title: "Reliability Testing and Game Days"
slug: reliability-testing-and-game-days
status: complete
summary: ../../_ai/chapter-summaries/189-reliability-testing-and-game-days.md
---

# Chapter 189 — Reliability Testing and Game Days

**Section outline:** combine workload, dependency and failure conditions in representative tests; rehearse human and technical recovery; use a prelaunch game day to verify service, observability and rollback gates.

## Test the system people will operate

DispatchDesk passes unit and API integration tests, then launches a new order flow. Under realistic traffic, a slow payment dependency causes retries, the queue grows, and the autoscaler adds workers that increase database contention. No single component test reproduced the combination. Reliability depends on the interactions between workload, dependency behavior, deployment state, monitoring and operator decisions.

Reliability testing covers functional correctness, load and capacity, dependency degradation, failure recovery, security boundaries and human response. It includes deterministic tests in CI, production-like load tests, resilience experiments from [Chapter 188](188-chaos-and-resilience-experiments.md), restore/failover drills from [Chapters 186–187](186-backup-engineering.md), and game days that exercise people and systems together. Passing a test demonstrates behavior only for its tested inputs, configuration, scale, duration and environment.

## Combine load, faults and recovery scenarios

Test from realistic user journeys and measurable service goals. Define ordinary traffic, peak rate, burst shape, payload sizes, tenant mix, arrival patterns, expected concurrency and data volume. Use synthetic or sanitized data. Ensure the load generator itself is not a bottleneck and that the test does not send uncontrolled traffic to external providers or customers. Production-scale tests can create real cost and external effects; get authorization, understand quotas and provider testing policies, and prearrange cleanup.

Build a scenario matrix that combines meaningful conditions, not every possible permutation. Examples include peak load during a rolling deployment; one availability-zone loss during sustained traffic; a slow database plus bounded client retries; a queue consumer restart while backlog exists; a credential refresh during a service failover; and restore from backup while dependency capacity is constrained. Use risk analysis and recent incidents to choose combinations likely to reveal shared dependencies or feedback loops.

For each scenario define setup, starting conditions, injection or workload ramp, expected behavior, evidence, maximum duration, abort owner and cleanup. Set success thresholds from the user SLI/SLO and business correctness: request latency and errors, order integrity, queue age, recovery lag, duplicate effects, resource saturation and time to restore. Do not judge only by CPU or process health. If the system enters a safe degraded mode, document which user features are reduced and whether the behavior meets the agreed service contract.

Run incremental load first to learn the operating curve, then sustain the target long enough to reveal queue growth, memory leaks, throttling, autoscaling delay and background-work contention. Include a controlled overload test to verify that the system sheds work or degrades safely rather than amplifying retries into a cascade. Separate capacity headroom from demonstrated capacity: a short successful burst does not prove sustainable peak service or quota availability.

Compare the environment to production: architecture, network paths, data shape, identity, quotas, dependency limits, feature flags and telemetry. A scaled-down test may not expose coordination, cache behavior or nonlinear bottlenecks. A production-like environment costs more and still differs from production; record the differences and bound what the result proves. Keep performance and reliability results with code/configuration version, test-data version, generator version, region, run window and known measurement error.

## Run a game day and rehearse a major launch

A game day is a planned exercise that tests response as well as technology. It can begin as a tabletop with no system changes, progress to a staging fault, and later include an approved limited production scenario. Assign a facilitator, incident commander, technical operator, observer/scribe and communications lead. Tell participants which environment is in scope, who can stop the exercise, how to distinguish a real incident from the simulation and how to reach help if the primary platform is affected.

Use a scenario that tests a concrete assumption: a region is unavailable, queue age rises, a deployment causes elevated errors, the identity provider is degraded, or a backup must be restored. Keep injects controlled and reveal only what a real responder would see, while preserving a safety observer who knows the exercise boundary. Do not confuse realism with withholding information from people who need to prevent actual customer harm. A game controller can pause or terminate the exercise without waiting for the simulated incident commander.

Observe whether responders can find current dashboards and runbooks, identify user impact, assign tasks, make a data-safe mitigation choice, contact dependencies, communicate uncertainty and hand off command. For technical exercises, verify the recovery is real: service requests succeed, state is consistent, queues drain, traffic uses the intended site and alerts return to expected operation. Stop on a customer-impact boundary, data-integrity concern, unexpected target or loss of observability.

Before a major launch, rehearse the full change path: build and artifact identity, migration compatibility, feature flags, staged traffic, SLO gates, alert routing, on-call staffing, support communication, quota and dependency headroom, abort authority, rollback/roll-forward choice and data recovery. Run a go/no-go review that names the approving roles and evidence. The launch plan should not assume that rollback is safe after an irreversible schema or data change.

After the exercise, debrief while evidence is fresh. Record the planned hypothesis, actual observations, deviations, what worked, what failed, confusing instructions, timing, customer risk, action owners and verification evidence. Separate exercise-control issues from system issues. Update the test plan and runbooks; rerun failed acceptance checks before the launch or recovery plan relies on them. A game day that finds an unstaffed escalation path or an untested backup is valuable only if the gap becomes owned work.

For DispatchDesk's launch rehearsal, the team sends a rising but bounded synthetic order load to staging, then adds payment-provider latency while a canary rollout is in progress. The team expects the circuit breaker to limit retries, the queue to remain within the drain objective and the order API SLI to stay within its launch gate. The first run shows alert noise from every worker instead of one grouped user-impact page. The facilitator stops the scenario when queue age reaches its preapproved limit. The team improves alert grouping and runbook links, repeats the experiment, verifies order idempotency and backlog recovery, and records that external payment behavior was simulated rather than exercised against the real provider. The production launch remains gated on a separate quota check and named on-call coverage.

Exercises:

1. A system passes peak load and separately passes a node-loss test. What combination could still reveal overload during failure?
2. A staging environment has half the production database size and no real identity provider. Which conclusions should the team avoid drawing?
3. During a game day, a real user-impact alert fires outside the scenario. Who stops the exercise and how is the event handled?
4. A launch rollback restores the previous binary but not the old schema. Which acceptance and recovery questions should the launch review resolve?

Answer guidance: combine sustained traffic with reduced capacity, dependency slowness or rollout overlap; test retry and queue feedback, not merely an isolated failed node. Bound conclusions to the reduced data size and mocked identity path, then validate production-scale behavior and identity dependencies separately. The designated exercise controller or incident commander stops the simulation on real impact, declares/coordinates a real incident and preserves clear communication. Verify schema compatibility, forward/backward data changes, rollback versus roll-forward, restore points, owner authority and data-integrity acceptance before the change.

Review questions:

- How do reliability tests differ from component functional tests?
- Which workload and failure combinations matter for a service with queues and external dependencies?
- What should a game day evaluate beyond whether the injected fault occurred?
- Why do launch rollback and database recovery need separate acceptance criteria?

Takeaways:

- Test interactions between realistic load, dependencies, change and failure, using user outcomes and correctness.
- Match environment and data shape to the claim, document differences and obey provider test limits.
- Rehearse human roles, communication, observability and recovery along with technical resilience.
- Turn exercise findings into owned fixes and rerun failed gates before relying on the plan.

## Sources checked 2026-10-04

- [AWS Well-Architected: Test reliability](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/test-reliability.html) — functional, non-functional and resilience testing, including game days.
- [AWS Well-Architected: Test scalability and performance](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_testing_resiliency_test_non_functional.html) — realistic load, scaling, quotas and monitoring.
- [Google SRE: Testing for Reliability](https://sre.google/sre-book/testing-reliability/) — limits of test confidence and environment equivalence.
- [Google SRE: Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) — overload testing and failure-mode analysis.
- [Chapter 188 — Chaos and Resilience Experiments](188-chaos-and-resilience-experiments.md) and [Chapter 181 — SLIs, SLOs and Error Budgets](181-slis-slos-and-error-budgets.md) — experiment guardrails and service measures.

All DispatchDesk traffic and thresholds are fictional. No load test, provider integration, fault injection, game day, launch or production change was run.
