# AI authoring and continuation guide

## Read before working

1. Read this guide and root `PROGRESS.md`.
2. Read the assigned chapter's brief in `SKELETON.md` and its record in `book/_ai/manifest.json`.
3. Read the chapter, its compact summary and existing review record.
4. Read relevant prerequisite summaries and canonical-topic chapters before introducing a dependency or cross-reference.
5. Continue from **Exact next section**. Existing complete material is not a request to rewrite it.

The approved task is to write the complete book, not merely create an outline. Preserve all user preferences across context resets: detailed comprehensive prose, minimal repetition, novice-to-senior progression, senior-reference value, inline examples, equal Ubuntu and Fedora/RHEL treatment, GitHub Actions/GitLab CI/Jenkins in depth, Grafana and related observability tools, different languages, a growing project, contrasting fictional company paths, and real sourced company examples.

## How to teach

Explain requirements → constraints → alternatives → decision → commands/configuration → mechanism → observable evidence → failure → diagnosis → recovery → scaling implications. Use concrete examples before abstractions. Explain why a choice fits the stated workload, budget, team and reliability target. Do not turn deployment size into an automatic argument for microservices or Kubernetes.

Use original prose and subject-specific examples. A chapter needs actual explanations, configuration, a practical procedure, operational failure analysis and decision reasoning. Template-generated paragraphs, bare definitions, lists of links, and placeholders are not chapters. Usually write 1,500–3,000 words per substantial chapter; expand technical subjects as needed. Reference chapters may be shorter. Do not pad with repeated introductions or generic safety prose.

For commands explain execution host, user/privilege, working directory, variables and prerequisites; each relevant flag and argument; expected evidence; state changes; likely failures; verification; and cleanup or rollback. Explain commands in connected prose or focused tables. Identify destructive and billable operations beside the example. Never execute cloud provisioning while authoring.

Show complete inline configuration or application files when necessary. Do not use undefined variables, unexplained hidden setup, shell prompts embedded in copyable blocks, or fabricated command output presented as measured results. Mark representative output as illustrative. Use fenced languages accurately: bash/sh for shell scripts, console for output, yaml/json/hcl for configuration, and text for pseudocode.

Prefer relative links to the canonical explanation. A short reminder is fine; rewriting namespace, SLO, retry, networking or scaling fundamentals in every tool chapter is not. The manifest gives stable chapter paths. Each chapter should provide prerequisite/context links, exercises with answer guidance, review questions, takeaways and supporting primary sources.

## Linux and version policy

Keep changing authoring status in front matter, summaries and progress, not in the published narrative. Verification sections explain actual evidence and limitations; avoid a trailing "independent review pending" sentence that will become stale when a chapter is approved. If it already exists, coordinate its removal and a refreshed independent review hash before final delivery.

Where packages, units, paths, networking or security differ, give separate Ubuntu and Fedora/RHEL commands and state the actual target. Fedora is not interchangeable with RHEL. Mark repositories, entitlement requirements and version availability where relevant; use supported RHEL-compatible distributions when readers lack subscriptions. SELinux and AppArmor examples must preserve their actual security models.

Before asserting current or exact tool behavior, browse official primary documentation. Record the verification date and the version or API assumptions. Do not claim a release is current based on memory. Use the baseline ledger for common assumptions, and add per-chapter differences. Container tags are examples, not immutable release identities; production examples should explain digest pinning and how to obtain a real digest rather than invent one.

Do not invent provider prices, quotas, free-tier promises, service guarantees, API versions or company technology stacks. Label historical practices and fictional cases explicitly. Cite the company publication's date and described system; do not generalize a corporate-network example to a company's entire production stack.

## Agent work and ownership

The user requested subagents with model `gpt-6.1-sol` and reasoning `low`. Spawn them with an explicit bounded task and `fork_turns="none"` or another supported limited-context value, so the requested overrides apply. The coordinator plus three workers is the concurrency limit.

Assignments are recorded under `book/_ai/assignments/`. Writers exclusively own their assigned chapter files and summaries. Reviewers initially own only separate review records. Only the coordinator changes shared skeletons, global indexes, progress and version/topic ledgers. Do not run the bootstrap utility during writing: it rebuilds shared files.

Write a chapter's bespoke section outline before its prose and update the chapter summary after each substantial section. Set chapter status to `drafting` while working and `draft` when its intended content exists. Save at natural section boundaries. When a context reset is needed, leave exact next steps, not a vague instruction to continue.

Independent review must cover correctness, CLI arguments, examples, Linux differences, missing prerequisites, version-sensitive claims, recovery reasoning, readability, repetition and links. Write findings with severity and an exact location. Authors resolve findings in their own chapters. The coordinator may repair cross-chapter consistency after ownership is released.

An approved review records `Reviewed body SHA256: <hash>` computed over the chapter after stripping its opening YAML front matter. This ties approval to the prose and examples rather than merely a filename. After an author changes approved prose, review the changes and update the hash. Import `body_hash` from `tools/promote_reviewed.py` or calculate the same SHA-256 operation. The coordinator uses `tools/promote_reviewed.py` only after validation; it does not treat unreviewed drafts as complete.

States: `planned → drafting → draft → reviewing → revising → complete`. A `complete` chapter requires an independent review record with `Verdict: approved`, resolved material findings, a factual summary and validation evidence. Lack of a live cloud or cluster test must remain visible; documentation review is not execution evidence.

## Required chapter summary

Keep summaries compact, factual and cheap to load. Include status; written sections; canonical concepts and terminology introduced; examples and assumptions; cross-references; open threads; exact next section; technical sources and dates; actual checks performed; checks not performed. Record partial sections precisely. Do not infer completion from the outline or a desired word count.

## Resume protocol

1. Inspect files and agent records before assuming a worker is still active.
2. Read `PROGRESS.md`; find the earliest unfinished dependency or an explicitly assigned independent batch.
3. Read only that chapter's summary, review and relevant prerequisites.
4. Reconcile the saved state with the actual chapter. Preserve existing prose and numbering.
5. Continue writing or resolving review findings; save summary and progress after each bounded batch.
6. Proceed until the complete manuscript and reviews exist. A completed skeleton or isolated sample is not final delivery.

The coordinator can run `tools/refresh_progress.py` after worker updates. This regenerates the status table from actual front matter and review files; it does not promote chapters automatically. Keep the coordinator handoff concise. Store detailed evidence with each chapter instead of appending the whole book history to one continuation file.
