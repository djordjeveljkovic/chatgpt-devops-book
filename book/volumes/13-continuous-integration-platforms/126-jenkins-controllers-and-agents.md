---
book: The Complete DevOps Engineering Book
volume: 13
volume_title: "Continuous Integration Platforms"
chapter: 126
title: "Jenkins Controllers and Agents"
slug: jenkins-controllers-and-agents
status: complete
summary: ../../_ai/chapter-summaries/126-jenkins-controllers-and-agents.md
---

# Chapter 126 — Jenkins Controllers and Agents

## Controller duties and agent execution

The Jenkins controller coordinates jobs, stores configuration and credentials, schedules work and serves the web interface. Agents provide executors that run builds when the controller assigns them. This separation protects controller availability and data only when the agent boundary is real: build scripts, tests and repository-controlled pipeline definitions execute code chosen by people who may have less trust than the Jenkins administrator.

Jenkins starts with a built-in node that can run builds. Builds on that node share the controller process's file-system access, including the Jenkins home directory. Jenkins recommends setting the built-in node's executor count to zero and using separate agents. The Agent-to-Controller Access Control system rejects unsafe remoting requests from agents; it is always enabled since Jenkins 2.326 and enabled by default in earlier releases. It does not make a compromised agent fully isolated from controller vulnerabilities or capabilities intentionally granted to jobs. Keep the controller on a private management network, limit inbound access, use a supported Jenkins release, and do not expose the controller's administrative port to build networks. See [controller isolation](https://www.jenkins.io/doc/book/security/controller-isolation/) and [managing nodes](https://www.jenkins.io/doc/book/managing/nodes/).

A Jenkins agent has labels, a connection method, executors and a workspace. Labels help a pipeline request an OS, toolchain or trust class, but a label is not an isolation boundary. Agents that serve untrusted pull requests should not share a user account, filesystem, credentials, network route or writable cache with release agents. Consider one executor per node for the strongest simple separation, particularly where different projects or trust levels share a controller. More executors increase concurrency but can create CPU, memory, disk and cross-build contention; an executor count is capacity, not a security control.

Use ephemeral cloud or container agents for untrusted work where possible, with a clean environment for each job and a controlled teardown. For static agents, run a dedicated unprivileged OS account, keep workspaces separate, remove stale workspaces and temporary credentials, and restrict access to controller files and other agents. Do not install agents on the controller host under the Jenkins service account. If a single host must run both roles, use a separate OS identity with no access to `JENKINS_HOME` or privilege escalation, and recognize that this remains weaker than separate hosts.

Jenkins remoting depends on controller-agent connectivity and compatible software. Agent-to-Controller Access Control, always enabled since Jenkins 2.326 and enabled by default in earlier releases, rejects unsafe remoting requests from agents; it does not make a compromised agent fully isolated from controller vulnerabilities or capabilities intentionally granted to jobs. Prefer a documented and secured inbound or outbound connection model for the environment; avoid exposing remoting ports broadly. Configure firewall rules around actual controller and agent needs, monitor offline agents and queue time, and alert on unexpected agent registration or configuration changes. An agent that disappears can stall jobs, while an over-permissive agent can expose credentials or workspace contents to every job it runs.

## Plugins, credentials and lifecycle

Plugins add SCM integrations, pipeline steps, agents, credentials providers and UI features. Each plugin expands the controller's code and compatibility surface. Install only plugins with an identified owner and operational need, keep Jenkins core and plugins updated, remove unused plugins, and test updates against a representative configuration before applying them to production. Review plugin security advisories and maintain a recovery path for a failed update. The [Jenkins security guide](https://www.jenkins.io/doc/book/security/) and [plugin documentation](https://www.jenkins.io/doc/book/managing/plugins/) describe supported administration practices.

Credentials stored in Jenkins are encrypted on the controller and referenced in jobs by credential IDs. Encryption at rest does not protect a credential from a pipeline authorized to use it. Scope credentials to the narrowest folder or job, prefer read-only SCM credentials for checkout, and use short-lived federation for cloud access where a supported integration exists. Never place secret values in a `Jenkinsfile`, repository file, build parameter or console output. Masking is a log aid, not an execution boundary; malicious build code can copy a credential to another output or network destination.

Multibranch pipelines make repository-controlled `Jenkinsfile` changes executable configuration. Jenkins documents that SCM scan credentials can be used arbitrarily by anyone able to change the `Jenkinsfile` in a branch that the multibranch project builds. Even if the `Jenkinsfile` itself is trusted, modified tests or build scripts can steal a credential bound around their execution. Separate fork validation from privileged release jobs, keep credentials away from test steps that execute unreviewed code, and use repository-specific, least-privilege credentials. Central pipeline definitions can reduce configuration drift, but the trusted pipeline may still execute untrusted build scripts; keep that distinction explicit. See [securing organization folders and multibranch pipelines](https://www.jenkins.io/doc/book/security/securing-org-folders-and-multibranch-pipelines/) and [credentials](https://www.jenkins.io/doc/book/security/credentials/).

Back up configuration, job definitions, plugin state and encrypted credential data using a consistent and access-controlled method, but exclude `$JENKINS_HOME/secrets/` from ordinary backups. Preserve the required decrypting material—`secrets/master.key` and `secrets/hudson.util.Secret`—separately in a highly restricted location apart from those backups; someone with both the key material and backup data can decrypt credentials and access what Jenkins can reach. Reintroduce the separately controlled key material only during a documented restore, then test restoration in an isolated environment and verify that administrators can recover access. Track plugin versions and configuration as code so a controller can be rebuilt, but do not commit secret values or unreviewed credential IDs to public repositories. Store logs and audit events outside the controller host so they survive a disk or controller failure.

## Installing and securing a Jenkins service

Install Jenkins from the official package repository or a maintained container image, and pin a deliberate release channel. The official Linux installation guide currently requires Java 21 or later for Jenkins; confirm the Java support policy for the exact controller release and plugins before upgrading. Prefer the Long-Term Support release for a production controller unless there is a specific need and test capacity for weekly releases. Keep controller and agent Java requirements distinct: each agent must use a runtime compatible with its Jenkins remoting and job toolchain.

The following package examples use Jenkins LTS and OpenJDK 21, matching the official Linux guide inspected on 2026-10-04. Run them on a newly prepared controller host from any working directory; `sudo` performs the package and system changes as an administrator. Confirm the supported Java release and repository instructions for the exact Jenkins version before use. The annual signing-key filename in the Ubuntu commands must be rechecked on the official site when the calendar year or repository guidance changes.

On Ubuntu 24.04 or a compatible Debian-based host, install Java before Jenkins, add the Jenkins LTS repository using its signing key, then install and start the systemd service:

```bash
sudo apt update
sudo apt install fontconfig openjdk-21-jre wget
java -version
sudo wget -O /etc/apt/keyrings/jenkins-keyring.asc \
  https://pkg.jenkins.io/debian-stable/jenkins.io-2026.key
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc]" \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update
sudo apt install jenkins
sudo systemctl enable --now jenkins
sudo systemctl status jenkins
```

On Fedora, the package manager is `dnf`; the official Jenkins LTS RPM repository is configured separately from the weekly-release repository:

```bash
sudo dnf install wget
sudo wget -O /etc/yum.repos.d/jenkins.repo \
  https://pkg.jenkins.io/rpm-stable/jenkins.repo
sudo dnf install fontconfig java-21-openjdk
sudo dnf install jenkins
sudo systemctl daemon-reload
sudo systemctl enable --now jenkins
sudo systemctl status jenkins
```

On Red Hat Enterprise Linux and compatible distributions, use the official LTS repository with the package manager supported by that release. The Jenkins guide uses `yum`; current RHEL releases may provide `yum` through DNF. Ensure the enabled RHEL repositories and entitlements provide OpenJDK 21 before installing:

```bash
sudo yum install wget
sudo wget -O /etc/yum.repos.d/jenkins.repo \
  https://pkg.jenkins.io/rpm-stable/jenkins.repo
sudo yum install fontconfig java-21-openjdk
sudo yum install jenkins
sudo systemctl daemon-reload
sudo systemctl enable --now jenkins
sudo systemctl status jenkins
```

`java -version` verifies the selected runtime; `systemctl status` verifies whether the service is active. If startup fails, inspect `sudo journalctl -u jenkins --since "10 minutes ago"` and confirm Java compatibility before changing the service unit. Do not open port 8080 to the public internet: Jenkins commonly listens there by default, so restrict it to a management network or proxy and expose browser access through HTTPS. Do not disable SELinux or AppArmor to work around a denial; inspect the service logs and correct the specific label or policy requirement. Package names, repository keys, service details and Java availability differ by release, so use the official [Linux installation guide](https://www.jenkins.io/doc/book/installing/linux/) and the target distribution's documentation for changes.

After installation, keep `JENKINS_HOME` on protected storage and limit network exposure. Put browser access behind a maintained HTTPS reverse proxy or load balancer, configure the Jenkins root URL, and allow only administrator and user networks that need the interface. Follow the setup wizard, create named administrator accounts, integrate the intended identity provider, and grant permissions by role rather than sharing the initial admin account. Disable anonymous access unless a specific read-only use case has been reviewed. Treat controller configuration and script approval as privileged changes.

Before accepting production jobs, set the built-in node to zero executors, create a separate agent pool, restrict job configuration rights, and verify which credentials are available to each folder and multibranch project. Configure a backup schedule and complete a restore exercise. Patch Jenkins core, plugins, Java and agent images under a tested change process. Review the controller's security warnings, logs, plugin health, queue depth, agent connectivity, disk capacity and backup completion. Do not infer that the service is secure because the package installed and the web page loads.

For DispatchDesk, public merge requests run tests on disposable agents with no deployment credentials or production route. Protected branch builds use a separate trusted pool. A release pipeline requests a scoped deploy credential only after approval and deploys a digest-identified artifact. The controller coordinates these jobs but does not execute application builds itself. [Chapter 125](125-gitlab-runners-and-credentials.md) covers GitLab runner boundaries; [Chapter 127](127-jenkins-declarative-pipelines.md) covers how Jenkinsfiles express job flow.

## Takeaways

Keep builds off the Jenkins controller and separate agents by trust. Treat Jenkinsfiles, plugins and trusted libraries as privileged code, and preserve decrypting key material separately from routine backups.

## Exercises and answer guidance

1. The built-in node has two executors because it speeds up small builds. What is the problem? Builds share the controller process's filesystem privileges and can interfere with controller state; set built-in executors to zero and run builds on separate agents.
2. A multibranch job binds an SCM credential around `sh 'make test'`. A fork can modify tests but not the Jenkinsfile. Is the credential safe? No. The modified test code executes while the credential is available and can exfiltrate it; do not expose credentials while executing untrusted build code.
3. A Jenkins administrator increases a shared agent from one to eight executors to reduce queue time. What should be assessed? Resource contention, workspace and process isolation, trust levels, and whether builds can inspect each other's files or credentials.
4. An agent is registered with the label `production`. Does this ensure only release jobs use it? No. Review who can configure jobs and labels, agent scope and permissions, folder access, credentials and network routes; routing metadata is not authorization by itself.
5. A restored Jenkins backup cannot decrypt stored credentials. What may be missing? The separately preserved `master.key` and `hudson.util.Secret`, or consistent encrypted credential data; keep key material outside ordinary backups, reunite it only during a restricted restore, and test that process before depending on the backup.
6. The controller web page is reachable over HTTP from a public network. What controls should be added? Restrict network access, put the UI behind HTTPS, configure authentication and least-privilege authorization, and review reverse-proxy and Jenkins URL settings.

Review questions: which work belongs on the controller, how do executor count and trust isolation differ, why can a safe Jenkinsfile still execute unsafe repository code, and what must a recoverable controller backup include?

## Verification and primary sources

Official Jenkins documentation for controller isolation, agents, plugin management, credentials, multibranch pipeline security and Linux installation was inspected on 2026-10-04. Ubuntu, Fedora and RHEL-family installation commands are illustrative and were not run; no Jenkins service was installed. Jenkins releases, Java and plugin compatibility, distribution repository keys and systemd behavior should be checked against the target platform at deployment time. Static book checks do not validate service configuration, network policy, plugin state, agent isolation or recovery.

Primary references: [Controller isolation](https://www.jenkins.io/doc/book/security/controller-isolation/), [agents](https://www.jenkins.io/doc/book/using/using-agents/), [nodes](https://www.jenkins.io/doc/book/managing/nodes/), [plugin management](https://www.jenkins.io/doc/book/managing/plugins/), [credentials security](https://www.jenkins.io/doc/book/security/credentials/), [controller backup and restore](https://www.jenkins.io/doc/book/system-administration/backing-up/), [multibranch credential security](https://www.jenkins.io/doc/book/security/securing-org-folders-and-multibranch-pipelines/), [Linux installation](https://www.jenkins.io/doc/book/installing/linux/), [systemd services](https://www.jenkins.io/doc/book/system-administration/systemd-services/), and [Java support policy](https://www.jenkins.io/doc/book/platform-information/support-policy-java/).
