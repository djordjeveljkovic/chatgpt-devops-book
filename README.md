# The Complete DevOps Engineering Book

A practical engineering guide from Linux and the CLI to containers, cloud infrastructure, Kubernetes, delivery, observability and production reliability.

Start at the [book index](book/README.md). The manuscript is organized into 22 volumes and 220 chapters. Each chapter's real writing and review status is visible in [PROGRESS.md](PROGRESS.md); the existence of a chapter file does not mean it is finished.

The book teaches commands alongside mechanisms, failure investigation and design decisions. Ubuntu and Fedora/RHEL receive parallel instructions where their behavior differs. A fictional application, DispatchDesk, follows contrasting VPS, AWS managed-service and Kubernetes paths. Dated real-company case studies are attributed separately.

## Continuing the book

Read [AI_AUTHORING_GUIDE.md](AI_AUTHORING_GUIDE.md), then [PROGRESS.md](PROGRESS.md), the relevant brief in [SKELETON.md](SKELETON.md), and the target chapter's summary. Continue from the exact saved boundary; do not restart existing chapters.

## Validation

Run `python3 tools/check_book.py` from this directory to check chapter metadata, local links, manuscript coverage and shell syntax. Run `python3 tools/refresh_progress.py` to rebuild the status index from chapter and review records. These are authoring utilities; all reader examples remain inline in Markdown.

## Structural attribution

The volume-based Markdown layout, chapter front matter, master teaching brief and continuation summaries are adapted from [The Complete Modern PHP Engineering Book](https://github.com/djordjeveljkovic/chatgpt-php-book). This manuscript contains original DevOps prose. The reference repository is checked out separately and is not part of this book.
