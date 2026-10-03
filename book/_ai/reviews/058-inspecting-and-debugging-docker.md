# Independent review — Chapter 58

Reviewer: review_055
Date: 2026-10-03
Verdict: approved
Reviewed body SHA256: 43a63decedd274b5311f9b580644e3879e6b4aa366398c7604b2f852094c6d44

## Findings

No unresolved material findings.

The event-readout finding is resolved: both examples capture an explicit UTC client timestamp and pass `--until`, making the look-back commands terminate. Prose distinguishes snapshots from deliberate live streams, identifies the client clock/context, and explains Ctrl-C for the live event client. The UTC timestamp syntax matches the official events reference.

The cleanup finding is resolved: the lab now gives `docker rm dispatchdesk-crash-lab` after evidence collection and explains that the stopped container's metadata/writable layer are removed without removing the image. No force or broad pruning is introduced. Re-inspected the changed commands and their surrounding evidence/recovery explanation; no new material issue was found.

## Factual assessment

The chapter follows the brief's diagnostic tools, host/container correlation and crashing-application sections. Compose service names are correctly passed to Compose commands, and container IDs from `compose ps` are passed to raw Engine commands; it does not assume the generated API container is literally named `api`. `ps --all` correctly finds stopped containers, quiet output selects IDs, and the one-instance constraint plus scaled-service guidance bounds quoted substitutions. The absent-container guard protects the primary inspect sequence. The top/PID sequence is explicitly for a running container; its default running-only Compose lookup would not retrieve a stopped container, so the subsequent PID-zero explanation should be read as a race/daemon-state qualification rather than a complete stopped-container procedure.

Logs, configured logging-driver limitations, inspect templates, runtime exec requirements and default user/working-directory behavior match official documentation. The prior Python slim image supplies the narrow `id`, shell and file-readability checks in this lab. Resource samples are correctly limited to live observations and correlated with configured limits and OOM evidence rather than treated as a diagnosis. The event-buffer warning is correct: the current documentation specifies the last 256 events. Context, rootful/remote/rootless/Desktop boundaries and host journal/data-root checks distinguish the daemon host from the workstation. The shared systemd commands need no Ubuntu/Fedora/RHEL syntax split for the stated installation model.

The controlled Alpine command prints to stderr and exits 42, remains inspectable without `--rm`, and has correctly formed single-backslash continuations. Expected output is explicitly unmeasured. Recovery reasoning protects evidence, secrets and data, relates rollback to compatible image/configuration, and avoids an ad hoc `docker commit` patch. The six exercises have relevant and accurate answer guidance. Local further-reading links resolve, including the corrected Chapter 141 observability link. The API/business-flow limits carry forward from Chapter 57 rather than being redefined. Prose is coherent and repetition is limited; the repaired event-client lifecycle and named cleanup complete the practical procedure.

## Validation evidence and limitations

Read the authoring guide, Chapter 58 brief, manuscript and summary, relevant Chapter 57 Compose prerequisites and the current review context. Computed the inspected body hash using `tools.promote_reviewed.body_hash`.

Inspected official primary documentation on 2026-10-03: [Compose ps](https://docs.docker.com/reference/cli/docker/compose/ps/), [Compose logs](https://docs.docker.com/reference/cli/docker/compose/logs/), [Compose exec](https://docs.docker.com/reference/cli/docker/compose/exec/), [container logs](https://docs.docker.com/reference/cli/docker/container/logs/), [container inspect](https://docs.docker.com/reference/cli/docker/container/inspect/), [container exec](https://docs.docker.com/reference/cli/docker/container/exec/), [container stats](https://docs.docker.com/reference/cli/docker/container/stats/), [container top](https://docs.docker.com/reference/cli/docker/container/top/), [system events](https://docs.docker.com/reference/cli/docker/system/events/), [logging configuration](https://docs.docker.com/engine/logging/configure/) and [runtime metrics](https://docs.docker.com/engine/containers/runmetrics/). Checked argument forms, service versus object identity, stopped/live behavior, templates and event streaming/retention against those sources.

Ran `python tools/check_book.py --chapters 58-58`: ten shell syntax blocks and 1,259 repository local-link checks passed with no errors or warnings. Manually reviewed shell quoting/substitutions, required image executables and inspect field semantics. Manually confirmed both event queries now have explicit cutoffs; static syntax checks alone would not establish their runtime behavior.

No Docker, Compose, crash, log/stat/event capture, HTTP/DNS request or host journal/storage command was executed. No container was created, modified or removed. Image availability, PID mapping, logging-driver output, event history and runtime recovery remain untested. Both prior findings are resolved. Approval covers the reviewed body and documentation/static evidence; runtime limitations remain unchanged.
