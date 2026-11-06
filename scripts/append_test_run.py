import csv
import json

tracker_path = r'C:\Users\rah_66160\iTopaz-agents\job\applications\tracker.csv'
json_path = r'C:\Users\rah_66160\iTopaz-agents\job\applications\PIPELINE_TEST_RUN_20261102.json'

with open(tracker_path, mode='r', encoding='utf-8-sig') as f:
    existing = list(csv.reader(f))

last_id = int(existing[-1][0].replace('J', '')) if len(existing) > 1 else 0

with open(json_path, mode='r', encoding='utf-8') as f:
    tested = json.load(f)

new_rows = []
for item in tested:
    last_id += 1
    job_id = f'J{last_id:03d}'
    status = 'submitted' if item['status'] == 'SUCCESS' else 'external_redirect'
    verification = 'application_submitted_naukri' if item['status'] == 'SUCCESS' else 'external_ats_redirect'
    track = item.get('dispatch', {}).get('track', 'SRE')
    resume = item.get('dispatch', {}).get('resume', 'Rahul_Kumar_Site_Reliability_Engineer_CV.pdf')
    exp = item.get('exp', '')
    sal = item.get('sal', '') or 'Open / Market'
    loc = item.get('loc', '')
    priority = '1' if ('Bengaluru' in loc or 'Hybrid' in loc) else '2'
    gaps = 'Awaiting recruiter review' if item['status'] == 'SUCCESS' else 'Requires external ATS submission'
    
    row = [
        job_id,
        item.get('company', ''),
        item.get('title', ''),
        track,
        loc,
        priority,
        item.get('url', ''),
        verification,
        f'Direct fit {exp} matching {track} profile',
        'AWS; Kubernetes; Terraform; Docker; Linux; SRE; Prometheus; Grafana',
        gaps,
        resume,
        '2026-11-02',
        sal,
        status,
        '2026-11-02' if item['status'] == 'SUCCESS' else '',
        f'naukri_smart_2026-11-02_{job_id}',
        '2026-11-16'
    ]
    new_rows.append(row)

with open(tracker_path, mode='a', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    for r in new_rows:
        writer.writerow(r)

print(f'Successfully added {len(new_rows)} jobs. Total jobs now: {len(existing) - 1 + len(new_rows)}')

