# Independent review — Chapter 28

Reviewer: review_volume3_026_030
Date: 2026-10-03
Reviewed body SHA256: 9b3d4a7f033765272b4d97ca966b098587cea29419c2b7bfead81fc45a6eeed7

## Findings

No unresolved material finding.

- Low — manuscript line 50, package prerequisites: clarify the distribution package name rather than naming only the upstream suite. Ubuntu packages the CLI as `conntrack`; Fedora packages it as `conntrack-tools`. The existing “where available” wording does not assert a wrong installation command, but exact names improve novice reproducibility. RHEL should retain release/repository/entitlement caveats.

## Inspection and evidence

Read the complete manuscript, its brief/manifest/summary and prerequisite Chapter 27, plus transport/routing summaries. Checked original/translated tuple reasoning, reply-path state, masquerade, NAT security limitations, independent proxy legs, forwarded-header trust, aggregate conntrack counters, namespace/module absence, local versus gateway source-port allocation, TIME-WAIT interpretation, retry containment and measured recovery. Exercises have answer guidance and the takeaway states the operational decision. No destructive rules, flush or limit mutations are prescribed.

On 2026-10-03 inspected [nftables NAT documentation](https://wiki.nftables.org/wiki-nftables/index.php/Performing_Network_Address_Translation_(NAT)), [conntrack-tools manual](https://conntrack-tools.netfilter.org/manual.html), [Linux conntrack sysctls](https://docs.kernel.org/networking/nf_conntrack-sysctl.html), [RFC 7239](https://www.rfc-editor.org/rfc/rfc7239.html), [Ubuntu package index](https://packages.ubuntu.com/conntrack) and [Fedora package record](https://packages.fedoraproject.org/pkgs/conntrack-tools/conntrack-tools/). Documentation supports translation-state behavior, module-dependent counters and untrusted forwarded metadata. Package indexes establish the optional naming clarification. No claim of provider-specific limits or live exhaustion is made.

## Verification and limits

Reviewer ran `python tools/check_book.py --chapters 26-30` on 2026-10-03: five manuscript checks, 16 shell syntax blocks, 1,294 global local-link checks; no errors or warnings. This validates syntax and local references, not operational semantics. External documentation retrieval is evidence only for the sources explicitly listed above, not an exhaustive external-link availability check. No host firewall, SSH daemon, remote system, NAT state, provider, load-balancer listener or production traffic was changed. HAProxy, UFW, firewalld, conntrack and MTR are unavailable in this environment; no HAProxy parser run, live SSH/tunnel, connection exhaustion, capture or distro matrix execution is claimed. Manuscripts/summaries/shared state were not edited by this reviewer.

Verdict: approved
