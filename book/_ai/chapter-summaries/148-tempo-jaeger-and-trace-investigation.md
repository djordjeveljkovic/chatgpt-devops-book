# Chapter 148 continuation

Status: complete

## Written material
Spans, parent relationships and timing; Sampling limits and backend choices; Finding a slow downstream dependency. Chapter-specific practical procedure, diagnosis, recovery, exercises and answer guidance exist.

## Concepts and terminology
Span causality and overlap, transient Jaeger2.21 lab, OTLP HTTP forwarding, Tempo ingestion/query roles, search bias and connection-pool diagnosis.

## Examples and cross-references
DispatchDesk fictional examples; inline commands/configuration. Prerequisite chapter 147 is context, not assumed executed setup.

## Open threads
Independent review and resolution of findings are required before complete.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Primary documentation inspected 2026-10-01: Jaeger2.21 getting started and architecture; Tempo deployment validation and TraceQL. Text and inline examples authored; no cloud provisioning, service execution, or load test performed. Installed-release compatibility remains a reader validation requirement.

## Review corrections
Collector exporter uses current otlp_http name; deprecated otlphttp alias and older-distribution compatibility are explicit. Core exporter README inspected2026-10-01. Independent reviewer recheck pending.
