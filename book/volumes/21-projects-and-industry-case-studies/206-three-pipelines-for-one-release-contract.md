---
book: The Complete DevOps Engineering Book
volume: 21
volume_title: "Projects and Industry Case Studies"
chapter: 206
title: "Three Pipelines for One Release Contract"
slug: three-pipelines-for-one-release-contract
status: complete
summary: ../../_ai/chapter-summaries/206-three-pipelines-for-one-release-contract.md
---

# Chapter 206 — Three Pipelines for One Release Contract

**Section outline:** GitHub Actions implementation; GitLab CI and Jenkins implementations; comparing evidence, credentials and recovery.

## Define the release contract first

DispatchDesk has repositories using GitHub Actions, GitLab CI and Jenkins after a merger. The teams want comparable evidence and security even though their pipeline syntax and credential models differ. They agree on one release contract: review source, run tests, build an immutable artifact once, record provenance, scan and sign it, publish it to a controlled registry, deploy the same digest through an approved environment, verify user outcomes and retain a rollback reference.

The contract says which branch or tag may publish, which identity can write artifacts, what approvals gate production, which evidence is retained, and who responds to a failed rollout. It does not require identical YAML or make every provider feature equivalent. Pin third-party actions/plugins by immutable version or digest where supported, scope tokens to the job, and keep untrusted pull-request code away from deployment credentials. Chapters 123–130 cover platform specifics; Chapters 175–179 cover identity and artifact evidence.

## GitHub Actions example

A simplified workflow shows job boundaries and a placeholder deployment. Production credentials are intentionally not supplied as long-lived repository secrets; use a narrowly trusted OIDC role and environment protection configured for the actual organization.

```yaml
name: release-contract
on:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  verify:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
      - run: ./ci/test.sh
  publish:
    needs: verify
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
      packages: write
    steps:
      - uses: actions/checkout@v4
      - run: ./ci/build-and-publish.sh
```

The fragment is illustrative: `@v4` is a moving major tag and production pipelines should pin trusted actions according to organizational policy; the publish script must produce and report an immutable digest. Job-level `permissions` replaces the workflow-level set for that job, so the verification job gets read-only source access while only the trusted main-branch publish job receives package-write and OIDC token permissions. Configure environment protection and constrain OIDC trust to repository, ref/environment and reusable-workflow claims as appropriate. `id-token: write` only allows requesting a token; the cloud role's trust policy determines whether it is accepted. GitHub documents OIDC and reusable workflow trust in its [OIDC reference](https://docs.github.com/en/actions/reference/security/oidc).

## GitLab CI and Jenkins equivalents

GitLab can express stages, protected environments, job tokens and OIDC ID tokens in `.gitlab-ci.yml`. A minimal shape is:

```yaml
stages: [verify, publish, deploy]
verify:
  stage: verify
  script: ./ci/test.sh
publish:
  stage: publish
  script: ./ci/build-and-publish.sh
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

The publishing identity, protected-branch policy, artifact retention, runner trust and any ID-token audience/claims still require explicit configuration. A shared runner can expose one job to another tenant's workload if isolation is weak. See [GitLab ID tokens](https://docs.gitlab.com/ci/secrets/id_token_authentication/) and [CI/CD YAML reference](https://docs.gitlab.com/ci/yaml/).

Jenkins represents the process in a `Jenkinsfile`, often with controller-managed credentials and isolated agents. Keep secrets scoped to the smallest folder/job and bind them only around trusted steps. A build that executes pull-request code must not receive deployment credentials merely because the same pipeline later deploys. Jenkins warns about credentials exposure in multibranch jobs; see [Jenkins credential security](https://www.jenkins.io/doc/book/security/credentials/) and its [multibranch security guidance](https://www.jenkins.io/doc/book/security/securing-org-folders-and-multibranch-pipelines/).

```groovy
pipeline {
  agent { label 'isolated-builder' }
  stages {
    stage('Verify') {
      steps { sh './ci/test.sh' }
    }
    stage('Publish') {
      when { branch 'main' }
      steps { sh './ci/build-and-publish.sh' }
    }
  }
}
```

This omits plugin installation, credential bindings, artifact repository setup and approvals; those are security and operational configuration, not harmless boilerplate. Pin Jenkins core and plugins, isolate agents, restrict script approval, back up controller configuration and separately protect keys needed for recovery.

## Compare evidence and recoverability

For each provider, test a trusted main-branch release and an untrusted fork/merge request. Verify which identity each job receives, where logs/artifacts are retained, whether a rerun rebuilds a different digest, and who can approve production. Record source commit, workflow/config revision, builder identity, artifact digest, test/scan/signature results, deployment target and observed rollout result in a durable release record. A green pipeline is not proof that the running service uses the tested image unless deployment receipt is linked to that digest.

A failed release should have a bounded stop/rollback procedure, database compatibility strategy and one clear deployment authority. Pipeline failure must not leave a half-published artifact marked releasable. Practice credential rotation and pipeline recovery when the CI control plane is unavailable. Compare ease of audit, isolation, maintenance, runner capacity and operator skill; provider labels do not guarantee equivalent security.

The contract includes provenance and retention independent of provider vocabulary. Preserve the workflow definition revision and the identity that initiated each privileged job. Keep release attestations and logs long enough to investigate a later incident, with access limited and secrets masked. Make reruns explicit: rerunning a test against a retained artifact differs from rebuilding source, and rerunning a deployment differs from a new release. A manual approval should identify the target environment and digest, expire when the plan changes, and leave an audit record. For an emergency fix, document the narrower path and restore normal review/verification controls afterward. This lets different CI systems satisfy common governance without claiming that one provider's feature name has the same security semantics in another.

 A migration between CI products should preserve evidence continuity. Keep old and new pipelines from publishing the same release independently, compare their artifact digests and test results, and define a cutover owner. Protect the old pipeline until the new one has passed a real rollback and credential rotation exercise. Retire obsolete credentials, webhooks and runners after traffic is verified on the new path.

Exercises:

1. A pull request can modify the test script and read a cloud deployment token. Which trust boundary failed?
2. A pipeline rerun rebuilds a different image from the same commit. What is missing from the release contract?
3. GitLab reports a green deploy job, but the cluster runs another digest. Which evidence link is absent?
4. Jenkins controller backups exist, but the restored instance cannot decrypt stored credentials. What recovery dependency was omitted?

Answer guidance: untrusted source code executed in a job with excessive credentials; isolate validation from publication/deployment and enforce trusted refs and identity claims. Preserve and promote the exact built artifact, pin dependencies/toolchains and record provenance; do not silently rebuild for promotion. Link job and artifact digest to deployment controller's observed revision and runtime image identity. Protect Jenkins secrets/key material through a separately controlled recovery path and test restore without coupling compromise domains.

Review questions:

- Which properties form the common release contract across CI products?
- How do OIDC and protected environments reduce static credential exposure?
- Why is runner/agent isolation part of pipeline security?
- What joins source, tested artifact and deployed runtime in the audit record?

Takeaways:

- Standardize required release evidence and controls while respecting product-specific configuration.
- Keep untrusted code separate from publication and deployment authority.
- Promote the same immutable digest and bind deployment evidence to it.
- Test failed release, credential rotation and CI recovery paths.

## Sources checked 2026-10-04

- [GitHub Actions OIDC](https://docs.github.com/en/actions/reference/security/oidc) and [reusable workflow OIDC](https://docs.github.com/en/enterprise-cloud@latest/actions/how-tos/secure-your-work/security-harden-deployments/oidc-with-reusable-workflows).
- [GitLab ID token authentication](https://docs.gitlab.com/ci/secrets/id_token_authentication/) and [CI/CD YAML](https://docs.gitlab.com/ci/yaml/).
- [Jenkins credentials](https://www.jenkins.io/doc/book/security/credentials/) and [multibranch pipeline security](https://www.jenkins.io/doc/book/security/securing-org-folders-and-multibranch-pipelines/).

YAML and pipeline fragments are teaching shapes and have not been run. No CI account, runner, plugin or deployment was configured.
