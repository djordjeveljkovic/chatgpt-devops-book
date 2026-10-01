# Independent review — Chapter 148

Reviewer: write_foundations (different author from write_operations)
Date: 2026-10-01
Verdict: approved
Reviewed body SHA256: 536a52dd5093035dad58e0ba175f9bcc1fb287a7fa01cb857456d9c595eadf10

## Scope and findings
Medium — transient Jaeger lab Collector YAML: current upstream exporter name is otlp_http; otlphttp is a deprecated compatibility alias scheduled for removal. Use otlp_http/jaeger_lab consistently or freeze an explicitly verified older Collector baseline and explain compatibility. Add exact exporter README source for base endpoint /v1/traces appending. Jaeger2.21.0 image/all-in-one transient storage and ports match official getting-started.

## Verification evidence
Official Jaeger2.21 getting-started inspected 2026-10-01; core otlphttpexporter README inspected: deprecated alias and signal-path behavior. No container or forwarding execution.

Book validator --chapters141-150 passed Python/shell syntax, YAML/JSON parsing and local-link checks without errors or warnings. These are parsing checks, not component-schema or live integration proof.

## Limits
No infrastructure, paid service, production data or tool integration executed by reviewer. Approval where given is for the documented draft and explicit execution limits, not proof of deployment success.

## Revision recheck
Current otlp_http component used consistently, deprecated older alias documented and exact README cited. Previous medium finding resolved by author; revised text compared with the same inspected official documentation. Re-run validator141–150 passed without errors/warnings. Integration limits unchanged.
