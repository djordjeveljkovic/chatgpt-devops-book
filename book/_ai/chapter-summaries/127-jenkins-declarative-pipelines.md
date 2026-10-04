# Chapter 127 — Jenkins Declarative Pipelines

Status: complete

## Written material

Declarative pipeline directives and agent allocation; `when`, `post`, workspace and stash behavior; credential-binding limits; trusted versus sandboxed shared libraries; DispatchDesk build/test/publish graph with separate untrusted and release agents and explicit artifact verification.

## Exact next section

None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology

Jenkinsfile, Declarative Pipeline, stage, step, agent, executor, workspace, `post`, stash/unstash, Shared Library, Groovy sandbox, credentials binding.

## Examples and cross-references

Illustrative Groovy pipeline using placeholder labels and repository scripts. It was not executed. Chapter 126 covers controller and agent trust boundaries.

## Open threads

Independent review approved the corrected body at its current hash. Validate Declarative Pipeline and plugin syntax on the target Jenkins LTS and verify multibranch/job permissions before use.

## Verification

Official Jenkins documentation inspected 2026-10-04. Static parser and local-link checks pending.
