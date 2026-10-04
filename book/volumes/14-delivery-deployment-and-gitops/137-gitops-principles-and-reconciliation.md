---
book: The Complete DevOps Engineering Book
volume: 14
volume_title: "Delivery, Deployment and GitOps"
chapter: 137
title: "GitOps Principles and Reconciliation"
slug: gitops-principles-and-reconciliation
status: complete
summary: ../../_ai/chapter-summaries/137-gitops-principles-and-reconciliation.md
---

# Chapter 137 — GitOps Principles and Reconciliation

## Why this matters

The DispatchDesk team has a tested, immutable container image and several ways to deploy it. A command run from a laptop can change a cluster, a CI job can call the Kubernetes API, or a controller can observe a reviewed configuration change and make the cluster converge toward it. The first two approaches can work, but leave an operational question: what record explains why the live system has this version and configuration? If the source of truth is a person’s command history or a job log that has expired, recovery and audit become harder.

GitOps makes desired system state a versioned declaration and gives a software agent responsibility for pulling that declaration and reconciling the runtime toward it. This changes the normal deployment path: instead of granting every build job broad production credentials, the build produces and verifies an artifact, a reviewed change selects that artifact for an environment, and an agent already running near the target applies the declared state. The pattern is useful well beyond Kubernetes, but Kubernetes supplies a clear controller model for understanding it.

GitOps does not make a workload correct, eliminate review, or guarantee that every change is safe. A reconciler can faithfully install a broken configuration. It cannot infer the intended contents of a database, repair an unavailable dependency, or decide whether a risky deletion is acceptable. Teams still need reliable builds, health evidence, access control, observability, and a recovery decision. For artifact identity and deployment mechanics, see [Chapter 131](131-release-engineering-and-artifact-promotion.md), [Chapter 132](132-deployment-to-vps-infrastructure.md), and [Chapter 133](133-container-deployment-to-aws.md). This chapter establishes the operating model; [Chapter 138](138-argo-cd-in-practice.md) and [Chapter 139](139-flux-in-practice.md) apply it to specific controllers.

## Git state, controllers and drift

OpenGitOps describes four principles: desired state is declarative; versioned and immutable; pulled automatically; and continuously reconciled. A declarative document says what should exist, such as three replicas of a named application using a particular image digest. It does not prescribe a sequence of imperative steps such as “create a pod, wait, then create two more.” The controller determines the actions needed to approach that target.

Versioned desired state gives each environment an auditable history. An image reference such as `registry.example/dispatchdesk@sha256:…` identifies fixed content, unlike a movable tag such as `latest`. Git history can show who proposed a change, which checks ran, who approved it, and which revision was merged. Branch protections, signed commits, protected environments, and immutable artifact storage strengthen this history; merely putting YAML in a repository does not make the history trustworthy or immutable.

“Pull” describes the agent’s relationship to the source of desired state. A controller in or near the target environment fetches declarations and acts using its own runtime identity. A webhook may tell it to check sooner, but periodic observation matters too: the agent must be able to notice drift even when no commit event arrives. This reverses an important credential flow. A CI system does not need standing permission to mutate every production object just because it can build an image. A deployment agent can have narrowly scoped permissions to manage a particular namespace or application.

Reconciliation is a control loop. Kubernetes’ built-in controllers watch API objects, compare their specification with observed cluster state, and make or request changes that move the system closer to the specification. An external GitOps agent adds another loop: it compares the revision and resources declared in the source with the resources visible in the cluster, then applies permitted changes. These loops are level-based, not a one-time script: they repeatedly observe state and respond to divergence. “Continuous” means recurring, not instantaneous. A controller can be delayed by polling intervals, API availability, rate limits, or failed health checks.

Suppose the desired declaration requests three replicas and someone manually scales the live Deployment to five. That is drift: actual state no longer matches the declared state. A reconciler configured to correct drift can scale back to three. A controller configured to report drift but wait for a human can alert and leave five running. Some controllers expose separate choices for automatic sync, self-healing, and pruning; do not assume one vendor’s defaults apply to another. A manual repair may be appropriate during an incident, but the team should promptly encode the accepted state in a reviewed change or let the controller restore the prior declaration. Otherwise the next reconciliation can undo the emergency fix.

The desired-state repository normally contains manifests, policy, and non-secret environment configuration. A simple environment layout might look like this:

```text
deploy/
  base/dispatchdesk/
    deployment.yaml
    service.yaml
  environments/
    staging/
      kustomization.yaml
    production/
      kustomization.yaml
```

The base describes shared workload structure; each environment overlay sets deliberate differences such as replica count, hostname, resource budget, or approved image digest. The exact directory convention is a team choice. The important property is that an operator can identify the full input revision used for an environment and recreate the same intended resources from it. Avoid hidden mutable inputs such as unpinned remote bases or a `latest` image tag if they can change the rendered result without a reviewed change. Pin dependency versions and record how the final manifests are rendered.

For a promotion, the build pipeline tests source, builds an image, scans and publishes it, and records the resulting digest. It then opens a change to the staging declaration that selects that digest. Reviewers can inspect the source revision, test results, provenance, and configuration diff before merging. The reconciler notices the merge and applies it. After staging evidence meets the release policy, a separate production change promotes the same digest. Rebuilding between environments can produce different bits, so promotion should usually move the tested artifact identity while environment-specific configuration changes separately.

This division keeps authority comprehensible. Build automation can write to an artifact registry and propose changes to a deployment repository. Repository policy controls which identities may merge production changes. The reconciler can read approved state and update only the target cluster scope required for its application. People can inspect status and logs without having unrestricted write access to the cluster. Small organizations may combine roles, but should still make the trust boundaries and identities explicit.

## Promotion and secret boundaries

Configuration belongs in version control only if readers of that repository can safely see it. A private repository is not a secret store: contributors, CI jobs, backups, mirrors, and later clones may all retain its history. Removing a committed password from the latest file does not erase the earlier value. If a real credential is committed, revoke or rotate it, then clean history only as a secondary containment step.

Kubernetes Secret objects help deliver sensitive values to workloads, but their values are base64-encoded, not encrypted by that encoding. Kubernetes documentation notes that Secret objects are stored unencrypted in etcd by default unless encryption at rest is configured. Access should use least-privilege RBAC; `list` or `watch` can expose all values, and permission to create a workload can indirectly expose secrets in that namespace. Restrict which containers receive each secret and prevent applications from logging it. Where appropriate, use an external secret manager and workload identity, or a supported secret-store integration, so the Git repository holds a reference and policy rather than the credential value.

A manifest should therefore contain a secret reference or name, not a production password:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dispatchdesk
  namespace: dispatchdesk
spec:
  replicas: 3
  selector:
    matchLabels:
      app: dispatchdesk
  template:
    metadata:
      labels:
        app: dispatchdesk
    spec:
      containers:
        - name: web
          image: registry.example/dispatchdesk@sha256:REPLACE_WITH_REAL_DIGEST
          env:
            - name: DATABASE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: dispatchdesk-database
                  key: password
```

This is an illustrative template, not an apply-ready deployment: replace the digest with the real published digest and provide the referenced Secret through an approved mechanism. The manifest makes a reference visible, but Kubernetes RBAC still determines which users and workloads can obtain the value. A cluster operator must configure encryption at rest and restrict API access according to the cluster’s threat model. A secret agent with broad namespace or cluster permissions is itself a sensitive component and needs rotation, audit, and recovery procedures.

Encrypted-secret workflows can allow ciphertext to be stored alongside manifests, but encryption at rest in Git does not settle key custody. The decrypting controller or CI identity becomes a high-value principal. Restrict who can request decryption, audit the operation, scope keys by environment, and ensure plaintext does not appear in build logs or rendered artifacts. A central external manager with short-lived credentials and workload identity may better fit teams that already operate such a service. Each design should state where plaintext exists, which identity can reveal it, how access is logged, and how rotation changes are rolled out.

The build-to-deploy boundary also matters for supply-chain evidence. The build pipeline is responsible for producing an artifact from a particular source revision and recording test and provenance evidence. The deployment repository selects an artifact; a reconciler applies that selection. The GitOps controller should not rebuild application source or silently replace the chosen digest with a floating tag. Conversely, the build job should not gain production write access simply to make deployment convenient. Policy can verify approved registries, digest-pinned references, signatures, provenance, and environment-specific review before a change merges or applies. Those checks establish an allowed path; they do not prove the application has no defects.

## Separating build from deployment authority

Consider DispatchDesk’s release of a tested image to staging. The pipeline has permission to publish to the registry and create a pull request against the deployment repository. It does not hold a long-lived production kubeconfig. The pull request changes only the staging image digest and links the tested source revision and release evidence. After review and merge, an agent in the cluster fetches the repository revision and reconciles the staging namespace. Production remains on the prior digest until its own promotion change passes policy and review.

This arrangement reduces blast radius in two ways. First, a compromised build runner cannot immediately issue arbitrary production API operations; it can at most publish artifacts and propose a change within its repository permissions. Second, production access is attached to a controller identity whose scope can be limited, audited, and rotated separately. A malicious or mistaken merged change can still affect production, so branch protection, required reviewers, policy checks, controller scope, and runtime monitoring remain necessary. GitOps moves the control point; it does not remove the need to secure it.

Reconciliation can also be unavailable while the application continues serving. A failed controller pod, inaccessible Git server, expired read credential, or API outage may delay new desired state. Existing workloads generally continue under their own control loops, but do not assume every external dependency or cluster component remains healthy. Alert on stale reconciliation time, failed fetches, apply errors, and persistent out-of-sync state. Record the last successfully applied revision so responders can distinguish “the desired change was rejected” from “the controller has not seen the change.” A controller being healthy does not mean the application is healthy; correlate deployment status with application metrics and probes.

Deletion deserves special care. If a reviewed revision removes a resource and the reconciler is allowed to prune, the controller may delete the live object. That can be correct for an obsolete Service but dangerous for persistent data, shared namespaces, or resources managed by another owner. Establish ownership boundaries, review rendered diffs, define deletion protections for stateful resources, and decide which removals require a second approval or manual confirmation. Recovery from deletion may require restoring a manifest, but persistent data recovery depends on backups and is not supplied by Git history. See [Chapter 136](136-database-and-message-compatibility.md) for application data compatibility and [Chapter 140](140-rollback-roll-forward-and-release-incidents.md) for release incident decisions.

## Procedure: investigate and resolve drift

Assume an alert says staging differs from its declared revision after an operator ran an emergency command. Start by identifying the Git revision the controller considers desired, the revision it last applied, its health and sync status, and the specific object fields that differ. Use the controller’s read-only dashboard or CLI where available. In a cluster where you are authorized to inspect the namespace, `kubectl` can provide independent evidence:

```bash
kubectl -n dispatchdesk get deployment dispatchdesk \
  -o jsonpath='{.metadata.generation}{" desired="}{.spec.replicas}{" ready="}{.status.readyReplicas}{" image="}{.spec.template.spec.containers[0].image}{"\n"}'
kubectl -n dispatchdesk describe deployment dispatchdesk
```

Run these commands from an administrator-approved workstation with a current kubeconfig and read access to the named namespace. They do not change cluster state. The first reports the object generation, requested and ready replica counts, and configured image; the second includes rollout conditions and recent events. If access is denied, request the evidence from the on-call cluster operator rather than elevating your identity casually. Compare these observations with the rendered desired manifests at the controller’s target commit, not with an unreviewed local working tree.

Next establish whether the difference is the intended emergency repair, an accidental manual change, a delayed controller, or a bad desired-state revision. Check the API audit record and incident timeline. If the live change is correct and must persist, encode that state in a reviewed commit and verify its rendered diff. If it was temporary or unsafe, allow or request reconciliation back to the approved declaration and monitor readiness. If the controller is unable to fetch or apply state, repair that failure before merging more changes; otherwise responders may believe a release occurred when the target never received it.

After resolution, verify both control-plane evidence and service behavior: the controller reports the intended revision applied, the Deployment has the expected image and ready replicas, and application health indicators meet the release gate. Preserve relevant controller events and audit evidence. If drift came from a human command, improve the operational path so emergency edits have an owner, expiry or follow-up change, and a clear rollback decision. If it came from a controller error, fix its credentials, scope, network path, or policy and test the recovery in a lower environment.

## Exercises with answer guidance

1. A CI job builds and scans an image, then runs `kubectl apply` using a production service-account token. Propose a GitOps alternative. A strong answer has the job publish an immutable digest and propose a narrowly scoped declaration change; protected review approves production state; an in-cluster or target-adjacent agent pulls and applies it with its own minimal identity. It also describes how to verify the applied revision and image.
2. An engineer changes a replica count directly during an incident. Explain why it may revert and how to make it durable. The reconciler compares live state with the declared revision and may restore the declared count. First decide whether the emergency change is correct, then either commit it through the normal review path or deliberately allow reconciliation to restore the prior target; monitor readiness and record the incident rationale.
3. A repository contains a Kubernetes Secret whose `data.password` is base64. What should the team do? Treat it as exposed, revoke or rotate the credential, inspect access and copies, and remove it from future state. Configure etcd encryption and least-privilege access. Then choose an external store or approved encrypted workflow with a documented decryption identity; deleting the latest manifest alone does not revoke or erase the value.
4. A production configuration change removes a PersistentVolumeClaim from desired state. What must be established before enabling automatic pruning? Determine controller ownership and deletion behavior, whether the claim or underlying data can be deleted, what backup and restore evidence exists, and which approval or deletion protection applies. Render and review the exact change in a representative environment first.

## Review questions

- What are the four OpenGitOps principles, and why does a webhook alone not provide continuous reconciliation?
- How does desired state differ from observed state, and what creates drift?
- Which credentials belong to build automation, repository reviewers, and the reconciliation agent?
- Why is a digest safer for promotion than a mutable image tag?
- What security properties are and are not provided by a Kubernetes Secret?
- Which resource deletions should require additional controls in your environment?
- What evidence proves the reconciler applied a revision, and what separate evidence proves the service is healthy?

## Takeaways

- GitOps uses declarative, versioned desired state, an agent that pulls it, and a recurring reconcile loop.
- Git history is useful only when its inputs, review policy, artifact references, and access controls are trustworthy.
- Separate build and deployment authority: build and verify immutable artifacts, review environment promotion, and let a scoped reconciler apply approved state.
- Drift is expected to be observed and handled according to policy; emergency live edits need an explicit follow-up decision.
- Secret references in Git do not secure secret values. Base64 is not encryption, and Kubernetes RBAC can expose secrets indirectly through workload creation.
- Reconciliation can fail or lag, workloads can remain unhealthy, and pruning can delete resources. Monitor, scope, protect, and rehearse recovery.

## References

- OpenGitOps, [GitOps Principles v1.0.0](https://github.com/open-gitops/documents/blob/v1.0.0/PRINCIPLES.md) and [GitOps Glossary v1.0.0](https://github.com/open-gitops/documents/blob/v1.0.0/GLOSSARY.md), accessed 2026-10-04.
- Kubernetes, [Controllers](https://kubernetes.io/docs/concepts/architecture/controller/), accessed 2026-10-04.
- Kubernetes, [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/), [Good practices for Kubernetes Secrets](https://kubernetes.io/docs/concepts/security/secrets-good-practices/), and [RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/), accessed 2026-10-04.
