---
book: The Complete DevOps Engineering Book
volume: 6
volume_title: "Docker in Practice"
chapter: 51
title: "Installing and Inspecting Docker"
slug: installing-and-inspecting-docker
status: complete
summary: ../../_ai/chapter-summaries/051-installing-and-inspecting-docker.md
---

# Chapter 51 — Installing and Inspecting Docker

Docker has a client and a server. The `docker` command is the client; the Docker Engine daemon manages images, containers, networks and volumes. They may run on one machine or communicate across an explicitly configured remote context. [Chapter 50](../05-container-internals-and-oci/050-the-container-contract.md) introduced the container runtime contract. This chapter installs Engine on a disposable Linux learning host and teaches you to confirm exactly which client and daemon you are controlling. It does not ask you to install Docker on a production machine without a change plan.

Package installation changes system services, firewall behavior and package sources. Before beginning, record the host's distribution and release, confirm you have console or SSH recovery access, check whether Podman or another engine already owns workloads, and save data that must survive. Docker's installation documentation lists conflicting packages; removing them can remove the existing runtime even though container data may remain on disk. Never paste a cleanup command blindly into a host that already runs workloads.

## Engine installation on both Linux families

Use the supported repository for the exact distribution and architecture. As of the documentation review date, Docker's pages listed Ubuntu 22.04, 24.04 and 26.04; Fedora 43 and 44; and RHEL 8, 9 and 10. Availability changes as distributions age and new releases appear, so check the official compatibility list at installation time. Fedora and RHEL use different repository URLs and package availability; RHEL may also require a valid subscription for the underlying operating system repositories. A compatible community rebuild is not the same support target as RHEL.

On a new Ubuntu host, the following follows Docker's APT repository procedure. It installs the signing key in a dedicated keyring, binds that key to the Docker repository and installs the engine, CLI and plugins:

```bash
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl status docker
```

The `tee` command writes the repository definition as root; the heredoc expands the host's release codename and architecture. Review those values before the final install, especially on derivatives that Docker does not officially support. The status command shows whether the service is active; if an intended service is stopped, inspect `journalctl -u docker` before deciding whether to start it. Installation of packages changes the host and may start a daemon.

On Fedora, the package repository setup uses the Fedora-specific repository file. The package installation does not start the daemon, so the explicit `systemctl` command is part of the procedure:

```bash
sudo dnf config-manager addrepo --from-repofile https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

On RHEL, install the repository-management plugin and use Docker's RHEL repository. This is not the Fedora repository:

```bash
sudo dnf -y install dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
sudo dnf install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

For both RPM procedures, inspect any signing-key prompt against Docker's published fingerprint and your organization's package policy. `enable --now` both starts the daemon now and arranges for it to start after reboot. If policy says Docker must be manually started, use `systemctl start docker` instead and record that choice. On SELinux hosts, keep enforcement enabled and use supported container labels and mounts; do not disable SELinux to make an application work. Docker Engine uses its own networking and packet-filter integration, so review the official firewall notes and your host's existing `firewalld`/`nftables` design before publishing ports. [Chapter 52](052-running-and-managing-containers.md) demonstrates a loopback-only test mapping; it does not replace firewall review.

Docker's convenience installation script is aimed at development and testing, not routine production provisioning. It chooses packages based on detection, installs the latest stable release, and is less explicit than a pinned, reviewed package policy. For managed hosts, record the selected Engine and plugin versions, test upgrades in a staging environment, and roll out through configuration management. If you need a fixed package version, list the versions available for that OS release and select an approved one rather than copying a version string from another machine.

## Daemon access and privilege

The rootful daemon generally has host-level authority. A user who can control it can often mount host filesystems into containers, start privileged containers or otherwise gain root-equivalent access. Membership in the `docker` group therefore grants broad administrative power even if the group name sounds like ordinary application access. Grant it only to trusted operators, audit membership and consider rootless mode where its limits fit the workload; [Chapter 47](../05-container-internals-and-oci/047-rootless-containers-and-user-mapping.md) explains user namespaces and rootless engines.

Initially, verify the rootful engine with the same privileged identity used for installation. The `hello-world` image is downloaded from a registry and runs a short process; it changes the local image cache but does not create durable application data. This first `--rm` example removes the container automatically after exit, so its immediate terminal output and shell exit status are the available evidence; it leaves no container object to inspect later:

```bash
sudo docker run --rm hello-world
```

If you need retained evidence after a failure or for a runbook, repeat the smoke test without `--rm`, give it a unique name, and inspect the stopped object before removing it:

```bash
sudo docker run --name docker-install-smoke-test hello-world
sudo docker inspect docker-install-smoke-test \
  --format 'status={{.State.Status}} exit={{.State.ExitCode}} image={{.Config.Image}}'
sudo docker logs docker-install-smoke-test
sudo docker rm docker-install-smoke-test
```

This retry again pulls the image only if absent. A successful one-shot container is expected to stop after printing its message; a failed `run` may leave a stopped container, depending on where creation failed. Capture the original terminal error as well as inspect/log evidence. If the name already exists, do not remove the prior object until you confirm it belongs to this exercise.

If the command fails, separate common boundaries. “Cannot connect” may mean the daemon is stopped, the socket path is wrong or the selected context points elsewhere. A DNS or TLS error indicates registry connectivity or trust. An authorization error can mean the registry requires authentication. A successful pull but failed start points later in the process chain; inspect its exit status and logs. Do not solve a socket permission error by making the socket world-writable.

## Verifying client, server and context

The installation procedure verified the local rootful socket with `sudo`. Use this block under that same identity and force the intended local socket for both version and daemon inspection:

```bash
sudo env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_CONFIG \
  docker --host unix:///var/run/docker.sock version
sudo env -u DOCKER_HOST -u DOCKER_CONTEXT -u DOCKER_CONFIG \
  docker --host unix:///var/run/docker.sock info
```

`env -u` removes endpoint and CLI-configuration overrides from this one invocation; `--host` selects the rootful local Unix socket explicitly. `docker version` reports separate client and server versions and API details. A missing server section means the client did not reach the specified Engine. `docker info` describes daemon configuration such as storage driver, cgroup version, security options and resource counts. The commands must use the same identity and target so that the version and info outputs describe the same server. Review metadata before assuming the host matches a tutorial, and redact internal details when sharing output publicly.

An ordinary operator should verify only a daemon they are authorized to access. Do not add that operator to the `docker` group as a troubleshooting shortcut. Under that identity, inspect the context and environment overrides, then test the intended target explicitly:

```bash
printf 'DOCKER_HOST=%s\n' "${DOCKER_HOST-<unset>}"
printf 'DOCKER_CONTEXT=%s\n' "${DOCKER_CONTEXT-<unset>}"
printf 'DOCKER_CONFIG=%s\n' "${DOCKER_CONFIG-<default>}"
docker context show
docker context inspect "$(docker context show)"
env -u DOCKER_HOST docker --context default version
```

`DOCKER_CONTEXT` can override the context selected with `docker context use`; `DOCKER_HOST` can name an endpoint directly; and the global `--context` or `--host` flags can select a target for one command. Do not combine `--context` and `--host`. `DOCKER_CONFIG` changes the CLI configuration directory and therefore which stored contexts and credentials are visible. The `default` context usually points to the local rootful socket, but its stored endpoint and access policy must be confirmed. If this user has no permission to that socket, the failed connection is expected; use the approved identity/path rather than changing permissions.

If a team supports both rootless and rootful Docker, name contexts clearly and verify the target before destructive operations. Context switching is persistent for the CLI user, so a shell opened later may still target a remote daemon. Make production scripts explicit by selecting a context under controlled configuration or using a reviewed endpoint; do not rely on a developer's interactive default. [Chapter 46](../05-container-internals-and-oci/046-oci-runtimes-and-container-engines.md) compares Docker and Podman interfaces and their security boundaries.

For a repeatable host, capture the expected package origin and version, systemd service state, active context, server version and security mode in configuration management or an inventory check. A command succeeding as root proves only that one identity reached one daemon at that moment. It does not show that the intended CI runner has access, that firewall behavior is correct, or that the host will recover after reboot.

## Exercises and review questions

1. Why should an operator inventory existing runtime packages and workloads before removing packages that conflict with Docker Engine?
2. Explain the difference between `systemctl start docker` and `systemctl enable --now docker`.
3. A CLI reports a client version but no server version. What evidence would distinguish a stopped local daemon from an unexpected remote context?
4. Why is access to a rootful Docker socket treated as administrative access?
5. A host supports both Ubuntu and RHEL. Which repository details must be independently checked rather than copied between them?

### Practical exercise and answer guidance

On a disposable host, install using the section for its actual distribution, inspect daemon status and record the client/server version pair. Run the initial `hello-world` command, then repeat with the named retained test container and capture its exit state and logs. Confirm that the context endpoint and any `DOCKER_HOST`, `DOCKER_CONTEXT` and `DOCKER_CONFIG` overrides match the daemon you intended to test. Clean up only the named smoke-test container.

Expected evidence is a running daemon, matching client and server version output, a successful short-lived hello-world process, an exited named container with exit code 0 and its retained message in logs. On access failure, inspect the actual user, socket access policy, selected endpoint, context and overrides; do not grant new authority just to make the command pass. Package repository URLs and service-start behavior must match Ubuntu, Fedora or RHEL separately. No host installation or runtime result is claimed here.

1. Inventory conflicts first because removing a runtime package can disrupt existing workloads and network configuration.
2. `start` activates the unit now; `enable --now` also configures it to start during future boots.
3. Check the context endpoint and override variables, then test the intended local endpoint with an explicit `--host` or `--context`. A context name alone is not a successful connection.
4. A rootful daemon can mount host paths and launch privileged processes; socket control therefore often enables host-root-equivalent actions.
5. Verify repository URL, signing key, release codename, architecture, supported versions, package names and startup policy independently. Fedora and RHEL use different Docker repositories, and RHEL host repositories may require subscription access.

## Takeaways

- Docker's client and daemon may target different machines; verify the exact endpoint before acting.
- Installation and package removal change host state, services and network integration; inventory existing workloads first.
- Rootful daemon access is administrative authority. Do not grant group membership or change socket modes casually.
- Context name, endpoint variables, CLI configuration directory and command-line flags all affect target selection.
- A disposable smoke test with `--rm` leaves terminal output and exit status; a named run preserves stopped-container inspection evidence.
- Ubuntu and Fedora/RHEL require separate repository procedures and current support checks.

## Sources and verification

Docker's official [Ubuntu](https://docs.docker.com/engine/install/ubuntu/), [Fedora](https://docs.docker.com/engine/install/fedora/), [RHEL](https://docs.docker.com/engine/install/rhel/), [Linux post-installation](https://docs.docker.com/engine/install/linux-postinstall/), [context](https://docs.docker.com/engine/manage-resources/contexts/), [context show](https://docs.docker.com/reference/cli/docker/context/show/), [run](https://docs.docker.com/reference/cli/docker/container/run/), [remove](https://docs.docker.com/reference/cli/docker/container/rm/) and [firewall](https://docs.docker.com/engine/network/packet-filtering-firewalls/) documentation were inspected on 2026-10-03. Supported release lists and package commands reflect that inspection date. No packages were installed and no daemon, registry or firewall was contacted from this workspace.
