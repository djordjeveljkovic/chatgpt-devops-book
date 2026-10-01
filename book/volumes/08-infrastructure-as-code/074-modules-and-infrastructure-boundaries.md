---
book: The Complete DevOps Engineering Book
volume: 8
volume_title: "Infrastructure as Code"
chapter: 74
title: "Modules and Infrastructure Boundaries"
slug: modules-and-infrastructure-boundaries
status: complete
summary: ../../_ai/chapter-summaries/074-modules-and-infrastructure-boundaries.md
---

# Chapter 74 — Modules and Infrastructure Boundaries

## Inputs, outputs, and composition

A module is an infrastructure interface. Its caller chooses inputs, its implementation manages resources, and its outputs publish results that other components can consume. The useful abstraction is a meaningful contract, such as “a network with named application subnets,” rather than a wrapper around every argument of one resource. DispatchDesk's Summit team wants to reuse its staging network pattern in production without making production a copy of staging's operational mistakes.

The distinction between a module and a state boundary matters. A child module inside one root is still managed by that root's operation and state. Moving code into `modules/network` does not create a separate approval scope, lock, credential boundary, or independent recovery procedure. A separate root with its own backend can create those operational boundaries, but introduces coordination when the application needs network outputs. Read [state and remote backends](073-state-locking-and-remote-backends.md) before choosing the split.

Design inputs around decisions the caller is qualified to make. A CIDR range belongs to network allocation policy; an environment label belongs to deployment context; a subnet map can express stable names and placements. Exposing an option to disable every protection makes the interface flexible at the expense of its guarantees. A module should document what it guarantees, what its caller must supply, and what it deliberately leaves to another layer.

Outputs are an API. If a consumer needs a VPC identifier and a map of subnet identifiers, publish those values with descriptions. Do not publish the complete internal resource object merely because it is convenient today: consumers may depend on attributes that the module author intended to change. Renaming an output or changing its shape is a compatibility change. [Terraform outputs](https://developer.hashicorp.com/terraform/language/values/outputs) describes the interface mechanism; compatibility is an engineering responsibility.

Composition connects explicit outputs to inputs. A compute module receiving `module.network.subnet_ids["app_a"]` tells the reviewer which network relationship matters. A module that searches for a network by a mutable tag can hide coupling and produce surprising results if two networks share the tag. Discovery is sometimes necessary for existing infrastructure, but a direct reference within an owned composition is usually easier to inspect.

## Environment and ownership boundaries

Summit's staging environment can tolerate removal during experimentation. Production's network supports an order API, workers, database connections, and possibly services owned by another team. Reusing code should not make their lifecycle identical. Use separate environment roots or another clearly documented isolation mechanism so the execution identity, backend, variables, and review policy are explicit. A directory name alone does not establish account or state isolation.

Harbor, the VPS company, may need only a small module that creates a host and DNS record, with host configuration handled elsewhere. Atlas, the platform company, may separate cluster networking from workload namespaces because different teams own them. These are alternative organizational arrangements, not a progression toward more modules. The goal is to keep an operational change's blast radius understandable to its reviewer and on-call owner.

A network module should not also deploy DispatchDesk's application, migrate its database, create CI runners, and rotate every secret. Those activities have different lifecycles and permissions. Bundling them makes a network change unexpectedly require application credentials and makes application teardown threaten shared infrastructure. Conversely, splitting the network into dozens of one-resource modules makes it difficult to establish an overall invariant. Choose a boundary that matches the thing an owner promises to maintain.

## Designing a reusable network module

The following complete small module creates an IPv4 VPC and a caller-supplied map of subnets. It is intentionally not a complete internet-facing architecture: it declares no internet gateway, NAT gateway, custom route table, endpoint, security group rule, or application. The owning [VPC chapter](../09-aws-foundations/084-vpc-subnets-and-routes.md) explains those routing decisions. A subnet name containing “private” does not itself enforce a network security policy.

Prepare a disposable directory with `main.tf` at its root and `modules/network/main.tf` below it. The child file is:

```hcl
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

variable "name" {
  type        = string
  description = "Stable network name used in resource tags."
}

variable "cidr" {
  type        = string
  description = "Approved IPv4 VPC range."
  validation {
    condition     = can(cidrnetmask(var.cidr))
    error_message = "cidr must be a valid IPv4 CIDR range."
  }
}

variable "subnets" {
  type = map(object({
    cidr = string
    zone = string
  }))
  description = "Stable subnet keys with approved CIDRs and availability zones."
}

variable "tags" {
  type        = map(string)
  description = "Ownership and environment tags."
  default     = {}
}

resource "aws_vpc" "this" {
  cidr_block           = var.cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = merge(var.tags, { Name = var.name })
}

resource "aws_subnet" "this" {
  for_each                = var.subnets
  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.zone
  map_public_ip_on_launch = false
  tags                    = merge(var.tags, { Name = "${var.name}-${each.key}" })
}

output "vpc_id" {
  value       = aws_vpc.this.id
  description = "Identifier of the module-managed VPC."
}

output "subnet_ids" {
  value       = { for name, subnet in aws_subnet.this : name => subnet.id }
  description = "Subnet identifiers indexed by caller-owned stable names."
}
```

`for_each` uses the caller's keys as stable identities. Adding `app_b` adds another subnet without changing the address of `app_a`. Removing or renaming a key can remove or replace its associated resource unless the change includes a deliberate move. A list indexed by position is often a weaker interface when names are the natural identity. The VPC reference gives the subnet an inferred dependency. `merge` combines caller tags with the module's generated Name tag; in this order, the generated Name wins on a collision.

The CIDR validation establishes syntactic IPv4 validity only. It does not prove AWS accepts the range, that subnets fall inside it, that they do not overlap, or that the range will not collide with future peering. A module's validation should not be described as stronger than it is. Production allocation needs network policy and tests. The module's `map_public_ip_on_launch = false` expresses one launch default, not a complete proof of isolation.

The root `main.tf` is:

```hcl
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

variable "region" {
  type        = string
  description = "Approved AWS region for the disposable lab."
}

variable "zone" {
  type        = string
  description = "An available zone in that region."
}

provider "aws" {
  region = var.region
}

module "network" {
  source = "./modules/network"
  name   = "dispatchdesk-lab"
  cidr   = "10.42.0.0/16"
  subnets = {
    app_a = { cidr = "10.42.10.0/24", zone = var.zone }
  }
  tags = {
    Project     = "DispatchDesk"
    Environment = "lab"
    Owner       = "training"
  }
}

output "network" {
  value = {
    vpc_id     = module.network.vpc_id
    subnet_ids = module.network.subnet_ids
  }
}
```

The module source is local and relative, so the repository supplies its implementation. Provider requirements name the provider; root provider configuration supplies the region and the execution environment supplies credentials. These examples intentionally do not invent a provider version. Before a real apply, select an approved provider release, review its documentation, add a tested version constraint, and commit the resulting dependency lock file. An unconstrained instructional configuration is not a production dependency policy.

## Review, verification, and teardown

No cloud commands are executed while authoring. Reader execution requires an authorized disposable account, a verified short-lived identity, permissions to manage and describe the named network resources, a selected region, and a zone actually available there. Estimate costs for any extensions using current AWS pricing; adding NAT, endpoints, public addresses, compute, or logs can introduce charges. Never assume this small configuration's absence of compute makes every surrounding account operation free.

On the operator workstation, as an ordinary user in the root directory, create `lab.tfvars` with real approved region and zone values. For example, the following is illustrative and must be checked against the account's availability:

```hcl
region = "eu-central-1"
zone   = "eu-central-1a"
```

Then perform the review sequence:

```bash
terraform init -input=false
terraform fmt -recursive
terraform validate
terraform plan -input=false -var-file=lab.tfvars -out=network.tfplan
terraform show network.tfplan
```

`fmt -recursive` formats the root and descendant module directories. Review the resulting source diff. The plan artifact should include one VPC and one subnet, with no gateway, compute, or database additions. Initialization can download provider code and planning can contact AWS; both need the documented environment. A successful validation is only a structural check.

An authorized reader can apply the reviewed plan and inspect the output with `terraform apply -input=false network.tfplan` followed by `terraform output -json network`. Record the real identifiers, verify the tags and subnet placement in provider inventory, and verify that the planned resource count matches actual ownership. Ubuntu and Fedora/RHEL use the same unprivileged CLI procedure; system package installation and certificate/proxy setup remain platform-specific prerequisites.

For cleanup, create and inspect `terraform plan -destroy -input=false -var-file=lab.tfvars -out=remove.tfplan`, then apply that saved plan. This is destructive and must run only against the disposable root's state. If deletion fails, inspect attached interfaces and other consumers before retrying. Do not delete an interface owned by another service merely to make a teardown finish. A module's intended boundary does not prevent external resources from acquiring dependencies on it.

## Failure and compatibility reasoning

A subnet creation fails because the supplied zone is not in the selected region. The VPC may already exist. Diagnose the failed resource and actual remote inventory, correct the zone input, and create a new plan using the existing state. Do not recreate the entire root or discard state. The failure demonstrates that input type correctness is weaker than provider-domain correctness.

Another failure appears after a module author changes `subnet_ids` from a map to a list. A consumer selecting `subnet_ids["app_a"]` can no longer resolve its input. Treat the output change as an interface break. Either retain compatibility during migration, add a new output, or update all consumers through a reviewed coordinated change. Document release behavior before distributing the module through a registry or Git source.

For remote modules, use a documented immutable revision or reviewed registry version rather than a moving branch for production. The module `version` argument applies to registry modules, while source-specific revision selection has its own syntax. [Module block reference](https://developer.hashicorp.com/terraform/language/block/module) describes those forms. Do not assume that a provider lock file freezes every module source; record module revisions explicitly. [Module composition guidance](https://developer.hashicorp.com/terraform/language/modules/develop/composition) supports keeping composition relationships clear.

## Exercises and answer guidance

1. Add an `app_b` map entry. What should remain stable? The `app_a` resource address should remain unchanged; the plan should add the new key's subnet. Inspect replacements rather than relying on the source diff alone.
2. Rename `app_a` to `orders_a`. Why is that more than editing a label? The map key participates in resource identity. Use a deliberate state move/refactor when preserving the same object is intended.
3. Should the network module include order database migrations? Explain. They have separate credentials, failure modes, and release lifecycles; compose their workflows at an appropriate orchestration boundary.

Review questions: Does a child module create a state boundary? Which inputs represent real caller decisions? Why are outputs compatibility commitments? What does the CIDR rule prove and what does it leave unproved?

A useful module preserves a small, explicit contract and hides incidental implementation without hiding operational consequences. Reuse is successful when ownership, upgrade behavior, and recovery remain understandable.

## Sources and verification

Terraform module block, composition, and output documentation was inspected 2026-10-01. AWS provider [VPC source documentation](https://raw.githubusercontent.com/hashicorp/terraform-provider-aws/main/website/docs/r/vpc.html.markdown) and [subnet source documentation](https://raw.githubusercontent.com/hashicorp/terraform-provider-aws/main/website/docs/r/subnet.html.markdown) were inspected because the registry rendering required JavaScript. Those moving-source pages establish inspected argument names, not a tested provider pin. No provider, HCL runtime, account, network, or teardown was executed.
