# Chapter 62 — The Podman Container Lifecycle

Status: complete

## Written material
Run, inspect, exec, logs and cleanup; Rootless versus rootful state; Operating an HTTP service; Diagnose a failed assumption; Exercises and review questions; Takeaways and further reading.

## Concepts and terminology
Container metadata versus process; bounded HTTP evidence; inspect/log/exec distinctions; local account store; retained exit evidence; graceful stop and replacement

## Examples and assumptions
Disposable Linux rootless labs executed by the owning ordinary account unless an administrator command is explicitly marked. Ubuntu 24.04 LTS, Fedora 44 and supported RHEL 9/10 package versions require local confirmation. Examples use fully qualified illustrative tags; production requires measured digests. No container runtime, package installation, registry transfer, systemd activation or host mutation was executed.

## Cross-references
Relative canonical links embedded in chapter; prerequisite Chapter 61.

## Open threads
Independent technical/editorial review required. Validate commands on target distribution and installed Podman version; run bounded labs on disposable authorized hosts. Confirm digest/platform, rootless mappings, security policy and restart behavior before production use.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Technical sources and dates
Official primary documentation inspected 2026-10-03: Podman inspect(1), logs(1), stop(1), run(1).

## Actual checks performed
Primary-source inspection and author inspection of examples. `python3 tools/check_book.py --chapters 61-70` passed: 10 draft chapters, 53 shell syntax checks, 2 YAML parses and 1,333 local links; no errors or warnings. Chapter 68 embedded Python compiled separately without execution. These are static checks, not runtime acceptance.

## Checks not performed
No runtime, network, volume, boot, upgrade, restore or registry test. Syntax parsing cannot establish runtime behavior.
