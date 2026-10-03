---
book: The Complete DevOps Engineering Book
volume: 3
volume_title: "Networking and Traffic"
chapter: 24
title: "HTTP and API Traffic"
slug: http-and-api-traffic
status: draft
summary: ../../_ai/chapter-summaries/024-http-and-api-traffic.md
---

# Chapter 24 — HTTP and API Traffic

## Why this matters

A user reports that DispatchDesk “is up” because its process manager says the service is running, but creating an order returns an error. That process state does not describe the HTTP request. The client may have reached a reverse proxy that cannot reach the application; the application may reject a request the proxy delivered; or the API may have accepted the order and lost the response on its way back.

This chapter follows one HTTP request through its method, headers, response and proxy boundaries. It builds on [DNS lookup](023-dns-from-resolver-to-authority.md) and [transport connections](022-tcp-udp-and-connections.md). Its self-contained server binds to loopback and changes no external service. A local success proves the local exchange used by the test, not public availability or durable business behavior.

## Methods, status and headers

An HTTP request includes a method, target, protocol version, headers and sometimes a body. The method states the operation's intended semantics. `GET` retrieves a representation and is defined as safe; `PUT` replaces or creates the target representation and is idempotent by definition; `POST` asks the target to process supplied data and can create effects. Retry policy must reflect the endpoint's actual contract. A client that loses the response to `POST /orders` cannot infer from the timeout that no order was created. [HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html).

A status code describes the result at the responding HTTP boundary. `200` indicates success with a response representation when appropriate. `201` indicates a resource was created, commonly with a `Location` header. `202` means accepted for processing; it does not promise processing has finished or succeeded. `204` means success without response content. `400` describes a request problem, `401` requires authentication credentials, `403` denies the request, `404` says the target was not found at that server, `429` signals rate limiting, and `5xx` describes a server-side failure. These codes need their response body and the identity of the server that returned them to guide recovery.

Headers carry metadata and control around the representation. `Content-Type` describes the body format; `Content-Length` describes its octet count when supplied; `Accept` describes acceptable response formats. `Host` identifies the authority for HTTP/1.1 virtual hosting. `Authorization` can contain secrets and must not be copied into an incident ticket. Header names are case-insensitive. Conflicting framing headers can create request-smuggling risks at proxy boundaries; use maintained server and proxy implementations rather than writing a custom HTTP parser. [HTTP/1.1 message syntax](https://www.rfc-editor.org/rfc/rfc9112.html).

An API contract also defines required fields, authentication, size limits, validation errors and side effects. DispatchDesk accepts an order only after persisting the order and its notification intent, then may return `202` while a worker sends the notification later. This project contract is fictional and does not mean that the example server in the next section implements durable order processing.

## Persistent connections and proxy boundaries

HTTP/1.1 commonly reuses a TCP connection for multiple exchanges. A connection carries request and response bytes; correct framing tells each side where one message ends. HTTP/2 multiplexes streams over a connection and has different framing, while HTTP/3 uses QUIC over UDP. Proxies may terminate one protocol and originate another. A packet capture or socket inspection must therefore identify which hop it observes.

A reverse proxy accepts a client connection and makes a separate upstream request to an application. Client-facing TLS, host routing, request-size limits, timeout budgets and forwarded headers can differ from the upstream settings. A `502` or `504` may come from the proxy even though the application's own health endpoint is fine. Identify the responding hop through request IDs, logs and response headers, taking care not to trust spoofable headers supplied by arbitrary clients.

Headers such as `Forwarded` or `X-Forwarded-For` can preserve client details across proxies. The application should trust those values only from known proxy peers, and the proxy should remove or overwrite client-supplied copies according to its policy. Otherwise a client can claim another source address or bypass IP-based audit assumptions.

Each hop has its own timeouts. A proxy's upstream read timeout can expire after the client-to-proxy TCP connection succeeds. A client can time out while the application later commits the order. Align stage budgets with an overall request deadline and define safe retry behavior for operations with side effects. Graceful proxy draining and application shutdown should allow in-flight work to complete within a measured deadline.

## A complete local HTTP lab

Save this program as `http_lab.py` in a reader-owned directory. It requires Python 3.14 and uses only its standard library. The server binds to `127.0.0.1:18081`, accepts requests locally, and returns a health response or a fictional order-accepted response. It does not store orders, authenticate callers, or send notifications, so never expose it on a public interface. The server handles one accepted TCP connection, then exits; terminate the client after its requests to let the server finish cleanly.

```python
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def reply(self, status, body):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(encoded)
        self.close_connection = True

    def do_GET(self):
        if self.path == "/healthz":
            self.reply(200, "process can respond\n")
        else:
            self.reply(404, "not found\n")

    def do_POST(self):
        if self.path != "/orders":
            self.reply(404, "not found\n")
            return
        if not self.headers.get("Idempotency-Key"):
            self.reply(400, "Idempotency-Key required\n")
            return
        try:
            size = int(self.headers.get("Content-Length", "-1"))
            if not 0 <= size <= 65536:
                raise ValueError("invalid content length")
            body = self.rfile.read(size)
            order = json.loads(body)
            if not isinstance(order, dict) or "order_id" not in order:
                raise ValueError("order_id required")
        except (ValueError, json.JSONDecodeError):
            self.reply(400, "invalid order body\n")
            return
        self.reply(202, "accepted for this lab response only\n")


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 18081), Handler)
    server.timeout = 20
    print("listening on http://127.0.0.1:18081", flush=True)
    server.handle_request()
    server.server_close()
```

The `Idempotency-Key` check illustrates an API contract; because this lab keeps no state, it cannot make retries safe. A production implementation must persist and scope the key with the operation result, define its expiration and replay behavior, and enforce authorization. Python's built-in HTTP server is a learning tool, not a production server. [Python HTTP server documentation](https://docs.python.org/3/library/http.server.html).

Check the chosen port is free with `ss -ltn 'sport = :18081'`. Start the lab in one terminal and copy each `curl` command into another terminal on the same host:

```bash
python3 http_lab.py
```

```bash
curl --include --connect-timeout 2 --max-time 5 http://127.0.0.1:18081/healthz
curl --include --connect-timeout 2 --max-time 5 http://127.0.0.1:18081/missing
curl --include --connect-timeout 2 --max-time 5 --request POST \
  --header 'Content-Type: application/json' \
  --header 'Idempotency-Key: lab-001' \
  --data-binary '{"order_id":"lab-001"}' \
  http://127.0.0.1:18081/orders
```

Expect HTTP `200`, `404` and `202` respectively, with a small text body. These are results from the local lab when run by the reader, not measured output claimed here. `--include` displays response headers. `--connect-timeout` limits connection establishment, while `--max-time` bounds the full curl transfer. `--data-binary` sends the provided body; the explicit content type describes its JSON encoding. `--request POST` selects the method. Curl can infer POST from body options, but the explicit method makes the example's intent visible. [curl manual](https://curl.se/docs/manpage.html).

The server closes each response connection, so the first curl process can finish its one request and the server exits after that accepted connection. For the three examples, restart the server before each separate command, or combine requests using a server implementation designed to serve multiple clients. The 20-second accept timeout releases an idle lab server. Stop early with Ctrl-C. After each server exits, inspect the listener again; remove the saved lab file during cleanup.

A connection refusal after the server stops differs from an HTTP `404`: refusal means curl did not receive an HTTP response, while `404` is an HTTP response from a reachable server. `curl --fail-with-body` can make HTTP error statuses produce a nonzero exit while preserving the response body; curl's default exit status alone does not mean every HTTP response was `2xx`.

## Following a request with curl

Use curl against the actual target only when you are authorized to make that request. A diagnostic request can change state if its method or endpoint has side effects. Start by testing a known health route and inspect status, headers and timing separately:

```bash
curl --silent --show-error --output /dev/null \
  --connect-timeout 2 --max-time 5 \
  --write-out 'status=%{http_code} connect=%{time_connect}s total=%{time_total}s remote=%{remote_ip}\n' \
  https://api.example.com/healthz
```

Here `api.example.com` is a placeholder you must replace with an approved hostname. The command suppresses the body, preserves curl's own errors, bounds connect and whole-transfer time, then prints response status, connection time, elapsed transfer time and chosen remote IP. A status of `000` means curl did not receive an HTTP status; inspect the reported transport or TLS error. A `2xx` health response is evidence only for the checks that endpoint performs.

For deeper evidence, add `--verbose` on a controlled request and review which address and protocol curl selected, the request headers, response headers and connection reuse. Verbose output can expose cookies, tokens, query parameters and internal addresses. Protect it like application logs, redact secrets before sharing, and avoid adding credentials to shell history. `--resolve api.example.com:443:203.0.113.55` can direct curl to a specific test address while retaining the hostname for HTTP and TLS; use a real approved test address, because `203.0.113.55` is documentation-only. This option tests a direct address choice while bypassing ordinary DNS selection for that invocation.

A trace ID can link client, proxy and application logs. Use a request identifier generated or validated at a trusted boundary, and keep high-cardinality order identifiers out of metric labels. Compare the API's structured error and status with the proxy's upstream result. A process health response, a proxy access log and a committed order are three different evidence points.

## Interpret failures across boundaries

Suppose Harbor clients receive `504` after the proxy connects to its upstream. Inspect the proxy's timeout and upstream address, then correlate its request ID with application logs and database-pool metrics. If the application has no matching request, routing or proxy policy may have prevented delivery. If it has a matching request still waiting on a database, raising only the client timeout merely makes the user wait longer. Contain retries while checking whether the operation already committed.

If a client sees `202` but no notification, follow the separate asynchronous notification path. The HTTP response means the API accepted work according to its contract. Check that the order and notification intent were committed together, then inspect worker acknowledgement and retry state. Do not report the notification as sent from an HTTP status alone.

When status and application logs disagree, verify that both refer to the same request and hop. An intermediary can synthesize an error; caches can return an older response; and a client can lose a successful response. Preserve timestamps, request IDs and connection endpoints, then reconcile state before retrying side effects. The recovery procedure follows the evidence to the responsible boundary instead of restarting every process.

## Exercises, review questions and takeaways

1. Run the local health and missing-path requests. Explain the difference between HTTP `404` and connection refusal. Guidance: one is an application-layer response; the other occurs before an HTTP status arrives.
2. Explain why a timed-out `POST /orders` can still have created an order. Guidance: the server may commit before the response is lost; use a durable idempotency contract and reconcile status.
3. A proxy records `504` while the application logs a database wait. Which deadline expired? Guidance: correlate request IDs and stage-specific timing before changing budgets.
4. Decide whether a `202` response is sufficient evidence that a notification was delivered. Guidance: follow the durable notification intent through the worker's acknowledgement and provider result.

Review questions: Which status codes can an intermediary generate? What does `Content-Length` frame? When is it safe to trust `X-Forwarded-For`? Strong answers identify the serving hop, framing boundary and trusted proxy policy.

Follow the request's method and response through every proxy and application boundary. Verify durable application outcomes independently from HTTP transport. Continue to [Chapter 25](025-tls-certificates-and-trust.md) to examine the encrypted and authenticated connection beneath the request.
