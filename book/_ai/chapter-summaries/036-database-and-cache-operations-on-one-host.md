# Chapter 36 continuation

Status: complete

## Written material
Single-host contention and service ownership; Ubuntu 24.04, Fedora 42 and RHEL 9 package/cluster discovery caveats; private PostgreSQL/Redis-compatible-cache boundaries; connection and memory budgets; bounded custom-format PostgreSQL dump and isolated restore; cache persistence trade-offs; monitoring-role visibility; read-only health inspection; separation criteria; answer-guided failure exercises.

## Concepts and terminology
Authority vs derived cache, listener vs authentication, `listen_addresses`, HBA, SCRAM, bounded pools, concurrent query memory, Redis ACL/eviction/persistence, RPO/RTO, WAL, restore validation.

## Examples and cross-references
Harbor uses PostgreSQL as authority for paired orders and intents; Redis is optional reconstructible cache. Local-only service check commands are observational and require distro-specific identity/service validation. Links to chapters 10, 27, 31, 33 and 163.

## Open threads
No host commands run against production; service names, versions, paths, ACLs and database role must be adapted to target distro. No backup was produced or restored.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Official PostgreSQL 18 connection, resource, dump/restore, backup and monitoring-role docs; Ubuntu and RHEL package guidance; and Redis security, ACL and persistence docs inspected 2026-10-04. No service changes, dump, restore or integration test performed. Scoped and full book syntax/link checks passed on 2026-10-04.
