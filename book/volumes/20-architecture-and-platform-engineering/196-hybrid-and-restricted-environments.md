---
book: The Complete DevOps Engineering Book
volume: 20
volume_title: "Architecture and Platform Engineering"
chapter: 196
title: "Hybrid and Restricted Environments"
slug: hybrid-and-restricted-environments
status: complete
summary: ../../_ai/chapter-summaries/196-hybrid-and-restricted-environments.md
---

# Chapter 196 — Hybrid and Restricted Environments

**Section outline:** map trust, connectivity and policy boundaries across sites and clouds; design repeatable delivery for restricted networks; validate operations without pretending the boundary has disappeared.

## Map the actual boundaries

Summit is moving a payment service to managed cloud, while a regulated customer-data store must remain in a private facility. A partner operates a separate network, and its maintenance window is not under Summit's control. Calling the design “hybrid” does not explain where identity, data, artifacts, monitoring or incident authority live. Draw the trust and dependency boundaries before selecting connectivity products.

Record each workload's data classification, authoritative location, identities, administrators, permitted flows, key custody, recovery copy, update path and support owner. Separate network reachability from authorization: a private link does not make every reachable system trusted. Use explicit service identity, mutual authentication where appropriate, least privilege, segmentation, logging and expiring credentials. Chapters 079–089 cover the underlying identity and network controls.

Map control-plane dependencies too. A workload may run locally yet depend on cloud identity, license checks, package repositories, time sources, DNS or telemetry ingestion. Determine which of these must work during an external outage and what a safe degraded mode looks like. Keep the emergency access path protected, monitored and rehearsed.

## Build a delivery path that can cross the boundary safely

Restricted environments often cannot pull arbitrary internet dependencies during deployment. Build from reviewed sources in a connected zone, scan and sign the resulting artifacts, then transfer them through an approved release channel. Verify digests and signatures at the receiving boundary and retain a manifest of source revision, build identity, dependencies, approval and destination. Avoid rebuilding separately inside each enclave if doing so destroys artifact identity; if policy requires a local rebuild, preserve the inputs and attest the transformation.

Make infrastructure configuration portable only where the semantics are portable. A template can express common intent, but cloud IAM, storage consistency, network controls and managed-service behavior differ. Maintain explicit environment overlays with validated allowed differences rather than a false universal abstraction. Pin provider versions, modules and packages; mirror required sources; plan upgrades offline; and document how emergency security updates reach disconnected sites.

For a disconnected site, define update bundles, signing keys, trusted time, revocation handling, expiry and rollback limits. A signature proves that an artifact was signed by a key; it does not prove the signer was authorized for this workload or that an offline verifier has fresh revocation state. Design key custody and approval independently from transport.

## Operate the seams

Set service ownership for each link and handoff. Document network request routes, firewall rules, DNS authority, certificate renewal, MTU assumptions, proxy behavior, queue limits and failure escalation. Cross-boundary requests can fail slowly, duplicate on retry or return after the caller timed out. Use timeouts, bounded retries, idempotency and durable queues where the business contract allows them. Do not queue sensitive payloads indefinitely without retention, encryption, access and deletion rules.

Monitoring should expose both sides of a boundary without copying restricted data into an unauthorized telemetry system. Agree on event fields, redaction, retention and incident access. Use synthetic checks with safe payloads and clock-skew detection. When direct telemetry is prohibited, design a controlled evidence-export process and state its delay and blind spots.

DispatchDesk's restricted archive site receives signed application bundles once per week. The team creates an offline mirror of approved base images and language packages, attaches a signed release manifest, and uses a two-person import procedure. The site verifies the bundle and deploys it through the same reviewed configuration. A drill disconnects the site from external identity and shows that routine service remains healthy while operator elevation fails. The team adds monitored, time-limited local emergency access with sealed recovery credentials and repeats the drill. This improves a defined failure path; it does not make the site fully independent of upstream suppliers.

Before choosing a connectivity pattern, define who can initiate sessions in each direction and what happens when routing is unavailable. Private peering, VPN and dedicated links have different failure, scale, routing and support characteristics; none should become an unreviewed transitive path between environments. Test certificate expiration, name resolution and asymmetric route failure, not only a successful ping. Keep firewall rules and route intent under reviewable ownership, and alert on drift. For third-party links, record the provider escalation path and expected response time so incident command can distinguish local failure from partner delay.

Exercises:

1. A private network link is encrypted, but a shared service account can administer both environments. Which risk remains?
2. A disconnected site rejects a correctly signed emergency patch because its revocation list is six months old. What should the update and emergency policy specify?
3. A site can run applications during cloud-control-plane loss, but deployment, DNS renewal and log export stop. How should the service contract describe this state?
4. A build is repeated independently inside a restricted network and produces a different image digest. What evidence is needed before release?

Answer guidance: network privacy does not constrain a compromised or overprivileged identity; separate trust domains and admin paths. Define trusted revocation freshness, exception authority, expiry, evidence capture and subsequent reconciliation. Explicitly classify serving, deploying, name resolution and observability capabilities with degraded-service limits. Preserve reproducible inputs and record the authorized local build, toolchain, scan/signature and artifact mapping; investigate differences before promotion.

Review questions:

- Which dependencies cross site, account, provider or classification boundaries?
- How can artifacts be promoted while preserving trustworthy provenance?
- What functions must work during loss of connectivity or central control plane?
- How do you keep telemetry useful without exporting prohibited data?

Takeaways:

- Draw data, identity, network, control-plane and support boundaries explicitly.
- Private connectivity complements identity and authorization; it does not replace them.
- Use reviewed, signed artifact promotion, mirrors and documented offline update procedures.
- Test degraded modes, evidence export and emergency access with the actual restrictions in force.

## Sources checked 2026-10-04

- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final) — resource-focused access rather than implicit network trust.
- [SLSA Provenance](https://slsa.dev/spec/v1.1/provenance) — build provenance structure and artifact origin evidence.
- [Chapter 176 — Federation, OIDC and Short-lived Identity](../18-security-and-software-supply-chains/176-federation-oidc-and-short-lived-identity.md) and [Chapter 178 — Artifact Signing and Provenance](../18-security-and-software-supply-chains/178-artifact-signing-and-provenance.md) — identity and artifact controls.

Environment constraints and incident examples are fictional. No restricted environment, network link or deployment was configured.
