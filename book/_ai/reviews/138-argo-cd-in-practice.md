# Independent review — Chapter 138

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: dc163095e3f3dcf5a4d0720f7f0e3edd1f532c788d26550796beb16a14258a16

## Scope and findings

Read complete current body, now-present summary, Chapter138 brief and authoring guide, with independently approved137 context. Reviewed Application/AppProject YAML, namespace/resource policy, automation/self-heal/pruning, sync versus health, credentials/RBAC, CLI inspection, recovery and assessment. No material technical finding. AppProject source/destination and namespaced allowlist are deliberate, cluster-resource permission omitted, Secrets excluded, with separate bootstrap/platform management and least-privilege caveats. CreateNamespace is explicitly conditional on approved bootstrap needs. Automated enabled/selfHeal without prune is documented behavior; manual removal can leave extraneous resources. Desired/reported status does not establish business health. Scope warns privileged workload creation remains dangerous even without explicit Secret kind permission.

Repository read credentials, credential-template prefixes, local/remote cluster identities and Argo versus Kubernetes permissions are correctly separated. CI proposal/sync authority is qualified against source/destination editing. Commands app get and app diff are read-oriented, context/auth/read permission explicit; no arbitrary local-manifest sync is recommended. Fetch/render/apply versus healthy rollout failures and data-aware Git revert/repair-forward are sound. Version-sensitive stable docs are qualified against installed release rather than asserting a release number. Summary accurately records nonexecution and current material. YAML and CLI examples supply prerequisites; no distro-specific package command requires additional platform treatment.

Low — paragraph before Application YAML: tag or commit pinning is offered for stricter promotion immutability, but Git tags can also move unless protected. Prefer an immutable commit SHA, or explicitly qualify tag protection and record resolved SHA. This does not invalidate the branch-tracking example whose reviewed revision and artifact digest are separately recorded.

## Primary evidence checked 2026-10-04

- [Projects](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/): default permissiveness and policy/role boundaries.
- [Automated sync](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/): enabled, self-heal and separate prune behavior.
- [Sync options](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-options/): CreateNamespace, managed namespace scope and deletion safeguards.
- [Argo RBAC](https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/): application permissions and source/config authority separation.
- [app diff](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd_app_diff/): comparison operation and configured CLI context.

## Validation and limits

`python3 tools/check_book.py --chapters 137-138` checked three YAML parses, two shell syntax checks and1,435 global local links.138 own body/summary links resolve. All body and summary links now resolve; transient authoring gaps have been resolved. Hash computed using tools.promote_reviewed.body_hash. No Argo installation/CLI/API, render/sync, admission/project deny test, namespace creation, credential access, health, prune/deletion, pause/recovery or Kubernetes workload executed. No CRD/schema/server semantic or version/OS matrix tested. Source inspection and static YAML cannot establish effective privilege, live configuration or recovery. Only separate review records137/138 changed in this assigned task.

## Completed-volume focused validation — 2026-10-04

137–139 bodies and summaries now present. Fresh `python3 tools/check_book.py --chapters 137-139` passed: four YAML parses, three shell syntax checks,1,440 global local links; no errors/warnings. Prior transient missing-file/summary gaps are resolved and are not remaining findings. Approved body hash is unchanged. All earlier source/technical/runtime limitations remain. Chapter138 tag-mutability note is an optional observation, not a required correction or approval blocker.

## Final batch validation — 2026-10-04

Fresh `python3 tools/check_book.py --chapters 137-140` passed four YAML parses, six shell syntax checks and1,443 global links; no errors/warnings. Approved138 body hash unchanged; optional tag-mutability observation remains nonblocking. All earlier runtime limits retained.

Verdict: approved
