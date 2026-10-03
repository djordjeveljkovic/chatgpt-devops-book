# Chapter 39 continuation

Status: draft; independent review pending.

## Written material
Why second host; state externalization and interchangeable API; database routing and pool limits; load-balancer readiness; safe rollout/drain/rollback; failure testing and exercises.

## Concepts and terminology
Failure domain, stateless app instance, shared authority, database cutover, private path, readiness, drain, connection multiplication, active-active consistency.

## Examples and cross-references
Harbor design uses two API VMs, PostgreSQL authority, optional derived Redis cache and separately governed notification worker. Architecture only; no infrastructure. Links to chapters 10, 27, 29, 34–38, 163 and later AWS paths.

## Open threads
No second host, database, router, TLS or traffic cutover was performed. Probe thresholds, connection budgets and provider network controls remain workload/host specific. Independent review pending.

## Exact next section
None. Begin Chapter 40, then request independent review before claiming completion.

## Verification
Book link and syntax checks pending for the final volume batch. Nginx upstream and PostgreSQL connection/backup primary docs inspected 2026-10-02.
