# Chapter 126 — Jenkins Controllers and Agents

Status: complete

## Written material

Controller duties and built-in node isolation; agent execution, labels, executors and ephemeral pools; plugin and credential lifecycle; Jenkinsfile/multibranch credential risks; recoverable backups; Linux package installation, Java compatibility, systemd service exposure and secure initial configuration.

## Exact next section

None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology

Controller, built-in node, agent, executor, workspace, label, remoting, `JENKINS_HOME`, multibranch pipeline, folder-scoped credential, plugin lifecycle.

## Examples and cross-references

DispatchDesk trust-separated merge-request, branch-build and release pools; cross-reference to Chapters 125 and 127. Official Ubuntu, Fedora and RHEL-family LTS installation commands with service verification; none were executed.

## Open threads

Independent review approved the corrected body at its current hash. Fresh independent review is pending after adding distribution-specific installation commands. Confirm supported Java, Jenkins and plugin versions before installation, and test backup restoration on the target release.

## Verification

Official Jenkins documentation inspected 2026-10-04. Static parser and local-link checks pending.
