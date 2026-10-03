---
book: The Complete DevOps Engineering Book
volume: 4
volume_title: "VPS and Server Operations"
chapter: 40
title: "VPS Incidents and Capacity"
slug: vps-incidents-and-capacity
status: draft
summary: ../../_ai/chapter-summaries/040-vps-incidents-and-capacity.md
---

# Chapter 40 — VPS Incidents and Capacity

## Start with impact, then narrow the cause

During a DispatchDesk outage, a useful first question is whether customers can still accept orders safely. A process can answer `/healthz` while the database pool is exhausted, or `/readyz` can fail because PostgreSQL is unreachable. A full disk can make order transactions fail while the operating system still responds to SSH. Define the customer-visible symptom, start time, affected requests and current data risk before changing the host.

An incident lead should coordinate diagnosis, assign an operator, preserve a timeline and communicate the known impact. Keep one person responsible for the next decision rather than running unrelated commands from several sessions. Record timestamps, commands and material output, but redact credentials, customer data, authorization headers and private addresses before sharing. The objective is to restore safe service and protect accepted data, then investigate root causes after immediate risk is controlled.

## Establish a read-only baseline

Begin with low-impact observations from an authorized shell. These commands do not restart or modify services:

```bash
date --iso-8601=seconds
uptime
free -h
df -h
df -i
systemctl --failed
sudo ss -ltnp
```

Compare current output with a recent healthy baseline and the time of the customer symptoms. `uptime` shows load averages, which are not CPU percentages; runnable and uninterruptible tasks both contribute. `free` reports memory counters whose meanings differ from simplistic “used versus free” interpretations because Linux uses reclaimable caches. `df -h` and `df -i` show block and inode capacity by mounted filesystem. A filesystem can have free bytes but no inodes, or the reverse. `systemctl --failed` identifies failed units but not every unhealthy application. Listener output establishes sockets, not whether a provider firewall permits traffic.

Collect short interval samples when a trend matters:

```bash
vmstat 1 5
iostat -xz 1 5
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
```

The first `vmstat` report summarizes activity since boot; later reports describe each interval. `iostat` similarly presents an initial since-boot view before interval reports on common versions. Check tool availability and local manual pages. High device utilization alone does not prove the disk is saturated for this workload; correlate throughput, latency, queueing and application waits. Pressure Stall Information (PSI), when available, reports time tasks spend stalled on CPU, memory or I/O. Trends and interval changes matter more than a single sample.

Inspect application logs for the same period and compare request rate, error rate, latency percentiles, readiness transitions, database pool wait and notification backlog. For a PostgreSQL system, a bounded view of active sessions and wait events can help distinguish query execution from lock, I/O or client waits:

```sql
SELECT pid, application_name, state, wait_event_type, wait_event
FROM pg_stat_activity
WHERE state <> 'idle'
ORDER BY wait_event_type NULLS FIRST, pid
LIMIT 40;
```

Run this as an authorized observability role. It omits query text and customer values; `application_name` should be set by clients and still reviewed for sensitive labels. A wait event is a clue, not a diagnosis. A process with an active query and a non-null wait event can be blocked on another resource. Check transaction age and blocking relationships using a reviewed query before terminating sessions. Killing a session may roll back work and should have a clear owner and reason.

## Follow symptoms to the owning layer

If remote clients cannot connect, trace DNS, provider ingress, host firewall, listener and proxy routing in order. Preserve the last known-good firewall policy and recovery console access. A successful loopback request proves only the local service path. Chapter 30 develops the network-layer sequence.

If Nginx returns upstream errors, inspect its error log, listener address and application service state. If the application responds but order acceptance fails, inspect PostgreSQL connectivity, pool waits, free storage, transaction errors and lock waits. If only notifications lag, inspect durable pending intent, worker ownership, retry delays and provider outcomes; do not “fix” a queue by deleting records. If all requests slow while CPU is busy, identify the consuming process and workload before resizing. If memory pressure or OOM kills rise, check process resident memory, swap activity, cache growth, recent deployment changes and kernel logs. A reboot may temporarily clear a symptom while erasing useful evidence and interrupting recovery.

If a filesystem is nearly full, identify which mount and directory are growing. Logs, database WAL, temporary files and backup staging have different owners and cleanup procedures. Do not remove PostgreSQL WAL, database files, unknown files in `/var/lib` or the only recovery copy. Rotate or truncate logs only through the owning service's supported procedure after confirming where data is stored. If bytes are available but inodes are exhausted, find the source of many small files and fix its lifecycle.

If load average is high but CPU is mostly idle, tasks may be blocked on I/O or another uninterruptible wait. If CPU is saturated but request rate is unchanged, compare process-level CPU, background jobs, query plans and recent code changes. If the provider reports low host utilization while customers see errors, examine the application pool and database constraints; virtual machine averages can hide a short saturation period. Correlate independent signals before assigning a cause.

## Stabilize before optimizing

Choose the smallest reversible action that reduces customer impact while preserving data. Options may include disabling a newly introduced nonessential feature, reducing background concurrency, draining a broken API instance, restoring a known-good application release or moving to a larger host through a tested provider operation. Each action can trade one risk for another. Lowering worker concurrency may reduce database pressure but increase notification delay. Restarting PostgreSQL can interrupt active transactions and delay recovery. Increasing timeouts can preserve slow work but also occupy more connections.

Before restarting a service, save relevant logs and current process state, confirm what work is durable and check the unit's shutdown timeout. Before resizing or migrating, confirm provider disk and network behavior, backups and the expected reboot or address change. Before rolling back an application release, check schema compatibility. Do not make several changes at once unless the incident requires immediate containment; preserve enough separation to learn which action affected the symptom.

Communicate an update with current user impact, mitigation in progress, known data integrity status, next checkpoint and owner. If the answer is unknown, say what evidence is being collected. Do not promise a restoration time from a dashboard alone. After service recovers, verify synthetic acceptance and retrieval, the paired notification intent, readiness, public routing and notification backlog before declaring the incident stable.

## Turn incidents into capacity decisions

Capacity planning uses observed workload over time, not a CPU snapshot during one outage. Track request rate, order transaction latency, database connections, lock and I/O waits, memory pressure, filesystem growth, network throughput, notification backlog and provider limits. Retain enough history to see daily and seasonal peaks. Define a warning threshold with time to act, a critical threshold tied to customer impact, and a response owner for each. Alert on symptoms and resource causes together.

Estimate when the next constraint arrives using a measured growth rate and an explicit safety margin. For example, if database storage grows by 12 GiB per month and 48 GiB remain usable after a recovery reserve, the simple estimate is four months before reserve. This assumes steady growth and ignores WAL, index maintenance, temporary files, backup staging and workload changes, so it is a planning signal rather than a deadline. Recalculate with actual data and schedule capacity work before the reserve is threatened.

Scale vertically when the bottleneck is a resource that the provider can add and the resulting host still meets cost and recovery needs. Separate the database or cache when contention, maintenance or failure-domain requirements justify the new network and operating burden. Add application hosts when the service is safe to run with shared authority and the router can remove failed instances. Revisit [Chapter 39](039-adding-a-second-server.md) before using more API capacity to address a database bottleneck. A larger VPS does not fix an unbounded query, leak, retry storm or missing index.

## Review the incident

After stabilization, build a timeline from alerts, requests, deployments and operator actions. Identify contributing conditions, not only the last failed component. Ask what made the incident detectable, what made diagnosis slow, which recovery step was missing and how the system behaved under retries. Assign actions with owners and dates: improve an alert, cap a pool, validate disk-growth forecasts, rehearse restore or test a shutdown path. Verify that actions reduce risk and update the runbook. Avoid blaming an individual for acting on incomplete evidence when the system did not make the safer choice clear.

## Exercises and review questions

1. Customers see 502 responses, but loopback `/healthz` succeeds. Trace the proxy, listener, readiness and application dependency evidence you need.
2. `df -h` reports 90% use and `df -i` reports 100% inode use. What classes of files could explain the difference, and which deletion actions are unsafe?
3. PostgreSQL has many active sessions waiting on `Lock`. What evidence would you collect before canceling or terminating any backend?
4. Write a short customer update that distinguishes known impact, unknown data risk, mitigation and next update time.
5. Estimate when a filesystem will reach its recovery reserve from a month of observed growth. List assumptions that make the estimate uncertain.

Good incident response protects customer data while reducing impact, and good capacity planning turns repeated pressure into an intentional architecture decision. Harbor can remain on a VPS while its measured workload and recovery contract fit; the next volume compares container workflows that can support this service on several hosting paths.

## Sources and verification

The Linux kernel's [PSI documentation](https://docs.kernel.org/accounting/psi.html), upstream `vmstat` and `iostat` manuals, and PostgreSQL 18 [monitoring](https://www.postgresql.org/docs/current/monitoring.html) and [statistics](https://www.postgresql.org/docs/current/monitoring-stats.html) documentation were inspected on 2026-10-02. The SQL query is read-only and was syntax-reviewed but not run against a database. Operational commands are observational; no VPS incident or resource change was performed. Independent review is pending.
