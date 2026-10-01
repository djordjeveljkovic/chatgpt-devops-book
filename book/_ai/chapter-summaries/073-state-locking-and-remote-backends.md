# Chapter 73 continuation

Status: complete

## Written material
State identity/sensitivity; remote backend and concurrency; complete existing-bucket S3 backend declaration; restricted backup and migration; stale lock/write failure recovery; state boundaries; exercises/sources.

## Concepts and terminology
State versus application backup; resource versus remote identity; locking scope; migration versus reconfiguration; recovery inventory reconciliation.

## Examples and cross-references
Terraform-specific S3 use_lockfile with prerequisite approved bucket/versioning/IAM, no provisioning. Migration commands and force-unlock with observed identifier. Links 075, 080, 082, 095, 186.

## Open threads
Independent review; CLI/backend/IAM integration execution unperformed. OpenTofu behavior deliberately not assumed identical.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Official Terraform locking, S3 backend, state pull, force-unlock inspected 2026-10-01. No live tests/cloud operations. Sources note DynamoDB locking deprecation and opt-in lockfile.

Local check: tools/check_book.py --chapters 71-73 passed 2026-10-01 with no errors or warnings; shell syntax/local-link checks only, not runtime semantics.

Local check: tools/check_book.py --chapters 71-80 checked shell/Python syntax, YAML parsing and links 2026-10-01. Initial079 shorthand CloudFormation tag exceeded generic YAML parser; changed to equivalent Ref mapping, then reran. No runtime/provider semantics claim.
