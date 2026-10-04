# Independent review — Chapter 154

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 20470742a47caf7925fb61bd7cd17156da0f9be7a3b0fc2e97974789c0892287

## Scope and findings

Read full current body, compact summary, Chapter 154 brief and authoring-guide requirements, with Chapters 151/153 prerequisite context. Reviewed complete loopback target, k6 JavaScript, Locust Python/CLI, tool installation assumptions, open/closed workload semantics, staged correctness and isolation, generator diagnosis, stop/recovery and local links. No material technical issue found. The summary's core concepts are accurate; its section enumeration reflects the brief rather than every actual additional tool section.

The Python lab server binds only loopback, serves a GET-only teaching contract and is explicitly unsuitable as production capacity evidence. Scratch-directory, ordinary-user, occupied-port and termination instructions are adequate. k6 archive architecture/checksum/release checks provide an equally applicable Ubuntu/Fedora/RHEL route; Python venv avoids changing the OS interpreter, and pip freeze is correctly distinguished from a production hash-pinned policy.

The k6 constant-arrival-rate options are valid: five scheduled iterations per second for thirty seconds, one HTTP request per iteration, bounded VU allocation and request timeout. Checks inspect both status and expected JSON; aggregate thresholds govern pass/fail. Dropped work is not silently counted as target capacity. Naming avoids label cardinality growth. The Locust HttpUser task, between wait, catch_response body failure and headless flags match current documentation. Five users at one-per-second spawning are correctly distinguished from a fixed five-request-per-second stream. Duration includes ramp-up in Locust; run completion and request interruption require actual evidence rather than multiplication.

The staged experiment explicitly requires an isolated tenant, authenticated contract, unique logical keys/reused retry keys, durable order/notification reconciliation, provider boundary, headroom and cleanup. Generator saturation is distinguished from insufficient execution slots caused by target latency. Closed-user self-throttling is correctly explained. Stop/recovery preserves synthetic durable work rather than assuming process exit deletes it. No throughput or correctness result is presented as measured.

Low observations:

- Failure evidence/stop instruction and k6 threshold paragraph: explicitly remind readers that the shown thresholds are end-of-test gates, not immediate abort controls; staging needs an operator/controller or reviewed abort logic. The GET-only lab is safe and the narrative does not claim automatic immediate abort, so this is useful precision rather than a material safety defect.
- Locust headless command discussion: mention that run-time includes spawning and default shutdown can interrupt tasks; a reviewed stop-timeout permits bounded finishing when adapting to stateful staging. Existing reconciliation/idempotency requirements address ambiguous outcomes.
- End of chapter before sources: add a concise explicit Takeaways section for easier authoring-guide inspection. The examples, exercises and recovery discussion already supply the substantive lessons.

## Primary evidence checked 2026-10-04

- [k6 installation](https://grafana.com/docs/k6/latest/set-up/install-k6/): supported binary routes.
- [k6 constant arrival rate](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/constant-arrival-rate/): independent scheduling, preallocated/max VUs, duration excluding graceful stop.
- [k6 thresholds](https://grafana.com/docs/k6/latest/using-k6/thresholds/): checks versus exit status and separate abortOnFail behavior. Current docs displayed v2.3.x.
- [Locust writing a locustfile](https://docs.locust.io/en/stable/writing-a-locustfile.html): HttpUser, waits, semantic response failure and stable request names.
- [Locust headless execution](https://docs.locust.io/en/stable/running-without-web-ui.html): user/spawn flags, run-time including spawning, default interruption, stop-timeout and exit behavior.
- [Locust configuration](https://docs.locust.io/en/stable/configuration.html): host/file/CSV CLI options. Current stable pages displayed 2.46.6.

## Validation and limits

`python3 tools/check_book.py --chapters 154-154` passed two Python syntax checks, one JavaScript syntax check, two shell syntax checks and 1,445 global local links with no errors/warnings. Exact body hash computed using `tools.promote_reviewed.body_hash`. No tool installation, local responder, k6/Locust run, staging order, provider integration, cleanup or load experiment executed. No OS/tool-release runtime matrix tested. Static syntax and documentation cannot establish integrated tool results, offered/completed rates, generator headroom or durable business correctness. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed the current threshold paragraph, Locust command discussion, new review questions/takeaways, source-date update and compact summary. All three earlier low observations are resolved. k6's default final threshold result versus explicit `abortOnFail` and optional `delayAbortEval` matches the previously inspected official documentation; independent time/operator controls remain required. Locust duration is correctly measured from test start, default task interruption is explicit, and `--stop-timeout 5s` is a valid bounded finishing allowance rather than a guarantee of business completion. Review questions and takeaways accurately distinguish models, semantic correctness, generator distortion, early abort and reconciliation. Summary now enumerates actual tool sections and the new concepts accurately. No material issue remains.

Fresh body hash computed with `tools.promote_reviewed.body_hash`: 20470742a47caf7925fb61bd7cd17156da0f9be7a3b0fc2e97974789c0892287. `python3 tools/check_book.py --chapters 154-154` again passed two Python syntax checks, one JavaScript syntax check, two shell syntax checks and 1,445 local links without warnings/errors. Earlier primary-source assessment and installation/runtime/load-test limitations remain applicable. Only this separate review record updated.

Verdict: approved
