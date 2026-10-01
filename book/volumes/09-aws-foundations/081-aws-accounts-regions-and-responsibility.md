---
book: The Complete DevOps Engineering Book
volume: 9
volume_title: "AWS Foundations"
chapter: 81
title: "AWS Accounts, Regions and Responsibility"
slug: aws-accounts-regions-and-responsibility
status: complete
summary: ../../_ai/chapter-summaries/081-aws-accounts-regions-and-responsibility.md
---

# Chapter 81 — AWS Accounts, Regions and Responsibility

## Accounts, organizations, and environments

Summit chooses AWS because managed databases, queues, and container execution fit its team's operating constraints. That choice begins with ownership and account access, before any instance or cluster. An AWS account is an important boundary for resource ownership, permissions, quotas, and billing. A local directory called staging does not establish an account boundary, and a console showing familiar resource names does not prove that the operator selected the intended account.

The prerequisite is [infrastructure lifecycle and recovery](../08-infrastructure-as-code/080-infrastructure-lifecycle-and-disaster-recovery.md). This chapter designs an account layout and a review artifact without creating accounts or resources. The next chapter supplies [concrete CLI identity sessions](082-aws-cli-and-identity-sessions.md). No cloud signup, paid service, or administrative mutation is performed while writing.

Separate the business owner of an account from the engineer currently operating it. The business needs durable control of contact details, payment arrangements, recovery channels, and privileged access. An employee's personal email address and phone should not be the only recovery route for production. Record a custodian and a succession procedure so ownership survives staffing changes.

The root identity has special account authority. Protect it with the documented authentication and recovery practices, avoid routine root use, and do not create root access keys for ordinary automation. Some organizational account-management arrangements support centralized root-access management; verify the selected arrangement rather than assuming every member account follows the same local login model. [AWS root-user guidance](https://docs.aws.amazon.com/IAM/latest/UserGuide/root-user-best-practices.html) is the authoritative source for current practices.

An organization can group accounts under common governance and consolidated arrangements. That does not make every account safe by default. Decide which accounts host workloads, where audit evidence is retained, who administers identity, and who can change organization policy. Service control policies and account permissions are different controls; the [IAM chapter](083-iam-policies-and-least-privilege.md) explains permission evaluation. An organizational boundary can constrain access while a workload role still needs its own specific grants.

For Summit's fictional learning layout, use separate sandbox and production workload accounts when the team can administer them responsibly. Sandbox permits disposable experiments with a deliberately bounded role. Production permits reviewed changes through a release identity. A separately governed security/logging arrangement can retain evidence beyond a workload operator's deletion scope. The exact number of accounts should follow ownership and failure isolation, not an arbitrary maturity checklist.

A single learning account is also possible if its limitations are explicit: experimentation shares quota, billing, and administrative scope with other resources. Never run a book lab in an employer's production account merely because you can authenticate there. Account authorization and the ability to execute an API call are different facts. The reader needs an approved disposable scope and a cleanup owner for later chapters.

## Regions, zones, and service boundaries

A region is a geographic service scope. Availability Zones provide infrastructure separation inside a region for services that support them. Resources and APIs have different scopes: some are regional, some zonal, and some use global or service-specific arrangements. A resource identifier, region, and account context together help the engineer find the actual object. Do not assume every resource appears when changing one console region selector.

Select a region by customer latency, required services/features, data policy, recovery design, operational familiarity, and current pricing. Availability of a service does not guarantee availability of every instance type, engine version, or feature. Verify the actual combination before designing around it. [AWS service endpoint reference](https://docs.aws.amazon.com/general/latest/gr/rande.html) records service endpoint and region information; service-specific documentation supplies deeper constraints.

The zone name an account sees can have account-specific mapping. When coordinating across accounts, use the documented stable zone identifiers where the service requires consistent physical placement. Do not assume that a suffix such as `a` names the same physical zone for all participants. [VPC and routing](084-vpc-subnets-and-routes.md) applies placement to subnet design.

Multi-zone deployment addresses selected local infrastructure failures. It does not protect against a common faulty release, compromised organization administrator, or a region-wide dependency. A multi-region design adds data, traffic, identity, and cost complexity. Start with a named failure scenario and acceptance evidence. [Reliability and risk](../01-engineering-mental-models/004-reliability-and-risk.md) owns the general failure-domain explanation.

A region selection in a CLI profile is a default, not a complete safety guard. A command can override it, a different profile can be selected, and service behavior can have a different scope. Put explicit account and region verification in operations. Treat a “resource not found” diagnostic as a possible context mismatch before concluding that data disappeared.

## Shared responsibility as an operating map

Managed services change the boundary of work. On EC2, Summit maintains guest operating-system and application configuration. With an abstracted storage service, the team primarily manages data, permissions, and service configuration rather than patching the underlying host. The exact responsibilities depend on the chosen service. AWS's [shared responsibility model](https://aws.amazon.com/compliance/shared-responsibility-model/) describes this distinction.

Translate that model into DispatchDesk decisions rather than reciting a slogan. Who approves database backup retention? Who verifies an order restore? Who restricts public access? Who rotates the application credential? Who decides whether notification delay is acceptable? Provider-operated hardware does not answer these product questions. The team still owns evidence that the assembled service fulfills its contract.

For Ubuntu 24.04, Fedora 44, or RHEL 9 EC2 guests, OS support, repository policy, security controls, and patching remain explicit choices. A RHEL image can involve entitlement or provider-specific subscription arrangements; inspect that image's terms. Fedora's shorter release lifecycle is a distinct maintenance consideration, not the same path as RHEL. An ECS/Fargate workload changes the host-maintenance boundary but leaves application dependencies and image updates with the team.

## A usable account layout

Write the account contract before creating resources. Save this complete fictional planning record as `account-layout.json` locally. It uses labels rather than invented actual account identifiers:

```json
{
  "project": "DispatchDesk",
  "company": "Summit",
  "accounts": [
    {
      "label": "sandbox",
      "purpose": "authorized disposable learning workloads",
      "operator_role": "sandbox-operator",
      "allowed_regions": ["eu-central-1"],
      "cleanup_owner": "Summit training owner",
      "production_data_allowed": false
    },
    {
      "label": "production",
      "purpose": "reviewed customer-serving workloads",
      "operator_role": "production-release",
      "allowed_regions": ["eu-central-1"],
      "cleanup_owner": "Summit service owner",
      "production_data_allowed": true
    }
  ],
  "root_custodian": "Summit account governance owner",
  "billing_owner": "Summit finance and service owner",
  "recovery_record": "controlled location independent of workload hosts"
}
```

This is a design document, not an AWS policy or provisioning configuration. Role names do not create roles; allowed region arrays do not enforce region restrictions. The artifact makes intended responsibility reviewable. The production label is not approval to deploy real customer data. Real organizational contacts and account IDs belong in the controlled inventory when accounts are established.

Run a local syntax check as an ordinary user in the directory containing that file:

```bash
python3 -m json.tool account-layout.json
```

`-m json.tool` loads Python's JSON formatting/checking utility, prints the parsed document, and fails for invalid JSON. It requires Python 3 and no cloud credentials. The document contains no secrets. This proves syntax only, not actual account layout or authorization. The command is the same on the stated Linux families; installing Python and supported packages is a platform-specific prerequisite.

Review the artifact with the account custodian, service owner, and billing owner. Confirm how an operator obtains each role, how environment identity is verified, which regions and data are permitted, where audit evidence is retained, and how forgotten resources are found. Add a cost estimate and lab expiry before provisioning anything. Budget alerts help detect spending; they should not be described as a guaranteed hard stop on every charge. [Budgets and inventory](090-aws-budgets-tags-and-inventory.md) develops that evidence.

Cleanup of this paper exercise removes only `account-layout.json` if it was created solely for the disposable exercise. It creates no AWS resources to tear down. Later labs need resource-specific teardown because account closure is not a substitute for understanding running services, retained data, and billing obligations.

## When the right operation used the wrong account

An engineer plans a sandbox network using a profile whose name is `training`, but that profile assumes a production role. The source is harmless-looking and the region is correct. The failure is the assumption that a profile label establishes account identity. A new network can consume address allocation, quota, and costs even if no existing resource is deleted.

Diagnosis records the actual caller identity, selected region, resource creation time, and affected resource identifiers. Freeze further changes from that workflow. Compare state and inventory before cleanup, determine whether any consumers attached, and have the appropriate owner approve the correction. Do not immediately destroy every similarly tagged resource: the tag may be shared with legitimate infrastructure.

Recovery removes only the confirmed accidental scope when safe, preserves evidence, and fixes the profile/role selection. Prevention binds a verified expected account ID to the workflow before a mutation and makes the resolved account visible in the review record. The next chapter shows the concrete STS check. A warning banner in the shell is insufficient if the command independently selects another profile.

Another incident is lost root recovery access after a custodian leaves. The service can continue running while administrative recovery is impaired. Resolve it through the documented AWS account recovery process and organizational authority, preserving evidence and contact ownership. Do not create informal shared permanent credentials to avoid the governance problem. Recovery capability needs periodic verification, not only a successful initial signup.

## Exercises and answer guidance

1. Does the JSON allowed-region list enforce anything? No. It documents intent; an actual permission/governance mechanism and verification are separate implementation work.
2. A resource is absent in the selected region. Name checks before treating it as deleted. Verify account, region, service scope, identifier, permissions, and current inventory/audit evidence.
3. Which responsibilities remain with Summit after adopting a managed database? Application correctness, data/access policy, backup choices and restore evidence remain; the provider's documented service boundary determines specific maintenance work.

Review questions: Who owns an account after an engineer leaves? What distinguishes role name from caller identity? Which failures does a zone boundary address? How does a service choice change OS-maintenance responsibility?

A usable AWS environment begins with durable ownership, explicit identity and region context, and a responsibility map that reaches the customer contract. Resource creation comes after those boundaries are reviewable.

## Sources and verification

AWS shared responsibility, root-user best practices, and endpoint/region documentation were inspected 2026-10-01. The account-management page fetch failed, so no claim of inspecting that page is made. The example account names and layout are fictional. No signup, account mutation, JSON command, AWS CLI call, resource creation, or teardown ran during authoring.
