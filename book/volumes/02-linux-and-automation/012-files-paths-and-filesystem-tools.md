---
book: The Complete DevOps Engineering Book
volume: 2
volume_title: "Linux and Automation"
chapter: 12
title: "Files, Paths and Filesystem Tools"
slug: files-paths-and-filesystem-tools
status: complete
summary: ../../_ai/chapter-summaries/012-files-paths-and-filesystem-tools.md
---

# Chapter 12 — Files, Paths and Filesystem Tools

## Paths, inodes and directory entries

DispatchDesk writes a database to `dispatchdesk.sqlite3`. From one terminal the order appears; from another it does not. The two processes started in different working directories and opened different files with the same name. A filename is part of a path interpreted in an execution context, not a globally unique identity.

Read [The Shell and Command Execution](011-the-shell-and-command-execution.md) first. This chapter owns filesystem path and file-identity basics used by deployment and container chapters. The lab needs Bash and ordinary GNU tools on a writable Linux filesystem. It uses only disposable files under a newly created temporary directory and requires no administrator rights on Ubuntu, Fedora or RHEL.

An **absolute path** begins at the filesystem root, `/`. A **relative path** starts from the process's current working directory. The components `.` and `..` mean the current and parent directory during resolution. A mount can place another filesystem at a directory; the path hierarchy does not guarantee that all its files reside on the same device.

A directory associates names with filesystem objects. An **inode** contains or identifies metadata associated with an object, including type, ownership, mode and link count. The inode number is unique within its filesystem, not across all filesystems; compare device and inode together for identity. The [Linux inode manual](https://man7.org/linux/man-pages/man7/inode.7.html) describes these fields. A directory entry's name and the inode's identity are related but distinct.

A **hard link** is another name for the same object within the filesystem. Editing through either name changes the same content. A **symbolic link** is a separate object containing a path to another location. That target can be relative, can cross a filesystem boundary and can cease to exist. Inspecting the link itself differs from following it to the target.

These distinctions matter during releases. A `current` symbolic link can select a release directory, but an already running process may retain open resources from its prior release. Changing the link does not magically restart the process or migrate stored state. Similarly, removing a pathname need not immediately reclaim an object that a process still holds open.

Timestamps have distinct meanings. `mtime` concerns content modification; `ctime` concerns inode status changes and is not a generic creation timestamp. Birth time may be available depending on filesystem and interface. Access time is affected by mount policy and other behavior. A timestamp can support a timeline but cannot prove who performed a change or whether it was legitimate.

## See names and identity in a disposable lab

Run sequentially in one Bash terminal, from any initial directory:

```bash
files_lab=$(mktemp -d)
cd "$files_lab" || exit 1
printf '%s\n' 'accepted-order-17' > order.txt
ln -- order.txt order-hard.txt
ln -s -- order.txt order-link.txt
ls -li -- order.txt order-hard.txt order-link.txt
stat --printf='%n device=%d inode=%i links=%h type=%F\n' -- order.txt order-hard.txt order-link.txt
```

`ln` without `-s` creates the hard link. With `-s`, it creates a symbolic link whose stored target is `order.txt`, relative to the directory containing that link. `ls -l` displays metadata and `-i` displays inode numbers. GNU `stat --printf` selects an explicit display: `%n` names the path, `%d` the device, `%i` the inode, `%h` the link count and `%F` the type. The [stat manual](https://man7.org/linux/man-pages/man1/stat.1.html) defines these fields; exact output values depend on the local filesystem.

Expect the original and hard-link names to share a device/inode and report two links. The symbolic link has its own identity. Ordinary stat inspects the symbolic link here; `stat -L` follows it. Compare:

```bash
stat -L --printf='%n target-inode=%i type=%F\n' -- order-link.txt
printf '%s\n' 'updated-order-17' > order-hard.txt
cat -- order.txt
rm -- order.txt
cat -- order-hard.txt
cat -- order-link.txt
```

The overwrite through the hard link changes the original's content. Removing `order.txt` deliberately removes that name; the hard link still names the retained content. The symbolic link now points to a nonexistent name and its read should fail. The final failed read is an intended negative test, not a reason to recreate unrelated data. This lab does not delete a real order database.

Cleanup removes the remaining explicit names:

```bash
rm -- order-hard.txt order-link.txt
cd /tmp || exit 1
rmdir -- "$files_lab"
```

This is destructive to the lab content. `--` ends option parsing, and `rmdir` refuses unexpected nonempty contents. Preserve the variable until cleanup. A hard-link error can indicate different filesystems, permissions or a filesystem restriction; this lab keeps all names in one new directory to avoid an intentional cross-device operation.

## Finding and inspecting files

Choose a search root before choosing a pattern. Searching `/` when the intended scope is one release tree can generate irrelevant permission errors, cross mounted filesystems and take considerable time. For a repository, `rg --files` is often an efficient initial inventory; its ignore and hidden-file defaults must fit the question. For filesystem predicates, find is the more direct tool.

Assume `./releases` is an existing, intentionally selected directory:

```bash
find ./releases -type f -name '*.json' -print
```

Run as an ordinary user in its parent directory. `-type f` selects regular files, the quoted `-name` pattern is interpreted by find and `-print` emits selected paths. Default find does not follow every symbolic link it encounters; changing link traversal changes scope. The [find manual](https://man7.org/linux/man-pages/man1/find.1.html) explains traversal and expression behavior. A denied directory means the result is incomplete, not proof that no matching file exists there.

For automatic handoff of filenames, ordinary newline separation is ambiguous when a name itself contains a newline. `find ... -print0` emits a null-delimited stream, and a compatible `xargs -0` or carefully written reader preserves names. An even simpler way to apply a known program to found names is find's argument-building form:

```bash
find ./releases -type f -name 'manifest.json' -exec stat -- {} +
```

The `{}` placeholder expands to selected path arguments; `+` batches them. It does not concatenate the filenames into shell source. The program is stat, so this command inspects rather than changes files. Do not replace it with a deletion action until the scope, link behavior and retention decision are established. [Text Processing](013-text-processing-and-pipelines.md) covers safe stream handling further.

Use metadata, content and allocation evidence for different questions. `file` can detect that a purported archive is an HTML error page. `stat` shows object metadata. `du` estimates allocated space under a path, while `df` reports filesystem capacity. A sparse file can have a large logical size but fewer allocated blocks. Permission gaps and mount crossings can change du's result. Do not infer database correctness from any one of these measurements.

## Safe copy, move and deletion workflows

A copy creates another object with selected content and metadata behavior. A move within one filesystem can rename an object; across filesystems it generally involves copying and then removing the source. Those operations have different failure and atomicity properties. The [GNU mv manual](https://man7.org/linux/man-pages/man1/mv.1.html) documents its behavior. Do not assume every move is an instantaneous rename just because the command is called mv.

For a nonsensitive single-file configuration change, retain prior state in an explicit unused backup path, create the new content separately, validate it and activate it deliberately. A same-filesystem rename can give readers a coherent path switch, but crash durability and application reload remain separate concerns. An application already holding an old file descriptor may continue reading the old object. [Service Lifecycles](016-systemd-and-service-lifecycles.md) explains how to coordinate activation with the process.

Preserving metadata deserves an explicit choice. Copying content alone may not retain ownership, ACLs, security labels or extended attributes as intended. Ubuntu's applicable AppArmor path policy and Fedora/RHEL's SELinux labels add access considerations beyond Unix mode bits. A copied database directory also needs a consistency procedure; copying live files does not become a valid database backup merely because permissions look correct.

Deletion removes names and can remove the last accessible reference to content. There is no universal undo. Recursive deletion widens scope to a tree, and broad patterns can select more than expected. Prefer explicit names for a disposable lab, preview relevant selection for larger maintenance, and retain a recoverable source when the service contract requires it. The inspection and deletion are still separate moments; in directories writable by untrusted processes, a race can change targets between them. Privileged automation needs a stronger design than a printed preview.

## The deleted log that still fills the disk

Harbor's disk is full. An engineer deletes a large active worker log, but free capacity barely changes. The worker still holds the file open and continues writing to the unlinked object. The name disappeared, yet the process's open reference keeps its storage allocated. The attempted cleanup also removed the ordinary pathname needed to inspect the evidence.

Diagnosis compares filesystem capacity with visible directory allocation, then checks the writing process's open descriptors through approved tools. A deleted-but-open file is one explanation for a df/du mismatch; mount layout, permissions and sparse files are others. The responder identifies the actual owner rather than restarting every service on the host.

Recovery uses the application's documented log-reopen or controlled restart behavior, preserving needed incident evidence first. Closing the final open reference allows reclamation when no other links remain. The team verifies disk headroom and new log output, then checks pending notification progress. A disk fix alone may leave work stalled or state uncertain.

The lasting design uses supported rotation and reopen procedures, bounds retention and reserves headroom away from authoritative data where appropriate. Replacing a log pathname and expecting every writer to follow it is an incomplete lifecycle assumption. The later [Journald and Loki chapter](../15-observability-and-telemetry/146-logs-with-journald-and-loki.md) provides another logging path with its own retention boundaries.

## Exercises and answer guidance

1. Why does a hard link survive deletion of the original name while a symbolic link may fail? They represent another name for the object versus a path lookup through a separate object. The original name is not privileged among hard links.
2. Two files have inode number123. Are they the same file? Not without filesystem/device identity; inode numbers are only filesystem-local. Even that observation must be interpreted at its recorded time.
3. Why can a move across mounts need extra free space? It may copy data before removing the source. A rename's assumptions do not cover the cross-filesystem path.
4. Find returns no matches and several permission errors. What can you conclude? No match was observed in accessible scope; the complete tree remains unknown. Do not erase errors to make the result look definitive.

## Review questions and takeaways

Which working directory resolves this path? Are you inspecting a link or its target? Does a copy retain the required metadata? Which filesystem contains the object? What holds the content alive after name removal? What evidence supports a deletion decision?

Treat pathnames, object identity and open references separately. Inspect scope before mutation, preserve needed metadata and avoid confusing file operations with application consistency. Continue with [Text Processing and Pipelines](013-text-processing-and-pipelines.md).

## Sources and verification

Linux inode and upstream GNU find/stat/mv manuals hosted by man7 were inspected on 2026-10-01; earlier cp/rm documentation supports the copy/removal discussion. No exact inode values are invented. The local link experiment was executed with GNU coreutils9.11: device/inode and two-link identity matched, write-through changed shared content, the hard link survived original-name removal and reading the dangling symbolic link failed. Temporary test state was removed. The deleted-open-file incident is fictional and was not executed. No real release, database or log was modified.
