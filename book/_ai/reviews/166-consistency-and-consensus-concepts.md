# Independent review — Chapter 166

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: bd8202a6377d4eb27a9d4e51b14e550fdfa40fed3d41c120b01473140088e599

## Scope and findings

Read complete current body/summary, Chapter 166 brief and authoring-guide requirements with Chapter 165 prerequisite context. Reviewed consistency definitions, quorum/set lab, partition/failure placement, Raft membership reasoning, fencing, versioned etcd guarantees/CLI, recovery and assessment. No material technical finding. Summary accurately reflects the examples and nonexecution boundaries.

Linearizability is correctly tied to an operation point between invocation/response and completed-operation real-time order, not a response-time guarantee. Serializability versus strict serializability and eventual convergence are distinctly scoped. A stale watch observation is not treated as an authoritative negative result. Consensus does not transact with an independent notification provider. The product boundary determines acceptable stale reads.

Quorum arithmetic is correct: counts 2/3/4/5 require 2/2/3/3 voters and tolerate 0/1/1/2 unavailable voters. Same-fixed-set majority intersections follow directly; the lab asserts them without pretending to implement a consensus protocol. ABC/DE partition permits a three-voter side for the fixed five-member set. Independently chosen AB and DE majorities of ABC and CDE can be disjoint even though the sets share C. Safe transition therefore needs the product's documented protocol. Learners are not silently counted as voters. Persistence/election/commitment and correlated placement assumptions remain explicit.

Fencing requires enforcement at the protected resource, not merely logging a lease/epoch. UUID ownership is distinguished from ordered authority; unsynchronized timestamps do not provide a safe epoch. External idempotency/reconciliation is a separate contract. etcd default KV versus serializable reads, watches/revision history and uncertain timed-out operations match the versioned guarantee documentation. Reconnect/history compaction needs documented resynchronization rather than assuming every watch is current.

The etcdctl endpoint status command uses documented endpoint/TLS/timeouts/table output with supplied existing credentials and ordinary operator context. The documentary endpoint must be replaced. It performs status observation without a write, health proposal or membership mutation. One endpoint response is correctly insufficient quorum/application-health proof. Membership changes remain incident-sensitive and use documented learner/promotion boundaries; quorum loss is not repaired by casually removing voters. Restored snapshots may lose newer state and need old-cluster exclusion/client revision acceptance. Exercises have answer guidance; takeaways are substantive.

Low observations:

- Opening: add the concise bespoke section outline required by the authoring guide.
- Prose: normalize majority ofN, shareC/includeC, etcd3.6 and date spacing. Consider linking the plain chapters161–162 reminder to canonical uncertainty/idempotency chapters for consistency.

## Primary evidence checked 2026-10-04

- [Raft extended paper](https://raft.github.io/raft.pdf): dated May 20, 2014; election/log safety and joint-consensus membership transition.
- [etcd 3.6 API guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/): KV read, watch/history, lease and uncertain-operation boundaries.
- [etcd 3.6 cluster status](https://etcd.io/docs/v3.6/tasks/operator/how-to-check-cluster-status/): endpoint status/table inspection.
- [etcd 3.6 runtime reconfiguration](https://etcd.io/docs/v3.6/op-guide/runtime-configuration/): supported learner/promotion and membership changes.
- [etcdctl release-3.6 reference](https://github.com/etcd-io/etcd/blob/release-3.6/etcdctl/README.md): endpoint, TLS, dial/command timeout and output flags.

## Validation and limits

`python3 tools/check_book.py --chapters 166-166` passed one Python syntax check, one shell syntax check and 1,449 global local links without errors/warnings. Exact stripped-front-matter hash computed using `tools.promote_reviewed.body_hash`. Set outcomes and command structure inspected directly. No quorum lab output presented as measured protocol behavior, etcd command, consensus implementation, watch/lease test, membership change, partition/fencing or restore executed. No OS/client/server/version runtime matrix tested. Static sources/sets cannot demonstrate protocol safety, actual cluster quorum, TLS authorization or stale-action rejection. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed the added bespoke outline, normalized mathematical/date/Python/etcd prose spacing and relative uncertainty/idempotency links to Chapters 161 and 162. Both prior optional observations are resolved. Outline accurately reflects consistency/quorum/fencing, versioned etcd observations and supported recovery. New links resolve to the correct canonical chapters and preserve the independent-provider boundary. Spacing does not change mathematical sets, code, API claims or semantics. No material issue introduced; approval remains.

Fresh stripped-front-matter body hash computed with `tools.promote_reviewed.body_hash`: bd8202a6377d4eb27a9d4e51b14e550fdfa40fed3d41c120b01473140088e599. `python3 tools/check_book.py --chapters 166-166` again passed one Python syntax check, one shell syntax check and 1,451 local links without warnings/errors. Earlier full assessment, primary evidence and nonexecuted etcd/consensus/runtime limits remain applicable. Only this separate review record updated.

Verdict: approved
