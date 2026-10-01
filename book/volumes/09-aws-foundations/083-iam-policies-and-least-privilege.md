---
book: The Complete DevOps Engineering Book
volume: 9
volume_title: "AWS Foundations"
chapter: 83
title: "IAM Policies and Least Privilege"
slug: iam-policies-and-least-privilege
status: complete
summary: ../../_ai/chapter-summaries/083-iam-policies-and-least-privilege.md
---

# Chapter 83 — IAM Policies and Least Privilege

## Actions, resources, and conditions

Summit's release job needs to read DispatchDesk artifacts from one S3 prefix. It does not need to delete orders, administer users, or read every bucket. Least privilege begins with the specific operation and its evidence: list the permitted artifact prefix, fetch a selected artifact, and reject deletion or access outside the intended scope. A broad managed policy may make the first deployment easy while leaving those boundaries unexamined.

Read [CLI identity sessions](082-aws-cli-and-identity-sessions.md) first. This chapter authors and inspects policy without attaching it to any real role. Reader-side validation requires an authorized sandbox identity with the documented Access Analyzer or simulator permissions. No AWS policy mutation, role creation, or paid resource is performed during authoring.

A policy statement identifies an effect, actions, resources, and optional conditions. The action names a service operation permission; the resource identifies the scope to which that action applies. Different actions support different resource types and condition keys. A plausible-looking ARN is not proof that an action supports resource-level scoping. Consult the service authorization reference for the exact action.

The following complete identity policy is an original example for a release reader. Replace the bucket name and prefix with approved real values before validation. Save as `artifact-read.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListReleasePrefix",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::replace-with-approved-artifact-bucket",
      "Condition": {
        "StringLike": {
          "s3:prefix": ["dispatchdesk/releases/*"]
        }
      }
    },
    {
      "Sid": "ReadReleaseObjects",
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::replace-with-approved-artifact-bucket/dispatchdesk/releases/*"
    }
  ]
}
```

The policy version string identifies IAM policy-language semantics. It is not a date to update with each deployment. Listing uses the bucket ARN; object reads use object ARNs. The condition restricts the requested prefix for listing. A caller that asks to list the bucket root may be denied even though a request using the intended release prefix is allowed. Design the client request to match the intended scope instead of expanding the policy to accommodate an accidental default.

No delete permission is granted here, but that alone does not prove the role cannot delete. Another applicable policy may grant it, or a resource policy may change effective access under its documented rules. Least privilege is a property of effective authorization for the actual principal/request, not just one JSON file. [S3 operation permission mapping](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-with-s3-policy-actions.html) explains the bucket/object distinctions.

Encryption can add another authority boundary. A KMS-encrypted object may require appropriate key authorization in addition to S3 access. Do not diagnose a failed download by inspecting only this policy. Document whether the bucket uses an encryption key and which identity needs its use. The owning [S3 chapter](088-s3-from-the-cli.md) develops the full workflow.

## Role trust and permission evaluation

A role's trust policy answers who may obtain its session. Its permissions policies answer what that session may do. These are separate questions. Granting `s3:GetObject` to a role does not allow an arbitrary external actor to assume it. Trusting a principal to assume a role does not, by itself, grant that role every resource action.

For illustration, this complete trust-policy shape permits one explicitly named role from another account to call AssumeRole. Every identifier is placeholder/example data and must be replaced with the intended verified principal. It is not a recommendation to create static users:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::111122223333:role/ApprovedReleaseCaller"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

The source principal also needs the appropriate permission to assume the destination role under the cross-account arrangement. Federated web identities use a different principal/action/condition contract; do not paste this trust policy into an OIDC workflow. [Role creation and trust documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user.html) describes the model; [federated identity](../18-security-and-software-supply-chains/176-federation-oidc-and-short-lived-identity.md) owns the detailed web-identity implementation.

Policy evaluation includes more than identity attachments. Resource policies, session restrictions, permissions boundaries, organization controls, and service-specific authorization can apply. An explicit deny can override an allow. A boundary or organizational maximum does not normally grant the permission missing from an identity policy. Same-account, cross-account, user, role, and role-session cases have documented nuances; do not reduce every case to one simplistic union diagram. [IAM evaluation logic](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html) is the starting reference.

For DispatchDesk, separate execution identities by job. A runtime API role reads its needed secret and uses its database/network contract. A worker role receives and acknowledges queue work. A release role promotes the approved artifact and updates the service. An administrator manages identities through reviewed governance. Combining all four into one “application role” hides which actor can perform a harmful operation and broadens incident scope.

## Validate before attaching

On the operator workstation, as the ordinary user in the directory containing `artifact-read.json`, first check JSON syntax:

```bash
python3 -m json.tool artifact-read.json
```

This requires Python 3 and does not call AWS. It does not establish action spelling, ARN applicability, condition correctness, or effective permissions. The command works on Ubuntu 24.04, Fedora 44, and RHEL 9 when Python is installed. Local sudo does not grant cloud authority.

An authorized reader can request service policy validation with explicit context:

```bash
lab_profile='dispatchdesk-sandbox'
lab_region='eu-central-1'
aws accessanalyzer validate-policy \
  --profile "$lab_profile" --region "$lab_region" \
  --policy-document file://artifact-read.json \
  --policy-type IDENTITY_POLICY --output json --no-cli-pager
```

`file://` loads the local document. `IDENTITY_POLICY` selects the type being checked; a role trust policy is resource-policy content and requires its appropriate validation context. The API returns findings rather than attaching the policy. Inspect every reported error, warning, and relevant suggestion. A zero CLI exit means the request succeeded, not necessarily that its findings list is empty. [Validate-policy reference](https://docs.aws.amazon.com/cli/latest/reference/accessanalyzer/validate-policy.html) defines the interface.

For a focused simulator check of the document, request both allowed and deliberately ungranted actions:

```bash
aws iam simulate-custom-policy \
  --profile "$lab_profile" --region "$lab_region" \
  --policy-input-list file://artifact-read.json \
  --action-names s3:GetObject s3:DeleteObject \
  --resource-arns arn:aws:s3:::replace-with-approved-artifact-bucket/dispatchdesk/releases/example.tar \
  --output json --no-cli-pager
```

The resource is a test ARN matching the authored object scope, not an existing object required by this paper policy. The expected evaluation for this policy alone is a permitted read and an implicitly denied delete. The simulation does not perform either operation. It also does not establish the complete live role/resource/organization context. Conditions can require explicit simulation context, and unsupported cases need other verification. [Simulator command reference](https://docs.aws.amazon.com/cli/latest/reference/iam/simulate-custom-policy.html) describes inputs and limits.

For production review, test the actual identity in a controlled disposable resource scope with positive and negative operations. A negative test must not risk deleting real data if the policy is unexpectedly broad. Use an expendable test object and a planned cleanup contract. Estimate service/request/logging costs from current pricing; do not assume that every analyzer feature or surrounding resource is free. This chapter creates no resources, so its cleanup is limited to locally saved fictional policy files.

## Debugging an access-denied response

The release job authenticates successfully but cannot fetch an artifact. Record the actual caller account/ARN, operation, target bucket/key, encryption arrangement, and sanitized error/request identifier. Do not paste credentials or the full environment into the ticket. Compare the failed request with the intended policy contract before editing permissions.

A common mistake places the object ARN in the ListBucket statement. The list request addresses the bucket, so the allow does not match. Correct that specific resource scope and retain the prefix condition. Another mistake lists the bucket root while the condition permits only `dispatchdesk/releases/`; change the caller's prefix when that is the intended contract. Granting `s3:*` on `*` obscures both mistakes instead of repairing them.

If the identity policy matches, examine the other applicable boundaries and resource policies with their administrators. A key policy, VPC endpoint policy, organization control, or explicit deny can be the controlling boundary. Enhanced denial messages vary by service and request context; use their detail when available without assuming every error identifies the exact policy. [AWS denied-access troubleshooting](https://docs.aws.amazon.com/IAM/latest/UserGuide/troubleshoot_access-denied.html) provides the documented investigation paths.

Recovery applies the narrow approved correction, validates it, and repeats positive and negative tests using a new or appropriately refreshed session where required. A policy change can take time to propagate; distinguish temporary propagation from a persistent scope error using bounded observation and actual diagnostics. Do not add repeated broad grants because the first immediate retry failed.

When a temporary emergency grant was used, record its owner and removal condition. Verify removal by testing the intended denied capability in a safe scope. A comment saying “temporary” is not an expiry mechanism. Preserve enough audit evidence to explain who changed authorization and why, while removing sensitive data from general collaboration records.

## Exercises and answer guidance

1. Why are bucket and object ARNs different in this policy? ListBucket authorizes listing the container; GetObject authorizes named objects. Match the resource type supported by each action.
2. Does a successful custom-policy simulation prove the real release role's access? No. It evaluates supplied policy/context with documented limits; live applicable policies and resource/encryption context still matter.
3. The role trust policy is correct but AssumeRole is denied. What else should be checked? Source principal's assumption permission, conditions, organizational controls, exact role/principal identity, and the sanitized denial context.

Review questions: What grants a role session its operations? What establishes trust? What can explicit deny override? How do negative tests remain safe?

Least privilege is a reviewed request contract: precise actions, correct resource scope, meaningful conditions, and verified effective behavior under the actual identity. Repair denied access by finding the controlling boundary rather than expanding authority blindly.

## Sources and verification

Official IAM policy elements/evaluation/trust/troubleshooting, S3 operation permissions, Access Analyzer validation, and custom-policy simulation documentation were inspected 2026-10-01. No policy attachment, role assumption, analyzer call, simulator call, or live positive/negative test ran during authoring. JSON/CLI syntax and local links are checked separately; no fake output is supplied.
