---
book: The Complete DevOps Engineering Book
volume: 17
volume_title: "Distributed Systems and Data Operations"
chapter: 166
title: "Consistency and Consensus Concepts"
slug: consistency-and-consensus-concepts
status: draft
summary: ../../_ai/chapter-summaries/166-consistency-and-consensus-concepts.md
---

# Chapter 166 — Consistency and Consensus Concepts

## State the observable contract before naming an algorithm

Consistency describes what observations concurrent clients may make. Consensus helps participants agree on an ordered decision despite selected failures. These are related ideas, not interchangeable words. A system can replicate bytes without supplying the application's required read contract, and a consensus-backed key-value store cannot make an unrelated notification provider participate in its transaction.

[Replication and failover](165-replication-and-failover.md) separated candidate selection from excluding old authority. This chapter supplies the reasoning behind coordinated authority and quorum. DispatchDesk may need a consistent configuration revision or a temporary worker owner, but its small Harbor deployment does not automatically need a separately operated consensus cluster. A database transaction can remain the simplest correct boundary for its current work. Summit can consume managed coordination where appropriate, and Atlas's platform can operate a coordination service with explicit ownership and failure placement.

For one register, linearizability means operations can be understood as taking effect at a point between call and response, with completed operations respecting real-time order. If a write completes before a later read begins, that read cannot simply return an older value under that contract. Concurrent operations can be ordered in either permitted way. Linearizability does not impose a maximum response time or make a disconnected client receive an answer.

Serializability concerns a set of transaction effects being equivalent to some serial execution. Strict serializability additionally respects real-time ordering. Eventual convergence is a weaker and differently scoped promise: replicas can converge after changes stop and communication recovers under the stated model, while intermediate reads may differ. Avoid calling all of these “strong consistency” without specifying the operations and boundary.

An order-result lookup and an analytics dashboard can need different contracts. A caller reconciling an uncertain accepted order needs authoritative evidence. A daily aggregate may tolerate delayed updates. Product requirements determine where stale reads are acceptable; a cache or replica choice should not silently change that promise.

## Quorum arithmetic is necessary but not the whole protocol

A majority ofN voting members has size floor(N/2)+1. Three members need two; five need three. Two majorities of the same fixed member set intersect. That overlap helps protocols ensure that later authority encounters relevant earlier decisions, but intersection alone does not select a correct value or resolve conflicting versions.

A replicated state-machine protocol also needs rules for elections, log order, persistence, commitment and membership changes. The historical [Raft extended paper](https://raft.github.io/raft.pdf), published2014-05-20 by Diego Ongaro and John Ousterhout, explains its separation of election, replication and safety. Its protocol is a reference for reasoning, not an invitation to implement a production replacement from the small lab below.

A three-member cluster with one lost member still has two voters. A partition of two versus one can permit progress on the majority side under the protocol while the minority cannot commit new consensus decisions. A two-versus-two partition of four has no majority. Adding a fourth voter to three does not increase the number of failed voters tolerated: both configurations can lose only one while retaining a majority.

Placement matters more than the host count alone. Three voters on one physical host share its failure. Three zones can improve independence while adding latency and operational constraints. A five-member cluster can tolerate more independent unavailable voters than three but requires a larger quorum and more resources. Correlated network and storage failures can defeat a naive count-based availability argument.

## A complete quorum and partition lab

Save this as `quorum_lab.py` and run `python3 quorum_lab.py` as an ordinary user with Python3 on Ubuntu, Fedora or RHEL. It enumerates mathematical sets and changes no infrastructure. It does not implement consensus, elections, persistent logs or network traffic.

```python
from itertools import combinations

for count in (2, 3, 4, 5):
    members = set(range(count))
    size = count // 2 + 1
    quorums = [set(group) for group in combinations(members, size)]
    assert all(left & right for left in quorums for right in quorums)
    tolerated_unavailable = count - size
    print(f"voters={count} majority={size} "
          f"independent unavailable tolerance={tolerated_unavailable}")

members = {"A", "B", "C", "D", "E"}
partitions = ({"A", "B", "C"}, {"D", "E"})
majority = len(members) // 2 + 1
for side in partitions:
    print("partition", sorted(side), "has fixed-set quorum:",
          len(side) >= majority)

# A membership change cannot use unrelated old/new majorities blindly.
old = {"A", "B", "C"}
new = {"C", "D", "E"}
old_vote = {"A", "B"}
new_vote = {"D", "E"}
assert len(old_vote) > len(old) // 2
assert len(new_vote) > len(new) // 2
assert not old_vote & new_vote
print("old and new majorities can be disjoint during an unsafe transition")
```

The final example exposes why a membership change is not simply editing a list on each server. The old and new member sets shareC, but their independently chosen majorities need not includeC. A correct reconfiguration protocol must preserve safety through the transition. The Raft paper describes a joint-consensus approach; deployed products have their own documented reconfiguration mechanisms. Follow those mechanisms rather than extrapolating from the set exercise.

The unavailable tolerance assumes a fixed voting set and independent loss; it is not a percentage uptime prediction. Learners or nonvoting replicas do not count toward the voting majority until the documented promotion step succeeds. Cleanup removes the local Python file only.

## Coordination authority must reach the protected resource

Suppose Atlas elects one controller to schedule a recurring report. The controller pauses for a long time, loses its lease, then resumes after a new controller has been elected. If the old controller still writes to the report store, two actors can perform the effect even though election worked correctly. A lease tells the actor when it should stop; fencing makes obsolete actions unacceptable at the resource.

A monotonically increasing authority token can be checked by the protected storage system. The receiver must reject an older token even if its holder claims to be leader. An arbitrary UUID distinguishes ownership but does not establish increasing authority order. A timestamp from unsynchronized wall clocks is not an equivalent safe epoch source. Define the enforcement point and persistence of the accepted epoch.

Some external APIs cannot enforce such a token. Then the application needs a supported provider idempotency/reconciliation contract or must tolerate duplicates under a defined product policy. Consensus among your controllers does not give you control over an independent provider's already accepted request. This is the same uncertain-effect boundary established in chapters161–162.

## etcd illustrates different operation guarantees

The inspected [etcd3.6 API guarantee document](https://etcd.io/docs/v3.6/learning/api_guarantees/) distinguishes default KV consistency, weaker read options, watch history and lease behavior. A lower-latency serializable read can observe stale state relative to consensus; a watch is not an immediately current linearizable read. A timed-out operation can remain uncertain even in a consensus-backed service. These distinctions matter when a controller uses watches to make decisions.

Treat a watch as a stream with revision and history rules. Keep the last applied revision, handle disconnection, and recover through the documented resumption or fresh-state path when history is no longer available. Applying every received event without checking the state model can regress a controller after reconnect or make it miss a required resynchronization. A revision is a logical ordering marker within its service contract, not a universal timestamp across databases.

Leases are useful for temporary ownership but must be combined with the protected resource's authority rule. Heartbeat success indicates the lease was maintained under that interaction; it does not prove the process can complete every downstream operation. A controller can retain its lease while its database path is broken. Conversely, a pause can cause lease expiry even while the process later appears healthy.

## Inspect an existing cluster without creating a new one

For an already authorized etcd deployment, use its supported operator tooling and actual TLS identities. Do not connect an improvised lab client to a production Kubernetes control-plane store. This read-only observation assumes an installed etcdctl matching the deployment's supported interface and approved endpoint, CA, client-certificate and private-key files. All three Linux families use these arguments; their package and certificate-provisioning policies differ.

From the operator workstation, set values supplied by the cluster owner. File paths below are example local locations for **existing** credentials, not files created by this chapter:

```bash
coord_endpoint='https://coordination.staging.example:2379'
coord_ca='./operator-ca.pem'
coord_cert='./operator-client.pem'
coord_key='./operator-client-key.pem'
etcdctl --endpoints="$coord_endpoint" --cacert="$coord_ca" \
  --cert="$coord_cert" --key="$coord_key" \
  --dial-timeout=3s --command-timeout=5s \
  endpoint status --write-out=table
```

Replace the documentary endpoint with the actual approved one before execution. `--endpoints` selects the contacted member; the TLS arguments authenticate and verify according to that deployment; dial and command timeouts bound different waiting stages. The [cluster-status guide](https://etcd.io/docs/v3.6/tasks/operator/how-to-check-cluster-status/) documents status inspection. Inspect member identity, leader information and applied/consensus progress fields in the installed tool's output. A status response from one member is not proof that the entire cluster has current quorum or that every client can perform a linearizable request. This command performs no membership change and creates no cleanup target.

## Membership changes are incident-sensitive mutations

A stopped voter still belongs to the voting set until the service's supported membership operation changes that set. Starting replacement processes with new identities can accidentally enlarge the required quorum. Adding several members before they are ready can reduce availability rather than improve it.

etcd's [runtime reconfiguration guidance](https://etcd.io/docs/v3.6/op-guide/runtime-configuration/) describes adding learners and promoting them after catch-up. Use the exact deployed version's workflow and bounds; the example here does not mutate membership. Before changing a cluster, preserve a tested recovery snapshot, inventory current member IDs and peer identities, confirm quorum, and assign the change owner. Rehearse the intended replacement in an isolated environment.

If quorum is lost, restarting a healthy subset or fixing connectivity can restore progress without discarding history. Forced reconstruction from a snapshot changes the recovery boundary and can lose newer data. Do not treat it as routine “remove the unreachable voters” maintenance. Follow the product's disaster-recovery procedure, preserve the old cluster's exclusion and validate clients against the restored revision/state contract.

## Exercises and answer guidance

Does adding a fourth voter to three increase independent voter-loss tolerance? No; both require a majority that tolerates one unavailable voter. Explain placement and latency before changing membership.

A watch has not delivered an update. Does that prove the update did not commit? No. Watch delay and disconnection have a different observation contract; use the authoritative read/revision path.

A consensus lease elects one worker, but its provider accepts requests from an expired worker. What boundary is missing? Enforced fencing or applicable provider idempotency/reconciliation. Local election does not retract external effects.

## Takeaways and verification

Consistency is an observable operation contract; consensus is one mechanism for ordered authority. Quorum intersection, safe membership, durable protocol state and resource-side enforcement all matter. The dated Raft paper and etcd3.6 primary documentation were inspected on2026-10-01. The set lab and existing-cluster inspection example are inline; no consensus implementation, etcd command, membership mutation, lease experiment or cluster restore was executed while authoring.

