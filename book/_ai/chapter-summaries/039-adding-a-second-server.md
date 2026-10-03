# Chapter 39 continuation

Status: complete

## Written material
Why second host; state externalization and interchangeable API; database routing and pool limits; load-balancer readiness; safe rollout/drain/rollback; failure testing and exercises.

## Concepts and terminology
Failure domain, stateless app instance, shared authority, database cutover, private path, readiness, drain, connection multiplication, active-active consistency.

## Examples and cross-references
Harbor design uses two API VMs, PostgreSQL authority, optional derived Redis cache and separately governed notification worker. Connection-budget exercise now includes the 78-connection arithmetic, ambiguity about process count, headroom, memory and fencing guidance. Architecture only; no infrastructure. Links to chapters 10, 27, 29, 34–38, 163 and later AWS paths.

## Open threads
No second host, database, router, TLS or traffic cutover was performed. Probe thresholds, connection budgets and provider network controls remain workload/host specific.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Nginx upstream and PostgreSQL connection/backup primary docs inspected 2026-10-04. No infrastructure or cutover performed. Scoped and full book syntax/link checks passed on 2026-10-04.
