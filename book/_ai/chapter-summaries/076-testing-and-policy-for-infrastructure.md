# Chapter 76 continuation

Status: complete

## Written material
Validation evidence layers; complete cloud-free Terraform native test configuration/tests; complete Python deletion gate; PR evidence/trust/integration cleanup; failures/exercises/sources.

## Concepts and terminology
Invariant tests, policy scope/provenance, unknown values, expected failures, plan-only versus apply tests.

## Examples and cross-references
Terraform >=1.6 native tests; JSON action-list deletion/replacement gate deliberately limited, complete inline code. Links 072, 074, 121.

## Open threads
Independent review; native tests and policy runtime not yet executed; no cloud integrations.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Official Terraform tests/show/JSON-format/validate inspected 2026-10-01. No execution claims.

Local check: tools/check_book.py --chapters 71-80 checked shell/Python syntax, YAML parsing and links 2026-10-01. Initial079 shorthand CloudFormation tag exceeded generic YAML parser; changed to equivalent Ref mapping, then reran. No runtime/provider semantics claim.
