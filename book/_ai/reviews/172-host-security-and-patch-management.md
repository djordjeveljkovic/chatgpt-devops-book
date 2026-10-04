# Independent review — Chapter 172

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: b418fbc63a31fcbe279b4255aecd287a478c7fee43d451589da934daf098d108

## Scope and findings

Read full current body/summary, Chapter 172 brief and authoring guide, with Chapter 171 threat-model context. Reviewed inspection/update flags, Ubuntu/Fedora/RHEL differences, mandatory access controls, restart/remediation evidence, maintenance failure and rollback, automation/exception policy, sources, assessment and links. No material technical finding; complete body is technically sound and approved.

ss -lntup selects listening TCP/UDP sockets with numeric addresses and process information subject to permissions. systemctl's service/running filter and enabled unit-file inventory are read-only and correctly distinguished from all reachable or socket-activated paths. APT refresh versus installed upgrade is correctly distinguished; proposed transactions remain interactive. DNF5 upgrade --refresh is valid for DNF5 hosts, with older Fedora interfaces explicitly conditioned on release. RHEL 9 dnf update --security and plain update distinctions match Red Hat documentation, as does needs-restarting process rather than unit output. The automatic-install timer applies configured upgrade_type and does not itself prove successful remediation. Ubuntu 24.04 default affected-service restart behavior is qualified by local configuration and criticality; reboot-required is checked rather than presumed.

AppArmor and SELinux are not treated as interchangeable configuration systems. Policy inspection/enforcement, file labels and audit evidence remain necessary; disabling policy is not prescribed as a repair. Subscription/repository claims are scoped to registered RHEL, rather than implicitly applying to compatible clones or Fedora. The scenario's compatible-host option does not assert Red Hat entitlement on clones.

The maintained process distinguishes installed files from a process still using old libraries. Canary stop criteria, out-of-band access, backup usability, configuration-versus-package diagnosis, restored EnvironmentFile configuration, controlled restart and application/queue/idempotency health make recovery inspectable. A vulnerable fallback needs isolation, owner and deadline; a compromised image is not automatically trusted. Evidence collection avoids secrets and automation/exception claims do not confuse scheduling with remediation. Exercises include substantive answer guidance, review questions and takeaways; no command execution result is fabricated.

Low optional observations:

- Opening paragraph and final paragraph of distro-differences section: make Chapter 171 and Chapter 173 actual relative links. Both are currently plain prose references, while the summary calls them links; authoring guide prefers clickable canonical/prerequisite references.
- Front matter currently says drafting, whereas summary says draft. Align status during coordinator maintenance; this review binds the complete body rather than status metadata.
- Sources: DNF5 advisory reference is valid background, but add the Upgrade Command reference for the actual upgrade --refresh example, so the direct command evidence is easier to trace.

## Primary evidence checked 2026-10-04

- [Ubuntu automatic updates](https://ubuntu.com/server/docs/how-to/software/automatic-updates/): origins/timers/logs, shared-library restart requirement, Ubuntu 24.04 needrestart defaults and exclusions.
- [RHEL 9 installing security updates](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_and_monitoring_security_updates/installing-security-updates_managing-and-monitoring-security-updates): registered-host prerequisites, security selection, process restart inspection and automatic-install timer/upgrade_type.
- [DNF5 upgrade command](https://dnf5.readthedocs.io/en/stable/commands/upgrade.8.html) and [DNF5 utility](https://dnf5.readthedocs.io/en/stable/dnf5.8.html): transaction semantics and refresh option.
- [RHEL 9 Using SELinux](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/index): enforcement modes/policy administration context.
- [ss manual](https://man7.org/linux/man-pages/man8/ss.8.html): exact inspection flags.

The attempted current upstream systemctl web manual retrieval returned an internal retrieval error; its conventional inspection flags were reviewed statically, not validated against a live host. No vendor support promise or exact current release number is asserted beyond explicit RHEL 9/Ubuntu 24.04 examples.

## Validation and limits

`python3 tools/check_book.py --chapters 172-172` passed four shell syntax checks and 1,466 global local links without warnings/errors (front-matter state drafting). Exact stripped-front-matter hash calculated using `tools.promote_reviewed.body_hash`. No package/index transaction, host listener/unit inventory, AppArmor/SELinux policy, advisory scanner, service restart, reboot, automatic timer, console access, backup restore or incident recovery executed. No distribution/release/repository/runtime matrix tested. Source checks and shell parsing cannot establish actual repository entitlement, patch applicability, process-library state or production remediation. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Inspected the two new relative chapter links, reordered DNF5 example and added direct Upgrade Command reference. Chapter 171 and 173 targets are valid and context remains accurate. `sudo dnf5 --refresh upgrade` places the documented global refresh option before its upgrade subcommand and preserves interactive transaction review. The direct upgrade source supports command behavior, alongside the earlier DNF5 utility reference for the global flag. All three earlier low observations are resolved; front matter and summary are aligned to revising during this refresh. No material issue introduced; approval remains.

Fresh body SHA256 from `tools.promote_reviewed.body_hash`: b418fbc63a31fcbe279b4255aecd287a478c7fee43d451589da934daf098d108. `python3 tools/check_book.py --chapters 172-172` passed four shell syntax checks and 1,468 global local links without warnings/errors. Earlier complete assessment, source evidence and host/runtime nonexecution limits, including the systemctl web-reference retrieval limit, remain applicable. Only this separate review record updated.

Verdict: approved
