import urllib.request
import json

req = urllib.request.Request('https://boards-api.greenhouse.io/v1/boards/postman/jobs', headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        jobs = data.get('jobs', [])
        print(f'Total Postman live jobs on Greenhouse: {len(jobs)}')
        for j in jobs:
            title = j['title']
            loc = j.get('location', {}).get('name')
            if any(k in title.lower() or k in loc.lower() for k in ['india', 'bangalore', 'bengaluru', 'gurugram', 'gurgaon', 'devops', 'sre', 'cloud', 'platform', 'infrastructure']):
                print(f"{j['id']} | {title} | {loc} | {j['absolute_url']}")
except Exception as e:
    print('Error:', e)

