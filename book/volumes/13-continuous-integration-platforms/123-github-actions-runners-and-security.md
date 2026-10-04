---
book: The Complete DevOps Engineering Book
volume: 13
volume_title: "Continuous Integration Platforms"
chapter: 123
title: "GitHub Actions Runners and Security"
slug: github-actions-runners-and-security
status: complete
summary: ../../_ai/chapter-summaries/123-github-actions-runners-and-security.md
---

# Chapter 123 — GitHub Actions Runners and Security

## Hosted and self-hosted execution

A runner executes a job's steps. GitHub-hosted runners are provisioned and managed by GitHub; self-hosted runners are machines or environments that your organization registers with GitHub. Runner selection through `runs-on` and labels routes a job to eligible capacity. A label describes capability or routing; it does not prove the host is isolated, clean or safe for a particular trust level. Runner groups add repository access controls for shared organization or enterprise capacity, but administrators still own the host, network and cleanup boundary. See GitHub's [runner groups](https://docs.github.com/en/actions/concepts/runners/runner-groups) and [hosted runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).

The useful decision is where a job may execute and what it can reach. Hosted runners suit many public build and test workloads because they avoid placing contributor-controlled code directly on a persistent internal machine. Self-hosted runners can provide private network access, custom hardware, local caches or predictable capacity, but expose those resources to every workflow that can reach the runner. GitHub warns against using self-hosted runners with public repositories because a fork can propose workflow code that runs on the host. Treat private-repository pull requests as untrusted too when contributors can modify workflow files or build scripts.

A persistent runner may retain files, credentials, processes, container state, caches or modified tools between jobs. A cleanup script reduces leftovers but cannot prove that a compromised host has returned to a trustworthy state. For untrusted jobs, prefer a fresh, ephemeral runner that handles one job, then destroy the environment. Keep runner images and the runner application patched, restrict outbound network access, avoid mounting broad host paths or privileged container sockets, and keep runner administration separate from repository contribution rights. Forward ephemeral runner logs before disposal so failures and suspected compromises remain diagnosable. GitHub's [self-hosted runner reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners) describes ephemeral runners and notes that each receives one job.

Separate trust classes into distinct runner pools: untrusted pull-request validation, trusted branch builds, and deployment or signing. Restrict each group to the repositories and workflows that need it. Do not route fork code to a runner with production network access just because its label says `linux`. If private network access is required for a test, expose a narrow service or temporary test environment instead of granting the runner general access to internal systems. Runner group controls can limit which repositories target a pool, but code that is allowed to execute in that pool still has the permissions and network access of the runner's job.

## Permissions, OIDC and action pinning

The workflow and cloud account form one authorization system. Set a minimal `GITHUB_TOKEN` permission baseline, then grant extra scopes only to the job that needs them. A job with `contents: read` and `id-token: write` can request a GitHub OIDC token; that permission does not grant cloud access by itself. The cloud provider must trust GitHub's issuer and validate the token's audience and subject (or other supported claims) against the intended repository, branch, environment and workflow. A broad trust rule for an entire organization or repository can let unrelated workflows obtain the same role. See the [OIDC reference](https://docs.github.com/en/actions/reference/security/oidc) and [cloud provider setup guide](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-cloud-providers).

An environment changes the identity context used by OIDC and can gate a deployment job on required reviewers, branch restrictions or other configured rules. Environment secrets become available to the job only after protection rules pass. This is useful separation, but it does not sandbox code on a self-hosted runner: a compromised or reused host can retain state beyond the environment gate. Match the cloud trust policy to the actual subject format configured for the repository. GitHub's current OIDC documentation describes an immutable subject format with owner and repository IDs for newer repositories and opt-in repositories; existing trust policies may still use the earlier name-based format. Verify the emitted claims and cloud-side conditions when setting up or changing the trust policy.

Actions and reusable workflows execute code inside the job's security context. Pin third-party actions to a reviewed full commit SHA; tags can move, and a pin only makes a reference immutable, not trustworthy. Review the pinned source, maintenance history and permissions, and update pins through a visible review process. Limit secrets to the steps and jobs that need them. Avoid passing credentials to an action that handles untrusted data, and do not assume a marketplace action is safe because it is popular. Use organization policy to restrict allowed actions when that matches the team's release and maintenance model.

Events that run with privileged repository context need special care. `pull_request_target` can access the base repository's token and secrets, so it should not check out or execute the pull request's head code. Use it only for narrow metadata tasks that do not consume attacker-controlled code or artifacts. A workflow triggered by `workflow_run` also crosses a trust boundary: a privileged follow-up must validate the upstream run, source revision and any downloaded artifact before use. Keep untrusted test and build execution on ordinary pull-request workflows with read-only permissions, then hand off reviewed outputs through an explicit verification step. GitHub's [secure use reference](https://docs.github.com/en/actions/reference/security/secure-use) and [pull_request_target guide](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) detail these event risks.

## Hardening a deployment workflow

DispatchDesk tests API, worker and web changes on GitHub-hosted runners. A separate protected-branch workflow builds an immutable release artifact. A deployment job references a protected environment and exchanges a short-lived OIDC identity for narrowly scoped cloud credentials. The trust chain must bind the deployed digest to the intended source revision, and the deployment runner must not also accept arbitrary pull-request jobs.

```yaml
name: DispatchDesk release

on:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@<REVIEWED_FULL_COMMIT_SHA>
      - run: ./ci/build-release
      - uses: actions/upload-artifact@<REVIEWED_FULL_COMMIT_SHA>
        with:
          name: dispatchdesk-release
          path: dist/

  deploy:
    needs: [build]
    runs-on: [self-hosted, production-deploy]
    environment: production
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@<REVIEWED_FULL_COMMIT_SHA>
      - uses: actions/download-artifact@<REVIEWED_FULL_COMMIT_SHA>
        with:
          name: dispatchdesk-release
          path: dist/
      - name: Verify digest and provenance
        run: ./ci/verify-release dist/
      - name: Exchange OIDC identity and deploy
        run: ./ci/deploy-release dist/
```

This excerpt shows trust placement, not a deployable workflow. Replace action placeholders with reviewed immutable SHAs. The `build-release`, `verify-release` and `deploy-release` scripts represent repository-owned interfaces and must be implemented and tested. The deploy job checks out the repository because each job runs in its own workspace; it must not rely on build-job files carrying over. Alternatively, package the scripts in a separately verified tool. The uploaded artifact must have a bounded retention policy and be verified against the expected run, source commit and digest before deployment. Artifact transfer alone does not prove provenance.

In production, keep the deployment runner pool inaccessible to pull-request jobs, constrain its egress and cloud role, and rebuild or destroy it after each deployment. Use an environment with required protection rules and scope the cloud trust policy to that environment and the intended repository or reusable workflow. Concurrency should serialize deployments to the same target; cancellation policy should not interrupt an operation that has already changed live state. Record the source revision, artifact digest, environment approval and deployment result so operators can trace what ran.

A workflow review should ask which event can start each job, what code that job executes, which runner can receive it, what token and secrets it can access, and which network destinations it can reach. Validate the answers against both workflow YAML and repository, organization, runner-group, environment and cloud settings. YAML parsing cannot test those external controls. Use a disposable repository and cloud role for an end-to-end rehearsal before granting production authority. [Chapter 122](122-github-actions-workflows.md) covers workflow construction; the next chapters apply the same boundary analysis to GitLab pipelines and runners.

## Takeaways

Choose runners by trust and reachable resources, not by label alone. Use ephemeral isolated execution for untrusted work, and bind OIDC access to a narrowly verified repository, ref or environment identity.

## Exercises and answer guidance

1. A public repository uses a persistent self-hosted runner for fork pull requests. What is exposed? The fork can propose workflow or build code that executes on the host, potentially accessing residual data, credentials and reachable networks; move untrusted work to isolated ephemeral runners or hosted runners.
2. A workflow grants `id-token: write` to every job. Does that let every job access cloud resources? Only if the cloud trust policy accepts the token's claims, but broad permissions increase the number of jobs able to request an identity. Grant it only to the deployment job and narrowly bind the cloud policy.
3. A job uses a reviewed action pinned to a full SHA. What does that guarantee? It fixes the referenced action revision; it does not establish that the code is safe, maintained or least-privileged.
4. A `pull_request_target` workflow checks out a fork branch and runs its tests using repository secrets. What is the flaw? It executes attacker-controlled code in a privileged context. Keep that event to metadata work, or use an unprivileged pull-request event for code execution.
5. A protected environment requires approval, but the job runs on a persistent shared self-hosted runner. What additional boundary is needed? Isolate the runner pool from untrusted jobs and discard or reliably rebuild runner state; environment approval does not clean or sandbox the host.
6. A deploy job downloads an artifact from an earlier workflow run. What must be verified? The producing run and source revision, expected artifact identity and digest, provenance or attestation where used, and whether the producer was allowed to handle untrusted changes.

Review questions: how do runner trust classes differ, what does OIDC permission authorize by itself, which cloud claims should be constrained, and why do environment approvals not replace runner isolation?

## Verification and primary sources

Official GitHub documentation for hosted and self-hosted runners, runner groups, OIDC, deployments and secure use was inspected on 2026-10-04. The YAML is illustrative, contains unresolved action SHA placeholders, and was not executed. Static parsing does not validate GitHub's workflow schema, action availability, cloud trust policy, runner group access, environment protection, script behavior, artifact provenance or production deployment safety.

Primary references: [GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners), [self-hosted runners](https://docs.github.com/en/actions/reference/runners/self-hosted-runners), [runner groups](https://docs.github.com/en/actions/concepts/runners/runner-groups), [OIDC](https://docs.github.com/en/actions/reference/security/oidc), [secure use](https://docs.github.com/en/actions/reference/security/secure-use), [securely using pull_request_target](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target), and [deployments and environments](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments).
