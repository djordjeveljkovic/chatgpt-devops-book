---
book: The Complete DevOps Engineering Book
volume: 19
volume_title: "Site Reliability and Recovery"
chapter: 188
title: "Chaos and Resilience Experiments"
slug: chaos-and-resilience-experiments
status: complete
summary: ../../_ai/chapter-summaries/188-chaos-and-resilience-experiments.md
---

# Chapter 188 — Chaos and Resilience Experiments

**Section outline:** test a falsifiable failure hypothesis under controlled conditions; limit targets and duration with independent stop signals; inspect recovery and apply evidence to reliability work.

## Test a resilience assumption deliberately

DispatchDesk's production architecture diagram says that one worker failure does not stop order processing. The team has never tested the assumption. During a regional event, all workers in one zone restart together, and the queue stops draining because the remaining consumers share a hidden dependency. A resilience experiment could reveal this failure mode earlier, if it is designed with an explicit safety boundary and reliable stop path.

Chaos engineering is a disciplined experiment in which a controlled fault is introduced to test a stated hypothesis about system behavior. It is not random breakage or a substitute for ordinary testing, monitoring, backups or capacity planning. The experiment should tell the team whether a resilience mechanism works, where its assumptions end and what evidence justifies a change.

## State a hypothesis and safety envelope

Write a hypothesis in observable terms: “If one of three queue consumers becomes unavailable for five minutes, the remaining consumers keep order completion within the SLO, the queue age stays below the recovery limit, and the failed consumer rejoins without duplicate processing.” Specify steady state before injection: user SLI, queue age, error rate, dependency saturation and expected operating range. Define how each signal is measured and confirm that alerting sees the target system before any experiment begins.

Choose the smallest useful target and fault: one isolated test instance, a staging namespace with representative data shape, a canary slice or a single failure domain. Define inclusions and exclusions precisely. Confirm customer, data, provider, security and change-management authorization, along with an experiment owner and an incident commander or stop authority. Set duration, start/end window, affected service, concurrency and cleanup. A narrow selector can still match the wrong resources if labels or filters are stale; preview and independently verify the target set.

Establish preconditions: service within steady-state bounds, sufficient capacity, healthy backup/recovery path, alert delivery tested, relevant responders available, no conflicting production maintenance, provider quota understood and an unambiguous manual stop route. An experiment that begins during a real incident or cannot be stopped safely should not start. Keep experiment permissions scoped to the selected resources and action types; the tool's role should not have unrelated account-wide mutation rights.

Create stop conditions tied to user impact and safe system limits. Examples include order SLI burn above a threshold, queue age beyond the recovery objective, database saturation, error rate, loss of observability or an unexpected target count. A stop condition is useful only if its signal is timely and independent of the injected failure. A monitor that depends on the same broken network path may not report the condition. Define manual abort criteria too, including responder uncertainty or collateral effects. Stop first and investigate later when the safety boundary is crossed.

## Run the experiment and verify restoration

Progress from low risk to higher risk: a paper review, deterministic unit/integration test, isolated fault simulation, staging experiment, limited canary and only then an explicitly authorized production experiment if risk warrants it. Change one failure mode at a time. Observe the full user path as well as internal metrics. Compare against the stated steady state before, during and after injection. If the hypothesis is not met, record the failure without extending the experiment beyond its approved boundary.

A tool can stop injecting a fault without restoring the application to its original state. Verify the target recovered, queues drained, temporary rules or resources were cleaned up, traffic returned to the expected path and no data inconsistency remained. Review whether a stop condition fired, whether an experiment action completed or failed, and whether the responder could identify the condition. A stopped experiment is not automatically a successful recovery.

AWS Fault Injection Service (FIS) models an experiment as actions, targets, stop conditions and an IAM role. Its stop conditions can use CloudWatch alarms, and a triggered stop ends the experiment rather than pausing it for resumption. FIS performs real actions against actual AWS resources, so a template is not a harmless simulation. Start in a preproduction environment and verify resource selection, permissions, stop alarms and cleanup before an authorized production run. Other frameworks have different scope, rollback and safety mechanics; read the exact version's documentation.

Record the experiment ID, owner, approved hypothesis, template/policy version, tool version, selected targets, authorization, start/end time, steady-state measurements, injected fault, alerts, stop reason, observations, recovery evidence and action items. Keep customer data and secrets out of public reports. A successful experiment supports only the tested fault, scope, environment, duration, version and load conditions. It does not establish resilience against every correlated failure.

For DispatchDesk, the team first simulates one worker loss in an isolated staging environment. The hypothesis predicts that two consumers keep queue age under ten minutes and that the restarted worker does not duplicate orders. The test reveals the consumers share a lease service, so the remaining workers slow even though their process health is green. The team records the measured queue age and duplicate checks, stops the experiment before exhausting the test queue, restores the lease service and verifies the backlog drains. They change the architecture and alerting, then repeat the same bounded test. They do not claim production-zone resilience from the staging result; a later production exercise would require separate authorization, targeted scope and independently monitored stop conditions.

Exercises:

1. A team proposes “randomly delete pods in production to see what happens.” What hypothesis, target, steady-state and authorization details are missing?
2. A stop alarm depends on metrics routed through the network path that the experiment disrupts. What failure does this create in the safety design?
3. An experiment stops when a threshold is crossed, but the injected fault remains active in one resource. What should responders do before declaring the exercise complete?
4. A staging experiment succeeds under low traffic. Which limits should appear in the report before anyone generalizes the result?

Answer guidance: define one predicted failure response, exact resource set, load/user signals, duration, owner, business authorization, abort criteria and cleanup before choosing an injection. Use an independent monitoring and manual stop path. Stop further actions, isolate or reverse the fault through the authorized recovery procedure, verify system state and data, and treat unexpected persistence as an incident if impact warrants. Record environment, traffic, resource count, software/tool versions, duration, dependencies and untested correlated failures.

Review questions:

- What distinguishes a resilience experiment from random production disruption?
- Which safety controls must be independent of the injected fault?
- Why does stopping an experiment not prove that recovery completed?
- How narrowly should results be generalized?

Takeaways:

- Use a falsifiable hypothesis with user-facing and internal success measures.
- Bound targets, fault duration, permissions, authorization and stop conditions before injection.
- Verify cleanup, data integrity and service recovery after the tool reports an experiment stopped.
- Record scope and limits; repeat after changes and do not overgeneralize a single result.

## Sources checked 2026-10-04

- [AWS FIS stop conditions](https://docs.aws.amazon.com/fis/latest/userguide/stop-conditions.html) and [experiment templates](https://docs.aws.amazon.com/fis/latest/userguide/experiment-templates.html) — steady state, targets, IAM role and alarm-driven stopping.
- [What is AWS FIS](https://docs.aws.amazon.com/fis/latest/userguide/what-is.html) — FIS performs real actions and recommends planning and preproduction testing.
- [Chaos Mesh experiment scope](https://chaos-mesh.org/docs/2.6.7/define-chaos-experiment-scope/) — explicit selector scope and blast-radius control for the cited version.
- [Chapter 187 — Disaster Recovery and Failback](187-disaster-recovery-and-failback.md) — recovery objectives and failover context.

The DispatchDesk test is fictional. No fault was injected and no AWS account, Kubernetes cluster, production workload or experiment tool was accessed.
