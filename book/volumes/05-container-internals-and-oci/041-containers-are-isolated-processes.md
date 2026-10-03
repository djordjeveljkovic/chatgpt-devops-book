---
book: The Complete DevOps Engineering Book
volume: 5
volume_title: "Container Internals and OCI"
chapter: 41
title: "Containers Are Isolated Processes"
slug: containers-are-isolated-processes
status: draft
summary: ../../_ai/chapter-summaries/041-containers-are-isolated-processes.md
---

# Chapter 41 — Containers Are Isolated Processes

## A container is an operating-system process environment

DispatchDesk currently runs as a Linux process supervised by systemd. Packaging it into a container changes how the process receives its filesystem, network view, identity and resource controls. It does not turn the process into a separate kernel or a miniature virtual machine. Linux containers use ordinary host-kernel processes with selected isolation and accounting mechanisms configured by a runtime.

That distinction affects security, debugging and capacity. A container process ultimately consumes host CPU, memory, file descriptors and storage. A host kernel panic can stop every container. A process that escapes its intended boundary can affect the host, depending on the runtime, privileges and kernel. Container isolation is useful but layered; it does not replace patching the kernel, controlling host access, limiting capabilities, separating secrets and monitoring the host.

The Open Container Initiative (OCI) specifies image formats and runtime behavior so compatible tools can exchange artifacts and process configurations. It does not prescribe one complete container platform. A low-level runtime such as `runc` or `crun` creates and manages a process from a runtime bundle. A higher-level engine adds image transfer, storage, networking, logging and lifecycle commands. An orchestrator may then schedule those workloads across machines. These layers interact, but they solve different problems.

## What the runtime assembles

A container launch combines an executable, arguments, environment, root filesystem, mounts, namespaces, credentials and controls. The root filesystem often comes from an image assembled from read-only layers plus a writable container-specific layer. The runtime prepares required kernel interfaces such as `/proc`, constructs the selected namespace and cgroup membership, configures capabilities and security policy, then starts the process. Exact behavior depends on the OCI runtime configuration and engine defaults.

The process is expected to stay in the foreground. If it daemonizes and its parent exits, the runtime may consider the container stopped even if a detached child remains in a confusing state. A container's lifecycle should follow the application process: start, report readiness using an agreed mechanism, handle termination, flush or preserve durable work, and exit. A supervisor inside the container can be appropriate for a deliberate multi-process design, but adding one merely to mimic a full virtual machine can obscure failure signals and shutdown behavior.

An image is not a running container. An image identifies filesystem content and metadata that can be used to create a container. A running container adds a process and mutable runtime state. Removing a container may discard its writable layer; persistent data belongs in an explicitly managed volume or external service. Rebuilding an image should reproduce the program and its runtime dependencies rather than capture a pet server's incidental state.

The container's PID 1 has special responsibilities within its process namespace. It should handle termination signals and reap orphaned child processes as required by the application. An application that launches subprocesses must verify that they exit during shutdown. Some engines can insert a small init process to forward signals and reap children; whether that is enabled is a runtime decision, not a property guaranteed by the image format. Test the actual signal path from the engine to the application.

## Isolation does not imply every boundary

A container may have its own process IDs and network interfaces while sharing the host's kernel and some other namespaces. A mounted host directory can expose sensitive files. A privileged container or broad host-device access can undermine isolation. A root user inside a container is not automatically equivalent to a host root user when user namespaces map identities, but a default rootful runtime and dangerous capabilities can create substantial host risk. The relevant boundary is the effective runtime configuration, including mounts, namespaces, capabilities, seccomp and Linux security modules.

Network isolation also does not mean no network access. A container may receive a virtual interface connected to a bridge, reach other containers or make outbound connections. A published port can map host traffic into the container. The process's listening address inside its network namespace is interpreted in that namespace; host firewall and engine rules determine how traffic crosses between host and container. [Chapter 55](../06-docker-in-practice/055-docker-networking.md) examines Docker networking in detail.

Filesystem isolation does not make writes durable. The writable layer usually belongs to the container instance and may disappear when it is removed. Bind mounts and volumes create data paths outside that layer, with their own ownership and backup obligations. Secrets mounted into a container remain accessible to its process and may appear in diagnostics if the application logs them. Use minimal mounts and give each workload only the files it needs.

## A process-oriented inspection

The following host commands observe the current shell's context. They do not create a container or change namespace membership:

```bash
printf 'PID=%s\n' "$$"
readlink "/proc/$$/ns/pid"
readlink "/proc/$$/ns/mnt"
readlink "/proc/$$/ns/net"
cat "/proc/$$/cgroup"
```

Namespace links contain identifiers that can be compared with another process's links when permissions allow. Matching identifiers mean those processes refer to the same namespace object; different identifiers indicate different namespace instances. The cgroup path shows the process's current resource-control grouping when the hierarchy is visible. These observations are not a complete inventory of isolation: a process can share some namespaces and differ in others, while mount, capability and security policy add further boundaries.

After a container engine is introduced in later chapters, repeat the inspection for a known test container and compare its process context with the host. Record the process ID as seen by the host and inside the container; PID namespaces can assign different numbers to the same task. Do not inspect or alter a production process without authorization. Host paths, cgroup mount layout and access permissions differ across distributions and runtime modes.

## Operational consequences for DispatchDesk

Containerizing DispatchDesk can make its runtime dependencies and launch command more reproducible. It does not automatically solve the order database, secret delivery, TLS, backups, capacity limits, deployment rollout or host recovery. PostgreSQL state should remain on a supported persistent service or managed database rather than disappearing with the container. The same accepted-order and durable-intent invariant still applies. A container restart cannot restore a missing database or determine whether an external notification was sent.

A container image should declare its listening port and expected entry point as useful metadata, but metadata alone neither publishes a host port nor makes the application ready. A health probe needs a real application endpoint and an orchestrator or engine configured to use it. The distinction between process health and readiness from Chapter 10 remains important. A container can be running yet unable to accept an order safely.

The image also carries software supply-chain risk. A base image can be outdated, a build can include unintended files or secrets, and a mutable tag can refer to different content over time. Later chapters address minimal builds, digest identity, registries, signing and promotion. A container is a packaging and process-isolation tool, not evidence that the artifact is trustworthy.

## Exercises and review questions

1. Explain why a container restart does not reboot the Linux kernel. Which failures still affect every container on one host?
2. A container is removed and its database file disappears. Which runtime storage assumption caused the loss, and where should authoritative data live?
3. List the effective isolation boundaries you would inspect before running untrusted code: identity mapping, namespaces, mounts, capabilities, seccomp, LSM policy and network exposure.
4. Design a termination test for DispatchDesk that verifies an accepted order and notification intent survive process shutdown.

A container is a process launched with a specific environment and a collection of kernel controls. Inspect those controls rather than treating the word “container” as a security or durability guarantee. The next chapter studies Linux namespaces, the kernel mechanism behind several of these isolated views.

## Sources and verification

The Open Container Initiative's [Runtime Specification](https://specs.opencontainers.org/runtime-spec/) and [Linux configuration](https://specs.opencontainers.org/runtime-spec/config-linux/) were inspected on 2026-10-02. The Linux namespace and cgroup interfaces are developed in Chapters 42 and 43. The process-inspection commands passed shell syntax checks; they were not used to inspect a running container. Independent review is pending.
