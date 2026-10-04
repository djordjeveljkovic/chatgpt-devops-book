---
book: The Complete DevOps Engineering Book
volume: 18
volume_title: "Security and Software Supply Chains"
chapter: 175
title: "Secrets and Credential Rotation"
slug: secrets-and-credential-rotation
status: complete
summary: ../../_ai/chapter-summaries/175-secrets-and-credential-rotation.md
---

# Chapter 175 — Secrets and Credential Rotation

**Section outline:** classify secret material and choose a delivery boundary; compare managed stores and Vault lease/rotation patterns; contain a leaked DispatchDesk credential and prove the old authority is gone.

## Secret distribution and lifecycle

A secret is any value whose disclosure or misuse grants authority: a database password, API token, private key, signing key, recovery code, session cookie or bootstrap credential. Encryption at rest protects stored material from some forms of storage access, but does not protect a value from an application or operator authorized to retrieve it. The core lifecycle is creation, narrowly scoped delivery, use, renewal or rotation, revocation, and evidence that old copies no longer work.

Map each credential to its authority and consumers. A credential used by one worker should not also administer the database or deploy the cluster. Give separate identities to humans, CI jobs, workloads and recovery automation. Prefer short-lived federated credentials or workload identity over long-lived passwords when the provider and application support them; [Chapter 176](176-federation-oidc-and-short-lived-identity.md) covers federation. If a static credential is necessary, limit its permissions, network reach, lifetime and audience. Record an owner and a tested revocation path when it is issued.

Choose a delivery path that matches the workload. A managed cloud secret service can enforce access through cloud identity and maintain versions, audit events and rotation integrations. A self-hosted store such as Vault can issue dynamic credentials with leases, but the team must operate its availability, storage protection, unseal/recovery process, policies, audit devices and integrations. Kubernetes Secrets provide a namespaced API object for distributing values to authorized workloads; base64 encoding in manifests is not encryption. Restrict RBAC, enable encryption at rest according to cluster requirements, protect etcd and backups, and keep Secret values out of version control. See [Chapter 174](174-kubernetes-security-boundaries.md) and [Chapter 203](../21-projects-and-industry-case-studies/203-the-managed-aws-company.md) for related cluster and managed AWS contexts.

Do not place secret values in source files, image layers, Docker build arguments, shell command lines, logs, CI artifacts or diagnostic bundles. Environment variables are easy to consume, but often propagate into process inspection, crash reports or child processes, and changing a secret in a manager does not change the environment of an already running process. Mounted files can support refresh without putting values in command arguments, but the application must reopen or reload them safely. A sidecar or agent may fetch secrets directly, but that adds identity, network, availability and update behavior that must be secured. Choose one documented path and test the consumer's reload behavior instead of assuming that storage updates reach the running process.

For Kubernetes delivery, a Pod can consume Secret values as environment variables or mounted files. Environment variables are populated when the container starts; rotating the Secret object does not rewrite those existing process variables, so rollout/restart is generally needed for a consumer to read the new value. A Secret volume is updated eventually when the kubelet refreshes its projection, but applications may still cache file contents or keep an old connection open. A `subPath` mount does not receive automatic updates. These details make rollout and connection-pool behavior part of the rotation plan, not a Kubernetes implementation footnote.

Protect the whole path, not only the secret-manager database. The application identity must be authenticated to the manager. A token used to retrieve the database password is itself a secret. Restrict which workloads can request which secret, which namespaces and service accounts can mount Kubernetes Secret objects, and which CI environments expose release credentials. Keep access logs and avoid logging values on error. A secret manager cannot prevent an authorized but compromised process from exfiltrating a value it needs to use.

## Vault, cloud secrets and rotation

Rotation means changing the credential at the service that accepts it and updating the authoritative secret consumers retrieve. Updating one side only creates a mismatch. Design the transition around overlap: can the target accept two keys or users temporarily, can consumers reload without dropping in-flight work, how do you verify the new credential, and how quickly can the old one be revoked? Some systems permit a second active key; others allow only a single password. For the latter, use a maintenance window, dual-user strategy or controlled outage plan rather than promising zero downtime.

Vault's database secrets engine can generate separate database identities for workloads. A dynamic secret comes with a lease and time to live. The consumer must renew it when allowed or obtain a replacement before expiry; Vault can revoke the lease and run the configured database revocation behavior. This reduces long-lived shared credentials and improves attribution, but it requires consumers to handle renewal, connection rotation and Vault outages. A short TTL with an application that reads credentials only at startup turns routine Vault unavailability into an outage when the process restarts. Choose a TTL longer than the expected refresh/recovery interval, and test the renewal path and revocation effects.

Static credentials need a rotation workflow. HashiCorp Vault can manage a static database role and periodically change a password while keeping a known username; its database configuration still relies on privileged root credentials that must also be maintained. AWS Secrets Manager supports managed rotation for certain integrations and Lambda-based rotation for other secrets. Its documented Lambda workflow uses four steps: create a pending version, set the new credential on the target, test that credential, then finish by moving the current version label. This order makes the update retryable and leaves a previous version for recovery, but the target, network and consumers still determine whether the rotation succeeds safely. Do not invent a universal rotation interval: select one based on credential authority, exposure, provider capabilities, maintenance risk and incident response objectives.

Consumers must respond to new versions. For a service that reads a file at startup, the rotation controller may update a mounted file but still need to restart or signal the service. For a database connection pool, create new connections with the new identity, verify them, then drain old connections before revoking the old account. For an API key, deploy a new key to all consumers, observe successful use, and then disable the old key. A version label moving in a secret manager proves a metadata transition, not that every consumer fetched the new version or stopped using the old credential.

Use a two-credential rollout where the target supports it:

1. Create a new credential with the same narrow permissions and a distinct identifier where possible.
2. Store the new version and release it to a small canary consumer.
3. Verify authentication, expected permissions, latency and error rates with the canary.
4. Roll the new credential to remaining consumers, reload/restart as needed, and verify every instance has transitioned.
5. Revoke the old credential at the target, test that it fails, and record the change and remaining copies to clean up.

For a single-password target that cannot accept both credentials, schedule and coordinate the target change and consumer rollout as one controlled operation. Keep an authorized break-glass path and a tested rollback sequence, but avoid leaving an old credential active indefinitely because rollback is convenient. Rollback may require issuing a third credential rather than reactivating a compromised value.

## Recovering from a leaked credential

DispatchDesk's worker uses a database password delivered from a managed secret service. A deployment job prints a debug environment dump to its log, including the password. The incident responder edits the manager's secret value but leaves the database credential unchanged, then restarts one worker and sees a successful health check. That worker reads the new manager value and fails when it opens fresh database connections, while already-established sessions may continue until closed or separately terminated. An unrefreshed worker and an untracked test client still hold the leaked old password, which continues to authenticate because the target database credential was not disabled. Updating the manager changed what future reads return; it did not revoke the accepted database credential or refresh every consumer.

Containment begins by identifying the credential's authority and exposure. Preserve the relevant CI run ID, access logs, deployment revision, secret version metadata, workload identity, database audit events and affected time range. Restrict access to the log artifact and remove unnecessary copies according to retention and evidence policy; do not paste the credential into an incident ticket. Identify every consumer and any systems reachable with the credential. Revoke the credential at the target service as soon as the containment plan permits, because removing or editing the secret-manager entry alone may not invalidate already issued material.

For the database incident, create a replacement role with only the worker's required schema privileges, place its password in a new secret version, and update one worker. Verify a new database connection uses the replacement identity, the worker can complete a representative job, and audit evidence attributes it to that account. Roll the replacement to the remaining workers, observe connection errors and queue age, and drain the old pool. Then disable the leaked database account and test rejection from a controlled connection attempt. If the database cannot accept two users, coordinate a brief credential cutover with explicit rollback and customer-impact limits.

After rotation, inspect consumers and copies. Search CI history and artifact stores using the run identifier and secret version metadata, not by reprinting the value. Revoke derived tokens and sessions if the credential could mint them; rotate dependent secrets if they were available from the same process. Confirm the old identity is disabled at the authority source, review access logs for unexpected use, and test the failure of the old credential without putting it in shell history. If a private key leaked, revoke or replace the corresponding certificate/key at every relying system; deleting the local file is not revocation.

The failed assumption in this incident was that “secret changed” meant “credential revoked everywhere.” Keep separate fields in the response record for secret-store version, target-system status, consumer rollout, old-value revocation, validation evidence, and remaining exposure. Preserve evidence before deleting CI artifacts, then apply the organization's retention and incident policy. Document owners, deadlines, customer impact, uncertain access and follow-up controls. Fix the workflow that printed the environment, add redaction/secret scanning where applicable, and test a leak drill with a disposable credential. Detection tools can miss values transformed or encoded by a process, so prevention and short-lived authority still matter.

Exercises:

1. A Kubernetes Secret object is updated, but pods consume the value as an environment variable. What must happen before the process can use the new value, and what failure should be observed during rollout?
2. A Vault dynamic database credential has a 30-minute lease, but the application opens connections only at startup. What renewal, refresh and outage behaviors must be designed?
3. A leaked API key is removed from the cloud secret manager. List the evidence needed before the incident can claim the key is no longer usable.

Answer guidance: environment variables are fixed in the running container, so replace/restart the workload or use an explicitly designed reload path; monitor readiness, authentication failures, in-flight work and rollback. The Vault consumer needs a lease renewal/reissue path before expiry, a way to refresh credentials and create new connections, and a defined response to Vault unavailability or revocation. The API key must be disabled at the target provider, sessions/tokens derived from it revoked where supported, all consumers migrated, old-key rejection tested, provider audit logs reviewed, and remaining copies/uncertainty recorded. Secret-store deletion alone is not proof of revocation.

Review questions:

- Which control protects secret storage, and which controls protect delivery, process use and revocation?
- Why should rotation be designed as a consumer transition instead of a scheduled write to a secret manager?
- What changes when a target supports only one active credential instead of two?

Takeaways:

- Track a secret from authority and owner through delivery, consumer reload, target-side rotation and revocation.
- Prefer narrow, short-lived credentials, while designing for manager outages and application refresh behavior.
- Staged rotation needs evidence from both the secret store and the system that accepts the credential.
- During a leak, preserve evidence, contain the authority at its source, migrate all consumers, and test old-value rejection.

## Sources checked 2026-10-04

- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) — object exposure, encryption-at-rest context and consumption behavior.
- [HashiCorp Vault leases](https://developer.hashicorp.com/vault/docs/concepts/lease) and [database secrets engine](https://developer.hashicorp.com/vault/docs/secrets/databases) — dynamic credentials, TTL, renewal, revocation and static-role rotation.
- [AWS Secrets Manager rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html) and [Lambda rotation functions](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotate-secrets_lambda-functions.html) — supported rotation approaches and pending/current version transition.
- [Docker build secrets](https://docs.docker.com/build/building/secrets/) — secret mounts and build-time secret exposure.

These vendor procedures were checked on the listed date. No secret manager, database, Kubernetes cluster, CI log, credential rotation, leak containment, or revocation test was operated.
