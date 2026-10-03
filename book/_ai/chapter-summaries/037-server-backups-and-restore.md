# Chapter 37 continuation

Status: complete

## Written material
RPO/RTO definition; reproducible host vs data recovery; remote encrypted backup boundary; illustrative Restic SFTP workflow with explicit credential exclusion and listing verification; staged PostgreSQL dump from Chapter 36; database-consistent backup separation; isolated restore workflow and protected cleanup; full-service recovery and integrity/retention; answer-guided exercises.

## Concepts and terminology
Recovery point/time objectives, failure domain, immutable artifact, encrypted repository, database-consistent backup, restore rehearsal, retention, repository integrity.

## Examples and cross-references
Restic selection excludes its own password file and includes protected PostgreSQL dump staging; PostgreSQL dump/restore instructions are in Chapter 36. Sample snapshot restore targets mktemp directory and is not executed. Links to chapters 31, 32, 34, 36 and 38.

## Open threads
Restic SFTP account/backend, package, backup and restore not run. Adapt path, target credentials and retention; no production data or repository involved.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Restic 0.19.1 official backup, restore and repository-check docs inspected 2026-10-04. No backup or restore evidence is claimed. Scoped and full book syntax/link checks passed on 2026-10-04.
