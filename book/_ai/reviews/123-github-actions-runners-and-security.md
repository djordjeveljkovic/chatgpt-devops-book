# Independent review — Chapter 123

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 6fb06060f3d0dff59e2ae576f921db25dff173f516afb2742e1a30a22ce458f5

## Scope and findings

Read current body, compact summary, skeleton brief and authoring guide, with Chapter122 prerequisite summary. The current hash matches the coordinator-supplied hash. Reviewed hosted/self-hosted execution, runner routing versus access/isolation, persistent state, ephemeral disposal, token/OIDC permissions and claims, environments, action pins, privileged events and exact workflow excerpt structure.

No material finding. YAML jobs are correctly separate, deploy needs build, deployment runner labels select all required labels, and job-level contents/read plus id-token/write are scoped to deployment. Checkout in deploy supplies repository scripts absent from its separate workspace; same-run named artifact transfer is explicit. The excerpt correctly declares unresolved full-SHA placeholders and unimplemented repository scripts, so approval does not mean it can execute. Environment and cloud trust are external controls, and artifact transfer is explicitly insufficient provenance. Serialization, safe cancellation, verified source/digest and ephemeral deployment-host cleanup remain production requirements in adjoining prose.

Security boundaries are accurate: runner labels do not establish isolation; environment approvals do not clean a compromised host; OIDC permission requests a token rather than authorizing a cloud role; SHA pinning fixes source revision rather than establishing trust; pull_request_target and privileged workflow_run follow-ups must not execute untrusted content. Newer immutable OIDC subject claims are a current documented feature, not an invented format. Existing/opt-in subject differences are correctly qualified and verification is required. Exercises provide direct guidance and summary accurately states the example's nondeployable nature.

## Dated primary-source evidence

Inspected on2026-10-04:

- [OIDC reference](https://docs.github.com/en/actions/reference/security/oidc): id-token permission, issuer/audience/subject, environment subject and immutable owner/repository-ID format. GitHub documents default immutable subjects for repositories created after July15,2026 and opt-in/rename/transfer changes; these do not apply to GHES.
- [Self-hosted runner reference](https://docs.github.com/en/actions/reference/runners/self-hosted-runners): operator-managed host maintenance and trust boundary.
- [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use): fork/public-runner risk, third-party actions, pinned revisions and privileged event concerns.
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax): needs, runs-on array, job environment and job permissions structure.

Primary-source review supports documented interfaces/security guidance; it is not an exhaustive external-link crawl or real repository authorization audit.

## Validation and limits

`python3 tools/check_book.py --chapters 123-123` passed:1 YAML parse and1,392 global local links; no errors/warnings. Static YAML parsing does not validate GitHub's workflow schema or availability of placeholder action revisions. No GitHub run, artifact transfer, repository/organization/runner-group/environment inspection, OIDC request, cloud-role exchange, script execution, runner disposal or deployment performed. No hosted-image or Ubuntu/Fedora/RHEL runner matrix executed. External trust policies, workflow source provenance, permissions, script behavior and environment gates require authorized rehearsal before production use. Only this separate hash-bound review record changed.


## Fresh additions review — 2026-10-04

Scope: reviewed the newly added takeaways and Chapter128 gate/exercise corrections and Chapter130 predecessor mention against prior recorded review scope; no new full runtime review. Current body hash recomputed with tools.promote_reviewed.body_hash: 6fb06060f3d0dff59e2ae576f921db25dff173f516afb2742e1a30a22ce458f5. All takeaway statements accurately summarize the chapter boundaries without introducing unsupported guarantees. Chapter130 predecessor explanation is accurate; a relative clickable link remains an optional editorial improvement. Existing documentation evidence and execution limits above remain applicable. `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses and 1,399 global local links; no errors/warnings. Only these separate review records changed.

## Final correction review — 2026-10-04

Final bounded refresh: all final hashes recomputed; takeaways remain accurate, Chapter128 remaining status sentence and Chapter130 clickable prerequisite link are resolved. Scoped checker `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses, three shell syntax checks and 1,400 global local links; no errors/warnings. Prior runtime/source limitations remain; this is a review of additions/fixes, not a new live-platform test. Only ten separate review records updated.

Verdict: approved
