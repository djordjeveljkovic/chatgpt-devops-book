---
book: The Complete DevOps Engineering Book
volume: 15
volume_title: "Observability and Telemetry"
chapter: 145
title: "Alertmanager and Actionable Alerts"
slug: alertmanager-and-actionable-alerts
status: complete
summary: ../../_ai/chapter-summaries/145-alertmanager-and-actionable-alerts.md
---

# Chapter 145 — Alertmanager and Actionable Alerts

**Section outline:** separate detection from notification; group by failure domain; route to an accountable owner; test a local notification chain; recover from silence, duplication and telemetry failure.

Prerequisite: [dashboard provisioning](144-grafana-dashboards-and-provisioning.md). An alert should lead to a useful investigation such as the dashboard just constructed.

## Grouping, routing and inhibition

Prometheus evaluates an alert expression; Alertmanager manages the resulting notifications. This separation lets several detectors share routing policy and lets a notification receiver change without rewriting every expression. It also creates distinct failure boundaries: an expression may become true while notification delivery fails, or a notification may arrive while its linked dashboard is unavailable.

An alert instance has identifying labels and explanatory annotations. Labels participate in grouping, routing and identity. An annotation can describe the current measurement or link to a runbook. Do not put a constantly changing numeric value into identifying labels. A changing identity produces a stream of apparently new incidents instead of updates to one incident.

Group alerts according to the unit of action. If one database outage affects ten API replicas, paging ten times is usually less useful than one incident containing the affected services. But grouping every alert in a region can hide simultaneous unrelated incidents. Choose labels that retain an actionable failure boundary, such as environment, service and alert name, then test the policy against actual incident examples.

The initial group wait permits related alerts to accumulate before the first notification. The group interval governs subsequent updates to a group. The repeat interval governs reminders for an unchanged ongoing alert. These are separate delays from the expression's pending period and the receiver's own scheduling. A rule with a two-minute pending period plus a thirty-second group wait cannot promise immediate notification at the first failed scrape.

Inhibition suppresses notifications for a target alert when a matching source alert is active. A fleet-wide outage might inhibit lower-severity warnings for the same service and environment. Keep the equality labels specific enough to avoid suppressing an unrelated service. Missing labels deserve careful review because matching policy can behave unexpectedly when both source and target lack the same dimension. Silences are time-bounded operational exceptions with an owner and reason; inhibition is a reusable dependency relationship.

## Ownership and alert fatigue

A page interrupts a human because prompt action is expected to reduce material harm. A ticket requests scheduled investigation. A dashboard provides context without an interruption. CPU above a threshold might belong in any of these categories depending on service behavior. CPU at ninety percent with low latency and headroom can be efficient usage; CPU at fifty percent with one saturated serial worker can coexist with a broken service.

For Harbor, the fictional small VPS company, two developers share operations. Its alert policy must be feasible for that staffing. Page for acceptance failure, an approaching exhaustion that has a bounded time to failure, and unrecoverable notification backlog. Record predictable maintenance explicitly, including whether it consumes the availability budget. A hundred symptom alerts cannot be managed by two people and will teach them to ignore the channel.

For Summit's managed AWS path, the service provider maintains parts of the infrastructure, but application outcomes still belong to Summit. A managed queue's availability does not prove timely notification delivery. Route age-of-work alerts to the team that can change worker behavior, provider limits or application retry policy. Atlas's Kubernetes platform team can own cluster collection failures while application teams own customer-boundary failures. These ownership divisions follow authority to act, not the novelty of the tool.

Every page needs a first action and an escalation condition. “High latency” without scope or a runbook forces a responder to invent the investigation at night. Include the affected boundary, environment, observation window and a link to evidence. Avoid embedding a secret-bearing query URL in the annotation. Measure page volume, acknowledgment time, repeated incidents and whether the responder had a useful action. Removing an unactionable alert is engineering work, not a reduction in diligence.

## A complete local notification chain

This lab uses the existing Prometheus instance and a verified official Alertmanager release matching the workstation architecture. As with Prometheus, unpack the release in a user-owned directory and record its actual version and checksum. Ubuntu, Fedora and RHEL-compatible systems run the same upstream binaries; no root privilege or distribution-specific package name is required for loopback listeners.

Save `lab_receiver.py` in a scratch directory:

```python
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length <= 1048576:
            self.send_error(413)
            return
        data = json.loads(self.rfile.read(length))
        print(json.dumps({"group": data.get("groupLabels"),
                          "status": data.get("status"),
                          "alerts": len(data.get("alerts", []))}), flush=True)
        self.send_response(204)
        self.end_headers()

HTTPServer(("127.0.0.1", 9080), Handler).serve_forever()
```

The receiver prints a minimal summary rather than forwarding messages to a real person. It is a teaching endpoint, lacking production authentication, persistence and robust malformed-input handling. Run it with `python3 lab_receiver.py`. Keep it on loopback.

Save `alertmanager.yml` beside the Alertmanager binaries:

```yaml
route:
  receiver: lab
  group_by: ['alertname', 'job', 'environment']
  group_wait: 10s
  group_interval: 1m
  repeat_interval: 30m
receivers:
  - name: lab
    webhook_configs:
      - url: http://127.0.0.1:9080/
        send_resolved: true
```

Validate and start from that directory:

```bash
./amtool check-config alertmanager.yml
./alertmanager --config.file=alertmanager.yml \
  --storage.path=./lab-alert-data \
  --web.listen-address=127.0.0.1:9093 \
  --cluster.listen-address=
```

The configuration selects a single local receiver and modest lab timing. The storage path confines state to the lab directory. The web listener is local. The empty cluster-listen address disables cluster listening for this single-process exercise; confirm the flag's accepted form against the installed binary's help before use. Production high availability requires its own network and state discussion, not an unexamined copy of this setting.

Create `lab-alerts.yml` in the Prometheus working directory:

```yaml
groups:
  - name: dispatchdesk-lab
    rules:
      - alert: DispatchDeskLabScrapeFailed
        expr: up{job="dispatchdesk-api"} == 0
        for: 1m
        labels:
          severity: warning
          environment: lab
          owner: dispatchdesk
        annotations:
          summary: 'The lab API metrics endpoint cannot be scraped'
          description: 'Check the endpoint and scraper network context; this is collection evidence.'
```

Add these top-level sections to the existing Prometheus configuration, retaining its earlier global and scrape settings:

```yaml
rule_files:
  - lab-alerts.yml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['127.0.0.1:9093']
```

Run `./promtool check rules lab-alerts.yml` and `./promtool check config prometheus.yml` from the Prometheus directory. Restart the disposable lab Prometheus process to load the settings, or use its documented reload mechanism if deliberately enabled. A service restart interrupts observation; production changes need a reviewed reload and rollback procedure. Do not assume a reload HTTP endpoint is enabled merely because it exists in documentation.

Stop the API, observe the failed scrape, wait for the pending period and group wait, and inspect the local receiver's printed notification. Then restart the API and inspect the resolved notification. The rule is deliberately a collection warning rather than a customer-impact page. It teaches the chain without pretending one failed scrape proves that users cannot submit orders. These commands and notification delivery were not executed during authoring.

## Paging on service impact

A production impact rule needs a valid metric contract and an objective. For this alert-design example, introduce a distinct request-based objective: at least 99.5% of eligible order-submission attempts succeed over a rolling thirty-day window, with attempts during maintenance included. This is separate from Harbor's time-based availability scenario; their denominators must not be mixed. The allowable request failure fraction is 0.005. A sustained measured request failure fraction of 0.05 has a burn-rate ratio of 0.05 / 0.005 = 10 against this request-based objective. The calculation expresses urgency under the same eligible-request definition; it does not prescribe exact paging windows or translate directly into minutes of outage.

Use both a short window that detects current damage and a longer window that resists brief noise. Ensure there is sufficient eligible traffic to interpret the ratio, and separately detect absence or reachability problems. Notification freshness needs another rule because an API can accept orders successfully while workers stop. Page before the notification promise is widely breached when the oldest outstanding work is increasing and the team has a useful recovery action.

Avoid paging only when a queue length exceeds a fixed number. A backlog of 500 may be trivial for a worker completing 1,000 items per second and catastrophic for a worker completing one per minute. Age, arrival rate, completion rate and retry behavior give the queue length meaning. The runbook should ask whether the provider is unavailable, whether workers are failing, or whether arrivals exceeded sustainable capacity.

## Failure and recovery of the alert path

If the expression is true but no notification arrives, inspect the pending/firing state, Alertmanager connectivity, routing matches, silences, inhibition and receiver errors in that order. A silence can be intentional and still be stale. A receiver may accept a webhook while its downstream paging system fails. Test the full path periodically with a controlled alert whose owner expects it.

If duplicate pages arrive, compare alert identities and replica labels. High availability can produce duplicate observations; deduplication policy must preserve the service's identity while allowing independent failures to remain separate. Do not delete environment or service labels merely to reduce duplicates. If an alert flaps, examine whether the threshold lacks recovery hysteresis, whether samples are sparse, or whether the underlying service repeatedly crosses the boundary. Increasing the pending period may hide a real unstable service.

Recovery evidence includes the user-boundary metric, the underlying work state and the notification chain. Resolving the alert is not always resolving the incident: absence of telemetry can remove an expression result. Keep collection coverage visible and confirm the actual service outcome before closing the incident.

## Exercises and takeaways

1. Estimate earliest notification after a continuously failed scrape for the lab rule. Answer guidance: include scrape/evaluation timing, one minute pending and ten seconds group wait; it is not exactly seventy seconds from process failure.
2. Design a grouping key for a regional database outage. Answer guidance: preserve environment and affected service/failure domain, then test whether independent incidents remain distinguishable.
3. The queue is small but its oldest message is one hour old. Answer guidance: inspect poison-message handling or repeated retries; length alone is insufficient.

Primary sources inspected 2026-10-01: [Alertmanager configuration](https://prometheus.io/docs/alerting/latest/configuration/) and [Prometheus alerting rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/). The receiver, routing scenario and objective calculations are original teaching examples; no notification integration was executed.

