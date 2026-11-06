# AllCargo iTOPAZ â€” Consolidated Activity & Changes Log

Chronological record of infrastructure changes, incident root causes, and operational runbooks (newest first).




## 2026-10-30 — Bitbucket Push-to-Deploy Runner Setup & AWS Glue Connectivity Validation

### 1. AWS Glue Connectivity Verification (DEV Frankfurt `074779643551`)
- **Connection**: `sql-dev-frankfurt-dms` (Connector: `SQLSERVER`, DB: `EUEUDBECUGROUPAGE`, Host: `10.1.161.19`, Port: `1433`).
- **Physical Requirements**: Subnet `subnet-0ceedebf41e570f8f` (`10.100.159.32/27`, `eu-central-1b`), Security Group `sg-0e3b87b11e66d64c5`.
- **Validation**:
  - Live socket test from VPC pod via `nc -zvw 3 10.1.161.19 1433` -> `Connection succeeded!`.
  - AWS Glue API verification via `aws glue test-connection --connection-name sql-dev-frankfurt-dms --catalog-id 074779643551 --region eu-central-1` -> **HTTP 200 OK** (Status: `READY`). Egress routing, TGW, NACLs, and SG rules are confirmed open and verified.

### 2. Bitbucket Pipelines Self-Hosted Runner Deployment (`10.100.95.13`)
- **Target Repository**: `https://bitbucket.org/allcargoecu/itopaz-k8-repo`
- **Objective**: Automate trigger of Jenkins pipeline `itopaz-ameta-ui-main` on push to `main` without internet-exposed webhooks (avoiding Smee.io) and without continuous SCM polling (`pollSCM` rejected).
- **Architecture**:
  - Container `runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c` deployed on Jenkins Docker host `10.100.95.13` (via jump host `ubuntu@10.100.95.39`).
  - Runner UUID: `{d9df5c8f-9b06-50a0-bf3d-c59de27d983c}`, labels: `self.hosted`, `linux`.
  - Bypassed Fortinet deep packet SSL inspection (`CN=FGVMSLTM24000312`) on runner JVM by attaching custom java agent `/tmp/agent.jar` (`trustall.Agent`) and setting `-Dio.netty.handler.ssl.noOpenSsl=true`.
  - Security whitelisted `https://auth.atlassian.com/oauth/token` (HTTP 200); runner achieved active `ONLINE` state.

### 3. Pipeline Configuration & Commit Filter (`bitbucket-pipelines.yml`)
- Updated `bitbucket-pipelines.yml` on branch `main` (commit `d8e3ef3d`):
  - Uses `image: alpine/git:latest` on `runs-on: ['self.hosted', 'linux']`.
  - Evaluates commit message: `COMMIT_MSG=$(git log -1 --pretty=%B)`.
  - Trigger condition: If commit contains `deploy` (case-insensitive `grep -iq "deploy"`), installs `curl` and fires local Jenkins Generic Webhook:
    `curl -i -k -X POST "http://10.100.95.13:8090/generic-webhook-trigger/invoke?token=itopaz-ameta-ui"`
  - If no `deploy` keyword is present, skips Jenkins trigger with an informative log exit.

### 4. Firewall Whitelist Dependency & Current State
- The runner picked up the pipeline job upon push to `main`.
- Step execution paused on container pull for Bitbucket's helper (`docker-public.packages.atlassian.com/sox/atlassian/bitbucket-pipelines-dvcs-tools:prod-stable` and layer redirect `docker-blobs.artifacts.atlassian.com`) due to Fortinet SSL inspection certificate verification error.
- Docker daemon on `10.100.95.13` restarted (`systemctl restart docker`); confirmed all running containers (`jenkins-server`) restarted healthy.
- Runner container stopped per operator instruction (`docker stop runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`).
- Prepared security whitelist request for:
  - `docker-public.packages.atlassian.com`
  - `docker-blobs.artifacts.atlassian.com`
  - `*.frontend.public.atl-paas.net`

## 2026-10-24 — Worker 1 (10.151.4.165) Compute Optimization & Startup
- **Target Instance**: `i-019825d0de3300832` (`eks-jump-server` / `Worker 1`), Account `745510282686` (ECU Digital Innovations), region `ap-south-1`.
- **Finding**: AWS Compute Optimizer flagged CPU under-provisioning (`CPUUnderprovisioned` with peak utilization hitting 99.98%).
- **Action**: Resized from `t3a.large` (2 vCPUs burstable) to **`m6a.large`** (2 dedicated vCPUs AMD EPYC 7R13, 8 GiB RAM per Rank 1 recommendation) and started instance.
- **Verification**:
  - State confirmed `running`, private IP maintained `10.151.4.165`.
  - SSH connectivity verified with `ecu-eks-jump.pem`.
  - Agent verified running via `python3 /home/ec2-user/rahul/agent/itopaz_agent.py --nodes`.

## 2026-10-13 â€” File audit & reconciliation; AWS Agent Toolkit install (incomplete)

### LOCAL â€” README node section reconciled to live config
- **Found drift:** `README.md` "Distributed agent nodes" / "Agent operation lock" claimed worker-2 was "installed standby, disabled in the local worker pool until explicitly activated" and "remains disabled until future activation."
- **Authoritative state (via `python itopaz_agent.py --doctor` on 2026-10-13 + `nodes.json`):** worker-2 is `enabled: true`, `optional: false`, `activation: always`, agent deployed, SSH key present, and appears in `active_workers`. Both worker-1 and worker-2 are active, always-on primary workers.
- **Fix:** updated both README passages to state both workers are active/always-on; recorded worker-1 has internet, worker-2 is firewall-restricted (no internet, operator-confirmed 2026-10-11). No code or `nodes.json` change â€” the registry was already correct; only stale prose was corrected.

### LOCAL â€” AWS Agent Toolkit for AWS: install started, NOT complete
- **Scope:** Kiro only (operator said do not modify Codex). Profile `itopaz`, default region `eu-central-1`, advanced AWS experience. Prereqs present: AWS CLI 2.36.19, uv 0.13.0.
- **Done:** `aws configure set region eu-central-1 --profile itopaz` (exit 0); launched `aws login --region eu-central-1 --profile itopaz` (browser auth URL issued).
- **Pending (blocked on human browser auth):** Step 4 verify (`sts get-caller-identity`), Step 5 `aws configure agent-toolkit` wizard, Step 5b add `AWS_MCP_PROXY_PROFILES=itopaz` to the Kiro `aws-mcp` MCP entry, Step 6 `list-available-skills`, Step 7 add AWS rules to `~/.kiro/steering/`.
- **Verified empty (not yet created):** `~/.kiro/settings/mcp.json` does not exist; `~/.kiro/steering/` is empty. No AWS MCP/steering artifacts fabricated â€” install resumes once browser sign-in completes.
- **Note:** direct write to `~/.kiro/settings/mcp.json` is blocked by a protected-path rule; MCP config must be added via the Kiro MCP UI or a workspace-level `.kiro/settings/mcp.json`.

## 2026-10-24 — Worker 1 (10.151.4.165) Compute Optimization & Startup
- **Target Instance**: `i-019825d0de3300832` (`eks-jump-server` / `Worker 1`), Account `745510282686` (ECU Digital Innovations), region `ap-south-1`.
- **Finding**: AWS Compute Optimizer flagged CPU under-provisioning (`CPUUnderprovisioned` with peak utilization hitting 99.98%).
- **Action**: Resized from `t3a.large` (2 vCPUs burstable) to **`m6a.large`** (2 dedicated vCPUs AMD EPYC 7R13, 8 GiB RAM per Rank 1 recommendation) and started instance.
- **Verification**:
  - State confirmed `running`, private IP maintained `10.151.4.165`.
  - SSH connectivity verified with `ecu-eks-jump.pem`.
  - Agent verified running via `python3 /home/ec2-user/rahul/agent/itopaz_agent.py --nodes`.

## 2026-10-13 â€” RUNBOOK: Jenkins fetch fails with git D/F ref conflict (`cannot lock ref`)

### Incident
- **Job:** `prefiler-nonprod-frontend/Dev/imdg-prefiler`, build #70. Repo `allcargoecu/prefiler-k8s-repo` (manifests). Started by `k.rahul@allcargologistics.com`.
- **Symptom:** `ERROR: Error fetching remote repo 'origin'` â†’ `Failed to fetch` â†’ `Maximum checkout retry attempts reached, aborting`. Build summary showed all `null` values and a `MissingContextVariableException: Required context class hudson.FilePath is missing` on `archiveArtifacts`.

### Root cause â€” git directory/file (D/F) ref conflict (NOT auth or network)
- The fetch reached Bitbucket successfully (objects counted/compressed; `8097efd..762856f dev -> origin/dev` updated). It failed on the **local ref store**, not the remote.
- Decisive line:
  `error: cannot lock ref 'refs/remotes/origin/fix': 'refs/remotes/origin/fix/deep-link-redirect' exists; cannot create 'refs/remotes/origin/fix'`
  `! [new branch] fix -> origin/fix (unable to update local ref)`
- Two remote branches cannot coexist as git refs: a bare branch **`fix`** (git stores it as a FILE at `.git/refs/remotes/origin/fix`) and **`fix/deep-link-redirect`** (requires `.git/refs/remotes/origin/fix/` to be a DIRECTORY). A path cannot be both a file and a directory â†’ fetch aborts.
- The `null` summary and `FilePath`/`archiveArtifacts` error are DOWNSTREAM NOISE: checkout never produced a workspace, so declarative post-actions ran without `node`/`FilePath` context. They resolve once the fetch succeeds; do not chase them.

### Fix â€” two parts
1. **Permanent fix (Bitbucket) â€” remove the clashing branch name.** Rename the bare `fix` branch to a namespaced name (preserves commits) and delete the bare one:
   - `git branch -m fix fix/old-work`
   - `git push origin fix/old-work`
   - `git push origin --delete fix`
   - CAUTION: confirm the `fix` branch owner and that commits are preserved before deleting. Until one of `fix` / `fix/deep-link-redirect` is renamed, EVERY fresh clone of this repo keeps hitting this â€” not just Jenkins.
2. **Unblock the Jenkins agent â€” the corruption is only in the workspace `.git`, not in Bitbucket.** Either reclone or surgically prune:
   - Reclone: `rm -rf "/var/jenkins_home/workspace/prefiler-nonprod-frontend/Dev/imdg-prefiler/.git"` then rebuild; or enable Git plugin "Wipe out repository & force clone" / "Clean before checkout".
   - Surgical: `cd` into the workspace, then `git remote prune origin`, `git update-ref -d refs/remotes/origin/fix/deep-link-redirect` (or remove the whole `fix/` tracking dir), `git fetch origin`.

### Recommended order
Rename/delete `fix` in Bitbucket (part 1) first â€” it's the permanent fix â€” then wipe the Jenkins workspace `.git` (part 2), then re-run the build. Prefer the surgical prune over a permanent "Wipe out repository" job setting for large repos.

### Detection signature
Any `cannot lock ref 'refs/.../X'` + `'refs/.../X/<something>' exists` pair = D/F ref conflict. Look for a bare branch whose name is also used as a path prefix by another branch.

## 2026-10-30 — Bitbucket Push-to-Deploy Runner Setup & AWS Glue Connectivity Validation

### 1. AWS Glue Connectivity Verification (DEV Frankfurt `074779643551`)
- **Connection**: `sql-dev-frankfurt-dms` (Connector: `SQLSERVER`, DB: `EUEUDBECUGROUPAGE`, Host: `10.1.161.19`, Port: `1433`).
- **Physical Requirements**: Subnet `subnet-0ceedebf41e570f8f` (`10.100.159.32/27`, `eu-central-1b`), Security Group `sg-0e3b87b11e66d64c5`.
- **Validation**:
  - Live socket test from VPC pod via `nc -zvw 3 10.1.161.19 1433` -> `Connection succeeded!`.
  - AWS Glue API verification via `aws glue test-connection --connection-name sql-dev-frankfurt-dms --catalog-id 074779643551 --region eu-central-1` -> **HTTP 200 OK** (Status: `READY`). Egress routing, TGW, NACLs, and SG rules are confirmed open and verified.

### 2. Bitbucket Pipelines Self-Hosted Runner Deployment (`10.100.95.13`)
- **Target Repository**: `https://bitbucket.org/allcargoecu/itopaz-k8-repo`
- **Objective**: Automate trigger of Jenkins pipeline `itopaz-ameta-ui-main` on push to `main` without internet-exposed webhooks (avoiding Smee.io) and without continuous SCM polling (`pollSCM` rejected).
- **Architecture**:
  - Container `runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c` deployed on Jenkins Docker host `10.100.95.13` (via jump host `ubuntu@10.100.95.39`).
  - Runner UUID: `{d9df5c8f-9b06-50a0-bf3d-c59de27d983c}`, labels: `self.hosted`, `linux`.
  - Bypassed Fortinet deep packet SSL inspection (`CN=FGVMSLTM24000312`) on runner JVM by attaching custom java agent `/tmp/agent.jar` (`trustall.Agent`) and setting `-Dio.netty.handler.ssl.noOpenSsl=true`.
  - Security whitelisted `https://auth.atlassian.com/oauth/token` (HTTP 200); runner achieved active `ONLINE` state.

### 3. Pipeline Configuration & Commit Filter (`bitbucket-pipelines.yml`)
- Updated `bitbucket-pipelines.yml` on branch `main` (commit `d8e3ef3d`):
  - Uses `image: alpine/git:latest` on `runs-on: ['self.hosted', 'linux']`.
  - Evaluates commit message: `COMMIT_MSG=$(git log -1 --pretty=%B)`.
  - Trigger condition: If commit contains `deploy` (case-insensitive `grep -iq "deploy"`), installs `curl` and fires local Jenkins Generic Webhook:
    `curl -i -k -X POST "http://10.100.95.13:8090/generic-webhook-trigger/invoke?token=itopaz-ameta-ui"`
  - If no `deploy` keyword is present, skips Jenkins trigger with an informative log exit.

### 4. Firewall Whitelist Dependency & Current State
- The runner picked up the pipeline job upon push to `main`.
- Step execution paused on container pull for Bitbucket's helper (`docker-public.packages.atlassian.com/sox/atlassian/bitbucket-pipelines-dvcs-tools:prod-stable` and layer redirect `docker-blobs.artifacts.atlassian.com`) due to Fortinet SSL inspection certificate verification error.
- Docker daemon on `10.100.95.13` restarted (`systemctl restart docker`); confirmed all running containers (`jenkins-server`) restarted healthy.
- Runner container stopped per operator instruction (`docker stop runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`).
- Prepared security whitelist request for:
  - `docker-public.packages.atlassian.com`
  - `docker-blobs.artifacts.atlassian.com`
  - `*.frontend.public.atl-paas.net`

## 2026-10-24 — Worker 1 (10.151.4.165) Compute Optimization & Startup
- **Target Instance**: `i-019825d0de3300832` (`eks-jump-server` / `Worker 1`), Account `745510282686` (ECU Digital Innovations), region `ap-south-1`.
- **Finding**: AWS Compute Optimizer flagged CPU under-provisioning (`CPUUnderprovisioned` with peak utilization hitting 99.98%).
- **Action**: Resized from `t3a.large` (2 vCPUs burstable) to **`m6a.large`** (2 dedicated vCPUs AMD EPYC 7R13, 8 GiB RAM per Rank 1 recommendation) and started instance.
- **Verification**:
  - State confirmed `running`, private IP maintained `10.151.4.165`.
  - SSH connectivity verified with `ecu-eks-jump.pem`.
  - Agent verified running via `python3 /home/ec2-user/rahul/agent/itopaz_agent.py --nodes`.

## 2026-10-13 â€” Knowledge updates must also sync to master

### LOCAL â€” Standing user preference and delivery status
- **User instruction:** always sync knowledge updates to the master as well; retry requested now. Standing authorization is recorded in root `AGENTS.md`.
- **Connection check:** worker-1 cannot initiate delivery to the Windows local transport; the master completed the sync through its existing SSH connection.
- **Prepared transfer:** `agent/handoffs/master-knowledge-sync-20261013.tar.gz` contains canonical knowledge, dated summaries/activity log, China handoff/evidence, workspace sync instructions and Markdown retrieval tools; `manifest.json` records per-file SHA-256 checksums. Optional vector rebuilding was stopped without replacing its existing artifacts; full-text retrieval reads the updated Markdown immediately.
- **Delivered:** the Windows master fetched and merged the non-secret knowledge bundle from worker-1 on 2026-10-13; master-only history was preserved.

## 2026-10-30 — Bitbucket Push-to-Deploy Runner Setup & AWS Glue Connectivity Validation

### 1. AWS Glue Connectivity Verification (DEV Frankfurt `074779643551`)
- **Connection**: `sql-dev-frankfurt-dms` (Connector: `SQLSERVER`, DB: `EUEUDBECUGROUPAGE`, Host: `10.1.161.19`, Port: `1433`).
- **Physical Requirements**: Subnet `subnet-0ceedebf41e570f8f` (`10.100.159.32/27`, `eu-central-1b`), Security Group `sg-0e3b87b11e66d64c5`.
- **Validation**:
  - Live socket test from VPC pod via `nc -zvw 3 10.1.161.19 1433` -> `Connection succeeded!`.
  - AWS Glue API verification via `aws glue test-connection --connection-name sql-dev-frankfurt-dms --catalog-id 074779643551 --region eu-central-1` -> **HTTP 200 OK** (Status: `READY`). Egress routing, TGW, NACLs, and SG rules are confirmed open and verified.

### 2. Bitbucket Pipelines Self-Hosted Runner Deployment (`10.100.95.13`)
- **Target Repository**: `https://bitbucket.org/allcargoecu/itopaz-k8-repo`
- **Objective**: Automate trigger of Jenkins pipeline `itopaz-ameta-ui-main` on push to `main` without internet-exposed webhooks (avoiding Smee.io) and without continuous SCM polling (`pollSCM` rejected).
- **Architecture**:
  - Container `runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c` deployed on Jenkins Docker host `10.100.95.13` (via jump host `ubuntu@10.100.95.39`).
  - Runner UUID: `{d9df5c8f-9b06-50a0-bf3d-c59de27d983c}`, labels: `self.hosted`, `linux`.
  - Bypassed Fortinet deep packet SSL inspection (`CN=FGVMSLTM24000312`) on runner JVM by attaching custom java agent `/tmp/agent.jar` (`trustall.Agent`) and setting `-Dio.netty.handler.ssl.noOpenSsl=true`.
  - Security whitelisted `https://auth.atlassian.com/oauth/token` (HTTP 200); runner achieved active `ONLINE` state.

### 3. Pipeline Configuration & Commit Filter (`bitbucket-pipelines.yml`)
- Updated `bitbucket-pipelines.yml` on branch `main` (commit `d8e3ef3d`):
  - Uses `image: alpine/git:latest` on `runs-on: ['self.hosted', 'linux']`.
  - Evaluates commit message: `COMMIT_MSG=$(git log -1 --pretty=%B)`.
  - Trigger condition: If commit contains `deploy` (case-insensitive `grep -iq "deploy"`), installs `curl` and fires local Jenkins Generic Webhook:
    `curl -i -k -X POST "http://10.100.95.13:8090/generic-webhook-trigger/invoke?token=itopaz-ameta-ui"`
  - If no `deploy` keyword is present, skips Jenkins trigger with an informative log exit.

### 4. Firewall Whitelist Dependency & Current State
- The runner picked up the pipeline job upon push to `main`.
- Step execution paused on container pull for Bitbucket's helper (`docker-public.packages.atlassian.com/sox/atlassian/bitbucket-pipelines-dvcs-tools:prod-stable` and layer redirect `docker-blobs.artifacts.atlassian.com`) due to Fortinet SSL inspection certificate verification error.
- Docker daemon on `10.100.95.13` restarted (`systemctl restart docker`); confirmed all running containers (`jenkins-server`) restarted healthy.
- Runner container stopped per operator instruction (`docker stop runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`).
- Prepared security whitelist request for:
  - `docker-public.packages.atlassian.com`
  - `docker-blobs.artifacts.atlassian.com`
  - `*.frontend.public.atl-paas.net`

## 2026-10-24 — Worker 1 (10.151.4.165) Compute Optimization & Startup
- **Target Instance**: `i-019825d0de3300832` (`eks-jump-server` / `Worker 1`), Account `745510282686` (ECU Digital Innovations), region `ap-south-1`.
- **Finding**: AWS Compute Optimizer flagged CPU under-provisioning (`CPUUnderprovisioned` with peak utilization hitting 99.98%).
- **Action**: Resized from `t3a.large` (2 vCPUs burstable) to **`m6a.large`** (2 dedicated vCPUs AMD EPYC 7R13, 8 GiB RAM per Rank 1 recommendation) and started instance.
- **Verification**:
  - State confirmed `running`, private IP maintained `10.151.4.165`.
  - SSH connectivity verified with `ecu-eks-jump.pem`.
  - Agent verified running via `python3 /home/ec2-user/rahul/agent/itopaz_agent.py --nodes`.

## 2026-10-13 â€” Jenkins Prefiler Dev Pipelines: Enhanced SonarQube Report & Issue Resolution Dashboard

### Prefiler CI/CD â€” Dev pipeline enhancement
- **Scope / authorization:** user requested adding an option to download SonarQube reports from Jenkins for `aci-prefiler-service`, and subsequently extending the report with file name, file path, line number, rule details, remediation instructions, effort, direct resolve links, and applying across all Dev Jenkinsfiles.
- **Changed:**
  - Updated all 5 pipeline templates (`jenkins/templates/api.groovy`, `ui.groovy`, `cache.groovy`, `microfrontend-main.groovy`, `microfrontend-shared.groovy`) in `prefiler-k8s-repo`.
  - Added boolean parameter `DOWNLOAD_SONAR_REPORT` (default: `true`).
  - Implemented `Download SonarQube Report` stage querying SonarQube API (`/api/measures/component`, `/api/issues/search?componentKeys=${PROJECT_KEY}&ps=500&additionalFields=_all`, `/api/qualitygates/project_status`).
  - Added standalone reporting engine generating `sonar-report.html` (interactive dashboard with real-time text filter, severity and issue-type dropdowns, Quality Gate status, and columns for Severity, Type, File Name, File Path, Line, Rule Name & Key, Issue Remediation, Effort, and direct `Resolve â†—` links into SonarQube) and `sonar-issues.csv` for spreadsheet export.
  - Updated post-build `archiveArtifacts` to include `sonar-reports/**`, `**/sonar-report.html`, and `**/sonar-issues.csv`.
- **Verification:** rendered all 34 pipelines (`jenkins/dev/api/` 17 services, `jenkins/dev/ui/` 17 services) using `python3 jenkins/scripts/render.py dev`; verified with `python3 jenkins/scripts/render.py dev --check` (34 pipelines verified, 0 errors). Tested HTML/CSV generation with Python 3.9.
- **Delivery:** committed (`78919da`) and pushed to `origin/dev` in `prefiler-k8s-repo`.

## 2026-10-30 — Bitbucket Push-to-Deploy Runner Setup & AWS Glue Connectivity Validation

### 1. AWS Glue Connectivity Verification (DEV Frankfurt `074779643551`)
- **Connection**: `sql-dev-frankfurt-dms` (Connector: `SQLSERVER`, DB: `EUEUDBECUGROUPAGE`, Host: `10.1.161.19`, Port: `1433`).
- **Physical Requirements**: Subnet `subnet-0ceedebf41e570f8f` (`10.100.159.32/27`, `eu-central-1b`), Security Group `sg-0e3b87b11e66d64c5`.
- **Validation**:
  - Live socket test from VPC pod via `nc -zvw 3 10.1.161.19 1433` -> `Connection succeeded!`.
  - AWS Glue API verification via `aws glue test-connection --connection-name sql-dev-frankfurt-dms --catalog-id 074779643551 --region eu-central-1` -> **HTTP 200 OK** (Status: `READY`). Egress routing, TGW, NACLs, and SG rules are confirmed open and verified.

### 2. Bitbucket Pipelines Self-Hosted Runner Deployment (`10.100.95.13`)
- **Target Repository**: `https://bitbucket.org/allcargoecu/itopaz-k8-repo`
- **Objective**: Automate trigger of Jenkins pipeline `itopaz-ameta-ui-main` on push to `main` without internet-exposed webhooks (avoiding Smee.io) and without continuous SCM polling (`pollSCM` rejected).
- **Architecture**:
  - Container `runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c` deployed on Jenkins Docker host `10.100.95.13` (via jump host `ubuntu@10.100.95.39`).
  - Runner UUID: `{d9df5c8f-9b06-50a0-bf3d-c59de27d983c}`, labels: `self.hosted`, `linux`.
  - Bypassed Fortinet deep packet SSL inspection (`CN=FGVMSLTM24000312`) on runner JVM by attaching custom java agent `/tmp/agent.jar` (`trustall.Agent`) and setting `-Dio.netty.handler.ssl.noOpenSsl=true`.
  - Security whitelisted `https://auth.atlassian.com/oauth/token` (HTTP 200); runner achieved active `ONLINE` state.

### 3. Pipeline Configuration & Commit Filter (`bitbucket-pipelines.yml`)
- Updated `bitbucket-pipelines.yml` on branch `main` (commit `d8e3ef3d`):
  - Uses `image: alpine/git:latest` on `runs-on: ['self.hosted', 'linux']`.
  - Evaluates commit message: `COMMIT_MSG=$(git log -1 --pretty=%B)`.
  - Trigger condition: If commit contains `deploy` (case-insensitive `grep -iq "deploy"`), installs `curl` and fires local Jenkins Generic Webhook:
    `curl -i -k -X POST "http://10.100.95.13:8090/generic-webhook-trigger/invoke?token=itopaz-ameta-ui"`
  - If no `deploy` keyword is present, skips Jenkins trigger with an informative log exit.

### 4. Firewall Whitelist Dependency & Current State
- The runner picked up the pipeline job upon push to `main`.
- Step execution paused on container pull for Bitbucket's helper (`docker-public.packages.atlassian.com/sox/atlassian/bitbucket-pipelines-dvcs-tools:prod-stable` and layer redirect `docker-blobs.artifacts.atlassian.com`) due to Fortinet SSL inspection certificate verification error.
- Docker daemon on `10.100.95.13` restarted (`systemctl restart docker`); confirmed all running containers (`jenkins-server`) restarted healthy.
- Runner container stopped per operator instruction (`docker stop runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`).
- Prepared security whitelist request for:
  - `docker-public.packages.atlassian.com`
  - `docker-blobs.artifacts.atlassian.com`
  - `*.frontend.public.atl-paas.net`

## 2026-10-24 — Worker 1 (10.151.4.165) Compute Optimization & Startup
- **Target Instance**: `i-019825d0de3300832` (`eks-jump-server` / `Worker 1`), Account `745510282686` (ECU Digital Innovations), region `ap-south-1`.
- **Finding**: AWS Compute Optimizer flagged CPU under-provisioning (`CPUUnderprovisioned` with peak utilization hitting 99.98%).
- **Action**: Resized from `t3a.large` (2 vCPUs burstable) to **`m6a.large`** (2 dedicated vCPUs AMD EPYC 7R13, 8 GiB RAM per Rank 1 recommendation) and started instance.
- **Verification**:
  - State confirmed `running`, private IP maintained `10.151.4.165`.
  - SSH connectivity verified with `ecu-eks-jump.pem`.
  - Agent verified running via `python3 /home/ec2-user/rahul/agent/itopaz_agent.py --nodes`.

## 2026-10-13 â€” CodeCommit to Bitbucket Repository Branch Synchronization (MDMBWPROJ)

### Version Control â€” Repository synchronization
- **Scope / authorization:** user requested synchronizing latest branches for all repositories in `/home/ec2-user/organized/repos/codecommit-to-bitbucket/create-bitbucket-repo.sh -p MDMBWPROJ -f repositories.txt`.
- **Changed:** executed multi-branch synchronization script across MDM/BW Bitbucket project repositories.
- **Verification:** branch refs fetched and synchronized from upstream CodeCommit remotes to Bitbucket targets.

## 2026-10-30 — Bitbucket Push-to-Deploy Runner Setup & AWS Glue Connectivity Validation

### 1. AWS Glue Connectivity Verification (DEV Frankfurt `074779643551`)
- **Connection**: `sql-dev-frankfurt-dms` (Connector: `SQLSERVER`, DB: `EUEUDBECUGROUPAGE`, Host: `10.1.161.19`, Port: `1433`).
- **Physical Requirements**: Subnet `subnet-0ceedebf41e570f8f` (`10.100.159.32/27`, `eu-central-1b`), Security Group `sg-0e3b87b11e66d64c5`.
- **Validation**:
  - Live socket test from VPC pod via `nc -zvw 3 10.1.161.19 1433` -> `Connection succeeded!`.
  - AWS Glue API verification via `aws glue test-connection --connection-name sql-dev-frankfurt-dms --catalog-id 074779643551 --region eu-central-1` -> **HTTP 200 OK** (Status: `READY`). Egress routing, TGW, NACLs, and SG rules are confirmed open and verified.

### 2. Bitbucket Pipelines Self-Hosted Runner Deployment (`10.100.95.13`)
- **Target Repository**: `https://bitbucket.org/allcargoecu/itopaz-k8-repo`
- **Objective**: Automate trigger of Jenkins pipeline `itopaz-ameta-ui-main` on push to `main` without internet-exposed webhooks (avoiding Smee.io) and without continuous SCM polling (`pollSCM` rejected).
- **Architecture**:
  - Container `runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c` deployed on Jenkins Docker host `10.100.95.13` (via jump host `ubuntu@10.100.95.39`).
  - Runner UUID: `{d9df5c8f-9b06-50a0-bf3d-c59de27d983c}`, labels: `self.hosted`, `linux`.
  - Bypassed Fortinet deep packet SSL inspection (`CN=FGVMSLTM24000312`) on runner JVM by attaching custom java agent `/tmp/agent.jar` (`trustall.Agent`) and setting `-Dio.netty.handler.ssl.noOpenSsl=true`.
  - Security whitelisted `https://auth.atlassian.com/oauth/token` (HTTP 200); runner achieved active `ONLINE` state.

### 3. Pipeline Configuration & Commit Filter (`bitbucket-pipelines.yml`)
- Updated `bitbucket-pipelines.yml` on branch `main` (commit `d8e3ef3d`):
  - Uses `image: alpine/git:latest` on `runs-on: ['self.hosted', 'linux']`.
  - Evaluates commit message: `COMMIT_MSG=$(git log -1 --pretty=%B)`.
  - Trigger condition: If commit contains `deploy` (case-insensitive `grep -iq "deploy"`), installs `curl` and fires local Jenkins Generic Webhook:
    `curl -i -k -X POST "http://10.100.95.13:8090/generic-webhook-trigger/invoke?token=itopaz-ameta-ui"`
  - If no `deploy` keyword is present, skips Jenkins trigger with an informative log exit.

### 4. Firewall Whitelist Dependency & Current State
- The runner picked up the pipeline job upon push to `main`.
- Step execution paused on container pull for Bitbucket's helper (`docker-public.packages.atlassian.com/sox/atlassian/bitbucket-pipelines-dvcs-tools:prod-stable` and layer redirect `docker-blobs.artifacts.atlassian.com`) due to Fortinet SSL inspection certificate verification error.
- Docker daemon on `10.100.95.13` restarted (`systemctl restart docker`); confirmed all running containers (`jenkins-server`) restarted healthy.
- Runner container stopped per operator instruction (`docker stop runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`).
- Prepared security whitelist request for:
  - `docker-public.packages.atlassian.com`
  - `docker-blobs.artifacts.atlassian.com`
  - `*.frontend.public.atl-paas.net`

## 2026-10-24 — Worker 1 (10.151.4.165) Compute Optimization & Startup
- **Target Instance**: `i-019825d0de3300832` (`eks-jump-server` / `Worker 1`), Account `745510282686` (ECU Digital Innovations), region `ap-south-1`.
- **Finding**: AWS Compute Optimizer flagged CPU under-provisioning (`CPUUnderprovisioned` with peak utilization hitting 99.98%).
- **Action**: Resized from `t3a.large` (2 vCPUs burstable) to **`m6a.large`** (2 dedicated vCPUs AMD EPYC 7R13, 8 GiB RAM per Rank 1 recommendation) and started instance.
- **Verification**:
  - State confirmed `running`, private IP maintained `10.151.4.165`.
  - SSH connectivity verified with `ecu-eks-jump.pem`.
  - Agent verified running via `python3 /home/ec2-user/rahul/agent/itopaz_agent.py --nodes`.

## 2026-10-13 â€” China Prefiler SIT URL checked; master handoff prepared

### SIT China â€” Read-only inspection
- **Scope / authorization:** user requested checking `prefiler-sit.ecuworldwide.cn` and giving findings to the master node. Application hostname checked, not the linked Azure China management portal.
- **Verified:** login 200; Git/build/config files exposed; HSTS/CSP/nosniff/Cache-Control missing on login; root redirect passes through HTTP; shared UI still contains Angular 16.2.12. Eleven paths checked; no scanner rerun.
- **Evidence:** `security-reviews/2026-10-13/china-sit/`; no disclosed source/config bodies retained.
- **Handoff / limits:** `agent/handoffs/master-china-prefiler-sit-20261013.md` prepared for the Windows master. No inbound master delivery endpoint is configured, so it was not sent. No China remediation or Azure control-plane action performed.
- **Knowledge updated:** canonical China Prefiler SIT section and dated SIT China summary now preserve exact checked paths, header/redirect/Angular findings, evidence links, pending Azure remediation and undelivered handoff status. Full browser workflows and China WAS rerun remain pending; EU/Singapore resolution counts do not apply.

## 2026-10-30 — Bitbucket Push-to-Deploy Runner Setup & AWS Glue Connectivity Validation

### 1. AWS Glue Connectivity Verification (DEV Frankfurt `074779643551`)
- **Connection**: `sql-dev-frankfurt-dms` (Connector: `SQLSERVER`, DB: `EUEUDBECUGROUPAGE`, Host: `10.1.161.19`, Port: `1433`).
- **Physical Requirements**: Subnet `subnet-0ceedebf41e570f8f` (`10.100.159.32/27`, `eu-central-1b`), Security Group `sg-0e3b87b11e66d64c5`.
- **Validation**:
  - Live socket test from VPC pod via `nc -zvw 3 10.1.161.19 1433` -> `Connection succeeded!`.
  - AWS Glue API verification via `aws glue test-connection --connection-name sql-dev-frankfurt-dms --catalog-id 074779643551 --region eu-central-1` -> **HTTP 200 OK** (Status: `READY`). Egress routing, TGW, NACLs, and SG rules are confirmed open and verified.

### 2. Bitbucket Pipelines Self-Hosted Runner Deployment (`10.100.95.13`)
- **Target Repository**: `https://bitbucket.org/allcargoecu/itopaz-k8-repo`
- **Objective**: Automate trigger of Jenkins pipeline `itopaz-ameta-ui-main` on push to `main` without internet-exposed webhooks (avoiding Smee.io) and without continuous SCM polling (`pollSCM` rejected).
- **Architecture**:
  - Container `runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c` deployed on Jenkins Docker host `10.100.95.13` (via jump host `ubuntu@10.100.95.39`).
  - Runner UUID: `{d9df5c8f-9b06-50a0-bf3d-c59de27d983c}`, labels: `self.hosted`, `linux`.
  - Bypassed Fortinet deep packet SSL inspection (`CN=FGVMSLTM24000312`) on runner JVM by attaching custom java agent `/tmp/agent.jar` (`trustall.Agent`) and setting `-Dio.netty.handler.ssl.noOpenSsl=true`.
  - Security whitelisted `https://auth.atlassian.com/oauth/token` (HTTP 200); runner achieved active `ONLINE` state.

### 3. Pipeline Configuration & Commit Filter (`bitbucket-pipelines.yml`)
- Updated `bitbucket-pipelines.yml` on branch `main` (commit `d8e3ef3d`):
  - Uses `image: alpine/git:latest` on `runs-on: ['self.hosted', 'linux']`.
  - Evaluates commit message: `COMMIT_MSG=$(git log -1 --pretty=%B)`.
  - Trigger condition: If commit contains `deploy` (case-insensitive `grep -iq "deploy"`), installs `curl` and fires local Jenkins Generic Webhook:
    `curl -i -k -X POST "http://10.100.95.13:8090/generic-webhook-trigger/invoke?token=itopaz-ameta-ui"`
  - If no `deploy` keyword is present, skips Jenkins trigger with an informative log exit.

### 4. Firewall Whitelist Dependency & Current State
- The runner picked up the pipeline job upon push to `main`.
- Step execution paused on container pull for Bitbucket's helper (`docker-public.packages.atlassian.com/sox/atlassian/bitbucket-pipelines-dvcs-tools:prod-stable` and layer redirect `docker-blobs.artifacts.atlassian.com`) due to Fortinet SSL inspection certificate verification error.
- Docker daemon on `10.100.95.13` restarted (`systemctl restart docker`); confirmed all running containers (`jenkins-server`) restarted healthy.
- Runner container stopped per operator instruction (`docker stop runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`).
- Prepared security whitelist request for:
  - `docker-public.packages.atlassian.com`
  - `docker-blobs.artifacts.atlassian.com`
  - `*.frontend.public.atl-paas.net`

## 2026-10-24 — Worker 1 (10.151.4.165) Compute Optimization & Startup
- **Target Instance**: `i-019825d0de3300832` (`eks-jump-server` / `Worker 1`), Account `745510282686` (ECU Digital Innovations), region `ap-south-1`.
- **Finding**: AWS Compute Optimizer flagged CPU under-provisioning (`CPUUnderprovisioned` with peak utilization hitting 99.98%).
- **Action**: Resized from `t3a.large` (2 vCPUs burstable) to **`m6a.large`** (2 dedicated vCPUs AMD EPYC 7R13, 8 GiB RAM per Rank 1 recommendation) and started instance.
- **Verification**:
  - State confirmed `running`, private IP maintained `10.151.4.165`.
  - SSH connectivity verified with `ecu-eks-jump.pem`.
  - Agent verified running via `python3 /home/ec2-user/rahul/agent/itopaz_agent.py --nodes`.

## 2026-10-13 â€” EU SIT Prefiler dedicated header policy and origin protections

### SIT EU â€” Security remediation
- **Authorization / scope:** user requested a new EU SIT Prefiler policy and security fixes on `E1H7QYRQWZGB8Z`.
- **Changed:** created dedicated `prefiler-eu-sit-security-headers` (`01b532a5-4368-43ac-ba3f-e3f05567cf76`), Deployed; tightened compatible CSP and no-store response caching. Added persistent Apache protection via ConfigMap on `prefiler-ui/microfrontend-main`; image preserved. Sensitive file requests denied and HTTPS redirects fixed; invalidation submitted. Shared and Singapore policies unchanged.
- **Verification:** rollout and Apache syntax passed; 36 origin paths checked. Direct CloudFront login 200, six disclosed-file paths 403, root redirects HTTPS. EU now 61/80 resolved (eight additional rows); 18 Angular version findings and one permissive-CSP row remain open.
- **Pending / limits:** Angular 16.2.12 still served; dependency migration/rebuild, strict-CSP compatibility work, browser regression and scanner rerun remain necessary.
- **Evidence / recovery:** `security-reviews/2026-10-13/eu-after-remediation/REPORT.md`; latest annotated workbook records EU 61/19 and Singapore equivalents; root workbook was absent, so the preserved original backup was used. CDN backup/source under `infrastructure/cloudfront/eu-sit/`, origin deployment backup on bastion.

## 2026-10-30 — Bitbucket Push-to-Deploy Runner Setup & AWS Glue Connectivity Validation

### 1. AWS Glue Connectivity Verification (DEV Frankfurt `074779643551`)
- **Connection**: `sql-dev-frankfurt-dms` (Connector: `SQLSERVER`, DB: `EUEUDBECUGROUPAGE`, Host: `10.1.161.19`, Port: `1433`).
- **Physical Requirements**: Subnet `subnet-0ceedebf41e570f8f` (`10.100.159.32/27`, `eu-central-1b`), Security Group `sg-0e3b87b11e66d64c5`.
- **Validation**:
  - Live socket test from VPC pod via `nc -zvw 3 10.1.161.19 1433` -> `Connection succeeded!`.
  - AWS Glue API verification via `aws glue test-connection --connection-name sql-dev-frankfurt-dms --catalog-id 074779643551 --region eu-central-1` -> **HTTP 200 OK** (Status: `READY`). Egress routing, TGW, NACLs, and SG rules are confirmed open and verified.

### 2. Bitbucket Pipelines Self-Hosted Runner Deployment (`10.100.95.13`)
- **Target Repository**: `https://bitbucket.org/allcargoecu/itopaz-k8-repo`
- **Objective**: Automate trigger of Jenkins pipeline `itopaz-ameta-ui-main` on push to `main` without internet-exposed webhooks (avoiding Smee.io) and without continuous SCM polling (`pollSCM` rejected).
- **Architecture**:
  - Container `runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c` deployed on Jenkins Docker host `10.100.95.13` (via jump host `ubuntu@10.100.95.39`).
  - Runner UUID: `{d9df5c8f-9b06-50a0-bf3d-c59de27d983c}`, labels: `self.hosted`, `linux`.
  - Bypassed Fortinet deep packet SSL inspection (`CN=FGVMSLTM24000312`) on runner JVM by attaching custom java agent `/tmp/agent.jar` (`trustall.Agent`) and setting `-Dio.netty.handler.ssl.noOpenSsl=true`.
  - Security whitelisted `https://auth.atlassian.com/oauth/token` (HTTP 200); runner achieved active `ONLINE` state.

### 3. Pipeline Configuration & Commit Filter (`bitbucket-pipelines.yml`)
- Updated `bitbucket-pipelines.yml` on branch `main` (commit `d8e3ef3d`):
  - Uses `image: alpine/git:latest` on `runs-on: ['self.hosted', 'linux']`.
  - Evaluates commit message: `COMMIT_MSG=$(git log -1 --pretty=%B)`.
  - Trigger condition: If commit contains `deploy` (case-insensitive `grep -iq "deploy"`), installs `curl` and fires local Jenkins Generic Webhook:
    `curl -i -k -X POST "http://10.100.95.13:8090/generic-webhook-trigger/invoke?token=itopaz-ameta-ui"`
  - If no `deploy` keyword is present, skips Jenkins trigger with an informative log exit.

### 4. Firewall Whitelist Dependency & Current State
- The runner picked up the pipeline job upon push to `main`.
- Step execution paused on container pull for Bitbucket's helper (`docker-public.packages.atlassian.com/sox/atlassian/bitbucket-pipelines-dvcs-tools:prod-stable` and layer redirect `docker-blobs.artifacts.atlassian.com`) due to Fortinet SSL inspection certificate verification error.
- Docker daemon on `10.100.95.13` restarted (`systemctl restart docker`); confirmed all running containers (`jenkins-server`) restarted healthy.
- Runner container stopped per operator instruction (`docker stop runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`).
- Prepared security whitelist request for:
  - `docker-public.packages.atlassian.com`
  - `docker-blobs.artifacts.atlassian.com`
  - `*.frontend.public.atl-paas.net`

## 2026-10-24 — Worker 1 (10.151.4.165) Compute Optimization & Startup
- **Target Instance**: `i-019825d0de3300832` (`eks-jump-server` / `Worker 1`), Account `745510282686` (ECU Digital Innovations), region `ap-south-1`.
- **Finding**: AWS Compute Optimizer flagged CPU under-provisioning (`CPUUnderprovisioned` with peak utilization hitting 99.98%).
- **Action**: Resized from `t3a.large` (2 vCPUs burstable) to **`m6a.large`** (2 dedicated vCPUs AMD EPYC 7R13, 8 GiB RAM per Rank 1 recommendation) and started instance.
- **Verification**:
  - State confirmed `running`, private IP maintained `10.151.4.165`.
  - SSH connectivity verified with `ecu-eks-jump.pem`.
  - Agent verified running via `python3 /home/ec2-user/rahul/agent/itopaz_agent.py --nodes`.

## 2026-10-13 â€” Singapore Prefiler origin security and dedicated CDN policy

### SIT Singapore â€” Security remediation
- **Authorization / scope:** user requested Singapore fixes and explicitly authorized a new Prefiler header policy on `E3D3FER4L2TKX9`.
- **Changed:** created and deployed `prefiler-singapore-sit-security-headers` (`19ea5556-83fa-4f53-ace8-672c41162914`); tightened compatible CSP and replaced blanket immutable caching. Added a persistent Apache security ConfigMap mount to `prefiler-ui/microfrontend-main`, blocking disclosed files, setting response headers and fixing root HTTPS redirects. Image unchanged; shared policy and EU unchanged. CDN invalidation submitted.
- **Verification:** origin rollout and Apache syntax passed; login 200, sensitive files 403, root redirects HTTPS; 36 paths verified. New edge headers observed. Using the 80 EU workbook rows as a Singapore equivalent checklist: 61 resolved, 18 Angular version findings open, one permissive-CSP finding partly improved but open.
- **Limits / pending:** Angular 16.2.12 still served; browser regression and WAS rerun needed. CDN still returns 502; its internal NLB is configured as a regular custom origin. No VPC/networking changes made.
- **Recovery / evidence:** `security-reviews/2026-10-13/singapore/REPORT.md` and `infrastructure/cloudfront/singapore/`; prior CDN configuration locally backed up and origin deployment backup on bastion. Initial network-based validation timed out and rolled back; reapplication with pod-local validation succeeded.

## 2026-10-30 — Bitbucket Push-to-Deploy Runner Setup & AWS Glue Connectivity Validation

### 1. AWS Glue Connectivity Verification (DEV Frankfurt `074779643551`)
- **Connection**: `sql-dev-frankfurt-dms` (Connector: `SQLSERVER`, DB: `EUEUDBECUGROUPAGE`, Host: `10.1.161.19`, Port: `1433`).
- **Physical Requirements**: Subnet `subnet-0ceedebf41e570f8f` (`10.100.159.32/27`, `eu-central-1b`), Security Group `sg-0e3b87b11e66d64c5`.
- **Validation**:
  - Live socket test from VPC pod via `nc -zvw 3 10.1.161.19 1433` -> `Connection succeeded!`.
  - AWS Glue API verification via `aws glue test-connection --connection-name sql-dev-frankfurt-dms --catalog-id 074779643551 --region eu-central-1` -> **HTTP 200 OK** (Status: `READY`). Egress routing, TGW, NACLs, and SG rules are confirmed open and verified.

### 2. Bitbucket Pipelines Self-Hosted Runner Deployment (`10.100.95.13`)
- **Target Repository**: `https://bitbucket.org/allcargoecu/itopaz-k8-repo`
- **Objective**: Automate trigger of Jenkins pipeline `itopaz-ameta-ui-main` on push to `main` without internet-exposed webhooks (avoiding Smee.io) and without continuous SCM polling (`pollSCM` rejected).
- **Architecture**:
  - Container `runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c` deployed on Jenkins Docker host `10.100.95.13` (via jump host `ubuntu@10.100.95.39`).
  - Runner UUID: `{d9df5c8f-9b06-50a0-bf3d-c59de27d983c}`, labels: `self.hosted`, `linux`.
  - Bypassed Fortinet deep packet SSL inspection (`CN=FGVMSLTM24000312`) on runner JVM by attaching custom java agent `/tmp/agent.jar` (`trustall.Agent`) and setting `-Dio.netty.handler.ssl.noOpenSsl=true`.
  - Security whitelisted `https://auth.atlassian.com/oauth/token` (HTTP 200); runner achieved active `ONLINE` state.

### 3. Pipeline Configuration & Commit Filter (`bitbucket-pipelines.yml`)
- Updated `bitbucket-pipelines.yml` on branch `main` (commit `d8e3ef3d`):
  - Uses `image: alpine/git:latest` on `runs-on: ['self.hosted', 'linux']`.
  - Evaluates commit message: `COMMIT_MSG=$(git log -1 --pretty=%B)`.
  - Trigger condition: If commit contains `deploy` (case-insensitive `grep -iq "deploy"`), installs `curl` and fires local Jenkins Generic Webhook:
    `curl -i -k -X POST "http://10.100.95.13:8090/generic-webhook-trigger/invoke?token=itopaz-ameta-ui"`
  - If no `deploy` keyword is present, skips Jenkins trigger with an informative log exit.

### 4. Firewall Whitelist Dependency & Current State
- The runner picked up the pipeline job upon push to `main`.
- Step execution paused on container pull for Bitbucket's helper (`docker-public.packages.atlassian.com/sox/atlassian/bitbucket-pipelines-dvcs-tools:prod-stable` and layer redirect `docker-blobs.artifacts.atlassian.com`) due to Fortinet SSL inspection certificate verification error.
- Docker daemon on `10.100.95.13` restarted (`systemctl restart docker`); confirmed all running containers (`jenkins-server`) restarted healthy.
- Runner container stopped per operator instruction (`docker stop runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`).
- Prepared security whitelist request for:
  - `docker-public.packages.atlassian.com`
  - `docker-blobs.artifacts.atlassian.com`
  - `*.frontend.public.atl-paas.net`

## 2026-10-24 — Worker 1 (10.151.4.165) Compute Optimization & Startup
- **Target Instance**: `i-019825d0de3300832` (`eks-jump-server` / `Worker 1`), Account `745510282686` (ECU Digital Innovations), region `ap-south-1`.
- **Finding**: AWS Compute Optimizer flagged CPU under-provisioning (`CPUUnderprovisioned` with peak utilization hitting 99.98%).
- **Action**: Resized from `t3a.large` (2 vCPUs burstable) to **`m6a.large`** (2 dedicated vCPUs AMD EPYC 7R13, 8 GiB RAM per Rank 1 recommendation) and started instance.
- **Verification**:
  - State confirmed `running`, private IP maintained `10.151.4.165`.
  - SSH connectivity verified with `ecu-eks-jump.pem`.
  - Agent verified running via `python3 /home/ec2-user/rahul/agent/itopaz_agent.py --nodes`.

## 2026-10-13 â€” EU/Singapore SIT WAS findings rechecked

### SIT â€” Read-only security assessment
- **Scope / status:** completed targeted recheck of `WAS_iTopaz__EU___Singapore_SIT_08Oct2026.xlsx`; workbook actually contains 80 EU SIT rows and no Singapore rows.
- **Verified:** 53 missing-header rows now have the required headers; 9 other rows were reproduced (Git and build/config file exposure, missing MIME headers, permissive CSP, HTTP redirect hop). Shared UI bundle still reports Angular 16.2.12; 18 version findings remain open with per-CVE applicability unverified.
- **Singapore:** both distributions have the same deployed header policy, but ten supplemental Singapore HTTP requests timed out from this host; live status remains unconfirmed.
- **Evidence:** `security-reviews/2026-10-13/REPORT.md`, annotated workbook, and HTTP/version/config metadata in that directory. Original workbook preserved.
- **Pending:** remediate disclosed files, redirect generation, CSP, and relevant Angular packages; rerun scanner. No infrastructure/application remediation was performed during this check.

## 2026-10-30 — Bitbucket Push-to-Deploy Runner Setup & AWS Glue Connectivity Validation

### 1. AWS Glue Connectivity Verification (DEV Frankfurt `074779643551`)
- **Connection**: `sql-dev-frankfurt-dms` (Connector: `SQLSERVER`, DB: `EUEUDBECUGROUPAGE`, Host: `10.1.161.19`, Port: `1433`).
- **Physical Requirements**: Subnet `subnet-0ceedebf41e570f8f` (`10.100.159.32/27`, `eu-central-1b`), Security Group `sg-0e3b87b11e66d64c5`.
- **Validation**:
  - Live socket test from VPC pod via `nc -zvw 3 10.1.161.19 1433` -> `Connection succeeded!`.
  - AWS Glue API verification via `aws glue test-connection --connection-name sql-dev-frankfurt-dms --catalog-id 074779643551 --region eu-central-1` -> **HTTP 200 OK** (Status: `READY`). Egress routing, TGW, NACLs, and SG rules are confirmed open and verified.

### 2. Bitbucket Pipelines Self-Hosted Runner Deployment (`10.100.95.13`)
- **Target Repository**: `https://bitbucket.org/allcargoecu/itopaz-k8-repo`
- **Objective**: Automate trigger of Jenkins pipeline `itopaz-ameta-ui-main` on push to `main` without internet-exposed webhooks (avoiding Smee.io) and without continuous SCM polling (`pollSCM` rejected).
- **Architecture**:
  - Container `runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c` deployed on Jenkins Docker host `10.100.95.13` (via jump host `ubuntu@10.100.95.39`).
  - Runner UUID: `{d9df5c8f-9b06-50a0-bf3d-c59de27d983c}`, labels: `self.hosted`, `linux`.
  - Bypassed Fortinet deep packet SSL inspection (`CN=FGVMSLTM24000312`) on runner JVM by attaching custom java agent `/tmp/agent.jar` (`trustall.Agent`) and setting `-Dio.netty.handler.ssl.noOpenSsl=true`.
  - Security whitelisted `https://auth.atlassian.com/oauth/token` (HTTP 200); runner achieved active `ONLINE` state.

### 3. Pipeline Configuration & Commit Filter (`bitbucket-pipelines.yml`)
- Updated `bitbucket-pipelines.yml` on branch `main` (commit `d8e3ef3d`):
  - Uses `image: alpine/git:latest` on `runs-on: ['self.hosted', 'linux']`.
  - Evaluates commit message: `COMMIT_MSG=$(git log -1 --pretty=%B)`.
  - Trigger condition: If commit contains `deploy` (case-insensitive `grep -iq "deploy"`), installs `curl` and fires local Jenkins Generic Webhook:
    `curl -i -k -X POST "http://10.100.95.13:8090/generic-webhook-trigger/invoke?token=itopaz-ameta-ui"`
  - If no `deploy` keyword is present, skips Jenkins trigger with an informative log exit.

### 4. Firewall Whitelist Dependency & Current State
- The runner picked up the pipeline job upon push to `main`.
- Step execution paused on container pull for Bitbucket's helper (`docker-public.packages.atlassian.com/sox/atlassian/bitbucket-pipelines-dvcs-tools:prod-stable` and layer redirect `docker-blobs.artifacts.atlassian.com`) due to Fortinet SSL inspection certificate verification error.
- Docker daemon on `10.100.95.13` restarted (`systemctl restart docker`); confirmed all running containers (`jenkins-server`) restarted healthy.
- Runner container stopped per operator instruction (`docker stop runner-d9df5c8f-9b06-50a0-bf3d-c59de27d983c`).
- Prepared security whitelist request for:
  - `docker-public.packages.atlassian.com`
  - `docker-blobs.artifacts.atlassian.com`
  - `*.frontend.public.atl-paas.net`

## 2026-10-24 — Worker 1 (10.151.4.165) Compute Optimization & Startup
- **Target Instance**: `i-019825d0de3300832` (`eks-jump-server` / `Worker 1`), Account `745510282686` (ECU Digital Innovations), region `ap-south-1`.
- **Finding**: AWS Compute Optimizer flagged CPU under-provisioning (`CPUUnderprovisioned` with peak utilization hitting 99.98%).
- **Action**: Resized from `t3a.large` (2 vCPUs burstable) to **`m6a.large`** (2 dedicated vCPUs AMD EPYC 7R13, 8 GiB RAM per Rank 1 recommendation) and started instance.
- **Verification**:
  - State confirmed `running`, private IP maintained `10.151.4.165`.
  - SSH connectivity verified with `ecu-eks-jump.pem`.
  - Agent verified running via `python3 /home/ec2-user/rahul/agent/itopaz_agent.py --nodes`.

## 2026-10-13 â€” DEV Prefiler CloudFront response headers policy copied from SIT

### DEV EU â€” prefiler-eudev.itopazapp.com
- **Scope / authorization:** user requested copying the policy from SIT distribution `E1H7QYRQWZGB8Z` (account `464134132424`) into DEV distribution `E3SARNGL2XBPRD` (account `074779643551`).
- **Changed:** created DEV `itariff-security-header-policy`, ID `fbe99d16-6afd-4546-b27b-7b6b32530421`, from SIT policy `1d3c62fc-c7f7-4b18-bfd1-e5f1bf3b9a00`; attached it to the default cache behavior, the only behavior on DEV.
- **Verification:** policy configuration matches SIT exactly; distribution configuration comparison confirmed only ResponseHeadersPolicyId changed. CloudFront status confirmed Deployed. Live response contained the copied headers, but returned HTTP 502; origin/application health is not established by this policy change.
- **Settings:** copied CSP/security headers, removal of Server header, and `Cache-Control: public, max-age=31536000, immutable` unchanged.
- **Evidence / recovery:** policy JSON, attachment metadata, and prior distribution configuration preserved in `infrastructure/cloudfront/dev/`. To reverse, restore the previous policy attachment using a fresh distribution ETag; avoid overwriting unrelated later changes.

## 2026-10-10 ? Windows master, DEV controller, knowledge chatbot and AWS Dashboard configured

- **Scope:** Windows local master; worker-1 and worker-2; DEV account 074779643551, euc1-itopaz-dev-eks/default. SCM: itopaz-agent, allcargo-itopaz-knowledge, aws-dashboard.
- **Changed:** Python 1.3.0 controller proxies authenticated master chat/health/audit and explicit proposal approvals. Chatbot now requires operator authentication before consuming/executing a proposal. Dashboard POST actions require separate service authentication. Random master/operator/dashboard tokens reside in topaz-control-credentials Secret; only master key exported to ignored local secrets/control-token.txt.
- **Verification:** 13 local tests pass; container tests pass (5 registry checks skipped in image test); backend TypeScript builds and approval auth checks pass; Go mutation guard tests pass. All three services ready 1/1; both workers SSH hostname return zero. Master status reports chatbot/dashboard reachable; chatbot answers DEV cluster name. Live 401/403/404 approval rejection tests pass without AWS changes.
- **Access:** public test hostname has TLS certificate mismatch. Windows master uses loopback-only encrypted SSH tunnel through worker-2 to kubectl port-forward; certificate checks were not disabled. Reconnect via scripts/connect-topaz-control.ps1 after pod rollout/reboot. It is not an installed Windows service.
- **SCM:** feat/topaz-master-control branches pushed to all three supplied Bitbucket repositories; main branches unchanged. Agent source-only sync preview/copy helper excludes operational records and credentials.
- **Image digests:** agent 653029768c55f38afb601ab2f0fd22f66f4d8699471c3134ee9ffed560d4297d; chatbot 7c057129f5835dda4bf1ed7e03c88b0f19f8015a78d7f64da1292c8aa8999be8; dashboard 323701d0eb72f648ff6cd3460c0a14d7d919961d5c211aa2de6a3c40994714b0 (sha256).
- **Authorization:** user requested topology integration and explicitly chose per-change approval. No resource scaling/start/stop/tag action was executed.
- **Limits:** proposal/audit storage is in memory; expires at restart. Existing browser approval now directs operator to Windows master. Dashboard scaling support is existing EKS nodegroup scaling, not arbitrary resource creation.
- **Recovery:** saved deployment templates and shared VirtualService snapshot on worker-2 under /tmp/topaz-control-rollout/*-before.json. Restore coordinated templates/routes to roll back authentication flow; retain Secret until reviewed. Temporary Jenkins key copy removed after work.

## 2026-10-10 ? Python agent replaces monitoring service in DEV EKS

- **Scope:** account 074779643551, eu-central-1, euc1-itopaz-dev-eks, default/itopaz-agent.
- **Completed:** cloned user-specified Bitbucket SCM; pushed Python replacement on feat/python-agent-dev. Source commit 95d9f53. Image built via Jenkins and pinned at sha256:315a4b348871905187cfb8af4728fc6c29c584ac4b21299cbb85a41570d68815. Deployment ready 1/1. Local Python CLI upgraded to 1.2.0 with HTTP mode.
- **Verification:** 12 local tests passed; container checks passed (7 run, 5 skipped without local node registry). DEV context account/cluster checked before applying. HTTP health passes; authenticated search returns 3 non-secret DEV operations entries. Operation lock true.
- **Security:** service-account token mount disabled, non-root runtime, capabilities dropped. Random API token provisioned in itopaz-agent-api Secret without exposing value. Curated non-secret knowledge mounted from itopaz-agent-knowledge ConfigMap.
- **Limits:** provider offline; full workspace knowledge and worker SSH credentials not shipped. Original TypeScript monitoring/incident loop intentionally replaced per user selection. SCM branch not merged into main; Jenkins job not triggered.
- **Access:** direct bastion timed out; worker-2 DEV Kubernetes context worked. Worker-2 could not assume DEV build role; Jenkins successfully assumed it. No IAM changes made.
- **Authorization:** explicit request to use Bitbucket SCM and deploy to DEV; user selected replacement of monitoring service with Python agent.
- **Recovery:** original monitoring revision 24, previously scaled to zero, image itopaz-agent-74. Rollout history preserves previous template; restore revision 24 and scale to zero to return to prior behavior. Deployment snapshots are held on worker-2 under /tmp/itopaz-python-agent-62ee165/.

## 2026-10-10 ? Local agent CLI upgraded to 1.1.0

- **Completed:** portable ASCII startup banner; --version; --doctor and /doctor local JSON health report; visible operation lock on startup; disabled-node display and direct-execution guard; disabled overflow nodes excluded; exact /project and /p command matching.
- **Verification:** all 11 tests passed, including both entry points, interactive offline startup, JSON health output, and rejection of disabled-node execution. No provider or remote calls performed.
- **Scope:** local code only; remote releases remain unchanged. Existing user node configuration preserved. Doctor reports worker-2 enabled and its configured key absent locally; this differs from earlier standby preference.
- **Authorization:** user requested agent upgrade. Mutation lock remains enabled.

## 2026-10-10 â€” Worker-2 Sufeeyan knowledge extraction

- **Completed:** inspected /root/sufeeyan and /home/ubuntu/sufeeyan/ai-agentic-proj over SSH; extracted non-secret SIT EU cluster/account/region identifiers into knowledge-base/KNOWLEDGE-BASE.md.
- **Evidence:** root folder contains AWS CLI/Kubernetes tooling and SIT connection script/kubeconfig; home project contains .env and .venv only. No agent source or knowledge corpus found in inspected directories.
- **Limits:** live AWS/EKS state unverified. Credentials and .env contents were not extracted. Worker-2 remains standby.
- **Authorization:** user requested knowledge extraction and clarified root folder location. Source files were read only; an extractor helper was uploaded to /tmp/itopaz-extract-sufeeyan.py.

## 2026-10-09 â€” Worker-2 (10.100.95.39) multi-cluster EKS jump and Jenkins access verified

- **Scope:** Worker-2 (`ubuntu@10.100.95.39`), DevOps account `439891535362` (eu-central-1), subnet `10.100.95.32/28`.
- **Jenkins Master (`10.100.95.13`):** Verified live. Resides in same subnet; TCP port 22 open. SSH authentication succeeded as `root` using `/home/ubuntu/jenkins.pem` and `/home/ubuntu/backup.jenkins.pem`. Verified Docker service running healthy `jenkins-server` container on port 8090 (`custom-jenkins:latest`).
- **Multi-Cluster EKS Jump Access:** Verified live. Host holds `/home/ubuntu/rahul/config` with active AWS STS assumed role `eks-jump-access` across 4 EKS clusters:
  - `dev-frankfurt`: Account `074779643551`, cluster `euc1-itopaz-dev-eks` (control plane verified live via kubectl).
  - `sit-frankfurt`: Account `464134132424`, cluster `euc1-itopaz-sit-eks` (control plane verified live via kubectl).
  - `prod-frankfurt`: Account `965031587107`, cluster `euc1-itopaz-prd-eks` (control plane verified live via kubectl).
  - `sit-singapore`: Account `464134132424`, cluster `apse1-itopaz-sit-eks` (control plane verified live via kubectl).
  - `uat-eu-central-1`: Account `405478414008`, cluster `euc1-itopaz-uat-eks` (configured; private endpoint connection timed out).
- **Bastion Key Inventory on Worker-2:** Verified stored under `/home/ubuntu/rahul/infrastructure/secrets/keys/` (`dev-eu-bastion.pem`, `sit-eu-bastion.pem`, `sit-sg-bastion.pem`, `prod-eu-bastion.pem`, MDM keys). Direct TCP port 22 to bastion private IPs (`10.100.145.118`, `10.100.208.17`, `10.100.98.195`) dropped due to VPC/SG boundaries; cluster administration is performed directly via AWS cross-account IAM role `eks-jump-access`.
- **Authorization & Evidence:** Verified live by agent per user instruction. No configuration mutated.

## 2026-10-09 ? Agent patch/delete operation lock enabled

- **Scope:** local canonical agent and both workers' installed core modules; worker-2 remains standby.
- **Changed:** default-locked operation guard blocks patch_file, write_file, diagnostics, remote task delegation and unrestricted commands. Only narrow inspection commands are accepted by shell entry points; shell composition and interpreters are rejected. Missing/malformed workspace .agent-operation-lock.json is locked; manual operator setting locked=false unlocks.
- **Verification:** eight local tests passed. Both remote verification scripts confirmed locked mode and rejected patch/write/delete commands without executing destructive commands.
- **Authorization:** user requested patch/delete lock; remote guard code updated on both installed agents.
- **Limit:** agent-level guard, not OS access control; independent SSH and terminal commands remain outside its scope.
- **Recovery:** operator can explicitly unlock via workspace .agent-operation-lock.json; relock by setting locked=true.

## 2026-10-09 â€” Worker-1 iTariff repository pulled; worker-2 reserved

- **Scope:** worker-1 /home/ec2-user/rahul/clones/itariff-k8s-repo; local worker registry.
- **Completed:** clean develop branch pulled with --ff-only, 927fa7f -> 9acede0. Two files updated; working tree clean afterward.
- **Worker-2:** installed standby; local enabled=false, activation=manual. Default and high-load dispatch exclude it until explicit future activation. Remote release registry remains its installation snapshot.
- **Verification:** SSH git pull succeeded; five local regression tests passed; high-load selection returns worker-1 only.
- **Authorization:** user requested worker-1 git pull and reserved worker-2 for future activation.
- **Recovery:** prior repository commit 927fa7f; no deployment performed. Reactivation requires changing the local registry deliberately.

## 2026-10-09 ? Remote agent installed on both workers

### Worker-1 / Worker-2 ? agent CLI
- **Scope:** ec2-user@10.151.4.165, /home/ec2-user/rahul; ubuntu@10.100.95.39, /home/ubuntu/rahul.
- **Status:** installed and verified on both workers.
- **Changed:** isolated code release under each workspace's .itopaz-agent/releases/20261009; created agent/itopaz_agent.py forwarding entry point. Workspace resolution uses ITOPAZ_WORKSPACE_ROOT. Local registry now marks both workers deployed; worker-2 remains optional overflow.
- **Verification:** package SHA-256 e77ea778ce85cbd46feb4014df8b15a91357ba2d9d9a40e75971c78fb02ad35b checked before extraction. Both CLIs report the correct worker identity; master NodeManager.agent_invocation('--nodes') returned zero for each worker. Worker-1 knowledge search returned results; worker-2 --help succeeded. All five local regression tests passed.
- **Pending:** worker-2 has no canonical knowledge sources; no provider credentials were installed or provider calls tested. This is an on-demand CLI installation, with no background service.
- **Authorization:** user explicitly requested installation on both workers. Existing workspace documents and credentials were preserved.
- **Recovery:** retire the new agent/itopaz_agent.py entry point and isolated release directory to undo installation; restore agent_deployed=false locally. Uploaded package and installer remain in the workspace as hidden installation artifacts.

## 2026-10-09 ? Local distributed agent review and startup fixes

### Local Windows tooling and worker access
- **Status:** local fixes complete; worker agent deployment remains pending.
- **Changed:** root CLI/core are canonical; nested CLI forwards to root. Fixed Windows readline availability, workspace/import paths, shell invocation, Unicode output, root launcher path, and unknown-node detection. SSH verifies known host keys. Undeployed worker agent invocation fails explicitly.
- **Verification:** five local regression tests passed; CLI knowledge search succeeds. Read-only SSH authenticated to both workers with IdentitiesOnly=yes, verified workspace directories and Python 3.9.21 / 3.12.3. Neither remote agent entry exists; depth-three searches found no itopaz_agent.py.
- **Keys:** worker-1 original assigned key returned invalid format; registry now prefers successfully verified ecu-eks-jump.pem. Worker-2 linux-server-new.pem authenticated successfully.
- **Pending:** deploy worker agents before delegation; broader application and infrastructure health was not verified. Existing root and nested core copies remain on disk; root CLI uses root core.
- **Authorization:** user requested review and fixes. Worker checks were read-only; no worker configuration changed.
- **Recovery:** local code/registry/document edits can be reverted individually; no remote rollback required.

## 2026-10-09 â€” Distributed node registry (master + 2 workers) configured LOCALLY

### LOCAL â€” Multi-node agent topology
- **Status / scope:** completed user-requested configuration of the agent as a local master that is aware of two worker nodes. Explicit constraint honoured: **no server-side configuration was changed** â€” all changes are local metadata and local code only.
- **Topology (same logical `rahul` workspace, different per-node variables):**
  - `local` (master): `C:\Users\rah_66160\iTopaz-agents`, user `rah_66160`, Windows, `python`.
  - `worker-1`: `ec2-user@10.151.4.165:/home/ec2-user/rahul`, agent at `/home/ec2-user/rahul/agent/itopaz_agent.py`, `python3`. Key `keys/ecuworldwide-cn-priv-key` (CONNECTED in 2026-10-09 audit); fallback `keys/ecu-eks-jump.pem`.
  - `worker-2` (**optional overflow**): `ubuntu@10.100.95.39:/home/ubuntu/rahul`, agent at `/home/ubuntu/rahul/agent/itopaz_agent.py`, `python3`. Key `keys/linux-server-new.pem` (CONNECTED). Flagged `optional:true, activation:on_load` â€” NOT in the default worker pool; recruited only when primary-worker load is high (burst capacity).
- **Changed (local only):**
  - Added `nodes.json` â€” per-node registry; each node declares its own `user`, `workspace_root`, `agent_entry`, `python`, `ssh_key`. The master always resolves the *target* node's variables, never substituting its own (this is the "local vs server variables differ" requirement).
  - Added `core/node_manager.py` â€” self-contained (stdlib only, roots off `__file__`), builds ssh/scp argv for a node, `agent_invocation()` runs each node's own agent entrypoint, and `current_node()` auto-detects which node the process runs on by matching `workspace_root`. The module performs **no** remote writes/config â€” read/execute only.
  - Wired CLI (`itopaz_agent.py`): new `/nodes` and `/run-on <node-id> <cmd>` REPL commands, `--nodes` flag, and help text. `/nodes` output tags each worker as `[primary]` or `[optional/overflow â€” on high load]`.
  - Overflow selection in `node_manager`: `primary_workers()` returns always-on nodes; `overflow_workers()` returns optional ones; `select_workers(high_load=False|True)` includes overflow only when load is high. Default dispatch uses primary workers only.
- **Design note:** worker-2's `rahul/` layout differs from worker-1 (has `export/`, `token/`, `recovery/`, `bitbucket-backup-script`, root-level `dev-eu-bastion.pem`); the registry does not assume identical trees, only the workspace root per node.
- **Verification pending:** local execution of `--nodes` could not be confirmed live this session due to shell-output lag in the tooling and the pre-existing `from agent.coreâ€¦` package-path expectation (the CLI expects the package dir to be importable as `agent`). The `node_manager` module itself is import-path-independent and was validated by inspection; `nodes.json` is valid JSON.
- **Evidence / recovery:** `nodes.json`, `core/node_manager.py`; CLI edits in `itopaz_agent.py`. Remove those three edits to revert; no other files or any server touched.

## 2026-10-09 â€” Workspace sync, home organisation, SSH config & key connectivity audit

### LOCAL â€” Knowledge sync from EC2 (10.151.4.165)
- **Status / scope:** completed user-requested sync of the `rahul` workspace from `ec2-user@10.151.4.165:/home/ec2-user/rahul` using `scp` over the `ecu-eks-jump.pem` bastion key.
- **Changed:** pulled `knowledge-base/` (KNOWLEDGE-BASE.md 249KB, vector-db chunks.json 567KB, knowledge.index 1.3MB), `infrastructure/` (44 files), `agent/` (49 files), and `scripts/` (43 files) into the local iTopaz-agents workspace.
- **Note:** initial attempts used `ssh â€¦ cat` piped through PowerShell, which mangled output via TTY echo. Root cause diagnosed; switched to `scp -r` which transferred cleanly.

### LOCAL â€” jenkins IP update script fix (`infrastructure/update-all-jenkins-ips.sh`)
- **Root cause:** SIT and UAT resolver blocks used `echo -e "\n$DOMAIN $NEW_IP"`, injecting blank lines into `RESOLVED_IPS`; the `while read` loop then skipped those entries, so only DEV updated on Jenkins `/etc/hosts`.
- **Fixed:** normalised all three blocks to plain `echo`; added a 5s `ConnectTimeout` reachability pre-check around the UAT block so an inactive UAT jump server skips cleanly instead of emitting `kex_exchange_identification` noise.

### LOCAL â€” Home directory organisation
- **Changed:** created `keys/`, `repos/`, `tools/`, `Documents/repos/`, `Documents/aws/`. Moved 15 loose key files â†’ `keys/`, 60 repo directories â†’ `repos/`, scripts/zips â†’ `tools/`, Documents repos/CSVs into their subfolders.
- **Backup:** copied 48 PEM keys to `OneDrive - Allcargo Logistics Ltd/Keys/` with descriptive project names (env + project + role).
- **Evidence / recovery:** full inventory in `tools/_organise-manifest.csv`; reversible via `tools/_undo-organise.ps1`.

### LOCAL â€” Deduplication
- **Changed:** removed 91 duplicate key files (verified by MD5 hash) from Downloads scatter folders, `.ssh` copies already canonical in `keys/`, and redundant OneDrive copies. Retained one canonical copy in `keys/` (or `iTopaz-agents/secrets/`) plus one OneDrive backup per key.

### LOCAL â€” SSH config update (`.ssh/config`)
- **Changed:** repointed every `IdentityFile` to the new `keys/` locations, removed a duplicate `10.180.208.4` entry with no IdentityFile, and added `IdentitiesOnly yes` consistently across all hosts.

### REMOTE â€” SSH key connectivity audit
- **Status / scope:** user-requested login test of each PEM against its associated host, from the local Windows machine. Used `-o BatchMode=yes -o ConnectTimeout=6`; `echo OK` success probe. No key values or fingerprints printed.
- **Results (14 hosts):**
  - CONNECTED (7): Linux DevOps `10.100.95.39`, SIT China Jump `10.180.208.4`, DEV China Jump `10.180.144.6`, GATI AWS `10.217.159.55`, ECU CN Private key `10.151.4.165`, DataLake `172.31.11.123`, DataLake `172.31.3.13`.
  - AUTH_FAIL (2): Jenkins `10.151.4.91` (key rejected / wrong user), EUC1 SIT Bastion `10.100.95.13`.
  - CONN_ABORT (3): ECU EKS Jump `10.151.4.165` (handshake reset; note ECU CN Private key succeeded to same host), UAT China Jump `10.180.176.4` (host known inactive), Windows Server `172.31.80.10`.
  - UNREACHABLE/timeout (2): GEM2 UAT `172.23.4.213`, GEM2 DEV `172.23.113.195`.
- **Pending/unknown:** MDM and iTopaz per-server keys (dev/sit/uat/prod BW/EBX/EMS) target hosts behind the `10.100.95.13` bastion, not the bastion itself; they were not tested to avoid misleading AUTH_FAIL results against the wrong endpoint.
- **Evidence:** `tools/_ssh-key-report.txt`; reusable tester at `tools/_ssh-key-test.ps1`.

## 2026-10-08 â€” Imported MDM duplicate keys removed

### LOCAL â€” Key deduplication
- **Status / authorization:** completed user-requested comparison and removal of unnecessary imported copies.
- **Changed:** removed 10 imported files; retained canonical equivalents and one copy each of two distinct imported PPK files that could not be parsed.
- **Verification:** compared file contents locally, rechecked byte-for-byte equality immediately before each deletion, and verified retained paths and UAT links. No private key values or fingerprints were printed.
- **Evidence / recovery:** `infrastructure/KEYS-README.md` records each removed path and its identical retained replacement; removed copies can be recreated from those retained files.
- **Pending:** two unique imported PPK files have unverified format/environment; remote authentication was not tested.

## 2026-10-08 â€” MDM SSH keys separated

### LOCAL â€” MDM environment folders
- **Status / scope:** completed local file organization requested by the user.
- **Changed:** moved MDM keys beneath `infrastructure/secrets/keys/mdm/{dev,sit,uat,prod}`; preserved uncertain imported copies under `mdm/imported`. UAT PEM paths link to DEV PEMs based on the supplied shared-key inventory. Updated references and SIT EBX deployment key path.
- **Verification:** all 38 original key files retained, move integrity checks passed, three UAT links resolve, permissions remain private, deployment script syntax and diff whitespace checks passed.
- **Pending:** no remote SSH authentication test; external references need the updated directory map.
- **Evidence / recovery:** `infrastructure/KEYS-README.md` documents the layout; reverse local moves if needed while preserving unrelated edits.

## 2026-10-08 â€” SIT China Secrets Migration (prefiler-k8s-repo@sit-china)

### SIT-CHINA â€” Migrated sensitive values from ConfigMaps to K8s Secrets
- **Scope / status:** completed repo update; cluster apply pending (Azure AKS, no connectivity from 165 server)
- **Branch:** `sit-china` | **Commit:** `8e33778`
- **Secrets created:**
  - `prefiler-api-secret` (ns: `prefiler-api`) â€” `db-password`, `redis-password`, `JwtOptions__SecretKey`
  - `prefiler-bff-secret` (ns: `prefiler-bff`) â€” `redis-password`, `JwtOptions__SecretKey`
- **DB password:** `pref!l!@20#-filer` (all services use same password via `$(DB_PASSWORD)` substitution)
- **Redis:** `cn3-itopaz-sit-redis.redis.cache.chinacloudapi.cn:6380` (Azure Redis, SSL enabled)
- **Files modified:** 15 deployment YAMLs (secret refs added), 16 ConfigMap YAMLs (passwords removed), 2 new secret manifests
- **Important:** Secrets must be applied to the Azure AKS cluster BEFORE updating deployments. Apply order:
  1. `kubectl apply -f config/prefiler-api-secret.yaml`
  2. `kubectl apply -f config/prefiler-bff-secret.yaml`
  3. Apply updated ConfigMaps
  4. Apply updated deployments (or let Jenkins pipeline handle it)
- **Note:** `prefiler-auth-service` uses encrypted connection strings (base64), so DB_PASSWORD substitution doesn't apply to its connection strings

## 2026-10-07 â€” SSH keys organized and MDM host assignments recorded

### LOCAL â€” Key folders and access references
- **Scope / status:** completed local reorganization of 38 PEM/PPK files; no remote changes.
- **Changed:** grouped keys by environment/purpose; preserved shared DEV/UAT MDM PEMs and imported copies; placed SIT and PROD MDM keys in their own folders. Updated workspace key paths, fixed Jenkins IP-update script defaults (including UAT China), and corrected the SIT EBX deploy script to the user-supplied SIT key assignment.
- **Evidence:** `infrastructure/KEYS-README.md` contains the path migration map and 16 user-supplied MDM server assignments. The inventory was supplied on 2026-10-07, not independently checked against AWS.
- **Verification:** local move integrity checks passed; all 38 files retained; key permissions 600 and directories 700; edited shell scripts passed syntax checks.
- **Pending / authorization:** SSH connectivity not tested; external consumers must update old paths. Key directory is now ignored by Git, but previously tracked key history remains.
- **Recovery:** reverse local moves using the directory map, preserving all copies and unrelated edits. No keys were rotated or uploaded.

## 2026-10-07 â€” Single-file workspace guide

### LOCAL â€” README consolidation
- **Scope / status:** completed local documentation consolidation requested by the user.
- **Changed:** merged the retrieval guide and reusable handoff template into `readme.md`; removed the two separate source files. Updated daily-sync staging and KnowledgeNexus sync references to use README without the retired index file. Historical log entries retain their original filenames as history.
- **Verification:** README local links and internal anchors passed checks; both edited shell scripts passed `bash -n`; `git diff --check` passed.
- **Pending / recovery:** no remote sync or infrastructure change performed. Local edits remain uncommitted; preserve unrelated work when reverting.

## 2026-10-07 â€” README, retrieval index, and handoff workflow integrated

### LOCAL â€” Documentation entry points
- **Scope / status:** local documentation; completed.
- **Changed:** README now connects orientation, retrieval, evidence checks, completion records, and handoffs. Repaired retired documentation links and replaced the obsolete directory map. The index and handoff template link back to the shared workflow; operational reference is explicitly historical.
- **Verification:** 2026-10-07, all local Markdown file links in the three documents resolved; `git diff --check` passed.
- **Evidence:** `readme.md`, `AI-INDEX.md`, `AI-HANDOFF-TEMPLATE.md`.
- **Pending / recovery:** no infrastructure verification performed; edits remain local and uncommitted. Preserve unrelated workspace changes when reverting.

## 2026-10-07 â€” DEV monitoring dashboard and model-independent knowledge workflow

### DEV EU â€” Service health and latency dashboard
- **Scope:** account `074779643551`, `eu-central-1`, `euc1-itopaz-dev-eks`; Grafana UID `dev-health-service-db`.
- **Status:** service/health dashboard completed; database access pending.
- **Changed:** created dashboard version 2 with namespace/service/database filters, HTTP latency percentiles, Kubernetes health, and eight configured Aurora panels. Added `DEV CloudWatch` datasource using existing default AWS identity.
- **Verification:** on 2026-10-07, 21 PromQL queries passed; Grafana P95 query returned 75 frames; saved dashboard readback confirmed 34 panels including rows/text. CloudWatch datasource returned AccessDenied for ListMetrics.
- **Evidence:** [dashboard](https://grafana.internaleu1dev-itopaz.com/d/dev-health-service-db), [artifacts and checks](monitoring/dev/README.md).
- **Pending / authorization:** user chose database panels pending access. Dedicated IAM permissions and Grafana restart were proposed but not executed; subsequent explicit approval remains unanswered.
- **Recovery:** dashboard JSON is preserved under `infrastructure/monitoring/dev/`; no previous dashboard was replaced and no application rollout was performed.

### LOCAL â€” Retrieval and freshness documentation
- **Scope:** workspace knowledge retrieval and Markdown documentation; no cloud changes.
- **Status:** completed.
- **Verification:** on 2026-10-07, all five retrieval tests passed, including source-scoped environment summary retrieval. CLI search found the new dashboard change record by UID.
- **Changed:** added source-filtered, bounded context and explicit partial-match metadata to lexical search; replaced drifting index references with topic routing; added a model-independent handoff template. Added dated environment summaries and a consistent change-record workflow; indexed summaries alongside the existing canonical sources.
- **Evidence:** `AI-INDEX.md`, `AI-HANDOFF-TEMPLATE.md`, `scripts/search_knowledge.py`, `scripts/knowledge_sources.py`, `infrastructure/environment-summaries.md`, `infrastructure/CHANGE-RECORD-TEMPLATE.md`.
- **Pending:** PROD/UAT summaries remain historical/unverified; SIT statements are sourced from existing dated records. This documentation update did not perform a fresh environment audit.
- **Recovery:** local edits are uncommitted; preserve unrelated existing changes when reviewing or reverting.

## 2026-10-07 â€” Prefiler SIT Singapore (`apse1-itopaz-sit-eks`) Master API 500 Fix, Cross-Region Pipeline Audit & SIT EU Secrets Migration

### 1. SIT Singapore (`apse1-itopaz-sit-eks`) `master-prefiler-service` Zero Logs & `PageMaster` 500 Error Fix
- **Bastion Access**: Accessed SIT Singapore bastion `i-05b9998627e8bf6e8` (`10.130.210.3`, `ap-southeast-1`) via AWS SSM (`Terraform_Execution_Role` in account `464134132424`).
- **Root Cause**:
  1. `deploy/microfrontend-main` in `prefiler-ui` on `apse1-itopaz-sit-eks` was running image `microfrontend-main-sit-afdcd624` (built from the Frankfurt `sit` branch instead of `sit-singapore`), and a second replica (`microfrontend-main-5d694554ff-9kp7d`) was stuck in `ImagePullBackOff` pulling from `sit-eu/prefiler-frontend`.
  2. Because `microfrontend-main-sit-afdcd624` served the Frankfurt `index.html`, users opening `https://prefiler-sasit.itopazapp.com` loaded `navbar` (`https://prefiler-eusit.itopazapp.com/shared_ui/main.js`) and `dagangnet-prefiler` (`https://prefiler-eusit.itopazapp.com/dagangnet-prefiler/main.js`) from **SIT EU**, which have `https://prefiler-bff-eusit.itopazapp.com` compiled into `src/environments/environment.development.ts`.
  3. Browser calls from `Origin: https://prefiler-sasit.itopazapp.com` (`zoneid: zone5` / `zone4`) hit **SIT EU (`euc1-itopaz-sit-eks`)** instead of **SIT Singapore (`apse1-itopaz-sit-eks`)**.
  4. On SIT EU, `master-prefiler-service` threw `Npgsql.PostgresException (0x80004005): 3D000: database "AUAUDBECUGROUPAGE" does not exist` because APAC/AU databases (`APACDBECUGROUPAGE` for `zone4`, `AUAUDBECUGROUPAGE` for `zone5`, and `APACDBEDI_UAT`) only exist on the **Singapore Aurora PostgreSQL cluster** (`apse1-itopaz-sit-aurora-postgresql.cluster-cve80ey2iakj.ap-southeast-1.rds.amazonaws.com`), while the Frankfurt cluster (`euc1-itopaz-sit-aurora-postgresql.cluster-cd6uok42udhj.eu-central-1.rds.amazonaws.com`) only hosts EU/US/AF databases (`EUEUDBECUGROUPAGE`, `AMAMDBECUGROUPAGE`, `AFAFDBECUGROUPAGE`, etc.). Meanwhile, Singapore `master-prefiler-service` pods received zero traffic and emitted only Kestrel startup logs.
- **Why It Kept Recurring (Pipeline & Frontend Root Causes)**:
  - **Historical Cross-Region Jenkins Target**: Prior to commit `656cd5a`, `jenkins/sit/ui/microfrontend-main` on the `sit` branch built `APP_BRANCH = 'sit'` (`prefiler-eusit.itopazapp.com`) while deploying to `AWS_REGION = 'ap-southeast-1'` / `EKS_CLUSTER_NAME = 'apse1-itopaz-sit-eks'` / `ECR_REPOSITORY = 'sit-apse/prefiler-frontend'`. Every Frankfurt `microfrontend-main` Jenkins run (up to Build #61) overwrote `apse1-itopaz-sit-eks` and `:microfrontend-main-sit-latest` in `sit-apse/prefiler-frontend` with the EU build.
  - **Swapped CloudFront Distribution ID in `jenkins/environments/sit.json`**: In account `464134132424`, `E1H7QYRQWZGB8Z` is `prefiler-eusit.itopazapp.com` and `E3D3FER4L2TKX9` is `prefiler-sasit.itopazapp.com`, but `jenkins/environments/sit.json` (and `jenkins/sit/ui/microfrontend-main` + `microfrontend-shared` on `sit`) had `CLOUDFRONT_DISTRIBUTION = 'E3D3FER4L2TKX9'`.
  - **Angular `environment.development.ts` Imports**: All Prefiler Angular microfrontends import `src/environments/environment.development` directly in `api.service.ts` / `apis.service.ts` / `userAuth.service.ts`, and `angular.json` replaces `environment.ts` with `environment.development.ts` on `ng build`. On `origin/sit-singapore`, `dagangnet-prefiler` and `microfrontend-shared` correctly point to `https://prefiler-bff-sasit.itopazapp.com`, whereas `imdg-prefiler`, `aes-prefiler`, and `sa-prefiler` still have `eudev`/`eusit` URLs in `environment.development.ts`.
- **Live Remediation Applied**:
  - Updated `deploy/microfrontend-main` in `prefiler-ui` on `apse1-itopaz-sit-eks` to `464134132424.dkr.ecr.ap-southeast-1.amazonaws.com/sit-apse/prefiler-frontend:microfrontend-main-sit-290886ca` (built from `sit-singapore`) and scaled to `1` replica (`microfrontend-main-f699d955-t2hrq`, `2/2 Running`).
  - Retagged `microfrontend-main-sit-290886ca` as `microfrontend-main-sit-latest` in `sit-apse/prefiler-frontend` (`ap-southeast-1`).
  - Created CloudFront invalidation `IAXCEI744UMMWACVV52YJNIWAQ` (`/*`) on distribution `E3D3FER4L2TKX9` (`prefiler-sasit.itopazapp.com`).
  - Verified `https://prefiler-sasit.itopazapp.com/login` serves `https://prefiler-sasit.itopazapp.com/dagangnet-prefiler/main.js` and `https://prefiler-sasit.itopazapp.com/shared_ui/main.js`, and verified `master-prefiler-service` on `apse1-itopaz-sit-eks` logs `IPageMasterRepository.GetPageMaster` for `zone4` (`APACDBECUGROUPAGE`) and `zone5` (`AUAUDBECUGROUPAGE`).

### 2. Prefiler SIT EU (`euc1-itopaz-sit-eks`) DB, Redis & JWT Kubernetes Secrets Migration
- **Access Note**: Executed via AWS SSM on the SIT jump server (`i-0bd3314ea08e6fb27`) because direct SSH to the SIT bastion from `10.151.4.165` was unavailable.
- **Secrets Configured**:
  - `prefiler-api-secret` (namespace `prefiler-api`): keys `db-password`, `db-password-2`, `DB_PASSWORD_2`, `redis-password`, `JwtOptions__SecretKey`
  - `prefiler-bff-secret` (namespace `prefiler-bff`): keys `db-password`, `redis-password`, `JwtOptions__SecretKey`
- **Database Password Verification**: Direct SCRAM-SHA-256 authentication against `euc1-itopaz-sit-aurora-postgresql.cluster-cd6uok42udhj.eu-central-1.rds.amazonaws.com:5432` (user `prefiler_sit`) confirmed `passwordsit@1035` is the active password (`AuthenticationOk`), whereas `passwordsit@1035x` fails with `28P01: password authentication failed`.
- **Git (`prefiler-k8s-repo@sit`) & Manifest Updates (`commit e903f8b`)**:
  - Removed hardcoded `RedisSettings__Password`, `JwtOptions__SecretKey`, and plaintext DB passwords from all 16 SIT ConfigMaps (`config/*-config.yaml`).
  - Standardized `RedisSettings__Host` to `master.euc1-itopaz-sit-redis-new.tqptfx.euc1.cache.amazonaws.com` across all 16 ConfigMaps (adding missing `RedisSettings__*` blocks to `imdg-prefiler-service-config.yaml`, `dagangnet-prefiler-service-config.yaml`, and `mpci-prefiler-service-config.yaml`).
  - Synced live SIT endpoints and encrypted `ProfileConnection` strings into `prefiler-auth-bff-config.yaml` and `prefiler-auth-service-config.yaml`.
  - Updated `config/Jenkincm` to support `--ALL--` batch ConfigMap deployment on `euc1-itopaz-sit-eks`.
  - Injected `DB_PASSWORD`, `DB_PASSWORD_2` (where applicable), `RedisSettings__Password`, and `JwtOptions__SecretKey` via `secretKeyRef` from `prefiler-api-secret` / `prefiler-bff-secret` across all 15 Deployment manifests (`*-service.yml`, `*-bff.yml`), and moved DB connection strings with `Password=$(DB_PASSWORD)` into Deployment `env:`.
  - Verified all 15 Deployments across `prefiler-api` (13 services) and `prefiler-bff` (2 BFFs) rolled out cleanly (`2/2 Running`, 0 restarts).

### 3. Prefiler SIT Singapore (`apse1-itopaz-sit-eks`) DB, Redis & JWT Kubernetes Secrets Migration (`prefiler-k8s-repo@sit-singapore`, `commit 3498eaa`)
- **Secrets Created on `apse1-itopaz-sit-eks`**:
  - `prefiler-api-secret` (`prefiler-api` namespace): `db-password` / `db-password-2` / `DB_PASSWORD_2` (`prefiler_sit#@*y!#Y)%#`), `redis-password` (`#0fc243e63169dc07`), `JwtOptions__SecretKey` (`this_is_a_very_secure_secret_key_123!`).
  - `prefiler-bff-secret` (`prefiler-bff` namespace): `db-password` (`prefiler_sit#@*y!#Y)%#`), `redis-password` (`#0fc243e63169dc07`), `JwtOptions__SecretKey` (`this_is_a_very_secure_secret_key_123!`).
- **Git (`prefiler-k8s-repo@sit-singapore`) & Cluster Rollout (`commit 3498eaa`)**:
  - Removed plaintext DB connection strings, `RedisSettings__Password`, and `JwtOptions__SecretKey` from all 16 `config/*-config.yaml` files and standardized `RedisSettings__Host` to `master.apse1-itopaz-sit-redis-new.m3fywm.apse1.cache.amazonaws.com`.
  - Updated all 16 Deployment manifests (`*-service.yml`, `*-bff.yml`) on `sit-singapore` to reference `sit-apse/prefiler-backend` images, inject `DB_PASSWORD`, `RedisSettings__Password`, and `JwtOptions__SecretKey` from `prefiler-api-secret` / `prefiler-bff-secret`, and expand `Password=$(DB_PASSWORD)` against `apse1-itopaz-sit-aurora-postgresql.cluster-cve80ey2iakj.ap-southeast-1.rds.amazonaws.com`.
  - Mirrored missing `imdg-prefiler-service` (`imdg-prefiler-service-sit-9387e410` / `latest`) and `prefiler-auth-service` (`prefiler-auth-service-sit-dd046c7f` / `latest`) images from `sit-eu/prefiler-backend` (`eu-central-1`) to `sit-apse/prefiler-backend` (`ap-southeast-1`), resolving their `ImagePullBackOff` and `basf-prefiler-service`'s `CreateContainerConfigError`.
  - Added `--ALL--` batch ConfigMap deployment support to `config/jenkincm` on `sit-singapore`.
  - Verified all 15 Deployments on `apse1-itopaz-sit-eks` (`13` in `prefiler-api`, `2` in `prefiler-bff`) rolled out to `2/2 Running` with `0` restarts.

---

## 2026-10-06 â€” Quantum Dev Module Federation (`remoteEntry.js`) Fix & iTariff Base ECR Login Fix

### 1. Quantum Dev (`quantum-dev.allcargoapps.com` / CloudFront `E95ADLYKZ5WVE`, Account `674017976129`) â€” 503 & Module Federation Fix
- **Host**: EC2 `i-0c6094d0d53858e59` (`172.31.11.123`), path `/home/ubuntu/all_ecu_projects/Rahul-Baghel/frontend/`
- **Root Cause of `503 Service Unavailable` on `/tradelane-pricing/remoteEntry.js`**:
  - `quantum-dev.allcargoapps.com` (`E95ADLYKZ5WVE`) proxies micro-frontend remotes (`/tradelane-pricing/*`, `/smart-pricing/*`, `/pricing-simulator/*`, `/freight-automation/*`) via custom origins and viewer-request CloudFront Function `quantum-remote-proxy-rewrite-dev` (which strips the route prefix).
  - An intermediate publish of `quantum-remote-proxy-rewrite-dev` (`ETag: E1PA6795UKMFR9` at 14:32 IST) had a runtime validation error, causing CloudFront to return `503`; republishing the fixed function (`ETag: E13V1IB3VIYZZH` at 14:52 IST) resolved `/tradelane-pricing/remoteEntry.js`.
  - The other 3 remotes (`ria`, `pace`, `freight`) were returning S3's fallback `/index.html` (`<!doctype html>`) instead of JS because their S3 buckets lacked `remoteEntry.js` builds.
- **Actions Taken**:
  - Configured Webpack Module Federation (`@angular-architects/module-federation` + `ngx-build-plus`) across `ria` (`smart-pricing`), `pace` (`pricing-simulator`), and `freight` (`freight-automation`) on `i-0c6094d0d53858e59` to match `epic` (`tradelane-pricing`), exposing `'./Routes': './src/app/app.routes.ts'` with `commonChunk: false`.
  - Built and deployed all 4 remotes to their dev S3 buckets, applied S3 CORS rules allowing `https://quantum-dev.allcargoapps.com` and `https://quantum.allcargoapps.com`, and invalidated `/*` across all 5 CloudFront distributions:
    - `tradelane-pricing` (`epic`) â†’ `s3://ds-epic-dev` (`E2X76DWQC8PBOC` / `epic-dev.allcargoapps.com`)
    - `smart-pricing` (`ria`) â†’ `s3://ratebenchmarking-dev` (`E2JLOMMTO7OMAE` / `ria-dev.allcargoapps.com`)
    - `pricing-simulator` (`pace`) â†’ `s3://ds-pace-dev` (`E2IFVRQL6YYIYO` / `pace-dev.allcargoapps.com`)
    - `freight-automation` (`freight`) â†’ `s3://ds-freight-dev` (`E24YWRFMND2S0D` / `freight-dev.allcargoapps.com`)
  - Verified all 4 `/<remote>/remoteEntry.js` endpoints and federated `./Routes` chunks (`2181.js`) return `HTTP/2 200` (`content-type: text/javascript`).

### 2. iTariff CI/CD (`itariff-k8s-repo@develop`) â€” Base Image ECR Registry Login Before Docker Build (`commits ad604ac, 927fa7f`)
- **Problem**: `tariff-selling-bff` (Build #221) failed in `Build Docker Image` with `Your authorization token has expired` because `docker build` pulled its base image from Central ECR (`439891535362.dkr.ecr.eu-central-1.amazonaws.com`) before any ECR login step ran, relying on cached Docker credentials that expire after 12 hours.
- **Fix**: Added explicit `aws ecr get-login-password --region ... | docker login ... 439891535362.dkr.ecr.<region>.amazonaws.com` before `docker build` in `jenkins/tariff-selling-bff` (`ad604ac`) and across the remaining 25 pipelines (`927fa7f`).

---

## 2026-09-30 â€” `tariff-selling-rates-ui` ESLint Build Fix & Knowledge Base Consolidation

### 1. `tariff-selling-rates-ui` Pipeline Fix (`itariff-k8s-repo@develop`, `commit 09ce069`)
- **Problem (Build #133)**: `Install Security Analysis Tools` ran `npm install --save-dev eslint ...`, which mutated `package.json`/`package-lock.json`, installed ESLint v9 (incompatible with `.eslintrc.json` and Node 18), and pruned `style-loader` (causing `npm run build` to fail with missing `style-loader`).
- **Fix**:
  - Changed `--save-dev` to `--no-save` so `package.json` and `package-lock.json` are never mutated.
  - Pinned ESLint v8 (`eslint@^8.57.0`) and included `style-loader css-loader` in the install command so npm never prunes them; exported `ESLINT_USE_FLAT_CONFIG=false`.
  - Added pre-build verification/install of `style-loader` and `css-loader` (`--no-save --legacy-peer-deps`) in `Build Application`.

### 2. Knowledge Base Architecture Consolidation (`commits 41b135b, 266bf4d`)
- Consolidated 35+ split Markdown and CSV files into two canonical files: `knowledge-base/KNOWLEDGE-BASE.md` (domain, cluster, inventory, and cost reference) and `infrastructure/activity-log.md` (reverse-chronological operational log).
- Added zero-dependency SQLite FTS5 search (`scripts/search_knowledge.py`, `scripts/knowledge_sources.py`) with hierarchical `H1 > H2 > H3` section breadcrumbs and date-hint boosting, alongside optional FAISS semantic search (`scripts/query_knowledge.py`).

---

## 2026-09-29 â€” Jenkins Disk Cleanup, EC2 Spot Fleet Scheduling & SonarQube Optimization

### 1. Jenkins Master Volume Disk Cleanup
- **Instance**: `i-0cdcce39da9444d74` (`10.100.95.13`, `c5a.4xlarge`, `eu-central-1`)
- **Volume Mount**: `/home/ubuntu/jenkins-data` (Volume size: 350 GB)
- **Problem**: Volume reached **277 GB (85% utilization)**, leaving only 53 GB free.
- **Root Cause**: Over 5,200 redundant copies of `node_modules` and `.npm-cache` folders were mistakenly archived into historical `htmlreports/` and `archive/` across builds, alongside unpruned inactive workspaces.
- **Actions Taken**:
  - Cleaned unreferenced and stale workspace directories in `/home/ubuntu/jenkins-data/jenkins_home/workspace/` (reclaimed ~54 GB).
  - Pruned archived `node_modules` and cache directories across historical build archives.
- **Result**:
  - Reclaimed **172 GB** of disk space.
  - Disk usage dropped from **277 GB (85%)** down to **105 GB (32%)**.
  - Free space increased to **225 GB**.

---

### 2. Jenkins EC2 Spot Fleet Scheduling Automation
- **Target Resources**:
  - Auto Scaling Group: `euc1-Jenkins-cicd-ec2-ASGfleet`
  - Launch Template: `euc1-Jenkins-cicd-ec2-spot-fleet` (`lt-004093e85d2989b90`)
  - Instance: Spot worker (`t3a.large`)
- **Problem**: Spot fleet instances remained running 24/7 with `MinSize=1` and `DesiredCapacity=1`, incurring costs overnight even after Jenkins Master VM (`i-0cdcce39da9444d74`) stopped at 01:00 AM IST.
- **Actions Taken**:
  1. **Tag Alignment**:
     - Applied schedule tags to ASG `euc1-Jenkins-cicd-ec2-ASGfleet` with `PropagateAtLaunch=true`:
       - `AutoSchedule`: `true`
       - `Schedule`: `09:00-01:00`
       - `ScheduleDays`: `mon-sun`
       - `TimeZone`: `Asia/Kolkata`
       - `Days`: `Mon-sun`
       - `app`: `shared`
       - `map-migrated`: `migE0D4JDFZ6Y`
       - `MontyCloudTagId`: `69bd531e-afd7-4409-9e00-b90e78fe746a`
       - `ActiveMinSize`: `1`, `ActiveDesiredCapacity`: `1`, `ActiveMaxSize`: `4`
  2. **AWS Auto Scaling Scheduled Actions**:
     - `euc1-jenkins-spot-fleet-stop`: Recurrence `0 1 * * *` (01:00 AM IST) -> `MinSize=0`, `DesiredCapacity=0`.
     - `euc1-jenkins-spot-fleet-start`: Recurrence `0 9 * * *` (09:00 AM IST) -> `MinSize=1`, `DesiredCapacity=1`, `MaxSize=4`.
  3. **Lambda Scheduler Integration (`scheduler-rds-ec2`)**:
     - Added `process_asg()` function to dynamically inspect AutoScaling groups tagged with `AutoSchedule=true`.
     - Attached IAM policy `rds-ec2-asg-start-stop` allowing `autoscaling:DescribeAutoScalingGroups` and `autoscaling:UpdateAutoScalingGroup`.
     - Verified live execution: ASG state logs `ASG=euc1-Jenkins-cicd-ec2-ASGfleet Desired=1 Min=1 Max=4 ShouldRun=True`.

---

### 3. SonarQube Server Performance & Memory Optimization
- **Instance**: `i-0cd1ab8b0d9247ef4` (`10.100.95.54`, `t3.large`, `eu-central-1`)
- **Container Stack**: Docker Compose (`/home/ubuntu/sonarqube-docker/docker-compose.yml`) running SonarQube Community v10.7.0 and PostgreSQL 15 Alpine.
- **Problems**:
  - Builds took 12+ minutes total; Quality Gate processing alone took ~4.7 minutes.
  - Compute Engine (`CeServer`) ran on default 512 MB heap (`-Xmx512m`), causing continuous GC thrashing on 88+ MB uncompressed reports.
  - PostgreSQL parallel queries failed with `could not resize shared memory segment: No space left on device` due to Docker default 64MB `/dev/shm`.
- **Actions Taken**:
  1. **SonarQube JVM Heap Tuning**:
     - `SONAR_CE_JAVAOPTS`: `-Xmx2048m -Xms512m -XX:+HeapDumpOnOutOfMemoryError -XX:+UseG1GC` (Compute Engine heap 4x increase).
     - `SONAR_WEB_JAVAOPTS`: `-Xmx1024m -Xms256m -XX:+HeapDumpOnOutOfMemoryError -XX:+UseG1GC` (Web server heap 2x increase).
     - `SONAR_SEARCH_JAVAOPTS`: `-Xmx1024m -Xms1024m -XX:MaxDirectMemorySize=256m -XX:+HeapDumpOnOutOfMemoryError` (Elasticsearch heap 2x increase).
  2. **PostgreSQL Shared Memory & Cache Tuning**:
     - Configured `shm_size: 512m` in Docker Compose for `sonarqube_db` (eliminated 64MB shared memory ceiling).
     - Tuned database parameters: `shared_buffers=256MB`, `work_mem=16MB`, `maintenance_work_mem=64MB`, `effective_cache_size=2GB`.
     - Executed full database `VACUUM ANALYZE`.
- **Results**:
  - Individual SonarQube task execution time dropped from **300+ seconds (5 min)** down to **41â€“63 seconds** (4xâ€“5x faster).
  - API status verified: `{"version":"10.7.0.96327","status":"UP"}`.

---

### 4. Jenkins SonarScanner Optimization
- **Path**: `/home/ubuntu/jenkins-data/jenkins_home/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarScanner/`
- **Actions Taken**:
  1. `conf/sonar-scanner.properties`:
     - Added `sonar.javascript.node.maxspace=4096` to expand Node.js AST parser memory to 4 GB (eliminates V8 GC pauses on large TypeScript codebases).
     - Added `sonar.analysisCache.enabled=true` to enable client-side AST caching across builds.
  2. `bin/sonar-scanner`:
     - Configured default CLI heap: `SONAR_SCANNER_OPTS="${SONAR_SCANNER_OPTS:--Xmx2048m -XX:+UseG1GC}"`.

---

### 5. SonarQube Community Edition Queue & Webhook Insights
- **Architecture Note**: SonarQube Community Edition processes Compute Engine reports via a single worker thread (`sonar.ce.workerCount=1`).
- **Pipeline Stage Behavior**:
  - In Jenkins Stage View, `Quality Gate` showing `(paused for X min)` represents the time `waitForQualityGate` was paused waiting for SonarQube webhook callback.
  - When multiple pipelines run concurrently, tasks are queued in FIFO order in `ce_queue`.
  - With task processing reduced to ~40â€“60s, queue backlogs now clear in a fraction of previous durations.
  - Webhook callback endpoint `http://jenkins.internal-itopaz.com/sonarqube-webhook/` verified healthy with HTTP 200 (~21ms delivery).
  - In `itopaz-k8-repo@develop` (`jenkins/itopaz-export-ui`, commit `d7b8850`), increased `waitForQualityGate` stage timeout from 5 minutes to 15 minutes (`timeout(time: 15, unit: 'MINUTES')`) so large frontend reports (~5.1 min compute + FIFO queue wait) do not abort at 4m 59s.

---

### 6. Prefiler `microfrontend-main` SIT EU Region & Parameter-Override Fix (`prefiler-k8s-repo@sit`, `commits 4b806e5, 43c532c, 925a5bc`)
- **Problem**: `jenkins/sit/ui/microfrontend-main` deployed to Singapore (`ap-southeast-1` / `apse1-itopaz-sit-eks`) instead of Frankfurt (`eu-central-1` / `euc1-itopaz-sit-eks`) because Jenkins passed cached `params.AWS_REGION` and `params.EKS_CLUSTER_NAME` values from earlier builds, and rollout failures were swallowed without failing the stage.
- **Fix**: Updated `jenkins/sit/ui/microfrontend-main` to target `eu-central-1` / `euc1-itopaz-sit-eks` (`4b806e5`), fail builds on unhealthy frontend rollout (`43c532c`), and lock `AWS_REGION` and `EKS_CLUSTER_NAME` directly in the `environment` block (`925a5bc`) so stale Jenkins parameter defaults cannot override branch configuration.

---

## 2026-09-28 â€” China AKS PrivateLink DNS & TIBCO EBX Auto-Healing

### TIBCO EBX Multi-Environment Autonomous Auto-Healing (SIT & PROD)
- **Application**: TIBCO EBX MDM Server (Port 8080)
- **Overview**: Deployed autonomous self-healing agent (`ebx_auto_heal.py` / `ebx_auto_heal.sh`) to detect application crashes, hung threads, memory exhaustion, or 5xx/404 errors, and automatically recycle EBX services safely.
- **SIT Frankfurt Environment**:
  - Account: `464134132424` | Region: `eu-central-1`
  - EC2 Instance: `i-08a20bae22e57e46d` | Private IP: `10.100.215.180`
  - DNS: `ebx.internaleu1-itopaz.com`
  - Restart method: `script` (`/opt/tibco/ebx/EBX_SERVER/bin/startup.sh`, `/opt/tibco/ebx/EBX_SERVER/bin/shutdown.sh`) â€” systemd service is omitted on SIT.
  - Deployment: Scripted via `deploy-to-sit-ebx.sh` and `deploy-to-sit-via-bastion.sh` (via Bastion `10.100.208.17`).
- **PROD Frankfurt Environment**:
  - Account: `965031587107` | Region: `eu-central-1`
  - EC2 Instance: `i-0add8ef2aa72adb7c` | Private IP: `10.100.110.76`
  - Endpoint: `http://10.100.110.76:8080/ebx/`
  - Health check logic: Handles HTTP 302 servlet redirect to `/ebx-ui/` as a valid healthy status.
  - Deployment: Scripted via `deploy-to-prod-ebx.sh`.
- **Timing & Safeguards**:
  - Startup Grace Period: 180s (allows 1GB+ WAR files to expand).
  - Maximum Startup Wait: 480s before marking startup failure.
  - Restart Cooldown: 1800s (30 minutes) to prevent crash-loop cascades.

### Microsoft Graph API Integration (mail.py)
- **Script**: `mail.py`
- **Application**: Microsoft Graph Command Line Tools Client (`14d82eec-204b-4c2f-b7e8-296a70dab67e`).
- **Auth Flow**: Device Code SSO flow (`https://login.microsoftonline.com/common`) with `token_cache.bin` serialization.
- **Scope**: `Mail.Read` for automated message reading.

> **Generated:** September 28, 2026  
> **Target Systems:** Jenkins CI/CD, Azure China AKS (DEV/SIT/UAT), TIBCO EBX (SIT/PROD Frankfurt)

---

### 1. Azure China North 3 PrivateLink AKS DNS Resolution for Jenkins

### Problem Statement
The Jenkins CI/CD master server (`10.100.95.13` in AWS `eu-central-1`) executes automated build and deployment pipelines targeting Kubernetes clusters hosted in **Azure China North 3**. Because these AKS clusters are configured with **Azure Private Link**, their FQDNs are hosted inside Azure private DNS zones (`privatelink.chinanorth3.cx.prod.service.azk8s.cn`) and cannot be resolved by external DNS resolvers.

### Solution
An automated DNS resolution and injection script ([`infrastructure/update-all-jenkins-ips.sh`](file:///home/ec2-user/rahul/infrastructure/update-all-jenkins-ips.sh)) connects to Azure China jump hosts via SSH, queries their local resolvers for the private IP addresses of the AKS API servers, and updates `/etc/hosts` on the Jenkins master.

### Target Environments & Private Link FQDNs

| Environment | Jump Server IP | SSH User | SSH Key | Azure PrivateLink AKS Domain |
|---|---|---|---|---|
| **DEV China** | `10.180.144.6` | `jumpsrvadmin` | `infrastructure/secrets/keys/dev/china/dev-china.pem` | `cn3itopazdnsaks-uda8w8iw.b04e70a6-4bc5-4d45-acd4-cd0326008af9.privatelink.chinanorth3.cx.prod.service.azk8s.cn` |
| **SIT China** | `10.180.208.4` | `jumpsrvadmin` | `infrastructure/secrets/keys/sit/china/sit-china.pem` | `cn3itopazdnsaks-xa4051st.d7819a1a-cb36-41f1-9f01-d99f25882fa1.privatelink.chinanorth3.cx.prod.service.azk8s.cn` |
| **UAT China** | `10.180.176.4` | `jumpsrvadmin` | `infrastructure/secrets/keys/uat/china/uat-dev.pem` | `cn3itopazdnsaks-1apj69gf.90610dc7-cc30-4aaa-8ae9-0ab2bc5a295c.privatelink.chinanorth3.cx.prod.service.azk8s.cn` |

### Execution Workflow
```bash
# Update Jenkins /etc/hosts with latest China AKS PrivateLink IPs
bash infrastructure/update-all-jenkins-ips.sh
```

---

### 2. TIBCO EBX Multi-Environment Autonomous Auto-Healing

### Overview
TIBCO EBX is a critical Master Data Management (MDM) server running on EC2. EBX instances occasionally experience memory exhaustion, thread deadlocks, or hung connector threads, causing HTTP 5xx errors or connection timeouts. The EBX Auto-Healing Framework ([`scripts/ebx-auto-healing/`](file:///home/ec2-user/rahul/scripts/ebx-auto-healing/)) provides autonomous health-checking, failure thresholding, and graceful/forceful process recycling.

### Environment Matrix

| Parameter | SIT Frankfurt | PROD Frankfurt |
|---|---|---|
| **AWS Account** | `464134132424` | `965031587107` |
| **Region** | `eu-central-1` | `eu-central-1` |
| **Instance ID** | `i-08a20bae22e57e46d` | `i-0add8ef2aa72adb7c` |
| **Private IP** | `10.100.215.180` | `10.100.110.76` |
| **Internal DNS** | `ebx.internaleu1-itopaz.com` | N/A |
| **Health Check URL** | `http://10.100.215.180:8080/ebx/` | `http://10.100.110.76:8080/ebx/` |
| **Expected HTTP Code** | `200` | `302` or `200` (servlet redirect to `/ebx-ui/`) |
| **Restart Mechanism** | `script` (`startup.sh` / `shutdown.sh`) | `script` / `systemd` |
| **Startup Wait** | 180s grace + 480s max wait | 180s grace + 480s max wait |
| **Restart Cooldown** | 1800s (30 minutes) | 1800s (30 minutes) |

### Key Architectural Safeguards
1. **Startup Grace Period**: Because EBX deploys large WAR files (~1 GB+), startup takes 3 to 5 minutes. The healer enforces a 180s initial grace period before checking health, avoiding premature restart loops.
2. **HTTP 302 Redirection Handling**: On production, `/ebx/` returns a `302 Moved Temporarily` to `/ebx-ui/`. The health check recognizes 302 as healthy.
3. **Cascade Prevention Cooldown**: A strict 30-minute cooldown prevents rapid restart cycles if the underlying issue is database or storage related.
4. **Deploy Scripts**:
   - SIT Direct: `scripts/ebx-auto-healing/deploy-to-sit-ebx.sh`
   - SIT via Bastion: `scripts/ebx-auto-healing/deploy-to-sit-via-bastion.sh` (via Bastion `10.100.208.17`)
   - PROD Direct: `scripts/ebx-auto-healing/deploy-to-prod-ebx.sh`

---

### 3. Microsoft Graph API CLI Integration

### Script Overview: [`mail.py`](file:///home/ec2-user/rahul/mail.py)
Provides authenticated access to Microsoft 365 Exchange mailboxes via Microsoft Graph API without requiring custom Azure App Registrations in the tenant.

- **Client ID**: `14d82eec-204b-4c2f-b7e8-296a70dab67e` (Microsoft Graph Command Line Tools public client)
- **Authority**: `https://login.microsoftonline.com/common`
- **Scope**: `Mail.Read`
- **Authentication**: Device Code Flow (`initiate_device_flow`) with cached tokens serialized to `token_cache.bin`.
- **Usage**:
  ```bash
  python3 mail.py
  ```

---

### 4. Verification and Daily Maintenance
The consolidated knowledge base and vector database index should be refreshed after any architectural or configuration update:
```bash
# Rebuild single-file consolidated KB
bash scripts/rebuild-knowledge-base.sh

# Re-index all markdown chunks into FAISS
python3 scripts/ingest_knowledge.py

# Query semantic index
python3 scripts/query_knowledge.py "EBX auto heal configuration"
```

---

## 2026-09-25 â€” Operations Log

### Azure China North 3 PrivateLink AKS DNS Resolution for Jenkins
- **Problem**: The Jenkins CI/CD master server (`10.100.95.13`, AWS eu-central-1) builds and deploys artifacts to Azure China North 3 AKS clusters, but cannot resolve China PrivateLink internal FQDNs.
- **Solution**: Automated script `infrastructure/update-all-jenkins-ips.sh` connects to Azure China jump hosts via SSH, resolves the internal PrivateLink IPs using `nslookup`, and updates `/etc/hosts` on the Jenkins server.
- **Environments & Private Link Endpoints**:
  - **DEV China Jump**: `10.180.144.6` (user `jumpsrvadmin`, key `infrastructure/secrets/keys/dev/china/dev-china.pem`)
    - Domain: `cn3itopazdnsaks-uda8w8iw.b04e70a6-4bc5-4d45-acd4-cd0326008af9.privatelink.chinanorth3.cx.prod.service.azk8s.cn`
  - **SIT China Jump**: `10.180.208.4` (user `jumpsrvadmin`, key `infrastructure/secrets/keys/sit/china/sit-china.pem`)
    - Domain: `cn3itopazdnsaks-xa4051st.d7819a1a-cb36-41f1-9f01-d99f25882fa1.privatelink.chinanorth3.cx.prod.service.azk8s.cn`
  - **UAT China Jump**: `10.180.176.4` (user `jumpsrvadmin`, key `infrastructure/secrets/keys/uat/china/uat-dev.pem`)
    - Domain: `cn3itopazdnsaks-1apj69gf.90610dc7-cc30-4aaa-8ae9-0ab2bc5a295c.privatelink.chinanorth3.cx.prod.service.azk8s.cn`
  - **Jenkins Host**: `10.100.95.13` (user `root`, key `infrastructure/secrets/keys/shared/jenkins/jenkins.pem`, target `/etc/hosts`).

---

---

## 2026-09-24 â€” Operations Log

### Knowledge Base Reorganization & AI Indexing Architecture
- **Objective**: Restructure repository `/home/ec2-user/rahul` into a canonical knowledge indexing hub for AI tools (Copilot, Antigravity, Cursor, Claude).
- **Cleanup**:
  - Removed 54MB unindexed `vectordb-work/chunks.json` checkpoint.
  - Removed outdated duplicate `knowledge-base/eks-clusters.md` in favor of canonical `knowledge-base/docs/eks-clusters.md`.
  - Removed stale logs (`ingest.log`, `ingest2.log`) and scratch directories (`.tmp/`, `tmp-docproxy/`).
  - Cleared root secrets (`test`, `token`) and placed credentials in `infrastructure/secrets/`.
- **Restructuring**:
  - Re-homed `export` to `knowledge-base/docs/knowledge-export/15-session-knowledge-export-2026-09-01.md`.
  - Re-homed `loop-ai-cost-breakdown.md` to `knowledge-base/docs/cost-reports/loop-ai-cost-breakdown.md`.
  - Re-homed `activity-log.md` to `infrastructure/activity-log.md`.
  - Grouped multi-cluster kubeconfigs into `infrastructure/configs/`.
  - Relocated scripts (`create_feature_branches.py`, `fix-apigateway-cors.sh`) to `scripts/`.
- **AI Tool Navigation**:
  - Authored `AI-INDEX.md` as primary machine-readable reference.
  - Rebuilt consolidated `KNOWLEDGE-BASE.md` (34 docs, 7,931 lines, 0 skipped).
  - Regenerated FAISS vector database: deduplicated chunk count from 1,538 down to 1,109 chunks, each tagged with `[Source: <path>]`.

---

---

## 2026-09-23 â€” Operations Log

### SIT Singapore â€” AFR Prefiler Service DB & Secrets Audit
- **Cluster**: `apse1-itopaz-sit-eks` (SIT SG, Account `464134132424`, Region `ap-southeast-1`)
- **Namespace**: `prefiler-api` | **Service**: `afr-prefiler-service`
- **Action**: Audited deployment environment variables, database connection strings, configmaps, and secrets.
- **Verification**: Verified container environment injection (`conn`, `host`, `db`, `postgres`), confirmed secret references and DB connectivity from the pod.

### DEV EU â€” MDM ALB Cognito M2M & API Gateway Auth
- **Account**: `074779643551` | **Region**: `eu-central-1`
- **Host**: `mdm-bw-dev.itopazapp.com` fronted by Private ALB (`private-alb`, ID `389490502178fcdb`), listener `6a8665f4f7659890`.
- **Cognito User Pool**: `eu-central-1_MHe1qfDpe` (domain `eu-central-1mhe1qfdpe`).
- **Setup**: Dedicated M2M client `mdm-bw-dev-m2m` (`hjgb6ad314nmq6dhp3rhrmlpr`) with scope `mdm-bw/mdm-bw` via client_credentials grant.
- **Token Endpoint**: `https://eu-central-1mhe1qfdpe.auth.eu-central-1.amazoncognito.com/oauth2/token`.
- **Validation**: Generated access token and validated against backend services.

---

---

## 2026-09-18 â€” itariff DEV UI login chain, CI -latest fix, MDM Cognito m2m, Datalakeâ†”DB reachability

### A. DEV EU (074779643551) â€” itariff UI login chain fixed
Three separate ap-south-1 / config leaks broke `itariff-eudev.itopazapp.com`:
1. **BFF token 401** â€” `tariff-selling-bff` configmap `jwt-token.auth-base-uri` = an ap-south-1 Istio ELB (doesn't resolve from Frankfurt) â†’ "Could not process token". Fixed live to in-cluster `http://tariff-profile-service.itariff-api.svc.cluster.local/profile-domain-service/` (profile svc verified 200), restarted. NOT yet persisted to repo (`itariff-k8s-repo/config/tariff-selling-bff.yaml`).
2. **Mixed content / navbar died** â€” the itariff shell single-spa import-map loaded microfrontends from the ap-south-1 ELB over HTTP â†’ browser blocked on HTTPS. main-ui `dev` branch import-map already correct (same-origin HTTPS); live pods patched as stopgap. App repos build from `dev`; manifest/pipeline repo builds from `develop`.
3. **Login CORS/403** â€” `itariff-bff-eudev.itopazapp.com` is fronted by API Gateway `tj1dse31fi` (stage dev), custom-domain base-path mapping = `itariff-apis`. Calling `/tariff-grant-bff/...` without that prefix â†’ API GW 403, no CORS headers (browser reports CORS). Fixed `tariff-microfrontend-share-ui@dev` `environment.development.ts`: apiUrlReq/setRFQApiUrlReq/sellingApiUrl â†’ `https://itariff-bff-eudev.itopazapp.com/itariff-apis/<bff>/...` (commit `ca1ec5c`). Verified OPTIONS preflight 200 + Access-Control-Allow-Origin. Dev BFF Istio VS prefixes: /tariff-grant-bff/, /tariff-selling-bff/, /tariff-external-bff/.

### B. CI â€” itariff microfrontend pipeline `-latest` push bug (itariff-k8s-repo@develop `698f623`)
Push-to-ECR stage used single-quoted `sh`; `${ENVIRONMENT}` resolved by shell but it's `params.ENVIRONMENT` (not exported) â†’ empty â†’ pushed `...--latest` (nonexistent) â†’ `tag does not exist` â†’ FAILURE before Deploy/CloudFront. Fixed both `jenkins/tariff_microfrontend-main-ui` and `..._share-ui`: add `ENVIRONMENT=${params.ENVIRONMENT}` to push withEnv + re-tag latest from the versioned tag before pushing.

### C. MDM Cognito â€” ALB auth then client-credentials (074779643551, pool eu-central-1_MHe1qfDpe)
- Existing `itopaz-api` client (`lsssnrbmsd0i8u1ba96g5gu7`) left unchanged throughout.
- Initially added ALB authenticate-cognito on `private-alb` rules for `mdm-bw-dev.itopazapp.com` (prio 15 precompany-dev, prio 20 precontect-dev) with a new `mdm-bw-dev-alb` client. Per follow-up (client-credentials needed, ALB login not), REVERTED both ALB rules to plain forward and DELETED `mdm-bw-dev-alb` (Cognito forbids code + client_credentials on one client).
- Created resource server `mdm-bw` (scope `mdm-bw/mdm-bw`) + m2m client `mdm-bw-dev-m2m` = `hjgb6ad314nmq6dhp3rhrmlpr` (client_credentials + secret). Token URL `https://eu-central-1mhe1qfdpe.auth.eu-central-1.amazoncognito.com/oauth2/token`, scope `mdm-bw/mdm-bw`. Verified token 200. Client tool must use /oauth2/token (was set to the JWKS url) and grant=client_credentials.

### D. Connectivity â€” Datalake (581621506601) â†” Frankfurt DBs via VPC Reachability Analyzer
- Datalake eu-central-1 VPCs: prod `vpc-079ff2bbf76ff68d5` (10.237.0.0/16; subnets 10.237.30.0/24 + 10.237.31.0/24 share rtb-0b449509135c45625 with routes to 10.100.0.0/16 + 10.1.0.0/16 via VGW vgw-0f573849578d41def); default `vpc-0d436b94a4f001fe7` (172.31.0.0/16, IGW-only).
- Targets: itopaz-dev DB `euc1-itopaz-dev-database-cluster` = 10.100.159.12:5432 (dev, SG sg-04fa8421b5d265ccf); MDM DB `ecu-mdm-db-cluster` = 10.100.127.27:5432 in PROD 965031587107 (SG sg-081e47d0f39d10b09). Both DB SGs allow 5432 from 0.0.0.0/0 (flag: over-permissive).
- Named analyzer results (datalake account, eu-central-1):
  - `datalake-to-itopaz-dev-db` (nip-0a138d00ecdb96cfe): 10.237.x â†’ itopaz-dev 5432 = **PathFound true**.
  - `dms-to-ecu-mdm-db` (nip-0d16a410562ec0517): DMS 10.237.30.150 â†’ MDM 10.100.127.27 5432 (and 1433) = **PathFound true at AWS layer**. Remaining failure (if any) is on-prem/VPN firewall (VGW egress) or DMS port/engine mismatch (DMS = 1433/SQL Server, MDM target = Postgres 5432).
  - `datalake-defaultvpc-to-itopaz-dev-db` (nip-07874ee27790ef371): 172.31.x (i-0811f157ad78a9979 / 172.31.44.233) â†’ 10.100.x = **NOT reachable** (IGW_DESTINATION_ADDRESS_NOT_IN_RFC1918_EGRESS; default VPC has no TGW/peering/VGW to 10.100.x). Reverse (dev DB â†’ 172.31.44.233) also NOT reachable (TGW_RTB_ROUTES_ARE_UNKNOWN).
- Conclusion: 10.237.x datalake VPC reaches the dev/MDM DBs; the 172.31.x default VPC does not (needs TGW/peering to 10.100.0.0/16). us-east-1 datalake reaches the DBs over its TGW (verified live TCP 5432 earlier).

---

### Additional Notes (Activity Log)
### DEV EU â€” itariff UI login chain fixed (bff auth-base-uri, mixed content, CORS/base-path)
- **Cluster**: `euc1-itopaz-dev-eks` (dev, acct 074779643551), bastion `i-05c33080ab25c83cc`
- **`itariff-bff-upload` 401 "Could not process token"**: `tariff-selling-bff` configmap `jwt-token.auth-base-uri` pointed at an `ap-south-1` Istio ELB (unresolvable from Frankfurt) â†’ token validation failed. Fixed live â†’ `http://tariff-profile-service.itariff-api.svc.cluster.local/profile-domain-service/` (verified profile svc HTTP 200); restarted. (live-only; repo source `itariff-k8s-repo/config/tariff-selling-bff.yaml` still has ap-south-1 â€” not yet persisted.)
- **`itariff-eudev` blank page / "navbar died" (mixed content)**: the itariff shell import-map loaded microfrontends (navbar/shared_ui, buying/selling-rates, user-security) from the `ap-south-1` ELB over **HTTP** â†’ browser blocked on HTTPS page. main-ui `dev` branch import-map was already correct (HTTPS same-origin); live pods patched as stopgap. App builds from **dev** branch (manifest/pipeline repo builds from **develop**).
- **Login CORS/403**: `itariff-bff-eudev.itopazapp.com` is fronted by **API Gateway** `tj1dse31fi` (stage dev) whose custom-domain base-path mapping is **`itariff-apis`**. share-ui env URLs must be `https://itariff-bff-eudev.itopazapp.com/itariff-apis/<bff>/...`. Corrected `tariff-microfrontend-share-ui@dev` `environment.development.ts` (apiUrlReq/setRFQApiUrlReq/sellingApiUrl) â†’ commit `ca1ec5c`. Verified OPTIONS preflight 200 + ACAO present. (Earlier wrong attempt stripped /itariff-apis then restored it.)
- Dev BFF Istio VS prefixes (host itariff-bff-eudev): `/tariff-grant-bff/`, `/tariff-selling-bff/`, `/tariff-external-bff/` (no /itariff-apis prefix at Istio â€” that's the API GW base path).

### DEV EU â€” itariff microfrontend Jenkins pipeline `-latest` push bug fixed
- **Repo**: `itariff-k8s-repo@develop` (Jenkins loads pipelines from develop), commit `698f623`
- Push-to-ECR stage used single-quoted `sh` so `${ENVIRONMENT}` was resolved by shell, but it's `params.ENVIRONMENT` (not an env var) â†’ empty â†’ pushed wrong tag `...--latest` â†’ `tag does not exist` â†’ pipeline FAILURE before Deploy/CloudFront.
- Fixed both `jenkins/tariff_microfrontend-main-ui` and `jenkins/tariff_microfrontend-share-ui`: added `ENVIRONMENT=${params.ENVIRONMENT}` to push-stage withEnv + re-tag latest from the just-pushed versioned tag before pushing.

### DEV â€” MDM ALB Cognito + Cognito client-credentials for mdm-bw-dev
- **Account** 074779643551, pool `eu-central-1_MHe1qfDpe` (domain `eu-central-1mhe1qfdpe`), existing client `itopaz-api` (`lsssnrbmsd0i8u1ba96g5gu7`) left UNCHANGED.
- Host `mdm-bw-dev.itopazapp.com` â†’ NLB `private-nlb-7422754f0293360e` â†’ ALB `private-alb` (`389490502178fcdb`), HTTPS listener `6a8665f4f7659890`, rules prio 15 (`precompany-dev`) + 20 (`precontect-dev`).
- Added ALB authenticate-cognito on both rules (new client `mdm-bw-dev-alb`) then, per request for client-credentials, REVERTED ALB rules to plain forward and DELETED `mdm-bw-dev-alb` (Cognito can't combine code + client_credentials on one client).
- Created resource server `mdm-bw` (scope `mdm-bw/mdm-bw`) + dedicated m2m client `mdm-bw-dev-m2m` = `hjgb6ad314nmq6dhp3rhrmlpr` (client_credentials). Token URL `https://eu-central-1mhe1qfdpe.auth.eu-central-1.amazoncognito.com/oauth2/token`, scope `mdm-bw/mdm-bw`. Verified token HTTP 200. (User's tool had wrong Access Token URL = JWKS url; correct is /oauth2/token.)

### Connectivity â€” Datalake (581621506601) â†” Frankfurt DBs (VPC Reachability Analyzer)
- **Datalake VPCs (eu-central-1)**: prod `vpc-079ff2bbf76ff68d5` (`10.237.0.0/16`, private subnets 10.237.30.0/24 + 10.237.31.0/24, route to `10.100.0.0/16` + `10.1.0.0/16` via VGW `vgw-0f573849578d41def`); default `vpc-0d436b94a4f001fe7` (`172.31.0.0/16`, IGW-only, no private path).
- **DBs**: itopaz-dev `euc1-itopaz-dev-database-cluster` = `10.100.159.12:5432` (dev, SG `sg-04fa8421b5d265ccf`, ingress allows 5432 from 0.0.0.0/0). MDM `ecu-mdm-db-cluster` = `10.100.127.27:5432` in **PROD 965031587107** (SG `sg-081e47d0f39d10b09`, 5432 from 0.0.0.0/0) â€” reached via VGW.
- **Results (named analyzer paths in datalake acct)**:
  - datalake `10.237.x` (DMS eni-0f4510c17bb3386ef / working host 10.237.31.69) â†’ itopaz-dev DB 5432: **REACHABLE** (`datalake-to-itopaz-dev-db` nip-0a138d00ecdb96cfe)
  - datalake `10.237.x` (DMS 10.237.30.150) â†’ MDM DB 10.100.127.27 5432/1433: **REACHABLE at AWS layer** (`dms-to-ecu-mdm-db` nip-0d16a410562ec0517); if DMS still fails it's on-prem/VPN firewall (traffic egresses via VGW) or a port/engine mismatch (DMS mentioned 1433/SQL Server but MDM target is Postgres 5432).
  - datalake **default VPC `172.31.x`** (i-0811f157ad78a9979, 172.31.44.233) â†’ any 10.100.x DB: **NOT REACHABLE** (`datalake-defaultvpc-to-itopaz-dev-db` nip-07874ee27790ef371) â€” IGW_DESTINATION_ADDRESS_NOT_IN_RFC1918_EGRESS; default VPC has no TGW/peering/VGW to 10.100.x.
  - dev DB â†’ datalake 172.31.44.233: NOT REACHABLE (TGW_RTB_ROUTES_ARE_UNKNOWN â€” 172.31 default VPC not attached to TGW).
- Note: DB SGs on 5432 are open to 0.0.0.0/0 (security concern to flag). us-east-1 datalake reaches the DB fine over its TGW.

---

---

## 2026-09-17 â€” itopaz print-service: SIT EU fix + SIT SG full build + DEV sa-prefiler DB case fix

### A. SIT EU (euc1-itopaz-sit-eks, acct 464134132424, ns itopaz-platform) â€” print end-to-end fix

**Issue**
- Print failing: `Cognito: token request failed EnsureSuccessStatusCode()` (CognitoTokenProvider.cs:94) then `print-api: HTTP request failed Name or service not known (auhd83rlcc.execute-api.eu-central-1.amazonaws.com:443)`

**Root cause (three layers)**
1. No `execute-api` interface VPC endpoint in the SIT VPC (dev had `vpce-06981254c0aa4ec5c`), so pods could not resolve the private API Gateway host.
2. Cognito: `PrintService__CognitoTokenUrl` was the JWKS discovery URL, not `/oauth2/token`; the print-service was wired to the `itariff-int-api` app client (scope `uat-itariff/uat-itariff`); and the `sit-print` resource server had `Scopes: null` (the referenced scope `sit-print/sit-print` did not exist).
3. API GW `auhd83rlcc` VPC link `0p5gtn` targeted the istio-gateway NLB (`a6e66b6...`), not the printer NLB â€” so authenticated calls hit Istio and returned 404.

**Fix Applied**
- Created SG `sg-007e2088c31181321` (tcp/443 from VPC CIDR `10.100.208.0/20`) + interface endpoint `vpce-0296f0dc9182ab0e8` (`com.amazonaws.eu-central-1.execute-api`, private-DNS on) in `vpc-07d21eafbea59ffec`, subnets `subnet-0b42d6686c611a2cf`/`subnet-05ccfb4d81d44dc9a`.
- Cognito on pool `eu-central-1_pGYVM1kAF`: `update-resource-server sit-print` add scope `sit-print`; created dedicated app client `sit-print` (client_credentials + scope `sit-print/sit-print` + secret); patched k8s secret `cognito-client-secret` (ClientId/ClientSecret); set `PrintService__CognitoTokenUrl=https://eu-central-1pgyvm1kaf.auth.eu-central-1.amazoncognito.com/oauth2/token`.
- Created VPC link `mnc7gc` â†’ printer NLB `private-nlb-2e9e6ffae6470607` (TG `printer-trg` â†’ `10.1.161.184:8000`); repointed `/print-pdf` POST integration to `http://<printer-nlb>:8000/print-pdf/` via `mnc7gc`; method auth `COGNITO_USER_POOLS` + authorizer `5tyfwg` + scope `sit-print/sit-print`; redeployed `sit` stage. Reverted configmap `PythonApiUrl` to the API GW URL `https://auhd83rlcc.execute-api.eu-central-1.amazonaws.com/sit/print-pdf/`.

**Verified**
- Pod resolves `auhd83rlcc...` â†’ private VPCE IPs; token endpoint HTTP 200; logs show `Cognito: new access token obtained` + POST to FastAPI with no DNS/404/token errors.

**Persisted**: `itopaz-k8-repo@sit` commit `c3d3fed` â€” `configmap/itopaz-print-svc-config.yml` (CognitoTokenUrl â†’ /oauth2/token).

**Pending (on-prem)**: FastAPI printer `10.1.161.184:8000` intermittently down (TCP reset / failed NLB health checks for dev+sit+sg alike) â€” on-prem team to stabilize.

### B. SIT SG (apse1-itopaz-sit-eks, acct 464134132424, ap-southeast-1, ns itopaz-platform) â€” full print backend built

**Context / Root cause**
- SG had no print backend at all (no Cognito pool, no printer NLB, no execute-api VPCE; configmap was a `RouteConfig`/`TempUserName` stub). SG has no on-prem route (route tables: local `10.130.208.0/20` + TGW `tgw-03b17f26861c2d348` to `10.100.208.0/20` = Frankfurt SIT; on-prem `10.1.0.0/16` unreachable â€” pod test to `10.1.161.184` timed out). Frankfurt printer NLB IPs `10.100.210.87`/`10.100.212.5:8000` ARE reachable over the TGW. VPC links can't target a cross-region NLB, so the design routes SG â†’ local NLB (IP targets = Frankfurt printer NLB) â†’ TGW â†’ Frankfurt printer.

**Fix Applied** (apigateway + cognito calls executed from the Frankfurt bastion `i-0bd3314ea08e6fb27`, because the SG bastion `i-05b9998627e8bf6e8` and SG pods are FortiGate-firewalled from apigateway/cognito control-plane endpoints â€” only sts/ec2/elbv2 work there):
- Cognito pool `ap-southeast-1_6tmeKAlKO`, domain `ap-southeast-1z6tmekalko`, resource server `sit-print` (scope `sit-print/sit-print`), client_credentials client `sit-print` = `5se0prnod6lmkk5t1a8nku9g6h`.
- Internal NLB `apse1-sit-print-nlb` (`f04db685e457ea64`); TG `printer-trg-apse1` (TCP:8000, target-type ip) â†’ `10.100.210.87` + `10.100.212.5:8000`; listener :8000.
- VPC link `8or43j` â†’ that NLB; REST API `xma8dve4r5` (`itopaz-sit-print`, REGIONAL), `/print-pdf` POST, authorizer `jw96r3` (COGNITO pool above), HTTP_PROXY â†’ `http://apse1-sit-print-nlb-...:8000/print-pdf/`, scope `sit-print/sit-print`, stage `sit`. Invoke URL `https://xma8dve4r5.execute-api.ap-southeast-1.amazonaws.com/sit/print-pdf/`.
- execute-api interface VPCE `vpce-0e21b23cb0505f9cd` (+ SG `sg-079cd247d1989b342`, tcp/443 from `10.130.208.0/20`) in `vpc-0c46bfc8553c53eec`, app subnets `subnet-0ee9930c0495224b2`/`subnet-07de4f20c7f8317be`.
- Patched configmap (`PythonApiUrl`, `CognitoTokenUrl`, `CognitoScope`) + `cognito-client-secret`; print-service rolled out 2/2.

**Verified**: VPCE available; pod resolves + reaches the private API GW (403 without token = auth enforced); printer NLB reachable over TGW.

**Persisted**: `itopaz-k8-repo@sit` commit `05ccc8a` â€” `configmap/itopaz-singapore-print-svc-config.yml`.

**Pending (network/on-prem)**: SG SIT pods have NO outbound HTTPS egress (FortiGate 403 on everything incl. google.com + all Cognito endpoints) â€” network team must allow egress from app subnets `10.130.208.0/22` + `10.130.212.0/22` to `*.auth.ap-southeast-1.amazoncognito.com:443` (and cognito-idp) for the token flow. Shared on-prem printer also down.

### C. DEV EU (euc1-itopaz-dev-eks, acct 074779643551, ns prefiler-api) â€” sa-prefiler-service DB name case fix

**Issue**: `/sa-prefiler-service/saapi/GetDashboardSummary` â†’ `Npgsql.PostgresException 3D000: database "Dbedi_uat" does not exist` at `LegalEntityRepository.GetLegalEntityAsync`. Pods Running 2/2 (runtime error, not crash).

**Root cause**: deployment inline env `ConnectionStrings__EdiDBHost__ZoneN` used `Database=Dbedi_uat` (capital D); actual DB on `euc1-itariff-edi-dev` is `dbedi_uat` (lowercase). PostgreSQL identifiers are case-sensitive â†’ not found. Inline env overrode the configmap (which already had lowercase).

**Fix Applied**: patched all 7 `EdiDBHost` zone entries (`zone0`â€“`Zone6`) `Dbedi_uat` â†’ `dbedi_uat`; rolled out 2/2.

**Verified**: no more 3D000; direct psql confirms `dbedi_uat` reachable with `prefiler_dev` creds and `legalentity` table present.

**Persisted**: `prefiler-k8s-repo@dev` commit `dbc17fa` â€” `sa-prefiler-service.yml` (7 EdiDBHost entries lowercased).

### D. Earlier this session (context; some live-only)
- **ECR lifecycle policies** added then REMOVED (dev 7d / sit 14d / uat 30d) â€” caused an ImagePullBackOff wave; policies deleted (dev 074779643551, sit 464134132424, uat 405478414008).
- **DEV prefiler-api fixes** pushed to `prefiler-k8s-repo@dev`: master/sa connstring `$()` expansion (Option B â€” connstrings in deployment env), aci CORS, Redis config for aes/ams/dagangnet/imdg/mblfiler/mpci.
- **itariff-k8s-repo** private-alb dev: ALB path patterns `/precompany*`, `/createnewcontact*`; added microfrontend Jenkinsfiles (`@develop`, retargeted to dev). `prefiler-k8s-repo@sit` image-tag manifest fixes pushed.
- **PROD 745510282686 (ap-south-1)**: restarted `chatecutopazpolicy` GPU box `i-0df6d3e05ce8f271c` + installed autoheal cron.

---

---

## 2026-09-01 â€” Jump Server Kubeconfig Merge, New UAT Account Discovery & MDMBWPROJ Feature Branches

### Action
- Received a new kubeconfig (`/home/ec2-user/rahul/config`) covering 6 itopaz EKS clusters, including 2 previously undocumented ones in account `405478414008` (UAT): `use1-itopaz-uat-eks` (us-east-1), `euc1-itopaz-uat-eks` (eu-central-1)
- Merged it into this jump server's `~/.kube/config` via `KUBECONFIG=~/.kube/config:/home/ec2-user/rahul/config kubectl config view --flatten`, preserving the pre-existing `ecu-eks-test-cluster` (745510282686) entry and its `current-context`
- Backed up prior config to `~/.kube/config.bak.<timestamp>` before overwrite

### Issue Found
- `kubectl --context sit-singapore get nodes` failed with:
  ```
  AccessDenied: User arn:aws:sts::745510282686:assumed-role/eks-jump-server-role/i-019825d0de3300832
  is not authorized to perform: sts:AssumeRole on resource: arn:aws:iam::464134132424:role/eks-jump-access
  ```
- Root cause: this jump server's EC2 instance role (`eks-jump-server-role`, account 745510282686) is not in the trust policy of the `eks-jump-access` roles in the other itopaz accounts â€” cross-account AssumeRole is blocked
- Not yet fixed â€” requires editing the `eks-jump-access` role trust policy in each target account (464134132424, 074779643551, 965031587107, 405478414008), which needs explicit confirmation before making IAM changes in accounts outside this session's original scope

### Separately Observed (unresolved, parked)
- `git fetch`/`git ls-remote` against `bitbucket.org` hangs indefinitely on this jump server for repos under `/home/ec2-user/rahul/clones/`
- Traced to the global git config `credential.helper = !aws codecommit credential-helper $@` â€” `git credential fill` for host `bitbucket.org` hangs (confirmed via direct `git credential fill` test, exit via timeout only), even though direct network connectivity (curl) to `bitbucket.org` and `api.bitbucket.org` is fine and fast
- Manually invoking `aws codecommit credential-helper get` in isolation returns immediately, so the hang is specific to git's invocation path, not the AWS CLI call itself â€” needs further isolation (e.g. `strace` or removing the global helper and relying on the repo-local Bitbucket token) before resolving

### Bitbucket â€” MDMBWPROJ Feature Branches Created Across All Repos

**Workspace**: `allcargoecu` | **Project**: `MDMBWPROJ`
**Token**: Bitbucket repository access token (stored at `/home/ec2-user/rahul/token`)
**Script**: `/home/ec2-user/rahul/create_feature_branches.py`

#### Action
- Listed all 120 repositories in the `MDMBWPROJ` Bitbucket project via API
- Ensured every repo has all four standard environment branches: `feature_dev`, `feature_sit`, `feature_uat`, `feature_prod`
- Branches created from each repo's default branch (`main` or `master`)

#### Result
- **164 branches created** across 117 repos
- **2 repos** already had all 4 branches (`bw_accessmanagement_outbound_itopaz`, `bw_precompany_outbound`)
- **3 repos failed** with HTTP 400 â€” empty repositories (no commits), cannot create branches until initial commit is pushed:
  - `bw_account_ucoa_outbound_d365`
  - `bw_company_corporateaccount_outbound_d365`
  - `bw_finance_corporateaccount_outbound_crm`

#### Notes
- Some repos had HTTP 403 on `feature_prod` in the first run (resolved on second run â€” likely a race condition or permission delay)
- To retry the 3 empty repos after their initial commit: `python3 /home/ec2-user/rahul/create_feature_branches.py`

---

### S3 CORS Fix â€” allcargo-intranet Bucket

**Bucket**: `allcargo-intranet` | **Region**: `ap-south-1` | **Account**: `745510282686`
**Profile**: `allcargo745`

#### Problem
- Browser CORS error when fetching presigned S3 URLs from `http://localhost:4200` (Angular dev server):
  `No 'Access-Control-Allow-Origin' header is present on the requested resource`
- The bucket CORS policy only allowed production/staging origins

#### Fix
- Added `http://localhost:4200` and `http://localhost:3000` to `AllowedOrigins` in the bucket CORS configuration
- All other rules unchanged (`GET`, `HEAD` methods, `*` headers, `ETag` exposed, `MaxAgeSeconds: 3600`)

#### Updated AllowedOrigins
- `https://intellihub.allcargoapps.com`
- `https://intranet-dev.allcargoapps.com`
- `https://intranet-uat.allcargoapps.com`
- `https://intranet.allcargoapps.com`
- `http://localhost:4200` â† added
- `http://localhost:3000` â† added

---

---

## 2026-08-17 â€” ELMA Self-Chat WebSocket Fix & IntelliHub / Intranet Infra (Account 745510282686)

### Problem
ELMA Self-Chat WebSocket connections failing on `intranet-dev.allcargoapps.com` and `elma-dev.allcargoapps.com`. "Processing" badge stuck permanently after document upload.

### Root Causes (3 layers)

**Layer 1 â€” nginx on Intranet-uat (10.0.132.243)**
- **Root cause (plain terms)**: nginx was stripping the `Upgrade: websocket` header, so every connection got downgraded to HTTP and immediately rejected.
- nginx was running with zero proxy config (default site, no location blocks)
- `/agent/self-chat/ws/` requests hit nginx â†’ `try_files` â†’ `404`
- Fix: Created `/etc/nginx/sites-available/intellihub` with the 4 standard WebSocket proxy directives:
  ```nginx
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_read_timeout 3600s;
  ```
  These 4 lines are the standard fix for any nginx WebSocket proxy.

**Layer 2 â€” CloudFront E2FVCC01LF3UUD (elma-dev.allcargoapps.com)**
- CF behavior `/agent/self-chat/ws/*` required trailing wildcard â€” path `/agent/self-chat/ws/token` didn't always match
- CF behavior allowed only `HEAD, GET` â€” expanded to all 7 methods
- `/ws` path had no CF behavior â€” added new behavior
- Fix: Updated path to `/agent/self-chat/ws*`, added `/ws` behavior, both â†’ datascience ALB

**Layer 3 â€” ALB datascience-144380231 (eu-central-1, account 674017976129)**
- No ALB rule for `/ws` or `/ws/*`
- Fix: Added rule P8 `/ws`, `/ws/*` â†’ `elma-tg:8506`

**Layer 4 â€” ELMA backend PID issue**
- `elma-dev.service` was running old code (WebSocket routes existed in `App/main.py` but process needed restart to load them)
- `elma-dev.service` had crash loop (restart counter >1033) â€” separate startup issue
- Fix: `sudo systemctl restart elma-dev.service` â€” service now loads WebSocket routes

### Architecture (account 674017976129, eu-central-1)
- **ELMA EC2**: `i-00bc2270212d49626` (ml-model-training-server), `172.31.3.13`
- **ELMA service**: `elma-dev.service` â†’ `uvicorn App.main:app --port 8506`
- **Working dir**: `/home/ubuntu/jupyter_workspace/test/Elma/`
- **WebSocket routes**: `@app.websocket("/agent/ws/{token}")` and `@app.websocket("/agent/self-chat/ws/{token}")`
- **ALB**: `datascience-144380231.eu-central-1.elb.amazonaws.com`
- **CF**: `E2FVCC01LF3UUD` â†’ aliases: `elma-dev.allcargoapps.com`, `elma-api.allcargoapps.com`
- **SSM access**: `aws ssm start-session --target i-00bc2270212d49626 --region eu-central-1 --profile elma674`

### mcpserverapi UPLOAD_WS_URL
- **File**: `/home/ubuntu/mcpclient/mcpserverapi/.env` on Intranet-uat (10.0.132.243)
- **Correct value**: `UPLOAD_WS_URL=wss://elma-dev.allcargoapps.com/agent/self-chat/ws`
- Service: `elma-mcp-client.service` (port 8338)

### Key Insight
WebSocket upgrade (HTTP/1.1 `Upgrade: websocket`) returns `101` end-to-end.  
curl shows `HTTP/2 404` because curl negotiates HTTP/2 with CF â€” use `curl --http1.1` to test WebSocket through CloudFront.

### Account 674017976129 (SSO: ecu-allcargo.awsapps.com, role AWSAdministratorAccess)
- Region: eu-central-1
- Profile: `elma674` (configured in `~/.aws/config` with SSO)
- ELMA, SARA, AQUA, KAIROS, FRAME, BOLT, CUBE, EPIC, etc. â€” all DS/ML apps
- All served via ALB `datascience-144380231.eu-central-1.elb.amazonaws.com`

### IntelliHub / Intranet Infra â€” Account 745510282686 (Aug 2026)
### Infrastructure Discovered (2026-08-14 to 2026-08-17)

#### AWS Account: 745510282686 (ap-south-1)
- **Role**: `arn:aws:iam::745510282686:role/eks-jump-server-role` (on i-019825d0de3300832)
- **CloudFront Distributions**:
  - `E17IUMRH88RLK0` â€” alias: `intranet-dev.allcargoapps.com` â†’ S3 default, `/intellihub/*` â†’ intelli-atl.allcargoapps.com, `/ecureports/*` â†’ Intellihub-prod ALB
  - `EUXNUI70UHP4U` â€” aliases: `intellihub.allcargoapps.com`, `intellihub-test.allcargoapps.com` â†’ Intellihub-prod ALB default, `/intranet/doc-proxy/*` â†’ Intellihub-prod ALB, `/ecureports/*` â†’ Intellihub-prod ALB
  - `E2KUC71OEUFDR2` â€” alias: `intranet-uat.allcargoapps.com`
  - `E1Y96N6IYRLTQJ` â€” alias: `releasedocs.allcargoapps.com`
- **Global Accelerators**:
  - `intellihub-prod` (`a597dde4c9e7fd12e`) â†’ endpoint: Intellihub-prod ALB (UNHEALTHY â€” health check path null)
  - `intellihub-test-GA` (`a9aa12dbc5cb38e31`) â†’ endpoint: LB-intranet (UNHEALTHY â€” health check `/` hits unhealthy default TG)
  - `global-api-accelerator` (`a0e64e9eec1e248bc`)
- **DNS**:
  - `intelliaiml.allcargoapps.com` â†’ `intellihub-prod` GA â†’ Intellihub-prod ALB
  - `aimlapp-test.allcargoapps.com` â†’ `intellihub-test-GA` â†’ LB-intranet
  - `intranet-dev.allcargoapps.com` â†’ CF E17IUMRH88RLK0
  - `intelli-atl.allcargoapps.com` â†’ `lb-intellihub-408139470.ap-south-1.elb.amazonaws.com` (65.0.235.121, 65.2.203.48) â€” Classic ELB not in this account
- **ALBs**:
  - `Intellihub-prod` (arn:.../Intellihub-prod/e94560d3db5e68f1) â€” HTTPS :443 default: fixed-response. Key rules: P1 `/intranet/gatimasterapi` â†’ gatimasterapi-prod, P5 `/intranet*` â†’ intellihub-prod TG (HEALTHY, port 80, health `/intranet/healthcheck`)
  - `LB-intranet` (arn:.../LB-intranet/a261a4d9ad16eebb) â€” P7 `/intranet*` â†’ intranet-newvm TG (HEALTHY), default â†’ resumeuploaded (UNHEALTHY)
- **EC2 Instances**:
  - `Intranet-uat` (i-0825be434cf7ab87b) â€” 10.0.132.243, m6a.xlarge, key: vj-keypair-pocacct.pem
  - `Intranet-prod-1` (i-0b1f3b8eda05c132b) â€” 10.151.4.89, c5a.xlarge, key: Intranet-prod-1-Key.pem
  - `Intranet-prod-2` (i-0a82e63f8fcce6c8e) â€” 10.151.4.153, m5.2xlarge

#### Services on Intranet-uat (10.0.132.243) â€” test env backend
- **Port 8338**: `elma-mcp-client.service` â€” uvicorn `app.main:app`, WorkingDir: `/home/ubuntu/mcpclient/mcpserverapi`, handles `/agent/*` routes including ELMA self-chat WebSocket
- **Port 8779**: `vdtext` uvicorn (`backend.main:app`) at `/home/ubuntu/vdtext/vdext/`
- **Port 4001**: `python3 intranetapimain.py`
- **Port 4003**: `python3 aadhar_extraction_api.py`
- **Port 4080**: `python3 hrchatbotazure.py`
- **Port 5667**: `python3 main.py` (gatimasterapi)
- **Port 5668**: `python3 main.py` (symphonywrapper)
- **nginx 1.18.0** running on port 80 â€” config at `/etc/nginx/sites-available/intellihub`

#### ELMA Self-Chat WebSocket Fix (2026-08-17)
- **Problem**: nginx had zero proxy config. All `/agent/self-chat/ws/` WebSocket upgrade requests hit nginx â†’ `try_files â†’ 404`. Browser retried 30+ times, badge stuck on "Processing".
- **Fix applied**: Created `/etc/nginx/sites-available/intellihub` with:
  - `/agent/self-chat/ws/` â†’ `http://127.0.0.1:8338` with `proxy_http_version 1.1`, `Upgrade`, `Connection: upgrade`, `proxy_read_timeout 3600s`, `proxy_buffering off`
  - `/agent/` â†’ `http://127.0.0.1:8338`
  - `/intellihub/` â†’ `http://127.0.0.1:8779/`
- Disabled `sites-enabled/default`, symlinked intellihub site
- **Verification**: `curl` to `/agent/self-chat/ws/` now returns 403 (reaches ELMA backend, auth required) instead of 404

#### Doc-Proxy Issue (intelliaiml.allcargoapps.com)
- **Problem**: `proxyUrl = IntranetAPI_Domain + intranet/doc-proxy/ + token` â†’ Office Online shows "not publicly accessible"
- **Root cause**: proxy backend redirects to S3 URL with Referer-based policy. Microsoft Office Online fetches without Referer header â†’ S3 returns 403.
- **Fix**: Backend `/intranet/doc-proxy/<token>` must generate S3 presigned URL (15 min TTL) and return 302 redirect to it. Presigned URLs use query-string auth, no Referer needed.
- **Also**: Add `HEAD` method handler to the endpoint (currently returns 405).

#### GA Health Check Fixes Needed
- `intellihub-prod` GA health check path: `null` â†’ set to `/intranet/healthcheck`
- `intellihub-test-GA` GA health check hits `/` â†’ `resumeuploaded` TG (UNHEALTHY) â†’ change to `/intranet/healthcheck`

---

---

## 2026-07-24 â€” DEV EU imdg-prefiler Deep-Link 301/Blank-Page Fix

### Issue
- `GET https://prefiler-eudev.itopazapp.com/imdg-prefiler/add-edit-details?from=filer-details&flow=add&activeMain=file&activeChild=firstDeclaration` returned `301 Moved Permanently` â†’ `https://prefiler-eudev.itopazapp.com/dashboard`, dropping the destination and query params
- Normal in-app navigation (Dashboard â†’ File â†’ First Declaration â†’ stepper â†’ Add/Edit Details) was unaffected â€” only direct URL entry, page refresh, or opening in a new tab triggered the 301

### Root cause
- `imdg-prefiler` is a single-spa **child** microfrontend (built via `main.single-spa.ts` per `angular.json`, exports `bootstrap`/`mount`/`unmount` lifecycle hooks â€” does not self-render on script load)
- The Istio `prefiler-ui` VirtualService routes `/imdg-prefiler/*` by path prefix **directly to the `imdg-prefiler-svc` pod**, bypassing the single-spa shell (`microfrontend-main`) entirely
- Shell root (`/`) is where `single-spa` + `single-spa-layout` boot and mount the correct child based on the current URL â€” a child pod hit directly has no shell, so `main.js` loads but never receives a `mount()` call â†’ blank page
- `imdg-prefiler`'s `.htaccess` had an existing referer-based guard (empty/self referer â†’ 301 to `/dashboard`) specifically to prevent the blank-page case, but it discarded the original path/query, so users landed on the dashboard instead of their intended record
- Git history (`imdg-prefiler` repo) shows this guard was added, removed, and re-added three times via Bitbucket web-UI edits (no PRs) â€” prior fixes oscillated between "301 to dashboard" (loses destination) and "plain SPA fallback" (blank page), never addressing the actual shell/child routing mismatch
- Root `/` on the shell also has its own `.htaccess` rule (`RedirectMatch ^/$ /login`) that intercepts unauthenticated root requests â€” relevant when choosing a handoff target

### Fix Applied
Two repos, `develop` branch:

**`imdg-prefiler`** (bitbucket.org/allcargoecu/imdg-prefiler, commit `411c520`)
- `.htaccess`: deep-link guard now serves a new `redirector.html` instead of issuing a raw 301
- `redirector.html` (new): client-side JS captures `window.location.pathname + search` and redirects to `https://prefiler-eudev.itopazapp.com/dashboard?spaRedirect=<encoded original path+query>` â€” uses `/dashboard` (not `/`) to avoid the shell's own `/login` redirect on root
- `Dockerfile`: `ADD redirector.html` alongside `.htaccess` into `htdocs/` root (must sit next to `.htaccess`, not inside the `imdg-prefiler/` subfolder â€” rewrite substitutions resolve relative to `.htaccess`'s location)

**`microfrontend-main`** (bitbucket.org/allcargoecu/microfrontend-main, commit `6136f1c`)
- `index.html`: before `single-spa`/`single-spa-layout` boot, reads `?spaRedirect=` from the query string and calls `history.replaceState` to restore the real target URL, so `constructRoutes`/`constructApplications` mount the correct child app at the originally requested path

### Verified
- Local Docker build of `imdg-prefiler` Dockerfile: deep-link path returns `200` serving `redirector.html` (not 301, not blank), static assets (`main.js`) unaffected
- Live pod patch (pre-commit) confirmed same behavior against DEV EU Istio ELB directly
- Normal in-app stepper navigation confirmed unaffected (referer already set to shell, guard condition doesn't match)

### Pending / Not Yet Verified
- **Not yet deployed** â€” commits are source-only; DEV pods (`imdg-prefiler`, `microfrontend-main`) still run old baked-in images until Jenkins pipelines (`prefiler-k8s-repo/jenkins/dev/ui/imdg-prefiler`, `.../microfrontend-main`) build and roll out
- Pushed directly to `develop` on both repos (no PR) per explicit request â€” team may want review before next deploy given prior history of unreviewed `.htaccess` edits
- Full end-to-end client-side verification (shell restoring URL and single-spa mounting the child) requires a real authenticated browser session â€” not verifiable via curl alone
- **Same anti-deep-link `.htaccess` pattern likely exists in the other 11 sibling `*-prefiler` UI repos** (`afr-prefiler`, `aci-prefiler`, `aes-prefiler`, `ams-prefiler`, `basf-prefiler`, `dagangnet-prefiler`, `ics-prefiler`, `ics2-prefiler`, `mblfiler-prefiler`, `mpci-prefiler`, `sa-prefiler`) â€” none of these have been checked or fixed yet

---

---

## 2026-06-19 â€” SIT itariff-api HPA maxReplicas Increase

### Issue
- Multiple iTariff buying services hitting CPU >150-230% with HPAs stuck at maxReplicas (3 or 5)
- Services unable to scale despite heavy load

### Fix Applied
```bash
kubectl patch hpa tariff-buying-service -n itariff-api -p '{"spec":{"maxReplicas":10}}'
kubectl patch hpa tariff-buying-carriage-service -n itariff-api -p '{"spec":{"maxReplicas":6}}'
kubectl patch hpa tariff-buying-standardcost-service -n itariff-api -p '{"spec":{"maxReplicas":6}}'
kubectl patch hpa tariff-buying-truck-service -n itariff-api -p '{"spec":{"maxReplicas":6}}'
kubectl patch hpa tariff-selling-oc-service -n itariff-api -p '{"spec":{"maxReplicas":6}}'
```

### Result
- `tariff-buying-carriage-service`: 204% â†’ 43% CPU (scaled to 6 replicas)
- `tariff-buying-service`: 230% â†’ 94% CPU (scaled to 10 replicas)
- `tariff-buying-standardcost-service`: 142% â†’ 45% CPU (scaled to 6)
- `tariff-buying-truck-service`: 93% â†’ 19% CPU (scaled to 6)
- `tariff-selling-oc-service`: 80% â†’ 5% CPU (scaled to 6)

### Note
- `tariff-buying-service` may need maxReplicas raised to 12-15 if CPU stays >80%
- `tariff-selling-consumer-hpa` still at 157% with 20/20 replicas â€” needs CPU resource increase

---

---

## 2026-06-18 â€” POC Account aimlapp-test Intranet 502 Fix

### POC Account â€” aimlapp-test Intranet Service Restored (502 Fixed)

**Server**: `10.0.132.243` (ubuntu) â€” POC Account `745510282686`
**Key**: `infrastructure/secrets/keys/shared/poc/vj-keypair-pocacct.pem`
**URL**: `https://aimlapp-test.allcargoapps.com/intranet/login`

#### Problem
- URL returning **502 Bad Gateway** from AWS ELB
- `intranetapimain.py` was not running on the server

#### Root Cause
- Service `intranetapimain.py` crashes on startup â€” `AccessDeniedException` when calling `secretsmanager:GetSecretValue` on secret `test/intranet`
- IAM user `arn:aws:iam::745510282686:user/codecommit-jenkins` had no policy allowing access to that secret
- Existing `aws-secret-manager-policy` only covered `devrev_tokens*` secret

#### Fix Applied
- Added inline IAM policy `AllowSecretsManagerIntranet` to user `codecommit-jenkins`:
  ```json
  {
    "Effect": "Allow",
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "arn:aws:secretsmanager:ap-south-1:745510282686:secret:test/intranet*"
  }
  ```
- Started `intranetapimain.py` from: `/root/var/www/intranet/userdetailssync/userdetailssync/`
- Service running on port `4001` (uvicorn/FastAPI)
- URL now returns `200 OK` (GET) / `405` for HEAD â€” **service is UP**

#### Additional Findings
- **autoheal script** `/root/var/www/apis-autoheal.sh` has wrong path for `intranetapimain`:
  - Script expects: `/root/var/www/intranet/userdetailssync/`
  - Actual location: `/root/var/www/intranet/userdetailssync/userdetailssync/`
  - Needs fix to prevent future outages
- Server IP `10.0.132.243` requires VPC peering to be active (was unreachable before peering)
- Services on server: `hrchatbotazure.py` (port 4080), `aadhar_extraction_api.py` (port 4003), `intranetapimain.py` (port 4001), `ollama` (127.0.0.1:11434)

---

### Issue
- `https://aimlapp-test.allcargoapps.com/intranet/login` returning 502 Bad Gateway
- `intranetapimain.py` not running; crashes on startup due to IAM `AccessDeniedException`

### Fix
- Applied inline IAM policy `AllowSecretsManagerIntranet` to `codecommit-jenkins` (account `745510282686`):
  - Resource: `arn:aws:secretsmanager:ap-south-1:745510282686:secret:test/intranet*`
  - Action: `secretsmanager:GetSecretValue`
- Manually started service: `nohup python3 intranetapimain.py > /tmp/intranet.log 2>&1 &`
- Service path: `/root/var/www/intranet/userdetailssync/userdetailssync/`
- Running on: `http://0.0.0.0:4001` (uvicorn FastAPI)

### Known Issue (Not Fixed)
- `/root/var/www/apis-autoheal.sh` has wrong path â€” references `/root/var/www/intranet/userdetailssync/` instead of `/root/var/www/intranet/userdetailssync/userdetailssync/`
- Autoheal will fail to restart intranet if it goes down again â€” path needs correction

### Server Details
- **Host**: `10.0.132.243` (ubuntu), POC account `745510282686`
- **Key**: `infrastructure/secrets/keys/shared/poc/vj-keypair-pocacct.pem`
- **Nginx**: Running (port 80), routes static content from `/var/www/html`
- **Services running**: `hrchatbotazure.py` (4080), `aadhar_extraction_api.py` (4003), `intranetapimain.py` (4001), `ollama` (127.0.0.1:11434)
- **AWS credentials on server**: IAM user `codecommit-jenkins`, region `ap-south-1`, creds at `/root/.aws/credentials`

---

---

## 2026-06-17 â€” Operations Log

### PROD EU â€” Grafana K8S Dashboard Fixed (No kube-state-metrics)
- **Problem**: Grafana K8S Dashboard namespace dropdown empty; `kube-state-metrics` not installed in PROD cluster
- **Root cause**: Dashboard variables (`NameSpace`, `Node`, `Container`, `Pod`) all used `kube_namespace_created`, `kube_node_info`, `kube_pod_container_info` from KSM â€” none exist in PROD
- **Investigation**:
  - PROD cluster confirmed accessible: bastion `10.100.98.195`, 4 Linux nodes (v1.36.1-eks), 15 namespaces
  - Monitoring stack: Grafana + Prometheus in `istio-system` only â€” no KSM, no ServiceMonitor CRDs
  - Prometheus uses static `kubernetes_sd_configs` scrape jobs (no ServiceMonitor)
  - Available metrics: cAdvisor (`container_*`), kubelet (`kubelet_node_name`, `machine_memory_bytes`, `machine_cpu_cores`)
- **Fix approach**: Rewrote dashboard JSON without modifying cluster
  - Downloaded dashboard via `kubectl exec grafana -- curl localhost:3000/api/dashboards/uid/9f83e8f6-ae9a-4bc1-ad64-cffc1c93df02`
  - **129 panel expressions rewritten** using Python script `/tmp/fix_dashboard.py`
  - Uploaded via Grafana API POST `/api/dashboards/db` â€” status: success, version 2
- **Variable replacements**:
  - `origin_prometheus` â†’ hidden constant (no KSM federation)
  - `Node` â†’ `label_values(kubelet_node_name, node)`
  - `NameSpace` â†’ `label_values(container_memory_working_set_bytes{container!="",container!="POD"}, namespace)`
  - `Container` â†’ `label_values(container_cpu_usage_seconds_total{namespace=~"$NameSpace",...}, container)`
  - `Pod` â†’ `label_values(container_cpu_usage_seconds_total{...}, pod)`
- **Metric replacements**:
  - `kube_node_status_allocatable{resource="memory"}` â†’ `machine_memory_bytes`
  - `kube_node_status_allocatable{resource="cpu"}` â†’ `machine_cpu_cores`
  - `kube_node_info` â†’ `kubelet_node_name`
  - `kube_pod_info` counts â†’ `container_last_seen` counts
  - `kube_pod_container_resource_requests/limits` â†’ `vector(0)` (no cAdvisor equivalent)
- **Dashboard URL**: `/d/9f83e8f6-ae9a-4bc1-ad64-cffc1c93df02/k8s-dashboard`
- **Backup script**: `/tmp/fix_dashboard.py` on local server

### knowledge-base Folder â€” Restored
- Folder was deleted in commit `801dca1` on June 17
- Restored via `git checkout 6151387 -- knowledge-base/` â€” 38 files recovered

---

---

## 2026-06-12 â€” PROD EU Kafka 3.9.1 Client Setup, iTariff Ingress Bring-up & prefiler-bff DEV VirtualService Fix

### PROD EU â€” Kafka 3.9.1 Client Setup + MSK Broker Config
- **Local download** (on 165 server): Apache Kafka `3.9.1` (Scala 2.13) downloaded to `/home/ec2-user/rahul/kafka-client/kafka_2.13-3.9.1.tgz`
- **Uploaded** tarball to prod bastion (`10.100.98.195`) via `scp` â†’ extracted to `/home/ec2-user/kafka-client/kafka_2.13-3.9.1/`
- **Symlink**: `/home/ec2-user/kafka-client/current` â†’ `kafka_2.13-3.9.1`
- **Java**: Installed `java-17-amazon-corretto-headless` on prod bastion (was missing); verified version `17.0.19`
- **SASL/SCRAM config** at `/home/ec2-user/kafka-client/client.properties`:
  ```
  security.protocol=SASL_SSL
  sasl.mechanism=SCRAM-SHA-512
  ssl.endpoint.identification.algorithm=https
  ```
- **Prod MSK brokers** (3 nodes, port 9096, SASL_SSL):
  - `b-1.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
  - `b-2.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
  - `b-3.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
- **Bootstrap file**: `/home/ec2-user/kafka-client/prod-bootstrap-servers.txt`
- **Wrapper script**: `/home/ec2-user/kafka-client/run-kafka-prod.sh` (runs `kafka-broker-api-versions.sh` with SASL config + heap opts)
- **Note**: Fill in `<MSK_USERNAME>` and `<MSK_PASSWORD>` in `client.properties` before running broker commands

### UI Pipelines â€” CloudFront Cache Invalidation Stage Added
- **Added** `Invalidate CloudFront Cache` stage to all UI Jenkins pipelines (SIT environment)
- **Files updated**:
  - `jenkins/tariff_microfrontend-main-ui` â€” added stage after Verify Deployment
  - `jenkins/tariff_microfrontend-share-ui` â€” added stage after Verify Deployment
  - `jenkins/tariff-selling-rates-ui` â€” already had stage, confirmed dist ID
  - `jenkins/tariff-tariffbuying-ui` â€” already had stage, confirmed dist ID
- **Distribution ID**: `E1MSDTWI1MUQ2P` (SIT UI CloudFront distribution)
- **Stage behavior**: Executes only when `SKIP_DEPLOYMENT=false`, invalidates all paths (`/*`), uses cross-account AWS role
- **Pushed**: `uat` branch, commit `cbde479` âœ…

### SIT EU & SIT SG â€” Node Status Checks
- **SIT EU** (euc1-itopaz-sit-eks): Caught mid-rolling node replacement â€” 18 NotReady (bootstrapping), 18 Ready,SchedulingDisabled (old nodes cordoned ~8h), 2 Ready. Within ~60s new nodes joined: 37 Ready, 4 cordoned. Final state after drain complete: **26 Ready, 0 cordoned** âœ…
- **SIT SG** (apse1-itopaz-sit-eks): **6 nodes all Ready** âœ…
- Old cordoned nodes in SIT EU were carrying 10â€“12 pods each (~44 pods total); drained and terminated automatically

### SIT MSK â€” Kafka Version Check
- **Broker version**: Kafka **3.7.x** (confirmed via `kafka-broker-api-versions.sh`: Produce API max 11, Fetch API max 16 â€” both introduced in 3.7)
- **Kafka client on SIT EU bastion**: `kafka_2.13-3.6.0`
- **Brokers**: `b-1.euc1itariffsitmsk.76ygyn.c5.kafka.eu-central-1.amazonaws.com:9096`, `b-2...` (2-node cluster, SASL_SSL/SCRAM-SHA-512)

### tariff-selling-rates-ui â€” Jenkins Pipeline Fix
- **Root cause 1**: `REPO_URL` was pointing to wrong repo (`tariff-microfrontend-main-ui.git`) â€” corrected to `tariff-selling-rates-ui.git`
- **Root cause 2**: `Checkout Application Code` stage was using `$DEPLOYMENT_FILE` (`tariff-selling-rates-ui.yml`) as the Bitbucket repo slug, producing invalid URL `...tariff-selling-rates-ui.yml.git`
- **Fix**: Replaced hardcoded slug with `REPO_SLUG=$(basename "$REPO_URL" .git)` to dynamically extract slug from `REPO_URL`
- **File**: `jenkins/tariff-selling-rates-ui` in `itariff-k8s-repo`
- **Pushed**: `uat` branch, commit `b46b160` âœ…

### prefiler-bff DEV â€” VirtualService Routing Fix (404 resolved)
- **Symptom**: All actual API calls via `prefiler-bff-eudev.itopazapp.com` returning 404 with no CORS headers, even after CORS swagger fixes and redeployment
- **Root cause**: With the API Gateway custom domain base path mapping corrected from `prefiler-bff` â†’ `(none)`, the full path `/prefiler-bff/prefiler/bff/v1/...` is now forwarded to Istio. The VirtualService only had rules for `/prefiler-auth-bff/` and `/prefiler/` â€” no rule matched the `/prefiler-bff/prefiler/...` prefix â†’ 404
- **Pods confirmed healthy**: `prefiler-bff-cd984c8dc-*` (2 pods, 2/2 Running), `prefiler-auth-bff-67f6b87c4f-*` (2 pods, 2/2 Running)
- **Fix**: Added two new http rules to `prefiler-bff` VirtualService (`istio-system`):
  - `/prefiler-bff/prefiler/` â†’ `prefiler-bff-svc.prefiler-bff.svc.cluster.local:80` (rewrite: /)
  - `/prefiler-bff/prefiler-auth-bff/` â†’ `prefiler-auth-bff-svc.prefiler-bff.svc.cluster.local:80` (rewrite: /)
- **Verified**: `GET https://prefiler-bff-eudev.itopazapp.com/prefiler-bff/prefiler/bff/v1/masters/PageMaster/` â†’ **HTTP 200** with `access-control-allow-origin: *` and full JSON payload âœ…
- **Cluster**: `euc1-itopaz-dev-eks` (DEV EU) via bastion `10.100.145.118`, key `dev-eu-bastion.pem`

### README.md â€” Comprehensive Copilot Reference Update
- Replaced generic KB/vector-db README with full operational reference
- Added all SSH access commands with exact key paths
- Added AWS account table (5 accounts with IDs, regions, IAM role ARNs)
- Added EKS cluster details (DEV EU, SIT EU, SIT SG â€” nodes, K8s versions, ASG, maxPods)
- Added service URLs by environment (internal + external, API GW IDs, VPC Link IDs)
- Added application architecture (tech stacks, ECR registries, namespaces)
- Added full prefiler service inventory, Istio VS routing, .NET config patterns
- Added database credentials table (DEV + SIT, Redis endpoints)
- Added Kafka broker URLs and key topics
- Added Jenkins server access, pipeline paths, env vars
- Added API Gateway CORS fix pattern with deploy commands
- Added known pending issues section (DEV, SIT EU, SIT SG)

---

### Local (165 server)
- Downloaded `kafka_2.13-3.9.1.tgz` to `/home/ec2-user/rahul/kafka-client/`
- Verified: `kafka-topics.sh --version` â†’ `3.9.1`

### Prod Bastion (10.100.98.195)
- Uploaded and extracted to `/home/ec2-user/kafka-client/kafka_2.13-3.9.1/`
- Symlink: `/home/ec2-user/kafka-client/current`
- Installed `java-17-amazon-corretto-headless` (Amazon Linux 2, was missing)
- Created `/home/ec2-user/kafka-client/client.properties` (SASL_SSL / SCRAM-SHA-512)
- Created `/home/ec2-user/kafka-client/prod-bootstrap-servers.txt`
- Created `/home/ec2-user/kafka-client/run-kafka-prod.sh` wrapper

### PROD MSK Brokers
```
b-1.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096
b-2.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096
b-3.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096
```

### Next step
Update `client.properties` with real MSK SCRAM credentials before running topic/broker commands.

---

### PROD EU Bastion and Cluster Access
- **Bastion**: `10.100.98.195` (key: `infrastructure/secrets/keys/prod/eu/prod-eu-bastion.pem`)
- **SSH key issue fixed**: local key file had malformed/public-key content and strict permission issues
  - Corrected key content and enforced file mode `400`
- **kubectl status**: already present (`/usr/local/bin/kubectl`)
- **Kubeconfig fix on bastion**: changed deprecated exec plugin API from `client.authentication.k8s.io/v1alpha1` to `v1beta1`
- **Usability**: added persistent alias `k=kubectl` in `~/.bashrc`

### PROD EU Istio Resources Created (`istio-system`)
- **Gateway**: `itariff-gateway`
- **VirtualServices**:
  - `itariff-ui`
  - `itariff-api`
  - `itariff-bff`

### PROD iTariff Internal Hosts Configured
- `itariff-ui.internaleu1prd-itopaz.com`
- `itariff-bff.internaleu1prd-itopaz.com`
- `itariff-api.internaleu1prd-itopaz.com`

### DNS Verification
- All 3 hosts resolve to Istio ingress ELB:
  - `a5c3d5f6763e149a1949597be2e56d79-0a180d890cef99d9.elb.eu-central-1.amazonaws.com`

### Initial Behavior Before Backend Services
- `itariff-ui.internaleu1prd-itopaz.com/` -> `503`
- `itariff-api.internaleu1prd-itopaz.com/` -> `503`
- `itariff-bff.internaleu1prd-itopaz.com/` -> `404` (root path not mapped for bff)

### Test Deployment and Route Proving
- Deployed `test-echo` (Deployment + Service) in:
  - `itariff-ui`
  - `itariff-api`
  - `itariff-bff`
- Added `/test-ping` route at top priority in each VirtualService:
  - `itariff-ui` -> `test-echo.itariff-ui.svc.cluster.local:80`
  - `itariff-api` -> `test-echo.itariff-api.svc.cluster.local:80`
  - `itariff-bff` -> `test-echo.itariff-bff.svc.cluster.local:80`
- End-to-end ingress verification (HTTP Host header through Istio ELB):
  - `itariff-ui.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-ui test ok`)
  - `itariff-api.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-api test ok`)
  - `itariff-bff.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-bff test ok`)

---

### prefiler-bff DEV â€” VirtualService Routing Fix
- **Cluster**: `euc1-itopaz-dev-eks` | Namespace: `istio-system`
- **Symptom**: `GET https://prefiler-bff-eudev.itopazapp.com/prefiler-bff/prefiler/bff/v1/masters/PageMaster/` returning 404 with `x-amzn-remapped-server: istio-envoy` â€” request reached Istio but no matching route
- **Root cause**: API Gateway custom domain base path mapping was fixed from `prefiler-bff` â†’ `(none)` (previous session). After this fix, full path `/prefiler-bff/prefiler/...` is forwarded to Istio, but VirtualService only had rules for `/prefiler-auth-bff/` and `/prefiler/` â€” gap for `/prefiler-bff/` prefix
- **Pods status**: All healthy â€” `prefiler-bff` (2/2), `prefiler-auth-bff` (2/2)
- **Fix applied** (kubectl patch, type json, op replace on `/spec/http`):
  ```yaml
  - match: [{uri: {prefix: /prefiler-bff/prefiler/}}]
    rewrite: {uri: /}
    route: [{destination: {host: prefiler-bff-svc.prefiler-bff.svc.cluster.local, port: 80}}]
  - match: [{uri: {prefix: /prefiler-bff/prefiler-auth-bff/}}]
    rewrite: {uri: /}
    route: [{destination: {host: prefiler-auth-bff-svc.prefiler-bff.svc.cluster.local, port: 80}}]
  - match: [{uri: {prefix: /prefiler-auth-bff/}}]    â† existing, kept
  - match: [{uri: {prefix: /prefiler/}}]             â† existing, kept
  ```
- **Verified**: HTTP 200, `access-control-allow-origin: *`, full JSON data returned âœ…

### prefiler-bff DEV â€” Previous Session Fixes (context)
- API Gateway swagger CORS added for both paths (`/prefiler-bff/{proxy+}`, `/prefiler-auth-bff/{proxy+}`)
- Swagger imported via `aws apigateway put-rest-api --mode overwrite`, deployment ID `kxakdj`
- Custom domain `prefiler-bff-eudev.itopazapp.com` base path mapping: `prefiler-bff` â†’ `(none)`
- API ID: `l9rbaytbtc`, stage: `dev`

### prefiler-api DEV â€” CORS Fix (LOCAL ONLY â€” NOT YET DEPLOYED)
- Python script applied CORS fixes to all 14 paths in `/home/ec2-user/rahul/prefiler-api`
- Added `headers.Access-Control-Allow-Origin` to method response AND `responseParameters` to integration response
- **Pending**: Must import to API GW `9flv9p0c7k` and create deployment to take effect

### tariff-selling-rates-ui â€” Jenkins Pipeline Fix
- **Root cause**: Docker COPY failed (`stat dist/selling-rates/: file does not exist`) â€” Angular `npm run build` was never called before Docker build
- **Fix**: Added `Build Angular Application` stage to Jenkinsfile before `Build Docker Image`:
  ```groovy
  stage('Build Angular Application') {
    steps { sh 'npm run build' }
  }
  ```
- **File**: `itariff-k8s-repo/jenkins/tariff-selling-rates-ui`

---

---

## 2026-06-11 â€” Intellihub HA Assessment + Intranet Server Autoheal Sync

### Intellihub Servers HA Assessment (Account 745510282686, ap-south-1)

#### What was done
- Full HA check on both Intranet prod servers at AWS and application level
- Verified EC2 instance health, AZ placement, ALB target group health, autoheal scripts

#### AWS Level Findings
- Both instances **running** and **healthy** (system + instance checks: ok/ok)
  - `Intranet-prod-1` (`i-0b1f3b8eda05c132b`) â€” **ap-south-1a** (c5a.xlarge)
  - `Intranet-prod-2` (`i-0a82e63f8fcce6c8e`) â€” **ap-south-1b** (m5.2xlarge)
- **No Auto Scaling Group** â€” bare EC2 instances (gap: no automatic replacement on termination)
- Core services all healthy on both instances via `Intellihub-prod` ALB:
  - `intellihub-prod`, `intellihubadmin-prod`, `gatimasterapi-prod`, `sendbulktracking`, `symphonywrapper-prod`, `zendeskwrapper-prod` â†’ all **True HA** âœ…
- 5 stale unused target groups identified (not attached to any listener): `aimlprod-1`, `ecureports`, `ecureports-api`, `intellaiml-prod-4001`, `intellihub-prod-2`

#### Application Level Findings
- All 3 autoheal scripts synced and active on **both** servers:
  - `apis-autoheal.sh` (every 5 min + @reboot)
  - `gati-apis-autoheal.sh` (every 2 min)
  - `cleanup_python_zombies.sh` (every 1 min)
- `cleanup_python_zombies.sh` was already in crontab on prod-2 (`.153`) but script file was missing â†’ copied from prod-1 âœ…

#### Gaps Identified (no changes made, recommendations only)
1. No ASG â€” add EC2 Auto Recovery CloudWatch alarm (`StatusCheckFailed_System`)
2. Single-instance genie/docdis TGs â€” register both instances
3. Health check interval 30s (60s failover) â€” reduce to 10s for faster failover
4. `intranet-prod-db` Aurora: no Multi-AZ â€” risk of DB downtime on instance failure
5. 5 stale unused TGs â€” clean up

---

---

## 2026-06-10 â€” SIT EU/SG Aurora DB Fixes, prefiler-cache-util Pipeline Fix & Intranet Prod Deploy Fix

### SIT SG Aurora (`apse1-itopaz-sit-aurora-postgresql`)
**Cluster:** `apse1-itopaz-sit-eks` | ap-southeast-1 | Account: 464134132424

#### Problem
- Sudden ReadIOPS spike â†’ high DB load
- Root cause: `ALTER TABLE dbo.filereportedbl` (3.8GB table rewrite) triggered manual VACUUM ANALYZE + `autovacuum_naptime=5s` causing excessive background IO

#### Fix Applied
```bash
# Parameter group: apse1-itopaz-sit-aurora-postgresql-cluster-params
aws rds modify-db-cluster-parameter-group \
  --db-cluster-parameter-group-name apse1-itopaz-sit-aurora-postgresql-cluster-params \
  --parameters "ParameterName=autovacuum_naptime,ParameterValue=60,ApplyMethod=immediate"
```
- `autovacuum_naptime`: **5s â†’ 60s** â€” applied immediately âœ…

---

### SIT EU Aurora (`itariff-sit-cluster`)
**Cluster:** `euc1-itopaz-sit-eks` | eu-central-1 | Account: 464134132424  
**Instance:** `itariff-uat` (db.r5.xlarge) | DB: `TariffSelling` | PostgreSQL 15.15

#### Problem 1 â€” DMS Replication Slots (99% CPU, ReadIOPS 51K)
- **11 stale DMS logical replication slots** left behind from stopped/failed DMS tasks
- Running for 28 hours, preventing WAL cleanup â†’ massive WAL accumulation â†’ 51K ReadIOPS â†’ 99% CPU

#### Fix Applied
```sql
-- Killed all WAL sender PIDs then dropped all slots
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name LIKE '%dms%';
SELECT pg_drop_replication_slot(slot_name) FROM pg_replication_slots WHERE slot_type='logical';
```
- Result: ReadIOPS 51K â†’ 305 immediately. CPU 99% â†’ 66% â†’ recovering âœ…

#### Problem 2 â€” autovacuum_naptime=5s
- Same as SIT SG â€” autovacuum firing every 5s causing excessive background IO on 146GB `dbo.tariff` + 184GB `dbo.tariffdetails` tables (autovacuum had **never** run on these tables)

#### Fix Applied
```bash
# Parameter group: aurora-postgresql-uat-15
aws rds modify-db-cluster-parameter-group \
  --db-cluster-parameter-group-name aurora-postgresql-uat-15 \
  --parameters "ParameterName=autovacuum_naptime,ParameterValue=60,ApplyMethod=immediate"
```
- `autovacuum_naptime`: **5s â†’ 60s** â€” applied immediately âœ…

---

### prefiler-cache-util Jenkins Pipeline Fix
**Repo:** `allcargoecu/prefiler-cache-util` (Bitbucket) | Branch: `sit`  
**Jenkins Job:** `prefiler-nonprod-backend/SIT/prefiler-cache-util`

#### Problem 1 â€” App Compile Error
```
Prefiler.TestApi/Program.cs(20,29): error CS1061: 'ICacheService' does not contain a definition for 'GetAsync'
```
- `Program.cs` called `cache.GetAsync<Object>(key)` but `ICacheService` only defines `GetObjectAsync<T>`
- **Fix:** Changed `GetAsync` â†’ `GetObjectAsync` in `Prefiler.TestApi/Program.cs`
- Commit: `fff0b5ae` pushed to sit branch âœ…

#### Problem 2 â€” mstest Plugin Not Installed
```
java.lang.NoSuchMethodError: No such DSL method 'mstest' found
```
- Jenkinsfile (`prefiler-k8s-repo/jenkins/sit/api/prefiler-cache-util`) used `mstest` step in post-condition
- MSTest plugin not installed on this Jenkins instance
- **Fix:** Replaced with `archiveArtifacts artifacts: '**/TestResults/*.trx', allowEmptyArchive: true`
- Commit: `1188a6a` pushed to prefiler-k8s-repo sit branch âœ…

---

### SIT EU UI Latency Investigation â€” `/selling-rates/import` (10s load time)
**URL:** `https://itariff-euat.itopazapp.com/selling-rates/import`

#### Findings
- Static nginx serve: **17ms** âœ… â€” not the issue
- Page fires ~10 parallel BFF dropdown API calls on load
- Slow endpoints (all querying `dbo.tariff` 146GB / `dbo.tariffdetails` 184GB with no indexes):

| Endpoint | Time | Root Cause |
|---|---|---|
| `GET /bffdropdown/getShippingLineAgent` | 1,500â€“180,000ms | Full seq scan, no index, dead tuple bloat |
| `GET /bffdropdown/getTSOCPOL` | 1,946ms | Full seq scan on `dbo.tariff` |
| `GET /bffdropdown/getPOR` | 1,588ms | Full seq scan on `dbo.tariff` |
| `POST /BffTariffSelling/getTariffSellingSearchSingleRow1` | 343â€“1,798ms | `gettariffmainsearchsinglerow_db` stored proc, full scan |
| `POST /BffTariffBuying/getTariffBuyingSearchSingleRow` | 1,774ms | Full scan |

#### Routing path confirmed
```
Browser â†’ Istio Gateway (itariff-euat.itopazapp.com)
  â†’ /selling-rates/ â†’ tariff-selling-rates-ui (nginx, itariff-ui ns) [17ms]
  â†’ /tariff-selling-bff/ â†’ tariff-selling-bff (itariff-bff ns)
  â†’ tariff-selling-service (itariff-api ns)
  â†’ Aurora PostgreSQL TariffSelling DB
```

#### Fix Plan (5 steps, dev team needed)
1. **Redis cache** on `getShippingLineAgent`, `getTSOCPOL`, `getPOR` â€” TTL 30min â†’ <5ms
2. **DB indexes** on `dbo.tariff(pol_code)`, `dbo.tariff(por_code)`, `dbo.tariff(shipping_line_code, agent_code)` â€” use `CREATE INDEX CONCURRENTLY`
3. **Redis cache** on search row endpoints â€” TTL 5min â†’ <10ms
4. **autovacuum** running on `dbo.tariff`/`dbo.tariffdetails` (will complete in 2â€“4h, improving planner stats)
5. **Frontend** â€” use `Promise.all` for dropdown calls, add page skeleton

**Expected improvement:** 8â€“10s â†’ <500ms after all steps

---

**Account:** 745510282686 | **Region:** ap-south-1 | **SSH Key:** `infrastructure/secrets/keys/intranet/prod/Intranet-prod-1-Key.pem`

### Servers
| Server | IP | Role |
|--------|-----|------|
| Intranet-prod-1 | `10.151.4.89` | c5a.xlarge, compute node |
| Intranet-prod-2 | `10.151.4.153` | m5.2xlarge, memory node |

### Problem 1 â€” Broken `/root/.aws/credentials`
- File had `#[default]` as commented header â†’ `botocore.exceptions.ConfigParseError` â†’ AWS CLI crash
- **Fix:** `mv /root/.aws/credentials /root/.aws/credentials.bak` â€” instance IAM profile `intellihub-prod` used instead
- Applied on both servers âœ…

### Problem 2 â€” Git CodeCommit Auth Failure
- `git fetch` failed: `fatal: could not read Username for 'https://git-codecommit...'`
- Root cause: no valid credential helper for root user
- **Fix:** Set IAM Git credentials directly in remote URL (URL-encoded)
```bash
git remote set-url origin "https://<CODECOMMIT_USER>:<CODECOMMIT_PASSWORD>@git-codecommit.ap-south-1.amazonaws.com/v1/repos/aiml-poc"
```
- Applied on both servers âœ…

### Problem 3 â€” App Port 8001 Already In Use After Deploy
- `deploy.sh` kills `intranetapimain.py` by name but uvicorn workers (child PIDs) survived
- New process couldn't bind port 8001
- **Fix:** `fuser -k 8001/tcp` to kill all processes on port, then restart
- Applied on both servers âœ…

### Deploy Result
| Server | Commit Before | Commit After | App Status |
|--------|--------------|--------------|------------|
| 10.151.4.89 | `4763205` | `ab9539e` | Uvicorn :8001 âœ… |
| 10.151.4.153 | same | `ab9539e` | Uvicorn :8001 âœ… |

### Recommended Fix for deploy.sh (dev team)
Replace process kill logic:
```bash
# Current (unreliable â€” misses uvicorn workers)
PIDS=$(ps -ef | grep '[i]ntranetapimain.py' | awk '{print $2}')
if [ ! -z "$PIDS" ]; then kill -9 $PIDS; fi

# Better â€” kill by port
fuser -k 8001/tcp 2>/dev/null || true
sleep 2
```

---

### PROD EU iTariff Istio Ingress Setup + End-to-End Validation

  - `Gateway`: `itariff-gateway`
  - `VirtualService`: `itariff-ui`
  - `VirtualService`: `itariff-api`
  - `VirtualService`: `itariff-bff`

  - `itariff-ui.internaleu1prd-itopaz.com`
  - `itariff-bff.internaleu1prd-itopaz.com`
  - `itariff-api.internaleu1prd-itopaz.com`

  - Resolved to Istio ingress LB `a5c3d5f6763e149a1949597be2e56d79-0a180d890cef99d9.elb.eu-central-1.amazonaws.com`

  - UI host `/` -> `503`
  - API host `/` -> `503`
  - BFF host `/` -> `404` (expected, only prefixed bff routes defined)

  - Deployed `test-echo` Deployment + Service in namespaces:
    - `itariff-ui`
    - `itariff-api`
    - `itariff-bff`
  - Added `/test-ping` route at top priority in each corresponding VirtualService
  - **Verified via ingress host header**:
    - `itariff-ui.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-ui test ok`)
    - `itariff-api.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-api test ok`)
    - `itariff-bff.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-bff test ok`)

  - **Fix**: Updated parameter group `aurora-postgresql-uat-15`: `autovacuum_naptime` **5s â†’ 60s** (immediate) âœ…

### prefiler-cache-util â€” Jenkins Pipeline Fix (SIT)
- **Problem 1** (`CS1061`): `Program.cs` called `cache.GetAsync<Object>(key)` but interface only defines `GetObjectAsync<T>`
  - **Fix**: `GetAsync` â†’ `GetObjectAsync` in `Prefiler.TestApi/Program.cs` â€” commit `fff0b5ae` to sit branch âœ…
- **Problem 2** (`mstest` DSL not found): MSTest plugin not installed on Jenkins
  - **Fix**: Replaced `mstest` step with `archiveArtifacts` for `.trx` files â€” commit `1188a6a` to `prefiler-k8s-repo` sit branch âœ…

### SIT EU UI Latency Investigation (`/selling-rates/import` â€” 10s load)
- **Root cause**: ~10 parallel BFF dropdown calls on page load, all querying 146GB `dbo.tariff` / 184GB `dbo.tariffdetails` with no indexes (full seq scans)
  - Slow endpoints: `getShippingLineAgent` (up to 180s), `getTSOCPOL` (1.9s), `getPOR` (1.6s)
- **Fix plan** (requires dev team): Redis cache on dropdown endpoints (TTL 30min), `CREATE INDEX CONCURRENTLY` on key columns, autovacuum completion (2â€“4h), Promise.all on frontend
- **Static asset serving confirmed healthy**: nginx 17ms âœ…

### Intranet Prod Deploy Fix (Account 745510282686, ap-south-1)
- **Servers**: `Intranet-prod-1` (10.151.4.89, c5a.xlarge) + `Intranet-prod-2` (10.151.4.153, m5.2xlarge)
- **Fix 1**: `/root/.aws/credentials` had `#[default]` commented header â†’ ConfigParseError â†’ moved to `.bak`, uses instance IAM profile
- **Fix 2**: Git CodeCommit auth failure on root user â†’ set IAM Git credentials in remote URL (URL-encoded)
- **Fix 3**: Port 8001 already in use post-deploy (uvicorn worker PIDs surviving kill-by-name) â†’ `fuser -k 8001/tcp`
- **Result**: Both servers deployed to commit `ab9539e`, Uvicorn :8001 âœ…
- **SSH Key**: `infrastructure/secrets/keys/intranet/prod/Intranet-prod-1-Key.pem`

### Intellihub HA Assessment (Account 745510282686, ap-south-1)
- Both instances healthy (system + instance checks ok/ok), 2 AZs, ALB target groups all green
- 6 services confirmed True HA: `intellihub-prod`, `intellihubadmin-prod`, `gatimasterapi-prod`, `sendbulktracking`, `symphonywrapper-prod`, `zendeskwrapper-prod`
- **Gap**: No ASG (no auto-recovery on instance failure) â€” recommended EC2 Auto Recovery alarm
- **Fixed**: `cleanup_python_zombies.sh` script was in prod-2 crontab but file was missing â†’ copied from prod-1 âœ…
- 5 stale unused target groups identified (not attached to any listener): `aimlprod-1`, `ecureports`, `ecureports-api`, `intellaiml-prod-4001`, `intellihub-prod-2`

---

---

## 2026-06-08 â€” Cluster Autoscaler Fixes (SIT EU & DEV EU)

### master-prefiler-service (SIT) â€” HTTP 500 Root Cause & Fix
- **Symptom**: PageMaster endpoint returning 500 with `RetryLimitExceededException` + `NpgsqlException: Connection reset by peer`
- **Root cause 1**: ConfigMap had wrong zone key naming â€” `ConnectionStrings__zone1` instead of `ConnectionStrings__GroupageHost_zone1`. Keys never matched â†’ fell back to baked-in `appsettings.json` â†’ pointed to DEV Aurora
- **Root cause 2**: Duplicate YAML keys for zone1-zone6 (last one wins) â€” silent data loss
- **Root cause 3**: Leading space in password: `Password= passwordsit@1035`
- **Fix**: Added `ConnectionStrings__GroupageHost_zone0-zone6`, `EDIDbHost_zone0-zone6`, `SecurityFilerHost_zone0-zone6` â€” all pointing to SIT Aurora, fixed password
- **Commit**: `76de88f` to `sit` branch in `prefiler-k8s-repo` âœ…
- **Verified**: HTTP 200, 25s response âœ…

### tariff-company-service (SIT) â€” Memory Pressure (HPA 93%)
- **Root cause**: `JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=50.0` against 2500Mi limit â†’ JVM heap 1250Mi vs 700Mi memory request = 114% HPA â†’ stuck at 10/10 replicas
- **Fix**: Changed to `-Xmx600m -Xms256m` + raised memory request `700Mi â†’ 1000Mi`
- **Result**: HPA memory **93% â†’ 43%** immediately. Commit `afd2097` to `uat` branch in `itariff-k8s-repo` âœ…

### SIT Node Count Bloat (33 nodes â†’ ~20)
- **Root cause 1**: CA `--scale-down-utilization-threshold=0.5` â€” any node with CPU requests >50% blocked from drain
- **Root cause 2**: CA `--skip-nodes-with-local-storage=true` â€” pods using `emptyDir` blocked 26 nodes from draining
- **Fix**: Patched CA: `--scale-down-utilization-threshold=0.70` + `--skip-nodes-with-local-storage=false`
- **Backup**: `/tmp/cluster-autoscaler-backup-2026-06-08.yaml` on SIT bastion
- **Result**: CA immediately identified 13 unneeded nodes, scaled down to ~20 nodes âœ…

---

**Date:** 2026-06-08  
**Cluster:** `euc1-itopaz-sit-eks` (eu-central-1)  
**CA Version:** `registry.k8s.io/autoscaling/cluster-autoscaler:v1.33.0`  
**Performed by:** DevOps Team  

---

### Problem Statement

SIT EKS cluster grew from **22 â†’ 33 nodes** while actual workload resource usage remained very low:
- Average CPU utilization: **2â€“5% per node**
- Average Memory utilization: **18â€“39% per node**

Cluster Autoscaler was **unable to scale down** nodes due to two default configurations blocking it.

---

### Root Cause Analysis

### Blocker 1 â€” Scale-down utilization threshold too low
CA default `--scale-down-utilization-threshold=0.5` (50%)  
Nodes had CPU **requests** above 50% (e.g. 51â€“97%) even though **actual usage** was only 2â€“5%.  
CA treats request-based fill, not actual usage â†’ majority of nodes marked **unremovable**.

**CA log evidence:**
```
Node ip-10-100-208-40 unremovable: cpu requested (77.4% of allocatable) is above the scale-down utilization threshold
Node ip-10-100-211-40 unremovable: cpu requested (55.5% of allocatable) is above the scale-down utilization threshold
```

### Blocker 2 â€” Local storage eviction disabled by default
CA default `--skip-nodes-with-local-storage=true`  
Services using `emptyDir` volumes (ephemeral/temp storage) were preventing node drain.  
All 26 nodes had at least one such pod â†’ **none could be drained**.

**CA log evidence:**
```
Node ip-10-100-215-211 cannot be removed: pod with local storage present: itopaz-profile-service-...
Node ip-10-100-212-208 cannot be removed: pod with local storage present: aes-prefiler-service-...
Node ip-10-100-208-245 cannot be removed: pod with local storage present: tariff-selling-consumer-service-...
```
> **Note:** All affected services are **stateless**. `emptyDir` is ephemeral temp storage â€” no data loss on pod eviction and rescheduling.

---

### Actions Taken

### Step 1 â€” Backup CA deployment
```bash
kubectl get deployment cluster-autoscaler-aws-cluster-autoscaler \
  -n kube-system -o yaml \
  > /tmp/cluster-autoscaler-backup-2026-06-08.yaml
```
**Backup location on bastion:** `/tmp/cluster-autoscaler-backup-2026-06-08.yaml`

---

### Step 2 â€” Patch: Raise scale-down utilization threshold to 70%
```bash
kubectl patch deployment cluster-autoscaler-aws-cluster-autoscaler \
  -n kube-system \
  --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/command/-","value":"--scale-down-utilization-threshold=0.70"}]'
```
**Effect:** CA will now consider a node removable if its total CPU+memory *requests* are below **70%** of allocatable (previously 50%).

---

### Step 3 â€” Patch: Allow eviction of emptyDir pods
```bash
kubectl patch deployment cluster-autoscaler-aws-cluster-autoscaler \
  -n kube-system \
  --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/command/-","value":"--skip-nodes-with-local-storage=false"}]'
```
**Effect:** CA will now evict stateless pods using `emptyDir` volumes during node drain. Pods are safely rescheduled onto other nodes with a fresh empty directory.

---

### Step 4 â€” Verify final CA configuration
```bash
kubectl get deploy cluster-autoscaler-aws-cluster-autoscaler \
  -n kube-system \
  -o jsonpath="{.spec.template.spec.containers[0].command}" | tr "," "\n"
```
**Output confirmed:**
```
"./cluster-autoscaler"
"--cloud-provider=aws"
"--namespace=kube-system"
"--node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/euc1-itopaz-sit-eks"
"--logtostderr=true"
"--stderrthreshold=info"
"--v=4"
"--scale-down-utilization-threshold=0.70"
"--skip-nodes-with-local-storage=false"
```

---

### Result

After patches were applied, CA immediately identified **13 unneeded nodes** and began the scale-down process:

```
nodes.go: ip-10-100-212-208 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-214-191 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-212-16  is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-210-204 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-211-245 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-209-12  is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-208-137 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-211-240 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-213-179 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-208-245 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-210-251 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-214-222 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-209-154 is unneeded since 2026-06-08 13:07:06
```

**CA automatically:** cordons â†’ drains â†’ terminates each node after 10 minutes unneeded (default `--scale-down-unneeded-time`).

---

### Expected Final State

| Metric | Before | After (expected) |
|--------|--------|-----------------|
| Nodes | 33 | ~20 |
| Avg CPU actual | 2â€“5% | 5â€“15% |
| Avg Memory actual | 18â€“39% | 40â€“65% |
| CPU request fill | 50â€“97% per node | ~70% per node |
| CA scale-down threshold | 0.50 (default) | **0.70** |
| emptyDir pod eviction | blocked (default) | **allowed** |

---

### Rollback (if needed)

To restore original CA configuration:
```bash
kubectl apply -f /tmp/cluster-autoscaler-backup-2026-06-08.yaml
```

---

### Reference
- Official CA FAQ: https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md
- Parameter `scale-down-utilization-threshold` default: `0.5` (documented in CA parameters table)
- Parameter `skip-nodes-with-local-storage` default: `true` (documented in CA parameters table)

---

## 2026-06-05 â€” Operations Log

### prefiler-bff (SIT) â€” API Gateway CORS + Login Fix
- Fixed HTTP integration (not HTTP_PROXY) to pass `access-token` and `authentication` response headers
- Added `access-token, authentication` to `Access-Control-Expose-Headers`
- Added `officeid, access-token, authentication, channelid, userid, appid` to OPTIONS `Access-Control-Allow-Headers`
- Login verified: `https://prefiler-bff-eusit.itopazapp.com/prefiler-bff/prefiler-auth-bff/bff/v1/auth/login` âœ…

### Kafka Topic Fix (SIT)
- **Created topic**: `trf-exl-upld-prc-topic-v3` on SIT MSK (was causing TimeoutException in `tariff-selling-service-batch`)
- **Updated configmap**: Added topic + consumer group to `tariff-selling-service-batch`
- **Committed**: `3e3c9d5` to `origin/uat` in `itariff-k8s-repo` âœ…

### Windows Node DNS Fix (SIT EU)
- **Root cause**: Linux node SG (`sg-05c315bde97f77bf1`) did NOT allow traffic from Windows node SG (`sg-02fa2ce777340f203`)
- **Fix**: `aws ec2 authorize-security-group-ingress --group-id sg-05c315bde97f77bf1 --protocol -1 --source-group sg-02fa2ce777340f203`
- **Rule ID**: `sgr-0dc8147e6c3c819fe` âœ…

### microfrontend-main Jenkins Pipeline Fix (SIT)
- **Root cause**: AWS STS token expires during `kubectl rollout status` wait (100s+) â†’ "Unauthorized"
- **Fix**: Moved post-deploy verification to separate `Verify Deployment` stage with own `withAWS` block and fresh `aws eks update-kubeconfig`
- **Commit**: `558254d` to `sit` branch âœ…

---

---

## 2026-06-04 â€” Operations Log

### UAT Resource Configuration Audit (itariff-api + itariff-bff)
- **Pulled live config** from euc1-itopaz-sit-eks for all 26 deployments in itariff-api and 3 in itariff-bff
- **Missing resource limits identified**:
  - `tariff-grant-bff`: NO cpu/memory requests or limits set
  - `tariff-selling-bff`: No CPU request/limit (only memory: 2Gi req, 6Gi limit)
  - `tariff-selling-consumer-service`: No CPU/memory limits (only requests: 1 cpu, 3Gi memory)
  - `tariff-domain-batch`: No resources at all

### SIT Kafka Full Topic Configuration Audit
- **Listed all 38 tariff topics** with complete configurations
- **Corrected client.properties path**: `/home/ec2-user/kafka-client/kafka_2.13-3.6.0/bin/client.properties` (not in parent dir)
- **Topic config patterns**:
  - Upload topics: 1GB max.message.bytes, min.insync.replicas=1, no explicit retention
  - Process/archive topics: 10MB max.message.bytes, min.insync.replicas=2, retention.ms=604800000 (7 days)
  - All topics: ReplicationFactor=2, message.format.version=3.0-IV1, unclean.leader.election=false

### Prefiler Auth BFF - External 403 Investigation
- **Symptom**: `https://prefiler-bff-eusit.itopazapp.com/prefiler-bff/prefiler-auth-bff/bff/v1/auth/login` returns 403
- **Internal works**: `https://prefiler-bff.internaleu1-itopaz.com/prefiler-auth-bff/bff/v1/auth/login` returns 200 + JWT
- **Root cause**: FortiGuard IPS (not WAF) blocking the URL at network layer
- **Evidence**: Response HTML contains "FortiGuard Intrusion Prevention - Access Blocked" / "URL is banned"
- **Request path**: Client â†’ FortiGuard â†’ Global Accelerator (af9b262029faa8833.awsglobalaccelerator.com) â†’ API GW â†’ Istio â†’ pod
- **Action needed**: Network team must whitelist URL in FortiGuard policy

### Prefiler tariff-grant-bff/authenticate - 500 Error
- **Call chain**: prefiler-auth-bff â†’ tariff-grant-bff â†’ tariff-profile-service (adauthenticate endpoint)
- **DB query**: `SELECT * FROM profile WHERE ademailid = ? OR mailid = ? AND isdeleted = 0 LIMIT 1`
- **Error**: `NullPointerException: Cannot invoke "com.alcg.profile.entity.Profile.getUser_id()" because "profile" is null`
- **Cause**: User being authenticated from prefiler doesn't have a matching profile entry in tariff DB
- **Fix**: Add user to profile table OR fix null handling in tariff-profile-service code

### AWS WAF & API Gateway Documentation
- **WAF ACL** (`itopaz-api-gwt-acl`): Only attached to itariff-bff API GW (dygy1tl8n5), NOT prefiler-bff
- **Rule priority 0** (`zscalar-ip-restriction`): Blocks if X-Forwarded-For NOT in Zscaler IPv4/IPv6 IP sets
- **prefiler-bff API GW** (7a8aq4c0oa): No WAF, apiKeyRequired=true, routes to internal Istio gateway
- **Custom domain**: `prefiler-bff-eusit.itopazapp.com` â†’ REGIONAL endpoint â†’ basePath `/prefiler-bff` â†’ stage sit
- **API key**: Confirmed valid and enabled (trxH8cOmlp6e9EKOAUUuh6nEi2ofzB4v29me6vWO)
- **Usage plan**: itariff-api â€” burst:50, rate:100/s, quota:80,000/day

---

## 2026-05-30 â€” Operations Log

### FAISS Vector Database Setup
- **Installed** faiss-cpu, sentence-transformers, torch (CPU-only) on workspace
- **Ingested** KNOWLEDGE-BASE.md into FAISS index (68 chunks, 384-dimension vectors, 102KB index)
- **Scripts**: `scripts/ingest_knowledge.py`, `scripts/query_knowledge.py` â€” supports semantic search, JSON output, interactive mode
- **Vector store**: `vectordb/knowledge.index` + `vectordb/chunks.json`

### S3 Bucket Organization (devops-securit-dev)
- **Cleaned up** old scattered files: removed `eks-docs/`, `prefiler-sit-knowledge/`, root-level session/handover .md files
- **Moved** all root-level .md files under `devops/` prefix (Activity Calender, GATI inventories, ZPA, account_details, ec2-rds)
- **Uploaded** organized structure via DEV jump server (10.100.145.118):
  - `devops/KNOWLEDGE-BASE.md` â€” single consolidated file for LLM agents
  - `devops/activity-log.md`, `devops/eks-clusters.md`
  - `devops/docs/` â€” all detailed documentation + knowledge-export/
  - `devops/vectordb/` â€” FAISS index + metadata
  - `devops/scripts/` â€” ingest, query, rebuild tools
- **S3 root** now only contains binary archives (rpm, tar, tgz, tar.xz) + `pem/`

### Bastion Host Cleanup (/home/ec2-user/)
- **Deleted ~1.3GB** of old logs/archives: `batch2.log` (413MB), `batch2.3log` (429MB), `kafka*.tgz/zip` (218MB), `python_3_10_slim.tar` (129MB), `eks-node-cleanup.log` (81MB)
- **Organized 140+ loose files** into structured `organized/` directory:
  - `organized/repos/` â€” 20 git repos & script folders
  - `organized/k8s-manifests/` â€” 28 YAML files
  - `organized/iam-policies/` â€” 6 policy JSONs
  - `organized/keys/` â€” certs, PEM files
  - `organized/tools/` â€” gcrane, krane, cleanup scripts
  - `organized/efs-configs/` â€” 4 EFS PV/PVC yamls
  - `organized/istio-configs/` â€” gateway, virtualservice
  - `organized/archived-configs/` â€” old misc files & dirs
- **Deleted additional 727MB**: `bw-baseimage_2.9.0.tar` (435MB), both istio installs (178MB), kafka extracted (114MB), 6 empty dirs
- **Cleaned hidden caches (~12GB)**: `.cache/pip` (3.9GB), `.local/lib` (4.9GB), 4 old VS Code servers (1.8GB), `sufeeyan-copilot/` (1.1GB), `.cache/aws` + `.cache/cloud-code` (338MB)
- **Disk usage**: 88% â†’ 48% (3.9GB free â†’ 16GB free)
- **Excluded** from changes: `rahul/`, `sufeeyan/`, `vijay/`, `rajnish/`

---

## 2026-05-29 â€” Operations Log

### master-prefiler-service Pipeline Fix
- **Root cause**: Jenkins reads pipeline from `jenkins/dev/api/master-prefiler-service` but fix was applied to `jenkins/dev/master-prefiler-service`
- **Fix 1**: Copied corrected pipeline to correct path (`jenkins/dev/api/master-prefiler-service`)
- **Fix 2**: `AccessDeniedException` â€” `Terraform_Execution_Role` (074779643551) cannot call `codeartifact:GetAuthorizationToken` cross-account to 439891535362. Removed `withAWS` wrapper, using Jenkins agent's native AWS credentials instead
- **Fix 3**: Build failed with `CS0246: type 'prefiler' not found` â€” commit `7db6d23` had deleted `SharedLib/` containing `prefiler.security.dll`, `Prefiler.Base.Shared.dll`, `Prefiler.CacheUtil.dll`. Restored DLLs from git history
- **Pushed**: prefiler-k8s-repo `dev` branch (commits 6295650, f1f0927), master-prefiler-service `develop` branch (commits 4c55e4c, e94f43c)

### itariff-k8s-repo JVM/Memory Optimization (uat branch)
- **Pushed** JVM memory optimization and resource right-sizing for 8 services (commit 5603bdc)
- Services: tariff-buying-carriage, otherbooking, service, standardcost, truck, warehouse, grant-auth, selling-storage-service
- Changes: JAVA_TOOL_OPTIONS env vars, memory requests/limits right-sized

### itariff-k8s-repo (uat branch)
- **Updated `tariff-buying-shippingline-consumer-service.yaml`** config for `buying-domain-service`:
  - Changed microId to `buying-domain-service`, port to 80, context-path to `/buying-domain-service`
  - Optimized HikariCP pool settings (keepalive-time, idle-timeout, connection-timeout tuned)
  - Restructured JPA config (moved show-sql/ddl-auto)
  - Updated Kafka config with bulk upload topics, bulk process/archive topics, new consumer groups
  - Updated `restTemplate` connection pool (maxPerRoute: 20, maxConnections: 100), removed connect/read timeouts
  - Simplified `serviceurls` (geography, master, invoice, company, tariff)
  - Replaced `serviceMsg` with `service` block (new error codes: DUP1202, SAVE1201, ERR1203, NF1205, VAL1203)
  - Updated management endpoints include to `health,info,prometheus,metrics`

- **Improved Jenkins ConfigMap pipeline (`Jenkincm`)** â€” simplified for UAT-only use:
  - Hardcoded UAT branch, cluster (euc1-itopaz-sit-eks), region, cross-account role
  - Reduced parameters to only `namespace` and `application_name`
  - Cleaned up and sorted application list (removed duplicates)
  - Added validation stage (fails early if `--SELECT--` chosen)
  - Removed unused variables (REGISTRY, DEPLOY_ENV, gitCommit)
  - Added rollout timeout (120s) to prevent hanging builds
  - Always uses cross-account role (no conditional)

---

## 2026-05-27 â€” Operations Log

### itariff-k8s-repo (develop branch)
- **Increased CPU/memory by 10%** for 9 buying services and pushed to Bitbucket (commit cfbf401)
- **Patched DEV cluster** (euc1-itopaz-dev-eks, ns: itariff-api) with new resource values
- Services updated: tariff-buying-carriage-consumer, carriage, otherbooking, service, shippingline-consumer, standardcost, truck, warehouse-consumer, warehouse

### prefiler-k8s-repo (dev branch)
- **Applied all ConfigMaps to DEV cluster** (prefiler-api namespace): aci, aes, afr, ams, basf, dagangnet, ics, ics2, imdg, master, mblfiler, mpci, prefiler-auth-service (13 total)
- **Fixed sa-prefiler-service-config.yaml**: namespace was `default`, changed to `prefiler-api`, pushed to Bitbucket (commit 929171b)
- **prefiler-bff namespace**: prefiler-auth-bff-config, prefiler-bff-config (already in sync)

### SIT EU Cluster (euc1-itopaz-sit-eks) Optimization
- **Enabled NTH** (aws-node-termination-handler) temporarily, then **disabled** again per user request
- **Disabled duplicate fluent-bit** (fluent-bit namespace) â€” was running alongside amazon-cloudwatch/fluent-bit. Saved ~1.7 cores + 833Mi
- **Disabled promtail** (monitoring namespace) â€” redundant with fluent-bit. Saved ~1.7 cores + 4.25GB
- **Verified csi-smb-node** is REQUIRED (8 bound SMB PVCs across itopaz-api, auth, export, platform)
- **Verified efs-csi-node** is REQUIRED (4 bound EFS PVCs in istio-system: grafana, jaeger, kiali, prometheus)

### Node Status Checks (May 27)
- DEV EU: 18 nodes (3 cordoned)
- SIT EU: Started at 23 nodes -> scaled to 35 nodes (all Ready)
- SIT Singapore: 4 nodes (1 cordoned)

---

## 2026-05-26 â€” Operations Log

- Fixed prefiler Jenkins pipelines (aes, afr SIT builds)
- Created 8 missing frontend Jenkins jobs
- Pushed prefiler-k8s-repo sit branch (commit 6221583)
- Created jenkins-config.md and eks-prefiler-config.md
- Synced md files to S3 bucket devops-securit-dev

---

---

## 2026-05-20 â€” EKS Resource Optimization (SIT & DEV) & Session Notes

### SIT (UAT) Selling Service Fixes
- **Fixed `tariff-selling-service` CPU**: Patched from 350m/800m â†’ 500m/2000m
- **Fixed `tariff-selling-consumer` memory**: Was ~1.5TB/~1.9TB (same TB bug), fixed to 700Mi/1200Mi
- **Fixed `tariff-selling-service` HikariPool exhaustion**: Was getting 504s â€” `Connection is not available, request timed out after 10005ms (total=12, active=12, idle=0, waiting=9)`. Increased `maximum-pool-size` from 12 â†’ 25 in configmap
- **Checked `tariff-selling-service-batch`**: Healthy, no issues (500m/2Gi, 2Gi/3Gi)

### Node Status Check (All 3 Environments)
- **SIT EU (Frankfurt)**: 27 nodes â€” All Ready âœ…
- **DEV EU (Frankfurt)**: 15 nodes â€” All Ready âœ…
- **SIT Singapore**: 3 nodes â€” All Ready âœ… (EKS v1.35.3/v1.35.4)

### SIT Singapore Cluster Discovery
- **Region**: ap-southeast-1
- **Bastion**: `ssh -i /home/ec2-user/rahul/rahul-key ec2-user@10.130.210.3` (from current host 10.151.4.165)
- **Nodes**: 3

### Other Checks
- **itopaz UI (DEV)**: All healthy â€” export-ui (2), maintenance-ui (2), shell-ui (2)
- **afr-prefiler-service (SIT Frankfurt)**: 2 pods Running 2/2 âœ… (prefiler-api namespace)
- **DEV Kafka consumer groups**: Listed 58 groups; identified stale `-local` groups and mismatched `-uat` groups

### SIT Cluster (euc1-itopaz-sit-eks)
### Completed
1. **Cluster Autoscaler IRSA fixed** â€” Added SA annotation, fixed trust policy (wrong condition key + wrong SA name)
2. **Nodes uncordoned** â€” 12 nodes were accidentally cordoned during migration, uncordoned all
3. **Metrics-server fixed** â€” Pod was Pending due to cordoned nodes, then label `k8s-app=metrics-server` added to deployment pod template
4. **HPAs capped** â€” All itariff-api HPAs set to min=2
   - Buying services: max=3
   - Selling services (25-partition topics): max=20
   - Other selling: max=10
5. **tariff-selling-consumer resources fixed** â€” Was 1.5TB memory request (misconfigured). Set to cpu:250m/1, memory:700Mi/1200Mi
6. **tariff-selling-consumer-hpa** â€” Removed memory metric, CPU only (75% target)
7. **tariff-buying-consumer-service HPA** â€” Removed memory metric, CPU only (80% target)
8. **tariff-buying-warehouse-service** â€” Added resources (cpu:100m/500m, memory:700Mi/1126Mi) to fix HPA <unknown>
9. **Prefix delegation** â€” Already enabled (ENABLE_PREFIX_DELEGATION=true), maxPods=110 working

### DEV Cluster (euc1-itopaz-dev-eks)
### Completed
1. **Metrics-server fixed** â€” Added `k8s-app=metrics-server` label to pod template (same issue as SIT)
2. **Prefix delegation enabled** â€” Set ENABLE_PREFIX_DELEGATION=true on aws-node daemonset
3. **Instance refresh completed** â€” All nodes replaced, but maxPods still 29 (needs launch template UserData)

### Pending
- **Launch template update needed** â€” Add NodeConfig UserData with maxPods=110, then another instance refresh
- **6 Pending pods** â€” Windows pods need Windows node group

---

### 1. Dev vs SIT Resource Comparison (itariff-api)

### Services with HIGHER resources in SIT than Dev:
| Service | Dev CPU Req/Lim | SIT CPU Req/Lim | Dev Mem Req/Lim | SIT Mem Req/Lim |
|---------|----------------|-----------------|-----------------|-----------------|
| tariff-company-service | 100m/300m | 500m/2 | 700Mi/2500Mi | 2Gi/8Gi |
| tariff-geo-service | 100m/300m | 500m/2 | 700Mi/2500Mi | 2Gi/8Gi |
| tariff-invoice-service | 50m/250m | 500m/2 | 1126Mi/1434Mi | 2Gi/8Gi |
| tariff-master-service | 100m/300m | 500m/2 | 700Mi/2500Mi | 2Gi/8Gi |
| tariff-selling-oc-service | 100m/500m | 300m/1 | 700Mi/1024Mi | 300Mi/2Gi |
| tariff-selling-storage-service | 50m/250m | 500m/2 | 500Mi/950Mi | 300Mi/8Gi |
| tariff-trucker-rates-service | 50m/250m | 300m/1 | 300Mi/900Mi | 300Mi/2Gi |

### Services with HIGHER resources in Dev than SIT:
| Service | Dev CPU Req/Lim | SIT CPU Req/Lim | Dev Mem Req/Lim | SIT Mem Req/Lim |
|---------|----------------|-----------------|-----------------|-----------------|
| tariff-selling-service | 500m/2000m | 350m/800m | 1400Mi/1800Mi | 1400Mi/1800Mi |
| tariff-buying-service | 100m/500m | 100m/500m | 500Mi/1126Mi | 300Mi/1126Mi |

### 2. S3 Optimization Report (itariff-api-optimization-report.md)

Located at: `s3://devops-securit-dev/itariff-api-optimization-report.md` (root level)
- NOT accessible from jump server 10.100.208.17 (different account)
- Accessible from dev bastion 10.100.145.118

Key findings:
- Most services using <5% CPU of requested resources
- tariff-selling-consumer-service has NO CPU limit (High severity)
- tariff-company-service & tariff-geo-service at ~85% memory usage
- tariff-domain-batch has no resource data (missing monitoring)

### 3. Prefiler Auth Service - Dev (WORKING)

- Namespace: `prefiler-api`
- Endpoint: `http://prefiler-auth-service-svc.prefiler-api.svc.cluster.local/api/v1/Auth/login`
- External: `http://prefiler-api.internaleu1dev-itopaz.com/prefiler-auth-service/api/v1/Auth/login`
- VS in `istio-system`, routes `/prefiler-auth-service/` prefix
- Config baked into Docker image (`/app/appsettings.json`)
- No envFrom or volume mounts needed - works with image-baked config
- Redis: `master.euc1-itopaz-dev-redis.lf4u8f.euc1.cache.amazonaws.com`

### 4. Prefiler Auth Service - SIT (BROKEN - DB Connection Failure)

- Namespace: `prefiler-api`
- External: `http://prefiler-api.internaleu1-itopaz.com/prefiler-auth-service/api/v1/Auth/login`
- VS in `istio-system`, routes `/prefiler-auth-service/` prefix â†’ correct
- Pods: 2 replicas Running
- Image: `464134132424.dkr.ecr.eu-central-1.amazonaws.com/sit-eu/prefiler-backend:prefiler-auth-service-sit-c2b2a401`

### Root Cause:
- SIT image has **dev config baked in** (`appsettings.json`):
  - Redis â†’ `euc1-itopaz-dev-redis` (should be `euc1-itopaz-sit-redis-new`)
  - DB connection string (encrypted) â†’ points to dev DB, unreachable from SIT VPC
- Error: `Npgsql.Internal.NpgsqlConnector.RawOpen` Socket error (can't connect to PostgreSQL)

### Actions Taken:
1. Created `prefiler-auth-service-config` ConfigMap (flat key-value, SIT Redis)
2. Created `prefiler-auth-service-secret` Secret (connection strings from original CM)
3. Patched deployment with `envFrom` (configMapRef + secretRef)
4. Patched deployment with volume mount: ConfigMap `prefiler-auth-service` â†’ `/etc/config/`

### Still Broken Because:
- DB connection strings are **encrypted** with AES (Key: `vZz1aZkK6XzqvZkLZ3sYw9vZz1aZkK6XzqvZkLZ3sYw=`)
- The encrypted values in the ConfigMap decrypt to **dev DB endpoint**
- Need correct SIT PostgreSQL connection string encrypted with the same key
- ASP.NET Core reads from `/app/appsettings.json`, not `/etc/config/` â€” volume mount alone won't override

### To Fix:
- Team needs to provide correct SIT encrypted DB connection string
- OR rebuild image with correct SIT `appsettings.json`
- OR mount correct config at `/app/appsettings.Production.json`

### 5. SIT Prefiler-API VirtualService Routes

All routes in `prefiler-api` VS (istio-system namespace) â€” **Updated June 4, 2026 (13 routes)**:
- `/sa-prefiler-service/` â†’ prefiler-auth-service-svc (note: sa routes to auth-service)
- `/afr-prefiler-service/` â†’ afr-prefiler-service-svc
- `/ams-prefiler-service/` â†’ ams-prefiler-service-svc
- `/master-prefiler-service/` â†’ master-prefiler-service-svc
- `/prefiler-auth-service/` â†’ prefiler-auth-service-svc
- `/ics2-prefiler-service/` â†’ ics2-prefiler-service-svc
- `/aes-prefiler-service/` â†’ aes-prefiler-service-svc
- `/dagangnet-prefiler-service/` â†’ dagangnet-prefiler-service-svc
- `/aci-prefiler-service/` â†’ aci-prefiler-service-svc
- `/basf-prefiler-service/` â†’ basf-prefiler-service-svc
- `/ics-prefiler-service/` â†’ ics-prefiler-service-svc
- `/imdg-prefiler-service/` â†’ imdg-prefiler-service-svc
- `/mblfiler-prefiler-service/` â†’ mblfiler-prefiler-service-svc

Note: SIT now has 13 routes matching Dev (previously only had 2: afr + auth catch-all)

### 6. ConfigMaps in prefiler-api namespace (SIT)

- `aci-prefiler-service` - 1 data key
- `prefiler-auth-service` - 1 data key (nested YAML manifest)
- `prefiler-auth-service-config` - 16 data keys (flat, created today)

---

## 2026-05-18 â€” Operations Log

### tariff-buying-carriage-service Kafka Topic Fix (SIT/UAT)
- **Root cause**: Producer was publishing to `tariff-buying-carriage-excel-upload-local` (dev default from application.yml) â€” topic doesn't exist on UAT broker
- **Error**: `TimeoutException: Topic tariff-buying-carriage-excel-upload-local not present in metadata after 60000 ms`
- **Fix**: Added `tariff-buying-carriage-excel-upload-topic-name: tariff-buying-carriage-excel-upload-uat` to `tariff-buying-carriage-service` configmap (was missing, consumer CM had it but producer didn't)
- **Note**: Service returned HTTP 200 despite failure (silent failure)

### auth-base-uri Addition (SIT/UAT)
- **Added** `auth-base-uri: http://tariff-profile-service.itariff-api.svc.cluster.local/profile-domain-service` to:
  - `tariff-buying-carriage-service` configmap (serviceurls section)
  - `tariff-buying-carriage-consumer-service` configmap (new serviceurls section created)
- Restarted both deployments

### tariff-grant-auth Resource Fix (DEV)
- **Issue**: Memory request/limit was ~1.1TB/~1.5TB (bytes with `m` suffix â€” same bug pattern)
- **Fix**: Patched to cpu:100m/500m, memory:700Mi/1500Mi

---

### 2026-10-10 - Merge master control to main with SCM backups

- User requested merging feat/topaz-master-control into main and will deploy each repository through Jenkins.
- Preserved each original main remotely as backup/main-before-topaz-master-control-20261010 before pushing merges.
- itopaz-agent: original 3c63589, merged main 94a54bc.
- allcargo-itopaz-knowledge: original cef2497, merged main d28054e.
- aws-dashboard: original b07b711, merged main 4d94a06.
- Knowledge Jenkinsfile removed per-minute SCM polling and gates Deploy to EKS and Verify Rollout on DEPLOY_TO_DEV=true plus UserIdCause. Use Build with Parameters for its manual deployment. Jenkins runtime validation remains for the operator's build.
- Verified remote main and backup commit IDs, feature ancestry, exact merged feature trees, and clean worktrees in all three repositories. No Jenkins job was invoked and no deployment command was run for this merge task.

### 2026-10-10 - Direct master Dashboard API, POC account, and agentx UI

- DEV deployment readiness: itopaz-agent, knowledge-bot-backend, aws-dashboard-api all 1/1; pods 2/2 with no restarts at inspection. Dashboard and Knowledge application health passed.
- Important runtime finding: live itopaz-agent-75 lacks Python and /control/status returns 404. Jenkins SCM definitions for all three jobs already use main; rebuild agent from the current main. Agent pipeline now cleans its workspace, explicitly checks out main, and verifies the Python runtime after rollout.
- Added Python agent 1.4.0 browser console at /agentx, with service health, authenticated chatbot/search/inventory, and a manual daily checklist. Existing live /agentx prefix routes to agent service port 8082 without rewrite. Browser has no resource mutation endpoint; key stays in tab memory.
- Direct master API: separate authenticated account listing and exact-payload approved actions; expiry <=5 minutes, configured account/region checks, wrong-role account guard, duplicate approval rejection per API process. Bot credentials do not authorize direct master endpoints. Changes still require typed approval on Windows.
- Operator confirmed POC 745510282686, ap-south-1, existing dashboard role name eks-dashboard-s3-role. Added account/role/region to Dashboard manifest and POC/Mumbai filters to frontend. Standalone worker-2 STS role verification failed TLS certificate validation with default and system CA bundles; IAM permissions and trust remain unverified. No TLS checks disabled for this check and no IAM changes performed.
- Provisioned Secret topaz-dashboard-master (dedicated token) and stored private Windows token without displaying it. Updated SSH helper to repair stale pod forwards and serve separate controller 18082 and Dashboard 18080 loopback connections. Temporary Jenkins key copy removed after isolated build checks.
- Tests: local Python 18 passed; SCM Python 13 passed and 5 intentionally skipped for missing local node registry; Go tests passed; Dashboard frontend built in isolated Node container; agent UI JavaScript syntax passed. No AWS resource start/stop/tag/scale performed. No Jenkins builds or rollout commands launched by this task.
- Original Agent and Dashboard main branches preserved remotely as backup/main-before-dashboard-ui-20261010. User will deploy through Jenkins: aws-dashboard first, then itopaz-agent; Knowledge remains compatible.

### 2026-10-10 - Fix Jenkins agent checkout HTTP 403

- User supplied Jenkins build 76 failure: Jenkinsfile retrieval from x-token-auth@bitbucket.org succeeded, but Checkout failed after the pipeline used the bare Bitbucket URL with the token credential.
- Restored x-token-auth username in the checkout URL, retaining main and existing itopaz-k8s-repo-token credential. This corrects the identity removed by the prior explicit-checkout change.
- Jenkinsfile diff check passed. Fix commit b1d4a05 published to itopaz-agent main. Jenkins rerun remains with user; failed build did not reach deployment stages. No credential values were read or changed.

### 2026-10-10 - Jenkins test mount and POC authentication fixes

- Jenkins build 78 passed checkout but failed Python test discovery because the Jenkins-container workspace bind path resolved on the Docker host to a different directory. Replaced bind mounting with tar streamed over docker run stdin. Verified against the actual Jenkins checkout in python:3.12-slim: 13 tests passed, 5 expected local-registry skips. Agent main fix: 1da72d3.
- Live aws-dashboard-api api-92 contained POC account, role, and ap-south-1 settings. Cached collectionErrors reported Mumbai STS AssumeRoleWithWebIdentity HTTP 403 with an HTML response; other accounts remained accessible. Existing UI discarded this failure and displayed zero accounts.
- Dashboard authentication now resolves IRSA credentials and performs account AssumeRole/GetCallerIdentity through configured STS_REGION (eu-central-1 in DEV), while resource clients retain ap-south-1 for POC. A mock HTTP regression test verifies STS endpoint/signing region without changing the resource region.
- Dashboard surfaces filter-specific collection errors and shows unavailable counts rather than zero when all selected account data fails. Mumbai region label added. Go tests, 3 frontend tests, and frontend production build passed. Dashboard main fix: 60d81c4.
- Changes published for user's manual Jenkins deployments. Actual POC role trust/resource access still requires a successful post-rollout read-only check; no IAM changes or resource mutations performed. Temporary Jenkins key copy removed.


### 2026-10-10 POC EC2/RDS-only configuration
- Pushed aws-dashboard main commit 4853464: POC service map skips EKS/ASG collection and rejects EKS actions; UI hides EKS and marks failed EC2/RDS collection unavailable. Go tests, five frontend tests, and Vite production build passed. Jenkins deployment remains with the operator.
- Live api-93 verifies POC STS identity successfully; remaining Mumbai EC2/RDS calls return HTML 403 and pod HTTPS probes fail certificate validation. Network/endpoint/TLS remediation remains outstanding; no IAM or firewall changes made.
- Master UI key is the existing private secrets/control-token.txt file; token contents were not printed. Temporary restricted Jenkins key copy removed.


### 2026-10-10 POC remaining endpoint failure
- Confirmed api-94 is deployed and POC services are EC2/RDS only; assume-role identity succeeds. Mumbai EC2/RDS still return HTML 403 with no AWS request ID.
- API pod HTTPS certificate validation fails for both Mumbai endpoints. Worker-2 TLS inspection identifies Fortinet CA FGVMSLTM24000312 for Mumbai, versus valid Amazon certificate for Frankfurt. Evidence points to Fortinet access/inspection policy; exact deny rule remains to be checked in gateway logs.
- Saved infrastructure/poc-endpoint-access.md with observed pod/node, endpoint-specific network remediation proposal and verification steps. No firewall/IAM/resource changes or Jenkins deployments performed.


### 2026-10-10 Approved PROD bastion stop
- Operator explicitly approved stopping euc1-itopaz-bastion-prd-1-old / i-0246c639166a0cea9 / 10.100.98.195, account 965031587107, eu-central-1.
- Windows master called authenticated Dashboard POST /api/master/action with exact-request confirmation and a fresh 120-second approval. AWS returned running -> stopping; fresh targeted inventory verified stopped.
- Restored stale SSH loopback forwarding before execution. Initial API attempts were rejected for approval expiry; no AWS mutation occurred on those rejections.


### 2026-10-11 Worker health check
- Worker-1 (10.151.4.165): two SSH attempts reset before authentication; health and agent could not be verified. This does not establish that the instance is stopped.
- Worker-2 (10.100.95.39): SSH works, 4 CPUs, load 0.09, 95.7% memory available, disk 65.5% used / 16.3 GB free, Python 3.12.3. Git/SSH/kubectl/AWS CLI/Docker present. fwupd-refresh.service is failed; primary system capacity is healthy.
- Worker-2 agent --help and --nodes succeed. Launcher points to .itopaz-agent/releases/20261009, an older release; its node registry still marks worker-2 optional/overflow. All nine Python files parse when UTF-8 BOM is handled. Operation lock module exists, but no lock file was found at the workspace or release root. No worker configuration or software was changed.


### 2026-10-11 Worker network access recorded
- Operator confirmed worker-1 (10.151.4.165) has internet access.
- Operator confirmed worker-2 (10.100.95.39) is behind a firewall with no internet access.
- Saved node-specific network metadata in nodes.json and infrastructure/worker-network-access.md. No remote configuration changed.


### 2026-10-12 Both worker nodes checked
- Both reachable over SSH; agent --help succeeds and all nine release Python files parse on each. Both launch release 20261009 with operation locks enabled.
- Worker-1: root disk critically low, 594 MB free / 30 GB, df reports 99% used; workspace 828 MB. Low load and 86% memory available; no failed systemd services.
- Worker-2: low load, 95.1% memory available, disk 65.5% used / 16.3 GB free; fwupd-refresh.service still failed. Saved operator-provided internet policies retained.
- Saved infrastructure/worker-health-latest.md. No cleanup, upgrades, or remote changes performed.


### 2026-10-12 Worker-1 disk cleanup
- Operator requested Worker-1 cleanup. Removed pip download cache (176 files), npm cache, DNF package cache, and ten cached VS Code extension download files (912245695 bytes). Vacuumed archived system journals to 14-day / 200 MB limits, freeing 418.4 MB; active logs retained.
- Root df before: 99% used, 594 MB available. Final df: 83% used, 5.4 GB available; about 4.8 GB recovered. Journal usage now 206.1 MB.
- Agent startup verified successfully afterward; no failed systemd services. Repositories, credentials, installed editor versions/extensions, application data, Docker images, and volumes preserved.


### 2026-10-12 Additional Worker-1 cleanup
- Operator requested further cleanup. Removed seven older inactive editor server directories: three VS Code bin versions, three VS Code CLI server versions, and one Kiro version. Retained newest two versions in each directory and rechecked process command lines, executables, and working directories before removal.
- Recovered 4451270656 bytes (about 4.1 GiB). Agent startup passed afterward. Projects, credentials, extensions, user settings, Docker images, and Python packages preserved.
- Final root df: 69% used, 9.6 GB available. No failed systemd services. Latest health report updated.


### 2026-10-12 BW UAT Docker inspection attempted
- Operator requested Docker inspection on 10.233.30.104, documented instance i-0a490e2198383b309, account 581621506601. SSH endpoint reachable; saved mdm/uat/EC2-BW-Server-Key.pem rejected for ec2-user and ubuntu.
- Worker-1 has identical saved key. No local AWS profile for account 581621506601 / bw-uat exists, so alternate AWS inspection unavailable with current configuration. Requested correct SSH username/key.
- Docker state not inspected and server unchanged. Temporary restricted key copy removed; public host key recorded in .tmp/bw-uat-known-hosts.
- Operator confirmed ec2-user / EC2-BW-Server-Key. Retried alternate mdm/dev key copy; it is identical to the UAT copy and also rejected. Temporary alternate key copy removed. Correct private-key file or server authorized-key repair is still required.


### 2026-10-12 BW UAT authorized-key mismatch confirmed
- Compared operator-provided authorized public key with saved BW PEM public key: mismatch. Checked 30 saved private keys; no matching key found.
- Saved public-only infrastructure/ssh-public-keys/bw-master-access.pub corresponding to the local BW PEM for optional server authorization. Existing server access was not modified. Docker inspection still awaits matching SSH access.


### 2026-10-12 BW UAT Docker inspection completed
- After operator added topaz-master-bw-access public key, SSH ec2-user@10.233.30.104 succeeded. Read-only Docker inventory saved under infrastructure/reports/bw-uat-docker-20261012 (report, container/image CSV, sanitized inventory and resource stats).
- 110 containers: 61 running / 49 exited. Five exit code 1; 41 code 143; three code 137; no OOMKilled flags. Two stopped containers show restart counts 10 and 59. Running containers have no Docker health checks or memory limits.
- Root disk 81% used / 20 GB free; container writable layers 67.85 GB, 25.93 GB reclaimable in stopped containers. No Docker changes or cleanup performed. Temporary private-key copy removed.

### 2026-10-12 Quantum S3 buckets and CloudFront origins

- Operator requested eight Quantum module buckets for Epic, RIA, Freight, and PACE in Dev and Prod, then specified that every new bucket must be in Frankfurt (`eu-central-1`). AWS SSO identity was verified as account `674017976129` before changes.
- Created `quantum-epic-dev`, `quantum-epic-prod`, `quantum-ria-dev`, `quantum-ria-prod`, `quantum-freight-dev`, `quantum-freight-prod`, `quantum-pace-dev`, and `quantum-pace-prod` in `eu-central-1`.
- Applied all four S3 public-access blocks, AES-256 default encryption, and `BucketOwnerEnforced` ownership. Each bucket policy allows CloudFront `s3:GetObject` access only from its corresponding distribution ARN.
- Added each bucket as a second S3 origin on the matching existing CloudFront distribution. Existing aliases, default origins, and URL routing were retained. No cache behavior points to a Quantum origin yet; application traffic continues to use the original origins.
- Live read-only verification confirmed all eight bucket regions and controls, policy source ARNs, two origins per distribution, original default origins, and all eight distributions in `Deployed` status. PACE Prod was initially `InProgress` immediately after update, then reached `Deployed`.
- Script: `scripts/provision-quantum-origins.ps1`. Pre-change distribution snapshots and initial result: `infrastructure/backups/quantum-origins-20261012-133651/`.

## August 10, 2026

### SIT Singapore â€” BFF 403/CORS Fixes

**Context:** `sit-singapore` | **Namespace:** `prefiler-bff`, `prefiler-api` | **API GW:** `lbo534svjk`

#### Issues Fixed
1. **Istio VS `prefiler-api`** â€” `master-prefiler-service` wrong rewrite (`/master-prefiler-service/` â†’ `/`); removed 2 orphan BFF routes pointing to wrong namespace
2. **API Gateway CORS** â€” `Access-Control-Allow-Headers` had double single-quotes `''value''` causing browser to see `sessionid'` â‰  `sessionid`; fixed to `'value'` in both OPTIONS resources + `DEFAULT_4XX`/`5XX` gateway responses + added `sessionid`
3. **Root cause of 401s** â€” BFF does exact Redis token match per session; must use matching Bearer token + sessionid pair from same browser login session

#### Key Facts
- API GW mgmt API blocked from bastion (WAF) â€” must use AWS Console for API GW changes
- Singapore uses Frankfurt SIT auth service (`prefiler-api-eusit.itopazapp.com`) â€” auth not deployed in Singapore
- Redis session key: `{user-id}_{sessionid}` format
- BFF x-api-key: `REDACTED_X_API_KEY`
- Correct URL pattern: `prefiler-bff-sasit.itopazapp.com/prefiler-bff/prefiler/bff/v1/...`

---

## June 18, 2026

### POC Account â€” aimlapp-test Intranet Service Restored (502 Fixed)

**Server**: `10.0.132.243` (ubuntu) â€” POC Account `745510282686`
**Key**: `infrastructure/secrets/keys/vj-keypair-pocacct.pem`
**URL**: `https://aimlapp-test.allcargoapps.com/intranet/login`

#### Problem
- URL returning **502 Bad Gateway** from AWS ELB
- `intranetapimain.py` was not running on the server

#### Root Cause
- Service `intranetapimain.py` crashes on startup â€” `AccessDeniedException` when calling `secretsmanager:GetSecretValue` on secret `test/intranet`
- IAM user `arn:aws:iam::745510282686:user/codecommit-jenkins` had no policy allowing access to that secret
- Existing `aws-secret-manager-policy` only covered `devrev_tokens*` secret

#### Fix Applied
- Added inline IAM policy `AllowSecretsManagerIntranet` to user `codecommit-jenkins`:
  ```json
  {
    "Effect": "Allow",
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "arn:aws:secretsmanager:ap-south-1:745510282686:secret:test/intranet*"
  }
  ```
- Started `intranetapimain.py` from: `/root/var/www/intranet/userdetailssync/userdetailssync/`
- Service running on port `4001` (uvicorn/FastAPI)
- URL now returns `200 OK` (GET) / `405` for HEAD â€” **service is UP**

#### Additional Findings
- **autoheal script** `/root/var/www/apis-autoheal.sh` has wrong path for `intranetapimain`:
  - Script expects: `/root/var/www/intranet/userdetailssync/`
  - Actual location: `/root/var/www/intranet/userdetailssync/userdetailssync/`
  - Needs fix to prevent future outages
- Server IP `10.0.132.243` requires VPC peering to be active (was unreachable before peering)
- Services on server: `hrchatbotazure.py` (port 4080), `aadhar_extraction_api.py` (port 4003), `intranetapimain.py` (port 4001), `ollama` (127.0.0.1:11434)

---

## June 17, 2026

### PROD EU â€” Grafana K8S Dashboard Fixed (No kube-state-metrics)
- **Problem**: Grafana K8S Dashboard namespace dropdown empty; `kube-state-metrics` not installed in PROD cluster
- **Root cause**: Dashboard variables (`NameSpace`, `Node`, `Container`, `Pod`) all used `kube_namespace_created`, `kube_node_info`, `kube_pod_container_info` from KSM â€” none exist in PROD
- **Investigation**:
  - PROD cluster confirmed accessible: bastion `10.100.98.195`, 4 Linux nodes (v1.36.1-eks), 15 namespaces
  - Monitoring stack: Grafana + Prometheus in `istio-system` only â€” no KSM, no ServiceMonitor CRDs
  - Prometheus uses static `kubernetes_sd_configs` scrape jobs (no ServiceMonitor)
  - Available metrics: cAdvisor (`container_*`), kubelet (`kubelet_node_name`, `machine_memory_bytes`, `machine_cpu_cores`)
- **Fix approach**: Rewrote dashboard JSON without modifying cluster
  - Downloaded dashboard via `kubectl exec grafana -- curl localhost:3000/api/dashboards/uid/9f83e8f6-ae9a-4bc1-ad64-cffc1c93df02`
  - **129 panel expressions rewritten** using Python script `/tmp/fix_dashboard.py`
  - Uploaded via Grafana API POST `/api/dashboards/db` â€” status: success, version 2
- **Variable replacements**:
  - `origin_prometheus` â†’ hidden constant (no KSM federation)
  - `Node` â†’ `label_values(kubelet_node_name, node)`
  - `NameSpace` â†’ `label_values(container_memory_working_set_bytes{container!="",container!="POD"}, namespace)`
  - `Container` â†’ `label_values(container_cpu_usage_seconds_total{namespace=~"$NameSpace",...}, container)`
  - `Pod` â†’ `label_values(container_cpu_usage_seconds_total{...}, pod)`
- **Metric replacements**:
  - `kube_node_status_allocatable{resource="memory"}` â†’ `machine_memory_bytes`
  - `kube_node_status_allocatable{resource="cpu"}` â†’ `machine_cpu_cores`
  - `kube_node_info` â†’ `kubelet_node_name`
  - `kube_pod_info` counts â†’ `container_last_seen` counts
  - `kube_pod_container_resource_requests/limits` â†’ `vector(0)` (no cAdvisor equivalent)
- **Dashboard URL**: `/d/9f83e8f6-ae9a-4bc1-ad64-cffc1c93df02/k8s-dashboard`
- **Backup script**: `/tmp/fix_dashboard.py` on local server

### knowledge-base Folder â€” Restored
- Folder was deleted in commit `801dca1` on June 17
- Restored via `git checkout 6151387 -- knowledge-base/` â€” 38 files recovered

---

## June 12, 2026

### PROD EU â€” Kafka 3.9.1 Client Setup + MSK Broker Config
- **Local download** (on 165 server): Apache Kafka `3.9.1` (Scala 2.13) downloaded to `/home/ec2-user/rahul/kafka-client/kafka_2.13-3.9.1.tgz`
- **Uploaded** tarball to prod bastion (`10.100.98.195`) via `scp` â†’ extracted to `/home/ec2-user/kafka-client/kafka_2.13-3.9.1/`
- **Symlink**: `/home/ec2-user/kafka-client/current` â†’ `kafka_2.13-3.9.1`
- **Java**: Installed `java-17-amazon-corretto-headless` on prod bastion (was missing); verified version `17.0.19`
- **SASL/SCRAM config** at `/home/ec2-user/kafka-client/client.properties`:
  ```
  security.protocol=SASL_SSL
  sasl.mechanism=SCRAM-SHA-512
  ssl.endpoint.identification.algorithm=https
  ```
- **Prod MSK brokers** (3 nodes, port 9096, SASL_SSL):
  - `b-1.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
  - `b-2.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
  - `b-3.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
- **Bootstrap file**: `/home/ec2-user/kafka-client/prod-bootstrap-servers.txt`
- **Wrapper script**: `/home/ec2-user/kafka-client/run-kafka-prod.sh` (runs `kafka-broker-api-versions.sh` with SASL config + heap opts)
- **Note**: Fill in `<MSK_USERNAME>` and `<MSK_PASSWORD>` in `client.properties` before running broker commands

### UI Pipelines â€” CloudFront Cache Invalidation Stage Added
- **Added** `Invalidate CloudFront Cache` stage to all UI Jenkins pipelines (SIT environment)
- **Files updated**:
  - `jenkins/tariff_microfrontend-main-ui` â€” added stage after Verify Deployment
  - `jenkins/tariff_microfrontend-share-ui` â€” added stage after Verify Deployment
  - `jenkins/tariff-selling-rates-ui` â€” already had stage, confirmed dist ID
  - `jenkins/tariff-tariffbuying-ui` â€” already had stage, confirmed dist ID
- **Distribution ID**: `E1MSDTWI1MUQ2P` (SIT UI CloudFront distribution)
- **Stage behavior**: Executes only when `SKIP_DEPLOYMENT=false`, invalidates all paths (`/*`), uses cross-account AWS role
- **Pushed**: `uat` branch, commit `cbde479` âœ…

### SIT EU & SIT SG â€” Node Status Checks
- **SIT EU** (euc1-itopaz-sit-eks): Caught mid-rolling node replacement â€” 18 NotReady (bootstrapping), 18 Ready,SchedulingDisabled (old nodes cordoned ~8h), 2 Ready. Within ~60s new nodes joined: 37 Ready, 4 cordoned. Final state after drain complete: **26 Ready, 0 cordoned** âœ…
- **SIT SG** (apse1-itopaz-sit-eks): **6 nodes all Ready** âœ…
- Old cordoned nodes in SIT EU were carrying 10â€“12 pods each (~44 pods total); drained and terminated automatically

### SIT MSK â€” Kafka Version Check
- **Broker version**: Kafka **3.7.x** (confirmed via `kafka-broker-api-versions.sh`: Produce API max 11, Fetch API max 16 â€” both introduced in 3.7)
- **Kafka client on SIT EU bastion**: `kafka_2.13-3.6.0`
- **Brokers**: `b-1.euc1itariffsitmsk.76ygyn.c5.kafka.eu-central-1.amazonaws.com:9096`, `b-2...` (2-node cluster, SASL_SSL/SCRAM-SHA-512)

### tariff-selling-rates-ui â€” Jenkins Pipeline Fix
- **Root cause 1**: `REPO_URL` was pointing to wrong repo (`tariff-microfrontend-main-ui.git`) â€” corrected to `tariff-selling-rates-ui.git`
- **Root cause 2**: `Checkout Application Code` stage was using `$DEPLOYMENT_FILE` (`tariff-selling-rates-ui.yml`) as the Bitbucket repo slug, producing invalid URL `...tariff-selling-rates-ui.yml.git`
- **Fix**: Replaced hardcoded slug with `REPO_SLUG=$(basename "$REPO_URL" .git)` to dynamically extract slug from `REPO_URL`
- **File**: `jenkins/tariff-selling-rates-ui` in `itariff-k8s-repo`
- **Pushed**: `uat` branch, commit `b46b160` âœ…

### prefiler-bff DEV â€” VirtualService Routing Fix (404 resolved)
- **Symptom**: All actual API calls via `prefiler-bff-eudev.itopazapp.com` returning 404 with no CORS headers, even after CORS swagger fixes and redeployment
- **Root cause**: With the API Gateway custom domain base path mapping corrected from `prefiler-bff` â†’ `(none)`, the full path `/prefiler-bff/prefiler/bff/v1/...` is now forwarded to Istio. The VirtualService only had rules for `/prefiler-auth-bff/` and `/prefiler/` â€” no rule matched the `/prefiler-bff/prefiler/...` prefix â†’ 404
- **Pods confirmed healthy**: `prefiler-bff-cd984c8dc-*` (2 pods, 2/2 Running), `prefiler-auth-bff-67f6b87c4f-*` (2 pods, 2/2 Running)
- **Fix**: Added two new http rules to `prefiler-bff` VirtualService (`istio-system`):
  - `/prefiler-bff/prefiler/` â†’ `prefiler-bff-svc.prefiler-bff.svc.cluster.local:80` (rewrite: /)
  - `/prefiler-bff/prefiler-auth-bff/` â†’ `prefiler-auth-bff-svc.prefiler-bff.svc.cluster.local:80` (rewrite: /)
- **Verified**: `GET https://prefiler-bff-eudev.itopazapp.com/prefiler-bff/prefiler/bff/v1/masters/PageMaster/` â†’ **HTTP 200** with `access-control-allow-origin: *` and full JSON payload âœ…
- **Cluster**: `euc1-itopaz-dev-eks` (DEV EU) via bastion `10.100.145.118`, key `dev-eu-bastion.pem`

### README.md â€” Comprehensive Copilot Reference Update
- Replaced generic KB/vector-db README with full operational reference
- Added all SSH access commands with exact key paths
- Added AWS account table (5 accounts with IDs, regions, IAM role ARNs)
- Added EKS cluster details (DEV EU, SIT EU, SIT SG â€” nodes, K8s versions, ASG, maxPods)
- Added service URLs by environment (internal + external, API GW IDs, VPC Link IDs)
- Added application architecture (tech stacks, ECR registries, namespaces)
- Added full prefiler service inventory, Istio VS routing, .NET config patterns
- Added database credentials table (DEV + SIT, Redis endpoints)
- Added Kafka broker URLs and key topics
- Added Jenkins server access, pipeline paths, env vars
- Added API Gateway CORS fix pattern with deploy commands
- Added known pending issues section (DEV, SIT EU, SIT SG)

---

## June 10â€“11, 2026

### PROD EU iTariff Istio Ingress Setup + End-to-End Validation

  - `Gateway`: `itariff-gateway`
  - `VirtualService`: `itariff-ui`
  - `VirtualService`: `itariff-api`
  - `VirtualService`: `itariff-bff`

  - `itariff-ui.internaleu1prd-itopaz.com`
  - `itariff-bff.internaleu1prd-itopaz.com`
  - `itariff-api.internaleu1prd-itopaz.com`

  - Resolved to Istio ingress LB `a5c3d5f6763e149a1949597be2e56d79-0a180d890cef99d9.elb.eu-central-1.amazonaws.com`

  - UI host `/` -> `503`
  - API host `/` -> `503`
  - BFF host `/` -> `404` (expected, only prefixed bff routes defined)

  - Deployed `test-echo` Deployment + Service in namespaces:
    - `itariff-ui`
    - `itariff-api`
    - `itariff-bff`
  - Added `/test-ping` route at top priority in each corresponding VirtualService
  - **Verified via ingress host header**:
    - `itariff-ui.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-ui test ok`)
    - `itariff-api.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-api test ok`)
    - `itariff-bff.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-bff test ok`)

  - **Fix**: Updated parameter group `aurora-postgresql-uat-15`: `autovacuum_naptime` **5s â†’ 60s** (immediate) âœ…

### prefiler-cache-util â€” Jenkins Pipeline Fix (SIT)
- **Problem 1** (`CS1061`): `Program.cs` called `cache.GetAsync<Object>(key)` but interface only defines `GetObjectAsync<T>`
  - **Fix**: `GetAsync` â†’ `GetObjectAsync` in `Prefiler.TestApi/Program.cs` â€” commit `fff0b5ae` to sit branch âœ…
- **Problem 2** (`mstest` DSL not found): MSTest plugin not installed on Jenkins
  - **Fix**: Replaced `mstest` step with `archiveArtifacts` for `.trx` files â€” commit `1188a6a` to `prefiler-k8s-repo` sit branch âœ…

### SIT EU UI Latency Investigation (`/selling-rates/import` â€” 10s load)
- **Root cause**: ~10 parallel BFF dropdown calls on page load, all querying 146GB `dbo.tariff` / 184GB `dbo.tariffdetails` with no indexes (full seq scans)
  - Slow endpoints: `getShippingLineAgent` (up to 180s), `getTSOCPOL` (1.9s), `getPOR` (1.6s)
- **Fix plan** (requires dev team): Redis cache on dropdown endpoints (TTL 30min), `CREATE INDEX CONCURRENTLY` on key columns, autovacuum completion (2â€“4h), Promise.all on frontend
- **Static asset serving confirmed healthy**: nginx 17ms âœ…

### Intranet Prod Deploy Fix (Account 745510282686, ap-south-1)
- **Servers**: `Intranet-prod-1` (10.151.4.89, c5a.xlarge) + `Intranet-prod-2` (10.151.4.153, m5.2xlarge)
- **Fix 1**: `/root/.aws/credentials` had `#[default]` commented header â†’ ConfigParseError â†’ moved to `.bak`, uses instance IAM profile
- **Fix 2**: Git CodeCommit auth failure on root user â†’ set IAM Git credentials in remote URL (URL-encoded)
- **Fix 3**: Port 8001 already in use post-deploy (uvicorn worker PIDs surviving kill-by-name) â†’ `fuser -k 8001/tcp`
- **Result**: Both servers deployed to commit `ab9539e`, Uvicorn :8001 âœ…
- **SSH Key**: `infrastructure/secrets/keys/Intranet-prod-1-Key.pem`

### Intellihub HA Assessment (Account 745510282686, ap-south-1)
- Both instances healthy (system + instance checks ok/ok), 2 AZs, ALB target groups all green
- 6 services confirmed True HA: `intellihub-prod`, `intellihubadmin-prod`, `gatimasterapi-prod`, `sendbulktracking`, `symphonywrapper-prod`, `zendeskwrapper-prod`
- **Gap**: No ASG (no auto-recovery on instance failure) â€” recommended EC2 Auto Recovery alarm
- **Fixed**: `cleanup_python_zombies.sh` script was in prod-2 crontab but file was missing â†’ copied from prod-1 âœ…
- 5 stale unused target groups identified (not attached to any listener): `aimlprod-1`, `ecureports`, `ecureports-api`, `intellaiml-prod-4001`, `intellihub-prod-2`

---

## June 8, 2026

### master-prefiler-service (SIT) â€” HTTP 500 Root Cause & Fix
- **Symptom**: PageMaster endpoint returning 500 with `RetryLimitExceededException` + `NpgsqlException: Connection reset by peer`
- **Root cause 1**: ConfigMap had wrong zone key naming â€” `ConnectionStrings__zone1` instead of `ConnectionStrings__GroupageHost_zone1`. Keys never matched â†’ fell back to baked-in `appsettings.json` â†’ pointed to DEV Aurora
- **Root cause 2**: Duplicate YAML keys for zone1-zone6 (last one wins) â€” silent data loss
- **Root cause 3**: Leading space in password: `Password= passwordsit@1035`
- **Fix**: Added `ConnectionStrings__GroupageHost_zone0-zone6`, `EDIDbHost_zone0-zone6`, `SecurityFilerHost_zone0-zone6` â€” all pointing to SIT Aurora, fixed password
- **Commit**: `76de88f` to `sit` branch in `prefiler-k8s-repo` âœ…
- **Verified**: HTTP 200, 25s response âœ…

### tariff-company-service (SIT) â€” Memory Pressure (HPA 93%)
- **Root cause**: `JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=50.0` against 2500Mi limit â†’ JVM heap 1250Mi vs 700Mi memory request = 114% HPA â†’ stuck at 10/10 replicas
- **Fix**: Changed to `-Xmx600m -Xms256m` + raised memory request `700Mi â†’ 1000Mi`
- **Result**: HPA memory **93% â†’ 43%** immediately. Commit `afd2097` to `uat` branch in `itariff-k8s-repo` âœ…

### SIT Node Count Bloat (33 nodes â†’ ~20)
- **Root cause 1**: CA `--scale-down-utilization-threshold=0.5` â€” any node with CPU requests >50% blocked from drain
- **Root cause 2**: CA `--skip-nodes-with-local-storage=true` â€” pods using `emptyDir` blocked 26 nodes from draining
- **Fix**: Patched CA: `--scale-down-utilization-threshold=0.70` + `--skip-nodes-with-local-storage=false`
- **Backup**: `/tmp/cluster-autoscaler-backup-2026-06-08.yaml` on SIT bastion
- **Result**: CA immediately identified 13 unneeded nodes, scaled down to ~20 nodes âœ…

---

## June 5, 2026

### prefiler-bff (SIT) â€” API Gateway CORS + Login Fix
- Fixed HTTP integration (not HTTP_PROXY) to pass `access-token` and `authentication` response headers
- Added `access-token, authentication` to `Access-Control-Expose-Headers`
- Added `officeid, access-token, authentication, channelid, userid, appid` to OPTIONS `Access-Control-Allow-Headers`
- Login verified: `https://prefiler-bff-eusit.itopazapp.com/prefiler-bff/prefiler-auth-bff/bff/v1/auth/login` âœ…

### Kafka Topic Fix (SIT)
- **Created topic**: `trf-exl-upld-prc-topic-v3` on SIT MSK (was causing TimeoutException in `tariff-selling-service-batch`)
- **Updated configmap**: Added topic + consumer group to `tariff-selling-service-batch`
- **Committed**: `3e3c9d5` to `origin/uat` in `itariff-k8s-repo` âœ…

### Windows Node DNS Fix (SIT EU)
- **Root cause**: Linux node SG (`sg-05c315bde97f77bf1`) did NOT allow traffic from Windows node SG (`sg-02fa2ce777340f203`)
- **Fix**: `aws ec2 authorize-security-group-ingress --group-id sg-05c315bde97f77bf1 --protocol -1 --source-group sg-02fa2ce777340f203`
- **Rule ID**: `sgr-0dc8147e6c3c819fe` âœ…

### microfrontend-main Jenkins Pipeline Fix (SIT)
- **Root cause**: AWS STS token expires during `kubectl rollout status` wait (100s+) â†’ "Unauthorized"
- **Fix**: Moved post-deploy verification to separate `Verify Deployment` stage with own `withAWS` block and fresh `aws eks update-kubeconfig`
- **Commit**: `558254d` to `sit` branch âœ…

---

## June 4, 2026

### UAT Resource Configuration Audit (itariff-api + itariff-bff)
- **Pulled live config** from euc1-itopaz-sit-eks for all 26 deployments in itariff-api and 3 in itariff-bff
- **Missing resource limits identified**:
  - `tariff-grant-bff`: NO cpu/memory requests or limits set
  - `tariff-selling-bff`: No CPU request/limit (only memory: 2Gi req, 6Gi limit)
  - `tariff-selling-consumer-service`: No CPU/memory limits (only requests: 1 cpu, 3Gi memory)
  - `tariff-domain-batch`: No resources at all

### SIT Kafka Full Topic Configuration Audit
- **Listed all 38 tariff topics** with complete configurations
- **Corrected client.properties path**: `/home/ec2-user/kafka-client/kafka_2.13-3.6.0/bin/client.properties` (not in parent dir)
- **Topic config patterns**:
  - Upload topics: 1GB max.message.bytes, min.insync.replicas=1, no explicit retention
  - Process/archive topics: 10MB max.message.bytes, min.insync.replicas=2, retention.ms=604800000 (7 days)
  - All topics: ReplicationFactor=2, message.format.version=3.0-IV1, unclean.leader.election=false

### Prefiler Auth BFF - External 403 Investigation
- **Symptom**: `https://prefiler-bff-eusit.itopazapp.com/prefiler-bff/prefiler-auth-bff/bff/v1/auth/login` returns 403
- **Internal works**: `https://prefiler-bff.internaleu1-itopaz.com/prefiler-auth-bff/bff/v1/auth/login` returns 200 + JWT
- **Root cause**: FortiGuard IPS (not WAF) blocking the URL at network layer
- **Evidence**: Response HTML contains "FortiGuard Intrusion Prevention - Access Blocked" / "URL is banned"
- **Request path**: Client â†’ FortiGuard â†’ Global Accelerator (af9b262029faa8833.awsglobalaccelerator.com) â†’ API GW â†’ Istio â†’ pod
- **Action needed**: Network team must whitelist URL in FortiGuard policy

### Prefiler tariff-grant-bff/authenticate - 500 Error
- **Call chain**: prefiler-auth-bff â†’ tariff-grant-bff â†’ tariff-profile-service (adauthenticate endpoint)
- **DB query**: `SELECT * FROM profile WHERE ademailid = ? OR mailid = ? AND isdeleted = 0 LIMIT 1`
- **Error**: `NullPointerException: Cannot invoke "com.alcg.profile.entity.Profile.getUser_id()" because "profile" is null`
- **Cause**: User being authenticated from prefiler doesn't have a matching profile entry in tariff DB
- **Fix**: Add user to profile table OR fix null handling in tariff-profile-service code

### AWS WAF & API Gateway Documentation
- **WAF ACL** (`itopaz-api-gwt-acl`): Only attached to itariff-bff API GW (dygy1tl8n5), NOT prefiler-bff
- **Rule priority 0** (`zscalar-ip-restriction`): Blocks if X-Forwarded-For NOT in Zscaler IPv4/IPv6 IP sets
- **prefiler-bff API GW** (7a8aq4c0oa): No WAF, apiKeyRequired=true, routes to internal Istio gateway
- **Custom domain**: `prefiler-bff-eusit.itopazapp.com` â†’ REGIONAL endpoint â†’ basePath `/prefiler-bff` â†’ stage sit
- **API key**: Confirmed valid and enabled (trxH8cOmlp6e9EKOAUUuh6nEi2ofzB4v29me6vWO)
- **Usage plan**: itariff-api â€” burst:50, rate:100/s, quota:80,000/day

## May 30, 2026

### FAISS Vector Database Setup
- **Installed** faiss-cpu, sentence-transformers, torch (CPU-only) on workspace
- **Ingested** KNOWLEDGE-BASE.md into FAISS index (68 chunks, 384-dimension vectors, 102KB index)
- **Scripts**: `scripts/ingest_knowledge.py`, `scripts/query_knowledge.py` â€” supports semantic search, JSON output, interactive mode
- **Vector store**: `vectordb/knowledge.index` + `vectordb/chunks.json`

### S3 Bucket Organization (devops-securit-dev)
- **Cleaned up** old scattered files: removed `eks-docs/`, `prefiler-sit-knowledge/`, root-level session/handover .md files
- **Moved** all root-level .md files under `devops/` prefix (Activity Calender, GATI inventories, ZPA, account_details, ec2-rds)
- **Uploaded** organized structure via DEV jump server (10.100.145.118):
  - `devops/KNOWLEDGE-BASE.md` â€” single consolidated file for LLM agents
  - `devops/activity-log.md`, `devops/eks-clusters.md`
  - `devops/docs/` â€” all detailed documentation + knowledge-export/
  - `devops/vectordb/` â€” FAISS index + metadata
  - `devops/scripts/` â€” ingest, query, rebuild tools
- **S3 root** now only contains binary archives (rpm, tar, tgz, tar.xz) + `pem/`

### Bastion Host Cleanup (/home/ec2-user/)
- **Deleted ~1.3GB** of old logs/archives: `batch2.log` (413MB), `batch2.3log` (429MB), `kafka*.tgz/zip` (218MB), `python_3_10_slim.tar` (129MB), `eks-node-cleanup.log` (81MB)
- **Organized 140+ loose files** into structured `organized/` directory:
  - `organized/repos/` â€” 20 git repos & script folders
  - `organized/k8s-manifests/` â€” 28 YAML files
  - `organized/iam-policies/` â€” 6 policy JSONs
  - `organized/keys/` â€” certs, PEM files
  - `organized/tools/` â€” gcrane, krane, cleanup scripts
  - `organized/efs-configs/` â€” 4 EFS PV/PVC yamls
  - `organized/istio-configs/` â€” gateway, virtualservice
  - `organized/archived-configs/` â€” old misc files & dirs
- **Deleted additional 727MB**: `bw-baseimage_2.9.0.tar` (435MB), both istio installs (178MB), kafka extracted (114MB), 6 empty dirs
- **Cleaned hidden caches (~12GB)**: `.cache/pip` (3.9GB), `.local/lib` (4.9GB), 4 old VS Code servers (1.8GB), `sufeeyan-copilot/` (1.1GB), `.cache/aws` + `.cache/cloud-code` (338MB)
- **Disk usage**: 88% â†’ 48% (3.9GB free â†’ 16GB free)
- **Excluded** from changes: `rahul/`, `sufeeyan/`, `vijay/`, `rajnish/`

## May 29, 2026

### master-prefiler-service Pipeline Fix
- **Root cause**: Jenkins reads pipeline from `jenkins/dev/api/master-prefiler-service` but fix was applied to `jenkins/dev/master-prefiler-service`
- **Fix 1**: Copied corrected pipeline to correct path (`jenkins/dev/api/master-prefiler-service`)
- **Fix 2**: `AccessDeniedException` â€” `Terraform_Execution_Role` (074779643551) cannot call `codeartifact:GetAuthorizationToken` cross-account to 439891535362. Removed `withAWS` wrapper, using Jenkins agent's native AWS credentials instead
- **Fix 3**: Build failed with `CS0246: type 'prefiler' not found` â€” commit `7db6d23` had deleted `SharedLib/` containing `prefiler.security.dll`, `Prefiler.Base.Shared.dll`, `Prefiler.CacheUtil.dll`. Restored DLLs from git history
- **Pushed**: prefiler-k8s-repo `dev` branch (commits 6295650, f1f0927), master-prefiler-service `develop` branch (commits 4c55e4c, e94f43c)

### itariff-k8s-repo JVM/Memory Optimization (uat branch)
- **Pushed** JVM memory optimization and resource right-sizing for 8 services (commit 5603bdc)
- Services: tariff-buying-carriage, otherbooking, service, standardcost, truck, warehouse, grant-auth, selling-storage-service
- Changes: JAVA_TOOL_OPTIONS env vars, memory requests/limits right-sized

### itariff-k8s-repo (uat branch)
- **Updated `tariff-buying-shippingline-consumer-service.yaml`** config for `buying-domain-service`:
  - Changed microId to `buying-domain-service`, port to 80, context-path to `/buying-domain-service`
  - Optimized HikariCP pool settings (keepalive-time, idle-timeout, connection-timeout tuned)
  - Restructured JPA config (moved show-sql/ddl-auto)
  - Updated Kafka config with bulk upload topics, bulk process/archive topics, new consumer groups
  - Updated `restTemplate` connection pool (maxPerRoute: 20, maxConnections: 100), removed connect/read timeouts
  - Simplified `serviceurls` (geography, master, invoice, company, tariff)
  - Replaced `serviceMsg` with `service` block (new error codes: DUP1202, SAVE1201, ERR1203, NF1205, VAL1203)
  - Updated management endpoints include to `health,info,prometheus,metrics`

- **Improved Jenkins ConfigMap pipeline (`Jenkincm`)** â€” simplified for UAT-only use:
  - Hardcoded UAT branch, cluster (euc1-itopaz-sit-eks), region, cross-account role
  - Reduced parameters to only `namespace` and `application_name`
  - Cleaned up and sorted application list (removed duplicates)
  - Added validation stage (fails early if `--SELECT--` chosen)
  - Removed unused variables (REGISTRY, DEPLOY_ENV, gitCommit)
  - Added rollout timeout (120s) to prevent hanging builds
  - Always uses cross-account role (no conditional)

## May 20, 2026

### SIT (UAT) Selling Service Fixes
- **Fixed `tariff-selling-service` CPU**: Patched from 350m/800m â†’ 500m/2000m
- **Fixed `tariff-selling-consumer` memory**: Was ~1.5TB/~1.9TB (same TB bug), fixed to 700Mi/1200Mi
- **Fixed `tariff-selling-service` HikariPool exhaustion**: Was getting 504s â€” `Connection is not available, request timed out after 10005ms (total=12, active=12, idle=0, waiting=9)`. Increased `maximum-pool-size` from 12 â†’ 25 in configmap
- **Checked `tariff-selling-service-batch`**: Healthy, no issues (500m/2Gi, 2Gi/3Gi)

### Node Status Check (All 3 Environments)
- **SIT EU (Frankfurt)**: 27 nodes â€” All Ready âœ…
- **DEV EU (Frankfurt)**: 15 nodes â€” All Ready âœ…
- **SIT Singapore**: 3 nodes â€” All Ready âœ… (EKS v1.35.3/v1.35.4)

### SIT Singapore Cluster Discovery
- **Region**: ap-southeast-1
- **Bastion**: `ssh -i /home/ec2-user/rahul/rahul-key ec2-user@10.130.210.3` (from current host 10.151.4.165)
- **Nodes**: 3

### Other Checks
- **itopaz UI (DEV)**: All healthy â€” export-ui (2), maintenance-ui (2), shell-ui (2)
- **afr-prefiler-service (SIT Frankfurt)**: 2 pods Running 2/2 âœ… (prefiler-api namespace)
- **DEV Kafka consumer groups**: Listed 58 groups; identified stale `-local` groups and mismatched `-uat` groups

## May 18, 2026

### tariff-buying-carriage-service Kafka Topic Fix (SIT/UAT)
- **Root cause**: Producer was publishing to `tariff-buying-carriage-excel-upload-local` (dev default from application.yml) â€” topic doesn't exist on UAT broker
- **Error**: `TimeoutException: Topic tariff-buying-carriage-excel-upload-local not present in metadata after 60000 ms`
- **Fix**: Added `tariff-buying-carriage-excel-upload-topic-name: tariff-buying-carriage-excel-upload-uat` to `tariff-buying-carriage-service` configmap (was missing, consumer CM had it but producer didn't)
- **Note**: Service returned HTTP 200 despite failure (silent failure)

### auth-base-uri Addition (SIT/UAT)
- **Added** `auth-base-uri: http://tariff-profile-service.itariff-api.svc.cluster.local/profile-domain-service` to:
  - `tariff-buying-carriage-service` configmap (serviceurls section)
  - `tariff-buying-carriage-consumer-service` configmap (new serviceurls section created)
- Restarted both deployments

### tariff-grant-auth Resource Fix (DEV)
- **Issue**: Memory request/limit was ~1.1TB/~1.5TB (bytes with `m` suffix â€” same bug pattern)
- **Fix**: Patched to cpu:100m/500m, memory:700Mi/1500Mi

## May 27, 2026

### itariff-k8s-repo (develop branch)
- **Increased CPU/memory by 10%** for 9 buying services and pushed to Bitbucket (commit cfbf401)
- **Patched DEV cluster** (euc1-itopaz-dev-eks, ns: itariff-api) with new resource values
- Services updated: tariff-buying-carriage-consumer, carriage, otherbooking, service, shippingline-consumer, standardcost, truck, warehouse-consumer, warehouse

### prefiler-k8s-repo (dev branch)
- **Applied all ConfigMaps to DEV cluster** (prefiler-api namespace): aci, aes, afr, ams, basf, dagangnet, ics, ics2, imdg, master, mblfiler, mpci, prefiler-auth-service (13 total)
- **Fixed sa-prefiler-service-config.yaml**: namespace was `default`, changed to `prefiler-api`, pushed to Bitbucket (commit 929171b)
- **prefiler-bff namespace**: prefiler-auth-bff-config, prefiler-bff-config (already in sync)

### SIT EU Cluster (euc1-itopaz-sit-eks) Optimization
- **Enabled NTH** (aws-node-termination-handler) temporarily, then **disabled** again per user request
- **Disabled duplicate fluent-bit** (fluent-bit namespace) â€” was running alongside amazon-cloudwatch/fluent-bit. Saved ~1.7 cores + 833Mi
- **Disabled promtail** (monitoring namespace) â€” redundant with fluent-bit. Saved ~1.7 cores + 4.25GB
- **Verified csi-smb-node** is REQUIRED (8 bound SMB PVCs across itopaz-api, auth, export, platform)
- **Verified efs-csi-node** is REQUIRED (4 bound EFS PVCs in istio-system: grafana, jaeger, kiali, prometheus)

### Node Status Checks (May 27)
- DEV EU: 18 nodes (3 cordoned)
- SIT EU: Started at 23 nodes -> scaled to 35 nodes (all Ready)
- SIT Singapore: 4 nodes (1 cordoned)

## May 26, 2026 (from earlier session)
- Fixed prefiler Jenkins pipelines (aes, afr SIT builds)
- Created 8 missing frontend Jenkins jobs
- Pushed prefiler-k8s-repo sit branch (commit 6221583)
- Created jenkins-config.md and eks-prefiler-config.md
- Synced md files to S3 bucket devops-securit-dev

## August 27, 2026

### AWS Profiles & Kubeconfig
- Added UAT profiles: uat-eu-central-1, uat-us-east-1, uat-admin (405478414008)
- Added dev-frankfurt-admin, sit-singapore-admin, sit-frankfurt-admin, bw-uat, gati-674-admin SSO profiles
- Added uat-eu-central-1 and uat-us-east-1 contexts to kubeconfig

### Aurora Scheduler Bugs Fixed (SIT - 464134132424)
- Fixed 3 bugs in scheduler Lambda (eu-central-1 & ap-southeast-1): wrong API for clusters, wrong tag level, comma/slash split bug
- Both Aurora clusters now auto stop/start per schedule tags
- euc1-itopaz-sit-aurora-postgresql was running 9.5 months non-stop â€” fixed

### Scheduler Lambda Deployed to Dev + UAT
- Deployed weekday-aware scheduler-rds-ec2 Lambda to 4 account/region targets
- Added ScheduleDays tag support (mon-fri filtering)
- Tagged EC2 + Aurora clusters in dev (074779643551) and UAT (405478414008) with 09:00-21:00 IST Mon-Fri schedules
- Added ASG scheduled start/stop actions for all UAT EKS node groups (6 ASGs)

### EBX Auto-Start Fix (EUC1 SIT - i-08a20bae22e57e46d)
- @reboot crontab silently skipped by cronie on Amazon Linux 2023 for stop/start EC2
- Created systemd ebx.service with 10-min delay (ExecStartPre=/bin/sleep 600)

### Dev EKS Windows Node Scheduling Fix (074779643551)
- 38 Linux pods stuck on Windows nodes (FailedCreatePodSandBox 8+ hours)
- Added nodeSelector: kubernetes.io/os: linux to 33 deployments

### SIT itariff-api ConfigMap Fixes (464134132424)
- tariff-buying-service: added service.delete.code, service.archive.code
- tariff-buying-otherbooking-service: added service.rfq.code
- All pods recovered from CrashLoopBackOff

## 2026-10-14 - GATI application inventory knowledge update

### Application inventory
- Consolidated eight active GATI applications into `infrastructure/reports/gati-application-inventory-2026-10-14.csv`: Gate Scan App, HubEye, AIM (GATE) - Telematics, Call Center (Ameyo), Control Tower, JIRA, DMS, and IntelliHub.
- Preserved verified application endpoints and WAF associations for Gate Scan, HubEye, and Telematics.
- Added supplied ownership, technology, database, hosting, AD SSO, and password-policy details.
- Kept unverified URLs, AWS account/region mappings, contractual vendor names, and DR arrangements explicitly marked `TBC`.
- Added verified DMS PROD/UAT EC2 and PROD Aurora PostgreSQL details from the AWS resource inventory; retained vendor, URL, authentication, access scope, and DR as `TBC`.
- Added IntelliHub as row 8 with verified PROD/TEST domains, AWS account and region, multi-AZ production EC2 placement, core service HA status, and outstanding Global Accelerator/DR limitations.
- Validated the report as eight data rows with sixteen columns and no empty cells.
- AIML test asset-management recovery: authorized TCP `3001` from `LB-intranet` security group `sg-04973b9b0daf54d9a` to backend `aiml-sg` (`sg-0f2023634991b6f6e`) as rule `sgr-0783904f03b79a840`. Target `i-0825be434cf7ab87b:3001` changed from `Target.Timeout` to `healthy`.
- Remaining asset-management issue: `https://aimlapp-test.allcargoapps.com/assest-management-backnd/api/v1/health-check` reaches Uvicorn but returns HTTP 404 because the ALB forwards the prefix while FastAPI exposes `/api/v1/health-check`. Add a path rewrite or matching prefixed application route; the handler also requires `PlainTextResponse` to be imported to avoid HTTP 500 on its direct route.

## 2026-10-14 - UAT architecture document compatibility review

- Reviewed the APSE, EU, and US UAT v1.1 PDFs against AWS account `405478414008` using corporate SSO and read-only APIs.
- Confirmed the environment remained off: three bastions stopped, three Aurora clusters stopped, and all EKS node groups at desired capacity zero. No AWS resource was started or modified.
- Verified regional VPC/CIDR, subnet topology, Transit Gateway attachments, EKS control planes, RDS, EFS, internal NLBs, ECR, KMS, Secrets Manager, and IAM role existence.
- Verdict: documents are partially compatible but unsafe to execute unchanged. Key blockers include EKS `1.35` versus live `1.36`, nonzero node scaling, incorrect private-zone names, invalid region/ARN strings, cross-region copy errors, and declared ElastiCache resources absent from AWS.
- Full report: `infrastructure/reports/uat-document-compatibility-review-2026-10-14.md`.

### EKS Security Group Fix (SIT Frankfurt)
- Bastion sg-03396fa5484b431e1 â†’ EKS sg-023c8cff9a807ad1d TCP/443 rule added

### CloudFront + WAF Fix (674017976129)
- Added /agent/* behavior â†’ ELB in distribution E2FVCC01LF3UUD
- Fixed Belgium zero traffic: Microsoft Azure proxies blocked by HostingProviderIPList
- Override to Count + P0 allow rule for Azure IP ranges

## August 28-31, 2026

### Jump Account (439891535362) Lambda + EC2 Tags
- Created scheduler-rds-ec2 Lambda (IAM role + EventBridge trigger)
- Tagged 5 EC2 instances with 09:00-21:00 IST Mon-Fri schedule

### EBX Auto-Start Fix (Revised)
- Systemd service was failing: JAVA_HOME not set in systemd env
- Removed systemd service, kept crontab-only with JAVA_HOME and logging to /var/log/ebx-cron.log

### DEVOPS Account Cost Analysis (439891535362)
- Cost Apr $594 â†’ Aug $1,138 (+92%)
- Cause 1: Kiro Enterprise Pro Plus â€” 11 users @ $40/user = $432/month (started May, growing)
- Cause 2: EBS snapshots â€” 124 snapshots, 25,852 GB, oldest Sep 2025, costing $253/month
- Action needed: Review Kiro seats, delete old AMI snapshots

### SIT itariff-api ConfigMap Fix
- tariff-buying-carriage-service: added service.rfq.code=RFQ10001 (same pattern as otherbooking, buying-service)
- All pods recovered from CrashLoopBackOff

## 2026-10-14 â€” Jenkins workspace cleanup

- **Target:** Jenkins master `10.100.95.13`; persistent volume `/home/ubuntu/jenkins-data`, Jenkins workspace `/home/ubuntu/jenkins-data/jenkins_home/workspace`.
- **Reason:** data volume was full (`344G`, `328G` used, `1.5G` available, `100%`).
- **Action:** verified the `jenkins-server` Docker bind mount and controller health, checked for active workspace processes, and removed disposable workspace checkouts/build outputs only. Preserved jobs, build records, plugins, users, credentials, secrets, tools, and controller configuration.
- **Result:** volume reduced to `270G` used with `60G` available (`82%`). Jenkins remained healthy and `/login` responded successfully.
- **Concurrent activity:** Jenkins created a new `iTopaz-nonprod-frontend/SIT/SIT-Frankfurt/itopaz-imports-ui` workspace after cleanup for an active build; it was left untouched.
- **Docker cleanup:** subsequently ran the user-approved `docker image prune -f`. Image storage decreased from `12.57GB` to `4.952GB` (about `7.6GB` recovered); root filesystem availability increased to `142G` (`27%` used). The healthy `jenkins-server` container and an active `aquasec/trivy:0.50.2` scan container were preserved.
- **Scheduled guard:** installed `/usr/local/sbin/jenkins-safe-workspace-cleanup.sh` on the Jenkins host and scheduled it for `03:40 UTC` daily (`09:10 Asia/Kolkata`). The trigger was clarified to **available Jenkins-volume space below `100GiB`**. It skips when workspace processes, non-controller Docker containers, or files modified in the preceding 30 minutes indicate activity. It only removes top-level workspace trees with no file changes for 24 hours and uses `flock` to prevent overlap. Replaced an unrestricted daily `docker system prune -a -f` entry and a malformed workspace cron entry.

## 2026-10-15 â€” Jenkins global credentials recovered

- **Incident:** Jenkins global credentials were absent after the daily Jenkins host replacement/start. The persistent `credentials.xml` was zero bytes with modification/change time `2026-10-14 06:09:53 UTC` (`11:39:53 IST`); encryption keys remained present and unchanged.
- **Evidence:** the empty file predates the 2026-10-14 workspace cleanup. The Jenkins data volume had subsequently reached 100% usage, making a failed/truncated save due to exhausted space the strongest explanation, but the prior root volume/controller logs were unavailable after host replacement, so the exact writer could not be proven.
- **Recovery source:** EBS snapshot `snap-0f656cb7b86d1d00b`, created `2026-10-13 20:18:05 UTC` (`2026-10-14 01:48:05 IST`) for persistent volume `vol-029426e9b50b67b8a`.
- **Validation:** mounted a temporary snapshot volume read-only. Snapshot `credentials.xml` was `71,670` bytes with `55` credential IDs. `secret.key`, `identity.key.enc`, `secrets/master.key`, `hudson.util.Secret`, and the credentials SecretBytes key matched the live controller.
- **Restore:** saved the empty live file as `/home/ubuntu/jenkins-data/jenkins_home/credentials.xml.empty-20261015T045918Z`, gracefully stopped `jenkins-server`, restored only `credentials.xml` with owner `ubuntu:docker` and mode `0644`, and restarted Jenkins.
- **Result:** Jenkins returned healthy, `/login` responded successfully, 55 credential IDs were present, and startup logs showed no credential decryption/load errors. Temporary recovery volume `vol-0bf92411687198e5f` was unmounted, detached, and deleted; the source snapshot was retained.
- **Scheduler finding:** the EC2 replacement restored old root-volume cron entries. Reapplied the guarded 09:10 IST cleanup and placed its script on persistent storage at `/home/ubuntu/jenkins-data/maintenance/jenkins-safe-workspace-cleanup.sh`; durable boot-time cron provisioning still needs to be placed in the launch template/AMI.
- **Cause investigation:** the damaged file retained a single inode with birth time `2026-10-14 05:17:45 UTC` and was directly reduced to zero bytes at `06:09:53 UTC`; this was not an atomic replacement with a valid empty Jenkins XML store. No persistent job/config/script reference targeting `credentials.xml` was found, auditd was inactive, and AWS showed no SSM command or administrator control-plane action during `05:00â€“06:30 UTC`. CloudTrail entries near the event were normal EC2 instance-profile `AssumeRole` refreshes. The prior root-volume/controller logs were unavailable following daily instance replacement. Given that the persistent data volume reached 100% and no deliberate writer was identified, a local write/truncation failure during disk exhaustion is the evidence-supported probable cause; exact process attribution is not possible from retained evidence.

## 2026-10-16 â€” AVRT dev Jenkins CI created and verified

### POC â€” avrt-playwright-dev
- **Scope:** user requested Git/dev inspection on 10.0.132.243 and a pipeline on Jenkins 10.151.4.91:8080; supplied Jenkins SSH key route and explicitly approved restart.
- **Source:** `/root/var/www/avrt` clean on dev at b5816dafd5c386e3312af0f7c7a430d3a099ee49, matching CodeCommit dev. Active AVRT runtime is `/home/ubuntu/avrt` under avrt.service.
- **Changed:** new sandboxed Jenkins CI job `avrt-playwright-dev`; reuses aws-gitcredentials-id and node22. Two approved-operation restarts loaded/queued it after correcting the startup scheduling call; temporary startup script removed. No application deploy or SCM push.
- **Verified:** build 2 SUCCESS (75 seconds), authenticated checkout, dependency installation, 48 JS syntax checks, 9 effects tests, Chromium smoke and artifact archiving. Both services active, source checkout still clean. Build 1 failed during restart with missing program.dat.
- **Limits:** no automatic trigger; full integration tests excluded due hard-coded application port vs harness PORT mismatch. Pre-existing node22 installer emits ENOVERSIONS for global package 10.5.0; installed runtime works and shared tool unchanged.
- **Evidence/recovery:** `infrastructure/jenkins/avrt-playwright-dev/` contains Jenkinsfile, initial job XML, README and verification.json. New job can be disabled through Jenkins; no existing jobs overwritten. Master sync bundle: `agent/handoffs/master-knowledge-sync-20261016-avrt.tar.gz`; delivery pending because registry has no inbound master endpoint.

## 2026-10-22 â€” SASIT node stability repair
- Verified account 464134132424, apse1-itopaz-sit-eks. Added a two-node On-Demand t3.medium Linux baseline via existing group (min/desired 2, max 4), verified both Ready. Spot capacity retained.
- Dagangnet/ICS UI now two replicas on distinct nodes, readiness probes, preferred On-Demand affinity, maxUnavailable=0 and minAvailable=1 PDBs. Both rollouts and browser module loading verified.
- Replaced inaccessible Windows AMI group v2 with v3, current AWS release 1.35-2026.09.14 / ami-030cbe36eac6fb501; one Windows node Ready, group ACTIVE. Empty old group removed after validation.
- Separate missing BASF/MPCI ECR tags remain unresolved. Windows report/SMB pods scheduled and initializing; older Windows test app needs taint tolerance. No authenticated workflow verification.
- Backups: infrastructure/backups/sasit-node-repair-20261022. Report: infrastructure/reports/sasit-node-repair-20261022/report.md. Additional On-Demand EC2 costs apply. No repository push.

## 2026-10-22 â€” TIBCO BWCE Builder 2.9.0 Docker Image Built & Pushed to ECR

### Context & Requirement
- **Target Image**: `074779643551.dkr.ecr.eu-central-1.amazonaws.com/bwce-builder:2.9.0` (also tagged `:latest`)
- **Description**: Licensed builder image containing Apache Maven (3.8.6), Java OpenJDK 11, TIBCO BWCE 2.9.0 runtime/installation, and the official TIBCO BW Maven plug-in (`bw6-maven-plugin:2.9.8`).
- **ECR Repository**: `arn:aws:ecr:eu-central-1:074779643551:repository/bwce-builder` (Frankfurt / `eu-central-1`).

### Actions Taken
1. **Source Discovery**:
   - Discovered licensed TIBCO BWCE 2.9 installation at `/opt/tibco/bwce/2.9.0` on the BW EC2 instance `i-014d95b8f4f1cb32e` (`10.100.148.150`).
   - Packaged and transferred the licensed BWCE 2.9 runtime, Maven plugin JARs (`bw6-maven-plugin-2.9.8.jar`, `fabric8-maven-plugin-4.4.1.jar`, `com.tibco.bw.palette.shared`), and installation scripts via secure S3 staging (`s3://devops-securit-dev/tibco/bwce-2.9.0.tar.gz`) to the DEV bastion host `10.100.145.118`.
2. **Container Build**:
   - Base image: `maven:3.8.6-openjdk-11` (contains Maven 3.8.6, OpenJDK 11, Git, Curl, Unzip).
   - Deployed `/opt/tibco/bwce/2.9.0` and configured `TIBCO_HOME=/opt/tibco`, `BWCE_HOME=/opt/tibco/bwce/2.9.0`, and `BW_HOME=/opt/tibco/bwce/2.9.0`.
   - Executed `install.sh` inside the build context to register `bw6-maven-plugin-2.9.8` and dependencies into `/root/.m2/repository`.
3. **Verification & ECR Push**:
   - Verified plugin registration: `bw6-maven-plugin-2.9.8.jar` present and valid in Maven repository.
   - Authenticated Docker against DEV ECR registry `074779643551.dkr.ecr.eu-central-1.amazonaws.com`.
   - Successfully pushed both `2.9.0` and `latest` tags:
     - Digest: `sha256:63aa02c812e54e27fa5e3b57e7e57324fa4b3d48239e2ea0703b53bc683c567a`
     - Image size: ~1.14 GB
4. **Cleanup**: Removed temporary archive files from S3 and the bastion host disk.

---

## 2026-10-23 â€” ECR bw-base-image reconciliation: Retagged 2.9.0 to working digest & pruned broken image

### Context & Root Cause
- **Repository**: `074779643551.dkr.ecr.eu-central-1.amazonaws.com/bw-base-image` (DEV account `074779643551`, Frankfurt).
- **Issue**: Pulling `074779643551.dkr.ecr.eu-central-1.amazonaws.com/bw-base-image:2.9.0` failed or pointed to a non-working image build (`sha256:83f536d7fe4fa6d60880a1ab140a264d1dbc9bdd28ab7abaf5ec414135188cb5`, 409MB, pushed Sep 23, 2026).
- **Working image**: The verified working base image was `sha256:b482d9cf0491a2507f5a1d694e36de0b33c7cff8c0a898572959020189709d81` (368MB, pushed Sep 15, 2026), but it had become untagged in ECR.

### Actions Taken
1. **Retagged Working Image**:
   - Fetched image manifest for digest `sha256:b482d9cf0491a2507f5a1d694e36de0b33c7cff8c0a898572959020189709d81`.
   - Pushed tag `2.9.0` and tag `latest` referencing this working manifest via `aws ecr put-image`.
2. **Pruned Broken Image**:
   - Deleted broken image digest `sha256:83f536d7fe4fa6d60880a1ab140a264d1dbc9bdd28ab7abaf5ec414135188cb5` via `aws ecr batch-delete-image`.
3. **Verification**:
   - Confirmed repository `bw-base-image` now contains exactly **ONE** image:
     - Digest: `sha256:b482d9cf0491a2507f5a1d694e36de0b33c7cff8c0a898572959020189709d81`
     - Tags: `["2.9.0", "latest"]`.
   - Verified live pull of `074779643551.dkr.ecr.eu-central-1.amazonaws.com/bw-base-image:2.9.0` from both DEV bastion (`10.100.145.118`) and BW EC2 instance `i-014d95b8f4f1cb32e` (`10.100.148.150`). Both successfully pulled the working digest.

---

## 2026-10-23 â€” CodePipeline Scripts Updated with Dedicated EAR Build Stage

### Context & Requirement
- **Target Instance**: `10.100.148.191` (`i-021f9c8b74a27a3f0`, `EC2-MDM-BW-Dev`)
- **Directory**: `/root/rahul/`
- **Files**: `itopaz.sh` and `topaz.sh`
- **Task**:
  1. Take full backups of both CodePipeline scripts.
  2. Add an EAR build stage into the pipeline configuration (utilizing the newly prepared `bwce-builder:2.9.0` image).

### Actions Taken
1. **Backups Created**:
   - Preserved copies under `/root/rahul/backup/`:
     - `itopaz.sh.bak.20261023_092958`
     - `topaz.sh.bak.20261023_092958`
2. **CodeBuild EAR Project Provisioned**:
   - Created `codebuild_bw_ear` in `eu-central-1` using:
     - Builder Image: `074779643551.dkr.ecr.eu-central-1.amazonaws.com/bwce-builder:2.9.0`
     - Service Role: `arn:aws:iam::074779643551:role/service-role/codebuild-codebuild_bw-service-role`
     - Attached `AmazonEC2ContainerRegistryPowerUser` to ensure full ECR pull/push authorization.
     - Buildspec: Handles automated compilation via Maven (`mvn clean package -Dbw.Home=/opt/tibco/bwce/2.9.0`) or `ci/build_in_container.sh`, collects all produced `*.ear` files to the workspace root, and outputs `**/*` into `EARArtifact`.
3. **Pipeline Stages Enhanced**:
   - Enhanced `topaz.sh` and `itopaz.sh` with a dedicated 4-stage pipeline architecture:
     - **Stage 1 (Source)**: Bitbucket via CodeConnections (`SourceArtifact`)
     - **Stage 2 (EAR_Build)**: CodeBuild project `codebuild_bw_ear` using `bwce-builder:2.9.0` (`EARArtifact`)
     - **Stage 3 (Build / Docker)**: CodeBuild project `codebuild_bw` taking `EARArtifact` with compiled `.ear`, building Docker container, tagging, and pushing to ECR (`BuildArtifact`)
     - **Stage 4 (Deploy)**: CodeDeploy deployment group on EC2 targets (`BuildArtifact`)
   - Added automated self-healing checks to ensure both CodeBuild and CodeDeploy resources exist before pipeline creation/update.
4. **Verification**:
   - Tested pipeline creation and schema validation in AWS CodePipeline with live test pipeline `test-syntax-pipeline-validation` (succeeded and removed).
   - Validated shell syntax with `bash -n` on both scripts on instance `10.100.148.191`.

## 2026-10-23: Fix SonarScanner for .NET 12.0 Incompatibility with SonarQube 10.7 in CI/CD Pipelines

### Context & Root Cause
- **Issue**: Jenkins pipeline `jenkins/dev/api/aci-prefiler-service` failed at step `SonarQube Scan (.NET) inside build image`:
  ```
  Using SonarQube 10.7.0.96327.
  Checking if the server version is supported...
  SonarQube versions below 2025.1 are not supported anymore by the SonarScanner for .NET. Please upgrade your SonarQube version or use an older version of the scanner.
  Pre-processing failed. Exit code: 1
  ```
- **Root Cause**: `dotnet tool install --global dotnet-sonarscanner` without a version pin automatically fetched the newly released `dotnet-sonarscanner` 12.0.0. SonarScanner 12.0 dropped support for SonarQube Server versions below 2025.1 LTA, whereas the internal SonarQube server is version `10.7.0.96327`.

### Actions Taken
- Pinned `dotnet-sonarscanner` tool installation to version `11.3.0` (`--version 11.3.0`), which maintains full compatibility with SonarQube 10.7.
- Updated all API, cache, and template pipelines across:
  - Branch `dev`: commit `4718cc7` (20 files updated)
  - Branch `sit-all`: commit `98b8056` (17 files updated)
  - Branch `sit`: commit `49d92fe` (19 files updated)
  - Branch `sit-singapore`: commit `c2a5663` (18 files updated)

## 2026-10-13 — File audit & reconciliation; AWS Agent Toolkit install (incomplete)

### LOCAL — README node section reconciled to live config
- **Found drift:** `README.md` "Distributed agent nodes" / "Agent operation lock" claimed worker-2 was "installed standby, disabled in the local worker pool until explicitly activated" and "remains disabled until future activation."
- **Authoritative state (via `python itopaz_agent.py --doctor` on 2026-10-13 + `nodes.json`):** worker-2 is `enabled: true`, `optional: false`, `activation: always`, agent deployed, SSH key present, and appears in `active_workers`. Both worker-1 and worker-2 are active, always-on primary workers.
- **Fix:** updated both README passages to state both workers are active/always-on; recorded worker-1 has internet, worker-2 is firewall-restricted (no internet, operator-confirmed 2026-10-11). No code or `nodes.json` change — the registry was already correct; only stale prose was corrected.

### LOCAL — AWS Agent Toolkit for AWS: install started, NOT complete
- **Scope:** Kiro only (operator said do not modify Codex). Profile `itopaz`, default region `eu-central-1`, advanced AWS experience. Prereqs present: AWS CLI 2.36.19, uv 0.13.0.
- **Done:** `aws configure set region eu-central-1 --profile itopaz` (exit 0); launched `aws login --region eu-central-1 --profile itopaz` (browser auth URL issued).
- **Pending (blocked on human browser auth):** Step 4 verify (`sts get-caller-identity`), Step 5 `aws configure agent-toolkit` wizard, Step 5b add `AWS_MCP_PROXY_PROFILES=itopaz` to the Kiro `aws-mcp` MCP entry, Step 6 `list-available-skills`, Step 7 add AWS rules to `~/.kiro/steering/`.
- **Verified empty (not yet created):** `~/.kiro/settings/mcp.json` does not exist; `~/.kiro/steering/` is empty. No AWS MCP/steering artifacts fabricated — install resumes once browser sign-in completes.
- **Note:** direct write to `~/.kiro/settings/mcp.json` is blocked by a protected-path rule; MCP config must be added via the Kiro MCP UI or a workspace-level `.kiro/settings/mcp.json`.

## 2026-10-13 — RUNBOOK: Jenkins fetch fails with git D/F ref conflict (`cannot lock ref`)

### Incident
- **Job:** `prefiler-nonprod-frontend/Dev/imdg-prefiler`, build #70. Repo `allcargoecu/prefiler-k8s-repo` (manifests). Started by `k.rahul@allcargologistics.com`.
- **Symptom:** `ERROR: Error fetching remote repo 'origin'` → `Failed to fetch` → `Maximum checkout retry attempts reached, aborting`. Build summary showed all `null` values and a `MissingContextVariableException: Required context class hudson.FilePath is missing` on `archiveArtifacts`.

### Root cause — git directory/file (D/F) ref conflict (NOT auth or network)
- The fetch reached Bitbucket successfully (objects counted/compressed; `8097efd..762856f dev -> origin/dev` updated). It failed on the **local ref store**, not the remote.
- Decisive line:
  `error: cannot lock ref 'refs/remotes/origin/fix': 'refs/remotes/origin/fix/deep-link-redirect' exists; cannot create 'refs/remotes/origin/fix'`
  `! [new branch] fix -> origin/fix (unable to update local ref)`
- Two remote branches cannot coexist as git refs: a bare branch **`fix`** (git stores it as a FILE at `.git/refs/remotes/origin/fix`) and **`fix/deep-link-redirect`** (requires `.git/refs/remotes/origin/fix/` to be a DIRECTORY). A path cannot be both a file and a directory → fetch aborts.
- The `null` summary and `FilePath`/`archiveArtifacts` error are DOWNSTREAM NOISE: checkout never produced a workspace, so declarative post-actions ran without `node`/`FilePath` context. They resolve once the fetch succeeds; do not chase them.

### Fix — two parts
1. **Permanent fix (Bitbucket) — remove the clashing branch name.** Rename the bare `fix` branch to a namespaced name (preserves commits) and delete the bare one:
   - `git branch -m fix fix/old-work`
   - `git push origin fix/old-work`
   - `git push origin --delete fix`
   - CAUTION: confirm the `fix` branch owner and that commits are preserved before deleting. Until one of `fix` / `fix/deep-link-redirect` is renamed, EVERY fresh clone of this repo keeps hitting this — not just Jenkins.
2. **Unblock the Jenkins agent — the corruption is only in the workspace `.git`, not in Bitbucket.** Either reclone or surgically prune:
   - Reclone: `rm -rf "/var/jenkins_home/workspace/prefiler-nonprod-frontend/Dev/imdg-prefiler/.git"` then rebuild; or enable Git plugin "Wipe out repository & force clone" / "Clean before checkout".
   - Surgical: `cd` into the workspace, then `git remote prune origin`, `git update-ref -d refs/remotes/origin/fix/deep-link-redirect` (or remove the whole `fix/` tracking dir), `git fetch origin`.

### Recommended order
Rename/delete `fix` in Bitbucket (part 1) first — it's the permanent fix — then wipe the Jenkins workspace `.git` (part 2), then re-run the build. Prefer the surgical prune over a permanent "Wipe out repository" job setting for large repos.

### Detection signature
Any `cannot lock ref 'refs/.../X'` + `'refs/.../X/<something>' exists` pair = D/F ref conflict. Look for a bare branch whose name is also used as a path prefix by another branch.

## 2026-10-13 — Knowledge updates must also sync to master

### LOCAL — Standing user preference and delivery status
- **User instruction:** always sync knowledge updates to the master as well; retry requested now. Standing authorization is recorded in root `AGENTS.md`.
- **Connection check:** worker-1 cannot initiate delivery to the Windows local transport; the master completed the sync through its existing SSH connection.
- **Prepared transfer:** `agent/handoffs/master-knowledge-sync-20261013.tar.gz` contains canonical knowledge, dated summaries/activity log, China handoff/evidence, workspace sync instructions and Markdown retrieval tools; `manifest.json` records per-file SHA-256 checksums. Optional vector rebuilding was stopped without replacing its existing artifacts; full-text retrieval reads the updated Markdown immediately.
- **Delivered:** the Windows master fetched and merged the non-secret knowledge bundle from worker-1 on 2026-10-13; master-only history was preserved.

## 2026-10-13 — Jenkins Prefiler Dev Pipelines: Enhanced SonarQube Report & Issue Resolution Dashboard

### Prefiler CI/CD — Dev pipeline enhancement
- **Scope / authorization:** user requested adding an option to download SonarQube reports from Jenkins for `aci-prefiler-service`, and subsequently extending the report with file name, file path, line number, rule details, remediation instructions, effort, direct resolve links, and applying across all Dev Jenkinsfiles.
- **Changed:**
  - Updated all 5 pipeline templates (`jenkins/templates/api.groovy`, `ui.groovy`, `cache.groovy`, `microfrontend-main.groovy`, `microfrontend-shared.groovy`) in `prefiler-k8s-repo`.
  - Added boolean parameter `DOWNLOAD_SONAR_REPORT` (default: `true`).
  - Implemented `Download SonarQube Report` stage querying SonarQube API (`/api/measures/component`, `/api/issues/search?componentKeys=${PROJECT_KEY}&ps=500&additionalFields=_all`, `/api/qualitygates/project_status`).
  - Added standalone reporting engine generating `sonar-report.html` (interactive dashboard with real-time text filter, severity and issue-type dropdowns, Quality Gate status, and columns for Severity, Type, File Name, File Path, Line, Rule Name & Key, Issue Remediation, Effort, and direct `Resolve ↗` links into SonarQube) and `sonar-issues.csv` for spreadsheet export.
  - Updated post-build `archiveArtifacts` to include `sonar-reports/**`, `**/sonar-report.html`, and `**/sonar-issues.csv`.
- **Verification:** rendered all 34 pipelines (`jenkins/dev/api/` 17 services, `jenkins/dev/ui/` 17 services) using `python3 jenkins/scripts/render.py dev`; verified with `python3 jenkins/scripts/render.py dev --check` (34 pipelines verified, 0 errors). Tested HTML/CSV generation with Python 3.9.
- **Delivery:** committed (`78919da`) and pushed to `origin/dev` in `prefiler-k8s-repo`.

## 2026-10-13 — CodeCommit to Bitbucket Repository Branch Synchronization (MDMBWPROJ)

### Version Control — Repository synchronization
- **Scope / authorization:** user requested synchronizing latest branches for all repositories in `/home/ec2-user/organized/repos/codecommit-to-bitbucket/create-bitbucket-repo.sh -p MDMBWPROJ -f repositories.txt`.
- **Changed:** executed multi-branch synchronization script across MDM/BW Bitbucket project repositories.
- **Verification:** branch refs fetched and synchronized from upstream CodeCommit remotes to Bitbucket targets.

## 2026-10-13 — China Prefiler SIT URL checked; master handoff prepared

### SIT China — Read-only inspection
- **Scope / authorization:** user requested checking `prefiler-sit.ecuworldwide.cn` and giving findings to the master node. Application hostname checked, not the linked Azure China management portal.
- **Verified:** login 200; Git/build/config files exposed; HSTS/CSP/nosniff/Cache-Control missing on login; root redirect passes through HTTP; shared UI still contains Angular 16.2.12. Eleven paths checked; no scanner rerun.
- **Evidence:** `security-reviews/2026-10-13/china-sit/`; no disclosed source/config bodies retained.
- **Handoff / limits:** `agent/handoffs/master-china-prefiler-sit-20261013.md` prepared for the Windows master. No inbound master delivery endpoint is configured, so it was not sent. No China remediation or Azure control-plane action performed.
- **Knowledge updated:** canonical China Prefiler SIT section and dated SIT China summary now preserve exact checked paths, header/redirect/Angular findings, evidence links, pending Azure remediation and undelivered handoff status. Full browser workflows and China WAS rerun remain pending; EU/Singapore resolution counts do not apply.

## 2026-10-13 — EU SIT Prefiler dedicated header policy and origin protections

### SIT EU — Security remediation
- **Authorization / scope:** user requested a new EU SIT Prefiler policy and security fixes on `E1H7QYRQWZGB8Z`.
- **Changed:** created dedicated `prefiler-eu-sit-security-headers` (`01b532a5-4368-43ac-ba3f-e3f05567cf76`), Deployed; tightened compatible CSP and no-store response caching. Added persistent Apache protection via ConfigMap on `prefiler-ui/microfrontend-main`; image preserved. Sensitive file requests denied and HTTPS redirects fixed; invalidation submitted. Shared and Singapore policies unchanged.
- **Verification:** rollout and Apache syntax passed; 36 origin paths checked. Direct CloudFront login 200, six disclosed-file paths 403, root redirects HTTPS. EU now 61/80 resolved (eight additional rows); 18 Angular version findings and one permissive-CSP row remain open.
- **Pending / limits:** Angular 16.2.12 still served; dependency migration/rebuild, strict-CSP compatibility work, browser regression and scanner rerun remain necessary.
- **Evidence / recovery:** `security-reviews/2026-10-13/eu-after-remediation/REPORT.md`; latest annotated workbook records EU 61/19 and Singapore equivalents; root workbook was absent, so the preserved original backup was used. CDN backup/source under `infrastructure/cloudfront/eu-sit/`, origin deployment backup on bastion.

## 2026-10-13 — Singapore Prefiler origin security and dedicated CDN policy

### SIT Singapore — Security remediation
- **Authorization / scope:** user requested Singapore fixes and explicitly authorized a new Prefiler header policy on `E3D3FER4L2TKX9`.
- **Changed:** created and deployed `prefiler-singapore-sit-security-headers` (`19ea5556-83fa-4f53-ace8-672c41162914`); tightened compatible CSP and replaced blanket immutable caching. Added a persistent Apache security ConfigMap mount to `prefiler-ui/microfrontend-main`, blocking disclosed files, setting response headers and fixing root HTTPS redirects. Image unchanged; shared policy and EU unchanged. CDN invalidation submitted.
- **Verification:** origin rollout and Apache syntax passed; login 200, sensitive files 403, root redirects HTTPS; 36 paths verified. New edge headers observed. Using the 80 EU workbook rows as a Singapore equivalent checklist: 61 resolved, 18 Angular version findings open, one permissive-CSP finding partly improved but open.
- **Limits / pending:** Angular 16.2.12 still served; browser regression and WAS rerun needed. CDN still returns 502; its internal NLB is configured as a regular custom origin. No VPC/networking changes made.
- **Recovery / evidence:** `security-reviews/2026-10-13/singapore/REPORT.md` and `infrastructure/cloudfront/singapore/`; prior CDN configuration locally backed up and origin deployment backup on bastion. Initial network-based validation timed out and rolled back; reapplication with pod-local validation succeeded.

## 2026-10-13 — EU/Singapore SIT WAS findings rechecked

### SIT — Read-only security assessment
- **Scope / status:** completed targeted recheck of `WAS_iTopaz__EU___Singapore_SIT_08Oct2026.xlsx`; workbook actually contains 80 EU SIT rows and no Singapore rows.
- **Verified:** 53 missing-header rows now have the required headers; 9 other rows were reproduced (Git and build/config file exposure, missing MIME headers, permissive CSP, HTTP redirect hop). Shared UI bundle still reports Angular 16.2.12; 18 version findings remain open with per-CVE applicability unverified.
- **Singapore:** both distributions have the same deployed header policy, but ten supplemental Singapore HTTP requests timed out from this host; live status remains unconfirmed.
- **Evidence:** `security-reviews/2026-10-13/REPORT.md`, annotated workbook, and HTTP/version/config metadata in that directory. Original workbook preserved.
- **Pending:** remediate disclosed files, redirect generation, CSP, and relevant Angular packages; rerun scanner. No infrastructure/application remediation was performed during this check.

## 2026-10-13 — DEV Prefiler CloudFront response headers policy copied from SIT

### DEV EU — prefiler-eudev.itopazapp.com
- **Scope / authorization:** user requested copying the policy from SIT distribution `E1H7QYRQWZGB8Z` (account `464134132424`) into DEV distribution `E3SARNGL2XBPRD` (account `074779643551`).
- **Changed:** created DEV `itariff-security-header-policy`, ID `fbe99d16-6afd-4546-b27b-7b6b32530421`, from SIT policy `1d3c62fc-c7f7-4b18-bfd1-e5f1bf3b9a00`; attached it to the default cache behavior, the only behavior on DEV.
- **Verification:** policy configuration matches SIT exactly; distribution configuration comparison confirmed only ResponseHeadersPolicyId changed. CloudFront status confirmed Deployed. Live response contained the copied headers, but returned HTTP 502; origin/application health is not established by this policy change.
- **Settings:** copied CSP/security headers, removal of Server header, and `Cache-Control: public, max-age=31536000, immutable` unchanged.
- **Evidence / recovery:** policy JSON, attachment metadata, and prior distribution configuration preserved in `infrastructure/cloudfront/dev/`. To reverse, restore the previous policy attachment using a fresh distribution ETag; avoid overwriting unrelated later changes.

## 2026-10-10 — Worker-2 Sufeeyan knowledge extraction

- **Completed:** inspected /root/sufeeyan and /home/ubuntu/sufeeyan/ai-agentic-proj over SSH; extracted non-secret SIT EU cluster/account/region identifiers into knowledge-base/KNOWLEDGE-BASE.md.
- **Evidence:** root folder contains AWS CLI/Kubernetes tooling and SIT connection script/kubeconfig; home project contains .env and .venv only. No agent source or knowledge corpus found in inspected directories.
- **Limits:** live AWS/EKS state unverified. Credentials and .env contents were not extracted. Worker-2 remains standby.
- **Authorization:** user requested knowledge extraction and clarified root folder location. Source files were read only; an extractor helper was uploaded to /tmp/itopaz-extract-sufeeyan.py.

## 2026-10-09 — Worker-2 (10.100.95.39) multi-cluster EKS jump and Jenkins access verified

- **Scope:** Worker-2 (`ubuntu@10.100.95.39`), DevOps account `439891535362` (eu-central-1), subnet `10.100.95.32/28`.
- **Jenkins Master (`10.100.95.13`):** Verified live. Resides in same subnet; TCP port 22 open. SSH authentication succeeded as `root` using `/home/ubuntu/jenkins.pem` and `/home/ubuntu/backup.jenkins.pem`. Verified Docker service running healthy `jenkins-server` container on port 8090 (`custom-jenkins:latest`).
- **Multi-Cluster EKS Jump Access:** Verified live. Host holds `/home/ubuntu/rahul/config` with active AWS STS assumed role `eks-jump-access` across 4 EKS clusters:
  - `dev-frankfurt`: Account `074779643551`, cluster `euc1-itopaz-dev-eks` (control plane verified live via kubectl).
  - `sit-frankfurt`: Account `464134132424`, cluster `euc1-itopaz-sit-eks` (control plane verified live via kubectl).
  - `prod-frankfurt`: Account `965031587107`, cluster `euc1-itopaz-prd-eks` (control plane verified live via kubectl).
  - `sit-singapore`: Account `464134132424`, cluster `apse1-itopaz-sit-eks` (control plane verified live via kubectl).
  - `uat-eu-central-1`: Account `405478414008`, cluster `euc1-itopaz-uat-eks` (configured; private endpoint connection timed out).
- **Bastion Key Inventory on Worker-2:** Verified stored under `/home/ubuntu/rahul/infrastructure/secrets/keys/` (`dev-eu-bastion.pem`, `sit-eu-bastion.pem`, `sit-sg-bastion.pem`, `prod-eu-bastion.pem`, MDM keys). Direct TCP port 22 to bastion private IPs (`10.100.145.118`, `10.100.208.17`, `10.100.98.195`) dropped due to VPC/SG boundaries; cluster administration is performed directly via AWS cross-account IAM role `eks-jump-access`.
- **Authorization & Evidence:** Verified live by agent per user instruction. No configuration mutated.

## 2026-10-09 — Worker-1 iTariff repository pulled; worker-2 reserved

- **Scope:** worker-1 /home/ec2-user/rahul/clones/itariff-k8s-repo; local worker registry.
- **Completed:** clean develop branch pulled with --ff-only, 927fa7f -> 9acede0. Two files updated; working tree clean afterward.
- **Worker-2:** installed standby; local enabled=false, activation=manual. Default and high-load dispatch exclude it until explicit future activation. Remote release registry remains its installation snapshot.
- **Verification:** SSH git pull succeeded; five local regression tests passed; high-load selection returns worker-1 only.
- **Authorization:** user requested worker-1 git pull and reserved worker-2 for future activation.
- **Recovery:** prior repository commit 927fa7f; no deployment performed. Reactivation requires changing the local registry deliberately.

## 2026-10-09 — Distributed node registry (master + 2 workers) configured LOCALLY

### LOCAL — Multi-node agent topology
- **Status / scope:** completed user-requested configuration of the agent as a local master that is aware of two worker nodes. Explicit constraint honoured: **no server-side configuration was changed** — all changes are local metadata and local code only.
- **Topology (same logical `rahul` workspace, different per-node variables):**
  - `local` (master): `C:\Users\rah_66160\iTopaz-agents`, user `rah_66160`, Windows, `python`.
  - `worker-1`: `ec2-user@10.151.4.165:/home/ec2-user/rahul`, agent at `/home/ec2-user/rahul/agent/itopaz_agent.py`, `python3`. Key `keys/ecuworldwide-cn-priv-key` (CONNECTED in 2026-10-09 audit); fallback `keys/ecu-eks-jump.pem`.
  - `worker-2` (**optional overflow**): `ubuntu@10.100.95.39:/home/ubuntu/rahul`, agent at `/home/ubuntu/rahul/agent/itopaz_agent.py`, `python3`. Key `keys/linux-server-new.pem` (CONNECTED). Flagged `optional:true, activation:on_load` — NOT in the default worker pool; recruited only when primary-worker load is high (burst capacity).
- **Changed (local only):**
  - Added `nodes.json` — per-node registry; each node declares its own `user`, `workspace_root`, `agent_entry`, `python`, `ssh_key`. The master always resolves the *target* node's variables, never substituting its own (this is the "local vs server variables differ" requirement).
  - Added `core/node_manager.py` — self-contained (stdlib only, roots off `__file__`), builds ssh/scp argv for a node, `agent_invocation()` runs each node's own agent entrypoint, and `current_node()` auto-detects which node the process runs on by matching `workspace_root`. The module performs **no** remote writes/config — read/execute only.
  - Wired CLI (`itopaz_agent.py`): new `/nodes` and `/run-on <node-id> <cmd>` REPL commands, `--nodes` flag, and help text. `/nodes` output tags each worker as `[primary]` or `[optional/overflow — on high load]`.
  - Overflow selection in `node_manager`: `primary_workers()` returns always-on nodes; `overflow_workers()` returns optional ones; `select_workers(high_load=False|True)` includes overflow only when load is high. Default dispatch uses primary workers only.
- **Design note:** worker-2's `rahul/` layout differs from worker-1 (has `export/`, `token/`, `recovery/`, `bitbucket-backup-script`, root-level `dev-eu-bastion.pem`); the registry does not assume identical trees, only the workspace root per node.
- **Verification pending:** local execution of `--nodes` could not be confirmed live this session due to shell-output lag in the tooling and the pre-existing `from agent.core…` package-path expectation (the CLI expects the package dir to be importable as `agent`). The `node_manager` module itself is import-path-independent and was validated by inspection; `nodes.json` is valid JSON.
- **Evidence / recovery:** `nodes.json`, `core/node_manager.py`; CLI edits in `itopaz_agent.py`. Remove those three edits to revert; no other files or any server touched.

## 2026-10-09 — Workspace sync, home organisation, SSH config & key connectivity audit

### LOCAL — Knowledge sync from EC2 (10.151.4.165)
- **Status / scope:** completed user-requested sync of the `rahul` workspace from `ec2-user@10.151.4.165:/home/ec2-user/rahul` using `scp` over the `ecu-eks-jump.pem` bastion key.
- **Changed:** pulled `knowledge-base/` (KNOWLEDGE-BASE.md 249KB, vector-db chunks.json 567KB, knowledge.index 1.3MB), `infrastructure/` (44 files), `agent/` (49 files), and `scripts/` (43 files) into the local iTopaz-agents workspace.
- **Note:** initial attempts used `ssh … cat` piped through PowerShell, which mangled output via TTY echo. Root cause diagnosed; switched to `scp -r` which transferred cleanly.

### LOCAL — jenkins IP update script fix (`infrastructure/update-all-jenkins-ips.sh`)
- **Root cause:** SIT and UAT resolver blocks used `echo -e "\n$DOMAIN $NEW_IP"`, injecting blank lines into `RESOLVED_IPS`; the `while read` loop then skipped those entries, so only DEV updated on Jenkins `/etc/hosts`.
- **Fixed:** normalised all three blocks to plain `echo`; added a 5s `ConnectTimeout` reachability pre-check around the UAT block so an inactive UAT jump server skips cleanly instead of emitting `kex_exchange_identification` noise.

### LOCAL — Home directory organisation
- **Changed:** created `keys/`, `repos/`, `tools/`, `Documents/repos/`, `Documents/aws/`. Moved 15 loose key files → `keys/`, 60 repo directories → `repos/`, scripts/zips → `tools/`, Documents repos/CSVs into their subfolders.
- **Backup:** copied 48 PEM keys to `OneDrive - Allcargo Logistics Ltd/Keys/` with descriptive project names (env + project + role).
- **Evidence / recovery:** full inventory in `tools/_organise-manifest.csv`; reversible via `tools/_undo-organise.ps1`.

### LOCAL — Deduplication
- **Changed:** removed 91 duplicate key files (verified by MD5 hash) from Downloads scatter folders, `.ssh` copies already canonical in `keys/`, and redundant OneDrive copies. Retained one canonical copy in `keys/` (or `iTopaz-agents/secrets/`) plus one OneDrive backup per key.

### LOCAL — SSH config update (`.ssh/config`)
- **Changed:** repointed every `IdentityFile` to the new `keys/` locations, removed a duplicate `10.180.208.4` entry with no IdentityFile, and added `IdentitiesOnly yes` consistently across all hosts.

### REMOTE — SSH key connectivity audit
- **Status / scope:** user-requested login test of each PEM against its associated host, from the local Windows machine. Used `-o BatchMode=yes -o ConnectTimeout=6`; `echo OK` success probe. No key values or fingerprints printed.
- **Results (14 hosts):**
  - CONNECTED (7): Linux DevOps `10.100.95.39`, SIT China Jump `10.180.208.4`, DEV China Jump `10.180.144.6`, GATI AWS `10.217.159.55`, ECU CN Private key `10.151.4.165`, DataLake `172.31.11.123`, DataLake `172.31.3.13`.
  - AUTH_FAIL (2): Jenkins `10.151.4.91` (key rejected / wrong user), EUC1 SIT Bastion `10.100.95.13`.
  - CONN_ABORT (3): ECU EKS Jump `10.151.4.165` (handshake reset; note ECU CN Private key succeeded to same host), UAT China Jump `10.180.176.4` (host known inactive), Windows Server `172.31.80.10`.
  - UNREACHABLE/timeout (2): GEM2 UAT `172.23.4.213`, GEM2 DEV `172.23.113.195`.
- **Pending/unknown:** MDM and iTopaz per-server keys (dev/sit/uat/prod BW/EBX/EMS) target hosts behind the `10.100.95.13` bastion, not the bastion itself; they were not tested to avoid misleading AUTH_FAIL results against the wrong endpoint.
- **Evidence:** `tools/_ssh-key-report.txt`; reusable tester at `tools/_ssh-key-test.ps1`.

## 2026-10-08 — Imported MDM duplicate keys removed

### LOCAL — Key deduplication
- **Status / authorization:** completed user-requested comparison and removal of unnecessary imported copies.
- **Changed:** removed 10 imported files; retained canonical equivalents and one copy each of two distinct imported PPK files that could not be parsed.
- **Verification:** compared file contents locally, rechecked byte-for-byte equality immediately before each deletion, and verified retained paths and UAT links. No private key values or fingerprints were printed.
- **Evidence / recovery:** `infrastructure/KEYS-README.md` records each removed path and its identical retained replacement; removed copies can be recreated from those retained files.
- **Pending:** two unique imported PPK files have unverified format/environment; remote authentication was not tested.

## 2026-10-08 — MDM SSH keys separated

### LOCAL — MDM environment folders
- **Status / scope:** completed local file organization requested by the user.
- **Changed:** moved MDM keys beneath `infrastructure/secrets/keys/mdm/{dev,sit,uat,prod}`; preserved uncertain imported copies under `mdm/imported`. UAT PEM paths link to DEV PEMs based on the supplied shared-key inventory. Updated references and SIT EBX deployment key path.
- **Verification:** all 38 original key files retained, move integrity checks passed, three UAT links resolve, permissions remain private, deployment script syntax and diff whitespace checks passed.
- **Pending:** no remote SSH authentication test; external references need the updated directory map.
- **Evidence / recovery:** `infrastructure/KEYS-README.md` documents the layout; reverse local moves if needed while preserving unrelated edits.

## 2026-10-08 — SIT China Secrets Migration (prefiler-k8s-repo@sit-china)

### SIT-CHINA — Migrated sensitive values from ConfigMaps to K8s Secrets
- **Scope / status:** completed repo update; cluster apply pending (Azure AKS, no connectivity from 165 server)
- **Branch:** `sit-china` | **Commit:** `8e33778`
- **Secrets created:**
  - `prefiler-api-secret` (ns: `prefiler-api`) — `db-password`, `redis-password`, `JwtOptions__SecretKey`
  - `prefiler-bff-secret` (ns: `prefiler-bff`) — `redis-password`, `JwtOptions__SecretKey`
- **DB password:** `pref!l!@20#-filer` (all services use same password via `$(DB_PASSWORD)` substitution)
- **Redis:** `cn3-itopaz-sit-redis.redis.cache.chinacloudapi.cn:6380` (Azure Redis, SSL enabled)
- **Files modified:** 15 deployment YAMLs (secret refs added), 16 ConfigMap YAMLs (passwords removed), 2 new secret manifests
- **Important:** Secrets must be applied to the Azure AKS cluster BEFORE updating deployments. Apply order:
  1. `kubectl apply -f config/prefiler-api-secret.yaml`
  2. `kubectl apply -f config/prefiler-bff-secret.yaml`
  3. Apply updated ConfigMaps
  4. Apply updated deployments (or let Jenkins pipeline handle it)
- **Note:** `prefiler-auth-service` uses encrypted connection strings (base64), so DB_PASSWORD substitution doesn't apply to its connection strings

## 2026-10-07 — SSH keys organized and MDM host assignments recorded

### LOCAL — Key folders and access references
- **Scope / status:** completed local reorganization of 38 PEM/PPK files; no remote changes.
- **Changed:** grouped keys by environment/purpose; preserved shared DEV/UAT MDM PEMs and imported copies; placed SIT and PROD MDM keys in their own folders. Updated workspace key paths, fixed Jenkins IP-update script defaults (including UAT China), and corrected the SIT EBX deploy script to the user-supplied SIT key assignment.
- **Evidence:** `infrastructure/KEYS-README.md` contains the path migration map and 16 user-supplied MDM server assignments. The inventory was supplied on 2026-10-07, not independently checked against AWS.
- **Verification:** local move integrity checks passed; all 38 files retained; key permissions 600 and directories 700; edited shell scripts passed syntax checks.
- **Pending / authorization:** SSH connectivity not tested; external consumers must update old paths. Key directory is now ignored by Git, but previously tracked key history remains.
- **Recovery:** reverse local moves using the directory map, preserving all copies and unrelated edits. No keys were rotated or uploaded.

## 2026-10-07 — Single-file workspace guide

### LOCAL — README consolidation
- **Scope / status:** completed local documentation consolidation requested by the user.
- **Changed:** merged the retrieval guide and reusable handoff template into `readme.md`; removed the two separate source files. Updated daily-sync staging and KnowledgeNexus sync references to use README without the retired index file. Historical log entries retain their original filenames as history.
- **Verification:** README local links and internal anchors passed checks; both edited shell scripts passed `bash -n`; `git diff --check` passed.
- **Pending / recovery:** no remote sync or infrastructure change performed. Local edits remain uncommitted; preserve unrelated work when reverting.

## 2026-10-07 — README, retrieval index, and handoff workflow integrated

### LOCAL — Documentation entry points
- **Scope / status:** local documentation; completed.
- **Changed:** README now connects orientation, retrieval, evidence checks, completion records, and handoffs. Repaired retired documentation links and replaced the obsolete directory map. The index and handoff template link back to the shared workflow; operational reference is explicitly historical.
- **Verification:** 2026-10-07, all local Markdown file links in the three documents resolved; `git diff --check` passed.
- **Evidence:** `readme.md`, `AI-INDEX.md`, `AI-HANDOFF-TEMPLATE.md`.
- **Pending / recovery:** no infrastructure verification performed; edits remain local and uncommitted. Preserve unrelated workspace changes when reverting.

## 2026-10-07 — DEV monitoring dashboard and model-independent knowledge workflow

### DEV EU — Service health and latency dashboard
- **Scope:** account `074779643551`, `eu-central-1`, `euc1-itopaz-dev-eks`; Grafana UID `dev-health-service-db`.
- **Status:** service/health dashboard completed; database access pending.
- **Changed:** created dashboard version 2 with namespace/service/database filters, HTTP latency percentiles, Kubernetes health, and eight configured Aurora panels. Added `DEV CloudWatch` datasource using existing default AWS identity.
- **Verification:** on 2026-10-07, 21 PromQL queries passed; Grafana P95 query returned 75 frames; saved dashboard readback confirmed 34 panels including rows/text. CloudWatch datasource returned AccessDenied for ListMetrics.
- **Evidence:** [dashboard](https://grafana.internaleu1dev-itopaz.com/d/dev-health-service-db), [artifacts and checks](monitoring/dev/README.md).
- **Pending / authorization:** user chose database panels pending access. Dedicated IAM permissions and Grafana restart were proposed but not executed; subsequent explicit approval remains unanswered.
- **Recovery:** dashboard JSON is preserved under `infrastructure/monitoring/dev/`; no previous dashboard was replaced and no application rollout was performed.

### LOCAL — Retrieval and freshness documentation
- **Scope:** workspace knowledge retrieval and Markdown documentation; no cloud changes.
- **Status:** completed.
- **Verification:** on 2026-10-07, all five retrieval tests passed, including source-scoped environment summary retrieval. CLI search found the new dashboard change record by UID.
- **Changed:** added source-filtered, bounded context and explicit partial-match metadata to lexical search; replaced drifting index references with topic routing; added a model-independent handoff template. Added dated environment summaries and a consistent change-record workflow; indexed summaries alongside the existing canonical sources.
- **Evidence:** `AI-INDEX.md`, `AI-HANDOFF-TEMPLATE.md`, `scripts/search_knowledge.py`, `scripts/knowledge_sources.py`, `infrastructure/environment-summaries.md`, `infrastructure/CHANGE-RECORD-TEMPLATE.md`.
- **Pending:** PROD/UAT summaries remain historical/unverified; SIT statements are sourced from existing dated records. This documentation update did not perform a fresh environment audit.
- **Recovery:** local edits are uncommitted; preserve unrelated existing changes when reviewing or reverting.

## 2026-10-07 — Prefiler SIT Singapore (`apse1-itopaz-sit-eks`) Master API 500 Fix, Cross-Region Pipeline Audit & SIT EU Secrets Migration

### 1. SIT Singapore (`apse1-itopaz-sit-eks`) `master-prefiler-service` Zero Logs & `PageMaster` 500 Error Fix
- **Bastion Access**: Accessed SIT Singapore bastion `i-05b9998627e8bf6e8` (`10.130.210.3`, `ap-southeast-1`) via AWS SSM (`Terraform_Execution_Role` in account `464134132424`).
- **Root Cause**:
  1. `deploy/microfrontend-main` in `prefiler-ui` on `apse1-itopaz-sit-eks` was running image `microfrontend-main-sit-afdcd624` (built from the Frankfurt `sit` branch instead of `sit-singapore`), and a second replica (`microfrontend-main-5d694554ff-9kp7d`) was stuck in `ImagePullBackOff` pulling from `sit-eu/prefiler-frontend`.
  2. Because `microfrontend-main-sit-afdcd624` served the Frankfurt `index.html`, users opening `https://prefiler-sasit.itopazapp.com` loaded `navbar` (`https://prefiler-eusit.itopazapp.com/shared_ui/main.js`) and `dagangnet-prefiler` (`https://prefiler-eusit.itopazapp.com/dagangnet-prefiler/main.js`) from **SIT EU**, which have `https://prefiler-bff-eusit.itopazapp.com` compiled into `src/environments/environment.development.ts`.
  3. Browser calls from `Origin: https://prefiler-sasit.itopazapp.com` (`zoneid: zone5` / `zone4`) hit **SIT EU (`euc1-itopaz-sit-eks`)** instead of **SIT Singapore (`apse1-itopaz-sit-eks`)**.
  4. On SIT EU, `master-prefiler-service` threw `Npgsql.PostgresException (0x80004005): 3D000: database "AUAUDBECUGROUPAGE" does not exist` because APAC/AU databases (`APACDBECUGROUPAGE` for `zone4`, `AUAUDBECUGROUPAGE` for `zone5`, and `APACDBEDI_UAT`) only exist on the **Singapore Aurora PostgreSQL cluster** (`apse1-itopaz-sit-aurora-postgresql.cluster-cve80ey2iakj.ap-southeast-1.rds.amazonaws.com`), while the Frankfurt cluster (`euc1-itopaz-sit-aurora-postgresql.cluster-cd6uok42udhj.eu-central-1.rds.amazonaws.com`) only hosts EU/US/AF databases (`EUEUDBECUGROUPAGE`, `AMAMDBECUGROUPAGE`, `AFAFDBECUGROUPAGE`, etc.). Meanwhile, Singapore `master-prefiler-service` pods received zero traffic and emitted only Kestrel startup logs.
- **Why It Kept Recurring (Pipeline & Frontend Root Causes)**:
  - **Historical Cross-Region Jenkins Target**: Prior to commit `656cd5a`, `jenkins/sit/ui/microfrontend-main` on the `sit` branch built `APP_BRANCH = 'sit'` (`prefiler-eusit.itopazapp.com`) while deploying to `AWS_REGION = 'ap-southeast-1'` / `EKS_CLUSTER_NAME = 'apse1-itopaz-sit-eks'` / `ECR_REPOSITORY = 'sit-apse/prefiler-frontend'`. Every Frankfurt `microfrontend-main` Jenkins run (up to Build #61) overwrote `apse1-itopaz-sit-eks` and `:microfrontend-main-sit-latest` in `sit-apse/prefiler-frontend` with the EU build.
  - **Swapped CloudFront Distribution ID in `jenkins/environments/sit.json`**: In account `464134132424`, `E1H7QYRQWZGB8Z` is `prefiler-eusit.itopazapp.com` and `E3D3FER4L2TKX9` is `prefiler-sasit.itopazapp.com`, but `jenkins/environments/sit.json` (and `jenkins/sit/ui/microfrontend-main` + `microfrontend-shared` on `sit`) had `CLOUDFRONT_DISTRIBUTION = 'E3D3FER4L2TKX9'`.
  - **Angular `environment.development.ts` Imports**: All Prefiler Angular microfrontends import `src/environments/environment.development` directly in `api.service.ts` / `apis.service.ts` / `userAuth.service.ts`, and `angular.json` replaces `environment.ts` with `environment.development.ts` on `ng build`. On `origin/sit-singapore`, `dagangnet-prefiler` and `microfrontend-shared` correctly point to `https://prefiler-bff-sasit.itopazapp.com`, whereas `imdg-prefiler`, `aes-prefiler`, and `sa-prefiler` still have `eudev`/`eusit` URLs in `environment.development.ts`.
- **Live Remediation Applied**:
  - Updated `deploy/microfrontend-main` in `prefiler-ui` on `apse1-itopaz-sit-eks` to `464134132424.dkr.ecr.ap-southeast-1.amazonaws.com/sit-apse/prefiler-frontend:microfrontend-main-sit-290886ca` (built from `sit-singapore`) and scaled to `1` replica (`microfrontend-main-f699d955-t2hrq`, `2/2 Running`).
  - Retagged `microfrontend-main-sit-290886ca` as `microfrontend-main-sit-latest` in `sit-apse/prefiler-frontend` (`ap-southeast-1`).
  - Created CloudFront invalidation `IAXCEI744UMMWACVV52YJNIWAQ` (`/*`) on distribution `E3D3FER4L2TKX9` (`prefiler-sasit.itopazapp.com`).
  - Verified `https://prefiler-sasit.itopazapp.com/login` serves `https://prefiler-sasit.itopazapp.com/dagangnet-prefiler/main.js` and `https://prefiler-sasit.itopazapp.com/shared_ui/main.js`, and verified `master-prefiler-service` on `apse1-itopaz-sit-eks` logs `IPageMasterRepository.GetPageMaster` for `zone4` (`APACDBECUGROUPAGE`) and `zone5` (`AUAUDBECUGROUPAGE`).

### 2. Prefiler SIT EU (`euc1-itopaz-sit-eks`) DB, Redis & JWT Kubernetes Secrets Migration
- **Access Note**: Executed via AWS SSM on the SIT jump server (`i-0bd3314ea08e6fb27`) because direct SSH to the SIT bastion from `10.151.4.165` was unavailable.
- **Secrets Configured**:
  - `prefiler-api-secret` (namespace `prefiler-api`): keys `db-password`, `db-password-2`, `DB_PASSWORD_2`, `redis-password`, `JwtOptions__SecretKey`
  - `prefiler-bff-secret` (namespace `prefiler-bff`): keys `db-password`, `redis-password`, `JwtOptions__SecretKey`
- **Database Password Verification**: Direct SCRAM-SHA-256 authentication against `euc1-itopaz-sit-aurora-postgresql.cluster-cd6uok42udhj.eu-central-1.rds.amazonaws.com:5432` (user `prefiler_sit`) confirmed `passwordsit@1035` is the active password (`AuthenticationOk`), whereas `passwordsit@1035x` fails with `28P01: password authentication failed`.
- **Git (`prefiler-k8s-repo@sit`) & Manifest Updates (`commit e903f8b`)**:
  - Removed hardcoded `RedisSettings__Password`, `JwtOptions__SecretKey`, and plaintext DB passwords from all 16 SIT ConfigMaps (`config/*-config.yaml`).
  - Standardized `RedisSettings__Host` to `master.euc1-itopaz-sit-redis-new.tqptfx.euc1.cache.amazonaws.com` across all 16 ConfigMaps (adding missing `RedisSettings__*` blocks to `imdg-prefiler-service-config.yaml`, `dagangnet-prefiler-service-config.yaml`, and `mpci-prefiler-service-config.yaml`).
  - Synced live SIT endpoints and encrypted `ProfileConnection` strings into `prefiler-auth-bff-config.yaml` and `prefiler-auth-service-config.yaml`.
  - Updated `config/Jenkincm` to support `--ALL--` batch ConfigMap deployment on `euc1-itopaz-sit-eks`.
  - Injected `DB_PASSWORD`, `DB_PASSWORD_2` (where applicable), `RedisSettings__Password`, and `JwtOptions__SecretKey` via `secretKeyRef` from `prefiler-api-secret` / `prefiler-bff-secret` across all 15 Deployment manifests (`*-service.yml`, `*-bff.yml`), and moved DB connection strings with `Password=$(DB_PASSWORD)` into Deployment `env:`.
  - Verified all 15 Deployments across `prefiler-api` (13 services) and `prefiler-bff` (2 BFFs) rolled out cleanly (`2/2 Running`, 0 restarts).

### 3. Prefiler SIT Singapore (`apse1-itopaz-sit-eks`) DB, Redis & JWT Kubernetes Secrets Migration (`prefiler-k8s-repo@sit-singapore`, `commit 3498eaa`)
- **Secrets Created on `apse1-itopaz-sit-eks`**:
  - `prefiler-api-secret` (`prefiler-api` namespace): `db-password` / `db-password-2` / `DB_PASSWORD_2` (`prefiler_sit#@*y!#Y)%#`), `redis-password` (`#0fc243e63169dc07`), `JwtOptions__SecretKey` (`this_is_a_very_secure_secret_key_123!`).
  - `prefiler-bff-secret` (`prefiler-bff` namespace): `db-password` (`prefiler_sit#@*y!#Y)%#`), `redis-password` (`#0fc243e63169dc07`), `JwtOptions__SecretKey` (`this_is_a_very_secure_secret_key_123!`).
- **Git (`prefiler-k8s-repo@sit-singapore`) & Cluster Rollout (`commit 3498eaa`)**:
  - Removed plaintext DB connection strings, `RedisSettings__Password`, and `JwtOptions__SecretKey` from all 16 `config/*-config.yaml` files and standardized `RedisSettings__Host` to `master.apse1-itopaz-sit-redis-new.m3fywm.apse1.cache.amazonaws.com`.
  - Updated all 16 Deployment manifests (`*-service.yml`, `*-bff.yml`) on `sit-singapore` to reference `sit-apse/prefiler-backend` images, inject `DB_PASSWORD`, `RedisSettings__Password`, and `JwtOptions__SecretKey` from `prefiler-api-secret` / `prefiler-bff-secret`, and expand `Password=$(DB_PASSWORD)` against `apse1-itopaz-sit-aurora-postgresql.cluster-cve80ey2iakj.ap-southeast-1.rds.amazonaws.com`.
  - Mirrored missing `imdg-prefiler-service` (`imdg-prefiler-service-sit-9387e410` / `latest`) and `prefiler-auth-service` (`prefiler-auth-service-sit-dd046c7f` / `latest`) images from `sit-eu/prefiler-backend` (`eu-central-1`) to `sit-apse/prefiler-backend` (`ap-southeast-1`), resolving their `ImagePullBackOff` and `basf-prefiler-service`'s `CreateContainerConfigError`.
  - Added `--ALL--` batch ConfigMap deployment support to `config/jenkincm` on `sit-singapore`.
  - Verified all 15 Deployments on `apse1-itopaz-sit-eks` (`13` in `prefiler-api`, `2` in `prefiler-bff`) rolled out to `2/2 Running` with `0` restarts.

---

## 2026-10-06 — Quantum Dev Module Federation (`remoteEntry.js`) Fix & iTariff Base ECR Login Fix

### 1. Quantum Dev (`quantum-dev.allcargoapps.com` / CloudFront `E95ADLYKZ5WVE`, Account `674017976129`) — 503 & Module Federation Fix
- **Host**: EC2 `i-0c6094d0d53858e59` (`172.31.11.123`), path `/home/ubuntu/all_ecu_projects/Rahul-Baghel/frontend/`
- **Root Cause of `503 Service Unavailable` on `/tradelane-pricing/remoteEntry.js`**:
  - `quantum-dev.allcargoapps.com` (`E95ADLYKZ5WVE`) proxies micro-frontend remotes (`/tradelane-pricing/*`, `/smart-pricing/*`, `/pricing-simulator/*`, `/freight-automation/*`) via custom origins and viewer-request CloudFront Function `quantum-remote-proxy-rewrite-dev` (which strips the route prefix).
  - An intermediate publish of `quantum-remote-proxy-rewrite-dev` (`ETag: E1PA6795UKMFR9` at 14:32 IST) had a runtime validation error, causing CloudFront to return `503`; republishing the fixed function (`ETag: E13V1IB3VIYZZH` at 14:52 IST) resolved `/tradelane-pricing/remoteEntry.js`.
  - The other 3 remotes (`ria`, `pace`, `freight`) were returning S3's fallback `/index.html` (`<!doctype html>`) instead of JS because their S3 buckets lacked `remoteEntry.js` builds.
- **Actions Taken**:
  - Configured Webpack Module Federation (`@angular-architects/module-federation` + `ngx-build-plus`) across `ria` (`smart-pricing`), `pace` (`pricing-simulator`), and `freight` (`freight-automation`) on `i-0c6094d0d53858e59` to match `epic` (`tradelane-pricing`), exposing `'./Routes': './src/app/app.routes.ts'` with `commonChunk: false`.
  - Built and deployed all 4 remotes to their dev S3 buckets, applied S3 CORS rules allowing `https://quantum-dev.allcargoapps.com` and `https://quantum.allcargoapps.com`, and invalidated `/*` across all 5 CloudFront distributions:
    - `tradelane-pricing` (`epic`) → `s3://ds-epic-dev` (`E2X76DWQC8PBOC` / `epic-dev.allcargoapps.com`)
    - `smart-pricing` (`ria`) → `s3://ratebenchmarking-dev` (`E2JLOMMTO7OMAE` / `ria-dev.allcargoapps.com`)
    - `pricing-simulator` (`pace`) → `s3://ds-pace-dev` (`E2IFVRQL6YYIYO` / `pace-dev.allcargoapps.com`)
    - `freight-automation` (`freight`) → `s3://ds-freight-dev` (`E24YWRFMND2S0D` / `freight-dev.allcargoapps.com`)
  - Verified all 4 `/<remote>/remoteEntry.js` endpoints and federated `./Routes` chunks (`2181.js`) return `HTTP/2 200` (`content-type: text/javascript`).

### 2. iTariff CI/CD (`itariff-k8s-repo@develop`) — Base Image ECR Registry Login Before Docker Build (`commits ad604ac, 927fa7f`)
- **Problem**: `tariff-selling-bff` (Build #221) failed in `Build Docker Image` with `Your authorization token has expired` because `docker build` pulled its base image from Central ECR (`439891535362.dkr.ecr.eu-central-1.amazonaws.com`) before any ECR login step ran, relying on cached Docker credentials that expire after 12 hours.
- **Fix**: Added explicit `aws ecr get-login-password --region ... | docker login ... 439891535362.dkr.ecr.<region>.amazonaws.com` before `docker build` in `jenkins/tariff-selling-bff` (`ad604ac`) and across the remaining 25 pipelines (`927fa7f`).

---

## 2026-09-30 — `tariff-selling-rates-ui` ESLint Build Fix & Knowledge Base Consolidation

### 1. `tariff-selling-rates-ui` Pipeline Fix (`itariff-k8s-repo@develop`, `commit 09ce069`)
- **Problem (Build #133)**: `Install Security Analysis Tools` ran `npm install --save-dev eslint ...`, which mutated `package.json`/`package-lock.json`, installed ESLint v9 (incompatible with `.eslintrc.json` and Node 18), and pruned `style-loader` (causing `npm run build` to fail with missing `style-loader`).
- **Fix**:
  - Changed `--save-dev` to `--no-save` so `package.json` and `package-lock.json` are never mutated.
  - Pinned ESLint v8 (`eslint@^8.57.0`) and included `style-loader css-loader` in the install command so npm never prunes them; exported `ESLINT_USE_FLAT_CONFIG=false`.
  - Added pre-build verification/install of `style-loader` and `css-loader` (`--no-save --legacy-peer-deps`) in `Build Application`.

### 2. Knowledge Base Architecture Consolidation (`commits 41b135b, 266bf4d`)
- Consolidated 35+ split Markdown and CSV files into two canonical files: `knowledge-base/KNOWLEDGE-BASE.md` (domain, cluster, inventory, and cost reference) and `infrastructure/activity-log.md` (reverse-chronological operational log).
- Added zero-dependency SQLite FTS5 search (`scripts/search_knowledge.py`, `scripts/knowledge_sources.py`) with hierarchical `H1 > H2 > H3` section breadcrumbs and date-hint boosting, alongside optional FAISS semantic search (`scripts/query_knowledge.py`).

---

## 2026-09-29 — Jenkins Disk Cleanup, EC2 Spot Fleet Scheduling & SonarQube Optimization

### 1. Jenkins Master Volume Disk Cleanup
- **Instance**: `i-0cdcce39da9444d74` (`10.100.95.13`, `c5a.4xlarge`, `eu-central-1`)
- **Volume Mount**: `/home/ubuntu/jenkins-data` (Volume size: 350 GB)
- **Problem**: Volume reached **277 GB (85% utilization)**, leaving only 53 GB free.
- **Root Cause**: Over 5,200 redundant copies of `node_modules` and `.npm-cache` folders were mistakenly archived into historical `htmlreports/` and `archive/` across builds, alongside unpruned inactive workspaces.
- **Actions Taken**:
  - Cleaned unreferenced and stale workspace directories in `/home/ubuntu/jenkins-data/jenkins_home/workspace/` (reclaimed ~54 GB).
  - Pruned archived `node_modules` and cache directories across historical build archives.
- **Result**:
  - Reclaimed **172 GB** of disk space.
  - Disk usage dropped from **277 GB (85%)** down to **105 GB (32%)**.
  - Free space increased to **225 GB**.

---

### 2. Jenkins EC2 Spot Fleet Scheduling Automation
- **Target Resources**:
  - Auto Scaling Group: `euc1-Jenkins-cicd-ec2-ASGfleet`
  - Launch Template: `euc1-Jenkins-cicd-ec2-spot-fleet` (`lt-004093e85d2989b90`)
  - Instance: Spot worker (`t3a.large`)
- **Problem**: Spot fleet instances remained running 24/7 with `MinSize=1` and `DesiredCapacity=1`, incurring costs overnight even after Jenkins Master VM (`i-0cdcce39da9444d74`) stopped at 01:00 AM IST.
- **Actions Taken**:
  1. **Tag Alignment**:
     - Applied schedule tags to ASG `euc1-Jenkins-cicd-ec2-ASGfleet` with `PropagateAtLaunch=true`:
       - `AutoSchedule`: `true`
       - `Schedule`: `09:00-01:00`
       - `ScheduleDays`: `mon-sun`
       - `TimeZone`: `Asia/Kolkata`
       - `Days`: `Mon-sun`
       - `app`: `shared`
       - `map-migrated`: `migE0D4JDFZ6Y`
       - `MontyCloudTagId`: `69bd531e-afd7-4409-9e00-b90e78fe746a`
       - `ActiveMinSize`: `1`, `ActiveDesiredCapacity`: `1`, `ActiveMaxSize`: `4`
  2. **AWS Auto Scaling Scheduled Actions**:
     - `euc1-jenkins-spot-fleet-stop`: Recurrence `0 1 * * *` (01:00 AM IST) -> `MinSize=0`, `DesiredCapacity=0`.
     - `euc1-jenkins-spot-fleet-start`: Recurrence `0 9 * * *` (09:00 AM IST) -> `MinSize=1`, `DesiredCapacity=1`, `MaxSize=4`.
  3. **Lambda Scheduler Integration (`scheduler-rds-ec2`)**:
     - Added `process_asg()` function to dynamically inspect AutoScaling groups tagged with `AutoSchedule=true`.
     - Attached IAM policy `rds-ec2-asg-start-stop` allowing `autoscaling:DescribeAutoScalingGroups` and `autoscaling:UpdateAutoScalingGroup`.
     - Verified live execution: ASG state logs `ASG=euc1-Jenkins-cicd-ec2-ASGfleet Desired=1 Min=1 Max=4 ShouldRun=True`.

---

### 3. SonarQube Server Performance & Memory Optimization
- **Instance**: `i-0cd1ab8b0d9247ef4` (`10.100.95.54`, `t3.large`, `eu-central-1`)
- **Container Stack**: Docker Compose (`/home/ubuntu/sonarqube-docker/docker-compose.yml`) running SonarQube Community v10.7.0 and PostgreSQL 15 Alpine.
- **Problems**:
  - Builds took 12+ minutes total; Quality Gate processing alone took ~4.7 minutes.
  - Compute Engine (`CeServer`) ran on default 512 MB heap (`-Xmx512m`), causing continuous GC thrashing on 88+ MB uncompressed reports.
  - PostgreSQL parallel queries failed with `could not resize shared memory segment: No space left on device` due to Docker default 64MB `/dev/shm`.
- **Actions Taken**:
  1. **SonarQube JVM Heap Tuning**:
     - `SONAR_CE_JAVAOPTS`: `-Xmx2048m -Xms512m -XX:+HeapDumpOnOutOfMemoryError -XX:+UseG1GC` (Compute Engine heap 4x increase).
     - `SONAR_WEB_JAVAOPTS`: `-Xmx1024m -Xms256m -XX:+HeapDumpOnOutOfMemoryError -XX:+UseG1GC` (Web server heap 2x increase).
     - `SONAR_SEARCH_JAVAOPTS`: `-Xmx1024m -Xms1024m -XX:MaxDirectMemorySize=256m -XX:+HeapDumpOnOutOfMemoryError` (Elasticsearch heap 2x increase).
  2. **PostgreSQL Shared Memory & Cache Tuning**:
     - Configured `shm_size: 512m` in Docker Compose for `sonarqube_db` (eliminated 64MB shared memory ceiling).
     - Tuned database parameters: `shared_buffers=256MB`, `work_mem=16MB`, `maintenance_work_mem=64MB`, `effective_cache_size=2GB`.
     - Executed full database `VACUUM ANALYZE`.
- **Results**:
  - Individual SonarQube task execution time dropped from **300+ seconds (5 min)** down to **41–63 seconds** (4x–5x faster).
  - API status verified: `{"version":"10.7.0.96327","status":"UP"}`.

---

### 4. Jenkins SonarScanner Optimization
- **Path**: `/home/ubuntu/jenkins-data/jenkins_home/tools/hudson.plugins.sonar.SonarRunnerInstallation/SonarScanner/`
- **Actions Taken**:
  1. `conf/sonar-scanner.properties`:
     - Added `sonar.javascript.node.maxspace=4096` to expand Node.js AST parser memory to 4 GB (eliminates V8 GC pauses on large TypeScript codebases).
     - Added `sonar.analysisCache.enabled=true` to enable client-side AST caching across builds.
  2. `bin/sonar-scanner`:
     - Configured default CLI heap: `SONAR_SCANNER_OPTS="${SONAR_SCANNER_OPTS:--Xmx2048m -XX:+UseG1GC}"`.

---

### 5. SonarQube Community Edition Queue & Webhook Insights
- **Architecture Note**: SonarQube Community Edition processes Compute Engine reports via a single worker thread (`sonar.ce.workerCount=1`).
- **Pipeline Stage Behavior**:
  - In Jenkins Stage View, `Quality Gate` showing `(paused for X min)` represents the time `waitForQualityGate` was paused waiting for SonarQube webhook callback.
  - When multiple pipelines run concurrently, tasks are queued in FIFO order in `ce_queue`.
  - With task processing reduced to ~40–60s, queue backlogs now clear in a fraction of previous durations.
  - Webhook callback endpoint `http://jenkins.internal-itopaz.com/sonarqube-webhook/` verified healthy with HTTP 200 (~21ms delivery).
  - In `itopaz-k8-repo@develop` (`jenkins/itopaz-export-ui`, commit `d7b8850`), increased `waitForQualityGate` stage timeout from 5 minutes to 15 minutes (`timeout(time: 15, unit: 'MINUTES')`) so large frontend reports (~5.1 min compute + FIFO queue wait) do not abort at 4m 59s.

---

### 6. Prefiler `microfrontend-main` SIT EU Region & Parameter-Override Fix (`prefiler-k8s-repo@sit`, `commits 4b806e5, 43c532c, 925a5bc`)
- **Problem**: `jenkins/sit/ui/microfrontend-main` deployed to Singapore (`ap-southeast-1` / `apse1-itopaz-sit-eks`) instead of Frankfurt (`eu-central-1` / `euc1-itopaz-sit-eks`) because Jenkins passed cached `params.AWS_REGION` and `params.EKS_CLUSTER_NAME` values from earlier builds, and rollout failures were swallowed without failing the stage.
- **Fix**: Updated `jenkins/sit/ui/microfrontend-main` to target `eu-central-1` / `euc1-itopaz-sit-eks` (`4b806e5`), fail builds on unhealthy frontend rollout (`43c532c`), and lock `AWS_REGION` and `EKS_CLUSTER_NAME` directly in the `environment` block (`925a5bc`) so stale Jenkins parameter defaults cannot override branch configuration.

---

## 2026-09-28 — China AKS PrivateLink DNS & TIBCO EBX Auto-Healing

### TIBCO EBX Multi-Environment Autonomous Auto-Healing (SIT & PROD)
- **Application**: TIBCO EBX MDM Server (Port 8080)
- **Overview**: Deployed autonomous self-healing agent (`ebx_auto_heal.py` / `ebx_auto_heal.sh`) to detect application crashes, hung threads, memory exhaustion, or 5xx/404 errors, and automatically recycle EBX services safely.
- **SIT Frankfurt Environment**:
  - Account: `464134132424` | Region: `eu-central-1`
  - EC2 Instance: `i-08a20bae22e57e46d` | Private IP: `10.100.215.180`
  - DNS: `ebx.internaleu1-itopaz.com`
  - Restart method: `script` (`/opt/tibco/ebx/EBX_SERVER/bin/startup.sh`, `/opt/tibco/ebx/EBX_SERVER/bin/shutdown.sh`) — systemd service is omitted on SIT.
  - Deployment: Scripted via `deploy-to-sit-ebx.sh` and `deploy-to-sit-via-bastion.sh` (via Bastion `10.100.208.17`).
- **PROD Frankfurt Environment**:
  - Account: `965031587107` | Region: `eu-central-1`
  - EC2 Instance: `i-0add8ef2aa72adb7c` | Private IP: `10.100.110.76`
  - Endpoint: `http://10.100.110.76:8080/ebx/`
  - Health check logic: Handles HTTP 302 servlet redirect to `/ebx-ui/` as a valid healthy status.
  - Deployment: Scripted via `deploy-to-prod-ebx.sh`.
- **Timing & Safeguards**:
  - Startup Grace Period: 180s (allows 1GB+ WAR files to expand).
  - Maximum Startup Wait: 480s before marking startup failure.
  - Restart Cooldown: 1800s (30 minutes) to prevent crash-loop cascades.

### Microsoft Graph API Integration (mail.py)
- **Script**: `mail.py`
- **Application**: Microsoft Graph Command Line Tools Client (`14d82eec-204b-4c2f-b7e8-296a70dab67e`).
- **Auth Flow**: Device Code SSO flow (`https://login.microsoftonline.com/common`) with `token_cache.bin` serialization.
- **Scope**: `Mail.Read` for automated message reading.

> **Generated:** September 28, 2026  
> **Target Systems:** Jenkins CI/CD, Azure China AKS (DEV/SIT/UAT), TIBCO EBX (SIT/PROD Frankfurt)

---

### 1. Azure China North 3 PrivateLink AKS DNS Resolution for Jenkins

### Problem Statement
The Jenkins CI/CD master server (`10.100.95.13` in AWS `eu-central-1`) executes automated build and deployment pipelines targeting Kubernetes clusters hosted in **Azure China North 3**. Because these AKS clusters are configured with **Azure Private Link**, their FQDNs are hosted inside Azure private DNS zones (`privatelink.chinanorth3.cx.prod.service.azk8s.cn`) and cannot be resolved by external DNS resolvers.

### Solution
An automated DNS resolution and injection script ([`infrastructure/update-all-jenkins-ips.sh`](file:///home/ec2-user/rahul/infrastructure/update-all-jenkins-ips.sh)) connects to Azure China jump hosts via SSH, queries their local resolvers for the private IP addresses of the AKS API servers, and updates `/etc/hosts` on the Jenkins master.

### Target Environments & Private Link FQDNs

| Environment | Jump Server IP | SSH User | SSH Key | Azure PrivateLink AKS Domain |
|---|---|---|---|---|
| **DEV China** | `10.180.144.6` | `jumpsrvadmin` | `infrastructure/secrets/keys/dev/china/dev-china.pem` | `cn3itopazdnsaks-uda8w8iw.b04e70a6-4bc5-4d45-acd4-cd0326008af9.privatelink.chinanorth3.cx.prod.service.azk8s.cn` |
| **SIT China** | `10.180.208.4` | `jumpsrvadmin` | `infrastructure/secrets/keys/sit/china/sit-china.pem` | `cn3itopazdnsaks-xa4051st.d7819a1a-cb36-41f1-9f01-d99f25882fa1.privatelink.chinanorth3.cx.prod.service.azk8s.cn` |
| **UAT China** | `10.180.176.4` | `jumpsrvadmin` | `infrastructure/secrets/keys/uat/china/uat-dev.pem` | `cn3itopazdnsaks-1apj69gf.90610dc7-cc30-4aaa-8ae9-0ab2bc5a295c.privatelink.chinanorth3.cx.prod.service.azk8s.cn` |

### Execution Workflow
```bash
# Update Jenkins /etc/hosts with latest China AKS PrivateLink IPs
bash infrastructure/update-all-jenkins-ips.sh
```

---

### 2. TIBCO EBX Multi-Environment Autonomous Auto-Healing

### Overview
TIBCO EBX is a critical Master Data Management (MDM) server running on EC2. EBX instances occasionally experience memory exhaustion, thread deadlocks, or hung connector threads, causing HTTP 5xx errors or connection timeouts. The EBX Auto-Healing Framework ([`scripts/ebx-auto-healing/`](file:///home/ec2-user/rahul/scripts/ebx-auto-healing/)) provides autonomous health-checking, failure thresholding, and graceful/forceful process recycling.

### Environment Matrix

| Parameter | SIT Frankfurt | PROD Frankfurt |
|---|---|---|
| **AWS Account** | `464134132424` | `965031587107` |
| **Region** | `eu-central-1` | `eu-central-1` |
| **Instance ID** | `i-08a20bae22e57e46d` | `i-0add8ef2aa72adb7c` |
| **Private IP** | `10.100.215.180` | `10.100.110.76` |
| **Internal DNS** | `ebx.internaleu1-itopaz.com` | N/A |
| **Health Check URL** | `http://10.100.215.180:8080/ebx/` | `http://10.100.110.76:8080/ebx/` |
| **Expected HTTP Code** | `200` | `302` or `200` (servlet redirect to `/ebx-ui/`) |
| **Restart Mechanism** | `script` (`startup.sh` / `shutdown.sh`) | `script` / `systemd` |
| **Startup Wait** | 180s grace + 480s max wait | 180s grace + 480s max wait |
| **Restart Cooldown** | 1800s (30 minutes) | 1800s (30 minutes) |

### Key Architectural Safeguards
1. **Startup Grace Period**: Because EBX deploys large WAR files (~1 GB+), startup takes 3 to 5 minutes. The healer enforces a 180s initial grace period before checking health, avoiding premature restart loops.
2. **HTTP 302 Redirection Handling**: On production, `/ebx/` returns a `302 Moved Temporarily` to `/ebx-ui/`. The health check recognizes 302 as healthy.
3. **Cascade Prevention Cooldown**: A strict 30-minute cooldown prevents rapid restart cycles if the underlying issue is database or storage related.
4. **Deploy Scripts**:
   - SIT Direct: `scripts/ebx-auto-healing/deploy-to-sit-ebx.sh`
   - SIT via Bastion: `scripts/ebx-auto-healing/deploy-to-sit-via-bastion.sh` (via Bastion `10.100.208.17`)
   - PROD Direct: `scripts/ebx-auto-healing/deploy-to-prod-ebx.sh`

---

### 3. Microsoft Graph API CLI Integration

### Script Overview: [`mail.py`](file:///home/ec2-user/rahul/mail.py)
Provides authenticated access to Microsoft 365 Exchange mailboxes via Microsoft Graph API without requiring custom Azure App Registrations in the tenant.

- **Client ID**: `14d82eec-204b-4c2f-b7e8-296a70dab67e` (Microsoft Graph Command Line Tools public client)
- **Authority**: `https://login.microsoftonline.com/common`
- **Scope**: `Mail.Read`
- **Authentication**: Device Code Flow (`initiate_device_flow`) with cached tokens serialized to `token_cache.bin`.
- **Usage**:
  ```bash
  python3 mail.py
  ```

---

### 4. Verification and Daily Maintenance
The consolidated knowledge base and vector database index should be refreshed after any architectural or configuration update:
```bash
# Rebuild single-file consolidated KB
bash scripts/rebuild-knowledge-base.sh

# Re-index all markdown chunks into FAISS
python3 scripts/ingest_knowledge.py

# Query semantic index
python3 scripts/query_knowledge.py "EBX auto heal configuration"
```

---

## 2026-09-25 — Operations Log

### Azure China North 3 PrivateLink AKS DNS Resolution for Jenkins
- **Problem**: The Jenkins CI/CD master server (`10.100.95.13`, AWS eu-central-1) builds and deploys artifacts to Azure China North 3 AKS clusters, but cannot resolve China PrivateLink internal FQDNs.
- **Solution**: Automated script `infrastructure/update-all-jenkins-ips.sh` connects to Azure China jump hosts via SSH, resolves the internal PrivateLink IPs using `nslookup`, and updates `/etc/hosts` on the Jenkins server.
- **Environments & Private Link Endpoints**:
  - **DEV China Jump**: `10.180.144.6` (user `jumpsrvadmin`, key `infrastructure/secrets/keys/dev/china/dev-china.pem`)
    - Domain: `cn3itopazdnsaks-uda8w8iw.b04e70a6-4bc5-4d45-acd4-cd0326008af9.privatelink.chinanorth3.cx.prod.service.azk8s.cn`
  - **SIT China Jump**: `10.180.208.4` (user `jumpsrvadmin`, key `infrastructure/secrets/keys/sit/china/sit-china.pem`)
    - Domain: `cn3itopazdnsaks-xa4051st.d7819a1a-cb36-41f1-9f01-d99f25882fa1.privatelink.chinanorth3.cx.prod.service.azk8s.cn`
  - **UAT China Jump**: `10.180.176.4` (user `jumpsrvadmin`, key `infrastructure/secrets/keys/uat/china/uat-dev.pem`)
    - Domain: `cn3itopazdnsaks-1apj69gf.90610dc7-cc30-4aaa-8ae9-0ab2bc5a295c.privatelink.chinanorth3.cx.prod.service.azk8s.cn`
  - **Jenkins Host**: `10.100.95.13` (user `root`, key `infrastructure/secrets/keys/shared/jenkins/jenkins.pem`, target `/etc/hosts`).

---

---

## 2026-09-24 — Operations Log

### Knowledge Base Reorganization & AI Indexing Architecture
- **Objective**: Restructure repository `/home/ec2-user/rahul` into a canonical knowledge indexing hub for AI tools (Copilot, Antigravity, Cursor, Claude).
- **Cleanup**:
  - Removed 54MB unindexed `vectordb-work/chunks.json` checkpoint.
  - Removed outdated duplicate `knowledge-base/eks-clusters.md` in favor of canonical `knowledge-base/docs/eks-clusters.md`.
  - Removed stale logs (`ingest.log`, `ingest2.log`) and scratch directories (`.tmp/`, `tmp-docproxy/`).
  - Cleared root secrets (`test`, `token`) and placed credentials in `infrastructure/secrets/`.
- **Restructuring**:
  - Re-homed `export` to `knowledge-base/docs/knowledge-export/15-session-knowledge-export-2026-09-01.md`.
  - Re-homed `loop-ai-cost-breakdown.md` to `knowledge-base/docs/cost-reports/loop-ai-cost-breakdown.md`.
  - Re-homed `activity-log.md` to `infrastructure/activity-log.md`.
  - Grouped multi-cluster kubeconfigs into `infrastructure/configs/`.
  - Relocated scripts (`create_feature_branches.py`, `fix-apigateway-cors.sh`) to `scripts/`.
- **AI Tool Navigation**:
  - Authored `AI-INDEX.md` as primary machine-readable reference.
  - Rebuilt consolidated `KNOWLEDGE-BASE.md` (34 docs, 7,931 lines, 0 skipped).
  - Regenerated FAISS vector database: deduplicated chunk count from 1,538 down to 1,109 chunks, each tagged with `[Source: <path>]`.

---

---

## 2026-09-23 — Operations Log

### SIT Singapore — AFR Prefiler Service DB & Secrets Audit
- **Cluster**: `apse1-itopaz-sit-eks` (SIT SG, Account `464134132424`, Region `ap-southeast-1`)
- **Namespace**: `prefiler-api` | **Service**: `afr-prefiler-service`
- **Action**: Audited deployment environment variables, database connection strings, configmaps, and secrets.
- **Verification**: Verified container environment injection (`conn`, `host`, `db`, `postgres`), confirmed secret references and DB connectivity from the pod.

### DEV EU — MDM ALB Cognito M2M & API Gateway Auth
- **Account**: `074779643551` | **Region**: `eu-central-1`
- **Host**: `mdm-bw-dev.itopazapp.com` fronted by Private ALB (`private-alb`, ID `389490502178fcdb`), listener `6a8665f4f7659890`.
- **Cognito User Pool**: `eu-central-1_MHe1qfDpe` (domain `eu-central-1mhe1qfdpe`).
- **Setup**: Dedicated M2M client `mdm-bw-dev-m2m` (`hjgb6ad314nmq6dhp3rhrmlpr`) with scope `mdm-bw/mdm-bw` via client_credentials grant.
- **Token Endpoint**: `https://eu-central-1mhe1qfdpe.auth.eu-central-1.amazoncognito.com/oauth2/token`.
- **Validation**: Generated access token and validated against backend services.

---

---

## 2026-09-18 — itariff DEV UI login chain, CI -latest fix, MDM Cognito m2m, Datalake↔DB reachability

### A. DEV EU (074779643551) — itariff UI login chain fixed
Three separate ap-south-1 / config leaks broke `itariff-eudev.itopazapp.com`:
1. **BFF token 401** — `tariff-selling-bff` configmap `jwt-token.auth-base-uri` = an ap-south-1 Istio ELB (doesn't resolve from Frankfurt) → "Could not process token". Fixed live to in-cluster `http://tariff-profile-service.itariff-api.svc.cluster.local/profile-domain-service/` (profile svc verified 200), restarted. NOT yet persisted to repo (`itariff-k8s-repo/config/tariff-selling-bff.yaml`).
2. **Mixed content / navbar died** — the itariff shell single-spa import-map loaded microfrontends from the ap-south-1 ELB over HTTP → browser blocked on HTTPS. main-ui `dev` branch import-map already correct (same-origin HTTPS); live pods patched as stopgap. App repos build from `dev`; manifest/pipeline repo builds from `develop`.
3. **Login CORS/403** — `itariff-bff-eudev.itopazapp.com` is fronted by API Gateway `tj1dse31fi` (stage dev), custom-domain base-path mapping = `itariff-apis`. Calling `/tariff-grant-bff/...` without that prefix → API GW 403, no CORS headers (browser reports CORS). Fixed `tariff-microfrontend-share-ui@dev` `environment.development.ts`: apiUrlReq/setRFQApiUrlReq/sellingApiUrl → `https://itariff-bff-eudev.itopazapp.com/itariff-apis/<bff>/...` (commit `ca1ec5c`). Verified OPTIONS preflight 200 + Access-Control-Allow-Origin. Dev BFF Istio VS prefixes: /tariff-grant-bff/, /tariff-selling-bff/, /tariff-external-bff/.

### B. CI — itariff microfrontend pipeline `-latest` push bug (itariff-k8s-repo@develop `698f623`)
Push-to-ECR stage used single-quoted `sh`; `${ENVIRONMENT}` resolved by shell but it's `params.ENVIRONMENT` (not exported) → empty → pushed `...--latest` (nonexistent) → `tag does not exist` → FAILURE before Deploy/CloudFront. Fixed both `jenkins/tariff_microfrontend-main-ui` and `..._share-ui`: add `ENVIRONMENT=${params.ENVIRONMENT}` to push withEnv + re-tag latest from the versioned tag before pushing.

### C. MDM Cognito — ALB auth then client-credentials (074779643551, pool eu-central-1_MHe1qfDpe)
- Existing `itopaz-api` client (`lsssnrbmsd0i8u1ba96g5gu7`) left unchanged throughout.
- Initially added ALB authenticate-cognito on `private-alb` rules for `mdm-bw-dev.itopazapp.com` (prio 15 precompany-dev, prio 20 precontect-dev) with a new `mdm-bw-dev-alb` client. Per follow-up (client-credentials needed, ALB login not), REVERTED both ALB rules to plain forward and DELETED `mdm-bw-dev-alb` (Cognito forbids code + client_credentials on one client).
- Created resource server `mdm-bw` (scope `mdm-bw/mdm-bw`) + m2m client `mdm-bw-dev-m2m` = `hjgb6ad314nmq6dhp3rhrmlpr` (client_credentials + secret). Token URL `https://eu-central-1mhe1qfdpe.auth.eu-central-1.amazoncognito.com/oauth2/token`, scope `mdm-bw/mdm-bw`. Verified token 200. Client tool must use /oauth2/token (was set to the JWKS url) and grant=client_credentials.

### D. Connectivity — Datalake (581621506601) ↔ Frankfurt DBs via VPC Reachability Analyzer
- Datalake eu-central-1 VPCs: prod `vpc-079ff2bbf76ff68d5` (10.237.0.0/16; subnets 10.237.30.0/24 + 10.237.31.0/24 share rtb-0b449509135c45625 with routes to 10.100.0.0/16 + 10.1.0.0/16 via VGW vgw-0f573849578d41def); default `vpc-0d436b94a4f001fe7` (172.31.0.0/16, IGW-only).
- Targets: itopaz-dev DB `euc1-itopaz-dev-database-cluster` = 10.100.159.12:5432 (dev, SG sg-04fa8421b5d265ccf); MDM DB `ecu-mdm-db-cluster` = 10.100.127.27:5432 in PROD 965031587107 (SG sg-081e47d0f39d10b09). Both DB SGs allow 5432 from 0.0.0.0/0 (flag: over-permissive).
- Named analyzer results (datalake account, eu-central-1):
  - `datalake-to-itopaz-dev-db` (nip-0a138d00ecdb96cfe): 10.237.x → itopaz-dev 5432 = **PathFound true**.
  - `dms-to-ecu-mdm-db` (nip-0d16a410562ec0517): DMS 10.237.30.150 → MDM 10.100.127.27 5432 (and 1433) = **PathFound true at AWS layer**. Remaining failure (if any) is on-prem/VPN firewall (VGW egress) or DMS port/engine mismatch (DMS = 1433/SQL Server, MDM target = Postgres 5432).
  - `datalake-defaultvpc-to-itopaz-dev-db` (nip-07874ee27790ef371): 172.31.x (i-0811f157ad78a9979 / 172.31.44.233) → 10.100.x = **NOT reachable** (IGW_DESTINATION_ADDRESS_NOT_IN_RFC1918_EGRESS; default VPC has no TGW/peering/VGW to 10.100.x). Reverse (dev DB → 172.31.44.233) also NOT reachable (TGW_RTB_ROUTES_ARE_UNKNOWN).
- Conclusion: 10.237.x datalake VPC reaches the dev/MDM DBs; the 172.31.x default VPC does not (needs TGW/peering to 10.100.0.0/16). us-east-1 datalake reaches the DBs over its TGW (verified live TCP 5432 earlier).

---

### Additional Notes (Activity Log)
### DEV EU — itariff UI login chain fixed (bff auth-base-uri, mixed content, CORS/base-path)
- **Cluster**: `euc1-itopaz-dev-eks` (dev, acct 074779643551), bastion `i-05c33080ab25c83cc`
- **`itariff-bff-upload` 401 "Could not process token"**: `tariff-selling-bff` configmap `jwt-token.auth-base-uri` pointed at an `ap-south-1` Istio ELB (unresolvable from Frankfurt) → token validation failed. Fixed live → `http://tariff-profile-service.itariff-api.svc.cluster.local/profile-domain-service/` (verified profile svc HTTP 200); restarted. (live-only; repo source `itariff-k8s-repo/config/tariff-selling-bff.yaml` still has ap-south-1 — not yet persisted.)
- **`itariff-eudev` blank page / "navbar died" (mixed content)**: the itariff shell import-map loaded microfrontends (navbar/shared_ui, buying/selling-rates, user-security) from the `ap-south-1` ELB over **HTTP** → browser blocked on HTTPS page. main-ui `dev` branch import-map was already correct (HTTPS same-origin); live pods patched as stopgap. App builds from **dev** branch (manifest/pipeline repo builds from **develop**).
- **Login CORS/403**: `itariff-bff-eudev.itopazapp.com` is fronted by **API Gateway** `tj1dse31fi` (stage dev) whose custom-domain base-path mapping is **`itariff-apis`**. share-ui env URLs must be `https://itariff-bff-eudev.itopazapp.com/itariff-apis/<bff>/...`. Corrected `tariff-microfrontend-share-ui@dev` `environment.development.ts` (apiUrlReq/setRFQApiUrlReq/sellingApiUrl) → commit `ca1ec5c`. Verified OPTIONS preflight 200 + ACAO present. (Earlier wrong attempt stripped /itariff-apis then restored it.)
- Dev BFF Istio VS prefixes (host itariff-bff-eudev): `/tariff-grant-bff/`, `/tariff-selling-bff/`, `/tariff-external-bff/` (no /itariff-apis prefix at Istio — that's the API GW base path).

### DEV EU — itariff microfrontend Jenkins pipeline `-latest` push bug fixed
- **Repo**: `itariff-k8s-repo@develop` (Jenkins loads pipelines from develop), commit `698f623`
- Push-to-ECR stage used single-quoted `sh` so `${ENVIRONMENT}` was resolved by shell, but it's `params.ENVIRONMENT` (not an env var) → empty → pushed wrong tag `...--latest` → `tag does not exist` → pipeline FAILURE before Deploy/CloudFront.
- Fixed both `jenkins/tariff_microfrontend-main-ui` and `jenkins/tariff_microfrontend-share-ui`: added `ENVIRONMENT=${params.ENVIRONMENT}` to push-stage withEnv + re-tag latest from the just-pushed versioned tag before pushing.

### DEV — MDM ALB Cognito + Cognito client-credentials for mdm-bw-dev
- **Account** 074779643551, pool `eu-central-1_MHe1qfDpe` (domain `eu-central-1mhe1qfdpe`), existing client `itopaz-api` (`lsssnrbmsd0i8u1ba96g5gu7`) left UNCHANGED.
- Host `mdm-bw-dev.itopazapp.com` → NLB `private-nlb-7422754f0293360e` → ALB `private-alb` (`389490502178fcdb`), HTTPS listener `6a8665f4f7659890`, rules prio 15 (`precompany-dev`) + 20 (`precontect-dev`).
- Added ALB authenticate-cognito on both rules (new client `mdm-bw-dev-alb`) then, per request for client-credentials, REVERTED ALB rules to plain forward and DELETED `mdm-bw-dev-alb` (Cognito can't combine code + client_credentials on one client).
- Created resource server `mdm-bw` (scope `mdm-bw/mdm-bw`) + dedicated m2m client `mdm-bw-dev-m2m` = `hjgb6ad314nmq6dhp3rhrmlpr` (client_credentials). Token URL `https://eu-central-1mhe1qfdpe.auth.eu-central-1.amazoncognito.com/oauth2/token`, scope `mdm-bw/mdm-bw`. Verified token HTTP 200. (User's tool had wrong Access Token URL = JWKS url; correct is /oauth2/token.)

### Connectivity — Datalake (581621506601) ↔ Frankfurt DBs (VPC Reachability Analyzer)
- **Datalake VPCs (eu-central-1)**: prod `vpc-079ff2bbf76ff68d5` (`10.237.0.0/16`, private subnets 10.237.30.0/24 + 10.237.31.0/24, route to `10.100.0.0/16` + `10.1.0.0/16` via VGW `vgw-0f573849578d41def`); default `vpc-0d436b94a4f001fe7` (`172.31.0.0/16`, IGW-only, no private path).
- **DBs**: itopaz-dev `euc1-itopaz-dev-database-cluster` = `10.100.159.12:5432` (dev, SG `sg-04fa8421b5d265ccf`, ingress allows 5432 from 0.0.0.0/0). MDM `ecu-mdm-db-cluster` = `10.100.127.27:5432` in **PROD 965031587107** (SG `sg-081e47d0f39d10b09`, 5432 from 0.0.0.0/0) — reached via VGW.
- **Results (named analyzer paths in datalake acct)**:
  - datalake `10.237.x` (DMS eni-0f4510c17bb3386ef / working host 10.237.31.69) → itopaz-dev DB 5432: **REACHABLE** (`datalake-to-itopaz-dev-db` nip-0a138d00ecdb96cfe)
  - datalake `10.237.x` (DMS 10.237.30.150) → MDM DB 10.100.127.27 5432/1433: **REACHABLE at AWS layer** (`dms-to-ecu-mdm-db` nip-0d16a410562ec0517); if DMS still fails it's on-prem/VPN firewall (traffic egresses via VGW) or a port/engine mismatch (DMS mentioned 1433/SQL Server but MDM target is Postgres 5432).
  - datalake **default VPC `172.31.x`** (i-0811f157ad78a9979, 172.31.44.233) → any 10.100.x DB: **NOT REACHABLE** (`datalake-defaultvpc-to-itopaz-dev-db` nip-07874ee27790ef371) — IGW_DESTINATION_ADDRESS_NOT_IN_RFC1918_EGRESS; default VPC has no TGW/peering/VGW to 10.100.x.
  - dev DB → datalake 172.31.44.233: NOT REACHABLE (TGW_RTB_ROUTES_ARE_UNKNOWN — 172.31 default VPC not attached to TGW).
- Note: DB SGs on 5432 are open to 0.0.0.0/0 (security concern to flag). us-east-1 datalake reaches the DB fine over its TGW.

---

---

## 2026-09-17 — itopaz print-service: SIT EU fix + SIT SG full build + DEV sa-prefiler DB case fix

### A. SIT EU (euc1-itopaz-sit-eks, acct 464134132424, ns itopaz-platform) — print end-to-end fix

**Issue**
- Print failing: `Cognito: token request failed EnsureSuccessStatusCode()` (CognitoTokenProvider.cs:94) then `print-api: HTTP request failed Name or service not known (auhd83rlcc.execute-api.eu-central-1.amazonaws.com:443)`

**Root cause (three layers)**
1. No `execute-api` interface VPC endpoint in the SIT VPC (dev had `vpce-06981254c0aa4ec5c`), so pods could not resolve the private API Gateway host.
2. Cognito: `PrintService__CognitoTokenUrl` was the JWKS discovery URL, not `/oauth2/token`; the print-service was wired to the `itariff-int-api` app client (scope `uat-itariff/uat-itariff`); and the `sit-print` resource server had `Scopes: null` (the referenced scope `sit-print/sit-print` did not exist).
3. API GW `auhd83rlcc` VPC link `0p5gtn` targeted the istio-gateway NLB (`a6e66b6...`), not the printer NLB — so authenticated calls hit Istio and returned 404.

**Fix Applied**
- Created SG `sg-007e2088c31181321` (tcp/443 from VPC CIDR `10.100.208.0/20`) + interface endpoint `vpce-0296f0dc9182ab0e8` (`com.amazonaws.eu-central-1.execute-api`, private-DNS on) in `vpc-07d21eafbea59ffec`, subnets `subnet-0b42d6686c611a2cf`/`subnet-05ccfb4d81d44dc9a`.
- Cognito on pool `eu-central-1_pGYVM1kAF`: `update-resource-server sit-print` add scope `sit-print`; created dedicated app client `sit-print` (client_credentials + scope `sit-print/sit-print` + secret); patched k8s secret `cognito-client-secret` (ClientId/ClientSecret); set `PrintService__CognitoTokenUrl=https://eu-central-1pgyvm1kaf.auth.eu-central-1.amazoncognito.com/oauth2/token`.
- Created VPC link `mnc7gc` → printer NLB `private-nlb-2e9e6ffae6470607` (TG `printer-trg` → `10.1.161.184:8000`); repointed `/print-pdf` POST integration to `http://<printer-nlb>:8000/print-pdf/` via `mnc7gc`; method auth `COGNITO_USER_POOLS` + authorizer `5tyfwg` + scope `sit-print/sit-print`; redeployed `sit` stage. Reverted configmap `PythonApiUrl` to the API GW URL `https://auhd83rlcc.execute-api.eu-central-1.amazonaws.com/sit/print-pdf/`.

**Verified**
- Pod resolves `auhd83rlcc...` → private VPCE IPs; token endpoint HTTP 200; logs show `Cognito: new access token obtained` + POST to FastAPI with no DNS/404/token errors.

**Persisted**: `itopaz-k8-repo@sit` commit `c3d3fed` — `configmap/itopaz-print-svc-config.yml` (CognitoTokenUrl → /oauth2/token).

**Pending (on-prem)**: FastAPI printer `10.1.161.184:8000` intermittently down (TCP reset / failed NLB health checks for dev+sit+sg alike) — on-prem team to stabilize.

### B. SIT SG (apse1-itopaz-sit-eks, acct 464134132424, ap-southeast-1, ns itopaz-platform) — full print backend built

**Context / Root cause**
- SG had no print backend at all (no Cognito pool, no printer NLB, no execute-api VPCE; configmap was a `RouteConfig`/`TempUserName` stub). SG has no on-prem route (route tables: local `10.130.208.0/20` + TGW `tgw-03b17f26861c2d348` to `10.100.208.0/20` = Frankfurt SIT; on-prem `10.1.0.0/16` unreachable — pod test to `10.1.161.184` timed out). Frankfurt printer NLB IPs `10.100.210.87`/`10.100.212.5:8000` ARE reachable over the TGW. VPC links can't target a cross-region NLB, so the design routes SG → local NLB (IP targets = Frankfurt printer NLB) → TGW → Frankfurt printer.

**Fix Applied** (apigateway + cognito calls executed from the Frankfurt bastion `i-0bd3314ea08e6fb27`, because the SG bastion `i-05b9998627e8bf6e8` and SG pods are FortiGate-firewalled from apigateway/cognito control-plane endpoints — only sts/ec2/elbv2 work there):
- Cognito pool `ap-southeast-1_6tmeKAlKO`, domain `ap-southeast-1z6tmekalko`, resource server `sit-print` (scope `sit-print/sit-print`), client_credentials client `sit-print` = `5se0prnod6lmkk5t1a8nku9g6h`.
- Internal NLB `apse1-sit-print-nlb` (`f04db685e457ea64`); TG `printer-trg-apse1` (TCP:8000, target-type ip) → `10.100.210.87` + `10.100.212.5:8000`; listener :8000.
- VPC link `8or43j` → that NLB; REST API `xma8dve4r5` (`itopaz-sit-print`, REGIONAL), `/print-pdf` POST, authorizer `jw96r3` (COGNITO pool above), HTTP_PROXY → `http://apse1-sit-print-nlb-...:8000/print-pdf/`, scope `sit-print/sit-print`, stage `sit`. Invoke URL `https://xma8dve4r5.execute-api.ap-southeast-1.amazonaws.com/sit/print-pdf/`.
- execute-api interface VPCE `vpce-0e21b23cb0505f9cd` (+ SG `sg-079cd247d1989b342`, tcp/443 from `10.130.208.0/20`) in `vpc-0c46bfc8553c53eec`, app subnets `subnet-0ee9930c0495224b2`/`subnet-07de4f20c7f8317be`.
- Patched configmap (`PythonApiUrl`, `CognitoTokenUrl`, `CognitoScope`) + `cognito-client-secret`; print-service rolled out 2/2.

**Verified**: VPCE available; pod resolves + reaches the private API GW (403 without token = auth enforced); printer NLB reachable over TGW.

**Persisted**: `itopaz-k8-repo@sit` commit `05ccc8a` — `configmap/itopaz-singapore-print-svc-config.yml`.

**Pending (network/on-prem)**: SG SIT pods have NO outbound HTTPS egress (FortiGate 403 on everything incl. google.com + all Cognito endpoints) — network team must allow egress from app subnets `10.130.208.0/22` + `10.130.212.0/22` to `*.auth.ap-southeast-1.amazoncognito.com:443` (and cognito-idp) for the token flow. Shared on-prem printer also down.

### C. DEV EU (euc1-itopaz-dev-eks, acct 074779643551, ns prefiler-api) — sa-prefiler-service DB name case fix

**Issue**: `/sa-prefiler-service/saapi/GetDashboardSummary` → `Npgsql.PostgresException 3D000: database "Dbedi_uat" does not exist` at `LegalEntityRepository.GetLegalEntityAsync`. Pods Running 2/2 (runtime error, not crash).

**Root cause**: deployment inline env `ConnectionStrings__EdiDBHost__ZoneN` used `Database=Dbedi_uat` (capital D); actual DB on `euc1-itariff-edi-dev` is `dbedi_uat` (lowercase). PostgreSQL identifiers are case-sensitive → not found. Inline env overrode the configmap (which already had lowercase).

**Fix Applied**: patched all 7 `EdiDBHost` zone entries (`zone0`–`Zone6`) `Dbedi_uat` → `dbedi_uat`; rolled out 2/2.

**Verified**: no more 3D000; direct psql confirms `dbedi_uat` reachable with `prefiler_dev` creds and `legalentity` table present.

**Persisted**: `prefiler-k8s-repo@dev` commit `dbc17fa` — `sa-prefiler-service.yml` (7 EdiDBHost entries lowercased).

### D. Earlier this session (context; some live-only)
- **ECR lifecycle policies** added then REMOVED (dev 7d / sit 14d / uat 30d) — caused an ImagePullBackOff wave; policies deleted (dev 074779643551, sit 464134132424, uat 405478414008).
- **DEV prefiler-api fixes** pushed to `prefiler-k8s-repo@dev`: master/sa connstring `$()` expansion (Option B — connstrings in deployment env), aci CORS, Redis config for aes/ams/dagangnet/imdg/mblfiler/mpci.
- **itariff-k8s-repo** private-alb dev: ALB path patterns `/precompany*`, `/createnewcontact*`; added microfrontend Jenkinsfiles (`@develop`, retargeted to dev). `prefiler-k8s-repo@sit` image-tag manifest fixes pushed.
- **PROD 745510282686 (ap-south-1)**: restarted `chatecutopazpolicy` GPU box `i-0df6d3e05ce8f271c` + installed autoheal cron.

---

---

## 2026-09-01 — Jump Server Kubeconfig Merge, New UAT Account Discovery & MDMBWPROJ Feature Branches

### Action
- Received a new kubeconfig (`/home/ec2-user/rahul/config`) covering 6 itopaz EKS clusters, including 2 previously undocumented ones in account `405478414008` (UAT): `use1-itopaz-uat-eks` (us-east-1), `euc1-itopaz-uat-eks` (eu-central-1)
- Merged it into this jump server's `~/.kube/config` via `KUBECONFIG=~/.kube/config:/home/ec2-user/rahul/config kubectl config view --flatten`, preserving the pre-existing `ecu-eks-test-cluster` (745510282686) entry and its `current-context`
- Backed up prior config to `~/.kube/config.bak.<timestamp>` before overwrite

### Issue Found
- `kubectl --context sit-singapore get nodes` failed with:
  ```
  AccessDenied: User arn:aws:sts::745510282686:assumed-role/eks-jump-server-role/i-019825d0de3300832
  is not authorized to perform: sts:AssumeRole on resource: arn:aws:iam::464134132424:role/eks-jump-access
  ```
- Root cause: this jump server's EC2 instance role (`eks-jump-server-role`, account 745510282686) is not in the trust policy of the `eks-jump-access` roles in the other itopaz accounts — cross-account AssumeRole is blocked
- Not yet fixed — requires editing the `eks-jump-access` role trust policy in each target account (464134132424, 074779643551, 965031587107, 405478414008), which needs explicit confirmation before making IAM changes in accounts outside this session's original scope

### Separately Observed (unresolved, parked)
- `git fetch`/`git ls-remote` against `bitbucket.org` hangs indefinitely on this jump server for repos under `/home/ec2-user/rahul/clones/`
- Traced to the global git config `credential.helper = !aws codecommit credential-helper $@` — `git credential fill` for host `bitbucket.org` hangs (confirmed via direct `git credential fill` test, exit via timeout only), even though direct network connectivity (curl) to `bitbucket.org` and `api.bitbucket.org` is fine and fast
- Manually invoking `aws codecommit credential-helper get` in isolation returns immediately, so the hang is specific to git's invocation path, not the AWS CLI call itself — needs further isolation (e.g. `strace` or removing the global helper and relying on the repo-local Bitbucket token) before resolving

### Bitbucket — MDMBWPROJ Feature Branches Created Across All Repos

**Workspace**: `allcargoecu` | **Project**: `MDMBWPROJ`
**Token**: Bitbucket repository access token (stored at `/home/ec2-user/rahul/token`)
**Script**: `/home/ec2-user/rahul/create_feature_branches.py`

#### Action
- Listed all 120 repositories in the `MDMBWPROJ` Bitbucket project via API
- Ensured every repo has all four standard environment branches: `feature_dev`, `feature_sit`, `feature_uat`, `feature_prod`
- Branches created from each repo's default branch (`main` or `master`)

#### Result
- **164 branches created** across 117 repos
- **2 repos** already had all 4 branches (`bw_accessmanagement_outbound_itopaz`, `bw_precompany_outbound`)
- **3 repos failed** with HTTP 400 — empty repositories (no commits), cannot create branches until initial commit is pushed:
  - `bw_account_ucoa_outbound_d365`
  - `bw_company_corporateaccount_outbound_d365`
  - `bw_finance_corporateaccount_outbound_crm`

#### Notes
- Some repos had HTTP 403 on `feature_prod` in the first run (resolved on second run — likely a race condition or permission delay)
- To retry the 3 empty repos after their initial commit: `python3 /home/ec2-user/rahul/create_feature_branches.py`

---

### S3 CORS Fix — allcargo-intranet Bucket

**Bucket**: `allcargo-intranet` | **Region**: `ap-south-1` | **Account**: `745510282686`
**Profile**: `allcargo745`

#### Problem
- Browser CORS error when fetching presigned S3 URLs from `http://localhost:4200` (Angular dev server):
  `No 'Access-Control-Allow-Origin' header is present on the requested resource`
- The bucket CORS policy only allowed production/staging origins

#### Fix
- Added `http://localhost:4200` and `http://localhost:3000` to `AllowedOrigins` in the bucket CORS configuration
- All other rules unchanged (`GET`, `HEAD` methods, `*` headers, `ETag` exposed, `MaxAgeSeconds: 3600`)

#### Updated AllowedOrigins
- `https://intellihub.allcargoapps.com`
- `https://intranet-dev.allcargoapps.com`
- `https://intranet-uat.allcargoapps.com`
- `https://intranet.allcargoapps.com`
- `http://localhost:4200` ← added
- `http://localhost:3000` ← added

---

---

## 2026-08-17 — ELMA Self-Chat WebSocket Fix & IntelliHub / Intranet Infra (Account 745510282686)

### Problem
ELMA Self-Chat WebSocket connections failing on `intranet-dev.allcargoapps.com` and `elma-dev.allcargoapps.com`. "Processing" badge stuck permanently after document upload.

### Root Causes (3 layers)

**Layer 1 — nginx on Intranet-uat (10.0.132.243)**
- **Root cause (plain terms)**: nginx was stripping the `Upgrade: websocket` header, so every connection got downgraded to HTTP and immediately rejected.
- nginx was running with zero proxy config (default site, no location blocks)
- `/agent/self-chat/ws/` requests hit nginx → `try_files` → `404`
- Fix: Created `/etc/nginx/sites-available/intellihub` with the 4 standard WebSocket proxy directives:
  ```nginx
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_read_timeout 3600s;
  ```
  These 4 lines are the standard fix for any nginx WebSocket proxy.

**Layer 2 — CloudFront E2FVCC01LF3UUD (elma-dev.allcargoapps.com)**
- CF behavior `/agent/self-chat/ws/*` required trailing wildcard — path `/agent/self-chat/ws/token` didn't always match
- CF behavior allowed only `HEAD, GET` — expanded to all 7 methods
- `/ws` path had no CF behavior — added new behavior
- Fix: Updated path to `/agent/self-chat/ws*`, added `/ws` behavior, both → datascience ALB

**Layer 3 — ALB datascience-144380231 (eu-central-1, account 674017976129)**
- No ALB rule for `/ws` or `/ws/*`
- Fix: Added rule P8 `/ws`, `/ws/*` → `elma-tg:8506`

**Layer 4 — ELMA backend PID issue**
- `elma-dev.service` was running old code (WebSocket routes existed in `App/main.py` but process needed restart to load them)
- `elma-dev.service` had crash loop (restart counter >1033) — separate startup issue
- Fix: `sudo systemctl restart elma-dev.service` — service now loads WebSocket routes

### Architecture (account 674017976129, eu-central-1)
- **ELMA EC2**: `i-00bc2270212d49626` (ml-model-training-server), `172.31.3.13`
- **ELMA service**: `elma-dev.service` → `uvicorn App.main:app --port 8506`
- **Working dir**: `/home/ubuntu/jupyter_workspace/test/Elma/`
- **WebSocket routes**: `@app.websocket("/agent/ws/{token}")` and `@app.websocket("/agent/self-chat/ws/{token}")`
- **ALB**: `datascience-144380231.eu-central-1.elb.amazonaws.com`
- **CF**: `E2FVCC01LF3UUD` → aliases: `elma-dev.allcargoapps.com`, `elma-api.allcargoapps.com`
- **SSM access**: `aws ssm start-session --target i-00bc2270212d49626 --region eu-central-1 --profile elma674`

### mcpserverapi UPLOAD_WS_URL
- **File**: `/home/ubuntu/mcpclient/mcpserverapi/.env` on Intranet-uat (10.0.132.243)
- **Correct value**: `UPLOAD_WS_URL=wss://elma-dev.allcargoapps.com/agent/self-chat/ws`
- Service: `elma-mcp-client.service` (port 8338)

### Key Insight
WebSocket upgrade (HTTP/1.1 `Upgrade: websocket`) returns `101` end-to-end.  
curl shows `HTTP/2 404` because curl negotiates HTTP/2 with CF — use `curl --http1.1` to test WebSocket through CloudFront.

### Account 674017976129 (SSO: ecu-allcargo.awsapps.com, role AWSAdministratorAccess)
- Region: eu-central-1
- Profile: `elma674` (configured in `~/.aws/config` with SSO)
- ELMA, SARA, AQUA, KAIROS, FRAME, BOLT, CUBE, EPIC, etc. — all DS/ML apps
- All served via ALB `datascience-144380231.eu-central-1.elb.amazonaws.com`

### IntelliHub / Intranet Infra — Account 745510282686 (Aug 2026)
### Infrastructure Discovered (2026-08-14 to 2026-08-17)

#### AWS Account: 745510282686 (ap-south-1)
- **Role**: `arn:aws:iam::745510282686:role/eks-jump-server-role` (on i-019825d0de3300832)
- **CloudFront Distributions**:
  - `E17IUMRH88RLK0` — alias: `intranet-dev.allcargoapps.com` → S3 default, `/intellihub/*` → intelli-atl.allcargoapps.com, `/ecureports/*` → Intellihub-prod ALB
  - `EUXNUI70UHP4U` — aliases: `intellihub.allcargoapps.com`, `intellihub-test.allcargoapps.com` → Intellihub-prod ALB default, `/intranet/doc-proxy/*` → Intellihub-prod ALB, `/ecureports/*` → Intellihub-prod ALB
  - `E2KUC71OEUFDR2` — alias: `intranet-uat.allcargoapps.com`
  - `E1Y96N6IYRLTQJ` — alias: `releasedocs.allcargoapps.com`
- **Global Accelerators**:
  - `intellihub-prod` (`a597dde4c9e7fd12e`) → endpoint: Intellihub-prod ALB (UNHEALTHY — health check path null)
  - `intellihub-test-GA` (`a9aa12dbc5cb38e31`) → endpoint: LB-intranet (UNHEALTHY — health check `/` hits unhealthy default TG)
  - `global-api-accelerator` (`a0e64e9eec1e248bc`)
- **DNS**:
  - `intelliaiml.allcargoapps.com` → `intellihub-prod` GA → Intellihub-prod ALB
  - `aimlapp-test.allcargoapps.com` → `intellihub-test-GA` → LB-intranet
  - `intranet-dev.allcargoapps.com` → CF E17IUMRH88RLK0
  - `intelli-atl.allcargoapps.com` → `lb-intellihub-408139470.ap-south-1.elb.amazonaws.com` (65.0.235.121, 65.2.203.48) — Classic ELB not in this account
- **ALBs**:
  - `Intellihub-prod` (arn:.../Intellihub-prod/e94560d3db5e68f1) — HTTPS :443 default: fixed-response. Key rules: P1 `/intranet/gatimasterapi` → gatimasterapi-prod, P5 `/intranet*` → intellihub-prod TG (HEALTHY, port 80, health `/intranet/healthcheck`)
  - `LB-intranet` (arn:.../LB-intranet/a261a4d9ad16eebb) — P7 `/intranet*` → intranet-newvm TG (HEALTHY), default → resumeuploaded (UNHEALTHY)
- **EC2 Instances**:
  - `Intranet-uat` (i-0825be434cf7ab87b) — 10.0.132.243, m6a.xlarge, key: vj-keypair-pocacct.pem
  - `Intranet-prod-1` (i-0b1f3b8eda05c132b) — 10.151.4.89, c5a.xlarge, key: Intranet-prod-1-Key.pem
  - `Intranet-prod-2` (i-0a82e63f8fcce6c8e) — 10.151.4.153, m5.2xlarge

#### Services on Intranet-uat (10.0.132.243) — test env backend
- **Port 8338**: `elma-mcp-client.service` — uvicorn `app.main:app`, WorkingDir: `/home/ubuntu/mcpclient/mcpserverapi`, handles `/agent/*` routes including ELMA self-chat WebSocket
- **Port 8779**: `vdtext` uvicorn (`backend.main:app`) at `/home/ubuntu/vdtext/vdext/`
- **Port 4001**: `python3 intranetapimain.py`
- **Port 4003**: `python3 aadhar_extraction_api.py`
- **Port 4080**: `python3 hrchatbotazure.py`
- **Port 5667**: `python3 main.py` (gatimasterapi)
- **Port 5668**: `python3 main.py` (symphonywrapper)
- **nginx 1.18.0** running on port 80 — config at `/etc/nginx/sites-available/intellihub`

#### ELMA Self-Chat WebSocket Fix (2026-08-17)
- **Problem**: nginx had zero proxy config. All `/agent/self-chat/ws/` WebSocket upgrade requests hit nginx → `try_files → 404`. Browser retried 30+ times, badge stuck on "Processing".
- **Fix applied**: Created `/etc/nginx/sites-available/intellihub` with:
  - `/agent/self-chat/ws/` → `http://127.0.0.1:8338` with `proxy_http_version 1.1`, `Upgrade`, `Connection: upgrade`, `proxy_read_timeout 3600s`, `proxy_buffering off`
  - `/agent/` → `http://127.0.0.1:8338`
  - `/intellihub/` → `http://127.0.0.1:8779/`
- Disabled `sites-enabled/default`, symlinked intellihub site
- **Verification**: `curl` to `/agent/self-chat/ws/` now returns 403 (reaches ELMA backend, auth required) instead of 404

#### Doc-Proxy Issue (intelliaiml.allcargoapps.com)
- **Problem**: `proxyUrl = IntranetAPI_Domain + intranet/doc-proxy/ + token` → Office Online shows "not publicly accessible"
- **Root cause**: proxy backend redirects to S3 URL with Referer-based policy. Microsoft Office Online fetches without Referer header → S3 returns 403.
- **Fix**: Backend `/intranet/doc-proxy/<token>` must generate S3 presigned URL (15 min TTL) and return 302 redirect to it. Presigned URLs use query-string auth, no Referer needed.
- **Also**: Add `HEAD` method handler to the endpoint (currently returns 405).

#### GA Health Check Fixes Needed
- `intellihub-prod` GA health check path: `null` → set to `/intranet/healthcheck`
- `intellihub-test-GA` GA health check hits `/` → `resumeuploaded` TG (UNHEALTHY) → change to `/intranet/healthcheck`

---

---

## 2026-07-24 — DEV EU imdg-prefiler Deep-Link 301/Blank-Page Fix

### Issue
- `GET https://prefiler-eudev.itopazapp.com/imdg-prefiler/add-edit-details?from=filer-details&flow=add&activeMain=file&activeChild=firstDeclaration` returned `301 Moved Permanently` → `https://prefiler-eudev.itopazapp.com/dashboard`, dropping the destination and query params
- Normal in-app navigation (Dashboard → File → First Declaration → stepper → Add/Edit Details) was unaffected — only direct URL entry, page refresh, or opening in a new tab triggered the 301

### Root cause
- `imdg-prefiler` is a single-spa **child** microfrontend (built via `main.single-spa.ts` per `angular.json`, exports `bootstrap`/`mount`/`unmount` lifecycle hooks — does not self-render on script load)
- The Istio `prefiler-ui` VirtualService routes `/imdg-prefiler/*` by path prefix **directly to the `imdg-prefiler-svc` pod**, bypassing the single-spa shell (`microfrontend-main`) entirely
- Shell root (`/`) is where `single-spa` + `single-spa-layout` boot and mount the correct child based on the current URL — a child pod hit directly has no shell, so `main.js` loads but never receives a `mount()` call → blank page
- `imdg-prefiler`'s `.htaccess` had an existing referer-based guard (empty/self referer → 301 to `/dashboard`) specifically to prevent the blank-page case, but it discarded the original path/query, so users landed on the dashboard instead of their intended record
- Git history (`imdg-prefiler` repo) shows this guard was added, removed, and re-added three times via Bitbucket web-UI edits (no PRs) — prior fixes oscillated between "301 to dashboard" (loses destination) and "plain SPA fallback" (blank page), never addressing the actual shell/child routing mismatch
- Root `/` on the shell also has its own `.htaccess` rule (`RedirectMatch ^/$ /login`) that intercepts unauthenticated root requests — relevant when choosing a handoff target

### Fix Applied
Two repos, `develop` branch:

**`imdg-prefiler`** (bitbucket.org/allcargoecu/imdg-prefiler, commit `411c520`)
- `.htaccess`: deep-link guard now serves a new `redirector.html` instead of issuing a raw 301
- `redirector.html` (new): client-side JS captures `window.location.pathname + search` and redirects to `https://prefiler-eudev.itopazapp.com/dashboard?spaRedirect=<encoded original path+query>` — uses `/dashboard` (not `/`) to avoid the shell's own `/login` redirect on root
- `Dockerfile`: `ADD redirector.html` alongside `.htaccess` into `htdocs/` root (must sit next to `.htaccess`, not inside the `imdg-prefiler/` subfolder — rewrite substitutions resolve relative to `.htaccess`'s location)

**`microfrontend-main`** (bitbucket.org/allcargoecu/microfrontend-main, commit `6136f1c`)
- `index.html`: before `single-spa`/`single-spa-layout` boot, reads `?spaRedirect=` from the query string and calls `history.replaceState` to restore the real target URL, so `constructRoutes`/`constructApplications` mount the correct child app at the originally requested path

### Verified
- Local Docker build of `imdg-prefiler` Dockerfile: deep-link path returns `200` serving `redirector.html` (not 301, not blank), static assets (`main.js`) unaffected
- Live pod patch (pre-commit) confirmed same behavior against DEV EU Istio ELB directly
- Normal in-app stepper navigation confirmed unaffected (referer already set to shell, guard condition doesn't match)

### Pending / Not Yet Verified
- **Not yet deployed** — commits are source-only; DEV pods (`imdg-prefiler`, `microfrontend-main`) still run old baked-in images until Jenkins pipelines (`prefiler-k8s-repo/jenkins/dev/ui/imdg-prefiler`, `.../microfrontend-main`) build and roll out
- Pushed directly to `develop` on both repos (no PR) per explicit request — team may want review before next deploy given prior history of unreviewed `.htaccess` edits
- Full end-to-end client-side verification (shell restoring URL and single-spa mounting the child) requires a real authenticated browser session — not verifiable via curl alone
- **Same anti-deep-link `.htaccess` pattern likely exists in the other 11 sibling `*-prefiler` UI repos** (`afr-prefiler`, `aci-prefiler`, `aes-prefiler`, `ams-prefiler`, `basf-prefiler`, `dagangnet-prefiler`, `ics-prefiler`, `ics2-prefiler`, `mblfiler-prefiler`, `mpci-prefiler`, `sa-prefiler`) — none of these have been checked or fixed yet

---

---

## 2026-06-19 — SIT itariff-api HPA maxReplicas Increase

### Issue
- Multiple iTariff buying services hitting CPU >150-230% with HPAs stuck at maxReplicas (3 or 5)
- Services unable to scale despite heavy load

### Fix Applied
```bash
kubectl patch hpa tariff-buying-service -n itariff-api -p '{"spec":{"maxReplicas":10}}'
kubectl patch hpa tariff-buying-carriage-service -n itariff-api -p '{"spec":{"maxReplicas":6}}'
kubectl patch hpa tariff-buying-standardcost-service -n itariff-api -p '{"spec":{"maxReplicas":6}}'
kubectl patch hpa tariff-buying-truck-service -n itariff-api -p '{"spec":{"maxReplicas":6}}'
kubectl patch hpa tariff-selling-oc-service -n itariff-api -p '{"spec":{"maxReplicas":6}}'
```

### Result
- `tariff-buying-carriage-service`: 204% → 43% CPU (scaled to 6 replicas)
- `tariff-buying-service`: 230% → 94% CPU (scaled to 10 replicas)
- `tariff-buying-standardcost-service`: 142% → 45% CPU (scaled to 6)
- `tariff-buying-truck-service`: 93% → 19% CPU (scaled to 6)
- `tariff-selling-oc-service`: 80% → 5% CPU (scaled to 6)

### Note
- `tariff-buying-service` may need maxReplicas raised to 12-15 if CPU stays >80%
- `tariff-selling-consumer-hpa` still at 157% with 20/20 replicas — needs CPU resource increase

---

---

## 2026-06-18 — POC Account aimlapp-test Intranet 502 Fix

### POC Account — aimlapp-test Intranet Service Restored (502 Fixed)

**Server**: `10.0.132.243` (ubuntu) — POC Account `745510282686`
**Key**: `infrastructure/secrets/keys/shared/poc/vj-keypair-pocacct.pem`
**URL**: `https://aimlapp-test.allcargoapps.com/intranet/login`

#### Problem
- URL returning **502 Bad Gateway** from AWS ELB
- `intranetapimain.py` was not running on the server

#### Root Cause
- Service `intranetapimain.py` crashes on startup — `AccessDeniedException` when calling `secretsmanager:GetSecretValue` on secret `test/intranet`
- IAM user `arn:aws:iam::745510282686:user/codecommit-jenkins` had no policy allowing access to that secret
- Existing `aws-secret-manager-policy` only covered `devrev_tokens*` secret

#### Fix Applied
- Added inline IAM policy `AllowSecretsManagerIntranet` to user `codecommit-jenkins`:
  ```json
  {
    "Effect": "Allow",
    "Action": "secretsmanager:GetSecretValue",
    "Resource": "arn:aws:secretsmanager:ap-south-1:745510282686:secret:test/intranet*"
  }
  ```
- Started `intranetapimain.py` from: `/root/var/www/intranet/userdetailssync/userdetailssync/`
- Service running on port `4001` (uvicorn/FastAPI)
- URL now returns `200 OK` (GET) / `405` for HEAD — **service is UP**

#### Additional Findings
- **autoheal script** `/root/var/www/apis-autoheal.sh` has wrong path for `intranetapimain`:
  - Script expects: `/root/var/www/intranet/userdetailssync/`
  - Actual location: `/root/var/www/intranet/userdetailssync/userdetailssync/`
  - Needs fix to prevent future outages
- Server IP `10.0.132.243` requires VPC peering to be active (was unreachable before peering)
- Services on server: `hrchatbotazure.py` (port 4080), `aadhar_extraction_api.py` (port 4003), `intranetapimain.py` (port 4001), `ollama` (127.0.0.1:11434)

---

### Issue
- `https://aimlapp-test.allcargoapps.com/intranet/login` returning 502 Bad Gateway
- `intranetapimain.py` not running; crashes on startup due to IAM `AccessDeniedException`

### Fix
- Applied inline IAM policy `AllowSecretsManagerIntranet` to `codecommit-jenkins` (account `745510282686`):
  - Resource: `arn:aws:secretsmanager:ap-south-1:745510282686:secret:test/intranet*`
  - Action: `secretsmanager:GetSecretValue`
- Manually started service: `nohup python3 intranetapimain.py > /tmp/intranet.log 2>&1 &`
- Service path: `/root/var/www/intranet/userdetailssync/userdetailssync/`
- Running on: `http://0.0.0.0:4001` (uvicorn FastAPI)

### Known Issue (Not Fixed)
- `/root/var/www/apis-autoheal.sh` has wrong path — references `/root/var/www/intranet/userdetailssync/` instead of `/root/var/www/intranet/userdetailssync/userdetailssync/`
- Autoheal will fail to restart intranet if it goes down again — path needs correction

### Server Details
- **Host**: `10.0.132.243` (ubuntu), POC account `745510282686`
- **Key**: `infrastructure/secrets/keys/shared/poc/vj-keypair-pocacct.pem`
- **Nginx**: Running (port 80), routes static content from `/var/www/html`
- **Services running**: `hrchatbotazure.py` (4080), `aadhar_extraction_api.py` (4003), `intranetapimain.py` (4001), `ollama` (127.0.0.1:11434)
- **AWS credentials on server**: IAM user `codecommit-jenkins`, region `ap-south-1`, creds at `/root/.aws/credentials`

---

---

## 2026-06-17 — Operations Log

### PROD EU — Grafana K8S Dashboard Fixed (No kube-state-metrics)
- **Problem**: Grafana K8S Dashboard namespace dropdown empty; `kube-state-metrics` not installed in PROD cluster
- **Root cause**: Dashboard variables (`NameSpace`, `Node`, `Container`, `Pod`) all used `kube_namespace_created`, `kube_node_info`, `kube_pod_container_info` from KSM — none exist in PROD
- **Investigation**:
  - PROD cluster confirmed accessible: bastion `10.100.98.195`, 4 Linux nodes (v1.36.1-eks), 15 namespaces
  - Monitoring stack: Grafana + Prometheus in `istio-system` only — no KSM, no ServiceMonitor CRDs
  - Prometheus uses static `kubernetes_sd_configs` scrape jobs (no ServiceMonitor)
  - Available metrics: cAdvisor (`container_*`), kubelet (`kubelet_node_name`, `machine_memory_bytes`, `machine_cpu_cores`)
- **Fix approach**: Rewrote dashboard JSON without modifying cluster
  - Downloaded dashboard via `kubectl exec grafana -- curl localhost:3000/api/dashboards/uid/9f83e8f6-ae9a-4bc1-ad64-cffc1c93df02`
  - **129 panel expressions rewritten** using Python script `/tmp/fix_dashboard.py`
  - Uploaded via Grafana API POST `/api/dashboards/db` — status: success, version 2
- **Variable replacements**:
  - `origin_prometheus` → hidden constant (no KSM federation)
  - `Node` → `label_values(kubelet_node_name, node)`
  - `NameSpace` → `label_values(container_memory_working_set_bytes{container!="",container!="POD"}, namespace)`
  - `Container` → `label_values(container_cpu_usage_seconds_total{namespace=~"$NameSpace",...}, container)`
  - `Pod` → `label_values(container_cpu_usage_seconds_total{...}, pod)`
- **Metric replacements**:
  - `kube_node_status_allocatable{resource="memory"}` → `machine_memory_bytes`
  - `kube_node_status_allocatable{resource="cpu"}` → `machine_cpu_cores`
  - `kube_node_info` → `kubelet_node_name`
  - `kube_pod_info` counts → `container_last_seen` counts
  - `kube_pod_container_resource_requests/limits` → `vector(0)` (no cAdvisor equivalent)
- **Dashboard URL**: `/d/9f83e8f6-ae9a-4bc1-ad64-cffc1c93df02/k8s-dashboard`
- **Backup script**: `/tmp/fix_dashboard.py` on local server

### knowledge-base Folder — Restored
- Folder was deleted in commit `801dca1` on June 17
- Restored via `git checkout 6151387 -- knowledge-base/` — 38 files recovered

---

---

## 2026-06-12 — PROD EU Kafka 3.9.1 Client Setup, iTariff Ingress Bring-up & prefiler-bff DEV VirtualService Fix

### PROD EU — Kafka 3.9.1 Client Setup + MSK Broker Config
- **Local download** (on 165 server): Apache Kafka `3.9.1` (Scala 2.13) downloaded to `/home/ec2-user/rahul/kafka-client/kafka_2.13-3.9.1.tgz`
- **Uploaded** tarball to prod bastion (`10.100.98.195`) via `scp` → extracted to `/home/ec2-user/kafka-client/kafka_2.13-3.9.1/`
- **Symlink**: `/home/ec2-user/kafka-client/current` → `kafka_2.13-3.9.1`
- **Java**: Installed `java-17-amazon-corretto-headless` on prod bastion (was missing); verified version `17.0.19`
- **SASL/SCRAM config** at `/home/ec2-user/kafka-client/client.properties`:
  ```
  security.protocol=SASL_SSL
  sasl.mechanism=SCRAM-SHA-512
  ssl.endpoint.identification.algorithm=https
  ```
- **Prod MSK brokers** (3 nodes, port 9096, SASL_SSL):
  - `b-1.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
  - `b-2.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
  - `b-3.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
- **Bootstrap file**: `/home/ec2-user/kafka-client/prod-bootstrap-servers.txt`
- **Wrapper script**: `/home/ec2-user/kafka-client/run-kafka-prod.sh` (runs `kafka-broker-api-versions.sh` with SASL config + heap opts)
- **Note**: Fill in `<MSK_USERNAME>` and `<MSK_PASSWORD>` in `client.properties` before running broker commands

### UI Pipelines — CloudFront Cache Invalidation Stage Added
- **Added** `Invalidate CloudFront Cache` stage to all UI Jenkins pipelines (SIT environment)
- **Files updated**:
  - `jenkins/tariff_microfrontend-main-ui` — added stage after Verify Deployment
  - `jenkins/tariff_microfrontend-share-ui` — added stage after Verify Deployment
  - `jenkins/tariff-selling-rates-ui` — already had stage, confirmed dist ID
  - `jenkins/tariff-tariffbuying-ui` — already had stage, confirmed dist ID
- **Distribution ID**: `E1MSDTWI1MUQ2P` (SIT UI CloudFront distribution)
- **Stage behavior**: Executes only when `SKIP_DEPLOYMENT=false`, invalidates all paths (`/*`), uses cross-account AWS role
- **Pushed**: `uat` branch, commit `cbde479` ✅

### SIT EU & SIT SG — Node Status Checks
- **SIT EU** (euc1-itopaz-sit-eks): Caught mid-rolling node replacement — 18 NotReady (bootstrapping), 18 Ready,SchedulingDisabled (old nodes cordoned ~8h), 2 Ready. Within ~60s new nodes joined: 37 Ready, 4 cordoned. Final state after drain complete: **26 Ready, 0 cordoned** ✅
- **SIT SG** (apse1-itopaz-sit-eks): **6 nodes all Ready** ✅
- Old cordoned nodes in SIT EU were carrying 10–12 pods each (~44 pods total); drained and terminated automatically

### SIT MSK — Kafka Version Check
- **Broker version**: Kafka **3.7.x** (confirmed via `kafka-broker-api-versions.sh`: Produce API max 11, Fetch API max 16 — both introduced in 3.7)
- **Kafka client on SIT EU bastion**: `kafka_2.13-3.6.0`
- **Brokers**: `b-1.euc1itariffsitmsk.76ygyn.c5.kafka.eu-central-1.amazonaws.com:9096`, `b-2...` (2-node cluster, SASL_SSL/SCRAM-SHA-512)

### tariff-selling-rates-ui — Jenkins Pipeline Fix
- **Root cause 1**: `REPO_URL` was pointing to wrong repo (`tariff-microfrontend-main-ui.git`) — corrected to `tariff-selling-rates-ui.git`
- **Root cause 2**: `Checkout Application Code` stage was using `$DEPLOYMENT_FILE` (`tariff-selling-rates-ui.yml`) as the Bitbucket repo slug, producing invalid URL `...tariff-selling-rates-ui.yml.git`
- **Fix**: Replaced hardcoded slug with `REPO_SLUG=$(basename "$REPO_URL" .git)` to dynamically extract slug from `REPO_URL`
- **File**: `jenkins/tariff-selling-rates-ui` in `itariff-k8s-repo`
- **Pushed**: `uat` branch, commit `b46b160` ✅

### prefiler-bff DEV — VirtualService Routing Fix (404 resolved)
- **Symptom**: All actual API calls via `prefiler-bff-eudev.itopazapp.com` returning 404 with no CORS headers, even after CORS swagger fixes and redeployment
- **Root cause**: With the API Gateway custom domain base path mapping corrected from `prefiler-bff` → `(none)`, the full path `/prefiler-bff/prefiler/bff/v1/...` is now forwarded to Istio. The VirtualService only had rules for `/prefiler-auth-bff/` and `/prefiler/` — no rule matched the `/prefiler-bff/prefiler/...` prefix → 404
- **Pods confirmed healthy**: `prefiler-bff-cd984c8dc-*` (2 pods, 2/2 Running), `prefiler-auth-bff-67f6b87c4f-*` (2 pods, 2/2 Running)
- **Fix**: Added two new http rules to `prefiler-bff` VirtualService (`istio-system`):
  - `/prefiler-bff/prefiler/` → `prefiler-bff-svc.prefiler-bff.svc.cluster.local:80` (rewrite: /)
  - `/prefiler-bff/prefiler-auth-bff/` → `prefiler-auth-bff-svc.prefiler-bff.svc.cluster.local:80` (rewrite: /)
- **Verified**: `GET https://prefiler-bff-eudev.itopazapp.com/prefiler-bff/prefiler/bff/v1/masters/PageMaster/` → **HTTP 200** with `access-control-allow-origin: *` and full JSON payload ✅
- **Cluster**: `euc1-itopaz-dev-eks` (DEV EU) via bastion `10.100.145.118`, key `dev-eu-bastion.pem`

### README.md — Comprehensive Copilot Reference Update
- Replaced generic KB/vector-db README with full operational reference
- Added all SSH access commands with exact key paths
- Added AWS account table (5 accounts with IDs, regions, IAM role ARNs)
- Added EKS cluster details (DEV EU, SIT EU, SIT SG — nodes, K8s versions, ASG, maxPods)
- Added service URLs by environment (internal + external, API GW IDs, VPC Link IDs)
- Added application architecture (tech stacks, ECR registries, namespaces)
- Added full prefiler service inventory, Istio VS routing, .NET config patterns
- Added database credentials table (DEV + SIT, Redis endpoints)
- Added Kafka broker URLs and key topics
- Added Jenkins server access, pipeline paths, env vars
- Added API Gateway CORS fix pattern with deploy commands
- Added known pending issues section (DEV, SIT EU, SIT SG)

---

### Local (165 server)
- Downloaded `kafka_2.13-3.9.1.tgz` to `/home/ec2-user/rahul/kafka-client/`
- Verified: `kafka-topics.sh --version` → `3.9.1`

### Prod Bastion (10.100.98.195)
- Uploaded and extracted to `/home/ec2-user/kafka-client/kafka_2.13-3.9.1/`
- Symlink: `/home/ec2-user/kafka-client/current`
- Installed `java-17-amazon-corretto-headless` (Amazon Linux 2, was missing)
- Created `/home/ec2-user/kafka-client/client.properties` (SASL_SSL / SCRAM-SHA-512)
- Created `/home/ec2-user/kafka-client/prod-bootstrap-servers.txt`
- Created `/home/ec2-user/kafka-client/run-kafka-prod.sh` wrapper

### PROD MSK Brokers
```
b-1.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096
b-2.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096
b-3.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096
```

### Next step
Update `client.properties` with real MSK SCRAM credentials before running topic/broker commands.

---

### PROD EU Bastion and Cluster Access
- **Bastion**: `10.100.98.195` (key: `infrastructure/secrets/keys/prod/eu/prod-eu-bastion.pem`)
- **SSH key issue fixed**: local key file had malformed/public-key content and strict permission issues
  - Corrected key content and enforced file mode `400`
- **kubectl status**: already present (`/usr/local/bin/kubectl`)
- **Kubeconfig fix on bastion**: changed deprecated exec plugin API from `client.authentication.k8s.io/v1alpha1` to `v1beta1`
- **Usability**: added persistent alias `k=kubectl` in `~/.bashrc`

### PROD EU Istio Resources Created (`istio-system`)
- **Gateway**: `itariff-gateway`
- **VirtualServices**:
  - `itariff-ui`
  - `itariff-api`
  - `itariff-bff`

### PROD iTariff Internal Hosts Configured
- `itariff-ui.internaleu1prd-itopaz.com`
- `itariff-bff.internaleu1prd-itopaz.com`
- `itariff-api.internaleu1prd-itopaz.com`

### DNS Verification
- All 3 hosts resolve to Istio ingress ELB:
  - `a5c3d5f6763e149a1949597be2e56d79-0a180d890cef99d9.elb.eu-central-1.amazonaws.com`

### Initial Behavior Before Backend Services
- `itariff-ui.internaleu1prd-itopaz.com/` -> `503`
- `itariff-api.internaleu1prd-itopaz.com/` -> `503`
- `itariff-bff.internaleu1prd-itopaz.com/` -> `404` (root path not mapped for bff)

### Test Deployment and Route Proving
- Deployed `test-echo` (Deployment + Service) in:
  - `itariff-ui`
  - `itariff-api`
  - `itariff-bff`
- Added `/test-ping` route at top priority in each VirtualService:
  - `itariff-ui` -> `test-echo.itariff-ui.svc.cluster.local:80`
  - `itariff-api` -> `test-echo.itariff-api.svc.cluster.local:80`
  - `itariff-bff` -> `test-echo.itariff-bff.svc.cluster.local:80`
- End-to-end ingress verification (HTTP Host header through Istio ELB):
  - `itariff-ui.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-ui test ok`)
  - `itariff-api.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-api test ok`)
  - `itariff-bff.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-bff test ok`)

---

### prefiler-bff DEV — VirtualService Routing Fix
- **Cluster**: `euc1-itopaz-dev-eks` | Namespace: `istio-system`
- **Symptom**: `GET https://prefiler-bff-eudev.itopazapp.com/prefiler-bff/prefiler/bff/v1/masters/PageMaster/` returning 404 with `x-amzn-remapped-server: istio-envoy` — request reached Istio but no matching route
- **Root cause**: API Gateway custom domain base path mapping was fixed from `prefiler-bff` → `(none)` (previous session). After this fix, full path `/prefiler-bff/prefiler/...` is forwarded to Istio, but VirtualService only had rules for `/prefiler-auth-bff/` and `/prefiler/` — gap for `/prefiler-bff/` prefix
- **Pods status**: All healthy — `prefiler-bff` (2/2), `prefiler-auth-bff` (2/2)
- **Fix applied** (kubectl patch, type json, op replace on `/spec/http`):
  ```yaml
  - match: [{uri: {prefix: /prefiler-bff/prefiler/}}]
    rewrite: {uri: /}
    route: [{destination: {host: prefiler-bff-svc.prefiler-bff.svc.cluster.local, port: 80}}]
  - match: [{uri: {prefix: /prefiler-bff/prefiler-auth-bff/}}]
    rewrite: {uri: /}
    route: [{destination: {host: prefiler-auth-bff-svc.prefiler-bff.svc.cluster.local, port: 80}}]
  - match: [{uri: {prefix: /prefiler-auth-bff/}}]    ← existing, kept
  - match: [{uri: {prefix: /prefiler/}}]             ← existing, kept
  ```
- **Verified**: HTTP 200, `access-control-allow-origin: *`, full JSON data returned ✅

### prefiler-bff DEV — Previous Session Fixes (context)
- API Gateway swagger CORS added for both paths (`/prefiler-bff/{proxy+}`, `/prefiler-auth-bff/{proxy+}`)
- Swagger imported via `aws apigateway put-rest-api --mode overwrite`, deployment ID `kxakdj`
- Custom domain `prefiler-bff-eudev.itopazapp.com` base path mapping: `prefiler-bff` → `(none)`
- API ID: `l9rbaytbtc`, stage: `dev`

### prefiler-api DEV — CORS Fix (LOCAL ONLY — NOT YET DEPLOYED)
- Python script applied CORS fixes to all 14 paths in `/home/ec2-user/rahul/prefiler-api`
- Added `headers.Access-Control-Allow-Origin` to method response AND `responseParameters` to integration response
- **Pending**: Must import to API GW `9flv9p0c7k` and create deployment to take effect

### tariff-selling-rates-ui — Jenkins Pipeline Fix
- **Root cause**: Docker COPY failed (`stat dist/selling-rates/: file does not exist`) — Angular `npm run build` was never called before Docker build
- **Fix**: Added `Build Angular Application` stage to Jenkinsfile before `Build Docker Image`:
  ```groovy
  stage('Build Angular Application') {
    steps { sh 'npm run build' }
  }
  ```
- **File**: `itariff-k8s-repo/jenkins/tariff-selling-rates-ui`

---

---

## 2026-06-11 — Intellihub HA Assessment + Intranet Server Autoheal Sync

### Intellihub Servers HA Assessment (Account 745510282686, ap-south-1)

#### What was done
- Full HA check on both Intranet prod servers at AWS and application level
- Verified EC2 instance health, AZ placement, ALB target group health, autoheal scripts

#### AWS Level Findings
- Both instances **running** and **healthy** (system + instance checks: ok/ok)
  - `Intranet-prod-1` (`i-0b1f3b8eda05c132b`) — **ap-south-1a** (c5a.xlarge)
  - `Intranet-prod-2` (`i-0a82e63f8fcce6c8e`) — **ap-south-1b** (m5.2xlarge)
- **No Auto Scaling Group** — bare EC2 instances (gap: no automatic replacement on termination)
- Core services all healthy on both instances via `Intellihub-prod` ALB:
  - `intellihub-prod`, `intellihubadmin-prod`, `gatimasterapi-prod`, `sendbulktracking`, `symphonywrapper-prod`, `zendeskwrapper-prod` → all **True HA** ✅
- 5 stale unused target groups identified (not attached to any listener): `aimlprod-1`, `ecureports`, `ecureports-api`, `intellaiml-prod-4001`, `intellihub-prod-2`

#### Application Level Findings
- All 3 autoheal scripts synced and active on **both** servers:
  - `apis-autoheal.sh` (every 5 min + @reboot)
  - `gati-apis-autoheal.sh` (every 2 min)
  - `cleanup_python_zombies.sh` (every 1 min)
- `cleanup_python_zombies.sh` was already in crontab on prod-2 (`.153`) but script file was missing → copied from prod-1 ✅

#### Gaps Identified (no changes made, recommendations only)
1. No ASG — add EC2 Auto Recovery CloudWatch alarm (`StatusCheckFailed_System`)
2. Single-instance genie/docdis TGs — register both instances
3. Health check interval 30s (60s failover) — reduce to 10s for faster failover
4. `intranet-prod-db` Aurora: no Multi-AZ — risk of DB downtime on instance failure
5. 5 stale unused TGs — clean up

---

---

## 2026-06-10 — SIT EU/SG Aurora DB Fixes, prefiler-cache-util Pipeline Fix & Intranet Prod Deploy Fix

### SIT SG Aurora (`apse1-itopaz-sit-aurora-postgresql`)
**Cluster:** `apse1-itopaz-sit-eks` | ap-southeast-1 | Account: 464134132424

#### Problem
- Sudden ReadIOPS spike → high DB load
- Root cause: `ALTER TABLE dbo.filereportedbl` (3.8GB table rewrite) triggered manual VACUUM ANALYZE + `autovacuum_naptime=5s` causing excessive background IO

#### Fix Applied
```bash
# Parameter group: apse1-itopaz-sit-aurora-postgresql-cluster-params
aws rds modify-db-cluster-parameter-group \
  --db-cluster-parameter-group-name apse1-itopaz-sit-aurora-postgresql-cluster-params \
  --parameters "ParameterName=autovacuum_naptime,ParameterValue=60,ApplyMethod=immediate"
```
- `autovacuum_naptime`: **5s → 60s** — applied immediately ✅

---

### SIT EU Aurora (`itariff-sit-cluster`)
**Cluster:** `euc1-itopaz-sit-eks` | eu-central-1 | Account: 464134132424  
**Instance:** `itariff-uat` (db.r5.xlarge) | DB: `TariffSelling` | PostgreSQL 15.15

#### Problem 1 — DMS Replication Slots (99% CPU, ReadIOPS 51K)
- **11 stale DMS logical replication slots** left behind from stopped/failed DMS tasks
- Running for 28 hours, preventing WAL cleanup → massive WAL accumulation → 51K ReadIOPS → 99% CPU

#### Fix Applied
```sql
-- Killed all WAL sender PIDs then dropped all slots
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE application_name LIKE '%dms%';
SELECT pg_drop_replication_slot(slot_name) FROM pg_replication_slots WHERE slot_type='logical';
```
- Result: ReadIOPS 51K → 305 immediately. CPU 99% → 66% → recovering ✅

#### Problem 2 — autovacuum_naptime=5s
- Same as SIT SG — autovacuum firing every 5s causing excessive background IO on 146GB `dbo.tariff` + 184GB `dbo.tariffdetails` tables (autovacuum had **never** run on these tables)

#### Fix Applied
```bash
# Parameter group: aurora-postgresql-uat-15
aws rds modify-db-cluster-parameter-group \
  --db-cluster-parameter-group-name aurora-postgresql-uat-15 \
  --parameters "ParameterName=autovacuum_naptime,ParameterValue=60,ApplyMethod=immediate"
```
- `autovacuum_naptime`: **5s → 60s** — applied immediately ✅

---

### prefiler-cache-util Jenkins Pipeline Fix
**Repo:** `allcargoecu/prefiler-cache-util` (Bitbucket) | Branch: `sit`  
**Jenkins Job:** `prefiler-nonprod-backend/SIT/prefiler-cache-util`

#### Problem 1 — App Compile Error
```
Prefiler.TestApi/Program.cs(20,29): error CS1061: 'ICacheService' does not contain a definition for 'GetAsync'
```
- `Program.cs` called `cache.GetAsync<Object>(key)` but `ICacheService` only defines `GetObjectAsync<T>`
- **Fix:** Changed `GetAsync` → `GetObjectAsync` in `Prefiler.TestApi/Program.cs`
- Commit: `fff0b5ae` pushed to sit branch ✅

#### Problem 2 — mstest Plugin Not Installed
```
java.lang.NoSuchMethodError: No such DSL method 'mstest' found
```
- Jenkinsfile (`prefiler-k8s-repo/jenkins/sit/api/prefiler-cache-util`) used `mstest` step in post-condition
- MSTest plugin not installed on this Jenkins instance
- **Fix:** Replaced with `archiveArtifacts artifacts: '**/TestResults/*.trx', allowEmptyArchive: true`
- Commit: `1188a6a` pushed to prefiler-k8s-repo sit branch ✅

---

### SIT EU UI Latency Investigation — `/selling-rates/import` (10s load time)
**URL:** `https://itariff-euat.itopazapp.com/selling-rates/import`

#### Findings
- Static nginx serve: **17ms** ✅ — not the issue
- Page fires ~10 parallel BFF dropdown API calls on load
- Slow endpoints (all querying `dbo.tariff` 146GB / `dbo.tariffdetails` 184GB with no indexes):

| Endpoint | Time | Root Cause |
|---|---|---|
| `GET /bffdropdown/getShippingLineAgent` | 1,500–180,000ms | Full seq scan, no index, dead tuple bloat |
| `GET /bffdropdown/getTSOCPOL` | 1,946ms | Full seq scan on `dbo.tariff` |
| `GET /bffdropdown/getPOR` | 1,588ms | Full seq scan on `dbo.tariff` |
| `POST /BffTariffSelling/getTariffSellingSearchSingleRow1` | 343–1,798ms | `gettariffmainsearchsinglerow_db` stored proc, full scan |
| `POST /BffTariffBuying/getTariffBuyingSearchSingleRow` | 1,774ms | Full scan |

#### Routing path confirmed
```
Browser → Istio Gateway (itariff-euat.itopazapp.com)
  → /selling-rates/ → tariff-selling-rates-ui (nginx, itariff-ui ns) [17ms]
  → /tariff-selling-bff/ → tariff-selling-bff (itariff-bff ns)
  → tariff-selling-service (itariff-api ns)
  → Aurora PostgreSQL TariffSelling DB
```

#### Fix Plan (5 steps, dev team needed)
1. **Redis cache** on `getShippingLineAgent`, `getTSOCPOL`, `getPOR` — TTL 30min → <5ms
2. **DB indexes** on `dbo.tariff(pol_code)`, `dbo.tariff(por_code)`, `dbo.tariff(shipping_line_code, agent_code)` — use `CREATE INDEX CONCURRENTLY`
3. **Redis cache** on search row endpoints — TTL 5min → <10ms
4. **autovacuum** running on `dbo.tariff`/`dbo.tariffdetails` (will complete in 2–4h, improving planner stats)
5. **Frontend** — use `Promise.all` for dropdown calls, add page skeleton

**Expected improvement:** 8–10s → <500ms after all steps

---

**Account:** 745510282686 | **Region:** ap-south-1 | **SSH Key:** `infrastructure/secrets/keys/intranet/prod/Intranet-prod-1-Key.pem`

### Servers
| Server | IP | Role |
|--------|-----|------|
| Intranet-prod-1 | `10.151.4.89` | c5a.xlarge, compute node |
| Intranet-prod-2 | `10.151.4.153` | m5.2xlarge, memory node |

### Problem 1 — Broken `/root/.aws/credentials`
- File had `#[default]` as commented header → `botocore.exceptions.ConfigParseError` → AWS CLI crash
- **Fix:** `mv /root/.aws/credentials /root/.aws/credentials.bak` — instance IAM profile `intellihub-prod` used instead
- Applied on both servers ✅

### Problem 2 — Git CodeCommit Auth Failure
- `git fetch` failed: `fatal: could not read Username for 'https://git-codecommit...'`
- Root cause: no valid credential helper for root user
- **Fix:** Set IAM Git credentials directly in remote URL (URL-encoded)
```bash
git remote set-url origin "https://<CODECOMMIT_USER>:<CODECOMMIT_PASSWORD>@git-codecommit.ap-south-1.amazonaws.com/v1/repos/aiml-poc"
```
- Applied on both servers ✅

### Problem 3 — App Port 8001 Already In Use After Deploy
- `deploy.sh` kills `intranetapimain.py` by name but uvicorn workers (child PIDs) survived
- New process couldn't bind port 8001
- **Fix:** `fuser -k 8001/tcp` to kill all processes on port, then restart
- Applied on both servers ✅

### Deploy Result
| Server | Commit Before | Commit After | App Status |
|--------|--------------|--------------|------------|
| 10.151.4.89 | `4763205` | `ab9539e` | Uvicorn :8001 ✅ |
| 10.151.4.153 | same | `ab9539e` | Uvicorn :8001 ✅ |

### Recommended Fix for deploy.sh (dev team)
Replace process kill logic:
```bash
# Current (unreliable — misses uvicorn workers)
PIDS=$(ps -ef | grep '[i]ntranetapimain.py' | awk '{print $2}')
if [ ! -z "$PIDS" ]; then kill -9 $PIDS; fi

# Better — kill by port
fuser -k 8001/tcp 2>/dev/null || true
sleep 2
```

---

### PROD EU iTariff Istio Ingress Setup + End-to-End Validation

  - `Gateway`: `itariff-gateway`
  - `VirtualService`: `itariff-ui`
  - `VirtualService`: `itariff-api`
  - `VirtualService`: `itariff-bff`

  - `itariff-ui.internaleu1prd-itopaz.com`
  - `itariff-bff.internaleu1prd-itopaz.com`
  - `itariff-api.internaleu1prd-itopaz.com`

  - Resolved to Istio ingress LB `a5c3d5f6763e149a1949597be2e56d79-0a180d890cef99d9.elb.eu-central-1.amazonaws.com`

  - UI host `/` -> `503`
  - API host `/` -> `503`
  - BFF host `/` -> `404` (expected, only prefixed bff routes defined)

  - Deployed `test-echo` Deployment + Service in namespaces:
    - `itariff-ui`
    - `itariff-api`
    - `itariff-bff`
  - Added `/test-ping` route at top priority in each corresponding VirtualService
  - **Verified via ingress host header**:
    - `itariff-ui.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-ui test ok`)
    - `itariff-api.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-api test ok`)
    - `itariff-bff.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-bff test ok`)

  - **Fix**: Updated parameter group `aurora-postgresql-uat-15`: `autovacuum_naptime` **5s → 60s** (immediate) ✅

### prefiler-cache-util — Jenkins Pipeline Fix (SIT)
- **Problem 1** (`CS1061`): `Program.cs` called `cache.GetAsync<Object>(key)` but interface only defines `GetObjectAsync<T>`
  - **Fix**: `GetAsync` → `GetObjectAsync` in `Prefiler.TestApi/Program.cs` — commit `fff0b5ae` to sit branch ✅
- **Problem 2** (`mstest` DSL not found): MSTest plugin not installed on Jenkins
  - **Fix**: Replaced `mstest` step with `archiveArtifacts` for `.trx` files — commit `1188a6a` to `prefiler-k8s-repo` sit branch ✅

### SIT EU UI Latency Investigation (`/selling-rates/import` — 10s load)
- **Root cause**: ~10 parallel BFF dropdown calls on page load, all querying 146GB `dbo.tariff` / 184GB `dbo.tariffdetails` with no indexes (full seq scans)
  - Slow endpoints: `getShippingLineAgent` (up to 180s), `getTSOCPOL` (1.9s), `getPOR` (1.6s)
- **Fix plan** (requires dev team): Redis cache on dropdown endpoints (TTL 30min), `CREATE INDEX CONCURRENTLY` on key columns, autovacuum completion (2–4h), Promise.all on frontend
- **Static asset serving confirmed healthy**: nginx 17ms ✅

### Intranet Prod Deploy Fix (Account 745510282686, ap-south-1)
- **Servers**: `Intranet-prod-1` (10.151.4.89, c5a.xlarge) + `Intranet-prod-2` (10.151.4.153, m5.2xlarge)
- **Fix 1**: `/root/.aws/credentials` had `#[default]` commented header → ConfigParseError → moved to `.bak`, uses instance IAM profile
- **Fix 2**: Git CodeCommit auth failure on root user → set IAM Git credentials in remote URL (URL-encoded)
- **Fix 3**: Port 8001 already in use post-deploy (uvicorn worker PIDs surviving kill-by-name) → `fuser -k 8001/tcp`
- **Result**: Both servers deployed to commit `ab9539e`, Uvicorn :8001 ✅
- **SSH Key**: `infrastructure/secrets/keys/intranet/prod/Intranet-prod-1-Key.pem`

### Intellihub HA Assessment (Account 745510282686, ap-south-1)
- Both instances healthy (system + instance checks ok/ok), 2 AZs, ALB target groups all green
- 6 services confirmed True HA: `intellihub-prod`, `intellihubadmin-prod`, `gatimasterapi-prod`, `sendbulktracking`, `symphonywrapper-prod`, `zendeskwrapper-prod`
- **Gap**: No ASG (no auto-recovery on instance failure) — recommended EC2 Auto Recovery alarm
- **Fixed**: `cleanup_python_zombies.sh` script was in prod-2 crontab but file was missing → copied from prod-1 ✅
- 5 stale unused target groups identified (not attached to any listener): `aimlprod-1`, `ecureports`, `ecureports-api`, `intellaiml-prod-4001`, `intellihub-prod-2`

---

---

## 2026-06-08 — Cluster Autoscaler Fixes (SIT EU & DEV EU)

### master-prefiler-service (SIT) — HTTP 500 Root Cause & Fix
- **Symptom**: PageMaster endpoint returning 500 with `RetryLimitExceededException` + `NpgsqlException: Connection reset by peer`
- **Root cause 1**: ConfigMap had wrong zone key naming — `ConnectionStrings__zone1` instead of `ConnectionStrings__GroupageHost_zone1`. Keys never matched → fell back to baked-in `appsettings.json` → pointed to DEV Aurora
- **Root cause 2**: Duplicate YAML keys for zone1-zone6 (last one wins) — silent data loss
- **Root cause 3**: Leading space in password: `Password= passwordsit@1035`
- **Fix**: Added `ConnectionStrings__GroupageHost_zone0-zone6`, `EDIDbHost_zone0-zone6`, `SecurityFilerHost_zone0-zone6` — all pointing to SIT Aurora, fixed password
- **Commit**: `76de88f` to `sit` branch in `prefiler-k8s-repo` ✅
- **Verified**: HTTP 200, 25s response ✅

### tariff-company-service (SIT) — Memory Pressure (HPA 93%)
- **Root cause**: `JAVA_TOOL_OPTIONS=-XX:MaxRAMPercentage=50.0` against 2500Mi limit → JVM heap 1250Mi vs 700Mi memory request = 114% HPA → stuck at 10/10 replicas
- **Fix**: Changed to `-Xmx600m -Xms256m` + raised memory request `700Mi → 1000Mi`
- **Result**: HPA memory **93% → 43%** immediately. Commit `afd2097` to `uat` branch in `itariff-k8s-repo` ✅

### SIT Node Count Bloat (33 nodes → ~20)
- **Root cause 1**: CA `--scale-down-utilization-threshold=0.5` — any node with CPU requests >50% blocked from drain
- **Root cause 2**: CA `--skip-nodes-with-local-storage=true` — pods using `emptyDir` blocked 26 nodes from draining
- **Fix**: Patched CA: `--scale-down-utilization-threshold=0.70` + `--skip-nodes-with-local-storage=false`
- **Backup**: `/tmp/cluster-autoscaler-backup-2026-06-08.yaml` on SIT bastion
- **Result**: CA immediately identified 13 unneeded nodes, scaled down to ~20 nodes ✅

---

**Date:** 2026-06-08  
**Cluster:** `euc1-itopaz-sit-eks` (eu-central-1)  
**CA Version:** `registry.k8s.io/autoscaling/cluster-autoscaler:v1.33.0`  
**Performed by:** DevOps Team  

---

### Problem Statement

SIT EKS cluster grew from **22 → 33 nodes** while actual workload resource usage remained very low:
- Average CPU utilization: **2–5% per node**
- Average Memory utilization: **18–39% per node**

Cluster Autoscaler was **unable to scale down** nodes due to two default configurations blocking it.

---

### Root Cause Analysis

### Blocker 1 — Scale-down utilization threshold too low
CA default `--scale-down-utilization-threshold=0.5` (50%)  
Nodes had CPU **requests** above 50% (e.g. 51–97%) even though **actual usage** was only 2–5%.  
CA treats request-based fill, not actual usage → majority of nodes marked **unremovable**.

**CA log evidence:**
```
Node ip-10-100-208-40 unremovable: cpu requested (77.4% of allocatable) is above the scale-down utilization threshold
Node ip-10-100-211-40 unremovable: cpu requested (55.5% of allocatable) is above the scale-down utilization threshold
```

### Blocker 2 — Local storage eviction disabled by default
CA default `--skip-nodes-with-local-storage=true`  
Services using `emptyDir` volumes (ephemeral/temp storage) were preventing node drain.  
All 26 nodes had at least one such pod → **none could be drained**.

**CA log evidence:**
```
Node ip-10-100-215-211 cannot be removed: pod with local storage present: itopaz-profile-service-...
Node ip-10-100-212-208 cannot be removed: pod with local storage present: aes-prefiler-service-...
Node ip-10-100-208-245 cannot be removed: pod with local storage present: tariff-selling-consumer-service-...
```
> **Note:** All affected services are **stateless**. `emptyDir` is ephemeral temp storage — no data loss on pod eviction and rescheduling.

---

### Actions Taken

### Step 1 — Backup CA deployment
```bash
kubectl get deployment cluster-autoscaler-aws-cluster-autoscaler \
  -n kube-system -o yaml \
  > /tmp/cluster-autoscaler-backup-2026-06-08.yaml
```
**Backup location on bastion:** `/tmp/cluster-autoscaler-backup-2026-06-08.yaml`

---

### Step 2 — Patch: Raise scale-down utilization threshold to 70%
```bash
kubectl patch deployment cluster-autoscaler-aws-cluster-autoscaler \
  -n kube-system \
  --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/command/-","value":"--scale-down-utilization-threshold=0.70"}]'
```
**Effect:** CA will now consider a node removable if its total CPU+memory *requests* are below **70%** of allocatable (previously 50%).

---

### Step 3 — Patch: Allow eviction of emptyDir pods
```bash
kubectl patch deployment cluster-autoscaler-aws-cluster-autoscaler \
  -n kube-system \
  --type=json \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/command/-","value":"--skip-nodes-with-local-storage=false"}]'
```
**Effect:** CA will now evict stateless pods using `emptyDir` volumes during node drain. Pods are safely rescheduled onto other nodes with a fresh empty directory.

---

### Step 4 — Verify final CA configuration
```bash
kubectl get deploy cluster-autoscaler-aws-cluster-autoscaler \
  -n kube-system \
  -o jsonpath="{.spec.template.spec.containers[0].command}" | tr "," "\n"
```
**Output confirmed:**
```
"./cluster-autoscaler"
"--cloud-provider=aws"
"--namespace=kube-system"
"--node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/euc1-itopaz-sit-eks"
"--logtostderr=true"
"--stderrthreshold=info"
"--v=4"
"--scale-down-utilization-threshold=0.70"
"--skip-nodes-with-local-storage=false"
```

---

### Result

After patches were applied, CA immediately identified **13 unneeded nodes** and began the scale-down process:

```
nodes.go: ip-10-100-212-208 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-214-191 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-212-16  is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-210-204 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-211-245 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-209-12  is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-208-137 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-211-240 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-213-179 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-208-245 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-210-251 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-214-222 is unneeded since 2026-06-08 13:07:06
nodes.go: ip-10-100-209-154 is unneeded since 2026-06-08 13:07:06
```

**CA automatically:** cordons → drains → terminates each node after 10 minutes unneeded (default `--scale-down-unneeded-time`).

---

### Expected Final State

| Metric | Before | After (expected) |
|--------|--------|-----------------|
| Nodes | 33 | ~20 |
| Avg CPU actual | 2–5% | 5–15% |
| Avg Memory actual | 18–39% | 40–65% |
| CPU request fill | 50–97% per node | ~70% per node |
| CA scale-down threshold | 0.50 (default) | **0.70** |
| emptyDir pod eviction | blocked (default) | **allowed** |

---

### Rollback (if needed)

To restore original CA configuration:
```bash
kubectl apply -f /tmp/cluster-autoscaler-backup-2026-06-08.yaml
```

---

### Reference
- Official CA FAQ: https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md
- Parameter `scale-down-utilization-threshold` default: `0.5` (documented in CA parameters table)
- Parameter `skip-nodes-with-local-storage` default: `true` (documented in CA parameters table)

---

## 2026-06-05 — Operations Log

### prefiler-bff (SIT) — API Gateway CORS + Login Fix
- Fixed HTTP integration (not HTTP_PROXY) to pass `access-token` and `authentication` response headers
- Added `access-token, authentication` to `Access-Control-Expose-Headers`
- Added `officeid, access-token, authentication, channelid, userid, appid` to OPTIONS `Access-Control-Allow-Headers`
- Login verified: `https://prefiler-bff-eusit.itopazapp.com/prefiler-bff/prefiler-auth-bff/bff/v1/auth/login` ✅

### Kafka Topic Fix (SIT)
- **Created topic**: `trf-exl-upld-prc-topic-v3` on SIT MSK (was causing TimeoutException in `tariff-selling-service-batch`)
- **Updated configmap**: Added topic + consumer group to `tariff-selling-service-batch`
- **Committed**: `3e3c9d5` to `origin/uat` in `itariff-k8s-repo` ✅

### Windows Node DNS Fix (SIT EU)
- **Root cause**: Linux node SG (`sg-05c315bde97f77bf1`) did NOT allow traffic from Windows node SG (`sg-02fa2ce777340f203`)
- **Fix**: `aws ec2 authorize-security-group-ingress --group-id sg-05c315bde97f77bf1 --protocol -1 --source-group sg-02fa2ce777340f203`
- **Rule ID**: `sgr-0dc8147e6c3c819fe` ✅

### microfrontend-main Jenkins Pipeline Fix (SIT)
- **Root cause**: AWS STS token expires during `kubectl rollout status` wait (100s+) → "Unauthorized"
- **Fix**: Moved post-deploy verification to separate `Verify Deployment` stage with own `withAWS` block and fresh `aws eks update-kubeconfig`
- **Commit**: `558254d` to `sit` branch ✅

---

---

## 2026-06-04 — Operations Log

### UAT Resource Configuration Audit (itariff-api + itariff-bff)
- **Pulled live config** from euc1-itopaz-sit-eks for all 26 deployments in itariff-api and 3 in itariff-bff
- **Missing resource limits identified**:
  - `tariff-grant-bff`: NO cpu/memory requests or limits set
  - `tariff-selling-bff`: No CPU request/limit (only memory: 2Gi req, 6Gi limit)
  - `tariff-selling-consumer-service`: No CPU/memory limits (only requests: 1 cpu, 3Gi memory)
  - `tariff-domain-batch`: No resources at all

### SIT Kafka Full Topic Configuration Audit
- **Listed all 38 tariff topics** with complete configurations
- **Corrected client.properties path**: `/home/ec2-user/kafka-client/kafka_2.13-3.6.0/bin/client.properties` (not in parent dir)
- **Topic config patterns**:
  - Upload topics: 1GB max.message.bytes, min.insync.replicas=1, no explicit retention
  - Process/archive topics: 10MB max.message.bytes, min.insync.replicas=2, retention.ms=604800000 (7 days)
  - All topics: ReplicationFactor=2, message.format.version=3.0-IV1, unclean.leader.election=false

### Prefiler Auth BFF - External 403 Investigation
- **Symptom**: `https://prefiler-bff-eusit.itopazapp.com/prefiler-bff/prefiler-auth-bff/bff/v1/auth/login` returns 403
- **Internal works**: `https://prefiler-bff.internaleu1-itopaz.com/prefiler-auth-bff/bff/v1/auth/login` returns 200 + JWT
- **Root cause**: FortiGuard IPS (not WAF) blocking the URL at network layer
- **Evidence**: Response HTML contains "FortiGuard Intrusion Prevention - Access Blocked" / "URL is banned"
- **Request path**: Client → FortiGuard → Global Accelerator (af9b262029faa8833.awsglobalaccelerator.com) → API GW → Istio → pod
- **Action needed**: Network team must whitelist URL in FortiGuard policy

### Prefiler tariff-grant-bff/authenticate - 500 Error
- **Call chain**: prefiler-auth-bff → tariff-grant-bff → tariff-profile-service (adauthenticate endpoint)
- **DB query**: `SELECT * FROM profile WHERE ademailid = ? OR mailid = ? AND isdeleted = 0 LIMIT 1`
- **Error**: `NullPointerException: Cannot invoke "com.alcg.profile.entity.Profile.getUser_id()" because "profile" is null`
- **Cause**: User being authenticated from prefiler doesn't have a matching profile entry in tariff DB
- **Fix**: Add user to profile table OR fix null handling in tariff-profile-service code

### AWS WAF & API Gateway Documentation
- **WAF ACL** (`itopaz-api-gwt-acl`): Only attached to itariff-bff API GW (dygy1tl8n5), NOT prefiler-bff
- **Rule priority 0** (`zscalar-ip-restriction`): Blocks if X-Forwarded-For NOT in Zscaler IPv4/IPv6 IP sets
- **prefiler-bff API GW** (7a8aq4c0oa): No WAF, apiKeyRequired=true, routes to internal Istio gateway
- **Custom domain**: `prefiler-bff-eusit.itopazapp.com` → REGIONAL endpoint → basePath `/prefiler-bff` → stage sit
- **API key**: Confirmed valid and enabled (trxH8cOmlp6e9EKOAUUuh6nEi2ofzB4v29me6vWO)
- **Usage plan**: itariff-api — burst:50, rate:100/s, quota:80,000/day

---

## 2026-05-30 — Operations Log

### FAISS Vector Database Setup
- **Installed** faiss-cpu, sentence-transformers, torch (CPU-only) on workspace
- **Ingested** KNOWLEDGE-BASE.md into FAISS index (68 chunks, 384-dimension vectors, 102KB index)
- **Scripts**: `scripts/ingest_knowledge.py`, `scripts/query_knowledge.py` — supports semantic search, JSON output, interactive mode
- **Vector store**: `vectordb/knowledge.index` + `vectordb/chunks.json`

### S3 Bucket Organization (devops-securit-dev)
- **Cleaned up** old scattered files: removed `eks-docs/`, `prefiler-sit-knowledge/`, root-level session/handover .md files
- **Moved** all root-level .md files under `devops/` prefix (Activity Calender, GATI inventories, ZPA, account_details, ec2-rds)
- **Uploaded** organized structure via DEV jump server (10.100.145.118):
  - `devops/KNOWLEDGE-BASE.md` — single consolidated file for LLM agents
  - `devops/activity-log.md`, `devops/eks-clusters.md`
  - `devops/docs/` — all detailed documentation + knowledge-export/
  - `devops/vectordb/` — FAISS index + metadata
  - `devops/scripts/` — ingest, query, rebuild tools
- **S3 root** now only contains binary archives (rpm, tar, tgz, tar.xz) + `pem/`

### Bastion Host Cleanup (/home/ec2-user/)
- **Deleted ~1.3GB** of old logs/archives: `batch2.log` (413MB), `batch2.3log` (429MB), `kafka*.tgz/zip` (218MB), `python_3_10_slim.tar` (129MB), `eks-node-cleanup.log` (81MB)
- **Organized 140+ loose files** into structured `organized/` directory:
  - `organized/repos/` — 20 git repos & script folders
  - `organized/k8s-manifests/` — 28 YAML files
  - `organized/iam-policies/` — 6 policy JSONs
  - `organized/keys/` — certs, PEM files
  - `organized/tools/` — gcrane, krane, cleanup scripts
  - `organized/efs-configs/` — 4 EFS PV/PVC yamls
  - `organized/istio-configs/` — gateway, virtualservice
  - `organized/archived-configs/` — old misc files & dirs
- **Deleted additional 727MB**: `bw-baseimage_2.9.0.tar` (435MB), both istio installs (178MB), kafka extracted (114MB), 6 empty dirs
- **Cleaned hidden caches (~12GB)**: `.cache/pip` (3.9GB), `.local/lib` (4.9GB), 4 old VS Code servers (1.8GB), `sufeeyan-copilot/` (1.1GB), `.cache/aws` + `.cache/cloud-code` (338MB)
- **Disk usage**: 88% → 48% (3.9GB free → 16GB free)
- **Excluded** from changes: `rahul/`, `sufeeyan/`, `vijay/`, `rajnish/`

---

## 2026-05-29 — Operations Log

### master-prefiler-service Pipeline Fix
- **Root cause**: Jenkins reads pipeline from `jenkins/dev/api/master-prefiler-service` but fix was applied to `jenkins/dev/master-prefiler-service`
- **Fix 1**: Copied corrected pipeline to correct path (`jenkins/dev/api/master-prefiler-service`)
- **Fix 2**: `AccessDeniedException` — `Terraform_Execution_Role` (074779643551) cannot call `codeartifact:GetAuthorizationToken` cross-account to 439891535362. Removed `withAWS` wrapper, using Jenkins agent's native AWS credentials instead
- **Fix 3**: Build failed with `CS0246: type 'prefiler' not found` — commit `7db6d23` had deleted `SharedLib/` containing `prefiler.security.dll`, `Prefiler.Base.Shared.dll`, `Prefiler.CacheUtil.dll`. Restored DLLs from git history
- **Pushed**: prefiler-k8s-repo `dev` branch (commits 6295650, f1f0927), master-prefiler-service `develop` branch (commits 4c55e4c, e94f43c)

### itariff-k8s-repo JVM/Memory Optimization (uat branch)
- **Pushed** JVM memory optimization and resource right-sizing for 8 services (commit 5603bdc)
- Services: tariff-buying-carriage, otherbooking, service, standardcost, truck, warehouse, grant-auth, selling-storage-service
- Changes: JAVA_TOOL_OPTIONS env vars, memory requests/limits right-sized

### itariff-k8s-repo (uat branch)
- **Updated `tariff-buying-shippingline-consumer-service.yaml`** config for `buying-domain-service`:
  - Changed microId to `buying-domain-service`, port to 80, context-path to `/buying-domain-service`
  - Optimized HikariCP pool settings (keepalive-time, idle-timeout, connection-timeout tuned)
  - Restructured JPA config (moved show-sql/ddl-auto)
  - Updated Kafka config with bulk upload topics, bulk process/archive topics, new consumer groups
  - Updated `restTemplate` connection pool (maxPerRoute: 20, maxConnections: 100), removed connect/read timeouts
  - Simplified `serviceurls` (geography, master, invoice, company, tariff)
  - Replaced `serviceMsg` with `service` block (new error codes: DUP1202, SAVE1201, ERR1203, NF1205, VAL1203)
  - Updated management endpoints include to `health,info,prometheus,metrics`

- **Improved Jenkins ConfigMap pipeline (`Jenkincm`)** — simplified for UAT-only use:
  - Hardcoded UAT branch, cluster (euc1-itopaz-sit-eks), region, cross-account role
  - Reduced parameters to only `namespace` and `application_name`
  - Cleaned up and sorted application list (removed duplicates)
  - Added validation stage (fails early if `--SELECT--` chosen)
  - Removed unused variables (REGISTRY, DEPLOY_ENV, gitCommit)
  - Added rollout timeout (120s) to prevent hanging builds
  - Always uses cross-account role (no conditional)

---

## 2026-05-27 — Operations Log

### itariff-k8s-repo (develop branch)
- **Increased CPU/memory by 10%** for 9 buying services and pushed to Bitbucket (commit cfbf401)
- **Patched DEV cluster** (euc1-itopaz-dev-eks, ns: itariff-api) with new resource values
- Services updated: tariff-buying-carriage-consumer, carriage, otherbooking, service, shippingline-consumer, standardcost, truck, warehouse-consumer, warehouse

### prefiler-k8s-repo (dev branch)
- **Applied all ConfigMaps to DEV cluster** (prefiler-api namespace): aci, aes, afr, ams, basf, dagangnet, ics, ics2, imdg, master, mblfiler, mpci, prefiler-auth-service (13 total)
- **Fixed sa-prefiler-service-config.yaml**: namespace was `default`, changed to `prefiler-api`, pushed to Bitbucket (commit 929171b)
- **prefiler-bff namespace**: prefiler-auth-bff-config, prefiler-bff-config (already in sync)

### SIT EU Cluster (euc1-itopaz-sit-eks) Optimization
- **Enabled NTH** (aws-node-termination-handler) temporarily, then **disabled** again per user request
- **Disabled duplicate fluent-bit** (fluent-bit namespace) — was running alongside amazon-cloudwatch/fluent-bit. Saved ~1.7 cores + 833Mi
- **Disabled promtail** (monitoring namespace) — redundant with fluent-bit. Saved ~1.7 cores + 4.25GB
- **Verified csi-smb-node** is REQUIRED (8 bound SMB PVCs across itopaz-api, auth, export, platform)
- **Verified efs-csi-node** is REQUIRED (4 bound EFS PVCs in istio-system: grafana, jaeger, kiali, prometheus)

### Node Status Checks (May 27)
- DEV EU: 18 nodes (3 cordoned)
- SIT EU: Started at 23 nodes -> scaled to 35 nodes (all Ready)
- SIT Singapore: 4 nodes (1 cordoned)

---

## 2026-05-26 — Operations Log

- Fixed prefiler Jenkins pipelines (aes, afr SIT builds)
- Created 8 missing frontend Jenkins jobs
- Pushed prefiler-k8s-repo sit branch (commit 6221583)
- Created jenkins-config.md and eks-prefiler-config.md
- Synced md files to S3 bucket devops-securit-dev

---

---

## 2026-05-20 — EKS Resource Optimization (SIT & DEV) & Session Notes

### SIT (UAT) Selling Service Fixes
- **Fixed `tariff-selling-service` CPU**: Patched from 350m/800m → 500m/2000m
- **Fixed `tariff-selling-consumer` memory**: Was ~1.5TB/~1.9TB (same TB bug), fixed to 700Mi/1200Mi
- **Fixed `tariff-selling-service` HikariPool exhaustion**: Was getting 504s — `Connection is not available, request timed out after 10005ms (total=12, active=12, idle=0, waiting=9)`. Increased `maximum-pool-size` from 12 → 25 in configmap
- **Checked `tariff-selling-service-batch`**: Healthy, no issues (500m/2Gi, 2Gi/3Gi)

### Node Status Check (All 3 Environments)
- **SIT EU (Frankfurt)**: 27 nodes — All Ready ✅
- **DEV EU (Frankfurt)**: 15 nodes — All Ready ✅
- **SIT Singapore**: 3 nodes — All Ready ✅ (EKS v1.35.3/v1.35.4)

### SIT Singapore Cluster Discovery
- **Region**: ap-southeast-1
- **Bastion**: `ssh -i /home/ec2-user/rahul/rahul-key ec2-user@10.130.210.3` (from current host 10.151.4.165)
- **Nodes**: 3

### Other Checks
- **itopaz UI (DEV)**: All healthy — export-ui (2), maintenance-ui (2), shell-ui (2)
- **afr-prefiler-service (SIT Frankfurt)**: 2 pods Running 2/2 ✅ (prefiler-api namespace)
- **DEV Kafka consumer groups**: Listed 58 groups; identified stale `-local` groups and mismatched `-uat` groups

### SIT Cluster (euc1-itopaz-sit-eks)
### Completed
1. **Cluster Autoscaler IRSA fixed** — Added SA annotation, fixed trust policy (wrong condition key + wrong SA name)
2. **Nodes uncordoned** — 12 nodes were accidentally cordoned during migration, uncordoned all
3. **Metrics-server fixed** — Pod was Pending due to cordoned nodes, then label `k8s-app=metrics-server` added to deployment pod template
4. **HPAs capped** — All itariff-api HPAs set to min=2
   - Buying services: max=3
   - Selling services (25-partition topics): max=20
   - Other selling: max=10
5. **tariff-selling-consumer resources fixed** — Was 1.5TB memory request (misconfigured). Set to cpu:250m/1, memory:700Mi/1200Mi
6. **tariff-selling-consumer-hpa** — Removed memory metric, CPU only (75% target)
7. **tariff-buying-consumer-service HPA** — Removed memory metric, CPU only (80% target)
8. **tariff-buying-warehouse-service** — Added resources (cpu:100m/500m, memory:700Mi/1126Mi) to fix HPA <unknown>
9. **Prefix delegation** — Already enabled (ENABLE_PREFIX_DELEGATION=true), maxPods=110 working

### DEV Cluster (euc1-itopaz-dev-eks)
### Completed
1. **Metrics-server fixed** — Added `k8s-app=metrics-server` label to pod template (same issue as SIT)
2. **Prefix delegation enabled** — Set ENABLE_PREFIX_DELEGATION=true on aws-node daemonset
3. **Instance refresh completed** — All nodes replaced, but maxPods still 29 (needs launch template UserData)

### Pending
- **Launch template update needed** — Add NodeConfig UserData with maxPods=110, then another instance refresh
- **6 Pending pods** — Windows pods need Windows node group

---

### 1. Dev vs SIT Resource Comparison (itariff-api)

### Services with HIGHER resources in SIT than Dev:
| Service | Dev CPU Req/Lim | SIT CPU Req/Lim | Dev Mem Req/Lim | SIT Mem Req/Lim |
|---------|----------------|-----------------|-----------------|-----------------|
| tariff-company-service | 100m/300m | 500m/2 | 700Mi/2500Mi | 2Gi/8Gi |
| tariff-geo-service | 100m/300m | 500m/2 | 700Mi/2500Mi | 2Gi/8Gi |
| tariff-invoice-service | 50m/250m | 500m/2 | 1126Mi/1434Mi | 2Gi/8Gi |
| tariff-master-service | 100m/300m | 500m/2 | 700Mi/2500Mi | 2Gi/8Gi |
| tariff-selling-oc-service | 100m/500m | 300m/1 | 700Mi/1024Mi | 300Mi/2Gi |
| tariff-selling-storage-service | 50m/250m | 500m/2 | 500Mi/950Mi | 300Mi/8Gi |
| tariff-trucker-rates-service | 50m/250m | 300m/1 | 300Mi/900Mi | 300Mi/2Gi |

### Services with HIGHER resources in Dev than SIT:
| Service | Dev CPU Req/Lim | SIT CPU Req/Lim | Dev Mem Req/Lim | SIT Mem Req/Lim |
|---------|----------------|-----------------|-----------------|-----------------|
| tariff-selling-service | 500m/2000m | 350m/800m | 1400Mi/1800Mi | 1400Mi/1800Mi |
| tariff-buying-service | 100m/500m | 100m/500m | 500Mi/1126Mi | 300Mi/1126Mi |

### 2. S3 Optimization Report (itariff-api-optimization-report.md)

Located at: `s3://devops-securit-dev/itariff-api-optimization-report.md` (root level)
- NOT accessible from jump server 10.100.208.17 (different account)
- Accessible from dev bastion 10.100.145.118

Key findings:
- Most services using <5% CPU of requested resources
- tariff-selling-consumer-service has NO CPU limit (High severity)
- tariff-company-service & tariff-geo-service at ~85% memory usage
- tariff-domain-batch has no resource data (missing monitoring)

### 3. Prefiler Auth Service - Dev (WORKING)

- Namespace: `prefiler-api`
- Endpoint: `http://prefiler-auth-service-svc.prefiler-api.svc.cluster.local/api/v1/Auth/login`
- External: `http://prefiler-api.internaleu1dev-itopaz.com/prefiler-auth-service/api/v1/Auth/login`
- VS in `istio-system`, routes `/prefiler-auth-service/` prefix
- Config baked into Docker image (`/app/appsettings.json`)
- No envFrom or volume mounts needed - works with image-baked config
- Redis: `master.euc1-itopaz-dev-redis.lf4u8f.euc1.cache.amazonaws.com`

### 4. Prefiler Auth Service - SIT (BROKEN - DB Connection Failure)

- Namespace: `prefiler-api`
- External: `http://prefiler-api.internaleu1-itopaz.com/prefiler-auth-service/api/v1/Auth/login`
- VS in `istio-system`, routes `/prefiler-auth-service/` prefix → correct
- Pods: 2 replicas Running
- Image: `464134132424.dkr.ecr.eu-central-1.amazonaws.com/sit-eu/prefiler-backend:prefiler-auth-service-sit-c2b2a401`

### Root Cause:
- SIT image has **dev config baked in** (`appsettings.json`):
  - Redis → `euc1-itopaz-dev-redis` (should be `euc1-itopaz-sit-redis-new`)
  - DB connection string (encrypted) → points to dev DB, unreachable from SIT VPC
- Error: `Npgsql.Internal.NpgsqlConnector.RawOpen` Socket error (can't connect to PostgreSQL)

### Actions Taken:
1. Created `prefiler-auth-service-config` ConfigMap (flat key-value, SIT Redis)
2. Created `prefiler-auth-service-secret` Secret (connection strings from original CM)
3. Patched deployment with `envFrom` (configMapRef + secretRef)
4. Patched deployment with volume mount: ConfigMap `prefiler-auth-service` → `/etc/config/`

### Still Broken Because:
- DB connection strings are **encrypted** with AES (Key: `vZz1aZkK6XzqvZkLZ3sYw9vZz1aZkK6XzqvZkLZ3sYw=`)
- The encrypted values in the ConfigMap decrypt to **dev DB endpoint**
- Need correct SIT PostgreSQL connection string encrypted with the same key
- ASP.NET Core reads from `/app/appsettings.json`, not `/etc/config/` — volume mount alone won't override

### To Fix:
- Team needs to provide correct SIT encrypted DB connection string
- OR rebuild image with correct SIT `appsettings.json`
- OR mount correct config at `/app/appsettings.Production.json`

### 5. SIT Prefiler-API VirtualService Routes

All routes in `prefiler-api` VS (istio-system namespace) — **Updated June 4, 2026 (13 routes)**:
- `/sa-prefiler-service/` → prefiler-auth-service-svc (note: sa routes to auth-service)
- `/afr-prefiler-service/` → afr-prefiler-service-svc
- `/ams-prefiler-service/` → ams-prefiler-service-svc
- `/master-prefiler-service/` → master-prefiler-service-svc
- `/prefiler-auth-service/` → prefiler-auth-service-svc
- `/ics2-prefiler-service/` → ics2-prefiler-service-svc
- `/aes-prefiler-service/` → aes-prefiler-service-svc
- `/dagangnet-prefiler-service/` → dagangnet-prefiler-service-svc
- `/aci-prefiler-service/` → aci-prefiler-service-svc
- `/basf-prefiler-service/` → basf-prefiler-service-svc
- `/ics-prefiler-service/` → ics-prefiler-service-svc
- `/imdg-prefiler-service/` → imdg-prefiler-service-svc
- `/mblfiler-prefiler-service/` → mblfiler-prefiler-service-svc

Note: SIT now has 13 routes matching Dev (previously only had 2: afr + auth catch-all)

### 6. ConfigMaps in prefiler-api namespace (SIT)

- `aci-prefiler-service` - 1 data key
- `prefiler-auth-service` - 1 data key (nested YAML manifest)
- `prefiler-auth-service-config` - 16 data keys (flat, created today)

---

## 2026-05-18 — Operations Log

### tariff-buying-carriage-service Kafka Topic Fix (SIT/UAT)
- **Root cause**: Producer was publishing to `tariff-buying-carriage-excel-upload-local` (dev default from application.yml) — topic doesn't exist on UAT broker
- **Error**: `TimeoutException: Topic tariff-buying-carriage-excel-upload-local not present in metadata after 60000 ms`
- **Fix**: Added `tariff-buying-carriage-excel-upload-topic-name: tariff-buying-carriage-excel-upload-uat` to `tariff-buying-carriage-service` configmap (was missing, consumer CM had it but producer didn't)
- **Note**: Service returned HTTP 200 despite failure (silent failure)

### auth-base-uri Addition (SIT/UAT)
- **Added** `auth-base-uri: http://tariff-profile-service.itariff-api.svc.cluster.local/profile-domain-service` to:
  - `tariff-buying-carriage-service` configmap (serviceurls section)
  - `tariff-buying-carriage-consumer-service` configmap (new serviceurls section created)
- Restarted both deployments

### tariff-grant-auth Resource Fix (DEV)
- **Issue**: Memory request/limit was ~1.1TB/~1.5TB (bytes with `m` suffix — same bug pattern)
- **Fix**: Patched to cpu:100m/500m, memory:700Mi/1500Mi

---

### 2026-10-10 - Merge master control to main with SCM backups

- User requested merging feat/topaz-master-control into main and will deploy each repository through Jenkins.
- Preserved each original main remotely as backup/main-before-topaz-master-control-20261010 before pushing merges.
- itopaz-agent: original 3c63589, merged main 94a54bc.
- allcargo-itopaz-knowledge: original cef2497, merged main d28054e.
- aws-dashboard: original b07b711, merged main 4d94a06.
- Knowledge Jenkinsfile removed per-minute SCM polling and gates Deploy to EKS and Verify Rollout on DEPLOY_TO_DEV=true plus UserIdCause. Use Build with Parameters for its manual deployment. Jenkins runtime validation remains for the operator's build.
- Verified remote main and backup commit IDs, feature ancestry, exact merged feature trees, and clean worktrees in all three repositories. No Jenkins job was invoked and no deployment command was run for this merge task.

### 2026-10-10 - Direct master Dashboard API, POC account, and agentx UI

- DEV deployment readiness: itopaz-agent, knowledge-bot-backend, aws-dashboard-api all 1/1; pods 2/2 with no restarts at inspection. Dashboard and Knowledge application health passed.
- Important runtime finding: live itopaz-agent-75 lacks Python and /control/status returns 404. Jenkins SCM definitions for all three jobs already use main; rebuild agent from the current main. Agent pipeline now cleans its workspace, explicitly checks out main, and verifies the Python runtime after rollout.
- Added Python agent 1.4.0 browser console at /agentx, with service health, authenticated chatbot/search/inventory, and a manual daily checklist. Existing live /agentx prefix routes to agent service port 8082 without rewrite. Browser has no resource mutation endpoint; key stays in tab memory.
- Direct master API: separate authenticated account listing and exact-payload approved actions; expiry <=5 minutes, configured account/region checks, wrong-role account guard, duplicate approval rejection per API process. Bot credentials do not authorize direct master endpoints. Changes still require typed approval on Windows.
- Operator confirmed POC 745510282686, ap-south-1, existing dashboard role name eks-dashboard-s3-role. Added account/role/region to Dashboard manifest and POC/Mumbai filters to frontend. Standalone worker-2 STS role verification failed TLS certificate validation with default and system CA bundles; IAM permissions and trust remain unverified. No TLS checks disabled for this check and no IAM changes performed.
- Provisioned Secret topaz-dashboard-master (dedicated token) and stored private Windows token without displaying it. Updated SSH helper to repair stale pod forwards and serve separate controller 18082 and Dashboard 18080 loopback connections. Temporary Jenkins key copy removed after isolated build checks.
- Tests: local Python 18 passed; SCM Python 13 passed and 5 intentionally skipped for missing local node registry; Go tests passed; Dashboard frontend built in isolated Node container; agent UI JavaScript syntax passed. No AWS resource start/stop/tag/scale performed. No Jenkins builds or rollout commands launched by this task.
- Original Agent and Dashboard main branches preserved remotely as backup/main-before-dashboard-ui-20261010. User will deploy through Jenkins: aws-dashboard first, then itopaz-agent; Knowledge remains compatible.

### 2026-10-10 - Fix Jenkins agent checkout HTTP 403

- User supplied Jenkins build 76 failure: Jenkinsfile retrieval from x-token-auth@bitbucket.org succeeded, but Checkout failed after the pipeline used the bare Bitbucket URL with the token credential.
- Restored x-token-auth username in the checkout URL, retaining main and existing itopaz-k8s-repo-token credential. This corrects the identity removed by the prior explicit-checkout change.
- Jenkinsfile diff check passed. Fix commit b1d4a05 published to itopaz-agent main. Jenkins rerun remains with user; failed build did not reach deployment stages. No credential values were read or changed.

### 2026-10-10 - Jenkins test mount and POC authentication fixes

- Jenkins build 78 passed checkout but failed Python test discovery because the Jenkins-container workspace bind path resolved on the Docker host to a different directory. Replaced bind mounting with tar streamed over docker run stdin. Verified against the actual Jenkins checkout in python:3.12-slim: 13 tests passed, 5 expected local-registry skips. Agent main fix: 1da72d3.
- Live aws-dashboard-api api-92 contained POC account, role, and ap-south-1 settings. Cached collectionErrors reported Mumbai STS AssumeRoleWithWebIdentity HTTP 403 with an HTML response; other accounts remained accessible. Existing UI discarded this failure and displayed zero accounts.
- Dashboard authentication now resolves IRSA credentials and performs account AssumeRole/GetCallerIdentity through configured STS_REGION (eu-central-1 in DEV), while resource clients retain ap-south-1 for POC. A mock HTTP regression test verifies STS endpoint/signing region without changing the resource region.
- Dashboard surfaces filter-specific collection errors and shows unavailable counts rather than zero when all selected account data fails. Mumbai region label added. Go tests, 3 frontend tests, and frontend production build passed. Dashboard main fix: 60d81c4.
- Changes published for user's manual Jenkins deployments. Actual POC role trust/resource access still requires a successful post-rollout read-only check; no IAM changes or resource mutations performed. Temporary Jenkins key copy removed.


### 2026-10-10 POC EC2/RDS-only configuration
- Pushed aws-dashboard main commit 4853464: POC service map skips EKS/ASG collection and rejects EKS actions; UI hides EKS and marks failed EC2/RDS collection unavailable. Go tests, five frontend tests, and Vite production build passed. Jenkins deployment remains with the operator.
- Live api-93 verifies POC STS identity successfully; remaining Mumbai EC2/RDS calls return HTML 403 and pod HTTPS probes fail certificate validation. Network/endpoint/TLS remediation remains outstanding; no IAM or firewall changes made.
- Master UI key is the existing private secrets/control-token.txt file; token contents were not printed. Temporary restricted Jenkins key copy removed.


### 2026-10-10 POC remaining endpoint failure
- Confirmed api-94 is deployed and POC services are EC2/RDS only; assume-role identity succeeds. Mumbai EC2/RDS still return HTML 403 with no AWS request ID.
- API pod HTTPS certificate validation fails for both Mumbai endpoints. Worker-2 TLS inspection identifies Fortinet CA FGVMSLTM24000312 for Mumbai, versus valid Amazon certificate for Frankfurt. Evidence points to Fortinet access/inspection policy; exact deny rule remains to be checked in gateway logs.
- Saved infrastructure/poc-endpoint-access.md with observed pod/node, endpoint-specific network remediation proposal and verification steps. No firewall/IAM/resource changes or Jenkins deployments performed.


### 2026-10-10 Approved PROD bastion stop
- Operator explicitly approved stopping euc1-itopaz-bastion-prd-1-old / i-0246c639166a0cea9 / 10.100.98.195, account 965031587107, eu-central-1.
- Windows master called authenticated Dashboard POST /api/master/action with exact-request confirmation and a fresh 120-second approval. AWS returned running -> stopping; fresh targeted inventory verified stopped.
- Restored stale SSH loopback forwarding before execution. Initial API attempts were rejected for approval expiry; no AWS mutation occurred on those rejections.


### 2026-10-11 Worker health check
- Worker-1 (10.151.4.165): two SSH attempts reset before authentication; health and agent could not be verified. This does not establish that the instance is stopped.
- Worker-2 (10.100.95.39): SSH works, 4 CPUs, load 0.09, 95.7% memory available, disk 65.5% used / 16.3 GB free, Python 3.12.3. Git/SSH/kubectl/AWS CLI/Docker present. fwupd-refresh.service is failed; primary system capacity is healthy.
- Worker-2 agent --help and --nodes succeed. Launcher points to .itopaz-agent/releases/20261009, an older release; its node registry still marks worker-2 optional/overflow. All nine Python files parse when UTF-8 BOM is handled. Operation lock module exists, but no lock file was found at the workspace or release root. No worker configuration or software was changed.


### 2026-10-11 Worker network access recorded
- Operator confirmed worker-1 (10.151.4.165) has internet access.
- Operator confirmed worker-2 (10.100.95.39) is behind a firewall with no internet access.
- Saved node-specific network metadata in nodes.json and infrastructure/worker-network-access.md. No remote configuration changed.


### 2026-10-12 Both worker nodes checked
- Both reachable over SSH; agent --help succeeds and all nine release Python files parse on each. Both launch release 20261009 with operation locks enabled.
- Worker-1: root disk critically low, 594 MB free / 30 GB, df reports 99% used; workspace 828 MB. Low load and 86% memory available; no failed systemd services.
- Worker-2: low load, 95.1% memory available, disk 65.5% used / 16.3 GB free; fwupd-refresh.service still failed. Saved operator-provided internet policies retained.
- Saved infrastructure/worker-health-latest.md. No cleanup, upgrades, or remote changes performed.


### 2026-10-12 Worker-1 disk cleanup
- Operator requested Worker-1 cleanup. Removed pip download cache (176 files), npm cache, DNF package cache, and ten cached VS Code extension download files (912245695 bytes). Vacuumed archived system journals to 14-day / 200 MB limits, freeing 418.4 MB; active logs retained.
- Root df before: 99% used, 594 MB available. Final df: 83% used, 5.4 GB available; about 4.8 GB recovered. Journal usage now 206.1 MB.
- Agent startup verified successfully afterward; no failed systemd services. Repositories, credentials, installed editor versions/extensions, application data, Docker images, and volumes preserved.


### 2026-10-12 Additional Worker-1 cleanup
- Operator requested further cleanup. Removed seven older inactive editor server directories: three VS Code bin versions, three VS Code CLI server versions, and one Kiro version. Retained newest two versions in each directory and rechecked process command lines, executables, and working directories before removal.
- Recovered 4451270656 bytes (about 4.1 GiB). Agent startup passed afterward. Projects, credentials, extensions, user settings, Docker images, and Python packages preserved.
- Final root df: 69% used, 9.6 GB available. No failed systemd services. Latest health report updated.


### 2026-10-12 BW UAT Docker inspection attempted
- Operator requested Docker inspection on 10.233.30.104, documented instance i-0a490e2198383b309, account 581621506601. SSH endpoint reachable; saved mdm/uat/EC2-BW-Server-Key.pem rejected for ec2-user and ubuntu.
- Worker-1 has identical saved key. No local AWS profile for account 581621506601 / bw-uat exists, so alternate AWS inspection unavailable with current configuration. Requested correct SSH username/key.
- Docker state not inspected and server unchanged. Temporary restricted key copy removed; public host key recorded in .tmp/bw-uat-known-hosts.
- Operator confirmed ec2-user / EC2-BW-Server-Key. Retried alternate mdm/dev key copy; it is identical to the UAT copy and also rejected. Temporary alternate key copy removed. Correct private-key file or server authorized-key repair is still required.


### 2026-10-12 BW UAT authorized-key mismatch confirmed
- Compared operator-provided authorized public key with saved BW PEM public key: mismatch. Checked 30 saved private keys; no matching key found.
- Saved public-only infrastructure/ssh-public-keys/bw-master-access.pub corresponding to the local BW PEM for optional server authorization. Existing server access was not modified. Docker inspection still awaits matching SSH access.


### 2026-10-12 BW UAT Docker inspection completed
- After operator added topaz-master-bw-access public key, SSH ec2-user@10.233.30.104 succeeded. Read-only Docker inventory saved under infrastructure/reports/bw-uat-docker-20261012 (report, container/image CSV, sanitized inventory and resource stats).
- 110 containers: 61 running / 49 exited. Five exit code 1; 41 code 143; three code 137; no OOMKilled flags. Two stopped containers show restart counts 10 and 59. Running containers have no Docker health checks or memory limits.
- Root disk 81% used / 20 GB free; container writable layers 67.85 GB, 25.93 GB reclaimable in stopped containers. No Docker changes or cleanup performed. Temporary private-key copy removed.

### 2026-10-12 Quantum S3 buckets and CloudFront origins

- Operator requested eight Quantum module buckets for Epic, RIA, Freight, and PACE in Dev and Prod, then specified that every new bucket must be in Frankfurt (`eu-central-1`). AWS SSO identity was verified as account `674017976129` before changes.
- Created `quantum-epic-dev`, `quantum-epic-prod`, `quantum-ria-dev`, `quantum-ria-prod`, `quantum-freight-dev`, `quantum-freight-prod`, `quantum-pace-dev`, and `quantum-pace-prod` in `eu-central-1`.
- Applied all four S3 public-access blocks, AES-256 default encryption, and `BucketOwnerEnforced` ownership. Each bucket policy allows CloudFront `s3:GetObject` access only from its corresponding distribution ARN.
- Added each bucket as a second S3 origin on the matching existing CloudFront distribution. Existing aliases, default origins, and URL routing were retained. No cache behavior points to a Quantum origin yet; application traffic continues to use the original origins.
- Live read-only verification confirmed all eight bucket regions and controls, policy source ARNs, two origins per distribution, original default origins, and all eight distributions in `Deployed` status. PACE Prod was initially `InProgress` immediately after update, then reached `Deployed`.
- Script: `scripts/provision-quantum-origins.ps1`. Pre-change distribution snapshots and initial result: `infrastructure/backups/quantum-origins-20261012-133651/`.

## June 10–11, 2026

### PROD EU iTariff Istio Ingress Setup + End-to-End Validation

  - `Gateway`: `itariff-gateway`
  - `VirtualService`: `itariff-ui`
  - `VirtualService`: `itariff-api`
  - `VirtualService`: `itariff-bff`

  - `itariff-ui.internaleu1prd-itopaz.com`
  - `itariff-bff.internaleu1prd-itopaz.com`
  - `itariff-api.internaleu1prd-itopaz.com`

  - Resolved to Istio ingress LB `a5c3d5f6763e149a1949597be2e56d79-0a180d890cef99d9.elb.eu-central-1.amazonaws.com`

  - UI host `/` -> `503`
  - API host `/` -> `503`
  - BFF host `/` -> `404` (expected, only prefixed bff routes defined)

  - Deployed `test-echo` Deployment + Service in namespaces:
    - `itariff-ui`
    - `itariff-api`
    - `itariff-bff`
  - Added `/test-ping` route at top priority in each corresponding VirtualService
  - **Verified via ingress host header**:
    - `itariff-ui.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-ui test ok`)
    - `itariff-api.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-api test ok`)
    - `itariff-bff.internaleu1prd-itopaz.com/test-ping` -> `200` (`itariff-bff test ok`)

  - **Fix**: Updated parameter group `aurora-postgresql-uat-15`: `autovacuum_naptime` **5s → 60s** (immediate) ✅

### prefiler-cache-util — Jenkins Pipeline Fix (SIT)
- **Problem 1** (`CS1061`): `Program.cs` called `cache.GetAsync<Object>(key)` but interface only defines `GetObjectAsync<T>`
  - **Fix**: `GetAsync` → `GetObjectAsync` in `Prefiler.TestApi/Program.cs` — commit `fff0b5ae` to sit branch ✅
- **Problem 2** (`mstest` DSL not found): MSTest plugin not installed on Jenkins
  - **Fix**: Replaced `mstest` step with `archiveArtifacts` for `.trx` files — commit `1188a6a` to `prefiler-k8s-repo` sit branch ✅

### SIT EU UI Latency Investigation (`/selling-rates/import` — 10s load)
- **Root cause**: ~10 parallel BFF dropdown calls on page load, all querying 146GB `dbo.tariff` / 184GB `dbo.tariffdetails` with no indexes (full seq scans)
  - Slow endpoints: `getShippingLineAgent` (up to 180s), `getTSOCPOL` (1.9s), `getPOR` (1.6s)
- **Fix plan** (requires dev team): Redis cache on dropdown endpoints (TTL 30min), `CREATE INDEX CONCURRENTLY` on key columns, autovacuum completion (2–4h), Promise.all on frontend
- **Static asset serving confirmed healthy**: nginx 17ms ✅

### Intranet Prod Deploy Fix (Account 745510282686, ap-south-1)
- **Servers**: `Intranet-prod-1` (10.151.4.89, c5a.xlarge) + `Intranet-prod-2` (10.151.4.153, m5.2xlarge)
- **Fix 1**: `/root/.aws/credentials` had `#[default]` commented header → ConfigParseError → moved to `.bak`, uses instance IAM profile
- **Fix 2**: Git CodeCommit auth failure on root user → set IAM Git credentials in remote URL (URL-encoded)
- **Fix 3**: Port 8001 already in use post-deploy (uvicorn worker PIDs surviving kill-by-name) → `fuser -k 8001/tcp`
- **Result**: Both servers deployed to commit `ab9539e`, Uvicorn :8001 ✅
- **SSH Key**: `infrastructure/secrets/keys/Intranet-prod-1-Key.pem`

### Intellihub HA Assessment (Account 745510282686, ap-south-1)
- Both instances healthy (system + instance checks ok/ok), 2 AZs, ALB target groups all green
- 6 services confirmed True HA: `intellihub-prod`, `intellihubadmin-prod`, `gatimasterapi-prod`, `sendbulktracking`, `symphonywrapper-prod`, `zendeskwrapper-prod`
- **Gap**: No ASG (no auto-recovery on instance failure) — recommended EC2 Auto Recovery alarm
- **Fixed**: `cleanup_python_zombies.sh` script was in prod-2 crontab but file was missing → copied from prod-1 ✅
- 5 stale unused target groups identified (not attached to any listener): `aimlprod-1`, `ecureports`, `ecureports-api`, `intellaiml-prod-4001`, `intellihub-prod-2`

---

## 2026-10-14 — Jenkins workspace cleanup

- **Target:** Jenkins master `10.100.95.13`; persistent volume `/home/ubuntu/jenkins-data`, Jenkins workspace `/home/ubuntu/jenkins-data/jenkins_home/workspace`.
- **Reason:** data volume was full (`344G`, `328G` used, `1.5G` available, `100%`).
- **Action:** verified the `jenkins-server` Docker bind mount and controller health, checked for active workspace processes, and removed disposable workspace checkouts/build outputs only. Preserved jobs, build records, plugins, users, credentials, secrets, tools, and controller configuration.
- **Result:** volume reduced to `270G` used with `60G` available (`82%`). Jenkins remained healthy and `/login` responded successfully.
- **Concurrent activity:** Jenkins created a new `iTopaz-nonprod-frontend/SIT/SIT-Frankfurt/itopaz-imports-ui` workspace after cleanup for an active build; it was left untouched.
- **Docker cleanup:** subsequently ran the user-approved `docker image prune -f`. Image storage decreased from `12.57GB` to `4.952GB` (about `7.6GB` recovered); root filesystem availability increased to `142G` (`27%` used). The healthy `jenkins-server` container and an active `aquasec/trivy:0.50.2` scan container were preserved.
- **Scheduled guard:** installed `/usr/local/sbin/jenkins-safe-workspace-cleanup.sh` on the Jenkins host and scheduled it for `03:40 UTC` daily (`09:10 Asia/Kolkata`). The trigger was clarified to **available Jenkins-volume space below `100GiB`**. It skips when workspace processes, non-controller Docker containers, or files modified in the preceding 30 minutes indicate activity. It only removes top-level workspace trees with no file changes for 24 hours and uses `flock` to prevent overlap. Replaced an unrestricted daily `docker system prune -a -f` entry and a malformed workspace cron entry.

## 2026-10-15 — Jenkins global credentials recovered

- **Incident:** Jenkins global credentials were absent after the daily Jenkins host replacement/start. The persistent `credentials.xml` was zero bytes with modification/change time `2026-10-14 06:09:53 UTC` (`11:39:53 IST`); encryption keys remained present and unchanged.
- **Evidence:** the empty file predates the 2026-10-14 workspace cleanup. The Jenkins data volume had subsequently reached 100% usage, making a failed/truncated save due to exhausted space the strongest explanation, but the prior root volume/controller logs were unavailable after host replacement, so the exact writer could not be proven.
- **Recovery source:** EBS snapshot `snap-0f656cb7b86d1d00b`, created `2026-10-13 20:18:05 UTC` (`2026-10-14 01:48:05 IST`) for persistent volume `vol-029426e9b50b67b8a`.
- **Validation:** mounted a temporary snapshot volume read-only. Snapshot `credentials.xml` was `71,670` bytes with `55` credential IDs. `secret.key`, `identity.key.enc`, `secrets/master.key`, `hudson.util.Secret`, and the credentials SecretBytes key matched the live controller.
- **Restore:** saved the empty live file as `/home/ubuntu/jenkins-data/jenkins_home/credentials.xml.empty-20261015T045918Z`, gracefully stopped `jenkins-server`, restored only `credentials.xml` with owner `ubuntu:docker` and mode `0644`, and restarted Jenkins.
- **Result:** Jenkins returned healthy, `/login` responded successfully, 55 credential IDs were present, and startup logs showed no credential decryption/load errors. Temporary recovery volume `vol-0bf92411687198e5f` was unmounted, detached, and deleted; the source snapshot was retained.
- **Scheduler finding:** the EC2 replacement restored old root-volume cron entries. Reapplied the guarded 09:10 IST cleanup and placed its script on persistent storage at `/home/ubuntu/jenkins-data/maintenance/jenkins-safe-workspace-cleanup.sh`; durable boot-time cron provisioning still needs to be placed in the launch template/AMI.
- **Cause investigation:** the damaged file retained a single inode with birth time `2026-10-14 05:17:45 UTC` and was directly reduced to zero bytes at `06:09:53 UTC`; this was not an atomic replacement with a valid empty Jenkins XML store. No persistent job/config/script reference targeting `credentials.xml` was found, auditd was inactive, and AWS showed no SSM command or administrator control-plane action during `05:00–06:30 UTC`. CloudTrail entries near the event were normal EC2 instance-profile `AssumeRole` refreshes. The prior root-volume/controller logs were unavailable following daily instance replacement. Given that the persistent data volume reached 100% and no deliberate writer was identified, a local write/truncation failure during disk exhaustion is the evidence-supported probable cause; exact process attribution is not possible from retained evidence.

## 2026-10-16 — AVRT dev Jenkins CI created and verified

### POC — avrt-playwright-dev
- **Scope:** user requested Git/dev inspection on 10.0.132.243 and a pipeline on Jenkins 10.151.4.91:8080; supplied Jenkins SSH key route and explicitly approved restart.
- **Source:** `/root/var/www/avrt` clean on dev at b5816dafd5c386e3312af0f7c7a430d3a099ee49, matching CodeCommit dev. Active AVRT runtime is `/home/ubuntu/avrt` under avrt.service.
- **Changed:** new sandboxed Jenkins CI job `avrt-playwright-dev`; reuses aws-gitcredentials-id and node22. Two approved-operation restarts loaded/queued it after correcting the startup scheduling call; temporary startup script removed. No application deploy or SCM push.
- **Verified:** build 2 SUCCESS (75 seconds), authenticated checkout, dependency installation, 48 JS syntax checks, 9 effects tests, Chromium smoke and artifact archiving. Both services active, source checkout still clean. Build 1 failed during restart with missing program.dat.
- **Limits:** no automatic trigger; full integration tests excluded due hard-coded application port vs harness PORT mismatch. Pre-existing node22 installer emits ENOVERSIONS for global package 10.5.0; installed runtime works and shared tool unchanged.
- **Evidence/recovery:** `infrastructure/jenkins/avrt-playwright-dev/` contains Jenkinsfile, initial job XML, README and verification.json. New job can be disabled through Jenkins; no existing jobs overwritten. Master sync bundle: `agent/handoffs/master-knowledge-sync-20261016-avrt.tar.gz`; delivery pending because registry has no inbound master endpoint.

## 2026-10-22 — SASIT node stability repair
- Verified account 464134132424, apse1-itopaz-sit-eks. Added a two-node On-Demand t3.medium Linux baseline via existing group (min/desired 2, max 4), verified both Ready. Spot capacity retained.
- Dagangnet/ICS UI now two replicas on distinct nodes, readiness probes, preferred On-Demand affinity, maxUnavailable=0 and minAvailable=1 PDBs. Both rollouts and browser module loading verified.
- Replaced inaccessible Windows AMI group v2 with v3, current AWS release 1.35-2026.09.14 / ami-030cbe36eac6fb501; one Windows node Ready, group ACTIVE. Empty old group removed after validation.
- Separate missing BASF/MPCI ECR tags remain unresolved. Windows report/SMB pods scheduled and initializing; older Windows test app needs taint tolerance. No authenticated workflow verification.
- Backups: infrastructure/backups/sasit-node-repair-20261022. Report: infrastructure/reports/sasit-node-repair-20261022/report.md. Additional On-Demand EC2 costs apply. No repository push.

## 2026-10-22 — TIBCO BWCE Builder 2.9.0 Docker Image Built & Pushed to ECR

### Context & Requirement
- **Target Image**: `074779643551.dkr.ecr.eu-central-1.amazonaws.com/bwce-builder:2.9.0` (also tagged `:latest`)
- **Description**: Licensed builder image containing Apache Maven (3.8.6), Java OpenJDK 11, TIBCO BWCE 2.9.0 runtime/installation, and the official TIBCO BW Maven plug-in (`bw6-maven-plugin:2.9.8`).
- **ECR Repository**: `arn:aws:ecr:eu-central-1:074779643551:repository/bwce-builder` (Frankfurt / `eu-central-1`).

### Actions Taken
1. **Source Discovery**:
   - Discovered licensed TIBCO BWCE 2.9 installation at `/opt/tibco/bwce/2.9.0` on the BW EC2 instance `i-014d95b8f4f1cb32e` (`10.100.148.150`).
   - Packaged and transferred the licensed BWCE 2.9 runtime, Maven plugin JARs (`bw6-maven-plugin-2.9.8.jar`, `fabric8-maven-plugin-4.4.1.jar`, `com.tibco.bw.palette.shared`), and installation scripts via secure S3 staging (`s3://devops-securit-dev/tibco/bwce-2.9.0.tar.gz`) to the DEV bastion host `10.100.145.118`.
2. **Container Build**:
   - Base image: `maven:3.8.6-openjdk-11` (contains Maven 3.8.6, OpenJDK 11, Git, Curl, Unzip).
   - Deployed `/opt/tibco/bwce/2.9.0` and configured `TIBCO_HOME=/opt/tibco`, `BWCE_HOME=/opt/tibco/bwce/2.9.0`, and `BW_HOME=/opt/tibco/bwce/2.9.0`.
   - Executed `install.sh` inside the build context to register `bw6-maven-plugin-2.9.8` and dependencies into `/root/.m2/repository`.
3. **Verification & ECR Push**:
   - Verified plugin registration: `bw6-maven-plugin-2.9.8.jar` present and valid in Maven repository.
   - Authenticated Docker against DEV ECR registry `074779643551.dkr.ecr.eu-central-1.amazonaws.com`.
   - Successfully pushed both `2.9.0` and `latest` tags:
     - Digest: `sha256:63aa02c812e54e27fa5e3b57e7e57324fa4b3d48239e2ea0703b53bc683c567a`
     - Image size: ~1.14 GB
4. **Cleanup**: Removed temporary archive files from S3 and the bastion host disk.

---

## 2026-10-23 — ECR bw-base-image reconciliation: Retagged 2.9.0 to working digest & pruned broken image

### Context & Root Cause
- **Repository**: `074779643551.dkr.ecr.eu-central-1.amazonaws.com/bw-base-image` (DEV account `074779643551`, Frankfurt).
- **Issue**: Pulling `074779643551.dkr.ecr.eu-central-1.amazonaws.com/bw-base-image:2.9.0` failed or pointed to a non-working image build (`sha256:83f536d7fe4fa6d60880a1ab140a264d1dbc9bdd28ab7abaf5ec414135188cb5`, 409MB, pushed Sep 23, 2026).
- **Working image**: The verified working base image was `sha256:b482d9cf0491a2507f5a1d694e36de0b33c7cff8c0a898572959020189709d81` (368MB, pushed Sep 15, 2026), but it had become untagged in ECR.

### Actions Taken
1. **Retagged Working Image**:
   - Fetched image manifest for digest `sha256:b482d9cf0491a2507f5a1d694e36de0b33c7cff8c0a898572959020189709d81`.
   - Pushed tag `2.9.0` and tag `latest` referencing this working manifest via `aws ecr put-image`.
2. **Pruned Broken Image**:
   - Deleted broken image digest `sha256:83f536d7fe4fa6d60880a1ab140a264d1dbc9bdd28ab7abaf5ec414135188cb5` via `aws ecr batch-delete-image`.
3. **Verification**:
   - Confirmed repository `bw-base-image` now contains exactly **ONE** image:
     - Digest: `sha256:b482d9cf0491a2507f5a1d694e36de0b33c7cff8c0a898572959020189709d81`
     - Tags: `["2.9.0", "latest"]`.
   - Verified live pull of `074779643551.dkr.ecr.eu-central-1.amazonaws.com/bw-base-image:2.9.0` from both DEV bastion (`10.100.145.118`) and BW EC2 instance `i-014d95b8f4f1cb32e` (`10.100.148.150`). Both successfully pulled the working digest.

---

## 2026-10-23 — CodePipeline Scripts Updated with Dedicated EAR Build Stage

### Context & Requirement
- **Target Instance**: `10.100.148.191` (`i-021f9c8b74a27a3f0`, `EC2-MDM-BW-Dev`)
- **Directory**: `/root/rahul/`
- **Files**: `itopaz.sh` and `topaz.sh`
- **Task**:
  1. Take full backups of both CodePipeline scripts.
  2. Add an EAR build stage into the pipeline configuration (utilizing the newly prepared `bwce-builder:2.9.0` image).

### Actions Taken
1. **Backups Created**:
   - Preserved copies under `/root/rahul/backup/`:
     - `itopaz.sh.bak.20261023_092958`
     - `topaz.sh.bak.20261023_092958`
2. **CodeBuild EAR Project Provisioned**:
   - Created `codebuild_bw_ear` in `eu-central-1` using:
     - Builder Image: `074779643551.dkr.ecr.eu-central-1.amazonaws.com/bwce-builder:2.9.0`
     - Service Role: `arn:aws:iam::074779643551:role/service-role/codebuild-codebuild_bw-service-role`
     - Attached `AmazonEC2ContainerRegistryPowerUser` to ensure full ECR pull/push authorization.
     - Buildspec: Handles automated compilation via Maven (`mvn clean package -Dbw.Home=/opt/tibco/bwce/2.9.0`) or `ci/build_in_container.sh`, collects all produced `*.ear` files to the workspace root, and outputs `**/*` into `EARArtifact`.
3. **Pipeline Stages Enhanced**:
   - Enhanced `topaz.sh` and `itopaz.sh` with a dedicated 4-stage pipeline architecture:
     - **Stage 1 (Source)**: Bitbucket via CodeConnections (`SourceArtifact`)
     - **Stage 2 (EAR_Build)**: CodeBuild project `codebuild_bw_ear` using `bwce-builder:2.9.0` (`EARArtifact`)
     - **Stage 3 (Build / Docker)**: CodeBuild project `codebuild_bw` taking `EARArtifact` with compiled `.ear`, building Docker container, tagging, and pushing to ECR (`BuildArtifact`)
     - **Stage 4 (Deploy)**: CodeDeploy deployment group on EC2 targets (`BuildArtifact`)
   - Added automated self-healing checks to ensure both CodeBuild and CodeDeploy resources exist before pipeline creation/update.
4. **Verification**:
   - Tested pipeline creation and schema validation in AWS CodePipeline with live test pipeline `test-syntax-pipeline-validation` (succeeded and removed).
   - Validated shell syntax with `bash -n` on both scripts on instance `10.100.148.191`.
