---
book: The Complete DevOps Engineering Book
volume: 22
volume_title: "Operational Reference"
chapter: 213
title: "Docker and Podman Command Reference"
slug: docker-and-podman-command-reference
status: complete
summary: ../../_ai/chapter-summaries/213-docker-and-podman-command-reference.md
---

# Chapter 213 — Docker and Podman Command Reference

This reference is for the moment when you know the question but cannot remember the command. Container mechanisms belong in [Volume 5](../05-container-internals-and-oci/README.md), Docker workflows in [Volume 6](../06-docker-in-practice/README.md), and rootless host operation in [Volume 7](../07-podman-and-the-rootless-host/README.md). Start with the target engine and execution identity: an excellent command against the wrong daemon is still the wrong operation.

## Establish whose containers you are seeing

| Question | Docker | Podman | Interpretation |
|---|---|---|---|
| Which client version? | `docker --version` | `podman --version` | Client output alone does not establish a remote server version. |
| Which execution endpoint? | `docker context show`; `docker context inspect` | `podman system connection list` for remote connections | Also inspect environment overrides before assuming the configured default is effective. |
| What can this engine report? | `docker info` | `podman info` | Storage, runtime and rootless-related details explain many apparent differences. Review before sharing output containing host details. |
| Which objects exist here? | `docker ps -a` | `podman ps -a` | `-a` includes stopped containers; an empty result says nothing about another endpoint or another user's storage. |

Docker contexts select daemon endpoints and related configuration. `DOCKER_HOST`, `DOCKER_CONTEXT` and explicit command options can affect selection; inspect them in the same shell that will run the operation. Podman ordinarily operates locally on Linux; named system connections matter when using its remote client. A listed connection is not evidence that an ordinary local invocation used it. These distinctions come from the [Docker context reference](https://docs.docker.com/reference/cli/docker/context/) and [Podman connection reference](https://docs.podman.io/en/latest/markdown/podman-system-connection.1.html).

```bash
id
printf 'DOCKER_HOST=%s\nDOCKER_CONTEXT=%s\n' "${DOCKER_HOST-}" "${DOCKER_CONTEXT-}"
printf 'CONTAINER_HOST=%s\nCONTAINER_CONNECTION=%s\n' "${CONTAINER_HOST-}" "${CONTAINER_CONNECTION-}"
docker context show
docker context inspect
```

The final two commands require Docker. With Podman use `podman info` and, for a remote workflow, `podman system connection list`. Rootless Podman storage belongs to the invoking user. Running `sudo podman ps` changes that scope; it does not grant a wider view of the same rootless container inventory. This explains the common Harbor incident in which an administrator believes the application disappeared after changing to a root shell.

Before modifying an object, record the engine endpoint, host, user and container ID. A friendly name may be reused when a deployment replaces the object. A monitoring history for yesterday's ID does not necessarily describe today's container of the same name.

## Lifecycle and image lookup

The following shorthand uses `ENGINE` to mean either `docker` or `podman`; replace it in your shell. Shared spelling does not promise identical defaults, inspect schemas or orchestration support.

| Task | Command pattern | What to remember |
|---|---|---|
| Fetch an image | `ENGINE pull registry.example.invalid/team/api@sha256:DIGEST` | Replace registry and digest with an actual approved artifact. A tag can move; a digest identifies content. |
| List cached images | `ENGINE images` | Local availability does not prove a registry still serves the image. |
| Inspect cached image | `ENGINE image inspect IMAGE` | Check platform, configured user, entrypoint and command before diagnosing startup. |
| Create and start | `ENGINE run --name NAME IMAGE` | Creates a new object. Calling it again can fail because the name already exists. |
| Start an existing object | `ENGINE start NAME` | Reuses its existing configuration; it does not adopt a newly pulled image automatically. |
| Stop an object | `ENGINE stop -t 30 NAME` | Gives the process a termination window; timeout can lead to forced termination. |
| Observe termination | `ENGINE wait NAME` | Useful in a bounded job workflow; it can wait indefinitely for a service. |
| Remove one stopped object | `ENGINE rm NAME` | Removes that container's writable layer, not a backup of application data. |

`--pull=never` makes a run depend on the local image cache and fail if absent. It is useful for a prepared offline lab, and different from pinning the image: the former controls lookup while the latter controls identity. Docker and Podman both document `missing`, `always` and `never` policies; Podman additionally documents `newer`. Do not copy its extra policy into a Docker script. Publishing `127.0.0.1:18080:8080` maps a host loopback port to the container's port8080; `EXPOSE` alone does not create this mapping. See the [Docker run options](https://docs.docker.com/reference/cli/docker/container/run/) and [Podman run options](https://docs.podman.io/en/latest/markdown/podman-run.1.html).

For production services the runtime's stop timeout must fit the application's drain behavior and the deployment controller's deadline. A process that ignores termination or is hidden behind an unforwarding shell wrapper can be killed before finishing an accepted request. The [Podman stop reference](https://docs.podman.io/en/latest/markdown/podman-stop.1.html) and [Docker stop reference](https://docs.docker.com/reference/cli/docker/container/stop/) describe the signal and timeout behavior; `-t` selects seconds in both engines, while the current long spellings are Podman `--time` and Docker `--timeout`; application correctness still requires the shutdown work taught in the container and delivery volumes.

## Inspect a failing service before replacing it

| Question | Command | Evidence limit |
|---|---|---|
| Did its main process exit? | `ENGINE inspect NAME` | State fields differ between engines; inspect the actual JSON rather than assuming a shared template. |
| What did it write recently? | `ENGINE logs --since 10m --tail 200 --timestamps NAME` | Bounded logs can omit an earlier cause; logging driver, rotation and application output determine availability. |
| What process tree exists? | `ENGINE top NAME` | The displayed users/PIDs depend on engine and namespace presentation. |
| What is its current resource use? | `ENGINE stats --no-stream NAME` | One sample can miss bursts; memory accounting is not identical across platforms. |
| Which ports were published? | `ENGINE port NAME` | Mapping does not establish application readiness or remote reachability. |
| Which filesystem paths were changed? | `ENGINE diff NAME` | Writable-layer differences do not represent all mounted-volume data. |
| Can an included diagnostic program run? | `ENGINE exec NAME PROGRAM ARGUMENTS` | Distroless images may lack a shell, curl or package manager. |

Log timestamps aid correlation but do not repair clock drift. `--tail` bounds returned lines, `--since` bounds time selection and `--timestamps` adds engine timestamps. A successful log request with no lines does not establish a quiet application: it may log to a file, have rotated its output, or use an unavailable logging path. The [Docker logs reference](https://docs.docker.com/reference/cli/docker/container/logs/) describes these flags and supported log retrieval behavior.

```bash
docker inspect --format '{{json .State}}' dispatchdesk-api
docker inspect --format '{{json .Mounts}}' dispatchdesk-api
docker logs --since 10m --tail 200 --timestamps dispatchdesk-api
docker stats --no-stream dispatchdesk-api
docker port dispatchdesk-api
```

These are targeted inspection examples, requiring an existing Docker object named `dispatchdesk-api`. They may expose operational details; use scoped output rather than publishing the entire inspect document. A configuration can contain environment secrets. The [Docker inspect reference](https://docs.docker.com/reference/cli/docker/container/inspect/) supports formatting, while [Podman's inspect reference](https://docs.podman.io/en/latest/markdown/podman-container-inspect.1.html) documents its own fields. Treat machine-readable output as a versioned interface in automation.

An OOM-related state field is evidence of runtime observation, but the absence of it does not rule out a host-level memory failure or a supervisor killing the workload. Compare the container's limit, cgroup events, host pressure and application timeline. Docker's Linux stats display adjusts its memory reporting for cache; numbers copied into a spreadsheet need an accounting definition. See [Docker stats](https://docs.docker.com/reference/cli/docker/container/stats/), [Chapter211](211-linux-and-shell-command-reference.md) and [Chapter217](217-scaling-and-architecture-decision-tables.md).

For a connection failure, diagnose in order: is the process running, does it listen on the expected container interface, is a host port published, and can the actual client reach it? An application listening only on container loopback will not automatically accept traffic directed to the container's other interface. A successful host-loopback curl also does not establish internet reachability through the VPS firewall and provider controls. Use [Chapter212](212-networking-and-vps-diagnostic-reference.md) for those layers.

## Build and distribution lookup

| Task | Docker | Podman | Operational distinction |
|---|---|---|---|
| Build current context | `docker build -t dispatchdesk-api:lab .` | `podman build -t localhost/dispatchdesk-api:lab .` | The final dot is the build context; its files and ignore rules affect what reaches the builder. |
| Select recipe | `docker build -f Dockerfile.release .` | `podman build -f Containerfile.release .` | A recipe path does not change the meaning of the context automatically. |
| Select target stage | `docker build --target test .` | `podman build --target test .` | A named stage is a build graph selection, not a runtime environment flag. |
| Add destination tag | `docker tag SOURCE DESTINATION` | `podman tag SOURCE DESTINATION` | Adds a reference; it does not rebuild the artifact. |
| Push artifact | `docker push DESTINATION` | `podman push DESTINATION` | Requires registry rights; inspect the published digest and platform selection. |
| Save/load local transport | `docker save -o image.tar IMAGE`; `docker load -i image.tar` | `podman save -o image.tar IMAGE`; `podman load -i image.tar` | Archive compatibility depends on format; preserve image metadata and verify after import. |

Docker's build entry integrates with its builder tooling; advanced multi-platform behavior belongs to the Docker chapter using Buildx, rather than assuming every `build` invocation publishes a complete platform set. Podman builds have their own supported flags and defaults. The relevant command sources are [Docker image build](https://docs.docker.com/reference/cli/docker/image/build/) and [Podman build](https://docs.podman.io/en/latest/markdown/podman-build.1.html).

For Atlas, the deployable record includes the registry digest, platform and provenance, not just the CI job's green status. A successful build for an engineer's ARM laptop can still produce the wrong artifact for an x86 worker. A runtime permission problem should be reproduced using the image's configured user and mounts; rebuilding with root can hide the defect while expanding privileges.

## Rootless and storage symptom index

| Symptom | First evidence | Next decision |
|---|---|---|
| Root shell sees no rootless containers | User identity and `podman info` storage details | Return to the service owner and intended execution context. |
| Mounted directory is unwritable | Host mode/ownership, container user, user-namespace map, SELinux denial evidence | Change the specific ownership/mapping or labeling arrangement justified by evidence. |
| Podman runs interactively but fails after logout | User service logs and lifecycle configuration | Review Quadlet, user systemd and deliberate lingering policy in Volume7. |
| Container consumes memory despite a supposed limit | Inspect configured limit and cgroup delegation/version | Fix enforcement capability before trusting an autoscaling calculation. |
| Host disk fills again after container replacement | Mounts, logs, image cache and host filesystem evidence | Attribute growth to an owner and retention policy; replacement alone does not remove all storage. |

`podman unshare` executes within Podman's user namespace. For example, `podman unshare cat /proc/self/uid_map` helps explain how IDs are mapped; it is not a universal repair command. A subsequent recursive ownership change inside that namespace still changes real files. The [unshare reference](https://docs.podman.io/en/latest/markdown/podman-unshare.1.html) explains the scope. SELinux relabeling and user mapping are separate controls: fixing one does not prove the other permits access.

Reserve cleanup for objects whose ownership and retention requirements you have established. `rm` of a named stopped lab object is narrower than `system prune`; deleting a volume is a separate data operation. If a service is managed by Compose, Quadlet or another controller, recover through that definition so the next reconciliation does not undo a manual adjustment.

## Diagnostic drills

1. **The image was pulled, but restarting the container still reports the old release.** Inspect its image identity. Starting or restarting the existing object retains its configuration; replace it through the deployment definition using the intended artifact and verify readiness. Preserve the failed instance's logs and state first.
2. **Podman logs show a healthy API, but Harbor cannot reach it remotely.** Check publication and the listener before opening a firewall. A deliberate loopback publication requires a local reverse proxy or tunnel for external access. Then check the provider and host path with the actual client address.
3. **A mounted directory becomes writable with a privileged container.** That experiment changes several security boundaries at once. It does not identify the failing control. Inspect the user mapping, DAC and SELinux evidence separately, and implement the least change that matches the cause.
4. **Replacing an API fixes latency for two minutes.** Correlate cache warmup, pool growth, memory and request distribution. A recurring resource or dependency limit needs a durable correction; repeated replacement merely establishes a temporary effect.

The reference commands were checked against the primary documentation on2026-10-01. Local Podman6.1.2 version and read-only inventory were inspected on the writing host. The Docker commands, builds, container lifecycle and rootless repair examples here were not executed against a reader environment. Engine version, remote platform, cgroups and distribution packaging remain part of the interpretation.
