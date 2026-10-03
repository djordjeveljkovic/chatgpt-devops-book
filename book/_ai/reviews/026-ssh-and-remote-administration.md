# Independent review — Chapter 26

Reviewer: review_volume3_026_030
Date: 2026-10-03
Reviewed body SHA256: 588a743406d2a4b79cabf4e8cbf24288d069346e120f14ec28ca2cc434237950

## Findings and repair verification

No unresolved material finding. Re-reviewed the complete current body after repair on 2026-10-03. The remote status example now uses GNU timeout with explicit TERM/KILL intervals, preserves the command status, explains 124/137 ambiguity, and states that a disconnected local client does not prove remote cancellation. The separate bastion profile makes jump-host identity/trust/timeout settings explicit. Both prior findings are resolved.

Re-review evidence: inspected [GNU timeout documentation](https://www.gnu.org/s/coreutils/manual/html_node/timeout-invocation.html) and installed GNU coreutils 9.11 help. Parsed both exact host profiles using isolated `ssh -F <temporary-file> -G <profile>` on OpenSSH 10.5p1: both exit 0, correct hosts, identity paths, strict checking, agent policy and timeout; destination selects the bastion alias. Exercised the exact status-capture branch with its remote invocation replaced by local exits 0 and 3: printed statuses 0 and 3. This is shell-control-flow evidence, not remote SSH or deadline execution. No remote connection or state change was made.

## Inspection and evidence

Read the complete manuscript, its brief/manifest/summary, prerequisite Chapter 25 summary, routing/transport summaries and the guide. Identity verification, key/passphrase distinction, agent-signing exposure, loopback forwarding, multiplexing lifecycle, atomic configuration changes and rotation recovery are substantively sound. Exercises include answer guidance and a closing takeaway. Relevant Ubuntu/Fedora/RHEL package distinctions are present; no exact current server-release claim is made.

On 2026-10-03 inspected [OpenSSH ssh manual](https://man.openbsd.org/ssh), [client configuration](https://man.openbsd.org/ssh_config) and [key generation](https://man.openbsd.org/ssh-keygen). These confirm `-G`, `-T`, `-N`, local forwarding, first-value configuration behavior, ProxyJump isolation and ConnectTimeout scope. On installed OpenSSH 10.5p1, parsed the exact client stanza from a temporary isolated configuration with `ssh -F <file> -G dispatchdesk-prod`: exit 0 and expected user, destination, identity, proxy, agent policy, strict host checking and timeout observed. No connection made.

## Verification and limits

Reviewer ran `python tools/check_book.py --chapters 26-30` on 2026-10-03: five manuscript checks, 17 shell syntax blocks, 1,304 global local-link checks; no errors or warnings. This validates syntax and local references, not operational semantics. External documentation retrieval is evidence only for the sources explicitly listed above, not an exhaustive external-link availability check. No host firewall, SSH daemon, remote system, NAT state, provider, load-balancer listener or production traffic was changed. HAProxy, UFW, firewalld, conntrack and MTR are unavailable in this environment; no HAProxy parser run, live SSH/tunnel, connection exhaustion, capture or distro matrix execution is claimed. Manuscripts/summaries/shared state were not edited by this reviewer.

Verdict: approved
