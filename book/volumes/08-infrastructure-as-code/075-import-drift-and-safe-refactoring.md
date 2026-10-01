---
book: The Complete DevOps Engineering Book
volume: 8
volume_title: "Infrastructure as Code"
chapter: 75
title: "Import, Drift and Safe Refactoring"
slug: import-drift-and-safe-refactoring
status: complete
summary: ../../_ai/chapter-summaries/075-import-drift-and-safe-refactoring.md
---

# Chapter 75 — Import, Drift and Safe Refactoring

## Discovery and import workflows

Summit's DispatchDesk network began as a manually created VPC. The team now wants reviewed infrastructure changes, but replacing the network would disrupt database and application connectivity. Adoption must preserve the existing object while establishing a clear configuration and state owner. Import is the identity step of that adoption; it is not evidence that a new configuration accurately describes the existing environment.

First discover the object through provider inventory and audit records. Record the real account, region, resource identifier, CIDR, tags, DNS settings, attachments, routing, and consumers. Identify whether another root already manages it. One remote object should not be independently managed by two addresses in two states. Duplicate ownership can make apparently valid plans fight each other. Speak with the network owner before assigning lifecycle control to DispatchDesk's repository.

Discovery is a read-only phase. Prefer a narrow approved read role while compiling the inventory. Avoid attaching broad write permissions merely because import will eventually modify state. The later apply can update remote fields if configuration differs, so treat importing and applying as controlled changes, not innocuous metadata housekeeping. Back up the relevant state and freeze competing writers as described in [state operations](073-state-locking-and-remote-backends.md).

Here is a complete Terraform configuration for adopting one VPC. It uses import blocks, which require Terraform support for that feature, with Terraform 1.5 as the feature baseline. Replace the example CIDR and DNS values with observed values before planning. Select and constrain an approved AWS provider release before operational use; the source address below is not a tested version pin.

```hcl
terraform {
  required_version = ">= 1.5, < 2.0"
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

variable "region" {
  type        = string
  description = "Region containing the existing VPC."
}

variable "existing_vpc_id" {
  type        = string
  description = "Verified existing VPC identifier."
}

provider "aws" {
  region = var.region
}

import {
  to = aws_vpc.orders
  id = var.existing_vpc_id
}

resource "aws_vpc" "orders" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name        = "dispatchdesk-existing"
    Environment = "staging"
  }
}

output "vpc_id" {
  value = aws_vpc.orders.id
}
```

This declares adoption of the VPC only. It does not implicitly adopt subnets, gateways, route associations, or security rules. Each has its own resource identity and ownership decision. Provider documentation defines the supported import identifier for each resource type. Generated configuration can assist discovery, but it still needs review: a mechanically produced representation may include incidental defaults, unsupported combinations, or details inappropriate for a durable interface.

Run on an operator workstation as an ordinary user in the root module directory, with a verified short-lived AWS identity, read access for discovery, and the approved state/change permissions. Create `adoption.tfvars` containing the actual region and observed VPC identifier, then run:

```bash
terraform init -input=false
terraform validate
terraform plan -input=false -var-file=adoption.tfvars -out=adopt.tfplan
terraform show adopt.tfplan
```

`-var-file` supplies the declared inputs. The saved plan should identify the import and any proposed remote updates. For an initial adoption intended to preserve behavior, resolve unexpected changes in source before applying. A tag update can be harmless operationally but still affect inventory, automation, or billing allocation; make it an explicit decision rather than silently accepting every difference.

Only an authorized reader applies `terraform apply -input=false adopt.tfplan`. Then inspect `terraform state show aws_vpc.orders`, check the output, and plan again with the same variable file. `state show` renders the tracked object at the address. A subsequent no-change plan supports successful adoption of the configured attributes, but does not prove all attachments or external consumers are understood. No import or cloud operation is executed during authoring.

## Address changes and replacement risk

A resource address belongs to the configuration structure. Changing it is often a source refactor; changing a CIDR or another immutable property can be an actual infrastructure replacement. The plan must distinguish those two intentions. Without explicit address-history information, deleting one address and adding another can look like deleting one object and creating a different object.

The following cloud-free lab teaches a rename without risking a real network. Use a new empty directory and the Terraform executable supporting `terraform_data`. Save this initial `main.tf`:

```hcl
terraform {
  required_version = ">= 1.4, < 2.0"
}

resource "terraform_data" "old_contract" {
  input = {
    service = "dispatchdesk"
    owner   = "Summit"
  }
}

output "contract" {
  value = terraform_data.old_contract.output
}
```

Initialize, plan, inspect, and apply using [CLI foundations](072-terraform-and-opentofu-cli-foundations.md). This records one local built-in data object. Record its address with `terraform state list`. Then replace the whole file with:

```hcl
terraform {
  required_version = ">= 1.4, < 2.0"
}

moved {
  from = terraform_data.old_contract
  to   = terraform_data.service_contract
}

resource "terraform_data" "service_contract" {
  input = {
    service = "dispatchdesk"
    owner   = "Summit"
  }
}

output "contract" {
  value = terraform_data.service_contract.output
}
```

The `moved` block documents the address transition. Produce `terraform plan -input=false -out=rename.tfplan` and inspect it with `terraform show rename.tfplan`. Expect the address move without a create/destroy operation for this unchanged input. Apply the reviewed artifact and run `terraform state list`; the new address should replace the old one. These are expected observations, not recorded execution output.

Keep move history long enough for every consumer to upgrade through it. Removing a move because the author's environment already migrated can break another environment still on the old address. A distributed module's history is part of its upgrade contract. When an input map key changes, the same principle applies to the indexed address: quote string keys correctly and describe the intended move rather than renaming them casually.

To clean up the disposable lab, review `terraform plan -destroy -input=false -out=remove.tfplan`, then apply that artifact. This removes only the data object tracked by that lab's state. Do not run destruction in the imported production root; adoption examples have no implied permission to delete the adopted network.

## Drift is evidence before it is a fix

At 03:00, an incident responder changes a security rule to restore order processing. At 09:00, a scheduled plan detects a difference. Calling the difference “drift” describes a relationship between intent and observation; it does not decide whether to revert it. Determine who made the change, why it was necessary, whether it is safe, and which state should become authoritative.

A normal plan can propose restoring declared values. A refresh-only plan focuses on updating the tool's record of remote changes and outputs instead of proposing configuration-driven remote changes. For a documented inspection, run `terraform plan -refresh-only -input=false -var-file=adoption.tfvars` in the correct root. It is still dependent on provider access and current observations. Applying a refresh-only plan does not rewrite the configuration to adopt every remote change; the next ordinary plan may still propose a correction.

Use drift detection as an owned queue. A daily automated job can report unexpected changes, but somebody must distinguish authorized emergency edits, controller-managed fields, provider defaults, and unauthorized activity. A report nobody reviews is not a control. An automatic repair loop can undo a mitigation while the incident is still active. Choose auto-correction only for changes whose desired ownership and recovery consequences are clear.

## Adopting existing infrastructure safely

The hardest adoption failure is the wrong environment. An engineer uses a staging variable file but a production backend, or selects the correct region with the wrong account identity. A VPC identifier alone is not an adequate human review context. Put account, region, root, backend key, and resource identifier in the change record; verify the execution identity before planning. [AWS CLI sessions](../09-aws-foundations/082-aws-cli-and-identity-sessions.md) owns the concrete identity check.

If the plan proposes replacing the VPC, stop before apply. Compare the observed CIDR and resource arguments with configuration. Determine whether the proposal comes from an actual immutable-property difference or an address mismatch. Correcting a source typo can eliminate the replacement; a deliberate network migration needs a separate staged design with consumer movement and rollback constraints. Do not silence the risk with a blanket ignore rule merely to get a clean plan.

If import fails because the identifier is invalid, verify account/region and the resource type's documented import format. If it succeeds but the next plan changes fields, inspect source defaults and provider representation. If an interrupted operation leaves uncertain state, preserve logs and use the state recovery procedure rather than importing the same object into a second address. Recovery must preserve the one-object/one-owner relationship.

There are costs even when the import itself is bookkeeping. Proposed changes can create replacement resources, and discovery can use metered APIs or logging/storage around the workflow. Estimate costs for the planned remote operations using current provider pricing. Teardown is not an adoption requirement: the desired successful outcome is the existing object continuing to serve its consumers under reviewed ownership.

Ubuntu and Fedora/RHEL execute the same HCL/CLI flow without sudo. Their package installation, credentials-file permissions, trust stores, and proxy configuration can differ. A denied file read on the workstation and an AWS AccessDenied response are different layers; investigate the actual diagnostic before expanding privileges. RHEL entitlement does not grant AWS permissions, and running the CLI as root does not make a cloud policy allow the operation.

## Exercises and answer guidance

1. Remove the moved block before planning the lab rename. What risk should the plan reveal? The old address appears removed and the new address appears new; compare this with the intentional move and restore the block before applying.
2. A manually created subnet belongs to a shared database team. Can DispatchDesk import it solely because its API can discover it? No. Discovery visibility is not lifecycle authority; resolve ownership and consumers first.
3. A refresh-only apply succeeds after an emergency tag edit. Is the source now updated? No. The state record and outputs can reflect observations while source still declares the old value. Decide whether to adopt the edit in code or restore the declared value through a reviewed normal plan.

Review questions: What does import establish? Why can a no-change plan still leave unknown consumers? How do address moves differ from replacement? Who decides how an emergency change is incorporated?

Safe adoption preserves identity and service behavior while making ownership explicit. Safe refactoring tells the tool that an address changed. Safe drift handling interprets evidence before choosing correction.

## Sources and verification

Official [Terraform import overview](https://developer.hashicorp.com/terraform/language/import), [module refactoring](https://developer.hashicorp.com/terraform/language/modules/develop/refactoring), and [plan reference](https://developer.hashicorp.com/terraform/cli/commands/plan) were inspected 2026-10-01. Import blocks use the Terraform 1.5 feature baseline; the local data lab uses 1.4-or-newer functionality. AWS VPC identifier import was checked in the official provider source documentation referenced in Chapter 074. Terraform/OpenTofu are unavailable on the authoring PATH, so no import, rename, drift, provider, or cloud integration ran.
