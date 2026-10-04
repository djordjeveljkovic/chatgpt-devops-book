# Chapter 133 continuation

Status: complete

## Written material

AWS release identity and distinct ECS/EKS control planes; ECS task-definition revisions, service updates, roles, rolling circuit-breaker bounds and staged traffic strategies; EKS Deployment manifest pinned to digest, rollout policy, capacity/readiness semantics and context/RBAC checks; multi-account staged promotion; failure diagnosis for ECS image pulls, EKS scheduling/readiness, IAM and network; rollback boundaries; exercises, answer guidance, review questions and takeaways.

## Concepts and terminology

ECS task-definition revision, ECS deployment controller/strategy, task execution role, application task role, Kubernetes Deployment revision, readiness, rollout progress, ECR image digest, staged promotion, cross-account artifact identity.

## Examples and cross-references

Fictional DispatchDesk API deployed either as an ECS service or an EKS Deployment. Relative links connect Chapters 93, 131, 132 and 137. Assumes existing AWS accounts, registry, service or cluster, networking and identity; no infrastructure is created.

## Open threads

Independent reviewer approved the final body hash after the two low cross-reference findings were resolved with links to prerequisite Chapter 132 and forward GitOps Chapter 137. No AWS API call, task launch, cluster apply, registry copy or live health check was executed.

## Exact next section

None. Independently approved; continue to the next unfinished chapter.

## Verification

AWS ECS service deployment strategies/circuit breaker and EKS/Kubernetes rollout docs checked 2026-10-04. `python3 tools/check_book.py --chapters 133-133` passed one YAML parse and 1,411 global local links; no errors or warnings. `git diff --check` passed. Static parsing does not establish AWS service acceptance, identity access or workload readiness.
