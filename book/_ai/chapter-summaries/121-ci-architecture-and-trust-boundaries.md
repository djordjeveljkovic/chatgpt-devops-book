# Chapter 121 continuation

Status: complete

## Written material
CI event/job/artifact architecture; fork and branch trust; GitHub Actions, GitLab and Jenkins security differences; runner isolation, token and credential scoping, cache/artifact trust, provenance and deployment separation; DispatchDesk artifact flow; threat-review checklist and exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Pipeline event, job graph, runner/agent, protected variable/runner, GITHUB_TOKEN, pull_request_target, artifact provenance, immutable digest, workload identity.

## Examples and cross-references
DispatchDesk untrusted pull request to protected artifact promotion; links to Chapter 118 and the upcoming platform-specific CI chapters.

## Open threads
Verify deployed provider edition, version and repository settings before applying any trigger or credential design; no live CI system was inspected.

## Verification
Scoped checker and local-link validation pending; official GitHub, GitLab and Jenkins security docs inspected 2026-10-04.
