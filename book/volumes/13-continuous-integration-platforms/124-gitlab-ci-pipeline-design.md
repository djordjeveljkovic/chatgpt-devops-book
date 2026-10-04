---
book: The Complete DevOps Engineering Book
volume: 13
volume_title: "Continuous Integration Platforms"
chapter: 124
title: "GitLab CI Pipeline Design"
slug: gitlab-ci-pipeline-design
status: complete
summary: ../../_ai/chapter-summaries/124-gitlab-ci-pipeline-design.md
---

# Chapter 124 — GitLab CI Pipeline Design

## Stages, jobs, rules and includes

GitLab reads `.gitlab-ci.yml` to construct a pipeline of jobs. Stages provide a broad sequence: jobs in a later stage normally wait for earlier stages to finish. `needs` declares specific job dependencies and allows a job to start as soon as its required predecessors finish, forming a directed acyclic graph. This can shorten feedback time in a monorepo, but every dependency also documents required outputs and failure coupling. Use `needs: []` only for jobs that truly have no prerequisite. GitLab's [needs reference](https://docs.gitlab.com/ci/yaml/needs/) describes how DAG scheduling differs from stage barriers.

`workflow: rules` determines whether a pipeline is created; job-level `rules` determines whether a job is included in that pipeline and can set its behavior. Rule order matters: the first matching rule decides. A final catch-all rule can unintentionally create both branch and merge-request pipelines for the same change. Decide which sources should create a pipeline—merge request events, default-branch pushes, schedules, tags or manual dispatch—and express that policy explicitly. Variables such as `CI_PIPELINE_SOURCE` describe the event that created a pipeline; a branch name alone does not distinguish a push from a merge-request pipeline.

GitLab requires merge-request pipeline rules directly in the root `.gitlab-ci.yml`, either under `workflow: rules` or on jobs. Rules only inside an included file or component do not satisfy this requirement. Merge-request pipelines test the source branch contents; merged-results pipelines test a synthetic result containing the source and target branches. These pipelines can therefore report different failures. A fork merge request normally runs in the fork project with its configuration, resources and variables. If a parent-project member starts a pipeline using the fork's configuration in the parent context, that pipeline may use parent resources and variables. Treat the configuration and source code as untrusted until reviewed; Chapter 121 explains this trust boundary in detail. See [merge request pipelines](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/).

Use `include` to organize a large configuration, share reviewed templates or consume a reusable CI/CD component. Includes expand into the pipeline configuration; they are not a runtime isolation boundary. A change to a centrally included file can alter jobs, images, scripts, permissions or deployment conditions across consumers. Pin cross-project includes and components to an immutable commit or reviewed version, establish an update process, and inspect the fully expanded configuration in the GitLab CI Lint view. Inputs and variables passed into included configurations should be validated and narrowly scoped. Avoid relying on implicit precedence between several sources of defaults; make ownership clear. GitLab documents [configuration includes](https://docs.gitlab.com/ci/yaml/includes/) and [CI/CD components](https://docs.gitlab.com/ci/components/).

## Artifacts, dependencies and environments

A job receives a workspace on a runner. Files created in one job do not become available to another just because the jobs use the same stage or project. A job artifact is an explicit output that GitLab stores and can pass to later jobs. A cache is a performance optimization for reusable inputs such as downloaded dependencies; it may be missing, stale or overwritten and must never be the correctness or authorization mechanism. Keep artifact paths narrow, set retention intentionally, and avoid storing credentials or sensitive test data in artifacts. By default, later stage jobs fetch artifacts from earlier stages; `needs:artifacts` or `dependencies` can narrow which artifacts are downloaded. See GitLab's [job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/) and [cache](https://docs.gitlab.com/ci/caching/) references.

With `needs`, each job should name the artifacts it consumes. For example, a test job can need the build job and receive its artifact, while an independent lint job can run in parallel. Be careful when a needed job is excluded by `rules`: a non-optional dependency on a job absent from the pipeline can make pipeline creation fail. Use matching rules across dependent jobs, or use `optional: true` only when the downstream job has a meaningful path without that input.

Environments name deployment targets such as `staging` and `production` and let GitLab track deployment history. Protected environments and deployment approvals are Premium and Ultimate features; when enabled, they can gate who may deploy. A YAML `environment:` declaration does not itself secure a runner, cloud role or secret. On Free-tier projects, use restricted protected-branch permissions and keep production credentials behind a separately controlled deployment project or cloud-side trust policy. A manual job can require an operator action, but it is not equivalent to protected-environment approval. See [protected environments](https://docs.gitlab.com/ci/environments/protected_environments/). Restrict protected variables and deployment credentials to the intended protected refs and authorized jobs, and configure cloud identity trust independently. Do not expose deployment credentials to jobs that execute unreviewed merge-request code. Keep the job that receives a production identity small and avoid running application tests in that same job.

Parent-child pipelines split one project's pipeline into smaller configurations, commonly for monorepos. Child pipelines run in the same project, ref and commit as the parent, but their status may not affect the parent/ref unless the trigger strategy is configured to mirror or depend on child completion. Their source value is `parent_pipeline`, even when the parent was a merge-request pipeline; use the passed merge-request variables where needed. Multi-project pipelines trigger another project and use `pipeline` as their source. Decide explicitly whether downstream failure should fail the upstream release and which project controls the deployment configuration. See [downstream pipelines](https://docs.gitlab.com/ci/pipelines/downstream_pipelines/).

## A merge-request and release pipeline

DispatchDesk has API and worker components. Both are built and tested for merge requests, but only the default branch can create a release package and deploy it. Build artifacts move through named dependencies; the cache can speed dependency downloads but does not supply the release binary. Where the GitLab tier supports it, a protected production environment gates deployment; a dedicated protected GitLab runner, locked to the intended project and eligible refs, supplies the execution capacity. Both controls are configured outside this YAML.

```yaml
workflow:
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - when: never

stages: [build, test, package, deploy]

build-api:
  stage: build
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
  script: ./ci/build api
  artifacts:
    paths: [dist/api/]
    expire_in: 1 week

build-worker:
  stage: build
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
  script: ./ci/build worker
  artifacts:
    paths: [dist/worker/]
    expire_in: 1 week

test-api:
  stage: test
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
  needs:
    - job: build-api
      artifacts: true
  script: ./ci/test api dist/api/

test-worker:
  stage: test
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
  needs:
    - job: build-worker
      artifacts: true
  script: ./ci/test worker dist/worker/

package-release:
  stage: package
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
  needs:
    - job: build-api
      artifacts: true
    - job: build-worker
      artifacts: true
    - job: test-api
      artifacts: false
    - job: test-worker
      artifacts: false
  script: ./ci/package-release
  artifacts:
    paths: [dist/release/]
    expire_in: 1 week

deploy-production:
  stage: deploy
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push" && $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
  needs:
    - job: package-release
      artifacts: true
  environment:
    name: production
  script: ./ci/deploy-release dist/release/
```

This is a structural example, not a production-ready configuration. The runner must provide the tools used by the repository scripts. Review the actual expanded configuration, validate it with CI Lint for the deployed GitLab version, and test both merge-request and default-branch paths. Where your GitLab tier supports protected environments, configure `production` there and restrict deployment runner access in project settings; on other tiers, keep production authority behind restricted branch permissions and an external deployment control. Those controls are not established by the example alone. The package artifact's short expiration is only a sample: a production release should go to a durable registry or release store with digest and provenance checks. The scripts are repository-owned interfaces and were not executed.

A release pipeline should preserve identity across stages: record the project, commit SHA, pipeline and job IDs, artifact digest, and deployment environment. Before deploy, compare the consumed artifact's digest and producer metadata with the expected build. A branch named `main` is not by itself proof that an artifact is authentic, and a successful test of one output does not prove that a different output was deployed. If artifacts cross project or pipeline boundaries, verify the exact upstream run and allowlisted producer rather than downloading “latest” by branch name.

Review the resulting graph from both directions. From each trigger, list jobs that can be created and their credentials; from each privileged job, trace its `needs`, artifact producers, included configuration, runner eligibility and environment rules. Exercise negative cases: a fork merge request must not access deployment variables or trusted runners, an absent optional component must not create a broken dependency, a failed test must block packaging, and an expired or mismatched artifact must fail deployment. The [CI/CD pipeline guide](https://docs.gitlab.com/ci/pipelines/) and [YAML reference](https://docs.gitlab.com/ci/yaml/) define platform behavior; group and instance settings can further change what the project permits.

## Takeaways

Model GitLab pipeline creation and job inclusion separately. Use `needs` for explicit scheduling and artifact edges, then enforce environment, runner and identity controls in project and cloud settings.

## Exercises and answer guidance

1. A lint job in stage `test` waits for every build job even though it has no build input. How can feedback improve? Give it no artifact dependency and use `needs: []` where appropriate so it can start immediately.
2. A merge-request pipeline exists only because an included file contains a matching `rules` condition. Why may this fail to satisfy GitLab's MR-pipeline requirement? The root `.gitlab-ci.yml` needs a matching `workflow: rules` or job-level `rules` condition for `merge_request_event`.
3. A downstream test reads a cache as its build output. What risk does this create? Cache availability and content are performance concerns, not reliable data transfer; declare an artifact and an explicit need.
4. `package-release` needs a job that is omitted on merge requests. What should be checked? Ensure package itself is also excluded for MRs or mark the dependency optional only if the package job can correctly proceed without the job's output.
5. A parent triggers a child pipeline but reports success before child tests finish. What setting is missing? Configure the trigger strategy so the parent waits for and reflects the child result, when that is the intended release contract.
6. A release job downloads the latest artifact for `main`. What identity checks are needed? Bind it to the expected pipeline/run and commit, verify digest and provenance, and reject unexpected producers or revisions.

Review questions: how do `workflow: rules` and job `rules` differ, when does `needs` bypass a stage barrier, how are caches different from artifacts, and which GitLab settings must complement environment declarations in YAML?

## Verification and primary sources

Official GitLab documentation for pipelines, workflow rules, merge-request pipelines, includes, components, needs, artifacts, cache, and downstream pipelines was inspected on 2026-10-04. The YAML is illustrative and its repository scripts were not executed. Static parsing does not validate GitLab's version-specific schema, CI Lint result, rules expansion, runner configuration, tier-dependent features, protected-variable behavior, artifact authorization or deployment controls.

Primary references: [Pipelines](https://docs.gitlab.com/ci/pipelines/), [workflow](https://docs.gitlab.com/ci/yaml/workflow/), [merge request pipelines](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/), [includes](https://docs.gitlab.com/ci/yaml/includes/), [CI/CD components](https://docs.gitlab.com/ci/components/), [needs](https://docs.gitlab.com/ci/yaml/needs/), [job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/), [cache](https://docs.gitlab.com/ci/caching/), and [downstream pipelines](https://docs.gitlab.com/ci/pipelines/downstream_pipelines/).
