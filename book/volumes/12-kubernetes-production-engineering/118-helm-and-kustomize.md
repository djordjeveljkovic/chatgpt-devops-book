---
book: The Complete DevOps Engineering Book
volume: 12
volume_title: "Kubernetes Production Engineering"
chapter: 118
title: "Helm and Kustomize"
slug: helm-and-kustomize
status: complete
summary: ../../_ai/chapter-summaries/118-helm-and-kustomize.md
---

# Chapter 118 — Helm and Kustomize

## Package and customize Kubernetes configuration

Helm and Kustomize help teams manage Kubernetes objects, but they solve different problems. Helm packages templates, default values, dependencies and release metadata into charts. Kustomize composes Kubernetes manifests and applies declarative transformations through bases and overlays. Both can produce resources that Kubernetes later admits and reconciles; neither proves that those resources are safe, compatible with the cluster or healthy at runtime. Select a tool based on configuration complexity, release lifecycle, ownership, reviewability and team familiarity. Avoid adding both layers to a simple deployment unless the composition has a clear benefit.

A Helm chart is a versioned package with a `Chart.yaml`, default `values.yaml`, templates and optional dependencies or schema. Templates render Kubernetes resources using chart values and release context. Values let operators customize the chart without editing templates, while `values.schema.json` can constrain accepted structure and types. Chart authors should document every supported value and keep defaults safe. A value that silently opens a public listener, grants broad RBAC or disables resource limits is a production API choice, not a harmless convenience. Read the Helm [chart guide](https://helm.sh/docs/topics/charts/) and [best practices](https://helm.sh/docs/chart_best_practices/) for chart structure and template guidance.

Kustomize starts from plain resource manifests. A base composes resources and reusable transformations; overlays specialize them for environments or tenants. Patches target resources and fields, while image, namespace, label and name transformations can provide common changes. The output remains rendered Kubernetes YAML, which can be reviewed and compared before applying. Keep overlays small and explicit: a production overlay should make meaningful differences visible instead of copying an entire base and drifting independently. The Kubernetes [Kustomize guide](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) describes bases, overlays, generators and patches.

Choose a single primary owner for each field. A Helm release that manages a Deployment should not compete with a second tool that continuously writes different replica counts or image versions to the same object. Likewise, an overlay should not patch chart output in a separate stage without clear responsibility for the combined result. Multiple reconcilers can overwrite each other's fields, create noisy diffs or cause emergency changes to disappear. If a GitOps controller owns delivery, define how chart or Kustomize output flows into that controller and who approves reconciliation.

## Helm values, releases and change control

Values are part of a chart's public interface. Prefer clear names, meaningful types, documented defaults and validation for required choices. Separate workload settings from infrastructure-specific parameters. Avoid a long list of opaque `--set` overrides in a shell history or deployment pipeline; store reviewed values in version control and keep secrets in an appropriate secret-management system. Helm values can appear in release records, rendered manifests or diagnostics. Do not assume that `--set` makes sensitive data private. Check chart behavior for Secret rendering and access to Helm release storage.

Pin chart versions and dependency versions in the release process. A chart version, application image tag and application version are different identifiers; record all that affect the rendered output. Review upstream changes, schema defaults and deprecations before adopting a new chart. Render against the target Kubernetes version and capabilities when chart templates branch on API availability. A chart that renders successfully can still produce invalid or operationally unsafe resources; validate policy, RBAC, requests, disruption budgets, storage and network exposure with the same controls used for hand-authored manifests.

Helm tracks releases and revisions, which helps operators inspect history and request a rollback. Rollback reapplies an earlier set of Kubernetes resources; it does not undo database migrations, external API changes, data writes, cloud resources changed outside the chart or irreversible hook effects. Hooks can create Jobs and other side effects at lifecycle points, so inspect them and understand their retry, timeout and cleanup behavior. `--wait` waits for selected Kubernetes readiness conditions up to a timeout; it does not prove user-facing correctness. Helm 3 documents `--atomic` for rollback after a failed operation; Helm 4 uses `--rollback-on-failure` and retains `--atomic` as a deprecated alias. Select flags from the installed Helm CLI version. Neither option makes the entire system transactionally reversible. Define database expand/contract migrations, backward compatibility, feature flags and data recovery separately. See the Helm [v3 upgrade reference](https://helm.sh/docs/v3/helm/helm_upgrade/), [current upgrade reference](https://helm.sh/docs/helm/helm_upgrade/) and [Helm 4 overview](https://helm.sh/docs/overview/).

Before a production change, compare current and proposed output, check the target cluster context, namespace and release, and preserve the exact chart version and values used. Review resource deletion, immutable field changes, selector changes, PVC behavior, CRD handling and hook effects. Be cautious with ownership changes: taking ownership of existing objects can alter who controls their future lifecycle. Keep a clear rollback revision and confirm that the old application version remains compatible with data and dependencies after any migration.

## Kustomize overlays and generated resources

A typical repository has a base for shared objects and overlays for environments. An overlay can set a namespace, change image references, attach labels and apply small patches to resources. Use stable label selectors and test the rendered result, because transformations to selectors and resource names can affect Service routing, workload ownership and RBAC subjects. A generated ConfigMap or Secret can receive a content-derived suffix by default, causing references to update when inputs change. Verify generator options and rollout behavior if an application expects a fixed name. Do not commit secret literals merely because Kustomize can generate Secret objects from files.

Patch scope should be easy to explain. A small patch that changes a production replica count or resource request is easier to review than a broad patch that rewrites an entire Deployment. Strategic merge patches depend on resource schema and list merge behavior; JSON patches target explicit paths and can fail when the expected object shape changes. Kustomize remote bases introduce an external dependency: pin a repository revision, review changes and preserve repeatable builds. Check the exact Kustomize version embedded in `kubectl` or used in CI, because features and output may differ.

Kustomize can be used directly with `kubectl kustomize` to render a directory, or with `kubectl apply -k` to submit the result. Helm can render a chart locally with `helm template`, run chart checks with `helm lint`, and inspect installed release state with commands such as `helm status` and `helm history`. The local render path helps code review, but the API server may have different discovery, admission and defaulting behavior. For existing resources, a dry-run or diff can help expose changes, but still review what would be created, changed or removed before an apply.

## DispatchDesk release example

DispatchDesk has three environments and one Helm chart for its API. A proposed production release changes the application image, adds a PVC and renames a Service. The rendered chart looks valid, but the Service name is used by an external Gateway route and the StorageClass sets `reclaimPolicy: Delete` for dynamically provisioned volumes. A CI test that only runs `helm lint` does not identify either operational consequence. The team renders the exact chart and values, reviews the Service reference and storage lifecycle, checks compatibility with the database migration, validates the API objects against the target cluster version and runs the chart in a disposable environment. It stages the application migration so old and new versions can coexist, then deploys with a monitoring window and a documented rollback decision. The Service rename is removed from the release because it provides no benefit and would break the external route.

For a service managed through Kustomize instead, keep a shared base for the Deployment and Service, with overlays for environment-specific image and replica differences. Make the production overlay reveal its intentional policy differences, such as external route references and storage class. Render the overlay in CI, compare it to the expected resources and run policy checks. If Helm packages a shared platform controller while Kustomize manages the application, establish clear ownership boundaries at resource level and avoid two controllers writing the same fields.

## Safe rendering and inspection

These commands render or inspect local configuration and installed release metadata; they do not apply Kubernetes resources:

```bash
helm lint ./charts/dispatchdesk-api
helm template dispatchdesk-api ./charts/dispatchdesk-api \
  --namespace production --values ./environments/production/values.yaml
kubectl kustomize ./environments/production
helm status dispatchdesk-api --namespace production --kube-context kind-dispatchdesk
helm history dispatchdesk-api --namespace production --kube-context kind-dispatchdesk
```

The chart and path names are examples; run local render commands from the repository root with the reviewed inputs. Before querying a live release, verify the kubeconfig context, API endpoint and account. `helm status` and `helm history` read release metadata, but output and access permissions depend on the Helm storage backend and installation. Rendered output may include internal endpoints or Secret data; inspect and redact it before sharing. `helm lint` checks chart structure and common issues, not cluster admission or runtime behavior. `kubectl kustomize` shows transformed YAML, not whether its resources can safely be applied.

If a deployment fails, preserve the rendered input, chart version, values revision, release history, Kubernetes events and relevant controller status before retrying. Identify whether failure occurred in rendering, admission, scheduling, hooks, readiness or application behavior. Do not repeatedly rerun an upgrade with changed values until the actual failed state and external side effects are understood. If rollback is appropriate, verify that the prior workload version supports the current schema and data state. If the release created a PVC or external resource, inspect its lifecycle separately. After recovery, make the smallest corrective change, test it in staging, and record which part of the release contract failed.

## Exercises and answer guidance

1. `helm lint` passes. Has the chart been proven safe for production? No. It has passed chart checks only; inspect rendered resources, target API/admission behavior, security policy, runtime readiness and external side effects.
2. `helm upgrade --atomic` fails and rolls back. Are database changes also reversed? No. Rollback covers Helm-managed Kubernetes resources within its behavior, not arbitrary data or external side effects.
3. A Kustomize overlay changes a Deployment image but the Service no longer selects its Pods. What should be checked? Rendered labels/selectors and transformations; test the complete output and endpoint behavior.
4. A values file contains a database password. Is it safe because it is not passed on the command line? Not necessarily. Values may be stored in release metadata or rendered resources; use the approved secret system and inspect the chart's handling.
5. Helm and GitOps both update the same replica count. What is the risk? Competing field ownership and reconciliation can overwrite changes or create drift; assign one authoritative owner and define the integration.

Review questions: how do Helm charts differ from Kustomize overlays, what can release rollback reverse, why should rendered output be reviewed, and how do teams prevent competing reconcilers?

## Verification and primary sources

Official Kubernetes Kustomize guidance and Helm chart, upgrade and hook documentation were inspected on 2026-10-04. Commands include local rendering/linting and read-only release inspection; they were not run. No chart release, manifest, cluster, hook, database migration or external resource was changed. Static checks cannot establish chart correctness for a specific cluster, API admission, rendered secrets, controller behavior, application health or rollback safety.

Primary references: [Kubernetes Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/), [Helm charts](https://helm.sh/docs/topics/charts/), [Helm best practices](https://helm.sh/docs/chart_best_practices/), [Helm v3 upgrade](https://helm.sh/docs/v3/helm/helm_upgrade/), [Helm current upgrade](https://helm.sh/docs/helm/helm_upgrade/), [Helm 4 overview](https://helm.sh/docs/overview/), and [Helm hooks](https://helm.sh/docs/topics/charts_hooks/).
