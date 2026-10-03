---
book: The Complete DevOps Engineering Book
volume: 11
volume_title: "Kubernetes Foundations"
chapter: 106
title: "ConfigMaps, Secrets and Configuration"
slug: configmaps-secrets-and-configuration
status: complete
summary: ../../_ai/chapter-summaries/106-configmaps-secrets-and-configuration.md
---

# Chapter 106 — ConfigMaps, Secrets and Configuration

## Configuration injection and updates

An image should describe the program; deployment-specific configuration should describe where and how that program runs. A staging API and a production API can use the same immutable application image while receiving different database endpoints, feature settings and resource limits. Kubernetes provides ConfigMaps for non-confidential values and Secrets for confidential values. These objects make configuration available to Pods as environment variables, command arguments or mounted files. They do not validate that an application accepts the values, nor do they automatically make a running process reload them.

Chapter 105 introduced the DispatchDesk API Service. The following ConfigMap provides two non-sensitive settings for its application:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dispatchdesk-api-config-v1
  namespace: production
data:
  LOG_LEVEL: "info"
  PUBLIC_API_BASE_URL: "https://api.example.invalid"
```

The `.data` field stores UTF-8 strings. `binaryData` is available for non-UTF-8 bytes, but it does not turn configuration into a file distribution system for large artifacts. Keep values small, version controlled and suitable for the access policy governing the namespace. Do not put passwords, signing keys or private certificates in a ConfigMap. ConfigMaps are not encrypted secret stores.

A container can import individual keys as environment variables or import a set of valid environment-variable names using `envFrom`. It can also consume a ConfigMap as files in a volume. A Deployment template might mount the settings as files and import only the log level as an environment variable:

```yaml
spec:
  template:
    spec:
      containers:
        - name: api
          image: registry.example.invalid/dispatchdesk/api@sha256:REPLACE_WITH_VERIFIED_DIGEST
          env:
            - name: LOG_LEVEL
              valueFrom:
                configMapKeyRef:
                  name: dispatchdesk-api-config-v1
                  key: LOG_LEVEL
          volumeMounts:
            - name: application-config
              mountPath: /etc/dispatchdesk
              readOnly: true
      volumes:
        - name: application-config
          configMap:
            name: dispatchdesk-api-config-v1
```

This is a Pod template excerpt, not a complete Deployment. It assumes the ConfigMap exists in `production`, the image is replaced by a verified digest, and the application knows how to read the mounted file paths. A missing referenced key or object can prevent a container from starting. Mounting the ConfigMap directory projects each key as a file; setting `items` can restrict keys and choose paths. Mounting over a directory already populated by the image can hide those original files, so choose the mount path deliberately. Mounting a single key with `subPath` is convenient for file layout but does not receive updates to the ConfigMap.

Kubernetes eventually updates a normal ConfigMap volume projection after the source ConfigMap changes. The delay depends on kubelet synchronization and its change-detection strategy. The application sees a new file only if it reads it again or watches for changes; software that loads config only at startup continues using old in-memory settings. Environment variables are snapshots taken when the container process starts. Updating the ConfigMap does not mutate a process's environment, so Pods must be replaced to receive new environment-variable values. An application should define its reload contract: poll and validate a file, watch for atomic replacement, or restart on an intentional template update. See the official [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/) and [update tutorial](https://kubernetes.io/docs/tutorials/configuration/updating-configuration-via-a-configmap/).

Do not treat a ConfigMap update as an atomic fleet-wide rollout. Some replicas can see new files before others, and application instances can retain different in-memory values for a period. If the setting changes protocol or data semantics, design backward-compatible transitions and coordinate a versioned rollout. For simple values that applications read at startup, changing the object name and updating the Pod template makes the transition visible in Deployment revision history. Immutable, versioned ConfigMaps also prevent accidental in-place mutation; changing values means creating a new object and updating the reference.

## Secret boundaries and application reload

A Kubernetes Secret is an API object for confidential data, not an encryption guarantee by itself. Secret values in the `data` field use base64 encoding. Encoding is reversible and provides no confidentiality. By default, Kubernetes stores Secret data unencrypted in etcd unless cluster administrators configure encryption at rest. Access through the API is controlled by RBAC, and anyone allowed to create a Pod in a namespace can often arrange to expose Secrets from that namespace to a container. Keep permissions narrow, restrict each Secret to the containers that need it, and configure encryption at rest and audit according to cluster policy. For broader guidance, see [Kubernetes Secret good practices](https://kubernetes.io/docs/concepts/security/secrets-good-practices/) and [encryption at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/).

Never commit a real credential or a base64-encoded credential to Git. Base64 does not make a checked-in value safe. A Secret manifest using `stringData` is readable plaintext source, while `data` can be trivially decoded. Prefer an approved external secret manager or controlled secret-delivery workflow. For a local isolated exercise, create the Secret from an already secured file whose path and permissions are managed outside the repository. The command below reads the file; it does not print its content, but the resulting Secret is still stored in the cluster API and protected only by that cluster's controls:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  create secret generic dispatchdesk-db-v1 \
  --from-file=password=/secure/local/path/dispatchdesk-db-password
```

The file must exist on the workstation running kubectl, contain only the intended password bytes, and be readable by that user. The command creates a namespace-scoped Secret and fails if the name already exists. Do not replace the path with an actual credential in shell history or paste a credential into a shared terminal. If an exercise creates a test Secret, remove it after validating the Pod and use only a disposable cluster. In production, Secret lifecycle, access audit, rotation and revocation belong to the credential management process.

After all test Pods have stopped using the exercise Secret, remove only the object created above:

```bash
kubectl --context kind-dispatchdesk --namespace production \
  delete secret dispatchdesk-db-v1
```

Deletion prevents new Pod references from resolving the object but does not revoke a credential at its upstream database or erase every historical copy, backup or audit record. Complete upstream revocation and data-retention actions through the credential-management process.

A Secret can be exposed to a container through an environment variable or a read-only volume. Environment variables are straightforward for libraries that expect them, but they remain available to the process and may leak through diagnostics, crash reports, subprocesses or overly broad inspection. A mounted file avoids some environment handling but the application still must keep the value private after reading it. Mount only the Secret into containers that need it; containers in the same Pod do not automatically share a mount unless the Pod template grants it. Avoid logging credentials, including them in error messages, or returning them in health endpoints.

For the DispatchDesk database password, the Pod template can reference one key without embedding the value in the Deployment:

```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: dispatchdesk-db-v1
        key: password
```

The object and key must exist before the Pod can start. As with ConfigMaps, changing the Secret does not update an already running environment variable. Updating a Secret used as a projected volume eventually updates the mounted files, subject to kubelet propagation and the `subPath` limitation. The application must reread the new bytes and safely switch connections or keys. A Secret rotation is not complete merely because the API object changed: confirm every relevant process has adopted the new value, the old credential has been revoked at the upstream system, and rollback no longer depends on the revoked credential.

Kubernetes Secrets have practical size and access limitations, and cluster policy can add its own constraints. Very sensitive credentials may be better fetched at runtime from a dedicated secret manager through a workload identity or provider integration. That design shifts dependencies to identity configuration, network reachability, provider availability and refresh logic. Chapter 109 covers persistent state; this chapter does not prescribe a particular cloud secret service or assume one is installed.

## Changing configuration predictably

Consider a planned change from a read-only DispatchDesk database endpoint to a new schema-compatible endpoint. An operator edits the ConfigMap and sees the object update, but some replicas continue using the old endpoint because they read configuration only during startup. Other replicas mounted the projected file and reload at different times. A single mutable name now hides the transition, and a quick rollback by editing the same object may leave replicas with mixed values. The recovery begins by identifying how the application consumes each key, which version each replica loaded, and whether both endpoints are safe during overlap.

A predictable pattern is to treat config as a versioned input to the workload. Create `dispatchdesk-api-config-v2`, validate the non-secret values, update the Pod template to reference it, and let the Deployment roll out with the image and readiness contract. The changed Pod template creates a new revision. Wait for all replicas to become available and verify the application behavior before removing the prior ConfigMap. This offers an auditable change and rollback target, but only if the old endpoint and configuration remain valid for the rollback window. Do not delete old versions while live Pods still reference them.

For a Secret rotation, stage the new credential with a distinct versioned Secret name, update the workload reference, and confirm every new Pod uses it. If the application supports safe live reload from a projected file, the object may be updated in place, but you still need observable adoption and a defined overlap period. Revoke the old credential only after all legitimate consumers have moved. For high-risk keys, plan the sequence with the upstream system's rotation semantics; some databases permit overlapping credentials, while others require a coordinated cutover. Never print the secret to prove it loaded. Check an authenticated health operation or connection state that does not expose the value.

Immutable ConfigMaps and Secrets can make accidental changes harder and reduce API watch work for large clusters. Once an object is immutable, its data cannot be changed back to mutable or edited in place; create a new version and update the workload reference. Immutability does not prevent deletion, restrict who can read the data, encrypt etcd, or force an application reload. It is a consistency aid, not a complete security or deployment strategy.

For any configuration change, define observable evidence before changing the object: expected Deployment revision, ready replica count, application configuration version or non-sensitive behavior check, and a rollback plan. Use `kubectl describe` and events to diagnose a Pod blocked by a missing ConfigMap or Secret; inspect only object metadata and keys when necessary, not decoded credentials. If a bad setting causes failures, restore a known compatible version through the workload's source of truth, then confirm all replicas converge. Avoid `kubectl edit` as the only record of a production change because the configuration source will drift and later automation may overwrite it.

## Exercises and answer guidance

1. A ConfigMap volume shows updated file contents, but application behavior is unchanged. What is likely missing? The process has not reloaded the file or its own cache; define and verify an application reload path.
2. A Pod uses a ConfigMap key in an environment variable. Will updating the ConfigMap change the running process value? No. Replace the Pod through a controlled rollout so the process starts with the new environment.
3. Why is a Secret with base64 data safe to commit? It is not. Base64 is reversible encoding; anyone with repository access can recover the value.
4. The team rotates a Secret but does not know whether all Pods adopted it. Is it safe to revoke the old credential? Not yet. Establish adoption evidence or use an overlap window before revocation.
5. A Pod mounts one ConfigMap file with `subPath` and does not see a later change. What design should be considered? Mount the directory or use versioned config plus a Pod template rollout; `subPath` projections do not receive updates.

Review questions: which configuration belongs in ConfigMaps versus Secrets, when does each consumption method observe a change, what does Kubernetes Secret storage protect by default, and how can a versioned rollout make rollback and adoption observable?

## Verification and primary sources

Official Kubernetes ConfigMap, Secret, Secret good-practices, encryption-at-rest and update-tutorial documentation was inspected on 2026-10-04. YAML and shell examples are illustrative; no Secret or ConfigMap was created and no credential was handled. The Secret command uses a fictitious local path and requires an externally secured file. Static checks do not verify cluster RBAC, etcd encryption, application reload behavior, credential rotation or provider integrations.

Primary references: [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/), [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/), [Secret good practices](https://kubernetes.io/docs/concepts/security/secrets-good-practices/), [updating ConfigMaps](https://kubernetes.io/docs/tutorials/configuration/updating-configuration-via-a-configmap/), and [encrypting confidential data at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/).
