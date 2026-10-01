---
book: The Complete DevOps Engineering Book
volume: 2
volume_title: "Linux and Automation"
chapter: 15
title: "Processes, Signals and Jobs"
slug: processes-signals-and-jobs
status: complete
summary: ../../_ai/chapter-summaries/015-processes-signals-and-jobs.md
---

# Chapter 15 — Processes, Signals and Jobs

## Why this matters

An application deployment replaces running work, not merely files on disk. Harbor cannot safely update DispatchDesk by killing whichever process happens to contain `python` in its command line. It must identify the service, stop accepting new work, preserve orders already acknowledged, and understand whether the worker has completed a provider request whose reply was lost.

Processes make those transitions concrete. Their parent relationships, identities, descriptors, signals, and exit statuses determine what survives a terminal disconnect or a restart. This chapter connects Linux process mechanics to service recovery. Its local exercises use only child processes created by the reader, avoiding broad process-name targeting.

## A process is a running context

A program file contains instructions. A process executes instructions with an address space, credentials, open descriptors, environment, working directory, and other kernel-managed state. Multiple processes may execute the same program with different configuration and authority. Threads share substantial process resources while providing separate execution flows; seeing several threads does not necessarily mean several independently managed services.

The PID identifies a process at a particular time. Its parent PID describes a relationship, not ownership by a human. A shell can start a child; the child can start descendants. A launcher may replace itself with the application through exec, preserving its PID while changing the program image. An unneeded wrapper that never forwards signals can therefore become a deployment bug.

PIDs can be reused after processes exit. An old PID file is not proof that its number still names DispatchDesk. Check identity and start time, and prefer the service manager's managed lifecycle when one exists. A numeric PID captured from your own just-started child is suitable for a short local exercise; a long-lived automation system needs stronger ownership than a stale integer.

Open descriptors connect process mechanics to earlier chapters. A child can inherit a log descriptor, a pipe endpoint, or a socket. If an unexpected descendant keeps a pipe's write end open, a reader may wait for end-of-file after the apparent producer exits. If a process retains a descriptor to an unlinked log, disk blocks can remain allocated. Both failures are about resource lifetime rather than visible filenames.

## Observe before sending a signal

Use a process listing to understand identity, age, state, and ancestry. On the baseline Ubuntu, Fedora, and RHEL systems, procps-style `ps` provides the following fields; package installation and optional utilities vary, but the kernel concepts do not:

```bash
ps -eo pid,ppid,user,stat,etimes,args
```

This is a host-wide view and may expose command-line arguments. Avoid putting secrets in arguments and sharing raw listings indiscriminately. A bounded inspection of a known process is usually more useful than searching every command line for a common runtime name. Confirm you are on the intended host and namespace; a container's PID view may differ from its host's.

Linux process-state letters include runnable/running, interruptible sleep, uninterruptible sleep, stopped, and zombie states. `S` often means a healthy process waiting for an event. `R` does not prove useful progress. `D` indicates an uninterruptible wait, often associated with I/O; determine the actual resource and context rather than assuming a deadlock. `Z` means the child has exited but its exit information has not yet been collected by its parent. The process-state definitions are documented in [Linux proc PID stat](https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html).

A zombie is not an actively executing worker. Sending it SIGKILL cannot make it execute cleanup: it has already terminated. The parent must collect the status with a wait operation, or a suitable reaper must do so after reparenting. A growing zombie population points toward a child-management defect. Restarting an unrelated service because its process listing looks unfamiliar is unlikely to address that defect. [Linux wait interfaces](https://man7.org/linux/man-pages/man2/wait.2.html).

CPU consumption, elapsed time, and process state are observations. Build a hypothesis connecting them to the symptom. A sleeping worker may be waiting correctly for new jobs, or waiting indefinitely on a provider without a timeout. Compare logs, pending state, and recent progress before changing its lifecycle.

## Signals request actions

A signal is a notification delivered according to a process's disposition. Many signals have default actions, while a program may catch or ignore some. SIGTERM conventionally requests termination and gives a cooperative application an opportunity to run its shutdown path. SIGINT is commonly generated by an interactive interrupt. SIGHUP is associated with terminal hangup and is sometimes repurposed by daemons for reload, but reload behavior must be documented by that program. Do not infer it from the signal name.

SIGKILL terminates without application cleanup and cannot be caught, blocked, or ignored. SIGSTOP similarly cannot be caught, blocked, or ignored and stops execution; SIGCONT resumes a stopped process. A stop is not a graceful drain. The process retains resources while stopped, potentially including locks and connections. Use signal names in documentation because numbers can vary across architectures. [Linux signal semantics](https://man7.org/linux/man-pages/man7/signal.7.html).

Successful `kill` reports that the signal operation was accepted, not that the process has finished. Verify its exit through the owning parent or service manager. A process in some uninterruptible kernel waits may not disappear immediately even after SIGKILL; the relevant wait must resolve sufficiently for termination to proceed. Repeatedly sending stronger signals does not repair a failed storage device.

Signal handlers have programming constraints. At the C/POSIX level only certain operations are safe in an asynchronous handler. A runtime may provide a safer deferred mechanism. A sound design often records shutdown intent and lets the normal execution loop perform cleanup rather than doing arbitrary database or logging work inside a low-level handler. Implementation must follow the chosen runtime's contract.

## Practice with an owned child

In Bash, `&` starts a command asynchronously. `$!` records the PID of the most recently started asynchronous job in the relevant context. `wait` lets the shell collect a child's completion status. This fixture creates an ordinary sleeping child and signals only that captured child:

```bash
sleep 30 &
child_pid=$!
printf 'owned child PID=%s\n' "$child_pid"
ps -p "$child_pid" -o pid=,ppid=,stat=,args=
kill -TERM "$child_pid"
if wait "$child_pid"; then
  printf 'child completed successfully\n'
else
  child_status=$?
  printf 'child wait status=%s\n' "$child_status"
fi
```

Bash reports a nonzero wait status for signal termination. On ordinary Linux Bash configurations SIGTERM commonly yields 143, following Bash's signal-status convention; the important observation is termination by a signal rather than successful application completion. A different API may represent that termination separately instead of returning the shell's numeric convention. This is why a service's exit code alone cannot explain every termination.

Do not replace the captured PID with `pkill python`, `killall`, a wildcard, or a negative process-group identifier in this exercise. Those target a different population. Process groups are useful for controlling a related job but require explicit membership and scope. A pipeline may involve several processes, so one member's exit does not establish that all work stopped.

The shell's `jobs`, `fg`, and `bg` commands manage its own job table, with interactive job-control behavior. They are conveniences for terminal work, not a persistent service supervisor. Backgrounding a process does not automatically provide restart policy, log retention, readiness checks, or orderly machine shutdown. `nohup` can alter hangup handling and output arrangements but does not provide those missing responsibilities either. Chapter 16 supplies an explicit supervisor.

## Graceful shutdown follows the business invariant

DispatchDesk's acceptance path persists an order and its notification intent before acknowledgment. Shutdown should preserve that pairing. A practical sequence is to mark the acceptance endpoint unready, stop taking new requests, allow bounded completion of in-flight acceptance transactions, stop claiming new notification work, and finish or safely release work already claimed. Finally, close resources and exit.

These steps need deadlines. A provider that never replies must not make every deployment hang forever. Define a maximum drain interval consistent with request and dependency timeouts. A forced stop after that interval is a recovery decision, not evidence that the work completed. The next instance must be able to reconcile durable state.

Notification delivery is especially subtle. A worker can submit a notification, have the provider accept it, then lose the reply before recording success. Restarting and blindly retrying may deliver twice. Durable intent protects against lost work; idempotency keys or reconciliation address ambiguous outcomes. A shutdown handler cannot magically undo an externally accepted request. Later application and queue chapters develop that protocol.

Readiness and process health answer different questions. `/healthz` may remain responsive while `/readyz` rejects new acceptance during drain. A monitoring probe that sees a live process should not route new business work into a draining instance. Likewise, an instance leaving traffic does not prove its pending notification work is finished. Record these transitions in observable events and test the actual acknowledgment invariant.

Harbor can tolerate a planned interruption within its stated objective if clients handle unavailable acceptance correctly. Summit may drain a task behind a managed load balancer. Atlas may coordinate readiness and a Kubernetes termination grace period. Each environment still needs the same application-specific answer: which work is accepted, which is durable, and which outcome is ambiguous when the process exits?

## Investigate a worker that will not stop

Suppose a Harbor deployment sends TERM to the managed worker, waits, and reaches its deadline. Preserve logs and the stop event time. Confirm the target is the current worker, then inspect its process tree and state. Determine whether a wrapper received TERM while its child continued, whether the program ignored or blocked TERM, or whether the normal shutdown loop is waiting on a dependency.

In this scenario a shell wrapper starts the worker as a child and waits without a forwarding arrangement. The supervisor signals the wrapper; the worker continues holding the database and sending notifications. The correct repair is lifecycle ownership: use a launcher that execs the worker when appropriate, or implement deliberate forwarding and child reaping when the wrapper genuinely needs to manage several children. Do not simply increase the timeout forever.

For recovery, prevent a second worker from claiming the same work until ownership is clear. Stop the intended service through its supervisor and verify descendants/resources have ended. If forced termination becomes necessary, record which notification operations had ambiguous outcomes and reconcile before replay. Preserve evidence of the wrapper defect, then validate a new deployment with a controlled stop under representative in-flight work.

Another observation would imply another action. A worker stuck in storage I/O needs storage diagnosis; an application blocked indefinitely on a network response needs a bounded client timeout and a safe retry protocol. The signal is a control input, not a diagnosis. Chapter 7's discriminating experiments prevent applying a wrapper repair to an unrelated wait.

## Exercises and review

1. Run the owned-child exercise and describe what `kill` success versus `wait` completion establishes. Guidance: signal submission precedes observed exit; wait also collects the child's status.
2. Explain why a zombie cannot be repaired with SIGKILL. Guidance: execution already ended; its parent must reap the exit information.
3. Design a DispatchDesk drain test with an acceptance transaction and a provider request in progress. Guidance: verify order/intent pairing, bounded exit, and reconciliation of a provider outcome whose response is lost.
4. A worker remains in `D` after a forced stop request. What evidence comes next? Guidance: inspect the waiting resource and storage context; do not claim that another signal will resolve the underlying operation.

Processes have lifetimes and resources beyond their command names. Signals communicate intent or enforce termination, while completion must be observed through the owner. Graceful shutdown requires a business protocol with deadlines and durable recovery, especially for external side effects. Continue to [Chapter 16](016-systemd-and-service-lifecycles.md) to express that ownership through supervised units.

## Verification

The author inspected Linux signal, process-state, and wait documentation. The local child exercise uses no application or infrastructure. Its executed result is recorded in the continuation summary. Wrapper incidents and DispatchDesk drain behavior are design scenarios, not claimed integration-test results.
