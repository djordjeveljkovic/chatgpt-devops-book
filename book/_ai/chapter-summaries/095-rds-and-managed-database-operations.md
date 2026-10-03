# Chapter 95 continuation

Status: complete

## Written material
Multi-AZ instance/cluster and read-replica distinctions; maintenance and client reconnect behavior; connection-budget arithmetic and RDS Proxy; automated backup/PITR/manual snapshot recovery; isolated validation and cutover; database saturation diagnosis; read-only AWS/CloudWatch/SQL inspection; exercises with answer guidance.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Multi-AZ DB instance/cluster, standby versus reader, asynchronous read replica, RPO/RTO, instance versus cluster PITR, connection budget, DatabaseConnections, proxy multiplexing/pinning, restoration and cutover.

## Examples and cross-references
Read-only RDS configuration and CloudWatch metric inspection; PostgreSQL session-state sample; isolated recovery scenario. Links to Chapter 82 for account preflight and Chapter 95 material for workload/connection scaling. No AWS or database operation executed.

## Open threads
Fresh independent review required. No identity/API call, metric query, DB connection, failover, snapshot, restore, parameter change, data query or recovery cutover executed. Engine behavior, RPO/RTO and production thresholds remain environment-specific.

## Verification
AWS RDS Multi-AZ, read-replica, instance and cluster backup/PITR, CloudWatch metrics, RDS Proxy and CLI documentation inspected 2026-10-04. Re-run the scoped checker after corrections; static checks do not prove restore usability or database saturation behavior.
