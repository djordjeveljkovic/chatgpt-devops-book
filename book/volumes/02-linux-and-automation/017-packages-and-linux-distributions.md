---
book: The Complete DevOps Engineering Book
volume: 2
volume_title: "Linux and Automation"
chapter: 17
title: "Packages and Linux Distributions"
slug: packages-and-linux-distributions
status: complete
summary: ../../_ai/chapter-summaries/017-packages-and-linux-distributions.md
---

# Chapter 17 — Packages and Linux Distributions

## Why this matters

DispatchDesk's source code is only part of what runs. The interpreter, C library, TLS implementation, database client, and operating-system utilities come from somewhere. A package manager records much of that relationship and handles dependencies. A copied binary or root-executed download script can bypass that record while still appearing to work.

Harbor needs an installation workflow that can explain what changed, which repository supplied it, and how a replacement host will receive compatible software. Summit and Atlas also need that workflow when building machine or container images. Packaging does not remove supply-chain risk, but a disciplined package transaction is easier to inspect than an undocumented collection of files.

This chapter treats Ubuntu 24.04 LTS, Fedora 44, and RHEL 9 as separate environments. Commands that look similar do not prove identical repositories, support periods, package versions, configuration paths, or security policy. Record the release and architecture before solving a dependency problem.

## Packages, repositories, and dependency resolution

A package includes files and metadata such as its identity, version, architecture, dependencies, and lifecycle actions. Installing it can run scripts and change services, users, caches, or configuration. An installation is therefore a host mutation, not just extracting an archive.

The low-level package database records installed content. A higher-level manager obtains repository metadata, resolves a compatible transaction, and downloads the chosen packages. On Ubuntu the Debian package layer is dpkg and APT manages repository-based resolution. Fedora and RHEL use RPM packages with DNF-family tools.

A dependency solver finds a transaction satisfying the package metadata. It does not test DispatchDesk's behavior. A solver-approved upgrade can change latency, configuration defaults, or a runtime interface the application relied on. Read the proposed additions, upgrades, removals, and source repositories before accepting it.

Repository metadata and package signatures help establish authenticity according to configured trust. That trust starts with the repository configuration and its key material. Adding a repository increases the set of parties whose software may be selected, sometimes including dependencies beyond the package you intended to install. Verify the publisher and supported release, use the vendor's documented trust scope, and avoid disabling signature checks to make an error disappear.

## Identify the actual environment

These read-only observations work before choosing a package branch:

```bash
cat /etc/os-release
uname -m
command -v python3
python3 --version
```

The final commands assume Python is present; failure is an observation, not an instruction to install an arbitrary runtime. An upstream version string alone does not identify the distribution's package revision. Vendors can backport fixes while retaining an older upstream number. Consult the vendor advisory and installed package identity before claiming a vulnerability is unfixed merely from a banner.

Similarly, `/usr/bin/python3` can differ from a virtual environment interpreter or a binary earlier in PATH. Resolve which executable the service unit uses. Chapter 16's absolute command path makes that relationship visible, while application dependencies still need their own lock and installation policy.

## Ubuntu: inspect, simulate, install, verify

Ubuntu 24.04 uses deb822-style repository configuration by default, commonly in `/etc/apt/sources.list.d/ubuntu.sources`. Inspect existing configuration rather than assuming older tutorials' `/etc/apt/sources.list` is authoritative. Ubuntu recommends `apt` for interactive use and `apt-get` for scripts. [Ubuntu package management guide](https://ubuntu.com/server/docs/how-to/software/package-management/).

On a disposable Ubuntu VM, use a small utility such as jq to practice. Inspect its candidate and simulate the transaction first:

```bash
apt-cache policy jq
apt-get --simulate install jq
dpkg-query -W -f='${Package} ${Version} ${Architecture}\n' jq
```

The last query can fail if jq is not installed. A simulation is based on the metadata currently available; stale metadata may not describe what a refreshed transaction selects. It also cannot prove that maintainer scripts or service interactions will succeed. A nonprivileged simulation may not have the same access to all configuration as the real operation; compare the proposed transaction again before accepting it. [APT transaction and simulation semantics](https://manpages.debian.org/bookworm/apt/apt-get.8.en.html).

Only in the intended disposable Ubuntu VM, refresh metadata and install after reviewing the proposal:

```bash
sudo apt-get update
sudo apt-get install jq
jq --version
dpkg-query -W -f='${Package} ${Version} ${Architecture}\n' jq
```

`update` refreshes repository information; it is not an upgrade of every installed package. The install command remains interactive so the reader can inspect its proposed transaction. Production automation can make a reviewed noninteractive choice, but blindly adding `-y` to an unfamiliar host is not a deployment design.

Removing a package and purging its package-managed configuration are distinct operations. Neither is a universal cleanup of application data, secrets, or every file created at runtime. Review ownership and retention separately before teardown. Also inspect automatically installed dependencies before removing them through an autoremove workflow; package relationships do not know every locally deployed consumer.

## Fedora: DNF5 is a distinct baseline

Fedora changed its default DNF implementation to DNF5; do not assume every DNF4 plugin or output parser works unchanged. Check the installed command and version. The Fedora 44 examples use the explicit `dnf5` executable so their intended interface is clear. [Fedora DNF5 change](https://fedoraproject.org/wiki/Changes/SwitchToDnf5).

On a disposable Fedora VM, inspect the candidate and decline the proposed installation transaction before applying it:

```bash
dnf5 --version
dnf5 info jq
dnf5 --assumeno install jq
rpm -q jq
```

`--assumeno` refuses confirmation; it is not a guarantee of zero activity. Repository metadata may be refreshed or cached, and the command can return a nonzero status because the transaction was declined. Inspect the displayed proposal instead of treating that deliberate refusal as an application fault. The install command resolves requested packages and their dependencies. [DNF5 utility options](https://dnf5.readthedocs.io/en/latest/dnf5.8.html), [DNF5 install command](https://dnf5.readthedocs.io/en/latest/commands/install.8.html).

After reviewing repositories, additions, and dependencies, install on that same disposable VM:

```bash
sudo dnf5 install jq
rpm -q jq
jq --version
```

Using an exact package specification can select a particular available build, but availability and dependencies still depend on the repository set. Do not copy a Fedora build identifier into RHEL and assume it belongs there. Package architecture and release suffixes are part of its environment contract.

## RHEL: repositories and streams matter

RHEL 9 uses its supported DNF interface and repositories tied to entitlement and host configuration. An unregistered machine or disabled repository can make a package unavailable; substituting an unrelated third-party repository changes the support and trust model. Check subscription and repository access through the organization's approved process before altering sources. Rocky Linux and AlmaLinux offer their own repositories and policies; their compatibility goals do not make their subscription or provenance evidence identical to RHEL's.

Practice the corresponding inspection and installation branch on a disposable, appropriately entitled RHEL 9 machine:

```bash
dnf --version
dnf repolist
dnf info jq
dnf --assumeno install jq
```

After reviewing the declined proposal, the actual mutation is:

```bash
sudo dnf install jq
rpm -q jq
jq --version
```

For software offered as modular content, a stream identifies a selected version line and a profile identifies a package grouping. Inspect what the current repositories offer and the support policy before selecting a stream. RHEL 9 does not predefine default module streams; an example stream from a manual is not a current recommendation for production. [RHEL 9 installation and modular-content guide](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_software_with_the_dnf_tool/assembly_installing-rhel-9-content_managing-software-with-the-dnf-tool).

RHEL 10 package availability and delivery can differ; do not mechanically repeat RHEL 9 module-selection instructions. Recheck the major release's installation documentation and actual repository results. Likewise, an Ubuntu 26.04 migration and a Fedora release upgrade require a release-specific plan, not just an ordinary package upgrade command.

## Reproducibility requires retained inputs

A list containing `python3` and `jq` expresses intent but does not freeze the complete installation. Repository contents change. The selected dependencies, architecture, distribution revision, and configuration also matter. Record the resolved package inventory and the repository/image provenance for a release, together with the application's own dependency lock.

An exact version request improves precision only while that version and its compatible dependencies remain obtainable. A controlled repository snapshot or retained image can make reconstruction more reliable. Retaining an old image does not justify ignoring security updates; establish a deliberate refresh and retest cadence. Reproducibility and patching are engineering responsibilities that need a common workflow.

Separating OS and application dependencies helps. Do not overwrite distribution-managed libraries with an unrelated language package installer run as root. Use an isolated application environment where appropriate, then record how it was built. A clean rebuild should either reproduce the intended artifact or explain the deliberate update; resolving whatever happens to be newest during production startup defeats that review boundary.

For Harbor, a small documented base package set and a tested replacement VM may be sufficient. Summit can build and retain an image with the runtime dependencies. Atlas can review a container base and application layer. None of these choices alone proves the application invariant; all need behavior checks after dependency changes.

## Recover an interrupted upgrade

Suppose Harbor upgrades its runtime dependencies, then the worker fails to start. Preserve the package transaction record and application error. Determine whether installation completed, whether configuration handling changed, and whether the running process still uses old mapped libraries while files on disk have changed. Inspect the specific executable and package identity rather than trusting your interactive shell's PATH.

In this scenario the package manager completed correctly, but a deployment script built the application's dependencies with a different Python interpreter than the service unit used. Repair the build/runtime contract and rebuild the isolated environment using the intended interpreter. Do not downgrade the whole operating system merely because one environment is mismatched.

An interrupted package transaction has a different recovery. Confirm no legitimate package process is still running and inspect the manager's diagnostic state. Do not delete lock files reflexively: a lock can be evidence of an active owner, and removing it permits competing mutations. Follow the distribution's repair procedure for the recorded incomplete state, then verify package database consistency and the affected service.

Rollback also has limits. An older package may be unavailable, dependencies may have changed, and an application or database may have migrated persistent data. A package-manager history entry is useful evidence, not a complete system restore. Maintain tested backups and a replacement-host path, and separate application data recovery from reinstalling software.

## Exercises and takeaways

1. Record release, architecture, interpreter path, upstream runtime version, and package identity on your lab VM. Guidance: each describes a different part of the running dependency contract.
2. Compare a declined jq transaction with the accepted installation on one distribution. Guidance: record selected dependencies and repositories; do not call a preview a runtime test.
3. Explain why an exact package version is insufficient for indefinite reproducibility. Guidance: repository retention, architecture, dependencies, and configuration remain inputs.
4. Draft a runtime-upgrade recovery plan. Guidance: preserve transaction evidence, distinguish incomplete installation from application incompatibility, test data compatibility before rollback, and verify service behavior afterward.

Package management is a controlled change to trusted host content. Inspect the environment and transaction, retain provenance, isolate application dependencies, and verify the running service after updates. Continue to [Chapter 18](018-shell-automation-that-survives-failure.md) to turn these operational intentions into bounded, restartable automation.

## Verification

The author inspected Ubuntu, APT, Fedora DNF5, upstream DNF5, and RHEL 9 primary documentation. Package commands are reader VM exercises; no repository refresh, installation, removal, subscription change, or upgrade was executed during writing. Baseline package availability and transaction output must be checked on the actual reader host.
