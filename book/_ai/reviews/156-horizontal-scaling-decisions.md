# Independent review — Chapter 156

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 2a463e37372e75aab1d85a0bf346bb1bd12de3ca7924ae8f08a91978836af4ba

## Scope and findings

Read complete current body, compact summary, Chapter 156 brief and authoring-guide requirements with Chapters 151–155 shared-resource/lifecycle context. Reviewed Python budget, Go shutdown/channel behavior, duplicate/lease reasoning, placement and shared state, ECS/Kubernetes lifecycle claims, failure/removal experiment, recovery and links. No material technical issue found. Summary correctly distinguishes static parsing from unperformed runtime/replica validation.

Arithmetic is correct: ceil(36/(8 × 0.75)) = 6 APIs; six twenty-connection pools plus four ten-connection worker pools yield 160 steady connections. One surge API yields 180, exactly the stated service budget; eight APIs yield 200 before surge. Equality passes the explicit greater-than budget test. This budget excludes already reserved administration/other consumers and is a ceiling hypothesis, not a claim that measured demand or performance fits. Real terminating processes and policy-specific surge can exceed a simplistic one-extra model; the text explicitly treats the input as a fictional plan requiring measurement.

Shared durable state, atomic unique-key arbitration, payload conflict, sticky-routing fragility and bounded leases are sound. Lease expiry can duplicate provider effects; ownership checks, deadlines and idempotency are appropriate controls. Placement is distinguished from merely having replicas. Partition ownership and ordering boundaries are explicit. Recovery avoids simultaneous connection storms and preserves accepted orders/notification intent.

The Go program's atomic readiness flag is concurrency-safe. Signal context cancellation wakes the drain goroutine; readiness is withdrawn, an illustrative convergence delay precedes Shutdown, and a separate five-second deadline bounds HTTP graceful waiting. Shutdown returns the listener's ErrServerClosed promptly, so the main goroutine's receive from the deferred-close drained channel correctly prevents early process exit. If graceful waiting fails, Close provides forced containment. A listener setup error exits via log.Fatal, which is appropriate for a failed startup. This is an ordinary loopback mechanics lab, not a production readiness integration or durability implementation. Platform grace must include the illustrative pre-shutdown delay; request cancellation does not undo committed data.

ECS deregistration and application-stop responsiveness are accurately separated from Kubernetes termination/endpoint behavior, without copying fixed provider defaults as universal values. Readiness, startup and liveness distinctions and controlled replica removal are sound. Exercises include answer guidance; closing takeaways state the core lessons.

Low observations:

- Go introduction, “handles GET requests only”: the handlers are registered by path and do not enforce r.Method, so other methods can receive these harmless responses. Say it demonstrates GET requests, or explicitly reject unsupported methods. This does not create business state or compromise the loopback lab.
- Opening: add the bespoke concise section outline required by the authoring guide. Chapter sections and substantive content are already complete.
- State paragraph: replace plain chapter141 with a relative link to the canonical instrumentation lab, for consistent prerequisite context.

## Primary evidence checked 2026-10-04

- [Go HTTP Shutdown](https://pkg.go.dev/net/http#Server.Shutdown): listener closure, ErrServerClosed, active-handler wait and requirement that main wait for shutdown completion.
- [Go signal NotifyContext](https://pkg.go.dev/os/signal#NotifyContext): signal-driven context cancellation and stop cleanup.
- [ECS connection draining](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/load-balancer-connection-draining.html): load-balancer deregistration and application stop responsiveness.
- [Kubernetes pod lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/): termination grace, endpoint readiness/termination and shutdown ordering.

No universal exactly-once or loss-free shutdown guarantee is inferred from these APIs.

## Validation and limits

`python3 tools/check_book.py --chapters 156-156` passed one Python syntax check, two shell syntax checks, one Go syntax check and 1,446 global local links without errors/warnings. Exact body hash computed with `tools.promote_reviewed.body_hash`. Code/control flow and arithmetic inspected statically. No Go lifecycle run, signal experiment, race test, live routing/replica removal, database arbitration, provider integration or load experiment executed. No OS/platform/toolchain runtime matrix tested. Syntax and documentation cannot demonstrate routing convergence, graceful completion, real connection headroom or business durability. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed the new section outline, relative Chapter 141 link and both Go method guards. The outline accurately reflects the chapter's actual sequence; the link resolves to the canonical instrumentation chapter and retains the in-memory durability caveat. Both handlers now reject non-GET requests with HTTP 405 and Allow: GET before producing health/readiness responses. Guard returns prevent unintended continuation; readiness and shutdown/channel behavior are unchanged. All three earlier optional manuscript observations are resolved. No material issue introduced.

Fresh body hash computed with `tools.promote_reviewed.body_hash`: 2a463e37372e75aab1d85a0bf346bb1bd12de3ca7924ae8f08a91978836af4ba. `python3 tools/check_book.py --chapters 156-156` again passed one Python syntax check, two shell syntax checks, one Go syntax check and 1,447 local links with no errors/warnings. Earlier primary assessment and runtime/replica limits remain applicable.

Low observation — summary Open threads still asks for the now-completed outline, Chapter 141 link and guards. Remove those completed tasks during summary maintenance. Only this separate review record updated.

Verdict: approved
