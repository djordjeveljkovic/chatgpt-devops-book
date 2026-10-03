---
book: The Complete DevOps Engineering Book
volume: 3
volume_title: "Networking and Traffic"
chapter: 22
title: "TCP, UDP and Connections"
slug: tcp-udp-and-connections
status: draft
summary: ../../_ai/chapter-summaries/022-tcp-udp-and-connections.md
---

# Chapter 22 — TCP, UDP and Connections

## Why this matters

A correct route does not establish that DispatchDesk can exchange application data. Harbor's worker may reach a host whose database has stopped listening, or it may establish a connection and then wait indefinitely for a response. “Connection failed” hides several different boundaries. The repair depends on which boundary actually failed.

Read [Chapter 21](021-packets-addresses-and-routing.md) first. This chapter uses a disposable local TCP/UDP lab, not a running DispatchDesk service. It introduces ports, connection evidence and bounded capture. These observations carry forward into database, proxy and container troubleshooting; they do not require opening a public port.

## Handshakes, retransmission and ports

A transport port helps the receiving host deliver traffic to a socket. An IP address and port together describe a transport endpoint, but the protocol matters too: TCP port 53 and UDP port 53 are distinct. A client usually selects a temporary local port, while a server uses a configured listening port. Observing a destination port tells you which endpoint was attempted, not whether the expected program owns it.

TCP establishes connection state using SYN, SYN-ACK and ACK messages in its ordinary handshake. Its sequence numbers, acknowledgments and retransmission behavior support an ordered byte stream. The stream has no application-message boundaries: two writes can arrive in one read, and one write can require several reads. Applications need framing such as lengths, delimiters or a protocol parser. [TCP specification](https://www.rfc-editor.org/rfc/rfc9293.html).

A successful TCP handshake establishes transport state between the observed endpoints. It does not prove authentication, database readiness or durable application acceptance. If a reverse proxy accepts the connection, the client has reached that proxy; the proxy's separate upstream connection can still fail.

TCP also controls transmission according to congestion and receiver capacity. A receiver that stops consuming data can create backpressure; a congested or lossy path can cause retransmission and reduced progress. More retries at the application layer can worsen that situation by introducing additional work. Inspect whether connections establish, whether bytes advance, and whether the application processes them before adjusting global network parameters. [Linux TCP behavior](https://man7.org/linux/man-pages/man7/tcp.7.html).

UDP sends datagrams without TCP's connection establishment and ordered-stream recovery. A received datagram preserves a message boundary, but a datagram can be lost, duplicated or arrive out of order. A successful send means the local stack accepted the operation; it does not acknowledge remote delivery. Applications using UDP define their own response, timeout and recovery behavior. [UDP specification](https://www.rfc-editor.org/rfc/rfc768.html).

UDP is useful where the application tolerates loss or implements the required reliability itself. Protocols built over UDP can be sophisticated: choosing UDP does not imply the application is an unreliable one-packet exchange. Conversely, switching a business operation to TCP does not automatically solve duplicate effects after a lost application response.

## Connection state and timeouts

A connection can wait during name resolution, transport establishment, TLS negotiation, request upload or response processing. One timeout named “network timeout” may cover only one of those stages. Record which budget expired and whether any application data had already been sent. A timeout after order submission leaves a different recovery question from a timeout before a connection existed.

A read timeout commonly limits waiting for progress on a read operation. It need not impose a total request deadline: a peer that sends small amounts repeatedly can keep an operation alive under some APIs. A complete service contract sets an overall deadline and allocates time across stages, including retries. Later chapters develop [partial failure](../17-distributed-systems-and-data-operations/161-partial-failure-and-timeouts.md) and [idempotent retries](../17-distributed-systems-and-data-operations/162-retries-idempotency-and-backoff.md).

Linux socket states provide clues. `SYN-SENT` indicates an initiating TCP socket awaiting establishment. `ESTAB` means the transport connection is established. `CLOSE-WAIT` means the peer has closed its sending direction and the local application has not finished closing its side. `TIME-WAIT` supports safe TCP connection teardown and is often normal. A snapshot cannot distinguish normal short-lived states from pathological accumulation; compare counts, ages and workload over time.

A rising `CLOSE-WAIT` population during repeated provider failures can indicate that the client is leaking sockets. A large `TIME-WAIT` population after a burst is a different observation. Do not solve both by copying a kernel-tuning recipe. Link the state to actual resource consumption and error evidence, including the descriptor limits from [Chapter 20](../02-linux-and-automation/020-scheduling-and-resource-limits.md).

## Inspect sockets with ss

Run these read-only commands on the process's Linux host. The current directory does not matter. Ubuntu supplies `ss` through `iproute2`; Fedora and RHEL package it through `iproute`. Ordinary users can inspect socket addresses, but process attribution can be restricted to sockets they own.

```bash
ss -ltn
ss -lun
ss -tn state established
ss -tan '( sport = :18080 or dport = :18080 )'
```

`-l` selects listening sockets, `-t` selects TCP, `-u` selects UDP, `-n` keeps addresses and ports numeric, and `-a` includes listening and other sockets. The quoted filter narrows TCP observations to the lab port. Add `-p` when process ownership is needed and your permissions allow it. Add `-i` for internal TCP information on a relevant socket; interpret those fields against the installed tool and kernel. [Socket-inspection manual](https://man7.org/linux/man-pages/man8/ss.8.html).

A loopback listener at `127.0.0.1:18080` should not be reachable from another host. A wildcard listener can receive traffic through eligible local addresses, but routing and filtering still decide which packets arrive. An IPv6 wildcard listener's IPv4 behavior depends on socket configuration; test each address family rather than assuming one displayed listener proves both.

Queues also need context. For an established TCP connection, receive and send queues describe data pending at the respective socket boundaries. Listening TCP queue fields have different meanings associated with pending connections and backlog. Compare observations with arrival rate and application progress; the same queue count has different implications for a brief burst and a sustained stall.

## A bounded TCP and UDP lab

Save the complete program below as `transport_lab.py` in a reader-owned directory. It requires Python 3 and no administrator privileges. Run each pair on the same Linux host. The server binds only to IPv4 loopback on port 18080 and handles one exchange. Check `ss -ltn` or `ss -lun` first for a conflicting listener; if the port is occupied, choose another unprivileged port and change the program's constant and all observations consistently.

```python
import argparse
import socket

ADDRESS = ("127.0.0.1", 18080)
REQUEST = b"probe\n"
RESPONSE = b"ack\n"


def read_line(connection):
    data = bytearray()
    while not data.endswith(b"\n"):
        chunk = connection.recv(64 - len(data))
        if not chunk:
            raise RuntimeError("peer closed before newline")
        data.extend(chunk)
        if len(data) == 64 and not data.endswith(b"\n"):
            raise RuntimeError("message exceeds lab limit")
    return bytes(data)


def serve(protocol):
    kind = socket.SOCK_STREAM if protocol == "tcp" else socket.SOCK_DGRAM
    with socket.socket(socket.AF_INET, kind) as server:
        server.settimeout(30)
        server.bind(ADDRESS)
        if protocol == "tcp":
            server.listen(1)
        print("ready:", protocol, ADDRESS, flush=True)
        if protocol == "tcp":
            connection, peer = server.accept()
            with connection:
                connection.settimeout(5)
                if read_line(connection) != REQUEST:
                    raise RuntimeError("unexpected request")
                connection.sendall(RESPONSE)
        else:
            message, peer = server.recvfrom(64)
            if message != REQUEST:
                raise RuntimeError("unexpected datagram")
            server.sendto(RESPONSE, peer)
        print("served:", peer, flush=True)


def request(protocol):
    kind = socket.SOCK_STREAM if protocol == "tcp" else socket.SOCK_DGRAM
    with socket.socket(socket.AF_INET, kind) as client:
        client.settimeout(5)
        if protocol == "tcp":
            client.connect(ADDRESS)
            client.sendall(REQUEST)
            reply = read_line(client)
        else:
            client.sendto(REQUEST, ADDRESS)
            reply, peer = client.recvfrom(64)
            if peer != ADDRESS:
                raise RuntimeError("unexpected response endpoint")
        if reply != RESPONSE:
            raise RuntimeError("unexpected response")
        print("response:", reply.decode("ascii").strip())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("role", choices=("server", "client"))
    parser.add_argument("protocol", choices=("tcp", "udp"))
    args = parser.parse_args()
    if args.role == "server":
        serve(args.protocol)
    else:
        request(args.protocol)
```

In terminal A run:

```bash
python3 transport_lab.py server tcp
```

After it prints `ready`, inspect its listener from terminal B, then run:

```bash
ss -ltn 'sport = :18080'
python3 transport_lab.py client tcp
```

Expect `response: ack` and the server's `served` message. The server then exits and its socket closes. Repeat both commands using `udp`, and inspect with `ss -lun`. The TCP read loop handles fragmentation of the short newline-delimited message; it does not assume a single `recv` equals a whole request. The receive timeouts bound individual socket operations, not an absolute transaction deadline. The small lab omits authentication and concurrent service operation. [Python socket API](https://docs.python.org/3/library/socket.html).

Run the TCP client again after the server has exited. On an ordinary local host with no intervening reject/drop policy, expect a refused connection. Run the UDP client without its server: it may time out because there is no application response. Neither result establishes what a remote firewall would do. Stop a waiting server with Ctrl-C; otherwise its 30-second accept/receive timeout ends the wait. Remove the saved lab file when finished. No firewall opening is required.

## Use a small packet capture

On a disposable host where you are authorized to capture this lab's traffic, start this command in a third terminal before a new TCP server/client exchange:

```bash
sudo timeout 15s tcpdump -i lo -nn -c 12 'tcp port 18080'
```

`-i lo` selects loopback, `-nn` suppresses address and service-name lookup, and `-c 12` stops after twelve matching packets. GNU `timeout` also bounds the wait to fifteen seconds if fewer packets arrive. Its timeout exit status is expected when that limit ends capture; it does not indicate that the application exchange failed. Installation packages are `tcpdump` on Ubuntu, Fedora and RHEL, subject to repository availability. Capture privileges differ from ordinary socket inspection.

Look for the initial SYN, the reply with SYN and ACK, acknowledgment, data and connection closure. Exact packet counts and grouping can differ. A capture at one point shows what that point observed; absence can mean a wrong filter or interface as well as no traffic. Capture files and payload displays can contain sensitive data, so keep the scope to the disposable lab. This example prints metadata and creates no packet file. [Upstream tcpdump manual](https://raw.githubusercontent.com/the-tcpdump-group/tcpdump/master/tcpdump.1.in).

Host offloading can make captured checksums or segment sizes appear different from packets on the physical wire. Establish your observation point before diagnosing corruption from a local trace. Do not disable offloading on a production interface merely to make a screenshot look familiar.

## Recover a connection failure

Harbor's database moves to a new private host, but the worker retains the old address. Route inspection succeeds because the old host still exists. The TCP client receives a refusal because nothing listens on that host's database port. Compare the worker's effective configuration with the approved endpoint, then inspect the intended host's listener. A refusal supports a reachable rejecting endpoint; a rejecting firewall can also produce a refusal, so process and policy evidence still matter.

Restore the correct endpoint through the application's configuration mechanism, restart or reload only as required by that application, and observe a real database exchange. Reconcile pending notification work before blindly retrying anything whose external outcome is uncertain. A TCP connection proves access to a transport endpoint, not that an earlier notification was never sent.

If the handshake instead completes but queries stall, investigate server processing, connection-pool waits and query progress. Bound new work and preserve database error evidence. Increasing the connect timeout cannot repair a slow query after connection establishment. Restarting every client can also amplify reconnection load; recovery should restore progress without causing a new surge.

## Exercises, review questions and takeaways

1. Run both protocol labs and inspect their waiting sockets. Guidance: TCP has a listener and handshake; UDP has a bound datagram socket and application response.
2. Remove each server and compare client failures. Guidance: record the actual result, and explain why UDP silence is ambiguous rather than promising one universal error.
3. Explain why one `recv(64)` is insufficient for a TCP message. Guidance: byte-stream delivery can split a message; framing determines completion.
4. Classify a case where TCP establishes but the response deadline expires. Guidance: the handshake boundary passed; application processing, upstream dependencies and later path failures remain candidates.

Review questions: What does `ESTAB` prove? Why is `TIME-WAIT` often expected? How can a proxy answer a TCP connection while its upstream is down? A useful answer ties each observation to its endpoint and stage.

A connection is one boundary in a larger operation. Observe transport state, bound waits and verify application outcomes separately. Continue to [Chapter 23](023-dns-from-resolver-to-authority.md) to investigate how the destination address was selected.
