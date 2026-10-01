# Chapter 143 continuation

Status: complete

## Written material
Counters, gauges, rates and histograms; Aggregation and missing series; Investigating latency and error rates. Chapter-specific practical procedure, diagnosis, recovery, exercises and answer guidance exist.

## Concepts and terminology
Counter rate/increase, gauge net change, label matching, absent versus zero, classic histogram aggregation, percentile estimation and population units.

## Examples and cross-references
DispatchDesk fictional examples; inline commands/configuration. Prerequisite chapter 142 is context, not assumed executed setup.

## Open threads
Independent review and resolution of findings are required before complete.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Primary documentation inspected 2026-10-01: Prometheus query functions; histograms and summaries. Author checked balanced code fences and preserved front matter; text and inline examples authored; no cloud provisioning, service execution, or load test performed. Installed-release compatibility remains a reader validation requirement.

Review correction: Gauge paragraph explicitly rejects rate() counter semantics and names delta()/deriv() for net change/trend. Reviewer recheck pending.
