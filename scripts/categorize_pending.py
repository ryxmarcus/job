import csv
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Read local tracker
local_jobs = {}
with open('job/applications/tracker.csv', 'r', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        local_jobs[r['id']] = r

# Read drive tracker
drive_jobs = {}
with open('job/drive_job_tracker.csv', 'r', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        drive_jobs[r['id']] = r

print(f'Local tracker count: {len(local_jobs)}')
print(f'Drive tracker count: {len(drive_jobs)}')

# Merge & find all open/pending jobs with valid URLs
all_pending = []
for j_id, r in local_jobs.items():
    status = (r.get('application_status') or '').lower()
    verif = (r.get('verification') or '').lower()
    url = r.get('url') or ''
    if status not in ['submitted', 'applied', 'confirmed'] and 'submitted' not in verif:
        all_pending.append(r)

print(f'Total pending/unsubmitted in local tracker: {len(all_pending)}')
# Categorize by portal type
portals = {}
for p in all_pending:
    u = p.get('url') or ''
    domain = u.split('/')[2] if '://' in u else 'no_url'
    portals[domain] = portals.get(domain, 0) + 1

print('Pending by domain:')
for d, c in sorted(portals.items(), key=lambda x: x[1], reverse=True):
    print(f'  {d}: {c}')

