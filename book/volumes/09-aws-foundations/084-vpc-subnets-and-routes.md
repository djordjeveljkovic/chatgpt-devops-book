---
book: The Complete DevOps Engineering Book
volume: 9
volume_title: "AWS Foundations"
chapter: 84
title: "VPC, Subnets and Routes"
slug: vpc-subnets-and-routes
status: complete
summary: ../../_ai/chapter-summaries/084-vpc-subnets-and-routes.md
---

# Chapter 84 — VPC, Subnets and Routes

## Address design and routing

Summit's DispatchDesk needs an application path from a load balancer to port 8080, a database path that does not accept internet clients, and an outbound path for notifications. Drawing those paths before creating resources prevents the common mistake of treating every subnet as a smaller independent network. A VPC supplies an address space and AWS networking boundaries. A subnet allocates a portion of that space within an Availability Zone. Route tables tell traffic where to go; authorization controls decide which traffic may proceed. Those are separate questions.

Read [packet addressing and routing](../03-networking-and-traffic/021-packets-addresses-and-routing.md) for CIDR and longest-prefix matching. Here the AWS-specific decision is how those concepts attach to resources. Use a fictional `10.42.0.0/16` VPC only after checking your organization's existing networks. A private address is not globally unique. A later VPN, peering connection, or corporate acquisition can make an overlapping range an expensive migration. Reserve space for future zones and environments, record an allocation owner, and distinguish development from production ranges. An attractive diagram is insufficient evidence that the address plan will interconnect.

For example, reserve `10.42.0.0/24` for one ingress subnet and `10.42.16.0/24` for an application subnet, with equivalent nonoverlapping ranges in another zone. These are design examples, not a production sizing recommendation. AWS reserves addresses within each subnet; inspect the [subnet sizing rules](https://docs.aws.amazon.com/vpc/latest/userguide/subnet-sizing.html) before choosing a small range. Container tasks, load balancers, endpoints, replacement deployments, and other network interfaces consume addresses. An application can run out of addresses during a rolling replacement even when steady-state task count fits.

A subnet uses one effective route table. Explicit associations take precedence over the VPC's main table fallback. A useful operational policy is to keep the main table isolated and explicitly associate intended public and private tables. This makes an accidentally unassociated subnet less likely to inherit internet access. An implicit association does not appear as an explicit subnet ID in `describe-route-tables`; absence from that list therefore does not mean the subnet lacks routing. AWS documents that distinction in the [CLI reference](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-route-tables.html).

Every path must have an appropriate destination route and a usable target. Within the VPC, a local route normally handles VPC-address traffic. A default IPv4 route, `0.0.0.0/0`, catches destinations without a more specific match. A route marked `blackhole` points at an unavailable target; an apparently correct destination alone does not establish reachability. For return traffic, check the reverse path too. A route table is not a firewall and does not open an application port.

## Internet access, NAT and endpoints

A public subnet has a route to an attached internet gateway. For ordinary IPv4 instance internet communication, the instance also needs a public IPv4 address or Elastic IP, alongside valid routes and permission controls. Adding a public address to an instance in an isolated subnet does not create the missing gateway route. Conversely, attaching an internet gateway does not automatically expose every private address. [AWS's internet gateway guide](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Internet_Gateway.html) describes these separate requirements.

A public NAT gateway provides outbound IPv4 connectivity for private clients when its own internet path is configured. The private subnet routes suitable destinations to NAT; NAT sends traffic through its public-side path and translates addresses. Internet peers cannot use that translation as a general invitation to initiate connections to private clients. NAT is useful for third-party notification APIs and package repositories, but it introduces an availability dependency, data processing costs, and ongoing charges. Consult the [current pricing page](https://aws.amazon.com/vpc/pricing/) for the selected region before provisioning it. This chapter does not create a NAT gateway or promise a free lab.

Do not assume every NAT arrangement has identical zone behavior. AWS's current [NAT documentation](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html) distinguishes gateway modes and placement options, including regional functionality. Choose against the documented service offering available to your account and region. For a zonal design, trace what happens if its zone fails and whether another zone depends on it. Redundant application tasks do not remove a shared egress dependency. Record whether reduced egress availability is acceptable for notification workers and how their retries recover after connectivity returns.

An endpoint offers another route to some AWS services. An interface endpoint introduces private network interfaces and associated DNS and security decisions; gateway endpoints for supported services use route-table integration. Endpoint presence alone does not authorize API calls. IAM policies, resource policies, endpoint policy where applicable, and service requirements still apply. Check [AWS's endpoint concepts](https://docs.aws.amazon.com/vpc/latest/privatelink/concepts.html) for the service's supported type. Endpoint charges and DNS behavior differ; adding endpoints for every service without a traffic and cost model can be worse than the original design.

Summit can send S3 artifact traffic over a suitable endpoint while still needing a deliberate path to an external notification provider. Atlas's Kubernetes implementation has additional pod and service networking concerns later in the book. Harbor can retain its VPS network without acquiring AWS network objects. The companies share the need to trace requests; they do not need matching infrastructure.

## A disposable isolated network

This optional lab creates a VPC and one subnet, examines their default routes, and removes both. It deliberately creates no compute, public address, NAT gateway, endpoint, or internet gateway. Run it only in an authorized sandbox with an agreed budget and cleanup owner. No cloud commands below were executed during authoring. Other resources added to this network can be billable and can block cleanup.

Use Bash on an ordinary workstation user account with AWS CLI v2 already installed. Ubuntu 24.04 LTS, Fedora 44, and RHEL 9 use the same AWS API commands; local package installation and enterprise proxy trust remain distribution-specific as discussed in [CLI setup](082-aws-cli-and-identity-sessions.md). You need an authenticated profile, a verified sandbox account, and permissions for the displayed create, describe, and delete operations. Complete the account preflight in that chapter before proceeding. Set the region to your authorized region, not merely the nearest-looking one.

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 describe-availability-zones   --query 'AvailabilityZones[?State==`available`].[ZoneName,ZoneId]'   --output table
```

`--profile` selects credentials, `--region` selects the API location, and `--no-cli-pager` keeps the output in the terminal. The query selects available zones and displays names alongside IDs. Pick an allowed zone from the actual result and enter it below. Zone names are account-relative labels; do not infer that another account's same letter represents the same physical zone.

```bash
read -r -p 'Approved zone name from the result: ' lab_zone
: "${lab_zone:?zone is required}"
lab_vpc=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager ec2 create-vpc --cidr-block 10.42.0.0/16   --tag-specifications   'ResourceType=vpc,Tags=[{Key=Name,Value=dispatchdesk-route-lab},{Key=Purpose,Value=temporary-lab}]'   --query 'Vpc.VpcId' --output text)
printf 'Record VPC for cleanup: %s\n' "$lab_vpc"
lab_subnet=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager ec2 create-subnet --vpc-id "$lab_vpc"   --cidr-block 10.42.16.0/24 --availability-zone "$lab_zone"   --tag-specifications   'ResourceType=subnet,Tags=[{Key=Name,Value=dispatchdesk-isolated-lab},{Key=Purpose,Value=temporary-lab}]'   --query 'Subnet.SubnetId' --output text)
printf 'Record subnet for cleanup: %s\n' "$lab_subnet"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 describe-route-tables --filters "Name=vpc-id,Values=$lab_vpc"   --output json
```

The command substitutions capture identifiers returned by AWS rather than invented IDs. Record them immediately in a protected lab log. Tags make inventory easier but do not grant ownership or prevent another person from using the network. `--cidr-block` allocates the address range; `--availability-zone` fixes the subnet's zone; the queries extract only the created identifiers. If subnet creation fails, the VPC may already exist. Bash stopping is not transaction rollback: retain `lab_vpc` and use the cleanup procedure rather than blindly rerunning creation.

Inspect the route-table JSON for the main association and the local route covering the VPC CIDR. There should be no default internet route from these commands. This predicts isolation; it is not a measured packet test because no host exists. Preserve the full JSON during diagnosis instead of filtering away target and state fields. An unexpected extra route means the environment differs from this lab and deserves investigation.

Delete only the recorded lab resources, after checking nobody attached workloads:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 delete-subnet --subnet-id "$lab_subnet"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 delete-vpc --vpc-id "$lab_vpc"
```

Successful delete requests return no resource inventory. Confirm removal in the same account and region using the recorded IDs and the console or corresponding describe calls; a not-found response is expected after deletion, whereas access denial is not proof of removal. If subnet creation never succeeded, skip its deletion and remove the recorded VPC. A dependency error requires inspecting remaining network interfaces and attached resources. Do not delete unfamiliar dependencies to force cleanup. Coordinate with their owners, and keep the cleanup ticket open until inventory confirms resolution.

## Tracing a failed connection

Suppose a private DispatchDesk worker cannot reach the notification provider after a deployment. The misleading assumption is that “the VPC has a NAT gateway” proves the worker has egress. First identify the actual task network interface, private address, subnet, and account/region. Then find the subnet's effective route table, including the main fallback. Compare the provider's resolved destination with routes and inspect the winning target's state. A healthy NAT in another route table does nothing for this subnet.

If the table contains only a local route, the failure has a concrete explanation: the external destination has no usable outbound route. Repair the intended association or approved route through the infrastructure owner, review its plan, and retest one notification operation. Do not attach a public address to the worker as an improvised bypass. If the route is present, inspect the target, its external path, DNS answers, security controls, and application timeout in that order. [Security groups and network ACLs](085-security-groups-and-network-acls.md) cover the next boundary. A timeout does not distinguish these causes by itself.

After restoring connectivity, check queued notification intents and duplicate-handling behavior. Network recovery can release accumulated retries and overwhelm a provider. Limit worker concurrency and preserve order durability while draining the backlog. The evidence for recovery is a successful intended request plus stable queue age and error rates, not merely a green infrastructure status.

## Exercises and answer guidance

1. A subnet has a public IPv4 instance but only a local route. Explain why internet access fails. The public address does not replace the missing internet gateway path; inspect the subnet's effective table and gateway attachment before changing permission rules.
2. The explicit subnet association filter returns nothing. Is routing absent? No. Inspect the VPC's main table because the subnet may use its implicit association.
3. A private worker reaches S3 through an endpoint but cannot contact a third-party API. What does that establish? The successful service-specific path does not prove general internet egress. Trace the third-party destination separately and retain IAM distinctions.
4. Creation fails after the VPC succeeds. What is the cleanup unit? The actual recorded resources, not the script as an imagined atomic operation. Inventory the VPC and delete only authorized lab objects in dependency order.

Review questions: which route wins for a destination, which subnet owns the initiating interface, what authorizes the request after routing succeeds, and who pays for the chosen egress path? A defensible answer names evidence for each boundary.

## Verification and primary sources

Official AWS VPC and CLI documentation was inspected on 2026-10-01. The examples assume AWS CLI v2 and the documented EC2 API operations; they do not assert a particular installed CLI version. No AWS resource was created and no live routing, pricing, quota, or connectivity integration was tested. Local syntax checks cannot establish cloud permissions or reachability.

Additional operation references: [create-vpc](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-vpc.html), [create-subnet](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-subnet.html), [delete-subnet](https://docs.aws.amazon.com/cli/latest/reference/ec2/delete-subnet.html), and [delete-vpc](https://docs.aws.amazon.com/cli/latest/reference/ec2/delete-vpc.html). Use the service documentation and current regional pricing when converting this isolated learning network into a production design.
