# Chapter 75 continuation

Status: complete

## Written material
Discovery/import; complete VPC import HCL; cloud-free data rename with complete before/after moved-block files; drift interpretation and refresh-only; adoption failures; exercises/sources.

## Concepts and terminology
Identity adoption versus configuration correctness, single ownership, address move versus remote replacement, refresh-only versus source adoption.

## Examples and cross-references
Terraform >=1.5 import baseline and >=1.4 data lab; explicit no-destroy rule for adopted production network. Links 072, 073, 074, 082.

## Open threads
Independent review; all CLI/provider/cloud execution unperformed; real provider version selection prerequisite.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Terraform import overview/refactoring/plan and provider VPC import docs inspected 2026-10-01. No fabricated execution evidence.

Local check: tools/check_book.py --chapters 71-80 checked shell/Python syntax, YAML parsing and links 2026-10-01. Initial079 shorthand CloudFormation tag exceeded generic YAML parser; changed to equivalent Ref mapping, then reran. No runtime/provider semantics claim.
