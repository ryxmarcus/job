import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

json_path = r'C:\Users\rah_66160\iTopaz-agents\job\scanned_docs\extracted_pipeline\sources\discovery_20261103T050514Z.json'

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

jobs = data.get('jobs', [])
errors = data.get('errors', [])

print(f"Total jobs extracted from ATS feeds: {len(jobs)}")
print(f"Board feed errors (if any): {len(errors)}")

india_matches = []
for j in jobs:
    loc = (j.get('location') or '').lower()
    title = (j.get('title') or '').lower()
    if any(k in loc for k in ['india', 'bengaluru', 'bangalore', 'gurgaon', 'gurugram', 'hyderabad', 'pune', 'delhi', 'remote']):
        india_matches.append(j)

print(f"India / Remote eligible jobs: {len(india_matches)}\n")
for idx, j in enumerate(india_matches[:15], 1):
    print(f"[{idx}] {j['board'].upper()} | {j['title']}")
    print(f"    Location: {j['location']}")
    print(f"    URL: {j['url']}\n")
