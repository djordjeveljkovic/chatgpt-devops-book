# Independent review — Chapter 56

Reviewer: review_054
Date: 2026-10-03
Verdict: approved
Reviewed body SHA256: 2cde41b90a0d80958e6d9a7f5a36e6eade187289cca197d1fa5f2688c513588c

## Findings and resolution

No unresolved material findings remain in the reviewed body.

- Added a non-sensitive marker written through the named volume and read through the replacement container, establishing expected content evidence in addition to mount metadata.
- Added archive extraction into a separate restore-check volume and a content assertion/checksum. The final preflight refuses an existing target name; the text explains tar overwrite behavior and confines the ordinary-file restore to the fresh target. Cleanup includes that additional volume and follows successful validation.
- Added runnable SELinux `-v ...:ro,Z` and backup/restore bind alternatives for the dedicated Fedora/RHEL lab directories. Private `:Z` versus shared `:z`, host metadata effects and inappropriate broad relabeling are explained without disabling enforcement. The ordinary `--mount` path remains suitable for the default Ubuntu case.
- Clarified current prune defaults, `--all` named-volume scope, API 1.42 requirement and references from stopped containers. The lab uses only explicit named removals.

## Factual assessment

The ordered sections match the brief. Writable-layer lifetime, volume independence, daemon-scoped identities, bind paths on the daemon host, read-only mounts, volume population/obscuring, `volume-nocopy`, user-namespace/rootless mapping and narrow deletion cautions are accurately described. Named versus anonymous cleanup behavior for `--rm` and `docker rm -v` is correct. Commands use valid mount source/target syntax and single continuation escapes. The initial local-daemon prerequisite bounds the lab; remote-context notes correctly warn that host paths and backup destinations belong to the daemon host rather than magically transferring from the CLI machine.

Database guidance correctly separates persistence from backup, rejects an uncoordinated live directory copy, identifies logical snapshots versus physical base backup/WAL recovery, and covers consistency across uploaded files and rows. A properly coordinated PostgreSQL filesystem snapshot can be valid; the text says snapshots are not automatically valid rather than categorically forbidding them, consistent with PostgreSQL's documented conditions. `pg_dump` covers one database; global roles/tablespaces require separate global-object capture such as `pg_dumpall`. The chapter does not promise that a checksum proves recoverability or that a mount survives host loss.

Assessment answers are relevant and present; relative links resolve. Repetition is limited and storage/recovery fundamentals are linked to canonical chapters. The revised lab supplies inspectable content and restore evidence while clearly limiting its claims to an ordinary sample file. The initial local-daemon assumptions bound the CLI-host checksum commands; remote notes remain caveats rather than instructions to execute this lab from another machine.

## Validation evidence and limitations

Read `AI_AUTHORING_GUIDE.md`, progress context, Chapter 56 brief and manifest record, the chapter and summary, prerequisite Chapter 55 material/summary, Chapter 45 storage material/summary and Chapter 37 restore material/summary. No prior Chapter 56 review record was present. Only this separate review record was written; manuscript, summary and shared indexes were not edited.

Inspected official primary sources on 2026-10-03: [Docker storage](https://docs.docker.com/engine/storage/), [volumes](https://docs.docker.com/engine/storage/volumes/), [bind mounts](https://docs.docker.com/engine/storage/bind-mounts/), [container run](https://docs.docker.com/reference/cli/docker/container/run/), [container removal](https://docs.docker.com/reference/cli/docker/container/rm/), [volume prune](https://docs.docker.com/reference/cli/docker/volume/prune/), PostgreSQL 18 [backup overview](https://www.postgresql.org/docs/18/backup.html), [filesystem backup](https://www.postgresql.org/docs/18/backup-file.html), [pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html), [pg_dumpall](https://www.postgresql.org/docs/18/app-pg-dumpall.html), [pg_basebackup](https://www.postgresql.org/docs/18/app-pgbasebackup.html) and [continuous archiving](https://www.postgresql.org/docs/18/continuous-archiving.html). Checked mounted-data lifetime, initial copy, read-only behavior, missing bind sources, labeling, cleanup scope, database snapshot/backup boundaries and global objects against these references.

Ran `python tools/check_book.py --chapters 56-56`: nine shell syntax checks and 1,247 repository local-link checks passed with no errors or warnings. Computed the inspected body hash with `tools.promote_reviewed.body_hash`, which strips opening YAML front matter. Reinspected the revised marker, SELinux alternatives, restore guard, cleanup and assessment answers. Checked the actual continuation characters; no doubled trailing backslashes remain. Locally checked only the harmless nested-shell marker `printf` behavior; it emits the intended record followed by a newline. No Docker command was involved in that check.

No Docker daemon, database or storage procedure was executed. No volume/container was created, image pulled, directory relabeled, archive captured/extracted, database backup taken, or recovery measured. Volume/SELinux/runtime behavior is assessed from the commands and official semantics, not execution evidence. Approval is a technical manuscript review, not a measured backup or recovery result.
