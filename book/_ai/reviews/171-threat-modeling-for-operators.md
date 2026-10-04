# Independent review — Chapter 171

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: a1724784ab1d288202e381acc661d9c520b883fa95e2499f00102827a32678ac

## Scope and findings

Read current complete body/summary, Chapter 171 skeleton brief and authoring-guide requirements, with Chapter 170 authority/recovery prerequisite context. Reviewed threat-model scope, STRIDE, assets/trust boundaries, diagram/table, privileged CI-to-runtime abuse path, controls/evidence and response/recovery, current primary references, assessment material and links. No material technical finding; chapter meets its brief and is approved.

The model is explicitly scoped, fictional, assumption-dependent and maintained; it does not promise exhaustive discovery or certification. STRIDE expansion is accurate and used as a coverage prompt, with business misuse and recovery errors retained. Risk labels require context and authorized residual-risk acceptance rather than fabricated quantitative certainty. Effective identities and enforcing resources are considered alongside desired workflow/network configuration.

The text diagram correctly joins acceptance state/outbox to publisher, queue, worker and provider, and separately represents source/build/registry/deploy/runtime authority. The repository-governance boundary is schematic rather than a precise deployed policy; surrounding instructions explicitly require actual identities, policies, audit sources and untrusted-code boundaries before treating it as a real model. The threat table supplies concrete impact assumptions, controls and denial/observation evidence, and is clearly not a claim those controls are deployed.

Compromised privileged workflows can alter artifact content or exercise deploy credentials, then obtain the permissions of the runtime identity through malicious deployed code. Digest identity does not establish trusted source or builder; signature authority is challenged in the exercise. Branch trust, environment gates, short-lived identity and runtime permissions are distinct boundaries. OIDC claims/trust are delegated to Chapter 176 and provider-specific review, rather than assuming a token itself establishes appropriate trust.

Provider ambiguity/duplicate effects match earlier durable-intent/idempotency chapters. Backup encryption is distinguished from deletion authority and usable recovery; key custody/reconciliation remains required. Incident diagnosis preserves release/registry/cloud evidence, containment restricts further promotion and exposed authority, and recovery rebuilds through a trusted path and reconciles customer state. A known-good digest does not alone prove unaffected data. Owners, review triggers, exception expiry and restricted model details complete the operational method. Exercises have answer guidance, review questions and bespoke takeaways. No OS-specific install/config command is present, so no distribution-dependent flag or package claim requires a runtime matrix.

Low optional observation — compact summary, Examples and cross-references: it says the body links Chapters 83, 170 and 176, but Chapter 83 is not linked in the current body. Remove 83 from that summary list or add an appropriate IAM-context relative link. Actual prerequisite Chapter 170 and forward Chapter 176 links exist.

## Primary evidence checked 2026-10-04

- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html): decomposition/flows/boundaries, threat identification, mitigation and review; iterative team method and optional technique selection.
- [AWS IAM security best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html): federation/temporary role credentials, human MFA and effective least-privilege review.
- [GitHub Actions secure-use reference](https://docs.github.com/en/actions/reference/security/secure-use): workflow/action hardening, permission minimization and untrusted-input/runner risks.
- [GitHub Actions OIDC reference](https://docs.github.com/en/actions/reference/security/oidc): contextual claims and audience/subject conditions for provider trust. No plan/tier-dependent enforcement capability or exact provider configuration is asserted here.

## Validation and limits

`python3 tools/check_book.py --chapters 171-171` passed 1,466 global local links without warnings/errors. The chapter has a text diagram and table, not executable command/configuration examples; none were executed. Exact stripped-front-matter hash computed using `tools.promote_reviewed.body_hash`. No cloud identity/policy, GitHub repository protection, runner, production deployment, security test, containment, backup restore or incident reconciliation inspected/executed against a live system. Primary docs and fictional analysis cannot establish effective deployed permissions, model completeness or incident scope. Only this separate review record written.

Verdict: approved
