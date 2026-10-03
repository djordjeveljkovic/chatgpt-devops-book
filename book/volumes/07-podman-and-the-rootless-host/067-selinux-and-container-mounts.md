---
book: The Complete DevOps Engineering Book
volume: 7
volume_title: "Podman and the Rootless Host"
chapter: 67
title: "SELinux and Container Mounts"
slug: selinux-and-container-mounts
status: complete
summary: ../../_ai/chapter-summaries/067-selinux-and-container-mounts.md
---

# Chapter 67 — SELinux and Container Mounts

## Labels, shared and private relabeling

DispatchDesk's attachment directory has correct Unix ownership and mode bits. The container still receives permission denied on a Fedora or RHEL host. Its successful run on Ubuntu does not prove that the Fedora machine is broken. SELinux evaluates mandatory policy in addition to numeric credentials. The right repair restores the intended container access while preserving confinement.

Read [volume ownership](063-rootless-identity-and-volume-ownership.md) and [Quadlet integration](066-quadlet-and-systemd-integration.md) first. This chapter's label lab specifically targets an enforcing SELinux Fedora 44 or supported RHEL 9/10 disposable host. Run ordinary Podman commands as the owning account. Audit inspection may require a host administrator. Ubuntu 24.04 commonly uses AppArmor and gets a separate diagnosis path below; do not execute SELinux policy commands on it merely to follow a Fedora example.

SELinux labels include a type and, for container isolation, category information. Process and file labels participate in access decisions alongside the requested operation. Container policy allows appropriately labeled content to be accessed by the relevant confined process. Private category labeling further distinguishes unrelated containers. Names such as `container_t` and `container_file_t` help interpretation, but consult installed policy rather than manufacturing a complete label string from memory.

Podman's `:Z` suffix asks it to relabel a mount source privately for the container; `:z` supplies a shared container content label. The sharing choice must match actual consumers. Unrelated containers that need a common directory cannot both independently treat it as exclusively private. Containers in the same Podman pod can share relevant security labeling, so inspect the pod arrangement rather than assuming every member has unrelated categories. The [container SELinux policy manual](https://github.com/containers/container-selinux/blob/main/container_selinux.8) supplies policy context.

Relabeling changes real filesystem metadata and can traverse a large tree. Its consequences outlive the launch command. Do not relabel `/etc`, `/var`, or an entire home directory to solve a narrow service mount. A relabeled system directory can break another confined service. Use a dedicated source whose ownership and policy are part of the deployment contract. Read-only publication still needs correct labels; `ro` limits writes but does not bypass read authorization.

## A bounded mount experiment

Inspect the host mode before creating anything:

```bash
getenforce
id
podman --remote=false info
```

If SELinux is disabled or permissive, this lab cannot demonstrate an enforcing denial. Do not change a production host's enforcement mode to manufacture one. Obtain a disposable enforcing environment instead. Confirm the engine reports SELinux support and record the package/policy versions through the host's normal inventory.

Create one dedicated directory and file, then inspect both labels and ordinary permissions:

```bash
lab_dir="$HOME/dd-selinux-67"
mkdir -m 700 "$lab_dir"
printf 'attachment label fixture\n' > "$lab_dir/marker"
ls -Zd "$lab_dir"
ls -Zl "$lab_dir/marker"
podman --remote=false run --name dd-unlabeled-67 \
  --volume "$lab_dir:/data:ro" \
  docker.io/library/busybox:1.37 cat /data/marker
```

The lab uses container root under default rootless mapping so ordinary access to the account-owned mode-700 source can work, isolating the intended label question. The unrelabeled mount may be denied on an enforcing host because home-directory content is not labeled for confined container access. Actual policy can differ; record the outcome and label evidence rather than declaring every home directory must fail.

Keep the failed object so its logs and inspect output remain available:

```bash
podman --remote=false logs dd-unlabeled-67
podman --remote=false inspect dd-unlabeled-67
```

An error printed by `cat` is not itself proof of SELinux involvement. It can result from DAC, an absent path or an unexpected mount. Compare host path, mount source, mode bits, mapping and label evidence. If an audit denial matches the operation and timestamp, the investigation becomes specific.

## Diagnosing AVC denials

On Fedora/RHEL with the audit tools installed and appropriate administrator access:

```bash
sudo ausearch -m AVC,USER_AVC -ts recent
sudo journalctl -k --since '10 minutes ago' --no-pager
```

Audit availability, logging configuration and privileges affect what these commands show. Narrow the time range and correlate the executable, path, process context, target context and denied permission. Preserve relevant records privately; they can reveal sensitive filenames. A denial from an unrelated process at the same time is not evidence about this container. The [RHEL troubleshooting guide](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/troubleshooting-problems-related-to-selinux_using-selinux) explains the audit workflow.

An AVC says policy denied an operation under particular contexts. It does not say the application should have been allowed. A compromised container probing the account's SSH files would also produce denials. Check the requested business behavior and intended source before deciding that policy needs changing. A broad automatically generated `audit2allow` module can legitimize unintended access and make future incidents harder to distinguish.

If no matching AVC appears, continue the ordinary checks. SELinux silence can reflect disabled auditing or suppressed messages, but it can also mean the denial occurred earlier in DAC. Investigate rather than turning off policy to test everything at once. Confirm a read-only mount is not being used for writes and that parent directories grant search permission to the mapped host identity.

## Fixing mounts without disabling policy

Remove only the retained test object and create a new one with a private label request:

```bash
podman --remote=false rm dd-unlabeled-67
podman --remote=false run --rm \
  --volume "$lab_dir:/data:ro,Z" \
  docker.io/library/busybox:1.37 cat /data/marker
ls -Zd "$lab_dir"
ls -Zl "$lab_dir/marker"
```

Expected acceptance combines successful read, label change on the dedicated source, and no matching denial for that read. A reader should also verify that unrelated paths remain outside the container's mount set. This demonstrates the intended contract without disabling host enforcement or container separation.

For two unrelated containers intentionally sharing content, choose `:z` instead and assess who can read or write it. Shared labeling widens the SELinux content boundary; it does not make Unix ownership irrelevant or create the mount in another container. Restrict the mount list and use `ro` for consumers that only need reads. A backup helper reading attachments may justify sharing, while two application versions writing a database directory concurrently do not become safe because a label permits it.

For long-lived administrator-managed paths, persistent file-context policy may be appropriate. `semanage fcontext` records a policy mapping and `restorecon` applies expected contexts. Those are host policy changes requiring knowledge of installed container policy and path ownership. Choose them when a static host directory has a documented role, rather than repeatedly issuing `chcon` that can be undone by relabeling. Dynamic private categories chosen at launch are a different mechanism; do not substitute a generic static type rule and assume identical isolation.

After a data restore, validate labels as well as owners and content. Some transfer methods omit security metadata; others faithfully preserve categories meaningful only in the old deployment. Reapply the approved host/engine labeling strategy and verify access through the restored service. A checksummed archive proves bytes survived, not that the new process can read them under current policy.

## Ubuntu and AppArmor diagnosis

Ubuntu's common mandatory-security model is AppArmor, which uses profiles and path-based access rules rather than SELinux file categories. Inspect the active profiles and kernel logs under administrator authorization:

```bash
sudo aa-status
sudo journalctl -k --since '10 minutes ago' --no-pager
```

Look for AppArmor denials associated with the relevant process/profile and requested path. Check that the engine's selected confinement profile exists and is compatible with the workload. `:Z` cannot repair an AppArmor rule. The [Ubuntu AppArmor guide](https://ubuntu.com/server/docs/how-to/security/apparmor/) describes profile management and diagnosis.

The migration lesson is to preserve security intent across distributions while implementing it through the actual local model. SELinux rules, AppArmor profiles and Unix ownership are not interchangeable files to copy. A service that works unconfined on Ubuntu has not passed confinement acceptance on either distribution. Avoid changing to `--privileged` or an unconfined profile as the final repair for a routine bind mount.

## Incident and cleanup

Suppose a replacement container privately relabels a directory used by an older unrelated container. The older instance suddenly loses access. The failed assumption was that both could own private categories for the same source. Stop writers if consistency requires it, preserve label evidence, decide whether concurrent sharing is intended, and recreate with the approved shared or separate-source design. If concurrent writes are unsafe, resolve the deployment sequencing instead of broadening the label.

For the dedicated fixture, cleanup removes its single file and directory:

```bash
rm -- "$lab_dir/marker"
rmdir -- "$lab_dir"
```

On a non-disposable path, removing a container does not restore original labels automatically. A rollback must include the approved host policy and any prior labels where appropriate. This lab avoids that complexity by using a new dedicated source.

## Exercises and review questions

1. A correct owner still gets permission denied. List evidence that would distinguish DAC, read-only mount and SELinux. **Guidance:** effective mapping, mode/ACL and parent access, inspected mount options, matching AVC contexts and timestamps.
2. Two unrelated containers need read-only common content. Choose a mount strategy. **Guidance:** explicit shared source with `ro,z` where SELinux applies, correct DAC, and no unintended mounts; private relabeling can revoke the other instance's access.
3. A restored archive passes its checksum but the service cannot read it. **Guidance:** verify owners, label policy/categories, path availability and the service's actual namespace.
4. Why is an Ubuntu success insufficient Fedora acceptance? **Guidance:** AppArmor and SELinux enforce different models and policy configurations.

## Takeaways and further reading

Treat label policy as a separate access decision and repair the intended mount, not the host's enforcement mode. Continue with [Buildah and Skopeo](068-buildah-and-skopeo-workflows.md).

Official container-selinux, RHEL SELinux troubleshooting and Ubuntu AppArmor documentation were inspected 2026-10-03. No enforcement mode, label, profile, policy or mount was changed by the author.
