---
book: The Complete DevOps Engineering Book
volume: 9
volume_title: "AWS Foundations"
chapter: 82
title: "AWS CLI and Identity Sessions"
slug: aws-cli-and-identity-sessions
status: complete
summary: ../../_ai/chapter-summaries/082-aws-cli-and-identity-sessions.md
---

# Chapter 82 — AWS CLI and Identity Sessions

## Profiles, regions, and output formats

An AWS CLI profile is a named collection of configuration, not an account guarantee. Summit's operator needs a session that resolves to the approved role in the approved sandbox before attempting any mutation. A command's exit status, a familiar profile label, and a successful login each establish different facts. This chapter makes their evidence explicit with read-only identity operations.

Read [account ownership](081-aws-accounts-regions-and-responsibility.md) first. Reader prerequisites are an authorized AWS environment, an approved identity arrangement, AWS CLI v2 installed for the workstation's architecture, and permission to use the assigned role. The authoring environment has no AWS CLI and executes no account login or AWS API operation. Following these examples does not require provisioning a paid resource; other services used later can be billable.

Use the official [AWS CLI installation instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) for Linux and verify the downloaded package's signature as documented. Ubuntu 24.04, Fedora 44, and RHEL 9 have different repository and package policies; a distribution `awscli` package can differ from the upstream CLI v2 installer. Check the executable rather than inferring its major version from the package name. RHEL repository entitlement is separate from AWS account authorization.

On the workstation, as the ordinary user who will hold the session, run:

```bash
command -v aws
aws --version
aws configure list-profiles
```

`command -v` shows the executable selected by the current shell. `--version` identifies the reported CLI and runtime packaging. `list-profiles` lists configured names, not verified remote identities. The working directory is irrelevant for these operations. Do not run setup as root merely to overcome a user configuration problem; that can create a separate configuration/cache under root's home and make later ordinary-user behavior differ.

Use explicit profile, region, and output arguments in operational scripts. Human tables are useful for reading, JSON is useful for structured processing, and text output needs careful field and pagination handling. An output formatter does not alter which remote objects an operation affects. A `--query` expression filters returned data for presentation; it is not an authorization boundary or a server-side resource filter unless the API has a distinct filtering argument.

A profile's region default helps convenience but can be overridden. Summit's change record should name the expected account, role, region, and resource identifiers. If a service uses a global endpoint or has a special regional scope, follow its documented behavior rather than assuming every call has the same regional meaning.

## SSO, role sessions, and credential precedence

IAM Identity Center can supply short-lived role credentials through a configured CLI session. Ask the account administrator for the actual portal/start or issuer URL, Identity Center region, account, and permission set. Do not invent these values from an application region. The identity service region and workload region can differ.

The workstation setup wizard is:

```bash
aws configure sso --profile dispatchdesk-sandbox
aws sso login --profile dispatchdesk-sandbox
```

The first command writes the selected profile/session configuration after the approved interactive choices. The second authenticates and caches the session material needed by subsequent calls. Current CLI v2 authentication behavior includes browser-oriented PKCE, with device-code options documented for different execution environments. Use the installed version's supported flow. [Identity Center configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html) and [SSO login](https://docs.aws.amazon.com/cli/latest/reference/sso/login.html) describe exact behavior.

For illustration, the resulting configuration has this shape in the user's AWS config file; every example value must be replaced with administrator-provided values:

```ini
[profile dispatchdesk-sandbox]
sso_session = dispatchdesk
sso_account_id = 111122223333
sso_role_name = SandboxOperator
region = eu-central-1
output = json

[sso-session dispatchdesk]
sso_start_url = https://replace-with-approved-portal.awsapps.com/start
sso_region = eu-central-1
sso_registration_scopes = sso:account:access
```

The account number is illustrative, not an observed account. This file contains configuration rather than a static access-key pair; authentication caches remain sensitive. The permission-set name is the actual authorized name, not a wish that the role should exist. Do not commit a personal AWS configuration directory or token cache to the application repository.

Credentials can come from environment variables, shared files, configured role assumptions, identity sessions, or execution-environment providers. Options and settings have documented precedence. A blanket statement that “the profile always wins” is unsafe. Inspect resolution and verify the caller rather than reasoning solely from one configuration file. [CLI configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) and [environment-variable reference](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html) define the specific precedence.

Temporary credentials include a session token as well as access-key material. An incomplete copied credential set can fail authentication. Prefer the approved session mechanism to manually copying secrets into shell history. Avoid `env` dumps and `set -x` around credential setup; revealing the whole environment creates an unnecessary secret exposure. For CI, use a documented federation/session mechanism with its own trust boundary, as developed in [short-lived identity](../18-security-and-software-supply-chains/176-federation-oidc-and-short-lived-identity.md).

## Verifying identity before a command

After login, inspect configuration resolution and ask STS for the actual caller. Run on the same workstation/user context that will execute the later change:

```bash
lab_profile='dispatchdesk-sandbox'
lab_region='eu-central-1'
aws configure list --profile "$lab_profile"
aws sts get-caller-identity \
  --profile "$lab_profile" --region "$lab_region" \
  --output json --no-cli-pager
```

`configure list` shows resolved settings and their sources; inspect any reported credentials carefully and do not share unnecessary identifiers. `get-caller-identity` returns account and caller identity information. It does not grant permission to create a VPC or access a database. `--no-cli-pager` keeps output in the invoking terminal rather than opening a pager. These are read-only observations, not creation commands. [Configure list](https://docs.aws.amazon.com/cli/latest/reference/configure/list.html) and [STS identity](https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html) supply the command references.

A human review compares the returned account to controlled inventory and the ARN to the expected role arrangement. Do not rely on a screenshot from yesterday. A role session can expire, another process can select a different environment, and a script can override its own options. Verification should occur immediately before a mutation in that execution path.

The following complete Bash preflight checks the account without printing credentials. Save as `verify-account.sh` on the workstation. It requires an approved profile and an expected account ID supplied as arguments:

```bash
#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 3 ]]; then
  printf '%s\n' 'Usage: verify-account.sh PROFILE REGION EXPECTED_ACCOUNT' >&2
  exit 2
fi
selected_profile=$1
selected_region=$2
expected_account=$3
actual_account=$(aws sts get-caller-identity \
  --profile "$selected_profile" --region "$selected_region" \
  --query Account --output text --no-cli-pager)
if [[ "$actual_account" != "$expected_account" ]]; then
  printf '%s\n' 'Caller account does not match the approved target.' >&2
  exit 1
fi
printf '%s\n' 'Caller account matches; review role and operation authorization separately.'
```

Run `bash verify-account.sh dispatchdesk-sandbox eu-central-1 ACTUAL_APPROVED_ACCOUNT_ID`, replacing the last explanatory placeholder with the controlled twelve-digit account ID. Quoting preserves arguments; the guarded comparison rejects a mismatch. The command substitution must succeed under this script's error handling before the account is accepted. This preflight checks account only: it does not prove role permissions, allowed region policy, backend identity, or resource selection. A pipeline should bind those additional checks to its actual operation.

Do not present a fixed example ARN or fabricated STS transcript as measured output. The expected evidence is a real account/ARN response for the reader's approved session and a successful account comparison. Preserve sanitized evidence with the change record according to access policy.

## Failure diagnosis and session recovery

An expired SSO session is different from AccessDenied on a resource operation. If login/session retrieval is expired, authenticate through the approved flow again and repeat caller verification. If STS succeeds but a VPC operation is denied, investigate authorization in [IAM policies](083-iam-policies-and-least-privilege.md). Repeated login cannot manufacture permissions that the role lacks.

A missing region diagnostic is a settings problem. Supply the intended region explicitly or fix the approved profile's default. A connection or certificate error is a network/trust problem; inspect proxy settings and the configured certificate bundle. Do not disable TLS verification as a normal repair. A local permission error in the AWS config/cache directory is a workstation ownership problem, often caused by mixed root and ordinary-user setup. Inspect paths before broadening permissions.

Suppose `dispatchdesk-sandbox` unexpectedly resolves to production. Stop before the resource operation. Read `configure list`, inspect the selected profile and session/account fields, and determine whether a wrapper, environment setting, or mistaken wizard selection caused the mismatch. Correct the specific source, log in if needed, and rerun STS. Deleting all credentials is a poor first diagnosis because it removes evidence and may interrupt unrelated approved sessions.

A successful identity check followed by a long operation can still encounter credential expiry. Use tool-supported refresh behavior and appropriate session duration under policy. If an apply partially completes before authentication fails, follow the operation's partial-failure recovery procedure; do not assume session renewal makes the old plan safe or that no resources changed. [State recovery](../08-infrastructure-as-code/073-state-locking-and-remote-backends.md) explains the IaC case.

For session cleanup, `aws sso logout` removes locally cached Identity Center tokens and temporary credentials described by the CLI. It can affect multiple configured SSO profiles, so coordinate its scope on a shared workflow. It does not delete cloud resources or universally revoke every already issued credential elsewhere. [SSO logout reference](https://docs.aws.amazon.com/cli/latest/reference/sso/logout.html) defines the local behavior. Remove the disposable preflight file if it is no longer needed; retain the approved profile only according to workstation policy.

## Exercises and answer guidance

1. STS succeeds but an S3 read is denied. What has passed? Authentication/identity observation passed; S3 authorization remains denied. Diagnose role and resource policy rather than reinstalling the CLI.
2. Can a `--query` hiding fields prevent their disclosure to the executor? No. It formats returned data; access must be controlled by the actual authorization boundary.
3. Why verify after selecting the profile instead of trusting its label? Labels are local intent; STS observes the resolved caller. Include account and role checks where the actual operation executes.

Review questions: Which region belongs to Identity Center? What does login cache? Which evidence identifies a role session? What can account preflight not prove?

CLI reliability comes from explicit execution context, short-lived approved identity, observed caller verification, and diagnostics that distinguish local configuration, authentication, authorization, and transport failures.

## Sources and verification

Official AWS CLI installation, settings/environment precedence, Identity Center configuration, configure-list, STS identity, and SSO login/logout pages were inspected 2026-10-01. CLI v2 is the assumed interface; readers record the installed version and verify authentication flow. No installation, browser login, credential cache, preflight, or AWS API call ran during authoring. No cloud resource was created.
