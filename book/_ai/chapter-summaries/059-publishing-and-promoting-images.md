# Chapter 59 — Publishing and Promoting Images

Status: complete

## Written material
Registry authentication and least privilege; mutable tags versus manifest digests; build-once workflow; registry-side release tags and destination verification; fictional DispatchDesk 1.4.0 promotion procedure; push/pull and tag-drift diagnosis; exercises, answer guidance, takeaways and further reading.

## Concepts and terminology
Registry namespace, credential helper, pull/push scope, mutable and immutable tags, manifest digest, multi-platform image index, promotion, provenance and rollback reference.

## Examples and cross-references
Private example registry `registry.example.internal`; build commit-tagged image from reviewed context; inspect and record registry digest; create semantic-version and production tags from a verified digest; deploy digest-qualified reference. Credentials, registry and digest are illustrative and were not used. Relative links to chapters 49, 53, 54, 58 and 131.

## Open threads
No Docker daemon, registry authentication, build, push, pull, promotion or deployment was run; review approval rests on primary documentation and static inspection.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Docker login, image push/tag, Buildx imagetools inspection/creation and immutable-tag documentation inspected 2026-10-03. Independent review approved current body SHA256 `8f55e8494cf5b259d48820be6807ab643fbc564177a836ee6fd0c30501bdbfbf`. Full checker passed 220 chapter records and all registered syntax/link checks with no errors or warnings. Static checks do not validate registry credentials, permissions, digest equivalence or runtime behavior.
