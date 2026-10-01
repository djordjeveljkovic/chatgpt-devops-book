---
book: The Complete DevOps Engineering Book
volume: 2
volume_title: "Linux and Automation"
chapter: 18
title: "Shell Automation That Survives Failure"
slug: shell-automation-that-survives-failure
status: complete
summary: ../../_ai/chapter-summaries/018-shell-automation-that-survives-failure.md
---

# Chapter 18 — Shell Automation That Survives Failure

## Why this matters

A manual action becomes automation when it can run with less supervision. That raises the importance of failure behavior. A developer can notice an unexpected path or diagnostic; a scheduled script may overwrite the previous good report and exit with a misleading success status. DispatchDesk needs scripts that explain their inputs, limit their effects, and remain understandable when interrupted halfway through.

Shell is well suited to coordinating existing commands and modest file operations. It becomes difficult when the task requires complex data validation, transactional updates across many objects, or a long-lived concurrency protocol. Choose another language when it gives clearer guarantees. A shorter shell script is not necessarily safer than a readable Python program.

This chapter builds a complete local script that publishes a configuration inventory. It uses Bash and established GNU utilities on the Ubuntu, Fedora, and RHEL baselines. It deliberately does not mutate the running service or send customer notifications: those operations need application-specific recovery contracts.

## Define the operation before implementing it

The inventory script accepts one existing directory and inventories regular files directly inside it. It records SHA-256 digests and names in the checksum utility's output format. It excludes nested files and symbolic links. It publishes `inventory.sha256` in the input directory only after collection succeeds, using a temporary sibling file. The directory is trusted, owned by the operator, and not concurrently modified by another actor during the lab.

Those constraints are part of the interface. A general incident collector might need nested traversal, a stable snapshot, secret exclusion, and provenance. Do not silently turn this local demonstration into that collector. The checksum text can expose filenames; real inventories belong in an appropriately restricted evidence location.

An idempotent operation can be repeated without changing its intended final result beyond the desired state. Replacing a report from unchanged input is a reasonable local example. Appending a notification to a provider on every invocation is not idempotent merely because the command is repeatable. For external side effects, the identity of the operation and the recovery record matter.

## A complete script with explicit boundaries

Save the following inline example as `publish-inventory.sh` in your disposable practice workspace. Run it with Bash rather than sourcing it into your login shell. The script deliberately restricts supported paths to an existing ordinary directory, rejects directory symlinks, and assumes no hostile concurrent mutation.

```bash
#!/usr/bin/env bash
set -u
set -o pipefail
umask 077

fail() {
  printf 'inventory: %s\n' "$*" >&2
  exit 1
}

if (( $# != 1 )); then
  printf 'usage: bash publish-inventory.sh DIRECTORY\n' >&2
  exit 2
fi

input_dir=$1
[[ -d "$input_dir" && ! -L "$input_dir" ]] || fail 'expected an ordinary directory'
cd -- "$input_dir" || fail 'cannot enter input directory'
input_dir=$PWD
[[ -w . ]] || fail 'directory is not writable'
[[ ! -d inventory.sha256 ]] || fail 'output name is a directory'

work_file=''
cleanup() {
  if [[ -n "$work_file" ]]; then
    rm -f -- "$work_file" || printf 'inventory: temporary cleanup failed\n' >&2
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

work_file=$(mktemp -- .inventory.XXXXXXXXXX) || fail 'cannot create temporary output'

shopt -s nullglob dotglob
files=()
for path in ./*; do
  [[ -f "$path" && ! -L "$path" ]] || continue
  [[ "$path" != ./inventory.sha256 && "$path" != "$work_file" && "$path" != "./$work_file" ]] || continue
  files+=("$path")
done

if (( ${#files[@]} )); then
  sha256sum -- "${files[@]}" > "$work_file" || fail 'checksum collection failed'
else
  : > "$work_file" || fail 'cannot initialize empty output'
fi

chmod 600 -- "$work_file" || fail 'cannot set output permissions'
mv -T -- "$work_file" inventory.sha256 || fail 'cannot publish output'
work_file=''
printf 'inventory: published %d file digests in %s\n' "${#files[@]}" "$input_dir"
```

`set -u` detects many references to unset variables. It is not full input validation. `pipefail` supplies the pipeline behavior discussed in Chapter 13, although this particular script does not need a multi-stage collection pipeline. The examples use explicit status checks rather than assuming a global error option proves all failures are handled.

The input count check happens before `$1` is read. Every path expansion is quoted. Arrays preserve separate arguments, including filenames with spaces, and `--` ends option parsing for utilities that support it. Prefixing matched names with `./` also makes a file named `-draft` an ordinary path argument. The script does not parse `ls` output.

Bash's nullglob avoids treating an unmatched pattern as a filename; dotglob includes ordinary dotfiles. The loop selects regular files and excludes symlinks, the prior report, and its current temporary output. This is a chosen scope, not recursive discovery. Its array-based approach is appropriate for a small configuration directory; extremely large collections can exceed argument-size limits and require a bounded streaming design.

## Temporary files and publication are different guarantees

`mktemp` creates the temporary object rather than merely inventing a plausible name. Avoid `mktemp -u`, which leaves a name unreserved and permits a race before creation. This script creates its file inside the destination directory to keep publication on the same filesystem under the lab assumptions. Its restrictive umask and explicit output mode protect the report from incidental broad access. [GNU mktemp manual](https://man7.org/linux/man-pages/man1/mktemp.1.html).

The final move replaces a directory entry after all checksums have been written. GNU `mv -T` treats the destination as the named object, avoiding an accidental move into a destination directory. On the intended same-filesystem case, a rename gives readers a transition between the old and new pathname contents instead of exposing the partially written staging file. Cross-filesystem moves can require copying and do not provide the same publication behavior. [GNU mv manual](https://man7.org/linux/man-pages/man1/mv.1.html).

Atomic pathname replacement does not establish power-loss durability, a multi-file transaction, or a snapshot of files changing during collection. Nor does this script defend against an attacker modifying the directory while it runs. A configuration inventory used for compliance or recovery needs a stronger collection boundary and a retained artifact identity. State the limit explicitly instead of calling every temporary-file pattern transactional.

If a collected file changes between hashing and later use, the published digest may describe an earlier content version. If an input disappears while the checksum command runs, collection fails and the prior report should remain. A database backup needs the database's backup protocol; hashing an actively changing database file is not a valid backup method.

## Traps clean up; they do not undo the world

An EXIT trap attempts to remove the temporary file when the shell exits. INT and TERM traps translate those signals into intentional exit statuses, allowing the EXIT cleanup path to run. SIGKILL cannot execute this cleanup. A machine crash may leave a temporary sibling behind. Diagnose and remove such remnants only after confirming that no active invocation owns them.

Cleanup is narrower than rollback. The trap cannot unsend a notification or restore an overwritten external resource. It also does not make concurrent invocations safe: another invocation's temporary file could be included as an input in this simple lab design. Chapter 20 adds overlap prevention. A production workflow needs an explicit single-writer contract or a lock, along with exclusion rules for its staging artifacts.

Some shell errors occur in contexts where `set -e` does not terminate as a casual reader expects, including conditional command contexts. It can be helpful under a understood policy, but it is not a substitute for branching on expected failure cases. Similarly, combining `local` or another declaration builtin with a failing command substitution can hide the command's status behind the builtin's result. Separate declaration from assignment when that status matters. Bash's conditional, trap, and option semantics are documented in the [upstream manual](https://man7.org/linux/man-pages/man1/bash.1.html).

Keep logs specific and bounded. A script should report the operation and failed stage without dumping all configuration or enabling sensitive tracing. A final success message belongs after publication, not after starting the work. That message says this invocation published a report, not that the report has already passed an independent audit.

## Exercise the contract locally

Create an empty practice directory separate from the script, then add two sample configuration files. The script path below assumes it was saved in the current directory:

```bash
mkdir inventory-input
printf 'PORT=8080\n' > inventory-input/service.conf
printf 'fictional worker settings\n' > 'inventory-input/worker settings.conf'
bash publish-inventory.sh inventory-input
cat inventory-input/inventory.sha256
(
  cd inventory-input || exit 1
  sha256sum --check inventory.sha256
)
bash publish-inventory.sh inventory-input
```

Two input files should be reported both times. The report must not include itself or its active temporary file. Checking the digests in the input directory should confirm both fixture contents. Use an initially absent lab directory so creation cannot silently mix with prior data.

Also run a no-argument invocation and an invocation naming a nonexistent directory. Both should fail without publishing anything. Test an empty directory: a successful empty report means the explicitly selected input population is empty, not that there is no configuration elsewhere. Chapter 13's collection-completeness reasoning still applies.

If you want to test a collection failure, use a disposable ordinary-user environment and arrange a genuinely unreadable regular file. Running as root can invalidate that denial test. Preserve a known prior report, then verify it remains unchanged after the failed collection. Do not describe a failure path as tested until the failure actually occurred.

## Investigate a script that damaged its report

Suppose Harbor's previous inventory became empty after a failed collection. Preserve the script version and execution context, then inspect its redirections. The old script wrote directly to `inventory.sha256` before invoking the collector. The shell truncated the prior report, and the collector then failed because an input was unreadable.

Recover the prior report from retained evidence if available; otherwise rebuild from a trustworthy input boundary and label the gap. Do not invent the missing historical state by treating today's digest as yesterday's. Repair publication with staging and a success check, then exercise a real failing collection on a disposable fixture. A successful run alone would not have exposed the defect.

Review permissions and collection scope as separate issues. If the service's secret file should be excluded, changing access to make the inventory work is wrong. If an authorized inventory requires it, grant the intended identity the smallest necessary access and protect the report. The script's success must follow the data policy, not redefine it.

## Exercises and takeaways

1. Run the fixture twice and compare report content. Guidance: exclude output/staging artifacts and preserve filenames as arguments; repetition should produce the same intended digest population.
2. Explain which interruptions the EXIT trap cannot handle. Guidance: forced kill and host failure cannot run shell cleanup; cleanup also cannot reverse external effects.
3. Change one fixture input after publication and run checksum verification. Guidance: a failing check establishes a mismatch with the recorded content, not which party changed it or whether the change was authorized.
4. Specify the changes required for concurrent invocations or actively changing inputs. Guidance: add ownership/locking and a stable collection boundary; temporary-file creation alone supplies neither.

Reliable automation states its contract, checks failures explicitly, preserves arguments, limits cleanup scope, and publishes only completed output. Know when those guarantees are insufficient and move the task to a stronger protocol or language. Continue to [Chapter 19](019-git-for-operational-changes.md) to review and retain the script's changes.

## Verification

The author inspected upstream Bash, GNU mktemp, and GNU mv manuals. Executed fixture cases and their exact limits are recorded in the continuation summary. No operational secrets, service changes, infrastructure, or customer-side effects were involved.
