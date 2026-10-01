---
book: The Complete DevOps Engineering Book
volume: 8
volume_title: "Infrastructure as Code"
chapter: 76
title: "Testing and Policy for Infrastructure"
slug: testing-and-policy-for-infrastructure
status: complete
summary: ../../_ai/chapter-summaries/076-testing-and-policy-for-infrastructure.md
---

# Chapter 76 — Testing and Policy for Infrastructure

## Validation, plans, and integration checks

Summit's network pull request changes a subnet range. The HCL is valid, the formatter is satisfied, and the author says the change is small. The useful question is whether it preserves the service contract: can DispatchDesk continue accepting orders, can workers reach durable notification intent, and can the change be recovered within the agreed maintenance constraints? Infrastructure testing needs several layers because no single command answers all of those questions.

Formatting finds inconsistent source presentation. Static validation checks language and schema consistency. A plan reveals proposed resource operations for specific inputs and state. Policy evaluates whether those proposed operations satisfy explicit constraints. Integration checks exercise real provider and application behavior. A recovery rehearsal checks that the environment can be repaired after failure. Each layer exposes a different class of mistake; describe a passing check by its actual scope.

A test that confirms a variable is copied into a tag is useful only if that tag is a meaningful interface contract. A test that merely restates every line of implementation adds maintenance without much evidence. Focus on invariants: no unintended production deletion, an approved region, stable subnet identities, mandatory ownership tags, and an application capacity floor that fits the availability requirement. Tests should make a failure explain a violated promise.

Use [module boundaries](074-modules-and-infrastructure-boundaries.md) to decide which interface to test. A network module can test output shapes and allocation rules without pretending to test HTTP order correctness. An application integration test can verify a synthetic order but cannot establish that every infrastructure operation is safe. Keep the assertions where their evidence is strongest.

## A complete cloud-free contract test

Terraform's native test framework has a Terraform 1.6 feature baseline. The following isolated example uses a built-in data resource and a plan-only test, so it does not create cloud resources. Save this complete `main.tf` in a new empty directory:

```hcl
terraform {
  required_version = ">= 1.6, < 2.0"
}

variable "environment" {
  type    = string
  default = "staging"
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Use staging or production."
  }
}

variable "workers" {
  type    = number
  default = 2
  validation {
    condition     = var.workers >= 1 && floor(var.workers) == var.workers
    error_message = "workers must be a positive whole number."
  }
}

locals {
  required_workers = var.environment == "production" ? max(2, var.workers) : var.workers
}

resource "terraform_data" "contract" {
  input = {
    environment = var.environment
    workers     = local.required_workers
  }
}

output "desired_workers" {
  value = local.required_workers
}
```

The production minimum of two is a fictional scenario rule for this test, not a universal reliability prescription. In a real service it needs a reason: failure-domain placement, workload demand, rollout behavior, and database capacity. The test checks that the rule is encoded consistently. Save this complete `contract.tftest.hcl` beside `main.tf`:

```hcl
run "production_capacity_floor" {
  command = plan
  variables {
    environment = "production"
    workers     = 1
  }
  assert {
    condition     = output.desired_workers == 2
    error_message = "Production contract must retain at least two workers."
  }
}

run "staging_explicit_capacity" {
  command = plan
  variables {
    environment = "staging"
    workers     = 1
  }
  assert {
    condition     = output.desired_workers == 1
    error_message = "Staging must preserve its explicit one-worker setting."
  }
}

run "reject_zero_workers" {
  command = plan
  variables {
    workers = 0
  }
  expect_failures = [var.workers]
}
```

The first assertion catches a missing production floor. The second catches an overbroad implementation that forces staging to use production capacity. The third expects the input validation to reject zero; an expected validation failure is a successful test outcome only because the test names that specific failed constraint. None of these establishes that workers are running, distributed across zones, or processing notifications.

Run as an ordinary user in this directory on Ubuntu 24.04 LTS, Fedora 44, or RHEL 9, with an installed compatible Terraform binary:

```bash
terraform init -input=false
terraform fmt -check
terraform validate
terraform test
```

`init` prepares the root. `fmt -check` leaves files unchanged and reports formatting differences. `validate` checks consistency. `test` discovers the `.tftest.hcl` test file. Every run explicitly selects `command = plan`; native tests otherwise can default to apply and create real infrastructure. Inspect any unfamiliar test file before granting cloud credentials or running it. Plan-only tests can still contact providers in provider-backed configurations, so they are not a guarantee of offline operation. [Native test documentation](https://developer.hashicorp.com/terraform/language/tests) defines the framework and command behavior.

For failure practice, replace `max(2, var.workers)` with `var.workers`, run the test, and examine the first assertion's diagnostic. Restore the expression and rerun. The meaningful evidence is that a production invariant catches a plausible regression while staging remains independently tested. The authoring process has not executed Terraform; these are reader steps and expected outcomes.

## Policy gates and change review

A policy gate encodes a rule with an owner and an exception process. “No production deletes without explicit approval” is easier to audit than “be careful.” The gate should report the exact resource and action that triggered it. A policy that silently approves unrecognized plan structures is weaker than it looks; one that rejects every unfamiliar optional field can create noisy false alarms. Design the parser to recognize the schema it uses and fail clearly when required evidence is missing.

The following complete Python checker demonstrates a narrow deletion gate over Terraform plan JSON. Save it as `check_plan.py`. It is not a comprehensive security policy or replacement for human review:

```python
#!/usr/bin/env python3
import json
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("Usage: python3 check_plan.py PLAN_JSON")
try:
    plan = json.loads(Path(sys.argv[1]).read_text())
except (OSError, json.JSONDecodeError) as exc:
    raise SystemExit(f"Cannot read plan JSON: {exc}")
version = str(plan.get("format_version", ""))
if version.split(".")[0] != "1":
    raise SystemExit("Unsupported or absent Terraform plan JSON format version")
changes = plan.get("resource_changes", [])
if not isinstance(changes, list):
    raise SystemExit("resource_changes must be a list")
violations = []
for resource in changes:
    if not isinstance(resource, dict):
        raise SystemExit("Malformed resource change")
    change = resource.get("change")
    if not isinstance(change, dict):
        raise SystemExit("Missing change object")
    actions = change.get("actions")
    if not isinstance(actions, list) or not all(isinstance(x, str) for x in actions):
        raise SystemExit("Malformed actions")
    if "delete" in actions:
        violations.append(str(resource.get("address", "<missing address>")))
if violations:
    for address in violations:
        print(f"Deletion requires separate approval: {address}", file=sys.stderr)
    raise SystemExit(1)
print("Deletion gate passed; other risks still require review.")
```

Replacement can include both creation and deletion actions, so the checker searches the action list rather than comparing it to the single-element list `['delete']`. It does not inspect networking, unknown values, costs, credentials, or application data. It deliberately treats plan policy as a limited claim.

Generate a real saved plan using the workflow in [CLI foundations](072-terraform-and-opentofu-cli-foundations.md), then export and check it:

```bash
umask 077
terraform show -json reviewed.tfplan > reviewed.json
python3 check_plan.py reviewed.json
```

`show -json` emits a machine-readable representation. The file can contain sensitive values, so keep it in a restricted workspace and control artifact retention. `umask` affects newly created files in this shell; it does not repair an already public file's permissions. Python exits nonzero for a rejected plan so a pipeline can stop. [Show documentation](https://developer.hashicorp.com/terraform/cli/commands/show) and [JSON format reference](https://developer.hashicorp.com/terraform/internals/json-format) define the inspected fields.

## Checking an infrastructure pull request

The pull request should bind evidence to the source revision, selected inputs, dependency lock file, executable version, and target environment. A reviewer should be able to explain why a policy result applies to this plan. If a contributor changes source after approval, regenerate the evidence. If state changes after planning, a later executor may need a new plan and renewed review. An artifact name such as `reviewed.tfplan` is not proof that anybody reviewed it.

Run low-privilege static checks for untrusted contributions. Avoid granting production credentials merely so an external pull request can produce a convenient plan. Provider-backed planning can execute downloaded code and read remote data. [CI trust boundaries](../13-continuous-integration-platforms/121-ci-architecture-and-trust-boundaries.md) owns the detailed execution model; this chapter establishes the evidence contract those pipelines must preserve.

Integration tests require a disposable scope, unique resource naming, quota and cost estimates, timeout limits, and teardown evidence. A test framework attempting cleanup does not guarantee that cleanup succeeds. If a runner disappears, use tagged inventory to find leftovers. If an integration test creates databases, establish whether test data is synthetic and whether backups/logs also require retention or removal. Never run cloud integration tests automatically while authoring the manuscript.

A realistic failure is a plan JSON gate that passes because the input file is a state JSON export rather than a plan. The script above is intentionally limited and cannot prove origin solely from a version field. The pipeline must supply the saved plan artifact through a controlled path and bind it to the change record. For production, strengthen document-kind checks and schema validation. Policy engines need provenance of their input as well as logic over its contents.

Another failure is a tag policy that treats an unknown planned value as compliant. Unknown means not established yet, not “safe.” Decide whether to reject it, require an explicit review, or verify it after apply. Silent conversion of uncertainty into approval defeats the point of policy. Report uncertainties in language reviewers can act on.

## Exercises and answer guidance

1. Break the production-floor expression and explain which assertion should fail. The production run detects one worker; the staging test remains useful because it guards a different requirement.
2. Feed the Python gate a replacement action list containing create and delete. What should happen? It must reject because deletion is present even when creation is also present.
3. An integration run passes but teardown fails. Is the job complete? No. Preserve resource identifiers, determine remaining cost/data exposure, and assign cleanup recovery rather than discarding logs.

Review questions: What does validation prove? Why can plan-only testing still need provider access? What evidence binds policy to a source revision? How should unknown values affect approval?

Testing is strongest when assertions express operational promises, gates report precise violations, and execution evidence states its limits. A green pipeline is useful only when the team knows which risks it has checked.

## Sources and verification

Official Terraform tests, show, JSON format, and validate documentation was inspected 2026-10-01. The native test example requires Terraform 1.6 or newer; no mock-provider behavior is assumed. No Terraform test, cloud integration, or Python policy execution has yet been run during authoring. Syntax/link checks are recorded separately in the continuation summary when performed.
