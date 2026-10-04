# Independent review — Chapter 176

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: de3ab0c086bbe1996e3e25e3e64a52836a79b887d1da0ec8a47174fac20c9a68

## Scope and findings

Read current body/summary, assigned brief and authoring guide with Chapter 175 revocation context. Reviewed issuer/audience/subject versus role permissions, GitHub current immutable subjects, AWS trust JSON, GitLab offering distinctions, Jenkins issuing versus login plugins, projected Kubernetes tokens, CI fragment, key migration/denial tests and recovery. No material technical finding; approved.

GitHub's July 15, 2026 owner/repository-ID default format is supported by current primary documentation. Example environment subject preserves that identity prefix and Production context; legacy subjects are identified separately and actual emitted claims must be inspected. JSON has valid federated principal, AssumeRoleWithWebIdentity action and exact aud/sub conditions. Role permissions remain a separate required policy. Workflow fragment grants scoped id-token write and contents read with empty workflow defaults; it is explicitly an explanatory incomplete exchange fragment, not a claimed working deployment integration. It does not retrieve or print credentials. Untrusted execution and reusable-action authority remain separate controls.

GitLab ID tokens supersede deprecated CI_JOB_JWT_V2 usage. Numeric project/namespace claims as AWS conditions are correctly attributed to GitLab.com rather than universally available for self-managed/Dedicated. Actual instance issuer and audience/trust matching are required. Jenkins OIDC Provider plugin issues build tokens; Authentication plugin login does not establish that issuer. Signing/discovery keys and temporary binding need effective job/trust security. Kubernetes projected audience/expiry/kubelet rotation require consumer rereading and relying-party validation; general API audience is not silently reused elsewhere. Short lifetime limits persistence but does not neutralize currently authorized malicious jobs.

Static-key removal and provider revocation are distinguished, allowed/denied subjects and effective role actions are tested separately, and wildcard repair is rejected as unsafe authority expansion. The context-change incident has specific claim evidence and restrictive recovery/break-glass ownership. Exercises/questions/takeaways and summary accurately reflect the actual material and nonexecution.

Low optional precision observations:

- Immutable GitHub rollout paragraph: expressly exclude GitHub Enterprise Server, and state that post-July-15 renames/transfers also transition older repositories to immutable format. Current generic rename/settings caveat and actual-claim requirement are sound but less exact than the cited source.
- GitLab paragraph/answer: name the AWS condition-key limitation directly: self-managed and Dedicated support only sub/aud for this integration; namespace_id changes on project transfer while project_id survives. Existing offering-dependent wording is accurate.
- Projected-token paragraph: clarify offline JWT signature/expiry validation alone does not discover Pod deletion; immediate bound-object invalidation requires live validation such as TokenReview or equivalent supported integration. Current relying-service validation caveat correctly avoids a universal guarantee.

## Primary evidence checked 2026-10-04

- [GitHub OIDC reference](https://docs.github.com/en/actions/reference/security/oidc): immutable owner/repository identifiers, rollout date, legacy opt-in and rename/transfer/GHES exceptions; environment versus branch subjects.
- [AWS IAM OIDC role guidance](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html): GitHub required non-null/non-wildcard-only sub trust condition, aud and scoped issuer role trust.
- [GitLab AWS federation](https://docs.gitlab.com/ci/cloud_services/aws/): ID tokens, supported offering-specific AWS claim conditions and stable identifier/transfer behavior.
- [Jenkins OIDC Provider plugin](https://plugins.jenkins.io/oidc-provider/): build token issuer/binding and provider discovery/trust examples.
- [Kubernetes projected volumes](https://kubernetes.io/docs/concepts/storage/projected-volumes/): audience, expiration and projected token behavior.

## Validation and limits

`python3 tools/check_book.py --chapters 176-176` passed one YAML/one JSON parsing check and 1,477 global local links without warnings/errors. Exact stripped-front-matter hash computed with `tools.promote_reviewed.body_hash`. No workflow run, token issuance/decode/exchange, IAM policy deployment, GitLab/Jenkins configuration, Kubernetes refresh/object deletion, denied subject test, deployment or access-key revocation executed. No platform offering/version/tier/cloud-partition matrix tested. Example subject identifiers and AWS account are fictional; primary documentation cannot establish the actual repository's emitted claims or deployed permissions. Only this separate review record written.

Verdict: approved
