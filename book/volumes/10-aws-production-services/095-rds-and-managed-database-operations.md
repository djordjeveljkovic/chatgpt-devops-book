---
book: The Complete DevOps Engineering Book
volume: 10
volume_title: "AWS Production Services"
chapter: 95
title: "RDS and Managed Database Operations"
slug: rds-and-managed-database-operations
status: complete
summary: ../../_ai/chapter-summaries/095-rds-and-managed-database-operations.md
---

# Chapter 95 — RDS and Managed Database Operations

## Availability, maintenance and connections

Amazon RDS operates supported database engines on managed infrastructure. AWS handles the service infrastructure and selected maintenance mechanisms; the application team still owns schema compatibility, query behavior, connection lifecycle, access policy, backup objectives and recovery validation. Managed operation changes the work boundary. It does not remove the need to understand the database engine or rehearse a failure.

Choose a deployment model by its failure and read behavior. A Multi-AZ DB instance deployment maintains a standby for failover; that standby does not serve application reads. A Multi-AZ DB cluster has a writer and two standby instances that can serve reads. A read replica uses asynchronous replication and can serve read-only queries, subject to engine-specific behavior and replication lag. The words “replica” and “Multi-AZ” alone do not identify whether an endpoint is readable or how current its data is. Inspect the exact deployment type and engine. [RDS Multi-AZ documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html) distinguishes the instance and cluster models; [read-replica guidance](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html) explains asynchronous replication.

An RDS endpoint is a DNS name, not a guarantee that existing application sockets will survive a role change. Failover changes where the endpoint resolves, but clients may retain stale DNS or broken pooled connections. Configure bounded connection and query timeouts, reconnect with jitter, retry only safe operations, and use transaction/idempotency design for ambiguous outcomes. A client can lose its response after the server commits. Do not assume that retrying every write is safe.

Maintenance also has application consequences. Review engine version support, parameter and option groups, storage growth, backup windows, maintenance windows and planned failover capacity. Apply engine upgrades and parameter changes through a reviewed process with a representative restore or compatibility test. “Available” is a control-plane status; it does not establish that connection latency, replication lag or query plans meet the service objective. Record the engine/version and endpoint owners alongside the operational runbook.

Connection demand is a capacity input. If an API runs `N` tasks and each process permits a pool of `P` database sessions, its potential demand is approximately `N × P`, before workers, scheduled jobs, migrations, health checks and operator sessions. During a deployment, old and new tasks may overlap. Scale-out can therefore exhaust database connections even while CPU is modest. Set bounded pools from a shared connection budget and reserve headroom for recovery and administration. RDS Proxy can pool and multiplex compatible sessions and smooth some connection surges, but session pinning can reduce reuse, and the database still has finite CPU, memory and connection capacity. See [RDS Proxy behavior](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.howitworks.html).

## Backups, replicas and recovery

For an RDS DB instance, automated backups support point-in-time recovery within the configured retention period. Restoring a DB instance creates a new DB instance and leaves its source in place. This protects a recovery path from direct modification of the original, but it also means the restored database is not automatically the production endpoint. The operator must validate the restored data, security groups, subnet group, parameter settings, encryption, credentials, DNS/application configuration and cutover authority. For a Multi-AZ DB cluster, use the separate cluster restore operation: point-in-time recovery creates a new DB cluster. See AWS's [DB-instance PITR documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html) and [Multi-AZ DB-cluster PITR documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.MultiAZDBCluster.html) before selecting the workflow.

A manual snapshot is a retained point-in-time image, useful before risky maintenance or for a deliberately long retention policy. Neither a successful backup job nor a snapshot listing proves application recovery. Define recovery point objective (RPO) in terms of acceptable lost data and recovery time objective (RTO) in terms of the full service becoming useful. Then restore into an isolated environment, run engine integrity checks and application queries, measure the time, and document who can authorize cutover. Name an owner for each rehearsal resource before creating it: restored instances and clusters, snapshots and supporting storage remain billable while they exist. The recovery owner should remove temporary resources only after evidence is retained and the cutover/retention decision is recorded. A backup that has never been restored is an untested dependency.

High availability and recovery solve different failures. Multi-AZ failover targets availability after certain instance/AZ problems. It does not roll back an accidental `DELETE`, bad migration, compromised credential or corrupt application write that successfully replicated. Read replicas can offload eligible reads or support a recovery strategy, but asynchronous replication can lag and a promoted replica requires an explicit application transition. Neither a standby nor a read replica replaces point-in-time backup and restore tests.

For DispatchDesk, an accidental cleanup job deletes valid orders at 14:05. First stop the job and preserve database/audit/application evidence. Select a recovery time just before the destructive transaction, restore to a distinct, isolated identifier, and verify expected order counts, recent known order IDs, referential integrity, notification intents and schema compatibility. Compare valid writes after the selected restore point and decide how to reconcile them. Only after the owner accepts the recovered state should traffic switch. Keep the original instance isolated until the incident and recovery decision are complete; do not rename, overwrite or delete it merely to make the new database match a familiar endpoint.

The restore may default to network or parameter settings different from the current production instance, and storage pages can initialize after the instance becomes available. Reapply reviewed security configuration, monitor restore progress, test representative queries and confirm TLS/application credentials. Perform a canary request and verify durable state before broad cutover. A DNS update alone does not migrate pooled application sessions or prove that every task uses the recovered database. Keep the rehearsal resource under its named recovery owner until retained evidence and cutover decisions are complete, then remove temporary resources through the approved cleanup process to stop ongoing charges.

## Diagnosing database saturation

Start with a symptom and time range. “The API is slow” could mean connection acquisition, database CPU, lock waits, storage latency, a query plan regression, network timeouts or an upstream dependency. Compare application-side pool metrics and request traces with RDS metrics such as `DatabaseConnections`, `CPUUtilization`, `FreeableMemory`, `FreeStorageSpace`, read/write latency and queue depth where supported. Metrics are evidence over time, not a single-cause diagnosis. AWS publishes RDS data in CloudWatch; consult the current [RDS metrics reference](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-metrics.html) for engine and deployment applicability.

Suppose DispatchDesk scales from four to twelve API tasks and then clients receive connection timeouts. Database CPU remains moderate. The failed assumption is that low CPU means the database has spare capacity. The old task set, new task set and worker may each hold their configured pools, reaching the engine's connection ceiling or proxy borrow limit. Inspect per-process pool usage, open and idle sessions, connection-establishment rate, `DatabaseConnections`, proxy borrow latency and the deployment timeline. For PostgreSQL, an authorized read-only sample can group visible sessions by state:

```sql
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state
ORDER BY count(*) DESC;
```

Visibility depends on database privileges; do not grant a broad superuser role simply to inspect sessions. Session state alone does not identify a blocked query or justify terminating it. Correlate query load, wait events, application pool limits, transaction age and database logs using the engine's supported tools.

Contain impact before adding capacity. Pause or reduce the offending worker/API scale-out through its controller owner, preserve enough healthy capacity for the service, bound new connection creation and verify whether a migration or retry storm is contributing. If a proxy is present, distinguish client connections from database connections and inspect pinning and borrow behavior. A proxy cannot make an overloaded query cheaper or repair a lock cycle. Increasing instance class, changing `max_connections` or killing sessions without evidence can move the failure or damage work in progress.

After the immediate incident, assign a shared connection budget across every workload and deployment overlap, add alerts that pair database metrics with application pool saturation, and test a staged rollout under realistic load. If the issue is query cost rather than sessions, use engine query analysis and a representative workload before changing indexes. If storage is nearly full, review growth and safe capacity changes; deleting database data to silence an alarm requires application-level retention approval and tested backup recovery.

## Read-only operational inspection

Use AWS CLI v2 from an authorized workstation with the expected profile, account and region. Complete [Chapter 82's account preflight](../09-aws-foundations/082-aws-cli-and-identity-sessions.md). These calls read RDS configuration and one CloudWatch series; they do not modify the database. Restrict saved output because it contains infrastructure identifiers:

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Expected AWS account ID: ' lab_expected_account
read -r -p 'Existing RDS DB instance identifier: ' lab_db
lab_actual_account=$(aws --profile "$lab_profile" --region "$lab_region" \
  --no-cli-pager sts get-caller-identity --query Account --output text)
[[ "$lab_actual_account" == "$lab_expected_account" ]] || {
  printf 'Profile resolved to account %s, not expected account %s\n' \
    "$lab_actual_account" "$lab_expected_account" >&2
  exit 1
}
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  rds describe-db-instances --db-instance-identifier "$lab_db" \
  --query 'DBInstances[0].{status:DBInstanceStatus,engine:Engine,version:EngineVersion,multiAZ:MultiAZ,endpoint:Endpoint.Address,backupDays:BackupRetentionPeriod,subnets:DBSubnetGroup.Subnets[*].SubnetIdentifier}'
```

For a recent connection trend, provide an explicit UTC interval and retain dimensions for the same DB identifier:

```bash
read -r -p 'Start time in UTC, YYYY-MM-DDTHH:MM:SSZ: ' lab_start
read -r -p 'End time in UTC, YYYY-MM-DDTHH:MM:SSZ: ' lab_end
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  cloudwatch get-metric-statistics --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value="$lab_db" \
  --start-time "$lab_start" --end-time "$lab_end" \
  --period 300 --statistics Maximum --output json
```

This is a five-minute maximum series, not a real-time session trace. Empty points can indicate an incorrect identifier, interval, region, metric availability or permissions; they do not mean zero connections. For a Multi-AZ cluster, replica, proxy or engine-specific metric, inspect its actual dimensions and endpoints rather than reusing the DB-instance identifier blindly.

## Exercises and answer guidance

1. A Multi-AZ standby is available but reporting queries overload the primary. Can clients send reads to that standby? Not for a Multi-AZ DB instance deployment; choose an appropriate read replica or cluster reader endpoint if the engine/model and consistency requirements permit.
2. Automated backups are enabled. Is point-in-time recovery proven? No. Restore to an isolated target, validate the application data and measure the recovery process against RPO/RTO.
3. API task count triples and connection timeouts begin while CPU stays low. Inspect pooled and database connection counts, deployment overlap, worker/job demand and proxy borrow metrics before scaling the DB.
4. A read replica has lag during a promotion. Is it equivalent to the primary? No. Quantify missing/stale writes, verify the promotion and application endpoint change, and reconcile according to the recovery plan.

Review questions: what fails over, what serves reads, what is the recovery point, how many sessions can deploy overlap create, and which observations prove recovery?

## Verification and primary sources

AWS RDS Multi-AZ, read-replica, backup/PITR, CloudWatch metrics, Proxy and CLI documentation was inspected on 2026-10-04. The SQL is a read-only PostgreSQL session summary and requires appropriate visibility. No AWS identity/API call, metric query, database connection, failover, snapshot, restore, parameter change, data query or recovery cutover was executed. Static and source checks cannot establish engine-specific behavior, actual RPO/RTO, database load, restore usability or a safe production threshold.

Primary references: [Multi-AZ deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html), [Multi-AZ failover](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.Failover.html), [read replicas](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html), [automated backups](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html), [point-in-time restore](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html), [CloudWatch metrics](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-metrics.html), [RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.howitworks.html), [describe-db-instances](https://docs.aws.amazon.com/cli/latest/reference/rds/describe-db-instances.html) and [get-metric-statistics](https://docs.aws.amazon.com/cli/latest/reference/cloudwatch/get-metric-statistics.html).
