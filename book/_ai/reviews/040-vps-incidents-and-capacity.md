# Independent review — Chapter 40

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: f4e121f38569df4c4ff22beff98fcdc5bd91b2cbbdb8e30263e3aa5b77a53bed

## Findings and repair review

No unresolved material finding. Re-read the entire current manuscript and compact summary on 2026-10-04. The new provider section distinguishes product-specific caps and burst credits from shared-host contention, names steal-time observations, requires correlated interval/provider/service evidence, states guest visibility limitations and describes measured escalation/resize/migration choices without inventing quotas. Package prerequisites now distinguish Ubuntu procps/sysstat from Fedora/RHEL procps-ng/sysstat. pg_monitor/pg_read_all_stats visibility and sensitive privilege scope are explained. Every exercise has answer guidance, and the stale pending-review tail is removed. All previous material gaps are resolved.

Low — monitoring prerequisite paragraph: describe the grant executor as an authorized role administrator rather than a database owner, since ownership of one database does not by itself confer membership-grant authority for cluster-wide predefined roles. The current text also names an administrator and requires policy review, so this is a precision improvement to the prerequisite, not a blocker.

On 2026-10-04 inspected [PostgreSQL 18 predefined monitoring roles](https://www.postgresql.org/docs/18/predefined-roles.html) and [Fedora procps-ng metadata](https://packages.fedoraproject.org/pkgs/procps-ng/procps-ng/) to check the added prerequisites. Role documentation confirms pg_monitor membership in pg_read_all_stats and privileged-information scope. The previously inspected vmstat, sysstat and AWS credit documentation supplies the added observation/limit semantics. Ubuntu's noble procps package URL timed out in reviewer retrieval; no successful exhaustive external-link audit is claimed. No monitoring grant or SQL query was executed.

## Inspection and dated evidence

Read AI_AUTHORING_GUIDE.md and current progress, assigned SKELETON brief and manifest entry, complete manuscript and summary, and relevant prerequisite summaries (Chapters 32–35, 36–39 as applicable). Checked the DispatchDesk order/intent contract against Chapter 10 summary and service/path references against Chapter 34. Read all five assigned bodies together for consistency. Prose is original, coherent and has operational takeaways; findings above identify required gaps rather than placeholders or fabricated measurements.

Primary sources below inspected on 2026-10-03. Inspected [Linux PSI](https://docs.kernel.org/accounting/psi.html), [vmstat manual](https://man7.org/linux/man-pages/man8/vmstat.8.html), [sysstat iostat upstream manual](https://github.com/sysstat/sysstat/blob/master/man/iostat.in), PostgreSQL 18 [statistics](https://www.postgresql.org/docs/18/monitoring-stats.html), and AWS [burstable credit concepts](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html) as one primary example for the missing provider-limit topic. Interval versus since-boot observations, wait-event caution, mount/inode distinction, PSI and conservative data cleanup are sound. SQL uses existing pg_stat_activity columns, valid NULLS FIRST ordering and LIMIT; it was read but not executed or server-parsed. Growth arithmetic 48/12 = 4 months is correct under stated assumptions.

## Repair validation

`python tools/check_book.py --chapters 38-40` passed on 2026-10-04: three drafts, four shell syntax checks and 1,333 global local-link checks; no errors or warnings. Re-review read only these assigned current manuscripts/summaries and earlier review findings; other manuscripts and records were not edited. Earlier source inspection is retained below as documentary evidence and does not claim repeat runtime checks.

## Validation and limits

`python tools/check_book.py --chapters 36-40` passed: five draft manuscripts, nine shell syntax blocks and 1,315 global local-link checks; no errors or warnings. This is syntax and local-link evidence only. External source availability is established only for successfully retrieved sources listed above, not every external link. PostgreSQL client reports 18.6; no database was initialized or contacted. Restic, Redis CLI/server, APT, DNF and iostat are unavailable in this environment. No package transaction, database dump/restore, repository write/check, cache operation, systemd change, cloud operation, notification, host probe or incident recovery was executed. Documentation inspection is not a live Ubuntu/Fedora/RHEL matrix test. No manuscript, summary, manifest, progress or other shared state was edited by the reviewer.

Verdict: approved
