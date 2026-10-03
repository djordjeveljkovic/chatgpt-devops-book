---
book: The Complete DevOps Engineering Book
volume: 7
volume_title: "Podman and the Rootless Host"
chapter: 65
title: "Podman Pods and Kubernetes YAML"
slug: podman-pods-and-kubernetes-yaml
status: complete
summary: ../../_ai/chapter-summaries/065-podman-pods-and-kubernetes-yaml.md
---

# Chapter 65 — Podman Pods and Kubernetes YAML

## Shared namespaces and pod membership

DispatchDesk's fictional VPS team is evaluating an application and a tightly coupled local helper. They need one deployment boundary and local communication, but not cross-host scheduling. A Podman pod groups containers that can share selected namespaces. It can express that relationship on one host. It does not provide a Kubernetes control plane, replicas spread over machines, or a persistent-volume controller.

Read [Podman networking](064-podman-networking-and-ports.md) and [Linux namespaces](../05-container-internals-and-oci/042-linux-namespaces.md) first. Use a disposable local Linux host, one ordinary Podman account, registry access, `curl` and free host port 8090. Keep this lab separate from the previous chapter's objects. The fixture is an HTTP server plus a request client, not a deployed DispatchDesk application or database.

```bash
podman --remote=false pod create --name dd-pod-65 \
  --publish 127.0.0.1:8090:80
podman --remote=false run --detach --name dd-web-65 \
  --pod dd-pod-65 docker.io/library/nginx:alpine
podman --remote=false pod inspect dd-pod-65
podman --remote=false ps --pod
curl --fail --show-error --max-time 5 http://127.0.0.1:8090/
podman --remote=false run --rm --pod dd-pod-65 \
  docker.io/library/busybox:1.37 \
  wget -T 5 -q -O - http://127.0.0.1:80/
```

Publication belongs to the pod's shared network boundary and is declared at pod creation. The BusyBox client can reach Nginx on loopback because it joins the same network namespace. This is intentionally different from Chapter 64's unrelated client container, where loopback could not address the server. Inspect namespace sharing rather than deriving it from the word “pod.” The [pod-create manual](https://docs.podman.io/en/stable/markdown/podman-pod-create.1.html) describes sharing and the infrastructure container that can maintain the pod's namespaces.

Two members cannot independently occupy the same address and port in that shared namespace. If a helper also listens on port 80, the second bind fails. Assign distinct ports or reconsider whether the components belong together. Containers can share networking while retaining separate filesystems; one container's path is not automatically another's path. Explicit volumes are needed for shared files, and their credentials/security policy still require Chapter 63's reasoning.

A pod's grouping also does not make every member's readiness identical. An HTTP server can run while its helper has exited. Inspect both member states and the application's dependency contract. If one member is an optional diagnostics task, treating its exit as a whole-service failure may be wrong. If it performs a mandatory local function, that exit must affect service readiness. The application and supervisor need to express that distinction.

## Generate kube and play kube boundaries

Podman can generate Kubernetes-style YAML from supported local objects and play supported YAML back into local objects. Current CLI spelling is `podman kube generate` and `podman kube play`; older material may show `generate kube` or `play kube`. Confirm local help rather than building a migration on an obsolete command form. The [generate reference](https://docs.podman.io/en/stable/markdown/podman-kube-generate.1.html) explains generated resources, and the [play reference](https://docs.podman.io/en/stable/markdown/podman-kube-play.1.html) lists supported fields.

Generation is a useful inspection and starting-point tool. It cannot infer the team's application readiness semantics, disaster-recovery objective or deployment approval policy. Generated YAML can encode host-specific paths and annotations; review it before committing. A portable API shape does not make a bind-mounted host directory portable data.

From a dedicated working directory, capture the fixture:

```bash
mkdir -m 700 "$HOME/dd-kube-65"
cd "$HOME/dd-kube-65"
podman --remote=false kube generate dd-pod-65 > generated-pod.yaml
```

Read the whole file. Identify the image references, member names, commands, ports, volumes and annotations. Check whether host publication is reproduced as intended. The output is an observation of this pod, not an immutable release manifest unless image identities and configuration have been approved. Do not apply it blindly while the source pod holds the same names and ports.

For a deliberate minimal manifest, save the following as `dd-fixture.yaml` in that directory:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: dd-yaml-65
  labels:
    app: dd-fixture
spec:
  containers:
    - name: web
      image: docker.io/library/nginx:alpine
      ports:
        - containerPort: 80
          hostPort: 8090
          hostIP: 127.0.0.1
          protocol: TCP
```

This file describes one pod containing one HTTP server. The `containerPort` documents its port; `hostPort` and `hostIP` request the local host publication in Podman's supported interpretation. It deliberately excludes a database, secrets and host paths. The tag is a lab convenience. Replace it with an actual verified digest for a release, and review the architecture on each target host.

A YAML parser can establish syntax, not Podman field support. The installed `kube play` implementation must interpret the particular fields. A Kubernetes server's schema validation is a separate acceptance process. Unsupported fields may be rejected or ignored depending on the implementation and field; consult the support table and inspect realized objects. Do not describe “the YAML parsed” as successful deployment evidence.

## Moving a small pod between environments

Stop and remove the first lab pod before playing the manifest, because it occupies the same host port. This deletes the lab containers and their disposable writable layers:

```bash
podman --remote=false pod stop --time 10 dd-pod-65
podman --remote=false pod rm dd-pod-65
podman --remote=false kube play dd-fixture.yaml
podman --remote=false pod ps
podman --remote=false ps --pod
curl --fail --show-error --max-time 5 http://127.0.0.1:8090/
```

Inspect the actual created names and pod membership. Compare the resulting image identity and publication with the file. Preserve logs if the fixture fails. An immediate HTTP failure may be a startup interval; use a bounded acceptance window with repeated observation, not an unbounded retry loop.

Moving this file to a second disposable host transfers intent. It does not transfer downloaded image layers, credentials, a named volume's content, subordinate IDs or systemd startup configuration. On the second host, verify engine version, architecture, rootless account, free port and registry reachability first. If a manifest later includes a host path, create and label the intended dedicated path there, restore consistent data and verify ownership separately.

A local pod does not become a highly available deployment merely because the file uses `apiVersion: v1`. If the host fails, every member fails together. If a Kubernetes migration is justified later, the application may need a Deployment, Service, storage class and scheduling decisions that are absent here. [The architecture tradeoff chapter](../01-engineering-mental-models/005-architecture-as-tradeoffs.md) provides the decision framework. Do not add a cluster solely because the manifest resembles a cluster API.

## Failure, diagnosis and recovery

Suppose a reader tries playing `generated-pod.yaml` while the original pod is still running. The failed assumption is that generation produces an independent second service automatically. Object names or ports collide. Preserve the error, inspect pod/container inventory, identify which object is intended to remain, and free only this lab's resources. Do not use `--replace` on an unreviewed manifest as the first response; replacement tears down previous resources and can cause downtime.

Suppose the second host accepts the pod but cannot pull its image. YAML validity is irrelevant to registry DNS, TLS, authorization or architecture support. Inspect the pull error and manually test the approved image reference under the same account. A private registry's credentials available in an interactive user's runtime directory may be absent in an unattended service. Chapter 70 explains how to diagnose that execution-context difference.

Suppose a helper expects a shared file at `/data/config.json` and fails even though another member has it. Inspect each container's mounts. Namespace sharing does not share writable layers. Use an explicitly declared shared volume if that is the correct contract, and decide whether the content is immutable configuration, temporary exchange data or durable application state. Those categories have different ownership and recovery requirements.

For rollback, preserve the previous approved manifest and image digest. Stop the failed fixture, restore the known configuration and verify the same HTTP path. For data-bearing services, assess whether the previous image can consume data written by the replacement. Pod grouping does not provide transactional rollback across members or automatically reverse migrations.

Teardown uses the same manifest's pod identity:

```bash
podman --remote=false kube down dd-fixture.yaml
podman --remote=false pod ps
rm -- generated-pod.yaml dd-fixture.yaml
cd "$HOME"
rmdir -- "$HOME/dd-kube-65"
```

`kube down` removes resources associated with this local lab file. Verify the target names and storage implications before using it on a data-bearing deployment. An unexpected remaining file should be inspected before broadening cleanup.

## Exercises and review questions

1. Explain why loopback succeeds for the BusyBox pod member but not for Chapter 64's unrelated client. **Guidance:** compare network namespace membership.
2. Add a second process attempting to bind port 80 in a disposable copy. Predict the failure. **Guidance:** members share the port namespace; filesystem separation does not prevent the collision.
3. Review a generated manifest for portability. **Guidance:** images/digests/platform, paths, IDs, port availability, annotations, supported fields and separate data transfer.
4. Name what is missing for multi-host availability. **Guidance:** placement, replication, health-driven reconciliation, network service discovery and data replication are separate mechanisms.

## Takeaways and further reading

Pods make shared-host boundaries explicit. Generation and playback transfer supported intent, not an entire operating environment. Continue with [Quadlet and systemd](066-quadlet-and-systemd-integration.md).

The pod-create, kube-generate and kube-play primary manuals were inspected 2026-10-03. No pod, YAML playback, host transfer or Kubernetes API validation was executed by the author.
