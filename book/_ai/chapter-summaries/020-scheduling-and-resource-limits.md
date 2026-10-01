# Chapter 20 continuation

Status: complete

## Written material
Complete chapter on eligibility versus execution/completion, wallclock/elapsed/timezones, full user-service/timer timestamp lab, catch-up limits, Cronie/Ubuntu implementation distinction, complete Bash flock contention lab, stable lock identity, descriptor/process limits, overlap and descriptor-leak incidents, exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
OnCalendar/OnUnitInactiveSec, Persistent catch-up, randomized delay/accuracy, advisory local flock, descriptor-held lock lifetime, soft/hard limits, legitimate concurrency versus resource leak.

## Examples and cross-references
Full inline user service/timer pair; parser/read-only/lifecycle reader commands with cleanup; conceptual noninstalled cron entry; complete trusted-owned-dir lock script; read-only ulimit. Chapters13/15/16/18 linked through concepts. Lock outside inventory population explicitly required.

## Open threads
Independent review. No timers/services/crontabs installed/started, no baseline VM scheduler or limit stress. No distributed locks/snapshot guarantee asserted. Reader host cron implementation must be checked before extensions.

## Verification
Inspected upstream systemd timer/time, util-linux flock, Cronie crontab and Linuxgetrlimit manuals hostedman7. Outside sandbox socket restrictions, extracted temporary user service+timer pair verified by systemd-analyze262 with exit0/no diagnostics. Calendar parsed/normalized and next three UTC elapses at five-minute boundaries. Lock fixture executed: first acquired; concurrent second exit75; first finished0; third acquired after completion/finished0. All temporary context removed, no unit installed or activated. Validator checks Bash/local links only; actual schedule execution and descriptor limits not stress tested.
