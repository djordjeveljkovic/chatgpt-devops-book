# Chapter 79 continuation

Status: complete

## Written material
First-boot/image boundaries; complete nonsecret cloud-config marker; complete CloudFormation VPC template; explicit create/review/execute/verify/delete sequence; drift limits; boot/stack failures; exercises/sources.

## Concepts and terminology
Guest versus API readiness, image preparation, logical/physical identities, change-set review limits, drift coverage.

## Examples and cross-references
Authorized reader-only AWS CLIv2 lab with profile/region variables, costs/teardown; Ubuntu24.04/Fedora44/RHEL9 image packaging differences. Links075.

## Open threads
Independent review; cloud-init image/schema and AWS stack integrations unrun.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Official cloud-init boot/debug/CLI and AWS change-set/drift/VPC docs inspected2026-10-01. No cloud resources created.

Local check: tools/check_book.py --chapters 71-80 checked shell/Python syntax, YAML parsing and links 2026-10-01. Initial079 shorthand CloudFormation tag exceeded generic YAML parser; changed to equivalent Ref mapping, then reran. No runtime/provider semantics claim.
