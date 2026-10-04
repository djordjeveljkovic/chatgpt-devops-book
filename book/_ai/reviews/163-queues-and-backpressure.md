# Independent review — Chapter 163

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: ecf619d254646f3171b9c52239aeacdad66d01c061767470c3ba0da21f5aa761

## Scope and findings

Read full current body/summary, Chapter 163 brief and authoring-guide requirements with Chapter 162 prerequisite context. Reviewed backlog/flow arithmetic, queue acceptance and backpressure boundaries, logical-clock SQLite lease code, ownership checks and attempt-cap limitation, SQS visibility/acknowledgment/dead letters, recovery and assessment. No material technical finding. Summary accurately distinguishes local logical-clock evidence from untested broker/provider recovery.

Arithmetic is correct: (50−35) × 60 = 900 jobs/minute; 9,000/(70−50) = 450 seconds drain; 20+12,000/600 = 40 completions/s for the ten-minute target. Stable assumptions, retries, cancellations/quarantine and physical completion limits are explicit. Depth, age and approximate broker metrics are not conflated. Accepted work must remain durably owned; unavailable broker versus unavailable transactional intent storage are properly distinguished.

SQLite BEGIN IMMEDIATE serializes selection and claiming. The new owner token is per attempt, the lease expires at equality, and finish requires matching current token, leased state and lease_until > now. The expired owner cannot mutate completion state; this does not fence an already sent external effect. Per-call connections close explicitly. Failed handled attempts become pending with two-unit eligibility until the third becomes dead. Repeated crashes before finish can bypass that handled-failure cap and be reclaimed indefinitely; the chapter explicitly discloses this rather than calling the helper a production scheduler. Logical time, selection order, missing fairness/schema/renewal and storage durability limitations are clear.

Independently executed the exact current lease lab extracted from the manuscript in a temporary local directory under Python 3.14.7. Exit 0; all assertions passed and the expired-owner/new-owner/poison-quarantine message appeared. Synthetic files were removed automatically. This supports the bounded recorded execution claim without establishing real-time renewal, crash-reclamation or external-effect behavior.

SQS receive/visibility is correctly separate from deletion and business completion. Visibility is not promised as an exactly-once lock. Acknowledging before durable outcome can lose the recovery path; acknowledging after persistence permits duplicate suppression, while provider effect before persistence remains ambiguous. Dead letters preserve unresolved work with ownership/replay obligations rather than proving success. Ordering and retention distinctions are scoped to documented broker behavior. Recovery bounds provider demand and replay, preserves identities/fairness, and reconciles accepted intent across completed/pending/terminal states; empty depth alone does not prove recovery. Exercises include answer guidance and substantive takeaways.

Low observations:

- Opening: add the concise bespoke section outline required by the authoring guide. Actual sections and content are complete.
- Numerical prose/verification: normalize spacing around backlog variables, values/units, dates and Python version (for example backlogB, on2026-10-01 and Python3.14.7) for readability; arithmetic is unaffected.

## Primary evidence checked 2026-10-04

- [SQLite transactions](https://www.sqlite.org/lang_transaction.html): immediate transaction authority, serialized writers and commit semantics.
- [SQS visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html): receipt, expiry, renewal and duplicate-delivery caveats.
- [SQS dead letters](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html): redrive policy, standard/FIFO retention and oldest-age distinctions, ordering warning.

## Validation and limits

`python3 tools/check_book.py --chapters 163-163` passed one Python syntax check and 1,449 global local links without errors/warnings. Exact stripped-front-matter body hash computed using `tools.promote_reviewed.body_hash`. Logical-clock lab executed once as above; arithmetic and recovery inspected directly. No real-time lease/renewal, repeated crash handling, distributed claim stress, power-loss/storage recovery, SQS/broker/provider operation or production backlog/load experiment executed. No OS/database/runtime matrix tested. Local assertions and docs cannot establish external duplicate suppression or durable production outcome. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed added outline and normalized rate, backlog-formula, date/version and exit-status prose spacing. Both prior optional observations are resolved. Outline accurately captures arrival/completion, capacity backpressure, ownership/acknowledgment and bounded recovery. `λ + B/T` and the 12,000/600 + 20 = 40 completion-rate example retain correct semantics and arithmetic. Code and prior execution claims are unchanged. No material issue introduced; approval remains.

Fresh stripped-front-matter body hash computed with `tools.promote_reviewed.body_hash`: ecf619d254646f3171b9c52239aeacdad66d01c061767470c3ba0da21f5aa761. `python3 tools/check_book.py --chapters 163-163` again passed one Python syntax check and 1,449 local links without warnings/errors. Earlier full assessment, primary evidence and independently executed lease-lab evidence retained; prose-only changes did not warrant another runtime run. All real-time/broker/provider/recovery limits remain applicable. Only this separate review record updated.

Verdict: approved
