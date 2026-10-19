"""Read public ATS feeds only. Never submit applications or modify the tracker."""
import csv
import datetime as dt
import html
import json
from pathlib import Path
import re
import time
from urllib import request, robotparser, parse

ROOT = Path(__file__).resolve().parents[1]
UA = 'RahulJobResearch/1.0'
ROLE = re.compile(r'\b(sre|devops|mlops|llmops|site reliability|forward[- ]deployed|ai platform|platform engineer|systems development engineer)\b', re.I)
robots_cache = {}

def fetch(url):
    origin = '{0.scheme}://{0.netloc}'.format(parse.urlsplit(url))
    if origin not in robots_cache:
        rp = robotparser.RobotFileParser(origin + '/robots.txt')
        try:
            with request.urlopen(request.Request(rp.url, headers={'User-Agent': UA}), timeout=20) as r:
                rp.parse(r.read(512000).decode('utf-8').splitlines())
        except Exception as exc:
            raise RuntimeError('Cannot verify robots rules; skipped: ' + str(exc)) from exc
        robots_cache[origin] = rp
    rp = robots_cache[origin]
    if not rp.can_fetch(UA, url):
        raise RuntimeError('robots.txt disallows this URL')
    delay = rp.crawl_delay(UA) or 1
    time.sleep(max(1, delay))
    with request.urlopen(request.Request(url, headers={'User-Agent': UA, 'Accept': 'application/json'}), timeout=30) as r:
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
        description = re.sub('<[^>]+>', ' ', html.unescape(html.unescape(description)))
        yield {'provider':provider, 'board':board, 'id':str(item['id']), 'title':title, 'location':location, 'priority':priority,
               'url':item.get('absolute_url', '') if provider == 'greenhouse' else item.get('hostedUrl',''),
               'location_note':'Manual eligibility review required; remote without India stays priority 99',
               'description':description, 'status':'discovered_not_applied'}

def main():
    jobs, errors, seen = [], [], set()
    for config in json.loads((ROOT/'boards.json').read_text(encoding='utf-8')):
        board, provider = config['board'], config['provider']
        if not re.fullmatch(r'[A-Za-z0-9_-]+',board):
            errors.append({'board':board,'error':'Invalid board slug'}); continue
        if provider == 'greenhouse':
            url = f'https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true'
        elif provider == 'lever':
            url = f'https://api.lever.co/v0/postings/{board}?mode=json'
        else:
            errors.append({'board':board,'error':'Unsupported provider'}); continue
        try:
            for row in normalise(provider, board, fetch(url)):
                key=(provider,board,row['id'])
                if key not in seen:
                    jobs.append(row); seen.add(key)
        except Exception as exc:
            errors.append({'board':board,'error':str(exc)})
    jobs.sort(key=lambda j:(j['priority'],j['board'],j['title']))
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dest=ROOT/'sources'/('discovery_'+stamp+'.json')
    dest.write_text(json.dumps({'checked_at_utc':stamp,'jobs':jobs,'errors':errors},indent=2),encoding='utf-8')
    fields=['provider','board','id','title','location','priority','url','location_note','status']
    with dest.with_suffix('.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(jobs)
    print(f'{len(jobs)} discovered; {len(errors)} boards skipped/failed. Output: {dest}')
    for error in errors:
        print(error['board']+': '+error['error'])

if __name__ == '__main__':
    main()
