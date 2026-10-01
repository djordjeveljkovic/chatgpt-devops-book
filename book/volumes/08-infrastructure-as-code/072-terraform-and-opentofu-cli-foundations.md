---
book: The Complete DevOps Engineering Book
volume: 8
volume_title: "Infrastructure as Code"
chapter: 72
title: "Terraform and OpenTofu CLI Foundations"
slug: terraform-and-opentofu-cli-foundations
status: complete
summary: ../../_ai/chapter-summaries/072-terraform-and-opentofu-cli-foundations.md
---

# Chapter 72 — Terraform and OpenTofu CLI Foundations

## Providers, resources, and variables

Before learning a cloud provider, learn the CLI workflow in a directory that has no credentials and creates no cloud resources. DispatchDesk's infrastructure repository needs a reliable contract between author, reviewer, and executor. A change must identify its inputs, produce an inspectable plan, and apply the reviewed operation. This chapter builds that contract with a built-in data resource, then explains where real provider configuration adds risk.

Terraform and OpenTofu are separate projects with similar language and commands. Select one tool for a given working directory and state lifecycle. Do not alternate executables casually to prove that an example works: compatibility depends on the features and versions involved. Record the chosen executable and version with the change. Follow each project's official installation instructions for the target system; Ubuntu's APT repositories, Fedora's DNF repositories, and entitled RHEL repositories are different distribution mechanisms. An arbitrary package with a familiar name is not evidence that it is the intended upstream binary.

The commands below use `terraform`; an OpenTofu reader can use `tofu` after checking the referenced official command documentation. This example requires support for the built-in `terraform_data` resource. It does not install a third-party provider, make an API request, or deploy DispatchDesk. It records a simple desired service contract in local state. The Terraform language constraint expresses the feature baseline rather than claiming a current release:

```hcl
terraform {
  required_version = ">= 1.4, < 2.0"
}

variable "environment" {
  type        = string
  description = "DispatchDesk deployment environment."
  default     = "staging"
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be staging or production."
  }
}

variable "minimum_workers" {
  type        = number
  description = "Desired minimum notification worker count."
  default     = 2
  validation {
    condition     = var.minimum_workers >= 1 && floor(var.minimum_workers) == var.minimum_workers
    error_message = "minimum_workers must be a positive whole number."
  }
}

resource "terraform_data" "service_contract" {
  input = {
    service         = "dispatchdesk"
    environment     = var.environment
    minimum_workers = var.minimum_workers
  }
}

output "service_contract" {
  value = terraform_data.service_contract.output
}
```

Save this complete file as `main.tf` in a new empty directory. A root module consists of configuration files in that directory; file names organize the source rather than establish execution order. The resource address is `terraform_data.service_contract`: a type plus a local name. Its `input` is a structured object, and the output exposes the resource's stored result. The reference in the output expresses a dependency. See [declarative infrastructure](071-declarative-infrastructure-and-reconciliation.md) for the graph model.

A cloud provider would add a source address, version constraint, authentication behavior, and resource-specific schema. Variables are typed input parameters; they are not an excuse to hide every architectural decision. Giving an operator a variable for every security boundary produces a configurable system that may be hard to reason about. Expose values that callers legitimately choose and encode invariants with validation and module design. Never place cloud access keys in a variable file committed to Git.

## Initialize, validate, plan, and apply

Run as an ordinary user on Ubuntu, Fedora, or RHEL in the directory containing `main.tf`. No sudo is required. The CLI must already be installed; these commands do not install it. First record which binary is on the path:

```bash
terraform version
terraform init -input=false
terraform fmt -check
terraform validate
terraform plan -input=false -out=reviewed.tfplan
terraform show reviewed.tfplan
```

`version` identifies the executable's reported version. `init` prepares the working directory; in real configurations it initializes the backend and installs required providers and modules. `-input=false` forbids interactive questions, so missing required input becomes an error that automation can diagnose. A plain `init` is not an instruction to select newer dependencies. Treat dependency upgrades as their own reviewed change.

`fmt -check` checks canonical formatting without rewriting the source. If it fails because the pasted file needs formatting, run `terraform fmt`, inspect the diff, and repeat the check. `validate` checks configuration consistency; it does not prove that a remote account has permission or sufficient capacity. `plan` compares configuration and observed state and saves an execution plan using `-out`. The filename is a local binary artifact, not human-readable JSON. `show` renders it for review. Do not edit the plan file or commit it as ordinary source code.

The expected plan for a fresh directory includes creation of the data resource. No cloud instance should appear. If the plan mentions remote resources, stop: the directory contains additional configuration or is connected to state outside this lab. This is why an empty directory and an explicit execution context are part of the exercise.

Apply only after reviewing the resource address and values:

```bash
terraform apply -input=false reviewed.tfplan
terraform output -json service_contract
terraform plan -input=false
```

Applying a saved plan executes that plan; it does not present the same interactive approval prompt as applying without a saved plan. Approval therefore belongs before this command. The local example changes state only, but the identical command shape can create billable cloud resources in another directory. `output -json` renders the named output in machine-readable form. Confirm the service name, environment, and worker count. The final plan should propose no changes when the configuration and recorded data match. These are expected outcomes, not measured output from authoring.

For a real DispatchDesk service, a clean plan is one verification layer. Additional evidence includes provider inventory, network reachability, application health, and a synthetic order. The data resource cannot validate these; its purpose is teaching the execution contract without relying on an account or a cloud bill.

## A reviewed infrastructure change

Create `staging.tfvars` in the same directory:

```hcl
environment     = "staging"
minimum_workers = 4
```

An explicitly selected variable file keeps this change's input clear. Unlike automatically loaded variable filenames, an arbitrary file named `staging.tfvars` is supplied through the command option:

```bash
terraform plan -input=false -var-file=staging.tfvars -out=scale.tfplan
terraform show scale.tfplan
terraform apply -input=false scale.tfplan
terraform output -json service_contract
```

`-var-file` assigns the two declared variables. The plan should show the contract's input changing from two workers to four. The output provides evidence that the stored contract changed. It does not scale a process, because no real compute resource is declared. In a provider-backed implementation, the team would map this reviewed input to a supported capacity argument and examine whether its modification updates an object or replaces it.

The reviewer needs source revision, executable version, dependency selections, target environment, and plan evidence. A saved plan should be considered sensitive because plans can contain data that configuration labels as sensitive. Store it with restricted access and short retention. Do not paste a complete machine-readable plan into a public issue merely because the terminal rendering concealed a secret. [State and locking](073-state-locking-and-remote-backends.md) explains the underlying storage responsibilities.

There is a useful separation between formatting, validity, intention, and outcome. Formatting reduces noisy diffs. Validation catches structural errors. Planning reveals proposed operations. Application changes state and remote objects. Operational verification establishes that the service works. Treating one as a substitute for another leaves a predictable blind spot.

## Diagnosing failed assumptions

Set `minimum_workers = 0` and plan again. The validation rule should reject the input. Fix the variable file and generate a new plan; do not reuse a plan from before the correction as if it represented the new source. This failure belongs to input constraints, so looking at cloud networking would waste time.

Another failure is a stale saved plan after another operator changes state. Do not force an old artifact through by disabling locking or manipulating state. Read the diagnostic, identify the intervening operation, and regenerate a plan from the current source and state. Have the revised plan reviewed because the facts have changed. Locking prevents certain concurrent mutations; it does not make every review artifact timeless.

If initialization fails while installing a provider, distinguish DNS, proxy, registry access, checksum verification, and unsupported platform errors. A failed download is not evidence that the HCL is invalid. Preserve the provider source address and selected version in the incident record. Avoid blindly adding `-upgrade`: that can change dependencies and create a second problem while investigating the first. An organization with restricted networking can establish a documented provider mirror, but the mirror must preserve authenticity and reproducibility.

For Ubuntu and Fedora/RHEL, the HCL and these unprivileged CLI commands are identical. Differences arise in installation, certificate stores, proxy settings, filesystem permissions, and mandatory access control when automation runs as a service. Diagnose the actual layer. Running everything with sudo can create root-owned state or cache files and conceal a user-environment problem, leaving the next ordinary run broken.

## Cleanup and operational limits

The lab has no application data. Review a destruction plan before removing its managed state entry:

```bash
terraform plan -destroy -input=false -var-file=staging.tfvars -out=remove.tfplan
terraform show remove.tfplan
terraform apply -input=false remove.tfplan
terraform state list
```

`-destroy` selects a plan whose goal is removal of managed resources. It is destructive in a real infrastructure directory. Here it removes the built-in data object from state. The last command should list no managed resource addresses. Keep the source if you want to repeat the lab. Local state and plan artifacts may remain in the directory; secure or delete them according to their content. Do not use a broad recursive cleanup command as a substitute for understanding what is being removed.

A CLI is an executor, not a change-governance system. Branch permissions, reviewer authority, credential lifetime, audit evidence, and environment concurrency belong to the surrounding workflow. Later chapters show [CI trust boundaries](../13-continuous-integration-platforms/121-ci-architecture-and-trust-boundaries.md) and platform implementations. Master the bounded local sequence first so an automated pipeline does not turn an unexplained failure into an unexplained deployment.

## Exercises and answer guidance

1. Supply `environment = "demo"` in a variable file. Explain where the failure should occur. Input validation rejects the value before a valid execution plan can be produced; restore a permitted environment.
2. Explain why `validate` can pass while a provider-backed apply fails. The configuration can be structurally valid while remote credentials, limits, service constraints, or concurrent changes prevent execution.
3. A colleague edits source after you review `scale.tfplan`. What does applying that saved plan mean? It applies the previously planned operations, subject to validity checks; it does not silently become a newly reviewed plan of the edited source. Regenerate and review when the intended change has changed.

Review questions: What does initialization prepare? Why should provider upgrades be reviewed separately? What is the difference between a root-module variable and a resource attribute? What evidence proves the lab contract changed, and what evidence would prove an order service works?

The key habits are selecting a known executable, making inputs explicit, inspecting a saved plan, applying the reviewed artifact, and checking the outcome at the layer the resource actually manages.

## Sources and verification

Official sources inspected 2026-10-01: [OpenTofu init](https://opentofu.org/docs/cli/commands/init/), [OpenTofu plan](https://opentofu.org/docs/cli/commands/plan/), [Terraform built-in data resource](https://developer.hashicorp.com/terraform/language/resources/terraform-data), and [Terraform apply](https://developer.hashicorp.com/terraform/cli/commands/apply). The example uses a Terraform 1.4-or-newer feature baseline without claiming a current release. Neither `terraform` nor `tofu` was available on the authoring PATH; commands and HCL were reviewed against documentation but not executed. No cloud integrations were run.
