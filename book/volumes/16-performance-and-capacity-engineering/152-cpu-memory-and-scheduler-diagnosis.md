---
book: The Complete DevOps Engineering Book
volume: 16
volume_title: "Performance and Capacity Engineering"
chapter: 152
title: "CPU, Memory and Scheduler Diagnosis"
slug: cpu-memory-and-scheduler-diagnosis
status: complete
summary: ../../_ai/chapter-summaries/152-cpu-memory-and-scheduler-diagnosis.md
---

# Chapter 152 — CPU, Memory and Scheduler Diagnosis

**Section outline:** compare utilization with blocked work; gather bounded host/process evidence; inspect resource limits; profile a controlled CPU-versus-wait example; choose recovery that fixes the measured constraint.

Prerequisite: [workload models](151-workload-models-and-measurement.md). Keep arrival rate, completed work and residence time visible while inspecting host resources.

## Utilization, contention and pressure

Harbor's expanded fictional peak now reaches forty orders per second after a new customer integration. Acceptance latency rises while the host's average CPU chart reads fifty percent. That percentage alone cannot decide whether Harbor needs a larger VPS. A single serial process may saturate one core on a two-core machine; processes may wait for disk or database connections; a container may exhaust its CPU quota while the host remains partly idle.

Utilization reports how much capacity a resource spent doing accounted work. Contention reports competition for access. Pressure reports time in which work cannot progress because a resource is unavailable. These related observations answer different questions. A busy CPU can be productive and meet latency targets. A modest utilization figure can coexist with long waits at a constrained resource or an imbalanced scheduler placement.

Inspect the measurement scope. Host CPU percent, one process's CPU percent and a cgroup's quota fraction have different denominators. A multithreaded process may report more than one hundred percent in a one-core-based display mode. A host aggregate can hide one overloaded core. A guest's CPU accounting can also include time the virtualized environment could not supply execution; investigate virtualization and provider evidence when this appears, rather than assuming application code suddenly became expensive.

Load average is not CPU percent. It reflects runnable and certain uninterruptible tasks under Linux's accounting, so disk-related waits can raise load without fully occupying CPU. Compare it with runnable-task counts, CPU states, storage latency and pressure. “Load above core count” is an investigation clue, not an automatic instruction to add CPU.

Memory has similar denominator traps. Used memory includes useful caches; little completely free memory can be normal. Available memory, reclaim activity, swap traffic, working-set growth and application latency give it meaning. A process's resident size is not the same as private allocated application objects; shared mappings and caches affect interpretation. A stable resident size can hide heavy allocation and garbage-collection work, while a growing cache can be intentional until its bound is exceeded.

## A bounded host inspection

On the affected Linux host, gather observations as an ordinary operator first. The following procps commands apply to Ubuntu 24.04, Fedora 44 and RHEL 9-compatible hosts when installed. Ubuntu packages these common tools through `procps`; Fedora/RHEL commonly use `procps-ng`, with actual package availability subject to their repositories. Check the installed commands' help and version; do not change packages in the middle of an incident unless missing evidence justifies it.

```bash
uptime
free -h
vmstat 1 6
```

Uptime provides time/load context. Free's human-readable display distinguishes memory categories; use the available-memory field rather than treating cache as waste. Vmstat samples at one-second intervals for six reports. Its first ordinary report includes averages since boot for relevant activity fields; subsequent reports describe the interval. Avoid comparing the first row directly with the later rows as if all represented one-second samples.

Read runnable work, blocked work, swap activity and CPU categories together. A rise in runnable work with high execution utilization suggests CPU competition. A rise in blocked work with storage wait suggests another path. Swap traffic can identify memory pressure, but absence of swap traffic does not prove safe memory headroom: swap may be disabled or a cgroup memory limit may trigger failure first.

Inspect per-thread process activity for an actual observed PID:

```bash
service_pid=$(systemctl show dispatchdesk-api.service --property=MainPID --value)
if [ "$service_pid" -gt 0 ] 2>/dev/null; then
  top -b -H -d 1 -n 3 -p "$service_pid"
else
  printf '%s\n' 'No running MainPID for the stated service.'
fi
```

The unit name must be the real systemd API unit; this block assumes it exists and does not create it. `systemctl show` requests the MainPID property without human-oriented surrounding output. The guard avoids accidentally treating PID zero as the intended service. Top's batch mode produces terminal-safe reports, thread mode distinguishes execution threads, delay sets one-second sampling, count bounds reports and PID selection narrows scope. Inspect current PID identity and start time if the service restarts during collection; PID reuse can otherwise confuse a saved artifact.

On a host with Pressure Stall Information enabled, read:

```bash
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
```

These interfaces report resource-related stalls over recent windows and cumulative time. Their availability depends on kernel configuration and environment. System-level CPU `full` does not carry the same meaningful interpretation as memory/IO full-stall measurements; consult the kernel documentation before plotting it as a universal threshold. Compare host pressure with the workload's own cgroup pressure when several tenants share the machine.

These commands are read-only. They do not attach a profiler, terminate processes or change limits. Collecting a process command line or environment can expose credentials, so avoid indiscriminate diagnostic archives. Record the timestamp, host identity, workload revision and sampling window with the observations.

## Resource limits and working-set evidence

A container limit can be the binding constraint even when the host has room. Find the process's cgroup membership through `/proc/<observed-pid>/cgroup` and the active mount/layout, then inspect the documented cgroup v2 controller files for that actual path. Do not guess a container-ID path from an old runtime tutorial. Cgroup namespaces, service managers and runtime versions change how the path appears.

For cgroup v2, CPU statistics and configured quota, memory current usage and memory events give scope-specific evidence. Compare changes over a defined interval, because event counters are cumulative. A memory kill counter increase near a process restart is more useful than a current memory value after the victim has disappeared. A quota-throttling increase suggests execution was constrained under that group's policy, not necessarily that the entire host ran out of CPU.

Do not edit cgroup files behind the orchestrator's back. Change the owning systemd unit or workload specification through the reviewed deployment path. If a temporary limit increase is the justified mitigation, preserve its reason and expiry, measure other tenants' impact and incorporate the intended durable setting into source. Resource governance is an ownership contract as well as a performance knob.

A working-set investigation asks what must remain resident for useful work. For DispatchDesk, API code, active connections, current request bodies and frequently accessed database pages have different growth patterns. A 64-KiB body bound does not bound memory if thousands of queued bodies remain resident simultaneously. Use the concurrency estimate from Chapter 151 and actual allocation measurements. Queue durable references rather than copying whole payloads into every worker's memory when the design permits it.

## Profiling CPU work versus waiting

A profile attributes resource activity to code paths. CPU profiling cannot by itself explain all elapsed time, because a blocked thread uses little CPU while its request waits. An allocation profile explains object creation and retention under its profiler's semantics; it is not automatically a whole-process resident-memory measurement. Choose the profile that can disprove the current hypothesis.

This complete Python teaching program compares elapsed time with process CPU time without installing a profiler or contacting a dependency. Save `cpu_or_wait.py` in a user-owned scratch directory:

```python
import hashlib
import time

def measure(name, work):
    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    work()
    elapsed = time.perf_counter() - wall_start
    cpu = time.process_time() - cpu_start
    print(f"{name}: elapsed={elapsed:.3f}s process_cpu={cpu:.3f}s")

def compute():
    payload = b"dispatchdesk-synthetic-payload"
    for _ in range(200000):
        payload = hashlib.sha256(payload).digest()

def wait():
    time.sleep(0.5)

measure("bounded hash computation", compute)
measure("simulated dependency wait", wait)
```

Run `python3 cpu_or_wait.py` as an ordinary user. The hash loop intentionally consumes bounded CPU; the sleep intentionally waits. Expect different ratios, but do not treat a particular duration as portable: hardware, virtualization, runtime and competing work vary. The printed values are actual observations only when the reader executes the program. This exercise is not a benchmark of DispatchDesk and its sleep is not a database simulation with realistic behavior.

In a real Python service, a sampled CPU profile showing JSON transformation dominating execution supports optimizing that path or parallelizing appropriately. A PHP-FPM pool may have idle-looking host CPU while all request workers wait on a slow database. A Go service may have many goroutines waiting on one constrained connection pool. A Node.js service may have one event loop occupied by synchronous CPU work while the host's other cores remain idle. Language-specific concurrency and runtime lifecycle matter; adding memory or replicas without understanding the path can move the bottleneck rather than remove it.

Attach production profilers under a reviewed scope and overhead budget. Confirm symbols, permissions, collection duration and artifact sensitivity. Fedora/RHEL SELinux and Ubuntu AppArmor can restrict attachment or file access. Investigate actual policy and profiler requirements; do not globally disable protection to obtain a graph. If a profiler cannot run safely during the incident, use existing metrics, trace timing and a reproduction environment first.

## Diagnosis, recovery and verification

Suppose Harbor's one API thread consumes nearly one core while other cores are idle, and traces show local serialization dominating latency. More cores on the same host might not help that single execution path. Reduce serialization work, cache a safe derived representation or use an appropriate worker/process model, then retest the same arrival stream and correctness checks. Compare CPU per completed order and tail latency rather than only total CPU percent.

In another incident, memory events show repeated limit hits after increasing worker concurrency. Request throughput briefly improves, then processes restart and backlog grows. Recover by reducing in-flight work to a known sustainable level, preserving queued intent and investigating retained allocations or payload duplication. Raising the memory limit can be a temporary mitigation only when host headroom and other workloads permit it. Verify stable process lifetime, bounded memory growth and declining oldest-work age.

If CPU stays low while acceptance waits, inspect dependency acquisition and network/storage timing. A restart may release leaked resources but erases some evidence and can repeat the problem. Preserve a bounded snapshot first when feasible, apply the narrow recovery and confirm actual order outcomes. Failure diagnosis succeeds when a resource observation connects to the customer-visible boundary through a mechanism.

Exercises: explain fifty-percent host CPU with one saturated thread on two cores; identify why vmstat's first row differs; calculate retained payload bytes for 1,000 concurrent 64-KiB bodies; distinguish a memory-limit kill from host free-memory exhaustion. Answer guidance: denominators and serial execution, since-boot accounting, roughly 62.5 MiB before objects/overhead, and scope-specific memory events establish the distinctions.

## Takeaways

- Anchor host diagnosis to user-visible delay and completed useful work; utilization alone cannot identify the bottleneck.
- Compare host, process, thread and cgroup scopes because each has a different denominator and limit.
- Use runnable and blocked work, PSI, CPU throttling and memory events together to distinguish execution contention from waiting and limit failures.
- Compare cumulative counters over a defined interval and discover the real cgroup path before interpreting container limits.
- Change resources through their owning service or deployment specification, then verify stable operation and customer outcomes.

Sources inspected 2026-10-01: [kernel PSI](https://docs.kernel.org/accounting/psi.html), [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html), [top manual](https://man7.org/linux/man-pages/man1/top.1.html) and [vmstat manual](https://man7.org/linux/man-pages/man8/vmstat.8.html). Online Python profile documentation retrieval failed; no profile-specific CLI is taught from that failed source. Host diagnostics, Python demonstration and production profiling were not executed during authoring.
