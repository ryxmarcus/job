"""Prepare application documents without submitting or changing prior receipts."""
from pathlib import Path
import csv
import html
import zipfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
jobs = [
    ('J024', 'Particle41', 'DevOps Engineer', 'Remote India', 'https://job-boards.greenhouse.io/particle41llc/jobs/5018960008', 'particle41_devops', 'DevOps engineer experienced in AWS infrastructure, Terraform, CI/CD, Docker, Kubernetes, and Linux. Automates deployments and operational tasks using Jenkins, Python, Bash, and Ansible.', 'Certification details unconfirmed. Required website can use supplied LinkedIn if accepted. Last working date is not established because candidate has not resigned.'),
    ('J025', 'Bosch', 'DevOps Engineer - Application Deployment & Configuration - K8S', 'Location unconfirmed', 'https://jobs.smartrecruiters.com/BoschGroup/744000155720139-devops-engineer-application-deployment-configuration-k8s-', 'bosch_devops', 'DevOps engineer experienced in Kubernetes application deployments, Docker image builds, Jenkins CI/CD, and release troubleshooting. Supports repeatable AWS infrastructure through Terraform and CloudFormation, with Linux administration and Python/Bash automation.', 'Role asks for 3+ years relevant experience. Exact Kubernetes tenure and job location need confirmation. Do not claim manufacturing deployment, Kafka, Solace, or gRPC experience.'),
    ('J026', 'JumpCloud', 'Site Reliability Engineer - India', 'Remote India', 'https://jobs.lever.co/jumpcloud/9bfc9bfb-15f0-4984-85dc-d1adc90a415c/apply', 'jumpcloud_sre', 'DevOps engineer with AWS, Kubernetes, Terraform, Linux, and Python/Bash automation experience. Supports cloud monitoring, infrastructure operations, and deployment troubleshooting for enterprise applications.', '5+ years requested; listed employment is approximately four years. Confirm reliable internet, electricity, phone, remote workspace, English proficiency and work authorization. Interview recording acknowledgement must be reviewed by candidate. Do not claim Go, Datadog, service mesh or disaster recovery experience.'),
    ('J027', 'GSPANN', 'DevOps Engineer', 'Gurugram / Hyderabad', 'https://careers.gspann.com/jobs/open-positions/devops-engineer', 'gspann_devops', 'DevOps engineer experienced in infrastructure as code, Jenkins CI/CD, Docker, Kubernetes, and Python/Bash automation on AWS. Supports repeatable infrastructure provisioning, application releases, Linux operations, and troubleshooting.', '6-10 years requested; candidate has approximately four years. Azure Data Factory, Fabric, Databricks and Azure Analysis Services expertise is not established. Significant fit gap; do not invent Azure experience.'),
]
base = (root / 'resumes/devops.txt').read_text(encoding='utf-8')
old_summary = base.split('SUMMARY\n', 1)[1].split('\n\nSKILLS', 1)[0]
tracker = root / 'applications/tracker.csv'
with tracker.open(encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, list(reader)
index = ['# Applications prepared 19 October 2026', '', 'Status: NOT SUBMITTED. No browser/form-upload tool is available in this session.', '', 'Confirmed answers: Rahul Kumar; Programming.com; DevOps Engineer; Delhi, India; 30-day notice; not serving notice; current CTC INR 20 LPA; expected INR 30 LPA.', '', 'Email: RKTECH7621@GMAIL.COM | Phone: +91-7210476048', 'LinkedIn: https://www.linkedin.com/in/rahul-kumar-74a7b662/', '', 'Use approximately four years for overall listed employment, not for every individual technology. MBA omitted pending completion confirmation.', '']
for jid, company, role, location, url, slug, summary, gaps in jobs:
    cv = base.replace(old_summary, summary)
    cv = '\n'.join(line for line in cv.splitlines() if not line.startswith('MBA,')) + '\n'
    cv = cv.replace('SUMMARY\n', 'LinkedIn: https://www.linkedin.com/in/rahul-kumar-74a7b662/\n\nSUMMARY\n', 1)
    (root / f'resumes/{slug}.txt').write_text(cv, encoding='utf-8')
    with zipfile.ZipFile(root / 'resumes/devops.docx') as z:
        entries = {name: z.read(name) for name in z.namelist()}
    paragraphs = ''.join('<w:p><w:r><w:t xml:space="preserve">' + html.escape(line) + '</w:t></w:r></w:p>' for line in cv.splitlines())
    entries['word/document.xml'] = ('<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + paragraphs + '<w:sectPr/></w:body></w:document>').encode()
    output = root / f'resumes/{slug}.docx'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in entries.items():
            z.writestr(name, data)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        ET.fromstring(z.read('word/document.xml'))
    cover = f'Dear {company} hiring team,\n\nI am applying for the {role} position. I currently work as a DevOps Engineer at Programming.com. {summary} I would welcome the opportunity to discuss how this experience could contribute to your team.\n\nMy notice period is 30 days, and I am not currently serving notice.\n\nRegards,\nRahul Kumar'
    (root / f'applications/{jid}_{slug}.md').write_text(f'# {company}: {role}\n\nStatus: prepared_portal_unsubmitted\n\nApply: {url}\n\nCV: ../resumes/{slug}.docx\n\nScreening notes: {gaps}\n\n## Cover note\n\n{cover}\n', encoding='utf-8')
    index.extend([f'## {company}', f'- [Apply]({url})', f'- [Tailored CV](../resumes/{slug}.docx)', f'- Screening: {gaps}', ''])
    if not any(r['url'].rstrip('/').removesuffix('/apply') == url.rstrip('/').removesuffix('/apply') for r in rows):
        assert not any(r['id'] == jid for r in rows), 'ID collision'
        row = dict.fromkeys(fields, '')
        row.update(id=jid, company=company, role=role, track='DevOps/SRE', location=location, url=url, verification='official_page_checked', preliminary_fit='See screening notes', gaps=gaps, resume_basename=slug, checked_date='2026-10-19', salary_status='30 LPA fit unconfirmed', application_status='prepared_portal_unsubmitted')
        rows.append(row)
with tracker.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
(root / 'applications/APPLY_20261019.md').write_text('\n'.join(index), encoding='utf-8')
print('Prepared and validated four CV documents; tracker updated. No applications submitted.')
