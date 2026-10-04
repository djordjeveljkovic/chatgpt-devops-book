# Independent review — Chapter 134

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: f0fe5d0eb1b07c3dc366cbebd0c3373fd7b191ed83b29013e5471d4642482560

## Inspection scope and findings

Read current full body and compact summary, Chapter134 brief and authoring guide. Compared with reviewed Chapter133 and Chapter136 brief/context (Chapter136 full substantive body not yet available). No material technical finding. Chapter134 provides strategy/overlap choice and incidents rather than duplicating133's configuration fragment and cloud release procedure; schema discussion remains a short pointer to136.

ECS/Kubernetes patterns are qualified rather than claiming a Deployment blue-green enum. Rolling availability/surge and parallel-pool capacity, readiness versus business transactions, DNS/connection persistence, queue side effects and session compatibility are sound. Routing rollback is distinguished from shared-state repair and old-version compatibility. Recovery preserves identity/events and permits repair-forward when state changed. No command/configuration mutation example is present. Exercises have sound answer guidance and takeaways. Platform API/controller semantics do not require distro package instructions in this chapter.

Low — Failure diagnosis first paragraph: make the incident concrete by specifying a positive maxUnavailable that intentionally permits old-Pod termination before pending replacements become available; insufficient surge capacity alone does not override maxUnavailable0. Replace “insufficient memory requests for the available nodes” with “memory requests exceed available schedulable memory.” The surrounding advice to inspect availability settings, pending events and capacity is sound but this wording is awkward.

Low — exercise3/answer3 and diagnosis: distinguish PDB/node-drain disruption from Deployment rollout controls. Kubernetes explicitly says Deployment rolling updates are not constrained by PDBs; maxUnavailable/maxSurge govern that update. Inspecting concurrent disruption evidence is useful, but readers should not infer a PDB fixes or blocks this rollout.

Low — summary claims relative links to132/137, but those mentions are plain text. Existing133/136 relative links pass; convert132/137 or narrow summary claim. These optional precision/link findings do not block technical approval.

## Primary evidence checked 2026-10-04

- [Kubernetes Deployment](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/): availability/surge, controller overlap, progress and workload rollback.
- [Kubernetes disruptions](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/): PDB constraints apply to eviction workflows, not Deployment rolling updates.
- [ECS deployment strategies](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_service-options.html): controller-specific rolling/traffic strategies, checked during adjacent Chapter133 review and retained for comparison.
- [ECS blue-green workflow](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/blue-green-deployment-how-it-works.html): concurrent revisions, traffic routing and validation.

## Validation and limits

`python3 tools/check_book.py --chapters 134-134` passed: one chapter and1,414 global local links; no errors/warnings. Hash computed with tools.promote_reviewed.body_hash matches supplied value. No ECS/Kubernetes rollout, Service/ingress swap, target group, DNS change, traffic test, queue/session/database state, capacity test or recovery execution. No version/controller/OS matrix tested. Chapter136 final-body overlap cannot yet be assessed; its intended canonical scope is respected by this body. Static links/documentation do not establish live rollout availability or traffic reversal. Only this review record written.

## Final bounded refresh — 2026-10-04

Inspected corrected incident, PDB/controller distinction and relative links against the original optional notes. Positive maxUnavailable1 now explains permitted old-Pod removal; memory requests exceeding schedulable capacity accurately explain Pending. Explicit PDB eviction-versus-Deployment distinction resolves that precision gap. Chapters132/137 now have relative links and accurately scoped context. All optional findings resolved, no remaining material finding. Current hash recomputed and matchesf0fe5d0eb1b07c3dc366cbebd0c3373fd7b191ed83b29013e5471d4642482560. Focused checker passed; earlier documentation evidence, Chapter136 future-body comparison limit and all runtime limits remain. No rollout or infrastructure action; only this separate review record changed.

Verdict: approved
