# Chapter 171 continuation

Status: complete

## Written material
Operational threat-model scope and trust boundaries; abuse-path analysis and evidence-bound controls; fictional DispatchDesk release/runtime threat register; incident diagnosis/recovery; model maintenance and ownership.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Assets; trust boundaries; actor capability and prerequisites; abuse path; preventive/detective/recovery controls; residual risk owner; model revision trigger.

## Examples and cross-references
DispatchDesk CI-to-runtime/queue/provider flows; threat register; release digest incident. Links to Chapters 170 and 176. No cloud/security operation was run.

## Open threads
None for this chapter. Threat models remain assumptions to validate against deployed identity and policy.

## Verification
Independent review approved the body hash recorded in `book/_ai/reviews/171-threat-modeling-for-operators.md`. Focused checker passed 1,466 global local links without warnings or errors. OWASP threat modeling, AWS IAM best practices and GitHub Actions secure-use/OIDC references checked on 2026-10-04. No cloud identity/policy, runner, deployment, security test, containment, backup restore or incident reconciliation was executed against a live system.
