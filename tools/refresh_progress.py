"""Rebuild the status index from actual manuscript and review records."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]

def status(text):
    match = re.search(r'^status:\s*([a-z-]+)\s*$', text, re.M)
    return match.group(1) if match else 'missing'

def main():
    records = json.loads((ROOT / 'book/_ai/manifest.json').read_text())
    rows, totals, unfinished = [], Counter(), []
    words = 0
    for r in records:
        path = ROOT / r['path']
        body = path.read_text() if path.exists() else ''
        state = status(body)
        totals[state] += 1
        count = len(re.findall(r"\b[\w'-]+\b", body.split('---', 2)[-1]))
        if state != 'planned':
            words += count
        review = ROOT / r['review']
        reviewed = review.exists() and bool(re.search(r'^Verdict:\s*approved\s*$', review.read_text(), re.M | re.I))
        summary = ROOT / r['summary']
        next_step = 'See chapter summary'
        if summary.exists():
            match = re.search(r'## Exact next section\s*\n([^#]+)', summary.read_text(), re.I)
            if match:
                next_step = ' '.join(match.group(1).strip().split())[:180]
        if state != 'complete':
            unfinished.append((r, next_step))
        rows.append(f"| {r['chapter']:03d} | {r['volume']} | [{r['title']}]({r['path']}) | {state} | "
                    f"{'approved' if reviewed else 'pending'} | {count if state != 'planned' else 0:,} | "
                    f"[Resume]({r['summary']}) |")
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    lines = ['# Book progress and exact continuation', '', f'Last refreshed: {stamp}.', '',
        '## Actual state', '', f"Chapters: {len(records)}. Approximate written words: {words:,}.", '',
        ', '.join(f'{name}: {count}' for name, count in sorted(totals.items())) + '.', '',
        'Statuses reflect files, not promises. `complete` requires independent approval and validation. '
        'References and code contribute to approximate word counts; counts do not measure quality.', '',
        '## Resume without the old conversation', '',
        'Read [AI_AUTHORING_GUIDE.md](AI_AUTHORING_GUIDE.md), [coordinator handoff](book/_ai/HANDOFF.md), '
        'the target brief in [SKELETON.md](SKELETON.md), and the linked chapter summary. '
        'Check [assignments](book/_ai/assignments/README.md) for ownership; recover stale work before spawning a replacement. '
        'Continue from the exact saved section. Never recreate finished material.', '',
        '## Earliest unfinished dependency', '']
    if unfinished:
        r, step = unfinished[0]
        lines += [f"Chapter {r['chapter']:03d}: [{r['title']}]({r['path']}). Exact next step: {step}.", '']
    else:
        lines += ['All chapter files report complete; verify the final acceptance report before delivery.', '']
    lines += ['## Chapter ledger', '', '| Chapter | Volume | Title | Writing | Review | Words | Exact section and evidence |',
              '|---|---|---|---|---|---:|---|', *rows, '',
              '## Outstanding global work', '',
              '- Finish all planned/drafting chapters and their factual summaries.\n'
              '- Independently review drafts, repair material findings and recheck changed examples.\n'
              '- Validate Linux alternatives, version-sensitive claims, navigation and command examples.\n'
              '- Review cross-volume repetition, project continuity and sourced company attribution.\n'
              '- Record actual execution limits and produce the final acceptance report.\n',
              '## Refresh', '', '`python3 tools/refresh_progress.py` rebuilds this file from actual chapter state; '
              'only the coordinator runs it while agents are active.', '']
    (ROOT / 'PROGRESS.md').write_text('\n'.join(lines))

if __name__ == '__main__':
    main()
