---
book: The Complete DevOps Engineering Book
volume: 14
volume_title: "Delivery, Deployment and GitOps"
chapter: 139
title: "Flux in Practice"
slug: flux-in-practice
status: complete
summary: ../../_ai/chapter-summaries/139-flux-in-practice.md
---

# Chapter 139 — Flux in Practice

## Why this matters

Flux is a set of Kubernetes controllers that implement GitOps through Kubernetes custom resources. Instead of managing deployments through a central dashboard, an operator declares a source and one or more reconciliation objects in the cluster. Flux controllers fetch source artifacts, build configuration, apply resources, report status, and retry when dependencies or the target are not ready.

For DispatchDesk, Flux can watch the deployment repository and reconcile the staging directory into a namespace. The build pipeline still tests and publishes a digest, then proposes a Git change that selects the digest. Flux does not build that image or decide its quality. It continuously applies the declared resources under Kubernetes identity and policy. That division follows the model in [Chapter 137](137-gitops-principles-and-reconciliation.md), while [Chapter 138](138-argo-cd-in-practice.md) covers another controller implementation. This chapter uses the Flux documentation available on 2026-10-04. Flux APIs and flags evolve; check the docs that match the installed controller and CLI release before applying manifests or commands.

## Flux resources and reconciliation flow

Flux separates fetching desired state from applying it. The source-controller reconciles source objects such as `GitRepository` and produces an artifact containing a resolved revision. The kustomize-controller watches `Kustomization` resources, retrieves their referenced source artifact, builds the path, applies the rendered objects, detects and corrects drift, and can prune resources it previously applied. The helm-controller reconciles `HelmRelease` resources when that optional controller is installed. Notification and image automation controllers are also optional parts of the toolkit; they do not need to be enabled just to deploy a pinned image from Git.

A Flux `GitRepository` is a namespaced custom resource describing a repository, a ref, and how often to check it. Its status records the fetched artifact and resolved revision. A Flux `Kustomization` is also a custom resource; it identifies a source, path, interval, target namespace, health behavior, and deletion policy. This name is distinct from the Kustomize tool’s `kustomization.yaml`, which describes how to render Kubernetes manifests. A Flux `Kustomization` can build from plain YAML or use a repository path containing the Kustomize file.

The following declarations are illustrative and assume Flux CRDs and controllers have already been installed by the platform team. The example assumes the repository is readable without authentication. For a private repository, add `secretRef.name` under `GitRepository.spec`, pointing to a credential Secret in the same namespace as the `GitRepository`; create it through a secured process rather than committing plaintext. The credential should be read-only because the controller fetches desired state and has no reason to push changes back.

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: dispatchdesk-deploy
  namespace: flux-system
spec:
  interval: 1m
  url: https://git.example.com/platform/dispatchdesk-deploy.git
  ref:
    branch: main
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: dispatchdesk-staging
  namespace: flux-system
spec:
  interval: 5m
  path: ./environments/staging
  prune: false
  sourceRef:
    kind: GitRepository
    name: dispatchdesk-deploy
  targetNamespace: dispatchdesk-staging
  wait: true
  timeout: 5m
```

The actual repo URL, branch, intervals, path, namespace and timeouts are policy choices, not universal recommendations. Because `targetNamespace` names a namespace that does not exist, create it through platform bootstrap or include its Namespace object in a separately authorized reconciliation path; the Flux Kustomization controller does not automatically create a missing target namespace simply because it is named here. `wait: true` asks the controller to wait for health of reconciled resources before reporting readiness. The timeout should fit expected image pulls and rollout times. `prune: false` is a conservative adoption setting: deleting a manifest from Git will not automatically clean up the object. If the organization later enables pruning, it should first review ownership and stateful-resource deletion behavior.

A release proceeds when the controller fetches a newer repository artifact, renders `./environments/staging`, applies it, checks health, and reports the resulting revision and conditions. Flux retries failed work with backoff. An optional webhook receiver can accelerate source checks, but recurring intervals ensure that missed notifications do not become the only way a change is noticed. The status revision is important release evidence: a healthy object reconciled from an unexpected commit is still the wrong release.

## Bootstrap and environment ownership

Flux itself must be bootstrapped into a cluster with sufficient privileges to install its controllers and custom resource definitions. The initial bootstrap is a privileged platform operation. Afterward, teams can store Flux resource declarations in Git and let Flux manage its own configuration, subject to a carefully designed trust boundary. A bootstrap identity with broad privileges must be protected and not reused by ordinary application pipelines. Keep cluster foundation, CRDs, policy engines, network plumbing, and shared operators under a platform-owned path or repository when application teams should not change them.

Split reconciliations along ownership and failure boundaries. A root or platform Kustomization may establish namespaces and shared controllers; workload Kustomizations can depend on those resources being ready. Flux `dependsOn` can order reconciliation resources and prevent an application configuration from applying before its dependency is ready. It does not make an unhealthy dependency work or understand application-specific compatibility. Circular dependencies can prevent progress, so keep the graph directed, small, and documented. Use separate environment paths or repositories when the access and approval policies differ materially.

For staging and production, separate the declarations or use explicit overlays so the approved digest and values are visible in the right environment. A branch name such as `main` is a moving reference; every fetched artifact still resolves to a commit, which Flux reports. Protect changes to the production path with repository review rules, and ensure the same digest is promoted when the release is intended to use the same tested binary. Avoid image automation that silently changes production references unless its policy, update strategy, and approval model are understood. Chapter 135 explains canary and feature-flag promotion decisions.

## Security and tenant permissions

Flux controllers need permission to read Flux custom resources and apply the Kubernetes objects requested by their `Kustomization` and `HelmRelease` resources. The default installation is convenient for a trusted single-team cluster, but the Flux security documentation describes controller roles that may include cluster-admin access for reconciling resources. Therefore, namespace separation alone does not prove that one tenant’s declaration is limited to its own namespace.

In shared clusters, explicitly design both Kubernetes RBAC and Flux object access. Flux supports using a service account specified by a reconciliation object so the controller can impersonate a more limited identity when applying resources. Platform administrators can enforce that model with controller settings. Bind tenant service accounts only to required resource kinds and namespaces, prevent tenants from creating or modifying other teams’ Flux source and reconciliation objects, and restrict cross-namespace references where the deployment requires tenant isolation. A tenant that can create arbitrary Flux Kustomization resources or choose a privileged service account may gain more reach than intended.

Repository credentials, decryption keys, and remote cluster credentials are also authority. Make source credentials read-only and namespace-scoped where appropriate. If using SOPS-encrypted configuration, the controller’s decryption identity and key access require least privilege, audit, and rotation. Keep plaintext out of Git history, rendered artifacts, and logs. Refer to [Chapter 137](137-gitops-principles-and-reconciliation.md) for Kubernetes Secret risks and supply-chain boundaries. Use separate keys or identities across environments if compromise of staging must not reveal production.

Flux CRDs accept potentially powerful configuration such as source references, service-account names, decryption references and remote kubeconfig references. Treat permission to create those custom resources as deployment authority. Use admission policies and namespace RBAC to constrain them, and inspect the actual controller arguments and role bindings in the installed release. Vendor documentation’s example defaults are not evidence of the live cluster’s effective privileges.

## Observe, pause and repair reconciliation

Status and conditions are the first diagnostic layer. With an authorized kubeconfig that can read Flux resources, these commands inspect source and reconciliation state without changing it:

```bash
kubectl -n flux-system get gitrepository dispatchdesk-deploy -o wide
kubectl -n flux-system describe gitrepository dispatchdesk-deploy
kubectl -n flux-system get kustomization dispatchdesk-staging -o yaml
kubectl -n flux-system describe kustomization dispatchdesk-staging
```

The `GitRepository` status helps identify whether the source controller fetched an artifact and which commit it resolved. The `Kustomization` status and events help distinguish a missing source, invalid path, build error, dependency wait, apply denial, pruning error or failed health check. Do not publish full YAML output blindly; status may contain references and annotations that reveal internal details. For application readiness, inspect the target namespace separately and correlate with service metrics and logs.

If a Kustomization is not ready, locate the first failing step rather than repeatedly forcing reconciliation. A source authentication problem will not be fixed by changing workload manifests. A path error requires correcting the Git path or repository structure. A build failure requires fixing rendered configuration; an apply denial points to identity, RBAC, admission policy, or an unsupported resource. A health check failure may mean resources were applied but did not become ready. Resolve the root cause and observe the next attempt. A manual reconcile command can trigger work immediately, but it does not correct invalid state and can increase pressure during an API or dependency outage; use the CLI appropriate to the installed version and an operator-approved procedure.

When an emergency manual change to a Flux-managed object disappears, compare the actual object to the source revision. The controller may be correcting drift. Decide whether the live repair was correct; encode an accepted target in Git and review it, or allow the reconciler to restore the declared state. The Flux Kustomization can be suspended for a deliberate intervention; while suspended, it does not apply newly fetched revisions or correct drift. Its referenced GitRepository can continue fetching revisions unless that source object is suspended separately. Establish an owner and a clear resume procedure before suspending either object. An indefinite pause creates hidden divergence and stale production configuration.

Flux garbage collection is tied to pruning and inventory ownership. When pruning is on and a manifest is removed from the source, Flux can delete an object it previously applied. Renaming reconciliation objects or changing ownership can alter what the controller considers managed. Before enabling pruning, test the effect in a disposable namespace, inspect the resource inventory, protect stateful resources with appropriate policy, and validate backups. Git can restore a manifest but cannot restore persistent data or reverse an external side effect. Consult [Chapter 140](140-rollback-roll-forward-and-release-incidents.md) when the change affects production and [Chapter 136](136-database-and-message-compatibility.md) before treating a configuration rollback as a database rollback.

## Exercises with answer guidance

1. The `GitRepository` is Ready but the Flux `Kustomization` is not. Name likely next checks. Inspect its source reference and resolved artifact, path, Kustomize build errors, dependencies, target namespace, controller identity and conditions. A healthy source only proves an artifact was fetched, not that rendering or applying succeeded.
2. A staging workload is ready, but status points to an older commit than the merge. What should you verify? Check branch/ref and source artifact revision, polling interval or webhook delivery, source authentication and controller freshness. Confirm that the merge landed in the repository and path the Flux object actually watches before considering a forced reconcile.
3. A tenant controls its namespace but can create a Flux Kustomization in `flux-system`. Why is this a concern? The controller may apply that declaration with a more privileged identity, so authority to create Flux objects can become indirect cluster authority. Restrict CR creation, enforce tenant impersonation and service-account policy, and prevent references across tenant boundaries.
4. Why might a team initially set `prune: false`, and what does that cost? It avoids automatic deletion while adopting resources or learning ownership, but removed resources remain live as orphaned/extraneous state. Track and review them, then introduce pruning only with tested ownership and data-protection controls.

## Review questions

- What work do source-controller and kustomize-controller perform?
- How is a Flux `Kustomization` different from a Kustomize `kustomization.yaml`?
- What does Flux status prove, and what application evidence must be gathered separately?
- Why are Flux custom resources themselves security-sensitive?
- How does service-account impersonation reduce deployment authority in a shared cluster?
- What pauses when a Kustomization is suspended?
- What state can Git history restore, and what requires a separate backup or recovery plan?

## Takeaways

- Flux fetches versioned source artifacts and applies them through Kubernetes controllers and custom resources.
- A ready source does not imply a successful build, apply, rollout, or healthy service; inspect each layer’s revision and conditions.
- Treat the ability to create Flux resources as deployment authority, and constrain the identity that applies resources through RBAC and impersonation.
- Use read-only credentials for sources and protect decryption and remote-cluster identities as carefully as cluster credentials.
- Pruning, suspension, and reconciliation intervals change operational behavior; rehearse them and assign ownership.
- Promote immutable artifact digests through reviewed environment changes, then verify both controller status and application health.

## References

- Flux, [Git Repositories](https://fluxcd.io/flux/components/source/gitrepositories/), [Kustomization](https://fluxcd.io/flux/components/kustomize/kustomizations/), accessed 2026-10-04.
- Flux, [Security Documentation](https://fluxcd.io/flux/security/), [Multi-tenancy](https://fluxcd.io/flux/installation/configuration/multitenancy/), and [Security Best Practices](https://fluxcd.io/flux/security/best-practices/), accessed 2026-10-04.
- OpenGitOps, [Principles v1.0.0](https://github.com/open-gitops/documents/blob/v1.0.0/PRINCIPLES.md), accessed 2026-10-04.
