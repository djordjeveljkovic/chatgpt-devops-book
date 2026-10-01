---
book: The Complete DevOps Engineering Book
volume: 1
volume_title: "Engineering Mental Models"
chapter: 2
title: "Requirements Before Tools"
slug: requirements-before-tools
status: complete
summary: ../../_ai/chapter-summaries/002-requirements-before-tools.md
---

# Chapter 2 — Requirements Before Tools

## Functional and operational requirements

A tool choice answers “how,” but a requirement answers “what must happen, for whom, and under which conditions?” The difference is consequential. “Use Kubernetes” does not specify whether an accepted order survives a storage failure. “Use a queue” does not specify when a customer receives a notification. Before evaluating those tools, describe the behavior they must support.

The prerequisite is [Chapter 1](001-what-devops-engineers-actually-own.md), particularly its distinction between an action and an operating outcome. Here you will turn DispatchDesk's product idea into a small service charter: a reviewable agreement about intended behavior, operating limits and evidence. The charter will guide later Linux, cloud and container examples without prematurely selecting their implementation.

A **functional requirement** describes what a product does. DispatchDesk accepts an order containing a customer reference and a list of items, returns an order identifier, allows authorized staff to inspect it, and arranges a notification. This sounds simple until you examine boundaries. Is an empty item list valid? Can staff alter an accepted order? Is the customer reference sensitive? Does an order identifier mean the order exists durably, or only that the request reached memory? These questions influence correctness before they influence deployment.

An **operational requirement** describes the conditions under which useful behavior must continue, and how it is maintained. Examples include a response-time objective, a recovery limit after host failure, a way to identify pending notifications, and an auditable access path. “Recover within two hours” implies that someone can identify the failure, obtain the necessary backups and credentials, restore software and data, and verify readiness within that interval. Merely scheduling a backup does not meet it.

A requirement should state its subject precisely. The notification requirement might mean the provider accepts a request, the receiving mail server accepts a message, or the customer reads it. DispatchDesk may observe the first event directly and receive imperfect information about the second; it cannot guarantee the third. Choosing an observable boundary makes the agreement honest. If customers need a stronger guarantee, the product needs another delivery channel or an explicit acknowledgement workflow.

Separate requirements from assumptions. “The business requires accepted orders to remain recoverable” is a desired property. “The workload peaks at ten order submissions per second” is an assumption that may be measured incorrectly. “The team can respond during local business hours” is a staffing constraint. Mixing them into one list makes later disagreement difficult: changing a workload assumption should not quietly weaken the data-retention requirement.

Also separate requirements from proposals. “Only authorized support staff can inspect order details” is a requirement. “Use this identity provider” is a proposed mechanism. Keeping both in a decision record is useful, provided their roles are clear. A rejected identity provider should not erase the access requirement.

## Constraints and measurable acceptance

Every design spends constrained resources: money, time, engineering attention, response capacity and risk. DispatchDesk's fictional VPS company has two application engineers and limited after-hours coverage. Its budget may support one small server, but the more important constraint may be the time required to maintain five independent services. A managed service can reduce specific maintenance work while adding account, permission, integration and billing responsibilities. A cheap component that nobody can restore has a cost missing from its invoice.

Begin measurement with the customer journey. For order submission, record when the service receives a valid request and when it finishes the response, whether the request is accepted, and whether the accepted order is retrievable. Choose an objective and an interval. For example: “Over a rolling seven-day window, at least 99% of valid order requests complete successfully within one second at the API boundary.” This is a fictional learning objective, not an industry benchmark.

Its denominator needs definition. Excluding requests with malformed payloads may be reasonable, but excluding every request during an outage would make the objective meaningless. If the service refuses a valid request because storage is down, that is a failure of the journey. Define where requests are counted: a backend cannot count a request that never passed the proxy. Later monitoring work must account for that blind spot.

A **service level indicator** is a defined measurement of service behavior, while a **service level objective** is its target. Google's 2016 [Service Level Objectives chapter](https://sre.google/sre-book/service-level-objectives/) discusses this distinction and the value of measurements relevant to users. The full mathematics and alerting policy belong to [Chapter 181](../19-site-reliability-and-recovery/181-slis-slos-and-error-budgets.md). Here, the crucial step is choosing a measurement that can prove or disprove the requirement.

Not every requirement is a percentage. “Only the support role can inspect a customer's order” requires positive and negative authorization checks. “A restore preserves all orders through the last committed backup point” requires reconciliation of known records. “A new engineer can identify the active release in ten minutes” requires a documentation and access rehearsal. A dashboard showing CPU usage cannot substitute for these different forms of evidence.

Acceptance criteria should be realistic enough to exercise the mechanism. A test that sends one request to an idle process cannot validate the peak-workload assumption. A backup test that only lists a file cannot validate restoration. Equally, do not begin with an elaborate performance suite when the unresolved question is whether the API acknowledges before saving. Choose the smallest experiment that answers the current question, then broaden it when new risks justify the work.

When stakeholders request “no downtime,” translate the phrase into scenarios. Does it mean no interruption during routine releases, during a host reboot, or after the loss of an entire provider region? Does delayed notification count as downtime? Each interpretation leads to different architecture and cost. Document the accepted boundary and the person authorized to change it.

## Writing a service charter

A short charter can live alongside the source code. It should contain decisions a future responder can use, rather than aspirational slogans. The following Markdown is a complete initial example for the fictional project; it is deliberately independent of Linux distribution and hosting provider.

```markdown
# DispatchDesk service charter — learning edition

Owner: DispatchDesk service team
Review trigger: workload doubles, recovery rehearsal fails, or delivery contract changes

## Customer journey
A valid order receives a stable identifier after durable acceptance.
Authorized staff can retrieve an accepted order using that identifier.
Notification delivery is asynchronous and does not determine order acceptance.

## Learning workload assumptions
Typical load: one order per second.
Peak experiment: ten order submissions per second for ten minutes.
Order payload: at most 64 KiB; attachments are outside this edition.

## Acceptance evidence
For a controlled order, record its identifier and retrieve its item list.
After a controlled application restart, retrieve that order again.
For a controlled notification, record provider acceptance or a pending reason.
Unauthorized order inspection returns no order details.

## Operating limits
Initial deployment has one application host and one persistent data store.
Host failure can interrupt order acceptance.
The learning edition has no contractual availability promise.
A restore rehearsal must document actual data loss and elapsed recovery time.

## Recovery decisions
Preserve accepted orders before resuming uncertain work.
Stop a worker that sends incorrect notifications.
Do not replay uncertain notification attempts without examining their state.

## Known gaps
Backup design, retention policy and measured service objectives are pending.
Production use requires their approval and verification.
```

The workload numbers are inputs for experiments, not measured facts. The charter explicitly admits gaps rather than implying the learning deployment is ready for real customer commitments. Later chapters may change these assumptions, but must record why. A team adopting the managed AWS route can retain the same acceptance contract while choosing different persistence and recovery mechanisms.

Review the charter with product, development, support and operations together. Product can explain whether a delayed notification harms the business. Support can identify the questions customers ask. Development can identify what the application records. Operations can explain recovery evidence and access dependencies. Their disagreement is valuable while changes are cheap.

Then connect each criterion to a procedure. The restart criterion needs a controlled lab environment, a known test order, a restart action and a retrieval check. The authorization criterion needs two identities and a safe test record. These prerequisites belong beside executable tests when the application exists. Inventing a successful transcript now would obscure the fact that the implementation has not yet been written.

For a paper exercise, trace these illustrative events:

```text
10:00:00.000 valid order request arrives
10:00:00.040 order record commits
10:00:00.055 API returns accepted order identifier
10:00:03.000 provider accepts notification attempt
```

Order acceptance latency is 55 milliseconds at the defined API boundary. Notification acceptance happens three seconds after arrival. Neither value describes the browser's full rendering time or the recipient's reading time. If the commit occurs after the API response instead, the trace fails the durable-acceptance contract even though the response is fast.

## When a requirement was silently changed

Suppose the team interprets “send notifications quickly” as “return quickly from the notification API call.” The provider responds with HTTP 202 and processes work later. DispatchDesk marks the notification delivered, but the provider subsequently rejects the destination. Support cannot find pending work because the local record says success.

The failure begins with an ambiguous requirement and becomes a state-model bug. [RFC 9110, section 15.3.3](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.3.3) describes 202 Accepted as accepted processing that has not completed. It is not proof of eventual delivery. The responder compares the provider's acceptance response with later delivery events, examines the local transition and identifies the premature success marker.

Recovery requires preserving uncertain records and agreeing which state the product actually promises. The team can distinguish pending, provider-accepted, delivered when confirmed, and failed. It can reconcile available provider events and expose uncertainty to support. If provider evidence is unavailable, the correct state may remain unknown; do not replace missing evidence with “delivered.” Any replay decision considers duplicate risk and customer impact. The long-term repair updates both the charter and the implementation, then tests the provider-rejection case.

This incident also shows why requirements must survive tool changes. A different queue or container runtime cannot correct a false interpretation of provider acceptance. A clear contract lets engineers compare alternatives against the same intended behavior.

## Exercises and answer guidance

1. Rewrite “make DispatchDesk fast.” Define the journey, timing boundary, workload, threshold and measurement interval. An answer mentioning only average CPU usage misses the customer's experience. Explain which failures count in the denominator.
2. Classify these statements: “ten requests per second,” “accepted orders are retrievable after restart,” and “use PostgreSQL.” They are respectively an assumed workload, a desired property and a proposed implementation. Explain how evidence could change the first and support the second.
3. Add a restore criterion to the charter. A useful answer specifies known test records, a backup boundary, an isolated restore environment, elapsed-time measurement and reconciliation. It does not claim zero data loss without a mechanism or evidence.

## Review questions and takeaways

Which behavior does an accepted identifier promise? What measurement boundary can conceal a customer's failure? Who decides whether a requirement can be weakened? Which assumptions should trigger an architecture review? Why does provider acceptance differ from customer delivery?

Requirements make tradeoffs comparable. Define customer behavior before implementation, distinguish assumptions from commitments, and choose evidence that tests the actual contract. Keep operational limits visible and revise the charter when evidence changes. Continue with [How Computers Execute Services](003-how-computers-execute-services.md).

## Sources and verification

Inspected on 2026-10-01: Google's SRE book chapter on service level objectives, part of the 2016 publication, and RFC 9110 HTTP Semantics, published June 2022, particularly 202 Accepted. No company-wide practices or current commercial guarantees are inferred from these sources. The charter, workload and event trace are fictional teaching examples. No application, load test or recovery procedure was executed. Independent review is pending.
