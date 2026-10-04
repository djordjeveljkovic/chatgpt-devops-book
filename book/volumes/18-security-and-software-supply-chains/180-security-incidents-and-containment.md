---
book: The Complete DevOps Engineering Book
volume: 18
volume_title: "Security and Software Supply Chains"
chapter: 180
title: "Security Incidents and Containment"
slug: security-incidents-and-containment
status: complete
summary: ../../_ai/chapter-summaries/180-security-incidents-and-containment.md
---

# Chapter 180 — Security Incidents and Containment

**Section outline:** establish a coordinated incident command; contain access and impact while preserving evidence; eradicate persistence and recover through verified, monitored steps.

## Why this matters

At 02:10, DispatchDesk's on-call engineer sees a new deployment and unusual outbound traffic from a worker. A repository credential may have been stolen, an image tag changed, and customer records accessed. Restarting every worker could stop the traffic, but it would also destroy volatile evidence and interrupt order processing before the team understands which credentials or systems are affected. Waiting for certainty could let the attacker continue.

Incident response is coordinated risk reduction under uncertainty. The first objectives are to protect people and customers, limit ongoing harm, preserve enough evidence to understand scope, and keep decision-makers informed. The plan must specify who can isolate workloads, disable identities, suspend releases, contact providers and authorize service disruption. This chapter follows the current NIST incident-response framing in which response readiness is integrated across cybersecurity risk management, rather than treating a single linear checklist as sufficient for every event.

Chapters 174–178 describe relevant boundaries and evidence: Kubernetes security, secret rotation, workload identity, vulnerability data, and signed artifacts with provenance. They help responders ask which identity, image, control plane and release path may be affected.

## Establish command and build the incident picture

Use the organization's incident plan and escalation contacts. Assign an incident lead to coordinate decisions, a technical lead to direct investigation and containment, an operations lead to manage service impact, and a communications/legal/privacy contact when the incident may affect customers, regulated data or contractual reporting. One person may cover several roles in a small team, but keep a clear decision owner and a durable timeline. Separate confirmed facts, working hypotheses and unknowns so that a plausible story does not become an assumed fact.

Start a case record with incident ID, detection time and timezone, reporter, affected service, initial indicators, decisions, approvers, actions, evidence references and next review time. Use an approved restricted channel. Avoid pasting secret values, personal data or unredacted customer payloads into a broad chat or ticket. Preserve original timestamps and record clock sources; event times from different systems may be skewed or delayed.

Build a working scope across identities, source repositories, build systems, registries, cloud accounts, clusters, hosts, networks and data stores. Record affected and potentially affected resources, known-good references, likely persistence paths and dependencies. Search provider audit events, source control changes, CI runs, image digests, identity-provider grants, Kubernetes events and application telemetry by shared identifiers and time window. Chapter 179's evidence discipline helps connect the events without treating one dashboard as a complete record.

Select containment actions based on threat, blast radius and service consequence. Possible actions include disabling or narrowing a compromised identity, revoking a session or token, blocking a malicious artifact digest, suspending a release workflow, isolating an affected workload, restricting egress, pausing an integration or moving traffic to a known-good deployment. Prefer targeted, reversible actions when they adequately stop the threat. If immediate containment requires a broad outage, make the impact and alternatives explicit, identify the approver, and set a reassessment time.

Before destroying or rebuilding a system, consider evidence value, volatility, legal or contractual preservation requirements, and operational risk. Preserve relevant audit logs and registry/source records promptly because retention may be short. For a high-risk host or workload, use an approved forensic process for disk or memory acquisition where feasible. Containment should not be delayed when harm is active: document what could not be captured and why. Restrict evidence access and maintain chain-of-custody information appropriate to the organization's investigation.

## Contain identity and software supply-chain compromise

Credential response must follow the credential's lifecycle and dependencies. Disable compromised identities or remove malicious grants, revoke active sessions where supported, rotate affected secrets and certificates, then update every consumer that depends on the replaced value. Revoking a refresh credential may not terminate already-issued access tokens; a password reset may not remove attacker-created access keys or federation trust. Verify the specific provider's revocation behavior and monitor for continued access. Chapter 175 covers coordinated rotation and consumer recovery; do not assume a new secret value alone ends an active session.

For a CI or repository compromise, pause affected release workflows and preserve workflow definitions, actor identities, review events, runner images, job logs and cloud audit records. Review changes to protected branches, workflow permissions, runner registration and OIDC trust. Revoke compromised runner or cloud access, remove unauthorized application grants, and rotate secrets exposed to the job. Rebuild on a trusted, isolated runner from a reviewed commit after confirming that the builder and dependencies are not themselves compromised.

For an artifact compromise, identify exact manifest digests and platforms from registry and deployment records. Do not rely only on tags, which may have moved. Compare expected signatures, signer identity and provenance subject as described in Chapter 178. Quarantine or block the suspicious digest through the approved registry and admission mechanisms; avoid deleting evidence. Deploy a verified known-good digest only after checking its source, compatibility and downstream data effects. A valid signature from an affected release identity may not be sufficient if the workflow or builder was compromised.

For an exposed secret, determine where it was used and whether logs, caches, artifacts, crash dumps or third-party systems retain copies. Restrict access to those materials, invalidate the credential and validate dependent services. Remove the exposed value from active configuration and history where feasible, but understand that history rewriting cannot retract clones or cached logs. Treat a leaked bearer token as compromised until the issuer's revocation and expiry behavior establish otherwise. Keep application recovery separate from proof that an attacker has lost access.

## Eradicate, recover and learn

Containment limits active impact; eradication removes the access and persistence that enabled it. Identify the initial access path, affected principals, persistence mechanisms, modified infrastructure and potential lateral movement. Patch or remove the entry point, revoke unauthorized access, rebuild affected systems from trusted sources when integrity is uncertain, and validate configuration before restoring connectivity. A narrow cleanup that leaves another foothold can create a false recovery signal.

Recover in controlled steps. Define what must be true before service resumes: artifact digest and provenance verified; workload identity and secrets rotated with consumers confirmed; deployment configuration reviewed; data integrity assessed; monitoring and alerting active; and a rollback or isolation path ready. Start with a test instance or canary, observe expected health and security signals, then expand traffic in stages. Monitor for renewed suspicious authentication, unexpected image changes, unusual egress, persistence attempts and data anomalies. If new signs of compromise appear, return to investigation and containment rather than continuing rollout to meet a schedule.

Communicate status at a cadence suited to impact. Keep internal responders aligned on confirmed scope, actions, owners and decisions. Use approved customer and regulator channels after the relevant legal, privacy and communications review; reporting obligations and deadlines vary by jurisdiction, contract and incident facts. Do not speculate publicly about attribution or claim eradication before evidence supports it. Provide affected teams with actionable service guidance and a next update time.

Close response only after accountable owners agree that the threat is contained, recovery meets business and security criteria, monitoring can detect recurrence, and open risks have owners and deadlines. Preserve the timeline and evidence references. In a blameless review, identify contributing system conditions, which controls detected or failed to prevent the event, where decisions were delayed, and which changes will reduce recurrence. Assign corrective actions with owners, due dates and verification evidence; update runbooks and exercise the changes.

In the DispatchDesk event, the team blocks the unexpected image digest at admission, suspends the affected release workflow, disables the suspected CI identity and checks for other active credentials and grants. They preserve provider and repository audit data before short retention windows expire. Investigators find that the attacker changed a release workflow and published a second digest; the production cluster ran the first untrusted digest for seven minutes. The team restores a previously verified artifact, rotates credentials across its consumers, rebuilds the workflow on a trusted runner and validates the new image's signature and provenance. Database audit records show no unauthorized query, but the team continues heightened monitoring and records the evidence limit: absence of a matching event does not prove no data was read through another path. Customer communications follow the incident plan after the scope and notification obligations are reviewed.

Exercises:

1. A suspected compromised workload is sending data out now. Which containment decisions are immediate, and which evidence can responders preserve in parallel?
2. A CI credential was rotated, but suspicious cloud access continues. What other credentials, sessions, grants and persistence paths should be investigated?
3. A signature verifies for a suspicious digest, but its release workflow may be compromised. What evidence determines whether the artifact is trustworthy enough to deploy?
4. A clean image is ready, but the service depends on a database that may have been modified. What recovery gates should be met before restoring normal traffic?

Answer guidance: stop active exfiltration using the narrowest effective control and preserve volatile/short-retention evidence in parallel when feasible; if safety requires immediate isolation, document lost evidence. Examine active sessions, access keys, service roles, OIDC trust, grants and downstream copies, then monitor for continued use. Validate signer identity, workflow integrity, builder trust, source review, provenance and the exact subject digest; signature validity alone is insufficient if the signer path may be compromised. Assess data integrity, restore from trusted recovery points if needed, validate application compatibility, use canary monitoring and preserve a rollback or isolation option.

Review questions:

- How should an incident team distinguish confirmed facts from hypotheses?
- Why can credential rotation fail to terminate an attacker's existing access?
- What identity and artifact evidence matters during a supply-chain incident?
- Which operational and security criteria should gate recovery?

Takeaways:

- Establish a decision owner, secure case record and shared incident timeline early.
- Contain active harm while preserving evidence where feasible; record the tradeoffs when actions destroy evidence.
- Revoke identities and restore artifacts based on their actual lifecycle, exact digest and trusted build path.
- Recover in monitored stages, return to containment when compromise recurs, and verify corrective actions after review.

## Sources checked 2026-10-04

- [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) — current NIST incident-response recommendations integrated with CSF 2.0 risk management; supersedes Rev. 2.
- [NIST Incident Response project](https://csrc.nist.gov/projects/incident-response) — current lifecycle framing and implementation resources.
- [CISA StopRansomware Guide](https://www.cisa.gov/stopransomware/ransomware-guide) — containment planning and preservation of volatile evidence.
- [Cosign verification](https://docs.sigstore.dev/cosign/verifying/verify/) — image digest, signer identity and attestation verification.
- [Chapter 175 — Secrets and Credential Rotation](175-secrets-and-credential-rotation.md) and [Chapter 178 — Artifact Signing and Provenance](178-artifact-signing-and-provenance.md) — related book guidance.

This chapter is an operational framework, not a substitute for organization-specific incident plans, forensic procedures, provider documentation, legal advice or reporting obligations. No incident was handled and no live credentials, workloads, accounts or artifacts were changed.
