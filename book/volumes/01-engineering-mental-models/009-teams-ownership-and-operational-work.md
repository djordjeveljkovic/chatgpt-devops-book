---
book: The Complete DevOps Engineering Book
volume: 1
volume_title: "Engineering Mental Models"
chapter: 9
title: "Teams, Ownership and Operational Work"
slug: teams-ownership-and-operational-work
status: complete
summary: ../../_ai/chapter-summaries/009-teams-ownership-and-operational-work.md
---

# Chapter 9 — Teams, Ownership and Operational Work

## Service ownership and handoffs

DispatchDesk's worker stalls shortly before a responder's shift ends. The outgoing engineer knows the likely cause, the incoming engineer knows the service, and both assume the other will finish the investigation. No one checks pending notifications for two hours. The gap is organizational, even though every relevant technical skill exists in the team.

Read [Working Safely at the CLI](008-working-safely-at-the-cli.md) first. This chapter turns Chapter 1's ownership map into daily operational behavior: explicit handoffs, useful documentation and readiness evidence. It uses complete Markdown examples rather than commands because the immediate work is agreeing responsibility, not modifying a server. The mechanics apply equally to Ubuntu and Fedora/RHEL services.

A service owner is responsible for maintaining the service contract and its operating path. An incident responder owns a particular response until responsibility is explicitly transferred. A specialist may investigate the database without becoming responsible for customer communication. These roles can be held by the same person in a small team, but the distinction prevents specialized work from leaving the broader outcome unattended.

Handoffs occur across time, teams and lifecycle stages. A developer can hand a release to the current responder. A platform team can hand an application capability to a product team. An outgoing shift can hand an incident to the next shift. In each case, a useful handoff transfers current state, decisions, evidence, unresolved questions, access prerequisites and the exact next action.

A message sent is not necessarily a responsibility received. For urgent ongoing work, the receiving person should acknowledge the scope and confirm that they can act. If they lack access, the sender has discovered a readiness failure while there is still someone available to help. The team should define how unresolved handoffs escalate rather than leave this to personal goodwill.

Harbor has two developers sharing operations. It cannot honestly promise a continuously staffed specialist response simply by installing an alerting application. It needs an explicit support window, an escalation arrangement and expectations matching its staffing. Summit may have a larger rotation with provider-support integration. Atlas may divide application and platform response but must define when an incident crosses that boundary. These are fictional arrangements, not employment recommendations or legal requirements.

Google's 2016 [Being On-Call chapter](https://sre.google/sre-book/being-on-call/) describes its own approach to sustainable response and escalation. The adaptable lesson is to treat response capacity as an engineered responsibility with support, not an unlimited personal resource. Copying its staffing numbers without its service scope and assumptions would miss that lesson.

## Toil, collaboration and documentation

A recurring ticket can reveal a system boundary that needs improvement. If support repeatedly asks an engineer to find pending notification state, the service may lack a safe inspection interface. If releases repeatedly require manual directory edits, packaging or configuration management may be incomplete. Record the trigger, time spent, impact and resolution so patterns become visible.

Not all repeated work should immediately be automated. A rare task can be cheaper to document and rehearse. A poorly understood task may be risky to automate because the script would reproduce uncertain decisions. A high-frequency deterministic task may be an excellent candidate. Evaluate expected saved work, implementation cost, maintenance cost and failure impact together. Google's historical [toil chapter](https://sre.google/sre-book/eliminating-toil/) supplies useful context, while the prioritization example below is original to DispatchDesk.

Suppose Harbor receives six weekly requests to inspect delayed notification state, taking about fifteen minutes each. That is a fictional estimate of ninety minutes per week, not measured evidence. A controlled support view may save time and improve customer communication. It also requires authorization and privacy design. A shell script that prints every customer's destination might save engineering time while creating a security defect. Define the information support needs before choosing the interface.

Useful collaboration brings different evidence together. Support identifies the customer-visible symptom. Development explains the application's state transitions. Operations identifies the active deployment and dependency path. Security clarifies acceptable access. These perspectives are complementary; a review should resolve a concrete decision rather than collect ceremonial approvals from every role.

Documentation has several purposes. A **runbook** describes what to do for a specific operating condition. A **reference** describes stable facts and commands. A **decision record** explains why a choice was made. A **handoff** records current temporary state. Putting all four into one long page makes it difficult to distinguish lasting procedure from yesterday's incident workaround.

A runbook should state the trigger, impact, prerequisites, read-only diagnosis, bounded actions, verification, recovery and escalation. Its commands must include target context and expected evidence. A runbook that starts “restart the worker” without checking whether provider work is uncertain can be actively harmful. Documentation should be rehearsed by someone other than its author so hidden assumptions become visible.

## A practical operational readiness review

A readiness review asks whether the intended service can be operated under its contract. It does not certify every possible future behavior. Choose scenarios from the actual design and known risks. Harbor's first release needs host recovery and basic release rollback evidence. Atlas additionally needs platform boundaries and tenant isolation. A checklist copied from a large organization can provide prompts, but irrelevant items and missing local risks reduce its usefulness.

Google's [launch checklist](https://sre.google/sre-book/launch-checklist/) is a historical primary example of broad launch questions. DispatchDesk's smaller review below is a fictional adaptation built around its specific journey. It records evidence and gaps rather than using checkmarks as substitutes for proof.

```markdown
# DispatchDesk readiness review — initial learning service

Scope: order acceptance and asynchronous notification on one host
Owner: service team
Decision: learning deployment only; production approval not yet established

## Acceptance and data
Evidence required: controlled order retrieved after application restart.
Evidence required: notification intent persists independently of worker lifetime.
Open gap: backup retention and host-loss restore rehearsal.

## Release
Evidence required: active artifact identifier can be found by the responder.
Evidence required: previous artifact reads the post-release data schema.
Open gap: rollback rehearsal with an in-flight order.

## Detection and response
Evidence required: pending notification age can be inspected safely.
Evidence required: alert route reaches the assigned responder.
Open gap: after-hours coverage agreement.

## Access
Evidence required: responder can reach approved diagnostics.
Evidence required: support cannot inspect another tenant's order.
Open gap: independent recovery access during host loss.

## Follow-up
Each gap receives an accountable owner and a review date.
Do not infer production readiness from successful process startup.
```

This document is a planning artifact, not a claim that its checks passed. Replace “evidence required” with actual rehearsal records only after doing the work. The decision at the top reflects current scope; unresolved material gaps should remain visible to anyone considering production use.

A good review has several possible outcomes. It may approve a narrow launch, approve with explicitly accepted limitations, or defer because a required contract lacks evidence. An exception should identify the accepted risk, owner, expiry or review trigger and compensating action. “We will fix it later” is not a useful exception because it gives a future responder no decision boundary.

Review readiness again when important assumptions change: traffic grows, staffing shrinks, tenancy changes, a new provider joins the acceptance path or recovery evidence fails. A service's operating needs evolve independently of its launch date. The review should be short enough to remain usable and precise enough to catch a broken boundary.

## Repairing the lost handoff

Return to the stalled worker. The outgoing engineer inspected provider authentication failures and disabled normal consumption to preserve pending work. Their final chat message said “worker issue investigated” but did not explain that consumption remained disabled. The incoming responder interpreted the phrase as completed recovery. Pending age increased even though no new error logs appeared.

The immediate responder restores shared understanding: what is disabled, why, which records are pending, whether provider attempts are uncertain and who owns the next step. They verify the corrected credential through a controlled item, resume consumption under the established delivery contract and check pending age. Support receives an accurate description of affected orders and expected delays. No one replays all items blindly merely because the queue is old.

A useful repaired handoff is:

```markdown
# Worker incident handoff — illustrative

Current owner: incoming service responder, acknowledged at 16:00 UTC
Impact: notifications delayed; order acceptance continues
Current state: normal worker consumption intentionally disabled
Reason: provider authentication fails after credential reference change
Evidence: sanitized error category and release record attached internally
Uncertainty: provider acceptance of two earlier attempts not yet reconciled
Next action: validate approved credential reference with controlled test item
Recovery check: pending age decreases; uncertain attempts reconciled separately
Escalation: integration engineer if authentication still fails
```

The wording transfers a specific responsibility and retains uncertainty. It is useful even if a future engineer has never read the original chat. Do not place real credentials or sensitive customer data into a shared handoff; link authorized evidence through the team's controlled system instead.

The lasting correction adds an acknowledged handoff to active-incident shift changes and makes intentionally disabled work visible in diagnostics. The team rehearses the handoff with a new responder. This combines organizational and technical repair: a better note helps, and observable disabled state prevents the note from being the only evidence.

## Exercises and answer guidance

1. A platform team provides a database, but a query migration causes an outage. Who owns which work? The application team owns query correctness and migration design; the platform team owns its stated database capability; the incident owner coordinates the joint outcome. Define the escalation boundary rather than assign blame from the component's name.
2. Rank a weekly manual inspection and a yearly maintenance task for automation. Include frequency, effort, consequence, implementation cost and uncertainty. Frequency alone is insufficient; a yearly dangerous procedure may need rehearsal before automation.
3. Write a handoff for an unresolved backup failure. State affected protection, last verified recoverable point, current actions, uncertainty, next owner and escalation. Avoid claiming data loss merely because a backup failed; distinguish increased exposure from an actual failure.

## Review questions and takeaways

When is a handoff complete? Which documentation describes current state and which describes stable procedure? What evidence supports a readiness decision? Which operating gaps can the actual team cover? What recurring work suggests a missing interface or automation opportunity?

Make responsibility explicit, transfer it with evidence and acknowledgement, and match promises to real response capacity. Prioritize recurring work by its lasting improvement. Review readiness against concrete service scenarios, retaining gaps until verified. Continue with [The DispatchDesk Project Begins](010-the-dispatchdesk-project-begins.md).

## Sources and verification

Google's 2016 SRE on-call, toil and launch-checklist chapters were inspected on 2026-10-01. The small-team procedures and documents are original fictional examples, not claims about Google's current organization. No alert route, handoff, access test, readiness rehearsal or infrastructure operation was executed. Independent review is pending.
