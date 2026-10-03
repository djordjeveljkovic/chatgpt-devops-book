# Chapter 54 — BuildKit, Caching and Multi-stage Builds

Status: complete

## Written material
Cache invalidation and layer ordering; BuildKit cache mounts; multi-stage Go build; BuildKit secret mount; registry-backed external cache; failure diagnosis; exercises with answer guidance, takeaways and further reading.

## Concepts and terminology
BuildKit frontend, cache key/reuse, cache mount, named stage, scratch image, build secret mount, external registry cache, `mode=max`.

## Examples and cross-references
Fictional DispatchDesk Go HTTP build/runtime stages, secret template, registry cache template; Docker build, secret and cache commands not executed. Go module/program source was extracted and passed local `go test` and static build. Relative links to chapters 52, 53 and 59.

## Open threads
Base image tags and builder/backend support vary. No Docker build, secret use or registry cache test; independent review approved.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Docker official cache optimization/invalidation, multi-stage, cache backends, builder drivers, Buildx CLI, secrets and Dockerfile docs plus Go modules reference inspected 2026-10-02. Extracted Go program passed `go test ./...` and `CGO_ENABLED=0 go build -buildvcs=false -trimpath`; no Docker image build, container run, secret use or registry/cache operation. Full `tools/check_book.py` passed 220 chapter checks and all registered syntax/link checks, with no errors or warnings. Checker does not validate runtime semantics. Reviewer `review_054` approved body SHA256 `0a1655ff5f3a9b374154f95834ee9d5fd55af6c1aa38f70cbb32f784d30d79b5`.
