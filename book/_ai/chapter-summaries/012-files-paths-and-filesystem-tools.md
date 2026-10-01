# Chapter 12 continuation

Status: complete

## Written material
Paths/inode/entry/link identity; complete hard/symbolic-link lab; find/stat search; copy/move/deletion boundaries; deleted-open-log incident; assessment.

## Concepts and terminology
Canonical pathname versus device/inode identity, hard/symbolic link, physical scope, mtime/ctime, allocated versus logical size, open reference after unlink.

## Examples and cross-references
Disposable local ln/stat/cat/rm lab with negative dangling-link read; find exec stat+; links011/013/016/146.

## Open threads
Independent review and recorded safe local lab; security labels detailed later.

## Exact next section
None. Independently approved; continue to the next unfinished chapter.

## Verification
Official Linux inode and upstream GNUfind/stat/mv manuals inspected2026-10-01. GNUcoreutils9.11 link lab executed: shared device/inode/linkcount2, shared overwrite, hardlink survival and dangling-symlink read failure verified. Temporary state cleaned. No database/log/release mutation.
