# Independent review — Chapter 64

Reviewer: review_volume3_021_025 (independent Volume 7 assignment)
Date: 2026-10-04
Reviewed body SHA256: c4b5763d1f72ab542e3778564a036c627274f7510f8e1de8a07051ff1dcd965e

## Scope and findings

Read AI_AUTHORING_GUIDE.md, chapter brief, manuscript and compact summary, and prerequisite/canonical context in Chapters 60, 47 and preceding assigned chapters. Reviewed exact examples, version claims, distro boundaries, rootless identity/storage, safety, recovery evidence, prose, local links and required exercises/guidance/takeaways. Quadlet configuration is deferred to Chapter 66 and is outside this five-chapter review.

Checked Netavark/Aardvark versus standalone pasta and named rootless bridge forwarding, version caveats, network DNS alias/membership, loopback publication versus container port, IPv4/IPv6 distinction, host.containers.internal limitations, proxy scheme errors, source-IP trust, backend migration/recreation and network removal scope. Stable documentation confirms pasta default but the chapter properly avoids claiming distro equivalence. Both diagnostic paths use bounded application probes. Assessment guidance/takeaways are complete. No material findings.

## Primary-source evidence

Official upstream stable documentation inspected during this review (2026-10-03–04):

- [podman-run.1.html](https://docs.podman.io/en/stable/markdown/podman-run.1.html).
- [podman-network-create.1.html](https://docs.podman.io/en/stable/markdown/podman-network-create.1.html).

## Verification and limits

`python3 tools/check_book.py --chapters 61-65` passed: 23 shell syntax checks, 1 YAML parse and 1,333 global local links; no errors or warnings. These establish syntax/local linkage, not Podman runtime, Kubernetes API validation or registry image content.

Attempted local `podman --version` and `podman --remote=false info`: both failed during configuration initialization with `mkdir /run/user/1001/libpod: read-only file system`. No engine version or working namespace/runtime can be inferred from that attempt. The authoring baseline reports 6.1.2; this review independently verified stable documented semantics, not execution on that version. No image pull, container/pod creation, ownership/relabel mutation, network allocation, kube playback, runtime HTTP exchange, systemd activation, package install or live restore performed. Ubuntu 24.04/Fedora 44/RHEL 9/10 VM matrix remains untested.

Summaries accurately retain draft status and unperformed runtime checks; they do not claim executed deployments. Optional low findings do not block approval.

Verdict: approved
