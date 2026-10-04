# Independent review — Chapter 128

Reviewer: independent reviewer agent
Date: 2026-10-04
Reviewed body SHA256: c7bb536bae73fd3d2bb4d528b7432465bce06cf23ed41f9b974c266c5bc4c97e

## Inspection scope

Read the current complete body, compact summary, SKELETON brief, authoring guide and predecessor context (Chapter 127 summary and Chapters 128–129 bodies). Inspected conceptual examples, trust boundaries, operational diagnosis/recovery, assessment guidance and primary-source claims. Summaries accurately describe the bodies and disclose non-execution. There are no executable command/configuration examples or distro package instructions in this scope; Ubuntu/Fedora/RHEL differences are therefore not introduced.

## Findings

No remaining material findings. The report/status paragraph, duration paragraph and exercise 5 now consistently distinguish skipped jobs (successful required checks) from filtered-out entire workflows (pending checks). The earlier material finding is resolved.

Takeaways addition is accurate and resolves the earlier editorial suggestion.

## Primary evidence checked on 2026-10-04

- [https://docs.gitlab.com/ci/testing/unit_test_reports/](https://docs.gitlab.com/ci/testing/unit_test_reports/)
- [https://www.jenkins.io/doc/pipeline/steps/junit/](https://www.jenkins.io/doc/pipeline/steps/junit/)
- [https://docs.github.com/en/pull-requests/reference/status-checks](https://docs.github.com/en/pull-requests/reference/status-checks)

GitLab report ingestion does not affect job status; Jenkins JUnit defaults to unstable on test failures. GitHub distinguishes skipped jobs (successful checks) from workflow filtering. Storage/provenance references support producer-consumer identity and verification boundaries. GitHub current concurrency documentation confirms one pending run by default and optional queuing; GitLab configuration documents long-polling bottlenecks and concurrent/limit/request_concurrency settings. Jenkins tour URL was inaccessible through the browser during this review; accessible official JUnit/basic-steps references supplied the relevant evidence.

## Validation and limits

`python3 tools/check_book.py --chapters 128-130` passed: three chapters and 1,398 global local links, no errors/warnings. No pipeline, scanner, registry, attestation, runner, deployment or security incident was executed/observed. No plan/version/platform or OS matrix was tested. Primary-source inspection and static links do not establish real gate enforcement, builder trust or isolation. Only separate review records changed.


## Fresh additions review — 2026-10-04

Scope: reviewed the newly added takeaways and Chapter128 gate/exercise corrections and Chapter130 predecessor mention against prior recorded review scope; no new full runtime review. Current body hash recomputed with tools.promote_reviewed.body_hash: 16e8d8083c4c2b7867a5ada99ba8af12496926449f30343a5dc436caaa6c77fe. All takeaway statements accurately summarize the chapter boundaries without introducing unsupported guarantees. Chapter130 predecessor explanation is accurate; a relative clickable link remains an optional editorial improvement. Existing documentation evidence and execution limits above remain applicable. `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses and 1,399 global local links; no errors/warnings. Only these separate review records changed.

## Final correction review — 2026-10-04

Final bounded refresh: all final hashes recomputed; takeaways remain accurate, Chapter128 remaining status sentence and Chapter130 clickable prerequisite link are resolved. Scoped checker `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses, three shell syntax checks and 1,400 global local links; no errors/warnings. Prior runtime/source limitations remain; this is a review of additions/fixes, not a new live-platform test. Only ten separate review records updated.

Verdict: approved
