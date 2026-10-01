---
book: The Complete DevOps Engineering Book
volume: 10
volume_title: "AWS Production Services"
chapter: 91
title: "EC2 Auto Scaling and Launch Templates"
slug: ec2-auto-scaling-and-launch-templates
status: draft
summary: ../../_ai/chapter-summaries/091-ec2-auto-scaling-and-launch-templates.md
---

# Chapter 91 — EC2 Auto Scaling and Launch Templates

## Immutable launches and capacity ownership

One EC2 host can be replaced manually. A fleet needs a reproducible launch definition and a controller that maintains its intended capacity. An Auto Scaling group can launch replacements and adjust capacity within configured bounds. It cannot reconstruct a database left only on a terminated host or decide that a new application version handles orders correctly. Summit's main DispatchDesk path remains ECS; a host-based specialized worker is an alternative evaluated here, not a required detour before containers.

A launch template records EC2 launch inputs and supports versions. Record a concrete approved AMI, compatible instance type, instance profile, network permissions, metadata options and storage behavior. [AWS's launch-template guide](https://docs.aws.amazon.com/autoscaling/ec2/userguide/launch-templates.html) explains the versioned interface. A mutable latest-image lookup weakens reproducibility. Likewise, a group referencing an unreviewed template version can launch different machines without an application release decision.

Capacity has distinct fields: minimum, desired and maximum. Minimum expresses the maintained floor; maximum constrains ordinary scaling capacity; desired expresses what the controller currently attempts to maintain. The service's actual healthy usable capacity may be lower. If launch permissions fail, a desired value of two does not mean two hosts exist. If both hosts wait on one unavailable database, adding more does not restore order acceptance.

Decide who owns desired capacity. An infrastructure definition, scheduled action, dynamic scaling policy and emergency operator should not continuously overwrite one another. For the explicit lab below, CloudFormation declares initial desired zero; a manual API change briefly demonstrates the controller and is restored to zero before cleanup. That temporary deviation is deliberate lab drift, not a production ownership recommendation. A production design should give dynamic capacity a documented owner and configure infrastructure reconciliation accordingly.

Choose a scaling signal that reflects useful demand. CPU can suit a CPU-bound process, while queue backlog per effective worker may better represent notification processing. Total queue depth alone changes its relationship to capacity when workers are added. Database saturation or provider rate limits can make scaling out harmful. [Target-tracking documentation](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html) describes metric requirements and controller behavior. Measure workload response, warmup and dependency limits before encoding a target.

## Health, draining and replacement

Health used for host replacement differs from the business readiness contract. EC2 health cannot establish `/readyz` or the durability of an order/intent transaction. Integrating load-balancer health provides another input, but an incorrectly configured readiness path can cause healthy infrastructure to be replaced repeatedly. [Chapter 89](../09-aws-foundations/089-route-53-certificates-and-load-balancers.md) owns the load-balancer boundary.

Replacement has time and capacity costs. The new host must boot, acquire configuration and secrets, initialize the runtime and pass the required acceptance checks. Warmup affects when scaling metrics should treat its capacity as useful. A health-check grace period avoids judging some startup conditions too early; it does not repair a broken image or guarantee an application is ready when the interval ends. Derive intervals from observed startup behavior and dependency timeouts rather than copying a familiar number.

An instance refresh provides a controlled replacement mechanism for a new launch configuration. [AWS's refresh guide](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html) covers monitoring, checkpoints and rollback. Review healthy-percentage settings, spare capacity, quotas and failure actions before replacing a fleet. A rollback to an earlier template can restore compute configuration while leaving an incompatible database migration unchanged. Keep application/data compatibility in the release plan.

Scale-in can terminate useful work. [Termination policies](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-instance-termination.html) select instances; they do not implement DispatchDesk's drain protocol. [Lifecycle hooks](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html) can coordinate launch or termination work with bounded waiting and completion signals. Their timeout behavior must be explicit. An application still needs to stop claiming new work, preserve durable intent and reconcile ambiguous provider outcomes. A hook is a control point, not a transaction across AWS and a notification provider.

## A zero-capacity launch definition

Save this complete CloudFormation file as `host-fleet.yaml`. It defines a private diagnostic fleet with no application and initial zero capacity. Supply an approved AMI already containing the management agent, compatible instance type, existing SSM instance-profile ARN, existing management group and two approved private subnets in distinct zones of one VPC. They need appropriate management connectivity. The file creates no network, role, database or customer endpoint.

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Disposable private diagnostic fleet, initially zero hosts
Parameters:
  ImageId:
    Type: AWS::EC2::Image::Id
  InstanceType:
    Type: String
  InstanceProfileArn:
    Type: String
  ManagementGroup:
    Type: AWS::EC2::SecurityGroup::Id
  PrivateSubnetOne:
    Type: AWS::EC2::Subnet::Id
  PrivateSubnetTwo:
    Type: AWS::EC2::Subnet::Id
Resources:
  Launch:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateData:
        ImageId:
          Ref: ImageId
        InstanceType:
          Ref: InstanceType
        IamInstanceProfile:
          Arn:
            Ref: InstanceProfileArn
        MetadataOptions:
          HttpEndpoint: enabled
          HttpTokens: required
        NetworkInterfaces:
          - DeviceIndex: 0
            AssociatePublicIpAddress: false
            Groups:
              - Ref: ManagementGroup
        TagSpecifications:
          - ResourceType: instance
            Tags:
              - Key: Purpose
                Value: temporary-lab
          - ResourceType: volume
            Tags:
              - Key: Purpose
                Value: temporary-lab
  Fleet:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      MinSize: '0'
      DesiredCapacity: '0'
      MaxSize: '2'
      HealthCheckType: EC2
      VPCZoneIdentifier:
        - Ref: PrivateSubnetOne
        - Ref: PrivateSubnetTwo
      LaunchTemplate:
        LaunchTemplateId:
          Ref: Launch
        Version:
          Fn::GetAtt: [Launch, LatestVersionNumber]
      Tags:
        - Key: Project
          Value: DispatchDesk
          PropagateAtLaunch: true
        - Key: Purpose
          Value: temporary-lab
          PropagateAtLaunch: true
Outputs:
  GroupName:
    Value:
      Ref: Fleet
  TemplateId:
    Value:
      Ref: Launch
  TemplateVersion:
    Value:
      Fn::GetAtt: [Launch, LatestVersionNumber]
```

The group uses the concrete latest version number produced by this stack's launch template, rather than asking EC2 to interpret `$Latest` on every launch. Updating the launch definition still requires review and a separate replacement decision for existing instances. Tagging both instances and volumes improves retained-resource discovery. The AMI's approved root storage layout remains an input; inspect encryption and delete-on-termination settings rather than assuming instance tags solve storage lifecycle.

Initial zero hosts is a useful resource-definition test, but it postpones the most important launch dependencies. A successful stack at zero capacity cannot prove the AMI exists for launch authority, that the role can be passed, or that management connectivity works. The subsequent single-host exercise is explicitly billable. Follow [EC2 preparation](../09-aws-foundations/086-ec2-and-instance-lifecycle.md), check current [EC2 pricing](https://aws.amazon.com/ec2/pricing/), set a cleanup deadline and never treat a budget notification as a hard cap.

## Scaling and investigating failed launches

Run optional commands from an ordinary Bash workstation user with AWS CLI v2 on Ubuntu 24.04 LTS, Fedora 44 or RHEL 9. Complete the verified account preflight from [Chapter 82](../09-aws-foundations/082-aws-cli-and-identity-sessions.md). You need CloudFormation, launch-template, Auto Scaling, EC2 and instance-profile pass permissions, plus the applicable service-linked-role setup. The network/image baseline must be approved for this sandbox. No AWS commands were executed during authoring.

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
lab_stack=dispatchdesk-host-fleet-lab
read -r -p 'Approved AMI ID: ' lab_image
read -r -p 'Compatible approved instance type: ' lab_type
read -r -p 'Approved management instance-profile ARN: ' lab_profile_arn
read -r -p 'Approved management security-group ID: ' lab_group
read -r -p 'First approved private subnet: ' lab_subnet_one
read -r -p 'Second approved private subnet: ' lab_subnet_two
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation create-change-set --stack-name "$lab_stack"   --change-set-name initial-fleet --change-set-type CREATE   --template-body file://host-fleet.yaml --parameters   "ParameterKey=ImageId,ParameterValue=$lab_image"   "ParameterKey=InstanceType,ParameterValue=$lab_type"   "ParameterKey=InstanceProfileArn,ParameterValue=$lab_profile_arn"   "ParameterKey=ManagementGroup,ParameterValue=$lab_group"   "ParameterKey=PrivateSubnetOne,ParameterValue=$lab_subnet_one"   "ParameterKey=PrivateSubnetTwo,ParameterValue=$lab_subnet_two"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation wait change-set-create-complete   --stack-name "$lab_stack" --change-set-name initial-fleet
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation describe-change-set   --stack-name "$lab_stack" --change-set-name initial-fleet
```

Review the two new resources and actual parameters. With that plan approved in your lab scope, execute and inspect outputs:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation execute-change-set   --stack-name "$lab_stack" --change-set-name initial-fleet
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation wait stack-create-complete --stack-name "$lab_stack"
lab_fleet=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager cloudformation describe-stacks --stack-name "$lab_stack"   --query 'Stacks[0].Outputs[?OutputKey==`GroupName`].OutputValue | [0]'   --output text)
printf 'Record group for capacity and cleanup: %s\n' "$lab_fleet"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   autoscaling describe-auto-scaling-groups   --auto-scaling-group-names "$lab_fleet" --output json
```

The output query captures the generated group name, not a guessed name. Inspect minimum/desired/maximum and the initial empty instance list. To begin the optional billable one-host demonstration:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   autoscaling set-desired-capacity --auto-scaling-group-name "$lab_fleet"   --desired-capacity 1
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   autoscaling describe-scaling-activities   --auto-scaling-group-name "$lab_fleet" --output json
```

`--desired-capacity 1` asks the group to maintain one host. It is asynchronous; inspect activities and group membership until the intended instance is present or a specific failure is reported. Neither API success nor `InService` establishes application readiness. This lab has no application. Use the actual instance identity and Chapter 86's status/management checks to inspect the approved diagnostic image.

A realistic failed assumption is that a zero-capacity stack proved the role and key were usable. When capacity becomes one, activities can show launch failure due to role permission, inaccessible encrypted image storage, incompatible architecture or unavailable capacity. Preserve the activity reason, template version, image ID and affected zone. Repair that concrete prerequisite through its owner; raising maximum capacity merely repeats the failure and may worsen costs once the cause is fixed.

For a production worker, a different failure is a launch that succeeds while readiness never does. Inspect bootstrap and runtime logs, database connectivity and the actual artifact/configuration identity. Do not disable readiness or extend grace indefinitely to make the fleet look healthy. Pause replacement according to its controller's documented mechanism, retain known healthy capacity, correct the new definition and validate a small replacement before resuming.

Restore the deliberate lab drift and tear down the fleet:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   autoscaling set-desired-capacity --auto-scaling-group-name "$lab_fleet"   --desired-capacity 0
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   autoscaling describe-auto-scaling-groups   --auto-scaling-group-names "$lab_fleet" --output json
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation delete-stack --stack-name "$lab_stack"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   cloudformation wait stack-delete-complete --stack-name "$lab_stack"
rm -- host-fleet.yaml
```

Reducing desired capacity terminates the lab host. Observe eventual empty membership and stack deletion; a describe request immediately after scaling is only a snapshot. Inspect retained volume/snapshot inventory using [Chapter 90](../09-aws-foundations/090-aws-budgets-tags-and-inventory.md). Do not manually terminate a member while expecting the group to forget its desired count: the controller may replace it. A failed create, launch or delete keeps cleanup responsibility open for whatever actually exists.

## Exercises and answer guidance

1. Desired capacity is two but no instances exist. What evidence comes first? Scaling activities and the concrete launch definition identify failed dependencies; a desired number is not an inventory result.
2. Why does a launch-template update not prove all existing hosts changed? New launch inputs and replacement of current instances are separate operations.
3. Would higher worker count fix provider throttling? It can worsen throttling. Inspect dependency limits and choose demand/concurrency controls before scaling.
4. A rollback restores the old AMI after a schema migration. What remains uncertain? Data compatibility and business behavior; compute rollback does not reverse persistent state.

Review questions: who owns desired capacity, which signal measures useful demand, when is new capacity effective, and which durable work survives termination?

## Verification and primary sources

Official Auto Scaling, EC2 launch-template, lifecycle-hook, refresh, target-tracking, CloudFormation and CLI documentation was inspected on 2026-10-01. No fleet, instance, capacity change, hook or refresh was executed. Local YAML parsing cannot establish CloudFormation schema correctness, permissions, regional capacity or application readiness.

Operation references: [Auto Scaling group resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-autoscaling-autoscalinggroup.html), [launch-template resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ec2-launchtemplate.html), [set-desired-capacity](https://docs.aws.amazon.com/cli/latest/reference/autoscaling/set-desired-capacity.html), and [scaling-activity inspection](https://docs.aws.amazon.com/cli/latest/reference/autoscaling/describe-scaling-activities.html).
