---
book: The Complete DevOps Engineering Book
volume: 1
volume_title: "Engineering Mental Models"
chapter: 6
title: "Environments and Reproducibility"
slug: environments-and-reproducibility
status: complete
summary: ../../_ai/chapter-summaries/006-environments-and-reproducibility.md
---

# Chapter 6 — Environments and Reproducibility

## Development, staging and production

“It worked in staging” is useful evidence only when you can explain what staging exercised and what differed in production. DispatchDesk might use the same application source in both environments while staging has an empty database, a permissive test credential and a mock notification provider. That setup can test basic behavior but cannot demonstrate production migration time, access permissions or provider failure handling.

Read [Architecture as Tradeoffs](005-architecture-as-tradeoffs.md) first. This chapter teaches how to identify the inputs to a deployment and investigate differences without treating every environment as an identical copy. Its practical lab uses Bash and GNU coreutils on Linux, available under the book's Ubuntu 24.04 LTS, Fedora 44 and RHEL 9 baseline. It requires no elevated privileges, containers or remote accounts.

A **development environment** supports rapid changes and diagnosis. It can use test data and convenient debugging, provided those choices cannot accidentally reach production. A **staging environment** exercises selected release risks under controlled conditions. A **production environment** serves the real contract and handles real customer data. These are purposes, not magical application modes. Naming a directory `production` does not configure its access or recovery.

Choose staging similarity by risk. If the release changes SQL query behavior, realistic data shape and database settings matter. If it changes identity integration, representative permissions and issuer configuration matter. If it changes graceful shutdown, the real process supervisor and request routing matter. A tiny staging replica might cover startup but fail to reveal memory demand under the production workload. Document that limitation instead of buying an expensive copy without a test objective.

Production data is not automatically appropriate for staging. Synthetic records can reproduce important shape without exposing customer information. If an authorized process uses transformed production data, the transformation, retention and access rules become part of its design. A test notification must go to a controlled recipient, not to every address copied into the dataset.

Ubuntu and Fedora/RHEL environments can support the same application contract while differing in package builds, security controls and service configuration. Reproducibility does not mean pretending those differences disappear. Record the actual operating-system release and validate relevant behavior in each supported path. Later Linux chapters explain distribution-specific procedures.

## Configuration and artifact identity

An **artifact** is an output intended for deployment: a binary, archive, package or container image. A source revision identifies input code, while an artifact identity identifies the resulting bytes. Those are different facts. Two builds of the same source can differ because of dependency resolution, compiler options, timestamps or build environment. A tag or filename can also be moved to different bytes.

The Reproducible Builds project's [definition](https://reproducible-builds.org/docs/definition/) describes reproducible builds in terms of identical specified artifacts from the same defined inputs and instructions. Applying that standard requires control of the build environment and comparison of results. Merely deploying the same artifact twice is valuable but is not proof that anyone can reproduce its build.

A simple release practice is to build once, record the artifact identity and promote that artifact through environments. Configuration changes between deployments, but the application bytes stay identifiable. A tested release can then be matched to the production release. Later release-engineering chapters develop provenance, promotion and signing; a hash alone does not establish who built something or whether it is trustworthy.

**Configuration** includes values that vary by deployment, such as a database location, listening port or provider endpoint. Keep those values explicit and validate their meaning at startup. A missing `DATABASE_URL` should produce a clear startup failure if the application requires durable storage. Falling back to an in-memory store might make a lab convenient while silently violating production acceptance.

The historical [Twelve-Factor configuration guidance](https://12factor.net/config), whose page records a 2017 update, argues for separating deployment configuration from application code. That is a useful principle. It does not make environment variables secret by themselves: a process, diagnostic dump or operator command may expose them. Use the hosting platform's approved secret mechanism and avoid publishing complete environments during debugging.

Record identities for the other inputs too: database schema version, configuration revision excluding secret values, operating-system release, runtime version and dependency lock state. A release record can include a secret reference identifier or rotation event without the credential. Logs should reveal which configuration category failed, not print a password to prove it was loaded.

## A disposable checksum experiment

This lab creates an artifact containing one line, records its SHA-256 checksum, verifies it, then changes the artifact and observes verification failure. Run as an ordinary user in Bash. The commands work from any initial directory and create an isolated directory under the normal temporary location.

```bash
lab_dir=$(mktemp -d)
cd "$lab_dir" || exit 1
printf '%s\n' 'DispatchDesk learning release 1' > artifact.txt
sha256sum artifact.txt > artifact.sha256
sha256sum --check artifact.sha256
printf '%s\n' 'local edit' >> artifact.txt
sha256sum --check artifact.sha256
```

`mktemp -d` creates a fresh directory and prints its path; `lab_dir` captures that path. Quoting the path ensures the shell passes it as one argument. The guarded `cd` stops if changing directory fails, preventing later writes in an unintended location. `printf` writes controlled text. The first redirection creates the artifact, and the second stores checksum output in a separate manifest. The `>>` operator appends a deliberate edit.

`sha256sum` computes a content checksum. `--check` reads the saved checksum record, recomputes the named file's checksum and compares it. The first check should report `artifact.txt: OK`; the second should report a mismatch and return failure. These are expected outcomes, not a transcript claimed as measured below. A missing file, unreadable file or malformed checksum record can also fail, so read the message rather than equating every nonzero exit with changed content.

After observing the failure, clean up only the explicit lab files and directory:

```bash
rm -- artifact.txt artifact.sha256
cd /tmp || exit 1
rmdir -- "$lab_dir"
```

The deletion is destructive to those two lab files, which is its intended purpose. `--` ends option parsing. `rmdir` removes the directory only if empty, so it will not silently remove additional material. If you changed the lab or are unsure which directory you are in, inspect it before deletion. The script does not restore changed artifact bytes; it discards this disposable experiment. A real release recovery would fetch the recorded artifact from a controlled store.

A checksum helps identify differing bytes. It cannot tell whether the original artifact was malicious, whether the manifest was replaced too, or whether production uses the file you checked. The trust path and deployment location require separate evidence. This is why a release record should include both artifact identity and where that artifact was activated.

## Preventing environment drift

**Drift** is a difference between intended and actual state. It can arise from manual host changes, mutable dependencies, undocumented configuration or a release process that rebuilds differently in each environment. Drift is not always accidental: an emergency repair may intentionally change production. The issue is whether that change is recorded and folded into the repeatable path.

Create a minimal comparison table for a release:

| Input | Staging evidence | Production evidence | Expected difference |
|---|---|---|---|
| Artifact checksum | Release record | Activated release record | None |
| Runtime version | Measured startup metadata | Measured startup metadata | None unless tested |
| Database target | Approved test reference | Approved production reference | Different stores |
| Schema compatibility | Migration rehearsal | Active schema inspection | Compatible state |
| Notification destination | Controlled recipient | Real provider route | Explicit policy |
| Secret reference | Test credential reference | Production credential reference | Different scopes |

This table distinguishes necessary differences from unexplained ones. Copying every staging setting into production would be dangerous if it selects a test store or recipient. Conversely, accepting any difference because “production is different” prevents the table from detecting drift.

Automate inspection when the inputs are stable and observable. Capture runtime versions during build or startup. Make the active release identifier visible through a controlled administrative path. Validate required settings before readiness. Manage host configuration through a reviewed repeatable procedure, then compare actual state to it. Avoid treating a successful configuration run as proof that an application dependency behaved correctly.

## A release that silently used a different dependency

Staging runs a successful release built on Monday. Production deployment rebuilds the same source on Thursday with an unconstrained library dependency. The library's changed default alters connection behavior, and requests begin failing. The source commit is identical, which initially distracts the responders from the artifact difference.

Diagnosis compares actual deployed artifacts, resolved dependency versions and startup behavior. The responders find that production's package set differs from staging's tested set. They preserve the failing release record, restore the previously known compatible artifact under the application's data-compatibility rules, and verify order acceptance and pending notifications. A source checkout alone cannot reconstruct the previously tested bytes unless its build inputs are retained.

The repair builds once for promotion, records dependency resolution and tests required runtime behavior. If source reproducibility is a requirement, the team additionally controls and verifies its build environment. Staging gains a test for the specific connection behavior that failed. The emergency rollback is not the end of the investigation: accepted work and uncertain requests may still need reconciliation.

Another common drift failure is a manual production setting fixed during an incident but absent from the configuration record. The next routine deployment resets it and repeats the incident. The corrective action should update the declared path and its test, not merely note “do not overwrite this host.” Keep the emergency change visible until that reconciliation happens.

## Exercises and answer guidance

1. Two files have different names but the same checksum. What does this suggest, and what does it not prove? It supports identical content under the chosen hash comparison; it does not establish provenance, deployment location or trustworthy build inputs.
2. Staging uses ten records while production uses millions. Which tests remain useful? Startup and basic functional checks may remain useful; query cost, migration duration and memory-demand claims need representative data and workload.
3. A production incident is fixed by changing `LOG_LEVEL`. How should that change be handled? Record the incident reason, compare against intended configuration, incorporate the chosen setting or restore it deliberately, and verify logging behavior without exposing secrets. A manual setting should not become forgotten state.

## Review questions and takeaways

Why can the same source produce different artifacts? Which configuration differences between environments are intentional? What evidence links a tested artifact to an active deployment? Which staging risks are not covered? What makes an emergency change reproducible later?

Give environments explicit purposes. Separate artifact identity from configuration, compare actual inputs and record necessary differences. Promote identifiable artifacts, and make drift reconciliation part of incident follow-up. Continue with [Learning to Investigate](007-learning-to-investigate.md).

## Sources and verification

Inspected on 2026-10-01: Reproducible Builds' definition and Twelve-Factor configuration guidance. GNU checksum documentation could not be fetched during inspection; the installed GNU coreutils 9.11 `sha256sum --help` and version output were inspected for `--check` semantics. The full disposable lab was not executed during drafting. No production deployment, reproducible build or secret integration was tested. Independent review is pending.
