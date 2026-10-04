# Independent review — Chapter 160

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: 168552615ddd80563a3e21a2b0c887dc7bc2c44824a148b89160de2be239acc1

## Scope and findings

Read complete current manuscript, compact summary, Chapter 160 brief and authoring-guide requirements with Chapters 158/159 forecasting and efficiency context. Reviewed Python/CSV arithmetic, successful-order denominator, recurring/migration/labor assumptions, ownership allocation, AWS interruption/commitment boundaries, staged recovery, exercises/takeaways and links. No material technical issue found. Summary accurately records the conceptual scope and lack of provider/runtime evidence.

The Python comparison is internally consistent. Infrastructure sums are 140, 270 and 230 units; twelve-month migration allocations are 10, 20 and approximately 33.33. At labor valuations 5/20/50, monthly totals are respectively VPS 210/390/750, ECS 320/410/590 and shared Kubernetes approximately 303.33/423.33/663.33. VPS wins the first two cases and ECS the third. Dividing by 100,000 successful orders produces the stated unit-cost metric. Values are explicitly fictional cost units, not quoted prices. Lower volume changes average unit cost; migration horizon and staff valuation are identified as sensitivity assumptions rather than guarantees.

Service boundaries include durable acceptance, notification timing, security and recovery. Retries consume resources without inflating successful logical-order counts. Fixed/variable, incremental/allocated and cash/time costs are distinguished. Overlapping support/labor is not double-counted by default. The exclusions and technical disqualification of an untested recovery proposal prevent the arithmetic from purporting to prove full TCO or reliability. No unsourced current pricing or universal platform ranking is asserted.

EC2 Spot warnings are correctly treated as best effort with different hibernation timing; abrupt-loss recovery remains required. Fargate Spot scarcity is correctly not treated as an automatic ordinary-Fargate fallback. Placement weights do not prove dependable reserve. Durable ownership and ambiguous provider side effects are tested at multiple boundaries, with retry/reserve/engineering costs included. Restartability alone is not interruption tolerance. Savings Plans are accurately described as hourly spending commitments over terms with eligible-usage variation, separate from capacity assurance. Exact contract eligibility and prices are deferred to current account review rather than invented.

Failure/recovery discussion preserves authoritative durable state and provider-effect reconciliation and recognizes operational duties that remain with managed services. Exercises provide useful answer guidance; concluding takeaways state the decision boundary and validation limits. Linux arithmetic lab uses ordinary-user standard-library Python with no hidden provider credentials or operations.

Low observations:

- Opening: add the concise bespoke section outline required by the authoring guide. Actual sections and substantive content are complete.
- Fictional proposal introduction: explicitly label infrastructure units and ops_hours as monthly, matching the program's monthly totals. The surrounding monthly denominator and migration amortization imply this, but the CSV otherwise leaves recurring-period interpretation to the reader.

## Primary evidence checked 2026-10-04

- [EC2 Spot interruption notices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html): best-effort notice and immediate hibernation versus stop/terminate warning.
- [Fargate capacity providers](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-capacity-providers.html): Spot interruption/scarcity and absence of automatic on-demand substitution.
- [Savings Plans overview](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html): spending commitment, terms and eligibility variation.

No pricing lookup or exact account-contract conclusion is needed or claimed for fictional cost units.

## Validation and limits

`python3 tools/check_book.py --chapters 160-160` passed one Python syntax check and 1,449 global local links without errors/warnings. Exact stripped-front-matter body hash computed using `tools.promote_reviewed.body_hash`. CSV/program/outputs inspected arithmetically, not executed as a measured runtime result. No billing query, purchase, Spot interruption test, provider provisioning, recovery experiment or performance test executed. No OS/account/provider runtime matrix tested. Static parsing and documentation cannot establish actual ownership hours, discounts, resource availability or interruption correctness. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed the new section outline and explicit recurring-cost period labels. Both prior low observations are resolved. The outline accurately represents the complete chapter. Four recurring infrastructure units columns and ops_hours are now expressly monthly, while migration_units remains one-time and is amortized across the program's migration_months. Labels therefore match the unchanged monthly totals and successful-orders-per-month denominator. No material issue introduced; previous approval stands.

Fresh body hash computed with `tools.promote_reviewed.body_hash`: 168552615ddd80563a3e21a2b0c887dc7bc2c44824a148b89160de2be239acc1. `python3 tools/check_book.py --chapters 160-160` again passed one Python syntax check and 1,449 local links without warnings/errors. Earlier technical assessment, primary-source evidence and provider/billing/runtime limitations remain applicable. Compact summary remains factually consistent. Only this separate review record updated.

Verdict: approved
