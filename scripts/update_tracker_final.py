import csv
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

csv_path = 'job/applications/tracker.csv'

with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

today_str = '2026-11-04'

updates = {
    'J093': {'status': 'submitted', 'date': '2026-11-03', 'conf': 'lever-thinkahead-fa8521eb-thanks'},
    'J094': {'status': 'submitted', 'date': '2026-11-03', 'conf': 'lever-thinkahead-a26ab4b0-thanks'},
    'J095': {'status': 'submitted', 'date': '2026-11-03', 'conf': 'lever-lingaro-b4aa26da-thanks'},
    'J096': {'status': 'submitted', 'date': '2026-11-03', 'conf': 'lever-zimperium-5b35759a-thanks'},
    'J097': {'status': 'submitted', 'date': '2026-11-03', 'conf': 'lever-zimperium-f77ac05f-thanks'},
    'J026': {'status': 'submitted', 'date': '2026-11-03', 'conf': 'lever-jumpcloud-9bfc9bfb-thanks'},
    'J022': {'status': 'submitted', 'date': '2026-11-03', 'conf': 'lever-brightedge-submitted'},
    'J023': {'status': 'submitted', 'date': '2026-11-03', 'conf': 'lever-mactores-submitted'},
    'J152': {'status': 'submitted', 'date': '2026-11-03', 'conf': 'workday-rbs-r-00285308'},
    'J174': {'status': 'submitted', 'date': '2026-11-03', 'conf': 'oracle-amex-26015724'},
    'J002': {'status': 'closed', 'date': today_str, 'conf': '404_closed'},
    'J024': {'status': 'staged_ready_to_apply', 'date': today_str, 'conf': 'greenhouse_staged_in_browser'},
    'J028': {'status': 'staged_ready_to_apply', 'date': today_str, 'conf': 'greenhouse_staged_in_browser'},
    'J029': {'status': 'staged_ready_to_apply', 'date': today_str, 'conf': 'lever_staged_in_browser'},
    'J031': {'status': 'staged_ready_to_apply', 'date': today_str, 'conf': 'lever_staged_in_browser'},
    'J091': {'status': 'staged_ready_to_apply', 'date': today_str, 'conf': 'greenhouse_staged_in_browser'},
    'J092': {'status': 'staged_ready_to_apply', 'date': today_str, 'conf': 'greenhouse_staged_in_browser'},
    'J001': {'status': 'staged_ready_to_apply', 'date': today_str, 'conf': 'greenhouse_staged_in_browser'},
    'J025': {'status': 'staged_ready_to_apply', 'date': today_str, 'conf': 'smartrecruiters_staged_in_browser'},
}

count = 0
for r in rows:
    jid = r.get('id')
    if jid in updates:
        u = updates[jid]
        r['application_status'] = u['status']
        if u['status'] == 'submitted':
            r['submitted_date'] = u['date']
            r['confirmation_id'] = u['conf']
        else:
            r['verification'] = u['conf']
        count += 1

with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Updated {count} records in {csv_path} successfully!")

