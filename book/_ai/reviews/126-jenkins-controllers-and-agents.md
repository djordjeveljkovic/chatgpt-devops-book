# Independent re-review — Chapter 126

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: e964130886b58569f110f0648c9e602a65702592461e8a219bba3f61aec10b8a

## Scope and findings

Freshly read the complete current body against all prior findings. Hash matches suppliedc38010f94b9fb8c71bf7250c78282ddd06e387519f0afcc2b7c0c47c2cd96d30.

Both current remoting discussions now accurately state always-enabled Agent→Controller Access Control since2.326, rejection of unsafe requests and residual vulnerabilities/intentionally granted capability limits. Backup guidance separately preserves both master.key and hudson.util.Secret outside ordinary backups, explains custody/reintroduction and requires isolated restore testing. Exercise5 matches the corrected decrypting chain. All prior material findings are resolved; no remaining material finding in the full chapter.

Earlier substantive assessments remain applicable: controller0 executors, trust-separated agents and labels, credential-binding/code risks, plugin lifecycle and exact-version Java/distro guidance are coherent. Approval covers documented guidance, not measured host isolation or recovery.

## Dated primary-source evidence

Inspected on2026-10-04:

- [Controller isolation](https://www.jenkins.io/doc/book/security/controller-isolation/): built-in node filesystem privileges, executor0, separate identity alternative, always-enabled Agent→Controller control since2.326.
- [Credentials](https://www.jenkins.io/doc/book/security/credentials/): folder scope, encrypted-data/key custody and separately preserved decrypting material.
- [Backups](https://www.jenkins.io/doc/book/system-administration/backing-up/): consistent restore state and master.key preservation separately from ordinary backup.
- [Multibranch SCM credentials](https://www.jenkins.io/doc/book/security/securing-org-folders-and-multibranch-pipelines/): repository configuration/code trust and scan credential exposure.
- [Linux installation](https://www.jenkins.io/doc/book/installing/linux/), [Java support policy](https://www.jenkins.io/doc/book/platform-information/support-policy-java/): Java21+, deliberate release channels, distro repository/package/systemd and target-release compatibility.

## Validation and limits

`python3 tools/check_book.py --chapters 126-126` passed:1 draft chapter and1,396 global local links; no errors/warnings. No config/code blocks to parse. No Jenkins installation, controller/agent remoting test, credential operation, update, backup or restore executed. No Linux/Java runtime matrix performed. Prior primary sources remain documentation evidence and cannot establish actual security controls or recoverability. Only this review record changed.


## Fresh additions review — 2026-10-04

Scope: reviewed the newly added takeaways and Chapter128 gate/exercise corrections and Chapter130 predecessor mention against prior recorded review scope; no new full runtime review. Current body hash recomputed with tools.promote_reviewed.body_hash: 96cddf4ecb35d815c86308c5ae95859c951ed94f28265ea06fcf8f66f21e885b. All takeaway statements accurately summarize the chapter boundaries without introducing unsupported guarantees. Chapter130 predecessor explanation is accurate; a relative clickable link remains an optional editorial improvement. Existing documentation evidence and execution limits above remain applicable. `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses and 1,399 global local links; no errors/warnings. Only these separate review records changed.

## Final correction review — 2026-10-04

Final bounded refresh: all final hashes recomputed; takeaways remain accurate, Chapter128 remaining status sentence and Chapter130 clickable prerequisite link are resolved. Inspected all three added installation sequences against official Jenkins Linux guidance on 2026-10-04: Ubuntu Java21 and 2026 LTS signing key/signed-by repository, Fedora dnf and RHEL-family yum LTS RPM repository/dependencies, daemon reload, enable --now/status and journalctl are structurally correct. Java/repository availability and RHEL entitlement are qualified, host/privilege context is explicit, management exposure is restricted and MAC is preserved. Official guide includes optional full-system upgrade steps; omitting those does not invalidate these new-host installation examples. No package command or service operation executed. Source: https://www.jenkins.io/doc/book/installing/linux/. Scoped checker `python3 tools/check_book.py --chapters 121-130` passed: ten chapters, four YAML parses, three shell syntax checks and 1,400 global local links; no errors/warnings. Prior runtime/source limitations remain; this is a review of additions/fixes, not a new live-platform test. Only ten separate review records updated.

Verdict: approved
