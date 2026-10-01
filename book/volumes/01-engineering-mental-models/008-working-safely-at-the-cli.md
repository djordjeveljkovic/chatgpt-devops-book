---
book: The Complete DevOps Engineering Book
volume: 1
volume_title: "Engineering Mental Models"
chapter: 8
title: "Working Safely at the CLI"
slug: working-safely-at-the-cli
status: complete
summary: ../../_ai/chapter-summaries/008-working-safely-at-the-cli.md
---

# Chapter 8 — Working Safely at the CLI

## Execution context and privileges

A command's text is only part of its meaning. `cp config.txt config.saved` acts on different files depending on the working directory. A service restart affects a different machine depending on the terminal connection. A cloud deletion affects a different account depending on credential selection. Before running an operational command, identify the context that gives it a target.

The prerequisite is [Learning to Investigate](007-learning-to-investigate.md). This chapter develops a read, change, verify and recover habit using a disposable local file. It introduces shell mechanics only where they change operational scope; [The Shell and Command Execution](../02-linux-and-automation/011-the-shell-and-command-execution.md) provides the canonical explanation. Use Bash on Linux as an ordinary user with GNU coreutils. No administrator privileges are needed.

The essential context includes execution host, user identity, working directory, interpreter, target resource and relevant environment or profile. “Run on the server” is too vague when a team has staging, production and recovery hosts. A runbook should state the intended host role and the evidence used to identify it. A prompt is a convenience, not authoritative proof: prompts can be customized or stale.

Read local context with:

```bash
hostname
id
pwd -P
```

Run these in the same terminal where you intend to act. `hostname` reports the configured host name, which may still need comparison with inventory. `id` shows the current process's user and group identities, documented by the [GNU id manual](https://man7.org/linux/man-pages/man1/id.1.html). `pwd -P` asks Bash to show the physical working path rather than preserve a logical path through symbolic links. None of these commands validates a cloud profile, remote service identity or authorization policy; add the target-specific identity check when those tools are introduced.

Privileges define what a process can do, not whether doing it is appropriate. Running as root can make a mistaken path writable. A command that fails with permission denied should first be compared with the intended owner and access model. Adding `sudo` without understanding the boundary may conceal a deployment error and create new root-owned files. Ubuntu, Fedora and RHEL have different access and security defaults; this habit applies to all three, while [Users and Permissions](../02-linux-and-automation/014-users-groups-and-permissions.md) covers their actual mechanisms.

Use a narrow privilege boundary. Editing a local note does not need root. Installing a system package may require an administrator. Managing a cloud resource requires the service's permitted identity, which is a different boundary from local root. Broad terminal privileges cannot substitute for deliberate target selection.

## Read, change, verify and recover

Operational work has four linked stages. Read the existing state and identify the target. Make a bounded change. Verify the intended effect using evidence relevant to the outcome. Recover if the change fails, preserving information needed to understand it. These are not four mandatory tool invocations; they are responsibilities that a procedure must cover.

Practice with a disposable configuration file. Run the following setup from any directory in Bash as an ordinary user:

```bash
cli_lab=$(mktemp -d)
cd "$cli_lab" || exit 1
printf '%s\n' 'LOG_LEVEL=info' > settings.env
pwd -P
cat -- settings.env
```

`mktemp -d` creates a new temporary directory. `cli_lab` stores its path. Quoting ensures the directory is one argument; the guarded `cd` exits if changing directory fails. `printf` creates exactly one line, and its redirection creates the file in that verified directory. `cat --` reads the explicit filename; `--` ends option interpretation. The file contains a nonsensitive teaching value, not a secret.

Now retain the prior state and make a controlled change:

```bash
cp -- settings.env settings.before
printf '%s\n' 'LOG_LEVEL=debug' > settings.env
cat -- settings.env
```

`cp` copies the existing contents to the explicitly named backup. The [GNU cp manual](https://man7.org/linux/man-pages/man1/cp.1.html) documents copy behavior. In this fresh lab, the backup name does not exist. On a real host, check that assumption: overwriting an earlier backup can destroy the only retained recovery state. The redirection overwrites the setting file, so it is a state change. The final read verifies contents, but no running application consumes this file; a real service would also need its documented reload or restart and a behavioral check.

Recover the original contents:

```bash
cp -- settings.before settings.env
cat -- settings.env
```

The expected restored line is `LOG_LEVEL=info`. This demonstrates reversible file content changes, not restoration of file ownership, access controls, extended attributes or application state. A more demanding system configuration procedure must identify those additional properties. Do not call a content copy a complete server backup.

Cleanup deliberately deletes the lab files:

```bash
rm -- settings.env settings.before
cd /tmp || exit 1
rmdir -- "$cli_lab"
```

This is destructive to the two named lab files. It is authorized by the purpose of this disposable exercise. `rmdir` removes only an empty directory and fails if unexpected contents remain. That failure is useful evidence; inspect unexpected files rather than widening deletion automatically. The [GNU rm manual](https://man7.org/linux/man-pages/man1/rm.1.html) describes removal semantics and available safeguards.

The lab should be run sequentially in one terminal, retaining the variable until cleanup. If you open a new shell, `cli_lab` is not automatically defined there. If a command fails, stop and inspect before continuing. The example's purpose is to make execution context visible, not to introduce a general automation framework.

## Recognizing destructive and costly commands

Commands can change more than files. A database migration can drop data or acquire locks. A firewall update can terminate the administrative path. A service restart can interrupt in-flight requests. Cloud creation can start ongoing charges; cloud deletion can remove recoverable state. The operation's risk follows its target and behavior rather than its length.

Read a command as code. Identify the executable, options, operands, expansions, redirections and control flow. A wildcard expands before the called program receives arguments. An unquoted variable can become several arguments. Output redirection is performed by the shell, so a seemingly read-only program can overwrite a file if its output is redirected there. A pipeline contains several processes whose failures may be reported differently from the overall shell result.

Do not copy a command because its first word looks familiar. A `curl` invocation can download a public page, send a sensitive payload or invoke a destructive API. A database client's `SELECT` can be read-only, but the same client can execute deletion. A shell script obtained from the network can contain arbitrary work regardless of its friendly filename. Inspect the actual content and source within the team's release policy.

A preview helps only if you understand what it previews. Printing a selected pathname can confirm expansion, but does not show whether that path is a symbolic link or whether a resource changed afterward. A cloud planning command may identify expected resources while missing an outside action that occurs before execution. Preview evidence reduces uncertainty; it does not turn every subsequent operation into a harmless one.

Recovery depends on retained state and access. Before modifying a remote firewall, maintain an approved alternate path and know how to restore the previous rules. Before a schema change, know whether application rollback can read the changed data. Before deleting a resource, know whether its backup and restore mechanism actually meet the required contract. These preparations are concrete engineering steps, not a reason to stop every routine reversible edit for another approval.

## A correct command in the wrong directory

A responder intends to change DispatchDesk's staging configuration. Their terminal remains inside a production release directory after an earlier investigation. A relative-path overwrite replaces the production setting instead. The shell reports success because the user had permission; success of the file operation does not establish correctness of the target.

Diagnosis begins with the physical working path, the affected file's location and the change timeline. The responder checks whether the running production process consumed the new value. If it has not, restoring the original file may prevent impact. If it has, the team restores the approved configuration through the actual service procedure and verifies the operating outcome. They preserve the incorrect change record for investigation, with secret values removed.

The corrective procedure uses explicit target paths, checks the environment identity and retains a known prior state. For frequent changes, a tool can require a declared environment and display its resolved target before applying the change. The control should fit the failure mechanism: a warning banner alone does not ensure that a script selected the right path.

A more subtle variant uses a symbolic link pointing to another release. `pwd -P` helps identify the physical path, but the complete target can still include links. The later filesystem chapter develops path and inode inspection. For now, the lesson is to verify target meaning rather than infer it from a familiar filename.

## Exercises and answer guidance

1. The command changes `settings.env`, but the service logs still show the previous level. What is missing from verification? The service may load configuration only at startup or from another path. Check its configured source and documented reload behavior before restarting arbitrarily.
2. A copy command reports permission denied. What should you establish before adding privilege? Identify the intended target, file and directory ownership, service user and relevant security policy. A wrong path or ownership defect can be more likely than insufficient legitimate privilege.
3. Why does the lab use an empty-directory removal instead of recursive cleanup? It limits removal scope and exposes unexpected contents. Explain that this is a scoped teaching cleanup, not a universal replacement for every legitimate recursive operation.
4. An infrastructure preview lists the expected resources. What still needs verification? Identity, actual target state at execution, credentials, outside changes, cost and rollback boundaries may matter. A preview is one piece of evidence.

## Review questions and takeaways

Which facts establish your execution context? Where does the shell perform expansion or redirection? Which state does a backup actually retain? What evidence verifies application behavior beyond file contents? How would you recover if your normal access path disappeared?

Treat commands as scoped changes to a specific system. Inspect context, use the needed privilege, retain recovery evidence and verify the outcome. A successful exit is evidence about command execution, not automatic proof of a correct operational decision. Continue with [Teams, Ownership and Operational Work](009-teams-ownership-and-operational-work.md).

## Sources and verification

Bash and GNU id/cp/rm upstream manual content hosted by man7 was inspected on 2026-10-01 after GNU's online manual requests timed out. The authoring environment reports Bash 5.3.20 and GNU coreutils 9.11. The full lab was not run while drafting; its shell syntax is subject to the book validator. No privileged host change, remote firewall, database or cloud operation was executed. The wrong-directory incident is fictional. Independent review remains required.
