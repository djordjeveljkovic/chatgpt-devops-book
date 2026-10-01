---
book: The Complete DevOps Engineering Book
volume: 8
volume_title: "Infrastructure as Code"
chapter: 79
title: "Cloud-init and CloudFormation"
slug: cloud-init-and-cloudformation
status: complete
summary: ../../_ai/chapter-summaries/079-cloud-init-and-cloudformation.md
---

# Chapter 79 — Cloud-init and CloudFormation

## First-boot configuration and image boundaries

A new Harbor VPS exists before it is ready to run DispatchDesk. It needs an approved login path, packages, configuration, and process supervision. Cloud-init supplies early guest configuration based on a cloud datasource and user data. CloudFormation manages AWS resource stacks through AWS APIs. They address different layers: a guest can fail its initialization while the surrounding instance resource exists, and a stack can fail before a guest ever boots.

Choose a provisioning boundary before writing a large startup script. An image can contain a tested runtime and fixed operating-system baseline. Cloud-init can provide small instance-specific settings and enrollment. Ansible can converge host configuration after access becomes available. A cloud stack can create the network, identities, storage, and instances. Let each layer own a clearly defined object instead of making every layer rewrite the same file.

Cloud-init runs through boot stages, and module frequency depends on module and datasource behavior. Do not assume every user-data operation repeats on every reboot. An SSH connection becoming possible is also weaker evidence than final initialization completion. The [official boot-stage explanation](https://docs.cloud-init.io/en/latest/explanation/boot.html) establishes the model; image packaging and installed cloud-init version can change unit names and available features.

The following complete user-data file creates a nonsecret enrollment marker on an image that already includes cloud-init. It installs no packages, makes no remote download, and starts no application:

```yaml
#cloud-config
write_files:
  - path: /etc/dispatchdesk-bootstrap
    owner: root:root
    permissions: '0644'
    content: |
      project=DispatchDesk
      role=application-lab
      configuration_owner=Ansible
runcmd:
  - [test, -s, /etc/dispatchdesk-bootstrap]
```

The first line identifies cloud-config content. `write_files` supplies complete owned file bytes and explicit mode. `runcmd` supplies a command as an argument list rather than relying on shell interpretation. The marker records ownership intent; it does not enroll in Ansible or validate an application. Use it as a small proof that the intended user data reached a disposable instance.

Save as `user-data.yml` on the workstation. A compatible locally installed cloud-init can validate it with `cloud-init schema --config-file user-data.yml`. This checks the configuration schema, not the provider datasource or guest's eventual behavior. On the authorized disposable guest, inspect `cloud-init status --wait` and `sudo cat /etc/dispatchdesk-bootstrap`. `--wait` waits for cloud-init completion; a successful status plus the marker is evidence for this small operation only. [Cloud-init CLI reference](https://docs.cloud-init.io/en/latest/reference/cli.html) defines these commands.

Ubuntu 24.04 cloud images, Fedora 44 cloud images, and RHEL 9 cloud images can package different cloud-init versions and defaults. A manually installed operating system may have no suitable datasource. RHEL cloud images also have subscription and repository considerations if startup later installs packages. Fedora is not a proxy for RHEL testing. Inspect actual image identity and cloud-init version rather than assuming that the same YAML implies identical host readiness.

Never place a long-lived database password in this marker or an arbitrary user-data script. User data and boot logs can be accessible through administrative APIs or local files, depending on platform. Fetch secrets using an approved identity and secret mechanism with an explicit runtime contract. A copied image must also have the documented preparation applied so stale machine identity and first-boot state do not leak into new instances. Avoid cleaning cloud-init state on an existing production host merely to rerun a failed script.

## AWS stacks, change sets, and drift

CloudFormation uses a template to describe stack resources, with logical identifiers inside the template and physical identifiers in AWS. A stack is an operational ownership unit. Changing a logical identifier without preserving identity can create replacement behavior just as an infrastructure address rename can. [Import and refactoring](075-import-drift-and-safe-refactoring.md) explains the general identity hazard; CloudFormation has its own documented resource import/refactor features.

For a small inspection example, save this complete `network.yml` on an AWS operator workstation:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Disposable DispatchDesk CloudFormation network lab
Resources:
  OrdersNetwork:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.42.0.0/16
      EnableDnsSupport: true
      EnableDnsHostnames: true
      Tags:
        - Key: Project
          Value: DispatchDesk
        - Key: Environment
          Value: lab
Outputs:
  VpcId:
    Description: Identifier of the disposable network
    Value:
      Ref: OrdersNetwork
```

The template format string is a documented CloudFormation template version, not the date this book was written. `OrdersNetwork` is the logical identity. `Ref` returns the resource's documented reference result. No subnet, internet gateway, compute instance, or database is declared. A VPC alone does not make a runnable application architecture. [VPC resource reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ec2-vpc.html) defines these properties and return values.

Reader execution requires AWS CLI v2, an authorized disposable account, a verified short-lived profile, a selected region, and permissions for CloudFormation and the VPC operations it will execute. A service role introduces a separate privilege boundary; document it if used. The writing process executes no AWS operations. Estimate current charges for any resources added to the lab; extending a network with NAT, endpoints, public addresses, logs, or instances can produce ongoing bills.

Set the task-specific variables to approved values in the workstation shell, in the directory containing `network.yml`:

```bash
lab_profile='replace-with-approved-profile'
lab_region='eu-central-1'
lab_stack='dispatchdesk-network-lab'
lab_change='initial-network'
aws cloudformation create-change-set \
  --profile "$lab_profile" --region "$lab_region" \
  --stack-name "$lab_stack" --change-set-name "$lab_change" \
  --change-set-type CREATE --template-body file://network.yml \
  --no-cli-pager
aws cloudformation wait change-set-create-complete \
  --profile "$lab_profile" --region "$lab_region" \
  --stack-name "$lab_stack" --change-set-name "$lab_change"
aws cloudformation describe-change-set \
  --profile "$lab_profile" --region "$lab_region" \
  --stack-name "$lab_stack" --change-set-name "$lab_change" \
  --no-cli-pager
```

`--profile` and `--region` bind each API call to explicit context. `CREATE` is appropriate for a new stack; an existing stack change uses `UPDATE`. `file://` reads the local template. The waiter polls until the change-set creation reaches its documented success state or fails/times out. Description provides the proposed operations and their status. Creating a change set does not execute the proposed resource changes, but it does create AWS change-set/stack metadata. [Create-change-set](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/create-change-set.html) and [describe-change-set](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/describe-change-set.html) define the arguments.

Review the proposal before an authorized execution:

```bash
aws cloudformation execute-change-set \
  --profile "$lab_profile" --region "$lab_region" \
  --stack-name "$lab_stack" --change-set-name "$lab_change"
aws cloudformation wait stack-create-complete \
  --profile "$lab_profile" --region "$lab_region" \
  --stack-name "$lab_stack"
aws cloudformation describe-stacks \
  --profile "$lab_profile" --region "$lab_region" \
  --stack-name "$lab_stack" --no-cli-pager
```

The execute call is the change boundary. A successful waiter supports resource creation according to stack status. Inspect outputs and inventory; it does not establish DispatchDesk readiness. If the waiter fails, inspect stack events before retrying. Change sets cannot guarantee that every runtime constraint, permission, or quota will allow execution. [AWS change-set guidance](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html) explains their review role.

Drift detection compares supported resource properties against stack expectations. Its coverage is not every byte of guest configuration or every resource attribute. A manually altered application file on an instance is not automatically a detected stack drift. Check supported resource/property coverage and detect status before interpreting a clean result. [Stack drift documentation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/detect-drift-stack.html) describes those limits.

## Choosing the right provisioning layer

Harbor can use cloud-init for first access and Ansible for maintained host configuration. Summit can use CloudFormation for AWS resources and ECS deployment for containers, reducing the need for mutable guest scripts. Atlas can use infrastructure tooling for the managed cluster and Kubernetes controllers for workloads. Avoid a bootstrap script that downloads a moving application branch on every new instance; it makes scale-out depend on unreviewed source and external availability.

A large first-boot dependency chain creates poor failure evidence. If package installation fails, SSH enrollment never happens, and a supervisor is not installed, the application symptom hides several earlier causes. Reduce the chain with tested images, versioned artifacts, and explicit status signaling where the platform supports it. Distinguish the resource reaching a running state from the guest completing initialization and the application passing readiness.

For a cloud-init failure, begin with `cloud-init status --long`, the relevant journal units for that installed version, and `/var/log/cloud-init.log` or `/var/log/cloud-init-output.log`. Restrict access to collected logs because scripts may have printed secrets. [Cloud-init debugging](https://docs.cloud-init.io/en/latest/howto/debugging.html) provides the current investigation workflow. If user data was malformed, fix the source and launch a fresh disposable instance to validate first-boot behavior rather than assuming a reboot will rerun everything.

For a failed CloudFormation operation, inspect stack events and the failed logical resource. A denied EC2 API, an invalid CIDR, and a dependency blocking deletion require different repairs. Rollback can itself fail; identify remaining objects and consumers before cleanup. Do not delete stack records as a way to make the error disappear while leaving resources unmanaged.

For authorized disposable-stack teardown, run `aws cloudformation delete-stack --profile "$lab_profile" --region "$lab_region" --stack-name "$lab_stack"`, then `aws cloudformation wait stack-delete-complete --profile "$lab_profile" --region "$lab_region" --stack-name "$lab_stack"`. Deletion is destructive. Retention policies, external attachments, and errors may leave resources behind; inspect inventory and billing after the waiter, especially if the lab was extended. Guest-marker cleanup belongs to disposal of the guest, not deletion of an unrelated production file.

## Exercises and answer guidance

1. Does the marker prove Ansible enrollment? No; it states intended ownership and proves only the marker operation when observed.
2. A change set is ready but execution fails on permission. Did review fail? Review described intent, while execution encountered an authorization constraint; diagnose the exact failed API and approved role policy.
3. Stack drift reports no difference while an application file changed. Explain. Drift coverage is supported resource properties, not arbitrary guest bytes; verify the configuration-owner layer separately.

Review questions: Which layer owns first boot? Why can SSH work before initialization is complete? What do logical identifiers mean? Why should image preparation be rehearsed?

Small bootstrap contracts and explicit stack review keep failures diagnosable. Each layer must publish the evidence it can actually establish and leave the next layer's readiness claim to its owner.

## Sources and verification

Cloud-init boot, debugging, and CLI plus AWS change-set, drift, CLI, and VPC template references were inspected 2026-10-01. Cloud-init moving documentation showed 26.2; packaged image versions may differ. No schema CLI, guest bootstrap, stack creation, cloud execution, or teardown ran during authoring.
