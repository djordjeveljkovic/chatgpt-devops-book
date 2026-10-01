# Source and verification policy

Prefer official project documentation, manuals, standards, source code, provider documentation and first-party engineering publications. Link to the exact page supporting a claim, not a search result or a vendor homepage when a specific command page exists.

Useful starting points, inspected on 2026-10-01:

- [Podman documentation](https://docs.podman.io/en/latest/): follow version-specific command manuals and Quadlet documentation.
- [Docker documentation](https://docs.docker.com/): distinguish Engine, Compose, BuildKit and Desktop.
- [Kubernetes documentation](https://kubernetes.io/docs/home/): follow stable API, feature and version-skew documentation.
- [AWS CLI v2 user guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html): supplement with the exact service command reference and IAM/service documentation.

The starting-point inspection does not verify every claim in the book. Each writer records the specific sources actually inspected in its chapter summary.

For a chapter, record:

1. Source URL, relevant behavior, publication/version context and date checked.
2. Actual locally tested commands, tool version, environment and observed outcome.
3. Syntax or configuration parsing checks, described as such.
4. Integration checks not performed, including cloud, cluster, privileged networking and live data recovery.

Use short excerpts only when necessary; write original explanations rather than translating or closely paraphrasing whole source sections. Historical publications support historical claims. Examples, estimated capacities and output must be labeled when they are fictional or illustrative.

An independent reviewer verifies claims rather than accepting a list of links as evidence. No chapter may claim its deployment worked merely because its YAML parsed or its shell passed `bash -n`.
