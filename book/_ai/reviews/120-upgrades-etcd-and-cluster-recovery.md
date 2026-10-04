# Independent review — Chapter 120

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: 27a7737f79b473c095a7cc74b82ded58c6115e8e246d3bc3177c7cb56856342c

## Findings

No material findings. Re-review confirms the restore sequence now explains revision rollback, informer/watch-cache inconsistency, version-matched revision bump and marking bumped revisions compacted. It requires sizing the bump above intervening revision growth using backup age/write rate and the exact installed-version runbook; no generic runnable recovery command or invented bump is provided. Post-restore controller progress and API/workload validation remain required.

## Scope and dated primary evidence

Read full body, summary, guide, SKELETON brief and Chapter 119 prerequisite. Compatibility/staged upgrade, control-plane backup/recovery and failed upgrade/quorum scenario cover the brief. Exercises include answer guidance and reconstruction evidence. Five kubectl reads pin context and correctly use cluster scope or all namespaces; no upgrade/drain/snapshot/restore execution occurs. Sensitive snapshot/credential boundaries are explicit. The fictional quorum-retained case correctly favors repair rather than snapshot rewind, and isolated restore is distinguished from measured success. Cluster/API state and application data backups, key dependencies, failure-domain copies and RTO/RPO evidence are correctly separate.

Official primary sources inspected 2026-10-04: [Version skew policy](https://kubernetes.io/releases/version-skew-policy/) confirms no skipped API-server minors and drain before minor kubelet upgrade; [kubeadm upgrades](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/) supports first/additional control-plane then worker sequence and separate integrations; [Operating etcd](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/) supports quorum, snapshot sensitivity and distribution-specific restoration; [etcd 3.6 recovery](https://etcd.io/docs/v3.6/op-guide/recovery/) and [3.7 recovery](https://etcd.io/docs/v3.7/op-guide/recovery/) support new logical cluster/member identity, snapshot integrity, etcdctl save versus etcdutl restore, revision-bump/compaction caveat and avoiding stale membership. General claims are appropriately version-qualified without fixed package instructions. Ubuntu/Fedora/RHEL installation changes are delegated to supported exact distribution/release runbooks. Summary accurately records no live restoration.

## Validation and limits

`python tools/check_book.py --chapters 120-120` passed on 2026-10-04: one draft chapter, one shell syntax block and 1,389 global local-link checks; no errors/warnings. Body hash calculated using tools.promote_reviewed.body_hash. No Kubernetes reads, host commands, provider calls, kubeadm upgrade, drain, etcd membership change, snapshot save/restore, key/certificate operation or application recovery occurred. No installed release/topology, OS matrix, actual quorum, snapshot integrity, revision handling, controller-cache behavior, provider contract or measured RTO/RPO was tested. Static/documentation review establishes mechanism rather than live resilience and does not exhaustively verify external links. Only this separate review record was written.

Verdict: approved
