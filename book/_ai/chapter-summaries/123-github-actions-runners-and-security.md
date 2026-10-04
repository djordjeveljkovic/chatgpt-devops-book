# Chapter 123 — GitHub Actions Runners and Security

Status: complete

## Written material

The chapter explains hosted and self-hosted runner boundaries, runner groups, persistent versus ephemeral execution, and separation of untrusted validation, trusted builds and deployment pools. It covers least-privilege `GITHUB_TOKEN` permissions, OIDC trust conditions and subject claims, environment gates, full-SHA action pinning, and risks from `pull_request_target` and `workflow_run`. The DispatchDesk example sketches a build and protected deployment workflow with artifact verification.

## Exact next section

None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology

Hosted runner, self-hosted runner, runner group, ephemeral runner, OIDC issuer/audience/subject claims, deployment environment, `pull_request_target`, `workflow_run`, artifact provenance.

## Examples and cross-references

The release workflow has intentionally unresolved action SHA placeholders and illustrative repository scripts. It is not ready to execute. Chapter 122 covers workflow construction; Chapters 124–125 cover GitLab pipelines and runner credentials.

## Open threads

Obtain an independent review, address findings, verify the final body hash, and promote when approved.

## Verification

Official GitHub Actions documentation inspected 2026-10-04. Static parser and local-link checks pending. No workflow or cloud deployment was executed.
