# Daily Job Search, Application & Project Routine (4-Slot Daily Schedule)

Candidate: Rahul Kumar (Asia/Kolkata)  
Location Preferences: Remote India > Gurgaon / Gurugram > Delhi > Visakhapatnam / Vizag  
Compensation Target: INR 30 LPA (2026 baseline)  

---

## Daily Schedule Structure (9 AM – 12 PM – 3 PM – 6 PM)

### 1. 09:00 AM — Morning Market Scan & Sourcing (30 Mins)
- **Objective:** Discover and ingest 3–5 newly posted openings matching target tracks (SRE, DevOps, MLOps, FDE).
- **Actions:**
  - Run discovery against public Greenhouse/Lever boards and saved job alerts.
  - Verify location eligibility (confirm Remote India or NCR onsite/hybrid).
  - Check experience requirements against verified tenure (~4 years in 2026, 5+ in 2027, 6+ in 2028).
  - Deduplicate against `applications/tracker.csv` and add new qualified entries.

### 2. 12:00 PM — Midday JD Analysis & CV Customization (45 Mins)
- **Objective:** Tailor 1–2 high-priority applications to match exact job descriptions.
- **Actions:**
  - Extract key JD requirements (e.g., AWS, EKS, Terraform, ArgoCD, Grafana, MLflow).
  - Customize the resume **Professional Summary**, **Skills**, and **Selected Project Bullets** using only verified facts from `FACT_CHECK.md`.
  - Generate matching tailored `resumes/<slug>.docx` and plain text `resumes/<slug>.txt` files.
  - Draft tailored cover letter / application body in `applications/<jid>_<slug>.md`.

### 3. 03:00 PM — Afternoon Portfolio Lab & Technical Upskilling (60 Mins)
- **Objective:** Build concrete, measurable project evidence and practice technical interviews.
- **Actions:**
  - Spend 40 minutes on the day's deliverable from the 28-Day "Reliable Operations Lab" plan (e.g., health endpoints, Kind/K3d clusters, GitOps pipelines, SLI/SLO dashboards, backup validation).
  - Spend 20 minutes on Linux kernel, Python automation, or Kubernetes troubleshooting questions.

### 4. 06:00 PM — Evening Submissions, Tracker Update & Email Digest (30 Mins)
- **Objective:** Execute submissions, update tracking records, and dispatch the daily summary report.
- **Actions:**
  - Submit email-channel applications with tailored DOCX attached (or stage portal applications for manual review).
  - Update `tracker.csv` and Google Sheet with submission timestamps, confirmation IDs, and 7-day follow-up dates.
  - Send an email digest to `RKTECH7621@GMAIL.COM` listing:
    1. Companies applied to and requisition URLs
    2. Fit score and matching technical topics
    3. Exact tailored CV format and summary sent
    4. Scheduled follow-up date and outstanding blockers

---

## Four-Week Technical Portfolio Plan (Reliable Operations Lab)

| Day | Milestone Deliverable |
| :---: | :--- |
| **1** | Confirm CV facts; initialize sanitized portfolio repo; write architecture problem statement |
| **2** | Implement minimal health endpoint and container build (Docker/Multi-stage) |
| **3** | Deploy to local kind/k3d cluster; document reproducible setup |
| **4** | Add CI lint/build checks (GitHub Actions) and versioned deployment artifact |
| **5** | Demonstrate failed release, health-check probe failure, and automated rollback |
| **6** | Weekly review of application conversion; practice architecture walkthrough |
| **7** | Rest and buffer |
| **8** | Instrument request count, error rates, and p95/p99 latency with Prometheus |
| **9** | Define lab SLIs/SLOs and configure Grafana observability dashboard |
| **10** | Add Prometheus alert rules and induce controlled container failure |
| **11** | Implement threshold/cooldown auto-recovery controller for dummy service |
| **12** | Measure recovery timings and author blameless post-mortem report |
| **13** | Mock SRE/DevOps technical interview and refine top application draft |
| **14** | Rest and buffer |
| **15** | Create synthetic database backup fixtures with sha256 checksums |
| **16** | Build backup validator; demonstrate detection of missing/undersized archives |
| **17** | Restore backup data into disposable test environment; measure RTO and RPO |
| **18** | Implement least-privilege IAM policies and disaster recovery runbook |
| **19** | Build read-only operational incident retrieval (RAG) over synthetic runbooks |
| **20** | Evaluate retrieval quality with labeled test question set (Recall@k) |
| **21** | Rest and buffer |
| **22** | Train sample machine learning model; record training dataset and baseline metrics |
| **23** | Track experiment runs and register model artifact using MLflow |
| **24** | Deploy low-latency inference endpoint with model versioning |
| **25** | Add input data schema validation, quality gate, and automated model rollback |
| **26** | Author customer deployment brief and acceptance criteria for FDE showcase |
| **27** | Record 5-minute technical demo walkthrough; publish only reviewed personal code |
| **28** | Update CV with measured lab results; review multi-year targets (2027–2028) |
