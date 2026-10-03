# Independent review — Chapter 51

Reviewer: review_055
Review date: 2026-10-03
Verdict: approved
Reviewed body SHA256: 6f57e29e32bcca93817242c1378d42b482b5bb9358519645ea7d28f449ef1ca2

## Findings and resolution

No unresolved material findings.

All four prior material findings are addressed. Rootful version/info verification now runs with the same privileged identity, explicitly selects `unix:///var/run/docker.sock`, and removes `DOCKER_HOST`, `DOCKER_CONTEXT` and `DOCKER_CONFIG` for those invocations. Ordinary-user access is separately explained without granting Docker group membership or changing socket permissions.

Target verification now inspects all three relevant environment overrides and the selected stored context, explains flag/environment/configuration effects and prohibits combining `--host` with `--context`. The ordinary-user `--context default` test explicitly selects that context and clears `DOCKER_HOST`. The commands are compatible with Docker's documented context precedence: explicit selection takes priority over stored interactive selection, and `DOCKER_CONTEXT` can override `DOCKER_HOST` when selection is ambient. The text correctly treats a context name as configuration evidence rather than a successful connection and cautions that sudo changes identity/configuration.

The `--rm` smoke test now explains automatic container removal and the remaining terminal/exit-status evidence. A named retry without `--rm` supplies inspect/log commands, scoped cleanup and ownership-aware name-conflict handling. Evidence can therefore be retained when creation succeeds; initial errors remain relevant if no container was created.

A practical installation/inspection exercise, expected evidence, failure guidance, five answers, takeaways and relative prerequisite/canonical links complete the chapter contract. No material new issue was found in the additions.

## Factual assessment

The manuscript covers the ordered installation, daemon authority and client/server/context sections. The Ubuntu deb822 repository/keyring commands match the current official procedure. Fedora and RHEL repository URLs and DNF syntax are distinct and match their respective installation pages. RPM startup is explicit; Ubuntu service status is checked. Supported-release lists agree with the inspected documentation: Ubuntu 22.04/24.04/26.04, Fedora 43/44 and RHEL 8/9/10. These are dated documentation claims, not a permanent support promise. RHEL repository/subscription and derivative-platform limitations are correctly qualified.

Package conflict removal is intentionally deferred to a host inventory and official procedure rather than performed blindly. Installation changes, recovery access, data preservation, signing-key prompts, systemd enable/start semantics, convenience-script limits and root-equivalent socket authority are explained. SELinux guidance preserves enforcement and firewall integration is identified as a separate exposure check.

Shell continuations contain one literal backslash. The Ubuntu heredoc expansion is appropriate; no undefined variables are needed. Privileged socket verification and ordinary-user environment checks are read-only. The named hello-world procedure correctly expects a one-shot stopped container and distinguishes retained metadata from downloaded image cache. Links to Chapters 46, 47, 50 and 52 resolve. Recovery reasoning separates socket/daemon, registry trust/authentication and process-start failures. Assessment is concise and relevant, with no substantial repetition.

The exercise phrase “matching client and server version output” should be understood as recording the two outputs for the intended daemon, not requiring identical numerical versions: the main text explicitly reports separate client/server versions and API details. No material correctness issue arises from that wording.

## Validation evidence and limitations

Read the previous review and all four findings, current manuscript and summary, skeleton brief, authoring contract and relevant prerequisite context. Calculated the current body hash using `tools.promote_reviewed.body_hash`.

Opened current official primary sources on 2026-10-03: [Ubuntu installation](https://docs.docker.com/engine/install/ubuntu/), [Fedora installation](https://docs.docker.com/engine/install/fedora/), [RHEL installation](https://docs.docker.com/engine/install/rhel/), [Linux post-installation](https://docs.docker.com/engine/install/linux-postinstall/), [contexts](https://docs.docker.com/engine/manage-resources/contexts/), [Docker CLI environment/options](https://docs.docker.com/reference/cli/docker/), [context show](https://docs.docker.com/reference/cli/docker/context/show/) and [container removal](https://docs.docker.com/reference/cli/docker/container/rm/). Retained the prior reviewed run/firewall semantics, also checked during the surrounding Docker review work. Checked repository syntax, support lists, privilege assumptions and target-selection controls against those sources.

Ran `python tools/check_book.py --chapters 51-51`: seven shell syntax blocks and 1,271 repository local-link checks passed with no errors or warnings. Manually checked shell expansion, target/identity consistency and retained-container cleanup semantics. Static parsing and documentation review do not establish runtime compatibility.

No packages were installed or removed. No service, daemon, registry, image pull/run, context mutation, socket permission/group change, firewall change or installation rollback was executed. Target-host package availability and actual privileged/unprivileged access remain untested. Approval covers the reviewed body and documentary/static evidence, with these runtime limits retained.
