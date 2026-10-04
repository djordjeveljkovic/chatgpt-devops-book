# Chapter 134 continuation

Status: complete

## Written material

Rolling versus blue/green definitions across ECS, EKS/Kubernetes and VPS; mixed-version API, database, message and session compatibility; readiness versus business health; traffic routing and connection/DNS behavior; surge/parallel capacity and costs; strategy selection; DispatchDesk examples; stalled-rollout and misleading-health diagnoses; exercises, answer guidance, review questions and takeaways.

## Concepts and terminology

Mixed-version window, rolling update, blue/green, target health, readiness, `maxUnavailable`, `maxSurge`, traffic cutover, bake period, session affinity, state rollback boundary.

## Examples and cross-references

DispatchDesk ECS/Kubernetes release strategy and incidents. Relative links to Chapters 132, 133, 136 and 137; official ECS and Kubernetes strategy references. Strategies and controller semantics are qualified per platform.

## Open threads

Independent reviewer approved the final body hash after the optional precision and link findings were resolved. The rollout incident states `maxUnavailable: 1`, distinguishes PodDisruptionBudget evictions from Deployment rollout controls, and links Chapters 132 and 137. No cloud rollout, traffic shift, load test, or database operation was executed.

## Exact next section

None. Independently approved; continue to the next unfinished chapter.

## Verification

AWS ECS deployment strategies and Kubernetes Deployment/rolling update/disruption-budget documentation checked 2026-10-04. `python3 tools/check_book.py --chapters 134-134` passed one chapter and 1,417 global local links; no errors or warnings. `git diff --check` passed.
