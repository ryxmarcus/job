import urllib.request
import json

for board, url in [('syfe_lever', 'https://api.lever.co/v0/postings/syfe?mode=json'),
                   ('syfe_gh', 'https://boards-api.greenhouse.io/v1/boards/syfe/jobs')]:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            jobs = data if isinstance(data, list) else data.get('jobs', [])
            print(f'{board} jobs count: {len(jobs)}')
            for j in jobs:
                title = j.get('text') or j.get('title')
                loc = j.get('categories', {}).get('location') if 'categories' in j else j.get('location', {}).get('name')
                u = j.get('hostedUrl') or j.get('absolute_url')
                print(f'  {title} | {loc} | {u}')
    except Exception as e:
        print(f'{board} error: {e}')

