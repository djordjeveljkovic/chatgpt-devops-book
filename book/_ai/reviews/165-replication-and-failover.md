# Independent review — Chapter 165

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: e79d509214e3e01140e65d8a12448fefd354214e0d41644ec9731a8e33128218

## Scope and findings

Read complete current body/summary, Chapter 165 brief and authoring-guide requirements with Chapter 164 prerequisite context. Reviewed symbolic receipt/persistence/replay model, PostgreSQL 18 observer SQL and null/timeline caveats, read-your-writes, asynchronous/synchronous acknowledgment boundaries, fencing, scoped RDS workflow, recovery and assessment. No material technical finding. Summary accurately distinguishes source/static review from unperformed replication/failover observation.

Symbolic sets are internally correct: primary-only acknowledgment includes D, absent from the recovered ABC copy; C is recoverable under the expressly stronger received-means-persisted assumption but not yet replay-visible; remote persistence acknowledges ABC without a modeled surviving-copy loss; remote visibility acknowledges AB already visible. The model intentionally does not implement WAL, fsync or provider guarantees, and synchronous evidence for one replica is not generalized to every candidate. Read freshness and acknowledgment durability remain separate contracts.

PostgreSQL observer queries use valid documented functions/columns. pg_current_wal_lsn is assigned to the confirmed primary; recovery-role checks precede the observer examples. Receive/replay positions and last replayed transaction time describe different stages. Nulls, idle-primary timestamp age, observation timing and incomparable histories/timelines are appropriately caveated. pg_is_in_recovery does not prove leadership authorization. SQL is read-only with required statistics privileges; no promotion/setup command is divorced from fencing or compatibility.

Read-after-write routes or bounded position waiting require actual authoritative/replication evidence. Replication correctly is not historical recovery from a copied deletion. Partitioned old authority needs effective exclusion, and fencing tokens require enforcement at the protected write resource. New routing or controller consensus alone is not that enforcement. RDS Multi-AZ DB instance failover is explicitly distinguished from clusters/read replicas/other engines and regions; endpoint/pool recovery is required rather than assuming DNS changes repair existing connections.

Failover acceptance includes declared RPO/RTO, candidate evidence, restorable history, synthetic order/intent reconciliation, ambiguous provider effects, warming and old-writer exclusion. Failback does not simply reopen a divergent primary. Lag/retention diagnosis preserves slot/archive ownership and backup consumers; deleting retention is not an automatic disk repair. Recovery validates sustained progress and degraded-redundancy ownership. Exercises include answer guidance and substantive takeaways.

Low observations:

- Opening: add the concise bespoke section outline required by the authoring guide.
- Model/prose verification: normalize spacing such as orderD/orderC, Chapter164, PostgreSQL18 and inspection dates. Symbolic identifiers in actual Python strings should remain unchanged unless intentionally renamed.

## Primary evidence checked 2026-10-04

- [PostgreSQL 18 standby](https://www.postgresql.org/docs/18/warm-standby.html): asynchronous/synchronous replication, receipt/replay and retained WAL recovery.
- [PostgreSQL 18 administration functions](https://www.postgresql.org/docs/18/functions-admin.html): role and WAL receive/replay inspection functions.
- [PostgreSQL 18 statistics](https://www.postgresql.org/docs/18/monitoring-stats.html): sender fields and lag/visibility limitations.
- [RDS Multi-AZ DB instance failover](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.Failover.html): explicitly scoped managed failover and endpoint/connection recovery.

## Validation and limits

`python3 tools/check_book.py --chapters 165-165` passed one Python syntax check and 1,449 global local links without errors/warnings. Exact stripped-front-matter body hash computed using `tools.promote_reviewed.body_hash`. SQL and symbolic set outcomes reviewed directly; checker does not validate SQL against a server. No symbolic output presented as measured platform behavior, live SQL observation, replication setup, promotion, RDS failover, fencing/partition, reseeding or recovery test executed. No OS/client/server/topology runtime matrix tested. Documentation and static checks cannot establish current leadership, recoverable WAL, actual RPO/RTO or old-writer exclusion. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed added concise outline and normalized Chapter 164, Python, symbolic-order, PostgreSQL version and date prose spacing. Both prior optional observations are resolved. Outline accurately covers acknowledgment/freshness, observer progress, loss-window model, effective fencing and scoped failover/backup distinction. Prose order C/D references still correspond to unchanged Python symbols and outcomes. No technical semantics changed or material issue introduced; approval remains.

Fresh stripped-front-matter body hash computed with `tools.promote_reviewed.body_hash`: e79d509214e3e01140e65d8a12448fefd354214e0d41644ec9731a8e33128218. `python3 tools/check_book.py --chapters 165-165` again passed one Python syntax check and 1,449 local links without warnings/errors. Earlier full technical assessment, primary evidence and nonexecuted database/replication/failover limitations remain applicable. Only this separate review record updated.

Verdict: approved
