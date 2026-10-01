---
book: The Complete DevOps Engineering Book
volume: 17
volume_title: "Distributed Systems and Data Operations"
chapter: 167
title: "Cache Design and Invalidation"
slug: cache-design-and-invalidation
status: drafting
summary: ../../_ai/chapter-summaries/167-cache-design-and-invalidation.md
---

# Chapter 167 — Cache Design and Invalidation

## Derived state should have an explicit reconstruction route

DispatchDesk's catalog cache can disappear without losing accepted orders. Its authoritative catalog data remains in the database, and the application knows how to reconstruct the derived response. That is the key design boundary. A Redis instance with persistence enabled is still a cache under this contract; enabling persistence does not turn it into the authority for orders and notification intent.

[Efficiency](../16-performance-and-capacity-engineering/159-caching-batching-and-efficiency.md) introduced reuse, TTL and batching. Here the concern is correctness across multiple writers, replicas and failures. [Consistency contracts](166-consistency-and-consensus-concepts.md) explain why a quickly responding cache can still return an unacceptable observation. Identify the owner of each source field, the allowed stale interval, authorization scope and reconstruction cost before adding invalidation.

Derived state can include rendered catalog responses, counts, search results and permission decisions. These have different freshness requirements. Caching a product description for thirty seconds may fit an explicit contract; caching a revoked privilege for thirty seconds may not. A cache hit must still be safe for its caller. Tenant, permission and representation scope belong in the key or in an equally strong access design.

A cache can be safely expendable while its absence is operationally dangerous. If ninety-eight percent of reads usually hit, removing it can expose the source to roughly fifty times its normal miss traffic under the same mix. Reconstruction ability alone does not prove reconstruction capacity. Prepare the degraded path as a first-class operating mode.

## Invalidation can race with a fill

Consider a catalog row at version7. ReaderA begins a source lookup. WriterB commits version8 and deletes the current cache key. ReaderA then writes its older result into that key. The cache is stale even though the invalidation happened after the authoritative write. “Delete on update” is therefore a protocol with concurrency assumptions, not a complete explanation.

Versioned keys can make older fills harmless to newer reads when the reader has an authoritative version selector. For example, cache entries keyed by tenant, item and version allow the version7response to coexist with version8. The challenge moves to obtaining the correct version selector and retiring unused versions. Caching the selector without a suitable freshness contract simply recreates the original problem at another key.

Another design conditionally updates a cache envelope only if the new source revision is at least the stored revision. This prevents regression within that comparison boundary, but it requires an atomic comparison at the shared cache and a trustworthy monotonically ordered source revision. A locally checked condition across two network operations races again. A wall-clock timestamp from two application hosts is not automatically a reliable source order.

Write-through, cache-aside and refresh-ahead describe when a cache is updated relative to application work. None alone creates an atomic transaction between a database and an independent cache. If the database commits but cache update fails, the design must tolerate and repair that divergence. Prefer source correctness and explicit stale behavior over rolling back a successfully committed order merely because a derived cache could not update.

## A complete revision-regression experiment

Save the following as `cache_revision_lab.py` and run `python3 cache_revision_lab.py` with Python3 as an ordinary user on Ubuntu, Fedora or RHEL. It models an atomic envelope in one process using a lock. It performs no Redis or database operation and contains only synthetic catalog data.

```python
import threading

class RevisionCache:
    def __init__(self):
        self.lock = threading.Lock()
        self.entries = {}

    def store_if_not_older(self, key, revision, value):
        with self.lock:
            existing = self.entries.get(key)
            if existing is not None and existing[0] > revision:
                return False
            self.entries[key] = (revision, value)
            return True

    def read(self, key):
        with self.lock:
            return self.entries.get(key)

key = ("harbor", "synthetic-book", "description-v1")
cache = RevisionCache()
# A newer writer fills before an older reader completes its source lookup.
assert cache.store_if_not_older(key, 8, "new description")
assert not cache.store_if_not_older(key, 7, "old description")
assert cache.read(key) == (8, "new description")
print("older fill did not regress the current envelope")

naive = {}
naive[key] = "new description"
naive[key] = "old description"
assert naive[key] == "old description"
print("unconditional fill regressed the naive cache")
```

The assertion establishes the local comparison mechanism under this model. It does not establish global source authority, distributed clock ordering, cross-process atomicity, TTL behavior or equal-revision payload correctness. The lab assumes the source supplies a revision with a single defined meaning. A production implementation must decide what to do if two different values claim the same revision; silently overwriting may hide a source or schema defect.

For a shared cache, implement the compare-and-store through the supported atomic server operation or library primitive and test it under concurrent fills. Do not replace the lock with an ordinary GET followed by SET and claim the same guarantee. Schema versions in the key keep incompatible representations separate, while source revisions order changes to the underlying data. Those are different version axes.

## A complete bounded cache-outage experiment

The next lab measures whether a fallback gate bounds concurrent source work after every read becomes a miss. It uses sixteen local callers and a source concurrency limit of three. Save as `cache_outage_lab.py` and run `python3 cache_outage_lab.py` in the same disposable directory. It uses Python's standard library on the three Linux families and contacts no service.

```python
import threading
import time
from concurrent.futures import ThreadPoolExecutor

callers = 16
source_limit = 3
start = threading.Barrier(callers)
gate = threading.BoundedSemaphore(source_limit)
lock = threading.Lock()
active = 0
peak = 0

class SourceBusy(Exception):
    pass

def bounded_source_read():
    global active, peak
    if not gate.acquire(blocking=False):
        raise SourceBusy("fallback capacity exhausted")
    try:
        with lock:
            active += 1
            peak = max(peak, active)
        time.sleep(0.1)  # Simulated source latency, not a database measurement.
        return {"description": "synthetic catalog result"}
    finally:
        with lock:
            active -= 1
        gate.release()

def request(_):
    start.wait()
    try:
        bounded_source_read()
        return "served"
    except SourceBusy:
        return "rejected"

with ThreadPoolExecutor(max_workers=callers) as pool:
    outcomes = list(pool.map(request, range(callers)))
assert peak <= source_limit
assert active == 0
print("peak concurrent source calls:", peak)
print("served:", outcomes.count("served"), "rejected:", outcomes.count("rejected"))
```

The exact served/rejected count depends on scheduling. The invariant is the source concurrency bound and release of all acquired slots. Rejection represents an explicit degraded-path outcome, not lost accepted work. This experiment concerns catalog reads only. If the API cannot durably accept an order, it must return the defined unavailable result rather than acknowledge and hope a future retry recovers missing state.

A real application can wait briefly for a slot within its deadline instead of rejecting immediately, or serve a previously successful value within an approved maximum stale age. Each choice needs a bounded queue and visible outcome. An unbounded wait converts cache outage into memory accumulation. A stale response needs its authorization and freshness policy; it must not be used for operations that require current authority.

The labs create no persistent state beyond their files. Cleanup removes the two scripts after inspection. They do not simulate real network partitions, distributed cache replication, provider outages or customer traffic.

## Stampedes, expiration and eviction are different events

Expiration ends the configured usable lifetime of a key. Eviction removes entries under a capacity policy. Invalidation removes or replaces entries because source meaning changed. Connection failure prevents observing the cache at all. Instrument these outcomes separately: a rising miss fraction has different remedies depending on its cause.

The inspected [Redis eviction documentation](https://redis.io/docs/latest/develop/reference/eviction/) explains memory bounds and policy behavior. Some server memory lies outside the dataset's eviction comparison, so setting `maxmemory` equal to every available host byte is not a complete memory budget. A no-eviction policy can reject new writes instead of making room. An application that ignores those errors can retain stale existing entries while assuming refresh succeeded.

Choose eviction against measured key access and object sizes. A key-count limit does not bound bytes when one cached report is enormous. A volatile-key policy can behave unexpectedly when the intended keys lack expiry. Do not mix expendable caches and indispensable state casually under an eviction policy that can discard both.

Jittering expirations reduces synchronized refresh of unrelated keys. Per-key single-flight limits duplicate fills of one key. A popular key can still overload the source if every application replica independently fills it, so understand the cross-replica boundary. Refresh-ahead must be rate-limited and should not turn every cold key into background source traffic.

Client-side invalidation also has connection semantics. Redis's [client-side caching introduction](https://redis.io/docs/latest/develop/clients/client-side-caching/) describes tracking and invalidation mechanisms. A disconnected client must follow its library's documented recovery policy rather than assume missed invalidations will arrive forever. A watch or notification is an observation stream, not a magical transaction shared with the application database.

## Diagnose a cache failure by testing the contract

Suppose Summit sees a high cache hit fraction and low database load, but recently updated descriptions remain old. Inspect the source revision, cache representation version, fill timing and invalidation path for a controlled authorized sample. A hit-rate success cannot prove freshness. The revision-regression race can explain a stale envelope after a valid deletion event.

Recovery may bypass the affected cache scope, fix the atomic/version design and refill a bounded set. A global flush can overwhelm the database and erase diagnostic evidence. Preserve enough revision/timing metadata to verify the cause without collecting unnecessary customer payloads. If stale authorization or tenant leakage is involved, treat the response scope as a correctness issue and withdraw that cache path until its contract is proven.

For a cache outage, inspect fallback rejections, source concurrency, pool waiting and request deadlines. Restore cache connectivity through its owner, then warm a bounded hot set while observing source load. Avoid opening fallback concurrency merely because many users are waiting: that can make the authoritative database fail and remove the reconstruction route. Recovery is complete when freshness and authorization are correct and the source remains within its operating budget, not merely when a Redis process responds to a ping.

## Exercises and answer guidance

A source write commits, invalidation succeeds, and an older fill subsequently overwrites the cache. What mechanism can prevent regression? A trustworthy source revision plus atomic conditional replacement, or versioned keys with an appropriately authoritative selector. A local GET/SET comparison is insufficient across replicas.

Does ninety-nine percent hit rate establish correct cache behavior? No. It says many lookups found entries, not that the entries were fresh, authorized or valid for the current schema.

After cache loss, every miss waits indefinitely for the database pool. What boundary is absent? A bounded fallback concurrency/wait policy and explicit outcome within the request deadline. The queue of waiting requests is consuming resources even if database connections are capped.

## Takeaways and verification

Cache correctness depends on source authority, scope, version order and a bounded failure path. Test stale fills and complete cache loss, not just normal hits. Redis primary documentation was inspected on2026-10-01. Both local Python experiments are inline; no Redis deployment, client tracking session, database fallback integration or production cache invalidation was executed while authoring.

