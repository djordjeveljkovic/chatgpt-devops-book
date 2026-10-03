---
book: The Complete DevOps Engineering Book
volume: 6
volume_title: "Docker in Practice"
chapter: 51
title: "Installing and Inspecting Docker"
slug: installing-and-inspecting-docker
status: draft
summary: ../../_ai/chapter-summaries/051-installing-and-inspecting-docker.md
---

# Chapter 51 — Installing and Inspecting Docker

Docker has a client and a server. The `docker` command is the client; the Docker Engine daemon manages images, containers, networks and volumes. They may run on one machine or communicate across an explicitly configured remote context. This chapter installs Engine on a disposable Linux learning host and teaches you to confirm exactly which client and daemon you are controlling. It does not ask you to install Docker on a production machine without a change plan.

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

For both RPM procedures, inspect any signing-key prompt against Docker's published fingerprint and your organization's package policy. `enable --now` both starts the daemon now and arranges for it to start after reboot. If policy says Docker must be manually started, use `systemctl start docker` instead and record that choice. On SELinux hosts, keep enforcement enabled and use supported container labels and mounts; do not disable SELinux to make an application work. Docker Engine uses its own networking and packet-filter integration, so review the official firewall notes and your host's existing `firewalld`/`nftables` design before publishing ports. Chapter 52 demonstrates a loopback-only test mapping; it does not replace firewall review.

Docker's convenience installation script is aimed at development and testing, not routine production provisioning. It chooses packages based on detection, installs the latest stable release, and is less explicit than a pinned, reviewed package policy. For managed hosts, record the selected Engine and plugin versions, test upgrades in a staging environment, and roll out through configuration management. If you need a fixed package version, list the versions available for that OS release and select an approved one rather than copying a version string from another machine.

## Daemon access and privilege

The rootful daemon generally has host-level authority. A user who can control it can often mount host filesystems into containers, start privileged containers or otherwise gain root-equivalent access. Membership in the `docker` group therefore grants broad administrative power even if the group name sounds like ordinary application access. Grant it only to trusted operators, audit membership and consider rootless mode where its limits fit the workload; chapter 47 explains user namespaces and rootless engines.

Initially, verify the engine with `sudo`. The `hello-world` image is downloaded from a registry and runs a short process; it changes the local image cache but does not create durable application data:

```bash
sudo docker run --rm hello-world
```

If the command fails, separate common boundaries. “Cannot connect” may mean the daemon is stopped, the socket path is wrong or the selected context points elsewhere. A DNS or TLS error indicates registry connectivity or trust. An authorization error can mean the registry requires authentication. A successful pull but failed start points later in the process chain; inspect its exit status and logs. Do not solve a socket permission error by making the socket world-writable.

## Verifying client, server and context

One command can show several pieces of evidence:

```bash
docker version
docker context show
docker context inspect "$(docker context show)"
docker info
```

`docker version` reports separate client and server versions and API details. A missing server section means the client did not reach an Engine. `docker context show` names the active target; `context inspect` displays its endpoint and TLS-related settings. The `docker info` output describes server configuration such as storage driver, cgroup version, security options and resource counts. Review it before assuming the host matches a tutorial. Treat endpoint configuration and daemon metadata as infrastructure information; redact internal addresses when sharing output publicly.

If a team supports both rootless and rootful Docker, name contexts clearly and verify the target before destructive operations. Context switching is persistent for the CLI user, so a shell opened later may still target a remote daemon. Make production scripts explicit by selecting a context under controlled configuration or using a reviewed endpoint; do not rely on a developer's interactive default. Chapter 46 compares Docker and Podman interfaces and their security boundaries.

For a repeatable host, capture the expected package origin and version, systemd service state, active context, server version and security mode in configuration management or an inventory check. A command succeeding as root proves only that one identity reached one daemon at that moment. It does not show that the intended CI runner has access, that firewall behavior is correct, or that the host will recover after reboot.

## Exercises and review questions

1. Why should an operator inventory existing runtime packages and workloads before removing packages that conflict with Docker Engine?
2. Explain the difference between `systemctl start docker` and `systemctl enable --now docker`.
3. A CLI reports a client version but no server version. What evidence would distinguish a stopped local daemon from an unexpected remote context?
4. Why is access to a rootful Docker socket treated as administrative access?
5. A host supports both Ubuntu and RHEL. Which repository details must be independently checked rather than copied between them?

## Sources and verification

Docker's official [Ubuntu](https://docs.docker.com/engine/install/ubuntu/), [Fedora](https://docs.docker.com/engine/install/fedora/), [RHEL](https://docs.docker.com/engine/install/rhel/), [Linux post-installation](https://docs.docker.com/engine/install/linux-postinstall/), [context](https://docs.docker.com/engine/manage-resources/contexts/) and [firewall](https://docs.docker.com/engine/network/packet-filtering-firewalls/) documentation were inspected on 2026-10-02. Supported release lists and package commands reflect that inspection date. No packages were installed and no daemon, registry or firewall was contacted from this workspace.
