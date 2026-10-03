# Chapter 70 — Podman Host Operations and Incidents

Status: complete

## Written material
Storage, upgrades and resource pressure; Upgrades and rollback boundaries; Service recovery and registry failures; Resource pressure and recovery sequence; Operating a fleet of rootless hosts; Exercises and review questions; Takeaways and further reading.

## Concepts and terminology
Account-aware fleet inventory; graph root/backing filesystem/inodes; scoped reclaim; engine migration maintenance; persistent registry auth through host `[Service]` REGISTRY_AUTH_FILE; OOM evidence; canary and recovery acceptance

## Examples and assumptions
Disposable Linux rootless labs executed by the owning ordinary account unless an administrator command is explicitly marked. Ubuntu 24.04 LTS, Fedora 44 and supported RHEL 9/10 package versions require local confirmation. Examples use fully qualified illustrative tags; production requires measured digests. No container runtime, package installation, registry transfer, systemd activation or host mutation was executed.

## Cross-references
Relative canonical links embedded in chapter; prerequisite Chapter 69.

## Open threads
Independent technical/editorial review required. Validate commands on target distribution and installed Podman version; run bounded labs on disposable authorized hosts. Confirm digest/platform, rootless mappings, security policy and restart behavior before production use.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Technical sources and dates
Official primary documentation inspected 2026-10-03: Podman system-df(1), system-prune(1), system-migrate(1), events(1), login(1), stats(1), auto-update(1).

## Actual checks performed
Primary-source inspection and author inspection of examples. `python3 tools/check_book.py --chapters 61-70` passed: 10 draft chapters, 53 shell syntax checks, 2 YAML parses and 1,333 local links; no errors or warnings. Chapter 68 embedded Python compiled separately without execution. These are static checks, not runtime acceptance.

## Checks not performed
No runtime, network, volume, boot, upgrade, restore or registry test. Syntax parsing cannot establish runtime behavior.
