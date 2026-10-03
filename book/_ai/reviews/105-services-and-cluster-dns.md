# Independent review — Chapter 105

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 9a615fea57762896706a50517538c235f304d2bc15ca1ea47ef6589858a2d8f8

## Findings

No unresolved findings. Fresh scoped re-review confirms the EndpointSlice controller is named correctly; the diagnostic Pod sequence waits for Ready with a 60-second timeout and explains inspecting Pod/events on timeout before diagnosing DNS; the Service port-forward explicitly pins kind-dispatchdesk/production. Approval remains appropriate. Other reviewed behavior and nonexecution limitations remain unchanged.

## Inspection and dated primary evidence

Read complete current Chapter 105, its SKELETON brief and summary, previously read authoring guide and the corrected Chapter 104 prerequisite/finding resolutions. Chapter 102 context and local-runtime setup were independently reviewed earlier. Selector/EndpointSlice, DNS/discovery and broken-backend diagnosis satisfy the assigned sections. Exercises have appropriate answers and diagnostic recovery requires verification from the affected client path. Summary accurately describes examples and nonexecution; chapter-number mentions are context references rather than all being clickable links.

Freshly retrieved [kubectl wait](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_wait/) on 2026-10-04, confirming condition=Ready, pod/name and bounded timeout syntax. This follow-up inspected the corrected passages; earlier complete-body source review below remains applicable.

Retrieved official documentation on 2026-10-04:

- [Services](https://kubernetes.io/docs/concepts/services-networking/service/) supports selectors, named targetPort resolution, default TCP/targetPort, Service types, selectorless manually managed backends and Endpoints deprecation from v1.33.
- [EndpointSlices](https://kubernetes.io/docs/concepts/services-networking/endpoint-slices/) supports per-Service label inventory, multiple slices and ready/serving/terminating conditions. Normal readiness discussion is sound; special publishNotReadyAddresses/terminating routing policies are outside this minimal example.
- [Service and Pod DNS](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/) supports namespace/search suffix names, configured cluster domains, regular versus headless answers and named-port SRV records. The hard-coded cluster.local diagnostic is scoped to a normal local lab while prose explicitly warns other domains differ.
- [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/) supports layered selector/port/endpoint/DNS/client-path diagnosis and separating name resolution from working traffic.
- [kubectl run](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_run/) and [kubectl exec](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_exec/) support the named standalone diagnostic Pod, Never policy, --command -- sleep 300 and exec -- nslookup forms. Port-forward mechanics were checked against official generated reference in Chapter 103's same-date review.

The Service YAML matches Chapter 104's two labels, namespace and named http/TCP port 8080; port 80 maps correctly. Selector lists are conjunctions. get endpointslices uses the correct service-name label and includes every returned slice; YAML output exposes conditions. All executable mutation/debug/cleanup blocks pin kind-dispatchdesk/production. Working-directory assumption is repository root with service.yaml saved there; prepared binaries, existing local cluster/namespace and applied Deployment are required. BusyBox is explicitly a mutable illustrative tag, not fabricated immutable provenance; no exact image bytes/availability are claimed. run creates a Pod; exec runs a read-only DNS utility inside it; delete removes the temporary Pod; Service deletion is conditional on lab ownership and its discovery/address effect is identified. DNS environment-variable creation order, TCP connection persistence, headless/ExternalName behavior and Service tunneling's bypass of normal routing are sound. Ubuntu/Fedora/RHEL prepared clients use identical kubectl API semantics; no host distro-specific package/unit/security changes occur.

## Validation and limits

`python tools/check_book.py --chapters 105-105` passed on 2026-10-04: one draft chapter, one YAML parsing check, four shell syntax blocks, 1,355 global local-link checks; no errors or warnings. Parsing is not API schema/admission validation. No cluster/API query, namespace/Service/Deployment/Pod creation/deletion, image pull, exec, DNS/network request, port-forward, policy change or recovery operation was executed. No installed versions, actual CoreDNS/domain/CNI/Service routing, endpoint readiness, credentials/RBAC, image availability or Ubuntu/Fedora/RHEL runtime matrix were verified. Retrieved official sources support documented semantics rather than live evidence; no exhaustive external-link audit occurred. Only separate review records for Chapters 104/105 were updated/written.

Verdict: approved
