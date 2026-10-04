# Independent review — Chapter 121

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 5b6b00e92559c2b6e7f4be021473e3f821c75a8eee30e2d22151531161d93a88

## Findings

No material findings. Fresh review confirms the GitLab paragraph explicitly excludes fork merge requests from protected variables/runners while distinguishing parent non-protected resources and same-project permission/settings conditions.

## Scope and dated primary evidence

Read complete body, summary, SKELETON brief, authoring guide and relevant previously reviewed Chapter 120/118 prerequisites. Event/worker/job graphs, untrusted code/credentials and artifact-producing pipeline cover the brief. DispatchDesk clearly illustrates separate fork validation, protected artifact production and approved digest promotion. Failure ownership, negative authorization tests, exercises with answer guidance and operational review questions are present. No command, workflow YAML, credential operation or live system configuration is supplied; there is no unsafe command to execute or cleanup to perform. Ubuntu/Fedora/RHEL runner-host installation differences belong to later implementation chapters; no interchangeable host instructions appear here. Summary is technically accurate, though its broad upcoming-chapter link mention is a continuation description rather than actual direct links.

Primary official documentation inspected 2026-10-04:

- [GitHub events](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows) and [pull_request_target security](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) support fork secret/token restrictions, trusted base workflow context and danger of executing fork code with elevated access. Permissions/settings qualifications prevent a universal write-token guarantee.
- [GitHub secure use](https://docs.github.com/en/actions/reference/security/secure-use) supports masking limitations, untrusted input/artifact/cache attacks, self-hosted persistent-compromise and network/credential exposure risks. Ephemeral hardware reuse still requires environment cleanup, consistent with the chapter's requirement to prove isolation.
- [GitHub OIDC](https://docs.github.com/en/actions/concepts/security/openid-connect) supports short-lived federation and provider claim/trust restrictions rather than automatically safe cloud authorization.
- [GitLab merge-request pipelines](https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/) explicitly supports fork-context defaults, parent-member triggered pipelines using fork configuration and parent resources, and protected-resource conditions. [GitLab caching](https://docs.gitlab.com/ci/caching/) supports cache/artifact distinctions and protected/non-protected cache separation; the chapter asks for trust-separated keys plus validation, without claiming a user-controlled key alone enforces security.
- [Jenkins controller isolation](https://www.jenkins.io/doc/book/security/controller-isolation/) supports avoiding built-in-node builds; [multibranch credential security](https://www.jenkins.io/doc/book/security/securing-org-folders-and-multibranch-pipelines/) supports child credential availability, Jenkinsfile authority and credential theft by contributor-controlled tests even with trusted Jenkinsfile.

Artifact source/run binding, immutable digest promotion, provenance limitations, downstream verification and exposure response are technically sound. A signature is explicitly insufficient proof of safe source/build, and approval/branch labels are not treated as independent controls when the same contributor can alter policy. No platform default, hosted-runner cleanliness or protected environment is falsely represented as exhaustive isolation evidence.

## Validation and limits

`python tools/check_book.py --chapters 121-122` passed on 2026-10-04: two draft chapters, one YAML parsing block and 1,391 global local-link checks; no errors/warnings. No executable shell/YAML block was available to check. Exact body hash computed using tools.promote_reviewed.body_hash. No CI run, runner/agent inspection, fork attack test, cache/artifact upload or retrieval, credential/token query, OIDC exchange, registry publication or deployment occurred. No actual repository visibility/edition/settings, provider trust policy, Jenkins plugin/version, runner OS matrix, cleanup isolation, masking, provenance or denied-access behavior was validated. Selective primary-source review establishes architecture and documented behavior rather than live security or exhaustive external-link validity. Only this separate review record was written.


## Fresh additions review — 2026-10-04

Scope: reviewed the newly added takeaways and Chapter128 gate/exercise corrections and Chapter130 predecessor mention against prior recorded review scope; no new full runtime review. Current body hash recomputed with tools.promote_reviewed.body_hash: 5b6b00e92559c2b6e7f4be021473e3f821c75a8eee30e2d22151531161d93a88. All takeaway statements accurately summarize the chapter boundaries without introducing unsupported guarantees. Chapter130 predecessor explanation is accurate; a relative clickable link remains an optional editorial improvement. Existing documentation evidence and execution limits above remain applicable. `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses and 1,399 global local links; no errors/warnings. Only these separate review records changed.

## Final correction review — 2026-10-04

Final bounded refresh: all final hashes recomputed; takeaways remain accurate, Chapter128 remaining status sentence and Chapter130 clickable prerequisite link are resolved. Scoped checker `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses, three shell syntax checks and 1,400 global local links; no errors/warnings. Prior runtime/source limitations remain; this is a review of additions/fixes, not a new live-platform test. Only ten separate review records updated.

Verdict: approved
