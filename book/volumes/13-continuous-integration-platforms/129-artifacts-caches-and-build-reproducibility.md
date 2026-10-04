---
book: The Complete DevOps Engineering Book
volume: 13
volume_title: "Continuous Integration Platforms"
chapter: 129
title: "Artifacts, Caches and Build Reproducibility"
slug: artifacts-caches-and-build-reproducibility
status: complete
summary: ../../_ai/chapter-summaries/129-artifacts-caches-and-build-reproducibility.md
---

# Chapter 129 — Artifacts, Caches and Build Reproducibility

## Artifacts versus disposable caches

An artifact is an output that a build deliberately produces and another job or operator is expected to consume: a package, container image, test report, release bundle or diagnostic file. A cache is a performance hint that may be absent, stale, incomplete or overwritten. A job must be able to regenerate or retrieve its inputs when a cache miss occurs. If deleting the cache changes whether a release can be built correctly, the cache has become an undocumented dependency or artifact store.

CI platforms expose similar-looking storage features with different lifecycle and trust behavior. GitHub distinguishes caches for reusable dependencies or intermediate files from artifacts passed between jobs or saved after a run. GitLab job artifacts explicitly connect producer and consumer jobs, while GitLab cache is intended to speed dependency reuse. Jenkins `stash`/`unstash` transfers small files within a run; archived artifacts can outlive that run according to retention and storage settings. None of those terms automatically means durable, immutable, authenticated or public. Configure expiry, access, size and retention for the actual purpose. See [GitHub caching](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching), [GitLab artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/) and [Jenkins test artifacts](https://www.jenkins.io/doc/book/pipeline/tour/tests-and-artifacts/).

Treat caches as untrusted input. A cache may cross branches, jobs or workflow triggers according to platform-specific rules. Untrusted code may read cache content or influence what a later trusted job restores. Never store secrets in a cache, and do not execute a cached binary or generated script in a privileged context without verification. Partition cache keys by dependency lockfile, toolchain and trust class where relevant, but remember that a key is routing metadata; it does not prove who produced the contents. Re-download and verify packages from trusted repositories, and use a clean cache or isolated namespace when trust boundaries differ.

Artifacts need an explicit producer-consumer contract. Name the output, record its source revision and digest, specify how long it is retained, and restrict who can fetch or replace it. Avoid downloading “latest” by branch name for a release: a later pipeline can change what latest means, and the lookup may not identify the producer you tested. Select a pipeline or immutable version, verify its metadata and digest, then promote the same bytes. If the destination registry permits overwriting tags, use a digest or enforce immutable-tag policy and verify the digest after publication.

## Dependency integrity and reproducible inputs

A reproducible build aims to produce the same output from the same declared inputs. This is stricter than “the build passed twice,” and it does not automatically prove the source is safe. Unrecorded inputs—floating container tags, package versions, plugins, downloaded scripts, locale, timezone, environment variables, filesystem ordering, timestamps, random seeds, network responses or compiler versions—can change the output. A lockfile narrows dependency resolution but does not freeze the operating system, build tool, plugin, remote repository content or every transitive build input.

Improve repeatability by pinning build images and tool versions by immutable digest or exact version, committing lockfiles, verifying dependency checksums or signatures where the ecosystem supports them, and avoiding network fetches during the build except through controlled, recorded dependencies. Generate outputs in a clean workspace with a documented toolchain. Normalize timestamps and archive ordering when the format permits. Keep build scripts and configuration under version control. Separate build-time dependencies from runtime packages and use a software bill of materials or inventory to describe dependencies where the release policy requires it.

A build can be deterministic for a fixed environment while that environment remains mutable across runs. Hermeticity narrows what the build can read from the host or network; reproducibility checks whether independent executions using the declared inputs yield identical outputs. These properties are related but distinct. Rebuilding the same commit on a different machine may produce different bytes because of a compiler, locale or timestamp. Conversely, two executions could produce identical bytes even though a dangerous undeclared dependency was used. Record the environment, materials and process rather than treating a matching hash as a complete supply-chain review.

Build provenance is verifiable metadata about where, when and how an artifact was produced. The SLSA provenance format identifies artifact subjects by digest and describes the build definition, resolved dependencies and builder identity. A consumer should verify that the attestation refers to the artifact being consumed, comes from an expected signer and builder, and records an allowed source revision and process. Provenance generated by the same compromised build process may repeat false claims; trust depends on the platform's control plane and the provenance-generation boundary. A signature establishes that a key or identity signed data, not that the source, dependencies or build were safe. See [SLSA build provenance](https://slsa.dev/spec/v1.2/build-provenance) and [verifying artifacts](https://slsa.dev/spec/v1.2/verifying-artifacts).

## Tracking one artifact through a pipeline

DispatchDesk builds its API container once from commit `C`, runs unit and integration tests against that image digest, scans the same image, and promotes that digest to staging and production. Let `sha256:D` identify the immutable image manifest. The test result, scan report, provenance statement, registry entry and deployment record should all refer to `C` and `D`. A later job must retrieve the image by digest, not rebuild from `C` and assume it gets the same bytes.

```text
source commit C + declared dependencies
                 |
                 v
          isolated build job
                 |
     image digest sha256:D + provenance
                 |
         +-------+--------+
         |                |
         v                v
    test sha256:D     scan sha256:D
         |                |
         +------- gate ---+
                 |
                 v
     promote the same sha256:D
                 |
                 v
     deploy record: C, D, environment
```

The diagram shows the identity relationship; it is not an implementation of a registry, signer or deployment system. In a real pipeline, the build job should publish to a staging namespace that untrusted jobs cannot overwrite. Test and scan jobs should fetch the explicit digest from the same pipeline and emit results linked to it. The promotion step should verify producer identity, source revision, digest and required gate results before granting write access to the production registry or deployment system. Separate credentials and jobs so that test code cannot replace an artifact after tests pass.

When a build fails or an artifact is missing, do not substitute a cache, a different pipeline's latest output or a fresh unverified rebuild. Stop promotion, preserve logs and metadata, identify the producer and retrieve the exact output if available. If the artifact cannot be reproduced, investigate which inputs were absent from the record. This can reveal floating dependencies, runner image drift, nondeterministic timestamps, external downloads or accidental dependence on shared workspace state.

A useful artifact record includes:

- Source repository and immutable commit identifier.
- Build pipeline, job, builder identity and configuration revision.
- Exact dependency and toolchain inputs that affect the output.
- Artifact name, media type, digest, registry location and retention policy.
- Test and scan result identifiers that evaluated that digest.
- Promotion approvals, destination environment and final deployment digest.

Do not confuse this record with proof that every claim is true. Review who can alter the pipeline, issue the attestation, write the registry, approve promotion and change cloud trust. Keep metadata protected against accidental overwrite, but make it available to incident responders and downstream verifiers. [Chapter 128](128-tests-quality-gates-and-feedback.md) explains test and scan gates; [Chapter 130](130-ci-incidents-and-platform-comparison.md) uses artifact lineage to diagnose a compromised or stalled pipeline.

## Takeaways

Caches may accelerate a build but must remain disposable and untrusted. Identify artifacts by digest, record their source and builder, and test, scan and promote the same bytes.

## Exercises and answer guidance

1. Deleting a dependency cache causes a release build to fail because a binary is available only in that cache. What is wrong? The build depends on cache contents for correctness; declare and retain the binary as an artifact or retrieve it from an authenticated immutable package repository.
2. A pipeline tests image digest A, rebuilds the commit, then deploys image digest B. What was not established? That the deployed bytes are those tested; promote A by digest or explicitly test and verify B before deployment.
3. Two rebuilds of the same commit produce different archives because timestamps differ. Is the source necessarily compromised? No. The build may be nondeterministic; identify and normalize undeclared inputs, then compare output digests and document the environment.
4. A signed provenance record points to the expected commit. Does that prove the software is safe? No. Verify signer and builder trust, subject digest, process and dependencies; provenance is evidence of origin and process, not a safety guarantee.
5. A trusted release job restores a cache written by a fork workflow. What should be considered? The cache may contain attacker-controlled data; prevent low-trust writes from reaching trusted cache scope, avoid executing restored content, and validate or regenerate inputs.
6. The release dashboard records a version tag but no digest. What should be added? Record the immutable artifact digest and link it to source, build, verification results, promotion and deployment.

Review questions: when is a cache safe to miss, what does an artifact digest identify, how do deterministic builds differ from hermetic builds, and what does provenance verification require the consumer to trust?

## Verification and primary sources

Official GitHub and GitLab CI storage documentation, Jenkins artifact behavior, and SLSA v1.2 provenance and verification guidance were inspected on 2026-10-04. The diagram is conceptual; no build, signature, attestation, registry publication, cache or deployment was executed. A matching artifact digest establishes byte identity only for the measured object; the chapter does not validate any specific builder, signer, artifact registry, SLSA level or consumer policy.

Primary references: [GitHub dependency caching](https://docs.github.com/en/actions/concepts/workflows-and-actions/dependency-caching), [GitLab job artifacts](https://docs.gitlab.com/ci/jobs/job_artifacts/), [Jenkins artifacts](https://www.jenkins.io/doc/book/pipeline/tour/tests-and-artifacts/), [SLSA v1.2](https://slsa.dev/spec/v1.2/), [SLSA build provenance](https://slsa.dev/spec/v1.2/build-provenance), and [SLSA artifact verification](https://slsa.dev/spec/v1.2/verifying-artifacts).
