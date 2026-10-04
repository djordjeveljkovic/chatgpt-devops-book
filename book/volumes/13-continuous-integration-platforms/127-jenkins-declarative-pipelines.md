---
book: The Complete DevOps Engineering Book
volume: 13
volume_title: "Continuous Integration Platforms"
chapter: 127
title: "Jenkins Declarative Pipelines"
slug: jenkins-declarative-pipelines
status: complete
summary: ../../_ai/chapter-summaries/127-jenkins-declarative-pipelines.md
---

# Chapter 127 — Jenkins Declarative Pipelines

## Jenkinsfile, stages and post actions

A Jenkins Pipeline describes work as stages and steps. Declarative Pipeline gives that work a structured Groovy-based syntax with explicit directives for agents, options, parameters, environment, stages, conditions and post-build actions. A `Jenkinsfile` stored in source control makes the pipeline reviewable with application changes, but it is executable code. Anyone whose changes are run by Jenkins must be trusted with the credentials, agents, plugins and network access available to that pipeline. Chapter 126 covers controller and agent separation; this chapter focuses on the job graph and Jenkinsfile behavior.

A top-level `agent` assigns an executor and workspace to the whole pipeline. `agent none` avoids holding one executor for the full run and requires each stage to select its own agent. Stage-level agents can separate toolchains and trust classes, but stages may run on different workspaces. Files do not move merely because stages occur in order; use `stash`/`unstash` for small, same-run transfers, or a durable artifact repository for outputs that must outlive a run. Stashes consume controller-side storage and are not a release registry. A `when` condition can skip a stage based on branch or other context, but it is not an authorization boundary if an untrusted author can edit the Jenkinsfile.

Use `post` blocks for cleanup, test reports, notifications and archiving results. An `always` action runs regardless of the build result; success, failure, unstable, changed and cleanup conditions have different meanings. Keep cleanup idempotent and make sure it runs with the workspace and credentials it needs. Avoid treating a notification or archived report as proof that the build was safe. Set timeouts to contain stuck work, timestamps for useful logs, and concurrency controls only when they preserve the intended behavior. Review syntax against the Pipeline Syntax reference and the installed plugin versions; Jenkins Pipeline steps are provided by core and plugins, so not every example exists on every controller. See [Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/) and [Using a Jenkinsfile](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/).

A build and test stage should run without release credentials. Jenkins credential bindings place secret values into an environment variable or temporary file for a limited block, but masking only reduces accidental console disclosure. Do not interpolate secrets into Groovy strings; use a single-quoted shell script so the shell reads the variable from its environment. Do not run untrusted tests while a production credential is bound. A malicious test can read environment variables, process arguments, files or network access even when the Jenkinsfile itself is controlled. Keep credentials out of global scope when only one folder or job needs them.

## Shared libraries and controlled reuse

A Shared Library packages reusable Pipeline code in a source-controlled repository. A globally trusted library can use Jenkins internals and unrestricted Groovy/Java APIs; Jenkins warns that anyone able to push to that library's source may gain broad access to Jenkins. Treat trusted libraries as privileged platform code: limit who can change them, review changes, pin a known version, test updates, and keep the default version override disabled when callers must not select arbitrary code. Untrusted libraries run in the Groovy sandbox and are appropriate for less privileged helpers, though sandboxing does not make the rest of the pipeline or its shell commands safe.

Folder-level libraries scope reuse to jobs in that folder and are untrusted by design. Scope can make ownership clearer, but folder placement does not protect a library if users who can edit it also control privileged consumers. Avoid loading mutable branch names of shared libraries into production pipelines when those branches can change without a reviewed release. A tag is only immutable if policy prevents it being moved; a commit SHA provides an explicit source revision. Record library revision in the build metadata so an incident can identify exactly which shared code ran. See Jenkins' [Shared Libraries guide](https://www.jenkins.io/doc/book/pipeline/shared-libraries/).

Shared code should expose a small, documented interface. Keep credential binding and privileged deployment in the narrowest trusted layer. A library that accepts arbitrary shell fragments, paths, URLs or credential IDs can transfer caller-controlled data into a privileged context. Validate parameters, restrict allowed destinations and credentials, and keep tests that prove invalid inputs fail closed. Centralization reduces duplicated logic but also multiplies the effect of an unsafe update.

## A build, test and publish pipeline

DispatchDesk builds and tests on an untrusted agent without secrets, then transfers the candidate within the run. Only a multibranch branch named `main` reaches the publish stage; `beforeAgent true` evaluates the branch condition before Jenkins allocates the trusted release agent. That stage uses a separate trusted agent, verifies the candidate's digest and source identity, then binds a narrowly scoped registry credential for the publish command.

```groovy
pipeline {
  agent none

  options {
    skipDefaultCheckout(true)
    timestamps()
    timeout(time: 30, unit: 'MINUTES')
  }

  stages {
    stage('Build and test') {
      agent { label 'linux-untrusted' }
      steps {
        checkout scm
        sh './ci/build-and-test'
        stash name: 'candidate', includes: 'dist/**'
      }
      post {
        always {
          archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
      }
    }

    stage('Publish') {
      when {
        beforeAgent true
        branch 'main'
      }
      agent { label 'linux-release' }
      steps {
        checkout scm
        unstash 'candidate'
        sh './ci/verify-candidate dist/'
        withCredentials([string(credentialsId: 'dispatchdesk-registry-write', variable: 'REGISTRY_TOKEN')]) {
          sh '''set +x
./ci/publish-release dist/
'''
        }
      }
    }
  }

  post {
    always {
      echo 'Pipeline finished; inspect the recorded result and candidate digest.'
    }
  }
}
```

This is an illustrative Declarative Pipeline, not a ready-to-run release process. It assumes a multibranch job where the `main` branch condition is available, the named labels map to correctly isolated agents, required Pipeline and Credentials Binding steps are installed, and repository scripts implement the described behavior. The `stash` is run-local and may not be suitable for large artifacts; use an artifact repository for durable or cross-controller promotion. The publish stage checks out the same run revision, restores the candidate, and verifies it before credential binding. `withCredentials` scopes the environment variable to the body but cannot stop malicious publish code from exfiltrating it. Protect the branch and Jenkins job configuration, keep the trusted agent inaccessible to untrusted jobs, and use a credential limited to the intended registry/repository.

A production pipeline should preserve an identity record linking the Jenkins build URL and number, source commit, shared-library revision, artifact digest and registry location. The verification step should reject an artifact from a different build or source revision even if the file is present. Test interruption, agent loss, failed tests, missing stash, credential binding failure and registry rejection. Confirm behavior on the installed Jenkins core and plugin versions; a parser or snippet generator cannot validate agent permissions, multibranch trust strategy or credential scope.

## Takeaways

A Jenkinsfile defines executable work, not authorization by itself. Allocate trusted agents only after eligibility checks, transfer explicit artifacts between stages, verify them, and bind credentials around the smallest operation.

## Exercises and answer guidance

1. A pipeline uses `agent any` while it waits for approval between test and deployment. What cost and risk can this create? It holds an executor/workspace during the wait and may keep files or state available longer; use `agent none` with stage agents where appropriate and pass only explicit outputs.
2. A deploy stage has `when { branch 'main' }`. Does that prevent an untrusted user from deploying? No. It is a pipeline condition, not an authorization boundary; restrict who can change/run the Jenkinsfile and who can access the agent and credential.
3. A globally trusted shared library is updated from a feature branch selected by the caller. What is wrong? Caller-controlled mutable code is running with trusted library powers; pin and review an immutable approved revision, and restrict library authors.
4. A shell step uses `sh "deploy --token ${TOKEN}"`. What is the problem? Groovy interpolates the secret into the command string; use a single-quoted shell script that expands the environment variable and keep the credential block narrow.
5. A publish stage runs after tests but reads files left on a shared agent workspace. Why is this fragile? It relies on mutable persistent state rather than an explicit artifact edge; transfer a named candidate, verify its digest/source, and isolate the trusted stage.
6. The `post { always { ... } }` block sends a successful notification. What does that establish? Only that the configured post step ran; inspect the actual build result, artifact identity, and deployment record before asserting release success.

Review questions: how do top-level and stage agents affect executor use, what is the trust difference between global trusted and sandboxed shared libraries, when is a stash appropriate, and what does a branch condition fail to authorize?

## Verification and primary sources

Official Jenkins documentation for Declarative Pipeline syntax, Jenkinsfiles, credentials binding and shared libraries was inspected on 2026-10-04. The Groovy example is illustrative and was not run through a Jenkins controller. Static book checks do not validate Declarative syntax against installed plugin versions, multibranch branch behavior, script approval, agent labels, stash capacity, credential availability, shell behavior or registry publication.

Primary references: [Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/), [Jenkinsfile](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/), [Shared Libraries](https://www.jenkins.io/doc/book/pipeline/shared-libraries/), [credentials security](https://www.jenkins.io/doc/book/security/credentials/), [multibranch credential security](https://www.jenkins.io/doc/book/security/securing-org-folders-and-multibranch-pipelines/), and [Credentials Binding step reference](https://www.jenkins.io/doc/pipeline/steps/credentials-binding/).
