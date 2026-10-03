# Chapter 32 continuation

Status: complete

## Written material
Administrative identities and sudo; Ubuntu APT vs Fedora/RHEL DNF patch workflow; update/reboot ownership; SSH key-only transition and effective-setting checks; host firewall/MAC controls; SELinux/AppArmor distinction; lockout diagnosis; exercises.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
Individual identity, least privilege, sudo elevation, patch cadence, unattended updates, SSH daemon include precedence, host firewall, SELinux label/policy, AppArmor profile, recovery console.

## Examples and cross-references
Separate APT and DNF command examples; OpenSSH setting block and parse/effective checks; links to Chapters 26, 27 and 31. Settings are not applied to this host.

## Open threads
Independent review; no host identities, package updates, SSH daemon or MAC policy changed. Audit SSH settings against target release and cloud-init defaults before use.

## Verification
Inspected Canonical Ubuntu server update and OpenSSH docs; Red Hat RHEL 9 DNF and SELinux docs on 2026-10-02. No host command with persistent side effects was executed. Commands remain guidance for a reader's intended distribution.
