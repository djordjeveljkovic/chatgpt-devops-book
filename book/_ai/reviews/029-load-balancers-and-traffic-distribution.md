# Independent review — Chapter 29

Reviewer: review_volume3_026_030
Date: 2026-10-03
Reviewed body SHA256: af8d9b0a6168a36b2e83d771b98caeb7632208e36687de061c492d2d3996e2aa

## Findings and repair verification

No unresolved material finding. Re-reviewed the complete current body after repair on 2026-10-03. DSR now explicitly uses asymmetric request/response paths and describes VIP source identity, neighbor/ARP handling, direct client return route and policy validation. The configuration explanation distinguishes backend connection setup from client/server inactivity timers and an independent overall application/client deadline. Both previous material findings are resolved.

Re-review evidence: compared corrected claims with the previously inspected HAProxy 3.2 manual and Red Hat direct-routing documentation, whose semantics support these corrections. No configuration directives changed. HAProxy remains unavailable, so documentation review does not establish a parser or live balancing result.

## Inspection and evidence

Read the complete manuscript, its brief/manifest/summary, prerequisite Chapter 28 and HTTP summary. Checked L4 connection assignment versus L7 request behavior, persistence and unequal workload, readiness dependencies, hysteresis, idempotent outcome reconciliation, algorithm tradeoffs, readiness 404 diagnosis and recovery. The exercises include guidance and a concise takeaway. HAProxy version assumption is explicitly 3.2; no current-version claim or measured execution is invented.

On 2026-10-03 inspected [HAProxy 3.2 configuration manual](https://docs.haproxy.org/3.2/configuration.html) (page identifies 3.2.25), including health request syntax, expect status, server check thresholds and connect/client/server timers. The manual defines client/server timers as inactivity limits. Inspected [Red Hat direct routing explanation](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/7/html/load_balancer_administration/s1-lvs-direct-vsa) for DSR packet flow and ARP/VIP requirements; this historical RHEL 7 source is used for the stable mechanism, not a recommendation of that OS release.

## Verification and limits

Reviewer ran `python tools/check_book.py --chapters 26-30` on 2026-10-03: five manuscript checks, 17 shell syntax blocks, 1,304 global local-link checks; no errors or warnings. This validates syntax and local references, not operational semantics. External documentation retrieval is evidence only for the sources explicitly listed above, not an exhaustive external-link availability check. No host firewall, SSH daemon, remote system, NAT state, provider, load-balancer listener or production traffic was changed. HAProxy, UFW, firewalld, conntrack and MTR are unavailable in this environment; no HAProxy parser run, live SSH/tunnel, connection exhaustion, capture or distro matrix execution is claimed. Manuscripts/summaries/shared state were not edited by this reviewer.

Verdict: approved
