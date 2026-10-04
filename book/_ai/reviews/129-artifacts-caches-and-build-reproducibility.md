# Independent review — Chapter 129

Reviewer: independent reviewer agent
Date: 2026-10-04
Reviewed body SHA256: 9c82134dfd44a13f6934580e4e337b75246254947d6b0acfe75d644caff18275

## Inspection scope

Read the current complete body, compact summary, SKELETON brief, authoring guide and predecessor context (Chapter 127 summary and Chapters 128–129 bodies). Inspected conceptual examples, trust boundaries, operational diagnosis/recovery, assessment guidance and primary-source claims. Summaries accurately describe the bodies and disclose non-execution. There are no executable command/configuration examples or distro package instructions in this scope; Ubuntu/Fedora/RHEL differences are therefore not introduced.

## Findings

No material technical findings. Cache trust, retention versus identity, deterministic/hermetic distinction, attestation subject/signer/builder trust and same-digest promotion are sound. Diagram is explicitly conceptual.

Takeaways addition is accurate and resolves the earlier editorial suggestion.

## Primary evidence checked on 2026-10-04

- [https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching)
- [https://docs.gitlab.com/ci/jobs/job_artifacts/](https://docs.gitlab.com/ci/jobs/job_artifacts/)
- [https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/)
- [https://slsa.dev/spec/v1.2/build-provenance](https://slsa.dev/spec/v1.2/build-provenance)
- [https://slsa.dev/spec/v1.2/verifying-artifacts](https://slsa.dev/spec/v1.2/verifying-artifacts)

GitLab report ingestion does not affect job status; Jenkins JUnit defaults to unstable on test failures. GitHub distinguishes skipped jobs (successful checks) from workflow filtering. Storage/provenance references support producer-consumer identity and verification boundaries. GitHub current concurrency documentation confirms one pending run by default and optional queuing; GitLab configuration documents long-polling bottlenecks and concurrent/limit/request_concurrency settings. Jenkins tour URL was inaccessible through the browser during this review; accessible official JUnit/basic-steps references supplied the relevant evidence.

## Validation and limits

`python3 tools/check_book.py --chapters 128-130` passed: three chapters and 1,398 global local links, no errors/warnings. No pipeline, scanner, registry, attestation, runner, deployment or security incident was executed/observed. No plan/version/platform or OS matrix was tested. Primary-source inspection and static links do not establish real gate enforcement, builder trust or isolation. Only separate review records changed.


## Fresh additions review — 2026-10-04

Scope: reviewed the newly added takeaways and Chapter128 gate/exercise corrections and Chapter130 predecessor mention against prior recorded review scope; no new full runtime review. Current body hash recomputed with tools.promote_reviewed.body_hash: 9c82134dfd44a13f6934580e4e337b75246254947d6b0acfe75d644caff18275. All takeaway statements accurately summarize the chapter boundaries without introducing unsupported guarantees. Chapter130 predecessor explanation is accurate; a relative clickable link remains an optional editorial improvement. Existing documentation evidence and execution limits above remain applicable. `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses and 1,399 global local links; no errors/warnings. Only these separate review records changed.

## Final correction review — 2026-10-04

Final bounded refresh: all final hashes recomputed; takeaways remain accurate, Chapter128 remaining status sentence and Chapter130 clickable prerequisite link are resolved. Scoped checker `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses, three shell syntax checks and 1,400 global local links; no errors/warnings. Prior runtime/source limitations remain; this is a review of additions/fixes, not a new live-platform test. Only ten separate review records updated.

Verdict: approved
