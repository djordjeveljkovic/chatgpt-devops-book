# Independent review — Chapter 143

Reviewer: write_foundations (different author from write_operations)
Date: 2026-10-01
Verdict: approved
Reviewed body SHA256: 4439c18068ffe3997dd2ea08746434cb3ad7b1f1239ad4f3576712f0209d91ab

## Scope and findings
Medium — Counters, gauges, rates and histograms, paragraph beginning “A counter records”: “Taking a rate of a backlog gauge ... gives the rate at which backlog changes” incorrectly implies PromQL rate is appropriate. rate assumes counters and treats decreases as resets. State that rate is invalid for backlog gauges; use deriv for fitted net-change slope or delta for net change, with their limits. Other checked formulas, rate-before-sum, classic le aggregation, no-traffic and missing-series caveats are sound.

## Verification evidence
Official PromQL functions inspected 2026-10-01: rate counter semantics, deriv/delta gauge semantics, absent and histogram_quantile. Mean-latency arithmetic manually checked; no PromQL server evaluation.

Book validator --chapters141-150 passed Python/shell syntax, YAML/JSON parsing and local-link checks without errors or warnings. These are parsing checks, not component-schema or live integration proof.

## Limits
No infrastructure, paid service, production data or tool integration executed by reviewer. Approval where given is for the documented draft and explicit execution limits, not proof of deployment success.

## Revision recheck
Gauge paragraph now explicitly rejects rate() and distinguishes delta/deriv from throughput. Previous medium finding resolved by author; revised text compared with the same inspected official documentation. Re-run validator141–150 passed without errors/warnings. Integration limits unchanged.
