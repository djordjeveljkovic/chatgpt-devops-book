# Chapter 40 continuation

Status: complete

## Written material
Incident roles, read-only Linux triage and distro package prerequisites, PostgreSQL activity query with monitoring-role visibility guidance, symptom-to-layer paths, provider caps and noisy-neighbor evidence, stabilization choices, capacity forecasting, post-incident review and answer-guided exercises.

## Concepts and terminology
Customer impact, timeline, load average, reclaimable memory, inode exhaustion, interval metrics, PSI, DB wait events, reversible mitigation, capacity reserve, incident action.

## Examples and cross-references
Observational host commands; read-only `pg_stat_activity` query omits SQL text and needs reviewed monitoring grants for cross-user visibility; hypothetical filesystem growth arithmetic; provider metrics are examples, not asserted limits. Links chapters 30, 33, 36, 37, 39 and volume 5.

## Open threads
No VPS/database query or incident was run. Tool and kernel support vary. Example SQL must be run using an authorized monitoring role and reviewed for local permissions. Provider metrics and thresholds vary by instance family.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Linux PSI, vmstat/iostat, PostgreSQL monitoring-role, Ubuntu/Fedora/RHEL package, and AWS burst-credit documentation inspected 2026-10-04. SQL was not run and no capacity action/provider limit is claimed. Run scoped and full book checks before promotion.
