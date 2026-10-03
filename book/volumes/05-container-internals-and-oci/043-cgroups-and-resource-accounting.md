---
book: The Complete DevOps Engineering Book
volume: 5
volume_title: "Container Internals and OCI"
chapter: 43
title: "Cgroups and Resource Accounting"
slug: cgroups-and-resource-accounting
status: draft
summary: ../../_ai/chapter-summaries/043-cgroups-and-resource-accounting.md
---

# Chapter 43 — Cgroups and Resource Accounting

## Account for groups of processes

Namespaces change what a process can see; control groups (cgroups) organize processes and account for or constrain selected resources. A container runtime places the workload in a cgroup so the host can observe its CPU and memory use and apply policies. A systemd service can also run in its own cgroup. This lets an operator reason about a service as a group even when it starts child processes.

Cgroups are hierarchical. A child group operates within limits and protections imposed by its ancestors. A child configured for a large memory limit cannot consume more than the parent permits. Multiple child limits may be overcommitted relative to available host capacity, so configured limits are not the same thing as reserved physical resources. Cgroups do not create extra CPU, memory or I/O bandwidth.

Linux systems may use the unified cgroup v2 hierarchy or an older cgroup v1 arrangement. The interfaces and files differ. Check the host rather than assuming that an example file exists. A container engine may also abstract away the kernel file paths; use its inspection tools alongside host-level metrics.

## CPU weight and maximum bandwidth

In cgroup v2, `cpu.weight` influences relative CPU distribution among sibling groups that compete for CPU. It is a weight, not a dedicated percentage or guaranteed core reservation. A higher weight matters during contention; it does not make a workload run faster when no CPU is available or remove parent-level constraints.

`cpu.max` sets a bandwidth ceiling over a period. A group that uses its quota early can be throttled until the next period even while another CPU appears idle, depending on hierarchy and contention. The `cpu.stat` file records usage and, when the controller is enabled, periods and throttling counters. Rising throttling correlated with application latency can indicate a tight quota; high CPU usage without throttling points toward different capacity or code causes.

For a systemd service, administrators can define CPU controls such as `CPUQuota=` through the unit. For a container, engine options map to cgroup controls. Do not edit a runtime-owned cgroup file behind the engine's back: the runtime or systemd may overwrite the change, and it may not survive restart. Set resource policy through the component that owns the workload configuration.

## Memory limits and failure behavior

`memory.current` reports memory charged to a cgroup and descendants. `memory.max` is a hard limit; when usage cannot be reclaimed sufficiently, allocations can fail and the cgroup's OOM handling may kill a process. This can leave an application unavailable while the host itself continues running. The default `max` means no explicit ceiling at that cgroup, not unlimited physical memory.

`memory.high` is a pressure and throttling boundary rather than the same hard-stop behavior as `memory.max`. Crossing it can cause processes to do direct reclaim and slow down. `memory.events` provides counters such as `high`, `max`, `oom` and `oom_kill`. Check whether counts increase during the incident and whether hierarchical totals include descendant events. Compare current and peak use with application-level heap metrics, page cache, socket buffers and host pressure. Memory accounting is broad but not a promise that every kernel allocation is charged identically on every version.

Set limits from measured workload and leave room for transient peaks. A low limit may convert a system-wide pressure event into a repeatable per-container kill; that can be a useful isolation boundary only when the service recovers correctly. A high limit on every container can overcommit the host and move the failure to the host OOM killer. The application should handle connection reset, process restart and replay according to its durable state contract.

## I/O and process-count controls

The cgroup v2 I/O controller can cap bytes or operations per second for a device using `io.max`, when the controller and device are available. An I/O cap can protect neighbors while increasing the limited workload's latency. It is not a disk scheduler or an end-to-end storage guarantee. Monitor device latency, queueing, application waits and cgroup-level statistics before changing it.

The `pids` controller limits tasks created in a cgroup. Linux counts task IDs, including threads, so a workload with many threads can reach the limit even when its process list looks small. `pids.current`, `pids.max` and `pids.events` help diagnose creation failures. A limit can prevent a fork bomb from exhausting all host process slots, but setting it below the application's normal thread and subprocess peak can cause failed requests or startup loops.

Resource controls have operational costs. A strict CPU quota can make latency burstier; a memory ceiling can trigger OOM events; an I/O cap can delay database commits; a task cap can prevent workers from starting. A control is useful when the team knows how it behaves at the boundary and has alerts and recovery behavior for that condition.

## Inspect the effective group

Start from a host PID for the workload and inspect its cgroup membership and the host's mounted hierarchy. This snippet reads files only:

```bash
read -r -p 'Host PID to inspect: ' workload_pid
ps -p "$workload_pid" -o pid=,ppid=,comm=,lstart=
cat "/proc/$workload_pid/cgroup"
findmnt -t cgroup,cgroup2
```

Confirm the PID still belongs to the process you intend to inspect. On a unified cgroup v2 host, `/proc/<pid>/cgroup` commonly has a `0::/path` entry. The visible path is relative to the cgroup hierarchy and may be interpreted through a cgroup namespace. Locate the cgroup mount and then inspect the corresponding directory. Read the parent groups too because their limits can constrain the workload.

For a systemd-managed service, inspect effective properties and resource counters through systemd:

```bash
systemctl show dispatchdesk.service \
  -p ControlGroup -p CPUWeight -p CPUQuotaPerSecUSec \
  -p MemoryCurrent -p MemoryHigh -p MemoryMax -p TasksCurrent -p TasksMax
```

Not every property is available on every systemd version, and an empty or infinity-like value does not mean the entire host has spare capacity. Compare the unit's cgroup with ancestor groups and the machine's overall usage. For an engine-managed container, record its configured limits and runtime-reported usage, then correlate them with the same host interval. Sampling once can miss short CPU throttling or memory spikes.

## Translate a limit event into a service symptom

Suppose DispatchDesk's API latency rises while the host CPU remains available. Its cgroup `cpu.stat` shows rapidly increasing throttling. The service may be constrained by `cpu.max` or a parent quota. Compare its configured quota, sibling workloads, request rate and per-request CPU before increasing the quota. If another process is consuming the host, changing the API quota may worsen contention. If the limit was set deliberately to protect the database, scale or reduce work with an explicit capacity decision.

Suppose one container restarts while host memory looks acceptable. Check the cgroup's `memory.events`, peak memory, exit reason and engine event history. A local `oom_kill` counter can reveal a scoped OOM event hidden by a healthy host average. Confirm whether the application committed accepted orders before termination and whether its retry behavior preserves the acceptance invariant. Raising the limit may be appropriate, but first identify a leak, unbounded cache or workload surge.

Suppose worker creation fails after adding concurrency. Compare thread count with `pids.current` and inspect `pids.events`. The issue may be a task limit, not an operating-system-wide process shortage. Reduce concurrency or adjust the intended cgroup policy after validating host capacity. Do not remove a limit without considering the other workloads it protects.

## Exercises and review questions

1. Explain the difference between `cpu.weight` and `cpu.max`. Which would you inspect for proportional fairness, and which for quota throttling?
2. `memory.current` stays below `memory.max`, but `memory.events` shows repeated `high` events. What behavior might users observe?
3. Why can `pids.max` be reached by a service with only a few process IDs visible in a simplified listing?
4. A container has no memory limit while its parent slice has one. Which effective boundary matters?
5. Design an alert that combines cgroup OOM or throttling evidence with DispatchDesk request latency instead of paging on a cumulative counter alone.

Cgroups explain how a process group consumes shared host resources and how the host can apply limits. Read the effective hierarchy and correlate counters with customer impact before tuning. The next chapter turns to container images, whose content can be identified and promoted independently of these runtime controls.

## Sources and verification

The Linux kernel's [cgroup v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html) and OCI [Linux configuration](https://specs.opencontainers.org/runtime-spec/config-linux/) were inspected on 2026-10-02. The shell snippet passed syntax checks but was not pointed at a live DispatchDesk process; no cgroup files were changed. Kernel controllers, mount layout and systemd property support depend on the target host. Independent review is pending.
