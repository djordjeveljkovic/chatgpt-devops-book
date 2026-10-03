# Chapter 40 continuation

Status: draft; independent review pending.

## Written material
Incident roles, read-only Linux triage, PostgreSQL activity query, symptom-to-layer paths, stabilization choices, capacity forecasting, post-incident review and exercises.

## Concepts and terminology
Customer impact, timeline, load average, reclaimable memory, inode exhaustion, interval metrics, PSI, DB wait events, reversible mitigation, capacity reserve, incident action.

## Examples and cross-references
Observational host commands; read-only `pg_stat_activity` query omits SQL text; hypothetical filesystem growth arithmetic. Links chapters 30, 33, 36, 37, 39 and volume 5.

## Open threads
No VPS/database query or incident was run. Tool and kernel support vary. Example SQL must be run using an authorized monitoring role and reviewed for local permissions. Independent review pending.

## Exact next section
None. Begin Chapter 41, then request independent review before claiming completion.

## Verification
Book shell syntax and local links checked. Linux PSI, vmstat/iostat, and PostgreSQL monitoring sources inspected 2026-10-02. No capacity action is claimed.
