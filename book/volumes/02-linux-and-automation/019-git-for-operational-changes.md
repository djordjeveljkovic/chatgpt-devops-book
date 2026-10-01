---
book: The Complete DevOps Engineering Book
volume: 2
volume_title: "Linux and Automation"
chapter: 19
title: "Git for Operational Changes"
slug: git-for-operational-changes
status: complete
summary: ../../_ai/chapter-summaries/019-git-for-operational-changes.md
---

# Chapter 19 — Git for Operational Changes

## Why this matters

Harbor changes a service timeout during an incident. The new value helps, but the explanation exists only in a chat message and the host differs from its documented deployment. A month later a replacement host restores the old setting and recreates the failure. Git can preserve the intended configuration, the reason for changing it, and a reviewable history. It cannot automatically prove that the live host matches that history.

Operational changes deserve the same clarity as application changes. A script, unit, firewall declaration, or infrastructure plan can affect many systems from a few lines. Review should connect those lines to their effect and recovery path. This chapter develops a local Git workflow without requiring a hosted account or publishing anything.

## Three places hold different versions

The working tree contains files you edit. The index, often called the staging area, contains the content selected for the next commit. A commit records a snapshot and its relationship to history. Editing a file after staging it produces a difference between the working tree and the index; the next commit will not automatically include that later edit.

`git diff` normally compares working-tree content with the index. `git diff --cached` compares staged content with the current commit. `git diff HEAD` shows tracked changes relative to that commit across those boundaries. Untracked files need separate attention through `git status`: a diff of tracked content can look clean while an important new file has never been added. [Git diff documentation](https://git-scm.com/docs/git-diff).

The staged boundary is useful for constructing a coherent change. It is also a source of mistakes when someone reviews one version and commits another. Inspect both status and staged diff immediately before committing, and validate the content that will actually be committed. Avoid staging an entire workspace by habit when it may contain secrets, unrelated experiments, or another person's work.

Git records file content and some file metadata, including the executable bit, but not every operational attribute. Owner/group assignments, many permissions, ACLs, runtime state, and secrets-delivery policy need an explicit configuration workflow. A checked-in unit does not establish that it has been installed, reloaded, or restarted on the host.

## Make a local operational change

Run this only in a new disposable directory. It creates its own repository and sets a fictional identity locally, leaving global Git configuration untouched. The repository contains a sample service policy, not an installed unit:

```bash
mkdir dispatchdesk-git-lab
cd dispatchdesk-git-lab
git init -b main
git config user.name 'DispatchDesk Lab'
git config user.email 'lab@example.invalid'
printf 'drain_seconds=30\n' > service-policy.conf
git add -- service-policy.conf
git commit -m 'Record initial drain policy'
git switch -c extend-drain
printf 'drain_seconds=45\n' > service-policy.conf
git diff -- service-policy.conf
git add -- service-policy.conf
git diff --cached -- service-policy.conf
git diff --cached --check
git commit -m 'Allow bounded notification drain to finish'
git status --short
git log --oneline -2
```

The change remains on a local branch. `git diff --cached --check` catches certain whitespace problems; it does not validate configuration semantics or prove a 45-second drain is appropriate. A useful commit explanation would identify the dependency timeout, observed work duration, and recovery behavior that justify the number. Later delivery checks should exercise the application's real stop protocol.

Branches are names pointing into commit history. They are inexpensive ways to keep a proposed change separate from another line of work. Switching branches changes the working context; it does not create a second independent running environment. For simultaneous edits in one checkout, communicate ownership or use separate worktrees where appropriate. Do not interpret a branch name as proof that its commit is deployed.

The example uses `git switch`, available in modern Git packages on the book's baselines. Check the installed Git version when working on older machines rather than assuming every new option from current upstream documentation exists there. [Git switch reference](https://git-scm.com/docs/git-switch).

## Review the effect, not merely the patch

A reviewer should understand the trigger, new behavior, and validation. For the drain change, useful questions are whether request/provider timeouts fit within the deadline, whether process shutdown still finishes before the supervisor forces termination, and whether uncertain notification outcomes are reconciled safely. The diff shows a number; the engineering review explains its relationship to the service.

Separate unrelated changes when they can be reviewed and rolled back independently. Combining a runtime upgrade, state migration, and timeout adjustment makes attribution difficult. Sometimes changes must be coordinated; then describe that coupling and their deployment order explicitly. A small patch can still require a substantial operational explanation if it changes access or persistent state.

Hosted pull or merge requests add discussion and checks around a proposed branch. The hosting interface is not required for this local exercise. Review and approval should bind to the actual commit being deployed; revisions after approval can invalidate the earlier evidence. Record the source commit, artifact digest, and environment-specific configuration identity during deployment so the live system can be related to the reviewed change.

Secrets do not belong in ordinary Git history. Removing a credential in the next commit leaves the previous commit reachable. Ignore rules prevent some accidental additions but do not make committed secrets safe. If a credential is committed, revoke or rotate it promptly according to the system's incident procedure, then address repository/history cleanup without claiming deletion alone removed every copy. Use fictional values for examples and restricted secret storage for real deployments.

## Merge conflicts reveal overlapping intent

A merge integrates histories. If both sides changed the same area incompatibly, Git asks a human to resolve the content. Conflict markers identify competing text, not which text is operationally correct. A syntactically valid resolution can still violate timeout relationships or delete a security restriction.

Before beginning a merge, preserve unrelated work and inspect your current status. Git warns that aborting a merge cannot always reconstruct preexisting uncommitted changes. Starting from a clean, understood boundary makes recovery easier. `git merge --abort` abandons an in-progress merge attempt; it is not a substitute for remembering which local work existed before the attempt. [Git merge reference](https://git-scm.com/docs/git-merge).

In the disposable repository, create a deliberate conflict from the initial commit. The following commands assume the first lab completed and the current branch is `extend-drain`:

```bash
git switch main
git switch -c shorter-drain
printf 'drain_seconds=20\n' > service-policy.conf
git add -- service-policy.conf
git commit -m 'Explore shorter drain interval'
git switch extend-drain
git merge shorter-drain
```

The final command is expected to report a conflict and return nonzero. Read `git status`, inspect the file, and explain the two intentions. For this lab, keep the 45-second policy by replacing the conflicted file with that one line, stage it, check the staged diff, and complete the merge:

```bash
printf 'drain_seconds=45\n' > service-policy.conf
git add -- service-policy.conf
git diff --cached --check
git commit -m 'Resolve drain-policy experiment in favor of bounded longer interval'
git status --short
```

This chosen lab resolution is not a factual conclusion that 45 is always correct. In production, resolve with the timeout/drain evidence and consult owners of both changes. After a conflict, rerun relevant configuration checks because the resolved result is new content. A successful merge operation only establishes that history and content were recorded.

## Revert preserves the story of a correction

To undo a shared change, a revert creates a new commit that reverses selected earlier changes. It preserves the visible history instead of pretending the original change never happened. Reverting a merge has additional parent-selection semantics and can affect later merging; do not select a parent number without understanding the graph. [Git revert documentation](https://git-scm.com/docs/git-revert).

A simple isolated revert exercise is clearer than applying it to the deliberate merge conflict. In the same disposable repository, create and revert a temporary diagnostic setting:

```bash
printf 'debug_inventory=true\n' > diagnostic-policy.conf
git add -- diagnostic-policy.conf
git commit -m 'Add temporary diagnostic policy'
git revert --no-edit HEAD
git status --short
git log --oneline -2
```

The new revert commit removes the file introduced by the immediately preceding commit. The history records both decisions. A working-tree restoration is different: `git restore` can replace uncommitted content from the index or a chosen source. Inspect the content and preserve work you want before doing so. `git restore --staged` adjusts the staged boundary; it need not discard the working file. [Git restore reference](https://git-scm.com/docs/git-restore).

Avoid casual `reset --hard`, forced pushes, or broad clean commands in a shared workflow. They can discard work or rewrite others' reference points. Recovery mechanisms such as reflogs are useful but depend on local retention and do not guarantee every uncommitted file can be recovered. A safer correction often begins with a new commit and a deliberate deployment decision.

## Source reversal is not service rollback

Suppose Harbor reverts the drain-policy commit but the live service still uses the larger interval. First identify the deployed configuration and process start time. A source revert changed desired history; it did not execute the deployment or restart the service. Reconcile the live state through the approved deployment path and verify the effective unit/application settings afterward.

A harder failure involves data. If an application upgrade migrated the database, reverting its source does not reverse the migration. The old program may be incompatible with the new state. A rollback plan must specify artifact/configuration compatibility, data handling, and verification. Preserve accepted orders and notification intent rather than restoring an old filesystem snapshot blindly over new customer work.

When an emergency host edit is necessary, capture its exact change and reason, then incorporate the intended result into the maintained configuration before routine deployment overwrites it. Compare actual and desired state to close the loop. Harbor's small team benefits from this as much as Atlas's larger review system: scale changes the workflow's volume, not the need for accountable intent.

## Exercises and takeaways

1. Stage a change, edit the file again, then compare ordinary and cached diffs. Guidance: identify which version the next commit includes; do not equate your latest editor view with staged content.
2. Complete the conflict lab and explain why checking syntax cannot choose the right drain interval. Guidance: conflicting business intent needs evidence, not just removal of markers.
3. Run the diagnostic revert and distinguish it from restoring an uncommitted file. Guidance: revert adds history; restore changes a working/index state from a selected source.
4. Design a deployment record connecting source, artifact, configuration, and live verification. Guidance: include identities and observed results for each; a branch name alone is mutable and insufficient.

Git makes operational intent reviewable and preserves the history of corrections. Inspect staged content, resolve conflicts through engineering evidence, and keep deployment/data recovery separate from source history. Continue to [Chapter 20](020-scheduling-and-resource-limits.md) for the scheduled execution of reviewed automation.

## Verification

The author inspected official Git diff, switch, merge, revert, and restore references. Local exercise execution is recorded in the continuation summary. No remote repository, hosted review, push, production deployment, or actual data rollback was performed.
