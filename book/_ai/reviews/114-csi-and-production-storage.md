# Independent review — Chapter 114

Reviewer: review_volume3_026_030
Date: 2026-10-04
Reviewed body SHA256: d86f3f03100653961eb78977f343304387bc317d980c805fb8100d52c86d5dc2

## Findings

No material findings. Low optional clarification in exercise 5: PVC/PV Delete reclaim policy does not generically delete independent CSI snapshots. Their backing-snapshot lifecycle is governed separately by snapshot deletion policy and backend behavior, already correctly explained in the snapshot section. Prefer “backing volume/data; independently verify snapshot retention” to “backing volume and snapshot/data.”

## Scope and dated primary evidence

Read complete body, summary, brief, authoring guide and relevant Chapter 109/113 prerequisites. Drivers/topology/snapshots, access modes/expansion/recovery and attachment diagnosis cover the brief. Commands are six observational reads, context pinned, with namespaced PVC/Pod and cluster-scoped PV/StorageClass queries; all-namespace Events are authorized and sensitivity/expiry limits explained. No destructive cleanup is instructed. Exercises include answers and operational review questions. Summary accurately identifies lack of backend tests.

Official sources inspected 2026-10-04: [PersistentVolumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/) supports RWO single-node rather than single-Pod semantics, CSI-dependent RWOP, reclaim behavior and expansion constraints; [StorageClasses](https://kubernetes.io/docs/concepts/storage/storage-classes/) supports delayed binding, nodeName bypass caveat, mount-option/provider differences and allowed expansion; [snapshot classes](https://kubernetes.io/docs/concepts/storage/volume-snapshot-classes/) supports independent snapshot driver/deletion policy; [CSI drivers](https://kubernetes-csi.github.io/docs/drivers.html) supports driver-specific capabilities and compatibility. The chapter correctly distinguishes binding/mount from application integrity, backups from snapshots, and application consistency from reported snapshot completion. WAL recovery and isolated validation are sound. No unsupported universal shrink, multi-node filesystem, performance or durability guarantee appears. Ubuntu/Fedora/RHEL differences are delegated to exact supported driver/node OS documentation without interchangeable package commands.

## Validation and limits

`python tools/check_book.py --chapters 114-115` passed on 2026-10-04: two draft chapters, two shell syntax blocks, one YAML parsing block and 1,380 global local-link checks; no errors/warnings. Hash computed with tools.promote_reviewed.body_hash. Static checks establish syntax/parsing and local links only. No cluster/API query, manifest application, storage operation, token generation, impersonation, identity-provider exchange or provider action occurred. No selected driver/controller/backend, OS matrix, real authorization, data recovery, performance or external federation was tested. Primary sources were inspected selectively rather than exhaustive external-link or deployment validation. Only separate review records were written.

Verdict: approved
