# Independent review — Chapter 152

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: c9bdc1a09345981f852dd9df8057bc0587cae712d591cc75a222cadd40bdbe2b

## Scope and findings

Read the complete current manuscript and compact summary, Chapter 152 brief, authoring-guide requirements and Chapter 151 prerequisite context. Reviewed utilization denominators, Linux load/available-memory distinctions, PSI and cgroup scope, bounded CLI/Python examples, runtime-specific CPU versus waiting explanations, operational recovery, exercises and local links. No material technical issue found. The summary accurately represents the chapter's concepts and explicitly bounded diagnostic scope.

The `systemctl show --property=MainPID --value` lookup and guarded `top -b -H -d 1 -n 3 -p` invocation are structurally sound for the stated existing service. PID identity/reuse and permissions are acknowledged. `vmstat 1 6` is bounded; the text correctly distinguishes since-boot activity from interval reports and instantaneous process/memory fields. Ubuntu procps versus Fedora/RHEL procps-ng packaging, installed-help/version checks and MAC restrictions are appropriately qualified rather than promising uniform visibility.

Linux load is not CPU utilization; aggregate host utilization can conceal a saturated serial thread. PSI stall measurements are not interchangeable with utilization. The qualification about system-level CPU full pressure matches kernel documentation. Cgroup membership/mount discovery and namespaces prevent a guessed path from being presented as authoritative. Cumulative memory/CPU counters need interval comparison, host headroom does not disprove a cgroup limit kill, and managed limits should be changed through their owner. The chapter avoids attributing every restart to memory events without contextual evidence.

Python's wall-versus-process CPU measurement correctly distinguishes bounded hashing from intentional sleep; it is explicitly a demonstration rather than a service benchmark or realistic database simulation. The retained-payload exercise is correct: 1,000 × 64 KiB = 62.5 MiB before object and allocator overhead. Recovery guidance preserves queued intent, constrains concurrency, requires headroom for temporary limit increases, and verifies process stability, memory growth and customer-visible outcomes. Exercises include answer guidance.

Low observation — final paragraph immediately before sources: an explicit concise Takeaways section would make compliance with the authoring guide easier to inspect. The existing closing paragraph already states utilization scope, waiting, ownership and runtime lessons, so this is a presentation improvement rather than a material completeness gap.

## Primary evidence checked 2026-10-04

- [Linux PSI](https://docs.kernel.org/accounting/psi.html): pressure accounting, scope and system-level CPU full qualification.
- [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html): resource hierarchy, CPU throttling and memory event/limit semantics.
- [procps-ng top manual](https://man7.org/linux/man-pages/man1/top.1.html): batch/thread modes, delay, iteration count, PID selection and CPU display conventions.
- [procps-ng vmstat manual](https://man7.org/linux/man-pages/man8/vmstat.8.html): bounded delay/count, initial report accounting and instantaneous process/memory fields.
- [Python time documentation](https://docs.python.org/3/library/time.html): wall elapsed counter and process CPU timer semantics; process CPU excludes sleep.

These are current primary project documentation/manuals, not evidence of installed distribution behavior. No profile-specific CLI is taught from the author's failed profile-document retrieval.

## Validation and limits

`python3 tools/check_book.py --chapters 152-152` passed: three shell syntax checks, one Python syntax check and 1,445 global local links; no errors or warnings. Exact stripped-front-matter body hash computed with `tools.promote_reviewed.body_hash`. Commands and arithmetic inspected statically. No diagnostic command against a live service, Python timing demonstration, profiler attachment, load test, cgroup mutation or recovery action was executed. No Ubuntu/Fedora/RHEL runtime matrix tested. Static syntax and documentation checks cannot establish actual service identity, permissions, kernel configuration, observed pressure, bottleneck or recovery effectiveness. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed the added explicit Takeaways section and updated compact summary. The takeaways accurately summarize user-visible boundaries, utilization denominators, combined pressure/throttling/memory evidence, interval counters, discovered cgroup paths and resource ownership with outcome verification. The earlier optional body observation is resolved; no material technical issue introduced. Fresh body hash: c9bdc1a09345981f852dd9df8057bc0587cae712d591cc75a222cadd40bdbe2b, computed with `tools.promote_reviewed.body_hash`.

Low observation — summary, Open threads: “Add explicit concise takeaways” remains as a stale instruction despite the section now being present and listed under Written material. Remove that completed item in the next summary maintenance pass. It does not change the manuscript's technical approval.

`python3 tools/check_book.py --chapters 152-152` again passed three shell syntax checks, one Python syntax check and 1,445 local links with no warnings/errors. Earlier full technical assessment, primary evidence and runtime limits remain applicable. Only this separate review record updated.

Verdict: approved
