import urllib.request
import json

for service, url in [('lever', 'https://api.lever.co/v0/postings/hasura?mode=json'),
                    ('greenhouse', 'https://boards-api.greenhouse.io/v1/boards/hasura/jobs'),
                    ('ashby', 'https://api.ashbyhq.com/posting-api/job-board/hasura')]:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f'{service} returned success!')
            jobs = data if isinstance(data, list) else data.get('jobs', [])
            print(f'Total jobs: {len(jobs)}')
            for j in jobs:
                t = j.get('text') or j.get('title')
                loc = j.get('categories', {}).get('location') if 'categories' in j else j.get('location', {}).get('name')
                u = j.get('hostedUrl') or j.get('absolute_url') or j.get('jobUrl')
                print(f'  {t} | {loc} | {u}')
    except Exception as e:
        print(f'{service} error: {e}')

