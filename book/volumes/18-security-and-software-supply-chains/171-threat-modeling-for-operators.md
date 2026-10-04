---
book: The Complete DevOps Engineering Book
volume: 18
volume_title: "Security and Software Supply Chains"
chapter: 171
title: "Threat Modeling for Operators"
slug: threat-modeling-for-operators
status: complete
summary: ../../_ai/chapter-summaries/171-threat-modeling-for-operators.md
---

# Chapter 171 — Threat Modeling for Operators

**Section outline:** identify assets and trust boundaries; turn system flows into abuse paths; select controls with observable evidence; model DispatchDesk's release-to-customer path; revisit the model when operations change.

## Assets, identities and trust boundaries

Threat modeling is a structured way to ask how a system could be abused, what would be harmed, which controls reduce that harm and who verifies the result. It makes architecture and operational assumptions visible while there is still time to change them. It does not predict every attacker or certify that a system is secure. A useful model is scoped, dated, connected to owners and revised as the system changes.

Start with the business outcome and the assets that must survive abuse: customer orders, notification intent, account credentials, signing keys, deployment authority, backups, availability and audit evidence. Include non-data assets such as the ability to release an approved fix or recover an account. For each asset, state its confidentiality, integrity and availability needs in terms of actual product and recovery commitments. “Protect the database” is too vague to drive a useful control.

Draw the system's people, processes, data stores and flows. Mark where identity changes, data crosses administrative ownership, network zones or privilege, and where an operator or automation system can alter behavior. A trust boundary is a point where an assumption about identity or integrity changes; a subnet label or private address alone does not prove trust. Note the protocol and credential at each important flow, who controls it and what evidence records its use.

For an operator review, include build runners, artifact registries, deployment roles, production runtime identity, secret delivery, database and queue permissions, backups, logs, DNS, support access and third-party endpoints. These components can be outside the application process while still controlling customer data or availability. A diagram that stops at the application load balancer hides many high-impact paths.

Set scope and assumptions explicitly. Identify the environments covered, excluded systems, data classifications, operator groups, external providers, and whether the model assumes a compromised workstation, maintainer account, build action, container image or cloud role. Threats change when an assumption changes. Do not expand the scope until the model becomes an unbounded inventory; create linked models for a specific critical path when necessary.

## Turn flows into abuse paths

Follow one valuable action from origin to effect. Ask who can initiate it, what identity authorizes each hop, which input is attacker-controlled, where it is validated, what persistent state changes and what makes the outcome detectable or recoverable. An abuse path is a sequence of prerequisites and actions that reaches an unacceptable outcome. This keeps the discussion specific enough to map controls and tests.

STRIDE is one useful way to prompt threat discovery across spoofing, tampering, repudiation, information disclosure, denial of service and elevation of privilege. Use it as a coverage aid rather than a requirement to invent one finding per letter for every component. Business misuse cases can be clearer: “a departing contractor still deploys,” “a duplicate provider effect is recorded as one,” or “an operator restores an old backup over accepted orders.” The [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html) describes decomposition, threat identification and ranking, mitigation, and review/validation; it also recommends representing flows, stores, actors and trust boundaries.

Write findings so a team can make a decision. A compact record includes an ID, affected asset/flow, actor capability, precondition, abuse path, impact, likelihood rationale, existing controls, needed action, verification evidence, accountable owner and residual risk. A risk label should explain the context behind it. A numeric score can help sort a defined backlog, but arithmetic does not remove uncertainty or decide who accepts the remaining exposure.

Controls need observable evidence. “Require MFA” should identify which human identities, which enforcement point and how the team tests denial without MFA. “Encrypt data” should name the path or store, key owner, rotation/access policy and recovery dependency. “Least privilege” should name a permission boundary and a negative test. Prefer layered prevention, detection and recovery when no single control can exclude an entire abuse path.

For operational changes, review both desired configuration and effective access. A workflow file may declare minimal permissions while a separate cloud role remains overbroad. A private queue may still trust the wrong principal. A signed artifact may be signed by a compromised build identity. Follow the path to the protected resource and test the boundary that actually enforces the requirement. [AWS IAM security best practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) recommend temporary role credentials and least privilege; the concrete trust and action scope still require account-specific review.

Prioritize by credible impact, exposure, prerequisites and recovery cost. A public unauthenticated path to customer data differs from a threat requiring console access by a tightly controlled administrator. Do not reduce likelihood merely because a mitigation is planned. Record the current state, the target state, the evidence that would close the item and the person authorized to accept residual risk.

## Threat model DispatchDesk

DispatchDesk accepts customer orders through an internet-facing API. The API writes an order and notification intent to a database; an outbox publisher sends an event to a queue; a worker calls an email provider. A CI system builds a container image, publishes it to a registry and updates the runtime. Operators use federated identities for cloud administration. Backups and logs are separate managed data stores. [Chapter 170](../17-distributed-systems-and-data-operations/170-stateful-recovery-and-data-migration.md) makes source-of-truth and recovery evidence explicit; those same assets matter when this system is abused.

A text flow diagram is enough to begin:

```text
Customer/browser
    | HTTPS, untrusted request
    v
Public edge -> API runtime -> orders + notification intent + outbox
                                  |
                                  v
                            event publisher -> queue -> worker -> email provider

Reviewed source -> CI runner -> image registry -> deploy identity -> runtime
      |                  |                              |
      +---- trust boundary: repository governance -------+

Operator identity -> cloud control plane -> runtime, data, secrets and backups
```

The diagram leaves out exact vendor topology on purpose. During a review, replace each generic connection with the actual identity, policy, network path, secret and audit source. Mark where untrusted pull-request code executes, where a build can receive a deploy credential, where a production image is selected, and which runtime principals can read each store. Do not draw a dashed arrow and call it controlled without naming the enforcing policy.

One concrete abuse path starts with a compromised maintainer credential or malicious change that reaches a privileged release workflow. If that workflow executes untrusted code with deployment credentials, the attacker can alter the release or use the credential directly. A changed image can then run under the production task identity, read data available to that identity and create fraudulent orders or notifications. The security boundary is not only the repository branch; it includes review policy, workflow triggers, runner persistence, artifact identity, deployment role and runtime permissions.

| Threat | Impact and current assumption | Control and evidence |
|---|---|---|
| Unreviewed workflow change reaches release credentials | An attacker can publish or deploy altered code. The assumption that “main is trusted” fails if review or branch protection is bypassed. | Restrict who can change workflows and environments; keep untrusted pull-request execution separate from production credentials; use narrowly scoped short-lived deployment identity. Verify protected-branch and environment policy, workflow permissions, audit records and a denied attempt from an untrusted revision. |
| Compromised build output is accepted because its tag looks familiar | A mutable tag can resolve to different content after review. | Promote by immutable digest, record the source revision and builder identity, and verify the approved digest at deployment. Test that a different digest is rejected and retain build/deploy evidence. |
| Runtime identity reads unrelated customer data or changes infrastructure | A compromised application can exercise every permission granted to its identity. | Separate API and worker roles, scope each role to the required data and queue actions, and test allowed and denied operations against the effective identity. Alert on unexpected administrative actions. |
| Worker timeout causes a duplicate receipt | A provider may accept an email whose response is lost, and redelivery can send again. | Reuse the notification identity, apply provider idempotency/reconciliation where supported, and keep uncertain outcomes visible. Test the effect-before-recording recovery path. |
| Ransomware or an operator error deletes primary and backup copies | Availability recovery becomes data loss if backup authority shares the same destructive principal. | Separate backup write/delete authority, retain protected recovery points under policy, and rehearse restore with integrity and customer reconciliation evidence. Verify access separation and restore records. |

The table is a starting register, not a claim that DispatchDesk has these exact controls or a compliance assessment. Assign each action to its actual repository, identity, runtime, data or recovery owner. A threat with no evidence is open even when the control name appears in a design document. A threat that is accepted needs a named decision maker and review date.

## Abuse path, diagnosis and response

The failed assumption in a release review is “the artifact passed CI, therefore production received the reviewed source.” During an incident, an unexpected image digest appears in the task definition after a workflow change. Preserve the deployed digest, deployment actor, source revision, workflow run, action versions, registry push identity and cloud audit events before replacing evidence. Compare them with the approved release record. A green test status does not establish which privileged workflow executed or what bytes it published.

Containment blocks further promotion from the suspected path, disables or narrows the affected deploy identity, and stops replacement tasks from receiving untrusted output. Preserve a known-good digest and verify the runtime actually runs it. Rotate exposed credentials through their owning process; do not paste replacement secrets into workflow logs or a terminal transcript. Review affected runtime permissions and determine whether customer records, outbox events, queues, secrets or backups were accessed or changed.

Recovery rebuilds from reviewed source using a trusted runner and approved dependencies, publishes a new immutable artifact, verifies its provenance and digest, and deploys through a corrected identity boundary. Reconcile order and notification outcomes for the suspect interval using stable IDs. If backups may share the compromised authority, verify their integrity and access logs before treating them as recovery evidence. Restore service only when the release path and customer state both meet the accepted criteria.

GitHub's [secure-use reference](https://docs.github.com/en/actions/reference/security/secure-use) discusses workflow hardening, action pinning and permissions; its [OIDC reference](https://docs.github.com/en/actions/reference/security/oidc) describes claims used in federation. These references help review one possible CI path, not certify every runner or cloud trust policy. Bind federated trust to the intended repository, ref or protected environment under the provider's current claim semantics, and verify the effective role. [Chapter 176](176-federation-oidc-and-short-lived-identity.md) owns the implementation details.

## Keep the model alive during operations

Threat models decay when diagrams and controls no longer match production. Revisit after new data stores, identity changes, public endpoints, queue consumers, build triggers, support paths, acquisitions, major incidents or recovery changes. Trigger review through change management, architecture records and incident follow-up rather than relying on an annual calendar alone. Security-relevant exceptions should have an expiry or explicit reevaluation trigger.

Keep the model useful by linking threats to deployable controls, tests, alerts and runbooks. Track unresolved risks next to ordinary engineering work, but restrict sensitive details that could help an attacker. A model should identify real component names and evidence locations without publishing secrets, exploit recipes or broad internal topology. Record the revision, participants, assumptions, decisions and next review trigger so another operator can continue it.

Threat modeling is a team activity. Operators know identity paths, production failure modes, recovery constraints and the actual configuration; developers know request and business invariants; security staff can challenge assumptions and adversary paths; service owners accept product tradeoffs. Escalate a risk when the designated owner lacks authority to accept it. A diagram is useful only when it changes a decision, test or recovery plan.

## Exercises and answer guidance

A deployment uses an immutable image digest and a valid signature, but the build runner executed an unreviewed workflow with permission to sign. What assumption remains? The signing identity itself may be compromised; verify workflow provenance, review boundaries and signer authority, then rebuild through a trusted path.

A queue is private to the account, but the runtime role can also delete queues and change access policies. What is the concern? The workload's effective permissions exceed message processing and let a compromised worker alter its own boundary. Separate administrative and runtime roles, then test denied control-plane actions.

The threat register says “backups are encrypted.” Is recovery risk closed? No. Confirm an independent destructive authority boundary, retained usable recovery points, decryption-key recovery, restore testing and reconciliation of changes since the recovery point.

A risk has a control owner but no verification evidence. Should it be marked mitigated? No. Keep it open until the named test, configuration inspection or operational evidence demonstrates the boundary works in the intended environment.

## Review questions

- Which assets, identities, data flows and trust-boundary changes are in this model's scope?
- What prerequisites connect the selected abuse path to a business impact?
- Which control prevents the path, which detects it, and what recovery evidence proves service integrity?
- What deployment or incident change should trigger the next model review?

## Takeaways and verification

Threat modeling turns operational assumptions into abuse paths, controls, evidence and accountable decisions. Follow authority and data to the resource that enforces a boundary, and revisit the model whenever a release, identity, dependency or recovery path changes. OWASP threat-modeling, AWS IAM best-practice and GitHub Actions security/OIDC documentation were checked on 2026-10-04. This chapter provides a fictional model and review process; no repository, cloud identity, production deployment or security test was executed while authoring.
