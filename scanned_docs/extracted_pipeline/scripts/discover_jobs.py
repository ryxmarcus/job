"""Read public ATS feeds only. Never submit applications or modify the tracker.
Includes graceful offline mode and cached discovery fallback.
"""
import csv
import datetime as dt
import html
import json
from pathlib import Path
import re
import sys
import time
from urllib import request, robotparser, parse, error

ROOT = Path(__file__).resolve().parents[1]
UA = 'RahulJobResearch/1.0'
ROLE = re.compile(r'\b(sre|devops|mlops|llmops|site reliability|forward[- ]deployed|ai platform)\b', re.I)
robots_cache = {}

def fetch(url):
    origin = '{0.scheme}://{0.netloc}'.format(parse.urlsplit(url))
    if origin not in robots_cache:
        rp = robotparser.RobotFileParser(origin + '/robots.txt')
        try:
            with request.urlopen(request.Request(rp.url, headers={'User-Agent': UA}), timeout=10) as r:
                rp.parse(r.read(512000).decode('utf-8').splitlines())
        except Exception as exc:
            raise RuntimeError('Network or robots rule verification failed: ' + str(exc)) from exc
        robots_cache[origin] = rp
    rp = robots_cache[origin]
    if not rp.can_fetch(UA, url):
        raise RuntimeError('robots.txt disallows this URL')
    delay = rp.crawl_delay(UA) or 1
    time.sleep(max(1, delay))
    with request.urlopen(request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'}), timeout=20) as r:
        return json.loads(r.read(15000000))

def normalise(provider, board, data):
    items = data['jobs'] if provider == 'greenhouse' else data
    for item in items:
        title = item.get('title', '') if provider == 'greenhouse' else item.get('text', '')
        if not ROLE.search(title):
            continue
        loc = (item.get('location') or {}).get('name', '') if provider == 'greenhouse' else (item.get('categories') or {}).get('location', '')
        workplace = item.get('workplaceType', '')
        location = loc + (' / ' + workplace if workplace else '')
        low = location.lower()
        priority = 1 if 'remote' in low and 'india' in low else 2 if any(v in low for v in ['gurgaon','gurugram']) else 3 if 'delhi' in low else 4 if any(v in low for v in ['vizag','visakhapatnam','vishakhapatnam']) else 99
        description = item.get('content', '') if provider == 'greenhouse' else item.get('descriptionPlain', '')
        if provider == 'lever':
            sections = [section.get('text', '') + '\n' + section.get('content', '') for section in item.get('lists', [])]
            description += '\n' + '\n'.join(sections) + '\n' + item.get('additionalPlain', '')
        description = html.unescape(re.sub('<[^>]+>', ' ', description))
        yield {'provider':provider, 'board':board, 'id':str(item['id']), 'title':title, 'location':location, 'priority':priority,
               'url':item.get('absolute_url', '') if provider == 'greenhouse' else item.get('hostedUrl',''),
               'location_note':'Manual eligibility review required; remote without India stays priority 99',
               'description':description, 'status':'discovered_not_applied'}

def load_cached():
    sources = ROOT / 'sources'
    cached_files = sorted(sources.glob('discovery_*.json'), reverse=True)
    if cached_files:
        print(f"Offline / Sandbox mode detected. Falling back to latest cached discovery: {cached_files[0].name}")
        data = json.loads(cached_files[0].read_text(encoding='utf-8'))
        return data.get('jobs', []), []
    return [], [{'error': 'No cached discovery files found'}]

def main():
    jobs, errors, seen = [], [], set()
    offline = '--offline' in sys.argv or '--cached' in sys.argv

    if offline:
        jobs, errors = load_cached()
    else:
        boards_path = ROOT / 'boards.json'
        configs = json.loads(boards_path.read_text(encoding='utf-8'))
        network_available = True

        for config in configs:
            board, provider = config['board'], config['provider']
            if not re.fullmatch(r'[A-Za-z0-9_-]+', board):
                errors.append({'board': board, 'error': 'Invalid board slug'})
                continue
            url = f'https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true' if provider == 'greenhouse' else f'https://api.lever.co/v0/postings/{board}?mode=json'
            try:
                data = fetch(url)
                for item in normalise(provider, board, data):
                    key = (item['provider'], item['board'], item['id'])
                    if key in seen:
                        continue
                    seen.add(key)
                    jobs.append(item)
            except Exception as exc:
                errors.append({'board': board, 'error': str(exc)})
                if 'Temporary failure in name resolution' in str(exc) or 'Errno -3' in str(exc):
                    network_available = False
                    break

        if not network_available and not jobs:
            print("Notice: External network access is unavailable in this environment. Loading cached discoveries...")
            jobs, _ = load_cached()

    out_id = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out_dir = ROOT / 'sources'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f'discovery_{out_id}.json').write_text(json.dumps({'checked_at_utc': out_id, 'jobs': jobs, 'errors': errors}, indent=2), encoding='utf-8')

    if jobs:
        headers = ['provider', 'board', 'id', 'title', 'location', 'priority', 'url', 'status']
        with (out_dir / f'discovery_{out_id}.csv').open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(jobs)

    print(f"Discovery complete: {len(jobs)} active jobs loaded. Output: {out_dir}/discovery_{out_id}.json")

if __name__ == '__main__':
    main()
