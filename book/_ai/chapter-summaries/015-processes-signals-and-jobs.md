# Chapter 15 continuation

Status: complete

## Written material
Complete chapter covering process context/ancestry/exec/PID reuse, inherited descriptors, ps states and zombies, signal semantics, owned-child Bash lab, shell jobs versus supervisors, invariant-preserving drain, and a wrapper signal-forwarding incident. Four exercises with answer guidance.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Concepts and terminology
PID/PPID, exec, descriptors, process states, zombie/reaping, TERM/KILL/STOP/CONT, wait status, drain deadlines, ambiguous provider outcomes.

## Examples and cross-references
Host ps view is explicitly sensitive/context-dependent; safe owned sleep child and TERM/wait lab. Chapters 7/10/16 discussed; Chapter16 linked. No process-name-wide signals prescribed. Canon health/readiness/order-intent invariant retained.

## Open threads
No baseline distribution image process testing or service integration/drain tests. Wrapper/I/O incidents fictional. Source-reviewed process semantics require independent review.

## Verification
Inspected Linux signal7, proc_pid_stat5, wait2; Bash manual inspected in Chapters11/13 supports shell wait/status semantics. Executed owned-child block in Bash5.3.20: ps showed owned sleep child, TERM delivered, wait reported143, parent block returned0 after explanation. Child reaped; no unrelated signals or infrastructure. Broad host ps block not captured to avoid unnecessary process arguments. Syntax/links checked separately.
