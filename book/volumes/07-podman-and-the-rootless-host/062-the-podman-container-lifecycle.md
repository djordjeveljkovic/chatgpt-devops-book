---
book: The Complete DevOps Engineering Book
volume: 7
volume_title: "Podman and the Rootless Host"
chapter: 62
title: "The Podman Container Lifecycle"
slug: the-podman-container-lifecycle
status: complete
summary: ../../_ai/chapter-summaries/062-the-podman-container-lifecycle.md
---

# Chapter 62 — The Podman Container Lifecycle

## Run, inspect, exec, logs and cleanup

A container is a process with a lifecycle and durable metadata, not a synonym for its image. A useful operator can answer what was requested, whether it started, why it exited, and what remains after deletion. This chapter builds that evidence chain with a disposable HTTP server. It represents DispatchDesk's transport boundary; it does not pretend that Nginx implements the project's business workflow.

Complete [installation acceptance](061-installing-and-understanding-podman.md) first. Run commands on a disposable Linux container host as the same ordinary account, with local engine operation confirmed. Install `curl` through the distribution package manager if absent. The image requires registry access and a compatible architecture. Port 8088 must be free. No persistent application volume is used, so deleting this fixture cannot remove DispatchDesk records.

```bash
podman --remote=false pull docker.io/library/nginx:alpine
podman --remote=false run --detach --name dd-http-62 \
  --publish 127.0.0.1:8088:80 \
  --label org.dispatchdesk.lab=chapter62 \
  docker.io/library/nginx:alpine
podman --remote=false ps --all
podman --remote=false inspect dd-http-62
podman --remote=false port dd-http-62
curl --fail --show-error --max-time 5 http://127.0.0.1:8088/
```

`pull` downloads image content into this account's store. `run` creates and starts a container; `--detach` returns control to the terminal. The name provides an operator handle, while the label identifies the lab's provenance. `--publish` maps host IPv4 loopback port 8088 to container TCP port 80. It deliberately avoids a public listener. `ps --all` includes stopped objects. `inspect` records the configuration and state, while `port` reports the publication. The HTTP probe fails on HTTP error status and stops after five seconds instead of hanging indefinitely.

The expected evidence is a running named object, the requested publication, and an HTTP response containing the image's welcome page. This is expected evidence, not measured output. A process listed as running does not establish that it can accept requests, and one successful HTTP response does not establish DispatchDesk readiness. A production probe should exercise its documented readiness endpoint and dependencies.

The lab uses a mutable tag for accessibility. Resolve a real digest and confirm platform compatibility before a production release. Retain the digest beside the container's inspected image identity; do not infer it from the tag text after the registry has moved that tag.

Inspection output may contain environment variables, mounts and internal paths. Save it in an access-controlled incident directory rather than a public ticket. To focus investigation, use the documented state and image fields or parse JSON with a tool that checks absent fields. The [inspect reference](https://docs.podman.io/en/stable/markdown/podman-inspect.1.html) is the schema starting point; inspect your installed release before making automation depend on a field.

```bash
podman --remote=false logs --timestamps --tail 50 dd-http-62
podman --remote=false exec dd-http-62 nginx -t
podman --remote=false inspect --format '{{.State.Status}} {{.State.ExitCode}}' dd-http-62
```

`logs` reads the logging backend's retained application output, not an arbitrary file inside the container. `--tail 50` bounds the volume and `--timestamps` helps correlate an HTTP probe. `exec` launches an additional process inside a running container; `nginx -t` checks this fixture's configuration. A successful diagnostic process does not restart PID 1 or fix it. An image without a shell or debugging utility may reject a familiar `exec sh`; that absence is not proof of corruption. Keep debugging tools out of the application's contract unless the deployment design deliberately supplies them.

## Rootless versus rootful state

All objects above belong to the invoking rootless account. `sudo podman inspect dd-http-62` generally addresses another store. Another ordinary user also has independent state. This separation applies to images, volumes and networks, not only to running processes. Do not mix `sudo` into a lab because one command returned a permission error: first determine which filesystem, helper or security policy denied access.

The engine account and container process UID are separate concepts. The default Nginx image may launch its main process as container root and switch workers to another identity. In rootless execution, container root does not become initial-namespace host root. Nevertheless, the workload can access paths deliberately mounted from the owning account. Chapter 63 shows why numeric mapping matters for writes.

When troubleshooting an apparently missing container, compare the local/remote mode and account before concluding that it was deleted. A script with `CONTAINER_HOST` set can inspect a server while an interactive shell inspects local storage. Use explicit selection for the investigation, then inspect the intended service unit to find its configured execution identity. Preserve object IDs as well as names: a name can be reused after replacement, while an incident report needs to identify the actual failed instance.

## Operating an HTTP service

Stopping is a controlled state change. Run this sequence after the first successful probe:

```bash
podman --remote=false stop --time 10 dd-http-62
podman --remote=false ps --all
podman --remote=false inspect --format '{{.State.Status}} {{.State.ExitCode}}' dd-http-62
podman --remote=false logs --timestamps --tail 50 dd-http-62
podman --remote=false start dd-http-62
curl --fail --show-error --max-time 5 http://127.0.0.1:8088/
```

`stop --time 10` allows a bounded graceful termination interval before forced termination. The image's configured stop signal can affect shutdown, so do not assume every workload receives an identical signal. The [stop manual](https://docs.podman.io/en/stable/markdown/podman-stop.1.html) defines the installed CLI's behavior. Application drain and data consistency remain the application contract from [Chapter 50](../05-container-internals-and-oci/050-the-container-contract.md).

Stopped metadata remains available. `start` reuses this object's configuration and writable layer; it does not rerun `run` with new flags. Changing a publication, environment value or mount usually requires creating a replacement with the intended configuration. Treat the image and runtime configuration together as a release. A changed file inside the old writable layer is not a reproducible deployment artifact.

There can be a short interval between process start and successful HTTP acceptance. If the immediate probe fails, inspect state and logs, then retry under a bounded deadline appropriate to the application. Do not add an unlimited sleep loop. A ten-second startup objective needs ten-second acceptance evidence, and a service with migrations may need a different readiness contract.

For teardown, stop and remove only the fixture:

```bash
podman --remote=false stop --time 10 dd-http-62
podman --remote=false rm dd-http-62
podman --remote=false ps --all
```

Removing the container deletes its writable layer and metadata. It does not mean a separately managed named volume or bind-mounted directory is deleted. Avoid global prune commands to tidy one exercise. The pulled image can remain cached; remove it separately only if you have confirmed no other exercise needs it. Deleting logs together with a failing object can destroy the best available incident evidence.

## Diagnose a failed assumption

Suppose `run` reports that the name already exists. The original container may have exited while still holding that name. Inspect `ps --all`, its state and logs; do not immediately add `--replace` to hide the history. If it is this disposable fixture, preserve relevant output, remove it and repeat the create step. If it belongs to an existing service, stop and investigate ownership instead.

If startup reports address already in use, inspect the host's listeners:

```bash
ss -ltn
podman --remote=false ps --all
podman --remote=false port dd-http-62
```

The unavailable port may belong to a host service, another account's container, or an earlier lab. Your own container inventory cannot enumerate every listener on a shared host. An administrator can identify owners through appropriately privileged host diagnostics. Choose another documented lab port or release the known fixture; do not kill an unknown process to satisfy the example.

If the object runs but `curl` fails, distinguish publication from application binding. An application bound to `127.0.0.1` inside its isolated namespace may not accept forwarded traffic addressed to its container interface. Inspect actual command/configuration, logs and publication. In this Nginx fixture, the standard image listens on container port 80; a custom application must establish its own listening contract.

If `exec` succeeds but the HTTP probe times out, the diagnostic confirmed only that another process could start. The application may be deadlocked, listening on another port, or serving errors. If logs are empty, inspect the selected driver and whether the application writes to stdout/stderr. The [logs manual](https://docs.podman.io/en/stable/markdown/podman-logs.1.html) describes log retrieval; it cannot recover output the application never emitted.

A clean recovery preserves evidence, repairs the specific cause, recreates the object when configuration must change, and probes the same client path that failed. In production, restore the last approved image and configuration together. A downgrade that reconnects incompatible persistent data is not a safe rollback merely because the process launches.

## Exercises and review questions

1. Run the fixture, stop it, and explain the difference between `ps` and `ps --all`. **Guidance:** default listing emphasizes running objects; stopped metadata can retain logs and exit evidence.
2. Try a second `run` with the same name on the disposable host. **Guidance:** diagnose existing object ownership; cleanup is scoped to your lab object, not all stopped containers.
3. Describe evidence needed before deleting an exited DispatchDesk instance. **Guidance:** object ID, image identity, runtime configuration, timestamps, exit state, logs and persistent mounts.
4. Why does `start` not apply a newly edited shell command's flags? **Guidance:** it starts an existing object; requested replacement configuration must be represented in a new object or declarative service.

## Takeaways and further reading

Follow create, observe, stop, inspect and cleanup as distinct operations. Process state, configuration and an HTTP probe answer different questions. Continue with [volume ownership](063-rootless-identity-and-volume-ownership.md).

The Podman inspect, stop and logs manuals linked above were inspected 2026-10-03. No image pull, HTTP request or lifecycle operation was run by the author; these are reader procedures whose outcomes require runtime verification.
