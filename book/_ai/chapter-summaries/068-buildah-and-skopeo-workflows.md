# Chapter 68 — Buildah and Skopeo Workflows

Status: complete

## Written material
Building OCI images with Buildah; Inspecting and copying images with Skopeo; A registry-independent image workflow; Failure, diagnosis and recovery; Cleanup and assessment; Exercises and review questions; Takeaways and further reading.

## Concepts and terminology
Buildah image versus working container; compatible account storage; explicit Skopeo transports; OCI layout; manifest/index/platform identity; narrow blob hashing; trust versus byte integrity

## Examples and assumptions
The message fixture explicitly sets mode 0644 before COPY so image UID 65532 can read it regardless of caller umask; reviewer reproducibility finding repaired 2026-10-04.
Disposable Linux rootless labs executed by the owning ordinary account unless an administrator command is explicitly marked. Ubuntu 24.04 LTS, Fedora 44 and supported RHEL 9/10 package versions require local confirmation. Examples use fully qualified illustrative tags; production requires measured digests. No container runtime, package installation, registry transfer, systemd activation or host mutation was executed.

## Cross-references
Relative canonical links embedded in chapter; prerequisite Chapter 67.

## Open threads
Independent technical/editorial review required. Validate commands on target distribution and installed Podman version; run bounded labs on disposable authorized hosts. Confirm digest/platform, rootless mappings, security policy and restart behavior before production use.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Technical sources and dates
Official primary documentation inspected 2026-10-03: Buildah build(1), rmi(1); Skopeo inspect(1), copy(1) official repository manuals.

## Actual checks performed
Primary-source inspection and author inspection of examples. `python3 tools/check_book.py --chapters 61-70` passed: 10 draft chapters, 53 shell syntax checks, 2 YAML parses and 1,333 local links; no errors or warnings. Chapter 68 embedded Python compiled separately without execution. These are static checks, not runtime acceptance. After the permission repair on 2026-10-04, `python3 tools/check_book.py --chapters 68-68` passed 9 shell syntax checks and 1,333 local links without errors/warnings. A temporary local fixture confirmed mode 0600 under umask 077 and mode 0644 after explicit chmod; no image build or container execution occurred.

## Checks not performed
No runtime, network, volume, boot, upgrade, restore or registry test. Syntax parsing cannot establish runtime behavior.
