# Current handoff

Updated: 2026-10-30 (Asia/Kolkata).

## Objective

Assist Rahul Kumar with DevOps automation across Bitbucket & Jenkins (`itopaz-k8-repo`), infrastructure connectivity validation (AWS Glue DEV), and career profile optimization.

## Latest completed work — 2026-10-30

- **Bitbucket Push-to-Deploy Runner Setup (`itopaz-k8-repo` / `itopaz-ameta-ui-main`):**
  - **Runner Deployment:** Deployed self-hosted Linux runner (`runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`, UUID `{d9df5c8f-9b06-50a0-bf3d-c59de27d983c}`, labels `self.hosted`, `linux`) on Jenkins host `10.100.95.13` (via jump host `ubuntu@10.100.95.39`).
  - **SSL Interception Bypass:** Attached custom Java agent (`/tmp/agent.jar`, `trustall.Agent`) with `-Dio.netty.handler.ssl.noOpenSsl=true` to bypass Fortinet SSL inspection (`CN=FGVMSLTM24000312`).
  - **Authentication:** Whitelisted `https://auth.atlassian.com/oauth/token` via security team; verified HTTP 200 and runner transitioned to `ONLINE` status.
  - **Commit Filter Logic:** Updated `bitbucket-pipelines.yml` on `main` (commit `d8e3ef3d`) to trigger Jenkins job `itopaz-ameta-ui-main` (`http://10.100.95.13:8090/generic-webhook-trigger/invoke?token=itopaz-ameta-ui`) **strictly when the commit message contains `"deploy"`** (case-insensitive `grep -iq "deploy"`). Any commit without "deploy" is cleanly skipped.
  - **Firewall Whitelist Dependency:** Docker container pulls for helper `docker-public.packages.atlassian.com/sox/atlassian/bitbucket-pipelines-dvcs-tools:prod-stable` and layer redirect `docker-blobs.artifacts.atlassian.com` are intercepted by Fortinet SSL inspection. Request prepared for security team to whitelist/bypass SSL inspection.
  - **Current State:** Runner container stopped per operator request (`docker stop runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`). Can be restarted anytime with `docker start runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`.

- **AWS Glue Connectivity Validation (`sql-dev-frankfurt-dms`):**
  - **Account:** `074779643551` (DEV Frankfurt, `eu-central-1`).
  - **Connection:** `sql-dev-frankfurt-dms` (Connector `SQLSERVER`, DB `EUEUDBECUGROUPAGE`, Subnet `subnet-0ceedebf41e570f8f` [`10.100.159.32/27`, AZ `eu-central-1b`], SG `sg-0e3b87b11e66d64c5`).
  - **Destination:** `10.1.161.19:1433`.
  - **Validation:** Live socket probe (`nc -zvw 3 10.1.161.19 1433`) succeeded. AWS Glue CLI `aws glue test-connection` returned HTTP 200 (Success, Status: `READY`). Connectivity, TGW, NACLs, and SGs confirmed open.

## Latest completed work — 2026-10-29

- **Intranet UAT CodeCommit repair:** On `10.0.132.243`, CodeCommit pulls failed because the distro AWS CLI (`1.22.34`) was loading incompatible pip-installed Botocore modules. Installed an isolated AWS CLI under `/home/ubuntu/.local/awscli-codecommit` and configured the affected checkout to use it as its sole Git credential helper.
- **Validation:** CodeCommit authentication succeeds for account `745510282686`; `uat-main-branch` was fast-forwarded from `29bb56e` to `b7b6664` in `/var/www/guru/aiml-poc/intellihub-uat-main/intranet/userdetailssync`.
- **Runtime files:** Existing untracked `__pycache__` and `logs` entries were preserved. No application service was restarted.

## Confirmed changes

1. **Employment Section Updates:**
   - **Programming.com (Current):**
     - **Title:** DevOps Engineer
     - **Vendor / Employer:** Programming.com
     - **Client / Project:** Allcargo Logistics — iTOPAZ Project (Global Logistics Platform)
     - **Key Contributions:** AWS multi-account management (DEV/SIT/UAT/PROD across eu-central-1, ap-southeast-1, us-east-1), Amazon EKS (Kubernetes 1.36), node group right-sizing (AMD EPYC m6a/r6a), Terraform IaC, Jenkins & AWS CodePipeline (4-stage EAR/Docker pipeline), Docker & ECR image scanning, Aurora PostgreSQL 17.5, Prometheus & Grafana observability.
   - **Midea India (Oct 2020 – Dec 2022):**
     - **Title:** DevOps Engineer
     - **Key Contributions:** Grounded strictly in verified CV technical evidence (AWS EC2, S3 with lifecycle policies, VPC, Security Groups, CloudWatch; Jenkins CI/CD automation with GitHub webhooks; Docker containerized environments; Ansible playbooks & Bash shell scripts for server/package configuration; Git branching and release coordination).
2. **Profile Optimization Highlights:**
   - **Resume Headline:** `AWS DevOps Engineer | 4+ Yrs Exp | Kubernetes (EKS), Terraform, CI/CD Pipelines, Jenkins, Docker, Linux, Python, AWS | 30 Days Notice`
   - **Key Skills:** Corrected `Kubernates` typo to `Kubernetes`, added `AWS`, `Docker`, `Terraform`, `CI/CD`, `Python`, `Bash`, `Jenkins`.
   - **Profile Summary:** Added structured technical summary highlighting 4+ years of AWS cloud infrastructure, EKS, IaC, CI/CD, and 30-day notice availability.
   - **Online Profiles (Accomplishments):** Added verified links to LinkedIn (`https://www.linkedin.com/in/rahul-kumar-74a7b662/`) and GitHub (`https://github.com/ryxmarcus`) with cloud/DevOps descriptions.
   - **Research Publication (Accomplishments):** Added published Springer review paper: *"Biometric System: Unimodal Versus Multibiometric Fusion and Its Current Applications: Review"* (Co-authored by Mahesh, Rahul Kumar, Kapil Sharma; Published Jan 2021).
   - **IT Skills Grid:** Populated 10 core DevOps technologies with 4 years experience and 2026 recency: `AWS`, `Kubernetes`, `Terraform`, `Docker`, `Jenkins`, `CI/CD`, `Linux`, `Python`, `Git`, and `Ansible`.
3. **Infrastructure Resolution — Intranet Prod-1 (10.151.4.89):**
   - **Incident:** Disk full (`/dev/root` 100% used, 0 bytes free) causing `git pull` failures in MobaXterm and Jenkins deployment pipeline (`No space left on device`).
   - **Remediation & EBS Expansion:**
     - Vacuumed systemd journal logs (`journalctl --vacuum-size=100M`), freeing 3.5 GB.
     - Cleaned apt package cache, root pip caches (`/root/.cache`), and 5 obsolete VS Code remote server installations, freeing 4.3 GB.
     - Truncated unrotated logs (`python_zombie_cleanup.log`, `apis-autoheal.log`).
     - **EBS Volume Expansion to 100 GB:** Modified EBS volume `vol-08d34e5eb361204b9` attached to `i-0b1f3b8eda05c132b` (Intranet-prod-1) from 60 GB to 100 GB via AWS CLI from Worker 1 (`eks-jump-server-role` in account `745510282686`).
     - Expanded partition (`growpart /dev/nvme0n1 1`) and resized filesystem (`resize2fs /dev/nvme0n1p1`).
     - Current filesystem: **97 GB total, 48 GB available (51% used)**.
   - **Deployment:** Pulled latest CodeCommit commit `d427c12` into `/root/var/www/prod-latest/aiml-poc/intellihub-prod-main/userdetailssync` (`lumina_genai_wrapper.py`, `intranetapimain.py`, `trainingmodule.py`). Restarted `intranetapimain` Uvicorn service (PID 1286079); verified `200 OK` on port 8001.
4. **Worker & Infrastructure Health Status:**
   - **Worker 1 (10.151.4.165 / ap-south-1):** Online, load 0.06, 6.1 GiB free RAM, 8.2 GB free disk (73% used).
   - **Worker 2 (10.100.95.39 / eu-central-1):** Online, load 0.27, 14.5 GiB free RAM, 27 GB free disk (44% used), containers healthy (`sre-agent-crewai`, `k8s-tool-server`).
   - **Intranet Prod-1 (10.151.4.89):** Online, 48 GB free disk (51% used), API port 8001 healthy (200 OK).
   - **Intranet Prod-2 (10.151.4.153):** ⚠️ **ALERT: Disk at 97% capacity (only 2.2 GB free / 58 GB total)**. Root causes: `/root/var/www/prod-training-manual` (24 GB) and `/home/ubuntu/.vscode-server` (5.3 GB). API currently 200 OK, but at high risk of deployment or logging disk failure.
5. **Naukri Applications:**
   - **31 total verified applications submitted (200 OK)** across Gurugram, Delhi NCR, and premier hybrid/remote tech hubs (Bengaluru, Hyderabad, Pune).
   - **Latest 9 applications (2026-10-27):**
     1. Infra360 (`231026026952`, Gurugram)
     2. Incedo (`121026021696`, Gurugram)
     3. Tekskills India (`131026924500`, Noida)
     4. Moneymul Technologies (`121026037009`, Delhi/NCR)
     5. Easemytrip (`220424001633`, Noida)
     6. Techugo (`061026008581`, Noida)
     7. Rangam Infotech (`211026016314`, Gurugram)
     8. Tata Consultancy Services (`130226028841`, Noida/NCR)
     9. Infosys (`290926041282`, Hybrid Noida/BLR)
   - Detailed audit logs: [`job/applications/NAUKRI_APPLIED_20261026.md`](file:///c:/Users/rah_66160/iTopaz-agents/job/applications/NAUKRI_APPLIED_20261026.md) & [`job/applications/NAUKRI_APPLIED_20261027.md`](file:///c:/Users/rah_66160/iTopaz-agents/job/applications/NAUKRI_APPLIED_20261027.md).

6. **iTariff EUAT UI Audit (`https://itariff-euat.itopazapp.com/`):**
   - **Login & Session:** Successfully authenticated with user `export` / password `yes` (signed in as `Admin Tst`, ID `4691`, default Legal Entity: `ECU WORLDWIDE (BELGIUM) - 24`).
   - **Header Controls:** Language switcher (`ENGLISH` / `SPANISH`) and Legal Entity Material Autocomplete selector verified live.
   - **All 11 UI Modules Tested:** Masters (`/abc`), Tariff Buying & Selling (`/selling-rates/export`, `/import`, `/export-other-container`, `/import-other-container`, `/export-storage`), Trucker (`/truckerlist`), and User Security (`/user-security/manage-profile`, `/role-management`).
   - **Sign Out:** Successfully signed out from `Admin Tst` session via user profile menu; redirected to `https://itariff-euat.itopazapp.com/login`.
   - Audit report: [`job/ITARIF_EUAT_UI_AUDIT.md`](file:///c:/Users/rah_66160/iTopaz-agents/job/ITARIF_EUAT_UI_AUDIT.md).

7. **Prefiler EUSIT UI Audit (`https://prefiler-eusit.itopazapp.com/`):**
   - **Login & Session:** Successfully authenticated with user `prefiler` / password `yes` (logged in as `Prefiler User`, ID `7268`).
   - **Dashboard & Micro-Frontends Tested:** All 6 primary security filing modules tested live (`BASF`, `AMS`, `AFR`, `ACI`, `ICS2`, `MBL Filer`).
   - **Grid & Modals Verified:** AMS module verified with full data table (8 filings: 3 WIP, 1 Submitted, 4 Successful) and interactive `Import File` modal dialog.
   - Audit report: [`job/PREFILER_EUSIT_UI_AUDIT.md`](file:///c:/Users/rah_66160/iTopaz-agents/job/PREFILER_EUSIT_UI_AUDIT.md).

8. **Oracle Cloud Always Free Tier Registration:**
   - **Target:** `https://signup.cloud.oracle.com/`
   - **Step 1 Completed:**
     - Country: `India`
     - Name: `Rahul Kumar`
     - Email: `rktech7621@gmail.com`
   - **Status:** **Email verification link sent** by Oracle Cloud to `rktech7621@gmail.com` (valid for 30 minutes).
   - **Next Action for Candidate:** Check inbox at `rktech7621@gmail.com`, click the Oracle verification link to continue to Step 2 (setting account password, cloud tenancy name, and selecting Home Region).

9. **S3 Bucket Ownership Identification:**
   - **Bucket:** `freightify-ecu-report`
   - **Account ID:** `581621506601` (`BW-UAT` / TIBCO BW & Data Integration Account)
   - **Region:** `us-east-1` (N. Virginia)
   - **Folders Verified:**
     - `ecu-report-process-expired/`
     - `ecu-report-delete-batch-id/`
     - `ecu-report-delete/`
     - `ecu-report-expired/`
     - `ecu-report-process/`
     - `archived_data/`
   - **Direct Console Access URL:**
     `https://us-east-1.console.aws.amazon.com/s3/buckets/freightify-ecu-report?region=us-east-1&bucketType=general`

10. **China Prefiler SIT UI & API Inspection:**
    - **UI Login:** `https://prefiler-sit.ecuworldwide.cn/login` successfully authenticated with `prefiler` / `yes`. Logged in as `Prefiler User` (ID: `7268`, Office: `XMN - 94`, default LE: `24`).
    - **API Endpoint:** `https://prefiler-sit-api.ecuworldwide.cn/prefiler-bff/prefiler/bff/v1/aci/SubmitFile/prefiler`
    - **Technical Architecture:**
      - The URL provided is a backend REST API endpoint (`[HttpPost("SubmitFile/{username}")]` implemented in `ACI.API.Controllers.AcifileController`).
      - It requires an `Authorization: Bearer <JWT>` header and JSON payload body. Direct browser URL navigation triggers `401 Unauthorized ("Missing Authorization token or User ID")` because standard browser address bars do not transmit JWT headers.
      - In the UI application, the authenticated route is at `https://prefiler-sit.ecuworldwide.cn/aci-prefiler/filer-details`.

11. **Prefiler SIT China "Failed to submit file" (HTTP 500) Resolution & Verification:**
    - **Issue:** On `https://prefiler-sit.ecuworldwide.cn/aci-prefiler/filer-information?from=filer-details&FileId=3798&NrFile=91572`, submitting file/BL (`CHI/DUB/02982`) triggered a red UI toast `"Failed to submit file"`. DevTools showed `POST https://prefiler-sit-api.ecuworldwide.cn/prefiler-bff/prefiler/bff/v1/aci/SubmitFile/prefiler` failing with **HTTP 500**.
    - **Root Cause Discovered in Pod Logs:**
      - In namespace `prefiler-api`, pod `aci-prefiler-service-7bf445fd97-jqc64` logged:
        `Npgsql.PostgresException (0x80004005): 22001: value too long for type character varying(3)` at `AcifileRepository.SaveFileAsync` line 292.
      - Cargo records imported from `ASASDBECUGROUPAGE` for several HBLs in file 91572 (e.g. `TAO/LZC/00540`, `TAO/CAL/01343`) carried descriptive `pkgtype` strings such as `"WOODEN CASES STC"` (16 chars) and `"PALLET STC"` (10 chars).
      - The underlying PostgreSQL tables in database `CNHKGDBAMS` on `sit-db.internal-itopaz.cn` had `pkgtype` strictly typed as `character varying(3)`. When `SaveFileAsync` executed before queueing the EDI transaction, PostgreSQL rejected the write with error code 22001.
    - **Database Schema Remediation:**
      - Authenticated to `sit-db.internal-itopaz.cn` (DB: `CNHKGDBAMS`) as database administrator `pgadmin`.
      - Executed schema alter operations:
        - `ALTER TABLE dbo.acicargodetail ALTER COLUMN pkgtype TYPE character varying(100);`
        - `ALTER TABLE dbo.amscargodetail ALTER COLUMN pkgtype TYPE character varying(100);`
      - Unlocked file 3798: `UPDATE dbo.acifile SET locked = 0, lockedby = '' WHERE acifileid = 3798;`.
    - **Browser Verification Completed:**
      - Executed submission directly from the authenticated browser on `https://prefiler-sit.ecuworldwide.cn/aci-prefiler/filer-information?from=filer-details&FileId=3798&NrFile=91572`.
      - Intercepted network response: `POST https://prefiler-sit-api.ecuworldwide.cn/prefiler-bff/prefiler/bff/v1/aci/SubmitFile/prefiler` returned **HTTP 200 OK**:
        `{"Status": "Success", "Message": "File Submitted successfully ", "StatusCode": 200, "Data": {"Result": "File submitted successfully."}}`.

12. **Diagnosis of 400 and 404 on `validateFile` Endpoint:**
    - **Endpoint:** `https://prefiler-sit-api.ecuworldwide.cn/prefiler-bff/prefiler/bff/v1/aci/validateFile`
    - **400 Bad Request Root Cause:**
      - In `aci-prefiler-service` (`AciValidationController.cs`, lines 48-68), the `BuildResponse` method explicitly sets:
        `var statusCode = result.IsValid ? HttpStatusCode.OK : HttpStatusCode.BadRequest; return StatusCode((int)statusCode, response);`
      - When any HBL or cargo in the file violates ACI business validation rules (e.g. Package code > 3 chars, invalid characters `&%*`, missing port/cargo info), the API returns **HTTP 400 by design** containing the validation error list in the body payload.
    - **404 Not Found Root Cause:**
      - The endpoint is mapped strictly as `[HttpPost(BFFApiRoutes.ValidateFileNew)]`. There is **no GET handler**.
      - Opening the URL directly in a web browser or issuing a `GET` request returns **404 Not Found** (or 405 Method Not Allowed). Requests omitting the `/prefiler/bff/v1/aci/validateFile` route also return 404.

13. **Headlamp Permanent Token Configuration & Verification:**
    - **Cluster & URL:** AKS China North 3 (`cn3-itopaz-sit-aks`), `https://headlamp-sit.internal-itopaz.cn`
    - **Root Cause of Expired Token:** The previous token was generated using projected short-lived tokens (`exp: 1790235932`) which expired.
    - **Permanent Token Creation:**
      - Created a dedicated `kubernetes.io/service-account-token` secret named `headlamp-admin-token` in namespace `istio-system` bound to ServiceAccount `headlamp-admin` (which has `cluster-admin` RBAC via `headlamp-admin-binding`).
      - Verified this token has no `exp` expiration claim and persists permanently.
      - Tested via CLI (`kubectl get nodes --token="..."`) and directly logged into `https://headlamp-sit.internal-itopaz.cn/c/main/token` in the browser, successfully reaching the cluster dashboard (`https://headlamp-sit.internal-itopaz.cn/c/main/`).

14. **iTariff EUAT Login & Comprehensive Module Automation Check:**
    - **Target URL:** `https://itariff-euat.itopazapp.com/login`
    - **Authentication:** Authenticated using credentials (`export` / `yes`), transitioning directly to `https://itariff-euat.itopazapp.com/dashboard`.
    - **Automated Module Traversal (Selenium Edge):**
      - Executed automated navigation across all 11 core modules:
        1. *Masters > User Masters* (`/abc`): **PASS**
        2. *Tariff > Buying > Export* (`/buying-rates/export/shipping-line`): **PASS**
        3. *Tariff > Buying > Import* (`/buying-rates/import/shipping-line`): **PASS**
        4. *Tariff > Selling > Export* (`/buying-rates/export/shipping-line`): **PASS**
        5. *Tariff > Selling > Import* (`/buying-rates/import/shipping-line`): **PASS**
        6. *Tariff > Selling > Export Other Container* (`/selling-rates/export-other-container`): **PASS**
        7. *Tariff > Selling > Import Other Container* (`/selling-rates/import-other-container`): **PASS**
        8. *Tariff > Selling > Export Traiff Storage* (`/selling-rates/export-storage`): **PASS**
        9. *Tariff > Trucker > TruckerModule* (`/truckerlist`): **PASS**
        10. *User Management > User Management* (`/user-security/manage-profile`): **PASS**
        11. *User Management > Role Management* (`/user-security/role-management`): **PASS**
      - Captured verification screenshots for every module into repo and artifact storage (`module_*.png`). No toast errors or uncaught exceptions observed.

15. **China Prefiler SIT Comprehensive Module Automated Check:**
    - **Target URL:** `https://prefiler-sit.ecuworldwide.cn/dashboard`
    - **Session:** Authenticated as `Prefiler User (7268)`, Office `XMN (94)`.
    - **Module Test Results (Selenium Edge):**
      1. *AMS* (`/ams-prefiler/filer-details`): **PASS** (Table loaded, 0 rows)
      2. *AFR* (`/afr-prefiler/filer-details`): **PASS** (Table loaded, 2 records)
      3. *ACI* (`/aci-prefiler/filer-details`): **PASS** (Table loaded, 54 records)
      4. *ICS2* (`/ics2-prefiler/filer-details`): **PASS** (Table loaded, 0 rows)
      5. *MBL Filer* (`/mblfiler-prefiler/filer-details`): **PASS** (Table loaded, 2 records)
    - **Artifacts:** Full module screenshots saved (`prefiler_*.png`) and results logged in `prefiler_modules_report.json`. No uncaught frontend exceptions or error toasts.

16. **Frankfurt Prefiler (DEV & SIT) Verification:**
    - **Frankfurt DEV (`https://prefiler-eudev.itopazapp.com`):**
      - Cluster: `euc1-itopaz-dev-eks` (Account `074779643551`).
      - Login URL: `https://prefiler-eudev.itopazapp.com/login` (HTTP 200).
      - Authentication: Successfully signed in with credentials `prefiler` / `yes`, reaching dashboard at `https://prefiler-eudev.itopazapp.com/dashboard` under user `Prefiler (6939)`.
    - **Frankfurt SIT (`https://prefiler-eusit.itopazapp.com`):**
      - Cluster: `euc1-itopaz-sit-eks` (Account `464134132424`).
      - Login URL: `https://prefiler-eusit.itopazapp.com/login` (HTTP 200).
      - Authentication: Successfully signed in with credentials `prefiler` / `yes`, reaching dashboard at `https://prefiler-eusit.itopazapp.com/dashboard` under user `Prefiler User (7268)`.
      - Live Modules: 6 active modules loaded on dashboard: **BASF, AMS, AFR, ACI, ICS2, MBL Filer**.
    - **Artifacts:** Captured verification screenshots for both environments (`prefiler_dev_dashboard.png`, `prefiler_sit_dashboard.png`) and documented in `prefiler_frankfurt_check.json`.

17. **ECU MDM PROD (`https://mdmecu.allcargoapps.com/ebx-ui/ui/`) Slowness Investigation & Remediation:**
    - **Instance:** EC2 `i-0add8ef2aa72adb7c` (`EBX-server-prod-primary-active` / `10.100.110.76` in `eu-central-1`, account `965031587107`).
    - **Root Cause:** A service restart triggered an intensive EBX cold repository validation against Aurora PostgreSQL (`ecu-mdm-db-cluster`), executing thousands of sequential lookups. The `RepositoryFacade.lookupRepository_waitIfRequired` held an exclusive monitor lock, causing all incoming Tomcat HTTP worker threads (`http-nio-8080-exec-*`) to enter `BLOCKED` state. The listen queue backlogged (`101/100`), causing external timeouts.
    - **Configuration Fix:** `ebx-auto-heal.service` had a short `startup_max_wait_seconds: 480` (8 mins), killing Tomcat prematurely. Tuned `startup_max_wait_seconds` to `1200` (20 minutes) and `startup_grace_period_seconds` to `300` in `/etc/ebx-auto-heal/config.json`. Restarted service and monitored deployment completion.

18. **Jenkins CI/CD Server (`10.100.95.13`) — Trivy Scan "No Space Left on Device" Resolution:**
    - **Issue:** Jenkins pipeline builds failed during Trivy image vulnerability/secret scanning with error: `write /tmp/fanal-196339645: no space left on device`.
    - **Root Cause:** The root partition `/dev/root` on host `10.100.95.13` was at **95% capacity** (183 GB used / 193 GB total, only 11 GB free). The Docker daemon had accumulated **139.1 GB** across 214 images and 22 containers because the automated docker prune cron had been commented out. Large frontend/backend images (~3.2 GB) being unpacked by Trivy into `/tmp` exhausted the remaining 11 GB.
    - **Remediation:**
      - Removed 21 stopped sonarbuild containers (`docker container prune -f`), reclaiming **3.88 GB**.
      - Removed 97 dangling image layers (`docker image prune -f`), reclaiming **53.64 GB**.
      - Removed stale images older than 7 days (`docker image prune -a --filter 'until=168h' -f`), reclaiming **35.4 GB**.
      - **Total space reclaimed:** **~93 GB**. Root disk `/dev/root` dropped from **95% down to 48% (101 GB free)**.
      - **Prevention:** Created automated daily cron `/etc/cron.daily/docker-cleanup` to prune stopped containers, dangling images, and images older than 72 hours automatically.
      - Verified Jenkins web UI (`http://10.100.95.13:8090/login` returning HTTP 200 OK).

19. **iTariff PROD S3 Tariff Templates Company Structure Sync (`s3://itariff-prod-bucket/tariff-template/`):**
    - **Source:** Local directory `C:\Users\rah_66160\Downloads\LE_S3_Country\LE_S3_Country` (60 country folders, 432 Excel template files with company ID subfolders, ~56.6 MB total).
    - **Destination:** `s3://itariff-prod-bucket/tariff-template/` (AWS Account `965031587107`, PROD Frankfurt).
    - **Execution:** Synced via Worker 1 (`10.151.4.165`) utilizing active SSO profile `prod-965`. Dryrun validated 426 upload actions. Full sync completed successfully, uploading all updated company-specific template hierarchies (e.g. `INDIA/8/`, `INDIA/88/`, `CHINA/67/`, `GERMANY/9/`).
    - **Cleanup:** Temporary archive files cleaned from Worker 1 and local downloads.

20. **Bitbucket BW Repositories (`MDMBWPROJ`) Feature Dev Branch Audit:**
    - **Scope:** Scanned all 124 BusinessWorks / TIBCO BW repositories in Bitbucket (`allcargoecu` workspace, project `MDMBWPROJ` + `mdm-bw-repo`).
    - **Findings:**
      - **42 repositories** contain dedicated development branches (47 active branches across `feature_dev`, `dev`, `feature-dev`, `feature/dev_backup`).
      - **82 repositories** operate exclusively on `feature_sit`, `feature_uat`, `feature_prod`, and `main` without an active dev branch.
      - **Most recent dev commit:** `bw_company_outbound_itopaz` (`feature_dev`: `2026-10-23 10:06 UTC`, commit `bffc0ca1` by Rahul).
      - Audit results documented in `scratch/bw_dev_branches_table.md` and `scratch/bw_dev_branches.json`.

## Jenkins cleanup status — 2026-10-27

- **Host:** Jenkins master `10.100.95.13`; root disk `/dev/root` is **101 GB free (48% used)**, NVMe `/home/ubuntu/jenkins-data` is 344 GiB total, 45 GiB free (87% used).
- **Docker Daemon:** 48 images (50.1 GB), 1 active container (`jenkins-server`), 0 stopped containers.
- **Automated Daily Prune:** `/etc/cron.daily/docker-cleanup` installed and active.

- Observation: Under "Projects", the project `Language API Integratioin Midea China HQ` has a typo in title (`Integratioin`) and duration shows `May 2021 to Present` rather than aligning with Midea tenure (`May 2021 to Dec 2022`).
- Next steps: Confirm with candidate if the project dates/spelling should be adjusted. Monitor recruiter views and incoming interview requests on Naukri.

## Job-search update — 2026-11-02

- **Confirmed submission:** Mercor — *DevOps / Platform Engineer Talent Network* (remote independent-contractor talent network). The controlled browser showed “2 of 2 steps finished” and “Your application has been submitted”; Mercor application ID `candidate_AAABoZa710DAltwIvs9HyYVd`.
- **Follow-up:** Mercor indicates an update may take up to four weeks. Tracker entry: `job/applications/tracker.csv` J032; planned follow-up 2026-11-30.

## Bitbucket access-token audit — 2026-11-03

- Source: authenticated controlled Bitbucket browser session; workspace `allcargoecu`; read-only review of two workspace tokens and all 19 project token inventories.
- Active project tokens expiring by 2026-12-03: `jenkins-itopaz-ibm-token` (project `ITOPAZB`, 2026-12-01), `K8SCON` (project `K8SCON`, 2026-11-30), and `prefiler-backend` (project `PREB`, 2026-12-01).
- Workspace tokens do not expire within this window (`bitbucket`: 2027-01-31; `backup-script`: 2026-12-31).
- Attention: `itopaz-database-token` (project `DB`) expired on 2026-10-29. No token was modified or revoked.

## China SIT PostgreSQL private DNS — 2026-11-03

- Azure China SIT subscription read-only verification: `cn3-itopaz-sit-pssql.postgres.database.chinacloudapi.cn` is Ready with public network access disabled.
- Its public FQDN CNAME targets `d30646c1be09.privatelink.postgres.database.chinacloudapi.cn`; the linked private DNS A record resolves to `10.180.223.4` (TTL 30 seconds).
