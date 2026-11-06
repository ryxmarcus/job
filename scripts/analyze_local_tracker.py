import csv
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('job/applications/tracker.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f'Total opportunities in local tracker.csv: {len(rows)}')
status_counts = Counter(r.get('application_status') or 'BLANK' for r in rows)
print('Application status counts:')
for s, c in status_counts.items():
    print(f'  {s}: {c}')

verif_counts = Counter(r.get('verification') or 'BLANK' for r in rows)
print('\nVerification counts:')
for v, c in verif_counts.most_common(10):
    print(f'  {v}: {c}')

pending_jobs = [r for r in rows if r.get('application_status') not in ['submitted', 'applied', 'confirmed'] and r.get('verification') != 'application_submitted_workday']
print(f'\nTotal unsubmitted / pending opportunities: {len(pending_jobs)}')
for j in pending_jobs[:25]:
    print(f"- {j['id']} | {j['company']} | {j['role']} | Status: {j['application_status']} | Verif: {j['verification']} | URL: {j['url']}")

