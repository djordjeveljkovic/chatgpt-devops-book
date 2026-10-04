# Independent review — Chapter 180

Reviewer: write_volume7_061_070
Date: 2026-10-04
Reviewed body SHA256: 6d889fd3d255673afd226b517d2808362701f21326fafadf0e049b8962c37427

## Scope and findings

Read manuscript, summary, brief, authoring guide, assigned manifest records and relevant Chapters 175–179 summaries/context. Reviewed evidence preservation versus active harm, coordinated command/scope, credential/session lifecycle, compromised release runner/workflow, exact artifact digest, trust-path failure, clean rebuild, data-integrity recovery, canary and recurrence monitoring, communication scope, exercise guidance and links. No material finding in this chapter; approved.

The operational response framework is appropriately provider-independent and makes no claim to execute a concrete provider revocation command without specifying its behavior. It correctly distinguishes rotation from active-session termination and requires checking remaining access keys, federation/grants and other footholds. The scenario preserves registry/repository evidence and rebuilds on a trusted runner rather than treating a signature from a compromised workflow as sufficient. Absence of a database audit match is expressly limited rather than treated as proof that no data was accessed. Containment is not delayed for perfect forensic capture. Notification obligations are routed to responsible organizational specialists instead of inventing a universal deadline.

The brief's evidence/isolation, credential revocation/clean rebuild and compromised-runner response are covered. A prose-based decision procedure suits this host/provider-neutral incident framework; hypothetical destructive CLI recipes would reduce safety and precision. Exercises with answer guidance, questions and takeaways are present and consistent. Low optional improvements: add canonical relative links where Chapters 174–179 are mentioned in prose, and expand the summary Verification with source dates and the actual review checks. These summary bookkeeping updates do not alter the approved body.

## Primary evidence checked 2026-10-04

- [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final): April 2025 publication, supersedes Rev. 2, incident response integrated with CSF 2.0 risk management.
- [NIST incident-response project](https://csrc.nist.gov/projects/incident-response): current guidance context.
- [Cosign verification](https://docs.sigstore.dev/cosign/verifying/verify/): identity/digest verification cannot establish uncompromised build-path integrity by itself.
- CISA StopRansomware Guide at the chapter URL was unavailable through the web tool during this review. No claim that its full current text was independently inspected; containment/evidence reasoning was reviewed against the NIST framing and chapter's explicit operational limits.

## Validation and limits

`python3 tools/check_book.py --chapters 178-180` passed 3 draft records, 2 shell syntax checks and 1,482 local links without errors or warnings. Body hashes computed with `tools.promote_reviewed.body_hash`; summaries reviewed separately. Shell parsing does not validate Cosign predicates, policy schemas or runtime semantics. No Cosign install/sign/verify, registry write, OPA/controller execution, admission denial, audit assessment, credential change, forensic acquisition, incident handling or provider operation was performed. Only separate review records written; manuscripts and summaries unchanged.

Verdict: approved
