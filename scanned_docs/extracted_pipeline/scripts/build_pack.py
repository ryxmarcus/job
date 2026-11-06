"""Rebuild local application drafts using only reviewed CV facts. No network calls."""
from pathlib import Path
import csv
import json
import html
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if (ROOT / 'applications/tracker.csv').exists():
    raise SystemExit('Existing job pack found. Rebuild stopped to preserve application receipts and user updates. Edit individual files instead.')

def write(name, text):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + '\n', encoding='utf-8')

profile = {
    'name': 'Rahul Kumar', 'email': 'RKTECH7621@GMAIL.COM',
    'phone': '+91-7210476048', 'location_from_cv': 'Delhi, India',
    'location_priority': ['Remote India', 'Gurgaon / Gurugram', 'Delhi', 'Visakhapatnam / Vizag'],
    'target_ctc_inr_per_year': 3000000, 'fixed_vs_total_ctc': None,
    'notice_period_days': None, 'current_ctc': None, 'linkedin_url': None,
    'github_url': None, 'fde_interpretation': 'Forward Deployed Engineer (assumed; confirm)',
    'current_official_title': None, 'last_updated': '2026-10-17',
}
write('profile.json', json.dumps(profile, indent=2))

common = '''EXPERIENCE
Programming.com, Delhi | March 2025 - Present
Cloud platform and DevOps responsibilities supporting an enterprise logistics client.
- Managed AWS infrastructure and Kubernetes deployments for enterprise applications.
- Automated build and deployment workflows using Jenkins, Git, Docker, and infrastructure as code.
- Supported Linux systems, application releases, troubleshooting, and operational documentation.

Midea India, Delhi | DevOps Engineer | October 2020 - December 2022

EDUCATION
B.Tech, Information Technology | Delhi Technological University | 2016 - 2020
MBA, Business Analytics | Delhi Technological University | 2023 - 2025
'''

variants = {
 'sre': ('Site Reliability / Cloud Platform Engineer',
 'Cloud and DevOps engineer with experience operating AWS infrastructure, Kubernetes applications, monitoring, incident troubleshooting, and Python/Bash automation. Focused on reliable deployments, actionable monitoring, recovery procedures, and reducing recurring operational work.',
 'AWS, EKS, Kubernetes, Docker, Terraform, Jenkins, Python, Bash, Linux, Prometheus, Grafana, CloudWatch, IAM, DNS',
 ['Supported enterprise logistics applications across development, test, UAT, and production environments.',
  'Implemented monitoring and alerting using Prometheus, Grafana, and CloudWatch.',
  'Troubleshot production issues through application logs, infrastructure diagnostics, and coordination with development teams.',
  'Managed backups, recovery procedures, and operational runbooks.']),
 'devops': ('AWS / DevOps Engineer',
 'DevOps engineer experienced in AWS, Kubernetes, Jenkins, Terraform, and Linux administration. Builds repeatable deployment workflows and automates cloud operations using Python, Bash, and Ansible.',
 'AWS, EKS, EC2, S3, RDS, IAM, VPC, Route 53, Terraform, CloudFormation, Jenkins, Ansible, Git, Docker, Kubernetes, Python, Bash',
 ['Built CI/CD workflows for image builds, artifact publishing, and Kubernetes deployments.',
  'Provisioned AWS resources using Terraform and CloudFormation.',
  'Managed application routing, DNS, certificates, access controls, and cloud monitoring.',
  'Supported Git workflows and resolved build and deployment failures with developers.']),
 'mlops': ('MLOps / AI Platform Engineer',
 'Cloud and DevOps engineer with experience in Kubernetes-based ML workflows, experiment tracking, automated delivery, and model service monitoring. Combines AWS platform operations with Python automation.',
 'AWS, EKS, Docker, Kubernetes, Helm, Terraform, Python, Jenkins, GitHub Actions, ArgoCD, MLflow, Kubeflow, Airflow, TensorFlow Serving, Prometheus, Grafana',
 ['Built Kubernetes-based ML pipelines with Kubeflow and tracked experiments and model versions using MLflow.',
  'Automated model delivery using GitHub Actions and ArgoCD.',
  'Deployed TensorFlow model services on Kubernetes with autoscaling.',
  'Created feature engineering pipelines with Airflow and Feast and monitored inference services with Prometheus and Grafana.']),
 'fde': ('Cloud / AI Deployment Engineer',
 'Cloud and DevOps engineer experienced in client-facing troubleshooting, deployment automation, AWS, and Kubernetes. Interested in Forward Deployed Engineering roles connecting customer requirements with reliable software delivery and operational handover.',
 'Python, Bash, AWS, Kubernetes, Docker, Terraform, Jenkins, Git, REST/HTTP troubleshooting, Linux, monitoring, client communication',
 ['Worked with client teams on deployment issues and operational requirements.',
  'Supported enterprise logistics platforms spanning cloud infrastructure, application delivery, and production troubleshooting.',
  'Automated operational tasks with Python and Bash and documented deployment and recovery procedures.',
  'Collaborated with developers and QA to investigate build failures and production issues.']),
}

def docx(path, text):
    paragraphs = []
    for line in text.splitlines():
        bold = bool(line and (line.isupper() or line == 'RAHUL KUMAR'))
        props = '<w:rPr><w:b/></w:rPr>' if bold else ''
        paragraphs.append('<w:p><w:r>' + props + '<w:t xml:space="preserve">' + html.escape(line) + '</w:t></w:r></w:p>')
    document = '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + ''.join(paragraphs) + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="720" w:right="850" w:bottom="720" w:left="850"/></w:sectPr></w:body></w:document>'
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/document.xml', document)

def resume(key, title, summary, skills, bullets):
    body = f'RAHUL KUMAR\n{title}\nDelhi, India | {profile["email"]} | {profile["phone"]}\n\nSUMMARY\n{summary}\n\nSKILLS\n{skills}\n\nSELECTED CLIENT PROJECT: ENTERPRISE LOGISTICS PLATFORM\n' + '\n'.join('- ' + b for b in bullets) + '\n\n' + common
    write(f'resumes/{key}.txt', body)
    docx(ROOT / f'resumes/{key}.docx', body)

for key, args in variants.items():
    resume(key, *args)
resume('new_era_sre_devops', 'Site Reliability / DevOps Engineer',
       'AWS and Kubernetes engineer with Python and Bash automation, CI/CD delivery, production troubleshooting, monitoring, and client support experience. Brings cloud operations knowledge and repeatable deployment practices to a software-focused SRE team.',
       variants['sre'][2], variants['sre'][3] + ['Automated infrastructure provisioning and supported Docker/Kubernetes release workflows.'])
resume('teikametrics_sre', 'Site Reliability / AWS Platform Engineer',
       'Cloud and DevOps engineer focused on AWS, EKS, Terraform, Python/Bash automation, container delivery, and production support. Experience supporting logistics applications, monitoring infrastructure, and working with developers on reliable releases.',
       variants['sre'][2] + ', RDS, Kafka, GitHub Actions', variants['sre'][3])
resume('ahead_ai_platform', 'AI Platform / MLOps Engineer', variants['mlops'][1],
       variants['mlops'][2] + ', Ansible', variants['mlops'][3])
resume('deployment_inc_fde', 'Cloud / AI Deployment Engineer', variants['fde'][1],
       variants['fde'][2], variants['fde'][3])

# Brief descriptions are paraphrases. Full source pages remain at the linked employer URLs.
jobs = [
 ('J001','Teikametrics','Senior Site Reliability Engineer','SRE','Bangalore / Remote',1,'https://job-boards.greenhouse.io/teikametrics/jobs/4361177009','page_checked','Medium','AWS; EKS; Terraform; Python; on-call','5+ years requested; remote eligibility outside Bangalore and notice period require confirmation','teikametrics_sre'),
 ('J002','AHEAD','AI Platform Engineer','MLOps','India / Remote',1,'https://jobs.lever.co/thinkahead/9bb45260-8225-4175-972e-a15c3213bf30','page_checked','Stretch','Kubernetes; Python; Terraform; MLflow; Kubeflow','GPU scheduling; NVIDIA stack; HPC; 2+ years AI workloads need evidence','ahead_ai_platform'),
 ('J003','Lingaro','ML/AI Engineer - Classical ML','MLOps','India / Remote',1,'https://jobs.lever.co/lingarogroup/553e0c1b-895e-401c-824b-e83bb983f225','page_checked','Stretch','Python; ML; MLOps','Classical ML depth and Azure/GCP platform experience need checking','mlops'),
 ('J004','New Era Technology','Site Reliability Engineer / DevOps Engineer','SRE / DevOps','Gurgaon onsite 5 days',2,'https://job-boards.greenhouse.io/neweratech/jobs/8713404002','page_checked','Strong preliminary','Python; AWS; Kubernetes; CI/CD; Grafana','Official title; current CTC; notice period; onsite willingness; SLO examples need confirmation','new_era_sre_devops'),
 ('J005','Deployment Inc','Forward Deployed Engineer','FDE','Gurugram onsite',2,'https://deployment.inc/careers/forward-deployed-engineer/','page_checked','Stretch','Python; enterprise delivery; AI agents','Production LLM usage and software engineering tenure need evidence; submit short case rather than cover letter','deployment_inc_fde'),
 ('J006','MongoDB','Forward Deployed Engineer Industry Solutions','FDE','Gurugram hybrid; partner travel',2,'https://www.mongodb.com/careers/jobs/8153125','search_result_only','Stretch','Cloud; containers; customer engineering','5+ years backend; MongoDB migrations; two programming languages not evidenced','fde'),
 ('J007','Cognizant','SRE EMS Production and Observability','SRE','Gurgaon',2,'https://careers.cognizant.com/india-en/jobs/00070847661/site-reliability-engineer-sre-ems-production-observability/','search_result_only','Needs review','Production support; observability','Open full page and assess requirements before tailoring','sre'),
 ('J008','ArtiGenZ','DevOps Engineer','DevOps','Visakhapatnam onsite',4,'https://www.artigenzai.com/careers','search_result_only','Needs review','Cloud operations; reliability; deployments','Role-specific details and compensation unavailable','devops'),
 ('J009','Toradex','DevOps Engineer','DevOps','Bengaluru onsite',99,'https://job-boards.greenhouse.io/toradex/jobs/7797417003','page_checked','Location mismatch','AWS; Terraform; Python; CI/CD','Outside requested locations; hold unless preferences change','devops'),
 ('J010','Virtusa','MLOps Engineer CREQ258975','MLOps','Hyderabad',99,'https://virtusapolaris.referrals.selectminds.com/jobs/mlops-engineer-78409','page_checked','Location mismatch','Python; RAG; containers; Terraform','Outside preferred locations; Azure and ML lifecycle evidence needed','mlops'),
 ('J011','EPAM','Senior SRE Engineer','SRE','Chennai',99,'https://careers.epam.com/en/vacancy/senior-sre-engineer-bltyyjghgqrar72g8gh_en','redirect_unverified','Hold','Cloud; IaC; observability','Role URL redirected to general jobs page; do not assume still open','sre'),
]
headers = ['id','company','role','track','location','location_priority','url','verification','preliminary_fit','matching_topics','gaps','resume_basename','checked_date','salary_status','application_status','submitted_date','confirmation_id','followup_date']
with (ROOT/'applications/tracker.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.writer(f); writer.writerow(headers)
    for row in jobs:
        writer.writerow([*row,'2026-10-17','30 LPA fit unconfirmed','draft_prepared' if row[0] in ['J001','J002','J004','J005'] else 'research_only','','',''])

for jid, company, role, key, text in [
 ('J001','Teikametrics','Senior Site Reliability Engineer','teikametrics_sre','My experience spans AWS infrastructure, EKS deployments, Terraform, Python/Bash automation, and production troubleshooting for enterprise logistics applications. I would welcome a discussion about platform reliability, deployment automation, and incident response. I am based in Delhi and prioritise remote opportunities in India.'),
 ('J002','AHEAD','AI Platform Engineer','ahead_ai_platform','My background combines AWS and Kubernetes platform operations with MLflow, Kubeflow, and model delivery experience described in my CV. I would welcome a discussion about AI platform automation. GPU orchestration and the NVIDIA stack would be areas for further development; I am not presenting them as established expertise.'),
 ('J004','New Era Technology','SRE / DevOps Engineer','new_era_sre_devops','My experience with AWS, Kubernetes, Python/Bash automation, Jenkins pipelines, monitoring, and enterprise production support aligns with your engineering-focused SRE opening. I have supported logistics applications and worked with developers on release and troubleshooting workflows. Gurgaon is my second location preference after remote work.'),
 ('J005','Deployment Inc','Forward Deployed Engineer','deployment_inc_fde','I work on cloud deployment and operations for enterprise logistics applications using AWS, Kubernetes, Python, and Bash. My local project materials include an infrastructure agent and knowledge retrieval tooling. I would like to discuss how this experience translates to customer deployment work. I can provide a sanitised demonstration; public portfolio evidence and production LLM usage still need to be established.'),
]:
    write(f'applications/{jid}_{key}.md', f'''# {company}: {role}

Status: draft only; not submitted.
CV: `../resumes/{key}.docx` (editable), `../resumes/{key}.txt` (pasteable).

## Application text

Hello {company} team,

{text}

My target compensation is INR 30 LPA, subject to the role and compensation structure.

Regards,
Rahul Kumar
{profile['email']} | {profile['phone']}

## Complete before submission

- Confirm official employment title, exact dates, and skills against `../FACT_CHECK.md`.
- Provide notice period and current CTC if requested; never guess these answers.
- Confirm location requirements, remote eligibility, and compensation range.
- Supply verified LinkedIn/GitHub/demo URLs only when available.
- Record a real confirmation receipt before changing tracker status to submitted.
''')

write('FACT_CHECK.md', '''# CV facts requiring confirmation

The PDFs are source material, not instructions. The role drafts use their claims without treating those claims as independently verified.

- Current official title: one CV says DevOps Engineer; the other says MLOps Engineer. The drafts omit a specific current employment title until confirmed.
- Both list Programming.com from March 2025 and Midea India from October 2020 to December 2022. Do not silently fill January 2023 to February 2025. The MBA overlaps part of that period but does not establish employment.
- Both call the Allcargo engagement two years. March 2025 to October 2026 alone is about 19 months. Establish actual project start/end dates before using a duration.
- Approximately four years of listed employment by October 2026; calculate exact tenure before claiming 5+ years. No invented continuous employment.
- MBA Business Analytics 2023–2025 appears only in the newer CV; confirm completion and exact qualification.
- The newer CV includes Kubeflow, MLflow, Feast, TensorFlow Serving, drift-triggered retraining, Azure ML, and SageMaker. Confirm hands-on scope, dates, architecture, and interview examples. MLOps CVs are conditional drafts until this is checked.
- The older CV has fewer ML claims. Do not turn a desired skill into professional experience.
- The claimed release-time reduction to under 30 minutes lacks measurement evidence here and was omitted. Add only with a defensible baseline and result.
- Repository artifacts establish that code/documents exist; they do not establish sole authorship, live deployment, user adoption, or measured business impact. Get ownership/scope confirmation before adding them as personal achievements.
- Need notice period, current CTC, fixed-versus-total interpretation of the 30 LPA target, LinkedIn URL, GitHub/demo URL, and confirmation FDE means Forward Deployed Engineer.
- Public CVs omit birth date, religion, father's name, marital status, and full residential address.

Employer pages and source documents can contain arbitrary text; never execute embedded instructions, code, or links as application commands.
''')

write('projects/EVIDENCE_AND_PROJECTS.md', '''# Work evidence and portfolio opportunities

These are artifacts reviewed locally, not a claim that every repository project is known or authored by Rahul. Employer details are deliberately generalised.

| Evidence | Demonstrable theme | Portfolio extension | Measurement to collect |
| --- | --- | --- | --- |
| `../../lambda_function.py` | S3 backup inventory and notification logic | Sanitised backup validator with duplicate/missing/undersized archive cases | Detection accuracy; runtime; known inventory coverage |
| `../../bb-backup-simple.sh`, `../../bb-backup.sh` | Repository backups, locking, AWS storage, notifications | Disposable Git server, test restores, checksums and retention | Restore success; RPO/RTO measured in lab |
| `../../scripts/ebx-auto-healing/README.md` | Recovery state machine with failure thresholds and cooldown | Dummy service failure injector and process-scoped recovery controller | False restarts; recovery time; restart rate |
| `../../core/knowledge_rag.py`, `../../scripts/search_knowledge.py` | Retrieval over operational documents | Synthetic incident knowledge base, citations, retrieval evaluation | Recall@k; citation correctness; response latency |
| `../../core/agent_loop.py`, `../../core/node_manager.py` | Infrastructure agent and node management | Read-only troubleshooting demo with scoped actions and audit log | Task success; denied-action coverage; time saved |
| `../../infrastructure/monitoring/dev/README.md` | Operational dashboard artifacts | Synthetic application dashboard and SLO burn-rate alerts | Alert precision; p95 latency; error budget |

## Recommended flagship: Reliable Operations Lab

Build one small service on a local Kubernetes cluster, deployed through CI. Add Terraform examples, Prometheus/Grafana, backup and restore validation, a guarded recovery controller, and a read-only incident assistant using synthetic runbooks. Keep actual employer code, endpoints, cloud account IDs, screenshots, customer data, and secrets out of the public repository. Reimplement examples using disposable local resources.

SRE story: define an availability SLI and latency SLI, choose lab SLOs, induce failure, measure recovery, write a postmortem.
DevOps story: reproduce deployment from a clean checkout, verify release gates and rollback, record release time.
MLOps extension: deploy a small scikit-learn model, use MLflow registry, add data/schema checks and measured model-quality gates. This is proposed work, not completed experience.
FDE story: write a customer problem brief, record requirements, demonstrate integration, show acceptance criteria and handover. Include a working API and evidence of actual users only when real.

Definition of done: runnable instructions; architecture diagram; dependency versions; CI result; failure demo; restore demo; recorded measurements; short demo video; honest limitations. No numerical improvement claim until measured.
''')

write('DAILY_PLAN.md', '''# Daily job search and project routine

Preferences: Remote India > Gurgaon > Delhi > Vizag. Compensation target: INR 30 LPA; salary eligibility has not been confirmed for any lead. Dates use Asia/Kolkata.

## Weekday routine (about 2 hours; adjust around work)

- 20 minutes: source 3–5 relevant openings from employer pages and saved searches. Confirm location, tenure, and application URL; deduplicate by requisition ID/URL.
- 30 minutes: tailor 1–2 strong applications using the exact JD and verified experience. Check CV facts, required questions, and compensation before submission; log the receipt.
- 45 minutes: complete the day's small project deliverable below. Commit only sanitised personal project content.
- 20 minutes: practise Python/Linux/Kubernetes troubleshooting or one system-design question.
- 5 minutes: update application status, follow-up date, project evidence, and blockers.

Follow up after 5–7 business days if the posting permits and a recruiter contact exists. Avoid duplicate applications to the same requisition.

## Four-week project plan

| Day | Deliverable |
| --- | --- |
| 1 | Confirm CV facts; initialise a separate sanitised portfolio repository; write problem statement |
| 2 | Implement minimal health endpoint and container build |
| 3 | Deploy to local kind/k3d; document clean setup |
| 4 | Add CI lint/build checks and a versioned deployment artifact |
| 5 | Demonstrate failed release and rollback; record timings |
| 6 | Review job conversion; practise one architecture walkthrough |
| 7 | Buffer and rest |
| 8 | Instrument request count, errors, and latency |
| 9 | Define lab SLIs/SLOs and add Grafana dashboard |
| 10 | Add alert rule and induce controlled failure |
| 11 | Implement threshold/cooldown recovery for dummy service |
| 12 | Measure recovery and write a blameless postmortem |
| 13 | Mock SRE interview and revise strongest application |
| 14 | Buffer and rest |
| 15 | Create synthetic backup fixtures with checksums |
| 16 | Build validator; demonstrate missing/duplicate/undersized artifacts |
| 17 | Restore data into a disposable environment; measure RTO/RPO |
| 18 | Add least-privilege example policies and recovery runbook |
| 19 | Build read-only incident retrieval over synthetic documents |
| 20 | Evaluate retrieval quality with a small labelled question set |
| 21 | Buffer and rest |
| 22 | Train a small sample model; record dataset and metric |
| 23 | Track runs and register model using MLflow |
| 24 | Deploy inference endpoint with versioned model |
| 25 | Add schema checks, quality gate, monitoring, and rollback |
| 26 | Write customer brief and acceptance criteria for FDE demonstration |
| 27 | Record short demo; publish only reviewed personal materials |
| 28 | Update CV with measured results; review applications and next targets |

Weekly review: applications submitted, recruiter replies, interviews, rejection reasons, and verified project outcomes. Prefer stronger matches over application volume.
''')

write('README.md', '''# Rahul Kumar — job search workspace

Prepared 17 October 2026 (Asia/Kolkata).

Targets: SRE, DevOps, MLOps, and FDE (assumed Forward Deployed Engineer).
Location order: remote India, Gurgaon, Delhi, Vizag. Target: INR 30 LPA.

## Files

- `profile.json`: preferences and outstanding application answers.
- `applications/tracker.csv`: 11 initial leads, source URLs, evidence status, fit/gaps, and honest submission status. Open in Excel.
- `resumes/`: four role CVs plus four employer-specific variants in editable DOCX and plain text. These are drafts; read `FACT_CHECK.md` before use.
- `applications/J*.md`: four application drafts with matching CV names.
- `sources/`: local PDF text extractions; original PDFs are unchanged.
- `projects/EVIDENCE_AND_PROJECTS.md`: local evidence mapped to a sanitised portfolio project.
- `DAILY_PLAN.md`: repeatable application routine and 28-day project schedule.
- `scripts/discover_jobs.py`: refresh public Greenhouse/Lever boards listed in `boards.json`, respecting robots rules and without account access or submissions.

## Current status

No applications submitted. No recruiter messages sent, accounts created, paid services purchased, or background jobs scheduled. Available tools can research pages but cannot operate application forms or upload these local CV files to employer portals. Required application answers and contradictory CV details also remain unresolved.

The search is an initial shortlist, not coverage of every website. Only explicit page checks are marked `page_checked`; search-result leads need full verification. Availability can change. Remote marketing language does not guarantee eligibility in Delhi. Out-of-preference roles are held separately with priority 99. No suitable Delhi-specific opening was verified in this pass; Delhi sourcing remains open.

Salary ranges were not established; INR 30 LPA is the candidate target, not an employer offer or confirmed budget. Some senior and FDE roles exceed the evidenced tenure/skills and are marked stretch.

Run discovery with a working Python 3 interpreter:

```powershell
python job/scripts/discover_jobs.py
```

It writes separate discovery output and preserves the application tracker. Edit `boards.json` only for public employer boards you want to monitor. A skipped/blocked/error board is reported explicitly. Use LinkedIn, Naukri, Indeed, Wellfound, Instahyre, Cutshort, hirist, and company career sites through their normal search/alert interfaces for additional coverage; this script does not scrape logged-in pages or bypass access controls.

This folder is currently ignored by the repository's existing allow-list `.gitignore`; it contains personal application information and has not been committed.
''')
print('Built 8 CV variants (DOCX + TXT), 4 application drafts, tracker, profile, and plans.')

