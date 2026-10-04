# Independent review — Chapter 167

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: d19975f1983703661521ecc1db61d3871478f317f2a5e76085930d84ed288200

## Scope and findings

Read complete current body/summary, Chapter 167 brief and authoring-guide requirements with Chapters 159/166 prerequisite context. Reviewed source authority/freshness, revision regression and fallback gate Python, Redis eviction/memory/client tracking, diagnostics/recovery, exercises/takeaways and links. No material technical finding. The chapter supplies an explicit outline and complete topic-specific labs with accurately limited claims.

Source of truth is correctly defined by the application's contract rather than Redis persistence alone. Derived authority, authorization and reconstruction capacity are distinct. At 98% hit fraction, complete cache loss exposes the source to approximately 1/0.02 = 50 times its former miss load under unchanged mix. Versioned selectors require their own authority; source/representation version axes are not conflated. Write-through/cache-aside labels do not claim a cross-system transaction. TTL/eviction/invalidation/connectivity have different observations and repairs.

The revision lab's lock makes comparison and replacement atomic within one process; older revision 7 cannot replace stored 8. Equal-revision ambiguity, global authority, TTL and cross-process boundaries are explicitly excluded. A shared implementation cannot replace the lock with ordinary separate GET/SET. No real Redis or source observation is claimed.

The outage lab uses a nonblocking BoundedSemaphore with capacity three, a synchronized start and locked active/peak counters. Acquired slots are released in finally after decrementing active; rejected callers do not enter the source. All sixteen worker slots can reach the barrier. Exact served/rejected counts are properly scheduling-dependent, while peak<=3 and final active==0 are the stated invariants. This bounds source concurrency, not real source latency, fleet-wide concurrency, durable acceptance or automatic waiting backpressure. Degraded read rejection is not lost accepted order work. Per-process demonstration and provider/database integration limits remain explicit.

Redis memory outside maxmemory eviction accounting and noeviction write failures are accurately qualified. Volatile-key policy requires expiry and object count is not a byte bound. Client tracking recovery after disconnect is assigned to the actual library policy; missed invalidations are not promised durable replay. Single-flight, jitter and warming have appropriately scoped load limits. Recovery withdraws unsafe authorization/freshness paths, avoids destructive global flush and verifies bounded source load/customer contract rather than only Redis reachability. Exercises include answer guidance and substantive takeaways.

Low observations:

- Revision comparison discussion: explicitly remind readers that eviction/deletion of the envelope loses its remembered revision; a later old fill can be accepted unless a separate watermark/authoritative selector preserves the freshness contract. The current text already limits comparison to its stored-envelope boundary, so this is precision rather than a false global guarantee.
- Summary Status is drafting while manuscript is draft. Align during coordinator summary maintenance. Concepts section could name revisions, fallback gates and eviction/tracking rather than only point to the outline.

## Primary evidence checked 2026-10-04

- [Redis key eviction](https://redis.io/docs/latest/develop/reference/eviction/): maxmemory accounting, replication/AOF buffers, noeviction and volatile-policy behavior.
- [Redis client-side caching](https://redis.io/docs/latest/develop/clients/client-side-caching/): tracking/invalidation and client/library integration boundaries.

No exact server-version capability, Redis command or selected library behavior is promised beyond the documented concepts; actual deployed compatibility remains required.

## Validation and limits

`python3 tools/check_book.py --chapters 167-167` passed two Python syntax checks and 1,451 global local links without warnings/errors. Exact stripped-front-matter body hash computed using `tools.promote_reviewed.body_hash`. Code/control flow and arithmetic inspected statically. No Python lab runtime result, Redis deployment/eviction/client tracking, source/database integration, distributed fill race or production outage test executed during this review. No OS/server/client/runtime matrix tested. Local code and primary docs cannot establish real stale-age bounds, fleet fallback limits or production invalidation correctness. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed the added surviving-envelope/watermark paragraph and aligned summary. Both earlier optional observations are resolved. The paragraph correctly explains that eviction/deletion removes comparison memory, permitting an older delayed fill into an empty key, and scopes prevention across loss to a suitable external watermark or authoritative version selection. It does not claim evictable cache comparison alone enforces global freshness. Summary now records draft status and actual revision/fallback/eviction/tracking concepts. No material issue introduced; approval remains.

Fresh stripped-front-matter body hash computed with `tools.promote_reviewed.body_hash`: d19975f1983703661521ecc1db61d3871478f317f2a5e76085930d84ed288200. `python3 tools/check_book.py --chapters 167-167` again passed two Python syntax checks and 1,451 local links without warnings/errors. Earlier complete assessment, primary evidence and nonexecuted cache/database/runtime limitations remain applicable. Only this separate review record updated.

Verdict: approved
