---
book: The Complete DevOps Engineering Book
volume: 9
volume_title: "AWS Foundations"
chapter: 85
title: "Security Groups and Network ACLs"
slug: security-groups-and-network-acls
status: complete
summary: ../../_ai/chapter-summaries/085-security-groups-and-network-acls.md
---

# Chapter 85 — Security Groups and Network ACLs

## Stateful and stateless boundaries

A network policy should express a connection contract: who initiates a connection, which destination receives it, which protocol and port it uses, and how responses return. Summit's DispatchDesk application receives HTTP on TCP 8080 from its load balancer and initiates PostgreSQL connections on TCP 5432. A rule saying “allow the application” is incomplete until it identifies those directions and peers. Read [TCP connections](../03-networking-and-traffic/022-tcp-udp-and-connections.md) and [VPC routing](084-vpc-subnets-and-routes.md) before changing these controls.

Security groups attach policy to associated resources and their network interfaces. They are stateful: a permitted connection's response traffic does not require a mirror-image rule in the opposite direction. Their rules allow traffic; they do not provide ordered deny rules. Multiple associated groups contribute an aggregate set of permissions. Attaching a second restrictive group therefore does not cancel a permissive first one. The [security-group guide](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html) explains these semantics. During review, inspect every group associated with the actual interface rather than the group whose friendly name looks relevant.

Network ACLs operate at subnet boundaries. They support ordered allow and deny decisions and do not track connections. An outbound request and its returning packets are separate evaluations. A low-numbered matching rule wins, so a later allow cannot rescue traffic already denied. AWS's [network ACL guide](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html) documents both the ordering and the stateless behavior. This makes an ACL useful for a deliberate subnet-level boundary, but copying a security group into an ACL usually produces a broken return path.

Consider a client using source port 42000 to connect to database port 5432. On the forward path, the database subnet sees destination port 5432. On the return path, the application subnet sees destination port 42000. An ACL that permits only inbound 5432 on both subnets misunderstands which endpoint owns the listening port. The ephemeral source port varies; the example's 42000 is illustrative. Select any allowed return-port range using the actual client and service requirements, following [AWS's custom ACL discussion](https://docs.aws.amazon.com/vpc/latest/userguide/custom-network-acl.html). Do not infer the whole fleet's behavior from one successful connection.

## Service exposure as a connection contract

The following is a design review table for a fictional same-VPC deployment. It is not a complete executable network: listeners, targets, routes, TLS, database authentication, and egress dependencies still need their own configuration.

| Initiator | Receiver | New connection | Intended policy |
| --- | --- | --- | --- |
| Internet client | Public load balancer | TCP 443 | Load-balancer ingress for the intended customer audience |
| Load balancer | DispatchDesk application | TCP 8080 | Application ingress from the load-balancer group |
| Application | PostgreSQL database | TCP 5432 | Database ingress from the application group |
| Notification worker | External provider | TCP 443 | Worker egress through the approved outbound path |

A source security-group reference expresses membership rather than a fixed list of current private addresses. In the simple same-VPC topology here, it lets replacement application instances retain the database contract when they use the approved application group. It does not copy the referenced group's rules, authenticate the application user, or create a route. Membership must itself be controlled: someone who can attach that group to unrelated compute may acquire the allowed network path. [Security-group referencing rules](https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html) also describe topology limitations, including middlebox paths; do not generalize this example across arbitrary transit networks.

For DispatchDesk, avoid opening database TCP 5432 to the entire VPC merely because the VPC uses private addresses. A compromised unrelated workload could then attempt database authentication. Conversely, restricting the database group cannot replace database credentials and TLS verification. Network access is one layer of authorization. A refused connection, TLS verification failure, and PostgreSQL authentication denial are different evidence and should lead to different repairs.

Egress deserves an explicit decision. New security groups begin with permissive outbound rules. Leaving that default can be reasonable for a disposable unattached lab, but it is not a declaration of production least privilege. Enumerate API endpoints, DNS behavior, package acquisition, telemetry, and managed-service dependencies before restricting a real application. IPv4 and IPv6 are separate policy paths. A carefully limited IPv4 rule does not constrain an independently allowed IPv6 path.

## A disposable security-group lab

This optional lab creates two unattached groups in an existing authorized sandbox VPC, adds one database ingress rule referencing the application group, inspects it, revokes it, and deletes both groups. It attaches neither group to running resources and does not change a subnet ACL. Use AWS CLI v2 from a normal Bash workstation account with the authenticated profile and account preflight from [Chapter 82](082-aws-cli-and-identity-sessions.md). The commands are the same on Ubuntu 24.04 LTS, Fedora 44, and RHEL 9; they call AWS APIs rather than changing the local host firewall.

You need permission for the shown EC2 group and rule operations and a VPC owned or administered under your lab authorization. Security groups and ACLs have no additional charge according to their linked service guides, but attached compute, endpoints, logs, and other services can incur charges. No cloud command was executed during authoring. Copy the actual VPC ID after inspecting it in the verified account and region; the prompts deliberately avoid fabricated identifiers.

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Verified sandbox VPC ID: ' lab_vpc
: "${lab_vpc:?VPC ID is required}"
lab_app_group=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager ec2 create-security-group --vpc-id "$lab_vpc"   --group-name dispatchdesk-app-policy-lab   --description 'Unattached application membership lab'   --query 'GroupId' --output text)
printf 'Record application group: %s\n' "$lab_app_group"
lab_db_group=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager ec2 create-security-group --vpc-id "$lab_vpc"   --group-name dispatchdesk-db-policy-lab   --description 'Unattached database ingress lab'   --query 'GroupId' --output text)
printf 'Record database group: %s\n' "$lab_db_group"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 authorize-security-group-ingress --group-id "$lab_db_group"   --protocol tcp --port 5432 --source-group "$lab_app_group"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 describe-security-group-rules   --filters "Name=group-id,Values=$lab_db_group" --output json
```

`--vpc-id` binds each new group to this VPC. The names must be unique within it; a name-collision error is not permission to reuse a stranger's group. The descriptions explain the lab's scope. The query captures returned identifiers and the printed records support cleanup after a later failure. `--group-id` names the receiver's group; `--source-group` names the initiator's group; `--protocol tcp --port 5432` permits that one listening port. None of these flags installs PostgreSQL.

Inspect returned rule fields for ingress direction, TCP port bounds, and the referenced source group. You will also see outbound defaults. The existence of the rule proves only control-plane configuration, not an application connection. To verify a real deployment, additionally inspect interface attachments, routing, ACLs, the listener, and an authorized database connection. Do not attach these lab groups to production just to obtain a packet test.

Reverse the change and remove the groups:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 revoke-security-group-ingress --group-id "$lab_db_group"   --protocol tcp --port 5432 --source-group "$lab_app_group"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 delete-security-group --group-id "$lab_db_group"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 delete-security-group --group-id "$lab_app_group"
```

The revoke request identifies the same permission tuple as creation. If the rule never existed because authorization failed, inspect the group before retrying cleanup; failure of one step does not undo preceding creations. Remove the referencing database group before the referenced application group. A dependency error indicates an attachment or reference requiring investigation. Preserve actual IDs and coordinate with its owner rather than deleting unfamiliar resources. Confirm the groups disappear from inventory in the original account and region.

## Investigating a private database timeout

Suppose Summit replaces application tasks and database connections start timing out. A developer sees the database group's correct 5432 rule and concludes PostgreSQL must be down. That assumption misses the sender's actual membership. Capture the new task's interface ID, private IP, subnet, associated group IDs, destination hostname and resolved address, and the time of one controlled connection attempt. Avoid printing passwords or complete connection strings into incident notes.

Compare new and previous task definitions and interfaces. If the replacement lost the intended application group, the database's reference no longer recognizes the source. Repair the task network configuration through the owning deployment definition and replace one task first. A database rule widened to the entire VPC would conceal the deployment defect while granting unrelated workloads access. Confirm the repaired task can connect and that an unauthorized group still cannot initiate the same connection.

If membership is correct, inspect the effective subnet routes and both ACLs. A missing return-port allow can produce retries and timeout even though database ingress is allowed. Write the forward and reverse packet tuples on paper; compare their destination ports against ordered rules. If a lower-numbered deny wins, a new higher-numbered allow has no effect. Repair the intended ACL rule order or return range after reviewing the impact on every subnet sharing that ACL.

Then distinguish transport from service failures. A TCP connection reaching a listener followed by authentication rejection establishes more than a timeout. Verify the application uses the intended endpoint and port, the database is ready, and credentials and TLS trust are valid. [RDS operations](../10-aws-production-services/095-rds-and-managed-database-operations.md) provide the managed database lifecycle details. Do not change routing to fix a password error.

A rule revocation also deserves careful validation. Existing tracked traffic can behave differently from newly initiated traffic, as the security-group rule documentation warns. Use a new connection to test the intended future access policy and consult the relevant connection-tracking documentation for urgent termination requirements. Avoid assuming that one surviving pooled connection proves the new rule was ignored. Record both the policy state and the test's connection lifetime.

## Exercises and answer guidance

1. Two groups attach to an interface: one allows TCP 5432 from the VPC and one allows it only from the application group. Which policy applies? The allows aggregate; the second group does not subtract the wider first permission.
2. A client's source port is 42000 and destination port is 5432. Which destination port appears in the response? 42000. A stateless ACL must account for the return direction using the appropriate actual ephemeral range.
3. A new task cannot connect but an old task can. Name a useful first comparison. Compare actual interface group membership and subnet associations, then deployment definitions; identical friendly group names are insufficient.
4. Why does a source-group rule fail to prove secure database use? It permits a network path for qualifying membership, while TLS, database identity, authorization, and application behavior remain separate controls.

Review questions: who may attach the trusted source group, which ACL rule matches first, which direction initiates the connection, and what test distinguishes policy state from application success? Keep these answers alongside the change review.

## Verification and primary sources

Official AWS VPC and CLI documentation was inspected on 2026-10-01. The examples assume AWS CLI v2 and documented EC2 operations. No security group, rule, ACL, or application interface was changed during authoring; transport and database integrations remain untested.

Operation references: [create-security-group](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-security-group.html), [authorize-security-group-ingress](https://docs.aws.amazon.com/cli/latest/reference/ec2/authorize-security-group-ingress.html), [describe-security-group-rules](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-security-group-rules.html), [revoke-security-group-ingress](https://docs.aws.amazon.com/cli/latest/reference/ec2/revoke-security-group-ingress.html), and [delete-security-group](https://docs.aws.amazon.com/cli/latest/reference/ec2/delete-security-group.html). Syntax and document inspection cannot establish live reachability.
