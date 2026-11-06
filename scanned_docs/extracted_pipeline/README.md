# Rahul Kumar — Job Search & Multi-Year Career Automation Workspace (2026 – 2028)

**Last Audited & Updated:** 18 October 2026 (Asia/Kolkata)  
**Target Tracks:** Site Reliability Engineering (SRE), DevOps Engineering, MLOps / AI Platform, and Forward Deployed Engineering (FDE).  
**Primary Employer Focus:** Global Capability Centers (GCCs) in Gurgaon / Delhi NCR, Remote India, and Tier-1 Tech Hubs (Bengaluru / Hyderabad).  
**Compensation Policy:** Open / Not Disclosed across all CVs, cover letters, and portal submissions.

---

## 1. Google Drive Workspace & Live Deliverables

All documents, trackers, and PDF resumes are synced to your Google Drive folder:
- **Main Drive Folder:** [Rahul Kumar - Career & Job Applications (2026-2028)](https://drive.google.com/drive/folders/19CtPRyBF4PqB8h15Hgio1O0YpEMFoktW)
- **Live Master Tracker:** [Job Application Tracker (2026-2028)](https://docs.google.com/spreadsheets/d/17p_0_0e3NYw685Wnbo5GSiW-UUMbdEzKsTMrGx48lgs/edit) (48 tracked listings)
- **Master Career Roadmap:** [Rahul Kumar - Multi-Year Career & Application Flow (2026-2028)](https://docs.google.com/document/d/159_EtUmXajJe0T_zFGW3oVzVT14q0P1buVYGKWknE2w/edit)
- **GCC Target Guide:** [Target GCC Companies Directory & Application Guide](https://docs.google.com/document/d/1UGqwGOwAoJdcI6i-MIu0gW2rcq1eD5JvpaHU5O7t3xg/edit)
- **GCC Agency Directory:** [Top Recruitment Agencies for GCC Companies (2026 Directory)](https://docs.google.com/document/d/1gjJPG1IazerRv_QMSQ7cuidFJNXNgMYJ8GNE5rgDOZg/edit)

---

## 2. Repository Structure & Automation Scripts

- `profile.json`, `profile_2027.json`, `profile_2028.json`: Candidate baselines, location priorities, and multi-year progression profiles.
- `config.json`: Active configuration for the hourly GCC scanning and alert engine (`0 9-19 * * *`).
- `boards.json`: 15 public Greenhouse and Lever ATS feeds monitored for relevant openings.
- `applications/tracker_2026_2028.csv`: Master CSV dataset with 48 tracked roles across 2026 actuals, GCC priority leads, and 2027–2028 cohorts.
- `applications/SUBMISSIONS.md`: Confirmed email and portal submission receipts and 7-day follow-up schedule.
- `applications/PIPELINE_HEALTH_REPORT.md`: Automated audit and compliance verification report.
- `resumes/`: Editable DOCX, plain text TXT, and PDF resumes across core tracks (`devops`, `sre`, `mlops`, `fde`), employer-specific variants, and `2027/` & `2028/` progression packs.
- `scripts/pipeline_manager.py`: End-to-end compliance auditor, deduplicator, and health report generator.
- `scripts/scheduler.py`: Hourly GCC scanning and email alert runner.
- `scripts/discover_jobs.py`: Public ATS board fetcher respecting `robots.txt`.

---

## 3. Quick Commands

Run the full pipeline compliance audit and health check:
```bash
python3 job/scripts/pipeline_manager.py
```

Refresh multi-year career projections and resume variants:
```bash
python3 job/scripts/career_projection.py
python3 job/scripts/generate_full_flow.py
```
