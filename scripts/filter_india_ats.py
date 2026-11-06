import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

json_path = r'C:\Users\rah_66160\iTopaz-agents\job\scanned_docs\extracted_pipeline\sources\discovery_20261103T050514Z.json'

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

pure_india = []
for j in data.get('jobs', []):
    loc = (j.get('location') or '').lower()
    if 'india' in loc or any(c in loc for c in ['bengaluru', 'bangalore', 'gurgaon', 'gurugram', 'hyderabad', 'pune', 'delhi', 'noida']):
        pure_india.append(j)

print(f"Total verified India / India-Remote Tier-1 openings: {len(pure_india)}\n")
for idx, j in enumerate(pure_india, 1):
    print(f"[{idx}] {j['board'].upper()} | {j['title']}")
    print(f"    Location: {j['location']}")
    print(f"    URL: {j['url']}\n")

