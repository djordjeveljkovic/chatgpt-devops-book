# Independent review — Chapter 175

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 2b94984a65674d7ea70c604844d53657911f5b01aae6f73b6771a84942affcd3

## Scope and findings

Read full manuscript, current summary, Chapter 175 brief and authoring guide, with Chapter 174 secret-access context. Reviewed delivery/lifecycle, Kubernetes projections, Vault lease/static-role behavior, AWS rotation, consumer transition, provider revocation and leak recovery, exercises/questions/takeaways. No material body technical defect found, but completion records need correction.

Medium — compact summary, all sections: summary still says planned, no material written and no verification performed despite complete current body. Replace with factual current topics, examples, references, actual static/source validation and nonexecution limits; align manuscript/summary state before promotion. This is required by authoring-guide continuation and completion requirements.

Low precision observations:

- Recovering from a leaked credential, opening paragraph: clarify why an old pooled connection is rejected while the leaked password still authenticates. A manager-only change can cause new-password reconnect failures but does not inherently invalidate old authenticated sessions; login/password changes likewise do not universally terminate established database sessions. The incident should separate these outcomes explicitly.
- Plain references to Chapters 174/176/203: convert to actual relative context links, especially brief prerequisite 174.

Technical assessment: secret-store encryption versus authorized retrieval and source-side authority are distinct. Kubernetes environment values remain fixed until container replacement, volume projection is eventual and subPath excluded; consumer cache/pool behavior remains necessary. Vault dynamic TTL/renewability and backend revocation are correctly qualified, not promised universally instantaneous external session destruction. Static username rotation and privileged configuration custody are distinguished. AWS pending/create-set-test-finish rotation is accurate; moving current does not prove consumers transitioned. Target single-credential versus dual-user/key support is explicit, with staged consumers/drained pools and old-value denial tests. Compromised values are not casually reactivated for rollback. Derived sessions/tokens and dependent credentials require review/revocation. Evidence preservation, restricted logs, stable version/run identifiers and disposable leak drills avoid printing secrets. No actual credentials or dangerous executable example appear.

## Primary evidence checked 2026-10-04

- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/): encoding/encryption, eventual mounted updates and subPath caveat.
- [Vault leases](https://developer.hashicorp.com/vault/docs/concepts/lease): dynamic secret leases, renewability, replacement/revocation and backend scope.
- [Vault database secrets engine](https://developer.hashicorp.com/vault/docs/secrets/databases): dynamic roles and static-role password rotation and privileged integration requirements.
- [AWS Lambda rotation functions](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_lambda-functions.html): pending/current version transition and four rotation steps.

## Validation and limits

`python3 tools/check_book.py --chapters 175-175` passed 1,473 global local links without warnings/errors, reporting state drafting; no executable syntax examples present. Exact stripped-front-matter body hash from `tools.promote_reviewed.body_hash`. No secret manager, database, cluster, credential creation/rotation/revocation, CI log or incident operation executed. No deployed Vault backend/version, database-session behavior or provider key overlap matrix tested. Sources and static lifecycle reasoning cannot prove real old-credential invalidity, consumer coverage or leak impact. Only this review record written.

## Bounded correction refresh — 2026-10-04

Summary/status completion and all three relative references are resolved. Existing sessions are correctly qualified as potentially continuing. Medium finding remains in the incident opening: the second worker's stale password is said to fail a fresh connection while the leaked old password still authenticates fresh connections, after only the secret manager was changed. For the same target identity/value those outcomes contradict. Describe a refreshed consumer attempting the new manager value (which fails because target remains unchanged), while the unrefreshed/leaked old value still succeeds. A shallow health check may miss new-authentication failures, but it must not demonstrate incompatible outcomes for the same old password.

Fresh body SHA256: bce02ae6a1788d398ddc06e7654eb7b8bfab448969c836810674450af9f7fa87. Focused 174-175 checker passed three YAML, two shell checks and 1,476 links without warnings/errors. Earlier complete technical assessment/source evidence and runtime limits remain applicable. Only this review record updated.

## Final paragraph correction refresh — 2026-10-04

The credential scenario now consistently separates changed secret-manager value from unchanged target credential: a refreshed worker fails fresh authentication using the new value, whereas unrefreshed/leaked old credentials still authenticate. Previously established sessions may continue; a health check is not authentication/remediation evidence. All body/summary findings are resolved and the technical body is approvable.

Fresh body hash: 2b94984a65674d7ea70c604844d53657911f5b01aae6f73b6771a84942affcd3. `python3 tools/check_book.py --chapters 175-175` currently reports seven broken global local links to absent Chapter 176, including this body's direct prerequisite-context reference, with 1,476 links inspected and no warnings. This is a transient workspace/link validation gap requiring the target to be restored and the checker rerun before final approval. No Chapter 175 prose change is required for that gap. Earlier primary evidence/nonexecution limits remain applicable. Only this review record updated.

## Link validation finalized — 2026-10-04

Chapter 176 is restored and the transient missing-target gap is resolved. Current Chapter 175 hash remains 2b94984a65674d7ea70c604844d53657911f5b01aae6f73b6771a84942affcd3. `python3 tools/check_book.py --chapters 175-176` passed one YAML/one JSON parsing check and 1,477 links without warnings/errors. All material findings are resolved; earlier evidence and nonexecution limits remain applicable.

Verdict: approved
