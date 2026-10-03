---
book: The Complete DevOps Engineering Book
volume: 6
volume_title: "Docker in Practice"
chapter: 52
title: "Running and Managing Containers"
slug: running-and-managing-containers
status: complete
summary: ../../_ai/chapter-summaries/052-running-and-managing-containers.md
---

# Chapter 52 — Running and Managing Containers

The `docker run` command combines creation and startup. It creates a container configuration from an image, asks the daemon to prepare networking and storage, and starts the image's configured process. Learning the lifecycle means learning what each part changes and how to inspect it afterward. The example here runs a disposable Nginx web server on a test host's loopback interface. It downloads an image, consumes local storage and occupies a port until removed. Do not run it on a production host without checking the selected engine, port and change window.

## `run`, `create`, `start`, `stop` and `remove`

Run this lab from a shell on the disposable Linux test host, against that host's local Docker Engine. The CLI user must already have authorized access to its daemon; these commands do not change user or socket permissions. Chapter [51](051-installing-and-inspecting-docker.md) explains Docker installation and context checks. Before continuing, confirm the selected context is the local `default` context and its endpoint is the host's local Engine. If `DOCKER_HOST` or `DOCKER_CONTEXT` selects a remote daemon, clear that override and select the local context deliberately; do not use `sudo` as a substitute for verifying the target. The socket checks and `curl` below also run on this same test host. The examples use the default bridge networking behavior and assume Docker Engine 28.0.0 or newer. First choose a port that is not already in use. The example uses host port 18080 mapped to container port 80:

```bash
docker run --detach \
  --name dispatchdesk-web-lab \
  --publish 127.0.0.1:18080:80 \
  nginx:alpine
```

`--detach` returns control to the shell while the service remains running. `--name` assigns a stable local identifier for later inspection and cleanup. `--publish` maps the host loopback address and port to the container's port 80; the process inside the container must listen on that port. With Engine 28.0.0 or newer and the default bridge network, binding to `127.0.0.1` limits the published port to local clients. Docker documents that on Engine releases before 28.0.0, peers on the same layer-2 segment could reach ports published to localhost, so do not rely on this isolation on older engines. Host firewall and engine-specific networking behavior still need verification, especially on systems where Docker publication interacts with firewall rules. `nginx:alpine` is a convenient learning tag, not a stable release identity; production deployments should promote and pin an approved image digest as discussed in [Chapter 49](../05-container-internals-and-oci/049-registries-and-image-distribution.md).

The command may fail because the image cannot be pulled, the daemon is unreachable, the requested name already exists or the host port is occupied. A name conflict can be diagnosed with `docker ps -a --filter name=dispatchdesk-web-lab`. Do not blindly remove a container whose ownership is unclear. A port conflict can be inspected with the test host's socket tools and by listing existing mappings. Choose another unused high port if needed, and update the later `curl` URL accordingly.

Inspect the result rather than assuming the process started correctly:

```bash
docker ps --filter name=dispatchdesk-web-lab
docker inspect dispatchdesk-web-lab --format '{{.State.Status}} {{.State.ExitCode}}'
docker port dispatchdesk-web-lab
docker logs --tail 50 dispatchdesk-web-lab
curl --fail --show-error http://127.0.0.1:18080/
```

The expected evidence is a running state, a mapping from host port 18080 to container port 80, startup logs and an HTTP response from the local web server. Output is environment-dependent; no measured output is reproduced here. If `curl` gets connection refused, check the container state, logs, port binding and active context. A successful HTTP response shows that this test host can reach the service; it does not prove external firewall behavior or production readiness.

`docker create` prepares a stopped container but does not start it. It is useful when an automation tool wants to inspect or adjust a created object before execution. `docker start` starts that existing container again. `docker stop` asks the main process to terminate, waits for its configured grace period, and then forcefully kills it if it has not exited. `docker rm` removes a stopped container's metadata and writable layer. The container's image remains cached. A named volume mounted into the container remains: `docker rm -v` removes associated anonymous volumes, never named volumes. The `--rm` run option also removes associated anonymous volumes when the container exits. Review the mount type before using either option if container data matters.

Compare a stopped container with a container removed after exit. Without `--rm`, a stopped container remains visible in `docker ps -a`, and its logs and exit state can be inspected. With `--rm`, the engine removes the container after its process exits, which is convenient for one-shot jobs but removes that post-exit inspection object. Choose based on the evidence you need during failure analysis.

## Names, ports and restart policy

Container names are unique within one daemon. They make operations readable but do not create service discovery across hosts. A port mapping reserves host networking state; two containers generally cannot bind the same host address and port at the same time. Container port 80 alone is not published to the host. If the host address is omitted, Docker publishes on all host interfaces by default, equivalent to a wildcard IPv4 bind in the common case. A mapping such as `127.0.0.1:18080:80` deliberately limits access to local clients under the version and network assumptions above, while `0.0.0.0:18080:80` listens on all IPv4 interfaces and can expose the service to every reachable network unless host controls restrict it. IPv6 behavior depends on daemon configuration and should be verified separately.

Restart policy describes what the daemon should do after a container exits or the daemon restarts. It is not an application health check and cannot repair bad configuration or corrupt state. For example, `--restart unless-stopped` keeps a long-running service eligible for automatic restart unless an operator explicitly stops it. If the process crashes in a tight loop, the restart policy may repeatedly launch it; inspect logs, exit codes and dependency conditions. Set restart behavior after the service has a meaningful shutdown path and externalized state.

For a learning run, the server can use a restart policy while still remaining easy to clean up:

```bash
docker run --detach \
  --name dispatchdesk-web-lab \
  --restart unless-stopped \
  --publish 127.0.0.1:18080:80 \
  nginx:alpine
```

Do not start a second container with the same name after running the first example. If the original is still running, inspect it and either keep it or stop and remove it deliberately before recreating it. A service supervisor can restart Docker itself; the container restart policy then governs container recovery under the daemon. That is different from Kubernetes or another orchestrator, which has its own desired-state and health mechanisms.

## Operating a small HTTP container

Follow the request path from the client to the process: `curl` connects to the host's loopback port 18080; Docker's published-port rules direct the connection to container port 80; Nginx serves its default page. To inspect the mapping and process metadata in one place, use:

```bash
docker inspect dispatchdesk-web-lab \
  --format 'image={{.Config.Image}} state={{.State.Status}} ports={{json .NetworkSettings.Ports}}'
```

If the mapping is absent, the container was created without the intended publish flag; changing an existing container's port mapping usually means recreating it. If the image process exits, inspect the exit code and logs before changing the image or restarting repeatedly. If the local request works but an external request fails, examine routing, cloud security groups, host firewalls and whether the published address is loopback-only. Do not widen the bind address until the exposure is intentional and the application has authentication and TLS appropriate to its role.

When you finish, stop and remove only the lab container you created:

```bash
docker stop dispatchdesk-web-lab
docker rm dispatchdesk-web-lab
```

The commands are scoped by the unique lab name. They leave the downloaded image in the daemon's cache for reuse. If this was a dedicated test daemon and you also want to remove that image, inspect its image identity and use an explicit image removal command; image cleanup affects every container on that daemon that depends on the image and may require reclaiming cache space. Do not prune all containers, volumes or images merely to clean up this exercise.

This lab illustrates process lifecycle and local networking. A production web service also needs immutable artifact selection, resource bounds, secret delivery, structured logs, health semantics, durable data handling, patching and monitored external reachability. Later chapters build those controls one at a time; the container contract from [Chapter 50](../05-container-internals-and-oci/050-the-container-contract.md) keeps application behavior portable across them.

## Exercises and review questions

1. Explain each part of `127.0.0.1:18080:80`. What changes if the host address is omitted?
2. Why might `docker run --rm` be a poor choice for a failing long-running service during diagnosis?
3. A container exits and Docker restarts it repeatedly. Which state, logs and exit details should you inspect before changing restart policy?
4. The local `curl` succeeds but a request from another machine fails. List the network boundaries that still need checking.
5. Remove the lab container while preserving the cached image. Which exact commands are appropriately scoped, and which broad prune commands should be avoided?

### Answer guidance

1. The fields are host address, host port and container port. Omitting the address publishes on all host interfaces by default, so check reachability and firewall controls rather than assuming loopback-only access.
2. `--rm` removes the container after exit, including the inspectable state and logs associated with that container object; run without it when exit code, configuration and logs must be examined after failure.
3. Check `docker inspect` for state, exit code, restart count and configured policy, then review `docker logs`. Also inspect dependencies and recent events before changing policy or restarting repeatedly.
4. Verify the test host and active daemon/context first, then the published address and port, host routing, cloud security groups, host firewall and any upstream network policy. A loopback-only mapping is intentionally unreachable from other machines.
5. Use `docker stop dispatchdesk-web-lab` followed by `docker rm dispatchdesk-web-lab`; this leaves the image cached. Avoid broad container, volume or image prune commands. `docker rm -v` and `--rm` remove associated anonymous volumes, while named volumes are retained.

## Takeaways

- `docker run` creates and starts a container; `create`, `start`, `stop` and `rm` expose those lifecycle changes separately.
- Inspect the selected daemon, container state, logs and published mapping before diagnosing a failed request. Run host socket checks and client requests on the host that owns the local Engine.
- An omitted host address publishes on all interfaces by default. Treat loopback publication as local-only only with Engine 28.0.0 or newer under the documented default bridge behavior.
- Remove the specifically named lab container when finished. Container removal leaves the image cache and named volumes; anonymous-volume options have separate cleanup behavior.

## Sources and verification

Docker's official [`run`](https://docs.docker.com/engine/containers/run/), [restart policy](https://docs.docker.com/engine/containers/start-containers-automatically/), [`inspect`](https://docs.docker.com/reference/cli/docker/inspect/), [`logs`](https://docs.docker.com/reference/cli/docker/container/logs/), [port publishing](https://docs.docker.com/engine/network/port-publishing/) and [firewall](https://docs.docker.com/engine/network/packet-filtering-firewalls/) documentation were inspected on 2026-10-02. The commands were checked for syntax and reviewed against the documentation but were not run because this workspace has no Docker daemon. Published-port behavior can vary with engine mode, host firewall and IPv6 settings; verify it on the actual test host.
