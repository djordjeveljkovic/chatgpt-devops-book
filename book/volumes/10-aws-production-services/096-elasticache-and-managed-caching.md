---
book: The Complete DevOps Engineering Book
volume: 10
volume_title: "AWS Production Services"
chapter: 96
title: "ElastiCache and Managed Caching"
slug: elasticache-and-managed-caching
status: complete
summary: ../../_ai/chapter-summaries/096-elasticache-and-managed-caching.md
---

# Chapter 96 — ElastiCache and Managed Caching

## Cache authority and eviction

A cache stores values that the application can reconstruct or safely treat as temporary. It is an optimization and may be unavailable, stale or empty. The authoritative order, customer, payment and notification-intent records for DispatchDesk belong in their durable database or queue. If losing a cache key would lose a business fact, the design has placed authority in the wrong system.

Cache-aside is a common pattern: read a key, load the authoritative source on a miss, then write the derived value with an explicit expiry. On a database update, commit authoritative state first and invalidate or version the affected key. If invalidation is lost, TTL bounds stale lifetime only when the TTL is actually set and the value's permitted staleness fits the requirement. A very short TTL can increase database work; a long TTL can expose stale customer information. Choose per-value semantics rather than one global cache duration. AWS's [cache-aside guidance](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/caching-patterns.html) describes the pattern; its [cache validity guidance](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/cache-validity.html) covers TTL tradeoffs and jitter.

Invalidation has races. A reader can start before a write, pause, then repopulate an old value after the writer deletes the cache key. Stronger patterns include versioned keys, write-through coordination or an outbox-driven invalidation event, each with costs and failure modes. For an order view that tolerates thirty seconds of staleness, a bounded TTL may be acceptable. For authorization, payment state or inventory reservation, stale cache results can violate a business invariant. Read from the authority or use a protocol whose consistency is explicit.

The cache's max-memory eviction policy handles memory pressure; application key expiry is separate. A key can expire by its TTL or be evicted early under a memory policy. An `allkeys-*` policy can evict any eligible key, while a `volatile-*` policy considers keys with expiry. `noeviction` refuses writes when memory is exhausted. No eviction policy makes a durable record recoverable. Monitor evictions and memory, and confirm that every evicted value can be rebuilt within the database's safe capacity. See AWS's [eviction policy guidance](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/evictions.html) and [ElastiCache engine parameters](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/ParameterGroups.Engine.html) for `maxmemory-policy` behavior.

Avoid cache stampedes. When one popular key expires, hundreds of requests can miss at once and send duplicate work to the database. Use request coalescing, bounded refresh, stale-while-revalidate only where permitted, expiry jitter and application concurrency limits. Negative caching can reduce repeated lookups for absent objects, but use a short TTL and do not let a temporary authorization failure become a cached “not found” decision. A cache hit ratio is not a correctness metric: a wrong or stale value can still be a hit.

## Failover, connections and access

ElastiCache for Valkey or Redis OSS can use a replication group with a primary and read replicas. Multi-AZ automatic failover promotes an available replica after certain primary failures and moves the primary endpoint through DNS. Replication is generally asynchronous, so recently written keys can be missing after promotion. A replica can improve read capacity and fault tolerance; it is not a transactionally synchronized durable database. Cluster mode enabled partitions keys across shards and changes client routing and scale behavior. A single-node cache can be completely lost, and a replacement may start empty. [ElastiCache replication](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Replication.html) explains these layouts and limits.

Treat cache values as ephemeral even when replicas and snapshots exist. If the entire cache fails, the application should rebuild values from their authority. Multi-AZ reduces some failover interruption, but clients still encounter dropped connections, timeouts, DNS changes or a cold cache. Application libraries need reconnect behavior, bounded retries, topology-aware clients where required, and timeouts shorter than the request's remaining budget. An automatic retry of a cache read is usually safe; retrying a write command depends on whether it is idempotent and whether the client knows if the first write completed.

A cache outage can overload the database through misses. A healthy failover that promotes a replica may also produce a sharp cold-key period. Size and rate-limit the fallback path using the database's remaining capacity, not the web tier's theoretical maximum. If the database cannot safely serve all requests, degrade selected features or return an explicit retryable response. Letting every request bypass cache indefinitely can convert a partial cache incident into a database outage.

Keep the cache in private subnets and allow client traffic only from the intended application security groups. Use encryption in transit and the engine's supported authentication/ACL controls where configured; network location alone is not authentication. Store credentials through an approved secret mechanism and rotate them with client reconnection in mind. Cache keys and values can contain personal or session data, so include an explicit data classification, retention and deletion policy. Use TLS and credentials supported by the selected engine/version, and test connection behavior before an enforcement change.

RDS Proxy and an ElastiCache cluster solve different problems. RDS Proxy pools connections to the relational database and can reduce connection churn; ElastiCache stores application-selected keys for faster reads or coordination. Adding a cache does not repair a database connection limit, and adding a proxy does not provide application cache semantics. See [Chapter 95](095-rds-and-managed-database-operations.md) for relational connection saturation and recovery.

## Designing for a cache outage

Consider an API that caches a customer's DispatchDesk summary for two minutes. The database remains healthy, but the cache's primary is replaced. Tasks reconnect, miss popular keys and increase database reads. The team's failed assumption is that “Multi-AZ enabled” means no cache errors and no lost cache entries. The right response is to protect the durable database, not to restore cache contents as if they were authoritative.

Use short cache-operation timeouts, one bounded retry only where the client can safely retry, and a circuit breaker or per-request fallback budget. Coordinate database load using a semaphore or request limiter. For low-risk summary endpoints, serve a value only if its age is inside the approved stale window; otherwise load from the database under the limit. For order submission or payment authorization, consult the authoritative transaction path. A cache outage must not make the API falsely claim that an order was accepted or rejected.

Define behavior before a game day:

| Operation | Cache healthy | Cache unavailable or cold |
|---|---|---|
| Read customer display summary | Read a versioned/TTL value; fill on miss | Bounded authority read; optionally return explicitly permitted stale summary |
| Submit an order | Commit to the durable transaction path; cache is optional | Continue only if the authoritative database and queue meet their own safety conditions |
| Check authorization or payment state | Read the authoritative policy/state or a consistency-qualified source | Fail closed or use the approved authority path; never treat cache timeout as approval |
| Refresh a hot key | Coalesce or rate-limit refresh work | Defer refresh and preserve database headroom |

If cache recovery causes timeouts, first determine if clients can resolve the current primary endpoint and reconnect. Inspect ElastiCache events and replication-group/node state, then correlate `CacheHits`, `CacheMisses`, `Evictions`, `CurrConnections`, memory, network and engine CPU with application cache latency, timeout rate and database load. For Valkey and Redis OSS, `EngineCPUUtilization` can reveal engine-thread saturation that aggregate host CPU obscures on supported node classes. Metric names and availability vary by engine and node type; consult the [current metric guide](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/CacheMetrics.WhichShouldIMonitor.html).

Contain a miss storm by limiting cache-bypass concurrency and refresh traffic, retaining only the safe read behavior, and shedding optional work if needed. Restore client connectivity and observe whether cache hits recover gradually. Do not flush a cache or invalidate every key during an incident without evidence: that can create an even larger backend surge. If cache contents are rebuilt from the database, verify that the rebuild rate does not saturate the primary. Close the incident only after cache latency, database headroom, API SLO and customer-visible behavior return to the agreed range.

For example, CPU stays below its usual alert while `Evictions` rise and API latency climbs. Check memory pressure and max-memory policy, key sizes, TTL distribution, hit rate and the rate of database fills. Adding a reader replica will not automatically fix a write-primary hot key or oversized working set. A larger node or shard change is a capacity decision with resharding, client and cost effects; confirm the bottleneck first. If the main issue is low hit rate from unique keys, a larger cache may add cost without reducing source reads.

## Read-only inventory and evidence

The following commands inspect an existing replication group and its recent events. Use AWS CLI v2 with a profile and region verified through [Chapter 82](../09-aws-foundations/082-aws-cli-and-identity-sessions.md). This does not connect to the cache endpoint or modify its configuration:

```bash
set -euo pipefail
lab_profile=dispatchdesk-sandbox
lab_region=eu-west-1
read -r -p 'Expected AWS account ID: ' lab_expected_account
read -r -p 'Existing ElastiCache replication-group ID: ' lab_group
lab_actual_account=$(aws --profile "$lab_profile" --region "$lab_region" \
  --no-cli-pager sts get-caller-identity --query Account --output text)
[[ "$lab_actual_account" == "$lab_expected_account" ]] || {
  printf 'Profile resolved to account %s, not expected account %s\n' \
    "$lab_actual_account" "$lab_expected_account" >&2
  exit 1
}
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  elasticache describe-replication-groups --replication-group-id "$lab_group" \
  --query 'ReplicationGroups[0].{status:Status,clusterMode:ClusterMode,automaticFailover:AutomaticFailover,memberClusterIds:MemberClusters,primaryEndpoint:NodeGroups[0].PrimaryEndpoint,readerEndpoint:NodeGroups[0].ReaderEndpoint}'
lab_cache_ids=$(aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  elasticache describe-replication-groups --replication-group-id "$lab_group" \
  --query 'ReplicationGroups[0].MemberClusters[]' --output text)
for lab_cache_id in $lab_cache_ids; do
  aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
    elasticache describe-cache-clusters --cache-cluster-id "$lab_cache_id" \
    --query 'CacheClusters[0].{id:CacheClusterId,engine:Engine,version:EngineVersion,status:CacheClusterStatus,nodeType:CacheNodeType}'
done
aws --profile "$lab_profile" --region "$lab_region" --no-cli-pager \
  elasticache describe-events --source-type replication-group \
  --source-identifier "$lab_group" --duration 60
```

An omitted endpoint field can reflect topology or API output differences; inspect the returned full group and node records instead of inferring there is no endpoint. Engine version is read from each member cache cluster because the replication-group response does not carry that field. Event history is finite. Correlate it with application logs and CloudWatch metrics using a common UTC interval. The inventory caller needs read permission only; do not add failover, modify-group or flush operations to an incident script without a separate reviewed procedure.

## Exercises and answer guidance

1. ElastiCache promotes a replica, but one recently written key is absent. Is that necessarily a service defect? Not necessarily; asynchronous replication can lose recent cache state, so reconstruct from the authoritative source.
2. A cache outage triggers a tenfold rise in database reads. What do you protect first? Bound fallback concurrency and refresh traffic, prioritize correctness-critical operations and use controlled degradation before the database is exhausted.
3. `Evictions` rise while hit rate falls. Should TTL be lengthened blindly? No. Inspect memory pressure, key size/working set, expiry distribution and source-fill rate; longer TTL may increase memory use or staleness.
4. The cache reports healthy and the API returns a cached payment status. Does that prove current authorization? No. Query the authoritative source or use a documented consistency model appropriate to the payment decision.

Review questions: what owns the value, which failure can lose it, how much staleness is allowed, how is a miss storm bounded, and what signals prove the authority remains healthy?

## Verification and primary sources

AWS ElastiCache components, replication, Multi-AZ failover, eviction strategy, metrics and CLI documentation was inspected on 2026-10-04. No AWS identity/API call, cache connection, failover test, flush, setting change, key read/write, data migration or recovery action was executed. Static command checks and source review do not establish actual cache latency, data freshness, node limits, application reconnect behavior or safe database fallback capacity.

Primary references: [ElastiCache components](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/WhatIs.Components.html), [replication and recovery](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/Replication.html), [Multi-AZ failover](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/AutoFailover.html), [AWS cache-aside and validity patterns](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/caching-patterns.html), [AWS eviction policy guidance](https://docs.aws.amazon.com/whitepapers/latest/database-caching-strategies-using-redis/evictions.html), [ElastiCache engine parameters](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/ParameterGroups.Engine.html), [metrics to monitor](https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/CacheMetrics.WhichShouldIMonitor.html), [describe-replication-groups](https://docs.aws.amazon.com/cli/latest/reference/elasticache/describe-replication-groups.html) and [describe-events](https://docs.aws.amazon.com/cli/latest/reference/elasticache/describe-events.html).
