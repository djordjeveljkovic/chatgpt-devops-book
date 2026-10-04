# Independent review — Chapter 112

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 359c6c7e28f8cd4392f855c605704a8516cad09932efe6a82884927dd0e9b966

## Findings

No material findings. The earlier universal disjoint node/Pod CIDR claim is resolved: the current body explicitly allows provider-integrated Pod IP allocation from node VPC subnets and distinguishes separate overlay/routed Pod CIDRs. Avoiding conflicting addresses and ambiguous interconnected routes remains correctly required.

Low optional prose correction: in “Diagnosing cross-node packet paths,” the paragraph after the commands calls `kube-system` a label. It is the namespace passed by the command. CNI agents may also live elsewhere; the paragraph already correctly requires discovering the installed implementation rather than guessing an agent name. This wording does not change the read command's behavior.

## Scope and dated primary evidence

Read current complete body, summary, SKELETON brief and relevant prerequisites, applying the authoring guide. The brief's Pod routing/network implementation, policy/reachability and cross-node packet-path coverage is complete. Exercises contain concrete answer guidance; the failure scenario distinguishes placement-dependent network evidence from restarting application processes and gives layer-specific recovery and post-change verification. The summary agrees with the manuscript's scope and lack of runtime validation.

Primary sources inspected on 2026-10-04:

- [Kubernetes network model](https://kubernetes.io/docs/concepts/cluster-administration/networking/) and [network plugins](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/) support shared Pod networking, Pod reachability and implementation-specific routing/CNI dependencies.
- [Amazon VPC CNI](https://docs.aws.amazon.com/eks/latest/userguide/managing-vpc-cni.html) documents node-attached network interfaces and VPC private addresses assigned to Pods; supports the corrected provider-integrated address allocation qualification.
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) supports required implementation enforcement, independent ingress/egress isolation, additive rules, AND within a combined peer and OR between peers. DNS egress, source-address translation and special host paths require deployment-specific testing; the body explicitly calls for that testing rather than promising universal implementation behavior.
- [Services](https://kubernetes.io/docs/concepts/services-networking/service/) and [virtual IPs/service proxies](https://kubernetes.io/docs/reference/networking/virtual-ips/) support separating virtual Service routing from endpoint membership and raw Pod connectivity, including alternative proxy implementations and headless discovery.

The five kubectl reads are syntactically sound: namespaced Pods/policies, cluster-scoped Nodes, EndpointSlices selected by the standard service-name label, and system Pods in kube-system. Explicit context is consistent throughout. No mutation, packet capture or privileged host command is presented as an observational API read. Readiness and endpoint membership are correctly insufficient proof of delivery. Output sensitivity, approved diagnostic images, temporary-Pod cleanup and capture privileges are discussed. Linux/CNI differences are delegated to the selected implementation's supported instructions; no distribution-specific host configuration commands are supplied. MTU, dual-stack and address-capacity claims are appropriately conditional rather than asserted as measured results.

## Validation and limits

`python tools/check_book.py --chapters 111-112` passed on 2026-10-04: two draft chapters, two shell syntax blocks and 1,376 global local-link checks; no errors/warnings. Body hash freshly computed using tools.promote_reviewed.body_hash after the live CIDR correction. No Kubernetes API calls, diagnostic Pods, network-policy changes, CNI installation, node routes/firewall changes, captures or traffic tests occurred. No installed plugin/version, Ubuntu/Fedora/RHEL matrix, actual policy enforcement, cross-node reachability, source NAT, MTU, dual-stack routing or address exhaustion was validated. Official documentation and static command inspection establish conceptual behavior, not live networking or exhaustive external-link checking. Only this review record was written.

Verdict: approved
