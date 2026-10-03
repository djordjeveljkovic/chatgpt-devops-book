---
book: The Complete DevOps Engineering Book
volume: 11
volume_title: "Kubernetes Foundations"
chapter: 104
title: "Deployments, ReplicaSets and Jobs"
slug: deployments-replicasets-and-jobs
status: complete
summary: ../../_ai/chapter-summaries/104-deployments-replicasets-and-jobs.md
---

# Chapter 104 — Deployments, ReplicaSets and Jobs

## Controllers and ownership

Use a Deployment for a long-running, usually stateless application that needs a desired replica count and controlled updates. The Deployment controller manages ReplicaSets; each ReplicaSet maintains a matching set of Pods from its template. A Job manages Pods that should complete finite work. A CronJob creates Jobs on a schedule. These controllers express different lifecycle contracts. A Deployment is not just a convenient Pod wrapper: it owns update history and coordinates replacement across ReplicaSets.

The Deployment's selector must match its Pod template labels. Selectors are how controllers find Pods, and overlapping selectors can make controllers adopt or delete each other's Pods. Treat labels as API-level ownership wiring. Give every workload a specific selector, avoid manually creating Pods with that label, and do not share a selector across Deployments. The Deployment controller adds a `pod-template-hash` label to separate its ReplicaSets; do not set it yourself. Kubernetes explains the [Deployment and ReplicaSet relationship](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) and [ReplicaSet matching behavior](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/).

A minimal Deployment might declare three `DispatchDesk` API replicas:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dispatchdesk-api
  namespace: production
  labels:
    app.kubernetes.io/name: dispatchdesk
    app.kubernetes.io/component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: dispatchdesk
      app.kubernetes.io/component: api
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  template:
    metadata:
      labels:
        app.kubernetes.io/name: dispatchdesk
        app.kubernetes.io/component: api
    spec:
      containers:
        - name: api
          image: registry.example.invalid/dispatchdesk/api@sha256:REPLACE_WITH_VERIFIED_DIGEST
          ports:
            - name: http
              containerPort: 8080
          resources:
            requests:
              cpu: 500m
              memory: 512Mi
```

The repository and digest in this teaching manifest are placeholders. Replace the entire image reference with the reviewed artifact digest that the registry actually serves. The example omits probes, configuration, security context and service account so the rollout fields stay visible; a production manifest must add the complete application contract. `maxUnavailable: 0` attempts to keep all three desired replicas available during an update, while `maxSurge: 1` lets the Deployment controller account for one extra Pod during the rollout. This is not a strict ceiling on all live Pods or resource use: terminating old Pods can overlap with replacements while their grace periods finish. The cluster must have capacity and quota for the rollout overlap. If no spare capacity exists, the rollout can stall rather than reducing the availability target.

When a Pod template field changes, the Deployment creates a new ReplicaSet for that template and scales old and new ReplicaSets according to strategy. Changing only Deployment metadata outside `.spec.template` does not necessarily change Pods. Scaling `.spec.replicas` changes desired count without creating a new template revision. If a HorizontalPodAutoscaler manages replica count, do not keep a competing fixed `replicas` value in the applied configuration; the two writers can overwrite each other. Keep a single authoritative management path, such as a GitOps controller or reviewed manifest workflow.

ReplicaSets are usually managed indirectly through Deployments. Editing a ReplicaSet directly can conflict with the Deployment controller, and editing a child Pod does not make a new Deployment revision. To change the running template, change the Deployment's `.spec.template` through its source of truth. To inspect ownership, use `kubectl get rs,pods -o wide --show-labels` and `kubectl describe` on the named owner. The `ownerReferences` field captures controller ownership; labels answer selection questions but are not identical to ownership. See [Chapter 103](103-pods-and-application-lifecycles.md) for Pod identity and [owner and dependent objects](https://kubernetes.io/docs/concepts/overview/working-with-objects/owners-dependents/).

## Rollouts, Jobs and CronJobs

A rolling update trades deployment speed, temporary capacity and unavailable replicas. `maxSurge` limits extra Pods in the controller's rollout accounting; terminating Pods can overlap and take total live Pods and resource use above that nominal limit. `maxUnavailable` limits how many may be unavailable relative to desired count. Percentages are rounded in directions documented by Kubernetes, which can matter for small replica counts. Neither setting proves that requests are served successfully. Readiness behavior determines when a Pod is considered available; application compatibility and downstream capacity still determine whether a new version is safe. [Chapter 107](107-probes-and-graceful-termination.md) covers readiness and graceful termination.

Track rollout progress instead of assuming an apply finished the deployment:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  rollout status deployment/dispatchdesk-api --timeout=120s
kubectl --context kind-dispatchdesk --namespace production \
  get deployment dispatchdesk-api
kubectl --context kind-dispatchdesk --namespace production \
  get replicasets -l app.kubernetes.io/name=dispatchdesk
kubectl --context kind-dispatchdesk --namespace production \
  get pods -l app.kubernetes.io/component=api -o wide
kubectl --context kind-dispatchdesk --namespace production \
  rollout history deployment/dispatchdesk-api
```

Save the manifest as `deployment.yaml` after replacing the image placeholder with a verified digest. The following commands create the namespace, apply the Deployment and then inspect its rollout. They change the selected local cluster; do not run them against a production context without an approved change:

```bash
kubectl --context kind-dispatchdesk create namespace production
kubectl --context kind-dispatchdesk --namespace production apply -f deployment.yaml
```

The namespace creation command fails if that namespace already exists; in that case, verify the existing namespace and continue with the apply. The rollout commands assume the Chapter 102 local cluster context and this manifest has been applied. Use an explicitly selected environment rather than copying this namespace into a real production context. No output is asserted because the commands were not run.

After saving any diagnostics needed for the lab, remove only the Deployment created for this exercise:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  delete deployment dispatchdesk-api
```

This removes its ReplicaSets and managed Pods. Delete the `production` namespace only if you created it for this isolated lab and have verified it contains no other resources; namespace deletion removes everything in it. Leave the namespace intact when it pre-existed or is shared.

Suppose a new image digest is applied and one new Pod repeatedly fails its readiness check. The Deployment may report `ProgressDeadlineExceeded` or remain below the desired available count. Compare current and desired template, inspect the new ReplicaSet and Pod events, and read the container logs. A wrong digest can cause image pull failures; a valid image can still fail on configuration or startup. If the release is harmful, the following command changes the named Deployment template back to a prior recorded revision in the intended local cluster:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  rollout undo deployment/dispatchdesk-api
kubectl --context kind-dispatchdesk --namespace production \
  rollout status deployment/dispatchdesk-api --timeout=120s
```

The first command does not reverse database migrations, customer writes or external side effects. Confirm backward compatibility and data state before using rollback; then verify the replacement Pods become available. The [rolling update guide](https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/) explains strategy behavior.

Use a Job when the workload has a finite goal: export a report, process a bounded backfill, or run a one-time data check. `completions` describes how many successful Pod completions are required; `parallelism` controls how many may run at once; `backoffLimit` bounds retries; `activeDeadlineSeconds` can cap total runtime. Choose `restartPolicy: Never` when you need separate failed Pod records, or `OnFailure` when restarting the container in a Pod is appropriate. Job retry does not guarantee exactly-once application effects. A worker can write a result and lose its acknowledgment before Kubernetes records success, so make the task idempotent and record progress by stable input key.

For a one-off task, inspect the Job and its owned Pods, logs, exit codes and events. Avoid deleting a failed Pod before collecting diagnostics; a Job may create another attempt, and removing the record can hide why retries occurred. Finished Job history consumes API objects; use an explicit retention policy or TTL after completion where appropriate, but retain enough evidence for operations and audit. The Job controller may start a task more than once even with one completion and `restartPolicy: Never`; do not use it for a non-repeatable side effect unless the application coordinates that effect.

A CronJob creates Jobs according to a schedule. It is suitable for recurring reports or bounded maintenance where a late, skipped or overlapping run has a defined consequence. Select `concurrencyPolicy` deliberately: `Allow` permits concurrent Jobs; `Forbid` skips a new run while the previous Job is active; `Replace` cancels/replaces the existing Job with a new one. These policies apply to Jobs from that CronJob, not other CronJobs or manually created Jobs. Set an explicit time zone when supported by the cluster version and business calendar. Decide whether missed schedules should catch up, be skipped after a deadline, or require operator recovery. Even if Kubernetes avoids duplicates in normal cases, CronJobs can create Jobs more than once; the task must be idempotent. See [Job semantics](https://kubernetes.io/docs/concepts/workloads/controllers/job/) and [CronJob scheduling](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/).

## Choosing a workload controller

For DispatchDesk, API replicas should run under a Deployment: they serve continuously, can be replaced, and usually should not own durable local state. A scheduled reconciliation task may use a CronJob if overlapping runs are safe or explicitly prevented, and each run records its own completion. A notification worker that continuously consumes SQS may fit a Deployment or a managed queue-to-function service; a Job would end after its finite work rather than remain a service. A large backfill with a known input set may use a Job with bounded parallelism and checkpointed/idempotent processing.

The controller choice follows lifecycle and retry semantics, not just the runtime language. Ask: should this process remain active, finish once, or start on a schedule? Is duplicate execution safe? What evidence indicates completion? How are retries bounded? What is the shutdown/data checkpoint contract? How much concurrency can the database and provider tolerate? For cron-style cleanup, also decide whether a missed run should catch up after a cluster outage; a schedule is not a durable queue of every intended occurrence.

During a failed rollout, do not scale a ReplicaSet directly to force a count, delete the newest Pod repeatedly, or change a child image by hand. Those actions fight the owning Deployment or produce mixed versions. Pause or roll back through the Deployment when appropriate, correct the reviewed template/source, and watch the rollout. For a stuck Job, inspect its Pod and logs, compare failure count to `backoffLimit`, verify input progress and determine whether an external write already happened before starting a manual duplicate.

## Exercises and answer guidance

1. A Deployment has three replicas and its rollout adds one Pod, but that Pod remains Pending. What should be checked? Surge capacity, quota, placement constraints and events; do not lower the availability target without an approved decision.
2. An operator patches a Pod image directly, but the Deployment has not changed. Will the controller necessarily create a new rollout? No. Change the Deployment template; direct child edits do not create a Deployment revision and can produce mixed Pods.
3. A Job has one completion and one Pod, but the process may have written its output before failing. Can the Job safely retry? Only if the work is idempotent or can detect/reconcile the prior effect.
4. A CronJob uses `Forbid` and the previous monthly report is still running at the next scheduled time. Will Kubernetes queue an unlimited backlog of missed runs? No. That occurrence can be skipped/missed under the policy and deadline behavior; define how to detect and recover the missing report.
5. A rollout rollback restores the previous image. Does it undo a database schema change? No. Rollback changes the Deployment template; data and external side effects require a separate recovery plan.

Review questions: who owns each Pod, what starts a new ReplicaSet, which availability/capacity tradeoff does rollout strategy encode, and how does each batch controller handle retries and duplicate effects?

## Verification and primary sources

Official Kubernetes Deployment, ReplicaSet, Job, CronJob and rolling update documentation was inspected on 2026-10-04. The manifest is a teaching fragment with a placeholder image digest; no Deployment, Job or CronJob was applied. The kubectl commands were syntax checked but not run against a cluster. No namespace was created, and no rollout, rollback, batch task, schedule, database operation or application side effect was executed. Static checks do not prove selector ownership, cluster admission, image availability, capacity, readiness, timing, job idempotency or recovery behavior.

Primary references: [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/), [ReplicaSets](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/), [rolling updates](https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/), [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/job/), and [CronJobs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/).
