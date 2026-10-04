---
book: The Complete DevOps Engineering Book
volume: 13
volume_title: "Continuous Integration Platforms"
chapter: 125
title: "GitLab Runners and Credentials"
slug: gitlab-runners-and-credentials
status: complete
summary: ../../_ai/chapter-summaries/125-gitlab-runners-and-credentials.md
---

# Chapter 125 — GitLab Runners and Credentials

## Executor choices and runner isolation

A GitLab Runner polls GitLab for jobs and uses an executor to run each job. The executor defines the execution environment and much of its isolation boundary. A shell executor runs scripts as the runner user's account on the host; GitLab warns that jobs can access files from other projects scheduled on that machine. Use it only for jobs whose authors and code are trusted, and avoid mixing trust levels on a shared host. A Docker executor creates a container, but containers share the host kernel and their safety depends on runner configuration. A Kubernetes executor creates pods, but cluster-wide permissions, mounted volumes, node placement, service accounts and container security settings still matter. A container or pod is a useful boundary only when configured and operated as one.

Privileged Docker execution grants the job broad access to host capabilities and can enable container escape; mounting the Docker socket can similarly expose the host daemon. Reserve these configurations for isolated, disposable machines dedicated to trusted image builds. Avoid host PID namespaces and broad host mounts. When jobs require only ordinary compilation and tests, use non-privileged containers, run as a non-root user where feasible, drop unneeded Linux capabilities, restrict images and services, and limit network access. A runner setting controls the maximum privilege available; project YAML and job scripts should not be able to override it. GitLab's [runner security guide](https://docs.gitlab.com/runner/security/) and [executor documentation](https://docs.gitlab.com/runner/executors/) describe these tradeoffs.

Runner tags route jobs to runners with matching labels. They do not, by themselves, make a runner protected or trusted. Lock sensitive runners to the intended project or group, configure them as protected when they should serve only protected refs, and control who can change runner settings. Separate untrusted merge-request validation, trusted default-branch builds and production deployment into different runner pools. GitLab 18.1 added controls for protected variables and runners in merge-request pipelines: access is permitted only when both source and target branches are protected, the triggering user can push or merge to the target, and both branches belong to the same project. Fork merge requests cannot access these protected resources. This is a conditional feature, not a reason to schedule fork code on a privileged runner. Confirm the deployed GitLab version and setting before relying on it. See [merge-request pipeline controls](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/).

Ephemeral capacity limits what a compromised job can leave behind. Prefer a fresh VM, instance or isolated pod per job for untrusted or privileged workloads, then delete it after the job. Autoscaling reduces idle capacity but does not automatically provide isolation if an instance can run multiple jobs or reuses caches, filesystems, credentials or network identity. Remove temporary credentials, persist runner and system logs externally, patch runner software and base images, and monitor runner registration and job assignment. Keep deployment runners out of general-purpose pools and constrain their route to only the deployment endpoints they require.

## Protected variables and federated identity

GitLab CI/CD variables can be defined at project, group or instance level. Their scope may be broad even when a pipeline job appears local. Use protected variables for secrets that should be available only on protected refs, and limit environment scope when different deployment environments need different credentials. Masking reduces accidental log disclosure; it cannot stop malicious job code from sending a value over the network or encoding it in another output. Never print credentials for debugging. Untrusted merge-request code should not receive release secrets, and credentials should not be available to test jobs that do not need them. GitLab's [CI/CD variables guide](https://docs.gitlab.com/ci/variables/) documents availability and protection behavior.

`CI_JOB_TOKEN` is a short-lived token created for a running job and revoked when the job finishes. It can access a limited set of GitLab features; its effective access is tied to the user who triggered the pipeline and their permissions. Cross-project access is normally constrained by the target project's job-token allowlist, and access can also depend on the triggering user's role. A broad group allowlist can include projects created later under that group, so prefer individual project entries where possible and audit them periodically. Avoid storing the token in artifacts, caches, job logs or persistent runner state. Do not mistake a job token's short lifetime for harmless access: while the job runs, malicious code can use every resource that token and its user can reach. See [CI/CD job token security](https://docs.gitlab.com/ci/jobs/ci_job_token/).

For cloud access, prefer a GitLab OIDC ID token exchanged for a short-lived cloud credential over a long-lived cloud key stored as a CI variable. Declare the token only on the job that needs it and set the exact audience the cloud identity provider expects. The cloud role must validate issuer, audience and a narrowly scoped subject or supported claims such as project identity, protected ref and pipeline source. Claim availability varies by provider and offering: for example, GitLab documents `namespace_id` and `project_id` condition keys for AWS when the identity provider is GitLab.com, but not for Self-Managed or Dedicated. Verify actual token claims and provider support before writing the trust policy. A `production` environment name in YAML does not itself limit the cloud role.

The following excerpt illustrates job-local identity and deployment gating. It is intentionally schematic; replace the audience and script with provider-specific reviewed values.

```yaml
deploy-production:
  stage: deploy
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
  environment:
    name: production
  id_tokens:
    CLOUD_ID_TOKEN:
      aud: https://cloud.example.invalid
  script:
    - ./ci/exchange-oidc-and-deploy
```

The OIDC exchange script should send the token to the configured identity endpoint without logging it, validate the returned credential lifetime and scope, and use it only for the required deployment. Protected environments and deployment approvals require GitLab Premium or Ultimate. Configure the production environment as protected and limit who can start or approve deployments when the tier supports it; on Free tier, follow the restricted-branch and external-control alternative in [Chapter 124](124-gitlab-ci-pipeline-design.md). The trust policy must enforce authorization even if someone changes the job's YAML; a branch rule in the file alone is not an external authorization control. Use a negative test to prove a fork or unprotected branch cannot obtain a cloud credential.

## Operating runners without cross-job leakage

DispatchDesk uses separate runner classes. Fork merge requests use isolated, unprivileged execution with no internal network route. Trusted default-branch jobs build release artifacts. A deployment job runs on a locked, protected runner and requests an OIDC token whose cloud trust policy accepts only the intended project and protected deployment context. Runner administrators own the boundary between those pools; a contributor-controlled tag in YAML cannot create access to an otherwise restricted runner.

Runner configuration should prevent cross-job leakage. Do not keep registry credentials in the runner user's home directory, shared Docker config, shell profile or host environment. GitLab warns that credentials present in the runner account's Docker configuration may be available to every job the runner runs. Use job-scoped authentication, remove temporary files, isolate work directories, and destroy ephemeral hosts. For a Docker or Kubernetes executor, prevent one tenant from reading another job's workspace, cache, service container or secret volume. Treat caches as untrusted inputs when they can cross branch or trust boundaries; separate keys by project and trust class, and validate cached content before use.

Use GitLab's recommended runner-creation workflow and runner authentication tokens. Legacy runner registration tokens are deprecated and disabled by default in GitLab 17.0 and later; protect the authentication token stored in the runner's `config.toml`, rotate or revoke it after exposure, and remove stale or unknown runners. See [runner registration migration](https://docs.gitlab.com/ci/runners/new_creation_workflow/). Keep runner versions compatible with the GitLab server and upgrade promptly for security fixes. Track assignment, job duration, runner image/version, executor, project and ref so that an unexpected job can be traced. A runner's network policy should start with no unnecessary access and allow only GitLab, required artifact and package endpoints, and the systems needed by that job. Build jobs generally should not have access to production databases or control planes.

Before using privileged builds, document why a less powerful builder will not work and isolate the exception. Validate that an untrusted job cannot reach a protected runner, protected variable, cloud role, registry write token or cross-project artifact. Test both positive and negative cases after changes to runner tags, protected-branch settings, job-token allowlists, environment controls or cloud trust. GitLab's [runner security guidance](https://docs.gitlab.com/runner/security/) specifically warns that shell executors and privileged containers can expose host resources; policy must be verified on the installed runner, not inferred from YAML alone.

## Takeaways

Executor isolation, token scope and network reachability jointly define runner risk. Keep untrusted jobs away from protected credentials, and verify protected-resource and OIDC policies on the deployed GitLab offering.

## Exercises and answer guidance

1. A shared shell runner handles public merge requests and production builds. What is the principal risk? The jobs execute on the same host account and may read or alter each other's state; separate trust classes and use isolated, preferably ephemeral, execution for untrusted code.
2. A Docker executor runs jobs with `privileged = true` because one project builds images. What should change? Move that workload to a dedicated disposable runner pool and keep ordinary test jobs non-privileged; privileged container mode weakens host isolation.
3. A masked variable is available to a merge-request script. Is it safe because logs redact it? No. The script can transmit or encode it. Restrict secret availability and keep untrusted code away from credentials.
4. An allowlist grants a whole group access to a project's job token resources. What can expand over time? New projects under that group may inherit allowlist eligibility; use narrower entries and audit group membership and token permissions.
5. An OIDC role trusts any branch in a GitLab group. What is missing? Conditions that bind issuer and audience plus the exact project, protected ref/environment and expected pipeline source, using claims supported by that GitLab offering and cloud provider.
6. A protected runner is selected with a tag in `.gitlab-ci.yml`. Is the tag alone sufficient? No. Runner protection, scope, project access and administrative controls must prevent unauthorized jobs from being assigned to it.

Review questions: what isolation does each executor actually provide, how are protected merge-request resources conditionally available, what does `CI_JOB_TOKEN` inherit, and how should an OIDC cloud role constrain the requesting job?

## Verification and primary sources

Official GitLab documentation for runner executors and security, protected CI/CD variables, merge-request protected-resource conditions, job-token access and OIDC ID tokens was inspected on 2026-10-04. The YAML is an illustrative excerpt with an example audience and unimplemented script; it was not executed. Static parsing cannot validate a runner's executor settings, host isolation, project allowlists, variable exposure, GitLab edition, token claims, cloud trust conditions or deployment network.

Primary references: [Runner security](https://docs.gitlab.com/runner/security/), [executors](https://docs.gitlab.com/runner/executors/), [CI/CD variables](https://docs.gitlab.com/ci/variables/), [merge request pipelines](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/), [CI/CD job token](https://docs.gitlab.com/ci/jobs/ci_job_token/), [OIDC ID tokens](https://docs.gitlab.com/ci/secrets/id_token_authentication/), and [cloud services](https://docs.gitlab.com/ci/cloud_services/).
