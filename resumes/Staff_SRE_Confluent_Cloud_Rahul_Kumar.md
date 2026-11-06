# RAHUL KUMAR
**Staff Site Reliability Engineer | Cloud Infrastructure & Distributed Systems**  
New Delhi / Bengaluru, India | +91 72104 76048 | [rktech7621@gmail.com](mailto:rktech7621@gmail.com) | [linkedin.com/in/rahul-kumar-74a7b662](https://www.linkedin.com/in/rahul-kumar-74a7b662/) | [github.com/ryxmarcus](https://github.com/ryxmarcus)

---

### EXECUTIVE SUMMARY
Staff Site Reliability Engineer with deep expertise in architecting, automating, and operating high-throughput multi-cloud distributed platforms (AWS, GCP, Azure) and event streaming architectures (Apache Kafka). Specialized in proactive reliability engineering—defining org-wide SLO/SLA frameworks, error budget policies, and AI-augmented incident response ecosystems. Trusted Incident Commander for Tier-0 critical outages with extensive experience authoring Customer Root Cause Analysis (CRCA) briefs, facilitating blameless post-mortems, and scaling Kubernetes-native platforms processing millions of events per second with 99.99% availability.

---

### CORE COMPETENCIES & TECHNICAL PROFICIENCY

- **Distributed Systems & Event Streaming:** Apache Kafka (Brokers, Partitioning, ISR, KRaft Consensus, High Watermark vs LEO, Tiered Storage, Exactly-Once Semantics, Consumer Lag, Cooperative Sticky Assignors), Event-Driven Architecture.
- **Proactive Reliability & SRE:** SLO/SLA Architecture, Error Budget Policies, Incident Commander (IC), Blameless Post-Mortems, Customer Root Cause Analysis (CRCA), FMEA, Chaos Engineering, Capacity Planning.
- **Incident & Automation Tooling:** Rootly (Automated Workflows & Integrations), PagerDuty, Jira, Confluence, Slack Enterprise Grid Bots, AI-Assisted Runbooks, Automated Timeline & Post-Mortem Synthesis.
- **Cloud, Kubernetes & OS:** Multi-Cloud (AWS, GCP, Azure), Kubernetes (EKS/GKE), Istio Service Mesh, StatefulSets, Karpenter Autoscaling, Pod Anti-Affinity, Linux Kernel Internals (Zero-Copy `sendfile()`, Page Cache, TCP Sockets).
- **Observability, IaC & CI/CD:** OpenTelemetry (Distributed Tracing), Prometheus, Grafana, Datadog, ELK Stack, Terraform, Terragrunt, Helm, ArgoCD (GitOps), GitHub Actions, Python, Go, Bash Scripting.

---

### PROFESSIONAL EXPERIENCE

#### **LEAD SITE RELIABILITY & CLOUD PLATFORM ENGINEER**
**Programming.com (Client: Allcargo Gati & Logistics)** | *March 2024 – Present | New Delhi / Remote*  
*Multi-account AWS architecture (PROD, SIT, DEV, UAT) supporting iTopaz Logistics, iTariff, and Prefiler streaming 50M+ events daily across Frankfurt (eu-central-1) and Singapore.*

- **Proactive Reliability & SLO Governance:** Architected org-wide Service Level Objective (SLO) and Error Budget frameworks across 40+ microservices (`itariff-api`, `itopaz-platform`, `prefiler`); leveraged error budget burn-rate alerts to govern release velocity, reducing high-severity production incidents by **48%** within 12 months.
- **Rootly & PagerDuty Modernization:** Spearheaded overhaul of incident response; integrated Rootly workflows with PagerDuty, Slack, and Jira, automating incident channel provisioning, role assignments (IC, Scribe, Comms Lead), and MTTR tracking. Slashed Mean Time to Acknowledge (MTTA) from **14 mins to < 90 seconds**.
- **Incident Command & Customer Root Cause Analysis (CRCA):** Served as primary Escalation Incident Commander for Tier-0/1 production outages during peak shipping events. Authored and peer-reviewed **45+ Customer Root Cause Analysis (CRCA)** briefs for enterprise clients with 100% adherence to 48-hour SLAs.
- **Distributed Streaming & Kafka Optimization:** Scaled multi-tenant Kafka clusters and Aurora PostgreSQL pipelines. Optimized Linux OS page cache writeback ratios (`dirty_ratio`), tuned broker TCP socket buffers (`net.core.rmem_max`), and resolved rebalance storms via Cooperative Sticky Assignors, mitigating consumer lag by **72%**.
- **Multi-Region EKS & Istio Mesh Resilience:** Designed multi-region AWS EKS clusters (`euc1-itopaz-prd-eks`, `apse1-itopaz-sit-eks`) with Karpenter autoscaling, strict pod anti-affinity, and Istio Service Mesh (mTLS, virtual services). Deployed GitOps zero-downtime pipelines via ArgoCD, sustaining **99.99% core platform availability**.
- **Automation, FinOps & AI Incident Intelligence:** Built EventBridge/Lambda serverless schedulers (`scheduler-rds-ec2`) optimizing cluster compute spend, and developed an internal GenAI pipeline ingesting Slack transcripts and PagerDuty telemetry to auto-draft post-mortem timelines, saving ~4 engineering hours per incident.

#### **FOUNDING SITE RELIABILITY & PLATFORM ENGINEER**
**VCorp Tech (Incubated at DTU Innovation & Incubation Foundation - DTU-IIF)** | *2023 – 2025 | Delhi, India*  
*High-availability distributed cloud systems and AI application infrastructure incubated at DTU-IIF.*

- **Distributed Systems Architecture:** Architected containerized cloud infrastructure on Kubernetes and AWS, establishing multi-AZ microservice deployment topologies and automated GitOps CI/CD pipelines.
- **SRE & Incident Readiness:** Implemented Prometheus, Grafana, and OpenTelemetry observability stacks with automated alerting; authored standard operating procedures (SOPs) and runbooks for zero-downtime releases.
- **Data Streaming & Caching:** Designed asynchronous event pipelines utilizing Kafka/Redis for real-time telemetry processing, reducing message delivery latency by **40%**.

#### **SENIOR SITE RELIABILITY & CLOUD INFRASTRUCTURE ENGINEER**
**Carrier Midea India (Midea)** | *October 2020 – December 2022 | Gurugram / New Delhi, India*  
*Cloud platform engineering, automation, and reliability leadership for enterprise commercial operations and IoT streaming services.*

- **Multi-Cloud Infrastructure as Code:** Architected modular Terraform and Terragrunt configurations to provision multi-AZ AWS environments (VPC, EKS, RDS Aurora, SQS, CloudWatch) complying with enterprise CIS security benchmarks.
- **Incident Management & Runbook Automation:** Acted as on-call incident lead for platform stability; built automated PagerDuty escalation policies, self-healing health check monitors, and executable runbooks that reduced Mean Time to Recovery (MTTR) by **38%**.
- **Observability & Distributed Monitoring:** Deployed centralized Prometheus, Grafana, and ELK clusters; engineered dashboards tracking Golden Signals (Latency, Traffic, Errors, Saturation), eliminating false alarms and alert fatigue by **55%**.
- **Resilience & Chaos Engineering:** Executed regular chaos experiments and game days validating auto-failover across multi-AZ RDS clusters and event broker replicas during simulated network partitions.

---

### EDUCATION & ACADEMIC CREDENTIALS

- **Master of Business Administration (MBA) – Business Analytics** | **Delhi Technological University (DTU, formerly DCE)** | *2023 – 2025*  
  *Focus: Quantitative Systems Modeling, Large-Scale Analytics, Technology Strategy*
- **Bachelor of Technology (B.Tech) – Information Technology** | **Delhi Technological University (DTU, formerly DCE)** | *First Class with Distinction*  
  *Focus: Operating Systems, Distributed Systems, Computer Networks, Database Architecture*

---

### CURRENT CERTIFICATIONS & CREDENTIALS

- **AWS Certified DevOps Engineer – Professional (DOP-C02)** — Amazon Web Services *(Issued Oct 2026)*
- **AWS Certified Data Engineer – Associate (DEA-C01)** — Amazon Web Services *(Issued Oct 2026)*
- **AWS Knowledge: AI Driven Development Lifecycle Foundations** — AWS Skill Builder / Credly *(Score: 97%)*
- **AWS Knowledge: Cloud Essentials** — AWS Skill Builder / Credly *(Score: 96%)*
- **AWS Cloud Quest: Cloud Practitioner** — Amazon Web Services *(Issued Oct 2026)*
