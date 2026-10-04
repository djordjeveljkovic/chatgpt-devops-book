# Independent review — Chapter 158

Reviewer: review_volume3_021_025
Date: 2026-10-04
Reviewed body SHA256: cfbcd9d2efc5c877ba6d36b7c5fcc56632098715ea3f8743c160508c76c4c23b

## Scope and findings

Read full current manuscript, compact summary, Chapter 158 brief and authoring-guide requirements with Chapter 157 prerequisite context. Reviewed scenario forecasting and uncertainty, CSV/Python arithmetic, storage units, placement/failure/rollout reserve, AWS identity/quota commands and limitations, operational lead times, failure/recovery and links. No material technical finding. Summary accurately describes the chapter and its unperformed provider/load validation.

Forecast arithmetic is correct: low demand 20/s needs ceil(20/8)+1 = 4 installed ready replicas and 100 rollout connections; expected demand 31.5/s needs 5 and 112; high demand 49.5/s needs ceil(49.5/8)+2 = 9 and 160. All supplied scenarios fit the stated 180 budget; the text's conditional high-case warning is appropriately hypothetical. Reserve is counted as installed/ready capacity and the rollout connection bound includes one extra process. Exact placement, rollout policy and terminating-process overlap must supply actual lost/surge counts; the narrative does not claim this simple model covers every zone failure.

Seventy attempts/s at twenty usable attempts/s/replica needs four serving replicas plus one failure reserve. Storage calculation is also correct: 86,400 × 2 KiB = 168.75 MiB/day, and ninety days approximately 14.83 GiB. Storage explicitly counts accepted durable orders, unlike retry-amplified compute attempts. Index contribution is already included, while WAL/backups/temporary space are excluded and must be budgeted separately. Scenario bounds are not falsely labeled statistical confidence intervals. Net growth, operational boundaries and lead-time triggers are correctly separated from raw time-to-full.

The AWS CLI v2 examples correctly specify profile, region, pagination/pager behavior and Quotas projection. STS identity inspection is read-only and must be completed before the separate quota block. `list-service-quotas` does not supply every applied quota; an absent item is correctly not treated as an unlimited resource. ECS service selection does not inventory EC2/VPC/provider limits, which the wider inventory discussion separately requires. An approved quota is not a capacity guarantee. No quota increase, pricing claim or provisioning command is taught. Recovery respects provider throughput and controls retries while correcting shared-resource forecasts.

Low observations:

- Forecast worksheet introductory paragraph: clarify that observed_peak_rps is the original logical-submission peak before retry amplification, or explain normalizing an already retry-inclusive measurement. “Observed peak” and “original attempts” can otherwise invite double-counting retries when readers substitute real data.
- AWS discovery prerequisite paragraph: explicitly name AWS CLI v2 and link the canonical profile/CLI setup chapter because --no-cli-pager is a v2 option; existing observer setup requirement is clear but not linked.
- Opening: add the concise bespoke section outline requested by the authoring guide. Actual sections, exercises/guidance and takeaways are complete.

## Primary evidence checked 2026-10-04

- [AWS CLI list-service-quotas](https://docs.aws.amazon.com/cli/latest/reference/service-quotas/list-service-quotas.html): response boundary, Quotas fields, pagination, query/output/profile/region flags and account-level default.
- [AWS CLI get-caller-identity](https://docs.aws.amazon.com/cli/latest/reference/sts/get-caller-identity.html): Account/Arn identity output and read-only operation.
- [AWS Service Quotas overview](https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html): quota management and increase-request limitations.

These are current CLI v2/service documents, not evidence of the observer account's actual values or available provider capacity.

## Validation and limits

`python3 tools/check_book.py --chapters 158-158` passed one Python syntax check, two shell syntax checks and 1,447 global local links with no errors/warnings. Exact body hash computed using `tools.promote_reviewed.body_hash`. CSV/code/units and arithmetic inspected directly. No Python runtime result presented as measured; no AWS identity/quota query, quota request, provider provisioning, volume operation, production forecast validation or load test executed. No account/provider/OS runtime matrix tested. Static syntax and documentation cannot establish real demand, growth, physical reserve, actual quota values or recovery lead time. Only this separate review record written.

## Bounded correction refresh — 2026-10-04

Reviewed added outline, renamed/explained forecast baseline in prose/CSV/Python, revised amplification exercise and AWS CLI v2 setup/reference links. All earlier optional manuscript observations are resolved. `observed_original_rps` consistently represents pre-retry new logical submissions, with growth then retry amplification yielding total attempt demand. The unchanged arithmetic remains correct. Exercise correctly distinguishes twenty logical submissions/s from thirty attempts/s and a 1.5 attempt amplification, while storage uses unique accepted records. Chapter 82/215 relative links resolve to CLI setup/reference context. Outline accurately represents the actual chapter. No material issue introduced.

Fresh body hash computed with `tools.promote_reviewed.body_hash`: cfbcd9d2efc5c877ba6d36b7c5fcc56632098715ea3f8743c160508c76c4c23b. `python3 tools/check_book.py --chapters 158-158` again passed one Python syntax check, two shell syntax checks and 1,449 local links without warnings/errors. Earlier primary-source assessment and provider/runtime/load limitations remain applicable.

Low observation — summary Open threads still asks for these now-completed refinements. Remove completed tasks during summary maintenance. Only this separate review record updated.

Verdict: approved
