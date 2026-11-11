import csv
from collections import Counter

with open(r'C:\Users\rah_66160\iTopaz-agents\job\applications\tracker.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

print(f"Total Rows Tracked: {len(rows)}")

# Submissions today
today = [r for r in rows if r.get('submitted_date') == '2026-11-11' and (r.get('application_status') or '').lower() in ['submitted', 'applied']]
print(f"\n--- SUBMITTED TODAY (11 Nov 2026): {len(today)} ---")
for r in today:
    comp = r.get('company') or 'Direct'
    print(f"  * [{r.get('id')}] {comp} - {r.get('role')} ({r.get('location')}) [{r.get('verification')}]")

# Total submitted all time
submitted_all = [
    r for r in rows 
    if (r.get('application_status') or '').lower() in ['submitted', 'applied', 'submitted_by_email', 'submitted_portal']
]
print(f"\n--- TOTAL SUBMITTED ALL TIME: {len(submitted_all)} ---")

# Breakdown by status
print("\n--- STATUS BREAKDOWN (ALL 225 LISTINGS) ---")
counts = Counter(r.get('application_status') for r in rows)
for s, c in counts.most_common():
    print(f"  - {s}: {c}")

# Verification breakdown among submitted
verif_counts = Counter(r.get('verification') for r in submitted_all)
print("\n--- SUBMISSION CHANNELS / VERIFICATION ---")
for v, c in verif_counts.most_common():
    print(f"  - {v}: {c}")
