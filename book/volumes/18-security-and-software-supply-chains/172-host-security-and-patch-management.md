---
book: The Complete DevOps Engineering Book
volume: 18
volume_title: "Security and Software Supply Chains"
chapter: 172
title: "Host Security and Patch Management"
slug: host-security-and-patch-management
status: complete
summary: ../../_ai/chapter-summaries/172-host-security-and-patch-management.md
---

# Chapter 172 — Host Security and Patch Management

**Section outline:** reduce exposed services and privileged access; compare Ubuntu with Fedora and RHEL update/security behavior; build an evidence-based maintenance and recovery process for DispatchDesk.

## Access, packages and attack surface

A host is secure only to the extent that its effective controls resist the actors and failures in its threat model. [Chapter 171](171-threat-modeling-for-operators.md) identified identities, release authority, service availability and recovery material as assets. This chapter turns that model into host-level work: restrict who can administer the machine, keep its installed software within a supported update stream, expose only necessary services, and preserve a way to recover when a change or compromise breaks the host.

Begin with the host's role. A public reverse proxy, a database node, a build runner and a developer laptop need different packages, inbound rules, credentials and maintenance windows. “Harden Linux” is not a list of magic toggles. It is a decision about which processes and people need which capabilities, how changes are delivered, and what evidence demonstrates that the intended state is active. Removing a service without checking dependencies can break an application; closing SSH without a second access path can lock out the operators. Every reduction in attack surface needs a tested operational alternative.

Use named administrative accounts and a separate, logged elevation path. Keep application processes unprivileged and avoid giving deploy automation a general-purpose root shell. Where practical, restrict administrative access at more than one boundary: the cloud or hypervisor network policy, host firewall, SSH authentication, and account authorization. A firewall does not authenticate an administrator, and SSH key authentication does not make an over-privileged account safe. Remove former staff and stale automation credentials promptly; rotate shared credentials where individual attribution is impossible, then remove the shared design.

Inventory listeners and services before disabling them. Run inspection commands as an administrator in a maintenance session; they do not change state:

```bash
sudo ss -lntup
sudo systemctl --type=service --state=running
sudo systemctl list-unit-files --state=enabled
```

The socket listing associates listening TCP/UDP ports with process information where the caller has permission. The service commands show running units and units enabled for future starts; neither list is a complete explanation of every reachable path. Compare the results with the service inventory and network policy. A service can be reachable through a local proxy, a container port mapping, a cloud rule or a socket-activated unit even when an operator did not expect it. Then disable only services with a known owner and dependency check, and verify monitoring and application behavior afterward.

Keep the host's mandatory access controls active. Ubuntu commonly uses AppArmor profiles, while Fedora and RHEL commonly ship SELinux policy. These systems confine processes beyond ordinary Unix user/group permissions, but their policy models and administration commands differ. Do not solve a denial by disabling enforcement or applying a broad allow rule before checking the executable label, file context, service domain and audit record. On RHEL, `getenforce` reports the active mode; SELinux enforcing mode both applies policy and records denials. Fedora also uses SELinux; the package and release lifecycle remain Fedora's, not RHEL's. Ubuntu's AppArmor profile status and logs need their own tools and policy. A host can report “running” while mandatory policy is permissive or a key service has no useful confinement.

## Ubuntu and Fedora/RHEL hardening differences

Package names, security metadata, repository support and restart behavior are distribution-specific. A patch policy should name the operating system release and approved repositories, not merely say “Linux.” Keep a machine on a supported release, apply updates from authenticated repositories, and avoid unreviewed package sources. An extra repository expands the set of publishers who can influence installed software. Where organizational policy permits it, prefer reproducible image builds or managed configuration that records repository definitions and package versions.

On Ubuntu Server, APT refreshes repository metadata separately from upgrading installed packages. An administrator can inspect and apply available upgrades in a planned maintenance session:

```bash
sudo apt update
apt list --upgradable
sudo apt upgrade
```

`apt update` changes local package indexes, not installed applications. `apt list --upgradable` is an inspection step. `apt upgrade` applies eligible upgrades; review the proposed transaction and package prompts on the actual release before accepting. If dependencies require removals or a broader transition, review that plan explicitly rather than adding `-y` to make the command unattended. Ubuntu's [automatic updates guide](https://ubuntu.com/server/docs/how-to/software/automatic-updates/) documents `unattended-upgrades`, its allowed origins and the daily APT timers. The default security-update behavior can reduce exposure between maintenance windows, but it does not replace fleet reporting, staged rollout or ownership. Additional repositories are not automatically included; their origins must be deliberately allowed.

Restart requirements need their own check. A package update can replace an on-disk library while a long-running process continues using the old in-memory copy. Ubuntu's `needrestart` integration can identify affected services; beginning with Ubuntu 24.04, the default behavior includes automatic restart of many affected services. That can interrupt traffic, so operators must confirm the release, local configuration and service criticality. Ubuntu may indicate a reboot is required with `/run/reboot-required`; test for the file instead of assuming its presence. Treat a reboot as a change with capacity, access and rollback planning.

Fedora is a fast-moving community distribution with a shorter release lifecycle than RHEL. Use Fedora documentation and repositories for Fedora systems, and plan release upgrades before the installed release leaves its support window. For package updates, DNF refreshes repository metadata and resolves a transaction; use the installed major release's documented command (`dnf5` on releases using DNF5, or `dnf` where that is the supported interface):

```bash
sudo dnf5 --refresh upgrade
```

Read the transaction summary and verify repositories and package sources before confirming. On Fedora, the package manager may expose advisory information when repository metadata supplies it, but advisory selection is not a complete vulnerability inventory: packages without applicable advisory metadata, third-party repositories and software installed outside the package manager need separate coverage. Do not copy RHEL subscription assumptions or support promises onto Fedora.

RHEL's package streams and support model are tied to its repositories and subscription state. For an advisory-scoped operation on a registered RHEL 9 host, Red Hat documents `dnf update --security`; without `--security`, `dnf update` applies all available updates, including bug fixes and enhancements. A subscription and correctly enabled repositories are prerequisites for that documented workflow. Inspect advisory and installed-package evidence, and record when a security-only selection is used instead of a full supported update. [Red Hat's security-update procedure](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_and_monitoring_security_updates/installing-security-updates_managing-and-monitoring-security-updates) also documents `dnf needs-restarting`; it lists processes that need restarting, not a ready-to-use list of systemd service names. Do not turn its output into blind `systemctl restart` commands.

Across all three distributions, separate package installation from the claim that a vulnerability is remediated. A scanner may report package versions, an advisory may identify affected builds, and a service may still have an old library mapped into memory. Record installed package versions, update transaction results, service restarts or reboot completion, and the application-level health check. For an immutable host, build a patched image, test it, roll it out by ring, and replace old instances; a base-image update does not patch machines that remain running. [Chapter 173](173-container-security-in-practice.md) applies a similar distinction to container images.

## A defensible host-maintenance process

DispatchDesk runs a fictional notification worker and database on a small Ubuntu VPS, with a second environment on RHEL-compatible hosts for a customer requiring that platform. The team receives a vulnerability report for a system library used by the worker. A rushed operator sees that APT or DNF has installed a newer package and closes the ticket. Hours later, the worker is still mapped to the vulnerable shared library. During the next restart, a separate configuration error causes the service to fail its health check. The package transaction succeeded; the service recovery and remediation proof did not.

The process needs an owner, a deadline derived from severity and exposure, a tested change path, and a way to identify every affected host. Start by mapping the finding to asset inventory: host identifier, distribution and release, package source, service owner, public exposure, data held and recovery tier. Verify the advisory against the vendor's notice and the host's installed package state. A scanner finding can be stale or can miss an application-bundled library; an advisory can be unavailable for a third-party package. Resolve the affected component before choosing a patch command.

Use a ringed rollout. Apply the patch first to a disposable or low-impact representative host, then a canary, then the rest of a fleet in controlled batches. For a single VPS, a staging clone and a scheduled production window provide a smaller version of this pattern. Before the change, check a restorable backup, tested console or out-of-band access, disk space, current service health and the last known-good application artifact. A backup that has never been restored is only an assumption. Define the stop condition before the window: failed package transaction, failed boot, unavailable SSH, worker error rate above threshold, or a health endpoint outside its normal range.

A host operator can collect a simple evidence bundle before and after the change. These commands are read-only; package inventory formats vary by release, so preserve full output and host identity:

```bash
date --iso-8601=seconds
cat /etc/os-release
uname -r
systemctl --failed
```

On Ubuntu, add `apt list --upgradable` before the upgrade, the relevant APT history/log records after it, and the reboot marker check. On Fedora/RHEL, record the DNF transaction history and the applicable advisory result; for RHEL 9, run `sudo dnf needs-restarting` after the transaction and interpret the entries as processes, not unit names. Capture `systemctl status dispatchdesk-worker` and the application's own health signal after any controlled service restart. Store evidence in the restricted change record, excluding secrets and unnecessary customer data.

If the canary fails, stop rollout and diagnose from evidence rather than repeating the update blindly. In DispatchDesk's incident, the package query shows the new library, but process inspection indicates the worker has not restarted. Restarting it then fails because a recent unit override references an environment file removed during deployment. The failed assumption was that “package updated” meant “process repaired.” The operator should compare the active unit with version-controlled configuration, restore the missing file or roll back the configuration change, then restart one worker and verify queue drain, error rate and duplicate handling before restoring capacity. If the patched package itself causes the regression, use the vendor-supported rollback or roll back to a known-good host image while keeping the vulnerable version isolated from untrusted traffic; record the temporary exposure owner and deadline. Never restore a compromised machine image as a trusted baseline without investigating persistence and credentials.

Routine automation can reduce delay, but it must preserve observability and control. Ubuntu's `unattended-upgrades` can apply selected origins daily; review logs under `/var/log/unattended-upgrades/`, allowed origins, service restart behavior and reboot policy. RHEL's documented `dnf-automatic-install.timer` can install updates using the configured `upgrade_type`; enabling it changes package state without a human at the console, so monitor transaction results and define reboot handling. A timer being active proves scheduling, not successful installation or remediation. For either distribution, automatic patching should report hosts that failed, fell behind, were excluded or require restart. For a fleet, use configuration management or a fleet tool to enforce policy and produce a host-by-host view; a shell loop over SSH is not a durable compliance system.

Patch management also needs exception management. A service owner may need to delay an update because a vendor application has a compatibility constraint. Record the package and affected hosts, reason, compensating controls, approver, review date and expiry. Reduce exposure while delayed, for example by removing public reachability or isolating a vulnerable service, and schedule a retest. “Held until further notice” creates permanent risk through administrative neglect. Reassess when the vendor publishes a fix, the host role changes or the exception expires.

Exercises:

1. A public Ubuntu host reports no pending APT upgrades, but the worker's process has been running for 90 days. What evidence distinguishes patched disk files from a remediated process, and what service interruption must be planned?
2. A Fedora canary succeeds, while a RHEL 9 node shows a security advisory update available. Which facts must be checked before choosing a DNF command, and why is Fedora's result insufficient evidence for the RHEL host?
3. A RHEL host fails its health check after a security update. Describe the stop condition, diagnostic evidence, rollback decision and temporary-risk record you would require.

Answer guidance: compare distro/release and installed package evidence, inspect the process/service restart requirement, and verify application health after a controlled restart or reboot. For RHEL, confirm subscription/repository availability and advisory applicability; `dnf update --security` is advisory-scoped while a plain `dnf update` includes all available updates. Fedora's repository state, lifecycle and test result do not establish RHEL behavior. Stop the rollout, preserve package and service logs, identify whether the failure is package or configuration related, restore a known-good supported state, and document any vulnerable version still exposed with a named owner and deadline.

Review questions:

- Why does an installed package version not always prove that a running service uses the patched code?
- Which host controls depend on distribution policy, and which require application or cloud-level evidence?
- What makes an update exception temporary and reviewable?

Takeaways:

- Reduce host attack surface from an inventory of roles, identities, listeners and dependencies.
- Treat Ubuntu, Fedora and RHEL as distinct release and package-management targets.
- Verify package state, process restart or reboot, and application health before claiming remediation.
- Roll out in rings, stop on defined failures, preserve recovery access and evidence, and expire exceptions.

## Sources checked 2026-10-04

- [Ubuntu Server: Automatic updates](https://ubuntu.com/server/docs/how-to/software/automatic-updates/) — APT timers, allowed origins, unattended-upgrades, restart and fleet-management caveats.
- [Ubuntu Server: Security suggestions](https://ubuntu.com/server/docs/explanation/security/security_suggestions/) — baseline update, access-control and network guidance.
- [Red Hat Enterprise Linux 9: Installing security updates](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_and_monitoring_security_updates/installing-security-updates_managing-and-monitoring-security-updates) — subscription prerequisites, advisory-scoped updates, automatic-update timer and restart inspection.
- [Red Hat Enterprise Linux 9: Security hardening](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html-single/security_hardening/index) — minimal package selection and post-install hardening context.
- [Red Hat Enterprise Linux 9: Using SELinux](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/index) — SELinux modes and policy administration.
- [DNF5 command reference](https://dnf5.readthedocs.io/en/stable/commands/advisory.8.html) — advisory subcommands and compatibility alias.
- [DNF5 Upgrade Command](https://dnf5.readthedocs.io/en/stable/commands/upgrade.8.html) — package upgrade transaction and `upgrade` command behavior.

The commands are documentation examples checked against the cited references on the listed date. No package transaction, host inspection, service restart, reboot, scanner run, backup restore or live incident exercise was performed.
