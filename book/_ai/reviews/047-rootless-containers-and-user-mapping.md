# Independent review — Chapter 47

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: bc268a5a3fe319df10c470cf9bab542bbd17210d9559b74e635acf94d993faf8

## Findings

No unresolved material findings. Fresh independent review of the complete corrected current manuscript body: The revised hypothetical maps distinguish custom/remapped and common rootless layouts. Independently checked arithmetic: the first maps UID 1000 to 232072; the second maps UID 0 to host 1000 and UID 1000 to 232071. Bind-mount discussion uses the second map consistently. All exercises now have appropriate guidance; the pending-review tail is removed.

## Inspection and dated evidence

Freshly retrieved Kubernetes [CRI documentation](https://kubernetes.io/docs/concepts/containers/cri/), Ubuntu [AppArmor documentation](https://documentation.ubuntu.com/server/how-to/security/apparmor/index.html), Docker [registry authentication](https://docs.docker.com/reference/api/registry/auth/) and [login](https://docs.docker.com/reference/cli/docker/login/) on 2026-10-04 for the corrected passages. Earlier same-date source inspection below remains applicable to unchanged passages.

Read the authoring guide, assigned SKELETON/manifest entry, complete manuscript and summary and prerequisite/canonical summaries 41–45. Reviewed all four assigned chapters together for terminology, dependency and publication consistency. The prior review included briefs, summaries and prerequisites. This fresh pass read current manuscript bodies and compared all recorded findings; summaries and prerequisites were not reread. Explanations, answer guidance and operational takeaways are coherent.

Inspected [Linux user namespaces](https://man7.org/linux/man-pages/man7/user_namespaces.7.html), Docker [rootless](https://docs.docker.com/engine/security/rootless/) and [userns-remap](https://docs.docker.com/engine/security/userns-remap/), and [Podman manual](https://docs.podman.io/en/stable/markdown/podman.1.html) on 2026-10-04. These support namespace-relative capability scope, separate engine stores/identity, subordinate range management and host-file permissions. The mapping examples are hypothetical rather than measured defaults. Storage/network limits and remote-engine caveats are directionally accurate and explicitly version dependent. Inspection commands read only the current shell's map and do not claim a workload was inspected.

## Validation and limits

`python tools/check_book.py --chapters 46-49` passed on 2026-10-04: four draft chapters, five shell syntax blocks and 1,336 global local-link checks; no errors or warnings. Static syntax/local-link checks cannot establish runtime behavior, application compatibility or availability of every external link. Successfully retrieved primary sources are listed above, not an exhaustive external-link audit. Docker is unavailable; no Docker/Podman engine, runtime bundle, registry, security profile or workload was contacted/started/changed. No namespace mapping, capability, host policy, registry login/pull, image-store migration, credential or recovery operation was executed. No Ubuntu/Fedora/RHEL runtime matrix test was performed. Only separate review records were written; manuscripts, summaries and shared state were unchanged.

Verdict: approved
