# Independent review — Chapter 151

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 15ec3f5269936ed8beda6a0a474fd4b9b38bc5e04ae4bce91b81da01089626ad

## Scope and findings

Read complete current body/summary, Chapter151 brief and authoring guide plus150 prerequisite summary. Reviewed workload boundaries, stability and Little-law arithmetic, CPU/retry budgets, open/closed generator behavior, percentile populations, charter, Python and failure/recovery. No material technical finding. Numerical examples are correct:10×0.2=2;10×2=20;50×0.02=1 CPU-second/second;10×1.4=14 attempts/second;20/(0.1+1)=18.18 and20/(2+1)=6.67 requests/second. Fictional assumptions and simplified CPU independence are explicit. Little-law usage requires stable matched boundaries rather than claiming growing queues are steady state.

Open versus closed iteration scheduling, offered/started/completed separation and generator capacity/drop limitations match current k6 documentation. Percentile/rare-path caution, success-only bias, warmup purpose and realistic working sets are sound. Charter has protected synthetic boundary, defined idempotency prerequisite, empty threshold/identity fields identified as instructions to fill before execution, telemetry and stop/recovery/targeted cleanup. It explicitly rejects using141 metrics-only endpoint as proof of durable acceptance. Python uses ordinary-user scratch working-directory context and no OS-specific dependency beyond Python3. Source/rendered configuration is planning rather than runnable load test.

Low — charter question/workload mix: clarify that10 offered requests/second with90% new and10% retries means9 new requests/second and1 retry/second, not10 new durable orders/second. Record both rates when interpreting notification demand and canonical peak. Current prose normally says order requests and includes duplicate reconciliation, so this is precision, not a material arithmetic contradiction.

Low — final questions/conclusion: explicit concise takeaway sentences would improve alignment with authoring-guide takeaways requirement; present conclusion already states workload/boundary lessons. Summary omitted the additional open/closed section from written-material enumeration but concepts list captures it; update next authoring pass if useful.

## Primary evidence checked 2026-10-04

- [k6 open/closed models](https://grafana.com/docs/k6/latest/using-k6/scenarios/concepts/open-vs-closed/): iteration completion coupling versus independently scheduled arrivals and closed-model self-throttling.
- [k6 constant arrival rate](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/): fixed scheduled iterations, VU capacity and dropped work bounds. These are current docs, not installed-generator runtime evidence.

## Validation and limits

`python3 tools/check_book.py --chapters 151-151` passed: one YAML parse, one Python syntax check and1,445 global links; no errors/warnings. Hash computed with tools.promote_reviewed.body_hash. Arithmetic inspected directly; no load generator, application/provider, database, durable deduplication, payload distribution, CPU benchmark or drain/cleanup executed. No Python/OS/generator runtime matrix tested. Static charter/Python syntax and sources cannot establish measured throughput, percentile confidence or operational correctness. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed added offered/new-order clarification and explicit takeaway section against prior observations.10 offered requests/s with90/10 mix correctly means9 new submissions and1 retry; separate10-new-orders requirement now calls for an adjusted rate/mix. Takeaways accurately summarize offered/started/completed boundaries, stable matched arithmetic, representative populations, correctness and drain/recovery. Both low body observations resolved; no material issue remains. Fresh body hash computed with tools.promote_reviewed.body_hash:15ec3f5269936ed8beda6a0a474fd4b9b38bc5e04ae4bce91b81da01089626ad. `python3 tools/check_book.py --chapters 151-151` passed one YAML parse, one Python syntax check and1,445 global links; no errors/warnings. Earlier primary-source assessment and runtime limitations retained; no load or provider/database action executed. Only this separate review record updated.

Verdict: approved
