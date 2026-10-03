# Independent review — Chapter 95

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 8ca2f44f215b1f8002fcd575722208b3704ad089c48ae7b48bfbde3f2b52fda0

## Scope and findings

Read current complete body and compact summary, skeleton brief, authoring guide and relevant prerequisite context (Chapter94 for95; current Chapter95 for96). Reviewed examples, claims, exact arguments/response projections, source links, diagnosis/recovery, command host assumptions, exercises and summary accuracy. Chapter95 review supersedes its prior record and verifies both recorded corrections; Chapter96 had no prior record.

Both prior findings are resolved: PITR now explicitly scopes instance restoration to a new DB instance and separately links Multi-AZ cluster restoration to a new cluster. Rehearsal resources have named ownership, ongoing billing, retained evidence/cutover decisions and cleanup responsibility. No material finding. The connection-budget example, pool/Proxy limits, safe retries, source preservation, reconciliation and canary recovery are coherent. Read-only RDS/CloudWatch CLI and PostgreSQL session grouping are appropriate; five-minute Maximum and missing-data limits are stated. Exercises provide answer guidance. The compact summary accurately records current content and nonexecution; its mention of “Chapter95 material” is redundant but harmless.

## Dated primary-source evidence

Inspected on2026-10-04:

- [Instance PITR](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html).
- [Multi-AZ cluster PITR](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.MultiAZDBCluster.html).
- [Multi-AZ](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html).
- [Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.howitworks.html).
- [RDS metrics](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-metrics.html).
- [describe-db-instances](https://docs.aws.amazon.com/cli/latest/reference/rds/describe-db-instances.html).
- [get-metric-statistics](https://docs.aws.amazon.com/cli/latest/reference/cloudwatch/get-metric-statistics.html).
- [PostgreSQL statistics](https://www.postgresql.org/docs/current/monitoring-stats.html).

Evidence supports the documented operation/schema and conceptual claims, not measured performance or live recovery. No claim about exact currently installed AWS CLI or database/cache engine version is made. Platform-neutral AWSCLIv2 Bash calls introduce no distro-specific host mutation; Chapter82 provides workstation setup.

## Validation and limits

`python3 tools/check_book.py --chapters 95-96` passed:2 draft chapters,3 shell syntax blocks and1,343 global local links; no errors/warnings. No AWS identity/API call, metric query, database/cache connection, SQL query, key read/write, failover, snapshot/restore, parameter change, flush, cutover or cleanup executed. No Ubuntu/Fedora/RHEL runtime matrix, load test, service-side validation or actual RPO/RTO measurement performed. Static checks cannot establish account permissions, engine configuration, usable backup, cache freshness, reconnect behavior or safe fallback capacity. Only the separate review records changed.

Verdict: approved
