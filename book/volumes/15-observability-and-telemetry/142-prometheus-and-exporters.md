---
book: The Complete DevOps Engineering Book
volume: 15
volume_title: "Observability and Telemetry"
chapter: 142
title: "Prometheus and Exporters"
slug: prometheus-and-exporters
status: complete
summary: ../../_ai/chapter-summaries/142-prometheus-and-exporters.md
---

# Chapter 142 — Prometheus and Exporters

**Section outline:** understand target identity; run a local scrape lab; separate exporter health from service health; design discovery and retention; recover from missing data.

Prerequisite: [questions and evidence](141-observability-from-questions-to-evidence.md). Its Python endpoint supplies the application metrics for this chapter; keep its in-memory limitation in mind.

## Scrapes, labels and time series

Prometheus turns successive observations of an endpoint into time series. The endpoint exposes the current values; Prometheus supplies the observation schedule and stores samples. This distinction matters when the network fails. A counter may continue increasing inside a healthy application while its scraper cannot reach it. The monitoring system then has a gap, not evidence of zero business activity.

The metric name and complete label set identify a series. Changing `instance` creates a new identity even if the replacement process serves the same role. A restart on the same address usually resets process-local counters without changing their label set. Keep both facts in mind when interpreting a deployment: continuity of a service is different from continuity of a process. Query rates over counters rather than subtracting the first visible value from the last without accounting for resets.

A job groups targets under a common scraping purpose. A node-exporter job provides host observations; an API job provides application observations. Neither label is an access boundary or an owner assignment by itself. Assign owner, service and environment deliberately so that discovery can create stable operational meaning. Avoid putting an ever-changing deployment timestamp into every metric when a single deployment-information metric or event provides the same investigative value.

Scraping is active work. With 2,000 targets every 15 seconds, the system starts roughly 133 scrapes each second, although their timing is distributed rather than perfectly uniform. If each target exposes 1,500 series, that is approximately 200,000 samples per second before considering scrape duration and errors. These are planning calculations, not a benchmark. Network traffic, parsing, write-ahead logging, memory and queries all compete for resources. A scrape interval should follow the decision cadence: a five-second incident signal and a fifteen-minute business report need different freshness.

## A local monitoring lab

Use the official release archive matching your workstation architecture, verify its published checksum, and unpack it into a user-owned lab directory. The book does not invent an archive name or release number: record the actual release and checksum you downloaded. Use the same release's `prometheus` and `promtool` binaries. This upstream-binary route works on Ubuntu, Fedora and RHEL-compatible Linux without depending on differently named distribution packages. Do not replace an existing system service with the lab binaries.

In the directory containing those binaries, create `prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  scrape_timeout: 5s
  evaluation_interval: 15s
scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ['127.0.0.1:9090']
  - job_name: dispatchdesk-api
    static_configs:
      - targets: ['127.0.0.1:8080']
        labels:
          service: dispatchdesk-api
          environment: lab
  - job_name: node
    static_configs:
      - targets: ['127.0.0.1:9100']
        labels:
          environment: lab
```

The loopback addresses refer to the host running Prometheus. They would refer to the container itself if Prometheus ran in a container; copying this file into a container does not preserve the host-network meaning. The five-second timeout bounds a scrape below the fifteen-second interval. A missing node exporter will make the node target fail while the other jobs remain independently observable.

Validate and run as your ordinary user:

```bash
./promtool check config prometheus.yml
./prometheus --config.file=prometheus.yml \
  --storage.tsdb.path=./lab-data \
  --storage.tsdb.retention.time=2d \
  --web.listen-address=127.0.0.1:9090
```

The first command checks the file before a running server depends on it. The server command chooses its configuration, keeps the lab database in a clearly scoped directory, requests two days of time retention and binds the web listener to loopback. Retention is a space-planning input, not a promise that every byte disappears at an exact second. Keep additional disk headroom for active ingestion and operational work. The flags are checked against the installed binary's `--help`; do this before adopting a release because startup options are release-sensitive.

Run the Python API from Chapter 141 in another terminal. In the browser at `http://127.0.0.1:9090`, inspect target health and query `up{job="dispatchdesk-api"}`. Send accepted and rejected requests, then query `dispatchdesk_requests_total`. Wait for at least two scrape intervals before expecting observations. The counter value should follow application activity; it is not a count of scrapes. No measured output is claimed here.

Download and verify the official node-exporter archive in the same manner, unpack it in its own directory, and run:

```bash
./node_exporter --web.listen-address=127.0.0.1:9100
curl --fail --silent --show-error http://127.0.0.1:9100/metrics
```

The listener flag confines the teaching service to the workstation. Curl's failure flag rejects HTTP error responses, silent suppresses its progress meter, and show-error preserves diagnostics. Host observations include CPU, memory and filesystem families, subject to the collectors enabled in the installed exporter and the host's available interfaces. Inspect the actual exposition instead of assuming every metric exists on every operating system.

For a persistent service, package the verified binary and unit through the infrastructure workflow rather than leaving a terminal session running. Ubuntu and Fedora/RHEL share systemd but differ in package availability and security policy. On Ubuntu check AppArmor denials if a confinement profile applies. On Fedora/RHEL check SELinux audit records before changing policy; do not use disabling enforcement as an installation step. A native exporter usually needs read access to host interfaces rather than broad write privileges. Keep the listener on a private management interface and permit only the scraper through the host firewall when moving beyond the local lab.

## Exporters, discovery and retention

An exporter translates another system's observations into a scrape endpoint. Its own HTTP success is not the same as the monitored dependency's success. A database exporter might return metrics while its database connection fails, with a metric describing the collection failure. Conversely, an exporter process can die while the database continues serving applications. Alert separately on missing collection and on evidence of database impact.

Static targets are easy to review for three VPS hosts. They become unreliable when tasks are rescheduled frequently. Discovery should obtain targets from the system that owns their lifecycle: file discovery for a controlled inventory, cloud discovery for instances, or Kubernetes discovery for cluster objects. Relabeling converts discovery metadata into operational labels and can filter unwanted endpoints. Metric relabeling acts on scraped samples. Confusing these stages causes surprising behavior: filtering a metric does not remove the scrape target, and dropping a target removes all its observations.

A discovery permission is a credential with its own lifecycle. Grant read access to the required inventory, not application-administration privileges. When discovery fails, existing targets and new targets may behave differently depending on the discovery implementation and failure. Monitor refresh errors and compare the expected deployment count with observed target count. A list of healthy targets is insufficient when half the service instances never entered the list.

Local retention fits a small VPS team's recent operational questions. A longer historical requirement may justify remote storage, but it adds another queue, network path and cost center. Keep local emergency evidence when appropriate, and observe remote-write backlog and failures. Sending all data to a central system does not automatically make collection more reliable. Decide what happens during a prolonged remote-storage outage: how much buffering is affordable, which data is lost and which business records still establish correctness.

## Failure evidence, diagnosis and recovery

Intentionally stop the API with Ctrl-C. After the scraper observes the failure, its target health should indicate a connection error and the generated `up` series should be zero. The accepted-order counter is not a fresh zero; it is no longer being observed. Restart the API, send an order, and examine the recovered scrape alongside the counter reset. This exercise separates scrape failure, application restart and business-state loss.

If curl reaches the endpoint but Prometheus does not, run curl from Prometheus's execution context. A host command reaching loopback tells you little about a container's loopback network. Inspect the target URL and last scrape error. Connection refused suggests no listener at that address; timeout suggests path, firewall or a stuck endpoint; HTTP unauthorized suggests missing authentication; parsing errors suggest exposition problems. These are hypotheses to test, not definitive diagnoses solely from one phrase.

If ingestion suddenly fails after a release, compare sample counts and series growth with the deployment. An accidental user-ID label can expand series dramatically. A configured sample limit may protect the scraper by rejecting a whole oversized scrape, producing missing observations rather than silently collecting the first portion. Recover by reverting the instrumentation or removing the unbounded label at the source. Dropping selected samples can be a temporary containment measure, but preserve the metrics needed to evaluate user impact.

When the storage volume is full, first stop uncontrolled growth and restore headroom using the documented storage procedure for your installed release. Do not delete arbitrary live database files. Consider stopping the lab server and moving its entire lab directory aside if the data is disposable; for production, follow a reviewed recovery plan and preserve forensic evidence. Verification requires successful scrapes, advancing sample timestamps, stable free space and queries over the incident window. A green process status proves only that the process is running.

## Exercises and operational takeaways

1. Move the API to a second host. Answer guidance: replace loopback with its private reachable address, define narrowly scoped firewall access, and test from the scraper host. Keep the metrics endpoint away from public ingress.
2. Explain why `up=1` is insufficient for order delivery. Answer guidance: it describes a successful scrape; use business-boundary metrics and durable records for delivery outcomes.
3. Estimate ingestion for 500 targets exposing 800 series every 20 seconds. Answer guidance: 500 × 800 / 20 = 20,000 samples per second before retries, extra jobs or changing series.

Review target identity, discovery coverage, bounded labels, listener exposure and retention headroom before increasing collection volume. Exporter availability and application reliability deserve separate evidence.

Documentation inspected on 2026-10-01: [getting started](https://prometheus.io/docs/prometheus/latest/getting_started/), [configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/), and [node exporter guide](https://prometheus.io/docs/guides/node-exporter/). The lab has not been executed during authoring; release-specific flags and enabled collectors require validation against the selected binaries.

