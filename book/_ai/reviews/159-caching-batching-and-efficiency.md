# Independent review — Chapter 159

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: a429532517c35cb356f5d3ea908ca3b9c72739f805eb2339d421e45175478b81

## Scope and findings

Read full current manuscript, compact summary, Chapter 159 brief and authoring-guide requirements with Chapter 158 context. Reviewed caching/batching cost arithmetic, complete Python and JavaScript labs, Redis expiration/lock boundaries, SQS partial results, freshness/authorization/idempotency, source outages, shutdown/recovery and links. Summary accurately describes the current material and nonexecution limits.

Medium — first section, second paragraph, cache cost example: the stated four-millisecond database lookup and one-millisecond cache lookup imply a cache-first miss pays both costs. At 90% hits the modeled mean is 0.9 × 1 + 0.1 × (1 + 4) = 1.4 ms, a 65% reduction versus 4 ms, excluding fill overhead. Current 1.3 ms/67.5% calculation implicitly treats 4 ms as the whole miss path while labeling it only database lookup cost. Correct the calculation or explicitly define 4 ms as inclusive miss-path cost. This is a material numerical-model inconsistency in the principal efficiency example.

Other arithmetic is correct: loss of a 95%-hit cache can increase source lookup demand by 1/0.05 = 20 under constant mix; ten individual modeled provider operations cost 10 × (10+1) = 110 ms versus 10+10 = 20 ms batched; the first item at one/s can wait nine seconds for ten items without a time flush. End-to-end improvement is appropriately distinguished from component savings.

The Python lab's monotonic TTL, deep copies, single-process lock, expiry cleanup and insertion-order eviction are coherent for the declared bounded default. Source exceptions propagate rather than manufacturing absence. Entry count is correctly distinguished from bytes, and serializing unrelated keys is explicit. It is not a distributed correctness mechanism. Real source timeout/concurrency and stale-age controls remain required.

Redis atomic expiring SET avoids a crash window in separate insertion/expiration. Ownership-token and lease limitations are not promoted into a universal distributed order lock; authoritative transaction/uniqueness controls remain separate. TTL does not bound authoritative source lag. Scope-safe keys, negative-cache classification, fill/invalidation race and fallback concurrency limits are sound.

The JavaScript lab flushes by size or timer and serializes simulated batch outcomes through a promise chain, awaits final work, and reports only the failed item's identity. The unbounded promise-chain backlog under unlimited input is explicitly disclosed; it is not taught as production backpressure. Production ownership, unfinished durable jobs and ambiguous per-item effects require idempotent recovery. SQS HTTP success versus per-entry failure semantics are correctly scoped; no unrelated notification-provider batch limit is invented. Larger database transactions' lock/retry effects and low-traffic batch latency are explained. Exercises include answer guidance and closing takeaways are substantive.

Low — opening: add the concise bespoke section outline required by the authoring guide. Actual sections and practical content are complete.

## Primary evidence checked 2026-10-04

- [Redis SET](https://redis.io/docs/latest/commands/set/): expiration/conditional write options and version boundaries.
- [Redis distributed locks](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/): ownership tokens and expiration-related safety assumptions; not a universal exactly-once contract.
- [SQS batch actions](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-batch-api-actions.html): batch operations and per-entry outcomes.
- [SQS SendMessageBatch](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_SendMessageBatch.html): successful and failed entries may coexist under HTTP 200; limits and identifiers belong to the actual provider API.

## Validation and limits

`python3 tools/check_book.py --chapters 159-159` passed one Python syntax check, one JavaScript syntax check and 1,449 global local links without errors/warnings. Exact body hash computed using `tools.promote_reviewed.body_hash`. Code/control flow and arithmetic inspected statically. No Python/Node lab, Redis command/lock, SQS batch, provider integration, shutdown or load experiment executed. No installed-version/OS/cache/queue runtime matrix tested. Parsing and documentation cannot establish actual freshness, lock safety, latency, backpressure or business durability. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed corrected cache-first cost paragraph and added concise section outline. The medium arithmetic finding is resolved: hits cost 1 ms, misses cost 1+4 ms, giving 0.9×1 + 0.1×5 = 1.4 ms and (4−1.4)/4 = 65% component reduction, with fill/other overhead explicitly excluded. End-to-end improvement remains appropriately qualified. Outline accurately represents cache/freshness/coordination, batching, waiting/failure and outcome measurement. The low outline observation is resolved. No material issue remains.

Fresh body hash computed with `tools.promote_reviewed.body_hash`: a429532517c35cb356f5d3ea908ca3b9c72739f805eb2339d421e45175478b81. `python3 tools/check_book.py --chapters 159-159` again passed one Python syntax check, one JavaScript syntax check and 1,449 local links without warnings/errors. Earlier full technical assessment, primary evidence and runtime/cache/queue/load limitations remain applicable.

Low observation — summary Open threads still asks for the now-completed arithmetic and outline fixes. Remove those completed tasks during summary maintenance. Only this separate review record updated.

Verdict: approved
