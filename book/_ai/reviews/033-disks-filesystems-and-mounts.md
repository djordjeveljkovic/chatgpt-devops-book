# Independent review — Chapter 33

Reviewer: review_volume3_021_025 (independent reviewer, Volume 4 assignment)
Date: 2026-10-03
Reviewed body SHA256: 727a80d980ba87a7ecfde4367a46993f00b0e7bf800a5395aa5df78760c7e669

## Scope and findings

Read AI_AUTHORING_GUIDE.md, baseline, skeleton brief, manuscript and summary, plus prerequisite/canonical context from Chapters 10, 26–30 and preceding chapters in this batch. Checked prose, safety, commands, Linux differences, recovery, links and assessment requirements.

Reviewed device/partition/LVM/LUKS/filesystem/mount boundaries, UUID identity, fstab fields, required mount versus nofail, findmnt verification, provider-to-filesystem growth order, ext4 versus XFS grow/shrink semantics, block/inode/deleted-open accounting, latency limitations, destructive mkfs scope and recovery precautions. Commands are explicit alternatives and destructive paths are clearly fictional. Exercises contain answer guidance. No material finding.

- Low, “Persistent mounts and safe growth”, mount-point permissions: permissions on the bare mount-point directory do not determine ownership of the filesystem root after mounting. Add a post-mount ownership/mode check before allowing a runtime identity to write.
- Low, diagnostic blocks: identify package prerequisites for lsof/sysstat and filesystem tools on images lacking them.

## Dated evidence and limitations

Inspected resize2fs and xfs_growfs manuals and RHEL 9 filesystem guide on 2026-10-03. No block device, filesystem, fstab, mount, resize or repair operation performed.

Primary sources inspected:

- https://man7.org/linux/man-pages/man8/resize2fs.8.html
- https://man7.org/linux/man-pages/man8/xfs_growfs.8.html
- https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html-single/managing_file_systems/managing_file_systems

Scoped checker `python3 tools/check_book.py --chapters 31-35` passed on 2026-10-03: 1 YAML parse, 14 shell syntax blocks, 1,315 global local links, no errors/warnings. Parsing is not cloud-init schema or Nginx/systemd runtime validation. No Ubuntu/Fedora/RHEL VM matrix, provider build, paid resource, live recovery or production application test performed.

Verdict: approved
