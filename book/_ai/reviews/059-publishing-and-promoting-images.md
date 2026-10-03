# Independent review — Chapter 59

Reviewer: review_055
Date: 2026-10-03
Verdict: approved
Reviewed body SHA256: 8f55e8494cf5b259d48820be6807ab643fbc564177a836ee6fd0c30501bdbfbf

## Findings

No material findings.

Both prior nonblocking precision refinements are resolved. The creation example now explains default `--prefer-index=true`, copying an existing index/list versus wrapping an ordinary platform manifest, and `--prefer-index=false` when preservation is required. Credential cleanup now explicitly distinguishes config-directory removal from helper-held credentials and calls for helper-aware registry logout plus CI-provider revocation. The edited paragraphs agree with the official sources inspected during the initial review; no new material finding arises. Approval is reconfirmed for the updated body hash.

## Factual assessment

The chapter follows the registry authentication/identity, build/promotion and versioned-release brief. The fictional registry, organization-specific repository/credentials, CI-injected variables and digest placeholders are explicit; the text neither fabricates a release digest nor presents a public push as a harmless lab. Login uses a hostname rather than a repository path, correctly scopes the private destination, and uses `--password-stdin` in automation. Shell tracing and credential publication are excluded, helper/config persistence is acknowledged, and publishing scope is separated from runtime pull authority. Authentication is correctly distinguished from repository authorization.

Tags are mutable unless registry policy prevents mutation; a digest identifies manifest content. Local image IDs are distinguished from registry manifest digests, and per-platform manifests from the top-level index. The example's `docker build` does not claim to generate a multi-platform index: required platforms are checked from registry output, and a missing architecture blocks promotion. Chapter 54 supplies builder/cache background rather than a complete multi-platform recipe; the current chapter's conceptual overview is accurate without executing such a recipe.

The build-context and full lowercase SHA-1 commit checks are internally consistent for the stated 40-character Git revision convention. They are not a general validator for Git SHA-256 repositories. `BUILD_CONTEXT` is explicitly injected and must contain the earlier reviewed Dockerfile; the local image is tagged, inspected and pushed in the same workflow. `--pull` is correctly separated from strict reproducibility. Clean source, pinned inputs, target daemon/builder and approval evidence remain operational prerequisites rather than promised consequences of a successful command.

The Buildx creation example tags a digest already present in the same registry/repository; it is not falsely presented as arbitrary cross-registry layer copying. Repeated tag options and inspection arguments are valid. The possibility of a changed top-level manifest is acknowledged, with destination inspection and per-platform/configuration comparison required. A tag alone does not prove tested artifact identity. The example does not rebuild per environment or silently promote a developer's local image. A deployment digest and human release record are separately retained.

Release evidence includes the exact candidate, platforms, approvals and policy results; signatures/scanner outcomes are correctly qualified. Push/pull failure diagnosis distinguishes naming, authentication, authorization, network and retention. Tag drift freezes deployment and triggers audit rather than overwriting evidence. Recovery selects a retained prior digest, and registry retention is separated from local image deletion. The five exercises and answers reinforce identity, authorization, architecture and promotion boundaries. Takeaways and relative prerequisite/canonical links resolve. Prose is readable and avoids retelling networking or container internals. No Linux-specific installation commands require distro variants in this registry/client workflow.

## Validation evidence and limitations

Read the authoring guide, Chapter 59 brief, manuscript and summary, relevant Chapter 49/53/54/58 prerequisite context and Buildx-related commands in Chapter 54. Computed the current hash using `tools.promote_reviewed.body_hash`.

Opened official primary documentation on 2026-10-03: [Docker login](https://docs.docker.com/reference/cli/docker/login/), [image push](https://docs.docker.com/reference/cli/docker/image/push/), [Buildx imagetools inspect](https://docs.docker.com/reference/cli/docker/buildx/imagetools/inspect/), [Buildx imagetools create](https://docs.docker.com/reference/cli/docker/buildx/imagetools/create/), [Docker Hub immutable tags](https://docs.docker.com/docker-hub/repos/manage/hub-images/immutable-tags/) and [multi-platform builds](https://docs.docker.com/build/building/multi-platform/). Checked credential helper/config behavior, standard-input authentication, manifest/index identity, creation/tagging defaults and platform-selection claims against those sources. Docker Hub immutability documentation supports that provider's feature, not a guarantee about the fictional private registry; the manuscript appropriately requires registry-specific support.

Ran `python tools/check_book.py --chapters 59-59`: five shell syntax checks, one YAML parsing check and 1,291 repository local-link checks passed with no errors or warnings. Manually inspected variable prerequisites, shell continuation/quoting, image-name construction, placeholder use and command ordering. These checks do not establish registry permissions or validate artifact equivalence.

No credentials were obtained or supplied. No login, daemon query, image build/pull/push, registry inspection/promotion, deployment, signature/policy check, retention change or cleanup command was executed. The fictional registry's TLS, scopes, immutability, media conversion, attestations, platforms and rollback availability remain untested. Approval covers the reviewed manuscript and documentary/static evidence, with these limits retained.
