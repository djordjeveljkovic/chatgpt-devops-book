---
book: The Complete DevOps Engineering Book
volume: 10
volume_title: "AWS Production Services"
chapter: 100
title: "Secrets, CloudWatch and Cloud Resilience"
slug: secrets-cloudwatch-and-cloud-resilience
status: complete
summary: ../../_ai/chapter-summaries/100-secrets-cloudwatch-and-cloud-resilience.md
---

# Chapter 100 — Secrets, CloudWatch and Cloud Resilience

## KMS, Secrets Manager and rotation

Production configuration includes values with different lifetimes and risks. A database password, signing key or provider token is a secret; a region name or log level is ordinary configuration. Do not place secrets in source control, container images, command history, deployment logs or metric labels. Give each workload an IAM role with access only to the secrets it needs. Keep secret retrieval behind a narrow application boundary, avoid logging the response, and define how cached credentials refresh after rotation.

AWS Secrets Manager stores secret versions and encrypts values using AWS KMS. Retrieving a secret requires both Secrets Manager permission and permission to use the encryption key where applicable. A customer-managed KMS key can provide separate policy and audit control, but it adds lifecycle responsibility and may add cost. Use Secrets Manager for credentials that need managed lifecycle and rotation integration; use encrypted deployment configuration or another approved store when its access, audit, refresh and rotation properties fit better. Do not fetch a secret on every request without understanding latency, throttling and cost, and do not cache it indefinitely when rotation must take effect promptly. AWS documents [Secrets Manager access control](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access.html) and [secret versions](https://docs.aws.amazon.com/secretsmanager/latest/userguide/whats-in-a-secret.html).

Credential rotation updates both the secret store and the target database or service. Secrets Manager provides managed rotation for supported resource types and Lambda-based rotation for other types. A typical Lambda rotation has four stages: create a pending value, apply it to the target, test it, then move `AWSCURRENT` to the new version. Rotation code must be idempotent and tightly scoped because it can modify credentials. Test new credentials before promoting them, coordinate application pools and connection refresh, and preserve a recovery procedure for failed rotation. If the app keeps an old connection open, rotation may appear successful while new connections fail. See the [rotation lifecycle](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html) and [Lambda rotation stages](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_lambda-functions.html).

KMS key rotation and secret rotation solve different problems. KMS automatic rotation changes key material used by the same logical key; KMS retains older material to decrypt existing ciphertext. It does not rotate data keys or re-encrypt protected data, and it does not replace a compromised application password. Creating a new KMS key and migrating encrypted data is a separate operation with different access and recovery consequences. Document key owners, grants, deletion protection, backup access and recovery expectations. Review [KMS key rotation behavior](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html) before treating a “rotated” flag as evidence that every dependent credential or ciphertext has changed.

For an incident, revoke or rotate the exposed credential, identify its consumers and audit access logs. Do not paste the value into a ticket or command transcript. If a key or database credential changes, check every deployment, scheduled job, worker and recovery environment that uses it. A rotation can cause an outage if one consumer cannot refresh; stale credentials can also remain in long-lived pools. Pair rotation success with application-level authentication success and a known rollback or forward-recovery plan.

## Logs, metrics and managed alarms

CloudWatch contains different evidence types. Metrics are time-series aggregates suited to alerting and trend analysis. Logs preserve structured events for investigation and may contain sensitive values. Alarms evaluate metrics over periods and move among `OK`, `ALARM` and `INSUFFICIENT_DATA`; alarm state is an operational signal, not a root-cause explanation. Use a small set of service and business signals together: request success/latency, queue age, database connections, task health, throttles and notification completion. A service can be healthy by CPU while its user-visible work is blocked.

Treat log schema, access and retention as part of application design. Emit a timestamp, service, environment, request/correlation ID, outcome and bounded error category. Avoid secrets, full authorization headers and unbounded customer data. Set retention to meet incident, audit and privacy requirements. CloudWatch Logs retains data indefinitely by default unless a log group has an explicit retention policy. Retention policy changes affect cost and evidence availability; verify new groups created by deployments inherit the intended setting. See [log-group retention behavior](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html).

Choose alarm periods and evaluation windows that fit the symptom. A one-minute alarm can detect a sustained API failure quickly but may be noisy for sparse traffic. A five-minute average can hide a short but severe burst. Use missing-data treatment deliberately: no datapoint might mean no traffic, telemetry failure or a broken target. For a heartbeat metric, missing data may be a problem; for a low-volume optional metric, it may be expected. Alert on a condition that has an owner and an action, and route pages only for customer-impacting or time-sensitive failures. [CloudWatch missing-data guidance](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarms-and-missing-data.html) explains how missing points affect evaluation.

Cost follows ingestion, storage, query and alarm choices. High-cardinality custom metrics multiply time series. Debug-level logs in a hot path can create more ingest and query cost than expected. Long retention increases stored evidence; short retention can erase incident context. Estimate event volume, bytes per event, retention days, metric dimensions, alarm count and query frequency before enabling broad telemetry. Use sampling or bounded detail only where it preserves the signal needed for diagnosis. Check current regional prices and service terms before committing a budget; this chapter does not assume a price or free tier.

## A multi-zone recovery and cost review

Consider DispatchDesk order acceptance on ECS across two Availability Zones, RDS Multi-AZ, an SQS notification queue and a public CloudFront distribution. An AZ issue removes some tasks and one subnet. The remaining tasks serve traffic, but the ALB reports unhealthy targets, queue age increases and a database connection alert fires. The failed assumption is that “Multi-AZ” means every dependency has spare capacity and application behavior is automatically safe. A second AZ needs adequate subnet addresses, task placement capacity, database headroom, healthy secrets access, working alarms and a tested routing/recovery path.

Define objectives before selecting a topology. RTO is the time to restore the service to useful operation; RPO is the acceptable lost data. Multi-AZ deployment can protect against some component/AZ failures, while a Region recovery plan addresses a larger failure domain and usually needs separate copies of data and configuration. Backups protect against logical corruption and accidental deletion; replication can copy those mistakes. Neither a backup schedule nor a green health check proves recovery. Restore data and application configuration in a rehearsal, run realistic transactions, verify permissions and DNS, and record measured time and data loss. AWS Well-Architected recommends [periodic recovery tests](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/back-up-data.html), and distinguishes [multi-location availability](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_fault_isolation_multiaz_region_system.html) from [disaster recovery objectives](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/plan-for-disaster-recovery-dr.html).

During the event, confirm whether the impairment is an AZ symptom or a broader application/dependency fault. Inspect target health, task placement and subnet capacity; compare database connection and failover metrics; verify the worker still consumes the queue; and check the exact alarm period and missing-data state. Reduce optional work if the remaining database or provider capacity is constrained. Use the published recovery runbook and record decisions. Do not fail over to another Region simply because one alarm is red; the alternative environment must have compatible data, secrets, permissions, images, DNS and capacity.

After service returns, reconcile queued notifications and duplicate side effects, confirm order records against the durable source, and test one controlled end-to-end order. Review whether any credential rotation or KMS access issue contributed. Preserve logs and metric ranges before retention or lifecycle policies remove them. A post-incident review should compare actual recovery evidence with the RTO/RPO, and turn every gap into an owner and deadline.

Use a cost review that compares comparable recovery choices:

| Design | Resilience benefit | Main ongoing cost and operational work |
|---|---|---|
| One-AZ application and single database | Lowest baseline footprint; appropriate only for a stated low-risk or nonproduction objective | A local failure can stop the service; recovery depends on replacement capacity and restore time |
| Multi-AZ application and managed database | Handles some AZ-level failures without rebuilding the whole service | Extra compute/data replication capacity, cross-AZ traffic, subnet headroom and failover exercises |
| Warm standby in another Region | Can reduce recovery time for a regional incident | Duplicated baseline, replicated data, cross-Region transfer, configuration drift controls and regular tests |
| Multi-site active/active | Can serve across independent locations with carefully designed data behavior | Highest architecture and data-consistency complexity, traffic steering, duplicated capacity and specialized operations |

These are tradeoffs, not a maturity ladder. Use current calculator/pricing sources for actual regions, traffic, storage, logging, retention and support. Include staff time for tests and on-call readiness. If a two-person team cannot operate a complex design, a less ambitious architecture with tested backups and honest recovery expectations may produce better real-world reliability. AWS advises matching [location strategy to business recovery needs and cost](https://docs.aws.amazon.com/wellarchitected/latest/framework/rel_planning_for_recovery_disaster_recovery.html).

For read-only inventory, inspect secret metadata, log-group retention and alarms without retrieving secret values or changing settings:

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Expected AWS account ID: ' lab_expected_account
read -r -p 'Existing secret name or ARN: ' lab_secret_id
read -r -p 'Existing CloudWatch log-group prefix: ' lab_log_prefix
lab_actual_account=$(aws --profile "$lab_profile" --region "$lab_region" \
  --no-cli-pager sts get-caller-identity --query Account --output text)
[[ "$lab_actual_account" == "$lab_expected_account" ]] || {
  printf 'Profile resolved to account %s, not expected account %s\n' \
    "$lab_actual_account" "$lab_expected_account" >&2
  exit 1
}
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  secretsmanager describe-secret --secret-id "$lab_secret_id" \
  --query '{name:Name,rotationEnabled:RotationEnabled,lastChanged:LastChangedDate,lastAccessed:LastAccessedDate,kmsKeyId:KmsKeyId}'
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  logs describe-log-groups --log-group-name-prefix "$lab_log_prefix" \
  --query 'logGroups[*].{name:logGroupName,retentionDays:retentionInDays,storedBytes:storedBytes}'
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  cloudwatch describe-alarms --alarm-types MetricAlarm CompositeAlarm \
  --state-value ALARM --output json
```

This requires read permissions for identity, secret metadata, log groups and both metric and composite alarms; it does not return the secret value. Restrict output because resource names, key IDs and alarm details reveal topology. An empty alarm list only says that this query found no alarms currently in `ALARM`; it does not prove all alarms are configured or healthy. For a complete review, inspect `OK` and `INSUFFICIENT_DATA` alarms and compare against the service inventory. Never add `get-secret-value`, key policy edits or alarm mutation to this triage snippet without a separate purpose and access review.

## Exercises and answer guidance

1. Secrets Manager reports rotation success, but new database connections fail. What should be checked? Confirm `AWSCURRENT`, test the new credential, verify app refresh/pool behavior and inspect whether every consumer uses the intended secret version.
2. KMS automatic rotation ran. Has the database password changed? No. KMS changes key material; secret rotation changes a credential in both the store and target service.
3. CloudWatch shows no metric point for a low-traffic service. Is the service down? Not necessarily. Evaluate expected telemetry cadence, traffic and missing-data policy, then corroborate with logs and external checks.
4. The standby Region is online, but applications cannot connect to the recovered database. What was missing? Recovery validation of network access, secrets, permissions, DNS, schema compatibility and workload capacity.
5. A two-Region design appears cheaper than a tested restore plan in a spreadsheet. What is absent? Recovery infrastructure, replication/transfer, duplicate capacity, tests, operational complexity and the price of keeping data/configuration consistent.

Review questions: who can read or rotate each secret, which data is encrypted by each key, how are missing metrics interpreted, what proves restore usability, and which ongoing costs support the chosen RTO/RPO?

## Verification and primary sources

AWS Secrets Manager rotation/access, KMS rotation, CloudWatch alarms/log retention and Well-Architected reliability guidance was inspected on 2026-10-04. The CLI example is read-only and intentionally omits secret-value retrieval; no AWS identity/API call or secret access was performed. No alarm, log retention, key policy, rotation, failover, restore, DNS change or regional recovery was executed. Static checks cannot establish application credential refresh, backup integrity, alarm delivery, failover time, RPO/RTO or live cost.

Primary references: [Secrets Manager rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html), [Lambda rotation lifecycle](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_lambda-functions.html), [Secrets Manager access](https://docs.aws.amazon.com/secretsmanager/latest/userguide/auth-and-access.html), [KMS key rotation](https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html), [CloudWatch missing data](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarms-and-missing-data.html), [CloudWatch Logs retention](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html), [backup recovery testing](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/back-up-data.html), and [multi-location strategy](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_fault_isolation_multiaz_region_system.html).
