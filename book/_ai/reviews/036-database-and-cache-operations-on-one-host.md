# Independent re-review — Chapter 36

Reviewer: review_volume3_021_025 (independent correction review)
Date: 2026-10-04
Reviewed body SHA256: 68af75c47e8fb515e4e126166ecc8ea50f31bf01a6dd71724818c8abc037d3a2

## Current scope and findings

Re-read the complete corrected manuscript and current summary against the previously recorded findings. This correction review is restricted to these current files and review records; no manuscript, summary or shared metadata changed.

All previous material findings are resolved. The body now supplies a protected custom-format pg_dump and archive-list check plus an isolated template0 database/pg_restore --exit-on-error procedure, identifies peer-authentication/server-client-version and role/extension/grant limits, and requires schema/application/order-intent verification. The staging path is concretely consumed by Chapter 37. Distro package/cluster discovery now separates Ubuntu cluster units from umbrella state, Fedora initialization and RHEL streams; Redis authentication failures are distinguished from PONG. Answer guidance is complete and pending-review prose is removed. No new material issue found.

- Low, distro examples and summary: Fedora 42 is explicitly named, whereas the book baseline is Fedora 44. Preserve the dated release qualification or update the example during future baseline maintenance; the chapter does not claim its package defaults apply universally.

## Fresh validation and limits

`python3 tools/check_book.py --chapters 34-37` passed on 2026-10-04: four drafts, 14 shell syntax blocks and 1,333 global local links; no errors or warnings. These do not validate Nginx configuration semantics, systemd runtime, SQL/schema, backup data or distribution package execution. No package installed, unit started/reloaded, SELinux boolean changed, PostgreSQL dump/restore, Restic operation, public request or recovery rehearsal executed. No new external-source inspection performed in this bounded correction review; prior dated primary-source evidence is retained below.

## Prior evidence retained

Read AI_AUTHORING_GUIDE.md and current progress, assigned SKELETON brief and manifest entry, complete manuscript and summary, and relevant prerequisite summaries (Chapters 32–35, 36–39 as applicable). Checked the DispatchDesk order/intent contract against Chapter 10 summary and service/path references against Chapter 34. Read all five assigned bodies together for consistency. Prose is original, coherent and has operational takeaways; findings above identify required gaps rather than placeholders or fabricated measurements.

Primary sources below inspected on 2026-10-03. Inspected [PostgreSQL 18 connection settings](https://www.postgresql.org/docs/18/runtime-config-connection.html), [resource consumption](https://www.postgresql.org/docs/18/runtime-config-resource.html), [backup overview](https://www.postgresql.org/docs/18/backup.html), [pg_restore](https://www.postgresql.org/docs/18/app-pgrestore.html), [Ubuntu PostgreSQL installation](https://ubuntu.com/server/docs/how-to/databases/install-postgresql/), and Redis [security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/), [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/) and [persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) documentation. They support listener/auth separation, per-operation memory, derived-cache loss versus durable data and backup boundaries. No incorrect fixed tuning value is given.

## Validation and limits

`python tools/check_book.py --chapters 36-40` passed: five draft manuscripts, nine shell syntax blocks and 1,315 global local-link checks; no errors or warnings. This is syntax and local-link evidence only. External source availability is established only for successfully retrieved sources listed above, not every external link. PostgreSQL client reports 18.6; no database was initialized or contacted. Restic, Redis CLI/server, APT, DNF and iostat are unavailable in this environment. No package transaction, database dump/restore, repository write/check, cache operation, systemd change, cloud operation, notification, host probe or incident recovery was executed. Documentation inspection is not a live Ubuntu/Fedora/RHEL matrix test. No manuscript, summary, manifest, progress or other shared state was edited by the reviewer.

Verdict: approved
