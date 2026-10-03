---
book: The Complete DevOps Engineering Book
volume: 5
volume_title: "Container Internals and OCI"
chapter: 42
title: "Linux Namespaces"
slug: linux-namespaces
status: draft
summary: ../../_ai/chapter-summaries/042-linux-namespaces.md
---

# Chapter 42 — Linux Namespaces

## Give processes different views

A Linux namespace wraps a selected global resource so processes inside it see a scoped view. It is one reason a container can have its own process IDs, network interfaces and mount table while running on the host kernel. A process may join some namespaces and not others; “inside a container” is not one indivisible kernel mode.

Namespace isolation answers which objects a process can see or name. It does not, by itself, cap CPU or memory, make a filesystem immutable, validate network traffic or remove a process's authority over accessible host resources. Cgroups account for and control resource use. Mount options, credentials, Linux capabilities, seccomp, SELinux/AppArmor and network policy contribute separate controls. Evaluate the combined configuration.

## The namespace types

Linux provides several namespace types. Their availability, configuration and exact behavior depend on the kernel and runtime. OCI describes these types in the container configuration; the kernel and system interfaces define their behavior.

| Namespace | View it scopes | Operational question |
|---|---|---|
| PID | Process identifiers and process visibility | Which PIDs can this process see, and which process is namespace PID 1? |
| Mount | Mount points and filesystem view | Which paths and mounts are visible, writable or propagated? |
| Network | Network devices, routes, sockets and related network state | Which interfaces, addresses, routes and firewall rules apply here? |
| IPC | System V IPC and POSIX message queue identifiers | Which shared-memory and message objects can processes discover? |
| UTS | Hostname and NIS domain name | Which hostname does the workload report? |
| User | User and group ID mappings and capabilities | Which host identity backs a container-visible UID? |
| Cgroup | View of the cgroup hierarchy | What hierarchy can the process see? Resource limits themselves are managed by cgroup controls. |
| Time | Selected monotonic and boot-time clock offsets | Does the process see adjusted clocks, and can that affect timeout assumptions? |

A new PID namespace gives its first process PID 1 inside that namespace while the host identifies the same task with a host PID. Parent namespaces can still observe processes in child PID namespaces, subject to permissions. If namespace PID 1 exits, the kernel terminates the remaining processes in that PID namespace. This makes signal handling and process supervision important for container shutdown.

A user namespace maps IDs between namespaces. A process can have UID 0 in its own user namespace while mapping to an unprivileged host UID. Capabilities are scoped relative to user namespaces, and operations still depend on the relevant namespace and kernel checks. This mapping is a useful isolation layer but does not make unsafe host mounts or exposed privileged interfaces safe. Rootless runtime behavior is covered in [Chapter 47](047-rootless-containers-and-user-mapping.md).

A mount namespace begins with a copy or propagated view of mount points, depending on how it is created and configured. Shared mount propagation can carry mount events across namespaces; private or slave propagation changes that relationship. A container runtime needs deliberate propagation behavior when a workload must see dynamically mounted storage. An unexpected propagation mode can expose host mount changes or hide a volume from the process.

A network namespace has its own network devices, addresses, routes, firewall state and port space. A newly created namespace commonly begins with only a loopback device, which may be down until configured. A runtime can connect it to other network namespaces using virtual devices and host routing. Publishing a port is an additional path from host or external traffic; merely creating a network namespace does not publish anything.

## Inspect namespace membership safely

Linux exposes namespace handles under `/proc/<pid>/ns/`. The link target includes a namespace type and inode-like identifier. Compare two process paths of the same type to see whether they refer to the same namespace object. Access can be restricted, and PIDs can be reused, so capture process identity and start time if correlating evidence over time.

For a process you own or are authorized to inspect, a compact read-only command is:

```bash
inspect_pid=1
ps -p "$inspect_pid" -o pid=,ppid=,comm=,lstart=
for namespace_path in /proc/"$inspect_pid"/ns/*; do
    printf '%s ' "${namespace_path##*/}"
    readlink "$namespace_path"
done
```

PID 1 in this example refers to the host's initial process as seen by the current shell, not a container init process. Replace it with a known host PID after checking that it still identifies the intended workload. Namespace link comparison is evidence about membership, not a complete security audit. Also inspect the process's cgroup, capabilities, mounts, credentials, open file descriptors and security policy as appropriate.

To inspect a process's mount view, `/proc/<pid>/mountinfo` records mounts visible through that process's mount namespace. To inspect network interfaces and routes, use tools inside the relevant network namespace or an authorized `nsenter` operation. Entering a namespace changes the operator's context and may grant access to sensitive resources; start with read-only inspection and confirm the PID and namespace type. Do not run a broad host command from a container namespace and assume its output describes the host.

## Common reasoning mistakes

Different PID namespace does not mean a process is invisible to the host. A separate network namespace does not mean egress is blocked. A separate mount namespace does not protect files bind-mounted into it. A cgroup namespace only changes the hierarchy view; cgroup controllers impose resource controls. A user namespace changes identity mapping but does not guarantee every filesystem or kernel interface is safe to delegate. Each statement names one boundary and leaves others to be configured.

Namespace APIs are also not a complete container runtime. Correctly preparing a workload involves filesystem construction, namespace creation, ID maps, cgroup placement, capabilities, device policy, network wiring, signal forwarding and cleanup. A sequence of shell commands that calls `unshare` and `mount` can fail halfway and leave confusing state. Prefer a maintained runtime for managed workloads, then inspect the generated configuration when learning or troubleshooting.

## Exercises and review questions

1. One host process appears as PID 1 inside a container and PID 28417 on the host. Which namespace boundary explains this, and which PID is useful to `kill` from the host?
2. A process sees `eth0` and can resolve DNS but cannot receive public traffic. Which network and host boundaries would you inspect?
3. A container sees `/data` because the host mounted it into the container. Which security and durability properties still depend on the host mount and filesystem?
4. Why does a cgroup namespace not by itself restrict memory consumption?

Namespaces provide process-scoped views of kernel resources. Diagnose the specific view involved and then check the independent authority, resource and network controls around it. [Chapter 43](043-cgroups-and-resource-accounting.md) turns to CPU, memory, I/O and process-count control.

## Sources and verification

The Linux `namespaces(7)`, `mount_namespaces(7)`, `pid_namespaces(7)`, `user_namespaces(7)` and `network_namespaces(7)` manuals and OCI [Linux runtime configuration](https://specs.opencontainers.org/runtime-spec/config-linux/) were inspected on 2026-10-02. The host inspection snippet passed shell syntax checks but was not used to enter or inspect another process namespace. Independent review is pending.
