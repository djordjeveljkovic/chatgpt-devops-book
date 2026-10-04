# Independent review — Chapter 139

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 8c7157a1e37ec523b40950eb1eae4e0795c9c9a32b179737ffb8c2c01b86d9c1

## Scope and findings

Read complete current body/summary, brief and authoring guide, with reviewed137/138 context. Checked Flux source/apply resources, v1 APIs, waits/dependencies, bootstrap/identity, suspension, inventory/pruning, commands and recovery. No material technical finding. GitRepository source artifact versus Kustomization build/apply/health distinction is sound; target namespace bootstrap requirement, wait/timeout and conservative prune false are explicit. Root/bootstrap authority versus tenant impersonation, CR creation authority, source/decryption/remote credential risk and controller configuration are appropriately qualified. Drift repair/controlled suspend/resume and persistent-data deletion limits are accurate. Read-only kubectl operations specify kubeconfig/read permission and avoid careless YAML disclosure. Version assumptions and nonexecution are transparent; platform API scope does not require distro package instructions.

Low — Observe, pause and repair reconciliation, suspension paragraph: “suspension pauses both source updates and drift correction for that reconciliation” should clarify that suspending a Kustomization stops applying new source revisions and drift correction, while its GitRepository may continue fetching unless separately suspended. Current “for that reconciliation” qualifier makes the intended scope defensible but could be clearer.

Low — source example introduction: GitRepository manifest omits secretRef, so explicitly say it assumes unauthenticated/readable Git; authenticated repositories need spec.secretRef pointing to the separately provisioned namespace Secret. Read-only credential policy alone does not wire that credential into the example. Existing illustrative/preinstalled source setup keeps this nonblocking.

Assessment and summary accurately reflect examples and operational bounds. Image automation is correctly optional and production updates require policy; it is not presented as silently authorizing every new registry tag. No substantive contradiction with138 alternative-controller model.

## Primary evidence checked 2026-10-04

- [Flux GitRepository](https://fluxcd.io/flux/components/source/gitrepositories/): source artifact/ref, credentials, polling and source suspension.
- [Flux Kustomization](https://fluxcd.io/flux/components/kustomize/kustomizations/): target namespace, wait/timeout, dependsOn, pruning/inventory, suspend and impersonation.
- [Flux multi-tenancy](https://fluxcd.io/flux/installation/configuration/multitenancy/): service-account and cross-namespace controller security controls.

## Validation and limits

`python3 tools/check_book.py --chapters 137-139` passed: four YAML parses, three shell syntax checks and1,440 global links; no errors/warnings. Exact body hash computed with tools.promote_reviewed.body_hash. No Flux install/bootstrap, schema/server validation, source fetch/auth, render/apply, status query, impersonation/tenant negative test, dependency/wait, suspension or prune/recovery executed. No controller/API/OS version matrix inspected. Static YAML/shell syntax and sources cannot establish live authority, health or safe deletion. Only139 review plus requested validation notes in137/138 records changed.

## Bounded correction review — 2026-10-04

Private source now explicitly requires GitRepository.spec.secretRef.name referencing same-namespace credentials, and unauthenticated source assumption is clear. Kustomization suspension now stops applying/drift correction while GitRepository fetching can continue unless separately suspended. Both optional observations resolved, no remaining material issue. Fresh hash8c7157a1e37ec523b40950eb1eae4e0795c9c9a32b179737ffb8c2c01b86d9c1 verified. `python3 tools/check_book.py --chapters 137-140` passes four YAML parses, six shell syntax checks and1,443 global links; no errors/warnings. Prior source/runtime limits remain.

Verdict: approved
