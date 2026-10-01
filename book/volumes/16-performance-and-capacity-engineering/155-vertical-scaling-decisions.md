---
book: The Complete DevOps Engineering Book
volume: 16
volume_title: "Performance and Capacity Engineering"
chapter: 155
title: "Vertical Scaling Decisions"
slug: vertical-scaling-decisions
status: draft
summary: ../../_ai/chapter-summaries/155-vertical-scaling-decisions.md
---

# Chapter 155 — Vertical Scaling Decisions

## A bigger machine must relieve a named constraint

Harbor runs DispatchDesk on a VPS because two developers can operate one well understood machine, its traffic is predictable, and its cash budget matters. At the canonical typical arrival rate of one request per second and short peaks near ten, a second orchestration platform would not create customer value by itself. A larger VPS might, if measurement shows the first machine lacks a resource that the workload can use. [The load experiment](154-load-testing-with-k6-and-locust.md) supplies a method for establishing that evidence; its synthetic health endpoint is not an order-processing benchmark.

Vertical scaling changes the resources available to one execution unit: more memory, additional cores, faster cores, different storage, or a machine with better network capacity. These changes are related but not interchangeable. A four-core machine can run more independent CPU work than a two-core machine. It cannot make one sequential CPU-bound Python request use four cores automatically. More memory can retain a database working set and reduce reads. It does not repair a query that scans unbounded historical rows for every request. A higher storage limit does not necessarily increase provisioned IOPS.

Start a decision with a sentence that can be disproved: “During the measured ten-request-per-second plateau, API CPU queueing causes the response-time violation; moving from two to four equivalent cores and using four independently scheduled application workers should reduce that queue.” The sentence specifies the limiting resource, workload, change, and result. “The server feels slow” specifies none of them. [CPU and memory diagnosis](152-cpu-memory-and-scheduler-diagnosis.md) and [storage and network diagnosis](153-disk-network-and-connection-bottlenecks.md) explain how to distinguish those constraints.

Headroom is usable capacity before a chosen operational boundary, not the percentage displayed by a dashboard at an arbitrary moment. Suppose measured CPU demand is 0.08 core-seconds per eligible order attempt. At ten attempts per second that component needs 0.8 cores on average. On two available cores it consumes forty percent before background work. If backups consume another core during that same interval, the combined demand is ninety percent of two cores. A four-core machine can separate those demands more comfortably. The calculation assumes comparable CPU performance, stable demand per attempt, and sufficient process parallelism; all three need verification. Retries and rejected requests may have different demand.

Memory headroom needs a different model. Imagine a deliberately fictional measured peak consisting of 1.4 GiB of application resident memory, 1.1 GiB of database resident memory, 0.6 GiB of other services and kernel allocations, and 0.9 GiB of useful reclaimable cache. An eight-GiB machine has room for variation that a four-GiB machine may not. These are illustrative measurements, not DispatchDesk defaults. Reclaimable cache is useful, so subtracting all cache and declaring the remainder “wasted memory” would destroy the rationale for the resize. Record memory pressure, swap activity, OOM evidence and latency together.

## Check limits below the machine boundary

A cloud console can report eight cores while a service cgroup is permitted only one core of CPU time. A container memory limit can remain at 512 MiB after its host doubles in size. In that situation, buying capacity changes the invoice before it changes the application's allocation. The Linux kernel's [cgroup v2 documentation](https://docs.kernel.org/admin-guide/cgroup-v2.html) describes hierarchical controls: a child's allocation remains constrained by its ancestors. A local limit cannot escape a restrictive parent.

Use the read-only process and cgroup inspection procedure from chapter152 to discover the actual service path, then inspect its CPU and memory controls before planning a resize. Do not assume that a path copied from another host names this service. Likewise inspect application worker counts, thread pools and database connection caps. Increasing a worker count is a separate change with its own memory and connection consequences. A PHP-FPM pool with more children can exhaust database connections sooner; a Node.js process with a blocked event loop needs a code or process-concurrency decision; Go goroutines waiting on a tiny database pool do not become useful merely because the host has more cores.

A single-thread bottleneck suggests faster per-core performance or less work per request. Parallel CPU saturation suggests more cores and an appropriate worker model. Memory pressure suggests more memory, smaller working sets, or corrected retention. A leak suggests a repair and bounded restart strategy; a larger machine only lengthens the time to the next failure. Storage queueing suggests investigating the volume and query path before choosing a CPU-heavy machine. These alternatives should appear beside the proposed resize, so the decision remains falsifiable.

## Build a resize record before touching production

A provider-specific resize procedure belongs to the provider's documented compatibility and recovery rules. It is dangerous to translate “change machine size” into one universal shell command. Root-volume type, CPU architecture, driver support, instance-local storage and the provider's stop/start behavior can change the procedure. AWS, for example, distinguishes compatible EBS-backed type changes from cases requiring migration in its [EC2 resize documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-resize.html). This is a compatibility reference, not an instruction to move Harbor onto AWS.

Create the following complete local decision file as `resize-decision.json`. These figures are hypothetical planning inputs; replace them with observations from the actual service. No prices or provider guarantees are implied.

```json
{
  "service": "dispatchdesk",
  "company": "Harbor",
  "constraint": "parallel CPU demand during peak plus backup overlap",
  "current_cores": 2,
  "candidate_cores": 4,
  "peak_attempts_per_second": 10,
  "cpu_seconds_per_attempt": 0.08,
  "background_core_demand": 1.0,
  "target_cpu_fraction": 0.65,
  "requires_worker_change": true,
  "requires_maintenance_window": true,
  "rollback": "restore previous supported size; restore application settings separately"
}
```

Save this complete Python file as `resize_budget.py` in the same directory. It uses the standard library on Ubuntu, Fedora and RHEL; run it as an ordinary user with Python3 installed. It performs arithmetic only, changes no infrastructure and contacts no provider.

```python
import json
from pathlib import Path

plan = json.loads(Path("resize-decision.json").read_text())
work = (plan["peak_attempts_per_second"] *
        plan["cpu_seconds_per_attempt"] +
        plan["background_core_demand"])
for field in ("current_cores", "candidate_cores"):
    cores = plan[field]
    if cores <= 0:
        raise ValueError("core counts must be positive")
    fraction = work / cores
    fits = fraction <= plan["target_cpu_fraction"]
    print(f"{field}: modeled CPU fraction={fraction:.3f}; "
          f"within target={fits}")
print("Model assumes equivalent cores and independently schedulable work.")
```

```bash
python3 resize_budget.py
```

The modeled demand is 1.8 cores, so the candidate has substantially more modeled reserve than the current machine. The script does not predict p99 latency, prove that workers use all cores, or include storage saturation. Keep the file with the measurements that supplied its inputs. Delete the two lab files when no longer useful; they contain planning information rather than service state.

## Downtime, durability and the recovery route

The resize plan must preserve accepted orders and notification intent. A planned interruption can be cheaper and clearer than adding redundant infrastructure for a workload that tolerates the agreed window, but it cannot silently discard acknowledged work. First confirm a recent restorable backup and the application's actual durable storage paths. A snapshot without a restore test is incomplete evidence. If storage lives on the old machine, distinguish keeping that volume from rebuilding the machine with an empty disk.

Before the window, record service version, worker settings, resource limits, database configuration, volume identifiers, firewall rules and routable addresses. Confirm provider compatibility and whether an address changes. Test the candidate with a staging restore if the decision includes architecture or driver changes. Notify the agreed customer-facing channel through the team's established process; this chapter does not authorize sending messages while authoring.

During the window, stop new routing or show the planned unavailable response, let bounded in-flight work drain, and stop the processes cleanly. Verify that background notification work has either completed or remains durably recorded for resumption. Perform the provider's supported resize. On boot, verify mounted volumes before starting the service. A healthy empty database is a more dangerous outcome than a service that refuses to start.

Check readiness, a controlled synthetic order through the durable contract, notification progression, and customer-facing routing. Reconcile the synthetic record and ensure it was not counted as genuine business. Inspect CPU limits and worker counts rather than assuming the new allocation propagated. Re-run a comparable bounded workload while watching error rates, latency, pressure and database waits. Keep the maintenance window open until evidence supports normal operation.

If performance worsens, identify whether the change affected CPU generation, storage, process limits or configuration. Rolling back the machine size does not roll back a changed worker pool. Restore those settings independently. Avoid incompatible database or application schema changes during the same window, because they can make infrastructure rollback misleading. When rollback requires a restore, specify its recovery-point consequence before executing it.

## Diminishing returns and a decision for Harbor

The first resize may buy enough time for Harbor to optimize a query and schedule backups outside peaks. Further resizes can encounter a sequential fraction or shared database lock. If thirty percent of a workflow remains strictly sequential, doubling perfectly parallel capacity cannot double the whole workflow. More memory may have diminishing value once the useful working set already fits. Larger machines also concentrate more work in one failure domain; capacity improvement alone does not improve availability.

Harbor therefore compares three concrete choices: schedule background work and keep the machine; optimize the expensive request path; or resize to create measured reserve while preserving its simple operations. The appropriate choice can combine optimization and a resize. Horizontal replication becomes attractive when the service needs failure tolerance, independent work scales well, and shared-state coordination is designed. It does not follow automatically from the first successful resize.

## Exercises and answer guidance

A two-core service is at fifty percent host CPU, but one application thread is consistently busy and latency rises with concurrency. Would four equivalent cores be your first intervention? The strong answer asks whether that thread is the serial bottleneck, inspects the worker model, and evaluates less work or faster per-core execution. Host-average CPU alone cannot support the purchase.

A resized host has sixteen GiB of memory, yet the container still dies around one GiB. Explain the evidence to collect. Inspect the actual container and ancestor memory limits, OOM events and application allocation trend. A host resize cannot override a lower enforced limit; a leak can survive a corrected limit.

Write Harbor's rollback acceptance criteria. Include preserved durable orders, mounted original storage, correct worker configuration, readiness, one reconciled synthetic transaction and the notification backlog trend. “The machine boots” is insufficient.

## Takeaways and verification

Vertical scaling is strongest when the team can name a resource constraint and demonstrate that the application can use the added resource. Preserve durable state, distinguish host allocation from service limits, and judge success by the same workload and customer result used to justify the change. Primary kernel and AWS compatibility documentation were inspected on 2026-10-01. The arithmetic lab is inline; no VPS resize, provider operation, restore or performance test was executed while authoring.

