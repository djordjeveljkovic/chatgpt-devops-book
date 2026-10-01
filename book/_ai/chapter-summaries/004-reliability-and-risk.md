# Chapter 4 continuation

Status: complete

## Written material
Availability/durability/correctness; physical and administrative failure domains; correlation; explicit risk-budget example; backup-access dependency incident; exercises.

## Concepts and terminology
Introductory risk budget and failure-domain model; full SLO/recovery semantics deferred to 181. Replica versus backup purpose.

## Examples and cross-references
Harbor risk map, newly introduced fictional 99.5% time-based objective over 30 days counting maintenance; 216-minute arithmetic. Distinguishes Chapter 002 illustrative request-based example. Links 003, 005, 181 and official PostgreSQL18 backup overview.

## Open threads
Independent review; later Harbor chapters must explicitly preserve/revise target and define actual recovery objectives.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Official SRE risk, AWS AZ isolation and PostgreSQL18 backup docs inspected 2026-10-01. Arithmetic manually checked; no service availability or backup/restore/provider execution.
