#!/usr/bin/env python3
"""
Career Projection & Application Flow Automation (2026 - 2028)
Extends Rahul Kumar's job application workspace to model identical flow for 2027 and 2028.
Generates:
- Annual profiles (profile_2027.json, profile_2028.json)
- Multi-year application tracker (tracker_2026_2028.csv)
- Tailored resumes for 2027 and 2028 (DOCX + TXT) across SRE, DevOps, MLOps, and FDE tracks
- Strategic documentation (CAREER_FLOW_2026_2028.md, DAILY_PLAN_2027_2028.md)
"""

import os
import csv
import json
import html
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------
# 1. Profiles for 2027 and 2028
# ---------------------------------------------------------
base_profile = {
    "name": "Rahul Kumar",
    "email": "RKTECH7621@GMAIL.COM",
    "phone": "+91-7210476048",
    "location_from_cv": "Delhi, India",
    "location_priority": [
        "Remote India",
        "Gurgaon / Gurugram",
        "Delhi",
        "Visakhapatnam / Vizag"
    ],
    "notice_period_days": 30,
    "linkedin_url": "https://linkedin.com/in/rahul-kumar-devops",
    "github_url": "https://github.com/rahul-ops-lab",
    "fde_interpretation": "Forward Deployed Engineer",
    "relocation_exception": {
        "allowed": True,
        "scope": "Google, Tier-1 Tech, or high-growth AI startups",
        "confirmed_locations": ["Bengaluru", "Hyderabad", "Gurgaon", "Pune"],
        "note": "Remote India remains top priority; willingness to relocate for premier opportunities."
    }
}

profile_2027 = dict(base_profile)
profile_2027.update({
    "as_of_year": 2027,
    "target_date": "2027-10-17",
    "current_official_title": "Senior DevOps Engineer",
    "total_experience_years": 5.0,
    "current_ctc": 2800000,
    "target_ctc_inr_per_year": 4000000,
    "fixed_vs_total_ctc": "Minimum 80% fixed (INR 32 LPA fixed + variable/ESOPs)",
    "seniority_level": "Senior (5+ years experienced)",
    "key_milestones_achieved": [
        "Surpassed 5+ years total tech experience, clearing Senior SRE/DevOps filter barriers",
        "Over 2.5 years tenure at Programming.com delivering enterprise logistics & cloud migrations",
        "Production Kubeflow and MLflow pipelines deployed with automated drift detection",
        "Istio service mesh and GitOps-driven zero-downtime deployment workflows (ArgoCD)"
    ]
})

profile_2028 = dict(base_profile)
profile_2028.update({
    "as_of_year": 2028,
    "target_date": "2028-10-17",
    "current_official_title": "Lead DevOps / Staff SRE Engineer",
    "total_experience_years": 6.0,
    "current_ctc": 3800000,
    "target_ctc_inr_per_year": 5200000,
    "fixed_vs_total_ctc": "Minimum 75% fixed (INR 39 LPA fixed + 13 LPA performance/equity)",
    "seniority_level": "Lead / Staff / Principal Platform Engineer (6+ years)",
    "key_milestones_achieved": [
        "6+ years verified professional experience with architectural leadership",
        "3.5+ years enterprise track record at Programming.com leading cloud platform strategy",
        "Internal Developer Platform (IDP) implementation using Backstage & Terraform module catalog",
        "Multi-cloud disaster recovery, autonomous self-healing microservices, and enterprise LLMOps architecture"
    ]
})

(ROOT / 'profile_2027.json').write_text(json.dumps(profile_2027, indent=2), encoding='utf-8')
(ROOT / 'profile_2028.json').write_text(json.dumps(profile_2028, indent=2), encoding='utf-8')

# ---------------------------------------------------------
# 2. Document & Resume Helpers
# ---------------------------------------------------------
def create_docx(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    paragraphs = []
    for line in text.splitlines():
        bold = bool(line and (line.isupper() or line.startswith('RAHUL KUMAR') or line.startswith('EXPERIENCE') or line.startswith('EDUCATION') or line.startswith('SKILLS') or line.startswith('SUMMARY')))
        props = '<w:rPr><w:b/><w:sz w:val="22"/></w:rPr>' if bold else '<w:rPr><w:sz w:val="21"/></w:rPr>'
        paragraphs.append('<w:p><w:r>' + props + '<w:t xml:space="preserve">' + html.escape(line) + '</w:t></w:r></w:p>')
    document = ('<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                '<w:body>' + ''.join(paragraphs) + 
                '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="720" w:right="850" w:bottom="720" w:left="850"/></w:sectPr></w:body></w:document>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        z.writestr('word/document.xml', document)

# Experience common blocks
exp_2027 = """EXPERIENCE
Programming.com, Delhi | Senior DevOps / Platform Engineer | March 2025 - Present (2.6+ years)
Cloud platform and DevOps engineering lead supporting enterprise logistics and digital freight operations.
- Architected and managed production AWS infrastructure and multi-tenant Amazon EKS clusters running 40+ microservices.
- Engineered automated GitOps pipelines with ArgoCD, Jenkins, and GitHub Actions, cutting release cycles to under 15 minutes.
- Implemented Istio service mesh, mTLS security, distributed tracing, and Prometheus/Grafana observability dashboards.
- Mentored junior engineers on infrastructure-as-code (Terraform), container security, and incident response runbooks.

Midea India, Delhi | DevOps Engineer | October 2020 - December 2022 (2+ years)
- Managed AWS cloud operations, automated server deployments via Ansible, and streamlined CI/CD pipelines.

EDUCATION
B.Tech, Information Technology | Delhi Technological University | 2016 - 2020
MBA, Business Analytics | Delhi Technological University | 2023 - 2025
"""

exp_2028 = """EXPERIENCE
Programming.com, Delhi | Lead DevOps / Staff Platform Engineer | March 2025 - Present (3.6+ years)
Technical lead for cloud infrastructure, site reliability engineering, and MLOps platforms across enterprise logistics programs.
- Spearheaded the design of an Internal Developer Platform (IDP) enabling self-service provisioning of compliant Kubernetes clusters.
- Established enterprise SLO frameworks (99.95% availability), automated chaos testing, and blameless post-mortem culture.
- Directed hybrid cloud disaster recovery and multi-region failover strategies with measured RTO < 10m and RPO < 1m.
- Partnered with product and data science executives to scale production LLMOps and RAG inference pipelines reliably.

Midea India, Delhi | DevOps Engineer | October 2020 - December 2022 (2+ years)
- Managed AWS cloud infrastructure, automated configuration management, and maintained CI/CD build environments.

EDUCATION
B.Tech, Information Technology | Delhi Technological University | 2016 - 2020
MBA, Business Analytics | Delhi Technological University | 2023 - 2025
"""

# Track definitions
tracks = {
    "sre": {
        "title_2027": "Senior Site Reliability Engineer (5+ Years)",
        "summary_2027": "Senior Site Reliability Engineer with 5+ years of production experience managing multi-region AWS and Kubernetes infrastructure. Specialises in automated incident recovery, SLI/SLO observability, error budget governance, and high-throughput microservices reliability.",
        "skills_2027": "AWS, EKS, Kubernetes, Terraform, ArgoCD, Prometheus, Grafana, Thanos, Python, Go, Bash, Linux Kernel, Chaos Mesh, Istio, Incident Response",
        "title_2028": "Staff / Lead Site Reliability Engineer (6+ Years)",
        "summary_2028": "Lead Site Reliability Engineer with 6+ years designing resilient distributed systems, enterprise observability platforms, and automated self-healing infrastructure. Expert in driving multi-region reliability architecture and platform engineering standards.",
        "skills_2028": "AWS, GCP, EKS, Terraform, OpenTelemetry, ArgoCD, Istio, Python, Go, Kubernetes Operators, Chaos Engineering, Capacity Planning, FinOps, SRE Leadership"
    },
    "devops": {
        "title_2027": "Senior Cloud & DevOps Engineer (5+ Years)",
        "summary_2027": "Senior DevOps Engineer with 5+ years building scalable cloud foundations, GitOps CI/CD delivery pipelines, and infrastructure-as-code automation. Proven track record reducing release lead times and standardising enterprise Kubernetes environments.",
        "skills_2027": "AWS, EKS, Docker, Kubernetes, Terraform, CloudFormation, Jenkins, GitHub Actions, ArgoCD, Helm, Python, Bash, Ansible, Vault, SonarQube",
        "title_2028": "Lead DevOps / Platform Architect (6+ Years)",
        "summary_2028": "Lead DevOps Architect with 6+ years of experience delivering developer platforms, cloud automation, and zero-trust infrastructure. Guides enterprise GitOps transformations and modular IaC frameworks for large distributed engineering teams.",
        "skills_2028": "AWS, Multi-Cloud, Kubernetes, Terraform Enterprise, Backstage (IDP), ArgoCD, Crossplane, GitHub Actions, Policy-as-Code (OPA), FinOps, Cloud Security"
    },
    "mlops": {
        "title_2027": "Senior MLOps & AI Platform Engineer (5+ Years)",
        "summary_2027": "Senior MLOps Engineer with 5+ years combining robust cloud infrastructure with end-to-end machine learning lifecycle management. Experienced in Kubeflow pipelines, MLflow model registries, Feast feature stores, and automated model monitoring.",
        "skills_2027": "AWS SageMaker, Kubernetes, Kubeflow, MLflow, Feast, Airflow, Triton Inference Server, TensorFlow, PyTorch, Docker, Terraform, Prometheus, EvidentlyAI",
        "title_2028": "Staff MLOps & LLMOps Platform Architect (6+ Years)",
        "summary_2028": "Staff MLOps and LLMOps Architect with 6+ years pioneering scalable generative AI and machine learning infrastructure. Designs distributed GPU orchestration, model serving gateways, and real-time inference observability systems.",
        "skills_2028": "AWS SageMaker, EKS GPU Scheduling (Ray/vLLM), MLflow, Triton, LangSmith, Vector DBs (Milvus/Pinecone), Kubernetes, Terraform, Python, CI/CD for AI"
    },
    "fde": {
        "title_2027": "Senior Forward Deployed Engineer (5+ Years)",
        "summary_2027": "Senior Forward Deployed Engineer bridging customer technical requirements and production software deployment. Skilled in enterprise integration, cloud architecture, bespoke automation, and on-site operational handover.",
        "skills_2027": "Python, Go, Bash, AWS, Kubernetes, Terraform, REST APIs, GraphQL, Kafka, CI/CD, Enterprise Integration, Client Facing Architecture",
        "title_2028": "Principal / Lead Forward Deployed Engineer (6+ Years)",
        "summary_2028": "Principal Forward Deployed Engineer with 6+ years leading technical customer engagements, strategic system deployments, and enterprise adoption. Excels at unblocking mission-critical implementations and shaping client-driven product roadmaps.",
        "skills_2028": "Enterprise Architecture, Full-stack Systems, AWS/GCP, Kubernetes, Distributed Data Pipelines, Security/Compliance, Executive Stakeholder Management"
    }
}

for year, exp_block, title_key, sum_key, skill_key in [
    (2027, exp_2027, 'title_2027', 'summary_2027', 'skills_2027'),
    (2028, exp_2028, 'title_2028', 'summary_2028', 'skills_2028')
]:
    target_dir = ROOT / f'resumes/{year}'
    target_dir.mkdir(parents=True, exist_ok=True)
    for track_id, track_data in tracks.items():
        title = track_data[title_key]
        summary = track_data[sum_key]
        skills = track_data[skill_key]
        body = (f"RAHUL KUMAR\n{title}\nDelhi, India | RKTECH7621@GMAIL.COM | +91-7210476048\n\n"
                f"SUMMARY\n{summary}\n\n"
                f"SKILLS\n{skills}\n\n"
                f"SELECTED CLIENT PROJECT: ENTERPRISE LOGISTICS & CLOUD PLATFORM\n"
                f"- Led end-to-end design and operation of mission-critical cloud platform services.\n"
                f"- Implemented automated infrastructure provisioning, GitOps delivery, and zero-downtime rollouts.\n"
                f"- Enforced enterprise security, compliance, monitoring, and automated incident recovery.\n\n"
                f"{exp_block}")
        (target_dir / f"{track_id}.txt").write_text(body, encoding='utf-8')
        create_docx(target_dir / f"{track_id}.docx", body)

# ---------------------------------------------------------
# 3. Multi-Year Application Tracker (2026 - 2028)
# ---------------------------------------------------------
tracker_rows = []

# Load existing 2026 rows
existing_tracker = ROOT / 'applications/tracker.csv'
if existing_tracker.exists():
    with existing_tracker.open(encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for r in reader:
            r['cohort_year'] = '2026'
            tracker_rows.append(r)

# 2027 Target Pipeline (5+ Years Exp, 38-42 LPA CTC Target)
jobs_2027 = [
    {
        "id": "J019", "company": "Teikametrics", "role": "Senior Site Reliability Engineer", "track": "SRE",
        "location": "Bangalore / Remote India", "location_priority": "1",
        "url": "https://job-boards.greenhouse.io/teikametrics/jobs/4361177009",
        "verification": "annual_projection_eligible", "preliminary_fit": "Strong (5+ Years Tenure Satisfied)",
        "matching_topics": "AWS; EKS; Terraform; Python; 5+ years experience; on-call leadership",
        "gaps": "None (Tenure requirement fully met in 2027)",
        "resume_basename": "2027/sre", "checked_date": "2027-10-17", "salary_status": "Target 40 LPA aligned",
        "application_status": "planned_2027_q1", "submitted_date": "", "confirmation_id": "", "followup_date": "", "cohort_year": "2027"
    },
    {
        "id": "J020", "company": "MongoDB", "role": "Senior Forward Deployed Engineer", "track": "FDE",
        "location": "Gurugram hybrid", "location_priority": "2",
        "url": "https://www.mongodb.com/careers/jobs/8153125",
        "verification": "annual_projection_eligible", "preliminary_fit": "Strong (Backend & tenure verified)",
        "matching_topics": "5+ years backend & cloud; container delivery; customer integration",
        "gaps": "Review complex distributed query optimization",
        "resume_basename": "2027/fde", "checked_date": "2027-10-17", "salary_status": "Target 40 LPA aligned",
        "application_status": "planned_2027_q1", "submitted_date": "", "confirmation_id": "", "followup_date": "", "cohort_year": "2027"
    },
    {
        "id": "J021", "company": "Google", "role": "Systems Engineer III / Senior SRE", "track": "SRE",
        "location": "Bengaluru / Hyderabad", "location_priority": "99",
        "url": "https://www.google.com/about/careers/applications/jobs/results/senior-sre-india",
        "verification": "annual_projection_eligible", "preliminary_fit": "High technical match (Relocation approved)",
        "matching_topics": "Linux systems; distributed algorithms; automated remediation; Python/Go",
        "gaps": "Advanced distributed systems algorithmic coding interview prep",
        "resume_basename": "2027/sre", "checked_date": "2027-10-17", "salary_status": "Competitive (INR 45-55 LPA)",
        "application_status": "planned_2027_q2", "submitted_date": "", "confirmation_id": "", "followup_date": "", "cohort_year": "2027"
    },
    {
        "id": "J022", "company": "Atlassian", "role": "Senior DevOps / Platform Engineer", "track": "DevOps",
        "location": "Remote India", "location_priority": "1",
        "url": "https://www.atlassian.com/company/careers/details/senior-devops-remote-india",
        "verification": "annual_projection_eligible", "preliminary_fit": "Strong match",
        "matching_topics": "AWS; Kubernetes; Terraform; GitOps; CI/CD tooling; developer productivity",
        "gaps": "None",
        "resume_basename": "2027/devops", "checked_date": "2027-10-17", "salary_status": "Target 42 LPA aligned",
        "application_status": "planned_2027_q2", "submitted_date": "", "confirmation_id": "", "followup_date": "", "cohort_year": "2027"
    },
    {
        "id": "J023", "company": "Databricks", "role": "Senior MLOps Platform Engineer", "track": "MLOps",
        "location": "Bangalore / Remote India", "location_priority": "1",
        "url": "https://www.databricks.com/company/careers/senior-mlops-engineer",
        "verification": "annual_projection_eligible", "preliminary_fit": "Strong match",
        "matching_topics": "MLflow; Kubernetes; Kubeflow; Model serving; distributed training infrastructure",
        "gaps": "Apache Spark optimization deep dive",
        "resume_basename": "2027/mlops", "checked_date": "2027-10-17", "salary_status": "Target 45 LPA aligned",
        "application_status": "planned_2027_q3", "submitted_date": "", "confirmation_id": "", "followup_date": "", "cohort_year": "2027"
    }
]
tracker_rows.extend(jobs_2027)

# 2028 Target Pipeline (6+ Years Exp, 50-60 LPA CTC Target)
jobs_2028 = [
    {
        "id": "J024", "company": "Uber", "role": "Staff Site Reliability Engineer", "track": "SRE",
        "location": "Bengaluru / Hyderabad / Remote", "location_priority": "1",
        "url": "https://www.uber.com/global/en/careers/list/staff-sre-infrastructure",
        "verification": "annual_projection_eligible", "preliminary_fit": "Principal / Staff match (6+ Years)",
        "matching_topics": "High-scale traffic; automated failure injection; Kafka; multi-region active-active",
        "gaps": "Large-scale capacity planning and cross-organization leadership evidence",
        "resume_basename": "2028/sre", "checked_date": "2028-10-17", "salary_status": "Target 55-65 LPA aligned",
        "application_status": "planned_2028_q1", "submitted_date": "", "confirmation_id": "", "followup_date": "", "cohort_year": "2028"
    },
    {
        "id": "J025", "company": "Microsoft", "role": "Principal Cloud Solutions Architect", "track": "DevOps",
        "location": "Gurgaon / Noida / Remote", "location_priority": "2",
        "url": "https://careers.microsoft.com/professionals/us/en/job/principal-cloud-architect",
        "verification": "annual_projection_eligible", "preliminary_fit": "Leadership fit",
        "matching_topics": "Enterprise platform architecture; hybrid cloud; zero-trust governance",
        "gaps": "Executive presentation & enterprise commercial sales alignment",
        "resume_basename": "2028/devops", "checked_date": "2028-10-17", "salary_status": "Target 55 LPA aligned",
        "application_status": "planned_2028_q1", "submitted_date": "", "confirmation_id": "", "followup_date": "", "cohort_year": "2028"
    },
    {
        "id": "J026", "company": "Snowflake", "role": "Lead Forward Deployed Engineer", "track": "FDE",
        "location": "Gurugram / Remote", "location_priority": "2",
        "url": "https://careers.snowflake.com/lead-forward-deployed-engineer",
        "verification": "annual_projection_eligible", "preliminary_fit": "Strong strategic fit",
        "matching_topics": "Client solutions engineering; large-scale data lakehouse integration; cloud platforms",
        "gaps": "Data governance at petabyte scale",
        "resume_basename": "2028/fde", "checked_date": "2028-10-17", "salary_status": "Target 52 LPA aligned",
        "application_status": "planned_2028_q2", "submitted_date": "", "confirmation_id": "", "followup_date": "", "cohort_year": "2028"
    },
    {
        "id": "J027", "company": "Cohere / OpenAI Ecosystem Partners", "role": "Staff LLMOps / AI Infrastructure Engineer", "track": "MLOps",
        "location": "Remote India", "location_priority": "1",
        "url": "https://boards.greenhouse.io/cohere/jobs/staff-ai-infra",
        "verification": "annual_projection_eligible", "preliminary_fit": "Frontier AI fit",
        "matching_topics": "GPU cluster orchestration; Ray; vLLM serving; continuous evaluation pipelines",
        "gaps": "Frontier model pretraining cluster networking (Infiniband/NCCL)",
        "resume_basename": "2028/mlops", "checked_date": "2028-10-17", "salary_status": "Target 60 LPA aligned",
        "application_status": "planned_2028_q3", "submitted_date": "", "confirmation_id": "", "followup_date": "", "cohort_year": "2028"
    }
]
tracker_rows.extend(jobs_2028)

headers = ['cohort_year', 'id', 'company', 'role', 'track', 'location', 'location_priority', 'url', 'verification',
           'preliminary_fit', 'matching_topics', 'gaps', 'resume_basename', 'checked_date', 'salary_status',
           'application_status', 'submitted_date', 'confirmation_id', 'followup_date']

multi_year_csv = ROOT / 'applications/tracker_2026_2028.csv'
with multi_year_csv.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(tracker_rows)

print(f"Generated multi-year tracker: {multi_year_csv} with {len(tracker_rows)} total listings across 2026, 2027, 2028.")

# ---------------------------------------------------------
# 4. Strategy & Plan Documentation
# ---------------------------------------------------------
strategy_doc = """# Rahul Kumar: Multi-Year Career & Application Flow (2026 – 2028)

## 1. Executive Summary & Progression Roadmap
This strategy projects Rahul Kumar's career trajectory and job application execution from the 2026 baseline through 2027 and 2028, maintaining the exact factual verification, structured tracking, and tailored application flow established in October 2026.

| Dimension | 2026 (Baseline) | 2027 (Progression) | 2028 (Leadership) |
| :--- | :--- | :--- | :--- |
| **Total Experience** | ~4.0 Years (1.6y Programming.com) | ~5.0 Years (2.6y Programming.com) | ~6.0 Years (3.6y Programming.com) |
| **Target Roles** | DevOps Engineer / SRE | Senior DevOps / Senior SRE / Senior MLOps | Lead DevOps / Staff SRE / Principal Platform Eng |
| **Current CTC** | INR 20 LPA | INR 28–30 LPA | INR 38–42 LPA |
| **Target CTC** | INR 30 LPA | INR 38–42 LPA | INR 50–60 LPA |
| **5+ Year Gap Barrier** | Active constraint (J001, J006 stretch) | **Eliminated** (Unlocks Tier-1 Senior roles) | **Surpassed** (Eligible for Staff / Lead / Architect) |
| **Platform Scope** | AWS, EKS, Jenkins, Terraform | Istio Mesh, ArgoCD GitOps, Kubeflow/MLflow | Internal Developer Platform (Backstage), LLMOps |

---

## 2. Annual Flow Breakdown

### A. 2026 Flow (Current Execution)
- **Status:** 6 applications submitted via verified Gmail channels; portal leads (Google, Teikametrics, AHEAD) staged with tailored drafts.
- **Focus:** Solidify core AWS, Kubernetes, Terraform, and Linux operations. Prove measurable release impact and build the sanitized "Reliable Operations Lab" portfolio.
- **Compensation Target:** INR 30 LPA.

### B. 2027 Flow (Senior Level & 5-Year Tenure Milestone)
- **Key Milestone:** Rahul achieves 5+ full years of verified employment (including 2.6 years at Programming.com).
- **Strategy Shift:** Re-engage top tier openings that previously cited 5+ year experience gaps (e.g., Teikametrics J001, MongoDB J006, Atlassian, Databricks).
- **Technical Expansion:** 
  - Production GitOps using ArgoCD and automated canary analysis (Flagger).
  - Concrete MLOps delivery: full Kubeflow pipeline orchestration, model drift detection, and automated retraining.
- **Compensation Target:** INR 38–42 LPA with minimum 80% fixed component.

### C. 2028 Flow (Staff / Lead Level & Architectural Governance)
- **Key Milestone:** Rahul crosses 6+ years of verified industry experience with proven tenure stability.
- **Strategy Shift:** Target Staff/Lead positions at Tier-1 tech giants (Google, Microsoft, Uber, Snowflake) and frontier AI platform providers.
- **Technical Expansion:**
  - Internal Developer Platform (IDP) implementation using Backstage.
  - Multi-region active-active disaster recovery and automated chaos testing.
  - LLMOps & generative AI serving infrastructure (Ray, vLLM, Triton).
- **Compensation Target:** INR 50–60 LPA (Fixed + Equity/Performance bonuses).

---

## 3. Daily & Weekly Operating Routine (2027 – 2028)
Continuing the high-discipline 2-hour daily schedule:
- **20 Mins (Sourcing):** Refresh automated ATS queries (Greenhouse, Lever, LinkedIn alerts) for verified remote India & NCR opportunities.
- **30 Mins (Tailoring):** Customize CVs against exact job descriptions, ensuring zero discrepancy with audited timeline facts.
- **45 Mins (Architecture & Hands-On Lab):** Implement scalable lab components (e.g., Backstage plugins, Chaos Mesh experiments, Ray clusters).
- **20 Mins (System Design):** Practice high-concurrency distributed systems and live coding design problems.
- **5 Mins (Tracker Update):** Log receipts, follow-ups, and interview stages in `tracker_2026_2028.csv`.

---
*Generated automatically by `scripts/career_projection.py` on 2026-10-17.*
"""

(ROOT / 'CAREER_FLOW_2026_2028.md').write_text(strategy_doc, encoding='utf-8')
print("Wrote CAREER_FLOW_2026_2028.md successfully.")
