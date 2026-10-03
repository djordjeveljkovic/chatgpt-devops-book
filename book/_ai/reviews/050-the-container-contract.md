# Independent review — Chapter 050

Reviewer: review_054
Verdict: approved
Review date: 2026-10-03
Reviewed body SHA256: 7b7fa2e687a60e7bd17044db48620f44901785bf2517ca7411a63c86e3b6815f
Scope: revised chapter body, summary, previous findings, chapter brief, authoring contract and linked canonical topics.

## Resolved previous findings

- Replaced the incorrect Chapter 74 shutdown pointer with the relative Chapter 107 probes/termination link.
- Replaced the undefined application wrapper with a generic `exec "$@"` entrypoint and supplied a complete Python program, Dockerfile, build/run/stop/inspect/log workflow and cleanup. Host, daemon authorization, directory and synthetic-drain assumptions are explicit. Configurable stop signals and forced deadline behavior are explained.
- Added compact answer guidance for every assessment question, covering PID 1, durable state, permission/policy diagnosis, dependency readiness and expand/backfill/contract migrations.
- Converted prerequisite/canonical pointers to relative links and separately explained Unix identity/mode, rootless mapping, Fedora/RHEL SELinux and Ubuntu AppArmor.
- Split `TimeoutStopSec` and `KillSignal` source links and explicitly withheld systemd fetches as Docker evidence. Docker stop behavior now has a direct primary reference.

## Startup-race resolution and residual findings

No unresolved material findings remain.

The revised `wait_for_started` helper is called before both stop demonstrations. Its marker is printed only after Python registers the SIGTERM handler, so a successful observation establishes the relevant startup boundary rather than relying on elapsed time or an unrelated `docker exec`. A missing marker triggers a bounded twenty-attempt loop with quarter-second pauses; an observed stopped container breaks the loop early. Failure prints state and logs and returns nonzero, and both call sites exit before sending the experimental signal. The logging-driver readability assumption is explicit.

The five-second description represents the configured polling/sleep budget, not a hard wall-clock deadline: Docker CLI/daemon round trips and diagnostics add latency and could block if the daemon is unresponsive. This does not undermine the controlled disposable-host signal experiment or its finite retry count, but it should not be reused as an incident deadline guarantee without per-command timeouts.

The earlier incorrect chapter pointer, undefined app, absent practical procedure, assessment guidance, relative links and combined systemd source attribution are all resolved. No additional material issue was found in the revised examples, answers or claims.

## Factual assessment

The runtime contract, logging/configuration boundaries, disposable versus durable state, readiness/liveness distinction and restart-safe schema/processing advice remain sound. Python registers its handler in the main thread, raises `SystemExit(0)` after the synthetic wait and flushes observable output. Dockerfile exec form, wrapper replacement, stop-signal selection, timeout flags, inspection templates and named cleanup are correct. Python's `time.sleep` can be interrupted by a Python signal handler; the stop mechanism is not forced to wait for the normal sixty-second sleep to end. The lab accurately limits its purpose to synthetic process shutdown rather than real HTTP request draining.

Exit 137 is appropriately qualified and correlated with timing and OOM state instead of treated as unique diagnosis. Local execution prerequisites avoid remote PID/path confusion. No distribution-specific installation is introduced; security-policy differences are explained separately and linked. Questions and answers are aligned, navigation resolves, and prose repetition is modest.

## Validation evidence and limitations

Re-read the revised manuscript, existing review and chapter summary against the authoring guide and Chapter 050 skeleton brief. Inspected canonical link targets and kept earlier review context for Chapters 49, 45, 36/37, 47/48 and 107.

Inspected official primary documentation on 2026-10-03: [Docker run](https://docs.docker.com/reference/cli/docker/container/run/), [Docker stop](https://docs.docker.com/reference/cli/docker/container/stop/), [Dockerfile entrypoint](https://docs.docker.com/reference/dockerfile/#entrypoint), [Docker logging](https://docs.docker.com/engine/logging/), [OCI runtime lifecycle](https://github.com/opencontainers/runtime-spec/blob/main/runtime.md), [Python 3.12 signal](https://docs.python.org/3.12/library/signal.html) and [Python 3.12 time](https://docs.python.org/3.12/library/time.html). The manuscript reports failed systemd documentation access and makes no Docker claim depend on it; those manuals were not independently successfully fetched in this review.

Ran `python tools/check_book.py --chapters 50-50`: five shell syntax checks, one Python syntax check and 1,271 repository local-link checks passed with no errors or warnings. Computed the inspected body hash with `tools.promote_reviewed.body_hash` after stripping opening YAML. Independently traced the startup-marker ordering and both helper call sites; syntax checks alone cannot establish runtime signal readiness. Inspected the actual single continuation escapes and current body-hash match.

No Docker/Podman build or operation occurred. No image was pulled, container started/stopped, handler signaled, logging backend inspected, volume changed or database recovery performed. The Python application was not run. Approval is based on primary-documentation review, static command/control-flow inspection and the repository checks above. No measured process-drain result is asserted.
