---
book: The Complete DevOps Engineering Book
volume: 15
volume_title: "Observability and Telemetry"
chapter: 146
title: "Logs with Journald and Loki"
slug: logs-with-journald-and-loki
status: complete
summary: ../../_ai/chapter-summaries/146-logs-with-journald-and-loki.md
---

# Chapter 146 — Logs with Journald and Loki

**Section outline:** define an event contract; preserve useful local evidence; collect selected journals with Alloy; query Loki by bounded streams then event fields; recover from gaps, overload and retention mistakes.

Prerequisite: [actionable alerts](145-alertmanager-and-actionable-alerts.md). Logs provide the event-level evidence behind an alert, but they are not the authority for accepted orders.

## Structured events and correlation

A DispatchDesk notification worker should distinguish `notification_attempted`, `notification_provider_accepted`, `notification_retry_scheduled` and `notification_failed_terminal`. These names describe different boundaries. A single ambiguous “sent” line prevents a responder from knowing whether code prepared a message, opened a connection or received confirmation. Design the vocabulary before choosing the log backend.

Use a consistent JSON object per event. Include an event name, severity, service, timestamp, request or trace reference, attempt count and a bounded outcome code where appropriate. Do not record full message contents, credentials or authorization headers. A controlled order reference may support support-team investigation, but access and retention must follow the sensitivity of the associated customer record. Correlation is useful only if it does not create a new uncontrolled copy of private data.

A representative event, explicitly illustrative rather than measured, is:

```json
{
  "event": "notification_retry_scheduled",
  "service": "dispatchdesk-worker",
  "level": "warning",
  "order_ref": "example-order-17",
  "trace_id": "example-correlation-reference",
  "attempt": 3,
  "outcome": "provider_timeout",
  "retry_after_seconds": 30
}
```

The trace reference above is a teaching placeholder, not a valid generated trace ID. Real instrumentation obtains the actual identifier from its active context. Attempt count is event data; it should not create a new Loki stream for every attempt. Provider response text may contain arbitrary sensitive content, so prefer a reviewed outcome code and retain any detailed response only under an explicit need and access policy.

Timestamps need a convention. Use UTC for cross-host investigation, synchronize hosts and retain collector arrival time when useful. A provider timestamp, application timestamp and ingestion timestamp describe different moments. A delayed collector can make an old incident appear new if a dashboard defaults to ingestion time. Trace duration should use an appropriate monotonic clock within a process; wall-clock jumps can distort naïve duration calculations.

## Local evidence with journald

When systemd supervises an application whose standard output goes to the journal, JSON appears inside the journal's `MESSAGE` field. `journalctl -o json` returns the journal entry as JSON; it does not automatically flatten the application's JSON into top-level journal fields. This nested structure matters when a collector is configured to parse event fields.

Assume a real system service named `dispatchdesk-worker.service` exists from the deployment workflow. On an Ubuntu or Fedora/RHEL systemd host, an authorized operator can inspect a bounded UTC window:

```bash
sudo journalctl -u dispatchdesk-worker.service \
  --since '2026-10-01 09:00:00 UTC' \
  --until '2026-10-01 09:15:00 UTC' \
  --utc --no-pager -o json
```

The unit option limits scope to the worker; since and until bound the incident window; UTC makes human display consistent; no-pager avoids an interactive pager; JSON preserves structured journal fields. The date is an example investigation window, not a claim that these records exist. Administrative access may be needed to read the system journal. Export only the necessary records to an access-controlled incident artifact.

For current activity, use:

```bash
sudo journalctl -u dispatchdesk-worker.service -n 100 -f --no-pager
```

`-n 100` starts with a bounded tail and `-f` follows new entries until Ctrl-C. It is an interactive observation command, not a completion check for an automation script. A quiet follow session can mean no events, wrong unit selection, insufficient permissions or an application writing somewhere else. Compare with the unit configuration and a controlled event.

Ubuntu and Fedora/RHEL both provide these systemd interfaces, but persistence and access configuration can differ by installation. Inspect the actual journal storage configuration and filesystem state before assuming reboot survival. On SELinux-enforcing Fedora/RHEL, preserve labels and inspect denied access rather than widening filesystem permissions or disabling enforcement. On Ubuntu, an applicable AppArmor profile can also restrict the collector. Log-reading privilege gives access to potentially sensitive system events; grant only the intended collection account and scope.

Before an incident consumes the disk, inspect `journalctl --disk-usage`. Journal vacuum commands remove historical evidence and are destructive retention operations. Define retention centrally and reserve application/storage headroom; do not reactively erase an incident window before exporting necessary evidence. Rotating and vacuuming have specific interactions with active and archived files, so use the installed systemd manual for the intended maintenance procedure.

## Collection, labels and retention

Loki organizes logs into streams identified by labels. Choose a small set of stable labels such as service, environment and host. Keep request IDs, order IDs and detailed outcomes inside the event, or use appropriate structured metadata when deliberately supported and configured. Creating a stream per request defeats the storage model and increases indexing and ingestion overhead.

### Assemble the loopback Loki backend

Download the official Loki and Alloy Linux binaries for your workstation architecture, verify their published checksums, and place the unpacked executables in a dedicated user-owned `loki-lab` directory as `loki` and `alloy`. Record the actual release versions. This upstream-binary route avoids assuming identical package names across Ubuntu 24.04, Fedora 44 and RHEL 9. Use the selected Loki release's matching configuration documentation; the following minimal TSDB/filesystem configuration follows the inspected upstream local configuration and is an isolated single-process lab.

Create `loki.yaml` in that directory:

```yaml
auth_enabled: false
server:
  http_listen_address: 127.0.0.1
  http_listen_port: 3100
  grpc_listen_address: 127.0.0.1
  grpc_listen_port: 9096
common:
  instance_addr: 127.0.0.1
  path_prefix: ./loki-data
  storage:
    filesystem:
      chunks_directory: ./loki-data/chunks
      rules_directory: ./loki-data/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory
schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: lab_index_
        period: 24h
analytics:
  reporting_enabled: false
```

The schema date selects a period that already covers the lab's event timestamps; it is not a source-publication date. One replica and filesystem storage intentionally provide no host-failure tolerance. Authentication is disabled only because both listeners remain loopback in this isolated exercise. This configuration does not enable production retention, backups or tenant isolation. Do not expose either listener publicly.

From `loki-lab`, as the ordinary user owning the directory, run:

```bash
mkdir -p loki-data/chunks loki-data/rules
./loki -config.file=loki.yaml
```

The directory creation makes the state locations explicit. Loki remains in the foreground; a configuration error appears in its startup diagnostics rather than being hidden behind a service manager. In another terminal, check readiness with `curl --fail --silent --show-error http://127.0.0.1:3100/ready`. Readiness should eventually return success, but readiness alone does not prove that a worker event can be collected and queried. Ctrl-C stops the lab. State remains in `loki-data`; deleting that directory would destroy the lab's stored evidence, so leave cleanup to an explicit decision after the exercise.

For a completely reproducible source event without the production worker, use a distinct transient systemd unit. This administrative command creates a short-lived **lab** service on the host:

```bash
sudo systemd-run --unit=dispatchdesk-worker-lab --wait \
  /usr/bin/printf '%s\n' \
  '{"event":"notification_retry_scheduled","outcome":"provider_timeout","order_ref":"example-order-17"}'
```

`--unit` gives the journal a distinct lab identity and `--wait` waits for the process result. Standard output uses the transient service's normal journal path; inspect the resulting unit records with `sudo journalctl -u dispatchdesk-worker-lab.service -n 10 --no-pager`. The command executes only printf and sends no notification. Set the Alloy graph's `matches` to `_SYSTEMD_UNIT=dispatchdesk-worker-lab.service` for this test, then restore the real worker match when intentionally monitoring that service.


The following complete Alloy collection graph reads only the stated worker unit and writes to the loopback backend just assembled. Production needs separately reviewed authentication, tenancy, TLS and storage configuration.

Save `worker.alloy` in a user-owned configuration directory:

```text
loki.source.journal "worker" {
  matches    = "_SYSTEMD_UNIT=dispatchdesk-worker.service"
  labels     = { service = "dispatchdesk-worker", environment = "lab" }
  max_age    = "1h"
  forward_to = [loki.write.local.receiver]
}

loki.write "local" {
  endpoint {
    url = "http://127.0.0.1:3100/loki/api/v1/push"
  }
}
```

The journal source's match is exact, not a substring filter. The one-hour maximum age bounds initial collection for the lab. The default event body is the journal message; with an application emitting one JSON object per line, LogQL can parse those fields later. The write component supplies the receiver to which the source forwards. Copy `worker.alloy` into the `loki-lab` directory. From that directory, use the same verified binary for validation and execution:

```bash
./alloy validate worker.alloy
mkdir -p alloy-data
./alloy run --storage.path=./alloy-data \
  --server.http.listen-addr=127.0.0.1:12345 worker.alloy
```

Run as the user owning this lab directory after verifying that account can read the selected journal. If it cannot, use the reviewed collector-account access procedure below rather than starting the process as root. The positional argument names the configuration, `--storage.path` gives components a writable state location, and the HTTP flag confines diagnostics to loopback. Validation returns zero for accepted configuration and nonzero with diagnostics for invalid input; it does not test journal access or Loki delivery. The foreground run continues until interrupted. Inspect its component diagnostics at the loopback HTTP endpoint, generate the controlled source event, and query Loki to verify flow. Preserve the state directory across normal restarts so collection state is not accidentally discarded.

The official component instructions describe membership in `adm` and `systemd-journal` for the packaged `alloy` account. On Ubuntu, verify both groups exist before applying the documented membership command. On Fedora/RHEL, inspect the installed package account, existing groups and journal ACL policy rather than inventing an `adm` group to copy a Debian-oriented command. The required outcome is demonstrated read access for the collector account under the host's security model. Restart a system service after a membership change so its process receives the new supplementary groups.

An especially dangerous failure is a healthy-looking collector with no readable journal. Component configuration health alone does not prove events are flowing. Generate a controlled worker event and check it locally, then check collection counters and finally query Loki. Observe each boundary, because an empty dashboard could result from no source events, denied reading, a wrong match, blocked writing or a wrong query.

Retention needs both a time requirement and a volume estimate. If an expanded scenario emits 100 events per second at an average serialized size of 600 bytes, raw event payload is roughly 60,000 bytes per second, or about 5.18 GB per day before compression, metadata, replication and storage overhead. These are scenario arithmetic, not a Loki sizing guarantee. Measure real payload distribution and ingest/query behavior before buying storage. A debug release that triples event rate can change the budget even when request volume stays constant.

## Following an error across services

First select streams narrowly, then inspect event contents:

```logql
{service="dispatchdesk-worker", environment="lab"}
  | json
  | event="notification_retry_scheduled"
  | outcome="provider_timeout"
```

The stream selector reduces the search population. The JSON parser extracts event fields for subsequent filters. This query assumes the message itself is the JSON object; a collector forwarding the entire journal envelope would need to parse its `MESSAGE` field as a second step. Inspect one raw entry before constructing a complicated parser.

For a known controlled order reference:

```logql
{service="dispatchdesk-worker", environment="lab"}
  |= "example-order-17"
  | json
  | order_ref="example-order-17"
```

The initial line filter is a cheap content restriction, while the parsed-field equality confirms the specific field. It does not authenticate the reader or authorize tenant access. Backend tenancy and UI access must protect the data independently of query conventions.

A fictional incident shows repeated timeouts for one provider beginning immediately after a proxy change. Compare worker events, proxy connection errors and deployment times. Find whether retries have scheduled deadlines and whether a terminal outcome exists. If there is a provider acknowledgment but the worker retries anyway, the problem may be lost acknowledgment state or duplicate-effect handling; blindly increasing the timeout can produce more duplicate notifications.

Recover by restoring the known-good proxy configuration or fixing the provider path, preserving queued work and bounding retry concurrency. Verify a controlled notification's provider acceptance, its durable final state and declining oldest-work age. A reduction in error logs may mean successful recovery, disabled logging, reduced traffic or collection failure. Use the business state and pipeline coverage to distinguish them.

## Gaps, overload and assessment

When events vanish, inspect local journal retention and collector progress before blaming the query backend. An agent outage longer than local retention can create an unrecoverable log gap. A source replay can create duplicate log records; an event ID helps reconcile them but should remain event data rather than a stream label. Logs are investigative evidence, so business workflows must tolerate losing a log without losing the accepted order.

Under overload, protect application behavior. Avoid blocking the request path indefinitely on a remote log sink. Choose buffering and drop policy deliberately, monitor lost-event counts and retain essential local evidence where feasible. Sampling repeated debug events can reduce cost, but errors that establish terminal business outcomes may need a different policy. Document which event classes can be absent and what remains authoritative.

Exercises:

1. A journal JSON export has a `MESSAGE` string containing JSON. Answer guidance: parse the envelope and then the message; do not assume application fields are top-level.
2. A collector says healthy but sends no logs. Answer guidance: prove source event existence, account read access, exact unit match, write connectivity and backend query scope in sequence.
3. Estimate raw daily payload for 20 events per second at 1,000 bytes each. Answer guidance: about 1.728 GB per day before storage effects; benchmark actual system overhead separately.
4. Decide whether order reference should be a Loki label. Answer guidance: retain it in controlled event data; its unbounded cardinality makes it unsuitable for stream identity.

Primary documentation inspected 2026-10-01: [Loki labels](https://grafana.com/docs/loki/latest/get-started/labels/), [LogQL log queries](https://grafana.com/docs/loki/latest/query/log_queries/), [Alloy journal source](https://grafana.com/docs/alloy/latest/reference/components/loki/loki.source.journal/) and [Alloy Loki writer](https://grafana.com/docs/alloy/latest/reference/components/loki/loki.write/), [Alloy validate](https://grafana.com/docs/alloy/latest/reference/cli/validate/), [Alloy run](https://grafana.com/docs/alloy/latest/reference/cli/run/), [Loki configuration](https://grafana.com/docs/loki/latest/configure/) and [upstream local Loki configuration](https://github.com/grafana/loki/blob/main/cmd/loki/loki-local-config.yaml). The local `journalctl --help` was inspected for the listed CLI options; the online systemd manual retrieval failed. No journal collection, Alloy configuration validation or Loki integration was executed.

