# Independent review — Chapter 31

Reviewer: review_volume3_021_025 (independent reviewer, Volume 4 assignment)
Date: 2026-10-03
Reviewed body SHA256: 6c8c930461a4ceac91531e959f09108afdb89d2b7eb3abc2187922359f51d730

## Scope and findings

Read AI_AUTHORING_GUIDE.md, baseline, skeleton brief, manuscript and summary, plus prerequisite/canonical context from Chapters 10, 26–30 and preceding chapters in this batch. Checked prose, safety, commands, Linux differences, recovery, links and assessment requirements.

Reviewed workload assumptions and vCPU/headroom/storage tradeoffs, failure objective, cost completeness, console trust, image ownership, cloud-init frequency/schema, public-key placeholder, root-equivalent sudo, host-key validation, first-boot evidence and recovery. Provider-specific claims are deliberately deferred and no invented plan/price is asserted. Exercises have guidance. No material findings.

## Dated evidence and limitations

Canonical cloud-init users/groups module and schema inspected via upstream source on 2026-10-03 after ReadTheDocs returned HTTP 429. The illustrative user structure and schema keys are supported; placeholder is explicitly unusable until replaced. No cloud-init executable is installed, so no schema invocation or first boot was performed.

Primary sources inspected:

- https://raw.githubusercontent.com/canonical/cloud-init/main/cloudinit/config/cc_users_groups.py
- https://raw.githubusercontent.com/canonical/cloud-init/main/cloudinit/config/schemas/schema-cloud-config-v1.json

Scoped checker `python3 tools/check_book.py --chapters 31-35` passed on 2026-10-03: 1 YAML parse, 14 shell syntax blocks, 1,315 global local links, no errors/warnings. Parsing is not cloud-init schema or Nginx/systemd runtime validation. No Ubuntu/Fedora/RHEL VM matrix, provider build, paid resource, live recovery or production application test performed.

Verdict: approved
