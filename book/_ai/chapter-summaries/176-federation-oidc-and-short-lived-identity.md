# Chapter 176 continuation

Status: complete

## Written material
OIDC issuer/audience/subject trust; CI-specific claim contexts; GitHub immutable-subject rollout; GitLab ID-token claims; Jenkins token issuer plugin; Kubernetes projected service-account tokens; staged static-key removal and revocation.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Federation; issuer; relying party; JWT claim; audience; subject; OIDC provider; trust policy versus permissions policy; bound service-account token; break-glass identity.

## Examples and cross-references
GitHub Actions AWS role trust example; GitLab claim conditions; Jenkins OIDC provider distinction; DispatchDesk static-key migration failure. Links to Chapter 175.

## Open threads
Independent review required. Claim format and provider integration behavior are version/setting dependent; examples must be matched to the actual issuer.

## Verification
GitHub, AWS IAM, GitLab, Jenkins plugin and Kubernetes primary references checked on 2026-10-04. Focused checker pending review. No CI, IAM role, external issuer, service account, deployment or credential revocation was operated.
