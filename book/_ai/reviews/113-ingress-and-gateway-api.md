# Independent review — Chapter 113

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 84e05200e343c49a2e9c8c59a82b42971dc38fcbcbcda09791a21cfab230752f

## Findings

No material findings. Optional low clarification in “The external request path”: name the two different cross-namespace permission mechanisms explicitly. Route-to-Gateway attachment uses listener allowedRoutes (and route parentRefs); cross-namespace backend or certificate references require ReferenceGrant in the target namespace. The current generic “explicit permission mechanisms” wording is correct and later listener-attachment discussion does not falsely imply ReferenceGrant is required for every attachment.

## Scope and dated primary evidence

Read the complete current body, summary and SKELETON brief, with authoring guide and independently reviewed Chapter 112 prerequisite. HTTP routing/controller ownership, TLS/classes/Gateway resources and publishing/migration decisions cover the ordered brief conceptually. The DispatchDesk annotation-migration failed assumption, canary request matrix, rollback and layered recovery are concrete operational examples. No runnable controller installation or publishing manifest is promised; examples are explicitly read-only diagnostics. Exercises supply answer guidance and operational review questions. Summary agrees with the content; its static-check-pending entry is administrative continuation state, not a technical claim of completed runtime testing.

Official primary evidence inspected on 2026-10-04:

- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) confirms stable but frozen API, no planned removal, recommendation of Gateway API, controller requirement and implementation-specific behavior.
- [Kubernetes Gateway API](https://kubernetes.io/docs/concepts/services-networking/gateway/) supports the add-on API/controller distinction, role-oriented infrastructure/application resources and controller-specific availability.
- [Gateway API versioning](https://gateway-api.sigs.k8s.io/docs/concepts/versioning/) and [conformance](https://gateway-api.sigs.k8s.io/docs/concepts/conformance/) support Standard/Experimental stability boundaries and feature/version-specific implementation support. The body makes no fixed controller/version compatibility promise.
- [HTTP routing](https://gateway-api.sigs.k8s.io/guides/user-guides/http-routing/) supports parent attachment, hostname/path matching and backend references.
- [TLS configuration](https://gateway-api.sigs.k8s.io/guides/user-guides/tls/) supports listener certificate references, cross-namespace ReferenceGrant permissions and distinct downstream/upstream TLS configurations. Edge handshake is correctly insufficient evidence of backend encryption or application authentication.

All seven kubectl queries are syntactically valid and explicitly context pinned. Ingress/GatewayClass reads are cluster scoped; Ingress/route/Service/EndpointSlice reads select production namespace; all-namespace Event inspection is observational and subject to authorization. Missing Gateway CRDs may fail resource discovery, as disclosed. No apply/install/delete, DNS/certificate change or opening firewall is supplied as a diagnostic shortcut. API acceptance/status is correctly separated from end-to-end DNS, listener, TLS, readiness and packet-path evidence. Broad output sensitivity and best-effort Events limits are stated. Linux and provider differences are intentionally implementation-specific; no host package commands or unsupported generic controller configuration is presented. Migration preserves old routing pending verified acceptance and rollback instead of assuming annotation equivalence.

## Validation and limits

`python tools/check_book.py --chapters 113-113` passed on 2026-10-04: one draft chapter, one shell syntax block and 1,376 global local-link checks; no errors/warnings. Exact body hash calculated using tools.promote_reviewed.body_hash. No Kubernetes API query, controller/CRD installation, route publication, provider request, DNS change, certificate operation or user traffic occurred. No selected controller/version/conformance report, OS matrix, listener isolation, TLS chain, migration behavior, live rollback or external reachability was tested. Concept documentation establishes mechanisms rather than actual deployment behavior. Two additional guessed Gateway guide URLs failed retrieval; the working official routing/TLS/versioning/conformance pages provide the evidence recorded here. External references were checked selectively, not exhaustively. Only this separate review record was written.

Verdict: approved
