# Independent review — Chapter 118

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 5188253b6eac31e6d73b02c41d641580b26028bcaff14058d3d835ec2e599307

## Findings

No material findings. Helm 3 --atomic versus Helm 4 --rollback-on-failure is now explicitly qualified. Official [Helm 4 overview](https://helm.sh/docs/overview/) inspected 2026-10-04 confirms the old flag remains a deprecated alias; this review corrects the prior incomplete inference from current generated command help. StorageClass reclaimPolicy now correctly governs dynamically provisioned PV initial reclaim behavior. Summary no longer claims nonexistent chapter links.

## Scope and dated primary evidence

Read full body, summary, SKELETON brief, guide and independently reviewed Chapter 117 prerequisite. Packages/templates/overlays, values/rendered/release state and deployment review cover the brief. Failure scenario, reversible route decision, external side effects and recovery are useful; exercises include concrete answer guidance. Five commands are valid local lint/render and release-state inspection commands. Local chart/values paths are explicitly illustrative reviewed-repository inputs, not claimed existing fixtures. Status/history pin context and namespace. Secret output risks, compatibility and no execution are explicit. No apply/upgrade/rollback/install or external mutation command is executed or provided as an unqualified safe read. Kustomize generators, selector transformations, schema-dependent patches, remote-base pinning and embedded-version differences are otherwise sound. Resource ownership and repeated-upgrade diagnosis are appropriate, though Helm CLI itself is not a continuous reconciler unless a delivery controller invokes it. No distribution-specific host installation commands need a Linux variant.

Official primary sources inspected 2026-10-04: [Helm upgrade](https://helm.sh/docs/helm/helm_upgrade/) currently renders Helm 4.3.0 documentation with --rollback-on-failure and wait strategies; [Helm template](https://helm.sh/docs/helm/helm_template/) supports local rendering and target capability options; [Helm hooks](https://helm.sh/docs/topics/charts_hooks/) supports lifecycle side effects and cleanup limits; [Kubernetes Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) supports bases/overlays, patches, generators and render/apply distinction; [PersistentVolumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) and [StorageClasses](https://kubernetes.io/docs/concepts/storage/storage-classes/) establish reclaim-policy object ownership. No claim of tested rollback, rendered manifest validity or secret privacy is fabricated.

## Validation and limits

`python tools/check_book.py --chapters 118-119` passed on 2026-10-04: two draft chapters, two shell syntax blocks and 1,387 global local-link checks; no errors/warnings. Exact body hash calculated using tools.promote_reviewed.body_hash. No Helm or kubectl commands, chart render/lint, release query, manifest application, hook, migration, storage operation or cluster/provider action occurred. No installed Helm/Kustomize versions, target API/admission, Ubuntu/Fedora/RHEL matrix, dependency files, secret handling, chart output, rollback or application health was tested. Documentation review and shell syntax do not prove these runtime behaviors. External sources checked selectively. Only this separate review record was written.

Verdict: approved
