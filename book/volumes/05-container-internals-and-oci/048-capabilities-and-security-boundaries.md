---
book: The Complete DevOps Engineering Book
volume: 5
volume_title: "Container Internals and OCI"
chapter: 48
title: "Capabilities and Security Boundaries"
slug: capabilities-and-security-boundaries
status: draft
summary: ../../_ai/chapter-summaries/048-capabilities-and-security-boundaries.md
---

# Chapter 48 — Capabilities and Security Boundaries

## Privilege is a collection of powers

Linux capabilities split many traditional superuser powers into separately controlled permissions. A process that needs to bind a privileged port may need `CAP_NET_BIND_SERVICE`; a process that changes network interfaces may need `CAP_NET_ADMIN`. `CAP_SYS_ADMIN` covers a broad set of operations and is often described as highly powerful. Giving a container all capabilities because one operation failed is a large and poorly understood expansion of authority.

Capabilities are per-thread attributes checked by the kernel. Their effect also depends on the user namespace, credentials, seccomp filters, Linux security module and resources visible to the process. A container's apparent UID 0 does not automatically mean unrestricted host root, but a rootful engine, host mounts, broad capabilities and privileged mode can make the host reachable. Evaluate the combined controls rather than relying on the container's user name.

Docker applies a default capability set and a default seccomp profile, but those defaults and behavior can change by engine version. Podman and other engines have their own default policies. Preserve tested defaults unless an application requirement demonstrates the need for a change. A syscall denied by seccomp or an operation denied by SELinux/AppArmor can look like an ordinary permission error; inspect the actual runtime and audit event before changing policy.

## Drop authority the application does not need

Run DispatchDesk as a non-root user inside the container and keep the application on an unprivileged port such as 8080. The process needs access to its read-only application files, selected configuration and state/database connection. It should not need to configure host networking, load kernel modules, mount filesystems or inspect unrelated host processes. Avoid host PID/network namespaces and host device access unless the workload has a reviewed system-level purpose.

An illustrative Docker command for a tested image could begin with:

```bash
docker run --rm \
  --read-only \
  --user 10001:10001 \
  --cap-drop=ALL \
  --security-opt=no-new-privileges=true \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  IMAGE_WITH_VALID_ENTRYPOINT
```

Replace the image placeholder with an image whose entry point and writable paths you have verified. This template starts a container and is not run as part of this chapter. `--read-only` makes the container root filesystem read-only; it does not make a mounted volume read-only. `--tmpfs` provides one bounded writable scratch path, and the application may need another explicitly mounted state or socket path. `--cap-drop=ALL` can break software that genuinely needs a capability; add only the documented capability after testing. If the runtime's default seccomp or LSM profile denies a required call, identify the smallest policy change and keep it scoped to that workload.

`no-new-privileges` prevents a process and its descendants from gaining new privileges through mechanisms such as setuid executables. It does not remove privileges the process already has, fix unsafe mounts or prevent application-level authorization bugs. `--read-only` similarly reduces write paths but does not make memory exhaustion, CPU denial, network misuse or data disclosure impossible.

## Layer independent controls

Linux seccomp filters restrict which system calls a process may make and can filter selected arguments. Docker's default profile is an allowlist that denies some calls; replacing it with an unconfined profile expands kernel attack surface. Seccomp is one control rather than a complete sandbox. Application authorization, namespaces, credentials, cgroups and Linux Security Modules still matter.

AppArmor and SELinux can restrict a process according to host policy. A denial may occur even when Unix file mode bits allow the operation. Keep the host's distribution policy enabled and use the supported profile tooling to understand denials. Do not disable SELinux or AppArmor to make a container start. Instead, verify the path label/profile, required access and the intended service identity, then make the narrowest policy correction.

A read-only root filesystem can make a compromised process less able to alter its own executable or configuration, but it needs carefully chosen writable locations for temporary files, sockets, caches and database state. Mount each writable path with the minimum scope and ownership required. Secrets mounted read-only remain readable to the process and can leak through logs, crash dumps or command output. Do not pass secrets in image layers or broad environment dumps.

The Docker daemon or engine socket is a separate, high-authority boundary. A user allowed to control a rootful daemon may be able to start a container with the host filesystem mounted. Do not mount `/var/run/docker.sock` into an application container unless granting engine-level host authority is intentional and tightly controlled. A Podman socket has the authority of its rootless or rootful service identity. Protect API endpoints and credentials like administrative access.

## Diagnose a blocked operation

When an application reports `Operation not permitted`, first identify the failing syscall, path or socket and whether the error occurs inside a user namespace. Check effective UID/GID and capability sets, container options, mount flags, seccomp result and SELinux/AppArmor audit records. Compare a known-working environment with the failing one and change one control at a time. Do not jump to `--privileged`, host PID mode or an unconfined profile; these can hide the underlying configuration problem while exposing the host.

A request to bind port 80 may be avoidable by listening on an unprivileged internal port and letting a proxy or load balancer own the public listener. If the application truly needs a privileged operation, document the reason and test the smallest capability in the correct user namespace. A failed write to `/var/lib/dispatchdesk` may be a volume ownership mismatch rather than a missing capability. A denied clock change should not be “fixed” by granting `CAP_SYS_TIME` to a web process; host time synchronization should own the clock.

## Review the boundary as a set

For every workload, record its host identity, container user, user namespace mapping, capabilities, seccomp profile, LSM policy, namespace sharing, device access, mounted paths, writable filesystems, network exposure and cgroup limits. Identify which operator can change each setting and how the effective runtime configuration is checked after deployment. A security exception should include owner, reason, scope, review date and removal condition.

Containers also share the host kernel and kernel drivers. Keep the host patched and minimize the set of workloads that can access sensitive host interfaces. Isolate workloads with different trust levels across hosts or stronger sandbox technologies when the threat model requires it. A container boundary is one layer in the host security design, not a substitute for a virtual machine in every adversarial workload.

## Exercises and review questions

1. Why should a web API on port 8080 normally not need `CAP_NET_BIND_SERVICE`?
2. A container can read a secret file through a bind mount even though the image runs as a numeric non-root user. Which host ownership and mapping facts do you need to inspect?
3. Explain how a seccomp denial differs from an SELinux or filesystem permission denial, and where evidence for each may appear.
4. What host authority can be granted by mounting the Docker Engine socket into a container?
5. Design a minimal writable-path list for an API with no local database and a temporary upload buffer.

Capabilities, seccomp, identity mapping, mount policy and LSM enforcement reduce different kinds of authority. Test the combined configuration against the real application and keep exceptions small. Next, [Registries and Image Distribution](049-registries-and-image-distribution.md) follows artifacts and credentials across the publishing boundary.

## Sources and verification

The Linux [`capabilities(7)`](https://man7.org/linux/man-pages/man7/capabilities.7.html) manual, kernel [seccomp filter documentation](https://docs.kernel.org/userspace-api/seccomp_filter.html), Docker [seccomp](https://docs.docker.com/engine/security/seccomp/) and [security](https://docs.docker.com/engine/security/) documentation were inspected on 2026-10-02. The illustrative Docker command passed shell syntax checks but was not run; its image placeholder must be replaced and writable paths verified. Engine defaults are version-specific. Independent review is pending.
