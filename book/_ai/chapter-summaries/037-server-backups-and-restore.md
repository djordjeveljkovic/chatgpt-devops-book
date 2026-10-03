# Chapter 37 continuation

Status: draft; independent review pending.

## Written material
RPO/RTO definition; reproducible host vs data recovery; remote encrypted backup boundary; illustrative Restic SFTP workflow; database-consistent backup separation; isolated restore workflow; full-service recovery and integrity/retention; diagnosis and exercises.

## Concepts and terminology
Recovery point/time objectives, failure domain, immutable artifact, encrypted repository, database-consistent backup, restore rehearsal, retention, repository integrity.

## Examples and cross-references
Restic config/releases backup excludes active PostgreSQL data directory; PostgreSQL backup lives in Chapter 36. Sample snapshot restore targets mktemp directory and is not executed. Links to chapters 31, 32, 34, 36 and 38.

## Open threads
Restic SFTP account/backend, package, backup and restore not run. Adapt path, target credentials and retention; no production data or repository involved. Independent review pending.

## Exact next section
None. Begin Chapter 40, then request independent review before claiming completion.

## Verification
Book shell syntax and local links checked. Restic 0.19.1 official backup, restore, repository-check and quickstart docs inspected 2026-10-02. No restore evidence is claimed.
