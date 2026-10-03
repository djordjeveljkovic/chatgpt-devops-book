# Independent re-review — Chapter 37

Reviewer: review_volume3_021_025 (independent correction review)
Date: 2026-10-04
Reviewed body SHA256: b07403bcbd5ccf25f94860a4c5669160fe966329417ebefe9ec3098ed205b405

## Current scope and findings

Re-read the complete corrected manuscript and current summary against the previously recorded findings. This correction review is restricted to these current files and review records; no manuscript, summary or shared metadata changed.

All previous material findings are resolved. The exact Restic backup now excludes `/etc/dispatchdesk/restic-password`, explains recursive inclusion/rotation consequences and requires absent-password listing verification and independent protected recovery credentials. Backup selection includes `/var/backups/dispatchdesk`, matching Chapter 36's concrete database-consistent dump. SQLite online backup now has a direct primary-source link. Exercises supply answer guidance and protected temporary-restore retention; pending-review prose is removed. Full current body and summary agree with nonexecution limits. No new material issue found.

- Low, “Restore to an isolated destination”, restic ls block: use the reviewed SNAPSHOT_ID consistently instead of unqualified latest, and list the staged-dump path separately when verifying it. The shown listing covers `/etc/dispatchdesk`; the prose also requires dump/release presence. This is optional clarity because snapshot host/time selection and full restored-tree inventory are already required.

## Fresh validation and limits

`python3 tools/check_book.py --chapters 34-37` passed on 2026-10-04: four drafts, 14 shell syntax blocks and 1,333 global local links; no errors or warnings. These do not validate Nginx configuration semantics, systemd runtime, SQL/schema, backup data or distribution package execution. No package installed, unit started/reloaded, SELinux boolean changed, PostgreSQL dump/restore, Restic operation, public request or recovery rehearsal executed. No new external-source inspection performed in this bounded correction review; prior dated primary-source evidence is retained below.

## Prior evidence retained

Read AI_AUTHORING_GUIDE.md and current progress, assigned SKELETON brief and manifest entry, complete manuscript and summary, and relevant prerequisite summaries (Chapters 32–35, 36–39 as applicable). Checked the DispatchDesk order/intent contract against Chapter 10 summary and service/path references against Chapter 34. Read all five assigned bodies together for consistency. Prose is original, coherent and has operational takeaways; findings above identify required gaps rather than placeholders or fabricated measurements.

Primary sources below inspected on 2026-10-03. Inspected Restic 0.19.1 [backup](https://restic.readthedocs.io/en/stable/040_backup.html), [restore](https://restic.readthedocs.io/en/stable/050_restore.html) and [repository checks](https://restic.readthedocs.io/en/stable/045_working_with_repos.html), plus [SQLite online backup](https://www.sqlite.org/backup.html) and PostgreSQL 18 [backup](https://www.postgresql.org/docs/18/backup.html). Recursive source selection establishes password-file inclusion. Snapshot selection and restore-under-target behavior are documented. Plain restic check checks structure; data reading needs the documented stronger check options, which the prose appropriately leaves as an explicit integrity policy rather than claiming every byte was read.

## Validation and limits

`python tools/check_book.py --chapters 36-40` passed: five draft manuscripts, nine shell syntax blocks and 1,315 global local-link checks; no errors or warnings. This is syntax and local-link evidence only. External source availability is established only for successfully retrieved sources listed above, not every external link. PostgreSQL client reports 18.6; no database was initialized or contacted. Restic, Redis CLI/server, APT, DNF and iostat are unavailable in this environment. No package transaction, database dump/restore, repository write/check, cache operation, systemd change, cloud operation, notification, host probe or incident recovery was executed. Documentation inspection is not a live Ubuntu/Fedora/RHEL matrix test. No manuscript, summary, manifest, progress or other shared state was edited by the reviewer.

Verdict: approved
