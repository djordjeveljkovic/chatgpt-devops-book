# Independent review — Chapter 161

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 0d952f4b48dd89b4186d7ed85169272f38095ec8f4f6c9abfa1c0e43236a5220

## Scope and findings

Read complete current manuscript and compact summary, Chapter 161 brief and authoring-guide requirements with Chapter 160 prerequisite context. Reviewed whole-request budgets, deadline/cancellation boundaries, HTTP/SQLite lab control flow and cleanup, identity/reconciliation, incident/recovery, exercises/takeaways and local links. No material technical issue found. Summary accurately separates authored/static examples from unperformed execution.

Budget arithmetic is correct: 150+550+300 = 1,000 milliseconds. Nested independent three-attempt policies can multiply to 27 leaf attempts; this is properly labeled a worst-case model. Pool time must consume the enclosing remaining budget rather than resetting it. Monotonic elapsed timing, cross-host propagation assumptions, bounded client budgets and request-phase distinctions are sound. Socket/blocking timeout is correctly not represented as a total operation deadline. Cancellation of waiting does not reverse committed or external state.

The complete loopback lab creates a synthetic UUID-keyed ledger, commits INSERT OR IGNORE before delaying its response, times out the caller and independently queries the token. Each HTTP handler creates its own connection in its own thread, avoiding default SQLite cross-thread connection use. SQL parameters avoid interpolation. The unique token deduplicates only the mock token, not different payload meanings; that limitation and real-provider lookup requirements are explicit. The response body's context closes HTTP resources; finally shuts down/closes the server and joins its serving thread. Expected scheduling/port-dependent behavior is not asserted as measured. ProxyHandler({}) correctly avoids ambient proxies. No actual notification, order acceptance or production-server capability is implied.

SQLite transaction context commits/rolls back pending work under the documented current default legacy transaction handling; engine single-writer behavior supports the local explanation. The script remains a synthetic demonstration rather than crash/storage durability evidence. Reconciliation branches distinguish definitive completion/rejection from uncertainty, preserve durable intent and identities, and control retry/replay concurrency. Stale authority reads and expired idempotency windows are correctly not treated as proof of no effect. Exercises include answer guidance; closing takeaways are complete.

Low observations:

- Python lab, all three sqlite3.connect context blocks: the connection context manager manages commit/rollback but does not close the connection. Add explicit close or contextlib.closing around connections for deterministic resource cleanup and to avoid ResourceWarning on current Python. Process exit ultimately releases these bounded lab resources; no production leak-free guarantee is claimed.
- Opening: add the concise bespoke section outline required by the authoring guide. Actual sections and substantive content are complete.
- Verification paragraph: the author's historical sqlite3 fetch failure is accurately recorded, but the reviewer successfully retrieved its official documentation on 2026-10-04. A future verification refresh can add that evidence without claiming a lab run.

## Primary evidence checked 2026-10-04

- [Python 3.14 urllib.request](https://docs.python.org/3.14/library/urllib.request.html): timeout for blocking operations, opener/proxy behavior and response context.
- [Python 3.14 http.server](https://docs.python.org/3.14/library/http.server.html): ThreadingHTTPServer and nonproduction warning.
- [Python 3.14 sqlite3](https://docs.python.org/3.14/library/sqlite3.html): current transaction defaults, thread ownership, lock timeout and connection-context versus close behavior. Retrieval succeeded in this review despite author's earlier failed fetch.
- [SQLite transactions](https://www.sqlite.org/lang_transaction.html): commit and single-writer behavior.

## Validation and limits

`python3 tools/check_book.py --chapters 161-161` passed one Python syntax check and 1,449 global local links without errors/warnings. Exact stripped-front-matter hash computed with `tools.promote_reviewed.body_hash`. SQL and request/thread/resource control flow inspected statically. No local socket/SQLite lab, database corruption/recovery test, provider call, cancellation or production experiment executed. No Python/distribution/runtime matrix tested. Syntax and documentation cannot establish a real timeout transcript, durable provider effects, recovery authority or successful cleanup under every runtime failure. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed added outline, all three SQLite connection blocks, numeric spacing and updated documentation evidence. All prior optional observations are resolved. `with closing(sqlite3.connect(...)) as db, db` enters closing first and the connection transaction context second; reverse exit order commits/rolls back before closing the connection. Thus the POST still commits before the delay and all initialization/request connections now close deterministically on normal/error exits. Query rows are materialized before close. The outline accurately describes the chapter, spacing does not change arithmetic, and documentation wording correctly distinguishes author engine inspection from reviewer sqlite3 retrieval. No material issue introduced; approval remains.

Fresh stripped-front-matter body hash computed with `tools.promote_reviewed.body_hash`: 0d952f4b48dd89b4186d7ed85169272f38095ec8f4f6c9abfa1c0e43236a5220. `python3 tools/check_book.py --chapters 161-161` again passed one Python syntax check and 1,449 local links without errors/warnings. Earlier full assessment, primary evidence and socket/database/runtime limits remain applicable. Only this separate review record updated.

Verdict: approved
