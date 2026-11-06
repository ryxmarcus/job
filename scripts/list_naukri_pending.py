import csv
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('job/applications/tracker.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for r in reader:
        u = r.get('url') or ''
        if 'naukri.com' in u and r.get('application_status') not in ['submitted', 'applied', 'confirmed']:
            print(f"[{r['id']}] {r['company']} - {r['role']} | Status: {r.get('application_status')} | URL: {u}")

