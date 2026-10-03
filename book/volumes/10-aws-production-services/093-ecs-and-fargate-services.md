---
book: The Complete DevOps Engineering Book
volume: 10
volume_title: "AWS Production Services"
chapter: 93
title: "ECS and Fargate Services"
slug: ecs-and-fargate-services
status: complete
summary: ../../_ai/chapter-summaries/093-ecs-and-fargate-services.md
---

# Chapter 93 — ECS and Fargate Services

## Tasks, services and capacity

Amazon ECS separates a task definition from a task and from a service. A task definition is a versioned declaration of containers, images, CPU and memory, networking mode, logging, health checks, volumes and IAM roles. A task is one running or stopped attempt using a revision of that definition. A service maintains a desired number of tasks and replaces tasks that stop or become unhealthy according to its scheduler and health configuration. These are different records with different lifecycles: registering a revision does not deploy it, and starting one task does not create a long-running service.

Fargate supplies task compute capacity without requiring the team to manage an EC2 container host. ECS still needs a cluster as an organizational and operational boundary, a task definition, a service scheduler and network placement. Fargate is not serverless in the sense of having no capacity, identity, subnet, quota, logging or cost decisions. The task remains a workload that must start, reach dependencies and satisfy health checks. A service desired count of two expresses intent; running healthy tasks and usable API capacity are observed outcomes.

Fargate task definitions require `awsvpc` networking. Each task receives an elastic network interface with the selected security groups and subnet placement. This makes the task's network identity explicit, but consumes subnet addresses and requires routes for image pulls, logs, secrets and application dependencies. Private subnets commonly use NAT or the necessary VPC endpoints. Avoid public IP assignment for the production-style example below; the load balancer is the public entry point. [Fargate task requirements](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-tasks-services.html) describes task networking and resource constraints.

Tasks have separate execution and application identities. The task execution role lets ECS/Fargate perform startup operations such as pulling a private ECR image and sending logs. The task role supplies AWS credentials to code inside the container. Giving an API's execution role access to the order database does not grant the application a task role, and placing data-plane permissions on a broadly reused task role expands the impact of compromise. Use a narrowly scoped role per workload. The worker that reads a queue should have only the queue and related secret permissions it requires; a stateless API should not inherit those permissions by copying the worker role. [ECS IAM role guidance](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/security-iam-roles.html) explains this distinction.

Fargate suits variable or modest workloads where the team values managed task hosts and accepts per-task resource, network and service limits. ECS on EC2 can suit steady high utilization, specialized host requirements or workloads whose economics justify managing capacity. Kubernetes on EKS adds a richer cluster API and ecosystem but also cluster and workload operations. Decide from workload shape, operating skills, portability needs, traffic, security and a measured cost model; no launch type is universally cheaper or simpler.

## Networking, identity and deployment health

An ALB target group for `awsvpc` tasks routes to the task's IP address and the container port. The task security group should accept that port from the ALB security group, not from every internet address. The ALB security group separately owns public listener access. Keep the task in private subnets with a route to required dependencies. A missing route, endpoint policy, DNS path or egress rule can prevent a task from pulling its image, retrieving a secret, emitting logs or connecting to a database even when the subnet ID is valid.

The application container should listen on its declared port on the task interface and implement a readiness endpoint that reflects whether it can serve the intended request. An ALB target health check answers a narrower question: whether a configured probe reached its target and returned an accepted result. Container health checks, load-balancer health, service deployment health and customer-visible readiness are related signals, not interchangeable guarantees. A large grace period can mask a slow but healthy startup briefly; it cannot make a deadlocked process ready or repair a security-group mistake. Derive timeouts and thresholds from measured startup, dependency and request behavior.

The API and worker should normally be separate ECS services even if they use the same image repository. They have distinct task definitions or command settings, IAM roles, scaling signals, health semantics, resource requests and failure policies. The API receives requests through the ALB. The worker polls a durable queue and should scale against useful backlog per effective worker while respecting downstream concurrency and provider limits. Scaling the web service does not increase worker capacity. Raising both desired counts can amplify database contention or notification-provider throttling.

For a rolling ECS deployment, the scheduler replaces tasks according to minimum and maximum healthy percentages. The deployment circuit breaker can detect repeated task-start or health failures and, when configured, roll back to a previously completed service revision. It does not prove successful order processing, prevent every transient error or create a previous good revision on a brand-new service. An initial deployment failure may therefore leave the service stalled for operator repair. Circuit-breaker events and service deployment state provide evidence; application metrics and a synthetic transaction provide evidence at a different layer. [Circuit-breaker behavior](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html) documents its stages and rollback requirement.

## Deploying an API and a background worker

This optional CLI walkthrough creates two Fargate services in existing infrastructure. It creates no VPC, subnet, ALB, queue, database, IAM role or application artifact. It assumes Chapter 92's approved images are already published by digest, Chapter 89 owns the ALB and API target group, and Chapter 97 owns the durable queue. Use a dedicated sandbox, unique service names, approved private subnets, separate least-privilege task roles and existing execution roles. Registering tasks and running services can incur charges. No AWS call was made while writing this chapter.

Run the walkthrough from an ordinary Bash workstation user account with AWS CLI v2 and Python 3; the same AWS steps apply on Ubuntu 24.04 LTS, Fedora 44 and RHEL 9. Complete [Chapter 82's account preflight](../09-aws-foundations/082-aws-cli-and-identity-sessions.md) first. Keep task JSON and command output in a new private working directory, and keep the same shell open through cleanup:

```bash
set -euo pipefail
umask 077
lab_workdir=$(mktemp -d "${TMPDIR:-/tmp}/dispatchdesk-ecs.XXXXXXXX")
cd "$lab_workdir"
lab_workdir=$PWD
printf 'Keep this shell in the private lab directory: %s\n' "$lab_workdir"
```

The API task definition uses a digest reference and the ALB's registered container/port pair. Save the following as `api-task.json`, replacing the image and role placeholders with reviewed values. The image must listen on port 8080 and provide the health path configured on the existing target group. Keep the task execution role separate from the application task role:

```json
{
  "family": "dispatchdesk-api-lab",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "REPLACE_WITH_ECS_EXECUTION_ROLE_ARN",
  "taskRoleArn": "REPLACE_WITH_API_TASK_ROLE_ARN",
  "runtimePlatform": {"operatingSystemFamily": "LINUX"},
  "containerDefinitions": [
    {
      "name": "api",
      "image": "REPLACE_WITH_APPROVED_API_IMAGE_DIGEST_URI",
      "essential": true,
      "portMappings": [
        {"containerPort": 8080, "protocol": "tcp"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/dispatchdesk/lab/api",
          "awslogs-region": "REPLACE_WITH_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Create `worker-task.json` from the approved worker image and queue contract. Its task role is a different role with the minimum queue actions. Retain the image's documented worker entry point as its default, and never assume an API image starts a consumer merely because it can reach the queue. Add a task-definition `command` override only when the image's reviewed deployment instructions require one.

```json
{
  "family": "dispatchdesk-worker-lab",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "REPLACE_WITH_ECS_EXECUTION_ROLE_ARN",
  "taskRoleArn": "REPLACE_WITH_QUEUE_SCOPED_WORKER_ROLE_ARN",
  "runtimePlatform": {"operatingSystemFamily": "LINUX"},
  "containerDefinitions": [
    {
      "name": "worker",
      "image": "REPLACE_WITH_APPROVED_WORKER_IMAGE_DIGEST_URI",
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/dispatchdesk/lab/worker",
          "awslogs-region": "REPLACE_WITH_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

The log groups must already exist or be created by the owning infrastructure definition, and the execution role needs permission to write to them. Replace each placeholder and validate the JSON before registration. The compact `256` CPU and `512` MiB memory pair is an illustrative starting point, not a benchmark or production recommendation. Verify supported task sizes and platform version for the selected operating system and region. Secrets should be injected from an approved secret store using task-definition secret references and narrowly scoped permissions, not copied into plaintext environment variables or committed JSON.

After preflight, repeat identity verification with the same profile and region. The caller needs the ECS registration, create, describe, update, delete and pass-role actions used below, including narrowly scoped [`iam:PassRole`](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html) permission for both supplied task and execution roles. The account also needs the ECS service-linked role; have its owner arrange that prerequisite if absent. Use an approved profile and region; prompt for the existing cluster, two private subnets, task security group, API target group and desired counts. These identifiers belong to the same VPC/account scope. The task security group must accept API traffic from the ALB security group and permit required egress. The subnets need available addresses and connectivity to ECR, logs, secrets and application dependencies:

```bash
set -euo pipefail
umask 077
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Expected authorized AWS account ID: ' lab_account
lab_actual_account=$(aws --profile "$lab_profile" --region "$lab_region" \
  --no-cli-pager sts get-caller-identity --query Account --output text)
[[ "$lab_actual_account" == "$lab_account" ]] || {
  printf 'Selected profile resolved to account %s, not expected account %s\n' \
    "$lab_actual_account" "$lab_account" >&2
  exit 1
}
read -r -p 'Existing ECS cluster name or ARN: ' lab_cluster
read -r -p 'Approved first private subnet ID: ' lab_subnet_a
read -r -p 'Approved second private subnet ID: ' lab_subnet_b
read -r -p 'Task security group ID: ' lab_task_sg
read -r -p 'Existing API target group ARN: ' lab_api_target_group
: "${lab_cluster:?cluster required}" "${lab_subnet_a:?subnet required}" \
  "${lab_subnet_b:?subnet required}" "${lab_task_sg:?security group required}" \
  "${lab_api_target_group:?target group required}"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  ecs describe-clusters --clusters "$lab_cluster" --include ATTACHMENTS
```

Register each reviewed task definition and retain the returned revision ARN:

```bash
lab_api_task=$(aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  ecs register-task-definition --cli-input-json file://api-task.json \
  --query 'taskDefinition.taskDefinitionArn' --output text)
lab_worker_task=$(aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  ecs register-task-definition --cli-input-json file://worker-task.json \
  --query 'taskDefinition.taskDefinitionArn' --output text)
printf 'API task revision: %s\nWorker task revision: %s\n' \
  "$lab_api_task" "$lab_worker_task"
```

Create the API service with a rolling-deployment circuit breaker and the existing target group. The named API container and port must match the task definition and target group contract. `assignPublicIp=DISABLED` keeps task ENIs private; it does not itself provide outbound access:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  ecs create-service --cluster "$lab_cluster" \
  --service-name dispatchdesk-api-lab --task-definition "$lab_api_task" \
  --desired-count 2 --launch-type FARGATE \
  --deployment-controller type=ECS \
  --deployment-configuration 'deploymentCircuitBreaker={enable=true,rollback=true},minimumHealthyPercent=100,maximumPercent=200' \
  --network-configuration "awsvpcConfiguration={subnets=[$lab_subnet_a,$lab_subnet_b],securityGroups=[$lab_task_sg],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=$lab_api_target_group,containerName=api,containerPort=8080"
```

Create the worker as a separate service without a load balancer. The reviewed worker image must have a documented default consumer entry point. If it does not, set its documented `command` in this task definition. ECS can observe a process that exits and any configured container health check, but a task with no effective health check can remain `RUNNING` while stalled; the worker's queue lag, processing rate and error metrics are needed to establish useful operation:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  ecs create-service --cluster "$lab_cluster" \
  --service-name dispatchdesk-worker-lab --task-definition "$lab_worker_task" \
  --desired-count 1 --launch-type FARGATE \
  --deployment-controller type=ECS \
  --deployment-configuration 'deploymentCircuitBreaker={enable=true,rollback=true},minimumHealthyPercent=100,maximumPercent=200' \
  --network-configuration "awsvpcConfiguration={subnets=[$lab_subnet_a,$lab_subnet_b],securityGroups=[$lab_task_sg],assignPublicIp=DISABLED}"
```

These creates are mutating requests. Before running them, verify the account/profile, service-name ownership, target group/VPC relationship, desired counts, roles, exact image digests and teardown owner. For a production service, use the team's reviewed infrastructure pipeline as the source of truth rather than creating unmanaged console or CLI state. A CLI success response means AWS accepted the request, not that any task is healthy or the service can handle a customer request.

Observe both service rollouts and task reasons:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  ecs describe-services --cluster "$lab_cluster" \
  --services dispatchdesk-api-lab dispatchdesk-worker-lab --output json
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  ecs list-tasks --cluster "$lab_cluster" --service-name dispatchdesk-api-lab
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  ecs list-tasks --cluster "$lab_cluster" --service-name dispatchdesk-worker-lab
```

Inspect service events, deployment rollout state, desired/running/pending counts, stopped-task reasons, container logs and ALB target health. For the worker, also inspect queue age/backlog, receive/delete counts and downstream throttle/error metrics. Complete a synthetic API request and verify that the expected durable order and notification intent exist; a green task status is not a business transaction test.

## Diagnosing a deployment that never becomes useful

Suppose the service reports two desired API tasks but has zero healthy targets. Do not start by raising the desired count or extending the health grace period. Check service events and task stop reasons first. An image pull failure suggests digest, ECR policy, execution-role or route/endpoint trouble. A task that starts and then exits points toward its entry point, configuration, secret access or application logs. A running task with an unhealthy target points toward listener/target-group settings, container port, security-group source, health path or actual readiness. The circuit breaker detects service startup and configured health failure; it cannot tell whether an accepted API request committed the intended durable state.

For example, a new task can start successfully while its security group allows port 8080 only from an operator workstation CIDR that excludes the ALB nodes. Targets remain unhealthy even though the container is listening. Confirm target health reason and the effective source rules, then ask the network owner to permit the task port from the ALB security group. Referencing that group expresses the intended path more narrowly than allowing the entire VPC CIDR. Do not open the task port to `0.0.0.0/0`. After correcting the dependency, deploy the reviewed service revision and verify task state, target health and a synthetic request.

Rollback returns to the latest completed service deployment only when such a deployment exists. A first deployment with no successful predecessor requires an operator to repair or redeploy; no rollback target is available. A successful rollback also does not revert an incompatible database migration or undo an external message already sent. Keep backward-compatible schema and idempotent consumer changes in the release plan. The worker's queue visibility timeout, retry policy and dead-letter handling must account for actual processing duration; duplicate delivery remains possible, so handlers need safe idempotency.

When retiring this optional lab, update each service to desired count zero, wait until tasks stop, then delete only the two services created here. Keep the task definitions and referenced shared infrastructure unless their owners approve separate cleanup. Never delete the shared ALB, queue, roles, cluster or subnets as part of this service exercise. If a service update or delete fails, record remaining task and service state and continue cleanup with the owning account/operator rather than assuming resources vanished:

```bash
for lab_service in dispatchdesk-api-lab dispatchdesk-worker-lab; do
  aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
    ecs update-service --cluster "$lab_cluster" --service "$lab_service" \
    --desired-count 0
done
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  ecs wait services-stable --cluster "$lab_cluster" \
  --services dispatchdesk-api-lab dispatchdesk-worker-lab
for lab_service in dispatchdesk-api-lab dispatchdesk-worker-lab; do
  aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
    ecs delete-service --cluster "$lab_cluster" --service "$lab_service"
done
```

## Exercises and answer guidance

1. A registered task definition has a task role, but a task cannot pull from ECR. Check the execution role, repository permissions and network path; the task role is for application calls after startup.
2. API tasks are running but the ALB marks them unhealthy. Compare target health reason, registered port/path, container listener and task security-group source before changing health thresholds.
3. Why run the queue consumer as a separate service? It has different scaling, IAM, health and dependency-concurrency needs; API desired count does not control worker throughput.
4. The deployment circuit breaker rolled back successfully. Is order processing verified? No. Check API readiness, queue and database signals, then submit a synthetic transaction and verify durable state.

Review questions: who owns desired count, what lets a task start, what grants application AWS access, which path reaches the container, and what evidence defines useful capacity?

## Verification and primary sources

AWS ECS task definition, service, Fargate networking, IAM roles, deployment circuit breaker, CloudFormation resource and CLI documentation were inspected on 2026-10-04. Local JSON and shell syntax checks do not prove task-definition registration, IAM sufficiency, target health, service readiness, queue semantics, quota availability or workload behavior. No AWS identity/API operation, service creation, task launch, deployment, payment or teardown was performed.

Primary references: [Fargate task networking and requirements](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-tasks-services.html), [ECS task-definition resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ecs-taskdefinition.html), [ECS service resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ecs-service.html), [ECS task IAM roles](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/security-iam-roles.html), [passing an IAM role](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html), [deployment circuit breaker](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-circuit-breaker.html), [register-task-definition](https://docs.aws.amazon.com/cli/latest/reference/ecs/register-task-definition.html), [create-service](https://docs.aws.amazon.com/cli/latest/reference/ecs/create-service.html) and [describe-services](https://docs.aws.amazon.com/cli/latest/reference/ecs/describe-services.html).
