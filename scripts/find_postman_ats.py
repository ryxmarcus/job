import urllib.request
import json

for service, url in [('lever', 'https://api.lever.co/v0/postings/postman?mode=json'),
                    ('ashby', 'https://api.ashbyhq.com/posting-api/job-board/postman'),
                    ('workable', 'https://apply.workable.com/api/v1/widget/accounts/postman')]:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f'{service} returned success!')
            if service == 'lever':
                print(f'Lever jobs: {len(data)}')
                for j in data[:5]:
                    print(' ', j.get('text'), '|', j.get('categories', {}).get('location'), '|', j.get('hostedUrl'))
            elif service == 'ashby':
                jobs = data.get('jobs', [])
                print(f'Ashby jobs: {len(jobs)}')
                for j in jobs[:5]:
                    print(' ', j.get('title'), '|', j.get('location'), '|', j.get('jobUrl'))
    except Exception as e:
        print(f'{service} error: {e}')

