---
book: The Complete DevOps Engineering Book
volume: 9
volume_title: "AWS Foundations"
chapter: 90
title: "AWS Budgets, Tags and Inventory"
slug: aws-budgets-tags-and-inventory
status: complete
summary: ../../_ai/chapter-summaries/090-aws-budgets-tags-and-inventory.md
---

# Chapter 90 — AWS Budgets, Tags and Inventory

## Ownership and allocation tags

A cloud resource outlives the terminal command that created it. Summit needs to connect every DispatchDesk resource to an accountable owner, environment, purpose and retirement decision. Otherwise a stopped diagnostic instance can disappear from the team's attention while its volumes, snapshots or public addresses continue charging. Harbor has fewer resource types but still needs ownership records for domains, VPS accounts and backups. Cost accountability is part of operating the service, not an accounting exercise postponed until the invoice.

A practical fictional tag contract is `Project=DispatchDesk`, `Environment=sandbox`, `Owner=platform-team`, and `Purpose=temporary-lab`. Names are case-sensitive and should have documented allowed values. Prefer stable team identifiers over personal email addresses that become stale. Do not place credentials, customer identifiers or confidential incident details in tags; they can appear in inventory and billing views. Tags aid discovery and allocation but are neither proof of current ownership nor automatic authorization to delete.

Apply the contract through infrastructure definitions and deployment processes, then check coverage. Many resource types differ in tagging support, creation-time tagging and propagation. A launch-template tag declaration does not establish that every related resource inherited the same tags. Review volumes, interfaces and snapshots separately. If tag policy is used for access controls, the ability to change those tags becomes security-sensitive; this chapter's inventory convention does not prescribe an IAM design.

Resource tags and cost allocation tags are related but distinct. The billing system must recognize and activate the intended allocation tags before they support the required reports. [AWS's cost allocation guide](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-alloc-tags.html) explains the billing-side process and timing. Adding `Project` to a resource this morning is not evidence that yesterday's spend is already grouped correctly. Reconcile unallocated spend and activation state rather than treating missing report rows as zero cost.

## Budgets, quotas and billing evidence

A budget compares selected cost or usage against a declared target and can notify or trigger configured actions. It is not a prepaid wallet or a universal real-time spending cap. Billing data and notifications lag usage. [AWS Budgets documentation](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html) explicitly explains the delay. A rapidly growing workload can exceed a threshold before an alert reaches its recipient; the response process must account for that possibility.

Define whose costs the budget includes, the time period, currency or usage unit, treatment of credits and other charges, and whether its notification concerns actual or forecast spend. A forecast is a model informed by available history, not certainty about tomorrow. For a new sandbox, actual-spend alerts plus frequent inventory may be more useful initially than relying only on forecast behavior. [Budget best practices](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-best-practices.html) cover these distinctions and notification dependencies.

A service quota is another boundary. [Service Quotas](https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html) manages service limits and eligible increase requests. A resource-count quota can prevent further launches without representing an acceptable monetary limit. Increasing a quota to fix deployment capacity can also enlarge a runaway workload's impact. Review capacity requirements, cost consequences and workload controls together. Do not assume that an account's default quotas are identical across services, regions or accounts.

When costs rise, separate unit price, quantity and ownership. More data transfer, longer retention, unexpected replacement capacity and an abandoned NAT gateway have different remedies. Use billing evidence by service and region to direct resource inspection. Running only EC2 instance inventory cannot find every expensive service. The completed AWS foundations labs deliberately recorded exact resource IDs so their cleanup does not depend entirely on a future aggregate invoice.

## A budget with an accountable recipient

The optional example creates a monthly account cost budget of USD 25 with an actual-spend alert above 80 percent. These numbers are fictional learning thresholds, not AWS prices or a recommended DispatchDesk production budget. They do not cap the account at USD 25. Use an authorized sandbox account and a recipient who agreed to receive and act on the alert. The creation may generate external notifications later; do not enter an unrelated person's address.

Save the complete budget definition as `lab-budget.json`:

```json
{
  "BudgetName": "dispatchdesk-sandbox-lab",
  "BudgetType": "COST",
  "TimeUnit": "MONTHLY",
  "BudgetLimit": {"Amount": "25", "Unit": "USD"}
}
```

This intentionally monitors the account without a tag filter, so untagged sandbox spend is not hidden. A management account's view and a member account's costs require explicit scope decisions; use the approved account described here rather than assuming all organization costs mean the same thing. Inspect the returned cost-type settings and adjust the owning definition if the chosen treatment of credits, tax or support differs from your financial requirement.

Use AWS CLI v2 and Python 3 from an ordinary Bash workstation user on Ubuntu 24.04 LTS, Fedora 44 or RHEL 9. Complete [Chapter 82's account verification](082-aws-cli-and-identity-sessions.md) and obtain budget create/read/delete permissions. Review [Budgets pricing](https://aws.amazon.com/aws-cost-management/aws-budgets/pricing/) and your intended features; no free-service claim is made. No budget or message was created during authoring.

```bash
set -euo pipefail
umask 077
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Verified sandbox account ID: ' lab_account
read -r -p 'Authorized alert recipient email: ' lab_recipient
: "${lab_account:?account required}" "${lab_recipient:?recipient required}"
python3 - "$lab_recipient" <<'PYTHON'
import json
import sys
from pathlib import Path
recipient = sys.argv[1]
notification = [{
    "Notification": {
        "NotificationType": "ACTUAL",
        "ComparisonOperator": "GREATER_THAN",
        "Threshold": 80,
        "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [{"SubscriptionType": "EMAIL", "Address": recipient}]
}]
Path("lab-alerts.json").write_text(json.dumps(notification, indent=2) + "\n")
PYTHON
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   budgets create-budget --account-id "$lab_account"   --budget file://lab-budget.json   --notifications-with-subscribers file://lab-alerts.json
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   budgets describe-budget --account-id "$lab_account"   --budget-name dispatchdesk-sandbox-lab --output json
```

`umask 077` limits newly created local file access because notification configuration includes an address. Python serializes it as JSON instead of interpolating unescaped text into a JSON string. `--account-id` names the verified budget account, while the selected profile must actually have authority there. The notification's threshold is a percentage of the budget, and its comparison is strictly greater than. Review the API result and recipient configuration using the billing console or relevant subscriber APIs; a create request alone does not prove delivery.

Test the response procedure with the recipient through an agreed exercise rather than intentionally incurring charges. Record who investigates, how quickly they respond, and which inventory they inspect. If configuring automated actions later, assess availability impact and the permissions required for the action. A controller may replace a stopped instance, so “stop compute” is not a universal cost-control strategy.

To remove only the optional lab budget and its local files:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   budgets delete-budget --account-id "$lab_account"   --budget-name dispatchdesk-sandbox-lab
rm -- lab-budget.json lab-alerts.json
```

Budget deletion removes monitoring configuration, not the billable resources or accumulated costs. Keep production monitoring and resource cleanup separate in ownership records. A name collision during creation requires inspecting the existing budget rather than deleting it to make the example work.

## Finding retained volumes without deleting evidence

Suppose an EC2 lab instance was terminated but the next bill still shows EBS storage. The failed assumption is that instance termination removed every storage object. Inspect actual retained volumes and snapshots, their original attachment/deletion settings, tags and ownership. [Chapter 87](087-ebs-and-cloud-storage-choices.md) owns snapshot and volume lifecycle; a backup retained deliberately for recovery must not be treated like forgotten scratch space.

The Resource Groups Tagging API can find supported tagged or previously tagged resources in the selected region, but it is not a complete inventory of every untagged resource. [GetResources documentation](https://docs.aws.amazon.com/resourcegroupstagging/latest/APIReference/API_GetResources.html) describes its scope. Pair tagging queries with service-specific inventory and repeat the process for authorized accounts and regions, including services with different regional or global behavior.

Run the inventory independently of the optional budget workflow. Use a dedicated, empty working directory for its output. The profile must have permission to call `sts:GetCallerIdentity`, `ec2:DescribeVolumes` and `tag:GetResources` in the selected account and region. This preflight makes no budget, notification or resource changes:

```bash
set -euo pipefail
umask 077
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Expected authorized inventory account ID: ' lab_account
: "${lab_account:?account required}"
lab_actual_account=$(aws --profile "$lab_profile" --region "$lab_region" \
  --no-cli-pager sts get-caller-identity --query Account --output text)
[[ "$lab_actual_account" == "$lab_account" ]] || {
  printf 'Selected profile resolved to account %s, not expected account %s\n' \
    "$lab_actual_account" "$lab_account" >&2
  exit 1
}
```

This explicitly selects and verifies the profile, region and account without depending on budget creation or a recipient email. The following read-only capture inspects all EBS volumes visible to this caller in that selected region. `umask 077` keeps the generated JSON private to the current user; retain complete CLI pagination and the capture's account, region and time:

```bash
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   ec2 describe-volumes --output json > lab-volumes.json
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager   resourcegroupstaggingapi get-resources   --tag-filters 'Key=Project,Values=DispatchDesk' --output json   > lab-tagged-resources.json
```

Save this complete report helper as `review-volumes.py`, then run `python3 review-volumes.py lab-volumes.json`:

```python
import json
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("usage: review-volumes.py inventory.json")
inventory = json.loads(Path(sys.argv[1]).read_text())
for volume in inventory.get("Volumes", []):
    tags = {item["Key"]: item["Value"] for item in volume.get("Tags", [])}
    reasons = []
    if not tags.get("Owner"):
        reasons.append("missing Owner")
    if volume.get("State") == "available":
        reasons.append("currently unattached")
    if reasons:
        print(volume["VolumeId"], volume.get("Size"),
              tags.get("Project", "unclassified"), "; ".join(reasons))
```

The report identifies review candidates, not deletion candidates. An unattached disk may be a planned recovery volume; a missing owner may reflect faulty tagging rather than expendability. It deliberately performs no write API calls. Preserve account, region and capture time alongside the file because those facts are not inferred by the helper. A permissions-limited result is not a complete organization inventory.

For each finding, locate the infrastructure definition, change history and responsible team. Confirm whether data must be retained, whether a verified backup exists and whether another workflow will recreate the resource. Then use the owning service's reviewed teardown procedure for the exact approved ID. Afterward, verify resource absence and follow later billing evidence to distinguish ongoing charges from delayed reporting of prior usage. Remove local inventory files under your evidence-retention policy when the investigation closes.

## Exercises and answer guidance

1. The budget is USD 25. Can spend exceed it? Yes. The budget monitors and alerts according to billing data and configured behavior; it is not a universal cap.
2. Tagging API results show no DispatchDesk resources. What should be checked? Account, region, permissions, tag spelling, supported-resource scope and service-specific untagged inventory.
3. The helper reports an unattached volume with a valid owner. Should it be deleted? Ask the owner and inspect its purpose and retention requirements; state alone cannot authorize destruction.
4. Removing a budget stops an alert. Does that stop costs? No. The actual resource and contract inventory still determines costs.

Review questions: who acts on an alert, what costs its scope omits, which resource survived cleanup, and what evidence authorizes its retirement?

## Verification and primary sources

Official AWS Billing, Budgets, Service Quotas, tagging API and CLI documentation was inspected on 2026-10-01. No budget, notification, inventory API, tag mutation or resource deletion was executed. Local parser and syntax checks do not prove account scope, billing freshness, recipient delivery or inventory completeness.

Operation references: [create-budget](https://docs.aws.amazon.com/cli/latest/reference/budgets/create-budget.html), [describe-budget](https://docs.aws.amazon.com/cli/latest/reference/budgets/describe-budget.html), [delete-budget](https://docs.aws.amazon.com/cli/latest/reference/budgets/delete-budget.html), [describe-volumes](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-volumes.html), and [tagging inventory](https://docs.aws.amazon.com/cli/latest/reference/resourcegroupstaggingapi/get-resources.html).
