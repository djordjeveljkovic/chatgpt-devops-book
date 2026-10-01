"""Coordinator-only: mark independently approved drafts complete after validation.

Run check_book.py first. Only metadata and factual continuation state are changed.
Reviewers record a hash of prose to prevent an approval covering later edits.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def body_hash(text):
    body = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)
    return hashlib.sha256(body.encode()).hexdigest()

def main():
    subprocess.run([sys.executable, str(ROOT / 'tools/check_book.py')], check=True,
                   stdout=subprocess.DEVNULL)
    promoted = []
    skipped = []
    for r in json.loads((ROOT / 'book/_ai/manifest.json').read_text()):
        path, review = ROOT / r['path'], ROOT / r['review']
        text = path.read_text()
        if not re.search(r'^status:\s*(draft|reviewing|revising)\s*$', text, re.M) or not review.exists():
            continue
        inspection = review.read_text()
        if not re.search(r'^Verdict:\s*approved\s*$', inspection, re.M | re.I):
            continue
        match = re.search(r'^Reviewed body SHA256:\s*([a-f0-9]{64})\s*$', inspection, re.M)
        if not match or match.group(1) != body_hash(text):
            skipped.append({'chapter': r['chapter'], 'reason': 'Review missing a matching manuscript-body hash'})
            continue
        path.write_text(re.sub(r'^status:\s*\w+\s*$', 'status: complete', text, count=1, flags=re.M))
        summary = ROOT / r['summary']
        note = summary.read_text()
        note = re.sub(r'^Status:\s*.*$', 'Status: complete', note, count=1, flags=re.M | re.I)
        note = re.sub(r'(## Exact next section\s*\n)[^#]+',
                      r'\1None. Independently approved; continue to the next unfinished chapter.\n\n', note, count=1, flags=re.I)
        summary.write_text(note)
        promoted.append(r['chapter'])
    print(json.dumps({'promoted': promoted, 'skipped': skipped}, indent=2))

if __name__ == '__main__':
    main()
