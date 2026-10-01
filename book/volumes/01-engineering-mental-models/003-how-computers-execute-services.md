---
book: The Complete DevOps Engineering Book
volume: 1
volume_title: "Engineering Mental Models"
chapter: 3
title: "How Computers Execute Services"
slug: how-computers-execute-services
status: complete
summary: ../../_ai/chapter-summaries/003-how-computers-execute-services.md
---

# Chapter 3 — How Computers Execute Services

## CPU, memory, storage and networks

DispatchDesk's requirement says an accepted order must be retrievable after an application restart. To evaluate that requirement, you need a picture of the machine beneath the application. Code is not a continuously operating object by itself. A running service consumes processor time, holds information in memory, asks the operating system to perform input and output, and depends on resources whose failure behaviors differ.

Read [Requirements Before Tools](002-requirements-before-tools.md) first. This chapter introduces a request's physical and software path; [Volume 2](../02-linux-and-automation/011-the-shell-and-command-execution.md) supplies the detailed Linux procedures. A Linux laptop, virtual machine or disposable host with Python 3 is enough for the small lab. No privileged access is required.

The **CPU** executes instructions. Application code may parse an order, validate fields, calculate a total and serialize a response. Some of that work is directly executable machine code; some is performed by a language runtime executing or compiling the program. Either way, processor time is finite. A request that performs unnecessary computation can delay other requests, even if the network and storage are healthy.

**Memory** holds information available to active computation: program instructions, objects, buffers and caches. An application may store an order in a Python dictionary and retrieve it quickly while the process lives. If the process exits, its private memory no longer constitutes an order store. A bigger memory allocation does not change that persistence property. A cache is useful precisely because it can avoid repeating slower work; whether its contents are reconstructible determines whether losing it is an inconvenience or a correctness failure.

**Storage** retains bytes beyond a process lifetime, subject to its own durability boundaries. A write may pass through application buffering, the kernel's page cache, a filesystem and a device or remote service. “The write function returned” is not automatically equivalent to “the data survives every failure.” A database can provide a defined commit contract using logging and synchronization, but that contract still depends on its configuration and storage behavior. This chapter establishes why the boundary matters; [Database Operations](../04-vps-and-server-operations/036-database-and-cache-operations-on-one-host.md) examines its implementation.

The **network** moves information between machines and processes. The API may wait for a database response or a notification provider. That wait is elapsed time even when the API consumes little CPU. Network communication can fail partway, and a peer can complete work even though its response never reaches the caller. A single “request time” includes several different kinds of work and waiting. Diagnose them separately before choosing a bigger machine.

These resources interact. A large request can increase memory pressure; memory pressure can increase storage activity; slower storage can hold database connections longer; exhausted connections can cause otherwise idle API handlers to wait. A low CPU reading during an outage therefore does not prove spare useful capacity. It may show that computation cannot proceed because another resource blocks it.

## Processes, kernels and system calls

A **program** is code and associated data. A **process** is a running instance with an address space, identity, open resources and execution state. Two processes can run the same program with different configuration and independent memory. Restarting one replaces its execution state; it does not inherently restore another process or repair stored data.

The **kernel** is the operating system component that manages resource access and coordinates execution. Applications normally run in user space and request kernel work through **system calls**. Reading a file, opening a socket and creating a process involve this boundary. The kernel checks permissions, resolves resources and arranges work, potentially waiting before returning a result.

An application can have several **threads**, execution flows sharing its process resources. A thread might compute while another waits for input. More threads can improve concurrency for some workloads, but they also need memory and coordination. A shared lock can serialize the work anyway. A language runtime may impose additional concurrency rules. Do not equate thread count with the number of requests a service can safely complete.

The kernel's scheduler chooses runnable execution flows for CPU time. A sleeping task might be waiting normally for another event. A runnable task might wait for processor availability. The distinction explains why elapsed request latency differs from consumed CPU time. It also warns against interpreting one instantaneous process state as a complete performance history.

Many resources are represented by a **file descriptor**, a small integer meaningful inside a process. A descriptor can refer to a regular file, pipe or socket. It is a handle to a resource, not the resource's contents. Descriptor 3 in one process need not refer to the same thing as descriptor 3 in another. The [Linux read manual](https://man7.org/linux/man-pages/man2/read.2.html) describes reading through such a descriptor, including shorter successful reads and end-of-file behavior.

## Observe a descriptor without deploying a service

Run this complete snippet in a terminal as an ordinary user on Linux with Python 3 installed. It can run from any directory. It creates a temporary file through the standard library, writes a small record, reads it in pieces and closes it on leaving the context. The temporary file is disposable; it is not a database or a durability demonstration.

```bash
python3 - <<'PY'
import os
import tempfile

with tempfile.TemporaryFile() as file:
    file.write(b'order-17\n')
    file.flush()
    file.seek(0)
    descriptor = file.fileno()
    print('pid:', os.getpid())
    print('descriptor:', descriptor)
    print('bytes:', os.read(descriptor, 5))
    print('remaining:', os.read(descriptor, 64))
    print('end:', os.read(descriptor, 64))
PY
```

`python3 -` reads Python source from standard input. The quoted heredoc delimiter prevents the shell from expanding the source. `TemporaryFile` supplies a file managed by a context; `file.write` uses the Python file interface, while `os.read` reads through the underlying descriptor. `flush` moves buffered Python writes out of that layer before the descriptor reads. `seek(0)` returns the position to the start; without it, reads would begin at the end after the write.

The first read asks for five bytes. The second asks for up to 64 but only four remain. The last returns empty bytes at the end. These facts illustrate why robust programs must interpret the returned amount rather than assume every read fills its requested buffer. The exact process ID and descriptor number vary.

The author ran this snippet using Python 3.14.7 on Linux kernel 7.2.7-arch1-1. The content results were:

```console
bytes: b'order'
remaining: b'-17\n'
end: b''
```

This measured local result validates the small file experiment only. It does not validate Ubuntu or RHEL packaging, a production filesystem, network sockets or persistence after host failure. Python installation differs by distribution: later package chapters provide Ubuntu and Fedora/RHEL procedures. The code itself makes no distribution-specific assumptions beyond Linux and an available Python interpreter.

A missing `python3` command means the prerequisite is absent. A temporary-file error may indicate unavailable temporary storage, permissions or a full filesystem. Those are distinct from a Python syntax error. Save the actual message and inspect the relevant boundary rather than copying a privileged workaround. The context closes its file on normal exit; the example creates no named project data to clean up.

## Following one request through a machine

Now trace an order request conceptually. A client sends bytes; the receiving machine's network stack makes them available to a listening socket. A server process obtains the connection through the kernel interface. Its HTTP library interprets the bytes, and its application handler validates the order. The application requests a database transaction, waits for the result, builds a response and sends response bytes through another kernel operation.

This is a model, not a claim that every runtime uses the same system-call sequence. An event-driven server and a process-per-request server organize concurrency differently. TLS termination may happen in a separate proxy. The database may be another process on the same host or a remote managed service. Put these actual boundaries in a diagram before investigating a production request.

```text
client → network/proxy → API process → database process/storage
                         ↓
                    response to client

database pending work → notification worker → external provider
```

The API's response should follow the commit boundary required by the charter. The worker's later activity is separate. A failed worker need not mean order acceptance failed; a failed database may prevent acceptance even if the API process remains alive. The diagram turns vague “server problems” into questions about specific exchanges.

Persistence deserves particular attention. `flush` in the lab addresses one language-buffering layer. Linux `fsync` requests synchronization of a file's data and relevant metadata to storage, with details and limitations documented by the [Linux fsync manual](https://man7.org/linux/man-pages/man2/fsync.2.html). Filesystem directory entries have their own considerations. This is why hand-writing an order database as an append-only text file is a poor novice shortcut for a production contract. Use a database whose commit, backup and recovery behavior you can verify.

## A service that is alive but waiting

Suppose DispatchDesk begins timing out. The process exists and CPU use is modest, so an engineer proposes restarting it and doubling its threads. The incident timeline instead shows the database's storage latency increased first, followed by long-running transactions and occupied API handlers. The API is alive but spends most of its time waiting for database results.

The responder examines request duration by stage, database connection use and host storage evidence. [The kernel's proc documentation](https://www.kernel.org/doc/html/latest/filesystems/proc.html) describes process status fields and their limits; a status snapshot can support the investigation but cannot establish database storage latency alone. Different tools expose different boundaries, and reading another process may require permissions. Do not expose its environment indiscriminately: configuration can contain credentials.

Recovery targets the constrained boundary. The team may stop a known expensive background operation if evidence links it to contention, shed new work under the service's admission policy, or restore a failing storage path. Restarting the API can release connections, but if the storage problem persists, the wait returns. Increasing concurrency can make the queue and storage contention worse. Preserve accepted orders and uncertain transaction state before replaying requests.

After recovery, compare storage latency and successful order outcomes with the incident baseline. Then determine whether the cause was device failure, workload interference, an inefficient query or capacity exhaustion. Each requires a different lasting change. A larger host may help capacity exhaustion, but cannot repair an incorrect query contract or guarantee the recovery of corrupted data.

## Exercises and answer guidance

1. An order exists in an in-memory dictionary and the API returns its identifier. Which charter criterion is at risk? Retrieval after application restart fails unless another durable mechanism stores it. Memory capacity does not resolve the issue.
2. Remove `file.seek(0)` from the disposable snippet. Predict the content reads, then run it. They begin at the current end position and return empty bytes. Explain why this is an offset issue rather than lost data.
3. A slow API consumes little CPU and all database connections are busy. Name two hypotheses and evidence that distinguishes them. Slow database operations and connections held unnecessarily are plausible; transaction timings, storage evidence and application traces help distinguish them. CPU alone cannot.

## Review questions and takeaways

What changes when a program becomes a process? Why can one descriptor number identify different resources in different processes? Why can waiting increase latency without increasing CPU use? Which persistence layer does a language-level flush address? What can a successful local lab actually prove?

Follow work across resource boundaries. Separate computation from waiting and process lifetime from data lifetime. Use measurements that correspond to the suspected mechanism. Detailed Linux primitives follow in Volume 2; next, [Reliability and Risk](004-reliability-and-risk.md) considers which failures the service must tolerate.

## Sources and verification

Linux man-pages `read(2)` and `fsync(2)`, and the kernel `/proc` documentation were inspected on 2026-10-01. The exact temporary-file snippet ran successfully in the authoring environment with versions recorded above. The Python documentation website returned a service error during attempted inspection; no claim of checking it is made. No network service, database, crash durability test or distribution-specific installation was executed. The incident is fictional. Independent review is required.
