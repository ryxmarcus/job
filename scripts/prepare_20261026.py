"""Prepare tailored CVs for roles verified on 26 October 2026; never submit."""
from pathlib import Path
import csv, html, zipfile
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
jobs = [
    ('J028', 'Cohere Health', 'DevOps Engineer', 'Hyderabad',
     'https://job-boards.greenhouse.io/coherehealth/jobs/8037633003', 'cohere_health_devops',
     'DevOps engineer with 4+ years of experience supporting AWS infrastructure, Kubernetes deployments, CI/CD, Linux systems, and production troubleshooting. Uses Terraform, CloudFormation, Jenkins, Python, and Bash to automate repeatable cloud operations and application delivery.',
     'Strong match on AWS, Terraform, Jenkins, Python/Bash and observability. Confirm a genuine example before answering the required SLO/SLI, incident leadership, runbook and post-mortem question. Do not claim Java, Datadog, Okta, LUA or direct SLO ownership without evidence.'),
    ('J029', 'Zimperium', 'Site Reliability Engineer - India', 'Remote India',
     'https://jobs.lever.co/zimperium/29aff3bb-b00f-457c-9ebb-70f3804c3fa6', 'zimperium_sre',
     'DevOps engineer with 4+ years of experience in AWS operations, Kubernetes and Docker deployments, Linux administration, CI/CD, infrastructure automation, and production troubleshooting. Builds repeatable delivery workflows using Terraform, Jenkins, Python, Bash, and Ansible.',
     'Good technical overlap, but the description calls the position Senior. Do not claim Datadog, Solaris, Docker Swarm, data warehousing or junior mentoring without evidence.'),
    ('J030', 'American Express Global Business Travel', 'DevOps Engineer', 'Gurgaon / Bangalore',
     'https://travelhrportal.wd1.myworkdayjobs.com/en-US/Jobs/job/DevOps-Engineer_J-80130', 'amex_gbt_devops',
     'DevOps engineer with 4+ years of experience in AWS infrastructure, Jenkins CI/CD, Kubernetes deployments, Terraform, CloudFormation, and Linux operations. Automates build, deployment, and operational workflows using Python, Bash, Git, Docker, and Ansible.',
     'Promising Gurgaon role. The accessible listing confirms CI/CD, Jenkins and GitHub Actions responsibilities, but the full qualification section was unavailable; recheck before submission. Do not add GitHub Actions experience unless confirmed.'),
    ('J031', 'Drivetrain', 'Site Reliability Engineer - SRE', 'Remote India',
     'https://jobs.lever.co/drivetrain/d1bc29ad-d0aa-47c8-8785-1094f279ccff', 'drivetrain_sre',
     'DevOps engineer with 4+ years of experience supporting reliable AWS infrastructure, Kubernetes application delivery, CI/CD pipelines, Linux systems, monitoring, and infrastructure as code. Automates cloud and deployment operations with Terraform, Jenkins, Python, Bash, and Ansible.',
     'Remote India but asks for 5+ years and describes a Senior SRE. Treat as a stretch application; do not inflate tenure or claim unverified SRE ownership.'),
]

base = (root/'resumes/devops.txt').read_text(encoding='utf-8')
old_summary = base.split('SUMMARY\n',1)[1].split('\n\nSKILLS',1)[0]
tracker = root/'applications/tracker.csv'
with tracker.open(encoding='utf-8-sig', newline='') as fh:
    reader = csv.DictReader(fh); fields, rows = reader.fieldnames, list(reader)
index = ['# Applications prepared 26 October 2026', '',
         'Status: NOT SUBMITTED. Use the official links below.', '',
         'Confirmed: 4+ years overall experience; Programming.com; DevOps Engineer; 30-day notice; current INR 20 LPA; expected INR 30 LPA.', '',
         'Unverified skills and ownership claims are excluded. MBA is omitted pending completion confirmation.', '']

for jid, company, role, location, url, slug, summary, gaps in jobs:
    cv = base.replace(old_summary, summary)
    cv = '\n'.join(line for line in cv.splitlines() if not line.startswith('MBA,')) + '\n'
    cv = cv.replace('SUMMARY\n', 'LinkedIn: https://www.linkedin.com/in/rahul-kumar-74a7b662/\n\nSUMMARY\n', 1)
    (root/f'resumes/{slug}.txt').write_text(cv, encoding='utf-8')
    with zipfile.ZipFile(root/'resumes/devops.docx') as source:
        entries = {name: source.read(name) for name in source.namelist()}
    paragraphs = ''.join('<w:p><w:r><w:t xml:space="preserve">'+html.escape(line)+'</w:t></w:r></w:p>' for line in cv.splitlines())
    entries['word/document.xml'] = ('<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'+paragraphs+'<w:sectPr/></w:body></w:document>').encode()
    output = root/f'resumes/{slug}.docx'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as target:
        for name, data in entries.items(): target.writestr(name, data)
    with zipfile.ZipFile(output) as check:
        assert check.testzip() is None; ET.fromstring(check.read('word/document.xml'))
    cover = f'Dear {company} hiring team,\n\nI am applying for the {role} position. I currently work as a DevOps Engineer at Programming.com. {summary} I would welcome the opportunity to discuss how my experience could contribute to your team.\n\nMy notice period is 30 days, and I am not currently serving notice.\n\nRegards,\nRahul Kumar'
    (root/f'applications/{jid}_{slug}.md').write_text(f'# {company}: {role}\n\nStatus: prepared_portal_unsubmitted\n\nApply: {url}\n\nCV: ../resumes/{slug}.docx\n\nScreening notes: {gaps}\n\n## Cover note\n\n{cover}\n', encoding='utf-8')
    index += [f'## {company}', f'- [Apply]({url})', f'- [Tailored CV](../resumes/{slug}.docx)', f'- Screening: {gaps}', '']
    if not any(r['url'].rstrip('/').removesuffix('/apply') == url.rstrip('/').removesuffix('/apply') for r in rows):
        row = dict.fromkeys(fields, '')
        row.update(id=jid, company=company, role=role, track='DevOps/SRE', location=location, url=url,
                   verification='official_page_checked', preliminary_fit='See screening notes', gaps=gaps,
                   resume_basename=slug, checked_date='2026-10-26', salary_status='30 LPA fit unconfirmed',
                   application_status='prepared_portal_unsubmitted')
        rows.append(row)
with tracker.open('w', encoding='utf-8-sig', newline='') as fh:
    writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
(root/'applications/APPLY_20261026.md').write_text('\n'.join(index)+'\n', encoding='utf-8')
print('Prepared and validated 4 tailored CVs; tracker updated; nothing submitted.')
