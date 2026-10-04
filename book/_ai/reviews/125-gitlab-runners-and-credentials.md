# Independent review — Chapter 125

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: e0ba7f59df9d3d7ef85076bd33df25e46614b4907b5638b141eb7921e4b6bbca

## Scope and findings

Read current body and compact summary against authoring-guide requirements with current Chapter124 prerequisite context. Reviewed shell/Docker/Kubernetes isolation, protected-ref/MR rules, variable exposure, CI_JOB_TOKEN scope/allowlist, OIDC job token and provider claim support, lifecycle and exercises. Current hash matches supplied603bf75c472c0a20a88da786f292edcc715501c41ebae20f1b35a66672c75e83.

No material finding. Shell shared-account and privileged-container/socket risks are accurately distinguished from configured container/pod isolation; labels do not authorize, and separate ephemeral pools/network/credential cleanup are explicit. GitLab18.1 protected MR resources are conditional on both protected branches, same project and triggering-user authorization, with setting/version verification and fork exclusion. Job token is limited to supported features and triggering-user permissions, expires with job completion, and target allowlists do not by themselves grant all triggering-user access. Broad group entries can expand eligible projects. Job-local ID token has deliberately placeholder audience/script; trust requires actual supported claims, and GitLab.com AWS namespace/project condition availability is qualified against Self-Managed/Dedicated. Summary accurately records schematic/nonexecution scope. Exercises provide direct answer guidance.

Fresh correction review: both optional findings resolved. Protected environments/approvals explicitly require Premium/Ultimate and point to Chapter124’s Free-tier alternative. Runner creation now uses authentication tokens and distinguishes deprecated legacy registration tokens, with migration reference and token custody/rotation guidance. No remaining finding.

## Dated primary-source evidence

Inspected on2026-10-04:

- [Runner security](https://docs.gitlab.com/runner/security/): shell-account exposure, privileged/host-PID escape risk, ephemeral dedicated protected machines and shared-host Docker credentials.
- [MR pipeline controls](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/): protected variables/runners and branch/user/project prerequisites.
- [Job token](https://docs.gitlab.com/ci/jobs/ci_job_token/): limited permissions, user context, revocation and cross-project allowlist.
- [OIDC ID tokens](https://docs.gitlab.com/ci/secrets/id_token_authentication/): job-scoped audience/claims and non-equivalence to cloud authorization.
- [AWS federation](https://docs.gitlab.com/ci/cloud_services/aws/): offering-specific namespace_id/project_id conditions.

- [Runner registration migration](https://docs.gitlab.com/ci/runners/new_creation_workflow/): current authentication-token workflow and legacy registration behavior checked on 2026-10-04.

## Validation and limits

`python3 tools/check_book.py --chapters 125-125` passed:1 YAML parse and1,399 global local links; no errors/warnings. No GitLab CI Lint/pipeline execution, runner/host configuration, protected-resource access, job-token use, OIDC request/role exchange or deployment performed. No GitLab version/edition or OS executor matrix tested. Syntax/source review cannot establish actual isolation, allowlists, token claim output or cloud trust. Only this separate review record changed.


## Fresh additions review — 2026-10-04

Scope: reviewed the newly added takeaways and Chapter128 gate/exercise corrections and Chapter130 predecessor mention against prior recorded review scope; no new full runtime review. Current body hash recomputed with tools.promote_reviewed.body_hash: e0ba7f59df9d3d7ef85076bd33df25e46614b4907b5638b141eb7921e4b6bbca. All takeaway statements accurately summarize the chapter boundaries without introducing unsupported guarantees. Chapter130 predecessor explanation is accurate; a relative clickable link remains an optional editorial improvement. Existing documentation evidence and execution limits above remain applicable. `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses and 1,399 global local links; no errors/warnings. Only these separate review records changed.

## Final correction review — 2026-10-04

Final bounded refresh: all final hashes recomputed; takeaways remain accurate, Chapter128 remaining status sentence and Chapter130 clickable prerequisite link are resolved. Scoped checker `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses, three shell syntax checks and 1,400 global local links; no errors/warnings. Prior runtime/source limitations remain; this is a review of additions/fixes, not a new live-platform test. Only ten separate review records updated.

Verdict: approved
