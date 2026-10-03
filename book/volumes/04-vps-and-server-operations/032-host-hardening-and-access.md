---
book: The Complete DevOps Engineering Book
volume: 4
volume_title: "VPS and Server Operations"
chapter: 32
title: "Host Hardening and Access"
slug: host-hardening-and-access
status: draft
summary: ../../_ai/chapter-summaries/032-host-hardening-and-access.md
---

# Chapter 32 — Host Hardening and Access

## Why this matters

Harbor's new VPS accepts SSH, runs DispatchDesk and stores order data. A weak login, unpatched service or public database listener can turn a routine outage into an incident. Hardening reduces unnecessary access and defines how operators retain control when a change fails. A single checklist cannot secure every host; choices depend on the threat, data, provider and recovery path.

This chapter builds on the first-boot process in [Chapter 31](031-choosing-and-provisioning-a-vps.md). It covers identities, updates, SSH, mandatory access control and exposed services. Commands that change host access can lock out a remote operator. Review the rollback and console path before applying them.

## Administrative identities and updates

Use individual human accounts for administration, with named ownership and auditable elevation. Avoid sharing a root password or a common private SSH key. Keep a break-glass identity controlled separately, monitor its use and test the recovery procedure. Give application processes dedicated non-login service accounts and only the filesystem and network access they need.

`sudo` can authorize a user to run selected commands as root while recording the invoking identity. Review the effective policy with `sudo -l`; membership in an administrative group is broad privilege. Prefer an established organization policy over a hand-written command list, because restricting a command by name can still permit access through its arguments or environment. Remove privileges promptly when responsibilities change.

Keep the operating system on a supported release and install security updates on a planned cadence. On Ubuntu, inspect whether `unattended-upgrades` is enabled and which origins it installs; recent security updates can trigger a reboot depending on policy. Test application compatibility, maintain a maintenance window for required restarts and monitor whether updates succeeded. [Ubuntu automatic updates guide](https://ubuntu.com/server/docs/how-to/software/automatic-updates/).

On Fedora, review the current release lifecycle and upgrade path; Fedora releases are not interchangeable with RHEL support lifecycles. For subscribed RHEL systems, verify repository entitlement and the supported minor-release policy. Ubuntu's interactive package workflow uses APT, while Fedora and RHEL use DNF. A manual update can alter many packages and require a reboot:

```bash
sudo apt update
sudo apt upgrade
```

```bash
sudo dnf upgrade --refresh
```

Run the appropriate pair on its intended distribution during a prepared maintenance window. `apt update` refreshes package metadata; `apt upgrade` applies available upgrades subject to APT's handling rules. `dnf upgrade --refresh` refreshes repository metadata and upgrades packages. Neither command alone confirms that the service remained healthy after an update. Review the transaction, scheduled reboots, service status, application checks and rollback options. RHEL commands require configured repositories and appropriate subscription access. [RHEL DNF documentation](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_software_with_the_dnf_tool/).

Unattended security updates trade manual scheduling for autonomous change. They can be appropriate when the team monitors results, understands reboot behavior and can recover the service. They are risky when no one owns alerts or when a critical workload cannot restart without coordination. Freezing all updates also accumulates exposure and makes the eventual change larger. Choose an update policy with an owner, validation signal, maintenance response and supported rollback.

## Reduce exposure while preserving recovery

Inventory the listeners and provider rules before closing access. A host's `ss -lntup` output shows local TCP/UDP listeners where permissions allow; it does not include provider network policy or service paths in other namespaces. Remove unused services and block administrative ports at both provider and host boundaries where possible. Keep SSH source access narrow, use a stable management network or bastion, and document how an operator can recover access.

The following OpenSSH settings illustrate a key-only administrative policy after you have verified key access and provider console recovery. Save the lines in a deliberately early drop-in only after checking the include order and cloud-init-managed files for that image:

```text
PermitRootLogin no
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
```

`PermitRootLogin no` prevents direct root login over SSH while preserving root through an approved local privilege path. `PubkeyAuthentication yes` enables public-key authentication. The password and keyboard-interactive settings disable those SSH authentication paths; they do not remove local passwords or other identity systems. Centralized SSH or PAM policy can add constraints, so inspect the effective configuration and intended access methods first.

Before editing, open a second SSH session and confirm the new user's key works. Validate syntax before reload, then inspect the effective settings:

```bash
sudo sshd -t
sudo sshd -T | rg '^(permitrootlogin|pubkeyauthentication|passwordauthentication|kbdinteractiveauthentication) '
```

If `rg` is unavailable, use `grep -E` with the same expression. `sshd -t` checks configuration parsing; `sshd -T` prints effective values for a basic context but may need `-C` parameters to evaluate conditional `Match` blocks. On a second terminal, establish a fresh key-authenticated session before ending the original. If access fails, restore the previous known-good configuration from the provider console. Ubuntu's OpenSSH server can use drop-ins under `/etc/ssh/sshd_config.d/`; check the exact include order and effective values rather than assuming a filename wins. [Ubuntu OpenSSH server guide](https://ubuntu.com/server/docs/how-to/security/openssh-server/).

Reload the server only after syntax and access paths are verified. Ubuntu commonly names the service `ssh`; Fedora and RHEL commonly use `sshd`. Confirm with `systemctl status ssh.service` or `systemctl status sshd.service` on the actual host before selecting the reload target. Keep the old session open until a new login succeeds. Do not paste a provider's default SSH configuration into a different image without checking its managed snippets.

Use the host's mandatory access control system in its intended mode. Fedora and RHEL generally ship with SELinux enforcing; inspect `getenforce` and investigate denials through audit logs and labels. Correct a mislabeled application directory or create a narrowly scoped policy using supported tools. Disabling SELinux removes a major enforcement boundary and can conceal the actual deployment error. Ubuntu commonly uses AppArmor; inspect loaded profiles and service denials with its tools. SELinux policy and AppArmor profiles are different models; do not copy commands between them. [RHEL SELinux introduction](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/getting-started-with-selinux_using-selinux).

Protect secrets in files and logs. Restrict private keys, database credentials, cloud metadata access and environment files to the identities that need them. Rotate credentials after suspected exposure and plan propagation to every dependent service. File permissions cannot protect a credential from a compromised process that legitimately reads it, so minimize both process privileges and credential lifetime.

## An Ubuntu and Fedora/RHEL baseline

A practical baseline has explicit ownership for account lifecycle, patching, firewall, remote access, logging, time synchronization, backups and incident contacts. On Ubuntu, preserve its AppArmor and UFW management. On Fedora/RHEL, preserve SELinux and firewalld. Record which firewall manager owns the policy; do not introduce direct nftables rules alongside an existing manager as a substitute for learning its configuration.

Before enabling a host firewall remotely, confirm its default policy and add the narrow management source rule through the owning manager. Keep the provider firewall and host firewall inventories aligned. Chapter 27 covers runtime versus persistent firewall rules and access-safe changes. A port need only be allowed at the boundaries required for the service; an application listener is not an instruction to publish it.

Set logging so an operator can answer who changed access, which update ran, when the service restarted and whether authentication failed. Protect and retain logs according to data policy, and send critical security events somewhere an attacker on the host cannot silently erase. Synchronize time through the approved service and monitor clock drift because timestamps underpin incident correlation and certificate validity.

Use the distribution's defaults as a starting point, not a substitute for review. Ubuntu's security guide recommends ordinary least-privilege accounts, updates, a firewall and SSH; RHEL supplies SELinux and firewalld workflows with their own policy conventions. A hardened server is a maintained system with tested restoration, rather than a collection of one-time settings. [Ubuntu security suggestions](https://ubuntu.com/server/docs/explanation/security/security_suggestions/).

## Validate access and respond to lockout

A change disables SSH passwords but the intended public key is absent from the new administrator's account. Existing operators remain connected, but new logins fail. Do not close the live session or reboot. Confirm the target hostname and account, inspect `authorized_keys` ownership and permissions, and compare the installed public key's fingerprint with the controlled source. Check `sshd -t`, effective settings, authentication logs and the provider-side source restriction.

Use the independent console to restore a known-good access path or install the verified key. Re-establish a fresh SSH connection before ending the console or original session. Preserve root login policy, firewall source constraints and mandatory access control while correcting the identity issue. Record the failure cause and add a first-login validation to the provisioning process.

After routine hardening, verify the installed release, pending updates, active listeners, firewall manager state, access from an approved operator path, mandatory access control mode, time synchronization, log forwarding and backup job status. A syntax check cannot prove that another team can recover access, and a successful SSH login cannot prove that all unwanted ports are blocked. Keep evidence from each relevant control plane.

## Exercises, review questions and takeaways

1. Design a patch process for a single-VPS service. Guidance: name the owner, update source, maintenance window, reboot policy, application checks and recovery image or backup.
2. Plan a move to key-only SSH. Guidance: verify the new key in a second session, inspect effective daemon settings, preserve console access and constrain source networks.
3. A service fails after a file move on enforcing SELinux. Guidance: inspect labels and denial evidence before changing the security mode; DAC permissions and mandatory policy both apply.
4. Compare Ubuntu and Fedora/RHEL host controls. Guidance: preserve their different default MAC systems and firewall managers rather than treating the command syntax as interchangeable.

Review questions: Why can a valid `sshd -t` result still lead to lockout? What does automatic updating fail to guarantee? Which privileges does the application process need? Strong answers distinguish parse, access, service health and durable recovery evidence.

Reduce unnecessary access while keeping a tested path for the people who operate the host. Continue to [Chapter 33](033-disks-filesystems-and-mounts.md) to prepare persistent storage without risking the root filesystem.
