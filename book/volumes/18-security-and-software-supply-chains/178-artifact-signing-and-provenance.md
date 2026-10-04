---
book: The Complete DevOps Engineering Book
volume: 18
volume_title: "Security and Software Supply Chains"
chapter: 178
title: "Artifact Signing and Provenance"
slug: artifact-signing-and-provenance
status: complete
summary: ../../_ai/chapter-summaries/178-artifact-signing-and-provenance.md
---

# Chapter 178 — Artifact Signing and Provenance

**Section outline:** distinguish signatures from attestations and provenance; sign and verify an immutable container image with Cosign; apply a deployment policy to signer identity and build evidence.

## Why this matters

DispatchDesk builds a container image in CI, pushes it to a registry, and deploys it to Kubernetes. A compromised developer account pushes a modified image under the familiar `stable` tag. The deployment controller pulls the tag later and runs the attacker's image. Vulnerability scanning and an SBOM may describe packages in that image, but neither establishes who authorized it or how it was built. A cryptographic signature can bind an authorized identity to an exact digest; a provenance attestation can describe the source and build process behind that digest.

These controls answer separate questions. A digest identifies bytes. A signature lets a verifier check that a signer approved a statement bound to those bytes. An attestation carries structured claims, such as build inputs and builder identity. Provenance is a type of attestation that describes where, when and how an artifact was produced. A verifier still has to decide which signer, claims and build process satisfy its policy. Cryptographic validity alone does not mean the signer was authorized, the source was reviewed, or the artifact is safe.

This chapter builds on short-lived workload identity in [Chapter 176](176-federation-oidc-and-short-lived-identity.md) and SBOM evidence in [Chapter 177](177-vulnerability-scanning-and-sboms.md). It follows a release from a build job through signature, provenance verification and deployment admission.

## Signatures, attestations and trust roots

A signature is a cryptographic check over a payload. In container signing, the payload includes the image digest, so a signature for one image digest does not authenticate a different image with the same mutable tag. Signatures may use a managed private key, a hardware or cloud key service, or keyless signing in which a CI job obtains a short-lived signing certificate through OpenID Connect. A keyless signature still has a trust model: the verifier checks the certificate chain and the signing identity and issuer against expected values.

In the Sigstore model, the CI job uses an OIDC identity to obtain an ephemeral certificate, signs the digest, and publishes signature material and a transparency-log entry. The private signing key is short-lived. The verifier trusts configured certificate roots and checks the identity and issuer from the certificate. A public log can make the signed event auditable, but it does not decide whether the identity is allowed to release this service. A broad rule such as “any identity from this CI provider” may accept unrelated projects or personal workflows.

An attestation is a signed statement about a subject. Its envelope binds a predicate and predicate type to one or more subject digests. For example, a provenance predicate might identify the source revision, build definition, builder and invocation. An SBOM attestation might identify packages discovered in the image. The signature protects the statement from undetected alteration; it does not make every claim true. The verifier must establish that the attestation subject equals the artifact digest being deployed and that the signer is trusted to make those claims.

Trust roots are the keys, certificate authorities, identity providers and policy rules that determine what signatures a system accepts. Keep the allowed signer narrow and explicit: expected OIDC issuer, repository or project, workflow identity, protected ref or environment, and permitted builder. Review changes to that policy like changes to production access. A signed image from an unexpected workflow is still untrusted for deployment.

Signatures and attestations can be removed or omitted while an attacker or registry operator controls distribution. Verification therefore needs a defined failure behavior: if a required signature or attestation is missing, invalid, expired under local policy, bound to another digest, or issued by an untrusted identity, do not deploy the artifact. Preserve access to signature and attestation storage during registry migration, replication and disaster recovery. Availability is an operational dependency of a fail-closed deployment policy.

## Cosign and provenance verification

The examples target the Cosign 3.1 CLI family and SLSA v1 predicate selector documented on 2026-10-04; pin the exact reviewed Cosign release and checksum in CI, then confirm the selector against that release's CLI reference before upgrading. The commands run in the protected release job after image publication. The runner needs the Cosign executable, a writable `evidence/` directory, an OIDC token from its configured workload-identity integration, network access to the registry and Sigstore services, registry permission to read the image and publish signature/attestation references, and the workflow's configured signing identity. The placeholder digest below must be replaced with the platform manifest digest from the build output. A mutable tag is useful for humans, but the signature and deployment decision should refer to the digest.

```bash
IMAGE_REF='registry.example/dispatchdesk-api@sha256:<platform-manifest-digest>'

# Keyless signing obtains a short-lived certificate from the CI job's OIDC identity.
mkdir -p evidence
cosign sign --yes "$IMAGE_REF"

# Verify the signature from the one authorized release workflow identity.
cosign verify "$IMAGE_REF" \
  --certificate-identity='https://github.com/acme/dispatchdesk/.github/workflows/release.yml@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com'
```

The signing command may prompt for OIDC authorization depending on the execution environment; a CI job normally receives identity through its configured workload identity integration. It also needs permission to read and attach signature material in the registry and to access the Sigstore services it uses. Never broaden verification to a regular expression that accepts every issuer or identity merely to make a failed release pass. For a private key or KMS-backed workflow, verification should instead pin the expected public key or trusted KMS identity, and the signing key should be protected and rotated under the organization’s key policy.

Provenance is useful only when it can be connected to an independently trusted build. A trusted builder should record the image digest as the subject, the source repository and immutable revision, the build definition and relevant parameters, and the builder identity. It should avoid embedding credentials, secret values or sensitive environment data in public predicates. A producer may generate a provenance predicate and pass it to Cosign for signing; the exact predicate schema and builder integration should be pinned and validated as part of the CI design. Do not hand-author a claim that a trusted managed builder is expected to produce.

After the builder has attached an in-toto/SLSA provenance attestation, a verifier can inspect it:

```bash
cosign verify-attestation "$IMAGE_REF" \
  --type slsaprovenance1 \
  --certificate-identity='https://github.com/acme/dispatchdesk/.github/workflows/release.yml@refs/heads/main' \
  --certificate-oidc-issuer='https://token.actions.githubusercontent.com' \
  > evidence/verified-attestations.json
```

The `--type` filter selects the SLSA provenance predicate family; use the exact supported type for the producer and pinned Cosign version (`slsaprovenance1` is the Cosign selector for SLSA provenance v1). `--yes` skips Cosign's confirmation prompt in this already protected automated job; it does not supply OIDC identity or bypass verification. A workstation operator should omit it unless the local authorization process explicitly requires non-interactive confirmation. Successful cryptographic verification only establishes that a trusted identity signed an attestation bound to the image according to the verifier’s checks. The deployment policy must also validate the attestation predicate contents. Check the subject digest, source repository and revision, approved builder identity, build definition or workflow, and required parameters. Reject an attestation that names a different subject, an unapproved source, an unprotected branch or a builder outside the approved set. If the image lacks the required attestation, treat that as a policy failure rather than silently falling back to signature-only acceptance. A nonzero exit or missing output is a failed gate; preserve the error and investigate digest, identity, issuer, predicate selector, registry access, OIDC configuration and tool version before retrying.

SLSA provenance describes a build’s origin and process; a higher assurance level depends on how the builder protects and generates that information. A signed statement from a compromised build job can faithfully preserve a malicious build. Provenance does not prove that source code is benign, every dependency is safe, tests were meaningful, or the runtime environment is uncompromised. Pair it with source review, isolated and hardened build workers, dependency controls, scanning and deployment policy. Store the artifact digest, signature bundle or registry reference, attestation, builder logs and policy decision as release evidence.

## Verify an artifact before deployment

The application team initially verifies signatures in a release script, but developers can bypass that script by applying a manifest directly to the cluster. Verification must happen at the boundary that controls deployment, such as a cluster admission policy or a protected deployment service, and apply to the resolved image digest. CI verification catches problems early; admission verification prevents a different client from bypassing the release path.

Define a policy with explicit outcomes:

1. Resolve tags to immutable digests before promotion. Record the selected platform digest for the cluster architecture.
2. Require a valid signature for that exact digest from the release workflow’s allowed identity and issuer.
3. Require a signed provenance attestation from the trusted builder and validate its predicate type, subject, source, revision and build identity.
4. Require the matching SBOM and vulnerability policy result where the release process depends on them; bind those documents to the same digest.
5. Deny admission when required evidence is absent, malformed, unverifiable or outside policy. Emit a decision record with digest, signer, attestation identity, policy version and reason.

Roll out enforcement in stages. First audit current images and discover all legitimate builders, repositories, registry mirrors, signing identities and exceptions. Resolve missing evidence by fixing the build path, not by granting a wildcard identity. Add policy in a nonblocking audit mode, then enforce for a test namespace and a canary workload. Test both accepted and rejected artifacts, including missing signatures, wrong signer, wrong issuer, wrong subject digest, stale or absent provenance, registry unavailability and multi-architecture images. Confirm that a rejected rollout leaves the last healthy workload running and that incident responders can retrieve evidence.

When verification fails, do not rebuild or retag the artifact just to make the check green. Compare the deployed digest with the release record, inspect the verifier output and policy version, confirm the expected OIDC identity and issuer, and check registry evidence availability. A failed signature may mean the artifact changed, the wrong identity signed it, the signature is unavailable, or verification roots/policy are misconfigured. Preserve the failure evidence, repair the cause, then verify the same digest again or create and verify a new release through the normal build path.

For DispatchDesk, admission denies the unexpected `stable` image because its signer is not the protected release workflow and the expected provenance is absent. The incident responder compares the registry digest with the release ledger, quarantines the untrusted digest, and restores the previously verified digest. The build team confirms the compromised account published a tag but could not run the protected workflow. They rotate affected credentials, investigate repository and registry audit records, rebuild from the reviewed commit on the isolated builder, scan the image, produce fresh SBOM and provenance evidence, and promote only after signature and policy checks pass. The trusted signature does not erase the incident; it narrows which artifact the cluster accepts while the team determines the compromise scope.

Exercises:

1. Two images use the same repository and tag at different times. What property lets verification prove the signature applies to the image your cluster will run?
2. A valid signature comes from the correct CI provider but an unrelated repository workflow. Which trust policy checks should reject it?
3. Provenance says the image was built from the expected commit, but the build worker was compromised. What does the attestation establish, and what additional evidence or controls are needed?
4. A signature verifies but the required provenance is missing. Should an admission controller allow the deployment? Explain how the result changes during an explicitly approved recovery exception, if any.

Answer guidance: verify the immutable manifest digest, not only a tag; constrain both OIDC issuer and exact workflow identity or equivalent project/ref claims; provenance records signed claims from a builder, whose trust and integrity still need assessment; required evidence remains a fail-closed policy condition. Any emergency exception should be narrow, approved, logged, time-bounded, and backed by compensating controls and a recovery plan.

Review questions:

- What does signature verification establish about an artifact, and what does it leave to policy?
- How do signatures, attestations, SBOMs and provenance differ?
- Which identity and predicate fields should a deployment gate validate?
- Why should required evidence fail closed, and how can the deployment path recover safely?

Takeaways:

- Sign and verify immutable artifact digests so tags cannot change the object under review.
- Trust a specific signer identity, issuer and builder under an explicit, version-controlled policy.
- Validate attestation subject and provenance claims; a valid signature does not make those claims sufficient or the artifact safe.
- Enforce verification at deployment admission, test rejection and recovery behavior, and retain evidence with each release decision.

## Sources checked 2026-10-04

- [Cosign container signing](https://docs.sigstore.dev/cosign/signing/signing_with_containers/) — keyless signing, key-backed signing and attaching image attestations.
- [Cosign signature verification](https://docs.sigstore.dev/cosign/verifying/verify/) — identity and issuer verification, digest claims and attestation verification.
- [Cosign in-toto attestations](https://docs.sigstore.dev/cosign/verifying/attestation/) — signed predicates and policy validation.
- [Cosign `verify-attestation` CLI reference](https://github.com/sigstore/cosign/blob/main/doc/cosign_verify-attestation.md) — predicate-type selector values and command flags.
- [SLSA provenance](https://slsa.dev/spec/v1.2/provenance) — provenance purpose and build/source origin.

Commands are documentation examples; no image was built, signed, published, admitted, or deployed. Replace the illustrative repository, digest and workflow identity with values from the actual CI identity configuration. The exact CLI integration and admission-policy behavior depend on the pinned Cosign and controller versions.
