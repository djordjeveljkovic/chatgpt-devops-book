# Chapter 125 — GitLab Runners and Credentials

Status: complete

## Written material

The chapter compares shell, Docker and Kubernetes executor trust boundaries; describes protected runners and the conditional protected-resource rules for merge requests; covers variable exposure, `CI_JOB_TOKEN` scope, job-token allowlists, OIDC audience and cloud claims, and runner operations that prevent cross-job leakage. The DispatchDesk scenario separates fork validation, trusted builds and protected deployment.

## Exact next section

None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology

Runner executor, protected runner, protected variable, `CI_JOB_TOKEN`, job-token allowlist, OIDC ID token, audience, subject claim, ephemeral runner, executor privilege.

## Examples and cross-references

Illustrative deploy job with a job-scoped ID token; Chapter 121 covers CI trust boundaries, Chapter 124 covers pipeline design.

## Open threads

Check deployed GitLab version, edition, runner configuration and cloud claim support before applying examples; no runner or cloud identity was configured.

## Verification

Official GitLab documentation inspected 2026-10-04. Scoped YAML and local-link checks passed before the optional low-risk clarifications; fresh checks and review pending.
