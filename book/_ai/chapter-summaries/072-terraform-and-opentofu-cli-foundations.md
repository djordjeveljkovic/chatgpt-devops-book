# Chapter 72 continuation

Status: complete

## Written material
Providers/resources/variables; complete cloud-free terraform_data HCL; initialize/format/validate/plan/apply workflow; explicit variable-file change; failure diagnosis; reviewed destruction; exercises and sources.

## Concepts and terminology
Root module, resource address, typed input, saved plan, structural validation versus operational verification, dependency upgrades.

## Examples and cross-references
Terraform >=1.4,<2.0 example, separate Terraform/OpenTofu selection policy. Links 071, 073, 121. Linux CLI identical; installation and privilege differences explained.

## Open threads
Independent review and actual executable tests. No providers/cloud provisioned.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Official OpenTofu init/plan and Terraform terraform_data/apply inspected 2026-10-01. command -v found neither executable; no HCL execution or integrations claimed.

Local check: tools/check_book.py --chapters 71-73 passed 2026-10-01 with no errors or warnings; shell syntax/local-link checks only, not runtime semantics.

Local check: tools/check_book.py --chapters 71-80 checked shell/Python syntax, YAML parsing and links 2026-10-01. Initial079 shorthand CloudFormation tag exceeded generic YAML parser; changed to equivalent Ref mapping, then reran. No runtime/provider semantics claim.
