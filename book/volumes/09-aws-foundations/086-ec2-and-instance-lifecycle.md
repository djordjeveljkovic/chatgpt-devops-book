---
book: The Complete DevOps Engineering Book
volume: 9
volume_title: "AWS Foundations"
chapter: 86
title: "EC2 and Instance Lifecycle"
slug: ec2-and-instance-lifecycle
status: complete
summary: ../../_ai/chapter-summaries/086-ec2-and-instance-lifecycle.md
---

# Chapter 86 — EC2 and Instance Lifecycle

## Images, instance types and metadata

An EC2 instance is a rented execution environment with an image, a hardware shape, network interfaces, storage attachments, and a lifecycle controlled through AWS APIs. Summit may use EC2 for a diagnostic host or specialized worker while keeping its main DispatchDesk service on ECS. Harbor's VPS remains a valid alternative. The operational question is whether a replacement can reproduce the intended service without preserving accidental changes on the old machine.

An AMI selects the operating-system starting point and its boot storage layout. Its identifier is regional, and a friendly name is not sufficient evidence of publisher identity. Record the AMI ID, publisher, architecture, image creation information, and approval date in a release record. [Canonical's image discovery documentation](https://ubuntu.com/aws/docs/aws-how-to/instances/find-ubuntu-images/) explains official Ubuntu discovery through Parameter Store, the image API, or the console. Resolve a candidate, inspect it, and approve a concrete ID before launch; an automatically changing “latest” lookup at deployment time weakens reproducibility.

This book's Linux baselines are Ubuntu 24.04 LTS, Fedora 44, and RHEL 9. Ubuntu 26.04 and RHEL 10 are alternatives requiring their own tested image and package decisions. Obtain Fedora images from the Fedora project and RHEL images through Red Hat's documented AWS offerings or an approved organization image. Verify publisher and image lifecycle rather than copying an arbitrary search result. RHEL licensing and repository entitlement depend on the chosen offering; a bring-your-own-subscription image is not interchangeable with a pay-as-you-go one. The example below prompts for a verified AMI and does not invent a universal ID or subscription claim.

Match image architecture to the instance type and application artifact. An ARM image cannot run an x86-only native binary merely because both machines run Linux. Evaluate memory, CPU, network and storage requirements against measured workload behavior rather than choosing a familiar type name. Burst-based CPU capacity, architecture compatibility, region availability, quotas, and actual regional price all affect the decision. A tiny machine that repeatedly exhausts memory may cost less per hour but cause more failed requests and operational work.

EC2's `running` state establishes an infrastructure milestone, not DispatchDesk readiness. Likewise, passing instance status checks does not establish that `/readyz` is successful or that order writes are durable. [AWS's lifecycle guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html) distinguishes stop, reboot, and termination. Stopping an EBS-backed machine preserves its EBS storage but does not mean every associated resource stops charging. Termination cannot be undone by starting the instance again. Check actual volume deletion settings and retained resources before using it as cleanup.

## Access and workload identity

Choose a deliberate administrative path. SSH requires a compatible public key, the image's correct login user, network reachability and host-key verification. It does not require internet exposure if a private management route is available. Use the access controls from [host hardening](../04-vps-and-server-operations/032-host-hardening-and-access.md), not world-open TCP 22 as an onboarding shortcut. Ubuntu, Fedora, and RHEL images can have different default users; inspect the publisher's image instructions rather than guessing from the distribution name.

Session Manager is another option. It needs a supported managed node, the SSM agent and its configuration, appropriate instance permissions, service connectivity, and authorized operator permissions. Interactive CLI use also needs the workstation plugin. [Session Manager prerequisites](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html) and the [plugin installation guide](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html) are the source of truth. Removing SSH exposure does not automatically satisfy these dependencies. Session auditing and command-output handling need explicit configuration and review.

An instance profile connects an IAM role to EC2. The workload retrieves temporary role credentials through supported credential mechanisms; do not place static access keys in user data or home directories. [EC2's role guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html) distinguishes roles and instance profiles. Give the diagnostic image only its required management permissions, not the production application's full data permissions. A broad role attached to a disposable host is still broad authority.

Require IMDSv2 for this lab. It uses a session token obtained from the link-local metadata service. The requirement reduces some metadata-abuse paths but does not make a compromised host safe. If executing the following optional read on a launched instance, use a normal shell user with curl available and do not print credential endpoints:

```bash
metadata_token=$(curl --fail --silent --show-error --max-time 3   --request PUT   --header 'X-aws-ec2-metadata-token-ttl-seconds: 60'   http://169.254.169.254/latest/api/token)
curl --fail --silent --show-error --max-time 3   --header "X-aws-ec2-metadata-token: $metadata_token"   http://169.254.169.254/latest/meta-data/instance-id
unset metadata_token
```

The first request obtains a short-lived token; the second uses it to read identity metadata. `--fail` makes HTTP errors unsuccessful, the timeout bounds a stalled request, and unsetting reduces accidental later reuse. Do not run this on a workstation and expect EC2 identity. Proxy settings can also interfere with link-local access; inspect them without exposing proxy credentials. The [IMDS guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html) documents the token headers and service behavior. Container hop-limit requirements must be tested separately; this host-only lab does not prescribe a production container setting.

## Provisioning an inspectable replacement

The optional example launches exactly one private diagnostic instance with an existing approved subnet, group and instance profile. It contains no DispatchDesk application or data. You must supply a tested image that already has a functioning SSM agent; the user data only writes a nonsecret marker. It is a billable EC2 launch with EBS storage and potentially related network charges. Establish a budget and termination owner first. No launch or cloud integration was performed while writing this chapter.

From an ordinary Bash workstation account with AWS CLI v2, use the preflight in [Chapter 82](082-aws-cli-and-identity-sessions.md). Required permissions include describing resources, launching with the selected profile, passing its role, reading instance status, and terminating your lab instance. The existing private subnet must have an approved path to the necessary SSM services, through suitable endpoints or egress. An isolated subnet from Chapter 84 alone will not satisfy management connectivity.

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Approved AMI ID in this region: ' lab_ami
read -r -p 'Approved compatible instance type: ' lab_type
read -r -p 'Verified sandbox subnet ID: ' lab_subnet
read -r -p 'Verified management security-group ID: ' lab_group
read -r -p 'Approved SSM instance-profile name: ' lab_instance_profile
: "${lab_ami:?AMI required}" "${lab_type:?type required}"
: "${lab_subnet:?subnet required}" "${lab_group:?group required}"
: "${lab_instance_profile:?instance profile required}"
cat > lab-user-data.yaml <<'YAML'
#cloud-config
write_files:
  - path: /etc/dispatchdesk-lab-marker
    owner: root:root
    permissions: '0644'
    content: |
      Purpose: disposable EC2 lifecycle lab
YAML
lab_instance=$(aws --profile "$lab_profile" --region "$lab_region"   --no-cli-pager ec2 run-instances --image-id "$lab_ami"   --instance-type "$lab_type" --count 1 --subnet-id "$lab_subnet"   --security-group-ids "$lab_group" --no-associate-public-ip-address   --iam-instance-profile "Name=$lab_instance_profile"   --metadata-options 'HttpEndpoint=enabled,HttpTokens=required'   --user-data file://lab-user-data.yaml   --tag-specifications   'ResourceType=instance,Tags=[{Key=Name,Value=dispatchdesk-lifecycle-lab},{Key=Purpose,Value=temporary-lab}]'   --query 'Instances[0].InstanceId' --output text)
printf 'Record instance for termination: %s\n' "$lab_instance"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 wait instance-status-ok --instance-ids "$lab_instance"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 describe-instances --instance-ids "$lab_instance" --output json
```

`--count 1` avoids an accidental multi-instance launch. The subnet and group determine actual networking; omitting a public address is an explicit choice. `--iam-instance-profile` supplies the approved management identity, while metadata options require token-based metadata access. User data is a local file read by the CLI and interpreted by the image's cloud-init support; it must not contain secrets. Its marker does not install management software. Review the AMI's root-volume encryption and deletion configuration before launch because this minimal request inherits its storage layout.

The waiter blocks until the documented status condition succeeds or its polling limit fails. A waiter failure is not rollback: inspect the recorded instance and continue diagnosis or cleanup. A request interrupted before the identifier is captured also needs inventory by the unique lab name, creation time and operator activity; do not repeatedly launch until one appears. Production automation should use an appropriate idempotency token and record its lifecycle.

With management prerequisites met, an authorized operator can open a session:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ssm start-session --target "$lab_instance"
```

Inside that session, inspect `cloud-init status --long` and `cat /etc/dispatchdesk-lab-marker`. The marker should contain the declared nonsecret purpose. Exit the session before cleanup. Record image-specific logs and agent status when the session fails; a missing session does not establish that the EC2 instance is stopped.

## Failed bootstrap and safe replacement

Suppose a replacement reaches `running` but never becomes managed. Investigate the boundary in order: actual image and architecture, agent presence, instance-profile attachment, role permissions, DNS and network path to SSM, then operator permissions and plugin installation. Cloud-init failures require inspecting its status and logs; an invalid YAML file and a missing package repository are different causes. [Bootstrap mechanisms](../08-infrastructure-as-code/079-cloud-init-and-cloudformation.md) explain the separation between launch input and ongoing configuration.

For an actual DispatchDesk replacement, first reproduce its release artifact, configuration references and service unit using the existing automation. Test readiness and a durable order flow before routing customers to it. Retain the old healthy instance until the replacement is accepted and traffic has drained. Do not terminate the only data copy while proving that an image boots. Ubuntu's AppArmor and Fedora/RHEL's SELinux requirements still apply to service deployment; EC2 does not erase local Linux policy.

After this diagnostic lab, terminate the recorded instance:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 terminate-instances --instance-ids "$lab_instance"
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 wait instance-terminated --instance-ids "$lab_instance"
rm -- lab-user-data.yaml
```

Termination is irreversible for the instance. Confirm its actual state and inspect associated EBS volumes, snapshots, addresses and other resources for retention and charges. Remove only lab-owned retained resources under the applicable storage procedure. If termination protection blocks the request, investigate why it exists rather than bypassing an unexplained control. Leave cleanup ownership explicit until retained inventory is resolved.

## Exercises and answer guidance

1. Status checks pass but `/readyz` fails. What was proven? Infrastructure checks passed; application readiness and data dependencies still require verification.
2. Session Manager reports the target is unavailable. Should you open public SSH immediately? First inspect agent, identity and management connectivity; a new public path introduces a separate exposure decision.
3. Why approve an AMI ID rather than launch whichever image is latest? A fixed approved identity makes replacement evidence reproducible while updates still undergo testing.
4. Does stopping eliminate the bill? No. Associated storage and other retained services can keep charging; inspect actual inventory and pricing.

Review questions: which system owns persistent order data, which identity can the host obtain, what proves replacement acceptance, and how will retained resources be found after termination?

## Verification and primary sources

Official EC2, SSM, CLI and Canonical documentation was inspected on 2026-10-01. The Fedora cloud documentation entry was inaccessible to this browser, so no exact Fedora image ID or installation assertion is made. No AWS instance, metadata request, session, cloud-init runtime or workload replacement was executed. The commands assume AWS CLI v2 and a separately approved image.

Additional CLI references: [run-instances](https://docs.aws.amazon.com/cli/latest/reference/ec2/run-instances.html), [instance-status-ok](https://docs.aws.amazon.com/cli/latest/reference/ec2/wait/instance-status-ok.html), and [terminate-instances](https://docs.aws.amazon.com/cli/latest/reference/ec2/terminate-instances.html). Check [EC2 pricing](https://aws.amazon.com/ec2/pricing/) and the selected image's licensing before using the lab.
