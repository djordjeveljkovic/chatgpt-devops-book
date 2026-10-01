"""Check book structure, links and inline-example syntax without executing examples."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
STATES = {'planned', 'drafting', 'draft', 'reviewing', 'revising', 'complete'}

def blocks(text):
    return re.findall(r'^```([^\n]*)\n(.*?)^```\s*$', text, re.M | re.S)

def prose(text):
    return re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)

def metadata(text):
    match = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ':' in line:
            key, value = line.split(':', 1)
            result[key] = value.strip().strip('"\'')
    return result

def anchors(text):
    found, counts = set(), Counter()
    for title in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', prose(text), re.M):
        title = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', title)
        key = re.sub(r'[^\w\- ]', '', title.lower()).replace(' ', '-')
        ordinal = counts[key]
        counts[key] += 1
        found.add(key if ordinal == 0 else f'{key}-{ordinal}')
    return found

def check_syntax(language, code, scratch):
    language = language.strip().lower()
    if language in {'bash', 'sh', 'shell'}:
        p = scratch / 'example.sh'
        p.write_text(code)
        interpreter = 'sh' if language == 'sh' else 'bash'
        result = subprocess.run([interpreter, '-n', str(p)], text=True, capture_output=True)
        return result.returncode == 0, result.stderr.strip(), 'shell syntax'
    if language in {'python', 'py'}:
        try:
            compile(code, '<book example>', 'exec')
            return True, '', 'Python syntax'
        except SyntaxError as exc:
            return False, str(exc), 'Python syntax'
    if language == 'json':
        try:
            json.loads(code)
            return True, '', 'JSON parsing'
        except json.JSONDecodeError as exc:
            return False, str(exc), 'JSON parsing'
    if language in {'yaml', 'yml'}:
        try:
            import yaml
        except ImportError:
            return None, 'PyYAML unavailable', 'YAML parsing'
        try:
            # Compose nodes without constructing values: CloudFormation !Ref/!Sub
            # and other valid application-specific tags remain valid YAML syntax.
            list(yaml.compose_all(code, Loader=yaml.SafeLoader))
            return True, '', 'YAML parsing'
        except yaml.YAMLError as exc:
            return False, str(exc), 'YAML parsing'
    if language in {'javascript', 'js'} and shutil.which('node'):
        p = scratch / 'example.mjs'
        p.write_text(code)
        result = subprocess.run(['node', '--check', str(p)], text=True, capture_output=True)
        return result.returncode == 0, result.stderr.strip(), 'JavaScript syntax'
    if language == 'php' and shutil.which('php'):
        p = scratch / 'example.php'
        p.write_text(code if code.lstrip().startswith('<?php') else '<?php\n' + code)
        result = subprocess.run(['php', '-l', str(p)], text=True, capture_output=True)
        return result.returncode == 0, result.stdout.strip() + result.stderr.strip(), 'PHP syntax'
    if language == 'go' and shutil.which('gofmt'):
        p = scratch / 'example.go'
        p.write_text(code)
        result = subprocess.run(['gofmt', '-d', str(p)], text=True, capture_output=True)
        return result.returncode == 0, result.stderr.strip(), 'Go syntax'
    return None, '', language or 'unlabelled'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true', help='Require all chapters to be independently reviewed and complete.')
    parser.add_argument('--report', action='store_true', help='Write book/_ai/VALIDATION.json with actual evidence.')
    parser.add_argument('--chapters', help='Restrict manuscript syntax checks to an inclusive range, e.g. 1-10.')
    args = parser.parse_args()
    records = json.loads((ROOT / 'book/_ai/manifest.json').read_text())
    chosen = set(range(1, len(records) + 1))
    if args.chapters:
        lo, hi = map(int, args.chapters.split('-'))
        chosen = set(range(lo, hi + 1))
    errors, warnings, checks = [], [], Counter()
    evidence = []
    states = Counter()
    with tempfile.TemporaryDirectory(prefix='devops-book-check-') as temp:
        scratch = Path(temp)
        for r in records:
            if r['chapter'] not in chosen:
                continue
            path = ROOT / r['path']
            if not path.exists():
                errors.append(f"Missing chapter: {r['path']}")
                continue
            text = path.read_text()
            meta = metadata(text)
            state = meta.get('status', 'missing')
            states[state] += 1
            if state not in STATES:
                errors.append(f"{r['path']}: invalid/missing status {state}")
            for key, expected in [('chapter', str(r['chapter'])), ('volume', str(r['volume'])), ('title', r['title'])]:
                if meta.get(key) != expected:
                    errors.append(f"{r['path']}: {key} does not match manifest")
            if not (ROOT / r['summary']).exists():
                errors.append(f"Missing summary: {r['summary']}")
            if meta.get('summary') and not (path.parent / meta['summary']).exists():
                errors.append(f"{r['path']}: front-matter summary link does not resolve")
            if state == 'complete':
                review = ROOT / r['review']
                approved = review.exists() and bool(re.search(r'^Verdict:\s*approved\s*$', review.read_text(), re.M | re.I))
                if not approved:
                    errors.append(f"{r['path']}: complete without independent approved review")
                else:
                    recorded = re.search(r'^Reviewed body SHA256:\s*([a-f0-9]{64})\s*$', review.read_text(), re.M)
                    body = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.S)
                    if not recorded or recorded.group(1) != hashlib.sha256(body.encode()).hexdigest():
                        errors.append(f"{r['path']}: completed manuscript differs from independently reviewed body")
            elif args.strict:
                errors.append(f"{r['path']}: unfinished ({state})")
            if state == 'planned':
                continue
            if re.search(r'Authoring placeholder|TODO|\bTBD\b', text):
                errors.append(f"{r['path']}: placeholder remains in written chapter")
            word_count = len(re.findall(r"\b[\w'-]+\b", prose(text).split('---', 2)[-1]))
            threshold = 500 if r['volume'] == 22 else 1000
            if state in {'draft', 'complete'} and word_count < threshold:
                warnings.append(f"{r['path']}: only {word_count} prose words; editorial depth review needed")
            chapter_checks = Counter()
            for index, (language, code) in enumerate(blocks(text), 1):
                ok, detail, label = check_syntax(language, code, scratch)
                if ok is False:
                    errors.append(f"{r['path']} block {index} ({label}): {detail[:350]}")
                if ok is not None:
                    checks[label] += 1
                    chapter_checks[label] += 1
            evidence.append({'chapter': r['chapter'], 'path': r['path'], 'status': state,
                             'sha256': hashlib.sha256(text.encode()).hexdigest(),
                             'prose_words': word_count, 'syntax_checks': dict(chapter_checks)})
    # All local Markdown links are checked, including navigation and authoring files.
    for path in ROOT.rglob('*.md'):
        for target in re.findall(r'(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)', prose(path.read_text())):
            target = target.strip().split(' "', 1)[0].strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith('//'):
                continue
            dest = path.parent / unquote(parsed.path) if parsed.path else path
            if not dest.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken local link {target}")
            elif parsed.fragment and dest.is_file() and dest.suffix == '.md':
                if unquote(parsed.fragment) not in anchors(dest.read_text()):
                    errors.append(f"{path.relative_to(ROOT)}: missing anchor {target}")
            checks['local links'] += 1
    report = {'chapters_checked': len(chosen), 'states': dict(states), 'checks': dict(checks),
              'errors': errors, 'warnings': warnings, 'evidence': evidence,
              'limits': 'Syntax/parsing and local links only; no infrastructure, provider, application, schema or runtime semantics execution.'}
    if args.report:
        (ROOT / 'book/_ai/VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('chapters_checked', 'states', 'checks', 'errors', 'warnings', 'limits')}, indent=2))
    raise SystemExit(1 if errors else 0)

if __name__ == '__main__':
    main()
