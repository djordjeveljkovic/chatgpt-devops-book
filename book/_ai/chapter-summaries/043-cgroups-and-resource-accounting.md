# Chapter 43 continuation

Status: complete

## Written material
Cgroup hierarchy and v1/v2 distinction; CPU weighting/quota; memory and OOM boundaries; I/O and pids; safe inspection via proc, findmnt and systemd; customer-symptom diagnosis and exercises.

## Concepts and terminology
cgroup v2, ancestor limits, `cpu.weight`, `cpu.max`, throttling, `memory.current/high/max/events`, `memory.events.local`, `oom_kill` scope, `io.max`, task-count `pids.max`, cgroup namespace.

## Examples and cross-references
Read-only shell inspection requests a known host PID, checks proc membership and systemd service properties. No cgroup files are written. Links chapters 41, 42, 51–52 and 108.

## Open threads
Controller/mount/systemd property support differs by kernel and distribution. `oom_kill` alone does not establish that a local `memory.max` caused a kill; compare local/ancestor event deltas and kernel/engine evidence. No live DispatchDesk cgroup inspected. Fresh independent review approved against the current body hash.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Shell syntax and local links checked. Kernel cgroup v2 and OCI runtime config primary docs inspected 2026-10-04.
