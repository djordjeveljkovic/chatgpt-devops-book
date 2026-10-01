---
book: The Complete DevOps Engineering Book
volume: 20
volume_title: "Architecture and Platform Engineering"
chapter: 193
title: "Multi-tenancy and Isolation"
slug: multi-tenancy-and-isolation
status: draft
summary: ../../_ai/chapter-summaries/193-multi-tenancy-and-isolation.md
---

# Chapter 193 — Multi-tenancy and Isolation

A tenant is a customer or organizational population whose data, permissions or resource expectations must be kept distinct. DispatchDesk might serve several businesses through one API. Atlas's platform can also host several internal teams, creating another tenancy layer. Application customer isolation and infrastructure team isolation are different: a namespace for the orders team does not separate that team's customer records.

Choose isolation from assets, threats, operating obligations and economics. A tenant who sends API requests has different attack opportunities from a tenant who can upload arbitrary workloads or obtain a database session. “Dedicated” needs qualification: a dedicated application process sharing a database administrator and recovery key is not independent in every relevant failure or access path.

## Identify the boundary and authority

| Layer | Isolation question | Authority that must enforce it |
|---|---|---|
| Identity | May this authenticated subject act for the requested tenant? | Verified identity and authorization policy. |
| Application/data | May this operation read or change this record? | Tenant-scoped application contract and applicable database controls. |
| Cache/message | Does this derived or delayed item retain tenant context? | Key schema, producer/consumer validation and access policy. |
| Resource use | How much shared capacity may this tenant consume? | Admission, scheduling, pool and workload controls. |
| Administration | Can one team modify another's workload or platform controls? | Account/cluster/API permissions and management boundaries. |
| Recovery | Can one tenant be restored without exposing or damaging another? | Backup layout, recovery tooling and authorized procedure. |

Tenant identifiers arriving in headers, URLs or messages are claims to validate, not authority. Derive the active tenant from an authenticated subject's permitted memberships and the operation's policy. Administrative support needs an explicit audited path; it should not quietly bypass scope through an undocumented flag.

A record ID can be globally unique or unique only within a tenant. Either scheme needs authorization: unguessable identifiers are not access control. Tenant-specific encryption limits some exposure, but if the shared application can obtain every key, its compromise can still cross those boundaries. Trace the actual trust path rather than assuming a label or key name establishes isolation.

## Choose pooled or dedicated resources

| Design | Why it can fit | Residual cost/risk |
|---|---|---|
| Shared application and tenant-scoped tables | High utilization and simple fleet operation for many modest tenants | Scoping bugs, contention and selective recovery complexity. |
| Shared application with separate schemas/databases | More distinct data and maintenance boundaries | Connection budgets, migration fleet and administrative access remain shared concerns. |
| Separate deployments with shared dependencies | Different release/configuration/compute envelopes | Shared database, gateway or control plane can still couple failures. |
| Separate infrastructure/account/cluster | Stronger permission and operating separation where justified | More patching, telemetry, cost allocation and recovery work. |

These are points on a spectrum, not tiers every business must climb. Harbor may pool ordinary API customers with careful scopes and per-tenant admission. Summit can retain a pooled path while placing a specially constrained customer in separate resources. Atlas must assess internal workload trust and platform-administrator authority alongside customer-data requirements.

Kubernetes's [multi-tenancy discussion](https://kubernetes.io/docs/concepts/security/multi-tenancy/) treats isolation strength as a spectrum involving control and data planes. A namespace provides useful scope for namespaced policies/resources. It does not provide a separate kernel, node or cluster-scoped control plane. For mutually hostile workloads, decide whether stronger runtime/node/cluster separation is needed and identify what remains shared.

## Complete tenant-scoped data lab

This original Python/SQLite exercise needs Python3 on Ubuntu or Fedora/RHEL. Save it as `tenant_lab.py` in a disposable directory. Fictional already-authenticated subjects demonstrate authorization and query scoping; this is not token verification or a production API.

```python
import sqlite3

# Fixtures representing memberships returned by a trusted identity system.
MEMBERSHIPS = {"alice": {"tenant-a"}, "bob": {"tenant-b"}}

def authorized_tenant(authenticated_subject, requested_tenant):
    allowed = MEMBERSHIPS.get(authenticated_subject, set())
    if requested_tenant not in allowed:
        raise PermissionError("subject is not permitted for this tenant")
    return requested_tenant

def fetch_order(db, tenant, order_id):
    return db.execute(
        "SELECT payload FROM orders WHERE tenant_id = ? AND order_id = ?",
        (tenant, order_id),
    ).fetchone()

def main():
    db = sqlite3.connect(":memory:")
    try:
        db.execute("""CREATE TABLE orders (
            tenant_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            payload TEXT NOT NULL,
            PRIMARY KEY (tenant_id, order_id))""")
        db.executemany("INSERT INTO orders VALUES (?, ?, ?)", [
            ("tenant-a", "order-1", "A-only payload"),
            ("tenant-b", "order-1", "B-only payload"),
        ])
        # Deliberately wrong lookup exposes missing tenant scope.
        wrong = db.execute(
            "SELECT payload FROM orders WHERE order_id = ? ORDER BY tenant_id",
            ("order-1",),
        ).fetchone()
        print("Unscoped lookup:", wrong[0])
        bob_tenant = authorized_tenant("bob", "tenant-b")
        print("Bob's scoped lookup:", fetch_order(db, bob_tenant, "order-1")[0])
        try:
            authorized_tenant("bob", "tenant-a")
        except PermissionError:
            print("Cross-tenant claim rejected")
        else:
            raise AssertionError("cross-tenant authorization unexpectedly passed")
        assert fetch_order(db, bob_tenant, "missing") is None
        assert fetch_order(db, bob_tenant, "' OR 1=1 --") is None
        assert fetch_order(db, "tenant-a", "order-1")[0] == "A-only payload"
        print("Missing/injection-shaped identifiers remained scoped values")
    finally:
        db.close()

if __name__ == "__main__":
    main()
```

Run `python3 tenant_lab.py`. The incorrect lookup returns tenant A's payload even when used from Bob's request path. The authorized scoped lookup returns B's payload, while a forged tenant A claim is rejected. Bound parameters keep the injection-shaped identifier a value; binding and authorization solve different problems. The process closes its in-memory database, leaving no retained database. Remove the owned lab files after retaining observations.

In a real server, obtain the subject from verified identity, not a supplied name. Every read/write/list operation needs scope, including administrative jobs. Calling `fetch_order` with an arbitrary tenant bypasses the preceding authorization; the helper alone is not an enforcement boundary. Centralize the request context and review privileged entry points. Tests should deliberately use the same order identifier in two tenants so accidental global lookup is visible.

PostgreSQL row-level security can add a database policy boundary. Its [row security reference](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) explains that superusers and `BYPASSRLS` roles bypass it; owners normally do too, subject to `FORCE ROW LEVEL SECURITY`. A test as the database administrator cannot establish application-role isolation. Policies need explicit read/write behavior and actual role testing. If tenant context is a session setting writable by the same shared application role, it can protect against some accidental unscoped queries but is not a strong boundary against that role's arbitrary SQL access.

## Preserve context in caches and asynchronous work

A cache keyed only by `order-1` can leak results even if the database query is correctly scoped. Include tenant and relevant authorization/version dimensions. Beware of caching a privileged representation and returning it through an ordinary user's path. Invalidation and tenant deletion must reach derived data too.

An asynchronous intent needs durable context and an authorized producer/consumer contract. A worker must not trust a payload tenant merely because a message arrived. Source permissions, schema, tenant authority and operation semantics determine what it can do. Scope idempotency keys to operation and tenant according to the contract; one customer's key should not suppress another's work.

Keep tenant attribution in controlled logs/audits without confidential payloads. Per-tenant metric labels can become costly with a large dynamic population; use bounded classes and controlled drilldown where appropriate. The telemetry and distributed-data volumes own these mechanisms. This chapter adds the requirement to preserve tenancy through every derived path, including exports, support tools and delayed messages.

## Bound noisy-neighbor effects

Isolation includes availability. Expensive queries, large payloads or retries can consume shared resources. Per-tenant admission should account for work cost, concurrency and dependency budgets, rather than raw request count alone. One large report can cost more than hundreds of cached reads.

In an original planning example, a shared worker can sustain100 equal-cost jobs/second. Tenant A submits80 and other tenants collectively submit40. Demand120 exceeds capacity even though no tenant exceeds100. Giving A at most60 and reserving40 for the others can bound interference, but A's excess20 must be rejected, deferred within an explicit age limit or assigned capacity. Fairness does not create throughput; retention and customer policy remain necessary.

Kubernetes [ResourceQuota](https://kubernetes.io/docs/concepts/policy/resource-quotas/) bounds aggregate namespace requests, limits and object counts. It does not directly guarantee request latency or database fairness. [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/) needs an enforcing network implementation and observed allow/deny tests; accepting the object is insufficient evidence. Application authorization remains necessary when network reachability is restricted.

Evaluate gateway admission, application concurrency, database pools, worker scheduling, storage and external provider quotas. A dedicated API deployment sharing an unbounded pool can still affect every tenant. Isolation may require reserved headroom; account for normal utilization and surviving capacity after failures. Observe the actual resource that causes interference before adding replicas.

## Administration and recovery

Onboarding should establish identity, limits, retention, access/telemetry and deletion/recovery policy before production work. Templates help, but a submitted `owner` label is not authenticated ownership, as [Chapter192](192-platform-teams-and-developer-experience.md) shows. Tenant administrators should not gain shared-platform permissions through convenience tooling. Maintain separate approval and audit for operations spanning customers.

Selective restoration is difficult with pooled data. Rolling back the entire database can damage unaffected customers; extracting one tenant requires referential integrity, conflict handling and reconciliation of external effects. Dedicated backup scope can simplify recovery while still depending on shared keys and artifacts. Define deletion across backups, logs and caches according to the organization's actual retention policy.

For suspected disclosure, preserve scoped audit evidence and contain the affected path using the security incident procedure. Do not copy all customer data into a debugging channel. Determine which subjects, records and exports were accessible, revoke inappropriate access and repair the invariant. A patched query does not undo already disclosed information or external actions.

## Exercises and operating conclusions

1. Add `list_orders` to the lab and prove Bob cannot enumerate A. Include missing and forged-tenant cases. Good answers validate membership and scope the query; a random-looking ID is irrelevant.
2. Design cache/idempotency keys for two tenants using the same order ID. Explain collision prevention and how deletion reaches derived records.
3. Review Atlas's claim that “a namespace per hostile customer” provides complete isolation. Assess runtime/nodes/control-plane permissions, storage/network enforcement and administrators.
4. If A's excess20 jobs/second is deferred for ten minutes, backlog grows by12,000 jobs. Decide whether the contract permits the resulting age and retention. A fair scheduler alone cannot remove overload.

A useful isolation statement names an asset, threat and enforced boundary, alongside shared dependencies and administrators. Primary Kubernetes/PostgreSQL sources were inspected on2026-10-01. The SQLite lab ran with Python3.14.7: incorrect/scoped lookups, forged-tenant rejection and missing/injection-shaped identifier assertions passed, and the owned temporary directory was removed. This is distinct from unexecuted database-role, quota, policy and hostile-workload tests; no production tenancy changes were performed.
