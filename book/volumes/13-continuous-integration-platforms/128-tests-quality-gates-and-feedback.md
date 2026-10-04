---
book: The Complete DevOps Engineering Book
volume: 13
volume_title: "Continuous Integration Platforms"
chapter: 128
title: "Tests, Quality Gates and Feedback"
slug: tests-quality-gates-and-feedback
status: complete
summary: ../../_ai/chapter-summaries/128-tests-quality-gates-and-feedback.md
---

# Chapter 128 — Tests, Quality Gates and Feedback

## Unit, integration and contract boundaries

A test level is defined by what it exercises and what it replaces, not by its name. Unit tests check a small unit of behavior with dependencies controlled or substituted. Integration tests exercise a boundary between components, such as an API and database, a worker and queue, or a service and identity provider. Contract tests verify an agreed interface between independently deployed components, often without running the full production topology. End-to-end tests exercise a user-visible path through several real or simulated components. Each level finds different defects and has different cost, setup needs and failure modes.

DispatchDesk has an API, queue worker and web client. Fast unit tests validate parsing, authorization decisions, retry rules and business invariants. API/database integration tests use a disposable database with the production migration path. A contract test checks that the API event schema and worker consumer agree on required fields and version behavior. A small number of end-to-end tests cover high-value paths such as submitting a job, processing it and reading its final status. None of these substitutes for operational tests of backups, deployment rollback, capacity or network failure.

Keep test boundaries explicit. If a test replaces a queue with an in-memory fake, it cannot establish that the deployed queue accepts the same message or retry behavior. If a contract fixture is copied manually into two repositories, it can drift from the real producer. Prefer a versioned schema or generated contract artifact, and test both producer and consumer compatibility during transition. Use disposable services and isolated data for integration tests. Never point a test job at production merely to make the environment “realistic.” Reset test state and avoid order-dependent tests that pass only after another test initializes hidden state.

A useful pipeline gives the fastest deterministic checks the shortest path to feedback, then runs more expensive checks when needed. Lint and unit tests can begin on every change. Integration tests run where database, queue and service containers are available. A compatibility matrix should include supported runtime or dependency versions, not every theoretical combination. End-to-end tests should cover high-risk user workflows instead of duplicating every unit test at much greater cost. Schedule deeper or slower checks when their findings still reach an owner before release; infrequent tests that nobody sees are not a useful gate.

Flaky tests reduce trust in the whole pipeline. A test that fails for timing, shared state or external dependency reasons must be investigated rather than rerun until green and forgotten. Record failures by test and environment, preserve diagnostics, and assign an owner. If a test must be quarantined to restore feedback, keep it visible and prevent it from becoming a permanent silent exception. A retry can distinguish a transient failure from a repeatable one, but it must not convert the original failure into evidence of correctness without recording it.

## Security scans and useful gates

A quality gate is a decision rule attached to a pipeline result: for example, unit tests must pass, a supported dependency policy must be met, or a release artifact must have a verified digest. Decide what happens when the gate fails, who owns the exception, and what evidence can permit a temporary waiver. A scan that produces a report but cannot block or inform a release is visibility, not enforcement. Conversely, a gate that fails on noisy or unactionable findings trains people to bypass it. Keep the rule measurable, tied to a risk, and assigned to an owner.

Use multiple security checks for different failure classes. Secret scanning can catch credentials committed to source; dependency analysis can identify known vulnerable packages; static analysis can find some risky code patterns; container scanning can report vulnerable base layers; infrastructure checks can catch unsafe configuration. These tools have blind spots, false positives, version and language coverage limits, and policy choices. A clean scan is evidence that a configured tool found no matching issue in the checked inputs. It is not proof that the application is secure or that runtime behavior is safe. Validate scanner version, paths, generated code handling, exclusions, severity policy and the identity of the scanned revision.

A gate should distinguish new findings from accepted baseline risk where the platform supports it. For a pull or merge request, teams often focus on newly introduced critical issues, while a separately owned backlog addresses older findings. Do not silently ignore a severity threshold or allow a contributor-controlled config change to disable the only scanner that evaluates that contributor's change. Protect central policies or run required scans from a trusted configuration source. Use a human exception with an expiry and audit trail when a release must proceed despite a known issue.

Reports and job outcomes are separate channels. GitLab's JUnit report artifact displays test results but does not determine job success: the test command must exit nonzero when a test fails. Jenkins can archive JUnit results and mark a build unstable, but pipeline behavior and deployment conditions determine whether later stages continue. GitHub treats a skipped job as successful, and that check can satisfy a required status check. A whole workflow omitted by a branch or path filter may instead leave its required check pending and block merging. Configure gates in the hosting platform as well as writing commands in CI; use an always-running aggregator to confirm that each required check actually ran and passed, and that a skipped test was legitimately inapplicable. Do not rely on a job-level skip to fail closed. See the primary docs for [GitLab unit test reports](https://docs.gitlab.com/ci/testing/unit_test_reports/), [Jenkins test reporting](https://www.jenkins.io/doc/book/pipeline/tour/tests-and-artifacts/) and [GitHub status checks](https://docs.github.com/en/pull-requests/reference/status-checks).

## Balancing confidence with pipeline duration

Measure time from a contributor's push to a useful result, not only total runner minutes. A 20-minute pipeline with early unit feedback may be more usable than a 10-minute pipeline that reports one opaque failure at the end. Show test names, actionable failure messages, the tested commit and links to logs or reports. Preserve reports when the test command fails so diagnosis does not require reproducing the exact runner state. Keep output small enough to find the failure, and avoid putting tokens, personal data or production records in logs or artifacts.

Make parallelism follow independent work. Separate jobs can run concurrently when they do not compete for one external test database, mutable cache or rate-limited account. Use isolated test tenants and unique resource names; clean them up even after cancellation. If a test depends on a shared service, serialize only the conflicting section or provide a disposable service instance. Do not optimize duration by weakening the correctness boundary, such as testing one artifact and rebuilding a different one for release.

Use required checks sparingly and deliberately. Required status names should be stable, uniquely identify the expected producer and represent a meaningful gate. A renamed required check or a workflow removed entirely by a branch or path filter can leave a pull request waiting indefinitely; a job skipped within a workflow is instead reported as successful. Keep a minimal always-present gate for required decisions, and let optional platform or path-specific checks report separately. For monorepos, define path filters carefully: a change to shared libraries, build scripts, schemas or pipeline configuration may affect several components even if a service directory did not change.

For DispatchDesk, a practical sequence is: validate formatting and static types; run API, worker and web unit suites; build each component once; run API/database and event-contract integration tests against isolated services; scan source and dependencies; then test a small set of user workflows against the exact candidate artifact. The release pipeline consumes the tested artifact by digest, evaluates required gates, records exceptions and deploys only through a protected path. Track queue wait, job duration, retry rate, flake rate, missing reports, cancellation and gate override frequency. A rising override rate may indicate an unclear policy or unreliable test rather than a need for more bypasses.

A team should periodically remove obsolete gates, add tests for incidents and review exclusions. Test design follows service boundaries, not organizational ownership alone: a cross-team contract needs an owner on both sides, and a global security gate needs an operator who can repair the scanner. [Chapter 127](127-jenkins-declarative-pipelines.md) covers pipeline execution behavior; [Chapter 129](129-artifacts-caches-and-build-reproducibility.md) covers the identity and repeatability of tested outputs.

## Takeaways

Use tests at boundaries that match real failure modes, and make reports and job status agree. Gates should be actionable, always visible when required, and tied to the same artifact that will be released.

## Exercises and answer guidance

1. A test replaces the queue with an in-memory fake and passes. What risk remains? Queue connectivity, permissions, serialization, delivery and retry behavior were not exercised; add a focused integration test against a disposable real queue implementation or service.
2. GitLab displays a red JUnit test in the merge request, but the job is green. What should be checked? The test command's exit status; JUnit report ingestion is for display and does not fail the job by itself.
3. Jenkins records a failed test report as unstable and then still runs deployment. Why? The pipeline's result policy permits later stages after unstable; make deployment conditional on a successful result or use a suitable Declarative option.
4. A security scanner reports thousands of old findings and developers disable it. How should the gate be redesigned? Separate the existing backlog from new findings, protect the scan policy, prioritize actionable risk, assign remediation owners, and make time-bounded exceptions auditable.
5. A required workflow is omitted entirely by a path filter after a change to a shared build script, leaving its status pending. What failed? The workflow-level filter prevented the expected check from reporting, so the required gate blocks merging. Keep an always-running gate that evaluates shared build changes and confirms applicable test jobs ran and passed; use a job skip only when it can be proven irrelevant and do not treat that skipped job as failure.
6. A release rebuilds an image after tests instead of publishing the tested image. What confidence is lost? The deployed output may differ from what passed; preserve and promote the same digest-identified artifact.

Review questions: what can each test boundary establish, how do test reports differ from job status, what makes a gate actionable, and how can pipeline time be improved without changing the artifact or hiding risk?

## Verification and primary sources

Official GitLab, Jenkins and GitHub documentation for unit-test reports, Jenkins test outcomes and GitHub status checks was inspected on 2026-10-04. The chapter's commands and service descriptions are examples only; no tests, scanners, service containers, repository checks or release gates were executed. Report presentation, merge policy and Jenkins plugin behavior depend on platform settings and installed versions.

Primary references: [GitLab unit test reports](https://docs.gitlab.com/ci/testing/unit_test_reports/), [GitLab code quality](https://docs.gitlab.com/ci/testing/code_quality/), [Jenkins test reports and artifacts](https://www.jenkins.io/doc/book/pipeline/tour/tests-and-artifacts/), [Jenkins JUnit step](https://www.jenkins.io/doc/pipeline/steps/junit/), [GitHub status checks](https://docs.github.com/en/pull-requests/reference/status-checks), and [GitHub required status checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks).
