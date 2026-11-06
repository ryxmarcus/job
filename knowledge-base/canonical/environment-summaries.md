# Dated environment summaries

Maintained: 2026-10-07 (Asia/Kolkata). These are scoped evidence summaries, not a live health feed. A review date records a document review; only a verification date records an actual check. Unknown dates remain unknown. Detailed history stays in [activity-log.md](activity-log.md); architecture stays in [KNOWLEDGE-BASE.md](../knowledge-base/KNOWLEDGE-BASE.md).

## DEV EU — Frankfurt — reviewed 2026-10-13

- **Scope:** account `074779643551`, region `eu-central-1`, cluster `euc1-itopaz-dev-eks`; monitoring and application namespaces.
- **Verified 2026-10-13:** All 34 Prefiler Dev pipelines in `prefiler-k8s-repo@dev` (`78919da`) rendered from 5 shared templates and verified (`python3 jenkins/scripts/render.py dev --check`). Added `DOWNLOAD_SONAR_REPORT` parameter, automated SonarQube issue extraction (`sonar-report.html` interactive dashboard + `sonar-issues.csv`), and artifact archiving.
- **Verified 2026-10-13:** DEV CloudFront distribution `E3SARNGL2XBPRD` is Deployed with `itariff-security-header-policy` (`fbe99d16-6afd-4546-b27b-7b6b32530421`), copied exactly from SIT. Live headers were observed on HTTP 502; investigate origin/application health separately if needed. See the 2026-10-13 activity entry and `infrastructure/cloudfront/dev/`.
- **Evidence status:** live monitoring checks performed during the 2026-10-07 dashboard task; not a full environment audit.
- **Verified 2026-10-07:** Grafana and Prometheus were running. The new dashboard was saved as version 2; all 21 PromQL queries passed, and Grafana returned 75 frames for the P95 query.
- **Completed:** [DEV health dashboard](https://grafana.internaleu1dev-itopaz.com/d/dev-health-service-db) provides service HTTP latency, Kubernetes health, and configured Aurora panels. Reusable artifacts and validation are in [monitoring/dev/README.md](monitoring/dev/README.md).
- **Pending:** database panels cannot load because Grafana's AWS identity lacks CloudWatch read access. The user chose to leave them pending; a later approval request remains unanswered. No IAM change or Grafana restart was performed.
- **Limit:** database panels measure I/O latency; per-service SQL execution timing is not collected. Idle/uninstrumented services may have no HTTP latency observations.
- **Next verification:** check datasource health and saved dashboard before diagnosing new failures; seek explicit approval before the previously declined IAM/restart action.

## SIT EU — Frankfurt — reviewed 2026-10-13

- **Latest verification 2026-10-13:** EU Prefiler origin security ConfigMap active; dedicated CDN policy deployed. Direct CloudFront login 200, sensitive files 403, HTTPS redirects verified. Workbook now 61/80 resolved, 19 open (18 Angular version rows + permissive CSP). Prior 53/27 entry below describes the pre-remediation check. Evidence: `security-reviews/2026-10-13/eu-after-remediation/REPORT.md`.

- **Verified 2026-10-13:** WAS recheck found 53 missing-header rows resolved, 9 other findings still reproducible, and Angular 16.2.12 in the shared UI bundle (18 version findings still open; applicability unverified). Evidence: `security-reviews/2026-10-13/REPORT.md`. Public Git/build/config exposure and insecure redirects remain.

- **Scope:** account `464134132424`, region `eu-central-1`, cluster `euc1-itopaz-sit-eks`; Prefiler API/BFF.
- **Evidence status:** source-reported results dated 2026-10-07, not independently rechecked while writing this summary.
- **Source-reported verification 2026-10-07:** 15 Prefiler deployments rolled out with two ready containers and zero restarts after migration to Kubernetes Secret references.
- **Completed in source:** commit `e903f8b`, removal of plaintext values from ConfigMaps, Secret references in deployments, and standardized SIT Redis configuration.
- **Evidence:** [activity-log.md](activity-log.md), heading “2026-10-07 — Prefiler SIT Singapore …”, subsection “2. Prefiler SIT EU … Secrets Migration”. Search `e903f8b` for the current location.
- **Pending/unknown:** this entry establishes the recorded rollout result, not current health of every SIT EU service.
- **Next verification:** inspect deployment readiness, image revisions, and application behavior in the exact cluster before further operational changes.

## SIT Singapore — reviewed 2026-10-13

- **Verified 2026-10-13:** Singapore Prefiler origin login 200; disclosed Git/build/config paths denied; HTTPS root redirects and security headers active. Dedicated CDN policy deployed. 61/80 EU-workbook-equivalent rows resolved, 19 open (Angular/CSP). CloudFront edge still returns 502 because the internal NLB is configured as a regular custom origin. Evidence: `security-reviews/2026-10-13/singapore/REPORT.md`.

- **Scope:** account `464134132424`, region `ap-southeast-1`, cluster `apse1-itopaz-sit-eks`; Prefiler UI/API/BFF.
- **Evidence status:** source-reported results dated 2026-10-07, not independently rechecked while writing this summary.
- **Source-reported verification 2026-10-07:** corrected UI served Singapore remote assets; Master API logs showed zone4/zone5 requests. Subsequent Secret migration recorded 15 API/BFF deployments ready with zero restarts.
- **Completed in source:** corrected UI image and cache invalidation, Secret migration (`3498eaa`), and missing image replication.
- **Evidence:** [activity-log.md](activity-log.md), 2026-10-07 Prefiler entry, subsections 1 and 3. Search `3498eaa` or `PageMaster`.
- **Pending/unknown:** the recorded audit identifies cross-region pipeline/frontend URL risks; the log does not establish that every affected frontend/pipeline has been permanently corrected.
- **Next verification:** confirm deployment target, build branch, frontend URLs, and CloudFront distribution together before another release.

## PROD EU — reviewed 2026-10-07

- **Scope:** account `965031587107`, region `eu-central-1`, cluster `euc1-itopaz-prd-eks` (historical inventory).
- **Evidence status:** historical reference only; no current production health check performed in this task.
- **Known dated evidence:** 2026-06-17 monitoring entry records a Grafana dashboard adjustment for missing kube-state-metrics. That absence is not a verified present-day fact.
- **Evidence:** [activity-log.md](activity-log.md), “2026-06-17 — Operations Log”, “PROD EU — Grafana K8S Dashboard Fixed”; [KNOWLEDGE-BASE.md](../knowledge-base/KNOWLEDGE-BASE.md), “PROD EU Cluster”.
- **Pending/unknown:** current cluster health, metric inventory, and later changes must be checked before action.
- **Next verification:** search later PROD entries and perform authorized read-only checks in the intended account and cluster.

## UAT — reviewed 2026-10-07

- **Scope:** account `405478414008`; documented clusters in `eu-central-1`, `ap-southeast-1`, and `us-east-1`.
- **Evidence status:** historical inventory; live verification date unknown in this summary.
- **Evidence:** [KNOWLEDGE-BASE.md](../knowledge-base/KNOWLEDGE-BASE.md), “EKS CLUSTERS” and “ACCOUNTS REFERENCE”.
- **Pending/unknown:** current readiness, schedules, and regional differences; no current health claim is made.
- **Next verification:** choose the region explicitly, check recent activity entries, and confirm account/cluster identity before operational work.

## DEVOPS (Jenkins & Multi-Cluster Jump Host) — verified 2026-10-09

- **Scope:** account `439891535362`, region `eu-central-1`, subnet `10.100.95.32/28`.
- **Verified 2026-10-09:**
  - **Worker-2 (`10.100.95.39`):** Online, reachable via `linux-server-new.pem`. Configured with multi-cluster kubeconfig (`/home/ubuntu/rahul/config`) assuming IAM role `eks-jump-access`. EKS control plane connectivity confirmed live for DEV EU (`074779643551`), SIT EU (`464134132424`), SIT SG (`464134132424`), and PROD EU (`965031587107`).
  - **Jenkins Master (`10.100.95.13`):** Online, in same subnet. SSH authentication verified as `root` via `jenkins.pem`. Docker container `jenkins-server` (`custom-jenkins:latest`) running healthy on port 8090.
- **Evidence:** [activity-log.md](activity-log.md) ("2026-10-09 — Worker-2 (10.100.95.39) multi-cluster EKS jump and Jenkins access verified"); [KNOWLEDGE-BASE.md](../knowledge-base/KNOWLEDGE-BASE.md) ("DevOps Jump Server & Multi-Cluster Host").
- **Limit:** Direct SSH from worker-2 to private bastion IPs (`10.100.145.118`, `10.100.208.17`, `10.100.98.195`) dropped due to VPC/SG boundaries; cluster administration is performed directly via AWS cross-account IAM role.

## Other accounts and environments — reviewed 2026-10-07

GATI, ECU, China, and other inventories remain in the knowledge base and activity log. They have not been audited for these summaries. Add a scoped summary when work occurs there, using the same evidence and date fields; do not infer health from document modification time.

## SIT China — Prefiler — reviewed 2026-10-13

- **Scope:** `https://prefiler-sit.ecuworldwide.cn`; eleven read-only application paths checked by worker-1 on 2026-10-13 (Asia/Kolkata). Azure management portal/control plane was not accessed; serving resource identity remains unverified.
- **Verified 2026-10-13:** login HTTP 200 and SAMEORIGIN frame protection; HSTS, nosniff, CSP and Cache-Control missing on login. Root redirect includes an HTTP login hop. Git config/index, Gitignore, Dockerfile, package-lock.json and nginx.conf exposed with HTTP 200; `.htaccess` denied with HTTP 403. Shared UI bundle contains Angular 16.2.12.
- **Evidence:** [China report](../security-reviews/2026-10-13/china-sit/REPORT.md), [HTTP evidence](../security-reviews/2026-10-13/china-sit/evidence.json), [Angular evidence](../security-reviews/2026-10-13/china-sit/angular-version.json).
- **Pending/limits:** no China remediation, full browser workflow verification or WAS rerun. Angular CVE applicability needs package/feature checks. EU/Singapore resolution counts do not apply.
- **Next work:** confirm authorization and serving Azure resources, back up configuration, remediate disclosure/headers/redirects and affected Angular packages, then verify browser workflows and scanner results. EU artifacts require Azure-specific adaptation.
- **Delivery:** [master handoff](../agent/handoffs/master-china-prefiler-sit-20261013.md) prepared locally, not sent; Windows master can fetch it through its existing worker SSH connection.
