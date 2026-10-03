# Chapter 36 continuation

Status: draft; independent review pending.

## Written material
Single-host contention and service ownership; private PostgreSQL/Redis boundaries; connection and memory budgets; PostgreSQL backup choices and restore rehearsal; Redis derived-cache persistence trade-offs; read-only health inspection; separation criteria; failure exercises.

## Concepts and terminology
Authority vs derived cache, listener vs authentication, `listen_addresses`, HBA, SCRAM, bounded pools, concurrent query memory, Redis ACL/eviction/persistence, RPO/RTO, WAL, restore validation.

## Examples and cross-references
Harbor uses PostgreSQL as authority for paired orders and intents; Redis is optional reconstructible cache. Local-only service check commands are observational and require distro-specific identity/service validation. Links to chapters 10, 27, 31, 33 and 163.

## Open threads
No host commands run against production; service names, versions, paths, ACLs and database role must be adapted to target distro. No backup was produced or restored. Independent review pending.

## Exact next section
None. Begin Chapter 37, then request independent review before claiming completion.

## Verification
Book checker passed chapter-specific syntax and links. Official PostgreSQL 18 connection, resource and backup docs and Redis security, ACL and persistence docs inspected 2026-10-02. No service changes or integration test performed.
