# Independent review — Chapter 91

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 64b8cdd10cc1ac152b572477e7d04e23b9d8b4d266d9d21673689f9cadbf41e4

## Scope and findings

Confirmed no existing review record. Read manuscript, summary, skeleton brief and prerequisite/canonical context from Chapters82,86,89,90 against AI_AUTHORING_GUIDE.md. Reviewed launch template and group property types, concrete template-version selection, instance-profile/metadata/network/tagging choices, zero-capacity evidence limits, scaling ownership, health/warmup/drain distinctions, asynchronous launch/cleanup, failure recovery, source links and answer guidance.

No material finding. The template's MinSize/DesiredCapacity/MaxSize strings match CloudFormation property types. Ref/Fn::GetAtt use actual generated group/template identifiers and LatestVersionNumber, not an EC2 $Latest selector. Network interfaces specify private address publication and management groups while the ASG supplies subnet placement. No IAM resource is created, and existing-profile/pass/service-linked-role requirements are stated. AMI storage defaults remain an explicit approval input. Cost-changing scale-up and terminating scale-down are identified beside the procedure; failed lifecycle operations keep cleanup ownership open.

The diagnostic fleet has no application and does not pretend to implement readiness or a safe business worker. Target tracking describes useful proportional demand and dependency limits; lifecycle hooks and refresh are separated from application/data transactions. Exercises provide direct answers. Summaries accurately retain runtime/nonexecution limits.

- Low, “Scaling and investigating failed launches”, paragraph beginning “A realistic failed assumption”: replace “role and key were usable” with “role, image and management path were usable”. The supplied template uses SSM management and contains no EC2 KeyName. This wording does not invalidate the actual procedure.

## Dated primary-source evidence

Inspected on 2026-10-04:

- [aws-resource-autoscaling-autoscalinggroup.html](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-autoscaling-autoscalinggroup.html).
- [aws-resource-ec2-launchtemplate.html](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ec2-launchtemplate.html).
- [aws-properties-ec2-launchtemplate-networkinterface.html](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-ec2-launchtemplate-networkinterface.html).
- [create-change-set.html](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/create-change-set.html).
- [set-desired-capacity.html](https://docs.aws.amazon.com/cli/latest/reference/autoscaling/set-desired-capacity.html).
- [describe-scaling-activities.html](https://docs.aws.amazon.com/cli/latest/reference/autoscaling/describe-scaling-activities.html).
- [lifecycle-hooks.html](https://docs.aws.amazon.com/autoscaling/ec2/userguide/lifecycle-hooks.html).
- [as-scaling-target-tracking.html](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html).
- [asg-instance-refresh.html](https://docs.aws.amazon.com/autoscaling/ec2/userguide/asg-instance-refresh.html).

AWS documentation confirms resource properties/return values, LatestVersionNumber attribute, ASG subnet placement for template network interfaces, CLI change-set CREATE workflow, asynchronous desired capacity/activities, useful target-tracking metrics and bounded lifecycle-hook/refresh semantics. Documentation review is not CloudFormation service-side validation.

## Validation and limits

`python3 tools/check_book.py --chapters 91-91` passed: 1 YAML parse, 4 shell syntax blocks and 1,336 global local links; no errors/warnings. No AWS CLI operation, account verification, change set, stack, launch template, ASG, instance, capacity change, lifecycle hook, refresh, management connection or teardown performed. No budget/pricing calculation or Ubuntu/Fedora/RHEL VM matrix executed. No paid resource or external message created.

Static YAML/shell parsing and primary-source comparison cannot establish real account permissions, image/profile validity, security-group/subnet compatibility, available capacity, service-linked-role readiness, encrypted-AMI access, stack schema acceptance or application recovery. Optional low wording finding does not block approval. Only this review record changed.

Verdict: approved
