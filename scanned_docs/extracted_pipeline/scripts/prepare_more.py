"""Prepare researched email applications; this script never sends mail."""
from pathlib import Path
import csv, json, zipfile, html

root=Path(__file__).resolve().parents[1]
batch=[
 ('J012','Decipher Consultancy','DevOps Engineer','careers@decipherconsultancy.in','https://decipherconsultancy.in/careers','decipher_devops','Your remote DevOps opening matches my AWS, Docker, CI/CD, Linux, and monitoring experience. I am interested in supporting reliable production operations and improving recurring operational workflows through automation.'),
 ('J013','Cylus Creators','Cloud & DevOps Engineer','careers@cyluscreators.com','https://cyluscreators.com/careers/','cylus_cloud_devops','I am interested in your remote Cloud & DevOps Engineer role. My strongest platform experience is AWS, with Terraform, Jenkins, Docker, and Kubernetes delivery workflows. I would welcome the opportunity to contribute to cloud foundations and repeatable client deployments.'),
 ('J014','JA Global','DevOps Engineer','careers@jaglobal.in','https://jaglobals.com/careers/','ja_global_devops','I am applying for your remote DevOps Engineer opening. I would like to build dependable deployment pipelines and cloud automation that make releases easier for engineering teams to operate and troubleshoot.'),
 ('J015','Algorian Software Solutions','DevOps Engineer','careers@algoriansolutions.com','https://www.algoriansolutions.com/jobs/dev-ops-engineer','algorian_devops','I am applying for the DevOps Engineer opening with Remote as my preferred location. My enterprise logistics application experience includes AWS infrastructure, CI/CD delivery, Kubernetes deployments, and production troubleshooting, which I would bring to supporting smooth application operations.'),
 ('J016','Vipra Software','DevOps','careers@viprasoftware.com','https://www.viprasoftware.com/','vipra_devops','I am interested in the DevOps opportunities advertised in your careers section. My experience supporting AWS infrastructure and enterprise application deployments aligns with reliable platform operations for distributed engineering teams. I am seeking a remote role in India.'),
]
base=(root/'resumes/devops.txt').read_text(encoding='utf-8')
old_summary=base.split('SUMMARY\n',1)[1].split('\n\nSKILLS',1)[0]
summaries=[
 'DevOps engineer experienced in AWS operations, Docker and Kubernetes deployments, CI/CD, Linux administration, and monitoring. Automates operational tasks using Python and Bash and collaborates with developers on reliable application releases.',
 'AWS and DevOps engineer with Terraform infrastructure automation, Jenkins CI/CD, Docker, and Kubernetes experience. Supports repeatable cloud deployments, application routing, access controls, and operational troubleshooting for enterprise applications.',
 'DevOps engineer with AWS, Terraform, Jenkins, Ansible, Docker, and Kubernetes experience. Builds repeatable deployment workflows and supports engineering teams through build troubleshooting, cloud operations, and Python/Bash automation.',
 'DevOps engineer experienced in AWS infrastructure and enterprise logistics application delivery. Combines Jenkins CI/CD, Kubernetes, Terraform, and Linux administration with operational troubleshooting and release support.',
 'AWS and DevOps engineer supporting enterprise application infrastructure, Kubernetes deployments, Terraform automation, and CI/CD delivery. Experienced in operational troubleshooting and Python/Bash scripting for distributed cloud environments.',
]
tracker=root/'applications/tracker.csv'
with tracker.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
existing={r['id'] for r in rows}
out=[]
for item, summary in zip(batch,summaries):
    jid,company,role,email,url,slug,note=item
    # Do not recreate or resend an application already recorded as submitted.
    previous=next((r for r in rows if r['id']==jid),None)
    if previous and previous['application_status'].startswith('submitted'):
        continue
    cv=base.replace(old_summary,summary)
    (root/f'resumes/{slug}.txt').write_text(cv,encoding='utf-8')
    with zipfile.ZipFile(root/'resumes/devops.docx') as z:
        entries={n:z.read(n) for n in z.namelist()}
    entries['word/document.xml']=entries['word/document.xml'].decode().replace(html.escape(old_summary),html.escape(summary)).encode()
    with zipfile.ZipFile(root/f'resumes/{slug}.docx','w',zipfile.ZIP_DEFLATED) as z:
        for name,data in entries.items(): z.writestr(name,data)
    body=f'''Hello {company} hiring team,

{note}

I currently work as a DevOps Engineer at Programming.com in Delhi. My experience includes AWS, Terraform, Jenkins, Docker, Kubernetes, Linux, and Python/Bash automation, supporting enterprise application infrastructure and releases.

Current CTC: INR 20 LPA
Expected CTC: INR 30 LPA, subject to role and compensation structure
Notice period: 30 days
Current location: Delhi, India
Preferred work arrangement: Remote India

Please find my tailored CV attached. I would welcome an opportunity to discuss the role.

Regards,
Rahul Kumar
+91-7210476048
RKTECH7621@GMAIL.COM'''
    data=dict(id=jid,company=company,role=role,to=email,url=url,resume_basename=slug,subject=f'Application: {role} — Rahul Kumar — Remote India',body=body)
    out.append(data)
    (root/f'applications/{jid}_{slug}.md').write_text(f'# {company}: {role}\n\nStatus: prepared; not submitted.\n\nSource: {url}\nRecipient: {email}\nCV: ../resumes/{slug}.docx\n\n{body}\n',encoding='utf-8')
    if jid not in existing:
        row={field:'' for field in fields}
        row.update(id=jid,company=company,role=role,track='DevOps',location='Remote India',location_priority='1',url=url,verification='employer_page_checked',preliminary_fit='Relevant; full screening pending',matching_topics='AWS; CI/CD; containers; automation',gaps='Salary budget unconfirmed; detailed role requirements may require recruiter screening',resume_basename=slug,checked_date='2026-10-17',salary_status='30 LPA fit unconfirmed',application_status='prepared_email')
        rows.append(row)
with tracker.open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
(root/'applications/batch_20261017.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(f'Prepared {len(out)} new tailored email applications; existing submission receipts preserved.')
