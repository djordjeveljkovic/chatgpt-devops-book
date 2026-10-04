---
book: The Complete DevOps Engineering Book
volume: 13
volume_title: "Continuous Integration Platforms"
chapter: 130
title: "CI Incidents and Platform Comparison"
slug: ci-incidents-and-platform-comparison
status: complete
summary: ../../_ai/chapter-summaries/130-ci-incidents-and-platform-comparison.md
---

# Chapter 130 — CI Incidents and Platform Comparison

## Queueing, flaky jobs and worker pressure

A long pipeline can be caused by slow execution, slow scheduling or both. Measure the interval from event to pipeline creation, time queued before a runner starts, runner provisioning time, job execution time, artifact transfer and cleanup. Compare these by project, runner label or tag, executor, job type, source event and time window. If queue time rises while execution time remains stable, adding more build parallelism may only move the bottleneck to a package registry, database, API quota or shared filesystem.

Start with the job's scheduling constraints. Is the workflow allowed to create this pipeline type? Does the job's condition include it? Does the requested label or tag match an online runner that is allowed to serve the project and ref? Is that runner at its executor limit, waiting for a cloud instance, blocked on a concurrency group, or unable to fetch an image? Check the pipeline graph and event filters before changing worker capacity. A job waiting for a runner and a job waiting for an upstream dependency need different fixes.

Platform details affect queue behavior. GitHub Actions permits concurrent jobs up to account and repository limits; its concurrency groups can cancel older work, and by default only one pending run remains in a group unless queuing is enabled. GitLab Runner scheduling depends on eligible runner tags, project access, configured concurrency and polling behavior; long-poll bottlenecks can delay jobs even when some workers appear idle. Jenkins schedules through controller queues and agent executors; a matching label with no available agent can leave work waiting while unrelated jobs run. Observe the actual platform state and runner logs rather than assuming “more agents” is always the remedy. See [GitHub concurrency](https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency), [GitLab Runner troubleshooting](https://docs.gitlab.com/runner/faq/) and [Jenkins monitoring](https://www.jenkins.io/doc/book/system-administration/monitoring/).

[Chapter 129](129-artifacts-caches-and-build-reproducibility.md) explains why incident responders should trace the exact artifact digest, source revision and producer rather than rely on a mutable version tag.

A practical DispatchDesk incident begins after a dependency update: API test jobs that usually start within two minutes remain queued for 28 minutes, while web jobs still run. The affected jobs request a Linux integration runner and start a disposable database. The team checks the pipeline graph, verifies the jobs were created for the expected event, and confirms that the runner selector is still valid. Runner telemetry shows all eligible integration slots occupied; completed jobs spend several minutes cleaning database containers, and the queue is growing faster than capacity. Registry latency is normal. The immediate response is to reduce duplicate pipelines and cap redundant matrix work, then add temporary isolated capacity for the queue. The follow-up is to shorten cleanup, reuse a managed disposable-service pool safely, and set demand and queue-time alerts. Increasing executors on a shared privileged runner would have reduced queue time while widening its trust and resource boundary.

Flakiness and queue pressure can reinforce each other. Retries consume more worker time; workers under memory or CPU pressure can make tests slower and less deterministic. A high retry rate may hide a broken dependency, a race in test setup or a capacity incident. Track first-attempt failures separately from final retry outcomes, keep the original logs and assign ownership. Quarantine only with visible tracking, expiry and a plan to restore the gate. Cancellation should clean up external test resources; if a canceled job leaves database instances or cloud resources behind, the cleanup path needs its own owner and monitoring.

## GitHub, GitLab and Jenkins tradeoffs

Choose a CI platform based on operating model and boundaries, not on the number of YAML features. GitHub Actions integrates closely with GitHub repositories, pull requests, workflow permissions and hosted runners. It offers a managed control plane and can also connect to self-hosted or larger runners. Teams still need to reason about event context, action dependencies, cache scopes, workflow concurrency and the security of any self-hosted environment.

GitLab CI/CD keeps pipeline configuration in `.gitlab-ci.yml`, with stages, DAG dependencies, artifacts, includes, components, downstream pipelines and integrated runner management. It can be GitLab-hosted or self-managed, and project behavior depends on GitLab version, runner configuration, tier and instance policy. A group-level template can standardize jobs, while a project can still run repository-controlled scripts. Operators must understand runner scope, protected-resource conditions, job-token access and how included configuration is expanded.

Jenkins offers an independently operated controller, agents, plugins, folders, shared libraries and a broad range of execution environments. This flexibility can fit heterogeneous or internal systems, but the organization operates the controller, plugin lifecycle, credential scope, agent trust, backups and capacity. A `Jenkinsfile` and shared library remain executable code, and a trusted shared library increases the importance of controlling its source and version.

| Decision area | GitHub Actions | GitLab CI/CD | Jenkins |
|---|---|---|---|
| Control plane | GitHub-managed service, with hosted or self-hosted execution | GitLab-hosted or self-managed service with GitLab Runner | Organization-managed controller and agents |
| Pipeline definition | Workflow YAML and referenced actions/reusable workflows | `.gitlab-ci.yml`, includes/components and downstream configs | Jenkinsfile, job configuration and plugins/shared libraries |
| Main scheduling model | Jobs and `needs` graph, with account concurrency limits | Stages plus `needs` DAG and runner eligibility | Controller queue, labels and agent executors |
| Key trust question | Which event, token, action and runner execute this job? | Which project/ref can reach this runner, variable or job token? | Who can change the Jenkinsfile/library and access its agent or credential? |
| Operational ownership | Workflow policy and any self-hosted runner fleet | GitLab settings, runner fleet and, for self-managed, GitLab service | Controller availability, plugin/Java updates, credentials, backups and agents |

This comparison describes typical control surfaces, not absolute security or feature parity. Hosted plans and self-managed editions differ; plugins and settings change behavior; each platform can be configured poorly or well. A managed runner can reduce host administration but does not remove the need to control workflow permissions and untrusted code. A self-hosted runner gives network or hardware control while increasing the operator's isolation burden. A flexible controller can model complex internal automation while requiring a team to maintain it. Compare total ownership, required integrations, policy enforcement, recovery objectives, execution trust and the skills available to operate the system.

## Diagnosing a compromised or stalled pipeline

Treat a suspicious pipeline as a security incident when evidence suggests credential access, unexpected code execution, artifact replacement, runner persistence or unauthorized deployment. Record the run, job, source repository and commit, triggering identity, event, runner identity, action/plugin versions, artifact digests, token scopes, network destinations and deployment target. Preserve logs and metadata before deleting the run or runner. Avoid rerunning a suspicious job on the same worker: a retry may execute attacker-controlled code again or destroy useful evidence.

Containment should follow the affected trust boundary. Stop or disable the affected workflow, job or runner pool; prevent new jobs from reaching a suspected persistent host; revoke or rotate credentials that may have been exposed; and block promotion of artifacts produced during the suspect interval. For ephemeral workers, preserve their external runner logs and relevant cloud control-plane records before teardown. Identify downstream consumers by artifact digest and deployment history, then verify whether any suspect output was promoted. A successful signature or green check is not enough if the pipeline that issued it may have been compromised.

For a stalled pipeline, determine whether the run is waiting on a rule, dependency, concurrency slot, eligible worker, provisioning call, external service, artifact transfer or cleanup. Compare with a known-good run on the same commit or equivalent job, then inspect the earliest divergence. Check worker health, disk and memory pressure, network connectivity, registry and package-service latency, API rate limits and runner configuration changes. A change in queue time without a change in build duration points toward scheduling or capacity; a sharp duration increase on one step points toward that step or its dependencies. Avoid force-canceling deployment jobs without checking whether they have already changed external state.

After containment or recovery, restore only from a known-good pipeline configuration, trusted runner image and verified artifact. Rebuild credentials with narrow scope, review permission and runner changes, and test negative authorization paths before restoring production access. Document the timeline, affected commits and artifact digests, credentials rotated, systems checked, gaps in logs and evidence that promotion is safe. Add a focused control or alert for the failed assumption—such as runner assignment monitoring, cache write separation, action/plugin pin review, digest verification or protected-environment policy—rather than adding a generic approval that can be bypassed without addressing the cause.

For DispatchDesk, an unexpected release appears from a workflow run triggered by a fork pull request. The incident lead preserves the run and runner evidence, blocks that artifact digest from deployment, revokes the cloud role credential and registry token available to the job, and checks deployments and downloads of that digest. The security team inspects event context, workflow revision, action pins, runner assignment, artifact producer and OIDC claims. The team then disables the privileged trigger, repairs the event boundary, rebuilds from a protected commit on a clean runner, verifies the new digest and provenance, and resumes promotion only after the trust policy and negative fork test pass. This sequence contains access, preserves evidence and restores from a known-good chain rather than trying to patch the suspect output.

## Takeaways

Separate queue delay from execution time, contain suspicious pipeline access quickly, preserve evidence, and resume only from a known-good build chain with verified artifact identity.

## Exercises and answer guidance

1. Integration jobs take 30 minutes to start, but their execution time is unchanged. What should be measured next? Pipeline creation delay, runner eligibility and state, concurrency or queue limits, provisioning, polling behavior, and upstream dependencies; separate scheduling delay from work duration.
2. GitHub runs show one active run and frequent cancellations in the same concurrency group. What is the risk? The group may combine independent events or deployments; inspect its identity and cancellation policy, then queue or separate work that must not be canceled.
3. GitLab jobs are delayed by about the runner polling interval while some workers are idle. What should operators inspect? Runner long-polling logs and the `concurrent`, `limit` and `request_concurrency` configuration against the actual workload.
4. Jenkins has a growing queue for one label while other agents are idle. What does that suggest? Those agents may not match the label or be eligible for the job, or the matching pool may lack capacity; inspect queue reasons, labels, node restrictions and executor state.
5. A suspected pipeline stole a deploy credential but produced a correctly signed artifact. Should that artifact be released? No. Block it, rotate exposed credentials, preserve evidence, trace consumers and rebuild through a verified trusted path; signing alone does not validate a compromised producer.
6. A team proposes adding more executors to a shared privileged runner. What should be weighed? Queue benefit against trust separation, host risk, resource contention and cross-job leakage; use isolated capacity for sensitive or untrusted work.

Review questions: how do you distinguish queue time from execution time, which platform settings can cancel or delay queued work, what evidence should be preserved during a compromise, and what must be verified before restoring artifact promotion?

## Verification and primary sources

Official GitHub documentation for workflow monitoring, concurrency, cancellation and runner troubleshooting; GitLab documentation for pipeline debugging and Runner queue behavior; and Jenkins documentation for monitoring and agents were inspected on 2026-10-04. The DispatchDesk incidents are illustrative, not observed. No CI run, runner, credential, registry artifact or deployment was inspected or changed. Platform limits, runner capacity, cancellation behavior and available telemetry depend on configured services, plans, versions and editions.

Primary references: [GitHub workflow troubleshooting](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows), [GitHub concurrency](https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency), [GitHub cancellation](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-cancellation), [GitHub runner monitoring](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/monitor-and-troubleshoot), [GitLab pipeline debugging](https://docs.gitlab.com/ci/debugging/), [GitLab Runner FAQ](https://docs.gitlab.com/runner/faq/), [GitLab Runner concurrency configuration](https://docs.gitlab.com/runner/configuration/advanced-configuration/), [Jenkins monitoring](https://www.jenkins.io/doc/book/system-administration/monitoring/), and [Jenkins agents](https://www.jenkins.io/doc/book/using/using-agents/).
