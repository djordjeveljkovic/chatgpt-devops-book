---
book: The Complete DevOps Engineering Book
volume: 20
volume_title: "Architecture and Platform Engineering"
chapter: 192
title: "Platform Teams and Developer Experience"
slug: platform-teams-and-developer-experience
status: draft
summary: ../../_ai/chapter-summaries/192-platform-teams-and-developer-experience.md
---

# Chapter 192 — Platform Teams and Developer Experience

Atlas has several teams deploying services. Each repeatedly assembles health checks, image references, resource settings, release jobs and ownership labels. A platform can make that recurring operating task easier, provided it offers a useful contract and owns the resulting maintenance. A portal is one possible interface; the product is the supported capability behind it.

Harbor's two developers may need only a documented service template and a reliable deployment command. Summit may benefit from managed AWS components with a small standard release interface. Choose a platform investment from observed repeated work and operating constraints, rather than adopting Atlas's topology as a required destination. [Chapter191](191-monoliths-services-and-organizational-boundaries.md) establishes workload/team boundaries; the Kubernetes and delivery volumes supply the underlying mechanisms.

## Find the recurring task

Interview an internal user while they perform a real deployment. Record where they wait, which decisions they understand, what errors they encounter and who resolves them. “Provision a service” may actually include account access, secret enrollment, artifact custody, DNS, monitoring and support ownership. Automating just YAML generation can leave most elapsed time unchanged.

Distinguish task time from waiting and recovery time. In an explicitly hypothetical Atlas sample of ten onboarding attempts, developers spend30 minutes entering configuration, wait six hours for credentials and spend another90 minutes correcting undocumented health-path assumptions. A prettier form may improve the first30 minutes while leaving the dominant problems intact. A useful first increment could establish the credential workflow and a tested application contract.

The CNCF platform paper describes platforms as curated capabilities for internal users and emphasizes their needs and value. We apply that idea by selecting a measurable task and a supported interface; a large catalog is not required to start. See the [CNCF Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/).

## Define a small supported contract

For this original lab, Atlas's initial path supports one type of stateless HTTP API in a preexisting staging namespace. It accepts an application name, owner, immutable image reference and replica count. It renders a Deployment and an internal Service. It deliberately excludes public routing, database provisioning, autoscaling and secret creation, each of which needs its own authority and lifecycle.

| Application promise | Platform promise | Verification needed |
|---|---|---|
| Listens on port8080 and respects `PORT` | Supplies the configured port and internal Service | Client test through the Service. |
| Implements `/healthz` and `/readyz` with the canon's semantics | Supplies separate probes with bounded timings | Actual startup, dependency and recovery behavior. |
| Runs as UID10001 with a read-only root filesystem | Supplies restricted security context and writable `/tmp` | Image/filesystem compatibility test. |
| Reads `DATABASE_URL` and logs to standard output | References an existing approved Secret and exposes owner metadata | Access, rotation, log handling and application acceptance. |
| Fits a measured envelope | Supplies illustrative staging requests/limits | Load/pressure evidence before adopting production values. |

The resource numbers below are teaching defaults, not a measured DispatchDesk sizing recommendation. Replica count is bounded to keep the lab input simple; it is not a global capacity or quota policy. The API image must satisfy the stated contract and be retrievable by the cluster. An image using local SQLite for authoritative state does not qualify as this stateless path.

## Complete local rendering lab

Use Python3 in a disposable user-owned directory on Ubuntu or Fedora/RHEL. Save `service-request.json`; the reserved registry name and all-zero digest are placeholders for rendering only. Replace them with a real reviewed image before any cluster operation.

```json
{
  "name": "dispatchdesk-api",
  "owner": "orders-team",
  "image": "registry.example.invalid/team/api@sha256:0000000000000000000000000000000000000000000000000000000000000000",
  "replicas": 2
}
```

Save the following complete `render_service.py`:

```python
import json
import re
import sys
from pathlib import Path

def render(request):
    fields = {"name", "owner", "image", "replicas"}
    if not isinstance(request, dict) or set(request) != fields:
        raise ValueError("required fields: name, owner, image, replicas; no extras")
    for field in ("name", "owner"):
        value = request[field]
        if not isinstance(value, str) or not re.fullmatch(r"[a-z](?:[a-z0-9-]{0,38}[a-z0-9])?", value):
            raise ValueError(f"invalid {field}: use 1-40 lowercase letters/digits/hyphens")
    image = request["image"]
    if not isinstance(image, str) or not re.fullmatch(r"[^\s]+/[^\s]+@sha256:[0-9a-f]{64}", image):
        raise ValueError("image must include a registry/path and sha256 digest")
    replicas = request["replicas"]
    if type(replicas) is not int or not 1 <= replicas <= 3:
        raise ValueError("replicas must be an integer between 1 and 3")
    name = request["name"]
    labels = {"app": name, "owner": request["owner"]}
    metadata = {"name": name, "namespace": "dispatchdesk-staging", "labels": labels}
    probe = {"port": "http"}
    container = {
        "name": "api", "image": image,
        "ports": [{"name": "http", "containerPort": 8080}],
        "env": [
            {"name": "PORT", "value": "8080"},
            {"name": "DATABASE_URL", "valueFrom": {"secretKeyRef": {
                "name": "dispatchdesk-db", "key": "url"}}}
        ],
        "readinessProbe": {"httpGet": dict(probe, path="/readyz"),
                           "periodSeconds": 5, "timeoutSeconds": 2},
        "livenessProbe": {"httpGet": dict(probe, path="/healthz"),
                          "initialDelaySeconds": 30, "periodSeconds": 10},
        "resources": {"requests": {"cpu": "100m", "memory": "128Mi"},
                      "limits": {"cpu": "500m", "memory": "512Mi"}},
        "securityContext": {"allowPrivilegeEscalation": False,
                            "readOnlyRootFilesystem": True,
                            "capabilities": {"drop": ["ALL"]}},
        "volumeMounts": [{"name": "tmp", "mountPath": "/tmp"}]
    }
    deployment = {
        "apiVersion": "apps/v1", "kind": "Deployment", "metadata": metadata,
        "spec": {"replicas": replicas, "selector": {"matchLabels": {"app": name}},
                 "strategy": {"type": "RollingUpdate", "rollingUpdate": {
                     "maxSurge": 1, "maxUnavailable": 0}},
                 "template": {"metadata": {"labels": labels}, "spec": {
                     "automountServiceAccountToken": False,
                     "securityContext": {"runAsNonRoot": True, "runAsUser": 10001,
                                         "runAsGroup": 10001, "fsGroup": 10001,
                                         "seccompProfile": {"type": "RuntimeDefault"}},
                     "containers": [container],
                     "volumes": [{"name": "tmp", "emptyDir": {"sizeLimit": "64Mi"}}]}}}
    }
    service = {
        "apiVersion": "v1", "kind": "Service", "metadata": metadata,
        "spec": {"selector": {"app": name}, "ports": [
            {"name": "http", "port": 8080, "targetPort": "http"}]}
    }
    return {"apiVersion": "v1", "kind": "List", "items": [deployment, service]}

def main():
    if len(sys.argv) != 2:
        raise ValueError("usage: render_service.py service-request.json")
    request = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(render(request), indent=2, sort_keys=True))

if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
```

Generate and inspect:

```bash
python3 render_service.py service-request.json > rendered.json
python3 -m json.tool rendered.json
```

The first command reads the input and writes JSON to standard output, which the shell redirects to a local file. It creates no cluster objects. The second parses and displays that file. In the workshop, a render failure can truncate the redirected destination; production tooling should preserve previously accepted output with a validated temporary file and atomic publication as taught in [Chapter018](../02-linux-and-automation/018-shell-automation-that-survives-failure.md).

Change `replicas` to0, add an unexpected `privileged` field and replace the digest with a mutable tag in separate fixtures. Each must fail with a nonzero exit and diagnostic. The image regex checks a limited shape; it does not resolve the registry, implement the full OCI naming grammar or verify provenance. The all-zero placeholder passes shape validation and remains unusable for deployment. That distinction prevents an input validator being mistaken for an artifact trust system.

## Interpret the generated policy

The Deployment keeps one stable app selector and adds owner labels separately, so changing team ownership does not require changing its immutable selector. Its rollout permits one extra replica and zero desired unavailability; it still requires spare node/dependency capacity and does not promise uninterrupted service. Kubernetes documents these semantics in [Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).

The Service selects the same app label and targets the container's named HTTP port; it creates an internal routing abstraction, not a public endpoint. See [Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/). Probes express different questions and need timings justified by actual startup behavior, as described in [probe configuration](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/).

The container references `dispatchdesk-db` key `url` in the same preexisting namespace. This requires an approved Secret and database/access configuration established through the canonical secret workflow; the renderer never receives the secret value. See [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/). The pod group settings allow the nonroot process to use the temporary volume; its size setting still needs workload/storage enforcement observation. The fixed probe timings require compatible startup behavior or an explicitly adjusted path. The restricted context and writable temporary mount follow documented [security-context fields](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/). The [resource-management reference](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) explains why requests, limits and measured use are different.

Before deploying a real rendered file, review identity/context, existing ownership and server validation through [Chapter214](../22-operational-reference/214-kubernetes-command-and-object-reference.md). Namespace, Secret, artifact retrieval, network/database access, telemetry and policy must already be established. Apply through the intended release/GitOps controller; do not let a developer's generated file silently become a competing production owner. Delete only lab objects created through that controller and dispose of local files after retaining results.

## Scaffolding is not ongoing operation

A template can create initial files or repositories. Backstage documents software templates that load a skeleton, substitute values and publish/register a component; see [Backstage Software Templates](https://backstage.io/docs/features/software-templates/). That is a useful interface, but it does not automatically update every generated service when a security default changes.

Decide whether generated output is a copied starting point, a versioned shared module or desired state continuously reconciled by a controller. Each choice changes upgrade ownership. A copied template can diverge; a shared module can introduce a large simultaneous blast radius; a controller can overwrite uncoordinated manual changes. Give users a supported update path with version compatibility, staged rollout and known reversal limits.

Authorization is also separate from validation. The `owner` label above is supplied by the request and carries no identity proof. Production tooling must derive or verify ownership from trusted identity and policy. A local “replicas<=3” rule is bypassable if users can create arbitrary cluster objects directly. Enforcement belongs to the appropriate API/admission/permission boundary, with exceptions explicit and audited.

## Measure value and handle exceptions

Measure the user's completed task: time to a working supported deployment, first-attempt success, recovery time, unplanned support effort and ability to operate without hidden knowledge. Track population and distribution, not just averages. More generated repositories can mean more abandoned services rather than more useful adoption.

Provide an exception path for workloads outside the contract, such as a Java service with different startup/resource needs or a specialized worker without HTTP semantics. An escape hatch identifies the unsupported behavior, owner, operating obligations and review trigger. Repeated exceptions can reveal a missing useful capability; a one-off workload need not force all users into a more complex contract.

During a platform outage, application teams need to know which capabilities are affected. A portal failure might leave existing services healthy while onboarding stops; a broken shared admission/controller update can affect deployment or availability much more broadly. Keep the platform's own dependencies, support and recovery procedures visible and test controlled upgrades before expanding adoption.

1. Explain why the renderer's successful output cannot certify image trust, owner identity or database readiness. Good answers identify the missing authoritative checks.
2. Compare copied templates with a shared module upgrade. Identify divergence and blast-radius costs, then choose a staged maintenance path.
3. Atlas's adoption count rises while deployment waiting time remains six hours. Revisit the observed task and credential bottleneck before adding portal features.

The original renderer and JSON fixtures are a local teaching implementation. Primary platform and Kubernetes sources were inspected on2026-10-01; the renderer was executed with Python3.14.7 and its Deployment/Service JSON parsed. Invalid replica count, extra field, mutable tag, trailing-hyphen name and boolean count were rejected with status1 and no output. The owned temporary directory was removed; server validation/deployment was not executed. No Backstage installation, cluster resources or production platform were created during writing.
