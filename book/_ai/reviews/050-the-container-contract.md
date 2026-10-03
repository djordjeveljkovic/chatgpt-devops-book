# Independent review — Chapter 050

Verdict: changes required
Review date: 2026-10-02
Scope: chapter body, summary, Chapter 49 prerequisite, Chapter 45 storage explanation, prerequisite/canonical summaries, manifest and authoring contract.

## Factual summary

The chapter defines a replaceable application instance through signal handling, stdout/stderr logging, external configuration, readiness, durable-state ownership and restart-safe processing. It includes a fictional DispatchDesk shell entrypoint, a data-lifetime table and five assessment questions. Its core recommendations are generally sound, and the prose is clear with little unnecessary repetition. It does not yet supply an operational procedure or assessment answer guidance.

## Unresolved findings

1. **Medium — wrong canonical reference; chapter line 36, “Chapter 74 covers graceful application shutdown.”** Chapter 74 is *Modules and Infrastructure Boundaries* and concerns Terraform. Replace this with the appropriate application/process shutdown explanation, or a correctly scoped link such as Chapter 107 for Kubernetes probes and termination. The present reference sends readers to unrelated material.

2. **Medium — missing practical procedure and inspectable recovery evidence; lines 22–36 and 64–80.** The sole script assumes a nonexistent-for-the-reader `/usr/local/bin/dispatchdesk` binary and its `serve --listen` interface, without identifying it as an illustrative application contract beside the example or showing how it becomes the container entrypoint. There is no runnable, self-contained procedure to observe PID 1, send a stop signal, measure the grace period, inspect logs/exit state, provoke a failed assumption and verify recovery. Add a small disposable lab with an inline application or explicit prerequisites, execution host/user/directory, stop timeout, expected evidence, failure diagnosis and cleanup. Explain that the configured stop signal can differ from SIGTERM. Keep runtime documentation inspection distinct from execution. For mount failure diagnosis, distinguish Unix UID/GID/mode or rootless mappings from SELinux on Fedora/RHEL and AppArmor on Ubuntu, with correctly scoped canonical links rather than treating Linux policy as a single permission mechanism.

3. **Medium — assessment lacks answer guidance; lines 82–88.** All five items are questions only. Add compact expected reasoning, including shell PID 1 versus `exec`, measured shutdown versus forced SIGKILL, reconstructible versus authoritative state, permission/policy inspection before changes, dependency readiness versus restart loops, and the expand/backfill/contract migration sequence. This is explicitly required by the chapter brief and authoring guide.

4. **Low — internal references are not relative links; lines 14, 36, 58 and 60.** The prerequisite and canonical pointers to Chapters 49, 74, 36/37 and 45 are plain text. Provide correct relative links and link the rootless identity/security explanations where the mount discussion depends on them. The link checker cannot detect an incorrect plain-text chapter number, which explains why finding 1 passes structural validation.

5. **Low — source attribution joins directives from different manuals; line 92.** `TimeoutStopSec` is documented by systemd.service, while `KillSignal` is documented by systemd.kill. Split the citations. For container stop behavior cite Docker's stop CLI reference directly, rather than relying on a systemd service timeout to substantiate an engine lifecycle policy.

## Actual validation evidence and limits

- Read `AI_AUTHORING_GUIDE.md`, `PROGRESS.md`, Chapter 050's skeleton brief and manifest entry, the chapter and summary, Chapter 049 and its summary, Chapter 045 and its summary, and summaries for Chapters 036, 037, 041 and 074. The manifest confirms Chapter 107's probes/termination topic and Chapter 074's Terraform module topic.
- Ran `python tools/check_book.py --chapters 50-50`: exit 0; one chapter checked, one shell-syntax block checked, 1,226 repository local links checked, no errors or warnings. This is syntax/link evidence, not runtime evidence; the tool's local-link count covers the repository, not 1,226 links in this chapter.
- Inspected official [Docker run documentation](https://docs.docker.com/engine/containers/run/), [Dockerfile reference](https://docs.docker.com/reference/dockerfile/#entrypoint), [Docker stop reference](https://docs.docker.com/reference/cli/docker/container/stop/) and [logging documentation](https://docs.docker.com/engine/logging/) on 2026-10-02. These support disposable layer/mount distinctions, exec-form entrypoint concerns, configurable stop signal and timeout, and stdout/stderr collection with logging-driver caveats.
- Attempts to retrieve the freedesktop systemd.service and systemd.kill pages failed (internal fetch error/403); their contents were not successfully independently inspected in this review.
- No application binary, Docker/Podman engine, signal-delivery test, health endpoint, volume, logging backend or database recovery was executed or inspected. No package or cloud resources were changed. No approval hash is recorded because material findings remain unresolved.
