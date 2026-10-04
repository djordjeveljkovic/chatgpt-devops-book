---
book: The Complete DevOps Engineering Book
volume: 14
volume_title: "Delivery, Deployment and GitOps"
chapter: 140
title: "Rollback, Roll Forward and Release Incidents"
slug: rollback-roll-forward-and-release-incidents
status: complete
summary: ../../_ai/chapter-summaries/140-rollback-roll-forward-and-release-incidents.md
---

# Chapter 140 — Rollback, Roll Forward and Release Incidents

## Why this matters

DispatchDesk has just promoted a release to production. Error rates rise within minutes. The team has to decide whether to restore the previous behavior, correct the defect in a new release, or mitigate the failing dependency while preserving the new version. The right action depends on what failed, what state the release changed, and whether an older application can still operate safely against current data and messages.

Rollback is not a synonym for “make the incident go away.” Reverting an image or manifest does not necessarily reverse a database migration, an emitted event, an external payment, or data already written in a new format. A rollback can also be overwritten by a GitOps controller if the declared state still selects the faulty release. A safe recovery decision considers application versions, schema compatibility, traffic, dependencies, persistent data, and how the change is managed. Chapter 134 covers rollout strategies; Chapter 136 covers compatibility and migration constraints; this chapter organizes the release-incident decision.

## Rollback and roll-forward are different recovery actions

A rollback selects an earlier artifact or configuration known to have worked. It can reduce exposure quickly when the failure is isolated to a reversible application change and the earlier version remains compatible with current state. A roll-forward builds or selects a corrected version and deploys it through the release path. It is usually preferable when a rollback would reintroduce a known defect, conflict with a completed schema change, or require undoing irreversible effects.

Mitigation may be faster than either. Examples include disabling a feature flag, shifting traffic away from a broken region, throttling a producer, scaling a healthy pool, or disabling a problematic integration. These actions reduce impact while the team verifies the durable correction. The choice should be tied to observable evidence: which cohort is failing, what changed, whether data is accumulating or corrupting, whether dependencies are available, and whether the prior version can read the current schema and messages.

Before changing production, identify the release revision, image digest, configuration revision, migration state, and time the failure began. Compare error rate, latency, saturation, and customer impact with the pre-release baseline. Identify a known-good version and ask whether it can safely run against current databases, queues, and APIs. The answer may differ across services: a web tier can roll back while a background worker must stay forward-compatible with messages already produced. A rollback should have a measurable success condition, such as errors returning to baseline and backlog drain stabilizing, plus a stop condition if data integrity worsens.

Avoid deciding from deployment status alone. A rollout can complete while user requests fail. A Kubernetes Deployment can be healthy at the pod level and still fail due to a downstream database. Conversely, a readiness probe can be too strict and mark a usable service unavailable. Use user-facing synthetic checks, application error metrics, dependency telemetry, and representative request traces along with controller status. Preserve the evidence that supports the decision.

## Restore desired state through its owner

In a GitOps environment, the durable source of deployment intent is the reviewed repository revision. If a new manifest selects a bad image digest, a pull request that restores the prior known-good digest provides a traceable change and allows the reconciler to converge. If a controller is still tracking the faulty manifest, a manual live change can disappear at its next reconciliation. During an emergency, an operator may temporarily pause reconciliation or make a direct change under an approved incident procedure, but they must record the change, identify its owner, and reconcile the Git declaration promptly. For controller-specific suspension and resumption behavior, see [Chapter 139](139-flux-in-practice.md) for Flux and [Chapter 138](138-argo-cd-in-practice.md) for Argo CD.

For example, suppose a production overlay at `environments/production/dispatchdesk.yaml` changes image digest in commit `abc1234`, and that change causes elevated HTTP 500 responses. A responder working in a clean checkout with repository write access can create a branch that restores the known-good digest and submit the normal urgent review:

```bash
git switch -c incident/dispatchdesk-restore
git diff -- environments/production/dispatchdesk.yaml
# Edit only the image digest to the last known-good immutable digest.
git diff --check
git diff -- environments/production/dispatchdesk.yaml
```

These commands create a local branch and inspect a focused change; they do not deploy anything. The comment identifies an intentional edit that the operator must make in the checked-out file. Before committing, verify that the target repository and branch are correct, the restored digest exists in the registry, and no unrelated configuration is included. Then follow the organization’s protected review and merge process. The reconciler must report that it applied the new desired revision; separately verify pod readiness, service metrics, and data integrity. If the deployment controller is blocked or stale, diagnose that control path instead of assuming the Git change reached production.

If only one commit needs reversal and the branch is shared, `git revert <commit>` creates a new commit that reverses the earlier patch. It preserves history and is generally the appropriate collaborative action for a published change. For a faulty merge commit, selecting the mainline parent has consequences for future merges, so consult Git’s revert documentation and repository owners before applying `-m`. Rewriting shared branch history with reset or force-push can discard others’ work and confuse reconciliation. A generated revert is also only a source change; it does not automatically roll back external effects or establish application compatibility.

Direct Kubernetes rollback can be a valid emergency tool when the GitOps controller is unavailable or an approved break-glass procedure calls for it. It must be coordinated with the controller. If the desired Git revision continues to specify the faulty pod template, reconciliation can restore it. If you use a direct rollback, record the object, previous and new revisions, operator, timestamp, reason, observed result, and whether reconciliation was paused. Then encode the durable target through the owner of desired state and restore the normal controller policy.

## What Kubernetes rollout undo does and does not do

For a Deployment that is managed directly or under an authorized break-glass procedure, `kubectl rollout undo` asks Kubernetes to restore a prior Deployment pod template revision. Kubernetes keeps a bounded history of ReplicaSets by default; the configured `revisionHistoryLimit` affects how much history remains available. Scaling alone does not create a new pod-template revision. A rollback changes the Deployment template and the normal Deployment controller performs the rollout; the command is not a snapshot restore of the whole application environment.

First inspect the target and rollout history using a current kubeconfig with authorization for the Deployment namespace:

```bash
kubectl -n dispatchdesk get deployment dispatchdesk
kubectl -n dispatchdesk rollout history deployment/dispatchdesk
kubectl -n dispatchdesk rollout history deployment/dispatchdesk --revision=12
```

The final command is an example; replace `12` with a revision shown by the history command. Review which image and pod-template settings that revision contains. If it is the appropriate recovery target and the change is authorized, the following command writes a new desired template to the live API:

```bash
kubectl -n dispatchdesk rollout undo deployment/dispatchdesk --to-revision=12
kubectl -n dispatchdesk rollout status deployment/dispatchdesk --timeout=5m
```

The first command changes cluster state and may conflict with GitOps reconciliation. Coordinate with the reconciler and other operators so another update cannot replace the recovery rollout while it is being assessed. The second waits for the latest Deployment rollout to complete or times out; serialize rollout changes during this observation because a concurrent update can make status refer to a different revision. Success establishes rollout status, not user-facing health. Verify the resulting image digest, ready replicas, controller events, and application metrics. The namespace and exact resource name are part of the target; check context and cluster identity before execution. The rollback may fail if history was removed, an image is no longer pullable, required configuration has changed, or the old version cannot use current data. A successful rollback still requires compatibility and business-level verification.

Deployment history covers the pod template, not all resources in a release. It does not restore a Service, ConfigMap, Secret, Ingress, Helm release, cloud resource, database schema, or message already produced. If a Secret or ConfigMap is mounted by mutable name, old pods may see changed configuration depending on how it is consumed. If an incompatible schema change completed, returning the application binary may worsen failures. Use Git history or the appropriate resource controller to restore declarative configuration, and use a separate tested data-recovery procedure for persistent state.

## Choose rollback or roll-forward with data in mind

Chapter 136’s expand-and-contract sequence makes application rollback safer during a migration: add compatible schema first, deploy code that supports both representations, backfill and verify, switch reads and writes, and remove the old representation only after the rollback window closes. If a destructive contract step has already run, old code may no longer function. At that point, a forward repair, restoration from backup, or carefully planned data migration may be safer than restarting an old binary.

Messages create a related compatibility window. A newer producer may emit a field or semantic value that an older consumer does not understand. Rolling a worker back without draining or replaying incompatible messages may create a poison-message loop or data loss. Pause or rate-limit production if needed, preserve messages, and determine which versions can read the queue before changing consumers. Replays must account for idempotency and external side effects. Feature flags can reduce exposure quickly, but disabling a flag does not erase work already done while it was enabled.

Use a roll-forward when the defect is narrow and a corrected build is available, or when data changes make the prior binary unsafe. A forward fix should be the smallest change that mitigates the cause and can be evaluated with explicit evidence. It is not a reason to skip review: emergency review may be abbreviated by policy, but the exact artifact, configuration, tests, rollback limits, and approver should still be recorded. After immediate recovery, perform the missing validation and return to the standard promotion path.

## Release incident procedure

1. **Stabilize impact.** Declare incident ownership, identify affected users and regions, and use a low-risk mitigation if one is clear. Preserve logs, traces, metrics, deployment events, and release metadata before retention or retries erase context.
2. **Identify the change.** Record source revision, artifact digest, configuration revision, rollout time, feature-flag state, schema or message changes, and the last known-good behavior. Compare affected and unaffected cohorts.
3. **Check reversibility.** Establish whether the old binary can read current data and messages; whether external side effects occurred; whether the old image and configuration are still available; and whether a revert will be reconciled or overwritten.
4. **Choose the recovery action.** Roll back the selected artifact/configuration, roll forward with a bounded fix, or keep a mitigation while investigating. State the expected metric change and a time to reassess.
5. **Apply through the owner.** Use Git and the reconciler for normal durable changes. Use direct API changes only through the incident break-glass process, then record and reconcile them. Avoid unreviewed mass changes across environments.
6. **Verify recovery.** Confirm controller revision and rollout, application errors and latency, dependencies, queue backlog, and data integrity. Watch through at least the relevant traffic and processing cycle; a brief green dashboard can hide delayed work.
7. **Close the loop.** Restore paused automation, document why the selected action worked or failed, rotate exposed credentials if needed, and add detection, compatibility tests, or rollback automation that addresses the actual gap.

This procedure does not require a single organization-wide rollback threshold. A low-volume internal service may tolerate a staged investigation; a payment path may need immediate traffic isolation. Define decision authority and customer-impact thresholds before an incident, and keep the actions consistent with the service’s recovery objectives.

## Exercises with answer guidance

1. A GitOps-managed Deployment has the wrong image, and `kubectl rollout undo` briefly restores service before the image changes again. Why? The desired Git revision still declares the faulty pod template, so reconciliation reapplies it. Make a reviewed desired-state change selecting the known-good digest; if the controller is unavailable, coordinate any direct mitigation and later restore the Git target.
2. A migration has removed the old database column, and the previous application version fails on startup. Should the team keep rolling back? No. Determine whether restoring the column/data is safe and available. A forward-compatible application fix or planned data restore may be required; an old binary is no longer a known-safe rollback target.
3. A Deployment rollout undo reports success, but customers still see errors. What does the command prove? It only indicates the Deployment template rollback and rollout status, depending on the command result. Check actual image and ready pods, application metrics, downstream dependencies, configuration objects, data, and user-facing synthetic tests.
4. During an incident, an operator scales a workload and pauses a reconciler. What follow-up prevents hidden drift? Record the exact action and owner, decide whether the scale change should persist, encode the target in Git if so, verify that the controller applies it, and explicitly resume reconciliation while confirming service health.

## Review questions

- What evidence distinguishes a safe rollback from a dangerous one?
- How does roll-forward differ from rollback, and when can mitigation be faster than both?
- What state does `kubectl rollout undo` restore for a Deployment?
- Why can a Git revert fail to reverse a database migration or external side effect?
- How should responders coordinate a direct cluster change with a GitOps controller?
- What recovery evidence should be checked after a rollout reports success?
- Which release decisions should be made before an incident rather than during one?

## Takeaways

- Choose a recovery action based on impact, failure cause, artifact availability, data compatibility, and external side effects.
- Use Git history and the reconciler to make durable GitOps changes; direct live changes need explicit break-glass ownership and reconciliation follow-up.
- Kubernetes Deployment rollback restores a prior pod template revision, not the entire environment or persistent data.
- A Git revert is a new source-history change. It cannot undo database writes, messages, or external actions by itself.
- Define success and stop conditions, preserve evidence, and verify service health after the controller reports a successful rollout.
- Practice the recovery path and define decision authority before release incidents occur.

## References

- Kubernetes, [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) and [`kubectl rollout undo`](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_undo/), accessed 2026-10-04.
- Git, [`git revert`](https://git-scm.com/docs/git-revert), accessed 2026-10-04.
- Chapters [136](136-database-and-message-compatibility.md), [137](137-gitops-principles-and-reconciliation.md), and [138](138-argo-cd-in-practice.md) in this volume.
