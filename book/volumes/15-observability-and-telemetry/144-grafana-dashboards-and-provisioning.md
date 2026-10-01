---
book: The Complete DevOps Engineering Book
volume: 15
volume_title: "Observability and Telemetry"
chapter: 144
title: "Grafana Dashboards and Provisioning"
slug: grafana-dashboards-and-provisioning
status: complete
summary: ../../_ai/chapter-summaries/144-grafana-dashboards-and-provisioning.md
---

# Chapter 144 — Grafana Dashboards and Provisioning

**Section outline:** organize a dashboard around an incident decision; provision a stable data source and complete small dashboard; constrain variables and access; diagnose empty and misleading panels; review dashboard changes as code.

Prerequisite: [PromQL for operational questions](143-promql-for-operational-questions.md). This chapter uses the lab counter from Chapter 141 rather than assuming that the production histogram contract has already been implemented.

## Data sources, queries and panels

A Grafana dashboard is an investigative interface. It should help an engineer decide whether users are affected, which boundary is failing and what evidence to inspect next. A wall of charts can be impressive yet useless if the engineer must guess the population, unit or time range behind every line. Give panels titles that name the measured boundary: “Order request outcomes per second” is more useful than “API stats.”

Grafana queries a configured data source and renders its result. It does not repair a missing scrape, change a metric's meaning or turn a sampled trace into a complete request census. Separate dashboard availability from telemetry availability. If Grafana is unreachable, the Prometheus API may still answer queries; if Prometheus has no samples, changing the panel visualization will not restore them.

A useful first screen has a small number of complementary views. For DispatchDesk, show acceptance throughput, acceptance failure fraction, latency against the stated threshold, outstanding notification age and telemetry coverage. A second screen can expose route, replica, queue and database detail. This arrangement keeps customer impact visible while making diagnosis one deliberate step away. It also prevents a host's CPU chart from becoming the first and only explanation for a business failure.

Use the same time window and units for comparisons. A five-minute error rate beside an instantaneous backlog gauge is legitimate when clearly labeled; treating them as measurements over identical intervals is misleading. A panel's displayed range, query evaluation step and data source's scrape interval are separate settings. Zooming into ten seconds does not create ten-second-resolution evidence from a minute scrape interval.

Prefer stable data-source UIDs in provisioned dashboards. A display name can change without changing the source's identity, and two names can look similar while pointing at different environments. Make environment visible in the dashboard title or a constrained selector, particularly when a responder can access both staging and production. Production-looking charts from the wrong data source have caused many avoidable investigative detours.

## A reproducible local dashboard

Assume Grafana is installed from its official instructions for the reader's chosen release and runs as a service on the same lab host as Prometheus. Installation is intentionally a prerequisite rather than a guessed distribution package command. Ubuntu uses the documented Debian/Ubuntu package repository path; Fedora uses the documented RPM path; RHEL requires checking the release's supported distributions and enabled repositories. Record the actual Grafana version. In this layout, the package's configuration directory is `/etc/grafana`; verify the active service arguments if your installation uses another path.

Save this complete data-source file as `/etc/grafana/provisioning/datasources/dispatchdesk.yaml`, with administrator privileges and permissions allowing the Grafana service to read it:

```yaml
apiVersion: 1
datasources:
  - name: DispatchDesk Lab Prometheus
    uid: dispatchdesk-lab-prometheus
    type: prometheus
    access: proxy
    url: http://127.0.0.1:9090
    isDefault: true
    editable: false
```

This URL is evaluated by the Grafana server. In the stated single-host layout, loopback reaches Prometheus. In a container or separate-host layout, it does not; use a reachable private service address and explicit authentication/TLS as required by that topology. `editable: false` makes the provisioned source's ownership clear. Do not put production credentials in this lab file or commit a credential-bearing source definition to an unrestricted repository.

Create the dashboard provider at `/etc/grafana/provisioning/dashboards/dispatchdesk.yaml`:

```yaml
apiVersion: 1
providers:
  - name: dispatchdesk-lab
    orgId: 1
    folder: DispatchDesk Lab
    type: file
    disableDeletion: false
    allowUiUpdates: false
    options:
      path: /var/lib/grafana/dispatchdesk-dashboards
```

The provider reads dashboard JSON from its directory. The deletion setting should be reviewed as a lifecycle decision: removing a provisioned file can remove its corresponding dashboard. Use a dedicated lab folder and backup production dashboard definitions before changing providers. The JSON model below is a classic dashboard example; Grafana's newer dashboard APIs and schemas are evolving, so validate the installed release's accepted model rather than treating a UI export as timeless.

Create `/var/lib/grafana/dispatchdesk-dashboards/request-outcomes.json`:

```json
{
  "uid": "dispatchdesk-request-outcomes",
  "title": "DispatchDesk Lab — Request Outcomes",
  "schemaVersion": 39,
  "version": 1,
  "tags": ["dispatchdesk", "lab"],
  "timezone": "utc",
  "refresh": "15s",
  "time": {"from": "now-30m", "to": "now"},
  "panels": [
    {
      "id": 1,
      "title": "Accepted and rejected requests per second",
      "type": "timeseries",
      "gridPos": {"h": 9, "w": 24, "x": 0, "y": 0},
      "datasource": {"type": "prometheus", "uid": "dispatchdesk-lab-prometheus"},
      "targets": [
        {
          "refId": "A",
          "expr": "sum by (result) (rate(dispatchdesk_requests_total[5m]))",
          "legendFormat": "{{result}}"
        }
      ],
      "fieldConfig": {
        "defaults": {"unit": "reqps", "min": 0},
        "overrides": []
      },
      "options": {
        "legend": {"displayMode": "list", "placement": "bottom"},
        "tooltip": {"mode": "multi"}
      }
    },
    {
      "id": 2,
      "title": "API scrape health: 1 succeeds, 0 fails",
      "type": "timeseries",
      "gridPos": {"h": 7, "w": 24, "x": 0, "y": 9},
      "datasource": {"type": "prometheus", "uid": "dispatchdesk-lab-prometheus"},
      "targets": [
        {"refId": "A", "expr": "up{job=\"dispatchdesk-api\"}", "legendFormat": "{{instance}}"}
      ],
      "fieldConfig": {
        "defaults": {"min": 0, "max": 1},
        "overrides": []
      },
      "options": {"legend": {"displayMode": "list", "placement": "bottom"}}
    }
  ]
}
```

The dashboard intentionally includes collection health so that a quiet outcome chart does not automatically suggest healthy inactivity. `schemaVersion: 39` identifies the example model, not a claim about the current Grafana release. Import it into a lab instance of your chosen release and inspect any migration/export changes before using it as a maintained artifact.

Once the files exist and are readable by the service account, restart the lab service with `sudo systemctl restart grafana-server`, provided that is the unit name installed by your package. Inspect `systemctl status grafana-server --no-pager` and `sudo journalctl -u grafana-server -n 100 --no-pager`. Restart interrupts active users, so schedule it for production and use the documented reload/lifecycle behavior supported by the installed release where appropriate. `-u` selects the unit, `-n 100` bounds recent records and `--no-pager` makes terminal output direct. These systemd commands apply to both Ubuntu and Fedora/RHEL package installations with that unit name.

Log into the lab Grafana UI through its configured local endpoint and open the DispatchDesk Lab folder. Send accepted and rejected requests to the teaching API, allow several scrape intervals, and compare the chart with the same PromQL in Prometheus. Stop the API and verify that scrape health changes independently of request history. These are reader validation steps; the chapter does not claim that provisioning or import was executed by the author.

## Variables, provisioning and access

A dashboard variable is a query input, not authorization. A tenant selector that hides other tenants in the UI does not prevent users from querying them through another dashboard or the data-source API. Enforce data access at the appropriate Grafana organization, data-source permission, backend authorization or tenant boundary. Select the mechanism according to the edition and backend capabilities actually deployed.

Begin with a constrained environment selector rather than a free-form text field. For a service selector, return the known service labels from the relevant data source. Keep “All” behavior explicit: a selector that expands to every service can make an incident panel expensive and can obscure a single failing service. Multi-value interpolation changes query syntax; inspect the generated query using Grafana's query inspection tools before accepting the dashboard.

A variable cannot add a label that the metric producer never emitted. The lab API has `result` but not route or tenant labels. Adding a route selector to its dashboard without changing instrumentation creates an empty query, not route-level observability. This simple constraint becomes important in large organizations where a shared dashboard assumes metric contracts that only some services follow.

Treat provisioned dashboards as reviewed operational code. Store the JSON and source/provider definitions in a repository with owners. A UI edit to a provisioned dashboard may be constrained or overwritten by the provisioning lifecycle, depending on the configuration and release. Choose whether the repository or the UI is authoritative, and document how a useful incident-time edit becomes a durable change. Otherwise responders recreate the same panel every outage.

## Diagnosing blank or misleading panels

When a panel is empty, inspect the chain in order: selected data source, generated query, time range, raw backend response and target coverage. Query the backend directly using the same expression. If the backend returns series, inspect transformations, label filters, field overrides and panel unit settings. If it returns none, investigate metric names, variable expansion and collection before editing the visual styling.

A panel that suddenly drops to zero may have a counter reset, a zero-filled gap, a changed label selector or actual activity loss. Disable misleading fill settings during diagnosis and inspect raw values. A line drawn continuously through a long gap can suggest evidence that was never collected. Keep absence visually distinct when the signal's absence is operationally meaningful.

If dashboard loading overwhelms the backend, measure query duration and selected-series count. Reduce unnecessarily broad selectors and excessive refresh frequency. Precompute stable expensive aggregates with recording rules where the tradeoff is justified. Do not increase backend capacity before checking whether forty panels all repeat the same fleet-wide expression every five seconds.

## Exercises and takeaways

1. Add a table of instance scrape health. Answer guidance: query `up{job="dispatchdesk-api"}` and preserve instance labels; distinguish no matching targets from observed zero values.
2. Move Grafana into a container. Explain the required URL change. Answer guidance: its loopback now refers to the container; configure a private network address or service name reachable from Grafana's actual runtime.
3. A panel displays 2,000% errors when the raw fraction is 0.2. Answer guidance: inspect both query multiplication and percentage-unit mode; apply exactly one conversion.
4. A tenant variable is proposed as a privacy boundary. Answer guidance: reject that assumption and require backend or data-source authorization that survives arbitrary queries.

A useful dashboard makes its population, units, freshness and gaps legible. Provisioning makes that design reproducible, but review and access controls make it dependable during an incident.

Source inspected on 2026-10-01: [Grafana provisioning documentation](https://grafana.com/docs/grafana/latest/administration/provisioning/). The classic JSON example requires installed-release validation; no Grafana instance was started or dashboard imported during authoring.

