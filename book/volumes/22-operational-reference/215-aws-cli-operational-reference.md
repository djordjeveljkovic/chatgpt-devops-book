---
book: The Complete DevOps Engineering Book
volume: 22
volume_title: "Operational Reference"
chapter: 215
title: "AWS CLI Operational Reference"
slug: aws-cli-operational-reference
status: complete
summary: ../../_ai/chapter-summaries/215-aws-cli-operational-reference.md
---

# Chapter 215 — AWS CLI Operational Reference

This reference is for an engineer who needs to inspect an AWS environment, connect an error to its permission or resource boundary, and remember the relevant CLI shape. Complete provisioning and production designs belong to [AWS Foundations](../09-aws-foundations/README.md) and [AWS Production Services](../10-aws-production-services/README.md). Cloud resource identity includes account and region as well as an instance, bucket or service name.

Examples use AWS CLI v2 on an authorized workstation. Installation differs across Linux distributions and processor architectures; use the verified procedure in [AWS CLI and Identity Sessions](../09-aws-foundations/082-aws-cli-and-identity-sessions.md). A reader needs a configured profile and an account they are allowed to inspect. None of the commands below was executed against an AWS account while authoring.

## Identity first, then resources

```bash
aws --version
aws configure list-profiles
book_profile='dispatchdesk-lab'
book_region='us-east-1'
aws --profile "$book_profile" --region "$book_region" --no-cli-pager sts get-caller-identity
```

The first command identifies the installed client. `list-profiles` lists local profile configuration; it does not establish that a session works. Replace the profile and region examples with your approved values. `--profile` selects configuration and its credential-resolution behavior. `--region` makes the target region explicit for regional services. `--no-cli-pager` avoids launching an output pager; it does not disable API pagination.

`get-caller-identity` returns the effective caller's account and ARN. Compare them with the intended change record before continuing. A familiar local profile name can resolve to a different role after configuration changes. An assumed-role ARN identifies a session, not simply the original user. The [STS command reference](https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html) defines the response. Session expiry, an unavailable credential helper and an incorrect role-trust condition produce different repair paths.

For an IAM Identity Center profile, `aws sso login --profile "$book_profile"` obtains or refreshes an authorized local session using the configured flow. It is an authentication action, separate from listing application infrastructure. It does not grant every permission in the account. A workstation login flow should not be copied into unattended CI; use an approved federated role and short-lived credentials there. [IAM Policies and Least Privilege](../09-aws-foundations/083-iam-policies-and-least-privilege.md) explains permission evaluation.

## Filter on the service, shape the output on the client

This example inspects only project-tagged EC2 instances and chooses useful fields:

```bash
aws --profile "$book_profile" --region "$book_region" --no-cli-pager \
  ec2 describe-instances \
  --filters 'Name=tag:Project,Values=DispatchDesk' \
  --query 'Reservations[].Instances[].{Id:InstanceId,State:State.Name,Type:InstanceType,PrivateIP:PrivateIpAddress}' \
  --output table
```

`describe-instances` is an observation, not an instance launch. The `--filters` syntax is defined by EC2 and limits matching service results. `--query` is a JMESPath expression evaluated by the client against returned data; it projects instance identifiers, states, types and private addresses. `--output table` formats that projection for a human. Use JSON for automation that needs typed values and explicit structural checks. The [EC2 command reference](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-instances.html) and [AWS filtering guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-filter.html) distinguish server filtering from client queries.

An empty result is evidence only within the selected account, region, permissions and filter. A missing tag or a misspelled value can conceal an existing instance. Tags are useful inventory metadata, but do not establish that a resource is disposable. Shared databases, retained volumes and production dependencies require ownership evidence before deletion.

## Pagination is part of a correct inventory

For supported list operations, the CLI normally follows service pages. `--page-size` adjusts the requested page size and can change the number of API calls; it is not a cap on total returned items. `--max-items` caps CLI output and can return a continuation token. Resume with that command's compatible `--starting-token` rather than guessing a service-specific token format. `--no-paginate` stops automatic continuation and can leave an inventory incomplete. These distinctions are documented in the [pagination guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-usage-pagination.html).

Use JSON when calculating across the whole response. With paginated text output, query evaluation can occur per page, making some aggregations differ from an intended whole-inventory calculation. Pagination also does not promise an immutable snapshot while other actors create or delete resources. An operational inventory should state its collection interval and tolerate reconciliation of changes.

For example, a script that counts only the first page of instances can falsely conclude that unused capacity is low. Before scaling or cleaning resources, record the selection criteria, whether all pages were retrieved, and any access errors. Do not turn a partially successful region loop into a complete-account report.

## Networking and instance investigations

The commands in this table require the explicit profile/region options established above. Replace resource IDs with values from verified inventory; names such as `i-EXAMPLE` are notation, not valid copyable identifiers.

| Service command | Arguments and useful outcome |
|---|---|
| `ec2 describe-instance-status --instance-ids INSTANCE_ID --include-all-instances` | Inspect instance/system status rather than only application uptime. `--include-all-instances` broadens the instance-state selection. |
| `ec2 describe-security-groups --group-ids GROUP_ID` | Inspect the selected security group's ingress and egress rules. A permitted rule does not prove routing or application listening. |
| `ec2 describe-route-tables --filters 'Name=vpc-id,Values=VPC_ID'` | Inspect routes in the selected VPC; determine the actual subnet association rather than choosing a table by a familiar name. |
| `ec2 describe-subnets --subnet-ids SUBNET_ID` | Inspect subnet identity and available address information relevant to launch or task-networking failures. |
| `ssm describe-instance-information` | List managed-node information visible to this identity. An absent node can reflect agent, network, role or account-selection conditions. |
| `elbv2 describe-target-health --target-group-arn TARGET_GROUP_ARN` | Inspect backend health states and reasons for one target group; continue to application and network evidence. |

An EC2 instance can be running while no public route reaches it. A healthy load-balancer target can serve the health endpoint while order writes fail. Walk the actual packet and request path: client DNS, load balancer, target registration, security policy, subnet routing, host listener and application dependencies. See [VPC, Subnets and Routes](../09-aws-foundations/084-vpc-subnets-and-routes.md) and [Route 53, Certificates and Load Balancers](../09-aws-foundations/089-route-53-certificates-and-load-balancers.md).

`ssm start-session --target INSTANCE_ID` creates an interactive operational session when configured and authorized. It changes the access context and may need an installed Session Manager plugin. Treat it as a remote administrative action, with scope and evidence, rather than just another list command. Session availability depends on the agent, role and service connectivity.

## Containers, databases and telemetry

| Service command | What to supply and inspect |
|---|---|
| `ecs describe-services --cluster CLUSTER_NAME --services SERVICE_NAME` | Inspect service deployments, desired/running counts and events in the identified cluster. |
| `ecs describe-tasks --cluster CLUSTER_NAME --tasks TASK_ARN` | Inspect exact task state, container exit details and stop reasons. |
| `ecs wait services-stable --cluster CLUSTER_NAME --services SERVICE_NAME` | Poll the documented service-stability condition. A successful waiter does not test every customer journey or database migration. |
| `eks describe-cluster --name CLUSTER_NAME` | Inspect managed cluster metadata; this is not a kubectl workload observation. |
| `rds describe-db-instances --db-instance-identifier DB_IDENTIFIER` | Inspect database instance status, endpoint and configuration rather than exposing stored customer data. |
| `ecr describe-images --repository-name REPOSITORY_NAME` | Inspect repository image identity and metadata; retain digest-based release evidence. |
| `logs tail LOG_GROUP --since 15m --follow` | Follow recent events from the named log group. `--since` bounds the starting window; `--follow` continues polling until interrupted. |

Use service events and task reasons to distinguish insufficient capacity, a failed image pull, bad configuration and an application crash. More desired tasks do not repair a denied registry operation or database connection ceiling. A waiter timeout means the observation condition was not met within its polling contract; inspect the reason before repeating a deployment.

For logging, identify the group and retention policy before opening a broad query. Avoid copying credentials or customer payloads into an incident note. Searching a small affected interval is both diagnostically clearer and better controlled than querying every retained event. Some observability operations are billed or create query work; their cost and access boundaries belong to the specific service.

## S3 inspection and copy semantics

For an existing authorized bucket, set a reader-owned variable with its actual name:

```bash
book_bucket='replace-with-your-approved-bucket'
aws --profile "$book_profile" --region "$book_region" --no-cli-pager \
  s3api list-objects-v2 --bucket "$book_bucket" --prefix 'dispatchdesk/releases/' \
  --query 'Contents[].{Key:Key,Bytes:Size,Modified:LastModified}' --output json
```

`--prefix` restricts keys by their beginning; S3 keys are not POSIX directory entries. `list-objects-v2` is an inventory operation, not proof that an object can be read or that a backup can restore the application. Empty content may require handling an absent `Contents` field rather than assuming a conventional directory exists.

`s3 cp` copies between a local path and an S3 URI; direction matters. `s3 sync` reconciles objects according to its documented comparison rules. Adding `--delete` can remove destination objects that are absent from the source, so it belongs in a separately reviewed procedure with a deliberate destination and recovery boundary. A versioned object store helps only when the relevant versions, retention and restore permissions actually exist. See [S3 from the CLI](../09-aws-foundations/088-s3-from-the-cli.md).

## Dry-run, change and recovery boundaries

Some EC2 operations, including `run-instances`, accept `--dry-run`. The [launch reference](https://docs.aws.amazon.com/cli/latest/reference/ec2/run-instances.html) documents that the authorization probe returns a specific dry-run error when permitted, or an authorization error when denied. A nonzero exit therefore needs interpretation. Dry-run is not a universal AWS feature and is not a simulation proving capacity, price, application readiness or recovery.

Before a real launch, update, stop or delete, preserve verified identity, exact resource IDs, desired artifact/configuration and a recovery procedure. A stopped instance can leave storage and other billable dependencies. A deleted database cannot be restored merely by recreating its infrastructure declaration. Use tagged inventory to locate related resources, then confirm their owners and retention requirements.

Review drill: an ECS service fails to reach its desired task count. Confirm account/region/cluster first, inspect service events and exact stopped tasks, identify whether the constraint is capacity, credentials, networking or the application, and verify a known request after the repair. A higher desired count is a scaling request, not a diagnostic explanation.

## Verification

Official AWS CLI identity, filtering, pagination, EC2 describe and EC2 launch references were inspected on 2026-10-01. Service command rows are navigation aids to their dedicated chapters and exact CLI help, not a claimed executed AWS inventory. AWS CLI and cloud credentials were not used in the authoring environment. No cloud resources, sessions, copies, queries, deployments or deletions were performed; reader operations need their own account permissions and cost-aware scope. Local shell/link checks do not establish AWS request validity or live outcomes.
