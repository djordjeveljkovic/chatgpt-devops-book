---
book: The Complete DevOps Engineering Book
volume: 22
volume_title: "Operational Reference"
chapter: 211
title: "Linux and Shell Command Reference"
slug: linux-and-shell-command-reference
status: complete
summary: ../../_ai/chapter-summaries/211-linux-and-shell-command-reference.md
---

# Chapter 211 — Linux and Shell Command Reference

Use this chapter when you know what you need to observe but cannot remember the command. For explanations of shell execution, permissions, processes and supervision, follow the links to [Volume 2](../02-linux-and-automation/README.md). A command's successful exit answers a specific question; it rarely proves that a customer journey works.

Examples target a Linux terminal with Bash and GNU utilities. They work as ordinary-user observations unless `sudo` is shown. Ubuntu 24.04, Fedora 44 and RHEL 9 can differ in installed packages, groups and service names. Inspect `command --help` and the package version before relying on a less familiar option. Do not infer that Fedora's installed package version matches RHEL's.

## Establish the execution context

Before investigating DispatchDesk, identify the host, user and path. This matters because a correct command on the wrong machine gives convincing but irrelevant evidence.

```bash
hostname
id
pwd -P
printf '%s\n' "$PATH"
command -v python3
```

`hostname` reports the local host name; it does not independently prove cloud account or cluster identity. `id` reports the current identity and group memberships. `pwd -P` resolves the physical working directory, which may differ from the symbolic path you entered. `printf` uses a literal format string and prints the value of `PATH`; its colon-separated entries determine where the shell searches for executables. `command -v` asks how the shell resolves a name. It can identify a function or builtin as well as a file. An absent executable returns a nonzero status.

Quote variable expansions when one argument is intended. In `cat -- "$report_path"`, double quotes keep spaces in the path within that argument. `--` ends option parsing for `cat`, allowing a file name beginning with a hyphen. Single quotes preserve literal text, which is why a search expression such as `'*.log'` should reach `find` without first expanding in the shell. The deeper mechanics are in [The Shell and Command Execution](../02-linux-and-automation/011-the-shell-and-command-execution.md); [Bash's quoting manual](https://www.gnu.org/software/bash/manual/html_node/Quoting.html) defines the syntax.

## Files, paths and text

These examples assume the named files already exist. They inspect data without rewriting it. Choose output limits deliberately when a file is large.

| Command | Meaning of the arguments and useful evidence |
|---|---|
| `ls -lah -- .` | List the current directory. `-l` shows metadata, `-a` includes hidden names, and `-h` scales sizes for humans. Directory size is not the total size of its contents. |
| `stat -- ./orders.log` | Show metadata for this exact path, including permissions, ownership, size and timestamps. A timestamp alone does not establish who changed the file. |
| `file -- ./release.tar.gz` | Identify likely content type from inspected bytes. The `file` package may need installation. This is useful when a downloaded archive is actually an error page. |
| `find . -type f -name '*.log' -print` | Search below the current directory for regular files whose names match the quoted pattern. `-print` emits paths; newline-containing names require a null-delimited workflow when handing them to another program. |
| `sed -n '1,80p' ./orders.log` | Suppress automatic printing with `-n`, then print lines 1–80. This does not edit the file. |
| `tail -n 50 -- ./orders.log` | Show the final 50 lines. For an active log, `tail -F` follows by name and retries when the file is replaced, such as during rotation. |
| `grep -nF -- 'order_failed' ./orders.log` | Search for literal text with `-F`, and show line numbers with `-n`. Exit 0 means a match, 1 means no match, and a higher error status means the search itself failed. |
| `wc -l -- ./orders.log` | Count newline characters. An unterminated final record can make this differ from a reader's intuitive line count. |
| `sort -- ./events.txt` | Sort lines using the current locale. Use `LC_ALL=C sort` when the intended comparison is byte-oriented and should be reproducible across locale settings. |
| `sort -- ./events.txt \| uniq -c` | Group identical lines before counting adjacent duplicates with `uniq -c`. Without the sort, separated occurrences do not form one count. |

The escaped pipe in the last table row is Markdown notation. At the shell, type the ordinary pipeline:

```bash
sort -- ./events.txt | uniq -c
```

For large repositories, ripgrep is often convenient: `rg -n --fixed-strings -- 'order_failed' .`. `-n` adds line numbers and `--fixed-strings` disables regular-expression interpretation. Its default traversal respects ignore rules and skips some hidden content; a missing match can therefore be a search-scope issue. Use its documented hidden/ignore options when that scope is actually required. Install `ripgrep` with `sudo apt-get install ripgrep` on Ubuntu or `sudo dnf install ripgrep` on Fedora; check enabled RHEL repositories before assuming that package is available.

Consult [Files, Paths and Filesystem Tools](../02-linux-and-automation/012-files-paths-and-filesystem-tools.md) and [Text Processing and Pipelines](../02-linux-and-automation/013-text-processing-and-pipelines.md) before constructing a destructive pipeline from a file search. File names are data, not shell code. The [GNU Coreutils manual](https://www.gnu.org/software/coreutils/manual/html_node/index.html) provides the individual utility definitions.

## Permissions and ownership

Inspect the target and its parent directories before changing access:

```bash
id
ls -ld -- . ./uploads
stat -- ./uploads/order-42.json
```

Directory execute permission permits traversal, while directory read permission permits listing names. A file's own readable mode is insufficient if a parent cannot be traversed. Group changes also do not alter the supplementary groups already held by an existing process; restart the relevant session or service under its intended identity.

`chmod u=rw,g=r,o= ./report.txt` sets owner read/write, group read, and no access for others on the named file. `chmod 0750 ./uploads` sets owner full access and group read/traverse on the directory. Neither command recursively changes children. `chown dispatchdesk:dispatchdesk ./uploads` changes the named object's owner and group, requiring the appropriate authority. Verify the resulting metadata and test access as the service account. Do not replace a diagnosis with `chmod -R 777`: it changes unrelated access boundaries and may leave ACL or SELinux causes unresolved.

On Fedora/RHEL, inspect `ls -Z` and relevant AVC evidence when ordinary Unix permissions seem correct. On Ubuntu, investigate an applicable AppArmor profile. Mandatory access controls add another decision boundary; changing file modes does not erase that policy. See [Users, Groups and Permissions](../02-linux-and-automation/014-users-groups-and-permissions.md) and [SELinux and Container Mounts](../07-podman-and-the-rootless-host/067-selinux-and-container-mounts.md).

## Processes and resource evidence

| Command | Question answered and important limit |
|---|---|
| `ps -eo pid,ppid,user,stat,%cpu,%mem,comm --sort=-%cpu` | Which processes have the highest reported CPU percentages? `-e` selects all processes and `-o` chooses fields. This snapshot does not identify a customer's slow request or necessarily represent recent instantaneous CPU use. |
| `pgrep -a -u dispatchdesk python3` | Which matching processes belong to that account? `-a` prints command lines, which can contain sensitive arguments. Matching a name does not establish service ownership. |
| `free -h` | How is host memory accounted for in human-readable units? Available memory is more useful than treating all cache as permanently unavailable. Container limits require separate cgroup evidence. |
| `vmstat 1 5` | Sample scheduling, memory and I/O indicators every second for five reports. The first report commonly summarizes since boot; do not mistake it for the same sampling interval as later reports. |
| `df -hT -- /var/lib/dispatchdesk` | Which mounted filesystem contains the path, and what are its type and capacity figures? It measures filesystem allocation, not the size of just that directory. |
| `df -i -- /var/lib/dispatchdesk` | Is the containing filesystem short of inodes even if byte capacity remains? |
| `du -sh -- ./releases` | Estimate allocated space below the named directory; `-s` summarizes and `-h` scales units. Mount crossings, permissions and deleted-but-open files can explain differences from `df`. |

Send a signal only after confirming the current process identity. `kill -TERM 12345` requests termination of that PID; the number here is illustrative and must not be copied as a real target. SIGTERM lets cooperative software clean up. SIGKILL removes that opportunity and cannot repair external state. For a supervised application, the service manager usually gives a clearer ownership boundary than a name search. See [Processes, Signals and Jobs](../02-linux-and-automation/015-processes-signals-and-jobs.md).

## Systemd and the journal

For a system service named `dispatchdesk-api.service`:

```bash
systemctl status dispatchdesk-api.service --no-pager
systemctl show dispatchdesk-api.service -p MainPID -p ActiveState -p SubState
systemctl cat dispatchdesk-api.service
journalctl -b -u dispatchdesk-api.service --since '-15 min' --no-pager
```

`status` provides a human view and can return nonzero when the unit is inactive or failed; that is an observed state, not automatically a command malfunction. `show` exposes selected properties using `-p`. `cat` displays the unit and drop-ins, useful when the effective service differs from the remembered file. In `journalctl`, `-b` restricts to the current boot, `-u` selects the unit, and `--since` bounds the time window. `--no-pager` makes these commands suitable for captured output. Journal access depends on identity and the host's access policy.

These commands change service state and may interrupt requests:

```bash
sudo systemctl daemon-reload
sudo systemctl restart dispatchdesk-api.service
sudo systemctl enable dispatchdesk-api.service
```

`daemon-reload` reloads the manager's unit definitions after an edit; it does not reload the application's own configuration. `restart` restarts an active service or starts an inactive one. `enable` establishes the configured startup links and does not itself start the service. `enable --now` combines enablement and startup. An application-specific `reload` works only when its unit and process support that lifecycle action.

For rootless user services, use `systemctl --user` and `journalctl --user-unit=dispatchdesk-api.service`; these address a different manager and ownership context. User-manager availability after logout requires deliberate lifecycle configuration. See [Systemd and Service Lifecycles](../02-linux-and-automation/016-systemd-and-service-lifecycles.md) and [Quadlet and Systemd Integration](../07-podman-and-the-rootless-host/066-quadlet-and-systemd-integration.md). The [systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html) and [journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html) manuals define manager and journal options.

## A short operational drill

DispatchDesk fails to write an uploaded document. First establish identity and the failing path; inspect parents, ownership, mount capacity and inode capacity. Examine the application's event and the applicable security policy. Change only the boundary supported by evidence, then retry a known test upload as the service identity and retrieve it. A successful `chmod` exit does not prove that the application can store or later read the document.

For a failed restart, compare the effective unit, its main-process state and current-boot journal. A missing executable, invalid configuration, unavailable working directory and exhausted restart limit require different repairs. After restoring the service, test the expected API journey and pending work. Preserve evidence of the failed release before making another change.

Review prompts: why can `df` and `du` disagree; why can `grep` exit 1 without an execution error; why does `enable` differ from `start`; and why can a readable file remain inaccessible? The linked chapters supply the mechanisms. This reference supplies the next observation, not a universal recovery command.

## Verification

Written on 2026-10-01. GNU Bash 5.3 quoting documentation was retrieved; the installed Bash is 5.3.20. Installed `systemctl --help` and `journalctl --help` were inspected. Online systemd manual retrieval returned HTTP 403, so those links are further reference rather than a claimed online inspection. The commands are operational examples, not transcripts of actions against a DispatchDesk host. No ownership, process, service or security-policy changes were executed while writing this reference. Independent review remains pending.
