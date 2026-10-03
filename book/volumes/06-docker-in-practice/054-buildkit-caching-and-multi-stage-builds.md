---
book: The Complete DevOps Engineering Book
volume: 6
volume_title: "Docker in Practice"
chapter: 54
title: "BuildKit, Caching and Multi-stage Builds"
slug: buildkit-caching-and-multi-stage-builds
status: complete
summary: ../../_ai/chapter-summaries/054-buildkit-caching-and-multi-stage-builds.md
---

# Chapter 54 — BuildKit, Caching and Multi-stage Builds

Build speed matters because slow feedback encourages developers to skip checks or combine unrelated changes. A fast build is valuable only when it still reflects the source, dependencies and security policy that the team intends to ship. BuildKit provides Docker's modern build engine, with instruction and mount features that support reusable cache, temporary secrets and multiple image stages. The design goal is to avoid repeating work while keeping build-only tools and credentials out of the final runtime artifact.

This chapter builds a small Go HTTP service similar to the DispatchDesk example in [chapter 53](053-dockerfiles-and-build-contexts.md), but compiles it into a separate runtime image. Create the following project files in a fresh `dispatchdesk-go` directory. The service listens on port 8080, returns a health response and prints a startup message. A real application would add graceful termination and broader tests before deployment.

```text
module dispatchdesk.local/api

go 1.26
```

Save that module definition as `go.mod`; because this example has no external modules, it needs no `go.sum` file. The application is `main.go`:

```go
package main

import (
	"fmt"
	"net/http"
)

func main() {
	http.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		w.Header().Set("Content-Type", "text/plain; charset=utf-8")
		fmt.Fprintln(w, "ok")
	})
	fmt.Println("listening on :8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		panic(err)
	}
}
```

This simple server is for observing build output and request flow; it does not implement graceful shutdown or application-level authentication.

Place this `.dockerignore` beside the Dockerfile so local Git state and Go build artifacts are not sent as context:

```text
.git
bin/
*.test
```

## Cache invalidation and dependency ordering

Build cache is an optimization, not a record of truth. The builder reuses a step when its instruction and relevant inputs match a cached result. A changed source file should invalidate the compile step, but it should not force unchanged modules to download again. Arrange the Dockerfile so relatively stable dependency metadata is copied before frequently changing source. Keep `.dockerignore` specific so editor state, local build output and secrets do not perturb the context or leak to a remote builder.

```dockerfile
# syntax=docker/dockerfile:1
FROM golang:1.26-bookworm AS build
WORKDIR /src

COPY go.mod ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

COPY . .
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    mkdir -p /out && CGO_ENABLED=0 go build -trimpath -o /out/dispatchdesk ./...

FROM build AS test
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    go test ./...

FROM scratch AS runtime
COPY --from=build /out/dispatchdesk /dispatchdesk
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["/dispatchdesk"]
```

`# syntax` selects the Dockerfile frontend whose features parse the build file. `FROM ... AS build` names the compiler stage; the second `FROM scratch` starts a new, empty runtime filesystem. The first copy of module metadata lets a source-only edit reuse `go mod download`. This standard-library-only example has no `go.sum`; projects with external modules should copy both `go.mod` and `go.sum` before downloading dependencies. BuildKit cache mounts preserve Go's module and compiler caches across builds without adding those directories to the resulting image. They are performance state: a clean builder can still rebuild correctly by downloading or recompiling. Cache contents are not a dependency lock and should not be trusted as the only source of a build input.

The compile step writes its binary to `/out`, outside the cache mounts and source tree. `CGO_ENABLED=0` requests a statically linked binary for this simple Go program; this choice is not appropriate for every dependency or application. `-trimpath` removes local filesystem prefixes from compiled output to improve repeatability. The runtime stage copies only the resulting executable. It therefore has no Go compiler or source tree. `scratch` contains no shell, package manager or certificate bundle; an application that makes outbound TLS connections may need trusted CA certificates copied explicitly. Confirm runtime requirements before choosing an empty base. The numeric `USER` means the process runs as a non-root identity; ensure any required writable path is prepared for it.

The exact cache boundary depends on inputs. If a dependency lock changes, `go mod download` should run again. If source changes but module files stay the same, the dependency layer can remain reusable while compilation repeats. If the base image tag resolves to a changed digest, dependent steps may rebuild. Tags are mutable; use an approved update process and record the resolved base digest for release builds. Disabling cache with `--no-cache` forces more work but does not automatically select a newer base image; `--pull` asks the builder to check the base reference. Neither flag validates application correctness.

## Build secrets and multi-stage boundaries

Multi-stage builds separate what is needed to build from what is needed to run. Stage names make artifact flow reviewable: `COPY --from=build` explicitly copies one output into the runtime stage. Tests can live in another named stage, and CI can target it with `--target test`; a production target should depend only on the stages it needs. The final image size is one benefit, but a smaller image is not automatically secure. Review the executable, OS/runtime libraries, user identity, exposed interfaces and supply-chain evidence.

Build credentials must not become a layer. For private modules, configure Go's `GOPRIVATE` and, where required, `GOPROXY`, `GONOSUMDB` or `GONOPROXY` according to the organization's module and proxy policy. A `.netrc` file only authenticates to a host named in its entries; it does not choose a proxy or mark modules private. Keep the credential file outside the build context. In that private-dependency variant, copy both `go.mod` and `go.sum`, remove the earlier dependency-download instruction, and replace the compile instruction after `COPY . .` with the following single step so credentials are present if the module cache is empty:

```dockerfile
ARG DEPENDENCY_REFRESH=0
RUN --mount=type=secret,id=netrc,target=/root/.netrc,required=true --mount=type=cache,target=/go/pkg/mod --mount=type=cache,target=/root/.cache/go-build test -n "$DEPENDENCY_REFRESH" && go mod download && mkdir -p /out && CGO_ENABLED=0 go build -trimpath -o /out/dispatchdesk ./...
```

An authorized build invocation can supply the file as a secret:

```bash
docker buildx build \
  --secret id=netrc,src="$HOME/.config/dispatchdesk/netrc" \
  --build-arg DEPENDENCY_REFRESH=1 \
  --load \
  --tag dispatchdesk-api:build .
```

This command uses the current user's protected credential file and sends it to BuildKit as a temporary secret mount rather than a Dockerfile `ARG` or copied layer. The file path and permissions must be verified first; never paste a real token into a command, commit the file or print it in build logs. `--load` exports the single-platform result into the local image store. `required=true` rejects a missing mount only when the instruction executes; it does not invalidate a cached result or prove a rotated credential works. Secret contents are excluded from the instruction cache key. Change a non-sensitive `DEPENDENCY_REFRESH` value or invalidate the relevant stage to re-test after rotation; never put a credential or its hash in a build argument. The command could still copy the mounted secret elsewhere, so review the instruction and output. Use a narrowly scoped, short-lived credential and revoke it if exposed. BuildKit cache mounts are not ordinary image layers; a new builder can fetch private modules again, which is why the credential must also be mounted on a compile step that may need downloads.

The private-module variant's `test` stage also needs the matching credentials if tests import private modules and the builder's module cache is empty. Replace its plain `go test` instruction with the same secret and cache mounts, after setting the appropriate non-secret Go private-module configuration:

```dockerfile
ARG DEPENDENCY_REFRESH=0
RUN --mount=type=secret,id=netrc,target=/root/.netrc,required=true --mount=type=cache,target=/go/pkg/mod --mount=type=cache,target=/root/.cache/go-build test -n "$DEPENDENCY_REFRESH" && go test ./...
```

As with the compile instruction, change a non-sensitive refresh value or invalidate the test stage when deliberately validating rotated credentials. The dependency-free example does not need a secret for tests.

A multi-stage boundary helps only if sensitive files and tools do not cross it. `COPY --from=build /out/dispatchdesk` copies one artifact. `COPY --from=build / /` would defeat the purpose. Keep private credentials outside the context, use secret mounts, and inspect intermediate stage access and cache policy. Build caches can contain intermediate artifacts even if the final image does not; restrict cache registry access and retention according to the data in those layers.

For local development, use `docker buildx build --target build --tag dispatchdesk-api:build-debug --load .` to load the named build-stage image into the local image store for inspection. The `--load` option requests a single-platform local image export; without an output option, a Buildx builder may retain the result only in its cache. For production, build the default runtime target. Run tests explicitly with `docker buildx build --target test --tag dispatchdesk-api:test --load .` before building or publishing the runtime target. BuildKit can skip unrelated stages, so the runtime build does not automatically prove the separate test stage passed.

## Reducing rebuild time and image size

Measure before optimizing. In the fresh `dispatchdesk-go` directory on the Docker host, confirm `docker buildx ls` shows the intended builder and the CLI identity can use its daemon. The default `docker` driver loads images locally; other drivers need `--load` for this single-platform example. Run a build that bypasses ordinary instruction-layer reuse and inspect its steps and image size:

```bash
docker buildx build --no-cache --progress=plain --load --tag dispatchdesk-api:local .
docker image inspect dispatchdesk-api:local --format '{{.Size}}'
```

Run the built service locally and verify its health route. These commands assume that host port 18082 is unused and that the shell is on the same host as the selected daemon:

```bash
docker run --detach --rm --name dispatchdesk-go-lab --publish 127.0.0.1:18082:8080 dispatchdesk-api:local
curl --fail --show-error http://127.0.0.1:18082/healthz
docker logs dispatchdesk-go-lab
docker stop dispatchdesk-go-lab
```

The expected response body is `ok`; this is a reader exercise and no output is claimed as measured. The `--rm` option removes the container after it exits. Check logs before stopping if the request fails.

`--no-cache` bypasses ordinary instruction-layer reuse but does not clear mutable cache mounts, which may still contain package data from an earlier build. Repeat without `--no-cache` and compare progress output. Make a small source-only change to `main.go` (for example, the startup message), build again and compare which steps rerun. The metadata/download step should remain eligible for reuse while compilation changes; the image size may stay the same. These are expected observations, not measured book output. Restore the source change after the experiment. A slow build may reflect network resolution, a large context, a frequently invalidated instruction, limited resources or absent cache, each requiring a different remedy.

After stopping and removing any lab container, remove the local image with `docker image rm dispatchdesk-api:local` if it is no longer needed. This removes that local image content only when no remaining container depends on it; it does not remove registry copies or other build cache.

For a CI runner that starts with an empty local builder, an external cache can preserve reusable results. Before using the registry backend, check `docker buildx ls` to identify the builder and confirm it supports registry import/export. The default `docker` driver supports only some cache exports and, as of the documentation review date, registry cache with that driver requires the containerd image store. A `docker-container` builder supports more cache backends, but registry access and authentication are still required. Follow the CI credential policy for the fictional cache registry below:

```bash
docker buildx build \
  --cache-from type=registry,ref=registry.example.net/dispatchdesk/api:buildcache \
  --cache-to type=registry,ref=registry.example.net/dispatchdesk/api:buildcache,mode=max \
  --tag registry.example.net/dispatchdesk/api:commit-REPLACE_WITH_REVISION \
  --push .
```

This is a template. Replace the fictional registry and revision placeholder with reviewed values; do not treat a mutable cache tag as a release artifact. The builder imports prior cache data, exports updated cache data, and pushes the tagged image. `mode=max` can export cache records for intermediate build stages, which may improve reuse but increases the material stored and shared. Grant the CI identity only the registry rights it requires, protect caches from untrusted pull-request jobs, and never put secrets in a cacheable layer. External cache export does not automatically preserve mutable cache-mount contents; do not assume a cache mount exists on another builder because registry layer cache was imported.

An external cache is untrusted input from an access-control perspective. Use it to save computation, not to establish artifact identity or bypass review. Build provenance should describe the actual source and inputs; release promotion should still test and identify the output digest. If a build behaves differently with cache enabled, investigate hidden inputs, timestamps, network downloads or an unsafe cache key rather than assuming that `--no-cache` is a durable fix.

Image size reduction should follow runtime requirements. Copy only the required binary and data into the runtime stage, use a suitable minimal base, and verify certificates, timezone data, shared libraries and writable paths required by the program. A distroless or scratch runtime can reduce included tools and package surface, but it also removes familiar debugging commands. Operators can inspect from the host, use a separate debug target or run a dedicated diagnostic image. Do not add a shell to production by habit if the process and diagnostics work without one; do not remove components that the service needs merely to hit an image-size target.

If builds are slow after a source edit, compare the changed file with the first invalidated step. If dependencies reinstall, move dependency metadata before source and ensure that installation truly depends only on the metadata. If a secret appears in image history or logs, stop distribution, revoke it, inspect caches and intermediate images, and rebuild from clean inputs. Deleting the final tag alone does not erase copies already pulled or cached elsewhere.

## Exercises and review questions

1. Why are Go module files copied before `main.go`? In a project with external modules, which change should invalidate dependency download?
2. Explain the difference between a cache mount and an image layer. What happens on a clean builder?
3. What properties does the second `FROM scratch` provide, and what dependencies might it omit?
4. Why can `COPY --from=build / /` defeat a multi-stage boundary?
5. A CI source change invalidates dependency downloads on every run. Name two likely causes and the evidence you would inspect.
6. What risks come with sharing an external `mode=max` cache with jobs that build untrusted changes?

### Answer guidance

1. Module metadata defines dependencies and usually changes less often than source. A change to it should rerun resolution; an ordinary source edit should repeat compilation but can reuse the download result. This standard-library example has no `go.sum`; dependency-using projects should copy both module and checksum files.
2. A cache mount persists builder performance data but is not copied into the image layer or automatically exported as registry cache. A clean builder may redownload/recompile and should still produce the result from declared inputs.
3. `scratch` starts with an empty filesystem, reducing included runtime files. It omits certificates, libraries, timezone data, shells and package tools; copy only what the program requires and verify actual dependencies.
4. It copies the entire builder filesystem, potentially including compiler, source, caches and accidental credentials rather than a narrow runtime artifact.
5. The lock/module metadata may be copied after all source, or the dependency instruction may depend on a changing file. Inspect Dockerfile order, build context and cache progress.
6. Intermediate artifacts can be exposed or poisoned. Restrict writers/readers, separate trusted release and untrusted job caches, avoid credentials in layers and verify output through normal release controls.

## Takeaways

- Order stable dependency inputs before frequently changing source, then measure actual cache behavior.
- Cache mounts improve rebuild speed but are not declared dependencies or release evidence.
- Multi-stage builds let the final image contain selected artifacts without build tools; copy narrowly and verify runtime dependencies.
- Supply build credentials through temporary secret mounts and protect intermediate cache data.
- External caches save work; they do not establish trust, freshness or artifact identity.

## Further reading

- [Dockerfiles and Build Contexts](053-dockerfiles-and-build-contexts.md) — Dockerfile instructions and context boundary.
- [Publishing and Promoting Images](059-publishing-and-promoting-images.md) — artifact identity and release movement.
- [Running and Managing Containers](052-running-and-managing-containers.md) — local lifecycle for observing an image.

## Sources and verification

Docker's [cache optimization](https://docs.docker.com/build/cache/optimize/), [cache invalidation](https://docs.docker.com/build/cache/invalidation/), [multi-stage builds](https://docs.docker.com/build/building/multi-stage/), [cache backends](https://docs.docker.com/build/cache/backends/), [builder drivers](https://docs.docker.com/build/builders/drivers/), [Buildx build reference](https://docs.docker.com/reference/cli/docker/buildx/build/), [build secrets](https://docs.docker.com/build/building/secrets/), [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) and [Go modules reference](https://go.dev/ref/mod) were inspected on 2026-10-02. The examples assume Dockerfile frontend syntax 1 and a Buildx builder supporting the requested features. No image was built, no secret was supplied and no registry cache was read or written because this workspace has no Docker daemon or registry credentials.
