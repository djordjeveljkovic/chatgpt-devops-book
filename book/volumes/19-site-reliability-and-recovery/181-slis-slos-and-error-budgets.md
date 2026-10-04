---
book: The Complete DevOps Engineering Book
volume: 19
volume_title: "Site Reliability and Recovery"
chapter: 181
title: "SLIs, SLOs and Error Budgets"
slug: slis-slos-and-error-budgets
status: complete
summary: ../../_ai/chapter-summaries/181-slis-slos-and-error-budgets.md
---

# Chapter 181 — SLIs, SLOs and Error Budgets

**Section outline:** measure reliability from a user-relevant service-level indicator; set a service-level objective and window; use the error budget and actionable alerts to balance changes and reliability work.

## Why reliability needs a measurement contract

DispatchDesk says its API is “99.9% reliable,” but the dashboard measures whether its pods are running. A pod can be healthy while requests time out at the public gateway, and a deployment can look green while order submission fails for a whole region. The team argues about whether a short outage broke the promise because nobody agreed on which requests counted or how the target was calculated.

A service-level indicator (SLI) is a measurement of a user-relevant behavior. A service-level objective (SLO) is a target or acceptable range for that indicator over a defined window. A service-level agreement (SLA) is a commitment to customers or users, often with consequences or remedies if terms are not met. An internal SLO can guide engineering before any external guarantee is made. These terms only help when the measurement contract is clear: who experiences the service, which events count, what data is authoritative, what window applies and how missing telemetry is handled.

## Choose indicators from the user journey

Begin with the service action users depend on, such as submitting an order or reading an account balance. Identify success and failure conditions from the client-visible boundary. For an API, an availability SLI might be the proportion of eligible requests that return a valid response within an agreed latency threshold. A latency SLI might measure the proportion of eligible requests completed under a threshold. A correctness SLI may verify that successful writes persist and later reads return the intended data. Queue or batch services may instead measure completion by a deadline, age of the oldest item, or data-loss rate.

Define numerator and denominator before choosing a target. For availability, if 998,900 out of 1,000,000 eligible requests succeeded within the response deadline, the observed good-event ratio is 99.89%. The team needs to define whether client cancellations, malformed requests, planned maintenance, test traffic, retries and dependency failures belong in the denominator. Excluding an event does not make the user impact disappear; exclusions should match the service contract and be visible to stakeholders.

Use a measurement boundary that reflects the user journey. A server-side counter can miss failures that occur before the request reaches the server. A synthetic probe can catch route-level failure but may not represent user authentication, payloads, device, geography or real dependency behavior. Combine indicators when needed and specify which one controls the objective. Do not let the easiest metric stand in for service health if it diverges from the user outcome.

For latency objectives, a percentile alone can hide how many events were slow and can change unexpectedly with low sample counts. Define a threshold-based ratio when the goal is “X% of eligible requests complete within Y.” Histograms or suitable event distributions can support percentile analysis, while means are useful for aggregate capacity but do not describe tail experience. For a multi-step transaction, measure the end-to-end operation and track component signals separately to locate causes.

Telemetry is part of the contract. Identify the instrument, labels, clock assumptions, aggregation rule, scrape or export interval, retention and treatment of missing data. Avoid high-cardinality labels such as unbounded customer IDs in metrics. If a monitoring gap makes the ratio unavailable, mark the objective unknown or conservatively failed according to policy; do not treat missing samples as good events.

## Set objectives and calculate the budget

Choose targets with product, operations and engineering stakeholders. The target should reflect user expectations, business impact, alternatives and cost to improve reliability. A target that is too easy fails to guide investment; an unreachable target creates permanent exception pressure. Define the service boundary, SLI query, window, target, data source, owner and review date together. Start with a measured baseline, but do not automatically set the objective to yesterday's performance.

Suppose the order API's availability SLO is 99.9% over a rolling 30-day window and it receives 1,000,000 eligible requests. The allowed bad-event ratio is 0.1%, so its request-based error budget is 1,000 bad events. If 400 eligible requests fail, the service has spent 40% of that window's budget. The error budget is the tolerated shortfall implied by the SLO, not a pile of guaranteed extra capacity or permission to harm users.

For a target `S` expressed as a good-event fraction and observed good-event ratio `G`, the remaining budget fraction of the original budget is approximately `(G - S) / (1 - S)` while `G` remains above `S`. In practice, calculate from the SLI's actual eligible and bad-event counts and the agreed rolling or calendar window. For request-based objectives, budget consumption varies with traffic; for time-based availability, use the appropriate duration-based measure. Do not mix event-based and time-based denominators as if they were interchangeable.

Use the objective to make a shared risk decision. When the budget is healthy, teams can make changes under normal safeguards. When consumption accelerates, slow or narrow risky changes, improve diagnosis and prioritize reliability work. If the budget is exhausted, an agreed policy may pause routine changes while allowing urgent security fixes, critical customer fixes or changes that reduce incident impact. Specify who decides, what constitutes an exception, how long a restriction lasts and what evidence permits normal release flow to resume. An error budget is a decision mechanism, not an automatic freeze law.

Do not set one target for every endpoint just because it is easy to dashboard. A rarely used administrative export and a core order submission path may have different user consequences. Keep the number of SLOs small enough to maintain and use a hierarchy of service-level goals where stakeholders need both an end-to-end result and critical component objectives. Revisit boundaries when product behavior or dependency ownership changes.

## Alert on actionable budget risk

An alert should tell a responder what user-impacting condition needs attention and what action they can take. Paging on every raw error or every budget fluctuation trains people to ignore alerts. A burn rate compares the current bad-event ratio with the allowed bad-event ratio: a burn rate of 1 means the budget is being consumed at exactly the rate that would exhaust it by the end of the SLO window if it continued. Larger values indicate faster consumption, but a short noisy burst should not necessarily page.

Use multiple windows and thresholds to balance speed with confidence. As an illustrative starting point for a 30-day SLO, a 14.4x burn observed over both a one-hour and five-minute window corresponds to roughly 2% of budget consumed over one hour. A longer six-hour/30-minute pair at 6x corresponds to about 5% consumed over six hours. These are examples from Google's SRE Workbook, not universal thresholds. Tune for user impact, traffic volume, expected response time and the organization's on-call capacity. Low-traffic services need special treatment because a single request can distort a short-window rate.

Keep paging and reporting separate. A page means a human should act now; a ticket means follow-up can wait; a dashboard or log supports analysis without interrupting a responder. Alert on sustained budget burn, loss of the telemetry needed to assess the SLO, and high-impact symptoms that do not appear in the selected indicator. Link each page to the service, current user impact, relevant graph, owner and runbook.

For DispatchDesk, the team replaces the “pods available” objective with an order-submission SLI measured at the public API boundary. A 99.9% rolling 30-day target yields a 0.1% request error allowance, but the first dashboard omits requests rejected by an unhealthy authentication dependency. Users still experience those as failed submissions. The team corrects the denominator, adds an explicit correctness check for persisted orders, and records how client cancellations are classified. During a downstream slowdown, the multiwindow burn alert fires while a synthetic transaction confirms the user journey is degraded. The on-call narrows rollout traffic, follows the dependency runbook and communicates the incident. Product and engineering review budget consumption and planned work together after recovery rather than blaming a single team for crossing a number.

Exercises:

1. A service reports 99.99% pod availability while users see failed requests. Which boundary and event definitions would you use to define a better SLI?
2. A 99.9% request SLO covers 500,000 eligible requests in its window. How many bad events consume the full request budget, and what can make the apparent ratio misleading?
3. A low-volume internal service has one failed request during a quiet hour. Why might a short-window burn-rate page overstate sustained risk, and what additional signals could help?
4. The budget is exhausted, but a security fix must ship. What should the error-budget policy say about this case, the decision owner and verification?

Answer guidance: measure the operation at the client-visible service boundary and define valid response/deadline, eligible requests and exclusions; a 0.1% budget permits 500 bad events, subject to those definitions and measurement quality. Low sample counts make rates volatile, so combine longer windows, synthetic checks or consequence-sensitive signals without hiding the error. Document an emergency-change exception that narrows scope, adds safeguards and confirms the security fix and service behavior.

Review questions:

- How do SLI, SLO and SLA differ?
- What choices determine whether an availability ratio represents user experience?
- How does an error budget support decisions without becoming a rigid release ban?
- Why can multiwindow burn alerts be more useful than paging on a short error spike?

Takeaways:

- Define reliability from user-visible behavior with an explicit denominator, data source and window.
- Set targets with stakeholders and translate the objective into a budget using the correct event or time unit.
- Use budget consumption to guide risk and engineering priorities under an agreed policy.
- Alert on actionable, sustained risk and telemetry failure; tune short-window signals for traffic and impact.

## Sources checked 2026-10-04

- [Google SRE: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — SLI/SLO concepts, measurement choices and objective setting.
- [Google SRE Workbook: Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/) — multiwindow, multi-burn-rate alerts and low-traffic considerations.
- [Google SRE Workbook: Error Budget Policy](https://sre.google/workbook/error-budget-policy/) — example policy tying budget state to release and reliability decisions.

Targets, alert thresholds and policies are illustrative; organizations should derive them from their users, traffic, service contracts and responder capacity. No production telemetry or alert rule was queried or deployed.
