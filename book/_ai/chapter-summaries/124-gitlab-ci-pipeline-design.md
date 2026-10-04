# Chapter 124 — GitLab CI Pipeline Design

Status: complete

## Written material

Pipeline stages and DAG scheduling through `needs`; workflow and job rules; merge-request and fork context; include/component trust; artifact and cache boundaries; deployment environments; child and multi-project pipelines. DispatchDesk example tests API and worker jobs on merge requests and gates packaging/deployment to the default branch.

## Exact next section

None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology

Pipeline source, stage, job, `workflow: rules`, job `rules`, `needs`, include, component, artifact, cache, protected environment, parent-child pipeline, multi-project pipeline.

## Examples and cross-references

Illustrative `.gitlab-ci.yml` with repository-owned scripts; links to Chapters 121 and the GitLab docs.

## Open threads

Independent review approved the corrected body at its current hash. Validate with CI Lint against the target GitLab version and project settings before use; no runner, environment or deployment was configured.

## Verification

Official GitLab documentation inspected 2026-10-04. Static parse and link checks pending.
