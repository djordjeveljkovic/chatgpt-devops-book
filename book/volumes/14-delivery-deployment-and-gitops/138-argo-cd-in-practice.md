---
book: The Complete DevOps Engineering Book
volume: 14
volume_title: "Delivery, Deployment and GitOps"
chapter: 138
title: "Argo CD in Practice"
slug: argo-cd-in-practice
status: complete
summary: ../../_ai/chapter-summaries/138-argo-cd-in-practice.md
---

# Chapter 138 — Argo CD in Practice

## Why this matters

Chapter 137 introduced the operating model: desired state is versioned, a controller pulls it, and reconciliation moves the target toward that state. Argo CD implements that model for Kubernetes. Its Application resource connects a source repository and path to a destination cluster and namespace, while Argo CD reports whether the rendered desired resources match the live objects and whether those objects are healthy.

For the DispatchDesk team, this means production deployment can be driven by a reviewed digest change in Git rather than a CI runner holding a long-lived cluster credential. Argo CD does not replace build and release engineering. It does not build or verify the application image, decide whether a release is safe, or guarantee the service is healthy because a sync succeeded. The team still supplies artifact evidence and policy, chooses sync and deletion behavior, scopes permissions, and observes application health. This chapter uses the Argo CD stable documentation as checked on 2026-10-04. CRDs, options, and CLI details can vary across releases; use documentation matching the installed Argo CD version before applying examples.

## Applications, projects and destinations

An Argo CD Application is a declaration of three important things: where desired resources come from, how Argo CD renders them, and where it may apply them. A source usually names a Git repository, revision, and directory path. The source can be plain YAML, Kustomize, Helm, or a supported config-management plugin. A destination identifies a registered cluster and namespace. The Application itself lives in the Argo CD namespace, while its managed resources live in the destination.

An AppProject provides a policy boundary around applications. It can restrict source repositories, destination clusters and namespaces, and resource kinds. The default project is convenient for a quick installation but is too permissive as a production design if many teams share an Argo CD instance. A project helps constrain the impact of an application declaration, but it is not a substitute for Kubernetes RBAC, admission policy, or repository review. In particular, allowing an application to create privileged workloads can grant effective access to namespace resources and secrets.

The following example uses the in-cluster API server and illustrative repository path. Replace the repository URL, branch, and namespace with values from the installation; create the namespace through an approved bootstrap process or retain `CreateNamespace=true` only when that is appropriate. This project permits one source and a limited namespaced resource set:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: dispatchdesk-staging
  namespace: argocd
spec:
  description: DispatchDesk staging application resources
  sourceRepos:
    - https://git.example.com/platform/dispatchdesk-deploy.git
  destinations:
    - server: https://kubernetes.default.svc
      namespace: dispatchdesk-staging
  namespaceResourceWhitelist:
    - group: apps
      kind: Deployment
    - group: ""
      kind: Service
    - group: ""
      kind: ConfigMap
```

The example omits cluster-scoped resource permission, which is desirable for an ordinary application release. It also omits Secret from the allowlist so the application cannot introduce arbitrary Secret objects through this project. A secret delivery controller or an operator can manage the required secret under a separate, deliberate policy. Confirm the source URL exactly matches the repository credential configuration, and test that the generated object kinds fit the allowlist; a Helm chart may create resources not obvious from its source templates.

An Application then points to an environment-specific path. The example below enables automated sync and self-healing but leaves pruning disabled. The source revision is illustrative: branch tracking is common for an environment repository, while teams that need stricter promotion immutability can pin a tag or commit revision and update it through a controlled process.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: dispatchdesk-staging
  namespace: argocd
spec:
  project: dispatchdesk-staging
  source:
    repoURL: https://git.example.com/platform/dispatchdesk-deploy.git
    targetRevision: main
    path: environments/staging
  destination:
    server: https://kubernetes.default.svc
    namespace: dispatchdesk-staging
  syncPolicy:
    automated:
      enabled: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

Automated sync applies a Git change when Argo CD detects that desired manifests differ from live state. Self-heal allows it to correct certain live changes that drift from Git. These settings do not imply deletion is safe: pruning is a separate choice and is omitted here. With pruning disabled, removing a resource from Git can leave the live object behind and show it as extraneous; this is often safer during initial adoption. If a team later enables pruning, define ownership and deletion safeguards, especially for persistent resources. Never treat a green sync indicator as evidence that deleting a resource had no effect.

Argo CD also distinguishes sync status from health. Sync status reports whether managed resources match the desired revision. Health status summarizes whether resources are progressing, healthy, degraded, or suspended according to resource-specific health checks. An Application can be synced while a deployment is degraded, or appear out of sync while the live service still serves traffic. Release policy should consider both controller state and application-level signals such as request success, latency, error rate, and dependency health.

## Installation and access boundaries

Argo CD is normally installed into a dedicated namespace and managed as platform software. Its components need network access to the Kubernetes API and the Git or Helm sources they read. Operators should pin and review the installation method, version, and configuration; define who can administer Argo CD; secure its API and web interface; protect repository and cluster credentials; and plan backup or recreation of declarative configuration. A production installation is a control-plane component, not merely a dashboard.

Repository credentials should be read-only for repositories that contain desired state. Prefer short-lived or narrowly scoped credentials when the source provider supports them. Store credentials using the installation’s secret-management design rather than committing plaintext credential manifests. Argo CD’s declarative setup supports repository credentials represented as Kubernetes Secrets in the Argo CD namespace; those Secrets need the same etcd encryption and least-privilege controls described in Chapter 137. Restrict credential templates carefully because a URL-prefix match can grant access to multiple repositories.

The cluster credential used by Argo CD is especially sensitive. When managing the local cluster, Argo CD runs within that cluster and can use its configured service account and API access. For remote destinations, credentials are stored by the Argo CD control plane. Restrict each Application’s project destination and resource-kind policy, and scope the Kubernetes identity where the deployment model allows it. Avoid granting cluster-admin just to make an example sync succeed. If a particular release needs a cluster-scoped CRD or namespace object, treat that as a platform-owned operation with a separate review and identity.

Argo CD has its own RBAC model for users and API tokens. Separate read-only visibility, application sync, application source editing, project administration, and system administration. A CI job that merely updates an image digest should normally change the Git deployment repository, not receive unrestricted Argo CD or Kubernetes privileges. If policy intentionally allows CI to request a sync, scope that ability to a specific application and ensure it cannot alter source, destination, or arbitrary local manifests. Review the effective permissions of both Argo CD and Kubernetes; one layer cannot compensate for an overly broad other layer.

## A release through Git

For a staging release, the build pipeline completes tests, creates an image, and publishes it by immutable digest as explained in [Chapter 131](131-release-engineering-and-artifact-promotion.md). An automation identity opens a pull request changing the staging manifest or overlay. The pull request should include the source revision, digest, test evidence, provenance or signature result where available, and any configuration change. A reviewer checks that the diff selects the intended artifact and does not accidentally expand access, replace resources, or remove stateful objects. After merge, Argo CD fetches and renders the source, displays the comparison, and automatically syncs according to Application policy.

The reconciliation agent may observe the new branch revision after its next poll or a configured refresh event. Do not promise a fixed deployment delay unless the installed version and configuration have been verified. The key evidence is the resolved revision, generated diff, sync result, resource health, Kubernetes rollout status, and application behavior. To promote to production, update the production path or revision through its own review and release gate. Keep the same tested digest when the goal is promotion of the same binary; alter environment-specific values only for deliberate configuration differences.

The deployment interface can be inspected through either the web UI or CLI. With the Argo CD CLI authenticated to the intended instance and authorized to read the application, a responder can query status and compare manifests:

```bash
argocd app get dispatchdesk-staging
argocd app diff dispatchdesk-staging
```

These commands are read-oriented: the first reports source, destination, sync and health state; the second compares desired and live resources. Check the CLI context before using it, because an operator may have access to more than one Argo CD instance. Do not paste output containing sensitive values into tickets or logs. A subsequent `argocd app sync` would initiate a write operation; automated sync is preferable when it already expresses the release policy, and a manual sync should be reserved for an explicit operational decision. CLI arguments and authorization behavior should be checked against the installed release.

## Diagnose a failed or unsafe sync

Suppose the Application shows `OutOfSync` after the staging pull request merged. First establish which revision Argo CD resolved and whether it successfully rendered the source. A missing repository credential, branch typo, invalid YAML, unavailable Helm dependency, unsupported API kind, or project allowlist rejection can stop the release before a Kubernetes object changes. Inspect the Application condition and controller or repo-server events; compare the intended target revision with the resolved revision. Correct the Git declaration or source access issue, then verify the newly rendered diff before retrying.

If the application is `Synced` but `Degraded`, inspect the affected resource’s conditions and events. A Deployment may have no available replicas because an image cannot be pulled, readiness fails, resources cannot be scheduled, or the application cannot connect to its database. A sync means the requested object specification was accepted, not that containers became ready or user requests succeeded. Diagnose with the relevant Kubernetes status and application telemetry. When the image or configuration is defective, use the release decision process in [Chapter 140](140-rollback-roll-forward-and-release-incidents.md): revert the desired revision or promote a corrected artifact, then observe recovery. A Git revert alone does not reverse a database migration, external side effect, or incompatible message already produced; see [Chapter 136](136-database-and-message-compatibility.md).

If a manual live edit disappears, check whether self-heal is enabled. Decide whether the manual change was a necessary repair. If it should persist, make a reviewed Git change and confirm Argo CD applies it. If not, let the declared state restore the prior configuration and verify workload behavior. During a high-impact incident, a controlled pause or sync-policy change may be justified, but the operator should know exactly how to resume reconciliation and should preserve an audit trail. Leaving automation disabled after the incident creates a new hidden state that future responders may misread.

Deletion and pruning require a separate review. When pruning is enabled, Argo CD can remove resources no longer present in the rendered desired set. Before enabling it for an application, inspect the generated diff, determine ownership, classify stateful resources, and test deletion behavior in a disposable environment. Argo CD supports sync options and resource annotations that influence pruning, but those details are version-sensitive. Prefer application-level policy and explicit protections appropriate to the resource; ensure backups and restore procedures exist for persistent data. If a desired change unexpectedly proposes deletion, stop and correct the source or policy before sync.

## Practical operating checklist

For each Argo CD Application, document its owning team, source repository and path, tracked revision, rendering method, destination, project, sync mode, drift policy, prune behavior, health checks, credential owners, and escalation path. Store the Application and AppProject declarations in an audited platform configuration repository where feasible. Keep cluster bootstrap and Argo CD installation under platform ownership; ordinary application teams should not need to edit global controller configuration to promote their service.

Monitor the controller itself: repository fetch failures, stale revisions, repeated sync failures, excessive reconciliation delay, permission errors, and capacity constraints. Alert on prolonged out-of-sync or degraded status according to service criticality. Keep application SLO alerts separate from controller alerts so a successful sync cannot mask a bad release. Define who may pause automation, how the pause is recorded, how long it may remain, and what evidence is required before resuming.

## Exercises with answer guidance

1. An Application is synced but degraded after a new digest is promoted. What should the operator check? Confirm the resolved revision, then inspect the Deployment conditions, pod events, image pull status, readiness, and service telemetry. Sync success means desired objects were applied; it does not mean the release passed its health gate. Roll back or roll forward according to impact and compatibility.
2. A team wants Argo CD to manage Deployments but not delete resources removed from Git. Which policy choices matter? Leave automated pruning disabled initially or configure explicit prune protections supported by the installed version. Verify extraneous resources are visible and decide how intentional retirement is approved. Protect persistent resources and test the exact behavior before enabling deletion.
3. A build runner needs to update an image. Should it receive a cluster-admin token? No. Let it publish and attest the immutable artifact, then make a scoped Git change or pull request. If a sync request is needed, limit its Argo CD permission to the named Application and prevent it from changing that Application’s source or destination.
4. A project permits a repository but sync fails because a chart creates an unapproved resource kind. How should this be handled? Inspect the rendered manifest and establish whether that resource belongs to the application or platform. Update the project allowlist only after review, or move the cluster-scoped/platform resource into separately managed configuration; do not broaden all permissions reflexively.

## Review questions

- What source, rendering, and destination information does an Argo CD Application connect?
- How does an AppProject constrain an application, and which other security controls remain necessary?
- What is the difference between sync status and health status?
- What changes when automated sync, self-heal, or pruning is enabled?
- Which identities need read access to the source repository and write access to a cluster?
- What evidence should be checked before and after a production promotion?
- Why can reverting Git fail to restore data or external effects?

## Takeaways

- Argo CD Application resources map a source revision and rendered path to a cluster and namespace; AppProjects constrain sources, destinations, and resource kinds.
- Automated sync can remove the build pipeline’s need to call a deployment API, while self-heal and pruning are distinct policy choices.
- `Synced` means resources match the selected desired state; health and service metrics decide whether the release is actually good.
- Protect repository, cluster, and Argo CD identities separately. Give CI authority to propose artifact selection instead of broad production mutation.
- Inspect exact rendered diffs and deletion behavior before enabling pruning, and test settings against the installed version.
- Monitor Argo CD’s own freshness and errors as well as application health, and record a deliberate path for pausing and resuming reconciliation.

## References

- Argo CD, [Automated Sync Policy](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/), [Application specification](https://argo-cd.readthedocs.io/en/stable/user-guide/application-specification/), and [Declarative Setup](https://argo-cd.readthedocs.io/en/stable/operator-manual/declarative-setup/), accessed 2026-10-04.
- Argo CD, [Projects](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/), [RBAC configuration](https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/), [Sync Options](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/), accessed 2026-10-04.
- Kubernetes, [Good practices for Kubernetes Secrets](https://kubernetes.io/docs/concepts/security/secrets-good-practices/), accessed 2026-10-04.
