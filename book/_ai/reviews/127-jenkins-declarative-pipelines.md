# Independent re-review — Chapter 127

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 5c705526aa98bf43a2f25622ed0bc6248b7852e3c85ea55edeccda6537212faf

## Scope and findings

Freshly reviewed current Publish directive and surrounding workflow/prose against the prior scheduling finding. Current hash matches suppliedc81aeeb9dc138dd96de20378cb1a2c70580eaf410103a446304a7f4d2a5b6d2e.

The finding is resolved: when now contains beforeAgent true and branch main, so Declarative evaluates the branch condition before entering the stage agent. The explanation correctly keeps this scheduling optimization separate from external authorization. Candidate checkout/unstash/verification remains on the trusted publish agent before scoped credential binding. Other prior structure and security assessments remain applicable; no remaining material finding. Repository scripts and agent policy remain explicitly illustrative/external assumptions.

## Dated primary-source evidence

Inspected on2026-10-04:

- [Declarative syntax](https://www.jenkins.io/doc/book/pipeline/syntax/): agent, options, when, post and beforeAgent timing.
- [Shared libraries](https://www.jenkins.io/doc/book/pipeline/shared-libraries/): globally trusted unrestricted code, version override and folder sandboxing.
- [Credentials Binding](https://www.jenkins.io/doc/pipeline/steps/credentials-binding/): scoped environment binding, interpolation and masking limitations.
- [Basic steps](https://www.jenkins.io/doc/pipeline/steps/workflow-basic-steps/): stash/unstash lifetime and artifact-transfer limits.

## Validation and limits

`python3 tools/check_book.py --chapters 127-127` passed:1 draft chapter and1,398 global local links; no errors/warnings. Checker does not validate Groovy/Declarative syntax; directive ordering was compared with official Pipeline Syntax's beforeAgent semantics already inspected2026-10-04. No Jenkins controller/linter, agent allocation, script, stash, credential or publication executed. No runtime/plugin matrix tested. Only this review record changed.


## Fresh additions review — 2026-10-04

Scope: reviewed the newly added takeaways and Chapter128 gate/exercise corrections and Chapter130 predecessor mention against prior recorded review scope; no new full runtime review. Current body hash recomputed with tools.promote_reviewed.body_hash: 5c705526aa98bf43a2f25622ed0bc6248b7852e3c85ea55edeccda6537212faf. All takeaway statements accurately summarize the chapter boundaries without introducing unsupported guarantees. Chapter130 predecessor explanation is accurate; a relative clickable link remains an optional editorial improvement. Existing documentation evidence and execution limits above remain applicable. `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses and 1,399 global local links; no errors/warnings. Only these separate review records changed.

## Final correction review — 2026-10-04

Final bounded refresh: all final hashes recomputed; takeaways remain accurate, Chapter128 remaining status sentence and Chapter130 clickable prerequisite link are resolved. Scoped checker `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses, three shell syntax checks and 1,400 global local links; no errors/warnings. Prior runtime/source limitations remain; this is a review of additions/fixes, not a new live-platform test. Only ten separate review records updated.

Verdict: approved
