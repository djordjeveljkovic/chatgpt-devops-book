---
book: The Complete DevOps Engineering Book
volume: 1
volume_title: "Engineering Mental Models"
chapter: 7
title: "Learning to Investigate"
slug: learning-to-investigate
status: complete
summary: ../../_ai/chapter-summaries/007-learning-to-investigate.md
---

# Chapter 7 — Learning to Investigate

## Observation, hypotheses and experiments

“The service is slow” is the beginning of an investigation, not its conclusion. Which operation is slow? For whom? Since when? Compared with what baseline? DispatchDesk's order creation may be delayed while existing-order lookup remains fast. That difference can identify the relevant write path long before a general host dashboard explains anything.

Read [Environments and Reproducibility](006-environments-and-reproducibility.md) first. This chapter teaches a repeatable reasoning process and a small diagnostic notebook. The later networking and performance volumes supply specialized tools. You can practice the notebook using the fictional evidence below; a curl probe requires an already running lab service and is not claimed to create one.

An **observation** is something obtained from an identifiable source: a request returned HTTP 503, the pending queue contains older work, or a process exited at a recorded time. An **interpretation** explains what the observation might mean. “Database failure caused the 503” is an interpretation until you connect it to evidence. Keeping these distinct prevents an early guess from becoming the incident's accepted history.

A **hypothesis** proposes a mechanism consistent with observations. Suppose order creation slowed immediately after a release. One hypothesis is that a new query scans too many rows. Another is that the release selected a different database destination. A third is that unrelated storage contention started at the same time. Timing makes the release worth examining; it does not establish which mechanism caused the delay.

An **experiment** obtains evidence that distinguishes hypotheses. Inspecting the activated configuration can test the destination hypothesis without changing production. Comparing query durations can test the new-query hypothesis. Temporarily disabling a known background job may test storage contention, but that is a state change with its own consequences and recovery requirement. Prefer a discriminating read-only observation when it can answer the question.

Before an experiment, predict results. If the API is waiting on a database connection pool, you expect connection-acquisition time to grow before query execution begins. If the query itself is slow, acquisition may remain short while execution grows. If both measurements are missing, you have an instrumentation gap rather than proof of either explanation. Write what evidence would weaken your hypothesis, not merely what would support it.

Google's 2016 [Effective Troubleshooting chapter](https://sre.google/sre-book/effective-troubleshooting/) discusses iterative hypothesis testing and the importance of system knowledge. The original DispatchDesk method here applies that principle to a small service. Familiarity helps you choose plausible mechanisms, but familiarity can also anchor you on yesterday's incident. A remembered fix is a candidate action, not a diagnosis.

## Evidence quality and uncertainty

Evidence has boundaries. A successful request from the host proves less about external users than a successful request through their actual access path. A host-level metric aggregates work from multiple processes. A trace may be sampled and omit the failed request. A log line may record an attempted action rather than its completion. Knowing these limits lets you combine signals instead of declaring one authoritative.

Time alignment matters. Record timestamps with their timezone or offset, and determine whether sources share a reliable clock. A client at 14:03 local time and a service log at 12:03 UTC may describe the same event. A clock offset can make a response seem to precede its request. Do not build a causal timeline without checking how time was recorded.

Missing evidence is ambiguous. No error log can mean no error, a disabled logger, a dropped record or a process that crashed before emitting it. No traffic metric can mean idle traffic or a broken metrics path. The best next observation often checks the measuring system itself. For example, a synthetic request with an identifiable test marker can establish whether the expected log appears, subject to privacy and sampling policy.

Compare affected and unaffected cases. If all customer accounts fail, a shared dependency is plausible. If one tenant fails on one operation, look for account-specific data, permission or routing differences. If one replica fails while another succeeds, compare artifact and configuration identity. Define the comparison dimensions before collecting hundreds of unrelated dashboard screenshots.

A useful evidence record states source, scope and confidence:

| Evidence | Scope | What it supports | What remains unknown |
|---|---|---|---|
| API health probe succeeds locally | One host and endpoint | Process can answer | External path and database writes |
| Controlled order creation times out | One request | That operation failed within deadline | Whether its transaction committed |
| Pending notifications are old | Observed stored work | Worker progress is delayed | Cause and provider completion state |
| New artifact active on one replica | One replica | Release placement | Other replica identity |

Avoid attaching certainty percentages without a model. “Likely because two independent observations agree” is more useful than an invented “95% confidence.” State what could still overturn the conclusion and which action is safe under that uncertainty.

## A disciplined troubleshooting notebook

During an incident, a notebook reduces repeated work and makes handoff possible. Record a concise problem statement, impact, timeline, observations, hypotheses, tests, decisions and the next owner. It should be readable by someone who did not watch your terminal.

```markdown
# DispatchDesk investigation — fictional exercise

Expected: valid order requests persist and return an identifier.
Observed: creation requests exceed the client's five-second deadline.
Scope: order creation affected; existing-order lookup still succeeds.
First known symptom: 2026-10-01 12:05 UTC.

## Observations
12:07 UTC: activated release identifier changed at 12:00 UTC.
12:09 UTC: API process health remains responsive.
12:11 UTC: create-order database execution duration increased.
12:12 UTC: database connection-acquisition duration stayed near baseline.

## Hypotheses
H1: a changed write query is slower for realistic data volume.
H2: connection-pool exhaustion delays work before execution.

## Discriminating evidence
H1 predicts longer execution duration for the changed query.
H2 predicts increased acquisition wait; current evidence weakens H2.

## Next step
Compare query behavior with the previous compatible release in a safe test environment.
Owner: current service responder.
Do not replay timed-out production requests without checking acceptance state.
```

Every line is illustrative, not a measured result. The notebook's distinction between acquisition and execution gives the next responder a specific question. It also preserves an important uncertainty: the client timed out, but the order might have committed. Later retry work must not turn a diagnostic test into duplicate orders.

A bounded timing probe can add evidence when a lab API already exists:

```bash
curl --silent --show-error --connect-timeout 2 --max-time 5 \
  --output /dev/null \
  --write-out 'status=%{http_code} connect=%{time_connect} first_byte=%{time_starttransfer} total=%{time_total}\n' \
  http://127.0.0.1:8080/healthz
```

Run as an ordinary user on the host serving the lab API, from any directory. It requires curl and a service on loopback port 8080. The flags are the same across Ubuntu, Fedora and RHEL; this chapter does not install or start that service. `--output` discards the body. The write-out fields report HTTP status and elapsed times from the transfer's start to connection establishment, first response byte and transfer completion. The [curl manual](https://curl.se/docs/manpage.html) defines these variables and timeouts.

Those are cumulative timings, not direct measurements of database work. For a loopback HTTP probe there is no external network path and no TLS handshake. Do not interpret a quick health result as proof of fast order creation. A refused connection, a timeout and an HTTP error status are distinct results. The command does not request failure solely on HTTP error status; inspect the status and curl's own error before using it in automation.

A diagnostic command must have an evidence question. Repeating the health probe can establish intermittency at that endpoint, but polling it aggressively can itself create load. For production, choose an approved interval and retain context about execution location. Never include credentials in shared command transcripts; a useful notebook records sanitized inputs and the relevant identity scope.

## Recovery while the cause is still uncertain

The notebook suggests a changed query. The team can reduce impact before fully explaining its cost if a previous artifact is known to be compatible with the active schema and restores the required behavior. That compatibility is a precondition, not a wish. If the release changed stored data irreversibly, rolling back the executable may fail or damage state.

Suppose comparison in a representative test database shows the new query touches substantially more rows. The team restores the compatible previous artifact, verifies controlled order acceptance and checks whether timed-out requests already created orders. It then repairs the query, tests with representative data shape and records the measured behavior. The incident is not closed by a green process status: user operations and uncertain work need verification.

Do not perform five changes at once simply because all are reversible individually. Restarting the API, increasing connections, resizing the database and rolling back in one interval can restore service while concealing which change mattered. Sometimes urgency requires several mitigations, but record their order and preserve evidence. A later controlled experiment can then recover the causal explanation.

Afterward, improve the weakest evidence link. If the incident lacked query-stage timings, add bounded instrumentation for those stages. If the release identifier was hard to find, expose it through an approved administrative path. If logs contained secrets, repair the diagnostic design as well as the code. Better investigation is partly a property of the system you build.

## Exercises and answer guidance

1. Classify “HTTP 503 from the proxy” and “the database is down.” The first is an observation if source and time are recorded; the second is a hypothesis until dependency evidence supports it. List a discriminating read-only observation.
2. A local probe succeeds while remote users time out. Draw both paths and identify missing boundaries. External DNS, routing, firewall, proxy and TLS can differ; do not assume a local probe exercises them.
3. A timed-out create-order request has no visible error log. Can it be safely retried? Not from that evidence alone. Check acceptance state or use an established idempotency contract; missing logs do not prove noncommit.
4. Two changes happened at the same time as recovery. How can a post-incident test help? Reproduce the relevant condition safely and vary one candidate mechanism while holding other inputs fixed. Record test limitations rather than promising production-identical behavior.

## Review questions and takeaways

What would disprove your current hypothesis? Which boundary does each observation cover? Are source clocks comparable? What state changes would your experiment make? Which recovery action is safe under the remaining uncertainty?

Write facts separately from explanations. Compare affected and unaffected paths, choose tests that distinguish mechanisms and preserve exact next steps. Restore useful service under a known contract, then resolve uncertain work and improve evidence. Continue with [Working Safely at the CLI](008-working-safely-at-the-cli.md).

## Sources and verification

The Google SRE troubleshooting chapter and curl manual were inspected on 2026-10-01. The notebook, timeline and incident are fictional. Curl timing fields and timeout options were documentation-reviewed, but no running DispatchDesk API or remote network path was probed. No production changes were made. Independent review is pending.
