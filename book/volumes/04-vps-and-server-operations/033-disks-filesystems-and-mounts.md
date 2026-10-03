---
book: The Complete DevOps Engineering Book
volume: 4
volume_title: "VPS and Server Operations"
chapter: 33
title: "Disks, Filesystems and Mounts"
slug: disks-filesystems-and-mounts
status: draft
summary: ../../_ai/chapter-summaries/033-disks-filesystems-and-mounts.md
---

# Chapter 33 — Disks, Filesystems and Mounts

## Why this matters

DispatchDesk writes orders to a data volume mounted at `/srv/dispatchdesk`. A provider expands the virtual disk, but the filesystem still reports its old capacity. In a different incident, the root disk fills with logs and PostgreSQL cannot write its journal. A disk, partition, filesystem and mount are separate layers; expanding one does not guarantee the next layer has usable space.

This chapter follows those layers and shows how to inspect them before changing storage. The commands that create a partition table or filesystem can destroy data. Use a disposable VM and a confirmed empty device for those operations. Do not run the destructive examples on a production disk.

## Block devices, partitions and filesystems

A block device provides fixed-size addressable storage to Linux. It can be a provider volume, local NVMe device, virtual disk, RAID device, logical volume or encrypted mapping. Names such as `/dev/vda`, `/dev/sdb` and `/dev/nvme1n1` depend on platform and discovery order. A name copied from another host is not proof that it identifies the same disk.

A partition table divides a whole disk into regions. GPT is common on modern Linux systems; the partition entries map ranges of sectors to partition devices such as `/dev/vda1`. Logical volume management can add another mapping layer between a disk, a physical volume, a volume group, a logical volume and the filesystem. LUKS encryption can also place a mapped device between the block volume and filesystem. Trace the actual stack before selecting a resize tool.

A filesystem manages directories, names, metadata and allocation within a block device or logical volume. ext4 and XFS are common Linux choices with different tools and resize capabilities. RHEL 9 recommends XFS as a general default for its workload profile and notes that it cannot shrink; ext4 can shrink offline. Measure the workload and verify the distribution's support policy rather than choosing from a universal performance slogan. [RHEL file-system guidance](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html-single/managing_file_systems/managing_file_systems).

A filesystem becomes part of a directory tree when mounted. `/` is the root filesystem; `/var`, `/home` and `/srv` may be separate mounts or directories on that root. `df` reports space available to mounted filesystems, while `lsblk` describes devices and their visible relationships. A mount can hide files that already exist in its mount-point directory. If a data volume fails to mount, an application that writes to the bare directory may fill the root disk with data meant for the volume.

Inspect the device and mount layers as an ordinary user where permissions allow:

```bash
lsblk --output NAME,PATH,SIZE,TYPE,FSTYPE,UUID,MOUNTPOINTS
findmnt --target /srv/dispatchdesk
findmnt --fstab
blkid
```

`lsblk` reads the kernel and device database; recently changed devices may require a refreshed udev view. `findmnt --target` identifies the filesystem that contains the path. `findmnt --fstab` inspects configured mount entries, not proof they mounted successfully. `blkid` reports recognized filesystem identifiers; a device path or UUID is still not a substitute for verifying its provider identity and contents. [lsblk manual](https://man7.org/linux/man-pages/man8/lsblk.8.html), [findmnt manual](https://man7.org/linux/man-pages/man8/findmnt.8.html).

## Persistent mounts and safe growth

For a stable data volume, mount by filesystem UUID rather than a discovery-order name such as `/dev/sdb1`. First inspect the UUID and file-system type, create an intended mount point, and record a backup copy of `/etc/fstab`. An ext4 entry for a confirmed device could take this form:

```fstab
UUID=REPLACE_WITH_VERIFIED_UUID /srv/dispatchdesk ext4 defaults 0 2
```

Replace the placeholder with the UUID read from the actual device. For XFS, use `xfs` and normally set the final fsck pass field to `0`; XFS recovery uses its own tools and does not use the ext-family boot-time check in the same way. The sixth field controls filesystem-check ordering on boot. Consult the installed `fstab(5)` and mount documentation for local systemd behavior.

`nofail` can let boot continue when an optional disk is absent, but it can also let an application write into the underlying empty mount-point directory. A required database volume should generally cause its service to wait for or fail on a missing mount, not silently start against the root filesystem. Configure the service dependency, such as systemd `RequiresMountsFor=/srv/dispatchdesk`, and verify the missing-device case in a disposable VM. Keep provider-specific mount behavior in its supported configuration tool when one owns it.

Before applying a new fstab entry, create the mount point with the intended owner and mode, check the table, reload systemd's generated mount units, and mount only the named target:

```bash
sudo findmnt --verify --verbose
sudo systemctl daemon-reload
sudo mount /srv/dispatchdesk
findmnt --target /srv/dispatchdesk
```

The first command verifies configuration syntax and references; it does not prove the selected disk contains the expected data. `mount` changes the live mount tree and requires privilege. If verification reports an issue, correct the entry before rebooting. To roll back, restore the saved fstab and unmount the specific volume when no process is using it. Do not use `umount -l` as a routine way to hide a busy filesystem.

Growing a filesystem starts outside the guest when the provider offers a resizable virtual volume. Confirm a recent independent backup and the exact resource ID, request the provider-side expansion, then inspect the new guest-visible size. This provider operation can incur storage charges and is not easily reversed; shrinking the virtual device later may be unsupported or may destroy data.

Next expand any partition or logical volume that limits the filesystem, and only then expand the filesystem. A typical simple partition layout may use `growpart`; an LVM layout needs its physical and logical volumes extended with LVM tools. Inspect `lsblk`, `pvs`, `vgs`, `lvs` and `findmnt` first. Never infer the root device name from an example. If the root filesystem is directly on a partition, the sequence may include a partition-growth tool followed by the correct filesystem tool. Cloud-init can also grow a configured partition on first boot; confirm its behavior before manually applying the same resize.

For an ext4 filesystem with already expanded backing storage, `resize2fs` can often grow the mounted filesystem. XFS must be mounted to grow and uses its mount point:

```bash
sudo resize2fs /dev/vda1
sudo xfs_growfs /srv/dispatchdesk
```

These are alternatives, not commands to run in sequence. Replace the device or mount point only after verifying that the filesystem type, partition and enlarged backing device match. The XFS example grows the filesystem mounted at `/srv/dispatchdesk`; it does not resize the provider volume or partition. XFS cannot be shrunk. [RHEL XFS procedure](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html-single/managing_file_systems/managing_file_systems) and [resize2fs manual](https://man7.org/linux/man-pages/man8/resize2fs.8.html).

## Diagnose capacity, inode and I/O failures

Check both free blocks and free inodes. A filesystem can reject new files while `df -h` still shows space if its inode capacity is exhausted:

```bash
df -hT
df -ih
sudo du -xhd1 /var | sort -h
```

`df -hT` shows human-readable block capacity and filesystem type; `df -ih` shows inode use. `du -xhd1` summarizes one directory level while staying on the same filesystem, and needs privilege to include protected directories. `sort -h` orders human-readable sizes. These commands identify large allocated directory trees but can be slow and may not count deleted files still held open by a process.

If `df` reports high use while `du` cannot find the space, inspect deleted-open files with an approved tool such as `lsof +L1`, inspect snapshots/reserved blocks, and compare mount namespaces. Restart or signal a process only through its safe service procedure after identifying the open descriptor; an abrupt kill can lose application work. Small-file workloads can exhaust inodes before bytes. A database or mail queue may create many small files even when each file is tiny.

Separate application growth from logs, package caches, temporary files and database WAL. Logs can be rotated or retained according to an approved policy; deleting an active log file may not release space while the process holds it open. Never remove PostgreSQL WAL, filesystem metadata or unknown files to make a graph look green. Move or archive data through the owning service and validate the result.

Storage latency and errors need more than a capacity check. Use available telemetry such as [`iostat`](https://man7.org/linux/man-pages/man1/iostat.1.html) with `iostat -xz 1 5`, `vmstat 1 5`, kernel journal messages and provider volume metrics to compare queueing, throughput, I/O wait and device errors over time. Those `iostat` fields depend on the installed sysstat version and provider device model; a high utilization percentage is not a universal saturation threshold for every virtual disk. Correlate the storage measurements with application latency and database waits.

## Recover a full or failed filesystem

Harbor sees database writes failing because `/var` is full. Responders first confirm which filesystem contains the database path, whether the problem is block or inode exhaustion, and whether writes are still failing. They preserve logs and database state, contain nonessential work, and identify the directory or open file responsible. They do not start with a larger disk or a broad `rm` command.

If growth is expected and the provider supports expansion, verify the independent backup and restore point, expand the virtual volume, then check each intervening partition/LVM/encryption layer and the filesystem type before extending. Monitor the operation, verify the new mounted size and perform a database write/read check. If the disk reports I/O errors rather than ordinary capacity exhaustion, stop mutation and follow the provider's data-recovery process; filesystem repair on a failing device can make recovery harder.

When creating a filesystem on a new empty partition in a disposable VM, the `mkfs` step initializes filesystem metadata. It destroys any previous filesystem and data on the selected partition. Confirm the device by size, parent disk, serial or provider volume ID and current `lsblk -f` output before running it. For example, on a confirmed empty lab partition only:

```bash
sudo mkfs.ext4 /dev/vdb1
sudo mkdir -p /srv/lab-data
sudo mount /dev/vdb1 /srv/lab-data
findmnt --target /srv/lab-data
df -hT /srv/lab-data
sudo umount /srv/lab-data
```

`/dev/vdb1` is fictional and must not be copied without identifying a disposable partition. `mkfs.ext4` overwrites filesystem metadata; the next commands create a mount point, attach the new filesystem, verify the mount and then unmount it. Cleanup after unmount can remove the lab mount-point directory only if it is empty and was created for this exercise. This lab does not alter a persistent mount table.

A filesystem repair tool is not a generic disk-full cleanup command. For ext4, `e2fsck` normally requires an unmounted filesystem; XFS uses `xfs_repair` under its documented recovery procedure. Stop writers, preserve a volume snapshot when appropriate and follow the distribution/provider recovery guide. Do not run checks against a mounted production filesystem just because an error appeared in the application log.

## Exercises, review questions and takeaways

1. Trace a sample device stack from provider volume to mount point. Guidance: include disk, partition, optional LUKS/LVM layers, filesystem UUID/type and the service path.
2. A provider says a volume was resized, but `df` is unchanged. Guidance: inspect the guest device size, partition/LVM allocation, filesystem type and mount before choosing the next expansion step.
3. Compare `df -h`, `df -i` and `du`. Guidance: bytes, inodes and directory allocation answer different questions; deleted-open files add another boundary.
4. Review the fstab entry for a required database volume. Guidance: assess UUID, type, fsck fields, boot failure behavior and the service's dependency on the mount.

Review questions: Why is `/dev/sdb1` a fragile persistent identifier? What layer does `resize2fs` change? Why can a filesystem fill while a directory scan looks small? Strong answers distinguish device identity, partition/container, filesystem and open-file accounting.

Verify the storage stack before every change, and grow each layer in order only after preserving a recovery point. Continue to [Chapter 34](034-deploying-a-service-with-systemd.md) to bind the application lifecycle to its persistent configuration and data paths.
