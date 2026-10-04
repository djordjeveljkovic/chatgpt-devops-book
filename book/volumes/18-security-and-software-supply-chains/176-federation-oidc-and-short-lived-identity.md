---
book: The Complete DevOps Engineering Book
volume: 18
volume_title: "Security and Software Supply Chains"
chapter: 176
title: "Federation, OIDC and Short-lived Identity"
slug: federation-oidc-and-short-lived-identity
status: complete
summary: ../../_ai/chapter-summaries/176-federation-oidc-and-short-lived-identity.md
---

# Chapter 176 — Federation, OIDC and Short-lived Identity

**Section outline:** validate issuer, audience and subject boundaries; exchange CI/workload identities for scoped temporary credentials; replace static keys with a tested migration and recovery plan.

## Trust claims and audience boundaries

Federation lets one identity system accept an identity assertion from another system under an explicit trust relationship. With OpenID Connect (OIDC), an issuer signs a JSON Web Token (JWT) containing claims such as issuer (`iss`), subject (`sub`), audience (`aud`) and expiry (`exp`). A relying party validates the issuer's signature and token claims, then decides whether that identity may exchange the assertion for a local session or cloud role. The assertion is not itself a cloud permission policy, and possession of a valid JWT does not make a workflow or workload trustworthy.

The trust decision has two parts. The provider must accept tokens only from the expected issuer and audience. The role or service account must also constrain which subjects and contexts may assume it, then grant only the permissions the resulting session needs. An audience mismatch should fail closed: it prevents a token intended for one relying service from being replayed to another. A broad subject wildcard weakens that boundary because unrelated repositories, branches or jobs may become eligible to request the same authority.

Inspect the exact token claims emitted by the configured issuer and make trust conditions match those claims. Do not rely on a copied example from another repository or job type. Environment-based deployment, branch-based deployment, pull-request workflows and reusable workflows can produce different subjects. Claims and customization options also change by provider and platform version. GitHub's OIDC reference, for example, documents an immutable subject format that began rolling out for repositories created after July 15, 2026, while older repositories retain the earlier format unless opted in. Renames/transfers can also alter trust identifiers. Check the actual repository's current subject and update provider trust before changing claim templates.

The cloud role trust policy is separate from its permissions policy. The trust policy answers who may assume the role. The permissions policy answers what that assumed role may do. Scope both: restrict the trusted issuer, exact audience and repository/environment identity; then grant only required resources and actions. Use provider conditions that compare exact values when possible. Test that an approved job succeeds and a job from another repository, branch or environment is denied. A successful token exchange alone does not prove the resulting role is least-privileged.

## CI and workload federation

CI pipelines often need registry, cloud or deployment access. Long-lived cloud keys stored as CI variables persist across runs and may be copied into logs, runner files or compromised job environments. OIDC replaces a reusable stored cloud key with a signed, short-lived assertion issued for a job. The cloud provider exchanges it for temporary credentials, often scoped to a role session. This reduces credential lifetime and centralizes authorization, but a malicious workflow that is allowed to request the token can still use that role while the job runs.

For GitHub Actions, the workflow job must receive `id-token: write` permission to request an OIDC token. Keep that permission on the deployment job rather than granting it globally. Put privileged deployment in a protected environment with required approvals and restricted deployment branches/tags. Separate untrusted pull-request build/test jobs from jobs that can access production roles. Do not checkout or execute untrusted contributor code in the same privileged job that requests production identity. Protect reusable workflows and third-party actions as part of the chain that can exercise the deployment job's authority.

This minimal workflow fragment shows where token-request authority belongs. It does not itself configure AWS authentication; a reviewed provider integration step must exchange the token under the matching trust policy. The name `Production` is case-sensitive in the subject example below.

```yaml
name: Deploy DispatchDesk
on:
  push:
    branches: [main]
permissions: {}
jobs:
  deploy:
    environment: Production
    permissions:
      contents: read
      id-token: write
    runs-on: ubuntu-latest
    steps:
      - name: Exchange job identity for the scoped cloud role
        run: echo "Insert the reviewed provider-specific OIDC exchange step here"
```

The `permissions: {}` line removes default token permissions at workflow scope; the job grants only repository read and OIDC token request. The placeholder command is explanatory and deliberately does not retrieve credentials. A real workflow needs a current, reviewed cloud-authentication action or supported CLI exchange, pinned and configured according to its official documentation. Confirm the job has no untrusted code execution after the token becomes available. Then verify the role identity and permissions using a harmless read-only operation before enabling deployment writes.

For AWS with GitHub Actions, the IAM OIDC provider trusts `token.actions.githubusercontent.com`; a role trust policy should require `aud` to equal `sts.amazonaws.com` and `sub` to identify one intended repository/context. Here is a trust-policy illustration based on GitHub's immutable subject format. The IDs and names are examples only; replace them with the exact values shown by the repository's token issuer and AWS account, and define a separate permissions policy for the role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:octo-org@123456/octo-repo@456789:environment:Production"
        }
      }
    }
  ]
}
```

An older repository that has not opted into immutable subjects may use the legacy `repo:OWNER/REPOSITORY:environment:NAME` pattern instead. Do not broaden the policy to both forms or to `repo:*` just to make a deployment pass without first identifying the repository's actual subject. AWS requires a non-null `sub` trust condition for GitHub's shared identity provider and recommends restricting it to a known repository or branch/environment. Environment protection rules are a separate gate: OIDC identifies the environment claim, while GitHub environment configuration governs who can deploy through it.

GitLab CI uses job ID tokens configured with `id_tokens` and a selected audience. Its default subject describes group/project and ref context. On GitLab.com, cloud conditions can also use stable numeric `project_id` and `namespace_id` claims where supported; availability differs for self-managed and dedicated installations. Prefer immutable IDs alongside path claims when the provider supports them, especially where project rename or transfer could otherwise break or unexpectedly reuse a path. Use the exact GitLab instance issuer and claims, not `gitlab.com` examples, for a self-managed installation. Protect the production environment and deployment branch in GitLab as well as narrowing the cloud trust policy.

Jenkins can use the OpenID Connect Provider plugin to issue build-scoped tokens, but this is distinct from installing the OpenID Connect Authentication plugin to let users log in to Jenkins. The provider plugin, issuer URL, signing key, claim template and renewal/rotation process become part of the trust boundary. An external cloud must be able to validate the issuer and retrieve its public signing key over HTTPS. Restrict claims to job identity, configure the cloud trust conditions, use a temporary token binding, and review plugin security/update history. If Jenkins already runs on a cloud with native workload identity, that platform-provided identity may be simpler than introducing a public Jenkins token issuer.

Kubernetes workloads can use projected, time-bound service-account tokens with an explicit audience instead of manually created, non-expiring token Secrets. The API server issues a token bound to a Pod and audience; the kubelet refreshes it as it nears expiry. The application must reload the projected token file rather than retaining one token forever. An external service should validate the expected issuer, signature, audience, expiry and object binding, or use the platform's supported federation integration. Deleting or replacing a Pod can invalidate a bound token, but only if the relying service validates it against the expected trust path. Do not mount a general-purpose Kubernetes API token into a workload that only needs cloud object storage.

Short-lived credentials do not eliminate identity risk. A compromised runner or pod may request a token while it is authorized, steal the temporary cloud credentials after exchange, or use over-broad role permissions until expiry. Limit job duration, runner access, network destinations and role actions. Set token/session lifetime according to the provider's supported limits and operational needs, then log issuer subject, role session identity, resource and time so incident responders can attribute actions without logging raw JWTs or credentials.

## Replacing static cloud keys

DispatchDesk's deployment workflow stores an IAM access key in a CI variable. The team creates a federated role, tests a branch subject in staging, then removes the static key. Production deploys fail because production jobs use a GitHub environment, which changes the subject from the branch form to an environment form. An operator widens the subject condition to all repositories to restore deployment. This fixes the outage by granting production deployment authority to an unintended set of workflows. The failed assumption was that branch and environment jobs emitted the same subject and that a trust failure should be repaired by broadening access.

Migrate credentials in stages. First inventory each static key's owner, last-use evidence, permissions, consumers and rotation owner. Create an equivalent narrowly scoped role and OIDC provider using actual issuer/audience/subject claims. Keep the old credential available only during a short, monitored migration window; do not leave it active as a permanent fallback. Exercise the exchange in a non-production role and verify both permitted and denied subjects. Confirm logs identify the federated principal and test application behavior with read-only access before enabling writes.

Deploy the OIDC integration to one protected production job. Verify role identity with the provider's read-only identity command, validate the permission boundary against expected operations, and observe a successful deployment to a controlled target. Then remove the static key from the CI variable store and revoke it at the identity provider. Deleting the variable does not invalidate a key copied into a runner, cache, build log or developer machine. Review cloud audit logs from the key's last known use, CI logs/artifacts and runner state; rotate any credentials it could access. If OIDC cannot be restored promptly, use an explicitly approved break-glass path with a separate short-lived credential and named owner, then revoke it after recovery.

When a token exchange fails, preserve the denied request's timestamp, workflow/job identity, issuer, audience and subject without retaining the raw token. Compare those claims to the trust policy and check clock skew, issuer metadata/JWKS availability, provider registration and role permissions. A subject mismatch is a signal to correct the intended environment or policy, not a reason to wildcard trust. Roll back the deployment integration if needed while preserving a restrictive temporary path. After the fix, test a second context that must be denied, record the exact expected claim format and assign an owner for claim/policy drift reviews.

Exercises:

1. A GitHub deployment job adds `environment: Production`; its AWS trust policy still matches a `ref:refs/heads/main` subject. Why might the token be denied, and what evidence should you inspect before editing IAM?
2. A GitLab project is renamed and a trust policy uses only the project path in `sub`. How can stable identifiers reduce accidental trust breakage, and which GitLab offering supports those claim conditions?
3. A Kubernetes workload consumes a projected OIDC token but caches it in memory at startup. What expiry and refresh failure should be tested, and why is an API-server audience inappropriate for a different cloud relying party?

Answer guidance: inspect the token's issuer, audience and exact subject for the actual job; GitHub subjects include the environment context when a job uses an environment, and immutable IDs may be included depending on repository age/settings. Do not broaden trust before comparing those claims. GitLab.com supports `project_id` and `namespace_id` claims for AWS trust conditions; feature/claim availability differs by offering. Projected tokens expire and are refreshed in the mounted file, so the client must reread it and the relying party must accept the intended audience. A token minted for the Kubernetes API should not be accepted by a separate cloud service unless that service explicitly trusts and validates that audience.

Review questions:

- What do issuer, audience and subject each establish in a federation exchange?
- Why do short token lifetimes fail to protect against a compromised job that can request tokens during its run?
- Which evidence demonstrates that static credentials were revoked rather than merely removed from a CI settings page?

Takeaways:

- Trust requires exact issuer, audience and subject conditions plus a separately least-privileged role policy.
- CI and workload tokens are useful only when jobs and pods protect their authority and reload short-lived credentials correctly.
- Claim formats vary by workflow context, repository settings, provider and platform offering; inspect actual claims before changing trust.
- Replace static keys with a staged migration, test denial boundaries, revoke at the provider and verify old-key failure.

## Sources checked 2026-10-04

- [GitHub Actions OIDC reference](https://docs.github.com/en/actions/reference/security/oidc) — claims, environment/branch subject behavior and immutable subject rollout.
- [AWS IAM OIDC role guidance](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html) — required GitHub subject scoping and trust policy conditions.
- [GitLab CI cloud federation](https://docs.gitlab.com/ci/cloud_services/) and [GitLab AWS setup](https://docs.gitlab.com/ci/cloud_services/aws/) — ID token audience/subject and stable claim availability by offering.
- [Jenkins OpenID Connect Provider plugin](https://plugins.jenkins.io/oidc-provider/) — build-scoped tokens, issuer, claims and distinction from login authentication.
- [Kubernetes service accounts](https://kubernetes.io/docs/concepts/security/service-accounts/) and [projected volumes](https://kubernetes.io/docs/concepts/storage/projected-volumes/) — bound token audience, expiry and kubelet refresh behavior.
- [Chapter 175](175-secrets-and-credential-rotation.md) — secret consumer transition and revocation context.

These references and changing claim assumptions were checked on the listed date. No CI provider, IAM role, GitLab project, Jenkins issuer/plugin, Kubernetes service account, cloud credential, production deployment or key revocation was configured or tested.
