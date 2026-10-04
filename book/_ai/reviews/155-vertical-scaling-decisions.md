# Independent review — Chapter 155

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: c8f40e90f1bd9cdcacd0015905b8c99484040982fb9cc88d742c4c8d4a2d3bef

## Scope and findings

Read the entire current body and compact summary, Chapter 155 brief, authoring-guide requirements and relevant Chapters 152–154 context. Reviewed CPU/memory arithmetic, complete JSON/Python lab, serial/parallel limits, hierarchical resource controls, provider compatibility, maintenance/durability, recovery and assessment. No material technical issue found. Summary accurately states the chapter's concepts and lack of executed resize/restore/load evidence.

Arithmetic is correct: ten attempts/s at 0.08 core-seconds/attempt need 0.8 cores; adding one background core yields 1.8 cores, or 0.900 of two cores and 0.450 of four. The 0.65 target therefore rejects the current modeled allocation and accepts the candidate. The model explicitly requires equivalent cores and independently schedulable work and does not predict tail latency. Memory components total 4.0 GiB with reclaimable cache distinguished from required non-reclaimable memory; the text does not incorrectly claim all four GiB are irreducible demand. Serial work and diminishing returns are correctly qualified.

The only executable command is ordinary-user Python arithmetic from the stated directory with its complete input file. No universal resize CLI or incompatible provider action is taught. AWS compatible EBS-backed changes versus migration are correctly scoped; CPU architecture, drivers, root/storage characteristics, addresses and provider stop/start behavior are identified as preflight dependencies. No present pricing, guaranteed capacity, downtime duration or reversible volume-shrink claim is asserted.

Cgroup limits remain restrictive after host expansion and cannot escape ancestor limits. Worker and pool changes are separate resource changes. The maintenance procedure records identities/settings, establishes restorable state, drains bounded accepted work and verifies durable volumes before service startup. Readiness, controlled order/notification outcomes, cgroup allocation and comparable workload evidence are stronger acceptance criteria than boot success. Rollback is conditional on a supported prior size; worker settings must be restored independently and a restore's recovery-point consequences remain explicit. Leak/serial/storage alternatives prevent resize from becoming an unsupported default recommendation. Exercises provide answer guidance; closing Takeaways and verification accurately state conclusions and limits.

Low observation — opening section and cgroup inspection paragraph: the bespoke section outline required by the authoring guide is absent, and the plain “chapter152” mention would read better as a relative Chapter 152 link. Existing actual sections are complete and Chapter 152 is already linked in the introduction, so these are editorial refinements rather than technical blockers.

## Primary evidence checked 2026-10-04

- [AWS EC2 instance type changes](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-resize.html): compatible EBS changes versus new-instance migration, and new-type billing without quoting current prices.
- [AWS resize compatibility](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/resize-limitations.html): architecture, virtualization, networking drivers, NVMe/device mapping and attached-volume limits.
- [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html): hierarchical resource restrictions and ancestor boundaries.

Provider compatibility documentation describes possible routes, not evidence that Harbor's unspecified VPS supports a particular change or rollback. Actual provider documentation and account/storage state must supply that decision.

## Validation and limits

`python3 tools/check_book.py --chapters 155-155` passed one JSON parse, one Python syntax check, one shell syntax check and 1,445 global local links with no warnings/errors. Body hash computed using `tools.promote_reviewed.body_hash`. Calculations and code inspected statically; no Python runtime result presented as measured. No provider resize, stop/start, snapshot/restore, billing lookup, routing change, synthetic business transaction or performance experiment executed. No OS/provider compatibility matrix tested. Documentation and parsing cannot establish real headroom, restorable data, rollback eligibility or downtime. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed the added concise section outline and relative Chapter 152 link. The outline accurately represents the complete chapter's constraint, limit, planning, recovery and decision sequence. The link points to the correct existing prerequisite chapter and contextualizes its read-only inspection procedure. Both earlier optional manuscript refinements are resolved; no technical issue introduced. Fresh body hash computed with `tools.promote_reviewed.body_hash`: c8f40e90f1bd9cdcacd0015905b8c99484040982fb9cc88d742c4c8d4a2d3bef.

Low observation — summary Open threads still asks to add the outline and fix the link, although both are completed. Remove these stale completed tasks during summary maintenance. This does not alter technical approval.

`python3 tools/check_book.py --chapters 155-155` again passed one JSON parse, one Python syntax check, one shell syntax check and 1,446 global local links without errors/warnings. Earlier technical assessment, primary evidence and runtime/provider/restore limitations remain applicable. Only this separate review record updated.

Verdict: approved
