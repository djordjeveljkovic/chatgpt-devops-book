---
book: The Complete DevOps Engineering Book
volume: 2
volume_title: "Linux and Automation"
chapter: 14
title: "Users, Groups and Permissions"
slug: users-groups-and-permissions
status: complete
summary: ../../_ai/chapter-summaries/014-users-groups-and-permissions.md
---

# Chapter 14 — Users, Groups and Permissions

## Why this matters

DispatchDesk needs to write its database and notification state, read its configuration, and execute its program. It does not need to rewrite the deployment scripts or read every developer's SSH key. Giving the service account exactly the access required makes a compromised application less capable of damaging its surroundings. It also makes failures explainable: an unexpected write attempt should fail rather than quietly mutate a release.

Permissions belong to a relationship between a process, an object, and an operation. Looking only at a file's mode is insufficient. The process identity may differ from your login; a parent directory may block traversal; an ACL may narrow effective access; a mandatory security policy may deny an operation even when ordinary permissions allow it. This chapter builds an investigation that follows that relationship.

## Users identify processes; names identify numbers

Linux tracks user and group identifiers numerically. Account names make those identifiers readable. Files store an owner UID and group GID; processes have credentials including their effective identity and supplementary groups. A name lookup problem can make `ls` show numbers without changing the underlying ownership. Conversely, creating an account with a reused number can grant access to files owned by that number. Treat account lifecycle and persistent storage ownership together.

Start an investigation with the actual execution identity:

```bash
id
id -u
id -G
```

The first displays your current shell's identity and groups. It does not prove the service has the same credentials. A service manager may start DispatchDesk with a dedicated user and a different supplementary group set. Inspect the configured identity and the running process. Chapter 16 develops systemd units; Chapter 15 explains process inspection.

A login session normally retains the groups established when it started. Adding an account to a group does not retroactively replace the credentials of every running process. Restart the relevant service or establish a new login through the intended procedure, then verify its identity. Do not grant broad access merely because an old shell has not acquired a new group.

Service accounts should have a clear owner and purpose. Shared administrator accounts obscure who performed a change. Separate human logins with scoped privilege are easier to audit, while a dedicated runtime identity limits what application code can access. This is equally relevant to Harbor's VPS, Summit's task runtime, and Atlas's workload identity, although the mechanisms for host and cloud permissions differ.

## Read the mode as an operation policy

Ordinary mode bits express read, write, and execute permissions for owner, group, and others. Values 4, 2, and 1 add within each category: `640` means owner read/write, group read, and no access through the other category. Symbolic notation can make a targeted change clearer: `chmod g-w file` removes group write without replacing unrelated ordinary bits.

For a regular file, read permits reading its content; write permits modifying content; execute participates in allowing execution. For a directory, read permits listing entry names, write permits changing entries, and execute means search or traversal. To access a known file path, the process needs search permission through the relevant directories. To delete a file, the containing directory's permissions matter; the file's read-only mode does not by itself protect its directory entry. Sticky-directory rules add restrictions in shared locations such as `/tmp`.

The kernel does not simply union owner, group, and other permissions. The matching identity category matters. An owner with no owner-read permission does not gain read access merely because the file grants read to others. ACLs extend the decision; privileges and mandatory policy further affect it. [Linux pathname resolution and permission rules](https://man7.org/linux/man-pages/man7/path_resolution.7.html).

Try a small mode exercise in a new, disposable directory owned by your ordinary account:

```bash
mkdir permissions-lab
cd permissions-lab
mkdir private
printf 'fictional configuration\n' > private/config.txt
chmod 700 private
chmod 600 private/config.txt
stat -c '%a %U:%G %n' private private/config.txt
chmod u-w private/config.txt
stat -c '%a %n' private/config.txt
chmod u+w private/config.txt
```

The intended directory mode is 700 and initial file mode 600. Removing owner write makes the file 400; restoring it returns 600. This demonstrates metadata changes on your files. It does not simulate another service identity or prove access under SELinux/AppArmor. Do not use a privileged shell for a denial demonstration: its capabilities can bypass the ordinary checks you intend to test. [GNU chmod manual](https://man7.org/linux/man-pages/man1/chmod.1.html).

## Set creation policy and ownership deliberately

A process umask removes permission bits from the mode requested when creating an object. It does not add bits and does not change existing files. For common creation requests, umask 027 yields files readable/writable by their owner and readable by their group, and directories searchable/readable by the group. Applications can request stricter modes. Default ACL inheritance can also affect creation behavior, so inspect the actual result.

```bash
(
  umask 027
  printf 'sample\n' > created.txt
  mkdir created-directory
  stat -c '%a %n' created.txt created-directory
)
```

Run this inside the disposable lab. Parentheses create a subshell, keeping the demonstration's umask from changing your surrounding shell. Expected ordinary results are 640 and 750 when no default ACL changes the inherited permissions. Verify rather than assume. A runtime should similarly set and document its creation policy through its launcher or service configuration.

A sensible Harbor layout separates executable releases, configuration, and mutable state. The deployment identity owns release content; the runtime can read and execute it but cannot rewrite it. The runtime owns its state directory. Configuration containing secrets has an intentionally restricted owner/group arrangement. Grant the worker access only to the state it needs, remembering that shared SQLite access also involves journal or WAL files in the database directory. Making only the database file writable may therefore be insufficient.

Avoid `chmod -R 777` and indiscriminate `chown -R` as diagnostic tools. They change many relationships simultaneously, mask the cause, and may traverse an unintended tree. A mode that repairs a directory may be excessive for files; a symlink or mount can make your visual scope misleading. Record the intended path and current metadata, change the smallest relevant object, test the specific operation, and retain a reversal plan.

## ACLs express exceptions, with a mask

An access ACL can grant a named user or group permissions beyond the simple owner/group/other model. `getfacl` displays these entries; `setfacl` changes them. The ACL mask bounds the effective permissions of named users, named groups, and the owning group entry. An entry saying read/write can therefore have effective read-only access. Read the effective annotations and mask together.

A default ACL on a directory influences newly created children; it does not retroactively rewrite the access ACL of existing children. Files and directories may inherit different effective execute permissions because their requested creation modes differ. An ACL solves a specific sharing requirement, not account ownership ambiguity. Its semantics and creation rules are documented in the [Linux ACL manual](https://man7.org/linux/man-pages/man5/acl.5.html).

For a shared state directory on a disposable host, a possible design is a runtime owner and a named read-only incident analyst. Before writing any `setfacl` command, specify whether the analyst needs to list the directory, traverse it, read each file, or read future files too. These are separate requirements. Record the original ACL with `getfacl` and test using the analyst's actual credentials. ACL support depends on the filesystem and mount configuration; a pasted command alone cannot establish that design.

## Privilege is a controlled transition

`sudo` can execute a command with another identity according to policy. Its value is an explicit, auditable transition. Running a full root shell for a single service restart broadens the scope of potential mistakes. Prefer a concrete operation with an approved policy, and inspect command arguments and environment handling when designing that policy.

A narrow-looking sudo rule can still be powerful if the allowed program executes arbitrary subprocesses, reads attacker-controlled configuration, or edits privileged files. Wildcards in arguments deserve special attention. Use `visudo` for policy editing and validation, and keep a separate administrative recovery session when changing access to a real host. The detailed matching and environment semantics belong to the [official sudoers manual](https://man7.org/linux/man-pages/man5/sudoers.5.html).

Shell redirection occurs in the invoking shell. `sudo printf ... > /protected/file` does not automatically elevate that shell's file opening. Avoid solving this by elevating an entire interactive session; use an intentional privileged file-installation workflow with explicit ownership and mode. Deployment automation should make that workflow reviewable. No privileged mutations are necessary for this chapter's local exercises.

## Ubuntu, Fedora, and RHEL add policy layers

Ubuntu's AppArmor constrains programs through profiles in addition to ordinary permissions. A profile can deny access that mode bits permit. Inspect profile state with the supported AppArmor tools and examine denial records before changing policy. A missing profile and a permissive profile are different situations; do not assume every custom DispatchDesk executable is automatically confined. Ubuntu's documentation describes profile management and troubleshooting. [Ubuntu Server AppArmor documentation](https://ubuntu.com/server/docs/how-to/security/apparmor/).

Fedora and RHEL commonly use SELinux. Its decisions include labels and policy domains, so copying a file into a new location can produce an unexpected context even when ownership and mode look correct. Inspect enforcement state, file context, process context, and the relevant audit denial. Fix an incorrect persistent labeling rule through the supported tooling and restore the expected labels; a temporary label change can disappear after relabeling. Fedora explicitly tests enforcement after installation; RHEL documents investigation and policy management: [Fedora SELinux installation test](https://fedoraproject.org/wiki/QA:Testcase_base_selinux) and [RHEL 9 SELinux guide](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/getting-started-with-selinux_using-selinux).

Disabling the policy can make a symptom disappear while weakening unrelated services. It also destroys evidence about which operation was denied. Distinguish a genuine application requirement from an unexpected access attempt before permitting it. These host policies differ from AWS IAM and Kubernetes authorization, which later volumes address; passing one layer does not imply passing another.

## Recover from a permission-denied deployment

A new Harbor release starts but its worker cannot create notification state. First capture the exact failed operation and pathname without exposing secret content. Confirm which process failed and its credentials. Walk the parent directories, inspect ownership/mode and ACLs, and verify whether the containing filesystem is writable. Read-only mounts can resemble an access design failure but need a different recovery.

Compare the failed path with the intended state directory. In this scenario a deployment copy put the database beneath the release directory, where the runtime has read access only. The directory policy is correct; the path is wrong. Moving mutable state into its designated directory through a controlled migration is preferable to making all release content writable.

Stop the relevant writers before migrating database files, use the database's safe backup/migration method rather than copying an actively changing file blindly, and keep the prior state until verification succeeds. Confirm accepted orders and durable notification intent remain paired, then start the runtime and test its intended write operation. Watch for sibling journal files and mandatory-policy denials. A process-health response alone cannot prove that state writes now work.

Document the corrected layout and add a predeployment check for writable state and read-only release content under the runtime identity. The recovery must preserve the invariant introduced in Chapter 10: an acknowledged order has durable notification intent. Permission troubleshooting is part of correctness, not merely a way to silence startup errors.

## Exercises and takeaways

1. Explain why a readable file behind a directory without search permission can be inaccessible. Guidance: pathname lookup must traverse every relevant directory before reading the final object.
2. Run the mode and umask exercises as an ordinary user. Record the actual modes. Guidance: distinguish changes to existing objects from creation policy; investigate default ACLs if creation differs.
3. An ACL grants a named analyst `rw-`, but its mask is `r--`. What is effective? Guidance: read-only through that entry; changing the mask may affect other entries too.
4. A service works from your shell but fails under its unit. Draft an investigation sequence. Guidance: compare identity, groups, working directory, paths, mount restrictions, ACLs, and mandatory policy before changing permissions.

Permissions are operational design expressed through identities, paths, and specific actions. Keep immutable releases separate from mutable state, verify the runtime identity, and diagnose each enforcement layer. Continue to [Chapter 15](015-processes-signals-and-jobs.md) for the process behavior behind these identities.

After the local exercises, while still inside `permissions-lab`, remove the known files and then its empty directories:

```bash
rm -- private/config.txt created.txt
rmdir -- private created-directory
cd ..
rmdir -- permissions-lab
```

If you added other exercise files, inspect and handle them deliberately; `rmdir` refuses to remove a nonempty directory.

## Verification

The author inspected Linux pathname/ACL manuals, GNU chmod, Ubuntu AppArmor, RHEL SELinux, and the upstream sudoers manual hosted by man7. Fedora installation enforcement was checked against its official QA test; shared SELinux mechanisms were checked against RHEL documentation. Local exercise results are recorded in the continuation summary. No service accounts, sudo policy, ACL exceptions, mandatory profiles, or real database migration were created or tested on baseline distribution images.
