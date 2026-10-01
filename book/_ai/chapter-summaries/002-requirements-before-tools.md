# Chapter 2 continuation

Status: complete

## Written material
Functional versus operational requirements; constraints and measurable acceptance; complete service charter; illustrative event trace; HTTP 202 ambiguity incident; exercises and review.

## Concepts and terminology
Requirement, assumption, proposal; acceptance criteria; measurement boundary; indicator and objective (introductory, canonical treatment chapter 181); provider acceptance versus delivery.

## Examples and cross-references
Fictional one/ten-order-per-second workloads and 64 KiB limit, explicitly unmeasured. Charter assumes durable acceptance and async notification but states backup/retention gaps. Links 001, 003 and 181.

## Open threads
Chapter 010 should adopt or explicitly revise learning workload assumptions. Independent review and later application execution required.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Official SRE objectives chapter and RFC 9110 inspected 2026-10-01. 202 semantics documentation-reviewed; illustrative trace arithmetic manually checked. No application, load or restore execution.

Coordinator check_book.py --chapters 1-3 executed by writer: no errors/warnings; YAML/shell syntax and local links only.
