---
book: The Complete DevOps Engineering Book
volume: 19
volume_title: "Site Reliability and Recovery"
chapter: 183
title: "Incident Command and Communication"
slug: incident-command-and-communication
status: complete
summary: ../../_ai/chapter-summaries/183-incident-command-and-communication.md
---

# Chapter 183 — Incident Command and Communication

**Section outline:** declare and scale a coordinated response; separate command, technical work and communications; maintain a shared incident record and hand off authority clearly.

## Coordinate the response as well as the repair

DispatchDesk's checkout path starts failing in two regions. Three engineers independently roll back different components, while a fourth tells customers that data loss is impossible. The actions conflict, ownership is unclear and the public statement exceeds the available evidence. A technical incident needs both a mitigation effort and a response structure that helps people coordinate safely.

Declare an incident when impact, uncertainty or coordination needs exceed normal on-call handling. Early declaration creates a place to organize work; it does not claim that the cause is understood or that the incident is severe by a particular external standard. Record a short incident name, commander, current impact, severity rationale and next update time. If the incident expands, add responders and roles deliberately rather than broadcasting an unbounded request for “all hands.”

## Assign command, operations and communications

Use a lightweight command model that fits the incident. The incident commander (IC) owns the response process: establish priorities, assign leads, resolve coordination conflicts, track decisions and set exit criteria. The operations lead directs technical mitigation and delegates bounded work to specialists. The communications lead maintains the shared status, answers stakeholder questions and issues approved updates. A scribe or planning lead can maintain the timeline, tasks, dependencies and handoff when incident size justifies the role.

One person may cover several roles for a small incident, but name which responsibilities are active. The IC should not become the default operator executing every command; separating response coordination from system modification lowers the risk that urgent technical work loses its decision context. Define who can authorize destructive changes, customer-visible failover or suspension of a revenue path. Role structure follows incident knowledge and availability, not organizational seniority alone.

Every task should have one owner, a specific outcome and a way to report completion. For example, “verify whether the database is rejecting new connections, using read-only telemetry, and report the time range and evidence in five minutes” is clearer and safer than “look at the database.” Separate parallel investigations from changes that alter the same system. The operations lead tracks system-changing work and avoids concurrent conflicting actions.

## Maintain a shared state and accurate updates

Maintain one durable incident record reachable even when the affected production system is unavailable. Keep the most useful current state at the top: impact, status, incident roles, command channel, actions in progress, decisions, risks, exit criteria and next update time. Append a timestamped timeline rather than rewriting history. Record both successful and failed mitigation attempts, command or change reference, executor and observed result. Link detailed evidence in access-controlled systems instead of copying secrets or customer data into the record.

Use a simple update structure: what users experience, when it began or was detected, scope known so far, mitigation underway, current uncertainty and when the next update will arrive. Distinguish “we have not observed” from “did not happen.” Give responders technical detail in their working channel and stakeholders a concise impact statement. Have the communications lead coordinate external wording with the incident commander and required legal, privacy or customer support functions. Do not publish guesses about cause, attribution, recovery time or data impact as fact.

Set an update cadence appropriate to incident impact and change rate. For a rapidly changing customer outage, updates may be frequent; a stable investigation may need a longer interval. If there is no new information, say what is being checked and when the next update will occur. Silence makes people seek status through side channels and distracts responders. Maintain an approved backup communication method if the primary chat, identity provider or network may be affected.

## Scale, hand off and close

Scale response when work, duration, stakeholder breadth or uncertainty exceed the current team's capacity. Add a subject-matter expert for a bounded technical question, not as an unassigned second commander. Bring in security, privacy, legal, vendor, facilities or business owners based on the risk. Keep the responder group small enough to maintain a shared picture, and route requests through the communications lead or designated liaison.

Hand off command explicitly. The incoming IC should read the shared record, hear current scope and risks, confirm outstanding actions and agree on the next update. The outgoing commander states the transfer and receives acknowledgement; update the record and announce the new owner in the command channel. Do not let a shift boundary or a calendar change silently transfer responsibility. Technical action ownership should also transfer by name and confirmation.

Define exit criteria before the response is over: user-impact signals are within the agreed range for a specified observation period; dangerous changes are stopped or controlled; data integrity has an owner and result; monitoring is active; unresolved risks and customer actions are assigned; and the follow-up review is scheduled. “The page stopped” is not enough when telemetry may be broken. The IC announces transition to recovery monitoring or closure and records the reason. Chapter 180 discusses containment and eradication for security incidents; this command model applies across operational incident types.

In the checkout event, an engineer declares the incident and remains IC while a database specialist takes Operations Lead and a support lead takes Communications Lead. The IC sets a user-impact objective and pauses unrelated rollouts. The operations team tests database saturation and edge retries in parallel, with one owner for each, then makes a controlled rollback after confirming the candidate release increased retry load. The communications lead tells customers which checkout path is impaired, which alternatives work, and when the next update will arrive. The team observes the SLI from Chapter 181, verifies queued orders are intact, hands command to the next shift by acknowledgement and keeps a recovery watch before closing.

Exercises:

1. Three responders are changing the same service and one announces an unverified root cause. Which roles and records should the IC establish first?
2. The outage is stable but customers still need updates. What should a useful update contain when there is no new cause or ETA?
3. The incident commander is ending their shift. What must happen before the incoming responder owns command?
4. The main chat provider is affected by the outage. Which communication prerequisites should the response plan include?

Answer guidance: establish a named IC and Operations Lead, pause conflicting changes, assign bounded tasks, create a shared timeline and label hypotheses. Report known impact, mitigation, current uncertainty and next update time without inventing an ETA. Transfer context and risks, confirm ownership and announce the handoff. Choose an out-of-band channel and access path before incidents, with a maintained contact tree that does not depend solely on the affected service.

Review questions:

- Why are incident coordination and technical mitigation separate activities?
- Which information belongs in the shared state record?
- How can a communications lead make updates useful without overstating certainty?
- What evidence supports transitioning from active response to recovery monitoring?

Takeaways:

- Declare early when coordination needs exceed ordinary on-call handling, and scale roles to the incident.
- Assign one owner to each task and coordinate system-changing work through Operations Lead.
- Keep a durable, timestamped record and communicate impact, actions, uncertainty and next update.
- Transfer command explicitly and close only against observable exit criteria.

## Sources checked 2026-10-04

- [Google SRE Workbook: Incident Response](https://sre.google/workbook/incident-response/) — command, operations and communications roles, coordination and incident declaration.
- [Google SRE: Managing Incidents](https://sre.google/sre-book/managing-incidents/) — incident roles, state records and acknowledged handoff.
- [Google SRE: Example Incident Document](https://sre.google/sre-book/incident-document/) — shared status, command hierarchy, exit criteria and timeline.
- [Chapter 181 — SLIs, SLOs and Error Budgets](181-slis-slos-and-error-budgets.md) and [Chapter 180 — Security Incidents and Containment](../18-security-and-software-supply-chains/180-security-incidents-and-containment.md) — related response context.

The fictional incident and roles are illustrative. No incident channel, customer update, system change, failover, rollback or shift handoff was executed.
