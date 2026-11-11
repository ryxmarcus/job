import csv
from pathlib import Path

tracker_path = Path(r"C:\Users\rah_66160\iTopaz-agents\job\applications\tracker.csv")
drive_path = Path(r"C:\Users\rah_66160\iTopaz-agents\job\drive_job_tracker.csv")

with open(tracker_path, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys())

# Check if J341 already present
if not any(r.get('id') == 'J341' for r in rows):
    j341_row = {fn: '' for fn in fieldnames}
    j341_row.update({
        'id': 'J341',
        'company': 'FieldAssist',
        'role': 'DevOps Engineer (Azure DevOps, AKS, Kubernetes & Observability)',
        'track': 'DevOps',
        'location': 'Gurgaon, Delhi NCR',
        'location_priority': '1',
        'url': 'https://www.instahyre.com/job-447558-devops-engineer-at-fieldassist-gurgaon/',
        'verification': 'application_submitted_instahyre',
        'preliminary_fit': 'Strong match (Gurgaon Priority-1 Tech Hub, DevOps Azure/AKS, Kubernetes, Grafana)',
        'matching_topics': 'DevOps; Azure DevOps; AKS; Kubernetes; Docker; Helm; Terraform; Grafana; GitHub Actions',
        'gaps': 'None',
        'resume_basename': 'DevOps_Engineer_Rahul_Kumar.pdf',
        'checked_date': '2026-11-11',
        'salary_status': 'Open / Not Disclosed',
        'application_status': 'submitted',
        'submitted_date': '2026-11-11',
        'confirmation_id': 'instahyre_fieldassist_447558',
        'followup_date': '2026-11-25'
    })
    rows.append(j341_row)
    with open(tracker_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print("Appended J341 to tracker.csv!")

# Sync drive_job_tracker.csv
drive_fieldnames = ['cohort_year'] + fieldnames
with open(drive_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=drive_fieldnames)
    writer.writeheader()
    for r in rows:
        row_dict = {'cohort_year': '2026'}
        row_dict.update(r)
        writer.writerow(row_dict)

print("Synchronized drive_job_tracker.csv (Total rows:", len(rows), ")")
