# Independent review — Chapter 157

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: ca66c6b8dc1d4f1ebcb60a807d93590f958f9d8c994ba1008395ad974c025e19

## Scope and findings

Read full current manuscript, compact summary, Chapter 157 brief and authoring-guide requirements with Chapter 156 prerequisite context. Reviewed feedback arithmetic, complete teaching simulation, autoscaling/v2 object and commands, ECS target-tracking boundaries, signal selection, diagnosis/recovery, exercises, takeaways and links. No material technical issue found. Summary accurately describes the examples and unperformed controller/cloud validation.

Arithmetic is correct: (48 − 4 × 6) × 90 = 2,160 excess attempts over the startup interval; six five-job/s workers with twenty arrivals/s provide ten jobs/s net drain, so 1,000 jobs require 100 seconds under stated stable assumptions. The controller model separately tracks ready and pending allocations, processes a bounded time-step capacity, includes backlog in its recommendation, clamps desired count and removes at most one ready replica after the chosen hold. Printed requested and ready fields are explicitly identified as pre-action and post-action observations. This is a teaching model, not an implementation of HPA stabilization, cooldown, observation history or real startup failure.

HPA schema and resource CPU target are structurally correct for autoscaling/v2. CPU utilization is relative to requests; the prerequisite metrics/API/access and existing Deployment are explicit. The two-pod scale-up and one-pod scale-down policies use sixty-second rate windows; downscale stabilization is 300 seconds and up stabilization zero. These constrain controller changes rather than guaranteeing startup delivery. Missing metrics/readiness/capacity remain operational evidence requirements. Applying mutates staging; context/ownership checks precede it. Server dry-run is correctly distinguished from a load/metrics test. Deleting the newly created HPA does not reset Deployment replicas, and restoration is assigned to the owning deployment mechanism.

ECS requested versus healthy running capacity, cooldown/deployment interaction and signal suitability are appropriately qualified. The chapter makes no unsupported claim that cooldown blocks all corrective action, that missing data proves low demand, or that task count bypasses capacity/quota limits. Floors and ceilings protect different requirements; ceiling saturation still requires admission/alerting. Recovery avoids fighting an active controller and requires recorded automation resumption. Queue age and correctness remain outcome metrics rather than automatically safe control signals. Exercises provide answer guidance and closing takeaways are substantive.

Low observations:

- HPA prerequisite paragraph: explicitly include sidecars among containers needing CPU requests for this Resource metric. Missing requests in contributing containers can make pod CPU utilization undefined; “every relevant application container” is less precise than the documented all-container requirement.
- Opening: add the concise bespoke section outline requested by the authoring guide. Existing actual sections and content are complete.
- Atlas policy explanation: explicitly name downscale stabilization as selecting the highest recent recommendation, and policy periodSeconds as a rolling change-rate window. Existing wording is correct but this would distinguish stabilization from a simple unconditional five-minute wait.

## Primary evidence checked 2026-10-04

- [Kubernetes HPA](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/): autoscaling/v2 resource utilization, request/metric readiness handling, scaling policies and downscale stabilization. Current documentation must not substitute for a target server's schema.
- [ECS service autoscaling](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-auto-scaling.html): desired versus running capacity, bounds and deployment/cooldown behavior.
- [ECS target tracking](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-autoscaling-targettracking.html): metric-driven capacity and deployment scale-in boundaries.

## Validation and limits

`python3 tools/check_book.py --chapters 157-157` passed one Python syntax check, one YAML parse, two shell syntax checks and 1,447 global local links with no errors/warnings. Exact body hash computed with `tools.promote_reviewed.body_hash`. Arithmetic/code/schema inspected statically. No simulation output presented as measured, HPA apply/server dry-run, API schema discovery, ECS policy change, metric adapter/controller run or load experiment executed. No cluster/provider/version runtime matrix tested. YAML parsing and documentation cannot prove server acceptance, useful metrics, startup latency, ready capacity or workload recovery. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed the added section outline, clarified Resource CPU metric paragraph, stabilization/policy explanation and source-date update against the earlier official HPA evidence. All three optional manuscript observations are resolved. Every measured container's CPU requests and sidecar contribution are now explicit; the ContainerResource alternative is appropriately gated on supported API capability. Downscale stabilization correctly uses the highest recent desired recommendation, separate from the rolling policy change-rate window. Default largest-change policy selection and the two-pod per-minute scale-up limit accurately explain the unchanged manifest. The outline matches the chapter's sequence. No material issue introduced.

Fresh body hash computed with `tools.promote_reviewed.body_hash`: ca66c6b8dc1d4f1ebcb60a807d93590f958f9d8c994ba1008395ad974c025e19. `python3 tools/check_book.py --chapters 157-157` again passed one Python syntax check, one YAML parse, two shell syntax checks and 1,447 local links without errors/warnings. Earlier source assessment and runtime/controller/cloud limits remain applicable.

Low observation — summary Open threads still lists the now-completed outline and HPA clarifications. Remove those completed tasks during summary maintenance. Only this separate review record updated.

Verdict: approved
