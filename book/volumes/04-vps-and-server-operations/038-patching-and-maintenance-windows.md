---
book: The Complete DevOps Engineering Book
volume: 4
volume_title: "VPS and Server Operations"
chapter: 38
title: "Patching and Maintenance Windows"
slug: patching-and-maintenance-windows
status: draft
summary: ../../_ai/chapter-summaries/038-patching-and-maintenance-windows.md
---

# Chapter 38 — Patching and Maintenance Windows

## Maintenance is a production change

Operating-system updates repair security defects, fix bugs and change software that DispatchDesk depends on. A kernel or runtime update may require a reboot. A library update can affect several processes, a database package can change service behavior, and a configuration-file prompt can preserve an old setting that no longer fits. Treat patching as a planned change with a source of truth, a recovery path and post-change validation.

Harbor has one VPS, so rebooting removes every application and database process at once. Before the maintenance window, establish who is available, how to reach the provider console if SSH fails, how to restore service, what interruption the customer can expect and how long the change may take. Check the applicable support lifecycle, security notices and release notes. A maintenance window is not an excuse to delay an actively exploited vulnerability indefinitely; use the risk process to choose an expedited and rehearsed path.

Routine package updates within the installed distribution release differ from a release upgrade. Do not combine a change from one Ubuntu or RHEL major release to another with an ordinary patching window unless that broader migration has its own plan, test and rollback strategy. Fedora releases have a shorter support lifecycle and their own release-upgrade process. Verify current supported releases with the distribution's lifecycle information before planning.

## Build a pre-change record

Record the machine identity, operating-system release, current kernel, package sources, pending updates, free disk, service health, database backup age, application release and provider recovery access. Check whether the latest database backup has been verified and whether an operator can retrieve its key. Confirm that the application can be drained, that durable notification intent remains in PostgreSQL, and that the expected interruption is acceptable. Capture current listener and readiness evidence so you can compare after reboot.

Review the proposed package transaction. Identify packages added, upgraded, held back or removed; inspect repository changes and locally modified configuration. Ensure sufficient disk for download, package staging and a fallback kernel if the distribution retains one. A powered-off host, unattached recovery console or expired SSH key can turn a small update into an outage. Make sure the on-call operator has a second authenticated session before changing SSH or firewall packages.

On Ubuntu, refresh package metadata and inspect updates before applying a planned change:

```bash
sudo apt update
apt list --upgradable
sudo apt-get -s upgrade
```

The simulation is evidence about the proposed transaction at that moment; it does not reserve package versions or guarantee a later identical result. Ubuntu may phase some non-security updates, so packages can remain held temporarily. Do not force them through without understanding why. Security updates have a different phasing policy. For RHEL and Fedora systems using DNF, inspect the available transaction first:

```bash
sudo dnf check-update
sudo dnf upgrade --assumeno
```

`dnf check-update` can return a nonzero status when updates are available, so automation must interpret its documented exit behavior instead of treating every nonzero result as a network failure. Package metadata and repositories vary by release. Review removals and dependency changes before accepting an update. When policy requires staging, reproduce the transaction on a test host with the same release, repositories and application dependencies.

## Apply the planned update

For a simple Ubuntu package maintenance window, an operator may apply the reviewed transaction with `sudo apt upgrade`. On a DNF-based Fedora or RHEL host, `sudo dnf upgrade` applies available package updates. These commands are state-changing and should only run after the review, backup and access checks above. Keep a persistent console session or provider recovery path. Do not combine routine patching with unrelated config edits, database schema migrations or application releases; separating changes makes diagnosis clearer.

Package managers can prompt about locally changed configuration. Read the difference and decide whether to keep the local file or install the maintainer's version, then reconcile the file against current policy. Do not blindly accept one choice across all packages. Record the decision and verify service-specific syntax before restarting a daemon. Package completion can leave updated libraries on disk while old processes still hold old code in memory.

A service restart may be sufficient for some updates; a kernel update requires a boot into the new kernel before the running system benefits. Other updates may require reboot depending on changed components and distribution guidance. Reboot indicators are hints, not a substitute for package-specific documentation. Capture the current kernel before the change and confirm the running kernel after reboot. If the host uses a provider-managed kernel or custom modules, follow the provider and module vendor's supported process.

When a reboot is required, confirm DispatchDesk has a safe drain behavior, then schedule the reboot and allow system services to stop normally. A forced power cycle is a recovery action, not routine maintenance. If shutdown stalls, inspect the console and logs and follow the database's crash-recovery guidance when it comes back. Preserve diagnostic evidence before repeating a destructive or uncertain action.

## Validate after maintenance

After package work or reboot, verify the OS and kernel version, failed units, service state, listeners, disk and memory pressure, time synchronization and provider monitoring. Check system logs for boot, filesystem, SELinux/AppArmor and service errors. Confirm PostgreSQL recovery completed and Redis is reachable according to its intended role. Verify DispatchDesk health and readiness separately, then perform a synthetic order acceptance and retrieval in a controlled environment. Confirm its durable notification intent exists and no real external notification was triggered by the test.

Review the security update status again and verify that package repositories remain the intended ones. Compare latency, error rate, database connection count and queue depth against the pre-change baseline. Keep the previous application artifact and recovery material available. If the kernel or service fails, use the provider console to select a supported fallback kernel or restore the documented host state. An OS package downgrade can be incomplete or incompatible with data written by the newer version; prefer a tested rollback plan over assuming every update can be reversed by reinstalling an older RPM or deb.

## Automate only after the contract is clear

Automatic security updates can reduce patch delay, but unattended package installation changes a live machine. Decide which updates may install automatically, which require a maintenance window, how reboots are handled, who receives failure alerts and how changes are audited. Pinning every package indefinitely creates a different security risk. Use the distribution's supported tooling and test it on a representative host. A report that says “nothing to do” is not evidence that the host can reboot successfully or that DispatchDesk remains healthy.

Use a maintenance record with the planned time, risk, owner, backup verification, package transaction, configuration decisions, reboot requirement, test results and rollback steps. After the change, close the maintenance only when expected service behavior has been checked. If it failed, record the incident and keep the window open until an owner accepts the recovery state.

## Exercises and review questions

1. Compare `apt-get -s upgrade` and a real package transaction. Which information is useful, and what can still change before execution?
2. A kernel package installed successfully but the running kernel version did not change. What action remains, and how do you confirm the result?
3. Design a low-risk maintenance window for a single-host database application. Include console access, data backup, notification drain, validation and escalation.
4. An update restarts OpenSSH while you are connected. What access evidence should you establish before closing the maintenance window?

Patching is complete only when the host runs the intended packages and the service's important behavior has been checked. Chapter 39 adds a second server and shows why two machines require shared state, traffic management and a more careful failure model.

## Sources and verification

Ubuntu Server's official [APT and phased-updates](https://documentation.ubuntu.com/server/explanation/software/about-apt-upgrade-and-phased-updates/index.html) and [release-upgrade](https://documentation.ubuntu.com/server/how-to/software/upgrade-your-release/index.html) documentation, Red Hat's [RHEL 9 DNF guide](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_software_with_the_dnf_tool/index) and Fedora's [system-upgrade guidance](https://docs.fedoraproject.org/en-US/quick-docs/upgrading-fedora-offline/) were inspected on 2026-10-02. Commands that apply package changes were not run. Package versions, currently supported releases and reboot requirements must be checked for the target host. Independent review is pending.
