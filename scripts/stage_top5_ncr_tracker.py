import csv
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TRACKER_FILE = Path(r"C:\Users\rah_66160\iTopaz-agents\job\applications\tracker.csv")

with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

headers = rows[0]
existing_ids = {r[0]: idx for idx, r in enumerate(rows[1:], 1)}

TOP_5 = [
    {
        "id": "J154",
        "company": "Postman",
        "title": "DevOps Engineer",
        "track": "DevOps_AWS",
        "location": "Gurugram, Haryana",
        "priority": "1",
        "url": "https://myinternships.in/jobs/postman-devops-engineer-gurugram-1683be",
        "verification": "portal_staged_myinternships",
        "fit": "Direct 4.0 Yrs production Docker/K8s/CI/CD fit",
        "topics": "Docker; Kubernetes; CI/CD; Jenkins; GitHub Actions; Linux; AWS",
        "gaps": "Candidate login required on portal to complete 1-click submit",
        "resume": "DevOps_Engineer_Rahul_Kumar.pdf",
        "date": "2026-11-03",
        "salary": "Open / Not Disclosed",
        "status": "prepared_portal_unsubmitted",
        "followup": "2026-11-17"
    },
    {
        "id": "J174",
        "company": "American Express",
        "title": "Data & Cloud Infrastructure Engineer II",
        "track": "DevOps_AWS",
        "location": "Gurugram, Haryana (Cyber City)",
        "priority": "1",
        "url": "https://careers.americanexpress.com/en/sites/CX_1/job/26015724/",
        "verification": "direct_oracle_cloud_portal",
        "fit": "Direct 4.0 Yrs AWS/K8s/CI/CD infrastructure match",
        "topics": "AWS; Kubernetes; CI/CD; Docker; Terraform; Linux; Cloud Infrastructure",
        "gaps": "Oracle Cloud Recruiting direct application staged",
        "resume": "DevOps_Engineer_Rahul_Kumar.pdf",
        "date": "2026-11-03",
        "salary": "Open / Not Disclosed",
        "status": "prepared_portal_unsubmitted",
        "followup": "2026-11-17"
    },
    {
        "id": "J175",
        "company": "Syfe",
        "title": "Senior Site Reliability Engineer",
        "track": "SRE",
        "location": "Gurgaon, Haryana",
        "priority": "1",
        "url": "https://www.instahyre.com/job-444216-senior-site-reliability-engineer-at-syfe-gurgaon/",
        "verification": "instahyre_direct_portal",
        "fit": "Direct 4.0 Yrs EKS/Prometheus/Grafana/SLO match",
        "topics": "AWS; EKS; Prometheus; Grafana; SLIs/SLOs; Disaster Recovery; Incident Response",
        "gaps": "Instahyre candidate login required to trigger 1-click apply",
        "resume": "Site_Reliability_Engineer_Rahul_Kumar.pdf",
        "date": "2026-11-03",
        "salary": "Open / Not Disclosed",
        "status": "prepared_portal_unsubmitted",
        "followup": "2026-11-17"
    },
    {
        "id": "J152",
        "company": "NatWest Group",
        "title": "Platform & Software Engineer",
        "track": "DevOps_AWS",
        "location": "Gurugram, Haryana (Candor TechSpace)",
        "priority": "1",
        "url": "https://rbs.wd3.myworkdayjobs.com/RBS/job/Bengaluru/Software-Engineer_R-00285308/apply?source=",
        "verification": "workday_ats_direct",
        "fit": "Direct 4.0 Yrs Linux/CI/CD/Cloud Platform match",
        "topics": "Linux; CI/CD; AWS; Docker; Kubernetes; Cloud Platform Tooling",
        "gaps": "Workday direct portal staged; candidate login to submit",
        "resume": "DevOps_Engineer_Rahul_Kumar.pdf",
        "date": "2026-11-03",
        "salary": "Open / Not Disclosed",
        "status": "prepared_portal_unsubmitted",
        "followup": "2026-11-17"
    },
    {
        "id": "J153",
        "company": "Hasura",
        "title": "DevOps Engineer",
        "track": "DevOps_AWS",
        "location": "Gurugram, Haryana / Remote India",
        "priority": "1",
        "url": "https://myinternships.in/jobs/hasura-devops-engineer-gurugram-6131af",
        "verification": "portal_staged_myinternships",
        "fit": "Direct 4.0 Yrs Linux/Docker/CI/CD release engineering fit",
        "topics": "Linux; Docker; CI/CD; Jenkins; Kubernetes; Cloud Services",
        "gaps": "Candidate login required on portal to complete 1-click submit",
        "resume": "DevOps_Engineer_Rahul_Kumar.pdf",
        "date": "2026-11-03",
        "salary": "Open / Not Disclosed",
        "status": "prepared_portal_unsubmitted",
        "followup": "2026-11-17"
    }
]

updated_count = 0
added_count = 0

for item in TOP_5:
    jid = item["id"]
    row_data = [
        jid,
        item["company"],
        item["title"],
        item["track"],
        item["location"],
        item["priority"],
        item["url"],
        item["verification"],
        item["fit"],
        item["topics"],
        item["gaps"],
        item["resume"],
        item["date"],
        item["salary"],
        item["status"],
        "",
        f"direct_ncr_{item['date']}_{jid}",
        item["followup"]
    ]
    if jid in existing_ids:
        rows[existing_ids[jid]] = row_data
        updated_count += 1
    else:
        rows.append(row_data)
        existing_ids[jid] = len(rows) - 1
        added_count += 1

with open(TRACKER_FILE, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"Top 5 NCR Applications: {updated_count} updated, {added_count} appended to tracker.csv.")
print(f"Total entries in master tracker: {len(rows) - 1}")
