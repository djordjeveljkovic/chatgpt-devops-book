---
book: The Complete DevOps Engineering Book
volume: 14
volume_title: "Delivery, Deployment and GitOps"
chapter: 133
title: "Container Deployment to AWS"
slug: container-deployment-to-aws
status: complete
summary: ../../_ai/chapter-summaries/133-container-deployment-to-aws.md
---

# Chapter 133 — Container Deployment to AWS

## Carry one release identity into the cloud

An AWS deployment is a sequence of decisions across an artifact registry, an identity system, network paths, a scheduler, and a traffic entry point. A successful API request that updates a service is not proof that customers now run the intended release. Tasks may be unable to pull the image, Pods may be unschedulable, health checks may fail, or the new version may start but reject real requests. A controlled cloud release binds the same artifact identity from Chapter 131 to a specific service or Kubernetes workload, then records rollout and application evidence before progressing.

AWS offers two common container control planes with different contracts. Amazon ECS manages tasks and services through ECS APIs and task-definition revisions. Amazon EKS runs the Kubernetes API; teams submit Deployments, Services and related objects through Kubernetes tools. Both can run digest-pinned images from Amazon ECR, but an ECS task definition is not a Kubernetes manifest and the identity permissions are not interchangeable. [Chapter 93](../10-aws-production-services/093-ecs-and-fargate-services.md) explains ECS tasks, roles, networking, and service health. Chapters 111–120 explain Kubernetes and EKS workload concepts. This chapter focuses on the release path across the two choices rather than repeating their initial setup. The single-host release procedure in [Chapter 132](132-deployment-to-vps-infrastructure.md) provides the same artifact-identity and health-check contract on a VPS.

## ECS task revisions and service updates

An ECS task definition revision describes a task’s image, resource allocation, ports, logs, execution role, application task role, and runtime settings. Registering a new revision records a candidate configuration. It does not make a running service use that revision. Updating the ECS service to reference the approved revision starts a deployment; the scheduler then replaces tasks according to the service’s deployment strategy and capacity.

The image field should identify the tested artifact by digest, for example `123456789012.dkr.ecr.us-east-1.amazonaws.com/dispatchdesk/api@sha256:<actual-image-digest>`. The account, region, repository, and digest are placeholders until replaced with the release record’s verified values. The task execution role and task role remain separate: the former supports task startup actions such as pulling a private ECR image and writing logs; the latter gives application code its runtime AWS permissions. A task can start-fail on registry authorization even when the application task role appears correct, because image pull occurs before the application has started.

For the common ECS rolling strategy, the service gradually replaces old tasks with new tasks. Deployment minimum and maximum healthy percentages influence how many tasks can be unavailable or started above the desired count, so deployment capacity, subnet addresses, and quotas must support the configured overlap. The ECS deployment circuit breaker can detect tasks that fail to reach steady state and can roll back to a previously completed deployment when rollback is enabled. It cannot roll back an initial deployment with no known-good completed revision, prove business behavior, or reverse database changes. AWS documents the circuit breaker for ECS rolling deployments; the service’s selected controller and strategy determine which deployment controls apply ([ECS service deployment strategies](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_service-options.html), [deployment circuit breaker](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html)).

Before updating a service, check the AWS account and region, cluster, service, current task-definition revision, desired/running counts, recent deployment events, and the approved candidate task definition. Review the exact plan in the deployment system and confirm that the caller has permission to pass only the required roles. After the update, observe deployment state, stopped-task reasons, target health, application logs, and service-level indicators. Do not treat “desired count equals running count” as readiness; load-balancer target health and a synthetic transaction answer different questions.

ECS also has deployment options that run old and new task sets concurrently or shift traffic in stages. Blue/green and canary approaches can provide a test-traffic or limited-traffic phase before full production exposure, but require compatible traffic-routing infrastructure, permissions, additional capacity, and alarm policy. The deployment strategy is part of the release architecture: choose rolling when resource efficiency and simplicity matter and a minutes-long rollback is acceptable; choose a separate traffic-shift strategy when validation before full cutover justifies extra moving parts and capacity ([ECS deployment workflow](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/blue-green-deployment-how-it-works.html)).

## EKS manifests and release evidence

EKS keeps the Kubernetes workload API. The deployment manifest declares the desired Pod template; a Kubernetes Deployment controller creates and replaces ReplicaSets and Pods to move toward that state. EKS supplies the control plane and AWS integrations, while the team still owns workload configuration, access control, resource requests, readiness behavior, image reachability, and compatibility. Apply the manifest using a principal authorized for the intended cluster and namespace, and confirm the current context before making a change. A developer’s valid AWS identity does not by itself mean the Kubernetes RBAC mapping authorizes that developer to update workloads.

This illustrative Deployment fragment uses a digest placeholder and a rolling-update policy. It assumes an existing namespace and cluster, a compatible application image, and cluster capacity for one surge Pod. Replace the placeholder with an actual verified digest before use; the text in angle brackets is deliberately not valid image content.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dispatchdesk-api
  namespace: production
  labels:
    app.kubernetes.io/name: dispatchdesk-api
spec:
  replicas: 3
  revisionHistoryLimit: 5
  progressDeadlineSeconds: 600
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: dispatchdesk-api
  template:
    metadata:
      labels:
        app.kubernetes.io/name: dispatchdesk-api
    spec:
      containers:
        - name: api
          image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/dispatchdesk/api@sha256:<actual-image-digest>
          ports:
            - name: http
              containerPort: 8080
          readinessProbe:
            httpGet:
              path: /readyz
              port: http
            periodSeconds: 5
            failureThreshold: 3
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
            limits:
              memory: 512Mi
```

`maxUnavailable: 0` asks the controller to keep the desired number of available Pods while replacing them; `maxSurge: 1` allows one extra Pod during rollout. This requires enough schedulable capacity and may be unsuitable for constrained clusters. A readiness probe gates whether a Pod is counted ready for service; it does not replace liveness checks, a load-balancer check, or a business-level transaction. CPU has a request but no limit in this example so the scheduling reservation is explicit without asserting one universal CPU cap. Memory has both a request and a limit; choose values from observed application behavior and test the consequences of throttling, eviction, and out-of-memory termination.

A controlled EKS workflow reviews the rendered manifest, verifies the cluster context and namespace, checks authorization, and compares the intended change before applying it. It then watches the exact Deployment rollout and inspects events, Pod conditions, image IDs, endpoint readiness, and application signals. Kubernetes documents `kubectl rollout status` for watching progress; its default follows the latest rollout, so concurrent updates can make that observation ambiguous. Serialize releases or pin observation to the approved revision, and record the manifest revision and artifact digest together ([Kubernetes rolling update](https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/), [`kubectl rollout status`](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_status/)).

If a cluster is managed through GitOps, change the declared source and let the reconciler apply it. An imperative `kubectl apply` may be reverted by the controller or create a difference between Git and the cluster. [Chapter 137](137-gitops-principles-and-reconciliation.md) covers that reconciliation model. For ECR access, confirm the relevant node or Pod execution identity and network route can reach the registry. Image pull credentials are needed by the runtime before a container starts; permissions granted only to the application process arrive too late. EKS may run on different node architectures, so ensure the pinned digest refers to a multi-platform image index or constrain scheduling to platforms for which the artifact has a manifest ([EKS workload overview](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-concepts.html)).

## A staged cloud deployment

DispatchDesk promotes a candidate from a lower-risk environment to production without rebuilding it. The release record starts with the source commit, builder, image digest, test results, provenance and scan evidence. Development uses a dedicated AWS account and test data. Staging in a production-like account verifies network paths, IAM permissions, database compatibility, target health, and synthetic requests. A production approver then authorizes the same digest plus a reviewed environment change. If the image is copied to another ECR registry or account, verify the destination digest; if the manifest representation changes, treat that destination as a new artifact identity and apply Chapter 131’s policy again.

The stages should be observable and stoppable. Before any AWS mutation, the release system should establish which account and region it targets, the specific ECS service or EKS context, the image digest, and the expected previous version. During rollout, inspect scheduler state and infrastructure signals, but also run a synthetic operation that exercises the application’s critical path. Set a bake interval based on traffic and failure detection time. Use alarms that can stop or roll back the relevant deployment strategy; a dashboard that no one monitors is not an automatic safeguard. After a stage passes, retain the approval, exact task-definition ARN or Kubernetes manifest revision, digest, deployment events, checks, and rollback target.

Account separation reduces accidental cross-environment privilege and gives teams clearer blast-radius boundaries, but it increases registry, identity, and network coordination. A single account with separate roles and environments may fit a small sandbox; it offers weaker isolation if developers or automation have broad account access. Do not let a convenient default profile select production accidentally. For human-operated commands, inspect the active identity and target first; for automation, bind environment selection to protected release inputs and role assumptions rather than mutable job text.

## Failure diagnosis and recovery

Imagine staging is healthy, and an ECS production update registers the candidate revision but tasks repeatedly stop before becoming healthy. The failed assumption is that a registered task definition proves the image and configuration are usable in production. Check the service deployment events and stopped-task reason, then separate likely layers: image digest or architecture, execution-role ECR permissions, private subnet routes and endpoints, secret retrieval, container startup, target-group health, or application dependency availability. Compare the production revision’s role ARNs, environment references, network settings, and platform architecture to staging. Do not broaden permissions for all tasks or make the subnet public as a quick diagnostic. If a prior completed deployment exists and rollback is enabled, confirm the service returned to it; then verify target health and a synthetic request.

In EKS, `ImagePullBackOff`, unschedulable Pods, failed readiness, and a Deployment that exceeds its progress deadline point to different causes. Inspect Pod events and conditions, node architecture, ECR access, requests versus available capacity, service account identity, and the rendered image string. A digest typo or unauthorized registry path can leave the rollout short of available replicas. A readiness probe that checks an unavailable downstream dependency can prevent all Pods from serving even when the binary itself started. Correct the actual constraint, then resume through the controlled deployment source. If the new version is unhealthy, restore the previous manifest or Git revision; ensure the prior image remains in ECR and that database changes remain compatible.

Application rollback and data recovery are separate plans. ECS circuit-breaker rollback or Kubernetes `rollout undo` can restore a previous workload template, but neither can reverse an incompatible schema, duplicate an external side effect, restore an expired image, or guarantee traffic was error-free during transition. Keep release artifacts and configuration history for the recovery window, maintain backward-compatible database changes, and rehearse the recovery path in a non-production environment.

## Exercises

1. The same ECS task definition works in staging but production tasks cannot pull its image. Give a diagnostic sequence that distinguishes role, registry, network, architecture, and image-identity problems.
2. A team updates a Kubernetes Deployment by tag `:release` in an EKS cluster. Explain two reasons later Pods may not use the bytes that staging tested, and propose a release reference.
3. A Deployment has three replicas, `maxUnavailable: 0`, and `maxSurge: 1`, but the new Pod stays Pending. What capacity and scheduling evidence should you inspect before lowering the availability requirement?
4. The ECS service circuit breaker returns the service to a prior revision, but a customer operation still fails. Why is the rollback not sufficient evidence of recovery?
5. A `kubectl rollout status deployment/dispatchdesk-api` command waits while a second release begins. What is ambiguous, and how should a release controller avoid recording the wrong rollout as successful?

### Answer guidance

1. Inspect the stopped-task reason and exact task-definition image digest first. Verify the execution role’s narrowly scoped ECR pull permissions, repository/account/region policy, subnet route or required VPC endpoint, and platform architecture. Compare the destination registry digest to the approved candidate. Avoid expanding the application task role, since it is not the pre-start image-pull identity.
2. A mutable tag can move after staging, and nodes may cache or resolve the tag at different times. Use a digest-pinned image reference, test and record that digest, then verify the registry copy retains the digest or explicitly approve and verify a new destination identity.
3. Check pending-Pod events, node allocatable CPU/memory, requests, quotas, taints/tolerations, affinity and architecture, subnet/IP availability where relevant, and autoscaler reaction time. Decide from availability requirements and measured capacity whether to add capacity or revise rollout settings.
4. The controller only restores workload configuration. Verify healthy tasks/Pods, load-balancer endpoints, logs, error rate, and a synthetic business operation; investigate persistent data changes and effects already sent to dependencies.
5. By default rollout status follows the latest update, so the command may observe a different revision than the approved release. Serialize changes or use a revision-pinned observation, and record the task-definition ARN or manifest revision and digest associated with the evidence.

## Review questions

- What event changes an ECS service from the old task definition to a new one?
- Why do image-pull permissions belong to a startup identity rather than only the application’s runtime role?
- What does a Kubernetes readiness probe control during a rollout, and what does it not prove?
- Why should an artifact copied between AWS accounts be checked for destination identity?
- Which parts of an AWS deployment can an automatic scheduler rollback restore, and which remain outside its scope?

## Takeaways

- ECS task-definition registration and EKS manifest application are different control-plane operations; both need identity and evidence.
- Pin and verify the image digest tested by CI, including after cross-account or cross-region registry copying.
- Separate image-pull and logging permissions from the application’s AWS runtime identity.
- Check desired state, scheduler progress, target readiness, and a synthetic application operation before advancing stages.
- Treat automatic rollback as workload recovery, not as proof that data and customer-visible behavior have recovered.

## Further reading

- [Chapter 93 — ECS and Fargate Services](../10-aws-production-services/093-ecs-and-fargate-services.md)
- [Chapter 131 — Release Engineering and Artifact Promotion](131-release-engineering-and-artifact-promotion.md)
- [Amazon ECS deployment strategies](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_service-options.html)
- [Amazon ECS deployment circuit breaker](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html)
- [Kubernetes Deployment rolling updates](https://kubernetes.io/docs/tasks/run-application/update-deployment-rolling/)
- [Amazon EKS workload concepts](https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-concepts.html)

Sources reviewed 2026-10-04. AWS commands were not executed; the examples are configuration fragments and decision procedures, not a provisioned lab.
