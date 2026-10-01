# Chapter 3 continuation

Status: complete

## Written material
Hardware resources; process/kernel/syscall model; complete Python descriptor lab; conceptual request path; storage-wait incident; exercises/review.

## Concepts and terminology
CPU work versus elapsed waiting; memory versus persistent storage; process, thread, kernel, syscall, descriptor; introductory buffering/commit boundaries.

## Examples and cross-references
Temporary-file snippet; asynchronous order/worker path; fictional storage contention. Links 002, 004, 011 and 036.

## Open threads
Independent review. Introductory Linux discussion must stay compact when Volume 2 is written.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
2026-10-01: official Linux read/fsync manual pages and kernel proc docs inspected. Python docs fetch failed (service error). Exact snippet executed: Python 3.14.7, kernel 7.2.7-arch1-1; reads yielded b'order', b'-17\n', b''. No Ubuntu/RHEL installation, network service, database or crash durability test.

Coordinator check_book.py --chapters 1-3 executed by writer: no errors/warnings; YAML/shell syntax and local links only.
