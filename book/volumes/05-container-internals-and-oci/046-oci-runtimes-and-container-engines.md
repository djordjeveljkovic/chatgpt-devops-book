---
book: The Complete DevOps Engineering Book
volume: 5
volume_title: "Container Internals and OCI"
chapter: 46
title: "OCI Runtimes and Container Engines"
slug: oci-runtimes-and-container-engines
status: complete
summary: ../../_ai/chapter-summaries/046-oci-runtimes-and-container-engines.md
---

# Chapter 46 — OCI Runtimes and Container Engines

## Trace a command through its layers

When an operator types `docker run`, several components coordinate. The CLI parses options and sends a request to the Docker Engine API. The Docker daemon manages image, network, volume and container objects. The engine uses container lifecycle and runtime components to prepare the filesystem and kernel configuration, then launches the workload process. The OCI Runtime Specification defines a standard configuration and lifecycle interface used by low-level runtimes; it does not define every higher-level engine feature.

The exact implementation changes over time. Current Docker Engine documentation describes containerd managing container lifecycle and `runc` as the default runtime, with other runtimes available through supported integration. Docker Engine 29 also changed the default image store for fresh installations to containerd's image store. Existing hosts may use a different storage backend. Check installed versions, selected context, daemon configuration and storage state rather than assuming every Docker host has the same architecture.

An engine coordinates useful concerns beyond the low-level process launch: pulling and storing image content, naming objects, configuring networks and mounts, collecting logs, exposing events and cleaning up resources. A container can continue running after the client command exits because the daemon or runtime lifecycle components own the long-lived operation. Conversely, if the API request reaches the wrong engine context, a command may inspect or mutate a different host than the operator intended.

## Docker client and daemon boundary

Docker uses a client-server architecture. The CLI commonly talks to a local Unix socket, but it can target a remote engine through a configured context or API endpoint. A Unix socket limits access by file permissions, but any user who can control a rootful Docker daemon can often mount host paths or start highly privileged containers. Treat membership in the Docker control group or possession of an authorized remote-engine credential as root-equivalent access to that host.

Do not expose an unauthenticated Docker API on a public or untrusted network. If remote management is needed, use the supported protected transport such as SSH or mutually authenticated TLS, restrict source access and account for the full authority those credentials grant. A network firewall alone does not authenticate an operator. Audit who can reach the socket and rotate access when duties change.

The commands below inspect the current CLI and engine context without starting a workload:

```bash
docker context show
docker context inspect
docker version
docker info
```

Check the context before running a future create, delete or build command. `docker version` separates client and server information; a missing server section can indicate the engine is unavailable or that the selected endpoint cannot be reached. `docker info` reports host-wide engine settings, which may include internal addresses, storage paths and environment details; share output only after reviewing it for sensitive information.

## Podman and daemonless operation

Podman provides a Docker-compatible command-line style and can manage OCI-compatible images and containers without a continuously running central daemon on Linux. A local Podman command typically invokes the engine behavior for the current user and stores rootless objects in that user's storage area. Rootful and rootless Podman have distinct object stores and authority. Running `sudo podman ps` will generally inspect a different container collection from ordinary `podman ps`.

Podman can also expose an API service for remote clients or compatibility workflows. “Daemonless” does not mean no privileged component or network API can exist; inspect how the command is operating, whether `CONTAINER_HOST` or a remote connection is configured, and which identity owns the target service. A Podman API socket, when enabled, carries authority over the associated rootless or rootful engine. Protect it according to the identity and resources it controls.

Docker and Podman often consume OCI image artifacts, but their flags, defaults, networking, storage, logging, rootless support and systemd integration are not identical. Portability should be verified for the concrete application and runtime configuration. A common image format does not imply identical operational behavior.

## Runtime selection and debugging

An OCI runtime receives a bundle describing the process and Linux-specific configuration, including root filesystem and namespace, cgroup, capability and security settings. It creates and starts the process according to the runtime's contract. Runtimes such as `runc` and `crun` implement OCI runtime behavior. Alternative sandboxes such as gVisor or Kata Containers change the isolation architecture and may use a compatible integration layer; they bring different compatibility, performance and operational tradeoffs.

For Kubernetes, distinguish the kubelet-facing Container Runtime Interface (CRI) from the OCI Runtime Specification. `containerd` can provide a CRI implementation and delegate workload creation to an OCI runtime such as `runc` or `crun`. `CRI-O` is another Kubernetes-focused CRI implementation; it also uses OCI runtime components to create containers. CRI-O and containerd therefore sit at the container-runtime integration layer, while `runc` and `crun` implement the lower-level OCI lifecycle. These components are related parts of a stack, not interchangeable names for the same layer. A single-host Docker or Podman lesson does not require installing Kubernetes to understand the distinction.

When startup fails, trace the owning component rather than repeating `run` blindly. Check whether the client reaches the intended daemon, whether the image manifest supports the host platform, whether storage has space and compatible backing filesystems, whether the runtime can create required namespaces and cgroups, and whether the application process exits with a useful log. Engine events and daemon logs can expose the stage where creation stopped. Preserve the container ID and error text so a cleanup operation does not remove useful evidence.

If a container starts but networking fails, distinguish runtime network setup from application binding and host firewall policy. If a volume is missing, inspect engine mount configuration and host path ownership. If a cgroup limit appears ineffective, identify the cgroup version, controller availability and parent limits. If a rootless workload fails on a mount or port, check user namespace mappings and rootless networking behavior. Chapters 42–45 develop those individual boundaries.

## Keep the API out of the application design

The DispatchDesk application should implement its HTTP and persistence contracts without depending on one particular engine's CLI. A systemd unit, Docker container, Podman container or orchestrator workload can all launch the same program with explicit configuration. Deployment tools own container lifecycle; the application owns request validation, durable order/intent commit, graceful shutdown and meaningful health/readiness behavior.

An engine is an important host control plane. Restrict administrative access, patch it with the host, monitor its storage and lifecycle events, and document how its objects are backed up or recreated. A container engine is not itself a scheduler across a fleet unless paired with an orchestration layer. [Volume 6](../06-docker-in-practice/051-installing-and-inspecting-docker.md) develops Docker operations, and [Volume 7](../07-podman-and-the-rootless-host/061-installing-and-understanding-podman.md) develops Podman and rootless-host operations; compare behavior against the needs of each deployment rather than expecting identical defaults.

## Exercises and review questions

1. Trace `docker run` from CLI to API, daemon, lifecycle manager, runtime and kernel process. Which component would you inspect for an image pull failure versus a namespace creation failure?
2. Why is access to a rootful Docker socket security-sensitive even if the caller cannot run `sudo`?
3. An operator's `docker ps` returns no containers, but a service is still running. Which context or engine differences could explain this?
4. What does OCI compatibility guarantee, and which operational differences between Docker and Podman still need testing?
5. A Podman host uses a remote API. Which authority and network controls should be reviewed before allowing another client?

**Answer guidance:** For exercise 1, the CLI/API and engine resolve the image and manage objects; containerd or another lifecycle manager coordinates creation, an OCI runtime such as `runc`/`crun` creates the process, and the kernel enforces namespaces, cgroups and security policy. Inspect registry/client/engine logs for pull failures and runtime/kernel details for namespace-creation failures. For exercise 2, a rootful socket grants control over container creation, host mounts and privilege, which can yield host-root authority even without `sudo`; protect its file permissions and all remote credentials accordingly. For exercise 3, check Docker context/API endpoint, rootful versus rootless service, user identity, namespace, object store and daemon state before concluding the process is absent. For exercise 4, OCI covers standardized image/runtime interfaces, not matching CLI flags, networking, storage, logging, security defaults or lifecycle; test those on the selected versions. For exercise 5, identify which user's rootless or rootful service is exposed, authenticate the client, restrict the network path, limit credential holders, audit access and confirm the API's authority over host files and workloads.

Container engines turn image and runtime specifications into an operational lifecycle. Verify which engine, identity, endpoint and storage configuration a command targets before drawing conclusions from it. Chapter 47 examines rootless execution and UID/GID mapping more closely.

## Sources and verification

The OCI [Runtime Specification](https://specs.opencontainers.org/runtime-spec/), Kubernetes [Container Runtime Interface](https://kubernetes.io/docs/concepts/containers/cri/), [CRI-O project](https://github.com/cri-o/cri-o), Docker's [architecture overview](https://docs.docker.com/get-started/docker-overview), [alternative runtime documentation](https://docs.docker.com/engine/daemon/alternative-runtimes/) and [engine security guidance](https://docs.docker.com/engine/security/), and Podman's [manual](https://docs.podman.io/en/stable/markdown/podman.1.html) were inspected on 2026-10-04. Engine inspection commands passed shell syntax checks but no Docker or Podman engine was contacted. Version-specific claims should be verified against the installed release.
