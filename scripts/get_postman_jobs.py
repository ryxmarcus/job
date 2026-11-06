import urllib.request
import json

req = urllib.request.Request('https://apply.workable.com/api/v1/widget/accounts/postman', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    jobs = data.get('jobs', [])
    print(f'Total Postman Workable jobs: {len(jobs)}')
    for j in jobs:
        title = j.get('title')
        city = j.get('city')
        country = j.get('country')
        url = j.get('shortlink')
        print(f'{title} | {city}, {country} | {url}')

