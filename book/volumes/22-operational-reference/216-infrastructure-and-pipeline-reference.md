---
book: The Complete DevOps Engineering Book
volume: 22
volume_title: "Operational Reference"
chapter: 216
title: "Infrastructure and Pipeline Reference"
slug: infrastructure-and-pipeline-reference
status: complete
summary: ../../_ai/chapter-summaries/216-infrastructure-and-pipeline-reference.md
---

# Chapter 216 — Infrastructure and Pipeline Reference

Use this chapter when a change is waiting and you need to remember the right inspection step. [Volume8](../08-infrastructure-as-code/README.md) teaches state and reconciliation; [Volume13](../13-continuous-integration-platforms/README.md) teaches the three CI platforms; [Volume14](../14-delivery-deployment-and-gitops/README.md) teaches release behavior. The reference joins those workflows at their boundaries: configuration, plan, artifact, execution identity and resulting service.

## Infrastructure command order

Run these commands inside the intended root module after establishing the backend, workspace and provider identity. Each row answers a different question.

| Command | Question answered | Limit |
|---|---|---|
| `terraform version` | Which CLI is running? | Provider and module versions are separate. |
| `terraform init -input=false` | Are this directory's backend and dependencies initialized? | May contact remote systems and install dependencies; configuration matters. |
| `terraform fmt -check -recursive` | Does formatting match the tool's conventions? | Formatting does not validate semantics. |
| `terraform validate` | Is configuration internally valid with available schemas? | Does not establish provider credentials or real capacity. |
| `terraform workspace show` | Which selected workspace does this directory report? | Workspaces alone do not establish account or backend isolation. |
| `terraform plan -out=release.tfplan` | Which changes are proposed against the observed state? | Contains potentially sensitive information; planning requires appropriate access. |
| `terraform show release.tfplan` | What is in this saved plan? | Review replacements, deletions, permissions and unknown values explicitly. |
| `terraform apply release.tfplan` | Execute that saved plan | This is a mutation and does not prompt for a new approval of the saved plan. |

`init -upgrade` deliberately changes dependency selection within constraints; it is unsuitable as an unexplained step in every release. Backend migration/reconfiguration is also a separate operation with its own review. Initialization behavior is documented in [Terraform init](https://developer.hashicorp.com/terraform/cli/commands/init). Formatting and validation have distinct scopes described in [fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) and [validate](https://developer.hashicorp.com/terraform/cli/commands/validate).

OpenTofu uses `tofu` for the equivalent core commands. Verify its own version and backend documentation instead of assuming every Terraform feature is portable. Do not alternate the two engines against production state as a casual troubleshooting experiment. [OpenTofu plan](https://opentofu.org/docs/cli/commands/plan/) documents its planning modes and output behavior; [Chapter072](../08-infrastructure-as-code/072-terraform-and-opentofu-cli-foundations.md) explains the choice and workflow.

## Plan exit codes and artifact custody

With `-detailed-exitcode`, Terraform plan reports0 for a successful empty diff,1 for an error and2 for a successful plan containing changes. A generic pipeline that rejects all nonzero statuses will wrongly reject2; a pipeline that ignores all errors will wrongly accept1. The mapping and saved-plan option are documented in [Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan).

This Bash fragment demonstrates deliberate status handling. It requires an initialized real module and may perform provider reads; it does not apply anything.

```bash
set -euo pipefail
umask 077
plan_status=0
terraform plan -input=false -detailed-exitcode -out=release.tfplan || plan_status=$?
case "$plan_status" in
  0) printf 'Plan succeeded; no changes.\n' ;;
  2) printf 'Plan succeeded; changes require review.\n' ;;
  *) printf 'Plan failed with status %s.\n' "$plan_status" >&2; exit "$plan_status" ;;
esac
terraform show -no-color release.tfplan > release-plan.txt
```

The review concerns the exact saved plan and its associated source revision, selected engine/provider versions, backend and target identity. If a new plan is generated after approval, it needs assessment again. A checksum can show whether a file changed, but does not by itself establish who produced or authorized it. Protect plan artifacts and rendered output with restricted storage, retention and runner access; a redacted terminal display is not proof that a binary plan contains no secrets.

Applying a saved plan executes its decisions; Terraform does not ask for the interactive confirmation used by an ordinary unsaved `apply`. Build the authorization boundary before invoking the command. A partial failure can leave some resources changed and others untouched. Inspect actual state and provider outcomes before creating a new plan; restoring an old state file blindly can create a second inconsistency. These are operational consequences of the [apply workflow](https://developer.hashicorp.com/terraform/cli/commands/apply), elaborated in [Chapter080](../08-infrastructure-as-code/080-infrastructure-lifecycle-and-disaster-recovery.md).

State locking and a deployment queue solve different problems. A state lock protects coordination for that state operation. It does not serialize every database migration, traffic switch or application deployment in the account. Keep the wider release transaction under an appropriate controller and ownership policy.

## Ansible lookup and its boundaries

| Command | Purpose | Watch for |
|---|---|---|
| `ansible-inventory -i inventory.yml --graph` | Inspect inventory group structure | Inventory plugins can obtain data dynamically; target names need verification. |
| `ansible-playbook -i inventory.yml site.yml --list-hosts` | List selected play hosts | Check the effective inventory and host pattern. |
| `ansible-playbook -i inventory.yml site.yml --syntax-check` | Parse the playbook | Parsing does not establish host reachability or module effects. |
| `ansible-playbook -i inventory.yml site.yml --list-tasks` | Inspect planned task structure | Dynamic includes and runtime conditions can limit what is visible. |
| `ansible-playbook -i inventory.yml site.yml --limit harbor-staging --check` | Predict supported changes on a bounded group | Module support and explicit task settings determine what really happens. |
| `ansible-playbook -i inventory.yml site.yml --limit harbor-staging` | Execute the selected play | This changes the selected hosts; verify the limit before execution. |

The [ansible-playbook CLI](https://docs.ansible.com/projects/ansible/latest/cli/ansible-playbook.html) documents selection and inspection flags. Check mode is a simulation supported by modules, not a universal no-effect guarantee for arbitrary playbooks. A task may explicitly force execution in check mode; unsupported modules may not provide useful predictions. Diff mode can disclose rendered secrets, so do not add `--diff` automatically to production jobs. These qualifications come from [Ansible check and diff mode](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_checkmode.html).

Harbor's change evidence should identify the exact hosts, configuration revision, privilege escalation scope and service verification. An idempotent file task can succeed while the application still fails due to a missing database grant. Handler execution can also depend on the run's changes and failure path. Use [Chapters077–078](../08-infrastructure-as-code/077-ansible-inventory-and-playbooks.md) for complete playbooks and secret handling, rather than treating a successful recap as customer acceptance.

## Inspect the pipeline that actually ran

| Platform | Evidence to capture | Failure that a green badge can hide |
|---|---|---|
| GitHub Actions | Repository, workflow/run ID, commit, event, attempt, jobs, artifact digest and environment | A job was skipped or checks ran for a different commit. |
| GitLab CI | Project/pipeline ID, commit, source, effective configuration, jobs, artifacts and environment | A failed job was allowed to fail; a manual release job never ran. |
| Jenkins | Controller/job path, build number, parameters, revision, agent and stage results | An unstable result or caught exception allowed later work to proceed. |

With authenticated GitHub CLI, these examples inspect a chosen repository and run. Replace the fictional repository and numeric ID; no run is triggered.

```bash
gh run list --repo example/dispatchdesk --limit 20
gh run view 123456 --repo example/dispatchdesk
gh run view 123456 --repo example/dispatchdesk --log-failed
```

`--log-failed` limits displayed logs to failed steps. Some unavailable job logs can affect retrieval, and logs may contain application data despite secret masking. The [gh run view manual](https://cli.github.com/manual/gh_run_view) explains the command's flags. Do not use `gh run rerun` until you understand whether repeating that run can reapply a migration or deployment.

For GitLab use the authenticated pipeline/job UI or API and match the pipeline's `sha` to the intended revision; the [Pipelines API](https://docs.gitlab.com/api/pipelines/) documents those records. `allow_failure: true` changes whether a job failure blocks progression. Manual-job defaults differ depending on whether they are expressed inside rules, so set a mandatory release gate's behavior explicitly. See the [GitLab YAML reference](https://docs.gitlab.com/ci/yaml/) and [Chapter124](../13-continuous-integration-platforms/124-gitlab-ci-pipeline-design.md).

For Jenkins a build's authenticated `api/json` and selected fields can support automation; use the installed controller's API page rather than inventing plugin endpoints. Read-only GET requests and build-triggering POSTs have different effects. The [Jenkins remote API](https://www.jenkins.io/doc/book/using/remote-access-api/) documents access patterns. The declarative [Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/) remains the source for stage/option behavior; the book's Jenkins chapters explain agents and credentials in context.

## Release serialization and credentials

GitHub environment protection and concurrency, GitLab resource groups and Jenkins concurrency controls are useful but have distinct scope. Define the resource you must protect: for example, the production DispatchDesk deployment and its compatible schema transition.

| Mechanism | What to verify before relying on it |
|---|---|
| GitHub Actions concurrency group | Every workflow touching the same release resource uses the same effective key; cancellation policy does not interrupt a nonrepeatable migration. |
| GitLab `resource_group` | Jobs for the shared target use the intended key and process policy; other projects/controllers are coordinated separately. |
| Jenkins `disableConcurrentBuilds()` | Serializes executions of that Pipeline; separate jobs touching the same target need additional coordination. |

Platform semantics are documented in [GitHub deployment controls](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments), [GitLab resource groups](https://docs.gitlab.com/ci/resource_groups/) and [Jenkins Pipeline options](https://www.jenkins.io/doc/book/pipeline/syntax/). Repository membership or a branch name alone is not sufficient evidence that a run may receive production credentials. Establish event trust, reviewer policy, runner isolation and short-lived credential audience/subject conditions in the CI security chapters.

Treat test artifacts and release artifacts differently. A cache accelerates work and may be missing or stale; an artifact promoted for release needs a durable identity and custody trail. Rebuilding the same commit after approval can change dependency resolutions or base images. Prefer promoting the already assessed artifact, with a clear compatibility check for configuration and data. See [Chapter129](../13-continuous-integration-platforms/129-artifacts-caches-and-build-reproducibility.md) and [Chapter131](../14-delivery-deployment-and-gitops/131-release-engineering-and-artifact-promotion.md).

## Failure index and drills

| Symptom | First question | Recovery direction |
|---|---|---|
| Plan unexpectedly replaces a database | Which attribute/provider/version changed, and what data/recovery evidence exists? | Stop the release boundary and assess replacement semantics; do not conceal it with targeting. |
| Apply reports an active lock | Is another operation still running and who owns it? | Coordinate with the owner; forced unlock is exceptional and requires proving the lock is stale. |
| Check mode looks clean, execution changes many hosts | Which module/settings and inventory differed? | Compare effective targets and check support; narrow and verify the real workflow. |
| All CI checks pass, production runs an older artifact | Which deployment completed and what digest is live? | Inspect release/environment/controller state separately from build status. |
| Canceled run left an incomplete migration | Is the operation repeatable and is the schema compatible? | Recover according to migration state and release policy, not automatic rerun. |

Practice explaining why plan exit2 is successful, why a saved-plan apply needs an upstream gate, and why a Jenkins per-job concurrency option cannot coordinate two different jobs. Then trace one fictional release from commit to running digest, listing every identity check. Good answers identify the scope of each control and what evidence remains missing.

Primary command and platform documentation was inspected on2026-10-01. Shell fragments were syntax checked; no provider planning, Ansible host execution or authenticated CI API calls were performed for this reference. Runtime examples and complete platform configurations are in the linked canonical chapters, with their own verification records.
