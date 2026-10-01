# Independent review — Chapter 071

Verdict: approved
Reviewed body SHA256: 0ea2b718cf40b2741387b20345f9fb0fb1726d6a084ab4c9d5f278c7de24d7cd
Reviewer: write_operations (separate writer from chapter author)
Date: 2026-10-01

## Scope and findings
Reviewed desired-state/dependency explanation, toy shell reconciler, whole-file ownership failure, partial-apply recovery and scoped cleanup. The reconciler does not preserve mode/owner or lock, and prose explicitly identifies those limits. No material correctness issue found. Coordinator local sh execution evidence is distinguished from infrastructure execution.

Severity: no unresolved material findings. Checked CLI context/arguments, complete inline lab/configuration, Linux differences, ownership, recovery, readability, cross-reference purpose and evidence scope.

## Primary-source verification
Terraform plan and apply references: partial apply is not transactional; plan previews operations, application correctness requires separate evidence.
Sources inspected independently 2026-10-01: https://developer.hashicorp.com/terraform/cli/commands/plan ; https://developer.hashicorp.com/terraform/cli/commands/apply ; https://developer.hashicorp.com/terraform/cli/commands/init ; https://developer.hashicorp.com/terraform/language/backend/s3 ; https://developer.hashicorp.com/terraform/cli/commands/state/pull ; https://developer.hashicorp.com/terraform/cli/commands/force-unlock ; https://opentofu.org/docs/language/resources/tf-data/ . Only relevant claims from this chapter evaluated against those pages.

## Actual validation and limits
Read the complete manuscript. Ran tools/check_book.py --chapters 71-73: shell syntax 11 and local-link validation, no errors/warnings. This is syntax/link evidence, not Terraform/OpenTofu/HCL semantic execution. No infrastructure CLI, provider, state migration, IAM, cloud or cluster test performed by reviewer. Chapter071's separately reported coordinator local shell-lab test is retained as authoring evidence, not relabeled as reviewer execution.

## Editorial delta recheck — 2026-10-01

Verified exact prior body hash by reconstituting only the removed trailing sentence about pending review. No other prose/example delta. Approval retained and reviewed hash refreshed for the publication cleanup.
