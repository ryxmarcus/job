import csv
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('job/applications/tracker.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for r in reader:
        u = r.get('url') or ''
        if 'lever.co' in u or 'greenhouse.io' in u or 'smartrecruiters.com' in u:
            status = r.get('application_status')
            print(f"[{r['id']}] {r['company']} - {r['role']} | Status: {status} | URL: {u}")

