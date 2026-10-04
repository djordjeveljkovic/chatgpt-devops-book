---
book: The Complete DevOps Engineering Book
volume: 13
volume_title: "Continuous Integration Platforms"
chapter: 122
title: "GitHub Actions Workflows"
slug: github-actions-workflows
status: complete
summary: ../../_ai/chapter-summaries/122-github-actions-workflows.md
---

# Chapter 122 — GitHub Actions Workflows

## Events, jobs, steps and expressions

A GitHub Actions workflow is a YAML file under `.github/workflows` that defines events, permissions, concurrency and one or more jobs. An event such as `push`, `pull_request`, `workflow_dispatch` or `schedule` creates a run. Jobs form a dependency graph through `needs`; independent jobs can run concurrently, while steps inside one job run in order on the assigned runner. A job starts with a fresh virtual environment only when the runner implementation provides that isolation; self-hosted runner cleanup and reuse are operator responsibilities. Workflow syntax and available events evolve, so check the [workflow reference](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) against the repository's current policy.

Choose triggers deliberately. A `pull_request` workflow can validate proposed changes, while a protected-branch `push` workflow can build release artifacts from merged code. Avoid triggering duplicate push and pull-request runs for the same branch without understanding branch filters and skip behavior. Scheduled workflows use the default branch's workflow and can experience delayed starts during load. Manual workflows need constrained inputs and a clear policy for which ref may be selected. Triggers decide when automation starts; job-level `if` conditions and environment protections decide which eligible stages proceed.

Use `permissions` to grant the `GITHUB_TOKEN` the minimum access required. If any permissions are listed, unspecified permissions are set to `none`; a workflow can grant read-only access by default and use job-level permissions for a stage that needs a specific write scope. A cloud deployment using GitHub OIDC may need `id-token: write` for that job, but the cloud trust policy must separately limit which repository, ref, environment and audience can assume a role. A permission declaration limits this token; it does not constrain other secrets or credentials injected through organization settings or third-party actions. See the GitHub [token permission reference](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions).

Jobs run on an environment selected by `runs-on`. A GitHub-hosted runner is managed by GitHub, while a self-hosted runner is part of the organization's infrastructure and network boundary. Labels select eligible runners; they are not themselves a security boundary. A job handling untrusted pull-request code should not share a persistent host or privileged network with a release job. Environment protection rules can require reviewers or restrict branches before a deployment job receives environment secrets, depending on repository plan and settings. Keep deployment jobs short and isolate their permissions from test jobs.

Expressions use contexts such as `github`, `env`, `matrix`, `needs`, `inputs`, `vars` and `secrets`. Context availability depends on where an expression appears. Treat contributor-controlled context values such as pull-request titles, branch names, commit messages and labels as untrusted data. Do not interpolate them directly into a shell program. Pass data through an environment variable or a file and handle it as data with the appropriate quoting and validation. For example, reading a pull-request title into an environment variable is safer than expanding the expression into shell source, though the value still needs validation before being used in commands or API calls. GitHub's [script injection guidance](https://docs.github.com/en/actions/concepts/security/script-injections) lists common untrusted contexts.

Outputs let a job communicate selected values to dependent jobs. Use them for small metadata such as an artifact digest or decision result, not as a general file-transfer mechanism. Upload build output as an artifact or publish it to a package registry; then verify the expected name, producer, source commit and digest before a privileged job consumes it. Avoid writing secrets to `$GITHUB_OUTPUT`, `$GITHUB_ENV`, job summaries, caches or artifacts. The runner's command files are part of the workflow interface and must not receive attacker-controlled strings without validation and correct encoding.

Concurrency groups coordinate workflow runs or jobs. They can cancel outdated validation runs or serialize deployments to one environment. With cancellation enabled, a new run may stop an in-progress run in the same group. This is useful for linting an older commit, but may be unsafe for a deployment that has already begun changing infrastructure. For releases, choose queuing or explicit serialization semantics that preserve the intended order; don't apply `cancel-in-progress: true` globally without considering the side effects of cancellation. Read GitHub's [concurrency guide](https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency) for current queuing and cancellation behavior.

## Reusable workflows and matrices

A matrix expands one job definition across a set of values, such as language, operating system, architecture or runtime version. This reduces duplicated YAML and makes the test dimensions visible. Keep matrices purposeful: every combination consumes runner capacity and can multiply time and cost. Use `include` and `exclude` when some components support different runtimes, and use `fail-fast: false` when independent failures are more useful than canceling remaining jobs after the first error. Matrix dimensions should come from trusted workflow configuration; avoid constructing privileged runner labels or deployment targets from untrusted pull-request text.

Reusable workflows standardize an entire job graph and can accept typed inputs, secrets and outputs. A caller invokes a reusable workflow at the job level; a composite action bundles steps within a job. Use a reusable workflow when teams need one reviewed process such as building, testing, releasing or deploying. Version reusable workflows with a protected tag or immutable commit reference, and review changes like shared library releases. The called workflow's token permissions can remain the same or be reduced through the call chain, not elevated. Pass only required secrets; `secrets: inherit` broadens the called workflow's access and should be avoided unless every inherited secret is appropriate. `env` values declared by a caller do not automatically propagate into a reusable workflow; use typed inputs and declared outputs instead. See GitHub's [reusable workflow guide](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows).

An organization can centralize common workflows but should preserve repository-level ownership over application tests and deployment approvals. A centrally maintained workflow can still run repository-controlled code, install project dependencies and execute tests. Do not treat the workflow's trusted source as proof that its inputs are trusted. Reusable workflow callers also control parameters and may pass untrusted source, artifacts or strings; define input validation, token scope and artifact expectations at the boundary.

Third-party actions are executable dependencies. Review the source, permissions, release process and maintenance history. Pin actions to full commit SHAs under an update policy so a mutable tag cannot silently change the code executed by a privileged job. Dependabot or another review process can propose updates, but teams still need to inspect them. A pinned action can still have vulnerabilities or request more context than necessary; a pin provides immutability, not a security endorsement. Prefer a small set of approved actions, and avoid passing secrets to an action that does not require them.

## A multi-language test workflow

DispatchDesk contains an API, a queue worker and a web client. Each component has its own runtime and test command. A useful CI graph gives contributors fast feedback on each changed component, while retaining a common security boundary: pull-request jobs use read-only token permissions, isolated runners, no release credentials and no privileged network access. A protected-branch workflow builds release artifacts after merge, records digests and provenance, and exposes a separate deployment job only after review.

The following structural excerpt shows trigger, permission, matrix and dependency relationships. The action reference is intentionally a placeholder: replace it with a reviewed full commit SHA and validate the complete file against the repository's current Actions policy before use.

```yaml
name: DispatchDesk CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true

jobs:
  component-tests:
    strategy:
      fail-fast: false
      matrix:
        component: [api, worker, web]
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@<REVIEWED_FULL_COMMIT_SHA>
      - name: Test component
        env:
          COMPONENT: ${{ matrix.component }}
        run: ./ci/test-component "$COMPONENT"

  artifact:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: [component-tests]
    permissions:
      contents: read
      packages: write
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@<REVIEWED_FULL_COMMIT_SHA>
      - name: Build and publish immutable artifact
        run: ./ci/build-and-publish
```

This is a workflow shape, not a ready-to-run file. The `component-tests` command is repository-owned and should invoke each component's lockfile-based, reproducible test process. The placeholder action reference must be replaced before GitHub can resolve the checkout action. The publish command represents an authenticated operation and needs a deliberately scoped package credential or federated identity; it should not inherit the write permission into test jobs. Each job gets its own runner workspace, so the artifact job checks out its source before invoking the repository-owned build command. A production workflow should verify that the built digest corresponds to the tested source and publish provenance. It should also separate untrusted pull-request builds from any artifact publication if the registry or artifact can later be consumed by privileged jobs. The concurrency group uses the pull-request number so same-named branches from different forks do not collide; on non-pull-request runs it falls back to the ref. The setting is suitable only for supersedable validation; do not reuse it unchanged on a deployment job where cancellation could interrupt an operation.

For multiple language versions, matrix axes can run separate toolchain checks. If the API supports only some runtime versions while the web client uses another, use one matrix per job or a reusable workflow with validated inputs rather than a Cartesian product that creates invalid combinations. A version matrix tests compatibility across the requested versions, but it does not prove support for every operating system, dependency resolver or production runtime. Record which axes are contractual and which are best-effort.

Workflow changes need their own review. A YAML parser confirms syntax, not event semantics, job permissions, action availability, expression safety, runner availability or artifact provenance. Test an unprivileged pull request, a protected branch, a canceled run and a failed dependency. Use a disposable repository or environment to verify behavior before connecting a workflow to signing keys, cloud roles or production deployment permissions. [Chapter 121](121-ci-architecture-and-trust-boundaries.md) covers the cross-platform trust boundary; a later chapter in this volume covers GitLab's pipeline model.

## Takeaways

Treat workflow files and actions as executable code. Scope permissions per job, pass untrusted values as data, and design concurrency, artifacts and reusable workflows around their actual trust and cancellation behavior.

## Exercises and answer guidance

1. A workflow uses a pull-request title directly inside a `run` script expression. What is the concern? The title is attacker-controlled and can become shell syntax; pass it as data and validate/quote it before use.
2. A reusable workflow requests `secrets: inherit`. What should be checked? Which secrets are available to the caller, what code the called workflow executes, whether every inherited value is needed, and whether the called workflow is pinned and reviewed.
3. A matrix build has many language and OS combinations, several of which cannot work together. How should it be redesigned? Separate compatible axes by job or reusable workflow, explicitly include/exclude valid combinations and control runtime/cost.
4. A newer validation run cancels an in-progress deployment because both share a concurrency group with `cancel-in-progress: true`. What failed? The group combined workflows with different cancellation semantics; isolate deployment concurrency and use a queue or safe serialization policy.
5. The artifact job has `packages: write`, and tests run in the same job. Is job-level permission scoping enough? No. Untrusted test code running within the job can access job credentials; separate jobs and ensure untrusted artifacts are validated before privileged consumption.
6. A third-party action is pinned to a full SHA. Does that establish trust? No. Review provenance, source and permissions, keep an update process, and limit its access.

Review questions: how do events determine a workflow run, how do jobs and steps differ, when should a matrix or reusable workflow be used, and how can expressions, credentials and concurrency change security or release behavior?

## Verification and primary sources

Official GitHub Actions workflow, expression, context, concurrency, reusable workflow and security documentation was inspected on 2026-10-04. The YAML is a structural excerpt with an intentionally unresolved action SHA and was not executed. No workflow, repository, runner, token, artifact or deployment was configured. Static parsing does not validate GitHub's workflow schema, event behavior, action resolution, permissions, runner state, script safety or release correctness.

Primary references: [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [contexts](https://docs.github.com/en/actions/concepts/workflows-and-actions/contexts), [script injections](https://docs.github.com/en/actions/concepts/security/script-injections), [reusable workflows](https://docs.github.com/en/actions/how-tos/reuse-automations/reuse-workflows), [concurrency](https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency), and [secure use](https://docs.github.com/en/actions/reference/security/secure-use).
