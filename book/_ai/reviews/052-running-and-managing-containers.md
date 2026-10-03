# Independent review — Chapter 52

Reviewer: review_052
Date: 2026-10-02
Verdict: changes required
Inspected body SHA256: 469171a9a13eb7780ac87eb181891afd649c93e1ff713374065e1f1e1e516a95

## Findings

1. **Medium — execution host and privilege prerequisites, lines 18–38 and 67.** The active context may point to a remote disposable Linux host, while `curl 127.0.0.1` and socket inspection run on the shell's host. Chapter 51 explicitly permits remote contexts and initially verifies Docker with `sudo`; this chapter neither establishes authorized unprivileged daemon access nor specifies that the shell and daemon are on the same host. Require a local Engine context on the actual test host, identify the CLI user's required access, and say that host socket checks and `curl` run there. Otherwise a correct remote deployment produces a misleading local connection failure.

2. **Medium — unbounded loopback isolation assumption, lines 27 and 49.** The chapter gives no Engine version baseline, but describes localhost publication as limiting access to local clients. Docker documents an exception for releases before 28.0.0: peers in the same L2 segment can reach localhost-published ports. State the supported/default bridge-network assumptions and Engine 28.0.0 or newer for this isolation claim, or explicitly describe the older-release exception. The generic final firewall caveat does not communicate this specific security boundary. Evidence: [Docker port publishing](https://docs.docker.com/engine/network/port-publishing/).

3. **Medium — assessment and navigation contract, lines 18, 27, 85 and 87–93.** There is no prerequisite link to Chapter 51; references to Chapters 49 and 50 are plain text; the five exercises have no answer guidance. Add relative links to the canonical chapters and concise expected-answer guidance, including default publication when the host address is omitted, preserved inspection evidence, restart diagnosis and scoped cleanup. These are explicit authoring-guide and chapter-brief requirements.

4. **Low — volume cleanup wording, lines 43–45.** Clarify that `docker rm -v` removes anonymous volumes and never removes named volumes; `--rm` also removes associated anonymous volumes. The named-volume sentence is correct, but the adjacent generic warning can leave a novice unsure which data the option deletes. Evidence: [Docker container removal](https://docs.docker.com/reference/cli/docker/container/rm/) and [Docker container creation options](https://docs.docker.com/reference/cli/docker/container/create/).

## Factual summary

The chapter teaches create/run/start/stop/remove distinctions, detached Nginx execution, explicit IPv4 loopback publication, inspection and logs, restart policy, request-path diagnosis and narrowly named cleanup. The mutable learning tag is clearly separated from production digest selection. The second run example explicitly warns about duplicate names, and cleanup preserves the cached image. Prose is readable with modest useful repetition; lifecycle and network fundamentals are not excessively duplicated. Commands and Go templates are syntactically plausible and match the official references. No distribution-specific package, mount or security-policy changes occur in this lab; installation and access are prerequisite concerns.

## Validation evidence and limits

Read the authoring guide, progress context, Chapter 52 brief and manifest record, chapter and summary, Chapter 51 and its summary, and Chapters 49/50 canonical material and summaries. No previous Chapter 52 review record existed.

Inspected current official Docker documentation on 2026-10-02: [run](https://docs.docker.com/engine/containers/run/), [create](https://docs.docker.com/reference/cli/docker/container/create/), [start](https://docs.docker.com/reference/cli/docker/container/start/), [stop](https://docs.docker.com/reference/cli/docker/container/stop/), [remove](https://docs.docker.com/reference/cli/docker/container/rm/), [listing and filters](https://docs.docker.com/reference/cli/docker/container/ls/), [port](https://docs.docker.com/reference/cli/docker/container/port/), [inspect](https://docs.docker.com/reference/cli/docker/inspect/), [logs](https://docs.docker.com/reference/cli/docker/container/logs/), [restart policies](https://docs.docker.com/engine/containers/start-containers-automatically/), [port publishing](https://docs.docker.com/engine/network/port-publishing/) and [firewalls](https://docs.docker.com/engine/network/packet-filtering-firewalls/). Checked detach/name/publish/restart arguments, inspection templates, tail count, created versus running states, stop escalation, restart limitations and scoped removal against those sources.

Ran `python tools/check_book.py --chapters 52-52`: five shell syntax checks and 1,226 repository local-link checks passed with no errors or warnings. Computed the inspected body hash using `tools.promote_reviewed.body_hash`; it identifies the reviewed draft and does not assert approval.

The chapter's Docker and curl commands were not executed. No daemon, image pull, container, firewall or restart behavior was runtime-tested. Documentation and shell parsing do not establish actual host exposure or application behavior. Material findings 1–3 remain unresolved; approval is withheld.
