---
book: The Complete DevOps Engineering Book
volume: 20
volume_title: "Architecture and Platform Engineering"
chapter: 191
title: "Monoliths, Services and Organizational Boundaries"
slug: monoliths-services-and-organizational-boundaries
status: draft
summary: ../../_ai/chapter-summaries/191-monoliths-services-and-organizational-boundaries.md
---

# Chapter 191 — Monoliths, Services and Organizational Boundaries

An architecture boundary decides who can change what independently and which failures must be handled across that boundary. Counting repositories or containers does not answer either question. Two processes can remain tightly coupled through a shared table and a coordinated release. One process can contain well-separated modules owned by different people, with deliberate interfaces and a straightforward operating model.

Harbor initially has two developers and a low-volume order service. A single deployable application with an asynchronous notification worker can fit its responsibilities. Summit's managed AWS path and Atlas's platform path introduce different staffing and scaling constraints; neither requires splitting every application function into a separate service. This chapter teaches how to choose an extraction, including the option of improving the existing boundary first.

## Four boundaries that are often confused

| Boundary | What it controls | What it does not guarantee |
|---|---|---|
| Code module | Dependencies, interfaces and implementation visibility | Independent deployment or failure isolation. |
| Repository | Source access and contribution workflow | A coherent business capability or independent release. |
| Process/deployment | Runtime resources and release lifecycle | Independent state ownership or a tolerable remote failure. |
| Team responsibility | Decisions, support, service contract and operating work | That all technical dependencies can be removed. |

A modular monolith is a single deployable application organized around deliberate internal boundaries. Modules can prohibit direct access to another module's private tables or types even while sharing a transaction and process. This can reduce accidental coupling without introducing remote communication. The limitation is that release and process failure still affect the application together; scaling one CPU-heavy function independently may be awkward.

A service extraction moves a capability into an independently operated deployment with an explicit contract. It introduces network, identity, timeout, telemetry and partial-failure behavior. Independent operation is an outcome to establish through data and release contracts, not a benefit obtained merely by moving files.

AWS describes decomposition by business capability as organizing around what the business does, with domain understanding needed to identify useful divisions. That can be a helpful starting point, but it does not decide this fictional system's boundaries for us. See [AWS business-capability decomposition](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-decomposing-monoliths/decompose-business-capability.html).

## Follow a customer operation before drawing boxes

DispatchDesk accepts an order only after persisting the order and notification intent. Notification delivery is asynchronous and has a different provider-related failure path. The durable boundary therefore matters more than a visual distinction between “API” and “worker.” A new notification service cannot make the acceptance path depend on an unbounded provider call without changing the customer's contract.

Trace the capability through input validation, authorization, durable state, asynchronous transitions and query responses. List which invariants need to be true together. If order acceptance and creation of the intent currently share one transaction, extraction must preserve that invariant through an explicitly designed integration. [Volume17](../17-distributed-systems-and-data-operations/README.md) owns outbox, delivery and idempotency mechanisms; an architectural diagram is not a substitute for them.

Also trace change. Who changes notification templates? Who approves retry policy? Does changing an order field require simultaneous updates to the worker, dashboard, support tool and reporting query? These are release dependencies. Observe actual revisions and incidents instead of asking teams to guess whether they are loosely coupled.

For a real repository, inspect a bounded period of history and the relevant module directories. Commands such as `git log --since=30.days --name-only --format=oneline -- modules/orders modules/notifications` can reveal co-changing files, but co-change is evidence to investigate rather than proof of bad design. A feature legitimately touching both modules can explain it. Review the actual change intent, tests and release consequences. A low co-change rate can also hide manually synchronized configuration outside the repository.

## A complete boundary-mapping lab

This original local exercise models synchronous call dependencies. Create a disposable directory and save the following as `dependencies.json`. It is a hypothetical future proposal, not an observed DispatchDesk topology.

```json
{
  "orders": ["inventory", "notifications"],
  "inventory": ["pricing"],
  "pricing": [],
  "notifications": ["orders"]
}
```

Save this program as `boundary_check.py` in the same directory:

```python
import json
import sys
from pathlib import Path

def reachable(graph, start):
    found = set()
    pending = list(graph[start])
    while pending:
        node = pending.pop()
        if node in found:
            continue
        found.add(node)
        pending.extend(graph[node])
    return found

def main():
    if len(sys.argv) != 2:
        raise ValueError("usage: boundary_check.py dependencies.json")
    graph = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    if not isinstance(graph, dict) or not graph:
        raise ValueError("graph must be a nonempty JSON object")
    for node, targets in graph.items():
        if not isinstance(targets, list) or not all(isinstance(t, str) for t in targets):
            raise ValueError(f"invalid target list for {node}")
        unknown = set(targets) - set(graph)
        if unknown:
            raise ValueError(f"unknown targets for {node}: {sorted(unknown)}")
    for node in sorted(graph):
        dependencies = reachable(graph, node)
        cycle = node in dependencies
        print(f"{node}: reachable={','.join(sorted(dependencies)) or '-'} cycle={cycle}")

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
```

Run:

```bash
python3 boundary_check.py dependencies.json
```

With this exact input, orders and notifications participate in a cycle. Inventory reaches pricing without cycling; pricing reaches nothing. Remove the synchronous notifications-to-orders edge in a second copy and compare the output. This simulates a proposed interface change only: it does not prove an asynchronous replacement is correct.

The script computes graph reachability, not distributed availability. The actual consequence of a dependency failing depends on whether the call is mandatory, cached, optional, bounded or already completed durably. A cycle is a review signal: it can complicate startup, retries and independent release, but graph shape alone does not identify the business contract. Unknown-node input intentionally fails so a mistyped dependency cannot quietly disappear from the analysis. No network, cloud account or container engine is required for the lab; cleanup consists of deleting only this disposable directory after retaining your notes.

## Choose the first extraction with evidence

| Candidate evidence | Why it may justify extraction | Question that could reverse the decision |
|---|---|---|
| Different load/capacity profile | Independent replicas/resources can improve efficiency | Can a separate worker in the same codebase meet the need? |
| Distinct change cadence and responsible team | Independent releases can reduce coordination | Do data/API changes still require synchronized deployment? |
| Strong isolation need | Separate permission/runtime/storage boundary may limit impact | Does shared state or administration still defeat the intended isolation? |
| Slow external provider path | Asynchronous ownership may isolate retries and quotas | Is durable delivery correctness established, including replay? |
| Clear capability and stable contract | A boundary can survive internal implementation change | Is the domain sufficiently understood, or is the interface still changing weekly? |

For Harbor, improving module interfaces and keeping notification work off the synchronous path can be enough. Two developers taking on multiple independent release pipelines, credentials, dashboards and on-call obligations may lose more time than independent deployment saves. For Summit, a managed queue and distinct notification deployment can fit a measured workload split without a large bespoke platform. Atlas may have several teams whose release and access needs justify stronger isolation, but it still needs compatible contracts.

Do not choose a service because its table count or directory size exceeds an arbitrary threshold. If every request requires synchronous calls to several services, a slow dependency can hold connection/thread resources upstream. The timeout and retry choices must fit one end-to-end deadline rather than each service consuming the full customer budget. Distributed failure handling is the cost of the boundary and belongs in its acceptance criteria.

## Data ownership and independent release

A service needs an authority model for its state. Giving another service direct writes to its private table couples both to storage schema and transaction behavior. Read access can still create hidden availability and schema dependencies. A service contract or deliberate read model can reduce that coupling, with explicit freshness and consistency limits.

Shared storage can be a temporary migration tactic, provided the allowed operations, owners and exit criteria are clear. It is risky to advertise independent deployment while every schema change coordinates all clients. Inventory the actual readers/writers, including maintenance scripts and reports, before moving authority. Maintain a compatibility matrix for old/new versions during the transition.

Consider an extraction in which the new notification worker first consumes the same durable intent format. It can compare decisions in shadow mode without making external deliveries. When authority changes, fence the previous consumer so both do not send. Preserve idempotency and reconciliation evidence. An external side effect makes naive shadowing dangerous: “send from both implementations and compare” is not an acceptable parity test for real notifications.

AWS's [strangler fig guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html) describes gradual routing from an existing application to extracted capabilities and warns about migration dependencies and proxy behavior. The useful principle here is controlled replacement with compatibility evidence; it does not require adopting the guide's particular cloud implementation. The migration should remain capable of preserving current customer behavior while the team learns.

## Test the claimed independence

Use a rehearsal in a disposable/staging environment with representative data. Deploy a backward-compatible worker while the previous API remains active; confirm durable acceptance and notification processing. Delay or stop the notification path and verify the acceptance path's stated behavior. Reintroduce processing and check backlog age, provider quota and duplicate protection. If the new boundary changes those contracts, record that change explicitly instead of labeling it isolation.

Test a malformed or newer event and establish whether it blocks all work or moves to an owned terminal/recovery path. Test old/new API and worker combinations within the promised window. Confirm that telemetry can correlate a request and its asynchronous work without using per-order metric labels. Record controller and credential ownership, including how the receiving team actually handles a page.

Each extra deployable adds recurring work: builds, dependency patches, secret rotation, release verification, runbooks and recovery. Google discusses simplicity as an operational goal in its [SRE simplicity chapter](https://sre.google/sre-book/simplicity/). For our design, the practical test is whether the boundary removes a specific costly coupling or risk while remaining operable by its owners.

## Failure investigation and exercises

**The service was extracted, but releases still stop for a coordinated database change.** Map private-schema readers and writers. The deployment boundary changed, but authority and compatibility did not. Improve the contract/read model or accept the shared-release constraint honestly; adding more processes does not solve it.

**The orders API becomes slow when notification providers time out.** Trace whether the new design introduced a mandatory synchronous dependency, blocked publish path or exhausted shared pool. Preserve durable acceptance semantics; diagnose the bounded integration rather than simply increasing every timeout.

1. Compare Harbor's modular monolith with Summit's independent notification deployment. Name the specific load/team evidence that would justify switching, and the operating work it introduces. A strong answer considers workload and ownership rather than company prestige.
2. Alter the graph lab to add a pricing-to-orders edge. Explain which nodes then participate in cycles and what contract evidence you still need. The program can detect structural reachability but cannot infer whether calls are mandatory.
3. Design a shadow comparison for notification logic. Answer guidance: compare generated decisions against controlled fixtures or an isolated sink; ensure one authority makes real deliveries and retain reconciliation before changing it.

Primary architecture sources were inspected on2026-10-01. The graph exercise was executed with Python3.14.7: the initial cycle, cycle removal and unknown-node failure produced the stated results; its temporary directory was removed. These local checks do not verify a staging migration or failure rehearsal. No service boundary or production deployment was changed during writing.
