---
book: The Complete DevOps Engineering Book
volume: 20
volume_title: "Architecture and Platform Engineering"
chapter: 191
title: "Monoliths, Services and Organizational Boundaries"
slug: monoliths-services-and-organizational-boundaries
status: complete
summary: ../../_ai/chapter-summaries/191-monoliths-services-and-organizational-boundaries.md
---

# Chapter 191 — Monoliths, Services and Organizational Boundaries

**Section outline:** distinguish deployment units from module and team boundaries; identify operational cost and coupling in a service architecture; evaluate a service extraction using domain, data, ownership and rollback criteria.

## Choose boundaries for change and ownership

DispatchDesk starts with one application and a small team. As the product grows, checkout changes require coordination with billing and fulfillment, and one shared deployment creates risk for unrelated work. The architecture group proposes ten microservices so every team can deploy independently. Six months later, order creation requires synchronous calls across five services and a distributed database transaction that nobody owns. The number of deployables increased; the system's ability to change independently did not.

A monolith packages several capabilities into one deployable application. It can still have strong internal module boundaries and separate owners. A modular monolith makes these boundaries explicit in code and data access while retaining an in-process runtime and often one release unit. A service architecture splits capabilities into independently running processes that communicate across network boundaries. These are choices about deployment, failure and operational ownership, not a ranking from old to modern.

Keep three boundaries distinct when designing the system:

- **Domain/module boundary:** which concepts, rules and data belong together, and which interfaces other areas use.
- **Deployment/runtime boundary:** what is built, released, scaled, monitored and failed independently.
- **Ownership boundary:** which team can make changes, operate the component, manage its data and answer for its reliability.

The boundaries should support a coherent capability. A strong module boundary can exist inside one deployable; a service boundary can exist without independent ownership, creating handoffs rather than autonomy. Conway's Law is a useful prompt to examine how team communication affects system structure, not a deterministic rule that organization charts automatically produce good architecture.

## Compare coupling and operational cost

A monolith can offer one process boundary, simpler local calls and easier transactional changes. A poorly structured monolith may make safe changes hard because modules share tables, global state and assumptions. Service decomposition can isolate releases, scale a hot workload separately and give teams clearer ownership. It also turns local calls into network dependencies that can time out, fail partially, return stale data, introduce serialization/version compatibility and require operational systems for deployment, discovery, telemetry, identity, retries and incident response.

Service count is not a measure of autonomy. A distributed monolith has multiple deployables but changes that must ship together, chatty call chains, shared mutable databases or circular dependencies. It inherits network failure modes without receiving independent change boundaries. Conversely, a modular monolith with stable interfaces and ownership rules may let teams ship their modules frequently even though they share a process.

Map a user journey and its dependencies before choosing a split. Record call count and critical-path latency, shared data reads/writes, transaction invariants, failure handling, release coordination, scaling profile, security boundary, team ownership and support burden. Consider whether the capability has a bounded vocabulary and rules, whether one team can operate it end to end, and whether callers can tolerate asynchronous or eventually consistent behavior. Split where concepts and change patterns cohere; do not divide simply by database table or screen.

Data ownership is a central boundary. If two services both write each other's tables, schema changes and recovery become coupled. Prefer a clear owner and published interface, with other components consuming APIs or events. A separate datastore is not a universal requirement for a domain module, but a service that claims independent ownership should not rely on arbitrary writes to shared tables. Cross-service transactions require explicit consistency and compensation decisions; an HTTP call chain does not preserve a local ACID transaction automatically.

Operational ownership includes more than on-call. A team needs deployment automation, observability, security updates, capacity planning, backup/recovery where it owns state, dependency management and support expectations. A service that nobody can safely release or troubleshoot adds organizational load. Chapters 181–190 cover reliability practices; use their SLO, on-call, backup and incident costs when estimating whether a boundary makes the whole product easier to operate.

## Decide whether to extract a service

Extract when a distinct capability has a demonstrated reason for independent release, scaling, security isolation or team ownership, and the organization can support its distributed-systems costs. Gather evidence from recurring coordination delays, risk coupling, module dependencies, load profile, security/compliance scope, deployment frequency and incident impact. If the problem is tangled internal dependencies, first enforce module interfaces and ownership inside the existing deployable; a network hop may make the coupling harder to see rather than remove it.

Treat extraction as a staged migration, not a rewrite. Establish a bounded API or event contract and the target team's operating responsibilities. Move code behind the interface while keeping behavior comparable. Decide which component is authoritative for each piece of data, how state moves, how duplicate events are handled and how reads/writes are verified. Avoid uncontrolled dual writes; use a staged ownership transfer, outbox/event strategy or a temporary reconciled copy with a clear termination date. Preserve a way to route traffic or data back while compatibility permits it.

Measure success against the original reason for extraction: teams deploy without synchronized releases, scaling cost/latency improves, failure is contained, security boundary is clearer, or lead time and incident load fall. Also track newly introduced network failures, duplicate/out-of-order events, operational overhead, latency and recovery work. A boundary that reduces one team's work but adds two other teams' interrupts has moved cost rather than removed it.

For DispatchDesk, billing and fulfillment are tightly coupled to order status and change together frequently, so the architecture group first adds explicit domain modules and stops direct cross-module database writes. Payments has a separate scaling profile and a named team with an operational rota, so it is selected as a candidate for extraction. The team defines the payment authorization API, timeout/idempotency semantics, data owner, event contract and degraded checkout behavior. They compare old and new results in shadow mode without sending duplicate provider charges, then migrate a small traffic cohort with a rollback route and clear stop signals. The extraction is considered successful only when the payment team can deploy and recover independently and the checkout SLO remains within target; creating a new repository alone is not evidence of autonomy.

Exercises:

1. A service has its own container and repository but requires five teams to approve each release. Which boundary is independent, and which is still coupled?
2. A monolith has a hot image-resize module that needs different scaling. What options should be evaluated before creating a service?
3. Two proposed services update the same order tables. What ownership and consistency decisions are missing?
4. A service extraction increases deployment frequency but raises on-call work and user-visible latency. How should the team judge success?

Answer guidance: deployment is separated but organizational/release ownership remains coupled; clarify authority and remove synchronized change dependencies. Compare process-level scaling, queue workers, resource isolation or a service split while weighing operational cost and interface coupling. Assign one system of record per data element and define API/event consistency, duplicate handling, migration and recovery. Evaluate the original business rationale together with reliability, latency, on-call burden and end-to-end change independence; adjust or reverse the design if net autonomy did not improve.

Review questions:

- How do domain, deployment and ownership boundaries differ?
- Which costs accompany a move from local calls to remote services?
- What conditions make a service extraction operationally plausible?
- Which evidence would show the extraction improved autonomy rather than only increasing deployables?

Takeaways:

- Monoliths can be modular and service architectures can remain tightly coupled.
- Draw boundaries around coherent domain rules, data ownership and teams able to operate a capability.
- Account for network failure, consistency, security and on-call costs before extraction.
- Migrate incrementally and measure success against the reason for creating the new service.

## Sources checked 2026-10-04

- [Martin Fowler: Microservice Trade-Offs](https://martinfowler.com/articles/microservice-trade-offs.html) — benefits/costs and modular monolith comparison.
- [Martin Fowler: Monolith First](https://martinfowler.com/bliki/MonolithFirst.html) — boundary discovery and prerequisites before decomposition.
- [Microsoft Azure Architecture Center: Domain Analysis](https://learn.microsoft.com/azure/architecture/microservices/model/domain-analysis) — bounded contexts and domain-driven boundary modeling.
- [Martin Fowler: Microservices](https://martinfowler.com/articles/microservices.html) — independent deployment, services and distributed transaction tradeoffs.
- [Chapter 190 — Reducing Toil and Improving Operations](../19-site-reliability-and-recovery/190-reducing-toil-and-improving-operations.md) — operating and toil costs in ownership decisions.

The architectural story is fictional. No production architecture, team structure, service extraction, migration or performance test was performed.
