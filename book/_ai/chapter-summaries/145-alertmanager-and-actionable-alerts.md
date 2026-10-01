# Chapter 145 continuation

Status: complete

## Written material
Grouping, routing and inhibition; Ownership and alert fatigue; Paging on service impact. Chapter-specific practical procedure, diagnosis, recovery, exercises and answer guidance exist.

## Concepts and terminology
Detection versus notification, alert identity, grouping delays, ownership, inhibition/silences, budget-consumption arithmetic and receiver delivery boundaries.

## Examples and cross-references
DispatchDesk fictional examples; inline commands/configuration. Prerequisite chapter 144 is context, not assumed executed setup.

## Open threads
Independent review and resolution of findings are required before complete.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Primary documentation inspected 2026-10-01: Alertmanager configuration; Prometheus alerting rules. Author checked balanced code fences and preserved front matter; text and inline examples authored; no cloud provisioning, service execution, or load test performed. Installed-release compatibility remains a reader validation requirement.

## Review corrections
Budget arithmetic now explicitly introduces a distinct request-based rolling30-day objective and forbids mixing it with Harbor time-based availability. Independent reviewer recheck pending.
