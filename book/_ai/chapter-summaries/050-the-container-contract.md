# Chapter 50 continuation

Status: complete; independently approved 2026-10-03.

## Written material
Runtime contract; generic exec-form shell wrapper; stdout/stderr/configuration/readiness; disposable versus durable state; separate UID/DAC, rootless mapping, Fedora/RHEL SELinux and Ubuntu AppArmor diagnosis; complete Python signal/timeout lab with graceful and deliberately forced stop, inspect/log evidence, cleanup; restart-safe design; five exercises with answer guidance.

## Concepts and terminology
PID 1, `exec`, `STOPSIGNAL`, grace period, synthetic shutdown/drain, readiness, liveness, persistent state, rootless UID/GID maps, SELinux labels, AppArmor profiles, expand/backfill/contract migration.

## Examples and cross-references
Dockerfile, `entrypoint.sh`, Python signal handler, two disposable container runs comparing `--stop-timeout 5` vs `1`, PID 1 inspection and cleanup. Relative links to chapters 36, 37, 44, 45, 47, 48, 49 and 107. No runtime execution.

## Open threads
Systemd pages returned HTTP 403 and are identified as separate host analogies; Docker-specific stop source was reviewed. Docker signal lab not executed; approval rests on primary-source and static review.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Docker lifecycle, `docker stop`, logging, OCI Runtime docs inspected 2026-10-03; systemd directive links separated. Chapter checker passed with five shell checks, one Python syntax check and 1,271 local links. Full-book checker passed after current changes. No container build/stop was run.
