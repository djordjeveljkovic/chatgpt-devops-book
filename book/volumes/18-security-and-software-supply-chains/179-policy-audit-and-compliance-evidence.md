---
book: The Complete DevOps Engineering Book
volume: 18
volume_title: "Security and Software Supply Chains"
chapter: 179
title: "Policy, Audit and Compliance Evidence"
slug: policy-audit-and-compliance-evidence
status: complete
summary: ../../_ai/chapter-summaries/179-policy-audit-and-compliance-evidence.md
---

# Chapter 179 — Policy, Audit and Compliance Evidence

**Section outline:** turn security requirements into testable operational controls; collect reliable evidence through the delivery lifecycle; prepare audit evidence that is scoped, attributable and useful to engineers.

## Why this matters

DispatchDesk tells a customer that production changes require review and that every release passes security checks. During a customer assessment, the team exports a screenshot of its CI dashboard. The screenshot shows a green run, but it does not identify the deployed digest, the policy version, the reviewer, or whether the screenshot belongs to the production release. The control may work, but the evidence does not demonstrate it.

A policy states what must be true. A control is the repeatable action or safeguard used to meet that requirement. Evidence records whether the control operated for a specific scope and time. Audit asks whether that evidence supports a conclusion against defined criteria. Compliance is not a property created by a folder of documents: it depends on a working system, a defined scope, accountable owners and evidence that faithfully represents operation.

This chapter connects policy to daily DevOps work: pull request review, identity, build, image signing, deployment, monitoring and incident handling. Chapter 178 covers artifact trust and provenance. Its signatures and attestations can provide evidence for a release control, but only when the policy identifies the expected signer, builder, subject digest and decision.

## Turn requirements into operational controls

Start with a requirement that can be tested. “Protect production” is too broad to assess. A more useful control statement might be: “Every production image must be deployed by the approved pipeline, reference an immutable digest, have a valid signature from the protected release workflow, and have a recorded approval before promotion.” It names the object, required state, responsible process and evidence to inspect.

Translate each statement into a control record with these fields:

- **Requirement and scope:** source framework or contract clause, systems and data in scope, and exclusions with rationale.
- **Control owner:** role responsible for design and operation, plus a backup and escalation path.
- **Frequency and trigger:** continuous, per release, daily, quarterly or after a material change.
- **Procedure and expected result:** how the control operates and what constitutes success or failure.
- **Evidence source:** system of record, event fields, retention period and access restrictions.
- **Exception path:** approver, business reason, compensating measure, expiry date and retest trigger.

Keep the control at the level of behavior rather than a particular dashboard button. A control such as “the CI system runs a protected release workflow for every production deployment” survives a vendor interface change more readily than “the green icon is visible on page 4.” However, identify the concrete sources that prove operation: repository branch-protection event, workflow run ID, artifact digest, signature identity, deployment record and admission decision.

Map overlapping requirements to one control when the same mechanism actually satisfies them. Maintain traceability from each requirement to the control, owner, system configuration, test and evidence. Do not assume two similar-sounding clauses are identical; record their different scopes or review requirements. Framework mappings are navigation aids, not a determination that a control meets a legal obligation. Legal, privacy and contractual interpretations belong with the responsible specialists.

Policy should match technical enforcement. If a written standard requires short-lived deployment identity but a production service account still has a static key, the policy and environment disagree. Record the gap, assess exposure, assign remediation and use an approved, time-limited exception if immediate replacement is not possible. Do not silently redefine the requirement so the existing implementation appears compliant.

## OPA decisions and admission evidence

Open Policy Agent (OPA) evaluates structured input against policy written in Rego. The policy decision point and the source of each input are separate trust boundaries. If a release policy receives `signature.verified: true`, that assertion must come from a trusted signature verifier bound to the artifact digest; OPA does not turn an untrusted Boolean into cryptographic proof. Version and review the policy bundle, and test allowed and denied cases before using it in a release or admission path.

This simplified policy illustrates the decision. The release system has already verified the signature and provenance with its trusted verifier, matched their subjects to the image digest, and joined a human approval to the exact commit and digest. The policy input below is a fictional projection of those upstream records, not cryptographic evidence by itself:

```rego
package release

default allow := false

allow if {
    input.environment == "production"
    input.image_digest != ""
    input.signature.verified == true
    input.signature.identity == "release-workflow"
    input.provenance.verified == true
    input.provenance.subject_digest == input.image_digest
    input.approval.status == "approved"
    input.approval.commit == input.commit
    input.approval.artifact_digest == input.image_digest
}
```

Example `release-input.json` for OPA CLI 1.x and Rego v1 syntax:

```json
{
  "environment": "production",
  "commit": "8b7e…",
  "image_digest": "sha256:<platform-manifest-digest>",
  "signature": {"verified": true, "identity": "release-workflow", "evidence_id": "sig-231"},
  "provenance": {"verified": true, "subject_digest": "sha256:<platform-manifest-digest>", "evidence_id": "att-992"},
  "approval": {"status": "approved", "reviewer": "release-approver-id", "event_id": "scm-event-58102", "commit": "8b7e…", "artifact_digest": "sha256:<platform-manifest-digest>"}
}
```

With the policy stored in `release.rego` and this JSON in `release-input.json`, evaluate the decision locally:

```bash
opa eval --format=json --data release.rego --input release-input.json data.release.allow
```

For this illustrative input, the expected policy decision is `true`; if the approval's `artifact_digest` differs from `image_digest`, the result is `false` because the default rule denies. These are expected outcomes, not captured command output. Unit-test allowed, wrong-environment, missing-evidence, wrong-signer, subject-mismatch and stale-approval cases with `opa test` in the same pinned CI toolchain. OPA 1.x Rego v1 syntax and CLI flags are assumed; pin the exact OPA release used by CI and validate before upgrades.

This is an illustrative release-gate policy, not a complete Kubernetes admission policy. A production Rego policy must define input schemas, reject missing or malformed fields, constrain repository/ref/builder and policy versions, and be tested against negative cases. The workflow identity string is a locally assigned alias for a verified identity, not a claim from a certificate by itself. Keep cryptographic verification and policy evaluation outputs linked by the exact digest.

An OPA decision record should include a unique decision ID, timestamp, queried policy path, result, policy bundle revision, input digest, commit, environment and the upstream evidence IDs. OPA decision logs can capture policy revision and query result, but input can include sensitive information; configure redaction before forwarding or retaining logs. A release approval record should be understandable without access to a transient chat thread. For example:

```json
{
  "release_id": "dispatchdesk-prod-2026-10-04-1842",
  "environment": "production",
  "commit": "8b7e…",
  "image_digest": "sha256:<platform-manifest-digest>",
  "artifact_reference": "registry.example/dispatchdesk-api@sha256:<platform-manifest-digest>",
  "approval": {"status": "approved", "reviewer": "release-approver-id", "event_id": "scm-event-58102", "commit": "8b7e…", "artifact_digest": "sha256:<platform-manifest-digest>"},
  "signature": {"verified": true, "identity": "release-workflow", "evidence_id": "sig-231"},
  "provenance": {"verified": true, "predicate": "slsaprovenance1", "subject_digest": "sha256:<platform-manifest-digest>", "evidence_id": "att-992"},
  "policy_decision": {"result": "allow", "bundle_revision": "policy-4f82", "decision_id": "decision-7831"},
  "build": {"workflow_run_id": "workflow-8184", "builder_identity": "release-builder", "evidence_id": "build-117"},
  "deployment": {"deployment_id": "rollout-4419", "admission_event_id": "admission-4401"},
  "recorded_at": "2026-10-04T18:42:00Z"
}
```

The values are fictional and the digest placeholder is not deployable. The record links an approval to a release candidate and its evidence. The signature and provenance entries are computed assertions that must point to trusted verifier outputs; approval and workflow IDs should resolve to the source-control and CI systems of record. The policy decision and admission event are produced by their respective enforcement boundaries. A release system should make the record append-only or otherwise protect its history, retain the linked source events under policy, and capture denials as well as approvals. Do not record approval as a Boolean with no named reviewer, source event, timestamp or object under review. If evidence is missing, default deny and record the reason. A temporary recovery exception must be separately approved, narrowly scoped to a digest and environment, have an expiry, name compensating safeguards, and be visible in the release record; it should not rewrite the ordinary policy result.

Kubernetes admission provides a distinct enforcement point for API requests. A validating admission policy or webhook can allow, warn, audit or deny incoming objects according to its implementation and configuration. OPA Gatekeeper is one integration that combines admission evaluation with periodic audit of existing resources; its audit results can be exposed through metrics and constraint status. Those results are a point-in-time report, may be capped in per-object detail, and do not by themselves prove that every production rollout was admitted under the intended revision. Retain the admission decision/event with the object digest and policy version, and separately preserve periodic audit run time, scope, constraint revision, violation counts and any truncation limits.

Roll out a new admission policy in observation or warning mode where supported, compare reported violations to the intended scope, then enforce it on a small production canary. Test allowed and denied requests and the admission service's unavailable behavior; a webhook configured to fail open creates a different control than one configured to fail closed. Preserve a recovery path for a bad policy, restricted to authorized operators and fully audited. Admission examines API requests; periodic audits evaluate existing objects. Neither substitutes for an end-to-end release approval record that links reviewed source, built digest, signature/provenance, policy result and deployment.

## Collect evidence across the delivery path

Useful evidence is attributable, scoped, time-bound and protected against inappropriate change. For a production release, an evidence chain might connect a reviewed commit to an approved workflow run, a built image digest, a signed provenance statement, a policy decision and a deployment event. Stable identifiers let an auditor or responder follow the chain without trusting copied screenshots.

Prefer structured records from authoritative systems: source control review events, CI run metadata, registry digests, identity-provider claims, deployment controller events, cloud audit records, monitoring alerts and incident tickets. Capture actor or workload identity, object identifier, timestamp and timezone, result, policy version and relevant correlation ID. Preserve the record's origin and retrieval time when exporting it. A manually assembled spreadsheet may help navigate evidence, but it should point back to immutable or access-controlled source records.

Evidence quality has operational limits. Events may be delayed, sampled, truncated or retained for less time than a contract requires. A screenshot can be altered and often omits its query scope. A green CI job can test one branch while production runs another digest. A deployment log can establish that an image started but not that the image passed the required policy. State what each record proves and what it does not; combine independent sources where one source cannot establish the full control.

Protect evidence as production data. Apply role-based access, retention and deletion schedules, encryption and backup policies. Minimize secrets, personal information and customer data in audit exports. Do not copy tokens, request payloads or unrestricted production logs into a general-purpose compliance repository. Record a digest or source event identifier when useful for integrity checking, while recognizing that a hash alone does not establish who created the original evidence.

Automate collection close to the event. For each release, store the commit ID, approval record, workflow run, image digest, signature verification result, provenance subject, policy version and deployment ID. A query can then reconstruct the release record without asking engineers to remember which links to paste. For periodic controls, run a scheduled query against source systems, retain the result with its query version and record failures as owned work items. Keep the automation itself under change control and test that it fails visibly when a source is unavailable or returns incomplete data.

## Audit preparation and exceptions

Before an assessment, agree on the time window, system boundary, sample method and evidence format. Provide a short index that maps the requested control to the evidence source, query or report, owner and limitations. For sampled production releases, select records using the assessor's method or an agreed reproducible method; do not quietly hand-pick only the most successful examples. Where source-system access is appropriate, a read-only walkthrough can be clearer than a large static export.

Review evidence before sharing it. Confirm dates and timezone, production scope, actor identities, integrity and relevant retention. Remove unrelated secrets and customer data without changing the fact being assessed. Preserve the unredacted source under authorized access and record who made the export and redaction. If required evidence is missing, report the gap and recovery plan plainly. Reconstructing a record from memory and presenting it as contemporaneous evidence damages trust and may violate retention or legal obligations.

Exceptions are controlled risk decisions, not erased findings. Every exception should identify the exact system/control, reason, risk owner and approver, compensating control, start and expiry time, and event that triggers earlier review. Make expired exceptions visible to an owner. A compensating control does not automatically satisfy a contract or regulation; obtain the required organizational approval and document the accepted residual risk.

When a control fails, open a remediation item with severity, owner, due date, containment, and a verification step. Preserve original evidence and link the corrective change to it. After correction, rerun the control against the affected scope and retain the result. A single successful rerun proves only that the sampled condition passed at that point; it does not establish continuous effectiveness across an entire period.

For DispatchDesk, the team replaces the dashboard screenshot with a release evidence bundle indexed by production deployment ID. It links the reviewed commit, protected workflow run, digest, signature and provenance verification, admission decision and rollout result. The first sample exposes an older deployment that used a mutable tag and has no retained provenance. The owner records a scoped control failure, verifies the currently running digest, blocks future tag-based deployment, documents the historical evidence gap and asks the customer assurance lead whether the missing record affects a specific contractual claim. The gap is not backfilled with a fabricated build statement.

Exercises:

1. A policy says all releases receive security review. What details make this control testable, and which systems could provide evidence?
2. A CI run passed, but the cluster runs another image digest. Which control failed, and which identifiers would help identify the break in the evidence chain?
3. An auditor requests a production log containing customer identifiers and credentials. How should the team preserve evidence while limiting disclosure?
4. A required source system retained events for 30 days, but the assessment covers a quarter. What should the team report, and what control improvement prevents recurrence?

Answer guidance: define the in-scope release and review criteria, approver, trigger, failure path and authoritative event records. Connect commit, workflow, digest, approval and deployment IDs; do not infer production deployment from CI success alone. Preserve the original under restricted access, provide a scoped/redacted export and document its source and transformation. State the retention gap candidly, assess its impact, and extend or export records under an approved policy before future evidence expires.

Review questions:

- How do policy, controls, evidence and audit criteria relate?
- What properties make a release record attributable and useful?
- Why is a dashboard screenshot usually weaker than linked source-system records?
- How should a team handle a missing control, exception or evidence gap?

Takeaways:

- Translate broad requirements into scoped behaviors with owners, procedures, expected results and exception paths.
- Connect evidence through stable identifiers from reviewed change to deployed artifact and policy decision.
- Protect evidence and disclose its scope and limits; never recreate missing records as though they were captured at the time.
- Treat audit findings as engineering work with ownership, remediation and verification.

## Sources checked 2026-10-04

- [NIST SP 800-53A Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final) — control assessment procedures and evidence-based assessment context.
- [NIST glossary: audit](https://csrc.nist.gov/glossary/term/audit) — audit as a systematic, independent and documented evaluation of evidence against criteria.
- [Cosign verification](https://docs.sigstore.dev/cosign/verifying/verify/) — signature identity, digest and attestation verification concepts referenced in the release evidence chain.
- [OPA policy testing](https://www.openpolicyagent.org/docs/policy-testing) and [decision logs](https://www.openpolicyagent.org/docs/management-decision-logs) — testable Rego policy and decision-record fields, with input redaction considerations.
- [Kubernetes policy](https://kubernetes.io/docs/concepts/policy/), [admission controllers](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/) and [Gatekeeper audit](https://open-policy-agent.github.io/gatekeeper/website/docs/audit/) — admission enforcement and periodic audit evidence boundaries.

Examples describe a fictional service and do not claim certification against a particular framework, law or customer contract. Evidence sources and retention obligations must be mapped to the organization's actual scope and agreements.
