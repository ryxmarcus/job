import csv
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('job/applications/tracker.csv', 'r', encoding='utf-8-sig') as f:
    master_rows = list(csv.DictReader(f))

# Write to drive_job_tracker.csv
drive_path = 'job/drive_job_tracker.csv'
fieldnames = ['cohort_year'] + list(master_rows[0].keys())

with open(drive_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in master_rows:
        row_dict = {'cohort_year': '2026'}
        row_dict.update(r)
        writer.writerow(row_dict)

print(f"Synced {len(master_rows)} rows to {drive_path} successfully!")

