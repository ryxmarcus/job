import csv
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('job/applications/tracker.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

pending = [r for r in rows if r.get('application_status') in ('prepared_portal_unsubmitted', 'draft_prepared', 'external_redirect')]
print(f"Total Pending in tracker.csv: {len(pending)}")
for p in pending:
    print(f"[{p['id']}] {p['company']} - {p['role']} | Status: {p['application_status']} | URL: {p['url']}")

