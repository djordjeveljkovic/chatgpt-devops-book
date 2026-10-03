# Independent review — Chapter 27

Reviewer: review_volume3_026_030
Date: 2026-10-03
Reviewed body SHA256: e97536173fe7b71e30e2160f7ee1816a90c4c11bd123c1c244a9abf66ba0ce4b

## Findings and repair verification

No unresolved material finding. Re-reviewed the complete current body after repair on 2026-10-03. The setup records initial allowance state and cleanup is separated until after an independent session test, conditionally removing only initially absent test permission. Prose restricts this service-level example to an appropriate disposable host, explains zone-wide scope versus source-scoped rich rules, and requires checking current change ownership before cleanup. The prior existing-allowance removal finding is resolved.

Re-review evidence: exercised both exact setup/cleanup shell blocks with a shell-only mock of sudo/firewall-cmd for initially enabled and initially absent SSH service states. Initially enabled policy remained enabled with no add/remove call; initially absent policy was added and then removed. This validates branch behavior only; no firewall daemon, privilege escalation, packet path or SSH session was exercised. Previously inspected firewalld primary documentation supplies the real command semantics.

## Inspection and evidence

Read the complete manuscript, its brief/manifest/summary and prerequisite Chapter 26, plus transport/routing summaries. Rule ownership, layers, state tracking, default denial, UFW source filtering, runtime/permanent distinction, network namespaces, diagnostic return paths and recovery verification are sound. Exercises and review-question guidance are present. Ubuntu versus Fedora/RHEL manager differences are explicit. Timed recovery is a planning requirement rather than an executed recipe.

On 2026-10-03 inspected [Ubuntu firewall documentation](https://ubuntu.com/server/docs/how-to/security/firewalls/), [firewalld firewall-cmd manual](https://firewalld.org/documentation/man-pages/firewall-cmd.html), and [nftables NAT documentation](https://wiki.nftables.org/wiki-nftables/index.php/Performing_Network_Address_Translation_(NAT)). firewalld documents add/remove/query service operations, successful treatment of already-enabled additions, and runtime/permanent separation. Those semantics established the initial-state restoration finding, now resolved as described above, without changing live rules.

## Verification and limits

Reviewer ran `python tools/check_book.py --chapters 26-30` on 2026-10-03: five manuscript checks, 17 shell syntax blocks, 1,304 global local-link checks; no errors or warnings. This validates syntax and local references, not operational semantics. External documentation retrieval is evidence only for the sources explicitly listed above, not an exhaustive external-link availability check. No host firewall, SSH daemon, remote system, NAT state, provider, load-balancer listener or production traffic was changed. HAProxy, UFW, firewalld, conntrack and MTR are unavailable in this environment; no HAProxy parser run, live SSH/tunnel, connection exhaustion, capture or distro matrix execution is claimed. Manuscripts/summaries/shared state were not edited by this reviewer.

Verdict: approved
