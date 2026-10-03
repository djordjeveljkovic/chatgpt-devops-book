# Independent review — Chapter 60

Reviewer: review_054
Date: 2026-10-03
Verdict: approved
Reviewed body SHA256: 45352d85459b17d802492a780851da0e794cfd995b9b1ef674c9143ce5a2507a

## Findings and resolution

No unresolved material findings remain in the final reviewed body.

1. **Resolved — separate storage filesystem.** Added Engine 29 fresh-install containerd-store defaults, separate system-containerd root/configuration inspection, actual root substitution, byte/inode checks and the Docker data-root limitation. Optional embedded mode is distinguished rather than assuming all installations use `/var/lib/containerd`. The Chapter 45 link and answer guidance now reflect that storage split. Embedded mode is an optional experimental feature in current docs; the chapter does not recommend enabling it.
2. **Resolved — daemon/logging rollout evidence.** Added `dockerd --validate --config-file`, its non-starting validation semantics, actual systemd startup-flag review, authorized restart/service/default inspection, effective per-container `.HostConfig.LogConfig` inspection, deployment-controlled recreation, override detection and known-good configuration rollback. File validation is correctly distinguished from systemd flag conflicts and service availability.
3. **Resolved — resource claim.** Memory/CPU/PID boundaries are qualified; disk, I/O, network, daemon/host and aggregate use remain separate controls. Swap is identified as a distinct policy. Example limits remain workload-measured choices rather than an availability guarantee.
4. **Resolved — links and summary.** Chapter 57/58 health references are relative links, and the required summary now exists with factual contents, assumptions and execution limitations.

## Factual assessment

The ordered sections match the brief, and the production review table, fictional canary failure, failure-boundary reasoning, exercises with answer guidance, takeaways and primary sources are present. Host/context boundaries are explicit: Docker state follows the selected daemon while filesystem/systemd checks belong on its owning host. Ubuntu and Fedora/RHEL share these rootful systemd commands; rootless/Desktop differences and SELinux enforcement are properly qualified.

Docker's default `json-file` has no default rotation; `local` rotates and compresses by default. The displayed `local` `max-size`/`max-file` JSON options are valid strings. The chapter correctly requires merge rather than replacement of existing JSON, distinguishes daemon defaults from existing containers, warns about restart availability and avoids externally rotating Docker-managed log files. Remote logging back-pressure/outage behavior is correctly treated as something to validate, not a universal guarantee. The rough log-cap estimate is appropriately qualified for compression/overhead and fleet aggregate use.

Docker health state does not trigger standalone restart policy repair. `unless-stopped`, cgroup-supported memory/CPU/PID flags and crash/OOM diagnosis are correctly described, including the revised resource and swap boundaries. The digest placeholder is explicit and not presented as a valid runnable release identity; the example preserves real configuration as an adaptation prerequisite. No ad hoc parallel deployment is recommended for a managed stack.

`docker system prune` scope is correctly separated from `--all` image widening and `--volumes` unused anonymous-volume removal. The chapter does not claim this command removes named volumes. It warns that an unused data object or cached rollback image can still matter, preserves database recovery ownership and recommends scoped retention rather than automated broad destruction. Recovery reasoning distinguishes bad release, dependency, host pressure and daemon configuration rather than treating every incident as a restart.

Relative links that exist resolve, prose is clear, and duplication is limited. The revised procedure supplies the concrete capacity, validation and rollout evidence needed by the brief.

## Validation evidence and limitations

Read the authoring guide, Chapter 60 brief/manifest record, current manuscript, prerequisite Chapter 59 summary, and relevant canonical storage/host/operations context from this review session. No Chapter 60 review or summary existed at the start of the initial inspection. Re-read the final revised body and newly supplied summary after the author corrected all findings; the author confirmed manuscript edits were finished before this approval hash.

Inspected official primary Docker sources on 2026-10-03: [logging configuration](https://docs.docker.com/engine/logging/configure/), [local logging driver](https://docs.docker.com/engine/logging/drivers/local/), [daemon configuration](https://docs.docker.com/engine/daemon/), [dockerd CLI/validation](https://docs.docker.com/reference/cli/dockerd/), [containerd image store](https://docs.docker.com/engine/storage/containerd/), [resource constraints](https://docs.docker.com/engine/containers/resource_constraints/), [restart policies](https://docs.docker.com/engine/containers/start-containers-automatically/), [live restore](https://docs.docker.com/engine/daemon/live-restore/), [Dockerfile health checks](https://docs.docker.com/reference/dockerfile/#healthcheck), [system df](https://docs.docker.com/reference/cli/docker/system/df/) and [system prune](https://docs.docker.com/reference/cli/docker/system/prune/). Checked default rotation/retention, configuration strings and new-container scope, file validation versus startup, daemon roots, health/restart distinctions, limit/swap behavior, prune scope and live-restore limitations against those references.

Ran `python tools/check_book.py --chapters 60-60`: eight shell syntax checks, one JSON parsing check and 1,294 repository local-link checks passed, with no errors or warnings. The chapter summary now exists and was independently read; static link checks alone did not detect its earlier absence. Computed the reviewed body hash with `tools.promote_reviewed.body_hash`, stripping opening YAML.

No Docker command, daemon validation, systemd operation, registry access, filesystem/configuration mutation, service rollout, workload/load test or recovery was executed. No measured log retention or resource capacity is claimed. Only this separate review record was written. Approval is a primary-documentation/static manuscript review, not measured daemon availability, capacity or recovery evidence.

Additional final source check: Docker’s [embedded containerd documentation](https://docs.docker.com/engine/daemon/embedded-containerd/) describes the optional experimental mode (Engine 29.7.0+) and its default state under the Docker data root, supporting the revised mode distinction. Attempts to fetch an obsolete daemon/containerd documentation path and old Moby source paths failed; those failures were not used as evidence. The successful official daemon, dockerd and embedded-containerd references substantiate the final storage statements.
