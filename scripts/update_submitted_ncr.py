import csv
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TRACKER_FILE = Path(r"C:\Users\rah_66160\iTopaz-agents\job\applications\tracker.csv")
TODAY_STR = "2026-11-03"

with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

updated_ids = {'J152', 'J174', 'J175'}

for r in rows[1:]:
    jid = r[0]
    if jid == 'J152': # NatWest Workday
        r[14] = 'submitted'
        r[7] = 'application_submitted_workday'
        r[10] = 'Confirmed submitted via NatWest Workday ATS'
        r[15] = TODAY_STR
    elif jid == 'J174': # AMEX Oracle Cloud
        r[14] = 'submitted'
        r[7] = 'application_submitted_amex_oracle'
        r[10] = 'Confirmed submitted via AMEX Oracle Cloud CX_1'
        r[15] = TODAY_STR
    elif jid == 'J175': # Syfe Instahyre
        r[14] = 'submitted'
        r[7] = 'application_submitted_instahyre'
        r[10] = 'Confirmed submitted via Instahyre direct apply'
        r[15] = TODAY_STR

with open(TRACKER_FILE, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"Successfully updated J152 (NatWest), J174 (AMEX), and J175 (Syfe) to SUBMITTED in tracker.csv!")

# Count breakdown
counts = {}
for r in rows[1:]:
    st = r[14]
    counts[st] = counts.get(st, 0) + 1

print(f"\nTotal Tracked Positions: {len(rows) - 1}")
print(f"Status Breakdown: {counts}")

