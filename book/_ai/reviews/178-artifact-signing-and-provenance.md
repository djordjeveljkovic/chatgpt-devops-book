# Independent review — Chapter 178

Reviewer: write_volume7_061_070
Date: 2026-10-04
Reviewed body SHA256: 3a5405a00584035cdb3bbe78e818e68471f57c7a547f877ef98a30e8bd6ec682

## Fresh review and resolved findings

Approved corrected body after fresh review. The SLSA attestation command now explicitly selects `--type slsaprovenance1`, corresponding to the SLSA provenance v1 predicate family. It preserves subject checks and exact identity/issuer constraints rather than bypassing validation. The chapter states a Cosign 3.1 family assumption, requires an exact reviewed/checksummed CI release, and identifies protected-job identity, OIDC, registry/Sigstore connectivity and permissions. It creates `evidence/` before output redirection and requires it to be writable. `cosign sign --yes` is explained as confirmation suppression, not identity provision or verification bypass; interactive versus automated authorization is distinguished. Nonzero exit/missing evidence remains a failed gate with diagnosis.

The original high predicate-filter finding and medium execution/version-prerequisite finding are resolved. The summary now lists source dates, repaired assumptions and unperformed runtime checks; its request for fresh review is accurate author handoff, to be updated by the coordinator after this review. Existing signer-policy, provenance/build integrity, deployment boundary, immutable digest, multi-platform and recovery reasoning remains sound. No remaining material finding.

## Primary verification 2026-10-04

- [Cosign v3.1.0 release](https://github.com/sigstore/cosign/releases/tag/v3.1.0) confirms the named version family exists; it is an assumption rather than an unsupported claim of latest release.
- [Cosign predicate source](https://raw.githubusercontent.com/sigstore/cosign/main/cmd/cosign/cli/options/predicate.go) confirms `slsaprovenance1` maps to the SLSA v1 predicate and the default is custom.
- [Cosign attestation verifier](https://raw.githubusercontent.com/sigstore/cosign/main/cmd/cosign/cli/verify/verify_attestation.go) confirms filtering and no-match failure; [signing documentation](https://docs.sigstore.dev/cosign/signing/signing_with_containers/) and verification references support identity and digest behavior.
- Direct v3.1.0-tagged source/manual retrieval returned web-tool cache-miss errors. Exact packaged 3.1 binary behavior was not executed; reviewed CLI semantics rest on official current source/documentation and the explicit instruction to validate the pinned version. This retrieval limitation is retained rather than claiming an executed 3.1 compatibility check.

## Validation and limits

Fresh `python3 tools/check_book.py --chapters 178-179` passed 2 draft records, 3 shell syntax checks, 2 JSON parses and 1,482 local links; no errors/warnings. Focused whitespace check was clean. JSON input/record alignment and Rego rule behavior reviewed manually; OPA executable was not available. No Cosign signing/verification, OIDC authorization, registry publication, OPA eval/test, admission service, cluster or audit environment was exercised. Static checks do not establish runtime/schema/predicate/controller behavior. Only these two separate review records changed; Chapter 180 review/body left untouched.

Verdict: approved
