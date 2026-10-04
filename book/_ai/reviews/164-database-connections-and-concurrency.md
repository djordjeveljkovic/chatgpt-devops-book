# Independent review — Chapter 164

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: eef00c162582ad52d866e47b1b5ab8bb1016b1deec927bb98ab1868556d50ba3

## Scope and findings

Read complete current manuscript/summary, Chapter 164 brief and authoring-guide requirements with Chapter 163 prerequisite context and existing linked database setup context. Reviewed PostgreSQL 18 SQL/locking/isolation, connection-service/psql flags, two-session procedure/cleanup, observer query, pool arithmetic, deadlock/timeout recovery, exercises/takeaways and local links. No material technical issue found. Summary correctly states that the checker does not validate SQL semantics and no PostgreSQL experiment was executed.

Pool arithmetic is correct: 4×20+3×10 = 110 possible connections; a temporary fifth API increases this to 130. Per-process/client behavior and operational reserve are qualified rather than equating pool maxima with actual activity. Acquisition wait is distinguished from execution, lock wait and connectivity. External provider effects remain outside the atomic order/intent transaction; pool borrowers must release completed/healthy transaction state.

PostgreSQL Read Committed statement snapshots and concurrent conditional-update behavior are correctly described. Session A's update holds its row lock until commit/rollback; session B's two-second lock_timeout is shorter than its five-second statement_timeout and aborts the failed transaction while A remains open. Explicit B rollback restores useful transaction state. The subsequent transaction sees zero remaining and returns zero rows; the nonnegative check is an additional invariant, not a complete business result. Same statements at stronger isolation can require whole-transaction retry, as the surrounding isolation discussion acknowledges. No fabricated transcript is presented.

Connection service supplies actual authorized host/database/user and approved credential/TLS behavior; psql -X suppresses startup files. Dedicated disposable schema, stop-on-existing-schema guidance and non-CASCADE cleanup constrain destructive scope. Loss of an interactive terminal requires confirmation of server session/rollback rather than an assumption. Linux setup/version differences are delegated to actual canonical prerequisites rather than inventing uniform packages.

The observer query is read-only, filters intended database/application names, returns at most twenty rows, omits SQL payloads and correctly uses clock_timestamp, transaction start, wait fields and pg_blocking_pids. Metadata visibility and PID reuse are caveated. LIMIT bounds output rather than proving a hard query-duration bound; frequent blocker inspection should follow an operational scope. Deadlock and serialization failure recovery uses rollback/fresh whole-transaction retry, preserving identity and budgets. Controlled owner-coordinated termination replaces indiscriminate backend killing. Recovery includes durable order and notification evidence. Exercises provide answer guidance and takeaways are substantive.

Low observations:

- Opening: add the concise bespoke section outline required by the authoring guide.
- SQL lab/prose verification: normalize spacing such as sessionA/sessionB, PostgreSQL18, permit110connections and dates for readability. Existing command identifiers and numerical semantics remain correct.

## Primary evidence checked 2026-10-04

- [PostgreSQL 18 isolation](https://www.postgresql.org/docs/18/transaction-iso.html): statement snapshots, conditional updates and whole-transaction serialization retry.
- [PostgreSQL 18 explicit locking](https://www.postgresql.org/docs/18/explicit-locking.html): row-lock lifetime and deadlock behavior.
- [PostgreSQL 18 client defaults](https://www.postgresql.org/docs/18/runtime-config-client.html): lock_timeout/statement_timeout and transaction-local settings.
- [PostgreSQL 18 information functions](https://www.postgresql.org/docs/18/functions-info.html): pg_blocking_pids scope and inspection considerations.
- [PostgreSQL 18 statistics](https://www.postgresql.org/docs/18/monitoring-stats.html): activity fields and statistics visibility.
- [PostgreSQL 18 psql](https://www.postgresql.org/docs/18/app-psql.html) and [connection services](https://www.postgresql.org/docs/18/libpq-pgservice.html): -X and service connection setup.

## Validation and limits

`python3 tools/check_book.py --chapters 164-164` passed one shell syntax check and 1,449 global local links without warnings/errors. Exact stripped-front-matter body hash computed with `tools.promote_reviewed.body_hash`. SQL reviewed directly against engine docs; no SQL parser/runtime check supplied by the checker. No PostgreSQL connection, row-lock/timeout/deadlock experiment, observation query, backend cancellation, pool change, provider or load operation executed. No client/server/OS/version matrix tested. Static documentation cannot establish actual session privileges, timeouts, application identity, blocked rows or durable service recovery. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed added concise outline and normalized pool-total, session A/B, PostgreSQL version and date spacing. Both prior optional observations are resolved. Outline accurately describes pool/transaction boundaries, the two-session row-lock lab, blocker inspection and bounded recovery. Spacing changes do not alter arithmetic or SQL/transaction semantics. No material issue introduced; approval remains.

Fresh stripped-front-matter body hash computed using `tools.promote_reviewed.body_hash`: eef00c162582ad52d866e47b1b5ab8bb1016b1deec927bb98ab1868556d50ba3. `python3 tools/check_book.py --chapters 164-164` again passed one shell syntax check and 1,449 local links without errors/warnings. Earlier full assessment, primary evidence and nonexecuted PostgreSQL/runtime limits remain applicable. Only this separate review record updated.

Verdict: approved
