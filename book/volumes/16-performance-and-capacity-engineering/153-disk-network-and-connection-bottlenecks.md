---
book: The Complete DevOps Engineering Book
volume: 16
volume_title: "Performance and Capacity Engineering"
chapter: 153
title: "Disk, Network and Connection Bottlenecks"
slug: disk-network-and-connection-bottlenecks
status: draft
summary: ../../_ai/chapter-summaries/153-disk-network-and-connection-bottlenecks.md
---

# Chapter 153 — Disk, Network and Connection Bottlenecks

**Section outline:** distinguish device latency from bandwidth; inspect bounded disk and socket evidence; account for connection pools and descriptors; localize shared-state limits; recover without multiplying demand.

Prerequisite: [CPU and memory diagnosis](152-cpu-memory-and-scheduler-diagnosis.md). Low CPU does not establish spare application capacity when requests wait for another resource.

## Latency, bandwidth, queues and IOPS

DispatchDesk commits an order and notification intent before acknowledging acceptance. The durable write path therefore matters even when request bodies are small. A storage device can have ample sequential bandwidth while small synchronous commits encounter unacceptable latency. Conversely, a backup can consume bandwidth without every database operation being latency-bound. Identify the access pattern before buying a faster volume.

IOPS counts operations per second; bandwidth measures bytes per second; latency measures time per operation. Queue depth describes outstanding work. Their relationship depends on request sizes, concurrency, merging, caching, filesystem behavior and the device. Ten thousand 4-KiB operations transfer much less data than ten thousand 1-MiB operations. A provider's nominal capacity numbers require their stated conditions and may include account or volume limits; verify current provider documentation for a real purchase.

The application also sees a different boundary from the device. A database query can wait for a lock before issuing IO. Filesystem caching can satisfy reads without device activity. A transaction may write several records then wait for durability. A trace showing a slow database operation should lead to database wait evidence and storage observations, not an immediate assumption that every millisecond belongs to the disk.

On the affected host, use a bounded sysstat sample after confirming the package is installed. Ubuntu 24.04 uses `sudo apt-get install sysstat`; Fedora 44 and RHEL 9-compatible systems use `sudo dnf install sysstat` from their enabled repositories. Installation changes package state and requires administrator privileges. It does not automatically authorize enabling historical collection services; live iostat use is sufficient for this exercise.

```bash
iostat -xz -y 1 5
```

Extended output exposes device-level detail; suppressing inactive devices reduces noise; omitting the since-boot first report with `-y` makes the interval sample easier to compare. The one-second interval and five-report count bound collection. Inspect the installed release's column definitions: device metrics and reported names can evolve. A percent-utilization field alone is not a universal saturation test for modern parallel devices. Compare latency, outstanding work, achieved throughput and the application's affected boundary.

Map the reported device to the actual database filesystem. Logical volumes, encrypted mappings and virtual disks can add layers. Observing one physical device does not prove which process generated the work. Compare the incident window with database activity, backups and other colocated jobs. A noisy neighbor or scheduled snapshot can create a shared-storage constraint even when the API release is unchanged.

## Network and connection evidence

Network bandwidth and request latency are also different. A small request can wait on DNS, connection establishment, TLS, retransmission or remote processing without moving many bytes. A high-throughput stream can perform efficiently at substantial link utilization. Examine the connection path and operation timing before equating low bytes per second with healthy networking.

On the API host, inspect TCP connections to the conventional PostgreSQL port only if that is the actual configured target:

```bash
ss -tn '( dport = :5432 )'
ss -tin '( dport = :5432 )'
```

`-t` selects TCP and `-n` keeps addresses and ports numeric. The filter selects destination port 5432, not every connection to a database identified by name. `-i` adds internal TCP observations supported by the installed kernel/tool. Run from the application's network namespace or an explicitly equivalent context: the host's socket list can differ from a container's. Process attribution with `-p` may require permission; add it only when needed and avoid exporting sensitive connection metadata broadly.

A send queue can indicate the application or kernel has data waiting to be transmitted or acknowledged under the socket's state. A receive queue can indicate data not yet consumed by the local process. Interpret the actual state and counter definition rather than treating every nonzero queue as loss. Compare RTT and retransmission-related observations across affected connections and time windows. One socket snapshot does not establish a sustained network failure.

Repeated connection creation can amplify network cost. If every order opens a new database connection, authentication and setup become part of every request's work. Pooling can amortize setup but introduces its own queue and concurrency policy. A long-lived connection can also become stale after failover. The application must detect unusable connections and replace them under bounded retry and timeout rules, not retain them forever because pooling is configured.

## Connection pools and file descriptors

A pool limits simultaneous database access from one process. Across replicas, the database sees the sum of all pools plus workers, administrative sessions and other clients. In a fictional expanded Summit scenario, eight API replicas with pools of twenty connections and four workers with pools of ten can request up to 200 connections before administrative reserve. Adding four API replicas increases that potential to 280. If the database's safe workload concurrency was already reached, application scaling worsens contention.

Pool size is not a throughput target. More active sessions can compete for locks, CPU and memory, increasing query duration. A smaller pool can protect the database while increasing local wait; that wait should be bounded and observed. Size the pool from measured query demand and the database's sustainable concurrency, retaining operational reserve for recovery. A connection proxy changes connection management but does not create unlimited database execution capacity.

File descriptors cover more than network connections: open files, sockets and other kernel interfaces consume them. Inspect the running process's actual limits rather than the interactive shell's `ulimit` alone. The process can have been started by systemd or a container runtime with different settings. For the real observed service PID from Chapter 152, inspect `/proc/<pid>/limits` under appropriate access and count entries in `/proc/<pid>/fd` without assuming every descriptor is a socket. A growing count after steady work can indicate leaked files or sockets; a stable high count can be intentional.

Raising a descriptor limit can postpone a leak rather than fix it. Preserve evidence of growth, identify which descriptor types accumulate and repair close/release paths. A restart may be justified containment when the process cannot accept work, but verify that durable orders and queued intent remain safe. Cleanup should close resources through the owning process or reviewed restart, not delete arbitrary `/proc` entries.

## Finding a shared resource ceiling

Use database activity to separate pool acquisition, lock waits and actual query execution. From an authorized read-only PostgreSQL session against the intended database, the following query groups visible sessions without exposing full SQL text:

```sql
SELECT application_name,
       state,
       wait_event_type,
       wait_event,
       count(*) AS sessions
FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY application_name, state, wait_event_type, wait_event
ORDER BY sessions DESC;
```

Run it in psql or the approved database console as an observer account with the permitted statistics visibility. It is read-only but its visibility depends on database privileges and release behavior. Null wait fields do not automatically mean a query is healthy or idle; combine state, transaction age and the application's timing. Set distinct application names for API and worker connections where the driver supports it so session groups correspond to operational roles.

A second bounded query locates long transactions by metadata:

```sql
SELECT pid,
       application_name,
       state,
       now() - xact_start AS transaction_age,
       wait_event_type,
       wait_event
FROM pg_stat_activity
WHERE datname = current_database()
  AND xact_start IS NOT NULL
ORDER BY xact_start
LIMIT 20;
```

This does not terminate sessions. Long transactions can retain locks and interfere with maintenance, but age alone does not prove they are illegitimate. Identify the application owner and operation before cancellation. A maintenance task and a leaked idle transaction require different treatment. Cancellation/termination is a mutating recovery action and belongs in a reviewed runbook with data consequences understood.

Suppose acceptance latency rises across every API replica while CPU remains low. Pool-acquisition duration rises to 500 milliseconds, active database sessions approach the scenario's sustainable limit, and several transactions are idle while still open. The mechanism connects evidence: requests wait for pool slots because transactions hold connections too long. Adding API replicas creates more contenders. Recover by stopping the offending workflow or rolling back the connection-leak release, ensuring transactions are closed and restoring bounded pool demand. Verify acquisition wait falls and order outcomes remain correct.

In a different incident, connection acquisition stays short but query execution and device latency rise during backup. Mitigate by rescheduling or throttling the backup through its own supported controls, while respecting the backup's recovery requirement. A faster application host would not remove the shared storage constraint. Verify with the same arrival stream and compare query latency, storage latency and completion throughput.

## Failure, recovery and scaling implications

An apparent network failure may be database admission failure. “Too many connections” is not repaired by changing the firewall, and a connection timeout does not establish which boundary failed. Inspect listener reachability, authentication/admission errors, pool state and server activity independently. Preserve the exact failure category without dumping credential-bearing connection strings into logs.

If a failover invalidates pooled connections, verify the resolved endpoint, driver reconnection behavior and transaction outcome ambiguity. Retry only according to the idempotency contract. A connection dropping after commit may leave the client uncertain even when the order exists. Query or retry with the same key rather than submitting a new independent order. Resource recovery cannot be separated from business correctness.

Before scaling, identify whether the bottleneck is local or shared. Larger disks, more network capacity, fewer queries per order, shorter transactions, batching and caching are alternatives with different correctness and recovery effects. More application replicas help only when work can be distributed and shared dependencies retain headroom. Separate database and application hosts can remove colocated contention while adding a network path that needs its own failure handling.

Exercises: calculate the total pool ceiling before/after replica addition; explain why low bandwidth can coexist with high synchronous-write latency; distinguish pool wait from executed SQL duration; identify what a steadily growing descriptor count suggests. Answer guidance: 200 versus 280 possible connections, per-operation latency matters independently of transfer size, separate timing establishes the stage, and investigate retained resource types before merely increasing limits.

Review the resource scope, observation interval, connection-budget sum and transaction outcomes before applying a capacity change. The useful capacity is completed correct work, not the largest count of simultaneously open connections.

Sources inspected 2026-10-01: [iostat manual](https://man7.org/linux/man-pages/man1/iostat.1.html), [ss manual](https://man7.org/linux/man-pages/man8/ss.8.html), [PostgreSQL connections](https://www.postgresql.org/docs/current/runtime-config-connection.html) and [statistics](https://www.postgresql.org/docs/current/monitoring-stats.html), whose current pages resolved to PostgreSQL 18. No device sample, database query, connection mutation or load experiment was executed during authoring.

