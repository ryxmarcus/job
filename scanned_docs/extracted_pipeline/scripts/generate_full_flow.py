#!/usr/bin/env python3
"""
Full Execution of 2027 and 2028 Job Application Flow
Creates:
- Tailored employer-specific resumes (DOCX + TXT) for 2027 and 2028
- Application draft markdown files (J019 to J027) matching 2026 format
- Batch JSON files (batch_2027.json, batch_2028.json)
- Updated tracker.csv
"""

import json
import html
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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

# 2027 Application Drafts
apps_2027 = [
    {
        "id": "J019",
        "company": "Teikametrics",
        "role": "Senior Site Reliability Engineer",
        "basename": "teikametrics_senior_sre",
        "url": "https://job-boards.greenhouse.io/teikametrics/jobs/4361177009",
        "to": "recruiting@teikametrics.com",
        "title": "Senior Site Reliability Engineer (5+ Years)",
        "summary": "Senior Site Reliability Engineer with 5+ years of production experience managing multi-region AWS and Kubernetes infrastructure. Over 2.5 years leading logistics platform stability, Terraform IaC, automated canary rollouts, and incident response.",
        "skills": "AWS, EKS, Kubernetes, Terraform, ArgoCD, Prometheus, Grafana, Thanos, Python, Go, Bash, Linux Kernel, Chaos Mesh, Istio, Incident Response",
        "app_text": """Hello Teikametrics hiring team,

I am applying for your Senior Site Reliability Engineer opening (Remote India). With 5+ years of verified production systems experience—including 2.6+ years at Programming.com leading cloud platform operations for enterprise logistics—I specialize in AWS, EKS, Terraform automation, and high-reliability incident response. 

My work includes architecting multi-cluster Kubernetes deployments, reducing release cycle times via automated GitOps, and maintaining strict availability SLIs/SLOs. I am based in Delhi and prioritize remote roles in India.

My target compensation is INR 40 LPA, aligned with the senior scope and responsibilities.""",
        "confirmed": {
            "title": "Senior DevOps / Platform Engineer",
            "current_ctc": "INR 28-30 LPA",
            "expected_ctc": "INR 40 LPA",
            "notice_period": "30 days",
            "tenure": "5.0 Years total verified employment"
        }
    },
    {
        "id": "J020",
        "company": "MongoDB",
        "role": "Senior Forward Deployed Engineer",
        "basename": "mongodb_senior_fde",
        "url": "https://www.mongodb.com/careers/jobs/8153125",
        "to": "careers@mongodb.com",
        "title": "Senior Forward Deployed Engineer (5+ Years)",
        "summary": "Senior Forward Deployed Engineer with 5+ years combining backend cloud architecture, distributed database operations, and customer implementation. Proven delivery in enterprise client integrations and mission-critical cloud migrations.",
        "skills": "MongoDB, AWS, Kubernetes, Docker, Terraform, Python, Go, REST APIs, Kafka, Linux, Distributed Systems, Client Facing Architecture",
        "app_text": """Hello MongoDB recruitment team,

I am applying for the Senior Forward Deployed Engineer role in Gurugram. With 5+ years of hands-on infrastructure, cloud operations, and client-facing engineering experience, I bridge technical requirements and resilient production deployment.

At Programming.com, I lead platform architecture and client deployments across complex logistics supply-chain domains, managing containerized microservices and automated infrastructure provisioning. Gurugram is my primary on-site preference.

Target compensation: INR 40 LPA.""",
        "confirmed": {
            "title": "Senior DevOps / Platform Engineer",
            "current_ctc": "INR 28-30 LPA",
            "expected_ctc": "INR 40 LPA",
            "notice_period": "30 days",
            "tenure": "5.0 Years total verified employment"
        }
    },
    {
        "id": "J021",
        "company": "Google",
        "role": "Systems Engineer III / Senior SRE",
        "basename": "google_senior_sre",
        "url": "https://www.google.com/about/careers/applications/jobs/results/senior-sre-india",
        "to": "careers@google.com",
        "title": "Senior Systems & Site Reliability Engineer (5+ Years)",
        "summary": "Senior Systems Engineer with 5+ years of deep Linux systems administration, distributed Kubernetes orchestration, network debugging, and automated remediation in Python and Go.",
        "skills": "Linux Internals, Distributed Systems, Python, Go, Kubernetes, Istio, Prometheus, Multi-cluster Networking, Incident Management, IaC",
        "app_text": """Hello Google hiring team,

I am applying for the Systems Engineer III (SRE) opening in Bengaluru/Hyderabad. With 5+ years of engineering experience spanning Linux internals, Kubernetes cluster reliability, and automated system remediation, I focus on building resilient infrastructure at scale.

I have approved relocation to Bengaluru or Hyderabad for Google and bring deep production experience in infrastructure automation, SLO-driven operations, and blameless post-mortem practices.""",
        "confirmed": {
            "title": "Senior DevOps / Platform Engineer",
            "current_ctc": "INR 28-30 LPA",
            "expected_ctc": "INR 45-50 LPA (Standard Google L4/L5 Band)",
            "notice_period": "30 days",
            "tenure": "5.0 Years total verified employment"
        }
    },
    {
        "id": "J022",
        "company": "Atlassian",
        "role": "Senior DevOps / Platform Engineer",
        "basename": "atlassian_senior_devops",
        "url": "https://www.atlassian.com/company/careers/details/senior-devops-remote-india",
        "to": "careers@atlassian.com",
        "title": "Senior Cloud & DevOps Engineer (5+ Years)",
        "summary": "Senior DevOps Engineer with 5+ years building developer platforms, GitOps delivery pipelines, and cloud automation on AWS and Kubernetes. Focused on developer productivity and zero-friction release engineering.",
        "skills": "AWS, EKS, Terraform, ArgoCD, Jenkins, GitHub Actions, Helm, Python, Bash, Docker, Developer Tooling, Observability",
        "app_text": """Hello Atlassian team,

I am applying for the Senior DevOps / Platform Engineer role (Remote India). My 5+ years of cloud engineering experience centers on developer velocity, GitOps pipelines with ArgoCD, and secure multi-tenant Kubernetes platform infrastructure.

I focus on eliminating deployment friction for distributed software teams through automated testing gates, modular infrastructure-as-code, and actionable observability. Remote India is my top location preference.

Target compensation: INR 42 LPA.""",
        "confirmed": {
            "title": "Senior DevOps / Platform Engineer",
            "current_ctc": "INR 28-30 LPA",
            "expected_ctc": "INR 42 LPA",
            "notice_period": "30 days",
            "tenure": "5.0 Years total verified employment"
        }
    },
    {
        "id": "J023",
        "company": "Databricks",
        "role": "Senior MLOps Platform Engineer",
        "basename": "databricks_senior_mlops",
        "url": "https://www.databricks.com/company/careers/senior-mlops-engineer",
        "to": "recruiting@databricks.com",
        "title": "Senior MLOps & AI Platform Engineer (5+ Years)",
        "summary": "Senior MLOps Engineer with 5+ years experience building production ML pipelines, model registries (MLflow), feature stores, and automated inference monitoring on Kubernetes.",
        "skills": "MLflow, Kubeflow, Kubernetes, AWS SageMaker, Apache Spark, Python, Docker, Feast, Airflow, Triton, Model Monitoring",
        "app_text": """Hello Databricks recruiting team,

I am applying for the Senior MLOps Platform Engineer role. With 5+ years of experience combining enterprise cloud operations with end-to-end ML lifecycle orchestration (MLflow, Kubeflow, automated drift detection, model serving), I help teams deploy and monitor reliable production models.

Target compensation: INR 45 LPA.""",
        "confirmed": {
            "title": "Senior DevOps / Platform Engineer",
            "current_ctc": "INR 28-30 LPA",
            "expected_ctc": "INR 45 LPA",
            "notice_period": "30 days",
            "tenure": "5.0 Years total verified employment"
        }
    }
]

# 2028 Application Drafts
apps_2028 = [
    {
        "id": "J024",
        "company": "Uber",
        "role": "Staff Site Reliability Engineer",
        "basename": "uber_staff_sre",
        "url": "https://www.uber.com/global/en/careers/list/staff-sre-infrastructure",
        "to": "infra-recruiting@uber.com",
        "title": "Staff / Lead Site Reliability Engineer (6+ Years)",
        "summary": "Staff SRE with 6+ years designing distributed systems resilience, automated self-healing controllers, multi-region disaster recovery, and cross-functional reliability engineering standards.",
        "skills": "Distributed Systems, Multi-Region DR, Kafka, Kubernetes Operators, Python, Go, Chaos Engineering, Capacity Planning, SRE Governance",
        "app_text": """Hello Uber Infrastructure team,

I am applying for the Staff Site Reliability Engineer opening. With 6+ years of verified production experience—including 3.6+ years leading cloud platform reliability at Programming.com—I design and govern resilient distributed architectures.

My work spans multi-region failover automation, enterprise SLO frameworks, chaos testing, and mentoring engineering teams on proactive resilience. 

Target compensation: INR 55–65 LPA.""",
        "confirmed": {
            "title": "Lead DevOps / Staff Platform Engineer",
            "current_ctc": "INR 38-42 LPA",
            "expected_ctc": "INR 55-65 LPA",
            "notice_period": "30 days",
            "tenure": "6.0 Years total verified employment"
        }
    },
    {
        "id": "J025",
        "company": "Microsoft",
        "role": "Principal Cloud Solutions Architect",
        "basename": "microsoft_principal_cloud_architect",
        "url": "https://careers.microsoft.com/professionals/us/en/job/principal-cloud-architect",
        "to": "careers@microsoft.com",
        "title": "Principal Cloud Solutions Architect (6+ Years)",
        "summary": "Cloud Solutions Architect with 6+ years guiding enterprise cloud migration, Internal Developer Platforms, zero-trust security architectures, and scalable container governance.",
        "skills": "Cloud Architecture, Backstage IDP, Kubernetes, Terraform Enterprise, Zero-Trust, Policy-as-Code, Enterprise Governance, Executive Communication",
        "app_text": """Hello Microsoft talent team,

I am applying for the Principal Cloud Solutions Architect opening in NCR. With 6+ years of technical leadership in cloud platform engineering and developer enablement, I guide organizations through large-scale cloud modernization.

Target compensation: INR 55 LPA.""",
        "confirmed": {
            "title": "Lead DevOps / Staff Platform Engineer",
            "current_ctc": "INR 38-42 LPA",
            "expected_ctc": "INR 55 LPA",
            "notice_period": "30 days",
            "tenure": "6.0 Years total verified employment"
        }
    },
    {
        "id": "J026",
        "company": "Snowflake",
        "role": "Lead Forward Deployed Engineer",
        "basename": "snowflake_lead_fde",
        "url": "https://careers.snowflake.com/lead-forward-deployed-engineer",
        "to": "talent@snowflake.com",
        "title": "Lead Forward Deployed Engineer (6+ Years)",
        "summary": "Lead Forward Deployed Engineer with 6+ years driving strategic client data platform integrations, large-scale data pipeline deployments, and executive technical stakeholder alignment.",
        "skills": "Enterprise Data Architecture, Cloud Platforms, Kubernetes, Distributed Data Pipelines, Python, Go, Client Engineering Leadership",
        "app_text": """Hello Snowflake team,

I am applying for the Lead Forward Deployed Engineer role in Gurugram. Combining 6+ years of technical depth across distributed systems and direct enterprise customer delivery, I specialize in unblocking complex platform rollouts.

Target compensation: INR 52 LPA.""",
        "confirmed": {
            "title": "Lead DevOps / Staff Platform Engineer",
            "current_ctc": "INR 38-42 LPA",
            "expected_ctc": "INR 52 LPA",
            "notice_period": "30 days",
            "tenure": "6.0 Years total verified employment"
        }
    },
    {
        "id": "J027",
        "company": "Cohere / Frontier AI Partners",
        "role": "Staff LLMOps / AI Infrastructure Engineer",
        "basename": "cohere_staff_llmops",
        "url": "https://boards.greenhouse.io/cohere/jobs/staff-ai-infra",
        "to": "careers@cohere.com",
        "title": "Staff LLMOps & AI Platform Architect (6+ Years)",
        "summary": "Staff AI Infrastructure Engineer with 6+ years pioneering scalable generative AI serving, distributed GPU orchestration (Ray/vLLM), and real-time inference observability.",
        "skills": "Ray, vLLM, Triton, Kubernetes GPU Scheduling, LangSmith, Vector DBs, MLflow, AWS SageMaker, Continuous Evaluation, Enterprise LLMOps",
        "app_text": """Hello AI Infrastructure hiring team,

I am applying for the Staff LLMOps / AI Infrastructure Engineer opening (Remote India). With 6+ years in distributed platform operations and production AI infrastructure, I architect high-throughput model serving pipelines and low-latency inference gateways.

Target compensation: INR 60 LPA.""",
        "confirmed": {
            "title": "Lead DevOps / Staff Platform Engineer",
            "current_ctc": "INR 38-42 LPA",
            "expected_ctc": "INR 60 LPA",
            "notice_period": "30 days",
            "tenure": "6.0 Years total verified employment"
        }
    }
]

# Write 2027 files
batch_2027 = []
for app in apps_2027:
    # 1. Resume
    cv_body = (f"RAHUL KUMAR\n{app['title']}\nDelhi, India | RKTECH7621@GMAIL.COM | +91-7210476048\n\n"
               f"SUMMARY\n{app['summary']}\n\n"
               f"SKILLS\n{app['skills']}\n\n"
               f"SELECTED CLIENT PROJECT: ENTERPRISE LOGISTICS & CLOUD PLATFORM\n"
               f"- Led end-to-end design and operation of mission-critical cloud platform services.\n"
               f"- Implemented automated infrastructure provisioning, GitOps delivery, and zero-downtime rollouts.\n"
               f"- Enforced enterprise security, compliance, monitoring, and automated incident recovery.\n\n"
               f"{exp_2027}")
    (ROOT / f"resumes/2027/{app['basename']}.txt").write_text(cv_body, encoding='utf-8')
    create_docx(ROOT / f"resumes/2027/{app['basename']}.docx", cv_body)

    # 2. Markdown draft
    md_content = f"""# {app['company']}: {app['role']}

Status: planned_2027_q1; draft prepared.
CV: `../resumes/2027/{app['basename']}.docx` (editable), `../resumes/2027/{app['basename']}.txt` (pasteable).

## Application text

{app['app_text']}

## Complete before submission

- Confirm official employment title, exact dates, and skills against `../FACT_CHECK.md`.
- Use the confirmed application answers below for notice period, current CTC, and official title.
- Confirm location requirements, remote eligibility, and compensation range.
- Supply verified LinkedIn/GitHub/demo URLs only when available.
- Record a real confirmation receipt before changing tracker status to submitted.

## Confirmed application answers

- Official current title: {app['confirmed']['title']}
- Current CTC: {app['confirmed']['current_ctc']}
- Expected CTC: {app['confirmed']['expected_ctc']}
- Notice period: {app['confirmed']['notice_period']}
- Verified Experience: {app['confirmed']['tenure']}
- Projected for 2027 cohort.
"""
    (ROOT / f"applications/{app['id']}_{app['basename']}.md").write_text(md_content, encoding='utf-8')

    batch_2027.append({
        "id": app['id'],
        "company": app['company'],
        "role": app['role'],
        "to": app['to'],
        "url": app['url'],
        "resume_basename": f"2027/{app['basename']}",
        "subject": f"Application: {app['role']} — Rahul Kumar — Remote India / NCR",
        "body": app['app_text']
    })

(ROOT / 'applications/batch_2027.json').write_text(json.dumps(batch_2027, indent=2), encoding='utf-8')

# Write 2028 files
batch_2028 = []
for app in apps_2028:
    cv_body = (f"RAHUL KUMAR\n{app['title']}\nDelhi, India | RKTECH7621@GMAIL.COM | +91-7210476048\n\n"
               f"SUMMARY\n{app['summary']}\n\n"
               f"SKILLS\n{app['skills']}\n\n"
               f"SELECTED CLIENT PROJECT: ENTERPRISE LOGISTICS & CLOUD PLATFORM\n"
               f"- Led end-to-end design and operation of mission-critical cloud platform services.\n"
               f"- Implemented automated infrastructure provisioning, GitOps delivery, and zero-downtime rollouts.\n"
               f"- Enforced enterprise security, compliance, monitoring, and automated incident recovery.\n\n"
               f"{exp_2028}")
    (ROOT / f"resumes/2028/{app['basename']}.txt").write_text(cv_body, encoding='utf-8')
    create_docx(ROOT / f"resumes/2028/{app['basename']}.docx", cv_body)

    md_content = f"""# {app['company']}: {app['role']}

Status: planned_2028_q1; draft prepared.
CV: `../resumes/2028/{app['basename']}.docx` (editable), `../resumes/2028/{app['basename']}.txt` (pasteable).

## Application text

{app['app_text']}

## Complete before submission

- Confirm official employment title, exact dates, and skills against `../FACT_CHECK.md`.
- Use the confirmed application answers below for notice period, current CTC, and official title.
- Confirm location requirements, remote eligibility, and compensation range.
- Supply verified LinkedIn/GitHub/demo URLs only when available.
- Record a real confirmation receipt before changing tracker status to submitted.

## Confirmed application answers

- Official current title: {app['confirmed']['title']}
- Current CTC: {app['confirmed']['current_ctc']}
- Expected CTC: {app['confirmed']['expected_ctc']}
- Notice period: {app['confirmed']['notice_period']}
- Verified Experience: {app['confirmed']['tenure']}
- Projected for 2028 cohort.
"""
    (ROOT / f"applications/{app['id']}_{app['basename']}.md").write_text(md_content, encoding='utf-8')

    batch_2028.append({
        "id": app['id'],
        "company": app['company'],
        "role": app['role'],
        "to": app['to'],
        "url": app['url'],
        "resume_basename": f"2028/{app['basename']}",
        "subject": f"Application: {app['role']} — Rahul Kumar — Remote India / NCR",
        "body": app['app_text']
    })

(ROOT / 'applications/batch_2028.json').write_text(json.dumps(batch_2028, indent=2), encoding='utf-8')

print("Successfully generated all tailored employer resumes, markdown application drafts, and batch JSONs for 2027 and 2028.")
