# Independent review — Chapter 32

Reviewer: review_volume3_021_025 (independent reviewer, Volume 4 assignment)
Date: 2026-10-03
Reviewed body SHA256: 4f90af6a7661629150340663647a9bff65b0dbc96ffd972cc0c4ebae87ad84a0

## Scope and findings

Read AI_AUTHORING_GUIDE.md, baseline, skeleton brief, manuscript and summary, plus prerequisite/canonical context from Chapters 10, 26–30 and preceding chapters in this batch. Checked prose, safety, commands, Linux differences, recovery, links and assessment requirements.

Reviewed individual identity/sudo scope, APT versus DNF and subscription constraints, interactive update semantics, key-only SSH settings, first-value/include order qualification, Match-context checks, service-name differences, console recovery, SELinux/AppArmor distinction and firewall ownership. No material finding.

- Low, “Reduce exposure while preserving recovery”, SSH validation sequence: make the post-reload fresh-session test explicitly sequential in the prose; a fresh session before reload validates the old daemon policy. The chapter already instructs retaining the old session until a new login succeeds, so this is clarification rather than a blocker.

## Dated evidence and limitations

Official Ubuntu OpenSSH and automatic-update guidance and RHEL DNF guidance inspected on 2026-10-03. No package transaction, SSH file edit/reload, identity change, firewall mutation or MAC-policy change executed.

Primary sources inspected:

- https://ubuntu.com/server/docs/how-to/security/openssh-server/
- https://ubuntu.com/server/docs/how-to/software/automatic-updates/
- https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/managing_software_with_the_dnf_tool/

Scoped checker `python3 tools/check_book.py --chapters 31-35` passed on 2026-10-03: 1 YAML parse, 14 shell syntax blocks, 1,315 global local links, no errors/warnings. Parsing is not cloud-init schema or Nginx/systemd runtime validation. No Ubuntu/Fedora/RHEL VM matrix, provider build, paid resource, live recovery or production application test performed.

Verdict: approved
