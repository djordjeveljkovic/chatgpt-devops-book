---
book: The Complete DevOps Engineering Book
volume: 16
volume_title: "Performance and Capacity Engineering"
chapter: 159
title: "Caching, Batching and Efficiency"
slug: caching-batching-and-efficiency
status: draft
summary: ../../_ai/chapter-summaries/159-caching-batching-and-efficiency.md
---

# Chapter 159 — Caching, Batching and Efficiency

## Avoid work before buying capacity for it

Caching reuses a result; batching shares setup cost across several pieces of work. Both can reduce demand, but both change timing and failure behavior. They deserve the same correctness review as a new database schema. For DispatchDesk, a catalog description can tolerate a short stale interval under an explicit product contract. An acknowledged order's existence and notification intent cannot depend on an evictable cache. Reuse the right work, not merely the easiest object to store.

[Capacity forecasting](158-capacity-planning-and-forecasting.md) modeled future demand. Efficiency changes the resource cost of that demand. If a database lookup costs four milliseconds of CPU and network overhead and a cache lookup costs one, a ninety-percent hit fraction reduces this component's modeled average cost to1.3milliseconds:0.9×1+0.1×4. That is67.5percent less work for this component under these assumptions. The service's total latency will not necessarily improve by the same fraction: order writes, queue work and unrelated waits remain. Measure the path that changed and the end-to-end result.

Locality matters. A process-local cache avoids a network call but is duplicated across replicas and disappears on restart. A shared cache improves cross-replica reuse while adding a dependency, network latency and an operational cost. The least complicated correct option can differ across Harbor's VPS, Summit's managed services and Atlas's platform. A cache is not an automatic architectural requirement.

## Freshness is part of the API contract

A time-to-live bounds how long a cached entry can be reused after insertion under the implementation's clock assumptions. It does not prove that the source was current when inserted. A stale read from a lagging replica can create a freshly timed cache entry containing old data. Explicit invalidation can shorten stale periods but introduces a race between a write, invalidation and another cache fill.

For example, one process reads catalog version7, another commits version8 and invalidates the cache, and the first then stores version7. The invalidation succeeded yet the cache regressed. Versioned keys or a carefully designed source/version check can avoid that particular race. For product decisions where stale data is unacceptable, consult authoritative state in the transaction rather than claiming a short TTL makes every read correct.

Keys must include the scope that changes the answer: tenant, authorization context, language, selected fields or schema version where relevant. A key based only on an order identifier can leak data across tenants if that identifier is not globally scoped and authorization is skipped on a cache hit. Do not cache a user-specific response under a public key. Sensitive payloads need access control and retention regardless of whether the storage is called a cache.

Negative caching stores an absence or error result. It can protect a backend from repeated nonexistent lookups, but a long negative TTL can hide a newly created record. Cache only deliberately classified absences for a short appropriate interval; a transient database failure should not silently become “order not found.” Distinguish hit, miss, expired, source error and rejected admission in telemetry.

## A complete single-process cache lab

Save this as `catalog_cache.py` and run `python3 catalog_cache.py` as an ordinary user on Ubuntu, Fedora or RHEL. It uses a fake catalog source and a monotonic clock; it contacts no database or Redis service. The lock serializes fills within this one process, which prevents a concurrent local stampede at the cost of serializing unrelated cache work. That deliberate limitation makes the mechanism visible before introducing a production library.

```python
import copy
import threading
import time

class CatalogCache:
    def __init__(self, source, ttl_seconds=1.0, max_entries=2):
        self.source = source
        self.ttl = ttl_seconds
        self.max_entries = max_entries
        self.entries = {}
        self.lock = threading.Lock()
        self.source_calls = 0

    def get(self, tenant, item):
        key = (tenant, item)
        with self.lock:
            now = time.monotonic()
            hit = self.entries.get(key)
            if hit is not None and hit[0] > now:
                return copy.deepcopy(hit[1]), "hit"
            if hit is not None:
                del self.entries[key]
            value = self.source(tenant, item)
            self.source_calls += 1
            # Drop expired entries, then an insertion-oldest entry if needed.
            now = time.monotonic()
            self.entries = {k: v for k, v in self.entries.items()
                            if v[0] > now}
            if len(self.entries) >= self.max_entries:
                del self.entries[next(iter(self.entries))]
            self.entries[key] = (now + self.ttl, copy.deepcopy(value))
            return copy.deepcopy(value), "miss"

catalog = {("harbor", "book"): {"description": "paperback", "version": 1}}
def source(tenant, item):
    return copy.deepcopy(catalog[(tenant, item)])

cache = CatalogCache(source)
print(cache.get("harbor", "book"))
print(cache.get("harbor", "book"))
catalog[("harbor", "book")] = {"description": "hardback", "version": 2}
print("before TTL:", cache.get("harbor", "book"))
time.sleep(1.1)
print("after TTL:", cache.get("harbor", "book"))
print("source calls:", cache.source_calls)
```

The first read misses and the next reuses the value. Updating the source does not update the cached value immediately; the later read after expiry reloads it. The printed values are the reader's observation, not an author-recorded runtime result. Returning copies prevents caller mutation from corrupting the cached object. The entry-count bound is not a byte bound, and the eviction rule is insertion order rather than a full least-recently-used policy. A production cache needs measured object sizes, a deliberate concurrency design and tests around its actual freshness contract.

The source exception propagates rather than caching a fabricated absence. That is a correctness choice. If the product allows serving a previously successful stale value during a source outage, implement an explicit maximum stale age and mark the result accordingly. Do not extend stale values indefinitely just to keep a dashboard green.

## Shared caches and stampede controls

A shared Redis-style cache can use an expiring write so insertion and expiration are one operation. The inspected [Redis SET reference](https://redis.io/docs/latest/commands/set/) documents expiration and conditional options. Avoid a two-command insert-then-expire sequence when a crash between the commands could leave a permanent entry. Client-library APIs and server versions must match the deployed service; this chapter does not install or assume an unauthenticated Redis server.

A stampede occurs when many callers miss the same popular key and all request the source. Expiration jitter spreads unrelated expirations. Single-flight coalesces concurrent requests for the same key. Prewarming may help predictable demand but can itself overload the source. A global cache flush destroys warmth precisely when traffic may already be stressful. Warm a bounded hot set and measure source load before broad invalidation.

Distributed fill locks have an additional ownership problem: a slow caller can outlive its lease, while another caller begins a fill. Redis's [locking discussion](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/) describes ownership tokens and expiration limitations. That discussion does not establish a universal lock solution for order correctness. Protect authoritative state with the database's transaction and uniqueness contract. A cache-fill lock can tolerate redundant reads in ways that a financial or order mutation cannot.

When the shared cache fails, a naive fallback sends every request to a backend sized for the miss fraction. At a95percent hit fraction, the backend may suddenly see twenty times its usual lookup demand. A bounded source concurrency limit, rate-limited refresh and product-approved stale responses can contain the transition. Some operations should fail clearly rather than perform an unsafe degraded read.

## Batching shares cost but adds waiting

Suppose one notification-provider request has a fixed ten-millisecond setup cost and one millisecond of per-item processing. Sending ten items individually costs approximately110milliseconds of that modeled work, while one ten-item batch costs20. This is an illustrative cost model, not a provider benchmark. A batch also makes the first item wait until the batch is full or a deadline expires. At one item per second, waiting for ten items would add roughly nine seconds for the first item unless a time bound flushes earlier.

Use both a size cap and a maximum waiting interval. Preserve the per-item identifier and outcome so partial failures can be retried independently. A successful HTTP batch response may still include failed entries. AWS's [SQS batch-action documentation](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-batch-api-actions.html) is a concrete example of per-entry results; the provider-specific batch limits and response semantics must be checked rather than transferred to an unrelated notification API.

The following complete JavaScript file demonstrates bounded batch formation with simulated per-item outcomes. Save it as `batch_demo.js` and run `node batch_demo.js` with an installed supported Node.js runtime on Ubuntu, Fedora or RHEL. It sends no real notifications and deletes no queue messages. Its `failed` list is evidence for a retry decision, not an implemented durable retry queue.

```javascript
const maxItems = 3;
const maxWaitMs = 100;
let pending = [];
let timer = null;
let sequence = Promise.resolve();

function flush() {
  if (timer !== null) clearTimeout(timer);
  timer = null;
  if (pending.length === 0) return;
  const batch = pending;
  pending = [];
  sequence = sequence.then(async () => {
    const outcomes = batch.map(item => ({
      id: item.id, ok: item.id !== "lab-2"
    }));
    const failed = outcomes.filter(result => !result.ok).map(result => result.id);
    console.log(JSON.stringify({ batch: batch.map(item => item.id), failed }));
  });
}

function add(item) {
  pending.push(item);
  if (pending.length >= maxItems) {
    flush();
  } else if (timer === null) {
    timer = setTimeout(flush, maxWaitMs);
  }
}

async function main() {
  add({ id: "lab-1" });
  add({ id: "lab-2" });
  add({ id: "lab-3" });
  add({ id: "lab-4" });
  await new Promise(resolve => setTimeout(resolve, maxWaitMs + 20));
  flush();
  await sequence;
}
main().catch(error => { console.error(error); process.exitCode = 1; });
```

Three items flush by size and the remaining item flushes by time. The modeled failure belongs only to `lab-2`; retrying every successful sibling would increase duplicate risk. This small lab does not impose a bound on the promise-chain backlog under unbounded input. A real consumer must bound fetched/in-flight batches, preserve durable ownership and respect provider rate limits. On shutdown, stop accepting new work, flush bounded pending work, wait within the grace period and leave unfinished durable jobs eligible for recovery.

Database batching has similar tradeoffs. Larger transactions reduce round trips but hold locks longer, produce bigger retry units and can increase replication lag. Bulk APIs need per-record validation and a defined partial-commit policy. An entire batch cannot be described as accepted unless its actual durable result supports that claim.

## Diagnose efficiency failures with customer evidence

A cache rollout can lower database read rate while producing stale prices. The performance goal succeeded and the correctness goal failed. Compare source version, cached version, insertion age and invalidation timing for an authorized sample; do not expose customer payloads in unrestricted telemetry. Roll back the cache path or shorten its allowed use while preserving authoritative writes.

A batch rollout can lower provider-call count but increase oldest-notification age. Inspect batch waiting, in-flight concurrency, provider throttling and per-item failures. Smaller batches or a shorter wait may restore the deadline at higher request cost. That is a product tradeoff, not an automatic optimization failure. Verify correctness and latency at low traffic as well as at peak; a size-only batch policy is often worst when traffic is quiet.

## Exercises and answer guidance

A catalog cache has a sixty-second TTL. Does it guarantee results are at most sixty seconds behind the authoritative database? No: the source read may already be stale, and the contract must include that lag or consult authoritative state.

A95percent-hit cache disappears. What source-load change should the team prepare for? Approximately twenty times the previous miss traffic under the same request mix, before retry effects. Bound fallback rather than assume the source can absorb it.

A batch contains ten notifications, with two failed entries. Which entries become retry candidates? The two failures, with their original durable identities and retry policy. Ambiguous provider outcomes need idempotent reconciliation rather than blind replay of all ten.

## Takeaways and verification

Efficiency is useful when it reduces work while preserving the promised freshness, authorization and durable result. Caches need bounded failure behavior; batches need both size and waiting limits plus per-item outcomes. Redis and AWS SQS primary documentation was inspected on2026-10-01. Python and JavaScript mechanics labs are inline; no Redis integration, provider batch call or production performance experiment was executed while authoring.

