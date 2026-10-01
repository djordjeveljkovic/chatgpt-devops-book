---
book: The Complete DevOps Engineering Book
volume: 2
volume_title: "Linux and Automation"
chapter: 20
title: "Scheduling and Resource Limits"
slug: scheduling-and-resource-limits
status: complete
summary: ../../_ai/chapter-summaries/020-scheduling-and-resource-limits.md
---

# Chapter 20 — Scheduling and Resource Limits

## Why this matters

Harbor schedules an inventory every five minutes. One run takes longer because storage is slow; the next starts anyway. Both collect different intermediate content and replace the same report. A schedule that looked precise has created a concurrency bug. Meanwhile, a notification worker approaches its descriptor limit and fails to open another connection even though memory appears plentiful.

Scheduling and resource limits shape how work enters and leaves a host. A useful design defines when a job becomes eligible, what happens if the host was down, whether another invocation may run, how long work can continue, and which evidence proves success. A calendar expression alone answers only part of that contract.

## Calendar time and elapsed time differ

Wall-clock schedules refer to dates and clock readings. Their behavior depends on timezone, daylight-saving transitions, and clock corrections. Elapsed-time schedules express intervals relative to events such as activation or completion. They better fit tasks described as “wait five minutes after the previous run finishes,” but their suspension and reboot behavior still needs an explicit policy.

For an incident report, UTC makes an interval easier to compare with other systems. For a local business deadline, the organization's timezone may be the correct requirement. Do not replace one with the other for convenience without explaining the consequence. A daylight-saving transition can make a local clock reading ambiguous or absent; inspect the specific scheduler's behavior and test the intended calendar.

Jobs should record both their intended reporting interval and their actual execution time. A late start can still produce the correct interval if collection is designed that way. Conversely, running on schedule does not prove collection covered the whole interval. A missing-run detector belongs beside the schedule, especially for backups and notification reconciliation.

## Systemd timers activate managed units

A timer normally activates a service with the same basename. A currently active target service is left running rather than duplicated by the same timer activation. This helps with a single managed oneshot, but it does not coordinate different unit names, manual commands outside the manager, or another host. Avoid `RemainAfterExit=yes` for a repetitive oneshot unless you deliberately want its completed unit to remain active. [Systemd timer manual](https://man7.org/linux/man-pages/man5/systemd.timer.5.html).

A complete user-manager practice pair writes a timestamp to the journal and performs no application mutation. On a disposable VM with a working user manager, save the first file as `~/.config/systemd/user/dispatchdesk-schedule-lab.service`:

```ini
[Unit]
Description=DispatchDesk schedule timestamp practice

[Service]
Type=oneshot
ExecStart=/usr/bin/date --iso-8601=seconds
TimeoutStartSec=20s
```

Save the companion as `~/.config/systemd/user/dispatchdesk-schedule-lab.timer`:

```ini
[Unit]
Description=DispatchDesk schedule practice timer

[Timer]
OnCalendar=*-*-* *:0/5:00 UTC
Persistent=true
RandomizedDelaySec=15s
AccuracySec=1s

[Install]
WantedBy=timers.target
```

The calendar makes the job eligible every five minutes in UTC. Random delay spreads starts within the chosen additional interval, while accuracy permits a scheduling window; eligibility is not a promise of an exact dispatch instant. `Persistent=true` remembers calendar activation state and can trigger a catch-up after downtime. It does not replay every missed business interval as a separate execution. If a report needs every interval, store and advance that interval cursor explicitly.

Inspect the expression before activating anything:

```bash
systemd-analyze calendar --iterations=3 '*-*-* *:0/5:00 UTC'
```

On the reader VM, verify both unit files and use the correct user scope:

```bash
systemd-analyze --user verify "$HOME/.config/systemd/user/dispatchdesk-schedule-lab.service" "$HOME/.config/systemd/user/dispatchdesk-schedule-lab.timer"
systemctl --user daemon-reload
systemctl --user start dispatchdesk-schedule-lab.timer
systemctl --user list-timers dispatchdesk-schedule-lab.timer --all
journalctl --user -u dispatchdesk-schedule-lab.service --since '20 minutes ago' --no-pager
systemctl --user stop dispatchdesk-schedule-lab.timer dispatchdesk-schedule-lab.service
```

This lab uses explicit start rather than enable; it need not persist across a new session. After stopping both units, remove only their two known unit files and reload the user manager. Review Chapter 16's user-manager lifetime distinction. The author has not activated this timer; parser and unit-verification results are recorded separately in the continuation summary. [Calendar syntax manual](https://man7.org/linux/man-pages/man7/systemd.time.7.html).

For a completion-relative job, a timer can instead combine an initial activation condition with `OnUnitInactiveSec=5min`. The requirement then differs from “every fifth minute of the clock.” Choose the requirement before choosing the directive. Do not combine several activation conditions accidentally and then interpret extra runs as a scheduler defect.

## Cron remains useful, with a different context

Cron entries combine time fields and a command. A user's crontab and a system crontab differ: system formats include an execution user field. Know which file/interface you are editing. Use `crontab -l` to inspect the intended user's existing schedule before changing it, and do not replace an entire crontab merely to add one job.

The job's environment is typically smaller than an interactive shell's. Set a working directory intentionally and use absolute program/script paths. If the script requires Bash, invoke Bash explicitly rather than assuming the scheduler's default shell provides arrays. Capture diagnostics in a protected destination or an implemented notification path; local mail must actually be configured if it is your failure-reporting mechanism.

A conceptual entry for a deployed, reviewed script might be:

```cron
*/5 * * * * /usr/bin/bash /opt/dispatchdesk/maintenance/run-inventory.sh
```

This is a format example, not a ready installation: the wrapper must exist, choose its configuration/paths, prevent overlap, and report failure. Cron does not inherently stop the previous process before the next matching minute. Nor does an ordinary cron entry promise catch-up for every time the host was off. Implementation-specific extensions differ; the upstream Cronie manual is particularly relevant to Fedora/RHEL and is not proof that Ubuntu's packaged cron implements every extension. [Crontab format manual](https://man7.org/linux/man-pages/man5/crontab.5.html).

## Lock the resource, not just the schedule

For a single trusted local host, `flock` can provide an advisory lock shared by cooperating invocations. All contenders must use the same lock identity and retain it for the protected operation. A lock on a local file does not protect an independent lock on another host. Filesystem and network-mount semantics matter; do not assume a local design provides distributed coordination.

The following complete Bash practice script accepts a reader-owned directory and holds a lock while simulating three seconds of maintenance. Save it as `lock-lab.sh` outside that directory:

```bash
#!/usr/bin/env bash
set -u
if (( $# != 1 )) || [[ ! -d "$1" || -L "$1" ]]; then
  printf 'usage: bash lock-lab.sh OWNED_DIRECTORY\n' >&2
  exit 2
fi
exec 9>"$1/maintenance.lock" || exit 1
if flock --nonblock --conflict-exit-code 75 9; then
  printf 'lock acquired\n'
else
  lock_status=$?
  printf 'lock unavailable, status=%s\n' "$lock_status" >&2
  exit "$lock_status"
fi
sleep 3 || exit 1
printf 'maintenance simulation finished\n'
```

Use an initially empty disposable directory. Start one invocation in a terminal; after it prints `lock acquired`, run another against the same directory in a second terminal. The second should refuse immediately with status 75, which this script intentionally reserves for lock contention. The first releases its lock when the owning descriptor closes on process exit. Run another after completion to confirm acquisition works again. [Util-linux flock manual](https://man7.org/linux/man-pages/man1/flock.1.html).

Keep the lock file in a stable, trusted location. Do not delete it to “clear” an active lock: replacing its directory entry can let another invocation lock a different inode while the first still holds the old one. Descendants inheriting the descriptor can extend lock lifetime; ensure your process tree and protected-work lifetime agree. After all lab invocations have exited, remove the known `maintenance.lock` and use `rmdir` on the now-empty practice directory.

For Chapter 18's inventory, place a production lock outside the input population so it is not hashed as configuration. A lock prevents cooperating concurrent collectors; it still does not freeze independently changing input files. Scheduling, serialization, and a stable snapshot are three distinct requirements.

## Limits bound resources and expose leaks

A process can exhaust descriptors while the host has free memory. Descriptors represent sockets, files, pipes, and other open resources. A soft descriptor limit bounds what the process can currently open; a hard limit constrains raising the soft limit without suitable privilege. Inspect the service's actual inherited/configured limit instead of changing your interactive shell and assuming the service follows.

```bash
ulimit -Sn
ulimit -Hn
```

These Bash observations describe the current shell context. A service manager can set its own limits, such as systemd `LimitNOFILE=`. Limits have resource-specific semantics: the Linux process-count limit is associated with real user identity and counts threads, rather than simply counting all service names. [Linux resource-limit interfaces](https://man7.org/linux/man-pages/man2/getrlimit.2.html).

A higher limit can be justified by measured legitimate concurrency, but it can also hide a leak until the failure becomes larger. Bound request concurrency, close resources reliably, and measure growth over time. CPU/memory/task restrictions through service cgroups add another layer, developed in later container and performance chapters. A timeout bounds elapsed waiting only when the operation can be interrupted and recovered safely; it does not guarantee external side effects were undone.

## Recover overlapping maintenance and descriptor exhaustion

Suppose Harbor's inventory runs overlap and reports become inconsistent. Record scheduler entries, invocation start/finish times, process ownership, and report publication times. Stop introducing new runs while allowing or deliberately stopping known current work. Preserve the reports as evidence. Add a shared local lock and test contention, then verify that the script's inputs are stable enough for its purpose. Increasing the schedule interval may reduce overlap frequency but does not establish serialization.

If the notification worker instead reports too many open files, inspect its actual descriptor limit and descriptor population over time. Distinguish a bounded traffic spike from monotonically accumulating sockets. In this scenario a provider error path fails to close responses; each retry consumes another descriptor. Restarting restores headroom temporarily, but raising the limit alone delays the same failure.

Recover by containing new work and restarting through the service's safe drain/recovery path if needed. Preserve pending notification state and reconcile ambiguous provider outcomes. Repair resource ownership in the client error path, test repeated failures with stable descriptor counts, and then size the limit for measured legitimate load. Scheduling another periodic restart would mask the leak and add avoidable interruption.

## Exercises and takeaways

1. Parse the UTC calendar and explain its actual next times. Guidance: account for current time, then distinguish eligibility from randomized execution delay.
2. Describe catch-up requirements after a host is off for two hours. Guidance: a timer activation is not twelve or twenty-four reconstructed business reports; the job must retain its reporting cursor if every interval matters.
3. Run the lock contention lab. Guidance: prove refusal while held and acquisition after completion; never remove a held lock file as recovery.
4. Draft a descriptor-exhaustion investigation. Guidance: inspect the service context, classify resources, observe growth, and fix leaks before choosing a justified new limit.

Schedules define eligibility, locks coordinate cooperating work, and limits bound resources. Design their failure and recovery semantics together, then observe successful completion rather than merely the presence of a schedule. Continue to [Volume 3](../03-networking-and-traffic/README.md) to follow packets, naming, transport, and traffic through the service path.
