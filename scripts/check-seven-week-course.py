#!/usr/bin/env python3
"""Verify preservation, seven-week coverage, starter packaging, and rendered links.

Run after `quarto render`. Uses only Python's standard library.
"""
import hashlib
import json
import re
import subprocess
import tarfile
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / '_book'


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.week_data = None
        self.feed(text)
        match = re.search(r'window\.PM_WEEK_VIEW\s*=\s*(\{.*?\});', text, re.S)
        if match:
            self.week_data = json.loads(match.group(1))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])


def chapters(config):
    return re.findall(r'^\s+- ([\w-]+\.qmd)\s*$', config, re.M)


def main():
    manifest = json.loads((ROOT / '_source-original/manifest.json').read_text())
    archive_path = ROOT / '_source-original' / manifest['snapshot']
    assert hashlib.sha256(archive_path.read_bytes()).hexdigest() == manifest['snapshot_sha256'], 'Source archive changed'
    tree = subprocess.check_output(['git', 'ls-tree', '-r', '-z', manifest['source_commit']], cwd=ROOT)
    blobs = {}
    for entry in tree.split(b'\0'):
        if entry:
            meta, name = entry.split(b'\t', 1)
            blobs[name.decode()] = meta.split()[2].decode()
    with tarfile.open(archive_path, 'r:gz') as archive:
        archived = {member.name: member for member in archive.getmembers() if member.isfile() or member.issym()}
        assert set(archived) == set(manifest['tracked_files']) == set(blobs), 'Source inventory mismatch'
        for name, member in archived.items():
            data = member.linkname.encode() if member.issym() else archive.extractfile(member).read()
            blob = b'blob ' + str(len(data)).encode() + b'\0' + data
            assert hashlib.sha1(blob).hexdigest() == blobs[name], f'Archive differs from Git: {name}'
        original_config = archive.extractfile('_quarto.yml').read().decode()
        original_index = archive.extractfile('index.qmd').read().decode()
        original_chapters = chapters(original_config)
        current_chapters = chapters((ROOT / '_quarto.yml').read_text())
        assert set(original_chapters) <= set(current_chapters), 'A published source chapter was dropped'
        # Preserve every heading in instructional chapters, including appendices and references.
        for name in original_chapters:
            if name.startswith(('00-', 'index')):
                continue
            original = archive.extractfile(name).read().decode()
            current = (ROOT / name).read_text()
            headings = re.findall(r'^#{1,6} .+$', original, re.M)
            assert all(heading in current for heading in headings), f'Instructional section removed: {name}'
    print(f'PASS: {len(blobs)} source files match Git; all original chapters and instructional headings retained')

    pages = {}
    for name in current_chapters:
        rendered = BOOK / Path(name).with_suffix('.html')
        assert rendered.is_file(), f'Render missing: {rendered.name}'
        pages[rendered] = Page(rendered.read_text())
    week_data = pages[BOOK / 'index.html'].week_data
    assert week_data and week_data['course-end'] == '2027-04-08'
    weeks = week_data['weeks']
    assert [int(week['week']) for week in weeks] == list(range(1, 8))
    expected_starts = [(date(2027, 2, 22) + timedelta(weeks=n)).isoformat() for n in range(7)]
    assert [week['start'] for week in weeks] == expected_starts
    assigned = [chapter + '.qmd' for week in weeks for chapter in week['read']]
    original_topics = {name for name in original_chapters if re.match(r'(?:0[1-9]|1[0-5])[a-z]?-', name)}
    essentials = sorted(ROOT.glob('W[0-9][0-9]-*.qmd'))
    assert len(essentials) == 7, 'Expected seven essentials guides'
    assert set(assigned) == {p.name for p in essentials} | {'00-computer-setup.qmd'}, 'Required path must contain essentials and setup only'
    assert len(assigned) == len(set(assigned)), 'Duplicate required reading'
    assert 'Apr 5' in weeks[-1]['date'] and '8' in weeks[-1]['date']
    optional_links = set()
    for n, guide in enumerate(essentials, 1):
        text = guide.read_text()
        assert guide.stem in weeks[n - 1]['read'], f'Guide assigned to wrong week: {guide.name}'
        for heading in ['## Prepare: Session 1', '## Prepare: Session 2', '## Teach One Another', '### Session 1', '### Session 2', '## Ponder and Prove', '## Assignments this week', '## Optional full chapters']:
            assert heading in text, f'Missing Learning Model activity: {guide.name}: {heading}'
        assert '20–30 minutes' in text and 'additional time' in text, f'Missing reading-load boundary: {guide.name}'
        # Count prose and labels, excluding metadata and URL destinations.
        visible = re.sub(r'^---.*?---', '', text, count=1, flags=re.S)
        visible = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', visible)
        count = len(re.findall(r"\b[\w'-]+\b", visible))
        assert 1200 <= count <= 1800, f'Essentials outside the agreed length budget: {guide.name}: {count}'
        links = set(re.findall(r'\]\(([\w-]+\.qmd)\)', text.split('## Optional full chapters', 1)[1]))
        optional_links |= links
        assert '00-assignments.qmd' in text, f'Missing assignment path: {guide.name}'
    assert optional_links == original_topics, 'Every original topic must remain reachable as optional reading'
    for name in original_topics:
        assert 'title="Optional full chapter"' in (ROOT / name).read_text(), f'Missing optional label: {name}'
    for rendered, page in pages.items():
        assert page.week_data == week_data, f'Inconsistent weekly metadata: {rendered.name}'
    print('PASS: seven short essentials guides, two-session Learning Model, and all full chapters optional and accessible')

    schedule_data = json.loads((ROOT / 'course-support/starter/course-schedule.json').read_text())
    assert schedule_data['timezone'] == 'America/Boise' and schedule_data['submission_time'] == '23:59'
    expected_wraps = [(date(2027, 2, 27) + timedelta(weeks=n)).isoformat() for n in range(6)]
    sprints = schedule_data['sprints']
    assert [sp['sprint'] for sp in sprints] == list(range(1, 7))
    assert [sp['week'] for sp in sprints] == list(range(1, 7))
    assert [sp['wrap_up_due'] for sp in sprints] == expected_wraps
    assert sprints[0]['plan_due'] is None and sprints[0]['plan_exception'] == 'During the first class'
    assert [sp['plan_due'] for sp in sprints[1:]] == expected_wraps[:-1]
    checklist = (ROOT / '00-assignments.qmd').read_text()
    schedule_text = (ROOT / '00-schedule.qmd').read_text()
    assessments = (ROOT / '00-assessments.qmd').read_text()
    for sp in sprints:
        n = sp['sprint']
        body = re.search(rf'### Sprint {n} \{{#sprint-{n}\}}(.*?)(?=\n### Sprint|\n## Peer Assignment)', assessments, re.S).group(1)
        for key in ['plan_due', 'wrap_up_due']:
            if sp[key] is None:
                assert 'During first class' in body
                continue
            d = date.fromisoformat(sp[key])
            assert d.weekday() == 5 and d <= date(2027, 4, 8), 'Sprint deadline outside Saturday/block boundary'
            long_label = f"Saturday, {d.strftime('%B')} {d.day}"
            assert long_label in body and long_label in checklist, f'Sprint {n} date missing in assessment/checklist'
            short_label = f"Sat, {d.strftime('%b')} {d.day}"
            assert short_label in schedule_text, f'Sprint {n} date missing in schedule'
            due_week = n if key == 'wrap_up_due' else n - 1
            expected_text = f"Sprint {n} {'wrap-up' if key == 'wrap_up_due' else 'plan'}: {short_label}"
            assert any(expected_text in it['text'] and it['href'].endswith(f'#sprint-{n}') for it in weeks[due_week - 1]['items']), f'Sprint {n} date missing in weekly navigation'
    assert not any('Sprint' in it['text'] for it in weeks[6]['items']), 'No new sprint submission belongs in Week 7'
    # America/Boise follows the local DST change instead of treating every deadline as MST.
    zone = ZoneInfo(schedule_data['timezone'])
    assert datetime(2027, 2, 27, 23, 59, tzinfo=zone).utcoffset() != datetime(2027, 4, 3, 23, 59, tzinfo=zone).utcoffset()
    assert schedule_data['peer_testing']['due'] == expected_wraps[-1]
    assert schedule_data['midterm'] == {'proposed': True, 'opens': '2027-03-12', 'closes': '2027-03-13', 'points': 25}
    assert schedule_data['final_exam'] == {'proposed': True, 'opens': '2027-04-05', 'closes': '2027-04-08', 'points': 25}
    for text in [checklist, schedule_text, assessments]:
        assert 'March 12–13' in text and 'April 5–8' in text and 'proposed' in text.lower(), 'Exam windows must be consistent and proposed'
        assert 'America/Boise' in text
    rows = [line for line in checklist.splitlines() if re.match(r'\| \[(?:Sprint \d (?:Plan|Wrap-up)|Peer Product Testing|Midterm Exam|Final Exam)\]', line)]
    assert len(rows) == 15 and sum(int(line.split('|')[-2].strip()) for line in rows) == 450, 'Assignment list must account for the 450-point grade exactly once'
    assert len([row for row in rows if 'Plan]' in row]) == 6
    assert len([row for row in rows if 'Wrap-up]' in row]) == 6
    for name in ['00-assignments.qmd', '00-schedule.qmd', '00-assessments.qmd']:
        assert name in current_chapters
    print('PASS: Saturday plans and wrap-ups, first-class exception, proposed exams, and complete 450-point assignment list')

    current_index = (ROOT / 'index.qmd').read_text()
    def grading_table(text):
        return re.search(r'\| Component \| Points \|.*?\*\*450\*\*.*?\n', text, re.S).group()
    assert grading_table(original_index) == grading_table(current_index), 'Grading model changed'
    for outcome in re.findall(r'^\| [1-5]\\?\. .*$', original_index, re.M):
        assert outcome in current_index, 'Learning outcome changed'
    admin_names = ['index.qmd', '00-assessments.qmd', '00-computer-setup.qmd', '00-schedule.qmd', '00-course-workflows.qmd', '00-assignments.qmd']
    for name in admin_names:
        text = (ROOT / name).read_text()
        assert not re.search(r'Murff|sdmurff|McCauley|TNRB|MSB 341|msb341|byu\.edu|byustrategyprogram|byu-strategy/builder-template', text), name
        assert not re.search(r'(?i)\b(?:Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d', text), f'Old course date in {name}'
    schedule = (ROOT / '00-schedule.qmd').read_text()
    for guide in essentials:
        assert f']({guide.name})' in schedule, f'Essentials missing from schedule: {guide.name}'
    for word in ['tuition', 'withdrawal', 'registration deadline', 'graduation deadline']:
        assert word not in schedule.lower(), 'Administrative deadline introduced'
    assert '5-point extra-credit' in checklist
    assert 'Optional full chapters do not independently add exam requirements' in assessments
    print('PASS: original grading and outcomes; updated administration; no extra calendar deadlines')

    starter = ROOT / 'course-support/starter'
    with ZipFile(ROOT / 'course-support/byui-product-management-starter.zip') as archive:
        expected = {f'byui-product-management-starter/{p.relative_to(starter).as_posix()}': p for p in starter.rglob('*') if p.is_file()}
        assert set(archive.namelist()) == set(expected), 'Starter zip inventory is stale'
        for name, path in expected.items():
            assert archive.read(name) == path.read_bytes(), f'Starter zip is stale: {name}'
    assert not list(BOOK.rglob('source.tar.gz')), 'Source archive leaked into publication'
    assert not (BOOK / '_source-original').exists(), 'Source archive directory leaked into publication'
    assert not list(BOOK.glob('AGENT*')), 'Repository guidance leaked into publication'
    header = (ROOT / '_header.html').read_text()
    assert 'googletagmanager' not in header and 'G-5TPMPSE4HZ' not in header
    print('PASS: starter zip matches source; original archive and inherited analytics excluded')

    broken = []
    for path, page in list(pages.items()):
        for href in page.links:
            url = urlsplit(href)
            if url.scheme or url.netloc or not url.path and not url.fragment:
                continue
            if url.path.startswith('/'):
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.exists():
                broken.append((path.name, href, 'missing file'))
            elif url.fragment and target.suffix == '.html':
                if target not in pages:
                    pages[target] = Page(target.read_text())
                if unquote(url.fragment) not in pages[target].ids:
                    broken.append((path.name, href, 'missing anchor'))
    assert not broken, 'Broken local links:\n' + '\n'.join(map(str, broken))
    print(f'PASS: local links and anchors across {len(pages)} rendered pages')


if __name__ == '__main__':
    main()
