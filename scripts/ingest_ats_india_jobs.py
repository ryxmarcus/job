import json
import csv
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"C:\Users\rah_66160\iTopaz-agents")
TRACKER_FILE = BASE_DIR / "job" / "applications" / "tracker.csv"
JSON_PATH = BASE_DIR / "job" / "scanned_docs" / "extracted_pipeline" / "sources" / "discovery_20261103T050514Z.json"

sys.path.append(str(BASE_DIR / "job" / "scripts"))
from smart_dispatcher import classify_job

# Load existing tracker
with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
    existing_rows = list(csv.reader(f))

last_id_num = int(existing_rows[-1][0].replace('J', '')) if len(existing_rows) > 1 else 0
applied_urls = {r[6].split('?')[0].strip() for r in existing_rows[1:] if len(r) > 6 and r[6]}

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

pure_india = []
for j in data.get('jobs', []):
    loc = (j.get('location') or '').lower()
    if 'india' in loc or any(c in loc for c in ['bengaluru', 'bangalore', 'gurgaon', 'gurugram', 'hyderabad', 'pune', 'delhi', 'noida']):
        pure_india.append(j)

new_entries = []
TODAY_STR = "2026-11-03"
FOLLOWUP_STR = "2026-11-17"

for j in pure_india:
    clean_url = j['url'].split('?')[0].strip()
    if clean_url in applied_urls:
        continue
    applied_urls.add(clean_url)
    
    last_id_num += 1
    job_id = f"J{last_id_num:03d}"
    
    company = j['board'].capitalize()
    title = j['title']
    loc = j['location']
    
    dispatch = classify_job(title, j.get('description', ''))
    track = dispatch['track']
    resume = dispatch['resume']
    
    priority = '1' if any(w in loc.lower() for w in ['gurgaon', 'gurugram', 'bengaluru', 'bangalore', 'remote']) else '2'
    
    row = [
        job_id,
        company,
        title,
        track,
        loc,
        priority,
        j['url'],
        'prepared_ats_submission',
        f"Tier-1 GCC opening matching {track} competencies",
        "AWS; Kubernetes; Terraform; Docker; Linux; SRE; Prometheus; Grafana; Python",
        "Ready for ATS submission / direct referral",
        resume,
        TODAY_STR,
        "Open / Market",
        "prepared_portal_unsubmitted",
        "",
        f"ats_discovery_{TODAY_STR}_{job_id}",
        FOLLOWUP_STR
    ]
    new_entries.append(row)

if new_entries:
    with open(TRACKER_FILE, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(new_entries)

print(f"Successfully ingested {len(new_entries)} pure-India GCC positions into tracker.csv.")
print(f"Total tracked opportunities now: {len(existing_rows) - 1 + len(new_entries)} (Target: 171)")

