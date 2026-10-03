---
book: The Complete DevOps Engineering Book
volume: 7
volume_title: "Podman and the Rootless Host"
chapter: 61
title: "Installing and Understanding Podman"
slug: installing-and-understanding-podman
status: complete
summary: ../../_ai/chapter-summaries/061-installing-and-understanding-podman.md
---

# Chapter 61 — Installing and Understanding Podman

## Installation and version inspection

DispatchDesk's fictional VPS team wants to run a small HTTP service under a dedicated ordinary account. The host already supplies TLS termination and backups. The requirement is repeatable process deployment with bounded authority; it does not require a cluster scheduler. Podman fits when the service can use unprivileged ports, local container storage and a systemd user manager. The choice still requires someone to own patching, account lifecycle, persistent data and recovery. A daemonless engine does not make those responsibilities disappear.

Read [Docker production operations](../06-docker-in-practice/060-docker-production-operations.md) for the operational comparison and [rootless mapping](../05-container-internals-and-oci/047-rootless-containers-and-user-mapping.md) for the underlying Linux model. This volume uses a disposable Linux host and an ordinary login account throughout. Use the same account for every command unless explicitly told otherwise. Commands run on the container host, from any directory except examples that create files. A desktop remote client is a separate case introduced below.

Install packages as a host administrator. On Ubuntu 24.04 LTS, use the distribution repositories:

```bash
sudo apt-get update
sudo apt-get install podman uidmap
apt-cache policy podman uidmap
```

On Fedora 44:

```bash
sudo dnf install podman
rpm -q podman
```

On a supported RHEL 9 or RHEL 10 host with the appropriate subscribed repositories enabled:

```bash
sudo dnf install podman
sudo dnf repolist
rpm -q podman
```

These are three targets, not a promise that they deliver the same upstream version or helpers. RHEL repository access depends on entitlement and image configuration. Rocky Linux and AlmaLinux operators should use their own supported repositories and release documentation. Do not substitute Fedora testing packages into a RHEL server. If a package is unavailable, inspect the release, enabled repositories and vendor support before adding another source. Podman's [installation instructions](https://podman.io/docs/installation) provide distribution entry points; Red Hat's [container guide](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/building_running_and_managing_containers/index) supplies RHEL-specific policy.

Return to the ordinary workload account after installation. Record identity and effective engine configuration:

```bash
id
podman --version
podman --remote=false version
podman --remote=false info
```

`--remote=false` deliberately selects local engine operation. `version` reports the executable's version; `info` attempts to inspect the engine environment. Read the rootless security status, OCI runtime, storage driver, graph root, cgroup version/manager and networking backend. Retain a redacted copy in the host inventory. The [info manual](https://docs.podman.io/en/stable/markdown/podman-info.1.html) explains its structured JSON and template interfaces. Use full output first because fields and defaults differ between releases.

Success means more than a printed version string. An executable can be installed while its namespace helpers, runtime directory or storage are unusable. Conversely, a sandbox's inability to create a user namespace says something about that sandbox, not necessarily the host kernel. This book's authoring baseline recorded Podman 6.1.2 on 2026-10-01, but did not demonstrate container execution. The examples here were checked against upstream stable documentation on 2026-10-03; they do not assert that every distribution ships that version.

A host record should identify the kernel, distribution, engine package, storage backing filesystem and account UID. Rootless files belong to a numeric mapping. Recreating a service account with the same spelling and a different UID does not recreate its authority over old files. Plan account preservation with the same care as a storage migration.

## Local and remote execution

Local Podman on Linux operates using the invoking account. Rootful Podman uses a separate store. The optional API service permits remote or compatibility clients to control an engine under the server account. Therefore, record four facts before mutation: client machine, execution host, engine account and store. The local shell's `id` identifies only the client account in a remote workflow.

Inspect possible redirection without starting any service:

```bash
printf 'CONTAINER_HOST=%s\n' "${CONTAINER_HOST-}"
printf 'CONTAINER_CONNECTION=%s\n' "${CONTAINER_CONNECTION-}"
podman system connection list
podman --remote=false ps --all
```

Review endpoint output before sharing it. A named connection may use SSH to reach a Unix socket on another machine. The client can also target a socket through environment configuration. When using a deliberate remote connection, select its known name explicitly and compare the server information with your inventory. Do not blindly unset a production environment and then issue a deletion: changing the destination can be as dangerous as leaving a mistaken destination selected.

Native macOS and Windows workflows commonly use `podman machine`, which runs containers inside a Linux guest. A path on a laptop and a path on a remote server are not interchangeable bind-mount sources. The service's listening port is likewise on the execution environment until the appropriate forwarding makes it reachable. This volume's labs avoid those additional boundaries by using a Linux host directly; remote operators should perform host filesystem diagnostics over an authorized host login.

API access grants control over the resources available to the service identity. A rootless socket can expose the account's readable files and credentials through container mounts. A rootful socket can permit much broader host control. Do not expose an unauthenticated TCP endpoint to make an integration convenient. Use protected local sockets or authorized SSH access, and audit both the account and endpoint permissions. The [service manual](https://docs.podman.io/en/stable/markdown/podman-system-service.1.html) explains the service boundary.

## Comparing daemonless operation with Docker

The useful comparison is how operational ownership changes. Local Podman does not need a permanently running central engine daemon for ordinary CLI operations. Container monitor and runtime processes still exist, and the workload still requires supervision. Closing the terminal does not become a deployment strategy. Chapter 66 establishes that strategy with Quadlet and systemd.

Docker's familiar `run`, `inspect`, `logs` and `exec` vocabulary makes learning easier, but command resemblance does not establish identical storage, network or restart behavior. Podman images can be shared with Buildah under compatible local configuration; Buildah's working containers are not Podman's running containers. Docker and Podman stores are separate. OCI image portability also does not transfer named volumes or daemon configuration.

For the fictional DispatchDesk VPS team, dedicated rootless accounts reduce the authority of routine deployment work. For its fictional managed-cloud team, provider workload services may eliminate host engine administration entirely. Neither choice makes the other team less mature. Decide according to operational constraints: required device access, available systemd integration, network performance, team familiarity and the cost of migrating existing tooling.

Suppose a developer runs a successful service, then an administrator checks `sudo podman ps` and sees nothing. The failed assumption is that all Podman invocations address one host-wide inventory. First identify the account that started the service and inspect local state under that account. Check listening ports and process ownership independently if the account is uncertain. Do not recreate the service as root merely to make it appear in the administrator's inventory; that can cause a port collision and create a second persistence domain.

A second common failure is an initial pull that prompts for a registry selection. Short names depend on host registry configuration and interactive behavior. Use fully qualified names such as `docker.io/library/nginx:alpine` in labs. This tag remains mutable. A production deployment should resolve and record an actual digest, architecture and approval evidence, as explained in [image promotion](../06-docker-in-practice/059-publishing-and-promoting-images.md). A memorable tag cannot substitute for that record.

## Acceptance evidence and recovery

Build an installation acceptance sheet before deploying DispatchDesk. It should contain the selected account, effective local/remote mode, version, rootless status, storage mount and cgroup support. Then run a disposable image that has a simple predictable exit contract. Chapter 62 supplies a retained HTTP fixture so failures leave evidence. Installation acceptance should include a pull, process launch, stop and cleanup, not just package presence.

If `info` fails, preserve its exact error. Check runtime directory access through the normal login session, namespace/helper availability and the storage filesystem. A service account entered through an improvised `su` session may lack the expected user manager and runtime environment. Establish the supported login or service setup rather than inventing `XDG_RUNTIME_DIR` paths. If package installation fails, restore the intended repository configuration before retrying. If a new engine package causes regression, use the vendor-supported rollback approach with known data compatibility; do not assume an older executable can read a newer store.

Rootless operation still permits disk exhaustion and access to the account's secrets. Give the deployment account a narrow purpose, separate persistent application state from caches, and monitor the host. Avoid using a human's entire home directory as the service's persistence boundary. That choice complicates both least privilege and later recovery.

## Exercises and review questions

1. Write an inventory row for a local rootless host and another for a laptop controlling a rootless Linux server. **Guidance:** distinguish client UID from server UID and identify where graph storage and published ports live.
2. Explain why `podman --version` can succeed while `podman info` fails. **Guidance:** the first may inspect the executable only; engine initialization needs runtime, namespace and storage access.
3. An administrator sees no containers under `sudo`. What evidence comes before a restart? **Guidance:** owning account, local/remote selection, process owner, listening socket and the owner's inventory.
4. Choose between local Podman and a managed workload service for a team without host on-call capacity. **Guidance:** include who patches kernels, restores data and diagnoses failed launches; CLI familiarity is insufficient.

## Takeaways and further reading

Identify the execution host and account before interpreting engine output. Installation is a staged acceptance process, and daemonless execution still needs a service lifecycle. Continue with [the container lifecycle](062-the-podman-container-lifecycle.md).

Primary documentation inspected 2026-10-03 includes the [Podman manual](https://docs.podman.io/en/stable/markdown/podman.1.html), installation and info references linked above. These examples have not been executed on the baseline distributions; package availability and engine initialization require target-host verification.
