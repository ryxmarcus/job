import csv
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('job/drive_job_tracker.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    drive_rows = list(reader)

print(f'Total jobs in Google Drive sheet: {len(drive_rows)}')
statuses = Counter(r.get('application_status') or 'BLANK' for r in drive_rows)
print('Drive application statuses:', statuses)

verifs = Counter(r.get('verification') or 'BLANK' for r in drive_rows)
print('Drive verification statuses:', verifs)

# Check which ones are unapplied / pending
pending = [r for r in drive_rows if (r.get('application_status') or '').lower() not in ['submitted', 'applied', 'confirmed']]
print(f'Total unapplied/pending jobs in Drive sheet: {len(pending)}')

for r in pending[:20]:
    print(f"- {r.get('id')} | {r.get('company')} | {r.get('role')} | {r.get('location')} | Status: {r.get('application_status')} | Verif: {r.get('verification')} | URL: {r.get('url')}")

