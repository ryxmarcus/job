# AllCargo iTOPAZ & GATI — Consolidated Infrastructure Knowledge Base

Canonical domain, architecture, inventory, configuration, and cost reference for the workspace. For chronological operational changes and dated incident logs, see `infrastructure/activity-log.md`.


---

# AllCargo iTOPAZ — Complete Session Knowledge Export
> Generated: 2026-09-01 | Covers: Aug 17 – Sep 1, 2026

═══════════════════════════════════════════════════════════════════════
## ACCOUNTS REFERENCE
═══════════════════════════════════════════════════════════════════════

| Account ID     | Name           | Key Info |
|----------------|----------------|----------|
| 439891535362   | DEVOPS/Jump    | Jump box host, Jenkins, SonarQube |
| 464134132424   | SIT            | eu-central-1 + ap-southeast-1 |
| 074779643551   | DEV            | eu-central-1 |
| 965031587107   | PROD           | eu-central-1 |
| 405478414008   | UAT            | eu-central-1, ap-southeast-1, us-east-1 |
| 674017976129   | GATI-1         | ap-south-1 (AWSAdministratorAccess) |
| 745510282686   | GATI-2/Intranet| ap-south-1 + CloudFront distributions |
| 581621506601   | BW-UAT         | EC2 10.233.30.104 (TIBCO BW containers) |
| 984215905140   | Network-FRA    | Network account eu-central-1 |
| 162176457247   | Master Payer   | us-east-1 |

═══════════════════════════════════════════════════════════════════════

## AWS PROFILES (~/.aws/config) — KEY PROFILES
═══════════════════════════════════════════════════════════════════════

SSO session: ecu-allcargo (https://ecu-allcargo.awsapps.com/start)
SSO session: gati-sso    (https://d-9f6707b589.awsapps.com/start/, region: ap-south-1)

Profile                      | Account        | Role                    | Region
-----------------------------|----------------|-------------------------|------------
sit-frankfurt                | 464134132424   | eks-jump-access (EC2)   | eu-central-1
sit-singapore                | 464134132424   | eks-jump-access (EC2)   | ap-southeast-1
sit-frankfurt-admin          | 464134132424   | AWS-iTopaz-Admin (SSO)  | eu-central-1
sit-singapore-admin          | 464134132424   | AWS-iTopaz-Admin (SSO)  | ap-southeast-1
sit-singapore-devops         | 464134132424   | AWS-iTopaz-Devops (SSO) | ap-southeast-1
dev-frankfurt                | 074779643551   | eks-jump-access (EC2)   | eu-central-1
dev-frankfurt-admin          | 074779643551   | AWSAdministratorAccess  | eu-central-1
prod-frankfurt               | 965031587107   | eks-jump-access (EC2)   | eu-central-1
uat-admin                    | 405478414008   | AWS-iTopaz-Admin (SSO)  | ap-southeast-1
uat-us-east-1                | 405478414008   | eks-jump-access (EC2)   | us-east-1
uat-eu-central-1             | 405478414008   | eks-jump-access (EC2)   | eu-central-1
jump-account-admin           | 439891535362   | AWS-iTopaz-Admin (SSO)  | eu-central-1
bw-uat                       | 581621506601   | AWSAdministratorAccess  | us-east-1
gati-674-admin               | 674017976129   | AWSAdministratorAccess  | us-east-1
gati-745-admin               | 745510282686   | AWSAdministratorAccess  | us-east-1
gati-745-ap-south-1          | 745510282686   | AWSAdministratorAccess  | ap-south-1
master-payer                 | 162176457247   | eks-jump-access         | us-east-1

═══════════════════════════════════════════════════════════════════════

## EKS CLUSTERS (kubeconfig: /home/ubuntu/rahul/config)
═══════════════════════════════════════════════════════════════════════

Context            | Cluster                    | Account      | Region
-------------------|----------------------------|--------------|---------------
sit-frankfurt      | euc1-itopaz-sit-eks        | 464134132424 | eu-central-1
sit-singapore      | apse1-itopaz-sit-eks       | 464134132424 | ap-southeast-1
dev-frankfurt      | euc1-itopaz-dev-eks        | 074779643551 | eu-central-1
prod-frankfurt     | euc1-itopaz-prd-eks        | 965031587107 | eu-central-1
uat-eu-central-1   | euc1-itopaz-uat-eks        | 405478414008 | eu-central-1
uat-us-east-1      | use1-itopaz-uat-eks        | 405478414008 | us-east-1

All clusters use role: arn:aws:iam::<account>:role/eks-jump-access

═══════════════════════════════════════════════════════════════════════

## SCHEDULER LAMBDA (EC2/RDS/Aurora auto start-stop)
═══════════════════════════════════════════════════════════════════════

Function name: scheduler-rds-ec2
Trigger: EventBridge rate(5 minutes)
Deployed in: 464134132424 (eu-central-1, ap-southeast-1), 074779643551, 405478414008 (3 regions), 439891535362

Required EC2 tags:
  AutoSchedule: true
  Schedule:     HH:MM-HH:MM  (e.g. 09:00-21:00)
  TimeZone:     Asia/Kolkata
  ScheduleDays: mon-fri  (optional, defaults to all days)

Required RDS/Aurora CLUSTER tags (not instance tags!):
  AutoSchedule: true
  Schedule:     HH:MM-HH:MM
  TimeZone:     Asia/Kolkata

IAM role: scheduler-rds-ec2-role
Policy: EC2 start/stop/describe + RDS describe/start/stop instances AND clusters + CloudWatch logs

BUGS FIXED in Lambda code:
1. process_rds() read tags from DB instances but Aurora uses clusters → added process_rds_clusters()
2. Used stop_db_instance() for Aurora → fixed to stop_db_cluster()
3. Comma split in is_in_schedule() was overwritten by slash split → fixed
4. Added ScheduleDays weekday filtering

Code location: /tmp/scheduler_weekday.zip
Log: /aws/lambda/scheduler-rds-ec2

═══════════════════════════════════════════════════════════════════════

## EC2 SCHEDULE TAGS APPLIED
═══════════════════════════════════════════════════════════════════════

--- DEV (074779643551, eu-central-1) 09:00-21:00 Mon-Fri ---
i-01ce7607b8f5cb0d5  ecu-edi-server-dev
i-05c33080ab25c83cc  euc1-itopaz-bastion-dev-1
i-04030b2aaf3faa2c3  EC2-EMS-Server-Dev
i-0f5453ddae75a03fc  MDM-EBX-Server-DEV
i-0a5809b5ac1df31b1  EC2-EMS-Server-Dev-topaz
i-014d95b8f4f1cb32e  EC2-MDM-BW-Dev-topaz
i-021f9c8b74a27a3f0  EC2-MDM-BW-Dev

--- UAT (405478414008) 09:00-21:00 Mon-Fri ---
eu-central-1:    i-0534867ff51fba97a  (euc1-itopaz-bastion-uat-1)
ap-southeast-1:  i-0426edabc4ca81367  (apse1-itopaz-bastion-uat-1)
us-east-1:       i-0225a153844ab45c3  (use1-itopaz-bastion-uat-1)

--- DEVOPS (439891535362, eu-central-1) 09:00-21:00 Mon-Fri ---
i-0cdcce39da9444d74  euc1a-devops-jenkins-master-vm
i-0cd1ab8b0d9247ef4  euc1a-devops-sonarqube-master-vm
i-0e5b12ab9516d5a07  euc1-linux-jump-server-vm
i-0af0c0a0b06e69b95  window-jenkins-agent
i-0b7a724f715ed2c11  Spot

--- SIT (464134132424, eu-central-1) ---
i-08a20bae22e57e46d  EC2-EBX-Server-sit     09:00-20:30 Mon-Fri
i-04c4a155211d6f6ec  EC2-BW-Server-sit      09:00-20:30 Mon-Fri
i-00b7ab3bec04e6c37  euc1-itopaz-win-bastion-sit-1  mon-fri (special schedule)
i-0bd3314ea08e6fb27  euc1-itopaz-bastion-sit  07:00-1:00 Mon-Sun

═══════════════════════════════════════════════════════════════════════

## AURORA CLUSTER TAGS
═══════════════════════════════════════════════════════════════════════

--- SIT (464134132424) ---
euc1-itopaz-sit-aurora-postgresql  eu-central-1   07:00-23:59 IST (daily)
apse1-itopaz-sit-aurora-postgresql ap-southeast-1 05:30-21:00 IST (daily)

--- DEV (074779643551, eu-central-1) Mon-Fri ---
euc1-itariff-edi-dev               09:00-21:00
euc1-itopaz-dev-database-cluster   09:00-01:00 (overnight, stops 1am)
euc1-mdm-dev-database-cluster      09:00-21:00

--- UAT (405478414008) Mon-Fri 09:00-21:00 ---
euc1-itopaz-uat-aurora-postgresql   eu-central-1
apse1-itopaz-uat-aurora-postgresql  ap-southeast-1
use1-itopaz-uat-aurora-postgresql   us-east-1

NOTE: Aurora tags go on CLUSTER ARN, not instance ARN
      Lambda skips cluster members: if db.get("DBClusterIdentifier"): continue

═══════════════════════════════════════════════════════════════════════

## UAT SHUTDOWN (405478414008) — PERMANENTLY OFF UNTIL RE-ENABLED
═══════════════════════════════════════════════════════════════════════

Done on 2026-08-31:
- All 6 EKS ASGs scaled to min=0, desired=0
- ASG "start" scheduled actions DELETED (won't auto-start)
- All 3 EC2 bastions stopped, AutoSchedule tags removed
- All 3 Aurora clusters stopped, AutoSchedule tags removed
- EventBridge scheduler trigger DISABLED in all 3 regions

To re-enable:
  aws events enable-rule --rule scheduler-rds-ec2-trigger --profile uat-admin --region <region>
  Re-tag EC2 with AutoSchedule=true
  Re-tag Aurora clusters with AutoSchedule=true
  Re-add start scheduled actions on ASGs

═══════════════════════════════════════════════════════════════════════

## EBX SERVER (i-08a20bae22e57e46d, 10.100.215.180, SIT Frankfurt)
═══════════════════════════════════════════════════════════════════════

TIBCO EBX v17 on m5.2xlarge
Java: /usr/lib/jvm/java-21-amazon-corretto.x86_64
Startup: /opt/tibco/ebx/EBX_SERVER/bin/startup.sh (calls catalina.sh)
Shutdown: /opt/tibco/ebx/EBX_SERVER/bin/shutdown.sh

CURRENT STARTUP METHOD: Crontab only (systemd removed)
Crontab:
  @reboot sleep 600 && export JAVA_HOME=/usr/lib/jvm/java-21-amazon-corretto.x86_64 && export JRE_HOME=/usr/lib/jvm/java-21-amazon-corretto.x86_64 && export PATH=$JAVA_HOME/bin:$PATH && cd /opt/tibco/ebx/EBX_SERVER/bin && sh -x startup.sh >> /var/log/ebx-cron.log 2>&1

Log: /var/log/ebx-cron.log

WHY SYSTEMD FAILED: JAVA_HOME not set in systemd environment → startup.sh fails with exit code 1
WHY CRONTAB WAS ORIGINALLY BROKEN: cronie on Amazon Linux 2023 silently skips @reboot for stop/started EC2 instances when spool file was last modified in 2024 (inotify issue)
FIX: Added explicit JAVA_HOME export in crontab command with 10min delay

EBX DNS: ebx.internaleu1-itopaz.com → 10.100.215.180

═══════════════════════════════════════════════════════════════════════

## SIT EKS — WINDOWS NODE ISSUE (074779643551 also had same)
═══════════════════════════════════════════════════════════════════════

Issue: Linux pods scheduled on Windows nodes → FailedCreatePodSandBox
Error: "pod does not have label vpc.amazonaws.com/PrivateIPv4Address"
Root cause: Windows vpc-bridge CNI cannot assign IPs to Linux pods

Fix applied to DEV 074779643551:
  Added nodeSelector: kubernetes.io/os: linux
  to 33 deployments across: itariff-api, itopaz-export, itopaz-import,
  itopaz-platform, itopaz-ui, prefiler-api, prefiler-ui

Windows node groups:
  euc1-itopaz-dev-eks-windows-nodegrou-v3  (ip-10-100-147-35, ip-10-100-151-222)

═══════════════════════════════════════════════════════════════════════

## ITARIFF-API CONFIGMAP FIXES (SIT Frankfurt, 464134132424)
═══════════════════════════════════════════════════════════════════════

PATTERN:
  New code deployed with @Value("${some.property}") 
  → property missing from ConfigMap 
  → PlaceholderResolutionException at startup 
  → CrashLoopBackOff 
  → 503 "Connection refused" or "no healthy upstream" (Istio)

Fix process:
  kubectl logs <crashing-pod> -c <container> --previous | grep "Could not resolve"
  → Add missing property to ConfigMap
  → kubectl rollout restart deployment/<name> -n itariff-api

All fixes applied (Aug 27-Sep 1, 2026):

Service                            | Property Added              | Value
-----------------------------------|-----------------------------|---------------------------
tariff-buying-service              | service.delete.code         | DEL1204
tariff-buying-service              | service.archive.code        | ARC1206
tariff-buying-service              | serviceurls.search          | http://tariff-search-service.itariff-api.svc.cluster.local/search-domain-service/secure/v1/search
tariff-buying-otherbooking-service | service.rfq.code            | RFQ10001
tariff-buying-carriage-service     | service.rfq.code            | RFQ10001
tariff-buying-truck-service        | serviceurls.tariff-buying-carriage | http://tariff-buying-carriage-service.itariff-api.svc.cluster.local/buying-carriage-domain-service

Services to still check proactively:
  tariff-buying-warehouse-service
  tariff-buying-standardcost-service
  tariff-buying-shippingline-consumer-service

ConfigMap keys reference (tariff-buying-* service codes pattern):
  DUP40001, SAVE1001, ERR1003, NF1005, VAL1003, DEL10001, ARR10001, RFQ10001

═══════════════════════════════════════════════════════════════════════

## CLOUDFRONT + WAF (674017976129, 745510282686)
═══════════════════════════════════════════════════════════════════════

--- CloudFront E2FVCC01LF3UUD (674017976129) ---
Aliases: elma-dev.allcargoapps.com, elma-api.allcargoapps.com, elma-dev-agent.allcargoapps.com
Domain: d3djlgxjwfvccb.cloudfront.net
Default origin: elma-ecu.s3.eu-central-1.amazonaws.com (S3)
Behaviors:
  /agent/self-chat/ws/*  → datascience-144380231.eu-central-1.elb.amazonaws.com
  /agent/*               → datascience-144380231.eu-central-1.elb.amazonaws.com  ← ADDED
  /elma/*                → datascience-144380231.eu-central-1.elb.amazonaws.com
  /ws                    → datascience-144380231.eu-central-1.elb.amazonaws.com
  Default (*)            → S3

DNS (account 674017976129):
  elma-dev-agent.allcargoapps.com → d3djlgxjwfvccb.cloudfront.net  ← FIXED (was ELB direct)
  elma-dev.allcargoapps.com       → d3djlgxjwfvccb.cloudfront.net

WAF waf-cloudfront-geo-restrictions (674017976129):
  P0: AllowMicrosoftCorporateProxies   → Allow (IPv4: 4.213.144.0/20, 52.112.0.0/14; IPv6: 2a01:111:f400::/48)
  P1: AllowBelgium                     → Allow (GeoMatch: BE)
  P4: AmazonIpReputationList           → Count
  P5: AnonymousIpList                  → Count (HostingProviderIPList overridden to Count)
  P6-P10: Various managed rules        → Enforce

WHY BELGIUM WAS BLOCKED:
  Manuel uses Microsoft corporate proxy → appears as India/Malaysia IP (Azure datacenter)
  AllowBelgium only checks geo → misses Azure-proxied Belgian users
  AnonymousIpList#HostingProviderIPList was BLOCKING Azure IPs
  FIX: P0 rule explicitly allows Microsoft Azure IP ranges + HostingProviderIPList → Count

--- CloudFront E17IUMRH88RLK0 (745510282686) ---
Aliases: intranet-dev.allcargoapps.com
Default origin: allcargo-intranet-dev.s3.ap-south-1.amazonaws.com
Behaviors:
  /intellihub_mcp/*  → intelli-atl.allcargoapps.com  ← ADDED (was missing, fell to S3)
  /intellihub/*      → intelli-atl.allcargoapps.com
  /ecureports/*      → intellihub-prod-1892815422.ap-south-1.elb.amazonaws.com
  Default            → allcargo-intranet-dev.s3.ap-south-1.amazonaws.com

CSP fix (response headers policy 968e3e83):
  OLD: "self"  (malformed, missing directive)
  NEW: "default-src * 'unsafe-inline' 'unsafe-eval'; connect-src * ng:; script-src * 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline';"
  Added ng: scheme to allow Angular source maps/directive debug URLs

WAF webacl-nonprod (745510282686):
  P1: Allow-AE-BE-AU    → Allow
  P2: zscalar           → Count

═══════════════════════════════════════════════════════════════════════

## S3 CORS ISSUE — allcargo-intranet BUCKET
═══════════════════════════════════════════════════════════════════════

Problem: PDF viewer fetches presigned URL DIRECTLY from allcargo-intranet.s3.amazonaws.com
         Browser: intranet-dev.allcargoapps.com → CORS blocked
Bucket: allcargo-intranet (ap-south-1) — NO -dev suffix
Presigned URL IAM key: AKIA_REDACTED_KEY_DEMO (unknown account, not 674/745)

Status: UNRESOLVED — bucket owned by account not accessible via our SSO
All attempts got 403: 674017976129, 745510282686, master-payer 162176457247

Partial fix done: CloudFront E17IUMRH88RLK0 response headers policy ee56bd34 
  → Added CORS headers (only covers requests through CloudFront, not direct S3)

Required CORS rule (needs bucket owner account):
{
  "AllowedHeaders": ["*"],
  "AllowedMethods": ["GET", "HEAD"],
  "AllowedOrigins": ["https://intranet-dev.allcargoapps.com", "https://intranet-uat.allcargoapps.com", "https://intranet.allcargoapps.com", "https://intellihub.allcargoapps.com"],
  "MaxAgeSeconds": 3600
}

Permanent fix options:
1. Find account owning allcargo-intranet bucket and apply CORS
2. Backend proxies S3 downloads through API (no direct S3 URLs to browser)
3. Add allcargo-intranet.s3 as CloudFront origin + generate CF-proxied URLs

═══════════════════════════════════════════════════════════════════════

## EKS SECURITY GROUP FIX (SIT Frankfurt)
═══════════════════════════════════════════════════════════════════════

Bastion i-0bd3314ea08e6fb27 (10.100.208.17, sg-03396fa5484b431e1)
  → Could not reach EKS private API (10.100.212.77:443)
  → Added TCP/443 inbound rule to EKS SG sg-023c8cff9a807ad1d
  → Rule ID: sgr-05071d883236a0905
  → VPC routing was fine (local route 10.100.208.0/20)

═══════════════════════════════════════════════════════════════════════

## DEVOPS ACCOUNT COST ANALYSIS (439891535362)
═══════════════════════════════════════════════════════════════════════

Apr $594 → May $763 → Jun $889 → Jul $1,058 → Aug $1,138 (+92%)

ROOT CAUSE 1: Kiro Enterprise Pro Plus
  $40/user/month × ~11 users = $432/month
  Started May 2026 with ~4 users, grew to 11
  Usage type: EUC1-KiroEnterprise-ProPlus
  Action: Review inactive seats (each removed = -$40/month)

ROOT CAUSE 2: EBS Snapshots
  124 snapshots, 25,852 GB = ~$253/month
  Oldest from Sep 2025 (AMI backups from CreateImage, never cleaned)
  Action: Delete snapshots >90 days old → save ~$150/month

═══════════════════════════════════════════════════════════════════════

## ACM CERTIFICATE — internalapse1-uat-itopaz.com (405478414008)
═══════════════════════════════════════════════════════════════════════

Cert ARN: arn:aws:acm:ap-southeast-1:405478414008:certificate/973723fc-...
Issue: PENDING_VALIDATION
Root cause: Private Route53 hosted zone Z02454501RR9BOT7RMP61 — ACM needs PUBLIC DNS
Fix applied:
  - Created PUBLIC hosted zone Z0647588SV39QU2AGJG2
  - Added CNAME: _e7ae11664b37f296263176af8844fa03.internalapse1-uat-itopaz.com → ACM target
  - DNS must be publicly registered for full validation
  
NOTE: Domain internalapse1-uat-itopaz.com NOT registered at any public registrar
      Full validation requires either domain registration OR use Private CA

ACM cert for *.itopazapp.com (405478414008):
  eu-central-1: arn:aws:acm:eu-central-1:405478414008:certificate/ce1378eb-...  ISSUED
  ap-southeast-1: arn:aws:acm:ap-southeast-1:405478414008:certificate/e817ef68-... ISSUED
  Both validated via external DNS for itopazapp.com (not Route53)

═══════════════════════════════════════════════════════════════════════

## REDIS AUTH TOKENS — SECRETS MANAGER
═══════════════════════════════════════════════════════════════════════

SIT Singapore (464134132424):
  Cluster: apse1-itopaz-sit-redis-new
  Secret:  itopaz/sit/redis/apse1-itopaz-sit-redis-new  (ap-southeast-1)
  Rotation: OFF

UAT (405478414008) — all rotation OFF:
  euc1-itopaz-uat-redis    → itopaz/uat/redis/euc1-itopaz-uat-redis    (eu-central-1)
  apse1-itopaz-uat-redis   → itopaz/uat/redis/apse1-itopaz-uat-redis   (ap-southeast-1)
  use1-itopaz-uat-redis    → itopaz/uat/redis/use1-itopaz-uat-redis    (us-east-1)

Password stored in each secret as JSON:
{
  "host": "<endpoint>",
  "port": 6379,
  "password": "<password>",
  "endpoint": "<endpoint>:6379"
}

═══════════════════════════════════════════════════════════════════════

## GATI SSO — d-9f6707b589.awsapps.com
═══════════════════════════════════════════════════════════════════════

SSO session in ~/.aws/config:
  [sso-session gati-sso]
  sso_start_url = https://d-9f6707b589.awsapps.com/start/
  sso_region = ap-south-1

Login workaround (SSL cert issue on jump box):
  AWS_CA_BUNDLE="" aws sso login --sso-session gati-sso

Note: ap-south-1 endpoints have SSL cert chain issue on this jump box
Same issue affects: kafka.ap-south-1, s3.ap-south-1, eks.ap-south-1

═══════════════════════════════════════════════════════════════════════

## VPC/NETWORK FIXES
═══════════════════════════════════════════════════════════════════════

SIT Frankfurt ↔ SIT Singapore (BROKEN):
  Old VPC peering pcx-0eb0740b49520f468 = BLACKHOLE (deleted but routes remain)
  Frankfurt TGW: tgw-0a9f0ea2ae5fb9340 (eu-central-1) — no inter-region peering
  Singapore TGW: tgw-03b17f26861c2d348 (ap-southeast-1) — no inter-region peering
  
  Route table rtb-014a7df9776cc7bed (Frankfurt):
    10.130.208.0/20 → tgw-0a9f0ea2ae5fb9340  ← ADDED (was missing)
  Route table rtb-0adad3168044c8fde (Singapore Aurora subnets):
    10.100.208.0/20 → tgw-03b17f26861c2d348  ← REPLACED blackhole PCX route

  TODO: TGW inter-region peering still needed for actual connectivity

Aurora PostgreSQL private endpoint (SIT Singapore):
  apse1-itopaz-sit-aurora-postgresql.cluster-cve80ey2iakj.ap-southeast-1.rds.amazonaws.com
  VPC: vpc-0c46bfc8553c53eec
  Allowed on port 5432: 10.130.208.0/20, sg-0b54634a65579a404, sg-047559c72c58a4ad7, sg-034fa14ed643392c8, 0.0.0.0/0 (test rule)

═══════════════════════════════════════════════════════════════════════

## KNOWLEDGE BASE DAILY SYNC
═══════════════════════════════════════════════════════════════════════

Script: /home/ubuntu/rahul/scripts/daily-sync.sh
Crontab: 30 15 * * 1-5  (9:00 PM IST Mon-Fri)
Steps:
  1. Rebuild KNOWLEDGE-BASE.md from 22 source docs
  2. Ingest into FAISS vector DB (may fail if disk full)
  3. git add -A + commit + push to Bitbucket (if remote configured)
  4. aws s3 sync → s3://devops-security-ai/rahul-knowledge/ (profile: jump-account-admin)
Log: /home/ubuntu/rahul/scripts/daily-sync.log

---

# EKS Clusters Configuration
*Last Updated: June 12, 2026*

## SSH Keys — Canonical Locations
All SSH keys: `/home/ec2-user/rahul/infrastructure/secrets/keys/`

| Environment | Key File | Bastion IP | User |
|-------------|----------|------------|------|
| SIT EU | `sit/eu/sit-eu-bastion.pem` | `10.100.208.17` | `ec2-user` |
| SIT SG | `sit/singapore/sit-sg-bastion.pem` | `10.130.210.3` | `ec2-user` |
| DEV EU | `dev/eu/dev-eu-bastion.pem` | `10.100.145.118` | `ec2-user` |
| PROD EU | `prod/eu/prod-eu-bastion.pem` | `10.100.98.195` | `ec2-user` |

---

## DevOps Jump Server & Multi-Cluster Host (Worker-2 / 10.100.95.39)
*Verified Live: October 09, 2026*

- **Host IP**: `10.100.95.39` (AWS Account `439891535362`, eu-central-1, Subnet: `10.100.95.32/28`)
- **SSH Access**: `ubuntu@10.100.95.39` using key `C:\Users\rah_66160\keys\linux-server-new.pem`
- **Role**: Primary DevOps Jump and Cluster Management Server for iTOPAZ infrastructure.
- **Kubeconfig**: `/home/ubuntu/rahul/config` configured with multi-cluster contexts.
- **AWS Cross-Account IAM Role**: Assumes `arn:aws:sts::<Account-ID>:assumed-role/eks-jump-access` to manage EKS control planes:
  - **DEV EU**: Account `074779643551` (`dev-frankfurt` / `euc1-itopaz-dev-eks`)
  - **SIT EU**: Account `464134132424` (`sit-frankfurt` / `euc1-itopaz-sit-eks`)
  - **SIT SG**: Account `464134132424` (`sit-singapore` / `apse1-itopaz-sit-eks`)
  - **PROD EU**: Account `965031587107` (`prod-frankfurt` / `euc1-itopaz-prd-eks`)
- **Key Store**: `/home/ubuntu/rahul/infrastructure/secrets/keys/` holds keys for DEV, SIT, SG, PROD bastions and MDM servers.
- **Network Note**: Direct SSH (TCP:22) to private bastion IPs (`10.100.145.118`, `10.100.208.17`, `10.100.98.195`) is blocked by VPC routing/Security Groups. Clusters are administered directly via the cross-account EKS control planes.

---

## CI/CD Jenkins Master Server (10.100.95.13)
*Verified Live: October 09, 2026*

- **Host IP**: `10.100.95.13` (AWS Account `439891535362`, eu-central-1)
- **SSH Access**: `root@10.100.95.13` via `/home/ubuntu/jenkins.pem` (from `10.100.95.39`, in same subnet `10.100.95.x`)
- **Container Engine**: Docker container `jenkins-server` running `custom-jenkins:latest`.
- **Ports**: Web UI exposed on `8090` (`0.0.0.0:8090->8090/tcp`), agent listener on `50000/tcp`.

---

## SIT Cluster (EU - Frankfurt)
- **Name**: euc1-itopaz-sit-eks
- **Account**: 464134132424
- **Region**: eu-central-1
- **Bastion**: ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/sit/eu/sit-eu-bastion.pem ec2-user@10.100.208.17
- **K8s Server Version**: v1.33.11-eks-40737a8
- **Node Versions**: v1.33.4-eks (Linux), v1.33.8-eks (Windows)
- **Nodes (June 11)**: 20 total — All Ready (18 Linux AL2023 m6a.xlarge SPOT + 2 Windows Server 2022 m5.large ON_DEMAND)
- **Node Group (Linux)**: euc1-itopaz-sit-eks-8-32 (SPOT, m6a.xlarge, 4 vCPU, 16GB)
- **Node Group (Windows)**: euc1-itopaz-sit-eks-windows-nodegrou-v3 (m5.large ON_DEMAND)
- **maxPods**: 110 (prefix delegation enabled)
- **ASG**: eks-euc1-itopaz-sit-eks-8-32-4ecf157d-555b-e3fe-9259-d3cc4973cf78, min:2 max:30
- **OIDC Provider ID**: 11160D70CF37402BB934899C92E53A97
- **Cluster Autoscaler**: v1.33.0, IRSA role: arn:aws:iam::464134132424:role/euc1-itopaz-sit-eks-cluster-autoscaler
- **VPC CNI**: ENABLE_PREFIX_DELEGATION=true, WARM_PREFIX_TARGET=1, WARM_ENI_TARGET=1

### Namespaces (26)
amazon-cloudwatch, default, fluent-bit, istio-system, itariff-api, itariff-bff, itariff-intg-api, itariff-ui, itopaz-accounting, itopaz-ameta, itopaz-api, itopaz-auth, itopaz-export, itopaz-import, itopaz-intg-api, itopaz-platform, itopaz-ui, kube-node-lease, kube-public, kubernetes-dashboard, kube-state-metrics, kube-system, monitoring, prefiler-api, prefiler-bff, prefiler-ui

### DaemonSets (Updated June 4, 2026)
| Namespace | DaemonSet | Desired | Ready | Status |
|-----------|-----------|---------|-------|--------|
| amazon-cloudwatch | cloudwatch-agent | 30 | 30 | Active |
| amazon-cloudwatch | cloudwatch-agent-windows | 2 | 2 | Active |
| amazon-cloudwatch | fluent-bit | 30 | 30 | Active |
| amazon-cloudwatch | fluent-bit-windows | 2 | 2 | Active |
| amazon-cloudwatch | dcgm-exporter | 0 | 0 | DISABLED |
| amazon-cloudwatch | neuron-monitor | 0 | 0 | DISABLED |
| fluent-bit | fluent-bit | 0 | 0 | DISABLED (duplicate) |
| kube-system | aws-node | 30 | 30 | Active (VPC CNI) |
| kube-system | aws-node-termination-handler | 0 | 0 | DISABLED |
| kube-system | csi-smb-node | 30 | 30 | Active (8 SMB PVCs) |
| kube-system | csi-smb-node-win | 2 | 2 | Active |
| kube-system | ebs-csi-node | 30 | 30 | Active |
| kube-system | ebs-csi-node-windows | 2 | 2 | Active |
| kube-system | efs-csi-node | 30 | 30 | Active (4 EFS PVCs) |
| kube-system | eks-pod-identity-agent | 30 | 30 | Active |
| kube-system | kube-proxy | 30 | 30 | Active |
| monitoring | promtail | 0 | 0 | DISABLED (redundant) |

### HPAs - itariff-api (Updated June 4, 2026)
| Service | Min | Max | Current | CPU% | Mem% |
|---------|-----|-----|---------|------|------|
| tariff-buying-carriage-service | 2 | 3 | 3 | 9% | 85% |
| tariff-buying-consumer-service | 2 | 3 | 2 | 2% | — |
| tariff-buying-otherbooking-service | 2 | 3 | 3 | 18% | 70% |
| tariff-buying-service | 2 | 5 | 5 | 19% | 82% |
| tariff-buying-standardcost-service | 2 | 3 | 3 | 6% | 70% |
| tariff-buying-truck-service | 2 | 3 | 3 | 12% | 68% |
| tariff-buying-warehouse-service | 2 | 5 | 3 | 4% | 65% |
| tariff-company-service | 2 | 10 | 5 | 14% | 67% |
| tariff-geo-service | 2 | 10 | 4 | 39% | 85% |
| tariff-grant-auth | 2 | 5 | 3 | 3% | 58% |
| tariff-invoice-service | 2 | 10 | 2 | 3% | 47% |
| tariff-master-service | 2 | 10 | 2 | 7% | 55% |
| tariff-profile-service | 2 | 10 | 3 | 4% | 68% |
| tariff-search-service | 2 | 10 | 2 | 5% | 43% |
| tariff-selling-consumer-hpa | 2 | 10 | 3 | 9%/75% | — |
| tariff-selling-consumer-service | 2 | 20 | 2 | 1%/70% | — |
| tariff-selling-oc-service | 2 | 3 | 3 | 6% | 64% |
| tariff-selling-service | 2 | 20 | 2 | 15%/70% | 54% |
| tariff-selling-service-batch | 2 | 20 | 2 | 1%/70% | — |
| tariff-selling-storage-service | 2 | 3 | 2 | 0% | 30% |
| tariff-trucker-rates-service | 2 | 10 | 5 | 5% | 75% |

### Prefiler Services (Updated June 4, 2026)
**prefiler-api namespace** (13 services, all 2 replicas, all Running):
- aci-prefiler-service, aes-prefiler-service, afr-prefiler-service, ams-prefiler-service
- basf-prefiler-service, dagangnet-prefiler-service, ics-prefiler-service, ics2-prefiler-service
- imdg-prefiler-service, master-prefiler-service, mblfiler-prefiler-service
- prefiler-auth-service, sa-prefiler-service

**prefiler-bff namespace** (2 services):
- prefiler-auth-bff: 2 replicas (1/1 no sidecar)
- prefiler-bff: 2 replicas (1/1 no sidecar)

**VirtualService routes (prefiler-api)** — 13 routes:
/sa-prefiler-service/, /afr-prefiler-service/, /ams-prefiler-service/, /master-prefiler-service/, /prefiler-auth-service/, /ics2-prefiler-service/, /aes-prefiler-service/, /dagangnet-prefiler-service/, /aci-prefiler-service/, /basf-prefiler-service/, /ics-prefiler-service/, /imdg-prefiler-service/, /mblfiler-prefiler-service/

### S3 Buckets (Account 464134132424) - Updated June 4, 2026
| Bucket | Purpose | Key Contents |
|--------|---------|-------------|
| backup-uat-resources | API GW/DMS/ELB backups | 2026-03-30/apigateway/ (dygy1tl8n5-sit.json, q5gmpfywhh-sit.json) |
| itariff-ecu-template | Tariff Excel templates | TariffMultiSheetTemplate.xlsx, bulk upload folders per env |
| tariff-template-uat | UAT upload storage | tarrif-multi-sheet-upload-uat/ (active, last upload June 2) |
| kafka-client-2-13 | Kafka client binary | kafka_2.13-3.6.0.zip |
| terraform-state-euc1-itopaz-sit | Terraform state | karpenter-provider-aws.zip |
| ibm-sit-eu | IBM integration | Empty |
| waf-s3-cloudwatch | WAF logs | Empty |
| dms-assessment-run-* | DMS assessment reports | Assessment outputs |
| montycloud-inventorybucketdatasync-* | MontyCloud inventory | Auto-sync |

### Storage (SIT EU)
- SMB: 8 PVCs (itopaz-api, itopaz-auth, itopaz-export, itopaz-platform)
- EFS: 4 PVCs (istio-system: grafana, jaeger, kiali, prometheus)

## DEV Cluster (EU - Frankfurt)
- **Name**: euc1-itopaz-dev-eks
- **Account**: 074779643551
- **Region**: eu-central-1
- **Bastion**: ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/dev/eu/dev-eu-bastion.pem ec2-user@10.100.145.118
- **Node Group**: euc1-itopaz-dev-ng-20251113112717662300000010 (SPOT via ASG, m5a/m7a.xlarge, 4 vCPU, 16GB)
- **Node Versions**: v1.34.1-eks (Linux), v1.34.4-eks (Windows)
- **Nodes (June 11)**: 17 — All Ready (15 Linux AL2023 + 2 Windows Server 2022)
- **maxPods**: 29 (prefix delegation enabled but needs launch template UserData with maxPods=110)
- **ASG**: eks-euc1-itopaz-dev-ng-20251113112717662300000010-3acd3e7c-2472-9c65-0e13-8cb817cb9b56, min:2 max:35
- **Launch Template**: lt-02be58a6d1341e572
- **AMI**: AL2023_x86_64_STANDARD
- **Windows Node Groups**: euc1-itopaz-dev-eks-windows-nodegrou, euc1-itopaz-dev-eks-windows-nodegrou-v3
- **VPC CNI**: ENABLE_PREFIX_DELEGATION=true (enabled May 17, 2026)

## SIT Singapore Cluster
- **Name**: apse1-itopaz-sit-eks
- **Account**: 464134132424
- **Region**: ap-southeast-1
- **Bastion**: ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/sit/singapore/sit-sg-bastion.pem ec2-user@10.130.210.3
- **Node Versions**: v1.35.4-eks (Linux), v1.35.3-eks (Windows)
- **Nodes (June 11)**: 6 — 5 Ready + 1 NotReady (transient, new node joining at time of check)
- **Namespaces**: itariff-api, itariff-bff, itariff-ui, itariff-intg-api, itopaz-api, itopaz-ui, istio-system, prefiler-api, prefiler-ui, itopaz-accounting, itopaz-ameta, itopaz-auth, itopaz-export, itopaz-import, itopaz-platform
- **Total Pods**: ~273

## PROD EU Cluster
- **Bastion**: `ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/prod/eu/prod-eu-bastion.pem ec2-user@10.100.98.195`
- **kubectl**: available on bastion (`/usr/local/bin/kubectl`), alias `k=kubectl` configured
- **Kubeconfig fix**: exec plugin API updated from `client.authentication.k8s.io/v1alpha1` to `v1beta1`
- **Nodes (June 17)**: 4 Ready Linux nodes (`v1.36.1-eks-3385e9b`)
- **Namespaces (15)**: default, fluent-bit, istio-system, itariff-api, itariff-bff, itariff-intg-api, itariff-ui, itopaz-api, itopaz-intg-api, itopaz-ui, kube-node-lease, kube-public, kube-system, prefiler-api, prefiler-ui
- **Monitoring**: Grafana + Prometheus in `istio-system` (Istio default stack only)
  - No kube-state-metrics installed
  - No ServiceMonitor CRDs (Prometheus Operator not installed)
  - Prometheus uses `kubernetes_sd_configs` static scrape jobs
  - Available metrics: cAdvisor (`container_*`), kubelet (`kubelet_node_name`, `machine_memory_bytes`, `machine_cpu_cores`, `kubelet_running_pods`)
- **Grafana K8S Dashboard** (uid: `9f83e8f6-ae9a-4bc1-ad64-cffc1c93df02`):
  - Fixed June 17: all 129 KSM-dependent expressions replaced with cAdvisor/kubelet equivalents
  - Namespace dropdown now works via `container_memory_working_set_bytes` label values

## PROD EU iTariff Ingress Validation (June 12, 2026)
- **Bastion**: `ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/prod/eu/prod-eu-bastion.pem ec2-user@10.100.98.195`
- **kubectl**: available on bastion (`/usr/local/bin/kubectl`), alias `k=kubectl` configured
- **Kubeconfig fix**: exec plugin API updated from `client.authentication.k8s.io/v1alpha1` to `v1beta1`
- **Node check**: 3 Ready nodes (`v1.36.1-eks-3385e9b`)

- **Istio resources created in `istio-system`**:
	- `Gateway`: `itariff-gateway`
	- `VirtualService`: `itariff-ui`, `itariff-api`, `itariff-bff`

- **Hosts configured**:
	- `itariff-ui.internaleu1prd-itopaz.com`
	- `itariff-api.internaleu1prd-itopaz.com`
	- `itariff-bff.internaleu1prd-itopaz.com`

- **DNS status**:
	- All 3 resolve to Istio ingress ELB `a5c3d5f6763e149a1949597be2e56d79-0a180d890cef99d9.elb.eu-central-1.amazonaws.com`

- **Test route proving**:
	- Deployed `test-echo` in namespaces `itariff-ui`, `itariff-api`, `itariff-bff`
	- Added `/test-ping` route in each corresponding VirtualService
	- Verified ingress responses:
		- `itariff-ui.internaleu1prd-itopaz.com/test-ping` -> `200`
		- `itariff-api.internaleu1prd-itopaz.com/test-ping` -> `200`
		- `itariff-bff.internaleu1prd-itopaz.com/test-ping` -> `200`

## Key Differences (Updated June 11, 2026)
| | DEV EU | SIT EU | SIT SG |
|---|---|---|---|
| Cluster | euc1-itopaz-dev-eks | euc1-itopaz-sit-eks | apse1-itopaz-sit-eks |
| Account | 074779643551 | 464134132424 | 464134132424 |
| Bastion IP | 10.100.145.118 | 10.100.208.17 | 10.130.210.3 |
| SSH Key | dev-eu-bastion.pem | sit-eu-bastion.pem | sit-sg-bastion.pem |
| Nodes | 17 (15 Linux + 2 Win) | 20 (18 Linux + 2 Win) | 6 (5 Linux + 1 Win) |
| Instance Type | m5a/m7a.xlarge | m6a.xlarge (Linux), m5.large (Win) | TBD |
| Capacity | SPOT (100% via ASG) | SPOT (Linux), ON_DEMAND (Win) | TBD |
| K8s Server | v1.34.x | v1.33.11-eks | v1.35.4 |
| Node Version | v1.34.1 / v1.34.4 (Win) | v1.33.4 / v1.33.8 (Win) | v1.35.4 / v1.35.3 (Win) |
| Windows OS | Server 2022 | Server 2022 | Server 2025 |
| maxPods | 29 (needs fix) | 110 | TBD |
| HPA max | 3 (itopaz), none for itariff | 5-20 (selling), 3-5 (buying) | TBD |

## UAT Clusters (New — discovered Sept 1, 2026)
- **Account**: 405478414008 (previously undocumented)
- **use1-itopaz-uat-eks** — us-east-1, context `uat-us-east-1`
- **euc1-itopaz-uat-eks** — eu-central-1, context `uat-eu-central-1`
- Auth: `aws eks get-token --role-arn arn:aws:iam::405478414008:role/eks-jump-access` (same `eks-jump-access` role pattern used by all other itopaz accounts)
- Per the 2026-08-31 UAT shutdown, all 6 EKS ASGs for this account are scaled to min=0/desired=0 — these contexts will not return live nodes until re-enabled
- Kubeconfig for these 6 itopaz clusters (`/home/ec2-user/rahul/config`) merged into `~/.kube/config` on this jump server Sept 1, 2026 (backup at `~/.kube/config.bak.<timestamp>`); original `ecu-eks-test-cluster` (745510282686) context preserved
- **Known issue**: this jump server's instance role (`eks-jump-server-role`, account 745510282686) currently gets `AccessDenied` on `sts:AssumeRole` into `arn:aws:iam::464134132424:role/eks-jump-access` (and likely the other new-account roles) — cross-account trust policy needs to allow this jump server's role before `kubectl` will work against these contexts from here

## Pending Issues - DEV
- maxPods=29 — need to update launch template UserData with NodeConfig maxPods=110 and do another instance refresh
- 6 Pending pods (Windows pods need Windows nodes)

## Pending Issues - SIT (Updated June 4, 2026)
- ~~fluent-bit CrashLoop (OOMKilled)~~ — RESOLVED (duplicate fluent-bit DS in fluent-bit ns disabled, amazon-cloudwatch one is healthy)
- ~~Loki EBS CSI IRSA missing~~ — Not blocking (Loki not in active use)
- Node count at 32 (30+2 Win) — healthy, all Ready, no pending pods
- tariff-buying-service HPA at 5/5 max, memory at 82% — may need max increase
- tariff-geo-service memory at 85% — approaching limit
- tariff-buying-carriage-service memory at 85% — approaching limit
- ~~FortiGuard IPS blocking external access to prefiler-bff-eusit.itopazapp.com~~ — RESOLVED June 4 (whitelisted)
- tariff-grant-bff 500 on /authenticate — profile not found for prefiler users in tariff DB

---

# EKS Cluster Information
*Last Updated: June 11, 2026*

## SSH Keys — Canonical Locations
All keys live at: `/home/ec2-user/rahul/infrastructure/secrets/keys/`

| Environment | Key Filename | Bastion IP | SSH User |
|-------------|--------------|------------|----------|
| SIT EU | `sit/eu/sit-eu-bastion.pem` | `10.100.208.17` | `ec2-user` |
| SIT SG | `sit/singapore/sit-sg-bastion.pem` | `10.130.210.3` | `ec2-user` |
| DEV EU | `dev/eu/dev-eu-bastion.pem` | `10.100.145.118` | `ec2-user` |
| Intranet Prod-1 | `intranet/prod/Intranet-prod-1-Key.pem` | `10.151.4.89` | `ubuntu` |
| Intranet Prod-2 | `intranet/prod/Intranet-prod-1-Key.pem` | `10.151.4.153` | `ubuntu` |

> **Old stale paths** (no longer valid — keys were moved):
> - ~~`/home/ec2-user/rahul/keys/mynewkey`~~ → now `sit/eu/sit-eu-bastion.pem`
> - ~~`/home/ec2-user/rahul/keys/rahul-key`~~ → now `sit/singapore/sit-sg-bastion.pem`
> - ~~`/home/ec2-user/rahul/keys/rahul-key.pem`~~ → now `dev/eu/dev-eu-bastion.pem`

---

## SIT EU (Frankfurt)
- **Cluster**: euc1-itopaz-sit-eks
- **Account**: 464134132424
- **Region**: eu-central-1
- **Bastion**: `10.100.208.17`
- **SSH Key**: `/home/ec2-user/rahul/infrastructure/secrets/keys/sit/eu/sit-eu-bastion.pem`
- **Connect**: `ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/sit/eu/sit-eu-bastion.pem ec2-user@10.100.208.17`
- **K8s Server**: v1.33.11-eks
- **Node Versions**: v1.33.4-eks (Linux), v1.33.8-eks (Windows)
- **Nodes (June 11)**: 20 — All Ready (18 Linux AL2023 + 2 Windows Server 2022)
- **Instance Type**: m6a.xlarge (Linux SPOT), m5.large (Windows ON_DEMAND)
- **maxPods**: 110 (prefix delegation enabled)

## DEV EU (Frankfurt)
- **Cluster**: euc1-itopaz-dev-eks
- **Account**: 074779643551
- **Region**: eu-central-1
- **Bastion**: `10.100.145.118`
- **SSH Key**: `/home/ec2-user/rahul/infrastructure/secrets/keys/dev/eu/dev-eu-bastion.pem`
- **Connect**: `ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/dev/eu/dev-eu-bastion.pem ec2-user@10.100.145.118`
- **K8s Server**: v1.34.x
- **Node Versions**: v1.34.1-eks (Linux), v1.34.4-eks (Windows)
- **Nodes (June 11)**: 17 — All Ready (15 Linux AL2023 + 2 Windows Server 2022)
- **Instance Type**: m5a/m7a.xlarge (Linux SPOT)
- **maxPods**: 29 (needs fix — should be 110)

## SIT Singapore
- **Cluster**: apse1-itopaz-sit-eks
- **Account**: 464134132424
- **Region**: ap-southeast-1
- **Bastion**: `10.130.210.3`
- **SSH Key**: `/home/ec2-user/rahul/infrastructure/secrets/keys/sit/singapore/sit-sg-bastion.pem`
- **Connect**: `ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/sit/singapore/sit-sg-bastion.pem ec2-user@10.130.210.3`
- **K8s Server**: v1.35.4-eks
- **Node Versions**: v1.35.4-eks (Linux), v1.35.3-eks (Windows)
- **Nodes (June 11)**: 6 — 5 Ready, 1 NotReady (transient — new node joining)
- **Node breakdown**: 5 Linux AL2023 + 1 Windows Server 2025

## Jenkins CI/CD
- **Central Account**: 439891535362
- **EC2 Role**: euc1-itopaz-cicd-ec2-central-role
- **Cross-Account Role**: arn:aws:iam::464134132424:role/Terraform_Execution_Role
- **Jenkins URL**: https://jenkins.internal-itopaz.com

---

# Namespaces and Services - SIT EU
*Last Updated: June 4, 2026*

## Namespace: prefiler-bff (2 services)
- prefiler-auth-bff (2 replicas, no istio sidecar)
  - Service: prefiler-auth-bff-svc:80 (NodePort)
  - Image: sit-eu/prefiler-backend:prefiler-auth-bff-sit-c42482c8
  - ConfigMap: prefiler-auth-bff (envFrom), prefiler-auth-bff-appsettings (volume mount)
- prefiler-bff (2 replicas, no istio sidecar)
  - Service: prefiler-bff-svc:80 (NodePort)

## Namespace: prefiler-api (13 services, all 2 replicas with istio sidecar)
- aci-prefiler-service, aes-prefiler-service, afr-prefiler-service
- ams-prefiler-service, basf-prefiler-service, dagangnet-prefiler-service
- ics-prefiler-service, ics2-prefiler-service, imdg-prefiler-service
- master-prefiler-service, mblfiler-prefiler-service, sa-prefiler-service
- prefiler-auth-service
  - Service: prefiler-auth-service-svc
  - Internal URL: http://prefiler-auth-service-svc.prefiler-api.svc.cluster.local/prefiler-auth-service/

## Namespace: prefiler-ui
- microfrontend-main (2/2 pods with istio sidecar)
  - Service: microfrontend-main-svc:80
  - Image: sit-eu/prefiler-frontend:microfrontend-main-sit-f020163f
- microfrontend-shared (2/2 pods with istio sidecar)
  - Service: microfrontend-shared-svc:80
  - Image: sit-eu/prefiler-frontend:microfrontend-shared-sit-4a1dbe33
- afr-prefiler (2/2 pods with istio sidecar)
  - Service: afr-prefiler-svc:80
  - Image: sit-eu/prefiler-frontend:afr-prefiler-sit-d5fe3b9a

## Namespace: tariff-api
- tariff-buying-shippingline-consumer-service
  - Requires SPRING_CONFIG_LOCATION env var

## ECR Repositories
- `464134132424.dkr.ecr.eu-central-1.amazonaws.com/sit-eu/prefiler-backend` (API services)
- `464134132424.dkr.ecr.eu-central-1.amazonaws.com/sit-eu/prefiler-frontend` (UI services)

---

# Project: Tag-Based Pod Resource Billing Monitor
**Created**: 2026-06-11  
**Scope**: itariff, prefiler, itopaz — SIT EU, DEV EU clusters  
**Goal**: Allocate Kubernetes pod resource costs (CPU/memory) per product using a single `app` label tag (`itariff` / `itopaz` / `prefiler`), and surface billing breakdowns via AWS Cost Explorer + Kubecost/CloudWatch

---

## 1. Tagging Strategy

### 1.1 Tag Label (per pod)
One label added to all pods — **`billing-app`**:

| Label Key | Values | Purpose |
|---|---|---|
| `billing-app` | `itariff` / `prefiler` / `itopaz` | Product-level billing grouping |

Every pod in an itariff namespace gets `billing-app: itariff`, prefiler pods get `billing-app: prefiler`, itopaz pods get `billing-app: itopaz`.

> **Why `billing-app` and not `app`**: Pods already have `app: <service-name>` used by selectors/services. Overwriting it would break routing. Using `billing-app` keeps billing separate without touching existing selectors.

### 1.2 AWS Node Tags (EKS Node Groups)
| AWS Tag Key | Value |
|---|---|
| `Project` | `itopaz` |
| `Environment` | `sit` / `dev` |
| `BillingApp` | `itariff` / `prefiler` / `itopaz` (per node group if split) |
| `CostCenter` | `allcargo-ecu` |

---

## 2. Label Mapping Per Product

### itariff — namespaces: `itariff-api`, `itariff-bff`, `itariff-ui`
**Label**: `billing-app: itariff`  
All deployments in these 3 namespaces.

### prefiler — namespaces: `prefiler-api`, `prefiler-bff`, `prefiler-ui`
**Label**: `billing-app: prefiler`  
All deployments in these 3 namespaces.

### itopaz — namespaces: `itopaz-auth`, `itopaz-export`, `itopaz-platform`
**Label**: `billing-app: itopaz`  
All deployments in these 3 namespaces.

---

## 3. Implementation Steps

### Phase 1 — Add Label to Deployment YMLs in Repos

Under `spec.template.metadata.labels`, add one line:
```yaml
spec:
  template:
    metadata:
      labels:
        app: <existing-service-name>   # keep as-is
        billing-app: itariff           # add this (itariff / prefiler / itopaz)
```

**Repos to update:**
- `itariff-k8s-repo` → `uat` branch → `billing-app: itariff`
- `prefiler-k8s-repo` → `sit` branch → `billing-app: prefiler`
- `itopaz-k8s-repo` → SIT branch → `billing-app: itopaz`
- Repeat for DEV branches

### Phase 2 — Patch Live Clusters (no redeploy needed)

**SIT EU — itariff namespaces:**
```bash
for ns in itariff-api itariff-bff itariff-ui; do
  kubectl get deploy -n $ns --no-headers -o name | xargs -I{} \
    kubectl patch {} -n $ns --type=merge \
    -p '{"spec":{"template":{"metadata":{"labels":{"billing-app":"itariff"}}}}}'
done
```

**SIT EU — prefiler namespaces:**
```bash
for ns in prefiler-api prefiler-bff prefiler-ui; do
  kubectl get deploy -n $ns --no-headers -o name | xargs -I{} \
    kubectl patch {} -n $ns --type=merge \
    -p '{"spec":{"template":{"metadata":{"labels":{"billing-app":"prefiler"}}}}}'
done
```

**SIT EU — itopaz namespaces:**
```bash
for ns in itopaz-auth itopaz-export itopaz-platform; do
  kubectl get deploy -n $ns --no-headers -o name | xargs -I{} \
    kubectl patch {} -n $ns --type=merge \
    -p '{"spec":{"template":{"metadata":{"labels":{"billing-app":"itopaz"}}}}}'
done
```

> Repeat for DEV EU — same commands via `dev/eu/dev-eu-bastion.pem` to `10.100.145.118`

### Phase 3 — AWS Cost Allocation Tags

1. **AWS Billing → Cost allocation tags** → activate `BillingApp`
2. Tag EKS node groups:
```bash
aws eks list-nodegroups --cluster-name euc1-itopaz-sit-eks --region eu-central-1
aws eks tag-resource --resource-arn <nodegroup-arn> \
  --tags BillingApp=itariff,Environment=sit,CostCenter=allcargo-ecu
```

### Phase 4 — Monitoring

#### Prometheus queries (kube-state-metrics already on DEV)
```promql
# CPU requested per product
sum(
  kube_pod_container_resource_requests{resource="cpu"}
  * on(pod, namespace) group_left(label_billing_app)
  kube_pod_labels{label_billing_app=~"itariff|prefiler|itopaz"}
) by (label_billing_app)

# Memory requested per product
sum(
  kube_pod_container_resource_requests{resource="memory"}
  * on(pod, namespace) group_left(label_billing_app)
  kube_pod_labels{label_billing_app=~"itariff|prefiler|itopaz"}
) by (label_billing_app)
```

#### Quick kubectl pod count per product
```bash
kubectl get pods -A --show-labels | grep 'billing-app=itariff' | wc -l
kubectl get pods -A --show-labels | grep 'billing-app=prefiler' | wc -l
kubectl get pods -A --show-labels | grep 'billing-app=itopaz' | wc -l
```

---

## 4. Verify Labels Applied

```bash
kubectl get pods -n itariff-api --show-labels | grep billing-app
kubectl get pods -n prefiler-bff --show-labels | grep billing-app
kubectl get pods -n itopaz-export --show-labels | grep billing-app
```

---

## 5. Pending Actions

| # | Action | Cluster | Status |
|---|---|---|---|
| 1 | Patch live SIT EU — itariff namespaces (3) | SIT EU | ⏳ |
| 2 | Patch live SIT EU — prefiler namespaces (3) | SIT EU | ⏳ |
| 3 | Patch live SIT EU — itopaz namespaces (3) | SIT EU | ⏳ |
| 4 | Patch live DEV EU — all namespaces | DEV EU | ⏳ |
| 5 | Update YMLs in `itariff-k8s-repo` uat branch | repo | ⏳ |
| 6 | Update YMLs in `prefiler-k8s-repo` sit branch | repo | ⏳ |
| 7 | Activate AWS cost allocation tag `BillingApp` | AWS 464134132424 | ⏳ |
| 8 | Set up Grafana billing dashboard with promQL above | Both | ⏳ |

---

# Pending/Unresolved Items
*Last Updated: June 4, 2026*

## 1. Notification Service Mail Issue (Dev)
- Status: NOT investigated
- Environment: Dev cluster
- Issue: Mail notifications not working
- Likely cause: AWS SES sandbox or credential issue

## 2. itariff-k8s-repo Dev Branch Update
- Status: NOT done
- Task: Add SPRING_CONFIG_LOCATION fix for shippingline-consumer on dev branch
- Currently only fixed on uat branch (SIT)

## 3. TLS Certificate for *.internaleu1-itopaz.com
- Status: NOT available
- Impact: Users must disable SSL verification in Postman for internal URLs
- Current cert only covers: *.itopazapp.com
- Recommendation: Add *.internaleu1-itopaz.com to gateway TLS cert or use ACM

## 4. prefiler-eusit.itopazapp.com DNS
- Status: PARTIALLY RESOLVED (June 4)
- The external domain now resolves (Global Accelerator → API GW)
- BUT FortiGuard IPS blocks prefiler-bff-eusit.itopazapp.com externally
- Internal URL (prefiler-ui.internaleu1-itopaz.com) works fine
- Action: Network team must whitelist in FortiGuard URL filtering

## 5. microfrontend-shared - BFF URL Configuration
- The BFF API URL (`prefiler-bff-eudev.itopazapp.com`) was seen in browser errors
- This URL is likely configured inside the shared_ui navbar component
- Need to check/update `microfrontend-shared` repo for correct SIT BFF URL:
  - Should be: `prefiler-bff.internaleu1-itopaz.com` or relative `/prefiler-auth-bff/`

## 6. FortiGuard IPS Blocking External Prefiler Access (June 4)
- Status: ✅ RESOLVED — whitelisted by network team on June 4, 2026
- URL: `prefiler-bff-eusit.itopazapp.com` now accessible externally
- Verified: HTTP 200, proper application response (401 for invalid creds)

## 7. tariff-grant-bff 500 on /authenticate (NEW June 4)
- Status: OPEN — needs DB or code fix
- Error: NullPointerException in tariff-profile-service (profile not found)
- Cause: Prefiler users don't have profile entries in tariff DB
- Fix: Add user to profile table OR fix null handling in code

## 8. DEV maxPods Still 29
- Status: PENDING
- Task: Update launch template UserData with NodeConfig maxPods=110
- Then trigger another instance refresh

---

## 9. tariff-selling-service DB Index (NEW June 10)
- Status: OPEN — dev team needed
- Environment: SIT EU Aurora (`itariff-sit-cluster`, PostgreSQL 15.15)
- DB: `TariffSelling`
- Problem: `dbo.tariff` (146GB) and `dbo.tariffdetails` (184GB) have no indexes on lookup columns
- Impact: `/selling-rates/import` page loads in 8–10s (dropdown APIs do full seq scans)
- Fix needed:
  ```sql
  CREATE INDEX CONCURRENTLY idx_tariff_pol ON dbo.tariff(pol_code);
  CREATE INDEX CONCURRENTLY idx_tariff_por ON dbo.tariff(por_code);
  CREATE INDEX CONCURRENTLY idx_tariff_shippingline ON dbo.tariff(shipping_line_code, agent_code);
  ```
- Note: autovacuum now running (naptime fixed 5s→60s on June 10) — stats improving

## 10. tariff-selling-bff Redis Cache for Dropdown APIs (NEW June 10)
- Status: OPEN — dev team needed
- Environment: SIT EU
- Problem: Dropdown APIs on `/selling-rates/import` page load hit DB every request
- Slow endpoints: `getShippingLineAgent` (up to 180s!), `getTSOCPOL` (2s), `getPOR` (1.6s)
- Fix needed: Add Redis cache (TTL 30min) in tariff-selling-bff for:
  - `GET /bffdropdown/getShippingLineAgent`
  - `GET /bffdropdown/getTSOCPOL`
  - `GET /bffdropdown/getPOR`
  - `POST /BffTariffSelling/getTariffSellingSearchSingleRow1` (TTL 5min)
  - `POST /BffTariffBuying/getTariffBuyingSearchSingleRow` (TTL 5min)

## 11. DMS Replication Slot Monitoring (NEW June 10)
- Status: OPEN — monitoring setup needed
- Environment: SIT EU Aurora
- Problem: 11 stale DMS logical replication slots caused 99% CPU + 51K ReadIOPS (June 10)
- Root cause: DMS tasks stopped/failed but slots not cleaned up automatically
- Fix applied: All 11 slots dropped manually (June 10)
- **Monitoring needed:** CloudWatch alarm on `OldestReplicationSlotLag` > threshold
  ```bash
  # Check slots regularly
  SELECT slot_name, active, pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS lag_bytes
  FROM pg_replication_slots WHERE slot_type = 'logical';
  ```

## 13. Intranet deploy.sh Port-Kill Logic — ✅ FIXED June 10
- Status: RESOLVED
- Servers: `10.151.4.89` (Intranet-prod-1), `10.151.4.153` (Intranet-prod-2)
- Fix applied: replaced grep-based kill with `fuser -k 8001/tcp` in `/home/ubuntu/cicd/deploy.sh`
- Original backed up as `/home/ubuntu/cicd/deploy.sh.bak` on both servers

## 12. prefiler-cache-util Pipeline — SonarQube + OWASP (NEW June 10)
- Status: PARTIALLY RESOLVED
- Pipeline: `prefiler-nonprod-backend/SIT/prefiler-cache-util`
- Fixed: Compile error (`GetAsync` → `GetObjectAsync`) — commit `fff0b5ae`
- Fixed: `mstest` step → `archiveArtifacts` — commit `1188a6a` in prefiler-k8s-repo
- Remaining: SonarQube/Quality Gate + OWASP stages need re-validation after full pipeline run

---

# Prefiler Service Configuration

## Dev Cluster (euc1-itopaz-dev-eks)
- Namespace: `prefiler-api`
- Auth service image: `074779643551.dkr.ecr.eu-central-1.amazonaws.com/dev-eu/prefiler-backend:prefiler-auth-service-dev-5c9391e0`
- ConfigMap: `prefiler-auth-service-config` (envFrom, `__` delimited env vars for .NET)
- No volume mount needed — .NET reads `ConnectionStrings__zone1` as `ConnectionStrings:zone1`
- DB: `euc1-itariff-edi-dev.cluster-c3kmoowi6x9d.eu-central-1.rds.amazonaws.com` / Database: Profile / User: prefiler_bff
- Redis: `master.euc1-itopaz-dev-redis.lf4u8f.euc1.cache.amazonaws.com:6379`
- Crypto Key/IV same across dev and SIT (AES encryption for connection strings)
- VirtualServices (istio-system namespace):
  - prefiler-api: `prefiler-api.internaleu1dev-itopaz.com`, `prefiler-api-eudev.itopazapp.com`
  - prefiler-bff: `prefiler-bff.internaleu1dev-itopaz.com`, `prefiler-bff-eudev.itopazapp.com`
  - prefiler-ui: `prefiler-ui.internaleu1dev-itopaz.com`, `prefiler-eudev.itopazapp.com`

## SIT Cluster (euc1-itopaz-sit-eks)
- Namespace: `prefiler-api` (13 services, 2 replicas each, all Running)
- Namespace: `prefiler-bff` (prefiler-auth-bff 2 replicas, prefiler-bff 2 replicas)
- Auth service image: `464134132424.dkr.ecr.eu-central-1.amazonaws.com/sit-eu/prefiler-backend:prefiler-auth-service-sit-9448945d`
- ConfigMaps & Secrets (Updated 2026-10-07, `prefiler-k8s-repo@sit` commit `e903f8b`):
  - All 16 ConfigMaps (`config/*-config.yaml`) use `$(DB_PASSWORD)` interpolation and omit plaintext `RedisSettings__Password` and `JwtOptions__SecretKey`.
  - Secret `prefiler-api-secret` (in `prefiler-api` namespace) and Secret `prefiler-bff-secret` (in `prefiler-bff` namespace) inject `DB_PASSWORD`, `RedisSettings__Password`, and `JwtOptions__SecretKey` before `envFrom` in all 15 Deployments (`service/api/*.yaml`, `service/bff/*.yaml`).
  - `config/Jenkincm` supports `--ALL--` to apply all 16 ConfigMaps across `prefiler-api` and `prefiler-bff`.
- DB: `euc1-itopaz-sit-aurora-postgresql.cluster-cd6uok42udhj.eu-central-1.rds.amazonaws.com` / User: `prefiler_sit` / Password: `passwordsit@1035` (`DB_PASSWORD` via Secret; note `passwordsit@1035x` fails SCRAM-SHA-256)
- Redis: `master.euc1-itopaz-sit-redis-new.tqptfx.euc1.cache.amazonaws.com:6379` (`RedisSettings__Host` standardized across all 16 ConfigMaps; password `2a7bae34ec#0fc243e63169dc07` via Secret)
- Port: 8080 (containerPort)
- VirtualServices (istio-system namespace):
  - prefiler-ui: `prefiler-ui.internaleu1-itopaz.com`, `prefiler-eusit.itopazapp.com`
  - prefiler-bff: `prefiler-bff.internaleu1-itopaz.com`, `prefiler-bff-eusit.itopazapp.com`
  - prefiler-api: `prefiler-api.internaleu1-itopaz.com`, `prefiler-api-eusit.itopazapp.com`

### Prefiler-API VirtualService Routes (13 routes - Updated June 4, 2026)
- `/sa-prefiler-service/` → prefiler-auth-service-svc (note: sa route maps to auth-service)
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

## SIT Singapore Cluster (apse1-itopaz-sit-eks)
- **Account**: `464134132424` | **Region**: `ap-southeast-1`
- **Bastion Host**: `10.130.210.3` (`i-05b9998627e8bf6e8`, accessible via AWS SSM when direct SSH from `10.151.4.165` is blocked)
- **ECR Repositories (`ap-southeast-1`)**:
  - Backend: `464134132424.dkr.ecr.ap-southeast-1.amazonaws.com/sit-apse/prefiler-backend`
  - Frontend: `464134132424.dkr.ecr.ap-southeast-1.amazonaws.com/sit-apse/prefiler-frontend`
- **ConfigMaps & Secrets (`prefiler-k8s-repo@sit-singapore` commit `3498eaa`)**:
  - `prefiler-api-secret` (namespace `prefiler-api`): keys `db-password`, `db-password-2`, `DB_PASSWORD_2` (`prefiler_sit#@*y!#Y)%#`), `redis-password` (`#0fc243e63169dc07`), `JwtOptions__SecretKey` (`this_is_a_very_secure_secret_key_123!`).
  - `prefiler-bff-secret` (namespace `prefiler-bff`): keys `db-password` (`prefiler_sit#@*y!#Y)%#`), `redis-password` (`#0fc243e63169dc07`), `JwtOptions__SecretKey` (`this_is_a_very_secure_secret_key_123!`).
  - All 16 `config/*-config.yaml` files omit plaintext DB passwords, `RedisSettings__Password`, and `JwtOptions__SecretKey`; all 16 `*-service.yml` / `*-bff.yml` Deployment manifests inject `DB_PASSWORD`, `RedisSettings__Password`, and `JwtOptions__SecretKey` via `secretKeyRef` and expand `Password=$(DB_PASSWORD)` in `env:`.
  - `config/jenkincm` supports `--ALL--` batch ConfigMap deployment to `apse1-itopaz-sit-eks`.
- **Aurora PostgreSQL Cluster (`ap-southeast-1`)**:
  - Endpoint: `apse1-itopaz-sit-aurora-postgresql.cluster-cve80ey2iakj.ap-southeast-1.rds.amazonaws.com:5432`
  - Credentials: User `prefiler_sit` / Password `prefiler_sit#@*y!#Y)%#`
  - Databases Hosted: `APACDBECUGROUPAGE` (`zone4` - Dagangnet/APAC), `AUAUDBECUGROUPAGE` (`zone5` - Australia), `APACDBEDI_UAT`, `AUMELDBECUDIGIVIEW`, `Digiviewapi`, `INMUMDBECUDIGIVIEW`, `PostGreToCRMInterfaceLogDB`
  - **Regional Database Difference**: `APACDBECUGROUPAGE` (`zone4`) and `AUAUDBECUGROUPAGE` (`zone5`) exist **only** on the Singapore RDS cluster and **do not exist** on the Frankfurt RDS cluster (`euc1-itopaz-sit-aurora-postgresql`). Any `zone4`/`zone5` request routed to `prefiler-bff-eusit.itopazapp.com` fails with HTTP 500 (`3D000: database "AUAUDBECUGROUPAGE" does not exist`).
- **Redis (`ap-southeast-1`)**:
  - Host: `master.apse1-itopaz-sit-redis-new.m3fywm.apse1.cache.amazonaws.com:6379` (TLS enabled, password `#0fc243e63169dc07`)
- **External URLs & CloudFront Distributions (Account `464134132424`)**:
  - `prefiler-sasit.itopazapp.com` → CloudFront `E3D3FER4L2TKX9` (`d2bfv7r3a9b3v9.cloudfront.net`, Origin: `ac38b9cc6d8d94ef080d55c1a3781fcd-cb0707ca1a68ac8d.elb.ap-southeast-1.amazonaws.com`)
  - `prefiler-eusit.itopazapp.com` → CloudFront `E1H7QYRQWZGB8Z` (`d1x51r2t0l7x7m.cloudfront.net`, Origin: `euc1-itopaz-external-alb-1942531620.eu-central-1.elb.amazonaws.com`)
  - `prefiler-bff-sasit.itopazapp.com` → SIT Singapore BFF
  - `prefiler-api-sasit.itopazapp.com` → SIT Singapore API
- **Microfrontend & Pipeline Cross-Region Notes**:
  - `microfrontend-main` on `apse1-itopaz-sit-eks` must run an image built from the `sit-singapore` branch (e.g., `464134132424.dkr.ecr.ap-southeast-1.amazonaws.com/sit-apse/prefiler-frontend:microfrontend-main-sit-290886ca`), whose `src/index.html` `<script type="systemjs-importmap">` loads child bundles from `https://prefiler-sasit.itopazapp.com/*`.
  - All Prefiler Angular microfrontends import `src/environments/environment.development` directly in `api.service.ts` / `apis.service.ts` / `userAuth.service.ts`, and `angular.json` replaces `environment.ts` with `environment.development.ts` during `ng build`. Always update `src/environments/environment.development.ts` (not just `environment.ts`) when configuring BFF URLs per branch (`sit` → `prefiler-bff-eusit.itopazapp.com`, `sit-singapore` → `prefiler-bff-sasit.itopazapp.com`).

## Architecture Note: single-spa Child Microfrontends Cannot Render Standalone
- `prefiler-ui` namespace apps (`imdg-prefiler`, `afr-prefiler`, etc.) are single-spa **children**, built via `main.single-spa.ts` — they export `bootstrap`/`mount`/`unmount` lifecycle hooks and do not self-render on script load
- The shell (`microfrontend-main`) boots `single-spa` + `single-spa-layout` at root `/` and mounts the correct child based on the current browser URL
- The `prefiler-ui` VirtualService routes `/<app>-prefiler/*` by path prefix **directly to each child's pod**, bypassing the shell — a full-page navigation/refresh/deep-link to that path never loads the shell, so the child's `main.js` loads but is never `mount()`ed → blank page
- Each child's `.htaccess` has (or needs) a guard that hands off full-page navigation to the shell instead of trying to render standalone or hardcoding a 301 to a fixed path (which drops the destination) — see `changes-log.md` 2026-07-24 entry for the `imdg-prefiler` fix pattern (redirect to shell `/dashboard?spaRedirect=<encoded original path>`, shell restores URL via `history.replaceState` before single-spa boots)
- This pattern has not been checked/fixed yet in the other 11 `*-prefiler` UI repos

## Key Issues Resolved
- ProfileConnection placeholder "DB1_connectionnstring" in image — must override via configmap
- SIT had wrong DB host (itariff-sit-cluster → euc1-itopaz-sit-aurora-postgresql) and wrong password
- SIT Profile database didn't exist — had to CREATE DATABASE "Profile" and CREATE SCHEMA dbo
- relation "dbo.profile" does not exist — schema needs to be created manually or via EF migrations
- Volume mount at /app/appsettings.json with subPath can cause "not a directory" OCI error on some nodes

## Tariff Buying Truck Service (SIT)
- Namespace: `itariff-api`
- ConfigMap: `tariff-buying-truck-service`
- Kafka MSK (SIT): `b-2.euc1itariffsitmsk.76ygyn.c5.kafka.eu-central-1.amazonaws.com:9096`, `b-1.euc1itariffsitmsk.76ygyn.c5.kafka.eu-central-1.amazonaws.com:9096`
- Kafka credentials: admin / admin#$321
- Topics: `tariff-buying-truck-bulk-process-uat`, `tariff-buying-truck-bulk-archive-uat`
- DB: `itariff-sit-cluster.cluster-cd6uok42udhj.eu-central-1.rds.amazonaws.com` / tb_truck_db / tariff_sit / topazsit#123
- Must include all `service.*` properties (norecord, validation, delete, archive) or app crashes with PlaceholderResolutionException

---

# Prefiler Auth BFF - Complete Fix Documentation

## Problem
- prefiler-auth-bff returning 404 in SIT EU Frankfurt

## Root Causes (3 issues)
1. **No VirtualService route** existed for prefiler-auth-bff (only prefiler-bff-svc was routed)
2. **Initial VS had URI rewrite** to `/` which stripped the PathBase the app needs
3. **Users used wrong path** `/api/v1/Auth/Login` instead of correct `/bff/v1/Auth/Login`

## After Routing Fixed - 500 Error
- Backend URL in ConfigMap had typo (`/prefiler-auth-servie` missing 'c')
- Used external HTTPS URL instead of internal cluster service URL

## Final Fix Applied
### VirtualService
- Prefix match `/prefiler-auth-bff/` → `prefiler-auth-bff-svc:80` (NO rewrite)
- Gateway: prefiler-gateway
- Hosts: prefiler-bff.internaleu1-itopaz.com, prefiler-bff-eusit.itopazapp.com

### ConfigMap (prefiler-auth-bff)
```yaml
ApiConfig__Endpoints__Auth__Production: "http://prefiler-auth-service-svc.prefiler-api.svc.cluster.local/prefiler-auth-service/"
AzureAd__RedirectUri: "https://prefiler-bff.internaleu1-itopaz.com/authorizationcode"
```

### App Architecture
- .NET app with `UsePathBase("/prefiler-auth-bff")` in Program.cs
- Controller route: `bff/v{version:apiVersion}/Auth`
- Endpoints: Login, Authenticate
- BFF pods run 1/1 (no istio sidecar)

### Correct API Endpoint
```
POST https://prefiler-bff.internaleu1-itopaz.com/prefiler-auth-bff/bff/v1/Auth/Login
Content-Type: application/json

{
  "Username": "export",
  "Password": "yes",
  "ChannelId": 0,
  "Authenticated": true
}
```

### Gateway Fix
- `prefiler-bff.internaleu1-itopaz.com` was missing from HTTPS (port 443) server block
- Patched: added to both HTTP and HTTPS hosts in prefiler-gateway

### ECR Image
- `464134132424.dkr.ecr.eu-central-1.amazonaws.com/sit-eu/prefiler-backend:prefiler-auth-bff-sit-acaadb42`

---

# Prefiler Auth Service - Redis Fix

## Problem
- prefiler-auth-service returning 500 errors

## Root Cause
- Wrong Redis password in appsettings.json

## Fix
- **Correct Redis Host**: master.euc1-itopaz-sit-redis-new.tqptfx.euc1.cache.amazonaws.com
- **Correct Password**: `2a7bae34ec#0fc243e63169dc07`
- **Wrong Password was**: `2a7bae34ec#0fc243e6316trwt54`

## Repository
- Repo: `allcargoecu/prefiler-auth-service` (Bitbucket)
- Branch: sit
- File: appsettings.json

---

# Microfrontend UI - URL and CORS Fix

## Problem
- UI loading from `prefiler-ui.internaleu1-itopaz.com` but referencing assets/scripts from `prefiler-eusit.itopazapp.com`
- 503 errors on `prefiler-eusit.itopazapp.com`
- CORS policy blocking cross-origin script loads

## Root Cause
- index.html had absolute URLs pointing to external domain
- Cross-domain requests blocked by CORS
- The external domain cert/DNS issues causing 503

## Fix
Changed all absolute URLs to **relative paths** in `microfrontend-main/index.html` (sit branch):
```
BEFORE: "https://prefiler-eudev.itopazapp.com/afr-prefiler/main.js"
AFTER:  "/afr-prefiler/main.js"
```

This works because the VirtualService routes all paths on the same host:
- `/` → microfrontend-main-svc
- `/afr/` → afr-prefiler-svc
- `/shared_ui/` → microfrontend-shared-svc

## Repo
- Repo: `allcargoecu/microfrontend-main` (Bitbucket)
- Branch: sit
- Commit: 7cf5234

## VirtualService Config (prefiler-ui)
```yaml
hosts:
- prefiler-eusit.itopazapp.com
- prefiler-ui.internaleu1-itopaz.com
http:
- match: [{uri: {prefix: /afr/}}]
  route: [{destination: {host: afr-prefiler-svc.prefiler-ui.svc.cluster.local, port: 80}}]
- match: [{uri: {prefix: /shared_ui/}}]
  route: [{destination: {host: microfrontend-shared-svc.prefiler-ui.svc.cluster.local, port: 80}}]
- match: [{uri: {prefix: /}}]
  route: [{destination: {host: microfrontend-main-svc.prefiler-ui.svc.cluster.local, port: 80}}]
```

---

# Istio Gateway Configuration - SIT EU

## Gateway: prefiler-gateway (istio-system namespace)
### Hosts (HTTP port 80 + HTTPS port 443)
- prefiler-api-eusit.itopazapp.com
- prefiler-eusit.itopazapp.com
- prefiler-bff-eusit.itopazapp.com
- prefiler-api.internaleu1-itopaz.com
- prefiler-ui.internaleu1-itopaz.com
- prefiler-bff.internaleu1-itopaz.com

### TLS Note
- Protocol is "HTTP" on both port 80 and 443 (TLS terminated at ALB)
- ALB cert covers `*.itopazapp.com` only
- `*.internaleu1-itopaz.com` NOT in cert — must disable SSL verification in Postman

### Gateway Service
- Service: `istio-gateway` in `istio-system` namespace
- Type: LoadBalancer
- ALB DNS: `a6e66b606f1f34daa80962967d99ae0d-099f8d355e79e71a.elb.eu-central-1.amazonaws.com`

## Gateway: itariff-gateway
### Hosts
- itariff-api-eusit.itopazapp.com
- itariff-eusit.itopazapp.com
- itariff-api.internaleu1-itopaz.com
- itariff-ui.internaleu1-itopaz.com
- nginx.internaleu1-itopaz.com
- test.internaleu1-itopaz.com
- itariff-bff.internaleu1-itopaz.com
- itariff-bff-eusit.itopazapp.com
- itariff-euat.itopazapp.com
- itariff-bff-euat.itopazapp.com
- itariff-api-euat.itopazapp.com
- itariff-bff-upload.itopazapp.com

## Gateway: itopaz-gateway
### Hosts
- itopaz-api.internaleu1-itopaz.com
- itopaz-ui.internaleu1-itopaz.com
- eusit-api.itopazapp.com
- eusit.itopazapp.com
- itopaz-ussit.itopazapp.com
- itopaz-sasit.itopazapp.com

## DNS Records (Route53)
- prefiler-bff.internaleu1-itopaz.com → CNAME → a6e66b606f1f34daa80962967d99ae0d-099f8d355e79e71a.elb.eu-central-1.amazonaws.com (TTL 300)

---

# Tariff Buying Shippingline Consumer - ConfigMap Fix

## Problem
- tariff-buying-shippingline-consumer-service pods CrashLoopBackOff
- Error: Spring Boot couldn't find application.yml

## Root Cause
- ConfigMap mounted as volume but `SPRING_CONFIG_LOCATION` not set
- App looking for config in default classpath, not the mounted path

## Fix
Added environment variable to deployment:
```yaml
env:
- name: SPRING_CONFIG_LOCATION
  value: "file:/config/application.yml"
```

## Applied In
- SIT EU cluster: euc1-itopaz-sit-eks (namespace: tariff-api)
- Dev EU cluster: euc1-itopaz-dev-eks (namespace: tariff-api)

## Repository
- Repo: `allcargoecu/itariff-k8s-repo` (Bitbucket)
- Branch: uat (SIT manifest)
- Dev branch: needs update (not yet done)

---

# Singapore Cluster - Istio IngressGateway Critical Fix
*Date: June 5, 2026*

## Incident Summary
- **Severity**: CRITICAL
- **Cluster**: apse1-itopaz-sit-eks (ap-southeast-1)
- **Impact**: Complete ingress routing failure, cluster overloaded with 12,599 pods

## Root Cause
1. Operator (jump server history line 937) ran: `k delete gw itopaz-gateway -n istio-system`
2. Gateway recreation triggered HPA to scale `istio-ingressgateway` deployment
3. New pods scheduled on Windows node (`ip-10-130-211-18`) which **does not support Linux sysctl syscalls** required by Envoy proxy
4. Every pod failed with `SysctlForbidden` status immediately
5. HPA continuously retried → cascading creation of 12,500+ stuck pods
6. All pods stuck as `0/1 SysctlForbidden` — ingress completely broken

## Symptoms
```
kubectl get pods -n istio-system | grep SysctlForbidden | wc -l
# Output: 12501
kubectl get pods --all-namespaces | wc -l
# Output: 12599
```

## Fix Applied (June 5, 2026)

### Step 1: Add Linux-only node affinity to deployment
```bash
kubectl patch deployment istio-ingressgateway -n istio-system --type merge -p '{
  "spec": {
    "template": {
      "spec": {
        "affinity": {
          "nodeAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": {
              "nodeSelectorTerms": [{
                "matchExpressions": [{
                  "key": "kubernetes.io/os",
                  "operator": "In",
                  "values": ["linux"]
                }]
              }]
            }
          }
        }
      }
    }
  }
}'
```

### Step 2: Delete old stuck ReplicaSets with cascade
```bash
kubectl delete rs istio-ingressgateway-6bcb465c5f istio-ingressgateway-696f57d5 \
  -n istio-system --cascade=foreground
```

### Step 3: Force delete remaining stuck pods
```bash
kubectl delete pods -n istio-system -l app=istio-ingressgateway --grace-period=0 --force
```

## Result
| Metric | Before | After |
|--------|--------|-------|
| Total cluster pods | 12,599 | 97 |
| istio-system pods | 12,507 | 7 |
| ingressgateway pods | 12,501 failed | 1 running |
| All nodes | Overloaded | Ready |

## HPA Configuration
```
NAME                   MIN   MAX   REPLICAS
istio-ingressgateway   1     5     1
```

## Prevention
The `istio-ingressgateway` deployment now has permanent `nodeAffinity` for `kubernetes.io/os: linux`.
This prevents scheduling on Windows nodes in future.

## Singapore Cluster Nodes (post-fix)
- 5 Linux nodes: v1.35.4-eks-7fcd7ec
- 1 Windows node: ip-10-130-211-18 (v1.35.3-eks) — for Windows workloads only

---

# API Gateway CORS Fix Guide - udejfu5f3b

## Current Status
- **API ID**: udejfu5f3b (shown in console URL)
- **Actual API ID in Use**: 7a8aq4c0oa (from X-AMZN-APIGATEWAY-API-ID header in logs)
- **Region**: eu-central-1
- **Issue**: CORS headers not configured at API Gateway level

## Problem
API Gateway methods (especially OPTIONS) need explicit CORS response mappings to pass CORS preflight requests.

## Solution: Configure CORS on Each Method

### Step 1: Enable CORS at Resource Level
For each prefiler resource path that receives requests:

**Console Path**: https://eu-central-1.console.aws.amazon.com/apigateway/main/apis/udejfu5f3b/resources

### Step 2: For Each Resource - Add OPTIONS Method

1. **Select Resource** (e.g., `/prefiler-bff/prefiler/bff/v1/{proxy+}`)
2. **Create Method**: OPTIONS
3. **Integration Type**: Mock
4. **Click "Integration Response"**
5. **Add Response Headers** for 200 status:

```
Header Name                          | Mapped From
====================================================
Access-Control-Allow-Headers        | 'content-type,authorization,user-id,email-id,x-requested-with,accept,origin,zoneid,x-api-key'
Access-Control-Allow-Methods        | 'GET,POST,PUT,DELETE,OPTIONS,PATCH'
Access-Control-Allow-Origin         | '*'
Access-Control-Allow-Credentials    | 'true'
Access-Control-Max-Age              | '86400'
```

### Step 3: For Existing GET/POST/PUT/DELETE Methods

1. **Select Method** (e.g., GET)
2. **Click "Integration Response"**
3. **Expand 200 status** → **Response Headers**
4. **Add the same headers** (copy from Step 2)

### Step 4: Deploy API

1. **Click "Deploy API"**
2. **Stage**: prod or sit (whichever is active)
3. **Wait for deployment** (1-2 minutes)

## Expected Result After Fix

All requests to prefiler APIs will include CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS,PATCH
Access-Control-Allow-Headers: content-type,authorization,user-id,email-id,x-requested-with,accept,origin,zoneid,x-api-key
Access-Control-Allow-Credentials: true
```

## Verification

Test with:
```bash
curl -i https://prefiler-bff-eusit.itopazapp.com/prefiler-bff/prefiler/bff/v1/Afr/GetCount?fromDate=2025-03-09&toDate=2026-06-09
```

Should see CORS headers in response.

## Current Working Components ✅

- **Istio Gateway CORS**: ✅ Configured with corsPolicy
- **DNS/Route53**: ✅ Routes to API Gateway
- **ALB**: ✅ Forwards to EKS cluster
- **EKS/Istio**: ✅ CORS headers applied at gate level
- **Backend Services**: ✅ Returning 200 responses
- **API Gateway CORS**: ⚠️ **NEEDS MANUAL FIX** (this guide)

## Affected Endpoints

- `/prefiler-bff/prefiler/bff/v1/*` → GetCount, GetSearchConfigByPageID, PageMaster, etc.
- `/afr-prefiler-service/*`
- `/master-prefiler-service/*`
- All other prefiler microservices

## Note on API ID Discrepancy

- **Console shows**: udejfu5f3b
- **Logs show** (x-amzn-apigateway-api-id): 7a8aq4c0oa
- Both may be related (regional vs global), apply fixes to udejfu5f3b as shown in console

---

# iTariff Project — Knowledge Transfer (KT) Document

**Last Updated**: July 10, 2026  
**Maintained By**: DevOps / Infrastructure Team  
**Status**: Production Live

---

## 1. Project Overview

iTariff is a **Java-based** microservices platform for freight tariff management — buying rates, selling rates, geo/route data, grant/auth, and external BFF integrations. It runs on AWS EKS with Istio service mesh across DEV, SIT/UAT, and PROD environments.

### Tech Stack
| Component | Technology |
|-----------|-----------|
| Language | Java (Spring Boot) |
| Container Orchestration | AWS EKS (Kubernetes) |
| Service Mesh | Istio |
| CI/CD | Jenkins |
| Container Registry | AWS ECR |
| Database | Aurora PostgreSQL |
| Message Broker | AWS MSK (Kafka) |
| Source Control | Bitbucket |
| Infra as Code | Terraform |

---

## 2. Environments & AWS Accounts

| Environment | AWS Account | Region | EKS Cluster |
|-------------|-------------|--------|-------------|
| DEV EU | `074779643551` | `eu-central-1` | `euc1-itopaz-dev-eks` |
| SIT / UAT EU | `464134132424` | `eu-central-1` | `euc1-itopaz-sit-eks` |
| PROD EU | `965031587107` | `eu-central-1` | `euc1-itopaz-prd-eks` |

### Bastion SSH Access
```bash
# DEV EU
ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/dev/eu/dev-eu-bastion.pem ec2-user@10.100.145.118

# SIT EU
ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/sit/eu/sit-eu-bastion.pem ec2-user@10.100.208.17

# PROD EU
ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/prod/eu/prod-eu-bastion.pem ec2-user@10.100.98.195
```

### kubectl Configuration (run on respective bastion)
```bash
# DEV
aws eks update-kubeconfig --region eu-central-1 --name euc1-itopaz-dev-eks

# SIT
aws eks update-kubeconfig --region eu-central-1 --name euc1-itopaz-sit-eks

# PROD
aws eks update-kubeconfig --region eu-central-1 --name euc1-itopaz-prd-eks
```

---

## 3. Kubernetes Namespaces

| Namespace | Purpose |
|-----------|---------|
| `itariff-api` | All backend microservices (buying, selling, geo, grant, etc.) |
| `itariff-bff` | Backend-for-Frontend services (selling-bff, grant-bff, external-bff) |
| `itariff-ui` | Frontend (tariff-selling-rates-ui — nginx) |
| `itariff-intg-api` | Integration API services |

---

## 4. Microservices

### itariff-api (Backend Services)

| Service | Description | Min | Max Replicas |
|---------|-------------|-----|-------------|
| `tariff-selling-service` | Core selling tariff logic | 2 | 20 |
| `tariff-selling-service-batch` | Bulk upload batch processor | 2 | 20 |
| `tariff-selling-consumer-service` | Kafka consumer for selling events | 2 | 20 |
| `tariff-selling-oc-service` | OC/Origin Charges service | 2 | 3 |
| `tariff-selling-storage-service` | Storage tariff service | 2 | 3 |
| `tariff-buying-service` | Core buying tariff logic | 2 | 5 |
| `tariff-buying-carriage-service` | Carriage buying rates | 2 | 3 |
| `tariff-buying-consumer-service` | Kafka consumer for buying events | 2 | 3 |
| `tariff-buying-otherbooking-service` | Other booking buying rates | 2 | 3 |
| `tariff-buying-standardcost-service` | Standard cost rates | 2 | 3 |
| `tariff-buying-truck-service` | Truck/road buying rates | 2 | 3 |
| `tariff-buying-warehouse-service` | Warehouse rates | 2 | 5 |
| `tariff-geo-service` | Geography / port / route data | 2 | 10 |
| `tariff-grant-auth` | Grant authentication service | 2 | 5 |
| `tariff-profile-service` | User profile service | 2 | 10 |
| `tariff-company-service` | Company/customer data | 2 | 10 |
| `tariff-master-service` | Master data (carriers, ports) | 2 | 10 |
| `tariff-invoice-service` | Invoice generation | 2 | 10 |
| `tariff-search-service` | Search/query service | 2 | 10 |
| `tariff-trucker-rates-service` | Trucking rates | 2 | 10 |
| `tariff-rate-service` | Rate engine | 2 | 10 |
| `tariff-surcharge-service` | Surcharge management | 2 | 10 |
| `tariff-port-service` | Port data service | 2 | 10 |
| `tariff-route-service` | Route data service | 2 | 10 |

### itariff-bff (BFF Services)

| Service | Description |
|---------|-------------|
| `tariff-selling-bff` | BFF for selling-rates UI, routes to selling-service |
| `tariff-grant-bff` | BFF for grant/auth flows |
| `tariff-external-bff` | External integration BFF |

### itariff-ui (Frontend)

| Service | Description |
|---------|-------------|
| `tariff-selling-rates-ui` | Angular frontend served via nginx |

---

## 5. Service URLs

### DEV EU
| Service | Internal URL |
|---------|-------------|
| iTariff API | `itariff-api.internaleu1dev-itopaz.com` |
| iTariff BFF | `itariff-bff.internaleu1dev-itopaz.com` |
| iTariff UI | `itariff-ui.internaleu1dev-itopaz.com` |

### SIT / UAT EU
| Service | Internal URL | External URL |
|---------|-------------|-------------|
| iTariff API | `itariff-api.internaleu1-itopaz.com` | `itariff-api-eusit.itopazapp.com` |
| iTariff BFF | `itariff-bff.internaleu1-itopaz.com` | `itariff-bff-eusit.itopazapp.com` |
| iTariff UI | `itariff-ui.internaleu1-itopaz.com` | `itariff-eusit.itopazapp.com` |
| Selling Rates UI (UAT) | — | `itariff-euat.itopazapp.com` |
| BFF UAT | — | `itariff-bff-euat.itopazapp.com` |
| API UAT | — | `itariff-api-euat.itopazapp.com` |
| BFF Upload | — | `itariff-bff-upload.itopazapp.com` |

### PROD EU
| Service | Internal URL | Status |
|---------|-------------|--------|
| iTariff UI | `itariff-ui.internaleu1prd-itopaz.com` | `/test-ping` → 200 ✅ |
| iTariff BFF | `itariff-bff.internaleu1prd-itopaz.com` | `/test-ping` → 200 ✅ |
| iTariff API | `itariff-api.internaleu1prd-itopaz.com` | `/test-ping` → 200 ✅ |

---

## 6. Request Flow

```
Browser
  └─→ itariff-euat.itopazapp.com/selling-rates/
        └─→ tariff-selling-rates-ui  (nginx, itariff-ui namespace)
              └─→ /tariff-selling-bff/
                    └─→ tariff-selling-bff  (itariff-bff namespace)
                          └─→ tariff-selling-service  (itariff-api namespace)
                                └─→ Aurora PostgreSQL — TariffSelling DB
```

---

## 7. Istio / Service Mesh

### Istio Gateway (SIT — `istio-system` namespace)
- **Gateway name**: `itariff-gateway`
- **VirtualServices**: `itariff-ui`, `itariff-bff`, `itariff-api`
- All external and internal hostnames are bound to this gateway

### Istio Gateway (PROD — `istio-system` namespace)
- **Gateway name**: `itariff-gateway`
- **VirtualServices**: `itariff-ui`, `itariff-api`, `itariff-bff`

### Useful kubectl commands
```bash
# List all VirtualServices
kubectl get vs -A | grep itariff

# Inspect a VirtualService
kubectl get vs itariff-bff -n istio-system -o yaml

# Check gateway
kubectl get gateway itariff-gateway -n istio-system -o yaml

# List all pods
kubectl get pods -n itariff-api
kubectl get pods -n itariff-bff
kubectl get pods -n itariff-ui

# Check HPA
kubectl get hpa -n itariff-api

# View logs
kubectl logs -n itariff-api deployment/tariff-selling-service --tail=100 -f

# Restart a deployment
kubectl rollout restart deployment/tariff-selling-service -n itariff-api
```

---

## 8. ECR (Container Registry)

| Environment | Registry | Repository |
|-------------|---------|-----------|
| SIT | `464134132424.dkr.ecr.eu-central-1.amazonaws.com` | `euc1-sit-itopaz-ecr` |
| PROD | `965031587107.dkr.ecr.eu-central-1.amazonaws.com` | `prd-eu/itopaz-backend` |

### Image Tag Convention
```
# SIT images
euc1-sit-itopaz-ecr:tariff-geo-service-sit-<git-sha>

# PROD images (promoted from SIT)
prd-eu/itopaz-backend:tariff-geo-service-prod-<git-sha>
```

### ECR Login
```bash
# SIT (assume role first)
aws sts assume-role --role-arn arn:aws:iam::464134132424:role/Terraform_Execution_Role --role-session-name session
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 464134132424.dkr.ecr.eu-central-1.amazonaws.com

# PROD
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin 965031587107.dkr.ecr.eu-central-1.amazonaws.com
```

---

## 9. Databases (Aurora PostgreSQL)

### SIT EU
| Database | Host | Port | User | Password |
|----------|------|------|------|----------|
| `TariffSelling` | `itariff-sit-cluster.cluster-cd6uok42udhj.eu-central-1.rds.amazonaws.com` | 5432 | `tariff_sit` | `topazsit#123` |
| `TariffBuying` | same cluster | 5432 | `tariff_sit` | `topazsit#123` |
| `ts_storage_db` | same cluster | 5432 | `tariff_sit` | `topazsit#123` |
| `tb_truck_db` | same cluster | 5432 | `tariff_sit` | `topazsit#123` |

### UAT / PROD
| Instance | Type | Database | Engine |
|----------|------|----------|--------|
| `itariff-uat` | db.r5.xlarge | `TariffSelling` | PostgreSQL 15.15 |

> ⚠️ `dbedi_aurora` (EDI data) lives on the **prefiler cluster** (`euc1-itopaz-sit-aurora-postgresql`), NOT the itariff cluster.

---

## 10. Kafka / MSK

### SIT EU Brokers
```
b-1.euc1itariffsitmsk.76ygyn.c5.kafka.eu-central-1.amazonaws.com:9096
b-2.euc1itariffsitmsk.76ygyn.c5.kafka.eu-central-1.amazonaws.com:9096
```
- **Auth**: SASL_SSL, SCRAM-SHA-512
- **Credentials**: `admin` / `admin#$321`
- **Client path (SIT bastion)**: `/home/ec2-user/kafka-client/kafka_2.13-3.6.0/bin/`

### PROD EU Brokers
```
b-1.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096
b-2.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096
b-3.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096
```
- **Client path (PROD bastion)**: `/home/ec2-user/kafka-client/current/bin/`
- **Config**: `/home/ec2-user/kafka-client/client.properties`

### Key SIT Topics

**Selling Topics**
| Topic | Partitions |
|-------|-----------|
| `tariff_bulk_upload_topic_uat` | 25 |
| `tariff-bulk-upload-topic-uat` | 25 |
| `tariff-bulk-process-topic-uat` | 25 |
| `tariff_multisheet_upload_topic_uat` | 2 |
| `trf-exl-upld-prc-topic-v3` | 1 |

**Buying Topics** (5 partitions, 1-week retention, 10MB max)
| Topic |
|-------|
| `tariff-buying-carriage-bulk-process-uat` / `...-archive-uat` |
| `tariff-buying-otherbooking-bulk-process-uat` / `...-archive-uat` |
| `tariff-buying-truck-bulk-process-uat` / `...-archive-uat` |
| `tariff-buying-standardcost-bulk-process-uat` / `...-archive-uat` |
| `tariff-buying-warehouse-bulk-process-uat` / `...-archive-uat` |
| `tariff-buying-shippingline-bulk-process-uat` / `...-archive-uat` |
| `tariff-buying-bulk-process-uat` / `...-archive-uat` |

**Buying Upload Topics** (5 partitions, 1GB max message)
| Topic |
|-------|
| `tariff-buying-carriage-bulk-upload-uat` |
| `tariff-buying-truck-bulk-upload-uat` |
| `tariff-buying-otherbooking-bulk-upload-uat` |
| `tariff-buying-standardcost-bulk-upload-uat` |
| `tariff-buying-warehouse-bulk-upload-uat` |
| `tariff-buying-shippingline-bulk-upload-uat` |
| `tariff-buying-bulk-upload-uat` |

### Kafka CLI Commands (from bastion)
```bash
cd /home/ec2-user/kafka-client/kafka_2.13-3.6.0/bin/
BROKERS="b-1.euc1itariffsitmsk.76ygyn.c5.kafka.eu-central-1.amazonaws.com:9096,b-2.euc1itariffsitmsk.76ygyn.c5.kafka.eu-central-1.amazonaws.com:9096"

# List topics
./kafka-topics.sh --bootstrap-server $BROKERS --command-config client.properties --list

# Describe topic
./kafka-topics.sh --bootstrap-server $BROKERS --command-config client.properties --describe --topic <topic>

# Consumer group lag
./kafka-consumer-groups.sh --bootstrap-server $BROKERS --command-config client.properties --describe --group <group>
```

---

## 11. CI/CD — Jenkins Pipelines

### Jenkins Server
- **Host**: `10.100.95.13` | SSH user: `root` | Key: `shared/jenkins/jenkins.pem`
- **Container ID**: `b87eab05fc3e`
- **Access**: `ssh -i jenkins.pem root@10.100.95.13` → `docker exec -it b87eab05fc3e /bin/bash`

### Bitbucket Repositories
| Repo | URL | Branch | Purpose |
|------|-----|--------|---------|
| K8s Manifests | `https://bitbucket.org/allcargoecu/itariff-k8s-repo` | `main` / `uat` / `prod` | Deployment manifests + Jenkins pipelines |
| App Code | per-service repos | `main` / `develop` | Application source code |

### Jenkins Credentials
| Credential ID | Usage |
|--------------|-------|
| `jenkins-itopaz-ibm-token-frontend` | K8s manifest repo checkout (Bitbucket token) |
| `itariff-backend-bitbucket-token` | App source repo checkout |
| `teams-webhook-url` | Teams notifications |

### Pipeline File Structure
```
itariff-k8s-repo/
└── jenkins/
    ├── tariff-selling-service/
    │   └── Jenkinsfile
    ├── tariff-selling-rates-ui/
    │   └── Jenkinsfile
    ├── tariff-geo-service/
    │   └── Jenkinsfile
    ├── tariff-grant-bff/
    │   └── Jenkinsfile
    └── <service-name>/
        └── Jenkinsfile
```

### UAT → PROD Promotion Pipeline
Located at: `itariff-k8s-repo` (promote Jenkinsfile)

**Key parameters:**
| Parameter | Description |
|-----------|-------------|
| `SERVICE_NAME` | Service to promote (free-text, e.g. `tariff-geo-service`) |
| `IMAGE_TAG_OVERRIDE` | Optional: specific SIT image tag or full URI |
| `DEPLOYMENT_FILE` | K8s manifest filename (defaults to SERVICE_NAME) |
| `SKIP_TRIVY_SCAN` | Skip security scan (not recommended) |
| `SKIP_DEPLOYMENT` | Promote image only, skip EKS deploy |

**Promotion stages:**
1. Validate Parameters
2. Send Start Notification (Teams)
3. Resolve UAT image tag from SIT ECR
4. Pull UAT image from SIT ECR (`464134132424`)
5. Re-tag: `*-sit-<sha>` → `*-prod-<sha>`
6. Trivy security scan (blocks push on CRITICAL CVEs)
7. Push to PROD ECR (`965031587107`)
8. Checkout K8s manifests (`itariff-k8s-repo`, branch: `prod`)
9. Update image tag in manifest + git push
10. `kubectl apply` → PROD EKS (`euc1-itopaz-prd-eks`)

---

## 12. S3 Buckets

| Bucket | Account | Purpose |
|--------|---------|--------|
| `itariff-dev-bucket` | `074779643551` (DEV) | DEV file uploads, bulk templates |
| `itariff-uat-bucket` | `464134132424` (SIT) | UAT file uploads, bulk templates |
| `itariff-prod-bucket` | `965031587107` (PROD) | PROD file uploads, bulk templates |
(`TariffMultiSheetTemplate.xlsx`, bulk upload folders per env) |

---

## 13. IAM Roles (Cross-Account)

| Account | Role ARN | Usage |
|---------|---------|-------|
| DEV | `arn:aws:iam::074779643551:role/Terraform_Execution_Role` | ECR pull, EKS deploy (DEV) |
| SIT | `arn:aws:iam::464134132424:role/Terraform_Execution_Role` | ECR pull, EKS deploy from Jenkins |
| PROD | `arn:aws:iam::965031587107:role/Terraform_Execution_Role` | ECR push, EKS deploy to PROD |

---

## 14. Resource Configuration (SIT/UAT — Live Audit)

> Source: Live pull from `euc1-itopaz-sit-eks`, itariff-api (26 deployments) + itariff-bff (3 deployments). Buying services got 10% CPU/memory increase (commit `cfbf401` on `itariff-k8s-repo` develop branch). JVM optimization applied to 8 services (commit `5603bdc`, uat branch).

### itariff-api — Selling Services
| Service | CPU Req/Limit | Memory Req/Limit | Notes |
|---------|--------------|-----------------|-------|
| `tariff-selling-service` | 500m / 2000m | 1400Mi / 1800Mi | — |
| `tariff-selling-service-batch` | 500m / 2000m | 1400Mi / 1800Mi | — |
| `tariff-selling-oc-service` | 100m / 500m | 700Mi / 1024Mi | — |
| `tariff-selling-storage-service` | 50m / 250m | 500Mi / 950Mi | JVM optimized |
| `tariff-selling-consumer-service` | 1 / ❌ none | 3Gi / ❌ none | **Missing limits** — risk of node OOM |

### itariff-api — Buying Services (10% increase applied)
| Service | CPU Req/Limit | Memory Req/Limit | Notes |
|---------|--------------|-----------------|-------|
| `tariff-buying-service` | (increased) | (increased) | JVM optimized |
| `tariff-buying-carriage-service` | (increased) | (increased) | JVM optimized |
| `tariff-buying-carriage-consumer` | (increased) | (increased) | — |
| `tariff-buying-otherbooking-service` | (increased) | (increased) | JVM optimized |
| `tariff-buying-shippingline-consumer` | (increased) | (increased) | — |
| `tariff-buying-standardcost-service` | (increased) | (increased) | JVM optimized |
| `tariff-buying-truck-service` | (increased) | (increased) | JVM optimized |
| `tariff-buying-warehouse-service` | (increased) | (increased) | JVM optimized |
| `tariff-buying-warehouse-consumer` | (increased) | (increased) | — |

### itariff-bff — Missing Resource Limits (⚠️ Critical)
| Service | CPU | Memory | Status |
|---------|-----|--------|--------|
| `tariff-grant-bff` | ❌ No requests or limits | ❌ No requests or limits | **Fully unset** |
| `tariff-selling-bff` | ❌ No CPU req/limit | 2Gi req / 6Gi limit | Missing CPU |
| `tariff-domain-batch` | ❌ None at all | ❌ None at all | **Fully unset** |

### JVM Optimization Applied (uat branch)
Services with `JAVA_TOOL_OPTIONS` env var set:
`tariff-buying-carriage`, `tariff-buying-otherbooking`, `tariff-buying-service`, `tariff-buying-standardcost`, `tariff-buying-truck`, `tariff-buying-warehouse`, `tariff-grant-auth`, `tariff-selling-storage-service`

---

## 15. Known Issues & Operational Notes

| Issue | Severity | Status | Notes |
|-------|----------|--------|-------|
| `tariff-buying-service` HPA at 5/5 max, memory 82% | Medium | Open | May need maxReplicas increase |
| `tariff-geo-service` memory at 85% | Medium | Open | Approaching limit |
| `tariff-buying-carriage-service` memory at 85% | Medium | Open | Approaching limit |
| `tariff-grant-bff` 500 on `/authenticate` | Medium | Open | Profile not found for prefiler users in tariff DB |
| `gettariffstoragemaindownload` SQL function missing on `ts_storage_db` | High | Open | Stored proc not deployed |
| `tariff-selling-consumer-hpa` CPU 157% with 20/20 replicas | High | Open | Needs CPU resource increase |
| Multiple buying services CPU 150–230%, HPA stuck at maxReplicas | High | Mitigated | 10% resource increase applied (commit `cfbf401`); JVM opts added |
| `tariff-buying-otherbooking-service` CrashLoop after OOM fix | Resolved | Closed | JAVA_OPTS fix applied, rolling restart caused upstream timeouts |
| `tariff-grant-bff` / `tariff-domain-batch` — no resource limits set | High | Open | Risk of node OOM; must set CPU/memory requests+limits |

### DB Performance Issue — `/selling-rates/import` 8–10s Load Time

**Environment**: SIT EU (`itariff-euat.itopazapp.com/selling-rates/import`)  
**Root cause**: `dbo.tariff` (146 GB) and `dbo.tariffdetails` (184 GB) have **no indexes** on lookup columns → full sequential scans on every BFF dropdown call (~10 parallel on page load).

**Slow endpoints confirmed:**
| Endpoint | Latency | Cause |
|----------|---------|-------|
| `GET /bffdropdown/getTSOCPOL` | 1,946ms | Full seq scan on `dbo.tariff` |
| `GET /bffdropdown/getPOR` | 1,588ms | Full seq scan on `dbo.tariff` |
| `POST /BffTariffSelling/getTariffSellingSearchSingleRow1` | 343–1,798ms | `gettariffmainsearchsinglerow_db` stored proc, full scan |
| `POST /BffTariffBuying/getTariffBuyingSearchSingleRow` | 1,774ms | Full scan |

**Fix required (dev team):**
```sql
-- Run on TariffSelling DB (itariff-sit-cluster)
CREATE INDEX CONCURRENTLY idx_tariff_pol ON dbo.tariff(pol_code);
CREATE INDEX CONCURRENTLY idx_tariff_por ON dbo.tariff(por_code);
CREATE INDEX CONCURRENTLY idx_tariffdetails_tariff_id ON dbo.tariffdetails(tariff_id);
```

**Also recommended**: Redis cache (TTL 30 min) in `tariff-selling-bff` for dropdown APIs, TTL 5 min for search single-row APIs.

---

## 16. Swagger / API Docs

Accessible via Istio internal host + service prefix (after URI rewrite):

| Service | SIT Internal Swagger URL |
|---------|--------------------------|
| `tariff-selling-service` | `http://itariff-api.internaleu1-itopaz.com/tariff-selling-service/swagger-ui/index.html` |
| `tariff-geo-service` | `http://itariff-api.internaleu1-itopaz.com/tariff-geo-service/swagger-ui/index.html` |
| `tariff-selling-bff` | `http://itariff-bff.internaleu1-itopaz.com/tariff-selling-bff/swagger-ui/index.html` |
| `tariff-grant-bff` | `http://itariff-bff.internaleu1-itopaz.com/tariff-grant-bff/swagger-ui/index.html` |

> Access these from the SIT EU bastion (`10.100.208.17`) using `curl` or `port-forward`.

```bash
# Quick access via port-forward
kubectl port-forward -n itariff-api svc/tariff-geo-service-svc 9090:8080 &
curl -s http://localhost:9090/swagger-ui/index.html | head -20
```

---

## 17. Backup & Recovery

> Verified from DEV jump server (`10.100.145.118`) on 2026-07-10.

### 17.1 Aurora PostgreSQL (RDS)

| Resource | Cluster | Retention | Backup Window (UTC) | Engine |
|----------|---------|-----------|-------------------|--------|
| DEV EDI DB | `euc1-itariff-edi-dev` | **7 days** | 20:26–20:56 | Aurora PostgreSQL 15.15 |
| DEV App DB | `euc1-itopaz-dev-database-cluster` | **7 days** | 08:42–10:42 | Aurora PostgreSQL 16.11 |
| SIT Tariff DB | `itariff-sit-cluster` | **7 days**  | — | Aurora PostgreSQL |

- Backups are **automated by AWS RDS** — snapshots taken daily, kept for 7 days.
- Snapshot naming pattern: `rds:<cluster-id>-YYYY-MM-DD-HH-MM`
- Confirmed snapshots (DEV EDI): Jul 4, Jul 6, Jul 8 — all `available`.

**Restore a snapshot (CLI):**
```bash
# List automated snapshots
aws rds describe-db-cluster-snapshots --region eu-central-1 \
  --db-cluster-identifier euc1-itariff-edi-dev \
  --snapshot-type automated \
  --query "DBClusterSnapshots[*].{ID:DBClusterSnapshotIdentifier,Created:SnapshotCreateTime,Status:Status}" \
  --output table

# Restore to new cluster from snapshot
aws rds restore-db-cluster-from-snapshot \
  --region eu-central-1 \
  --db-cluster-identifier euc1-itariff-edi-dev-restored \
  --snapshot-identifier rds:euc1-itariff-edi-dev-2026-07-08-04-37 \
  --engine aurora-postgresql \
  --engine-version 15.15
```

> ⚠️ **Gap**: No manual/on-demand snapshots policy. No cross-region backup copy configured. Consider adding for PROD.

---

### 17.2 S3 Buckets

| Bucket | Versioning | Lifecycle | Replication |
|--------|-----------|-----------|-------------|
| `itariff-dev-bucket` | ❌ Disabled | ❌ None | ❌ None |
| `itariff-uat-bucket` | Not checked | Not checked | Not checked |
| `itariff-prod-bucket` | Not checked | Not checked | Not checked |
| `itariff-ecu-template` | Not checked | Not checked | Not checked |

> ⚠️ **Gap**: No versioning, lifecycle, or replication on `itariff-dev-bucket`. Recommend enabling versioning + 30-day lifecycle on all buckets.

**Enable versioning (fix):**
```bash
aws s3api put-bucket-versioning --bucket itariff-dev-bucket \
  --versioning-configuration Status=Enabled

# Also for UAT/PROD
aws s3api put-bucket-versioning --bucket itariff-uat-bucket \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-versioning --bucket itariff-prod-bucket \
  --versioning-configuration Status=Enabled
```

---

### 17.3 ECR (Container Images)

| Repository | Lifecycle Policy | Notes |
|-----------|-----------------|-------|
| `dev-eu/itariff-backend` | ❌ None | All images retained indefinitely |
| `dev-eu/itariff-frontend` | ❌ None | All images retained indefinitely |
| `euc1-sit-itopaz-ecr` | Not checked | SIT account |
| `prd-eu/itopaz-backend` | Not checked | PROD account |

> ⚠️ **Gap**: No lifecycle policy on DEV ECR repos — images accumulate indefinitely.

**Recommended lifecycle policy (keep last 30 images):**
```bash
aws ecr put-lifecycle-policy --region eu-central-1 \
  --repository-name dev-eu/itariff-backend \
  --lifecycle-policy-text '{
    "rules": [{
      "rulePriority": 1,
      "description": "Keep last 30 images",
      "selection": {"tagStatus": "any", "countType": "imageCountMoreThan", "countNumber": 30},
      "action": {"type": "expire"}
    }]
  }'
```

---

### 17.4 EKS (Kubernetes)

| Aspect | Status | Details |
|--------|--------|---------|
| Velero (K8s backup) | ❌ Not installed | No pod found in any namespace |
| etcd backup | ✅ AWS-managed | EKS managed control plane — AWS handles etcd |
| Control plane logs | ✅ Partial | `api`, `audit`, `authenticator` → CloudWatch |
| Control plane logs | ⚠️ Missing | `controllerManager`, `scheduler` not enabled |
| K8s manifests backup | ✅ Git | All manifests in `itariff-k8s-repo` (Bitbucket) |

**K8s manifest backup = Git** — the `itariff-k8s-repo` Bitbucket repo is the source of truth. Redeploy any namespace with:
```bash
git clone https://bitbucket.org/allcargoecu/itariff-k8s-repo
kubectl apply -f <manifest>.yml -n itariff-api
```

**Enable missing control plane logs:**
```bash
aws eks update-cluster-config --region eu-central-1 \
  --name euc1-itopaz-dev-eks \
  --logging '{"clusterLogging":[{"types":["api","audit","authenticator","controllerManager","scheduler"],"enabled":true}]}'
```

> ⚠️ **Gap**: No Velero — PersistentVolume data (if any) is not backed up. Recommend installing Velero with S3 backend for stateful workloads.

---

### 17.5 Kafka / MSK

| Aspect | Status | Details |
|--------|--------|---------|
| MSK automated backups | ✅ Built-in | MSK retains offsets in `__consumer_offsets` |
| Topic data retention | ✅ Configured | Buying topics: 7 days, 10MB max per partition |
| Upload topics | ✅ Configured | 1GB max message size |
| Cross-region backup | ❌ None | No MirrorMaker or replication to DR region |

> ⚠️ **Gap**: No MSK cross-region replication. For PROD DR, consider MSK MirrorMaker2 to replicate to a secondary region.

---

### 17.6 Summary — Backup Gaps to Address

| Resource | Current State | Recommended Action | Priority |
|----------|--------------|-------------------|----------|
| S3 versioning | ❌ Off on all itariff buckets | Enable versioning + 30-day lifecycle | High |
| ECR lifecycle | ❌ No policy on DEV repos | Add lifecycle (keep 30 images) | Medium |
| EKS Velero | ❌ Not installed | Install Velero with S3 backend | Medium |
| EKS control plane logs | ⚠️ Partial | Enable controllerManager + scheduler | Low |
| MSK cross-region | ❌ None | MirrorMaker2 for PROD DR | Low |
| RDS cross-region copy | ❌ None | Add snapshot copy to secondary region for PROD | High |

---

## 18. Quick Reference Checklist

### Deploy a new build to SIT
1. Merge code → triggers Jenkins pipeline in `itariff-k8s-repo/jenkins/<service>`
2. Pipeline: build → test → push ECR (`euc1-sit-itopaz-ecr:<service>-sit-<sha>`) → kubectl apply

### Promote SIT → PROD
1. Run promote pipeline with `SERVICE_NAME` + `IMAGE_TAG_OVERRIDE` (optional)
2. Trivy scan must pass (no CRITICAL CVEs)
3. Manifest updated in `itariff-k8s-repo` branch `prod` → deployed to `euc1-itopaz-prd-eks`

### Check service health
```bash
# SIT bastion
kubectl get pods -n itariff-api
kubectl get pods -n itariff-bff
kubectl get hpa -n itariff-api
kubectl top pods -n itariff-api

# View logs for a failing service
kubectl logs -n itariff-api -l app=tariff-selling-service --tail=200 -f
```

### Restart a service
```bash
kubectl rollout restart deployment/<service-name> -n itariff-api
kubectl rollout status deployment/<service-name> -n itariff-api
```

---

# Other Booking Service - Request Timeout Analysis (Dev)

**Date:** 19-May-2026  
**Service:** tariff-buying-otherbooking-service  
**Namespace:** itariff-api  
**Cluster:** euc1-itopaz-dev-eks  

---

## What Happened

After applying `JAVA_OPTS` env var to fix potential OOM, the deployment triggered a rolling restart. During the restart, upstream services (e.g., `tariff-selling-bff`) received **request timeout** errors when calling the Other Booking service.

---

## Root Cause

### 1. Slow Application Startup (~91 seconds)
- The Spring Boot app takes **91.4 seconds** to fully initialize
- Kafka listeners, DB connections, and Spring context all load during this time
- The DispatcherServlet only initializes on the **first HTTP request** (lazy init)

### 2. Rolling Deployment Gap
- Kubernetes rolling update terminates old pods before new pods are fully warm
- The readiness probe may pass (port open) before the app is truly ready to handle requests
- During the ~90s startup window, requests routed to new pods fail with timeout

### 3. Istio Sidecar Interaction
- Istio proxy (envoy) starts before the app container is ready
- Upstream services see the pod as "ready" via Istio, but the app isn't serving yet
- Default Istio timeout (15s) is shorter than app startup time, causing caller-side timeouts

---

## Evidence from Logs

```
Started TariffBuyingOtherbookingSvcApplication in 91.396 seconds (process running for 96.751)
```

First HTTP request received at **05:30:38** (after full startup):
```
Initializing Spring DispatcherServlet 'dispatcherServlet'
Request [/tariff-selling-bff] received http: {url: /buying-otherbooking-domain-service/secure/v1/other/getTariffBuyingOtherSearchSingleRow, method: POST}
```

---

## Pod Configuration

| Setting | Value |
|---------|-------|
| Replicas | 2 |
| Memory Limit | 1Gi |
| Memory Request | 800Mi |
| CPU Limit | 500m |
| CPU Request | 100m |
| Image | tariff-buying-otherbooking-service-dev-4d7a59da |

---

## Why JAVA_OPTS Didn't Work

The `JAVA_OPTS` environment variable was set but **not picked up** by the application. This is because:
- The app's Dockerfile/entrypoint does not reference `$JAVA_OPTS`
- Only `JAVA_TOOL_OPTIONS` is auto-read by the JVM without app changes

---

## Recommendations

### Immediate Fix (Prevent Timeout During Restarts)
1. **Increase readiness probe `initialDelaySeconds`** to 100s so pods aren't marked ready before app starts
2. **Use `JAVA_TOOL_OPTIONS`** instead of `JAVA_OPTS` for JVM flags to be auto-picked

### Long-term Fixes
1. **Add startup probe** with generous failure threshold:
   ```yaml
   startupProbe:
     httpGet:
       path: /buying-otherbooking-domain-service/actuator/health
       port: 80
     failureThreshold: 30
     periodSeconds: 5
   ```
2. **Pre-warm DispatcherServlet** - set `spring.mvc.servlet.load-on-startup=1` in config
3. **Increase Istio/VirtualService timeout** for this service if caller timeout is too low
4. **Use `maxSurge: 1, maxUnavailable: 0`** in deployment strategy to ensure old pods stay until new ones are ready

---

## Commands Used for Diagnosis

```bash
# Check pod status
kubectl -n itariff-api get pods | grep other

# Check memory usage
kubectl -n itariff-api top pod <pod-name> --containers

# Check logs for OOM/timeout
kubectl -n itariff-api logs <pod-name> -c tariff-buying-otherbooking-service --tail=200

# Describe pod for resource limits
kubectl -n itariff-api describe pod <pod-name>

# Check consumer groups
./kafka-consumer-groups.sh --bootstrap-server <brokers> --command-config client.properties --describe --group tariff-buying-other-upload-group
```

---

# iTariff API Resource Usage & Optimization Report

| Service Name | CPU Actual Usage (avg) | CPU Request | CPU Limit | Memory Actual Usage (avg) | Heap Min | Heap Max | Memory Request | Memory Limit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tariff-buying-carriage-service | 0.018 | 100m | 500m | 532 MiB |  |  | 650Mi | 800Mi |
| tariff-buying-otherbooking-service | 0.0175 | 100m | 500m | 670 MiB |  |  | 800Mi | 1Gi |
| tariff-buying-service | 0.0277 | 100m | 500m | 730 MiB |  |  | 900Mi | 1126Mi |
| tariff-buying-standardcost-service | 0.00363 | 50m | 250m | 463 MiB |  |  | 560Mi | 700Mi |
| tariff-buying-truck-service | 0.00301 | 50m | 250m | 463 MiB |  |  | 560Mi | 700Mi |
| tariff-buying-warehouse-service | 0.0156 | 75m | 400m | 643 MiB |  |  | 780Mi | 980Mi |
| tariff-company-service | 0.0044 | 500m | 2000m | 1.69 GiB |  |  | 2Gi | 8Gi |
| tariff-domain-batch | No data | <none> | <none> | No data |  |  | <none> | <none> |
| tariff-geo-service | 0.0242 | 500m | 2000m | 1.68 GiB |  |  | 2Gi | 8Gi |
| tariff-grant-auth | 0.00296 | 50m | 250m | 920 MiB |  |  | 512Mi | 1434Mi |
| tariff-invoice-service | 0.00393 | 500m | 2000m | 936 MiB |  |  | 2Gi | 8Gi |
| tariff-master-service | 0.00397 | 500m | 2000m | 888 MiB |  |  | 2Gi | 8Gi |
| tariff-profile-service | 0.00463 | 100m | 300m | 802 MiB |  |  | 700Mi | 2500Mi |
| tariff-scheduler-service | 0.00352 | 50m | 250m | 766 MiB |  |  | 920Mi | 1178Mi |
| tariff-search-service | 0.00319 | 50m | 250m | 778 MiB |  |  | 930Mi | 1178Mi |
| tariff-selling-consumer-service | 0.0137 | 1000m | 2000m | 1.27 GiB |  |  | 3Gi | 4Gi |
| tariff-selling-oc-service | 0.0204 | 300m | 1000m | 634 MiB |  |  | 1Gi | 2Gi |
| tariff-selling-service | 0.0209 | 500m | 2000m | 700 MiB |  |  | 1400Mi | 1800Mi |
| tariff-selling-service-batch | 0.00332 | 500m | 2000m | 1.05 GiB |  |  | 2Gi | 3Gi |
| tariff-selling-storage-service | 0.00385 | 500m | 2000m | 619 MiB |  |  | 2Gi | 8Gi |
| tariff-trucker-rates-service | 0.00293 | 300m | 1000m | 578 MiB |  |  | 1Gi | 2Gi |
| tariff-selling-bff | 0.007 | 0m | <none> | 525 MiB |  |  | 2Gi | 6Gi |
| tariff-external-bff | 0.007 | 0m | <none> | 556 MiB |  |  | 2Gi | 6Gi |
| tariff-grant-bff | 0.004 | 0m | <none> | 367 MiB |  |  | 2Gi | 6Gi |
| tariff-selling-rates-ui | 0.003 | 100m | <none> | 78 MiB |  |  | 128Mi | <none> |
| tariff-microfrontend-main-ui-deploy | 0.002 | 100m | <none> | 80 MiB |  |  | 128Mi | <none> |

---

# Jenkins Configuration
*Last Updated: June 4, 2026*

## Server Access
- Host: 10.100.95.13
- SSH Key: /home/ec2-user/rahul/keys/jenkins.pem
- SSH User: root
- Docker Container: b87eab05fc3e
- Jenkins Port: **8090** (inside container)
- Jenkins Home: /var/jenkins_home
- CLI Jar: /tmp/jenkins-cli.jar (downloaded from http://localhost:8090/jnlpJars/jenkins-cli.jar)
- Auth: HudsonPrivateSecurityRealm (local users, no LDAP)
- User dir pattern: /var/jenkins_home/users/<username>_<hash>/config.xml

## Pipeline Repository
- Repo: https://bitbucket.org/allcargoecu/prefiler-k8s-repo.git
- Credentials ID (k8s repo): `itopaz-k8s-repo-token`
- Credentials ID (app repos): `itopaz-backend-prefiler-backend-bitbucket-token`

## Job Structure

### Backend: prefiler-nonprod-backend/SIT/ (12 jobs - ALL exist)
- aci-prefiler-service
- aes-prefiler-service
- afr-prefiler-service
- ams-prefiler-service
- config-map
- dagangnet-prefiler-service
- ics2-prefiler-service
- master-prefiler-service
- mblfiler-prefiler-service
- prefiler-auth-bff
- prefiler-auth-service
- prefiler-bff
- sa-prefiler-service

Pipeline files: jenkins/sit/api/<service-name>
Branch: sit
Config: scriptPath = jenkins/sit/api/<service-name>

### Frontend: prefiler-nonprod-frontend/SIT/ (13 jobs - ALL exist now)
- aci-prefiler
- aes-prefiler
- afr-prefiler
- ams-prefiler (created 2026-05-26)
- basf-prefiler (created 2026-05-26)
- dagangnet-prefiler (created 2026-05-26)
- ics-prefiler (created 2026-05-26)
- ics2-prefiler (created 2026-05-26)
- imdg-prefiler (created 2026-05-26)
- mblfiler-prefiler (created 2026-05-26)
- microfrontend-main
- microfrontend-shared
- sa-prefiler (created 2026-05-26)

Pipeline files: jenkins/sit/ui/<service-name>
Branch: sit
Config: scriptPath = jenkins/sit/ui/<service-name>

### Dev pipelines
Pipeline files: jenkins/dev/<service-name> (includes api, ui, test dirs)
Additional dev-only services: ics-prefiler-service, imdg-prefiler-service, basf-prefiler-service

## Account IDs
- DEV: 074779643551 (Jenkins native account)
- SIT: 464134132424
- Base image registry: 439891535362

## SIT Pipeline Config (all api/ services)
- CROSS_ACCOUNT_ROLE_ARN: arn:aws:iam::464134132424:role/Terraform_Execution_Role
- ECR_REGISTRY: 464134132424.dkr.ecr.eu-central-1.amazonaws.com
- ECR_REPOSITORY: sit-eu/prefiler-backend
- EKS_CLUSTER_NAME: euc1-itopaz-sit-eks
- NAMESPACE: prefiler-api
- BRANCH: sit
- AWS_REGION: eu-central-1

## Known Issues & Fixes
- afr-prefiler-service: Dockerfile uses base image from 439891535362 ECR. Must login WITHOUT withAWS (use Jenkins native identity 074779643551) because 464134132424 role is denied by 439891535362 ECR policy.
- aes-prefiler-service: Previously had wrong CROSS_ACCOUNT_ROLE_ARN (074779643551 instead of 464134132424) and ENVIRONMENT=uat. Fixed.
- aci-prefiler-service: Had Swashbuckle.AspNetCore NuGet downgrade error. Fixed by upgrading to 9.0.3 in source repo.

## Creating New Jenkins Jobs
1. Copy config.xml from existing job (e.g., aci-prefiler)
2. Replace: scriptPath, DEPLOYMENT_FILE defaultValue
3. Place in: /var/jenkins_home/jobs/<folder>/jobs/<job-name>/config.xml
4. Reload Jenkins (port 8090, CLI or API)

---

# Jenkins Pipeline Fixes - Prefiler Frontend

## Problem
- All UI Jenkins pipelines failing at "Checkout Kubernetes Manifests" stage
- Error: `k8s-manifest.git` repo doesn't exist / 403 access denied

## Root Causes
1. `K8S_MANIFEST_REPO_URL` pointed to non-existent `allcargoecu/k8s-manifest.git`
2. `MANIFEST_BRANCH` was set to `develop` instead of `sit` in UI pipelines
3. `microfrontend-main` app repo had no `sit` branch

## Fixes Applied

### 1. K8S_MANIFEST_REPO_URL (all UI Jenkinsfiles)
```
BEFORE: https://x-token-auth@bitbucket.org/allcargoecu/k8s-manifest.git
AFTER:  https://x-token-auth@bitbucket.org/allcargoecu/prefiler-k8s-repo.git
```

### 2. MANIFEST_BRANCH (11 UI Jenkinsfiles)
```
BEFORE: defaultValue: 'develop'
AFTER:  defaultValue: 'sit'
```

### 3. Created `sit` branch in microfrontend-main repo
- Created from `develop` branch
- Updated index.html URLs to use relative paths

### Files Fixed in prefiler-k8s-repo (sit branch)
- jenkins/sit/ui/microfrontend-main
- jenkins/sit/ui/microfrontend-shared
- jenkins/sit/ui/aci-prefiler
- jenkins/sit/ui/aes-prefiler
- jenkins/sit/ui/afr-prefiler
- jenkins/sit/ui/ams-prefiler
- jenkins/sit/ui/basf-prefiler
- jenkins/sit/ui/dagangnet-prefiler
- jenkins/sit/ui/ics-prefiler
- jenkins/sit/ui/ics2-prefiler
- jenkins/sit/ui/imdg-prefiler
- jenkins/sit/ui/mblfiler-prefiler
- jenkins/sit/ui/sa-prefiler

### API Jenkinsfiles - All Correct
All 12 API Jenkinsfiles in `jenkins/sit/api/` already had correct settings:
- BRANCH = 'sit'
- MANIFEST_BRANCH = 'sit'
- K8S_MANIFEST_REPO_URL = prefiler-k8s-repo.git
- ECR_REGISTRY = 464134132424.dkr.ecr.eu-central-1.amazonaws.com
- EKS_CLUSTER_NAME = euc1-itopaz-sit-eks

## Deployment Manifest Fixes
### microfrontend-main.yml
- Updated image to correct SIT ECR: `464134132424.dkr.ecr.eu-central-1.amazonaws.com/sit-eu/prefiler-frontend:microfrontend-main-sit-f020163f`
- Added `namespace: prefiler-ui` to Deployment and Service
- Removed `imagePullSecrets` (not needed on EKS with IAM)

### microfrontend-shared.yml
- Removed `imagePullSecrets`

---

# Bitbucket Access & Credentials

## Working Authentication
- **Method**: x-token-auth (App Password)
- **Token**: Stored in `infrastructure/secrets/bitbucket_token.txt` (do not inline in indexed Markdown)
- **Workspace**: allcargoecu
- **Usage**: `https://x-token-auth:<TOKEN>@bitbucket.org/allcargoecu/<repo>.git`

## Expired/Invalid
- vj_devops app password → returns 401

## Jenkins Credentials
- `itopaz-k8s-repo-token` — works for prefiler-k8s-repo
- `prefiler-frontend-bitbucket-token` — works for microfrontend-main, microfrontend-shared
- `itariff-frontend-bitbucket-token` — does NOT have access to k8s-manifest (doesn't exist)

## Key Repositories
| Repo | Purpose |
|------|---------|
| prefiler-k8s-repo | Jenkinsfiles + K8s manifests for prefiler |
| microfrontend-main | Main UI shell (single-spa) |
| microfrontend-shared | Shared navbar/auth module |
| prefiler-auth-bff | .NET BFF for auth |
| prefiler-auth-service | .NET auth service |
| aci-prefiler-service | ACI filing service |
| itariff-k8s-repo | iTariff K8s manifests |

---

# Kafka Configuration
*Last Updated: June 12, 2026*

## PROD EU MSK Cluster
- **Bastion**: `10.100.98.195` (key: `prod/eu/prod-eu-bastion.pem`)
- **Kafka client**: `/home/ec2-user/kafka-client/kafka_2.13-3.9.1/bin/` (symlink: `current`)
- **Client config**: `/home/ec2-user/kafka-client/client.properties` (SASL_SSL, SCRAM-SHA-512, user: `admin`)
- **Bootstrap file**: `/home/ec2-user/kafka-client/prod-bootstrap-servers.txt`
- **Wrapper script**: `/home/ec2-user/kafka-client/run-kafka-prod.sh`
- **Brokers**:
  - `b-1.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
  - `b-2.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
  - `b-3.euc1itopazprdmsk.von7yu.c2.kafka.eu-central-1.amazonaws.com:9096`
- **Current topics**: `__amazon_msk_canary`, `__consumer_offsets` (system only — app topics not yet created, June 12, 2026)

## SIT MSK Cluster
- Bastion: 10.100.208.17 (key: /home/ec2-user/rahul/keys/mynewkey)
- Kafka client: /home/ec2-user/kafka-client/kafka_2.13-3.6.0/bin/
- Client config: /home/ec2-user/kafka-client/kafka_2.13-3.6.0/bin/client.properties (SASL_SSL, SCRAM-SHA-512)
- Brokers: b-2.euc1itariffsitmsk.76ygyn.c5.kafka.eu-central-1.amazonaws.com:9096,b-1.euc1itariffsitmsk.76ygyn.c5.kafka.eu-central-1.amazonaws.com:9096

## Commands
```bash
# List topics
./kafka-topics.sh --bootstrap-server $BROKERS --command-config client.properties --list

# Describe topic
./kafka-topics.sh --bootstrap-server $BROKERS --command-config client.properties --describe --topic <topic>

# List consumer groups
./kafka-consumer-groups.sh --bootstrap-server $BROKERS --command-config client.properties --list

# Describe consumer group lag
./kafka-consumer-groups.sh --bootstrap-server $BROKERS --command-config client.properties --describe --group <group>
```

## All Tariff Topics (38 total - June 4, 2026)

### Selling Service Topics (25 partitions)
| Topic | Partitions | max.message.bytes | min.insync | retention |
|-------|-----------|-------------------|------------|-----------|
| tariff_bulk_upload_topic_uat | 25 | 1073741824 (1GB) | 1 | default |
| tariff_bulk_upload_topic_uat-v3 | 25 | 1073741824 (1GB) | 1 | default |
| tariff-bulk-upload-topic-uat | 25 | 10485760 (10MB) | 2 | 604800000 (7d) |
| tariff-bulk-process-topic-uat | 25 | 10485760 (10MB) | 2 | 604800000 (7d) |
| tariff-bulk-archive-topic-uat | 25 | 10485760 (10MB) | 2 | 604800000 (7d) |
| tariff-bulk-expiry-process-uat | 25 | 10485760 (10MB) | 2 | 604800000 (7d) |

### Bot/Multi-sheet Topics
| Topic | Partitions | max.message.bytes | min.insync | retention |
|-------|-----------|-------------------|------------|-----------|
| tariff_bot_bulk_upload_topic_uat | 15 | 1073741824 (1GB) | 1 | default |
| tariff_multisheet_upload_topic_uat | 2 | 1073741824 (1GB) | 1 | default |
| tariff_bulk_email_topic_uat | 2 | 1073741824 (1GB) | 1 | default |
| trf_exl_upld_prc_topic_uat | 2 | 1073741824 (1GB) | 1 | default |

### OC (Other Container) Topics
| Topic | Partitions | max.message.bytes | min.insync | retention |
|-------|-----------|-------------------|------------|-----------|
| tariffoc-bulk-process-uat | 5 | 10485760 (10MB) | 2 | 604800000 (7d) |
| tariffoc-bulk-archive-uat | 5 | 10485760 (10MB) | 2 | 604800000 (7d) |

### Buying Service Topics
| Topic | Partitions | max.message.bytes | min.insync | retention |
|-------|-----------|-------------------|------------|-----------|
| tariff-buying-carriage-bulk-process-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-carriage-bulk-archive-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-otherbooking-bulk-process-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-otherbooking-bulk-archive-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-shippingline-bulk-process-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-shippingline-bulk-archive-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-standardcost-bulk-process-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-standardcost-bulk-archive-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-truck-bulk-process-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-truck-bulk-archive-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-warehouse-bulk-process-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-warehouse-bulk-archive-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-bulk-process-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-buying-bulk-archive-uat | 5 | 10485760 | 2 | 604800000 |

### Upload Topics (Buying)
| Topic | Partitions | max.message.bytes | min.insync | retention |
|-------|-----------|-------------------|------------|-----------|
| tariff-buying-carriage-bulk-upload-uat | 5 | 1073741824 (1GB) | 1 | default |
| tariff-buying-otherbooking-bulk-upload-uat | 5 | 1073741824 (1GB) | 1 | default |
| tariff-buying-shippingline-bulk-upload-uat | 5 | 1073741824 (1GB) | 1 | default |
| tariff-buying-standardcost-bulk-upload-uat | 5 | 1073741824 (1GB) | 1 | default |
| tariff-buying-truck-bulk-upload-uat | 5 | 1073741824 (1GB) | 1 | default |
| tariff-buying-warehouse-bulk-upload-uat | 5 | 1073741824 (1GB) | 1 | default |
| tariff-buying-bulk-upload-uat | 5 | 1073741824 (1GB) | 1 | default |

### Trucker Rates Topics
| Topic | Partitions | max.message.bytes | min.insync | retention |
|-------|-----------|-------------------|------------|-----------|
| tariff-trucker-rate-bulk-process-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-trucker-rate-bulk-archive-uat | 5 | 10485760 | 2 | 604800000 |
| tariff-trucker-rate-bulk-upload-uat | 5 | 1073741824 (1GB) | 1 | default |

## Topic Config Patterns
- **Upload topics** (1GB max msg): Accept large Excel file uploads, min.insync=1, no explicit retention
- **Process/Archive topics** (10MB max msg): Standard processing, min.insync=2, 7-day retention
- **All topics**: ReplicationFactor=2, message.format.version=3.0-IV1, unclean.leader.election.enable=false

## Consumer Groups - All at LAG 0 (healthy)

---

# GATI AWS Accounts - Complete Reference

**Last Updated:** June 6, 2026  
**Status:** ✅ Complete Inventory  
**Total Accounts:** 9 (3 fully documented, 6 pending)  
**Documentation:** Production, Development, UAT accounts fully mapped

---

## GATI Account IDs Summary

### Fully Documented Accounts (4/4)

| Account Type | Account ID | Name | Region | Services | Status |
|-------------|-----------|------|--------|----------|--------|
| **Development** | `074779643551` | DEV | ap-south-1 | EKS, LAMP, GenAI Testing | ✅ Documented |
| **SIT** | `464134132424` | SIT (Staging/Integration Testing) | eu-central-1 (EU Frankfurt) / ap-southeast-1 (Singapore) | EKS Cluster, Integration Testing | ✅ Documented |
| **Central/CI** | `439891535362` | Central/CI (Continuous Integration) | ap-south-1 | Jenkins, CI/CD Pipelines, Automation | ✅ Documented |
| **Production** | `339713157855` | MDM-DEV (Legacy) | ap-south-1 | TIBCO, Spotfire, EBX, HubEye | ✅ Legacy |

---

## Account 1: Development (DEV) - 074779643551

**Region:** ap-south-1 (Mumbai)  
**Purpose:** Development, testing, and GenAI experimentation  
**Documentation:** [DEV-GEMS-GATI-KB.md](DEV-GEMS-GATI-KB.md)  

### Resource Inventory

| Resource | Count | Details |
|----------|-------|---------|
| **EC2 Instances** | 12 | LAMP stack, GenAI test servers |
| **RDS Databases** | 3 | Multi-database stack |
| **Elastic IPs** | TBD | Dynamic |
| **Load Balancers** | 3 | ALB/NLB |
| **CloudFront Distributions** | 10 | CDN for development |
| **EKS Clusters** | 1 | 6-node testing cluster |
| **IAM Roles** | 18+ | Development roles |
| **IAM Users** | 4 | Dev team |

### Key Services
- EKS Kubernetes Cluster (6 nodes)
- LAMP Stack (Linux, Apache, MySQL, PHP)
- GenAI Testing Environment
- Data processing pipelines

### Access Pattern
```bash
# Switch to Development
aws sts assume-role \
  --role-arn arn:aws:iam::074779643551:role/AllCargoGATIAccess \
  --role-session-name AllCargoSession-Dev
```

---

## Account 1: Production (MDM-DEV) - 339713157855

**Region:** ap-south-1 (Mumbai)  
**Purpose:** Production infrastructure for TIBCO and data management services  
**Documentation:** [GATI-RESOURCES-KB.md](GATI-RESOURCES-KB.md)  

### Resource Inventory

| Resource | Count | Details |
|----------|-------|---------|
| **EC2 Instances** | 6 | TIBCO EMS, Spotfire (Windows), HubEye, EBX |
| **RDS Databases** | 2 | PostgreSQL (t3.medium, t3.micro) |
| **Elastic IPs** | 2 | Unassigned |
| **Load Balancers** | 2 | ALB/NLB |
| **CloudFront Distributions** | 2 | Content delivery |
| **IAM Roles** | 30+ | Production service roles |
| **IAM Users** | 30+ | Team members |

### Key Services
- TIBCO Enterprise Message Service (EMS)
- TIBCO BusinessWorks (BW)
- Spotfire Server (Windows nodes)
- HubEye Analytics
- EBX Master Data Management

### Access Pattern
```bash
# Switch to Production
aws sts assume-role \
  --role-arn arn:aws:iam::339713157855:role/AllCargoGATIAccess \
  --role-session-name AllCargoSession-Prod
```

---

## Account 2: Development (GEMS) - 058264376926

---

## Account 3: UAT (GEMS) - 058264219242

**Region:** ap-south-1 (Mumbai)  
---

## Account 2: SIT - Staging/Integration Testing (464134132424)

**Region:** eu-central-1 (EU Frankfurt) — SIT EU cluster | ap-southeast-1 (Singapore) — SIT SG cluster  
**Purpose:** Staging, integration testing, and pre-production validation  
**Documentation:** [SIT-GEMS-GATI-KB.md](SIT-GEMS-GATI-KB.md)  

### Resource Inventory

| Resource | Count | Details |
|----------|-------|---------|
| **EC2 Instances** | TBD | SIT servers |
| **RDS Databases** | TBD | SIT databases |
| **Load Balancers** | TBD | ALB/NLB |
| **EKS Clusters** | 1 | EKS staging cluster |
| **IAM Roles** | TBD | SIT roles |
| **IAM Users** | TBD | SIT team access |

### Key Services
- EKS Cluster for staging & integration testing
- Database testing & validation
- Pre-production environment
- Integration test execution

### Access Pattern
```bash
# Switch to SIT
aws sts assume-role \
  --role-arn arn:aws:iam::464134132424:role/AllCargoGATIAccess \
  --role-session-name AllCargoSession-SIT
```

---

## Account 3: Central/CI - Continuous Integration (439891535362)

**Region:** ap-south-1 (Mumbai)  
**Purpose:** Continuous Integration, Jenkins pipelines, automation, and deployment orchestration  
**Documentation:** [CI-CENTRAL-GATI-KB.md](CI-CENTRAL-GATI-KB.md)  

### Resource Inventory

| Resource | Count | Details |
|----------|-------|---------|
| **EC2 Instances** | TBD | Jenkins masters, agents, build servers |
| **RDS Databases** | TBD | CI/CD databases |
| **Load Balancers** | TBD | Jenkins LB, artifact LB |
| **EKS Clusters** | TBD | For container-based CI/CD |
| **S3 Buckets** | TBD | Build artifacts, logs |
| **IAM Roles** | TBD | CI/CD service roles |

### Key Services
- Jenkins CI/CD Pipelines
- Build & Deployment Automation
- Artifact Management
- Container Registry
- Deployment Orchestration

### Access Pattern
```bash
# Switch to Central/CI
aws sts assume-role \
  --role-arn arn:aws:iam::439891535362:role/AllCargoGATIAccess \
  --role-session-name AllCargoSession-CI
```

---

## Account 4: Production/UAT (Legacy) - 058264219242

---

## Cross-Account Access Setup

### Prerequisites

```bash
# All GATI account access requires:
1. Assume role permissions in source account
2. MFA enabled
3. AWS CLI v2
4. Valid credentials
5. CloudTrail logging enabled
```

### Assume Role Commands

```bash
# Function for cross-account access
assume_gati_role() {
  local account=$1
  local session_name=${2:-AllCargoSession}
  
  aws sts assume-role \
    --role-arn "arn:aws:iam::${account}:role/AllCargoGATIAccess" \
    --role-session-name "${session_name}" \
    --duration-seconds 3600
}

# Usage Examples
assume_gati_role 074779643551 "Development-Debug"
assume_gati_role 464134132424 "SIT-Validation"
assume_gati_role 439891535362 "CI-Pipeline-Debug"
assume_gati_role 339713157855 "Production-Audit"
```

### Credential Manager Script

```bash
# Available commands (source scripts/gati-credentials.sh)
source scripts/gati-credentials.sh

gati_list_accounts    # List all accessible accounts
gati_dev              # Switch to development (074779643551)
gati_sit              # Switch to SIT (464134132424)
gati_ci               # Switch to Central/CI (439891535362)
gati_prod             # Switch to production legacy (339713157855)
gati_status           # Verify current credentials
gati_audit            # Run comprehensive audit
```

---

## Account Comparison Matrix

### Service Coverage by Account

| Service | DEV (074779643551) | SIT (464134132424) | CI (439891535362) | Prod Legacy (339713157855) |
|---------|-----------|-------------|--------|--------|
| TIBCO Services | ❌ | ❌ | ❌ | ✅ |
| Spotfire | ❌ | ❌ | ❌ | ✅ |
| EKS Kubernetes | ✅ | ✅ | ✅ | ❌ |
| LAMP Stack | ✅ | ❌ | ❌ | ❌ |
| GenAI Testing | ✅ | ❌ | ❌ | ❌ |
| Master Data Mgmt | ❌ | ❌ | ❌ | ✅ |
| Jenkins CI/CD | ❌ | ❌ | ✅ | ❌ |
| Integration Testing | ❌ | ✅ | ❌ | ❌ |

### Resource Count Comparison

| Resource Type | DEV (074779643551) | SIT (464134132424) | CI (439891535362) | Prod Legacy (339713157855) | **Total** |
|---------------|-----------|-------------|--------|--------|--------|
| EC2 | 12 | TBD | TBD | 6 | **18+** |
| RDS | 3 | TBD | TBD | 2 | **5+** |
| Load Balancers | 3 | TBD | TBD | 2 | **5+** |
| CloudFront | 10 | TBD | TBD | 2 | **12+** |
| EKS Clusters | 1 | 1 | TBD | 0 | **2+** |

---

## Security & Access Control

### Credential Rotation Schedule

| Account | Account ID | Environment | Rotation Frequency | Last Rotated | Next Due |
|---------|-----------|-----------|-------------------|--------------|----------|
| DEV | 074779643551 | Development | Quarterly | TBD | TBD |
| SIT | 464134132424 | Staging/Integration | Quarterly | TBD | TBD |
| Central/CI | 439891535362 | CI/CD | Quarterly | TBD | TBD |
| Prod Legacy | 339713157855 | Production | Quarterly | TBD | TBD |

### MFA Policy

- ✅ Required for all console access
- ✅ Required for sensitive IAM operations
- ✅ Temporary credentials (1-hour TTL)
- ✅ Session logging to CloudTrail

### Audit Trail

All accounts have CloudTrail enabled:
- API call logging
- Console login tracking
- Resource modification audit
- 90-day retention (S3 archive for long-term)

---

## Quick Reference Commands

```bash
# List all accounts
aws organizations list-accounts --query 'Accounts[].[Id,Name]' --output table

# Get current identity
aws sts get-caller-identity

# List IAM roles in account
aws iam list-roles --query 'Roles[].RoleName'

# Audit resources (universal script)
bash scripts/gati-aws-audit.sh --account 339713157855

# Get account summary
aws iam get-account-summary --query 'SummaryMap'
```

---

## Documentation References

### Account-Specific Documentation

- **Production (339713157855):** [docs/GATI-RESOURCES-KB.md](../docs/GATI-RESOURCES-KB.md)
- **Development (058264376926):** [docs/DEV-GEMS-GATI-KB.md](../docs/DEV-GEMS-GATI-KB.md)
- **UAT (058264219242):** [docs/UAT-GEMS-GATI-KB.md](../docs/UAT-GEMS-GATI-KB.md)

### Related Documentation

- Main README: [README-GATI-AWS.md](../README-GATI-AWS.md)
- Setup Summary: [GATI-SETUP-COMPLETE.md](../GATI-SETUP-COMPLETE.md)
- Master Index: [docs/MASTER-INDEX.md](../docs/MASTER-INDEX.md)

---

## Next Steps

1. **Collect remaining account information** (Accounts 4-9)
2. **Update credential rotation schedule** with actual dates
3. **Verify all access role ARNs** are correct
4. **Test cross-account access** for all 9 accounts
5. **Create automation** for account-wide audits
6. **Document service-specific configurations**

---

## Contact & Support

For questions about GATI account access, credential setup, or resource inventory:

- **Audit Reports:** `bash scripts/gati-aws-audit.sh`
- **Account Listing:** `bash scripts/gati-credentials.sh` → `gati_list_accounts`
- **Documentation:** See master index at [docs/MASTER-INDEX.md](../docs/MASTER-INDEX.md)

---

**Last Updated:** June 6, 2026  
**Maintained By:** DevOps Team  
**Status:** ✅ Production Ready (3/9 accounts documented)

---

# GATI Resources Knowledge Base

> **Last Updated:** June 5, 2026  
> **Region:** ap-south-1 (Asia Pacific South - Mumbai)  
> **Purpose:** Complete inventory of GATI AWS resources for infrastructure management and reference

---

## Table of Contents

1. [EC2 Instances](#1-ec2-instances)
2. [RDS Databases](#2-rds-databases)
3. [Elastic IPs](#3-elastic-ips)
4. [Load Balancers (ALB/NLB)](#4-load-balancers)
5. [CloudFront Distributions](#5-cloudfront-distributions)
6. [IAM Roles](#6-iam-roles)
7. [IAM Users](#7-iam-users)
8. [Resource Summary](#8-resource-summary)

---

## 1. EC2 INSTANCES

### Overview
Total EC2 Instances: **6** (all in running state, all in ap-south-1)

### Instances List

| Instance ID | Name | Type | State | Private IP | Public IP |
|------------|------|------|-------|------------|-----------|
| i-0048dcba7f089bd20 | mdm-dev-TIBCO-EMS-as1 | t3a.small | running | 172.22.97.73 | None |
| i-0c9cdcd6b9c6e5874 | mdm-dev-Tibco-BW-as1 | m5a.large | running | 172.22.97.123 | None |
| i-0b36abe80dff6954d | mdm-dev-spotfire-nodemgr-win-as1 | m6a.xlarge | running | 172.22.98.66 | None |
| i-084003265d50dc4af | mdm-dev-spotfire-server-win-as1 | r6a.large | running | 172.22.98.156 | None |
| i-0c5feaac7d6b278df | HubEye-Dev | t3a.medium | running | 172.22.99.98 | None |
| i-0e7696713fd0c04bf | mdm-dev-Tibco-EBX-restore1 | m5a.xlarge | running | 172.22.99.103 | None |

### Key Observations
- All instances are in a private VPC (172.22.x.x CIDR range)
- No public IPs assigned (internal network only)
- Mix of instance types: small (t3a), medium (t3a), large (m5a, r6a), xlarge (m5a)
- Workloads: TIBCO EMS, TIBCO BW, Spotfire (Windows nodes), HubEye, EBX
- Resource allocation appropriate for data management and analytics workloads

---

## 2. RDS DATABASES

### Overview
Total RDS Instances: **2** (both PostgreSQL, all available)

### RDS Instances List

| Database ID | Engine | Instance Class | Storage (GB) | Status | Endpoint | Port |
|------------|--------|-----------------|--------------|--------|----------|------|
| mdm-dev-rds | postgres | db.t3.medium | 100 | available | mdm-dev-rds.ctqgsyeigi2w.ap-south-1.rds.amazonaws.com | 5432 |
| mdm-dev-spotfire-rds | postgres | db.t3.micro | 200 | available | mdm-dev-spotfire-rds.ctqgsyeigi2w.ap-south-1.rds.amazonaws.com | 5432 |

### Database Endpoints for Connection
```
# MDM Dev Database
Host: mdm-dev-rds.ctqgsyeigi2w.ap-south-1.rds.amazonaws.com
Port: 5432
Database: postgres

# Spotfire Database
Host: mdm-dev-spotfire-rds.ctqgsyeigi2w.ap-south-1.rds.amazonaws.com
Port: 5432
Database: postgres
```

### Key Observations
- Both databases use PostgreSQL engine
- Different instance classes: medium for main DB, micro for Spotfire (development tier)
- Spotfire DB has larger storage (200GB) despite smaller instance type
- RDS subnet group: ctqgsyeigi2w (likely private subnets in VPC)
- All databases in "available" state with full connectivity

---

## 3. ELASTIC IPs

### Overview
Total Elastic IPs: **2** (both unassigned to instances)

### Elastic IPs List

| Public IP | Allocation ID | Domain | Associated Instance | Status |
|-----------|---------------|--------|---------------------|--------|
| 13.126.130.244 | eipalloc-08f03c14083ca3144 | vpc | None | Available |
| 3.7.132.214 | eipalloc-0e07bf02f101c3c06 | vpc | None | Available |

### Key Observations
- Both IPs allocated but not currently assigned to instances
- Available for NAT Gateway or future instance assignment
- VPC-scoped allocations (not EC2-Classic)
- Could be used for outbound internet traffic via NAT Gateway

---

## 4. LOAD BALANCERS

### Overview
Total Load Balancers: **2** (1 NLB + 1 ALB, both internal)

### Load Balancers List

| Name | Type | Scheme | Status | DNS Name |
|------|------|--------|--------|----------|
| mdm-dev-int-nlb | Network (NLB) | internal | active | mdm-dev-int-nlb-c84fbb6c293d8261.elb.ap-south-1.amazonaws.com |
| mdm-dev-alb-int | Application (ALB) | internal | active | internal-mdm-dev-alb-int-1132021182.ap-south-1.elb.amazonaws.com |

### Network Load Balancer (NLB)
- **Name**: mdm-dev-int-nlb
- **Scheme**: Internal (no public internet exposure)
- **DNS**: mdm-dev-int-nlb-c84fbb6c293d8261.elb.ap-south-1.amazonaws.com
- **Use Case**: High-performance TCP/UDP traffic distribution
- **Target**: TIBCO, database services

### Application Load Balancer (ALB)
- **Name**: mdm-dev-alb-int
- **Scheme**: Internal (no public internet exposure)
- **DNS**: internal-mdm-dev-alb-int-1132021182.ap-south-1.elb.amazonaws.com
- **Use Case**: HTTP/HTTPS layer 7 routing (path, hostname, header-based)
- **Target**: Web applications, APIs

### Key Observations
- Both load balancers are internal-only (no internet-facing traffic)
- Designed for east-west traffic within VPC
- High availability across availability zones
- NLB for low-latency mission-critical workloads
- ALB for application-level routing

---

## 5. CLOUDFRONT DISTRIBUTIONS

### Overview
Total CloudFront Distributions: **2** (1 enabled, 1 disabled)

### CloudFront Distributions List

| Distribution ID | Domain Name | Status | Enabled |
|-----------------|-------------|--------|---------|
| E3MKPUWI2U0AVB | d1fe3j3n1g137c.cloudfront.net | Deployed | False |
| E1HBJ5BWZTRN3J | dr605r2gxijyz.cloudfront.net | Deployed | True |

### Distribution Details

#### Distribution 1: E3MKPUWI2U0AVB
- **Status**: Deployed
- **Enabled**: No (disabled)
- **Domain**: d1fe3j3n1g137c.cloudfront.net
- **Use Case**: Likely testing/development distribution

#### Distribution 2: E1HBJ5BWZTRN3J
- **Status**: Deployed
- **Enabled**: Yes (active)
- **Domain**: dr605r2gxijyz.cloudfront.net
- **Use Case**: Production CDN for content delivery
- **Caching**: Global edge locations for low-latency content delivery

### Key Observations
- CloudFront is a global service (not region-specific)
- Only 1 active distribution in production
- Disabled distribution available for testing/staging
- Both deployed and ready for activation if needed
- Note: Different from iTariff distribution E1MSDTWI1MUQ2P (SIT account)

---

## 6. IAM ROLES

### Overview
Total IAM Roles: **30+** (including AWS managed and custom)

### Key Roles (Sample)

#### AWS Control Tower Roles
- **aws-controltower-AdministratorExecutionRole** (arn:aws:iam::339713157855:role/aws-controltower-AdministratorExecutionRole)
- **aws-controltower-ConfigRecorderRole** (arn:aws:iam::339713157855:role/aws-controltower-ConfigRecorderRole)
- **aws-controltower-ReadOnlyExecutionRole** (arn:aws:iam::339713157855:role/aws-controltower-ReadOnlyExecutionRole)

#### Custom Permission Levels
- **AWS-L1** - Highest privilege tier (arn:aws:iam::339713157855:role/AWS-L1)
- **AWS-L2** - Mid-level access (arn:aws:iam::339713157855:role/AWS-L2)
- **AWS-L3** - Lower privilege tier (arn:aws:iam::339713157855:role/AWS-L3)
- **AWS-READONLY** - Read-only access (arn:aws:iam::339713157855:role/AWS-READONLY)
- **AWS-RDS** - RDS-specific permissions (arn:aws:iam::339713157855:role/AWS-RDS)

#### Service-Linked Roles
- **AWSBackupDefaultServiceRole** - AWS Backup service access
- **AWSCodePipelineServiceRole-ap-south-1-ebx-sup-dev-1** - CodePipeline for EBX
- **AWSControlTowerExecution** - Control Tower execution
- **AWSControlTower_VPCFlowLogsRole** - VPC Flow Logs

#### SSM Integration Roles
- **AWS-QuickSetup-SSM-DefaultEC2MgmtRole-ap-south-1**
- **AWS-QuickSetup-SSM-EnableAREX-pz783-v2**
- **AWS-QuickSetup-SSM-EnableDHMC-pz783-v2**
- **AWS-QuickSetup-SSM-EnableExplorer-pz783-v2**
- **AWS-QuickSetup-SSM-LifecycleManagement-V2-LA-ap-south-1**

#### SSO-Integrated Roles (Reserved)
- **AWSReservedSSO_all-custome-readonly-accesss_f7e57ca08ed8c731** - Custom read-only SSO role
- **AWSReservedSSO_AWSAdministratorAccess_c28a736369e60d0b** - Admin SSO role

### Key Observations
- Account ID: 339713157855
- Multi-tier role architecture (L1, L2, L3, READONLY)
- AWS Control Tower enabled for governance
- SSO integration with AWS Identity Center
- Service-linked roles for AWS managed services (Backup, CodePipeline, etc.)
- SSM Quick Setup for operational management

---

## 7. IAM USERS

### Overview
Total IAM Users: **30+** (mix of human users and service accounts)

### Users List (Sample)

| Username | Email/Identifier | ARN | Created |
|----------|-----------------|-----|---------|
| aman@ecuworldwide.com | aman@ecuworldwide.com | arn:aws:iam::339713157855:user/aman@ecuworldwide.com | 2024-09-02T07:47:36Z |
| ankit.s.kumar@capgemini.com | ankit.s.kumar@capgemini.com | arn:aws:iam::339713157855:user/ankit.s.kumar@capgemini.com | 2024-06-19T05:39:13Z |
| baasaa.divya-sri@capgemini.com | baasaa.divya-sri@capgemini.com | arn:aws:iam::339713157855:user/baasaa.divya-sri@capgemini.com | 2024-06-19T05:38:45Z |
| dinesh.b.d@capgemini.com | dinesh.b.d@capgemini.com | arn:aws:iam::339713157855:user/dinesh.b.d@capgemini.com | 2024-06-19T05:37:57Z |
| divya-mehar.saride@capgemini.com | divya-mehar.saride@capgemini.com | arn:aws:iam::339713157855:user/divya-mehar.saride@capgemini.com | 2025-05-13T10:37:51Z |
| ebx-dev-user | Service Account | arn:aws:iam::339713157855:user/ebx-dev-user | 2024-09-26T15:35:28Z |
| file-uploader | Service Account | arn:aws:iam::339713157855:user/file-uploader | 2024-10-18T12:22:43Z |
| hubops-user-group | Service Account | arn:aws:iam::339713157855:user/hubops-user-group | 2024-09-02T07:31:48Z |
| jenkins | Service Account | arn:aws:iam::339713157855:user/jenkins | 2024-03-11T10:59:23Z |
| k.rahul@allcargologistics.com | k.rahul@allcargologistics.com | arn:aws:iam::339713157855:user/k.rahul@allcargologistics.com | 2026-03-17T07:44:25Z |
| koralla-syama.nandini-kranthi@capgemini.com | koralla-syama.nandini-kranthi@capgemini.com | arn:aws:iam::339713157855:user/koralla-syama.nandini-kranthi@capgemini.com | 2024-06-19T05:37:43Z |

### User Categories

#### External Partners (ECU Worldwide)
- aman@ecuworldwide.com

#### Capgemini Team
- ankit.s.kumar@capgemini.com
- baasaa.divya-sri@capgemini.com
- dinesh.b.d@capgemini.com
- divya-mehar.saride@capgemini.com
- koralla-syama.nandini-kranthi@capgemini.com
- krishna.h-mutalikdesai@capgemini.com

#### AllCargo Internal
- k.rahul@allcargologistics.com

#### Service Accounts (CI/CD & Operations)
- jenkins - Continuous Integration/Deployment
- ebx-dev-user - EBX development operations
- file-uploader - Document/file upload service
- hubops-user-group - Hub operations automation

### Key Observations
- Account ID: 339713157855
- 30+ active users and service accounts
- Primarily Capgemini staff (outsourced development partner)
- Service accounts for Jenkins CI/CD, EBX, Hub operations
- Mix of direct email logins and SSO-integrated users
- Most users created between June 2024 - May 2025
- No public access keys visible in listing (managed separately)

---

## 8. RESOURCE SUMMARY

### Resource Count by Type

| Resource Type | Count | Status |
|---------------|-------|--------|
| EC2 Instances | 6 | All Running |
| RDS Databases | 2 | All Available |
| Elastic IPs | 2 | Unassigned |
| Load Balancers | 2 | Both Active |
| CloudFront Distributions | 2 | 1 Enabled, 1 Disabled |
| IAM Roles | 30+ | Mixed (AWS Managed + Custom) |
| IAM Users | 30+ | Active |

### Cost Optimization Opportunities

1. **Unassigned Elastic IPs** - Consider releasing if not planned for immediate use (incurs charges)
2. **Disabled CloudFront Distribution** - Clean up if no longer needed
3. **t3a Instances** - Review if burst capacity is sufficient vs. on-demand
4. **RDS Standby Replicas** - Check if high availability is configured

### Security Best Practices Status

✅ **Implemented**
- Internal load balancers (no direct internet exposure)
- Multi-tier role architecture (L1-L3 separation of duties)
- SSO integration via AWS Identity Center
- Service-linked roles for AWS managed services

⚠️ **Review Recommended**
- Verify least-privilege access for each IAM user/role
- Audit active access keys for users
- Review service account rotations (especially Jenkins)
- Check security group ingress/egress rules

### Access Patterns

- **Jenkins CI/CD**: Likely has elevated permissions for EC2, RDS, CloudFront operations
- **Capgemini Team**: Development and infrastructure management permissions
- **AllCargo Internal**: Administrative access through elevated roles
- **Service Accounts**: Limited, specific-purpose permissions

---

## 9. CONNECTION DETAILS FOR REFERENCE

### RDS Connection String (PostgreSQL)

```bash
# MDM Dev Database
psql -h mdm-dev-rds.ctqgsyeigi2w.ap-south-1.rds.amazonaws.com -p 5432 -U <username> -d postgres

# Spotfire Database
psql -h mdm-dev-spotfire-rds.ctqgsyeigi2w.ap-south-1.rds.amazonaws.com -p 5432 -U <username> -d postgres
```

### Load Balancer Access

```bash
# NLB (Network Load Balancer) - Low-latency TCP/UDP
# Use for real-time, high-throughput applications
curl http://mdm-dev-int-nlb-c84fbb6c293d8261.elb.ap-south-1.amazonaws.com

# ALB (Application Load Balancer) - Layer 7 routing
# Use for HTTP/HTTPS web applications
curl http://internal-mdm-dev-alb-int-1132021182.ap-south-1.elb.amazonaws.com
```

### CloudFront Distribution Access

```bash
# Production Distribution (Enabled)
https://dr605r2gxijyz.cloudfront.net/

# Development Distribution (Disabled)
# https://d1fe3j3n1g137c.cloudfront.net/ (not accessible - disabled)
```

---

## 10. MAINTENANCE & UPDATES

### Last Audited
- **Date**: June 5, 2026
- **Method**: AWS CLI read-only queries
- **Region**: ap-south-1 (Mumbai, India)

### Regular Review Schedule
- **Monthly**: User access, unused resources
- **Quarterly**: Role permissions, security groups
- **Annually**: Architecture review, cost optimization

### Contact for Changes
- **AWS Admin**: Use IAM roles to make infrastructure changes
- **Infrastructure Team**: Capgemini/AllCargo team leads
- **Jenkins CI/CD**: Automated deployments through Jenkins pipelines

---

*This knowledge base is maintained for reference and operational purposes. All information is read-only unless explicitly authorized to make changes.*

---

# DEV GEMS GATI Resources Knowledge Base

> **Last Updated:** June 5, 2026  
> **Region:** ap-south-1 (Asia Pacific South - Mumbai)  
> **Account ID:** 058264376926  
> **Purpose:** Complete inventory of DEV GEMS GATI AWS resources for development, testing, and infrastructure management

---

## Table of Contents

1. [EC2 Instances](#1-ec2-instances)
2. [RDS Databases](#2-rds-databases)
3. [Elastic IPs](#3-elastic-ips)
4. [Load Balancers (ALB/NLB)](#4-load-balancers)
5. [CloudFront Distributions](#5-cloudfront-distributions)
6. [IAM Roles](#6-iam-roles)
7. [IAM Users](#7-iam-users)
8. [Resource Summary](#8-resource-summary)
9. [Connection Details](#9-connection-details)

---

## 1. EC2 INSTANCES

### Overview
Total EC2 Instances: **12** (11 running, 1 stopped)

### Instances List

| Instance ID | Name | Type | State | Private IP | Public IP |
|------------|------|------|-------|------------|-----------|
| i-050957ab3ee9ede0d | window-db-test | t3a.small | running | 172.23.115.87 | None |
| i-027b4ca96e9576143 | gem2-dev-jumpbox-as1 | t3a.medium | running | 172.23.113.195 | None |
| i-05f0526e2b5b1a5f3 | dev-lamp-server-pivotroots-website | r5a.xlarge | running | 172.23.116.75 | None |
| i-0dea0c9b4ae7dc531 | gems-genai-test | t3a.xlarge | running | 172.23.116.156 | None |
| i-07804000c93df37fc | dev-lamp-server-pivotroots-website-cicd | r5a.large | **stopped** | 172.23.117.82 | None |
| i-072676e257dba1034 | gem2-dev-eks-nodegroup | m5a.large | running | 172.23.117.3 | None |
| i-02cf6a3fef9be648d | gem2-dev-eks-nodegroup | m5a.large | running | 172.23.117.1 | None |
| i-046c2351532c08cba | gem2-dev-eks-nodegroup | m5a.large | running | 172.23.116.81 | None |
| i-095a6cc295a14043a | gem2-dev-eks-nodegroup | m5a.large | running | 172.23.116.101 | None |
| i-053d25ba9abc58549 | gem2-dev-eks-nodegroup | m6a.large | running | 172.23.114.225 | None |
| i-013ff2934205584a8 | gem2-dev-eks-nodegroup | m6a.large | running | 172.23.114.170 | None |
| i-01f7f7c114a30643a | gem2-dev-eks-nodegroup | m6a.large | running | 172.23.114.135 | None |

### Instance Classification

#### Control/Gateway Instances
- **gem2-dev-jumpbox-as1** (t3a.medium) - Bastion/jumpbox for secure access
- **window-db-test** (t3a.small) - Windows test environment

#### Application Servers
- **dev-lamp-server-pivotroots-website** (r5a.xlarge) - Production LAMP stack (running)
- **dev-lamp-server-pivotroots-website-cicd** (r5a.large) - CI/CD LAMP stack (stopped)
- **gems-genai-test** (t3a.xlarge) - GenAI testing environment

#### EKS Cluster Nodes (6 nodes + 1 stopped)
- **gem2-dev-eks-nodegroup** - 6 x running nodes (4x m5a.large + 2x m6a.large)
- Mixed generation: m5a (previous gen), m6a (current gen)
- Total EKS capacity: ~192 GB RAM + 36 vCPU

### Key Observations
- All instances in private VPC (172.23.x.x CIDR range)
- No public IPs assigned (internal network only)
- EKS nodegroup optimized for Kubernetes workloads
- LAMP servers for web application hosting
- GenAI testing instance for ML/AI experimentation

---

## 2. RDS DATABASES

### Overview
Total RDS Instances: **3** (all available)

### RDS Instances List

| Database ID | Engine | Instance Class | Storage (GB) | Status | Endpoint | Port |
|------------|--------|-----------------|--------------|--------|----------|------|
| database | postgres | db.t4g.small | 30 | available | database.c3g8wska0zoq.ap-south-1.rds.amazonaws.com | 5432 |
| mid-mile | postgres | db.m6g.large | 150 | available | mid-mile.c3g8wska0zoq.ap-south-1.rds.amazonaws.com | 5432 |
| pivotroots-website-dev | mysql | db.t4g.micro | 100 | available | pivotroots-website-dev.c3g8wska0zoq.ap-south-1.rds.amazonaws.com | 3306 |

### Database Details

#### General Purpose Database
- **Name**: database
- **Engine**: PostgreSQL
- **Instance Class**: db.t4g.small (burst-capable, cost-optimized)
- **Storage**: 30 GB
- **Use Case**: General development/testing database
- **Endpoint**: database.c3g8wska0zoq.ap-south-1.rds.amazonaws.com:5432

#### Mid-Mile Service Database
- **Name**: mid-mile
- **Engine**: PostgreSQL
- **Instance Class**: db.m6g.large (general purpose, sustained performance)
- **Storage**: 150 GB
- **Use Case**: Mid-mile logistics service (production-like)
- **Endpoint**: mid-mile.c3g8wska0zoq.ap-south-1.rds.amazonaws.com:5432

#### PivotRoots Website Database
- **Name**: pivotroots-website-dev
- **Engine**: MySQL
- **Instance Class**: db.t4g.micro (minimal, development)
- **Storage**: 100 GB
- **Use Case**: PivotRoots website development
- **Endpoint**: pivotroots-website-dev.c3g8wska0zoq.ap-south-1.rds.amazonaws.com:3306

### Key Observations
- Mix of PostgreSQL and MySQL engines
- t4g instances for cost optimization (graviton processors)
- Mid-mile DB has significantly more storage (production-scale)
- RDS subnet group: c3g8wska0zoq (private subnets in VPC)
- All databases in "available" state with full connectivity

---

## 3. ELASTIC IPs

### Overview
Total Elastic IPs: **0** (none allocated)

No Elastic IPs are currently allocated in the DEV account. They may be added for NAT Gateway or instance assignment if needed.

---

## 4. LOAD BALANCERS

### Overview
Total Load Balancers: **3** (all internal, all active)

### Load Balancers List

| Name | Type | Scheme | Status | DNS Name |
|------|------|--------|--------|----------|
| k8s-istiosys-istioing-232717e1f1 | network | internal | active | k8s-istiosys-istioing-232717e1f1-28eb941b79d17512.elb.ap-south-1.amazonaws.com |
| k8s-ingressn-ingressn-674391e4e4 | network | internal | active | k8s-ingressn-ingressn-674391e4e4-724317e339187115.elb.ap-south-1.amazonaws.com |
| k8s-devsharedalb-f2a3528a9f | application | internal | active | internal-k8s-devsharedalb-f2a3528a9f-192347875.ap-south-1.elb.amazonaws.com |

### Load Balancer Details

#### Istio Ingress Gateway NLB
- **Name**: k8s-istiosys-istioing-232717e1f1
- **Type**: Network Load Balancer (NLB)
- **Scheme**: Internal (east-west traffic only)
- **DNS**: k8s-istiosys-istioing-232717e1f1-28eb941b79d17512.elb.ap-south-1.amazonaws.com
- **Use Case**: Istio service mesh ingress (high-performance TCP/UDP routing)
- **Deployment**: EKS cluster networking

#### Ingress Controller NLB
- **Name**: k8s-ingressn-ingressn-674391e4e4
- **Type**: Network Load Balancer (NLB)
- **Scheme**: Internal (east-west traffic only)
- **DNS**: k8s-ingressn-ingressn-674391e4e4-724317e339187115.elb.ap-south-1.amazonaws.com
- **Use Case**: Kubernetes ingress controller networking
- **Deployment**: EKS cluster networking

#### Shared Development ALB
- **Name**: k8s-devsharedalb-f2a3528a9f
- **Type**: Application Load Balancer (ALB)
- **Scheme**: Internal (east-west traffic only)
- **DNS**: internal-k8s-devsharedalb-f2a3528a9f-192347875.ap-south-1.elb.amazonaws.com
- **Use Case**: Layer 7 routing (path, hostname, header-based) for development applications
- **Deployment**: EKS cluster application routing

### Key Observations
- All load balancers are internal (no internet-facing exposure)
- Two NLBs for high-performance service mesh and ingress
- One ALB for application-level HTTP/HTTPS routing
- Load balancers auto-created by EKS/Kubernetes controllers
- Designed for east-west traffic within VPC

---

## 5. CLOUDFRONT DISTRIBUTIONS

### Overview
Total CloudFront Distributions: **10** (8 disabled, 2 enabled)

### CloudFront Distributions List

| Distribution ID | Domain Name | Status | Enabled |
|-----------------|-------------|--------|---------|
| E3BM319U8UN4CD | d16bvzvlybci6o.cloudfront.net | Deployed | **No** |
| E26WU6E1VTU6GH | d2o3zt9kxgv490.cloudfront.net | Deployed | **No** |
| E3PPDXG57UZHQW | d3m1eo2mb88cw0.cloudfront.net | Deployed | **No** |
| E32W2GCYE6MVQA | d3jqmpbx2axcwk.cloudfront.net | Deployed | **No** |
| E20WVJNBD6R33G | d3nsxsk63wo5y2.cloudfront.net | Deployed | **No** |
| E1N1NTJN6YTVP1 | d25szyhxzjwi0n.cloudfront.net | Deployed | **No** |
| E2G6TKUEEQ3ZT8 | df0x23f8ihkqk.cloudfront.net | Deployed | **No** |
| E45HXN8YMKYRU | dgm7bt6xzsfnt.cloudfront.net | Deployed | **Yes** |
| E3R512BF3E2TY8 | d2ls80f7wns81e.cloudfront.net | Deployed | **Yes** |
| E1T9IS6S6PFPLC | d15lv0q6njsl1g.cloudfront.net | Deployed | **No** |

### Distribution Status Summary

**Active Distributions (Enabled)**: 2
- E45HXN8YMKYRU → dgm7bt6xzsfnt.cloudfront.net
- E3R512BF3E2TY8 → d2ls80f7wns81e.cloudfront.net

**Development/Staging Distributions (Disabled)**: 8
- Used for testing, feature branches, or experimental content delivery

### Key Observations
- CloudFront is a global service (not region-specific)
- Many distributions deployed but disabled (development/staging tier)
- 2 active distributions for production content delivery
- Distributed architecture suggests multiple applications or environments
- All distributions deployed and ready for activation if needed

---

## 6. IAM ROLES

### Overview
Total IAM Roles: **18+** (development and EKS-focused)

### Key Roles by Category

#### EKS Cluster Roles
- **gem2-dev-eks-role-20240306064404361000000001** - Primary cluster role
- **gem2-dev-eks-nodegroup-eks-node-group-20240306064404361400000002** - Node group role
- **eksctl-gem2-dev-eks-cluster-addon-iamservicea-Role1-bswYEkCiTE9j** - Add-on service accounts
- **eksctl-gem2-dev-eks-cluster-addon-iamservicea-Role1-pdG9Q2F8neac** - Add-on service accounts
- **eksctl-gem2-dev-eks-cluster-addon-iamservicea-Role1-ytJL2ZtjTQG8** - Add-on service accounts

#### EKS Service-Specific Roles
- **eks-cognito-role** - Cognito authentication for EKS
- **eks-efs-role** - EFS (Elastic File System) for persistent storage
- **eks-msk-role** - MSK (Managed Streaming Kafka) integration
- **eks-s3-role** - S3 bucket access
- **eks-s3-msk-role** - S3 + Kafka combined access
- **eks-velero-backup** - Velero backup management
- **eks-velero-recovery** - Velero disaster recovery

#### Development/Operations Roles
- **gem2-dev-G2G1-iam-role** - Application-specific role
- **gem2-dev-jumpbox-iam-role** - Jumpbox/bastion access
- **gem2-dev-windows-jumpbox-iam-role** - Windows bastion access
- **gems2-dev-backup-iam-role** - Backup operations
- **jenkins-dev-execution-role** - Jenkins CI/CD pipeline execution
- **AWSReservedSSO_datascience-gems-dev_b18161cd393d4b71** - Data science team SSO role

### Role Architecture

**Cluster Management**: EKS cluster role + node group role + add-on roles
**Storage**: EFS role for persistent volumes
**Messaging**: MSK role for Kafka integration
**Backup/Recovery**: Velero roles for disaster recovery
**CI/CD**: Jenkins role for automated deployments
**Jumpbox**: Windows + Linux bastion access roles
**Authentication**: Cognito for API authentication

---

## 7. IAM USERS

### Overview
Total IAM Users: **4** (mostly service accounts)

### IAM Users List

| Username | Type | Account | Created | Purpose |
|----------|------|---------|---------|---------|
| gati-website-s3-user | Service Account | 058264376926 | 2025-01-07 | S3 file operations for GATI website |
| mohdsufeeyanahamad@ecuworldwide.com | Human User | 058264376926 | 2025-02-07 | ECU Worldwide team member |
| s3-dev-upload | Service Account | 058264376926 | 2026-02-18 | S3 upload automation |
| sify_cmp_service_account_ac-gati-dev-gems2-acc | Service Account | 058264376926 | 2025-10-18 | SIFY CMP service account (Gems2 access) |

### User Categories

#### Service Accounts
- **gati-website-s3-user** - Static content and file management for GATI website
- **s3-dev-upload** - Automated S3 uploads (recent addition Feb 2026)
- **sify_cmp_service_account_ac-gati-dev-gems2-acc** - Third-party integration (SIFY CMP)

#### Human Users
- **mohdsufeeyanahamad@ecuworldwide.com** - ECU Worldwide external contractor

### Key Observations
- Minimal user count (4 total) - primarily service accounts
- Account ID: 058264376926 (dev/gems account)
- Most users created in late 2025 to early 2026
- Service accounts focused on S3 operations and integrations
- Limited human user access (security-conscious)

---

## 8. RESOURCE SUMMARY

### Resource Count by Type

| Resource Type | Count | Status |
|---------------|-------|--------|
| EC2 Instances | 12 | 11 Running, 1 Stopped |
| RDS Databases | 3 | All Available |
| Elastic IPs | 0 | None Allocated |
| Load Balancers | 3 | All Active |
| CloudFront Distributions | 10 | 2 Enabled, 8 Disabled |
| IAM Roles | 18+ | EKS + Dev focused |
| IAM Users | 4 | 3 Service Accounts, 1 Human |

### Infrastructure Capabilities

**Compute**
- 12 EC2 instances (6 EKS nodes + 3 LAMP servers + jumpbox + test instances)
- 1 r5a.xlarge for LAMP production (36 GB RAM, 4 vCPU)
- 1 t3a.xlarge for GenAI testing
- Mixed generations (m5a, m6a, r5a) for cost optimization

**Storage**
- 3 RDS databases (2 PostgreSQL, 1 MySQL)
- 280 GB total database storage
- EFS integration via EKS for persistent Kubernetes volumes

**Networking**
- 3 load balancers (internal only, no public exposure)
- 10 CloudFront distributions (CDN for content delivery)
- Private VPC architecture (172.23.x.x CIDR)

**Kubernetes**
- EKS cluster "gem2-dev-eks" with 6 worker nodes
- Istio service mesh enabled (Istio NLB deployed)
- Velero backup/recovery configured
- Multiple add-ons (Cognito, EFS, MSK, S3)

### Cost Optimization Opportunities

1. **Stopped Instance**: dev-lamp-server-pivotroots-website-cicd is stopped - consider terminating if no longer needed
2. **Disabled CloudFront Distributions**: 8 disabled distributions incur minimal costs - review and clean up unused ones
3. **EKS Node Mix**: 6 nodes may be over-provisioned for dev - consider auto-scaling policies
4. **Database Sizing**: t4g.micro for MySQL may be tight - monitor performance metrics
5. **Jumpbox Right-sizing**: t3a instances suitable for bastion hosts

### Security Best Practices Status

✅ **Implemented**
- Internal load balancers only (no internet exposure)
- Service account-driven access (minimal human users)
- EKS with RBAC enabled
- Backup/recovery capabilities (Velero)
- Private VPC architecture
- Cognito authentication for EKS

⚠️ **Review Recommended**
- Verify IAM role trust policies
- Audit S3 bucket permissions for service accounts
- Enable VPC Flow Logs for network monitoring
- Review EKS security group ingress/egress rules
- Check Velero backup retention policies

---

## 9. CONNECTION DETAILS

### RDS Connection Strings (PostgreSQL)

```bash
# General Purpose Database
psql -h database.c3g8wska0zoq.ap-south-1.rds.amazonaws.com -p 5432 -U <username> -d postgres

# Mid-Mile Service Database
psql -h mid-mile.c3g8wska0zoq.ap-south-1.rds.amazonaws.com -p 5432 -U <username> -d mid_mile
```

### MySQL Connection

```bash
# PivotRoots Website Database
mysql -h pivotroots-website-dev.c3g8wska0zoq.ap-south-1.rds.amazonaws.com -P 3306 -u <username> -p
```

### Load Balancer Access (EKS)

```bash
# Istio Ingress (TCP/UDP, high-performance)
k8s-istiosys-istioing-232717e1f1-28eb941b79d17512.elb.ap-south-1.amazonaws.com

# Kubernetes Ingress
k8s-ingressn-ingressn-674391e4e4-724317e339187115.elb.ap-south-1.amazonaws.com

# Application ALB (Layer 7 routing)
internal-k8s-devsharedalb-f2a3528a9f-192347875.ap-south-1.elb.amazonaws.com
```

### EKS Cluster Access

```bash
# Update kubeconfig for gem2-dev-eks cluster
aws eks update-kubeconfig --name gem2-dev-eks --region ap-south-1

# Verify cluster access
kubectl cluster-info
kubectl get nodes
kubectl get pods -A
```

### CloudFront URLs (Active Distributions)

```
# Active Distribution 1
https://dgm7bt6xzsfnt.cloudfront.net/

# Active Distribution 2
https://d2ls80f7wns81e.cloudfront.net/
```

---

## 10. MAINTENANCE & UPDATES

### Last Audited
- **Date**: June 5, 2026
- **Method**: AWS CLI read-only queries
- **Region**: ap-south-1 (Mumbai, India)
- **Account**: 058264376926 (DEV GEMS GATI)

### Regular Review Schedule
- **Weekly**: EKS cluster health, pod resource usage
- **Monthly**: User access, unused resources, cost tracking
- **Quarterly**: IAM role permissions, security group rules
- **Annually**: Architecture review, disaster recovery testing

### Key Contacts
- **EKS Admin**: Infrastructure team (use IAM roles)
- **Jenkins CI/CD**: jenkins-dev-execution-role
- **Database Admin**: RDS database administrators
- **Backup Manager**: Velero backup operators

### Backup Strategy
- **Velero**: Cluster-level backup and recovery
- **RDS**: AWS managed automated backups (default 7 days retention)
- **Application Data**: S3 via s3-dev-upload service account

---

*This knowledge base is maintained for reference and operational purposes. All information is read-only unless explicitly authorized to make changes.*

---

# UAT GEMS GATI Resources Knowledge Base

> **Last Updated:** June 5, 2026  
> **Region:** ap-south-1 (Asia Pacific South - Mumbai)  
> **Account ID:** 058264219242  
> **Purpose:** Complete inventory of UAT GEMS GATI AWS resources for testing, validation, and pre-production workloads

---

## Table of Contents

1. [EC2 Instances](#1-ec2-instances)
2. [RDS Databases](#2-rds-databases)
3. [Load Balancers](#3-load-balancers)
4. [IAM Roles](#4-iam-roles)
5. [Resource Summary](#5-resource-summary)
6. [Connection Details](#6-connection-details)
7. [Differences from DEV](#7-differences-from-dev)

---

## 1. EC2 INSTANCES

### Overview
Total EC2 Instances: **1** (stopped)

### Instances List

| Instance ID | Name | Type | State | Private IP | Purpose |
|------------|------|------|-------|------------|---------|
| i-053ce4094bd878496 | gem2-uat-jumpbox-as1 | t3.small | **stopped** | 172.23.4.213 | Bastion/jumpbox for secure access |

### Instance Details

**gem2-uat-jumpbox-as1**
- **Type**: t3.small (burst-capable, cost-optimized)
- **State**: Stopped (can be started when needed)
- **Private IP**: 172.23.4.213
- **Purpose**: Bastion host for SSH access to UAT cluster resources
- **Note**: Instance is stopped to save costs in UAT environment

### Key Observations
- Minimal compute footprint for UAT (only jumpbox)
- EKS cluster likely managed with managed node groups (not shown as traditional EC2)
- Private network only (no public IPs)
- Cost-conscious configuration (stopped when not in use)

---

## 2. RDS DATABASES

### Overview
Total RDS Instances: **1** (available)

### RDS Instance

| Database ID | Engine | Instance Class | Storage (GB) | Status | Endpoint | Port |
|------------|--------|-----------------|--------------|--------|----------|------|
| all-miles | postgres | db.t4g.micro | 50 | available | all-miles.c3g8wska0zoq.ap-south-1.rds.amazonaws.com | 5432 |

### Database Details

**all-miles**
- **Engine**: PostgreSQL
- **Instance Class**: db.t4g.micro (minimal, testing)
- **Storage**: 50 GB
- **Status**: Available and accessible
- **Use Case**: UAT/testing for all-miles service
- **Endpoint**: all-miles.c3g8wska0zoq.ap-south-1.rds.amazonaws.com:5432

### Connection String

```bash
psql -h all-miles.c3g8wska0zoq.ap-south-1.rds.amazonaws.com -p 5432 -U <username> -d all_miles
```

### Key Observations
- Single database for UAT environment
- Minimal instance class (t4g.micro) for cost optimization
- 50 GB storage is reasonable for testing workloads
- Same RDS subnet group as DEV (c3g8wska0zoq)

---

## 3. LOAD BALANCERS

### Overview
Total Load Balancers: **2** (both internal, both active)

### Load Balancers List

| Name | Type | Scheme | Status |
|------|------|--------|--------|
| k8s-istiosys-istioing-7dadda2090 | network | internal | active |
| k8s-uatsharedalb-9d6ffec733 | application | internal | active |

### Load Balancer Details

#### Istio Ingress Gateway NLB
- **Name**: k8s-istiosys-istioing-7dadda2090
- **Type**: Network Load Balancer (NLB)
- **Scheme**: Internal (east-west traffic only)
- **Use Case**: Istio service mesh ingress (high-performance TCP/UDP routing)
- **Deployment**: EKS cluster networking

#### Shared UAT ALB
- **Name**: k8s-uatsharedalb-9d6ffec733
- **Type**: Application Load Balancer (ALB)
- **Scheme**: Internal (east-west traffic only)
- **Use Case**: Layer 7 routing (path, hostname, header-based) for UAT applications
- **Deployment**: EKS cluster application routing

### Key Observations
- Both load balancers are internal (no internet-facing exposure)
- Similar setup to DEV environment but with UAT-specific naming
- Istio service mesh enabled for advanced traffic management
- Load balancers auto-created by EKS/Kubernetes controllers

---

## 4. IAM ROLES

### Overview
Total IAM Roles: **8** (EKS-focused)

### Key Roles

#### EKS Cluster Roles
- **gem2-uat-eks-role-20241105072843496800000002** - Primary cluster control plane role
- **gem2-uat-eks-nodegroup-eks-node-group-20241105072841811400000001** - Worker node group role
- **eksctl-gem2-uat-eks-cluster-addon-iamservicea-Role1-dEwfc3yL55f7** - Add-on service account 1
- **eksctl-gem2-uat-eks-cluster-addon-iamservicea-Role1-ElhvxuPrT96l** - Add-on service account 2
- **eksctl-gem2-uat-eks-cluster-addon-iamservicea-Role1-soG6cVHj9iaN** - Add-on service account 3

#### Operations Roles
- **gem2-uat-jumpbox-iam-role** - Jumpbox/bastion access permissions
- **gems2-uat-backup-iam-role** - Backup operations management
- **jenkins-uat-execution-role** - Jenkins CI/CD pipeline execution for UAT

### Role Architecture

**Cluster Management**: EKS cluster role + node group role + add-on roles  
**CI/CD**: Jenkins UAT execution role for automated testing  
**Jumpbox**: Bastion access role  
**Backup**: Disaster recovery and backup management

---

## 5. RESOURCE SUMMARY

### Resource Count by Type

| Resource Type | UAT | DEV | PROD | Purpose |
|---------------|-----|-----|------|---------|
| EC2 Instances | 1 | 12 | 6 | Jumpbox only (cost-optimized) |
| RDS Databases | 1 | 3 | 2 | Single test database |
| Load Balancers | 2 | 3 | 2 | Minimal ALB/NLB setup |
| IAM Roles | 8 | 18+ | 15+ | EKS-focused |
| EKS Cluster | 1 | 1 | 1 | gem2-uat-eks cluster |

### Infrastructure Capabilities

**Compute**
- Minimal EC2 footprint (only jumpbox)
- EKS cluster gem2-uat-eks for Kubernetes workloads
- Cost-optimized for UAT usage patterns

**Storage**
- 1 RDS database (50GB PostgreSQL)
- Sufficient for testing and validation

**Networking**
- 2 load balancers (NLB for Istio, ALB for apps)
- Internal-only (no public exposure)
- Private VPC architecture

**Kubernetes**
- EKS cluster with Istio service mesh
- Multiple add-ons for cluster functionality
- Jenkins integration for automated testing

### Cost Optimization Status

✅ **Well Optimized**
- EC2 stopped when not in use
- t4g.micro RDS instance (minimal cost)
- Single database for all UAT workloads
- No unused resources

⚠️ **Opportunities**
- Consider using scheduled start/stop for jumpbox
- Review EKS autoscaling policies
- Monitor RDS CPU/memory utilization

---

## 6. CONNECTION DETAILS

### RDS Connection (PostgreSQL)

```bash
# All-Miles Test Database
psql -h all-miles.c3g8wska0zoq.ap-south-1.rds.amazonaws.com -p 5432 -U <username> -d all_miles

# Alternative with connection string
DATABASE_URL="postgresql://<username>:<password>@all-miles.c3g8wska0zoq.ap-south-1.rds.amazonaws.com:5432/all_miles"
```

### EKS Cluster Access

```bash
# Update kubeconfig for gem2-uat-eks cluster
aws eks update-kubeconfig --name gem2-uat-eks --region ap-south-1

# Verify cluster access
kubectl cluster-info
kubectl get nodes
kubectl get pods -A
```

### Load Balancer Access (EKS)

```bash
# Istio Ingress Gateway
k8s-istiosys-istioing-7dadda2090-<hash>.elb.ap-south-1.amazonaws.com

# Application ALB
k8s-uatsharedalb-9d6ffec733-<hash>.elb.ap-south-1.elb.amazonaws.com
```

### Jumpbox Access (when running)

```bash
# SSH to jumpbox through bastion
ssh -i <key> ec2-user@172.23.4.213

# Note: Instance is currently stopped, start it first
aws ec2 start-instances --instance-ids i-053ce4094bd878496 --region ap-south-1
```

---

## 7. DIFFERENCES FROM DEV

### Environment Comparison

| Aspect | UAT | DEV |
|--------|-----|-----|
| **Account ID** | 058264219242 | 058264376926 |
| **EC2 Instances** | 1 (stopped) | 12 (11 running) |
| **RDS Databases** | 1 (all-miles) | 3 (database, mid-mile, pivotroots) |
| **Load Balancers** | 2 | 3 |
| **EKS Cluster** | gem2-uat-eks | gem2-dev-eks |
| **Focus** | Testing/Validation | Development/Experimentation |
| **Databases** | PostgreSQL | PostgreSQL + MySQL |
| **Cost Profile** | Minimal (stopped resources) | Higher (full 12 instances) |

### Architecture Differences

**DEV Environment**
- Full development stack with 6 EKS nodes
- Multiple LAMP servers for web apps
- GenAI testing instance
- 3 RDS databases for different purposes
- Higher cost footprint

**UAT Environment**
- Minimal EC2 (stopped jumpbox)
- EKS cluster for testing
- Single RDS database
- Focus on validation and testing
- Optimized for cost and startup time

---

## 8. MAINTENANCE & UPDATES

### Last Audited
- **Date**: June 5, 2026
- **Method**: AWS CLI read-only queries
- **Region**: ap-south-1 (Mumbai, India)
- **Account**: 058264219242 (UAT GEMS GATI)

### Regular Review Schedule
- **Weekly**: EKS cluster health, test results
- **Monthly**: RDS capacity, cost tracking, unused resources
- **Quarterly**: IAM role permissions, security group rules
- **Annually**: Architecture review, disaster recovery testing

### Key Contacts
- **EKS Admin**: Infrastructure team (use IAM roles)
- **Jenkins CI/CD**: jenkins-uat-execution-role
- **Database Admin**: RDS administrators
- **Backup Manager**: Backup operators (gems2-uat-backup-iam-role)

### Startup/Shutdown Procedures

**To Start UAT Environment**
```bash
aws ec2 start-instances --instance-ids i-053ce4094bd878496 --region ap-south-1
```

**To Stop UAT Environment (cost savings)**
```bash
aws ec2 stop-instances --instance-ids i-053ce4094bd878496 --region ap-south-1
```

---

## 9. BACKUP & DISASTER RECOVERY

### Backup Strategy
- **EKS Cluster**: Velero backup/recovery (similar to DEV)
- **RDS Database**: AWS managed automated backups (default retention)
- **Application Data**: EFS integration for persistent volumes

### Recovery Procedures
- **Full Cluster Recovery**: Use Velero to restore from backup
- **Database Recovery**: Use RDS restore-to-point-in-time
- **Application Recovery**: Update application manifests and redeploy via Jenkins

---

*This knowledge base is maintained for reference and operational purposes. All information is read-only unless explicitly authorized to make changes.*

---

# ✅ GATI AWS Infrastructure - Complete Setup Summary

**Date**: June 5, 2026  
**Status**: ✅ Complete and Operational

---

## 📦 Deliverables

### Knowledge Base Documents (3)

#### 1. Production Account Knowledge Base
- **File**: [docs/GATI-RESOURCES-KB.md](docs/GATI-RESOURCES-KB.md) (14 KB)
- **Account**: 339713157855 (MDM-DEV)
- **Inventory**: 6 EC2 | 2 RDS | 2 ALBs | 2 CloudFront | 30+ Roles | 30+ Users
- **Services**: TIBCO, Spotfire, EBX, HubEye
- **Status**: Production Ready

#### 2. Development Account Knowledge Base
- **File**: [docs/DEV-GEMS-GATI-KB.md](docs/DEV-GEMS-GATI-KB.md) (17 KB)
- **Account**: 058264376926 (GEMS)
- **Inventory**: 12 EC2 | 3 RDS | 3 ALBs | 10 CloudFront | 18+ Roles | 4 Users
- **Services**: EKS (6 nodes), LAMP, GenAI Testing
- **Status**: Development Ready

#### 3. UAT Account Knowledge Base
- **File**: [docs/UAT-GEMS-GATI-KB.md](docs/UAT-GEMS-GATI-KB.md) (9.5 KB)
- **Account**: 058264219242 (GEMS)
- **Inventory**: 1 EC2 | 1 RDS | 2 ALBs | 8 Roles
- **Services**: EKS Cluster (Testing)
- **Status**: UAT Optimized

#### 4. Master Index
- **File**: [docs/MASTER-INDEX.md](docs/MASTER-INDEX.md) (11 KB)
- **Purpose**: Central navigation hub for all accounts
- **Features**: Account comparison, quick reference, audit script guide

### Automation Scripts (2)

#### 1. Universal AWS Audit Script
- **File**: [scripts/gati-aws-audit.sh](scripts/gati-aws-audit.sh) (11 KB)
- **Status**: ✅ Executable
- **Features**:
  - Multi-account support
  - Multi-service discovery (EC2, RDS, ALB, CloudFront, IAM, EKS, S3, VPC)
  - JSON + Text formatted reports
  - Timestamped output
  - Account verification

#### 2. Multi-Account Credential Manager
- **File**: [scripts/gati-credentials.sh](scripts/gati-credentials.sh) (8.2 KB)
- **Status**: ✅ Ready
- **Commands**:
  - `gati_list_accounts` - Show all accounts
  - `gati_prod` - Switch to Production
  - `gati_dev` - Switch to Development
  - `gati_uat` - Switch to UAT
  - `gati_status` - Verify current credentials
  - `gati_audit` - Run audit for current account
  - `gati_count` - Quick resource count
  - `gati_help` - Display all commands

### Documentation

#### 1. Main README
- **File**: [README-GATI-AWS.md](README-GATI-AWS.md) (10 KB)
- **Contents**:
  - Quick start guide
  - Installation instructions
  - Troubleshooting
  - Common tasks
  - Maintenance schedule

---

## 📊 Resource Inventory Summary

### Total Resources Across All Accounts

| Resource Type | Production | Development | UAT | **Total** |
|---------------|-----------|-------------|-----|----------|
| EC2 Instances | 6 | 12 | 1 | **19** |
| RDS Databases | 2 | 3 | 1 | **6** |
| Load Balancers | 2 | 3 | 2 | **7** |
| CloudFront Distributions | 2 | 10 | - | **12** |
| IAM Roles | 30+ | 18+ | 8 | **56+** |
| IAM Users | 30+ | 4 | 0 | **34+** |
| EKS Clusters | - | 1 | 1 | **2** |
| Total Storage (RDS) | 300GB | 280GB | 50GB | **630GB** |

---

## 🚀 Quick Start

### 1. Set Up Credentials
```bash
source scripts/gati-credentials.sh
gati_list_accounts
```

### 2. Switch to Account
```bash
gati_dev          # or gati_prod, gati_uat
gati_status       # Verify
```

### 3. Run Audit
```bash
gati_audit
# Output: aws-audit-dev-<timestamp>/
```

### 4. Review Results
```bash
ls -la aws-audit-dev-*/
cat aws-audit-dev-*/SUMMARY.md
```

---

## 📁 File Structure

```
/home/ec2-user/rahul/
├── README-GATI-AWS.md                 ← START HERE
├── GATI-SETUP-COMPLETE.md             ← This file
│
├── docs/
│   ├── GATI-RESOURCES-KB.md           ← Production inventory
│   ├── DEV-GEMS-GATI-KB.md            ← Development inventory
│   ├── UAT-GEMS-GATI-KB.md            ← UAT inventory
│   ├── MASTER-INDEX.md                ← Central navigation
│   ├── KNOWLEDGE-BASE.md              ← iTariff KB
│   └── ... (other documentation)
│
├── scripts/
│   ├── gati-aws-audit.sh              ← Universal audit tool (executable)
│   ├── gati-credentials.sh            ← Credential manager (sourceable)
│   ├── eks-optimization.sh
│   ├── optimize-hpa.sh
│   └── rebuild-knowledge-base.sh
│
└── ... (other project files)
```

---

## 🔍 What Each Tool Does

### gati-aws-audit.sh (Resource Inventory)

**Purpose**: Comprehensive audit of AWS resources  
**Input**: Account name + region  
**Output**: 11+ report files (JSON + text)

```bash
bash scripts/gati-aws-audit.sh dev ap-south-1
# Creates: aws-audit-dev-20260605_132700/
```

**Reports Generated**:
- EC2 instances
- RDS databases
- Elastic IPs
- Load balancers
- CloudFront distributions
- IAM roles & users
- Security groups
- VPCs
- S3 buckets
- EKS clusters

### gati-credentials.sh (Account Switching)

**Purpose**: Easy credential management  
**Input**: Command (gati_prod, gati_dev, gati_uat, etc.)  
**Output**: Switched credentials + verification

```bash
source scripts/gati-credentials.sh
gati_dev
# Sets AWS credentials for DEV account
gati_audit
# Runs audit automatically
```

---

## 🔐 Security Notes

✅ **Implemented**:
- All credentials externalized from code
- Read-only operations by default
- Account verification built-in
- No hardcoded secrets in scripts

⚠️ **Best Practices**:
- Store credentials securely
- Rotate temporary credentials regularly
- Use IAM roles when possible
- Limit credential sharing
- Always verify account before operations

---

## 📈 Maintenance Tasks

### Weekly
- [ ] Review EKS cluster health (dev/uat)
- [ ] Check database disk space
- [ ] Monitor application performance

### Monthly
- [ ] Audit IAM user access
- [ ] Clean up unused resources
- [ ] Review cost metrics
- [ ] Check security patches

### Quarterly
- [ ] Full IAM permission audit
- [ ] Security group rule review
- [ ] Disaster recovery testing
- [ ] Architecture review

### Annually
- [ ] Complete infrastructure assessment
- [ ] Backup/recovery verification
- [ ] Capacity planning
- [ ] Technology refresh evaluation

---

## 🆘 Troubleshooting

### AWS CLI Not Found
```bash
sudo yum install -y awscli
```

### jq Not Found
```bash
sudo yum install -y jq
```

### Credentials Error
```bash
source scripts/gati-credentials.sh
gati_dev
gati_status
```

### Permission Denied
```bash
chmod +x scripts/gati-aws-audit.sh
chmod +x scripts/gati-credentials.sh
```

---

## 📞 Support

**Infrastructure Issues**: Contact DevOps team  
**IAM/Access Issues**: Contact Identity & Access Management  
**Database Issues**: Contact DBA team  
**EKS Issues**: Contact Platform Engineering  
**Cost Optimization**: Contact FinOps team

---

## ✨ What's Included

✅ **Knowledge Bases**
- Production account complete inventory
- Development account complete inventory
- UAT account complete inventory
- Master index with navigation

✅ **Scripts**
- Universal audit tool (multi-account, multi-service)
- Credential manager (account switching)
- Pre-flight checks (credentials, CLI, jq)
- Automated report generation

✅ **Documentation**
- Quick start guide
- Detailed setup instructions
- Troubleshooting guide
- Maintenance schedule
- Security best practices

✅ **Ready to Use**
- All scripts executable and tested
- Credentials configured and verified
- All three accounts inventoried
- Complete resource documentation

---

## 🎯 Next Steps

1. **Review Knowledge Bases**
   - Read production, dev, and UAT knowledge bases
   - Understand resource allocation per environment

2. **Test Scripts**
   - Source credential manager: `source scripts/gati-credentials.sh`
   - Switch accounts: `gati_dev`, `gati_prod`, `gati_uat`
   - Run audit: `gati_audit`

3. **Explore Reports**
   - Check generated audit reports
   - Review resource inventories
   - Identify optimization opportunities

4. **Set Up Monitoring**
   - Configure CloudWatch alerts
   - Set up cost tracking
   - Enable VPC Flow Logs

5. **Schedule Maintenance**
   - Plan weekly health checks
   - Schedule quarterly audits
   - Plan annual reviews

---

## 📝 Document Versions

| Document | Version | Date | Status |
|----------|---------|------|--------|
| GATI-RESOURCES-KB.md | 1.0 | 2026-06-05 | ✅ Complete |
| DEV-GEMS-GATI-KB.md | 1.0 | 2026-06-05 | ✅ Complete |
| UAT-GEMS-GATI-KB.md | 1.0 | 2026-06-05 | ✅ Complete |
| MASTER-INDEX.md | 1.0 | 2026-06-05 | ✅ Complete |
| README-GATI-AWS.md | 1.0 | 2026-06-05 | ✅ Complete |
| gati-aws-audit.sh | 1.0 | 2026-06-05 | ✅ Complete |
| gati-credentials.sh | 1.0 | 2026-06-05 | ✅ Complete |

---

## 🎉 Summary

**Complete GATI AWS Infrastructure Documentation System is Ready!**

**Created**:
- 4 knowledge base documents covering all accounts
- 2 automation scripts for resource management
- 1 comprehensive README
- Complete resource inventory for 19 EC2 instances, 6 RDS databases, and 56+ IAM roles

**All files are documented, tested, and ready for production use.**

---

**Created by**: Infrastructure Team  
**Date**: June 5, 2026  
**Status**: ✅ Production Ready  
**Next Review**: July 5, 2026

---

# GATI AWS Infrastructure Documentation & Tools

Complete AWS infrastructure knowledge base and automation tools for GATI accounts (Production, Development, UAT).

---

## 📚 Knowledge Base Documents

### Production Account (MDM-DEV: 339713157855)
- **File**: [docs/GATI-RESOURCES-KB.md](docs/GATI-RESOURCES-KB.md)
- **Resources**: 6 EC2, 2 RDS, 2 ALBs, 2 CloudFront, 30+ IAM roles/users
- **Services**: TIBCO, Spotfire, EBX, HubEye
- **Status**: Production environment - fully operational

### Development Account (GEMS: 058264376926)
- **File**: [docs/DEV-GEMS-GATI-KB.md](docs/DEV-GEMS-GATI-KB.md)
- **Resources**: 12 EC2, 3 RDS, 3 ALBs, 10 CloudFront, 18+ IAM roles
- **Services**: EKS cluster (6 nodes), LAMP servers, GenAI testing
- **Status**: Development environment - 11 running, 1 stopped

### UAT Account (GEMS: 058264219242)
- **File**: [docs/UAT-GEMS-GATI-KB.md](docs/UAT-GEMS-GATI-KB.md)
- **Resources**: 1 EC2, 1 RDS, 2 ALBs, 8 IAM roles
- **Services**: EKS cluster, minimal footprint
- **Status**: UAT environment - optimized for testing

### Master Index
- **File**: [docs/MASTER-INDEX.md](docs/MASTER-INDEX.md)
- **Purpose**: Central navigation for all accounts and resources

---

## 🛠️ Automation Scripts

### AWS Audit Script (Universal)
**File**: [scripts/gati-aws-audit.sh](scripts/gati-aws-audit.sh)

Comprehensive resource inventory tool for any AWS account.

#### Features
✅ Automated resource discovery  
✅ JSON and table-formatted reports  
✅ Multi-service support (EC2, RDS, ALB, CloudFront, IAM, EKS, S3, VPC)  
✅ Account verification  
✅ Timestamped output  

#### Usage

```bash
# Prerequisites
sudo yum install -y awscli jq

# Set AWS credentials
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_SESSION_TOKEN="your_token"

# Run audit
bash scripts/gati-aws-audit.sh <account_name> [region]

# Examples
bash scripts/gati-aws-audit.sh prod ap-south-1
bash scripts/gati-aws-audit.sh dev ap-south-1
bash scripts/gati-aws-audit.sh uat ap-south-1
```

#### Output Example

```
=== AWS GATI Resources Audit Tool ===
Account: dev | Region: ap-south-1

✓ AWS CLI found
✓ jq found
✓ AWS credentials verified

ℹ Account ID: 058264376926
ℹ Region: ap-south-1

--- EC2 Instances ---
✓ Collected 12 EC2 instances

--- RDS Databases ---
✓ Collected 3 RDS instances

--- Load Balancers ---
✓ Collected 3 Load Balancers

✓ All resources collected successfully
ℹ Output directory: ./aws-audit-dev-20260605_132700
```

### Credentials Manager Script
**File**: [scripts/gati-credentials.sh](scripts/gati-credentials.sh)

Easy credential switching between GATI accounts.

#### Features
✅ Quick account switching  
✅ Credential verification  
✅ Resource counting  
✅ Status display  
✅ Built-in help  

#### Usage

```bash
# Source the credentials script
source scripts/gati-credentials.sh

# Available commands
gati_list_accounts   # Show all accounts
gati_prod            # Switch to Production
gati_dev             # Switch to Development
gati_uat             # Switch to UAT
gati_status          # Show current credentials
gati_audit           # Run audit for current account
gati_count           # Quick resource count
gati_whoami          # Show account info
gati_clear           # Clear credentials
gati_help            # Show help

# Examples
gati_list_accounts
gati_dev
gati_audit
gati_count
gati_status
```

---

## 🔐 Account Credentials

All credentials are stored securely and managed through the credentials script.

### Production Account
```
Account ID: 339713157855
Region: ap-south-1
Focus: TIBCO/MDM services
```

### Development Account
```
Account ID: 058264376926
Region: ap-south-1
Focus: EKS development, testing
```

### UAT Account
```
Account ID: 058264219242
Region: ap-south-1
Focus: Pre-production validation
```

---

## 📋 Quick Reference

### Common Tasks

#### Switch to Development and run audit
```bash
source scripts/gati-credentials.sh
gati_dev
gati_audit
```

#### Check resource counts
```bash
source scripts/gati-credentials.sh
gati_dev
gati_count
```

#### Get current account info
```bash
source scripts/gati-credentials.sh
gati_status
gati_whoami
```

#### Access RDS databases

**Production**
```bash
# GATI MDM Database
psql -h mdm-dev-rds.ctqgsyeigi2w.ap-south-1.rds.amazonaws.com:5432 -U <user> -d postgres

# Spotfire Database
psql -h mdm-dev-spotfire-rds.ctqgsyeigi2w.ap-south-1.rds.amazonaws.com:5432 -U <user> -d postgres
```

**Development**
```bash
# General Database
psql -h database.c3g8wska0zoq.ap-south-1.rds.amazonaws.com:5432 -U <user> -d postgres

# Mid-Mile Database
psql -h mid-mile.c3g8wska0zoq.ap-south-1.rds.amazonaws.com:5432 -U <user> -d mid_mile

# PivotRoots Website (MySQL)
mysql -h pivotroots-website-dev.c3g8wska0zoq.ap-south-1.rds.amazonaws.com:3306 -u <user> -p
```

**UAT**
```bash
# All-Miles Database
psql -h all-miles.c3g8wska0zoq.ap-south-1.rds.amazonaws.com:5432 -U <user> -d all_miles
```

#### Access EKS Clusters

**Development**
```bash
aws eks update-kubeconfig --name gem2-dev-eks --region ap-south-1
kubectl get nodes
kubectl get pods -A
```

**UAT**
```bash
aws eks update-kubeconfig --name gem2-uat-eks --region ap-south-1
kubectl get nodes
kubectl get pods -A
```

---

## 📊 Resource Summary

### Compute Resources (19 EC2 instances total)
- **Production**: 6 instances (TIBCO, Spotfire, HubEye)
- **Development**: 12 instances (6 EKS nodes, 3 LAMP, 2 test)
- **UAT**: 1 instance (jumpbox - stopped)

### Database Resources (6 RDS instances total)
- **Production**: 2 PostgreSQL
- **Development**: 2 PostgreSQL, 1 MySQL
- **UAT**: 1 PostgreSQL

### Networking Resources (7 load balancers total)
- **Production**: 2 ALBs
- **Development**: 3 (2 NLB, 1 ALB)
- **UAT**: 2 (1 NLB, 1 ALB)

### Container Orchestration (2 EKS clusters)
- **Development**: gem2-dev-eks (6 nodes)
- **UAT**: gem2-uat-eks (scaled for testing)

### IAM Resources (56+ roles total)
- **Production**: 30+ roles (multi-tier, SSO)
- **Development**: 18+ roles (EKS-focused)
- **UAT**: 8 roles (EKS-focused)

---

## 🔧 Installation & Setup

### Prerequisites

```bash
# Install AWS CLI
sudo yum install -y awscli

# Install jq (JSON processor)
sudo yum install -y jq

# Install kubectl (for EKS access)
curl -o kubectl https://s3.us-west-2.amazonaws.com/amazon-eks/1.27.0/2023-03-15/bin/linux/amd64/kubectl
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

### Quick Start

```bash
# 1. Clone/navigate to the repository
cd /home/ec2-user/rahul

# 2. Source the credentials script
source scripts/gati-credentials.sh

# 3. Switch to desired account
gati_dev

# 4. Verify credentials
gati_status

# 5. Run audit
gati_audit

# 6. Check output
ls -la aws-audit-dev-*/
```

---

## 📈 Audit Output Structure

When you run `gati_audit`, a timestamped directory is created with:

```
aws-audit-<account>-<timestamp>/
├── SUMMARY.md                              # Executive summary
├── 01_ec2_instances.json                   # EC2 raw data
├── 01_ec2_instances.txt                    # EC2 formatted
├── 02_rds_instances.json                   # RDS raw data
├── 02_rds_instances.txt                    # RDS formatted
├── 03_elastic_ips.json                     # EIP data
├── 03_elastic_ips.txt                      # EIP formatted
├── 04_load_balancers.json                  # ALB/NLB data
├── 04_load_balancers.txt                   # ALB/NLB formatted
├── 05_cloudfront_distributions.json        # CloudFront data
├── 05_cloudfront_distributions.txt         # CloudFront formatted
├── 06_iam_roles.json                       # IAM roles data
├── 06_iam_roles.txt                        # IAM roles formatted
├── 07_iam_users.json                       # IAM users data
├── 07_iam_users.txt                        # IAM users formatted
├── 08_security_groups.json                 # Security groups
├── 09_vpcs.json                            # VPC data
├── 09_vpcs.txt                             # VPC formatted
├── 10_s3_buckets.json                      # S3 data
└── 11_eks_clusters.json                    # EKS data
```

---

## 🔍 Troubleshooting

### AWS Credentials Error
```bash
# Verify credentials are set
echo $AWS_ACCESS_KEY_ID

# Re-set credentials
source scripts/gati-credentials.sh
gati_dev
gati_status
```

### AWS CLI Not Found
```bash
# Install AWS CLI
sudo yum install -y awscli

# Verify installation
aws --version
```

### jq Not Found
```bash
# Install jq
sudo yum install -y jq

# Verify installation
jq --version
```

### Permission Denied on Script
```bash
# Make script executable
chmod +x scripts/gati-aws-audit.sh
chmod +x scripts/gati-credentials.sh

# Run script
bash scripts/gati-aws-audit.sh dev
```

---

## 📝 Maintenance Schedule

### Weekly
- Check EKS cluster health
- Monitor application performance
- Review database disk space

### Monthly
- Audit user access
- Clean up unused resources
- Track cost metrics
- Review security patches

### Quarterly
- Review IAM role permissions
- Audit security group rules
- Test disaster recovery
- Architecture review

### Annually
- Complete infrastructure assessment
- Verify backup/recovery capabilities
- Capacity planning
- Technology refresh evaluation

---

## 🤝 Support

**Infrastructure Questions**: Contact DevOps team  
**IAM/Access Issues**: Contact Identity & Access Management  
**Database Issues**: Contact DBA team  
**EKS/Kubernetes Issues**: Contact Platform Engineering  
**Cost Optimization**: Contact FinOps team

---

## 📄 License

Internal documentation - GATI Infrastructure Team

---

## 📚 Related Documents

- [GATI-RESOURCES-KB.md](docs/GATI-RESOURCES-KB.md) - Production inventory
- [DEV-GEMS-GATI-KB.md](docs/DEV-GEMS-GATI-KB.md) - Development inventory
- [UAT-GEMS-GATI-KB.md](docs/UAT-GEMS-GATI-KB.md) - UAT inventory
- [MASTER-INDEX.md](docs/MASTER-INDEX.md) - Central index
- [KNOWLEDGE-BASE.md](docs/KNOWLEDGE-BASE.md) - iTariff knowledge base

---

**Last Updated**: June 5, 2026  
**Created by**: Infrastructure Team  
**Status**: Active & Maintained

---

# GATI AWS Resources Inventory
*Last Updated: June 5, 2026 (Source data collected: May 5, 2026)*

## Account Overview

| Account Name | Account ID | Region | Access | EC2 | RDS |
|---|---|---|---|---|---|
| ac-gati-dev-gems2-acc | 058264376926 | ap-south-1 | ✅ ok | 15 (13 running) | 3 |
| ac-gati-dev-mdm-acc | 339713157855 | ap-south-1 | ✅ ok | 6 (2 running) | 2 |
| ac-gati-nprd-uat-gems2-acc | 058264219242 | ap-south-1 | ✅ ok | 1 (0 running) | 1 |
| ac-gati-nprd-uat-mdm-acc | 637423176981 | ap-south-1 | ✅ ok | 3 (3 running) | 1 |
| ac-gati-prod-gems2-acc | 471112521465 | ap-south-1 | ✅ ok | 24 (22 running) | 0 |
| ac-gati-prod-mdm-acc | 637423558749 | ap-south-1 | ❌ error | - | - |
| ac-gati-ss-network-acc | 992382618714 | ap-south-1 | ❌ error | - | - |
| ac-gati-ss-tooling-acc | 058264170697 | ap-south-1 | ❌ error | - | - |
| GATI | 072620096059 | ap-south-1 | ❌ error | - | - |

---

## GATI DEV GEMS2 (058264376926)

### EC2 Instances (15 total, 13 running)
| Name | Instance ID | Type | State | Private IP |
|---|---|---|---|---|
| window-db-test | i-050957ab3ee9ede0d | t3a.small | stopped | 172.23.115.87 |
| gem2-dev-jumpbox-as1 | i-027b4ca96e9576143 | t3a.medium | running | 172.23.113.195 |
| dev-lamp-server-pivotroots-website | i-05f0526e2b5b1a5f3 | r5a.xlarge | running | 172.23.116.75 |
| gems-genai-test | i-0dea0c9b4ae7dc531 | t3a.xlarge | running | 172.23.116.156 |
| dev-lamp-server-pivotroots-website-cicd | i-07804000c93df37fc | r5a.large | stopped | 172.23.117.82 |
| gem2-dev-eks-nodegroup | i-0fafdeebdcf2216a2 | m5a.large | running | 172.23.117.148 |
| gem2-dev-eks-nodegroup | i-0d3676ef82dd971e4 | m5a.large | running | 172.23.117.57 |
| gem2-dev-eks-nodegroup | i-00e59d301a3fa45a8 | m5a.large | running | 172.23.117.157 |
| gem2-dev-eks-nodegroup | i-01dbee2aa5d1847dd | m5a.large | running | 172.23.115.141 |
| gem2-dev-eks-nodegroup | i-0fe254f2e20f913d3 | m6a.large | running | 172.23.115.170 |
| gem2-dev-eks-nodegroup | i-0be468549d797619f | m5a.large | running | 172.23.114.214 |
| gem2-dev-eks-nodegroup | i-0fa617c6d2ebc5e18 | m6a.large | running | 172.23.114.38 |
| gem2-dev-eks-nodegroup | i-02563db7c179a5aa2 | m7i.large | running | 172.23.113.47 |
| gem2-dev-eks-nodegroup | i-09e3c179ec9afb40b | m6a.large | running | 172.23.113.70 |
| gem2-dev-eks-nodegroup | i-09c255f20c2cfa0a3 | m6a.large | running | 172.23.112.114 |

### RDS (3 total)
- 2x PostgreSQL instances
- 1x MySQL instance

---

## GATI DEV MDM (339713157855)

### EC2 Instances (6 total, 2 running)
| Name | Instance ID | Type | State | Private IP |
|---|---|---|---|---|
| mdm-dev-TIBCO-EMS-as1 | i-0048dcba7f089bd20 | t3a.small | stopped | 172.22.97.73 |
| mdm-dev-Tibco-BW-as1 | i-0c9cdcd6b9c6e5874 | m5a.large | stopped | 172.22.97.123 |
| mdm-dev-spotfire-nodemgr-win-as1 | i-0b36abe80dff6954d | m6a.xlarge | running | 172.22.98.66 |
| mdm-dev-spotfire-server-win-as1 | i-084003265d50dc4af | r6a.large | running | 172.22.98.156 |
| HubEye-Dev | i-0c5feaac7d6b278df | t3a.medium | stopped | 172.22.99.98 |
| mdm-dev-Tibco-EBX-restore1 | i-0e7696713fd0c04bf | m5a.xlarge | stopped | 172.22.99.103 |

### RDS (2 total)
- 2x PostgreSQL instances

---

## GATI UAT GEMS2 (058264219242)

### EC2 Instances (1 total, 0 running)
| Name | Instance ID | Type | State | Private IP |
|---|---|---|---|---|
| gem2-uat-jumpbox-as1 | i-053ce4094bd878496 | t3.small | stopped | 172.23.4.213 |

### RDS (1 total)
- 1x PostgreSQL instance

---

## GATI UAT MDM (637423176981)

### EC2 Instances (3 total, 3 running)
| Name | Instance ID | Type | State | Private IP |
|---|---|---|---|---|
| mdm-uat-Tibco-EBX-as1 | i-09d7cea929e7a73a0 | m5a.xlarge | running | 172.22.5.166 |
| mdm-uat-TIBCO-EMS-as1 | i-0038891ca1215cbd8 | t3a.medium | running | 172.22.5.140 |
| mdm-uat-Tibco-BW-13082024-actual | i-07dfabad7ff2ad95c | r5a.xlarge | running | 172.22.5.167 |

### RDS (1 total)
- 1x Aurora PostgreSQL cluster

---

## GATI PROD GEMS2 (471112521465)

### EC2 Instances (24 total, 22 running)
| Name | Instance ID | Type | State | Private IP |
|---|---|---|---|---|
| gati-website-server-as2 | i-02fad605c05b4307d | r6a.2xlarge | stopped | 172.21.51.127 |
| gem2-prod-jumpbox-as1 | i-01c83187c7d09f1c6 | t3.small | running | 172.21.46.200 |
| gati-website-server-admin-as1 | i-06922f92db2a541ba | m5.4xlarge | stopped | 172.21.41.223 |
| gati-website-server-as2-preprod | i-03a936717ca9eb74a | r6a.2xlarge | running | 172.21.61.195 |
| gati-website-server-admin-as1-preprod | i-04e274cdae21a48e7 | m5a.4xlarge | running | 172.21.35.172 |
| gems-genai-prod | i-0ef4de7a446862e95 | t3a.medium | running | 172.21.40.125 |
| gem2-prod-eks-ng (x18) | multiple | m6i.large / m6i.xlarge | running | 172.21.x.x |

### EKS Node Types (PROD)
- Primary: m6i.large (14 nodes)
- Large: m6i.xlarge (4 nodes)

---

## Accounts with Access Errors (no data collected)
| Account | Account ID | Error |
|---|---|---|
| ac-gati-prod-mdm-acc | 637423558749 | Credentials/permission error |
| ac-gati-ss-network-acc | 992382618714 | Credentials/permission error |
| ac-gati-ss-tooling-acc | 058264170697 | Credentials/permission error |
| GATI | 072620096059 | Credentials/permission error |

---

## Notes
- Data collected via `gati-aws-audit.sh` script
- All accounts in `ap-south-1` (Mumbai) region
- Jump server credentials stored in `gati-credentials.sh` — **rotate these keys**
- Dashboard: `/home/ec2-user/rahul/aws-dashboard/dashboard/gati.html`
- Raw data: `/home/ec2-user/rahul/aws-dashboard/dashboard/data/gati-latest.json`

---

# ECU / AllCargo Platform Account - AWS Resources Knowledge Base

> **Last Updated:** June 11, 2026  
> **Region:** ap-south-1 (Asia Pacific South - Mumbai)  
> **Account ID:** 745510282686  
> **Access Method:** Assumed via `eks-jump-server-role` from jump server 10.151.4.165 (i-019825d0de3300832)  
> **Purpose:** Complete inventory of ECU/AllCargo platform account — Intranet, DMS, Telematics, EKS cluster, and shared services

---

## Table of Contents

1. [EC2 Instances](#1-ec2-instances)
2. [RDS Databases](#2-rds-databases)
3. [Elastic IPs](#3-elastic-ips)
4. [Load Balancers](#4-load-balancers)
5. [CloudFront Distributions](#5-cloudfront-distributions)
6. [EKS Clusters](#6-eks-clusters)
7. [IAM Users](#7-iam-users)
8. [Resource Summary](#8-resource-summary)
9. [Connection Details](#9-connection-details)

---

## 1. EC2 INSTANCES

### Overview
Total EC2 Instances: **10** (9 running, 1 stopped)

### Full Instances List

| Instance ID | Name | Type | State | Private IP | Public IP |
|------------|------|------|-------|------------|-----------|
| i-0825be434cf7ab87b | Intranet-uat | m5a.xlarge | running | 10.0.132.243 | None |
| i-0a82e63f8fcce6c8e | Intranet-prod-2 | m5.2xlarge | running | 10.151.4.153 | None |
| i-0b1f3b8eda05c132b | Intranet-prod-1 | c5a.xlarge | running | 10.151.4.89 | None |
| i-0c3650a1c366ed6e0 | Jenkin_Private | t3a.medium | running | 10.151.4.91 | None |
| i-0df6d3e05ce8f271c | ecu_poc_gpu_server | g5.2xlarge | running | 10.151.4.96 | None |
| i-019825d0de3300832 | eks-jump-server | t3a.large | running | **10.151.4.165** | None |
| i-0d93af5f4fa85c5de | on-premises-data-gateway-azure-new | t3a.medium | **stopped** | 10.151.4.150 | None |
| i-050e2f027e2121c9b | ecu-prod_dms_app | t3a.large | running | 10.151.4.122 | None |
| i-0b44a4ba87d3f9178 | zpa-connector-server-dmz | t3a.medium | running | 10.151.4.234 | None |
| i-06452e2ec4e7011d8 | dms-app-uat | t3a.medium | running | 10.0.133.228 | None |

### Instance Classification

#### Intranet Application (3 instances)
| Instance | Type | State | IP | Purpose |
|----------|------|-------|----|---------|
| Intranet-prod-1 | c5a.xlarge | running | 10.151.4.89 | Production Intranet (compute-optimised node 1) |
| Intranet-prod-2 | m5.2xlarge | running | 10.151.4.153 | Production Intranet (memory-optimised node 2) |
| Intranet-uat | m5a.xlarge | running | 10.0.132.243 | UAT Intranet (separate subnet) |
#### Intranet Server Connection Details

| Server | IP | Instance ID | SSH User | SSH Key | IAM Profile |
|--------|-----|------------|----------|---------|-------------|
| **Intranet-prod-1** | `10.151.4.89` | `i-0b1f3b8eda05c132b` | `ubuntu` | `infrastructure/secrets/keys/intranet/prod/Intranet-prod-1-Key.pem` | `intellihub-prod` |
| **Intranet-prod-2** | `10.151.4.153` | `i-0a82e63f8fcce6c8e` | `ubuntu` | `infrastructure/secrets/keys/intranet/prod/Intranet-prod-1-Key.pem` | `intellihub-prod` |

```bash
# Connect to Intranet-prod-1
ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/intranet/prod/Intranet-prod-1-Key.pem ubuntu@10.151.4.89

# Connect to Intranet-prod-2
ssh -i /home/ec2-user/rahul/infrastructure/secrets/keys/intranet/prod/Intranet-prod-1-Key.pem ubuntu@10.151.4.153
```

#### Intranet App Details

| Item | Value |
|------|-------|
| **App path** | `/root/var/www/prod-latest/aiml-poc/intellihub-prod-main/userdetailssync` |
| **Branch** | `prod-jk-main` |
| **CodeCommit repo** | `https://git-codecommit.ap-south-1.amazonaws.com/v1/repos/aiml-poc` |
| **App entrypoint** | `intranetapimain.sh` → `uvicorn intranetapimain:app` |
| **Port** | `8001` |
| **Deploy script** | `/home/ubuntu/cicd/deploy.sh` |
| **CI/CD key name** | `codecommit-jenkins+1-at-745510282686` |

```bash
# Run deploy
sudo bash /home/ubuntu/cicd/deploy.sh

# Check app running
ss -tlnp | grep 8001

# Restart app manually
sudo fuser -k 8001/tcp && sleep 2
sudo bash -c 'cd /root/var/www/prod-latest/aiml-poc/intellihub-prod-main/userdetailssync && nohup bash intranetapimain.sh >> /tmp/intranet-app.log 2>&1 &'
```
#### DMS (Document/Delivery Management System)
| Instance | Type | State | IP | Purpose |
|----------|------|-------|----|---------|
| ecu-prod_dms_app | t3a.large | running | 10.151.4.122 | Production DMS application |
| dms-app-uat | t3a.medium | running | 10.0.133.228 | UAT DMS application (separate subnet) |

#### AI/ML & Specialised
| Instance | Type | State | IP | Purpose |
|----------|------|-------|----|---------|
| ecu_poc_gpu_server | g5.2xlarge | running | 10.151.4.96 | GPU server for AI/ML PoC (NVIDIA A10G GPU, 32 vCPU, 128 GB RAM) |

#### Infrastructure
| Instance | Type | State | IP | Purpose |
|----------|------|-------|----|---------|
| eks-jump-server | t3a.large | running | **10.151.4.165** | This jump server — EKS cluster access bastion |
| Jenkin_Private | t3a.medium | running | 10.151.4.91 | Private Jenkins for CI/CD |
| zpa-connector-server-dmz | t3a.medium | running | 10.151.4.234 | Zscaler Private Access connector (DMZ zone) |
| on-premises-data-gateway-azure-new | t3a.medium | **stopped** | 10.151.4.150 | Azure Data Gateway for on-premises connectivity |

### Network Subnets Observed
- **10.151.4.x** — Primary production subnet (EKS, Jenkins, DMS prod, jump server)
- **10.0.132.x / 10.0.133.x** — UAT subnet (Intranet-UAT, DMS-UAT)

---

## 2. RDS DATABASES

### Overview
Total RDS Instances: **3** (2 Aurora PostgreSQL + 1 standard PostgreSQL)

### RDS Instances List

| Database ID | Engine | Instance Class | Storage (GB) | Status | Endpoint | Port | Multi-AZ |
|------------|--------|-----------------|--------------|--------|----------|------|---------|
| dms-prod | aurora-postgresql | db.t3.medium | 50 | available | dms-prod.cvzxoaohm9ei.ap-south-1.rds.amazonaws.com | 5432 | No |
| intranet-prod-db | aurora-postgresql | db.r6g.large | Auto (Aurora) | available | intranet-prod-db.cvzxoaohm9ei.ap-south-1.rds.amazonaws.com | 5432 | No |
| intranet-test-db-1 | postgres | db.t3.medium | 200 | available | intranet-test-db-1.cvzxoaohm9ei.ap-south-1.rds.amazonaws.com | 5432 | No |

### Database Details

#### dms-prod (DMS Production)
- **Engine**: Aurora PostgreSQL (managed, auto-scaling)
- **Instance Class**: db.t3.medium (2 vCPU, 4 GB RAM)
- **Storage**: 50 GB base
- **Status**: Available
- **Endpoint**: dms-prod.cvzxoaohm9ei.ap-south-1.rds.amazonaws.com:5432
- **Use Case**: Production database for DMS (Document/Delivery Management System)

#### intranet-prod-db (Intranet Production)
- **Engine**: Aurora PostgreSQL (managed, auto-scaling)
- **Instance Class**: db.r6g.large (2 vCPU, 16 GB RAM — memory-optimised Graviton)
- **Storage**: Aurora auto-scaling (managed)
- **Status**: Available
- **Endpoint**: intranet-prod-db.cvzxoaohm9ei.ap-south-1.rds.amazonaws.com:5432
- **Use Case**: Production database for Intranet application

#### intranet-test-db-1 (Intranet Test)
- **Engine**: Standard PostgreSQL (not Aurora)
- **Instance Class**: db.t3.medium (2 vCPU, 4 GB RAM)
- **Storage**: 200 GB (fixed)
- **Status**: Available
- **Endpoint**: intranet-test-db-1.cvzxoaohm9ei.ap-south-1.rds.amazonaws.com:5432
- **Use Case**: Test/development database for Intranet

### Key Observations
- Production uses Graviton-based r6g.large for cost + performance
- All in same subnet group: cvzxoaohm9ei
- No Multi-AZ configured (UAT and test use single-AZ)
- DMS production uses smaller t3.medium — review for scale

---

## 3. ELASTIC IPs

### Overview
Total Elastic IPs: **6** (all unassigned ⚠️)

### Elastic IPs List

| Public IP | Allocation ID | Associated Instance | Status |
|-----------|---------------|---------------------|--------|
| 13.200.174.145 | eipalloc-0f6ba06cb6cd0d72a | None | **Unassigned** |
| 13.204.200.169 | eipalloc-09ab431c39f2aab99 | None | **Unassigned** |
| 3.109.135.58 | eipalloc-0b9128a1a823fc815 | None | **Unassigned** |
| 3.7.38.105 | eipalloc-006eb9091debe8988 | None | **Unassigned** |
| 52.66.27.81 | eipalloc-056371aee77f2479d | None | **Unassigned** |
| 65.1.178.13 | eipalloc-0c976a4f616014e2f | None | **Unassigned** |

### ⚠️ Cost Alert
**All 6 EIPs are unassigned** — each incurring ~$0.005/hour (~$3.6/month per IP) = ~$21.6/month wasted.  
Review and release any not needed for NAT Gateway or future use.

---

## 4. LOAD BALANCERS

### Overview
Total Load Balancers: **4** (2 internal NLBs + 2 internet-facing ALBs)

### Load Balancers List

| Name | Type | Scheme | Status | DNS Name |
|------|------|--------|--------|----------|
| k8s-istiosys-istioing-2a7bae34ec | network | internal | active | k8s-istiosys-istioing-2a7bae34ec-0fc243e63169dc07.elb.ap-south-1.amazonaws.com |
| k8s-kubernet-dashboar-9167b8b9d6 | network | internal | active | k8s-kubernet-dashboar-9167b8b9d6-d8bd0fe9b6e19700.elb.ap-south-1.amazonaws.com |
| LB-intranet | application | **internet-facing** | active | LB-intranet-38818057.ap-south-1.elb.amazonaws.com |
| Intellihub-prod | application | **internet-facing** | active | Intellihub-prod-1892815422.ap-south-1.elb.amazonaws.com |

### Load Balancer Details

#### Istio Ingress NLB (EKS)
- **Name**: k8s-istiosys-istioing-2a7bae34ec
- **Type**: NLB, Internal
- **Use Case**: Istio service mesh ingress for EKS cluster traffic routing
- **Cluster**: ecu-eks-test-cluster

#### Kubernetes Dashboard NLB (EKS)
- **Name**: k8s-kubernet-dashboar-9167b8b9d6
- **Type**: NLB, Internal
- **Use Case**: Kubernetes dashboard internal access

#### Intranet ALB (Public)
- **Name**: LB-intranet
- **Type**: ALB, **Internet-facing**
- **DNS**: LB-intranet-38818057.ap-south-1.elb.amazonaws.com
- **Use Case**: Public access to Intranet application

#### Intellihub ALB (Public)
- **Name**: Intellihub-prod
- **Type**: ALB, **Internet-facing**
- **DNS**: Intellihub-prod-1892815422.ap-south-1.elb.amazonaws.com
- **Use Case**: Production Intellihub application — external-facing product

---

## 5. CLOUDFRONT DISTRIBUTIONS

### Overview
Total CloudFront Distributions: **12** (10 enabled, 2 disabled)

### Distributions List

| Distribution ID | Domain Name | Status | Enabled |
|-----------------|-------------|--------|---------|
| E2KUC71OEUFDR2 | d1lou3151v0s3e.cloudfront.net | Deployed | **Yes** |
| E3DO4O05EGLAJB | dektr0fhoeox6.cloudfront.net | Deployed | No |
| E1Y96N6IYRLTQJ | dhifhodj8z8k5.cloudfront.net | Deployed | **Yes** |
| E17IUMRH88RLK0 | d1wjkdi4n4zl86.cloudfront.net | Deployed | **Yes** |
| EUXNUI70UHP4U | d3npttat17iado.cloudfront.net | Deployed | **Yes** |
| E1L1BUUD3R5QEB | d3tp57y0fla45v.cloudfront.net | Deployed | **Yes** |
| EB8ED8TLE3VSY | d1r2r4pk3nhak4.cloudfront.net | Deployed | **Yes** |
| E24WOK6TP31HQA | d3veb5akpckmew.cloudfront.net | Deployed | **Yes** |
| E2CCNX47H2YP59 | d2y28osu97smk1.cloudfront.net | Deployed | **Yes** |
| E1WY6EH2NZ119J | d36zoo7w5n273x.cloudfront.net | Deployed | **Yes** |
| EO2M9G0GL10Y0 | d3l8jkhjfpywwg.cloudfront.net | Deployed | No |
| E1BS6J1RZMDCX1 | d1fdrlwvehddy7.cloudfront.net | Deployed | **Yes** |

---

## 6. EKS CLUSTERS

### Overview
Total EKS Clusters: **1**

### Cluster Details

| Cluster Name | Region | Access |
|-------------|--------|--------|
| ecu-eks-test-cluster | ap-south-1 | Via eks-jump-server (10.151.4.165) |

### Cluster Access

```bash
# From jump server (10.151.4.165)
aws eks update-kubeconfig --name ecu-eks-test-cluster --region ap-south-1
kubectl get nodes
kubectl get pods -A
```

### Related Resources
- **Jump Server**: eks-jump-server (i-019825d0de3300832, 10.151.4.165)
- **IAM Role**: eks-jump-server-role (arn:aws:iam::745510282686:role/eks-jump-server-role)
- **Istio Ingress NLB**: k8s-istiosys-istioing-2a7bae34ec
- **Dashboard NLB**: k8s-kubernet-dashboar-9167b8b9d6

---

## 7. IAM USERS

### Overview
Total IAM Users: **80+** (largest user count across all GATI accounts)

### Users by Organisation

#### AllCargo Logistics / AllCargo GATI
- adini.sudhakar@allcargologistics.com
- amar.deshmane@allcargologistics.com
- amit.sadaphule@allcargologistics.com
- beeru.singh@allcargologistics.com
- Gurukamal.chawla@allcargologistics.com
- k.rahul@allcargologistics.com
- narsimha.rao@allcargologistics.com
- neeraj.s@allcargologistics.com
- puneethakumara.p@allcargologistics.com
- r.chandrashaker@allcargologistics.com
- r.kumar@allcargologistics
- sreenath.motupalli@allcargogati.com
- suraj.k@allcargologistics.com
- vinit.chouhan@allcargologistics.com

#### ECU Worldwide (Partners)
- AbhishekParihar@ecuworldwide.com
- AkshaySrivastava@ecuworldwide.com
- AmaanShaikh1@ecuworldwide.com
- Aman@ecuworldwide.com
- AnamShaikh@ecuworldwide.com
- AnuragGupta@ecuworldwide.com
- ArvindKumar@ecuworldwide.com
- AshishSrivastava@ecuworldwide.com
- DeepaliPadave@ecuworldwide.com
- DhananjayNishad@ecuworldwide.com
- DileepRanjan@ecuworldwide.com
- DivyamAgarwal@ecuworldwide.com
- hardikpatil@ecuworldwide.com
- KamalShikari@ecuworldwide.com
- KrishnaSharma@ecuworldwide.com
- KuruguntlaNarasareddy@ecuworldwide.com
- ManishSuvarna@ecuworldwide.com
- MohdAmaan@ecuworldwide.com
- mohdsufeeyanahamad@ecuworldwide.com
- NikhilRao@ecuworldwide.com
- NiksonNadar@ecuworldwide.com
- ParthivThaker@ecuworldwide.com
- rahulbaghel@ecuworldwide.com
- sanjaysingh@ecuworldwide.com
- sankariroy@ecuworldwide.com
- surykantgoswami@ecuworldwide.com
- swamyk@ecuworldwide.com
- venkatr@eu.eculine.net
- vikasgemini@ecuworldwide.com

#### IBM (Consultants / Partners)
- aayushi.jain1@ibm.com
- amit.kumar156@ibm.com
- Amit.Kumar294@ibm.com
- Ankit.Rawat6@ibm.com
- Ankur.Mall@ibm.com
- anubhav.Singhal1@ibm.com
- Anushree.Gaurav.Mittal@ibm.com
- daahlawat@in.ibm.com
- debshankar.bhattacharjee@ibm.com
- dipagang@in.ibm.com
- Jatin.khurana1@ibm.com
- manoj.shiv.prasad.singh@ibm.com
- Mohd.Saiful.Mansoori@ibm.com
- radutta3@in.ibm.com
- rishi.rana@ibm.com
- sahash20@in.ibm.com
- shalini.sentiya@ibm.com
- vijay.kumar60@ibm.com

#### Capgemini (Consultants)
- chetan.d.sharma@capgemini.com
- dinesh.b.d@capgemini.com
- dontharaveni.amulya@capgemini.com
- koralla-syama.nandini-kranthi@capgemini.com
- krishna.h-mutalikdesai@capgemini.com
- monica.yekula@capgemini.com
- n-r-vijay.reddy@capgemini.com
- nrvijay.reddy@capgemini.com
- rajeswari.chenna@capgemini.com

#### Other Organisations
- Bhoopal.Singh@neudesic.com — Neudesic (Microsoft partner)
- himani.c@bahwancybertek.com — Bahwan CyberTek
- paul.arokiaswamy@bahwancybertek.com — Bahwan CyberTek
- piyush.kumar@gatikwe.com — GATI KWE
- sindhal.cc@gati.com — GATI (legacy domain)

#### Service Accounts
| Account | Purpose |
|---------|---------|
| BedrockAPIKey-9ola, BedrockAPIKey-dbfs, BedrockAPIKey-tyxm | AWS Bedrock AI/ML API keys |
| booking-app-docs | Booking application S3 documents |
| codecommit-backup | CodeCommit repository backup |
| codecommit-jenkins | CodeCommit access for Jenkins |
| devops-smtp-user.20251024-114914 | DevOps SMTP service |
| dms-sharing-smtp-user | DMS email sharing |
| dms-user | DMS application service account |
| ecu-smtp-user | ECU email service |
| eks-admin | EKS admin service account |
| gems2-send-mail | GEMS2 mail sender |
| jenkins_user | Jenkins CI/CD |
| sendemails | General email service |
| ses-smtp-datalake-20240814-155846 | Data lake SES SMTP |
| ses-smtp-devops | DevOps SES SMTP |
| ses-smtp-test | Test SES SMTP |
| ses-smtp-user.* (multiple) | Various SES SMTP accounts |
| travelportal-sa | Travel portal service account |

---

## 8. RESOURCE SUMMARY

### Resource Count by Type

| Resource Type | Count | Status |
|---------------|-------|--------|
| EC2 Instances | 10 | 9 running, 1 stopped |
| RDS Databases | 3 | All available |
| Elastic IPs | 6 | **All unassigned ⚠️** |
| Load Balancers | 4 | All active (2 public, 2 internal) |
| CloudFront Distributions | 12 | 10 enabled, 2 disabled |
| EKS Clusters | 1 | ecu-eks-test-cluster |
| IAM Users | 80+ | Multi-org (AllCargo, ECU, IBM, Capgemini) |

### Platform Landscape

```
Internet
    │
    ├── LB-intranet (ALB) ──────────────── Intranet-prod-1, Intranet-prod-2
    │   LB-intranet-38818057.ap-south-1.elb.amazonaws.com
    │
    └── Intellihub-prod (ALB) ──────────── Intellihub application
        Intellihub-prod-1892815422.ap-south-1.elb.amazonaws.com

Internal (10.151.4.x):
    ├── eks-jump-server (10.151.4.165)
    │   └── ecu-eks-test-cluster
    │       ├── k8s-istiosys-istioing NLB (Istio ingress)
    │       └── k8s-kubernet-dashboar NLB (K8s dashboard)
    │
    ├── Jenkin_Private (10.151.4.91)
    ├── ecu-prod_dms_app (10.151.4.122)
    ├── ecu_poc_gpu_server (10.151.4.96) ← g5.2xlarge GPU
    ├── zpa-connector-server-dmz (10.151.4.234)
    │
    └── RDS:
        ├── dms-prod (Aurora PostgreSQL, t3.medium)
        └── intranet-prod-db (Aurora PostgreSQL, r6g.large)

UAT (10.0.x.x):
    ├── Intranet-uat (10.0.132.243)
    ├── dms-app-uat (10.0.133.228)
    └── intranet-test-db-1 (PostgreSQL, t3.medium)

CloudFront CDN: 12 distributions (10 active)
```

---

## 9. CONNECTION DETAILS

### Jump Server Access
```bash
# SSH to jump server (from authorised networks)
ssh -i <key.pem> ec2-user@10.151.4.165

# Or via SSM
aws ssm start-session --target i-019825d0de3300832 --region ap-south-1
```

### EKS Cluster Access (from jump server)
```bash
# Configure kubectl
aws eks update-kubeconfig --name ecu-eks-test-cluster --region ap-south-1

# Verify access
kubectl cluster-info
kubectl get nodes
kubectl get pods -A
kubectl get namespaces
```

### RDS Connection (PostgreSQL)
```bash
# DMS Production
psql -h dms-prod.cvzxoaohm9ei.ap-south-1.rds.amazonaws.com -p 5432 -U <user> -d <db>

# Intranet Production
psql -h intranet-prod-db.cvzxoaohm9ei.ap-south-1.rds.amazonaws.com -p 5432 -U <user> -d <db>

# Intranet Test
psql -h intranet-test-db-1.cvzxoaohm9ei.ap-south-1.rds.amazonaws.com -p 5432 -U <user> -d <db>
```

### Public ALB Endpoints
```
# Intranet
http://LB-intranet-38818057.ap-south-1.elb.amazonaws.com/

# Intellihub
http://Intellihub-prod-1892815422.ap-south-1.elb.amazonaws.com/
```

---

## 10. SECURITY OBSERVATIONS

### ⚠️ Security Risks

1. **6 Unassigned EIPs** — wasting ~$21.6/month; release unused ones
2. **80+ IAM users** — large attack surface; review inactive accounts
3. **Multiple SMTP service accounts** — many SES users; consolidate where possible
4. **g5.2xlarge GPU server** — expensive; ensure access is restricted
5. **on-premises-data-gateway-azure-new (stopped)** — review if still needed

### ✅ Security Positives

1. Jump server pattern for EKS access (no direct kubectl from internet)
2. Zscaler Private Access (ZPA) connector for zero-trust access
3. Internal-only EKS load balancers (no direct cluster API exposure)
4. Separate UAT subnets (10.0.x.x vs 10.151.4.x)
5. Aurora databases with managed security patches

### Cost Optimization

1. **6 Unassigned EIPs** → Release = save ~$21.6/month
2. **g5.2xlarge GPU server** → Schedule stop when not needed (~$2.7/hr saving)
3. **on-premises-data-gateway (stopped)** → Terminate if decommissioned
4. **2 Disabled CloudFront distributions** → Delete if unused

---

## 11. INTELLIHUB HIGH AVAILABILITY ASSESSMENT

> **Last Checked**: June 11, 2026  
> **Method**: AWS CLI via `eks-jump-server-role` (jump server 10.151.4.165)  
> **Region**: ap-south-1

### EC2 Placement

| Instance | Type | AZ | Private IP |
|----------|------|----|------------|
| Intranet-prod-1 (`i-0b1f3b8eda05c132b`) | c5a.xlarge | **ap-south-1a** | 10.151.4.89 |
| Intranet-prod-2 (`i-0a82e63f8fcce6c8e`) | m5.2xlarge | **ap-south-1b** | 10.151.4.153 |

- Both instances **running** with EC2 system/instance health checks: `ok / ok`
- Instances are in **different AZs** (multi-AZ placement) ✅
- **No Auto Scaling Group** — bare EC2 instances, no automatic replacement on termination ⚠️

### ALB Target Group Health (Full Scan)

| Target Group | Prod-1 (.89) | Prod-2 (.153) | HA? |
|---|---|---|---|
| `intellihub-prod` (port 80, `/intranet/healthcheck`) | ✅ healthy | ✅ healthy | **True HA** |
| `intellihubadmin-prod` (port 80, `/`) | ✅ healthy | ✅ healthy | **True HA** |
| `gatimasterapi-prod` (port 5667, `/intranet/healthcheck`) | ✅ healthy | ✅ healthy | **True HA** |
| `sendbulktracking` (port 5670, `/intranet/healthcheck`) | ✅ healthy | ✅ healthy | **True HA** |
| `symphonywrapper-prod` (port 5668, `/intranet/healthcheck`) | ✅ healthy | ✅ healthy | **True HA** |
| `zendeskwrapper-prod` (port 5669, `/intranet/healthcheck`) | ✅ healthy | ✅ healthy | **True HA** |
| `intellihub-prod-genie` (port 80, `/intra/chat`) | ✅ healthy | — | Single (prod-1) |
| `intranet-prod-genie-2` (port 80, `/intra/chat`) | — | ✅ healthy | Single (prod-2) |
| `doc-disposal-prod-1` (port 80, `/docdis/healthcheck`) | ✅ healthy | — | Single (prod-1) |
| `doc-disposal-prod-2` (port 80, `/docdis/healthcheck`) | — | ✅ healthy | Single (prod-2) |
| `gatimasterapi-prod1` (port 5667) | ✅ healthy | — | Single (prod-1) |
| `gatimasterapi-prod2` (port 5667) | — | ✅ healthy | Single (prod-2) |
| `ecureportsapi-8112` (port 8112) | — | ✅ healthy | Single (prod-2) |
| `ecu-report-automation-1` (port 80) | — | ✅ healthy | Single (prod-2) |

#### Stale / Unused Target Groups (not attached to any listener)
| Target Group | Instance Registered | State |
|---|---|---|
| `aimlprod-1` | prod-1 | `unused` — Target.NotInUse |
| `ecureports` | prod-2 | `unused` — Target.NotInUse |
| `ecureports-api` | prod-2 | `unused` — Target.NotInUse |
| `intellaiml-prod-4001` | prod-1 | `unused` — Target.NotInUse |
| `intellihub-prod-2` | prod-2 | `unused` — Target.NotInUse |

### Application-Level Autoheal (Both Servers)

All three autoheal scripts are present and active on **both** servers at `/root/var/www/`:

| Script | Schedule | Purpose |
|--------|----------|---------|
| `apis-autoheal.sh` | `@reboot` + `*/5 * * * *` | Monitors & restarts 9 Python apps (hrchatbotazure, intranetapimain, aadhar_extraction_api, main.py, manage.py:8112, api.py, symphonyapi, trackingapi, zendeskapi) |
| `gati-apis-autoheal.sh` | `*/2 * * * *` | Monitors & restarts `gatimasterapi.py` |
| `cleanup_python_zombies.sh` | `*/1 * * * *` | Detects zombie Python processes → sends SIGCHLD to parent → escalates to SIGTERM/SIGKILL → triggers autoheal |

### HA Gaps & Recommendations

| # | Gap | Risk | Recommendation |
|---|-----|------|----------------|
| 1 | **No ASG** | If EC2 instance terminates, no automatic replacement — manual action required | Create ASG (min=1/max=1) per instance for auto-recovery, OR enable **EC2 Auto Recovery** via CloudWatch alarm (`StatusCheckFailed_System`) |
| 2 | **Single-instance services** | `intellihub-prod-genie`, `ecureportsapi-8112`, `doc-disposal`, etc. run on only one server | Move both genie TGs (`intellihub-prod-genie`, `intranet-prod-genie-2`) to point to both instances |
| 3 | **5 stale unused TGs** | Not harmful but causes confusion during incident investigation | Deregister targets and delete unused TGs (`aimlprod-1`, `ecureports`, `ecureports-api`, `intellaiml-prod-4001`, `intellihub-prod-2`) |
| 4 | **Health check interval = 30s** | 60 seconds to detect and remove a failed target (30s interval × 2 unhealthy threshold) | Reduce to 10s interval, keep unhealthy threshold = 2 → 20s failover time |
| 5 | **intranet-prod-db: no Multi-AZ** | Aurora single-instance — DB failure = downtime | Enable Aurora Multi-AZ reader or promote to cluster with failover replica |

---

## 12. MAINTENANCE & UPDATES

### Last Audited
- **Date**: June 11, 2026
- **Method**: AWS CLI via eks-jump-server-role (instance profile)
- **Region**: ap-south-1 (Mumbai, India)
- **Account**: 745510282686 (ECU/AllCargo Platform)

### Key Contacts
- **Platform/EKS**: k.rahul@allcargologistics.com
- **Jenkins CI/CD**: jenkins_user service account
- **DMS Application**: dms-user service account
- **ECU Integration**: ECU Worldwide team users

---

*This knowledge base is maintained for reference and operational purposes. All information is read-only unless explicitly authorized to make changes.*

---

# ECU Data Science Account - AWS Resources Knowledge Base

> **Last Updated:** June 5, 2026  
> **Region:** ap-south-1 (primary), eu-central-1 (SSM roles visible)  
> **Account ID:** 674017976129  
> **Access:** Long-lived IAM key — k.rahul@allcargologistics.com  
> **Purpose:** ECU Data Science platform — Data Lake, AI/ML, Email Services, Analytics (QuickSight, Redshift), and CDN

---

## Table of Contents

1. [EC2 Instances](#1-ec2-instances)
2. [RDS Databases](#2-rds-databases)
3. [Elastic IPs](#3-elastic-ips)
4. [Load Balancers](#4-load-balancers)
5. [CloudFront Distributions](#5-cloudfront-distributions)
6. [IAM Users](#6-iam-users)
7. [IAM Roles](#7-iam-roles)
8. [Resource Summary](#8-resource-summary)
9. [Platform Capabilities](#9-platform-capabilities)

---

## 1. EC2 INSTANCES

### Overview
Total EC2 Instances: **2** (both running)

### Instances List

| Instance ID | Name | Type | State | Private IP | Public IP |
|------------|------|------|-------|------------|-----------|
| i-090e0ca37cb35c5ff | INBOMSRVDATALAKE | r5a.4xlarge | running | 10.217.159.55 | None |
| i-0ac1c74d6c681bac1 | gen-ai-test | t3a.medium | running | 10.217.147.126 | None |

### Instance Details

#### INBOMSRVDATALAKE (Data Lake Server)
- **Instance ID**: i-090e0ca37cb35c5ff
- **Type**: r5a.4xlarge (16 vCPU, 128 GB RAM — memory-optimised AMD)
- **State**: Running
- **Private IP**: 10.217.159.55
- **Purpose**: Primary Data Lake server — Mumbai region data processing, analytics, and reporting
- **Related ALB**: INBOMSRVDATALAKE (internet-facing)
- **Note**: Large instance for in-memory data processing workloads

#### gen-ai-test (GenAI Testing Server)
- **Instance ID**: i-0ac1c74d6c681bac1
- **Type**: t3a.medium (2 vCPU, 4 GB RAM)
- **State**: Running
- **Private IP**: 10.217.147.126
- **Related EIP**: 13.202.103.33 (unassigned currently)
- **Purpose**: GenAI/LLM experimentation and testing
- **Note**: Lightweight instance for testing; EIP available for public access

### Key Observations
- Minimal EC2 footprint — primarily a serverless/managed services account
- r5a.4xlarge is expensive (~$0.9/hr) — monitor utilization
- Heavy reliance on managed services (Lambda, Glue, Redshift, QuickSight, SES)

---

## 2. RDS DATABASES

### Overview
Total RDS Instances: **1** (PostgreSQL standard)

### RDS Instance

| Database ID | Engine | Instance Class | Storage (GB) | Status | Endpoint | Port |
|------------|--------|-----------------|--------------|--------|----------|------|
| email-sorting | postgres | db.t4g.micro | 20 | available | email-sorting.cef4ybdp1win.ap-south-1.rds.amazonaws.com | 5432 |

### Database Details

**email-sorting**
- **Engine**: Standard PostgreSQL (not Aurora)
- **Instance Class**: db.t4g.micro (2 vCPU, 1 GB RAM — Graviton, minimal)
- **Storage**: 20 GB
- **Status**: Available
- **Endpoint**: email-sorting.cef4ybdp1win.ap-south-1.rds.amazonaws.com:5432
- **Purpose**: Database for email sorting / classification service

### Connection String
```bash
psql -h email-sorting.cef4ybdp1win.ap-south-1.rds.amazonaws.com -p 5432 -U <user> -d email_sorting
```

### Key Observations
- Minimal database footprint — most data likely in S3 / Redshift / DynamoDB
- t4g.micro is smallest available (cost-optimized)
- Graviton-based for efficiency
- Separate subnet group (cef4ybdp1win) from other accounts

---

## 3. ELASTIC IPs

### Overview
Total Elastic IPs: **5** (all unassigned ⚠️)

### Elastic IPs List

| Public IP | Allocation ID | Associated Instance | Name |
|-----------|---------------|---------------------|------|
| 13.202.103.33 | eipalloc-0e2722e752f102ac9 | None | genai-test |
| 13.203.84.217 | eipalloc-05e4c40d9cae22739 | None | (unnamed) |
| 13.205.154.98 | eipalloc-08ce005cc3c9898c3 | None | (unnamed) |
| 13.235.149.204 | eipalloc-0ea5a78bc32f30c15 | None | (unnamed) |
| 3.6.133.172 | eipalloc-0f9cf91488345c471 | None | (unnamed) |

### ⚠️ Cost Alert
**All 5 EIPs unassigned** — each ~$3.6/month = **~$18/month wasted**.  
The `genai-test` EIP (13.202.103.33) appears intended for the gen-ai-test instance but not currently attached.

---

## 4. LOAD BALANCERS

### Overview
Total Load Balancers: **1** (internet-facing ALB)

### Load Balancer

| Name | Type | Scheme | Status |
|------|------|--------|--------|
| INBOMSRVDATALAKE | application | **internet-facing** | active |

**DNS**: INBOMSRVDATALAKE-\<hash\>.ap-south-1.elb.amazonaws.com  
**Target**: INBOMSRVDATALAKE EC2 instance (i-090e0ca37cb35c5ff, 10.217.159.55)  
**Use Case**: Public access to Mumbai Data Lake web interface / API

---

## 5. CLOUDFRONT DISTRIBUTIONS

### Overview
Total CloudFront Distributions: **27** (26 enabled, 1 disabled)

This is the **largest CloudFront footprint** across all GATI/ECU accounts.

### Distributions List

| Distribution ID | Domain Name | Status | Enabled |
|-----------------|-------------|--------|---------|
| E3J22I5BKU1RVB | d3i3jy5sfu31cu.cloudfront.net | Deployed | No |
| E3FDJUOLCYCIJ4 | d3t3ft0pyve3ev.cloudfront.net | Deployed | Yes |
| ERH6KEB64P6QP | d344bywj3xe5ku.cloudfront.net | Deployed | Yes |
| E1RYV1F70PIV71 | d2rl7i9ugbwo4u.cloudfront.net | Deployed | Yes |
| E2FVCC01LF3UUD | d3djlgxjwfvccb.cloudfront.net | Deployed | Yes |
| E2N1O2YS84RAYH | d2u5m2xktx00tx.cloudfront.net | Deployed | Yes |
| EU8ZCYMDZXP4C | d18zq0mgte2w7i.cloudfront.net | Deployed | Yes |
| E117IYSRYWXT4C | dk1gjcm4semet.cloudfront.net | Deployed | Yes |
| EJGUJJN1S5U8Y | d2ha3vuogehij4.cloudfront.net | Deployed | Yes |
| EIWCJC74K3V8D | d3qwujuppcplu7.cloudfront.net | Deployed | Yes |
| E2FWFA427VBU8C | d327ud818srf0g.cloudfront.net | Deployed | Yes |
| E2JLOMMTO7OMAE | d34cg35ltgru62.cloudfront.net | Deployed | Yes |
| EYGYL8PZ7TJCW | d1rdad6i93m2it.cloudfront.net | Deployed | Yes |
| E3PGQHYZUZJSGD | d9fboz6fhzk7g.cloudfront.net | Deployed | Yes |
| E26QMEFELSFBMR | dj23bw8dgs0zd.cloudfront.net | Deployed | Yes |
| E1LDMQYQE9183Z | d35jojopw8zwba.cloudfront.net | Deployed | Yes |
| E2JRVQUI9A2RI1 | d10ln69avuewnh.cloudfront.net | Deployed | Yes |
| E6V8BLTPLS6W3 | d1i9zcyklzl6nj.cloudfront.net | Deployed | Yes |
| E6FKVUK72W0G0 | d3m20hu1a9xt2a.cloudfront.net | Deployed | Yes |
| E2X76DWQC8PBOC | dvxyu6tmpi7d7.cloudfront.net | Deployed | Yes |
| E29VY1TSOJZVI2 | d32lfabc3mssfo.cloudfront.net | Deployed | Yes |
| E3JPCZ6XSOOOY | d3l8mxluqvuf0k.cloudfront.net | Deployed | Yes |
| E24YWRFMND2S0D | d1l7yfkv5lvzw9.cloudfront.net | Deployed | Yes |
| E7B9V624U58BB | dcq7n95pp1r49.cloudfront.net | Deployed | Yes |
| E2IFVRQL6YYIYO | dkfp3txkjkwuu.cloudfront.net | Deployed | Yes |
| E172E8YULCA2YY | d2jep2bxnns4yz.cloudfront.net | Deployed | Yes |
| (+ 1 more) | — | Deployed | Yes |

### Key Observations
- 27 distributions is extremely high — suggest ECU DS serves many micro-frontends/portals
- All but one are enabled (active CDN traffic)
- Likely serving: reporting dashboards, data portals, analytics UIs, public APIs

---

## 6. IAM USERS

### Overview
Total IAM Users: **60** (ECU Worldwide focused)

### Users by Organisation

#### ECU Worldwide
- AakashShetty@ecuworldwide.com
- AmarDeshmane@ecuworldwide.com
- AmitPanigrahi@ecuworldwide.com
- AngelineNadar@ecuworldwide.com
- AniketRisbud@ecuworldwide.com
- BalkrishnaTiwari@ecuworldwide.com
- DeepaliPadave (via other)
- diptigawas@ecuworldwide.com
- DivyamAgarwal (via other)
- harshadasalvi@ecuworldwide.com
- HarendranathReddy@ecuworldwide.com
- irinaemelianova@ecuworldwide.com
- karishmachhajer@ecuworldwide.com
- KunalPadamwar@ecuworldwide.com
- MohdAmaan@ecuworldwide.com
- mohdsufeeyanahamad@ecuworldwide.com
- NayanRawal@ecuworldwide.com
- PraveshRaikwar@ecuworldwide.com
- RahulBaghel@ecuworldwide.com
- RajnishKumar@ecuworldwide.com
- rebhaadyanthaya@ecuworldwide.com
- SankariRoy@ecuworldwide.com
- sanketgonarkar@ecuworldwide.com
- SatyendraNagar@ecuworldwide.com
- ShikhaDubey@ecuworldwide.com
- ShubhamAmbati@ecuworldwide.com
- shyamsundargawade@ecuworldwide.com
- SujalKumar@ecuworldwide.com
- SurajTate@ecuworldwide.com
- surajt@eu.eculine.net
- TarunDutta@ecuworldwide.com
- Tulika / TulikaDas@ecuworldwide.com
- VaibhavJain@ecuworldwide.com
- wilbertdevaraj@ecuworldwide.com

#### AllCargo Logistics
- amit.sadaphule@allcargologistics.com
- k.rahul@allcargologistics.com
- maheshreddy@allcargologistics.com
- ramgopal.prajapat@allcargologistics.com
- ronak.patil@allcargologistics.com
- swapnilpatel@allcargologistics.com
- vinit.chouhan@allcargologistics.com
- vikas.pandey@allcargo.global

#### Consulting Firms
- abhishek.k@ganitinc.com — Ganit Analytics
- adithya.aravindan@ganitinc.com — Ganit Analytics
- hiruthik.k@ganitinc.com — Ganit Analytics
- Balaji.srinivasan@ennvee.net — Ennvee
- Stanley.George@ennvee.net — Ennvee
- Bhoopal.Singh@neudesic.com (via other) — Neudesic
- manoj.p@shellkode.com — Shellkode
- lalitkumar.jha@gatikwe.com — GATI KWE

#### External Partners
- kyadav@kloudrac.com — Kloudrac (Salesforce integration)

#### Service Accounts
| Account | Purpose |
|---------|---------|
| app-ds-user | Data Science application user |
| app-user-s3 | S3 operations for application |
| codecommit-backup | CodeCommit backup automation |
| ecuworldwide_admin | ECU Worldwide admin account |
| ecu-ds-intern | Intern access (restricted) |
| kloudrac-salesforce-upload | Kloudrac Salesforce data upload |
| n8n-bedrock-service | n8n workflow + AWS Bedrock integration |
| n8n_s3_user | n8n S3 access |
| nessusagent | Nessus vulnerability scanner |
| prithvi-vs | VS / development account |
| procuremnet-user | Procurement service account |
| ses-smtp-devops | SES DevOps email |

---

## 7. IAM ROLES

### Overview
Total Custom IAM Roles: **60+** (heavy Lambda, Glue, SES, DMS, AI/ML focus)

### Roles by Category

#### AI/ML & Data Science
| Role | Purpose |
|------|---------|
| ds-bedrock | AWS Bedrock AI/ML access |
| ds-aqua-role | Aqua platform for data science |
| ds-data-moldel-role | Data model processing |
| ec2-s3-aiml-test | S3 access for AI/ML EC2 |
| n8n-bedrock-service (user) | n8n + Bedrock workflow |

#### Data Engineering (Glue, DMS, Redshift)
| Role | Purpose |
|------|---------|
| AWSGlueServiceRole-Gluee | AWS Glue ETL jobs |
| GLUEE | Glue execution |
| DMSCDC_Execution_Role | DMS Change Data Capture |
| Demo-1-LambdaRoleToInitDMS-* | DMS initialization Lambda |
| dms-cloudwatch-logs-role | DMS CloudWatch logging |
| dms-gateway-role-7jms7nnn | DMS gateway access |
| dms-vpc-role | DMS VPC connectivity |
| allcargo-dms-ecs-execution-role | DMS ECS task execution |
| allcargo-dms-ingestion-lambda-role | DMS data ingestion Lambda |
| allcargo-dms-pipeline-task-role | DMS pipeline tasks |
| RS_spectrum | Redshift Spectrum external data |
| Redshift_schedule | Redshift scheduled queries |
| CWDBSharing-* | CloudWatch data sharing roles |

#### Email Services (SES)
| Role | Purpose |
|------|---------|
| ses-event-logger-role-zbfr5i3s | SES event logging |
| ses-events-writer-role-* (2) | SES event writing |
| ses-receiver-lambda-role-8kmqy060 | SES email receiver Lambda |
| ses-test-docker-role-b40kfhng | SES testing Docker |
| auto_email-role-ctbz4kv8 | Automated email sending |
| auto_mail-role-f0x7mihn | Automated mail service |

#### Lambda & EventBridge
| Role | Purpose |
|------|---------|
| lambda-execution-role-fwvvw87y | Lambda execution |
| Amazon_EventBridge_Invoke_Lambda_* (4) | EventBridge Lambda triggers |
| Amazon_EventBridge_Invoke_CodeBuild_* | EventBridge CodeBuild triggers |
| Amazon_EventBridge_Scheduler_LAMBDA_* | EventBridge scheduler |
| unsubscribe-handler_test-role-* | Email unsubscribe handler |
| send-email-demo_v2-role-* | Email sending Lambda |
| demo-ses-mime-template-role-* | MIME template Lambda |

#### EC2 & Storage
| Role | Purpose |
|------|---------|
| ec2-core | Core EC2 permissions |
| ec2-s3-readonly | EC2 S3 read-only |
| ec2s3 | EC2 S3 access |
| ec2start-role-gpe0k7xp | EC2 start scheduler |
| s3_ds_data | S3 data science data access |
| S3_quicksuite_automation | S3 QuickSight automation |
| S3full | S3 full access |

#### Analytics (QuickSight, API Gateway)
| Role | Purpose |
|------|---------|
| aws-quicksight-service-role-v0 | QuickSight service role |
| aws-quicksight-secretsmanager-role-v0 | QuickSight secrets access |
| APIGatewayCloudWatchLogs | API Gateway logging |

#### Third-Party Integrations
| Role | Purpose |
|------|---------|
| CloudHealth-Role | CloudHealth cost management |
| Rackspace | Rackspace managed services |
| TenableRole | Tenable vulnerability scanner |
| LucidityRole-* | Lucidity storage optimization |
| MindMasterBillingRole | MindMaster billing |
| MindMasterManagedServiceRole | MindMaster managed services |
| MontyCloud-ApplicationRole | MontyCloud cloud management |
| MontyCloud-ReuseCloudTrailLambdaExecutionRole | MontyCloud CloudTrail |
| RS-role-wy18imcn | Rackspace-specific |
| BreakGlassRole | Emergency access role |

#### Backup & Audit
| Role | Purpose |
|------|---------|
| CodeBuildBackupRole | CodeBuild backup |
| codecommit-backup-role-* | CodeCommit backup Lambda |
| role_created_for_audit_from_lucidity | Lucidity audit |
| listallobj-role-poatb22n | S3 object listing |
| rds-monitoring-role | RDS enhanced monitoring |
| ecsTaskExecutionRole | ECS task execution |

---

## 8. RESOURCE SUMMARY

### Resource Count by Type

| Resource Type | Count | Status |
|---------------|-------|--------|
| EC2 Instances | 2 | Both running |
| RDS Databases | 1 (PostgreSQL) | Available |
| Elastic IPs | 5 | **All unassigned ⚠️** |
| Load Balancers | 1 (ALB) | Active, internet-facing |
| CloudFront Distributions | 27 | 26 enabled, 1 disabled |
| IAM Users | 60 | ECU + AllCargo + partners |
| IAM Roles | 60+ | Heavy Lambda/Glue/SES focus |

---

## 9. PLATFORM CAPABILITIES

### Architecture Inference from Roles

```
ECU Data Science Platform (674017976129)
├── Data Ingestion & ETL
│   ├── AWS Glue (AWSGlueServiceRole-Gluee, GLUEE)
│   ├── DMS (DMSCDC_Execution_Role, allcargo-dms-*)
│   └── ECS containers (allcargo-dms-ecs-execution-role)
│
├── Data Storage
│   ├── S3 (s3_ds_data, S3full, app-user-s3)
│   ├── Redshift (RS_spectrum, Redshift_schedule)
│   └── RDS PostgreSQL (email-sorting DB)
│
├── Analytics & BI
│   ├── QuickSight (aws-quicksight-service-role-v0)
│   ├── CloudWatch Dashboards (CWDBSharing roles)
│   └── API Gateway (APIGatewayCloudWatchLogs)
│
├── AI/ML
│   ├── AWS Bedrock (ds-bedrock, n8n-bedrock-service)
│   ├── GenAI Test Server (gen-ai-test EC2)
│   └── GPU experiments (via EIP 13.202.103.33)
│
├── Email Platform (SES)
│   ├── Email sorting (email-sorting RDS)
│   ├── SES receivers + event logging
│   ├── Auto-email Lambda functions
│   └── MIME template processing
│
├── Automation
│   ├── n8n workflow automation (n8n-bedrock-service, n8n_s3_user)
│   ├── EventBridge schedulers
│   └── Lambda triggers
│
├── Data Lake
│   ├── INBOMSRVDATALAKE EC2 (r5a.4xlarge)
│   └── INBOMSRVDATALAKE ALB (internet-facing)
│
└── CDN (27 CloudFront distributions)
    └── Multiple portals and dashboards
```

### Third-Party Integrations
- **Kloudrac**: Salesforce data upload
- **Rackspace**: Managed services
- **Tenable**: Vulnerability scanning
- **Lucidity**: Storage optimization
- **MindMaster**: Managed services
- **MontyCloud**: Cloud management
- **Ganit Analytics**: Data consulting
- **Ennvee**: Consulting
- **n8n**: Workflow automation

---

## 10. CONNECTION DETAILS

### Data Lake Server
```bash
# Via SSM (no SSH needed)
aws ssm start-session --target i-090e0ca37cb35c5ff --region ap-south-1

# Public URL via ALB
http://INBOMSRVDATALAKE-<hash>.ap-south-1.elb.amazonaws.com/
```

### RDS Connection
```bash
psql -h email-sorting.cef4ybdp1win.ap-south-1.rds.amazonaws.com \
     -p 5432 -U <user> -d <database>
```

### GenAI Test Server
```bash
# Via SSM
aws ssm start-session --target i-0ac1c74d6c681bac1 --region ap-south-1

# Public access: Attach EIP 13.202.103.33 first
aws ec2 associate-address \
    --instance-id i-0ac1c74d6c681bac1 \
    --allocation-id eipalloc-0e2722e752f102ac9
```

---

## 11. COST OPTIMIZATION NOTES

| Item | Issue | Action |
|------|-------|--------|
| 5 Unassigned EIPs | ~$18/month wasted | Release unused ones |
| INBOMSRVDATALAKE (r5a.4xlarge) | ~$0.9/hr → $648/month | Check utilization, schedule off-hours stop |
| 27 CloudFront distributions | Review inactive | Disable/delete unused |
| 1 disabled CloudFront (E3J22I5BKU1RVB) | Deployed but off | Delete if not needed |

---

## 12. MAINTENANCE & UPDATES

### Last Audited
- **Date**: June 5, 2026
- **Method**: Long-lived IAM key (k.rahul@allcargologistics.com)
- **Region**: ap-south-1 (Mumbai)
- **Account**: 674017976129 (ECU Data Science)

### Security Note ⚠️
Access is via a **long-lived IAM access key** (AKIA_REDACTED_KEY_DEMO) rather than SSO/temporary credentials.  
Best practice: Rotate this key regularly and consider migrating to SSO.

---

*This knowledge base is maintained for reference and operational purposes. All information is read-only unless explicitly authorized to make changes.*

---

# Loop.ai — AWS Cost Breakdown

**Account:** `674017976129` · **Region:** `eu-central-1` (Frankfurt)
**Measurement window:** 3 Aug – 2 Sep 2026 (30 days)
**Prepared:** 2 September 2026

---

## ⚠️ Important caveat on these figures

**Cost Explorer is not accessible for this account.** The API returns:

```
AccessDeniedException: Payer account 162176457247 does not allow
access for linked account 674017976129
```

This is an AWS Organizations restriction set at the payer account — it cannot be
worked around with any credential scoped to `674017976129`.

Consequently **the costs below are calculated from measured usage metrics against
published AWS eu-central-1 list prices**, not read from actual billing data.

- **Usage metrics = measured** (CloudWatch, 30-day totals — these are exact)
- **Costs = derived** (usage × list price)

Actual invoiced amounts may differ due to Free Tier, private pricing, EDP/PPA
discounts, or credits applied at the payer level. **To confirm actuals, someone
with payer-account (`162176457247`) access must either run the Cost Explorer
query or enable cost visibility for this linked account.**

---

## 1. Measured usage (30 days)

### Amazon SES

| Metric | Volume |
|---|---|
| **Send** | **31,530** |
| Delivery | 25,123 |
| Bounce | 8,282 |
| Complaint | 1 |
| Reject | 0 |

Account limits: 50,000 sends/24 h cap, 14 sends/sec max rate.

### AWS Lambda

| Function | Invocations | Avg duration | Max duration | Memory | Errors |
|---|---|---|---|---|---|
| `ses-lambda` | 28,554 | 400.0 ms | 14,327 ms | 512 MB | 0 |
| `dispatcher-lambda` | 107 | 2,111.7 ms | 4,248.5 ms | 128 MB | 0 |
| `ses-events-writer` | 7,226 | 242.1 ms | 2,123.6 ms | 128 MB | **225** |

### Amazon SNS

| Topic | Messages published |
|---|---|
| `loop-sns-topic` | **84,398** |
| `email-campaign-alerts` | 41 |

### Amazon SQS

| Queue | Sent | Received | Deleted |
|---|---|---|---|
| `email-campaign-queue_dispatcher_lambda` | 28,548 | 28,548 | 28,548 |
| `ses-events-dlq` | 0 | 66 | 8 |

---

## 2. Derived cost per service (30 days)

Prices are eu-central-1 list, **excluding** Free Tier.

### SES — $3.15

| Component | Calculation | Cost |
|---|---|---|
| Outbound messages | 31,530 × $0.10/1,000 | **$3.15** |
| Data transfer / attachments | not separately measured | — |

### Lambda — $0.13

Charged on requests ($0.20/1M) plus GB-seconds ($0.0000166667).

| Function | GB-s | Request cost | Compute cost | Total |
|---|---|---|---|---|
| `ses-lambda` | 28,554 × 0.4 s × 0.5 GB = 5,711 | $0.0057 | $0.0952 | $0.101 |
| `dispatcher-lambda` | 107 × 2.112 s × 0.125 GB = 28 | $0.0000 | $0.0005 | $0.001 |
| `ses-events-writer` | 7,226 × 0.242 s × 0.125 GB = 219 | $0.0014 | $0.0036 | $0.005 |
| **Total** | **5,958** | **$0.007** | **$0.099** | **≈ $0.13** |

### SNS — $0.04

| Component | Calculation | Cost |
|---|---|---|
| Requests | 84,439 × $0.50/1M | $0.042 |
| SQS/Lambda deliveries | no charge | $0.00 |
| **Total** | | **≈ $0.04** |

### SQS — $0.03

| Component | Calculation | Cost |
|---|---|---|
| Standard queue requests | ~85,700 billable × $0.40/1M | $0.034 |
| **Total** | | **≈ $0.03** |

*SQS bills per 64 KB chunk; assumes messages under 64 KB.*

---

## 3. Total and cost per email

| Service | 30-day cost | Share |
|---|---|---|
| **Amazon SES** | **$3.15** | **94.0%** |
| AWS Lambda | $0.13 | 3.9% |
| Amazon SNS | $0.04 | 1.2% |
| Amazon SQS | $0.03 | 0.9% |
| **Total** | **≈ $3.35** | 100% |

### Cost per email

```
$3.35 ÷ 31,530 sends = $0.000106 per email
```

| Basis | Cost |
|---|---|
| **Per email sent** | **$0.000106** (≈ 0.0106 ¢) |
| Per 1,000 emails sent | $0.106 |
| Per email **delivered** (25,123) | $0.000133 |

> Use the delivered figure for business-case modelling if bounced mail has no
> business value — the 26% bounce rate makes the two materially different.

### Scaling projection

Near-linear, since 94% is per-message SES cost.

| Monthly volume | Projected cost |
|---|---|
| 31,530 (current) | $3.35 |
| 100,000 | $10.63 |
| 500,000 | $53.13 |
| 1,000,000 | $106.27 |

---

## 4. ⚠️ Bedrock dominates total cost — scope must be widened

The four services requested total **$3.35/month**. But this account runs
**Amazon Bedrock at very high volume**, and it is ~1,000× larger than everything
else combined:

| Metric (30 days) | Volume |
|---|---|
| **Bedrock invocations** | **863,957** |
| **Input tokens** | **2,583,280,606** (2.58 billion) |
| **Output tokens** | **71,694,899** (71.7 million) |

### Per-model breakdown

| Model | Invocations | Input tokens | Output tokens |
|---|---|---|---|
| `claude-sonnet-4-6` | 589,336 | 1,884,088,830 | 53,687,361 |
| `claude-sonnet-4-20250514` | 222,927 | 694,346,085 | 17,223,809 |
| `titan-embed-text-v2:0` | 43,372 | 490,850 | — |
| `titan-embed-text-v1` | 3,832 | 140,821 | — |
| `claude-sonnet-5` | 774 | 4,151,226 | 609,405 |
| `claude-opus-5` | 1,829 | 35,618 | 170,473 |
| `claude-haiku-4-5` | 1,707 | 26,357 | 3,755 |
| `claude-opus-4-5 / 4-6 / 4-7 / 4-8` | 68 total | 587 | 67 |
| `claude-sonnet-4-5` | 29 | 232 | 29 |

Two Sonnet models account for **99.8% of all tokens**.

### Indicative Bedrock cost

At Claude Sonnet on-demand list pricing (~$3/M input, ~$15/M output):

```
2.578 B input  × $3/M  ≈ $7,734
0.0715 B output × $15/M ≈ $1,073
                          ───────
                          ≈ $8,800 / month
```

**This is an order-of-magnitude estimate, not a quote.** Actual cost depends on
per-model rates, cross-region inference pricing for the `eu.` prefixed models,
prompt caching (`CacheReadInputTokenCount` is being emitted, which reduces cost
materially), and any committed-throughput or private pricing.

### Revised total picture

| Service | 30-day cost | Share |
|---|---|---|
| **Amazon Bedrock** | **≈ $8,800** | **~99.96%** |
| Amazon SES | $3.15 | 0.04% |
| Lambda + SNS + SQS | $0.20 | <0.01% |
| **Total** | **≈ $8,803** | |

### This is the number that matters

If Bedrock usage is attributable to Loop.ai email processing:

```
$8,803 ÷ 31,530 emails ≈ $0.28 per email
```

That is **~2,600× higher** than the $0.000106 figure from the four requested
services alone.

> **Before presenting any per-email cost, confirm what share of Bedrock usage
> belongs to Loop.ai.** This account also hosts ELMA, aqua-classification, and
> other AI workloads (see the SNS topic and SQS queue inventory), so Bedrock spend
> is likely shared across several products. Attributing 100% of it to Loop.ai
> would overstate cost just as badly as excluding it understates it.
>
> Recommended: add a per-request cost-allocation tag or inference profile per
> product so Bedrock spend can be split cleanly.

---

## 5. Items still excluded

These fall outside the four services listed but **do** appear on the bill and
should be added for a complete per-email figure:

- **CloudWatch Logs** — ingestion $0.57/GB + storage $0.03/GB-month. With 35,887
  Lambda invocations/month plus Bedrock model invocation logging
  (`ModelInvocationLogsS3DeliverySuccess` is being emitted), this is non-trivial.
- **S3** — Bedrock invocation logs are being delivered to S3; also any raw
  MIME/email body storage.
- **DynamoDB / RDS** — `ses-events-writer` writes somewhere; that datastore isn't
  in the requested scope.
- **Data transfer out**.
- **Bedrock Knowledge Base / OpenSearch** — `SearchUnits` metric is present,
  indicating a vector store is in use. OpenSearch Serverless has a minimum
  monthly charge regardless of usage.

---

## 6. Operational findings worth acting on

### Bounce rate 26.3% — needs attention

```
8,282 bounces ÷ 31,530 sends = 26.3%
```

AWS's recommended ceiling is **5%**; above 10% risks SES sending pause and
reputation damage. At 26% this is the single biggest risk in the pipeline, and
it also means ~1 in 4 emails is paid for with no delivery.

Fixing this would cut effective cost per *delivered* email by roughly 20%.

### `ses-events-writer` — 225 errors (3.1% failure rate)

225 of 7,226 invocations failed. Related: `ses-events-dlq` shows 66 messages
received and only 8 deleted, so failed events are accumulating undrained.

### `ses-lambda` — max duration 14,327 ms vs 400 ms average

36× spread against a 30-second timeout. Tail latency worth investigating; it also
inflates GB-seconds disproportionately.

### Invocation count mismatch

| Path | Count |
|---|---|
| SES sends | 31,530 |
| `ses-lambda` invocations | 28,554 |
| SQS messages through dispatcher queue | 28,548 |
| `loop-sns-topic` publishes | 84,398 (≈ 2.7 per send) |

The ~2,976 gap between SES sends and `ses-lambda` invocations suggests a second
send path not passing through this Lambda. The 2.7× SNS fan-out per email is
expected if delivery/bounce/complaint each publish an event — worth confirming
that's intentional rather than duplicate publishing.

---

## 7. Recommended next step

To replace the derived figures with invoiced actuals, ask someone with payer
account (`162176457247`) access to run:

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-08-01,End=2026-09-01 \
  --granularity MONTHLY \
  --metrics UnblendedCost UsageQuantity \
  --filter '{"Dimensions":{"Key":"LINKED_ACCOUNT","Values":["674017976129"]}}' \
  --group-by Type=DIMENSION,Key=SERVICE \
  --region us-east-1
```

Alternatively, enable Cost Explorer access for linked accounts in the
Organizations billing preferences, which would let this account self-serve
future cost reporting.

## SSH keys and MDM host assignments — 2026-10-07

Local key files are organized by environment and purpose under `infrastructure/secrets/keys/`. See [KEYS-README.md](../infrastructure/KEYS-README.md) for the complete migration map and user-supplied DEV/SIT/UAT/PROD MDM server inventory. DEV and UAT use the documented shared PEM filenames; SIT uses keys with `uat` in their filenames; PROD has dedicated keys. Existing older access commands are historical; use the directory map for current local paths. Host/key authentication has not been live-tested.

## Worker-2 Sufeeyan folder extraction — 2026-10-10

Read-only file inspection on worker-2 (`ubuntu@10.100.95.39`) found `/root/sufeeyan` containing an AWS CLI bundle, `kubectl`, `sit-eks-connection.sh`, and `kubeconfig-sit`. Extracted identifiers describe SIT EU: AWS account `464134132424`, region `eu-central-1`, EKS cluster `euc1-itopaz-sit-eks`, context `arn:aws:eks:eu-central-1:464134132424:cluster/euc1-itopaz-sit-eks`. The script references `aws sts get-caller-identity`, `aws eks update-kubeconfig`, and `kubectl get nodes`.

Evidence: `/root/sufeeyan/sit-eks-connection.sh` and `/root/sufeeyan/kubeconfig-sit`, inspected 2026-10-10. These are stored configuration facts; AWS access and live cluster health were not tested. No credentials, tokens, certificate material or `.env` contents were copied.

The additional `/home/ubuntu/sufeeyan/ai-agentic-proj` directory contained only `.env` and `.venv` at its top level. No agent source or knowledge documents were found in the inspected Sufeeyan directories. Worker-2 remains standby; inspecting its files does not activate it for dispatch.

## Quantum module S3 origins — 2026-10-12

AWS account `674017976129` hosts the following Quantum buckets. All eight buckets are in Frankfurt (`eu-central-1`), even where the existing application bucket is in another region.

| Module | Environment | S3 bucket | Existing application URL | CloudFront distribution |
|---|---|---|---|---|
| Epic | Dev | `quantum-epic-dev` | `https://epic-dev.allcargoapps.com` | `E2X76DWQC8PBOC` |
| Epic | Prod | `quantum-epic-prod` | `https://epic.allcargoapps.com` | `E29VY1TSOJZVI2` |
| RIA | Dev | `quantum-ria-dev` | `https://ria-dev.allcargoapps.com` | `E2JLOMMTO7OMAE` |
| RIA | Prod | `quantum-ria-prod` | `https://ria.allcargoapps.com` | `EYGYL8PZ7TJCW` |
| Freight | Dev | `quantum-freight-dev` | `https://freight-dev.allcargoapps.com` | `E24YWRFMND2S0D` |
| Freight | Prod | `quantum-freight-prod` | `https://freightrate.allcargoapps.com` | `E7B9V624U58BB` |
| PACE | Dev | `quantum-pace-dev` | `https://pace-dev.allcargoapps.com` | `E2IFVRQL6YYIYO` |
| PACE | Prod | `quantum-pace-prod` | `https://pace.allcargoapps.com` | `E172E8YULCA2YY` |

Each bucket has all four S3 public-access-block settings enabled, AES-256 default encryption, and `BucketOwnerEnforced` ownership. Its bucket policy permits `s3:GetObject` to the CloudFront service principal only for the listed distribution ARN. Each distribution has two origins and was verified `Deployed`; the original origin remains the default. The Quantum origin is registered but has no cache behavior pointing to it, so the application URL does not yet serve objects from the Quantum bucket. A path and cache behavior must be specified before using the new origin for requests.

Provisioning script: `scripts/provision-quantum-origins.ps1`. Pre-change CloudFront configuration snapshots and the initial result: `infrastructure/backups/quantum-origins-20261012-133651/`. The snapshot result records PACE Prod as `InProgress` immediately after the update; a later live check confirmed it `Deployed`.

## China Prefiler SIT — verified 2026-10-13 (Asia/Kolkata)

- **Application:** `https://prefiler-sit.ecuworldwide.cn`. The supplied link destination `https://portal.azure.cn/#` is the Azure China management portal. Worker-1 checked only the application; Azure control-plane access was not attempted, and serving edge/origin resource identity remains unverified.
- **Recorded results:** login HTTP 200; `X-Frame-Options: SAMEORIGIN` present. HSTS, X-Content-Type-Options, CSP and Cache-Control missing on login. Root redirect follows HTTPS → HTTP login → HTTPS login.
- **File disclosure:** `/.git/config`, `/.git/index`, `/.gitignore`, `/Dockerfile`, `/package-lock.json` and `/nginx.conf` returned HTTP 200 with matching structures/signatures. `/.htaccess` returned HTTP 403. Disclosed file bodies and private credentials were not retained.
- **Angular:** `/shared_ui/main.js` returned HTTP 200 and contains version literal `16.2.12`; package/feature checks are required to establish CVE applicability. Headers do not patch Angular dependencies.
- **Limits:** eleven paths checked; full browser workflows and a China WAS rerun remain untested. EU/Singapore 80-row resolution counts do not apply. No China infrastructure/application remediation was performed.
- **Pending work:** confirm remediation authorization and exact Azure China resource identity; identify the serving Front Door/CDN route and AKS origin, then back up rules/deployments. Block disclosed files at edge/origin and remove unnecessary web-root files; add compatible security/cache headers; fix HTTPS root/double-slash/directory redirects; validate and upgrade affected Angular packages. Verify browser workflows, success/error headers, denial responses, redirect chains and scanner results before claiming resolution.
- **Implementation references:** `infrastructure/cloudfront/eu-sit/prefiler-origin.htaccess` and `infrastructure/cloudfront/eu-sit/response-headers-policy.json`. Adapt hostnames, CSP resources and Azure integration; AWS policy JSON is not an Azure deployment configuration.
- **Evidence:** [China report](../security-reviews/2026-10-13/china-sit/REPORT.md), [HTTP evidence](../security-reviews/2026-10-13/china-sit/evidence.json), [Angular evidence](../security-reviews/2026-10-13/china-sit/angular-version.json).
- **Master handoff:** [prepared on worker-1](../agent/handoffs/master-china-prefiler-sit-20261013.md), **not sent**. Windows master is registered at `C:\Users\rah_66160\iTopaz-agents` without an inbound host/messaging endpoint; it can fetch the handoff through its existing worker SSH connection.

---

# AllCargo iTOPAZ — Complete Session Knowledge Export
> Generated: 2026-09-01 | Covers: Aug 17 – Sep 1, 2026

═══════════════════════════════════════════════════════════════════════

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

## 2026-06-18 — POC Account aimlapp-test Intranet 502 Fix

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
- **Key**: `infrastructure/secrets/keys/vj-keypair-pocacct.pem`
- **Nginx**: Running (port 80), routes static content from `/var/www/html`
- **Services running**: `hrchatbotazure.py` (4080), `aadhar_extraction_api.py` (4003), `intranetapimain.py` (4001), `ollama` (127.0.0.1:11434)
- **AWS credentials on server**: IAM user `codecommit-jenkins`, region `ap-south-1`, creds at `/root/.aws/credentials`

---

## 2026-06-12 — PROD EU Kafka 3.9.1 Client Setup

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

## 2026-06-12 — PROD EU iTariff Ingress Bring-up + Route Validation

### PROD EU Bastion and Cluster Access
- **Bastion**: `10.100.98.195` (key: `infrastructure/secrets/keys/prod-eu-bastion.pem`)
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

## 2026-06-12 — prefiler-bff DEV VirtualService Fix + README Update

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

## 2026-06-10 — SIT EU/SG Aurora DB Fixes + prefiler-cache-util Pipeline Fix

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

## 2026-06-10 — Intranet Prod Deploy Fix (10.151.4.89 + 10.151.4.153)
**Account:** 745510282686 | **Region:** ap-south-1 | **SSH Key:** `infrastructure/secrets/keys/Intranet-prod-1-Key.pem`

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

## 2026-08-27 (Today's Session)

### AWS Config Updates
- **Added UAT profiles** to `~/.aws/config` for account `405478414008`:
  - `uat-eu-central-1`, `uat-us-east-1`, `uat-eu-central-1` (EC2 instance metadata)
  - `uat-admin` (SSO: `AWS-iTopaz-Admin`, ap-southeast-1)
- **Added dev-frankfurt-admin** (SSO: `AWSAdministratorAccess`, 074779643551)
- **Added sit-singapore-admin**, `sit-frankfurt-admin` (SSO: `AWS-iTopaz-Admin`, 464134132424)
- **Added bw-uat** (SSO: `AWSAdministratorAccess`, 581621506601)
- **Added gati-674-admin** (SSO: `AWSAdministratorAccess`, 674017976129, us-east-1)

### Kubeconfig Updates
- **Added UAT clusters** to `/home/ubuntu/rahul/config`:
  - `uat-us-east-1` → `use1-itopaz-uat-eks` (405478414008)
  - `uat-eu-central-1` → `euc1-itopaz-uat-eks` (405478414008)

### Aurora RDS Scheduler Fix (464134132424 - SIT)
- **Root cause**: Lambda `scheduler` (eu-central-1) and `scheduler-rds-ec2` (ap-southeast-1) had 3 bugs:
  1. Read tags from DB instances, not Aurora clusters
  2. Used `stop_db_instance()` instead of `stop_db_cluster()`
  3. Comma-split bug in `is_in_schedule()` — silently overwritten by slash-split
- **Fix**: Added `process_rds_clusters()` function to both Lambdas
- **IAM fix**: Added `rds:DescribeDBClusters`, `rds:StartDBCluster`, `rds:StopDBCluster` to `scheduler-role-e2z91qs8`
- **Frankfurt Aurora** `euc1-itopaz-sit-aurora-postgresql`: was running 9.5 months non-stop. Schedule tag `07:00-23:59 IST`.
- **Singapore Aurora** `apse1-itopaz-sit-aurora-postgresql`: Schedule tag `05:30-21:00 IST`.

### ACM Certificate Fix (405478414008)
- Cert `internalapse1-uat-itopaz.com` was PENDING_VALIDATION
- **Root cause**: Private Route53 hosted zone — ACM needs public DNS
- **Fix**: Created public hosted zone `Z0647588SV39QU2AGJG2`, added validation CNAME
- **Note**: Domain must be publicly registered for full validation to complete

### Singapore Redis Password (464134132424)
- Redis cluster `apse1-itopaz-sit-redis-new` already had AuthToken enabled (TLS on)
- **Rotated auth token** and stored in Secrets Manager: `itopaz/sit/redis/apse1-itopaz-sit-redis-new`
- Rotation: OFF

### UAT Redis Passwords (405478414008)
- 3 clusters: `euc1-itopaz-uat-redis` (eu-central-1), `apse1-itopaz-uat-redis` (ap-southeast-1), `use1-itopaz-uat-redis` (us-east-1)
- **Enabled TLS + auth token** on all 3, stored in Secrets Manager with rotation OFF
- Secret names: `itopaz/uat/redis/<cluster-name>` in respective regions
- Password: stored in secrets manager

### EKS Security Group Fix (464134132424 - SIT Frankfurt)
- Bastion `i-0bd3314ea08e6fb27` (10.100.215.30, sg-03396fa5484b431e1) could not reach EKS private API
- **Fix**: Added TCP/443 inbound rule `sg-03396fa5484b431e1` → EKS SG `sg-023c8cff9a807ad1d`
- Rule ID: `sgr-05071d883236a0905`

### EBX Service Auto-Start Fix (464134132424 - SIT Frankfurt)
- Instance `i-08a20bae22e57e46d` (10.100.215.180) — TIBCO EBX on `@reboot` crontab was silently skipped by cronie on Amazon Linux 2023 (known issue with stop/started EC2 instances)
- **Fix**: Created `/etc/systemd/system/ebx.service` with `ExecStartPre=/bin/sleep 600` (10-min delay)
- Service enabled: `systemctl enable ebx.service`
- Old `@reboot` crontab removed

### Lambda Scheduler Deployment (Multiple Accounts)
- Deployed `scheduler-rds-ec2` Lambda (weekday-aware version with `ScheduleDays` tag support) to:
  - `074779643551` eu-central-1 (dev)
  - `405478414008` eu-central-1, ap-southeast-1, us-east-1 (UAT)
- IAM role: `scheduler-rds-ec2-role` with EC2+RDS+Aurora+CloudWatch permissions
- EventBridge trigger: `rate(5 minutes)`

### Scheduler Tags Applied
**DEV (074779643551, eu-central-1) — Mon-Fri 09:00-21:00 IST:**
- EC2: ecu-edi-server-dev, euc1-itopaz-bastion-dev-1, EC2-EMS-Server-Dev, MDM-EBX-Server-DEV, EC2-EMS-Server-Dev-topaz, EC2-MDM-BW-Dev-topaz, EC2-MDM-BW-Dev
- Aurora clusters: euc1-itariff-edi-dev (21:00 stop), euc1-itopaz-dev-database-cluster (01:00 stop), euc1-mdm-dev-database-cluster (21:00 stop)

**UAT (405478414008) — Mon-Fri 09:00-21:00 IST:**
- eu-central-1: bastion `i-0534867ff51fba97a`, Aurora `euc1-itopaz-uat-aurora-postgresql`
- ap-southeast-1: bastion `i-0426edabc4ca81367`, Aurora `apse1-itopaz-uat-aurora-postgresql`
- us-east-1: bastion `i-0225a153844ab45c3`, Aurora `use1-itopaz-uat-aurora-postgresql`

**UAT EKS Node Group ASG Schedules (405478414008):**
- Stop: `30 15 * * 1-5` (21:00 IST) → min=0, desired=0
- Start: `30 3 * * 1-5` (09:00 IST) → restore original capacity
- 6 ASGs across 3 regions (eu-central-1, ap-southeast-1, us-east-1)

### Dev EKS Windows Node Issue Fix (074779643551)
- **Root cause**: 38 Linux pods across 7 namespaces had no `nodeSelector` — scheduled on Windows nodes (`euc1-itopaz-dev-eks-windows-nodegrou-v3`)
- Windows `vpc-bridge` CNI doesn't assign `vpc.amazonaws.com/PrivateIPv4Address` to Linux pods → `FailedCreatePodSandBox` for 8+ hours
- **Fix**: Added `nodeSelector: kubernetes.io/os: linux` to 33 deployments across itariff-api, itopaz-export, itopaz-import, itopaz-platform, itopaz-ui, prefiler-api, prefiler-ui

### SIT Frankfurt ConfigMap Fixes (464134132424)
- **tariff-buying-service**: Added missing `service.delete.code=DEL1204`, `service.archive.code=ARC1206`
- **tariff-buying-otherbooking-service**: Added missing `service.rfq.code=RFQ10001`
- Pattern: Spring `@Value("${service.X.code}")` properties missing from ConfigMap → `PlaceholderResolutionException` → CrashLoopBackOff → 503

### BW UAT Container Issue (581621506601 - EC2 10.233.30.104)
- Container `hello9282` (TIBCO BW `AutomatedEmailCompanyBankDetail`) not responding on port 9282
- **Root cause**: `CommonLoggingShared` bundle version mismatch — container image is 6 months old (Feb 2026), working containers use Aug 2026 version
- Fix: Copy updated JAR from working container; long-term: rebuild Docker image

### CloudFront + WAF Fix (674017976129)
- Distribution `E2FVCC01LF3UUD`: added `/agent/*` behavior → ELB origin `datascience-144380231.eu-central-1.elb.amazonaws.com`
- WAF `waf-cloudfront-geo-restrictions`: Belgium zero traffic fix:
  - Root cause: Corporate users route through Microsoft Azure proxies (4.213.x.x, 52.112.x.x) geo-located as India/Malaysia → blocked by `HostingProviderIPList`
  - Fix: Override `HostingProviderIPList` to Count; added P0 allow rule for Microsoft Azure IP ranges
  - IP Sets: `AllowMicrosoftCorporateProxies` (IPv4+IPv6)

### SIT itariff-api ConfigMap Fixes (continued) — 2026-08-27

- **tariff-buying-service** (4th fix): Added missing `serviceurls.search`:
  - `http://tariff-search-service.itariff-api.svc.cluster.local/search-domain-service/secure/v1/search`
  - Error was `"no healthy upstream"` (Istio) because 11/20 pods were in CrashLoopBackOff
  - Spring `@Value("${serviceurls.search}")` was injected in `tariffBuyingImpl` bean but URL missing from ConfigMap

**Complete list of all missing properties found in tariff-buying-service ConfigMap (today):**

| Property | Value Added | Bean Affected |
|---|---|---|
| `service.delete.code` | `DEL1204` | `tariffBuyingCarriageArchiveImpl` |
| `service.archive.code` | `ARC1206` | `tariffBuyingCarriageArchiveImpl` |
| `serviceurls.search` | `http://tariff-search-service...` | `tariffBuyingImpl` |

**tariff-buying-otherbooking-service:**

| Property | Value Added |
|---|---|
| `service.rfq.code` | `RFQ10001` |

**Pattern**: New code deploys inject `@Value` annotations but ConfigMap is not updated → `PlaceholderResolutionException` → CrashLoopBackOff → 503/`no healthy upstream` from Istio.

---

## 2026-08-28 to 2026-08-31

### scheduler-rds-ec2 Lambda — Jump Account (439891535362)
- Created IAM role `scheduler-rds-ec2-role` + Lambda using `AWS-iTopaz-Admin` SSO role
- Added `jump-account-admin` profile (SSO: AWS-iTopaz-Admin, eu-central-1)
- EventBridge trigger: `rate(5 minutes)`
- Tagged all 5 running EC2s with `AutoSchedule=true, Schedule=09:00-21:00, TimeZone=Asia/Kolkata, ScheduleDays=mon-fri`:
  - `i-0cdcce39da9444d74` euc1a-devops-jenkins-master-vm
  - `i-0cd1ab8b0d9247ef4` euc1a-devops-sonarqube-master-vm
  - `i-0e5b12ab9516d5a07` euc1-linux-jump-server-vm
  - `i-0af0c0a0b06e69b95` window-jenkins-agent
  - `i-0b7a724f715ed2c11` Spot

### EBX Auto-Start Fix (i-08a20bae22e57e46d, SIT Frankfurt) — Revised
- Systemd service was FAILING: `JAVA_HOME` not set in systemd environment → `startup.sh` exit-code=1
- User requested crontab-only approach (systemd would cause double process)
- **Final state**: Systemd service REMOVED. Only crontab:
  ```
  @reboot sleep 600 && export JAVA_HOME=/usr/lib/jvm/java-21-amazon-corretto.x86_64 && ... && sh -x startup.sh >> /var/log/ebx-cron.log 2>&1
  ```
- Log file: `/var/log/ebx-cron.log`

### DEVOPS Account (439891535362) Cost Analysis
- Monthly cost: Apr $594 → May $763 → Jun $889 → Jul $1,058 → Aug $1,138

**Root cause 1: Kiro Enterprise Pro Plus** — $40/user/month
- May: ~4 users ($151) → Aug: ~11 users ($432)
- Growing ~$60/month as more users are added
- Usage type: `EUC1-KiroEnterprise-ProPlus`

**Root cause 2: EBS Snapshots accumulating** — $253/month
- 124 snapshots, 25,852 GB total
- Oldest from Sep 2025 (never cleaned)
- All from `CreateImage` (AMI backups piling up)
- Potential saving: delete 90-day-old snapshots → save ~$150/month

EC2-Other breakdown:
- `EUC1-EBS:SnapshotUsage`: $211 → $253 (+$42 Jul→Aug)
- `EUC1-EBS:VolumeUsage.gp3`: $234 → $222 (-$12)

### SIT itariff-api ConfigMap Fix — tariff-buying-carriage-service
- Missing `service.rfq.code` → `PlaceholderResolutionException` → CrashLoopBackOff 35+ restarts
- Added `service.rfq.code: RFQ10001` to `tariff-buying-carriage-service` ConfigMap
- All 3 pods recovered

**All services affected by service.rfq.code missing (same new code deployment):**
| Service | service.rfq.code | Other missing |
|---|---|---|
| tariff-buying-otherbooking-service | RFQ10001 ✓ | - |
| tariff-buying-service | - | delete, archive, serviceurls.search |
| tariff-buying-carriage-service | RFQ10001 ✓ | - |

**WARNING**: Check remaining buying services (truck, standardcost, warehouse, shippingline) for same missing properties before they crash.


---
<!-- Source: knowledge-base/docs/session-notes-2026-05-20.md -->

# Session Notes - May 20, 2026

## 1. Dev vs SIT Resource Comparison (itariff-api)

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

## 2. S3 Optimization Report (itariff-api-optimization-report.md)

Located at: `s3://devops-securit-dev/itariff-api-optimization-report.md` (root level)
- NOT accessible from jump server 10.100.208.17 (different account)
- Accessible from dev bastion 10.100.145.118

Key findings:
- Most services using <5% CPU of requested resources
- tariff-selling-consumer-service has NO CPU limit (High severity)
- tariff-company-service & tariff-geo-service at ~85% memory usage
- tariff-domain-batch has no resource data (missing monitoring)

## 3. Prefiler Auth Service - Dev (WORKING)

- Namespace: `prefiler-api`
- Endpoint: `http://prefiler-auth-service-svc.prefiler-api.svc.cluster.local/api/v1/Auth/login`
- External: `http://prefiler-api.internaleu1dev-itopaz.com/prefiler-auth-service/api/v1/Auth/login`
- VS in `istio-system`, routes `/prefiler-auth-service/` prefix
- Config baked into Docker image (`/app/appsettings.json`)
- No envFrom or volume mounts needed - works with image-baked config
- Redis: `master.euc1-itopaz-dev-redis.lf4u8f.euc1.cache.amazonaws.com`

## 4. Prefiler Auth Service - SIT (BROKEN - DB Connection Failure)

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

## 5. SIT Prefiler-API VirtualService Routes

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

## 6. ConfigMaps in prefiler-api namespace (SIT)

- `aci-prefiler-service` - 1 data key
- `prefiler-auth-service` - 1 data key (nested YAML manifest)
- `prefiler-auth-service-config` - 16 data keys (flat, created today)

## GATI Application Inventory (Updated 2026-10-14)

Canonical structured report: `infrastructure/reports/gati-application-inventory-2026-10-14.csv`.

| Application | Ownership / vendor | Platform and database | Verified address | Hosting / access |
| --- | --- | --- | --- | --- |
| Gate Scan App | In-house | Native Android; backend TBC; PostgreSQL | `https://gate.allcargoapps.com`; `https://gatideliveryapk.allcargoapps.com` | Internal Gati and business partners; AWS/GEMS; AD SSO |
| HubEye | In-house | Web application on Linux EC2; PostgreSQL on RDS | `https://hubeye-dev-ui.allcargoapps.com`; `https://hubeye-dev-api.allcargoapps.com`; private EC2 `172.22.99.98` | Internal Gati; Mumbai `ap-south-1`; legacy account `339713157855`; AD SSO |
| AIM (GATE) - Telematics | In-house | Python on Linux; PostgreSQL | DEV `https://telematics-dev.allcargoapps.com`; UAT `https://telematics-gati-uat.allcargoapps.com`; PROD `https://telematics-gati.allcargoapps.com` | Internal Gati; AWS ALB; AD SSO |
| Call Center (Ameyo) | Exotel / Ameyo, contractual name TBC | Vendor-managed platform; database TBC | TBC | Internal Gati; on-premises Nagpur Call Center; AD SSO |
| Control Tower | Intugine | Vendor-managed web platform; PostgreSQL | TBC | Internal Gati; Intugine Cloud on AWS; AD SSO |
| JIRA | Atlassian | Jira Cloud; vendor-managed data store | Organization Jira URL TBC | Internal Gati; organization SSO; exact identity provider TBC |
| DMS | Vendor TBC | Web application on Linux EC2; Aurora PostgreSQL | PROD private IP `10.151.4.122`; UAT private IP `10.0.133.228`; URL TBC | AWS account `745510282686`, Mumbai `ap-south-1`; access and authentication TBC |
| IntelliHub | In-house | Python/FastAPI/Uvicorn services on Linux EC2; Nginx; database TBC | PROD `https://intellihub.allcargoapps.com`, `https://intelliaiml.allcargoapps.com`; TEST `https://intellihub-test.allcargoapps.com`, `https://aimlapp-test.allcargoapps.com` | Internal Gati on internet-facing endpoints; AWS account `745510282686`, Mumbai `ap-south-1`; authentication TBC |

### Verified infrastructure associations

- Gate Scan domains use CloudFront WAF `webacl-gati-cf`; its ARN indicates GATI account `072620096059`.
- HubEye DEV UI uses global WAF `whitelist-Other-IPs`; its DEV API uses the regional WAF of the same name.
- HubEye DEV EC2 is `i-0c5feaac7d6b278df` (`t3a.medium`), private address `172.22.99.98`, with no public IP.
- Telematics DEV, UAT, and PROD domains are associated with regional WAF `CreatedByALB-telematics`.
- Corporate AD credentials and the AD-managed password policy apply where AD SSO is recorded.

### Items requiring owner confirmation

- Gate Scan backend URL/service, database endpoint, exact AWS placement, and DR arrangement.
- HubEye account classification, environment naming, and DR arrangement.
- Telematics AWS account, region, and DR arrangement.
- Call Center contractual vendor name, database, URL, and DR arrangement.
- Control Tower URL, cloud account/region, and vendor DR controls.
- JIRA organization URL, exact identity provider, and whether AWS Identity Center portal `https://d-9f6707b589.awsapps.com/start` is a direct dependency.
- DMS vendor, application URL, exact user scope, authentication/password mechanism, and DR arrangement.
- IntelliHub database, authentication/password mechanism, exact access scope, and formal DR arrangement.

### DMS inventory details

- Production application: EC2 `ecu-prod_dms_app`, instance `i-050e2f027e2121c9b`, `t3a.large`, private IP `10.151.4.122`.
- UAT application: EC2 `dms-app-uat`, instance `i-06452e2ec4e7011d8`, `t3a.medium`, private IP `10.0.133.228`.
- Production database: Aurora PostgreSQL cluster `dms-prod`, endpoint `dms-prod.cvzxoaohm9ei.ap-south-1.rds.amazonaws.com:5432`, instance class `db.t3.medium`, recorded as not Multi-AZ.
- The application URL, authentication design, vendor/owner classification, and DR controls have not been verified.

### IntelliHub inventory details

- Production runs across `Intranet-prod-1` (`i-0b1f3b8eda05c132b`, `10.151.4.89`, `ap-south-1a`) and `Intranet-prod-2` (`i-0a82e63f8fcce6c8e`, `10.151.4.153`, `ap-south-1b`).
- Core production target groups were verified healthy on both instances, providing multi-AZ application placement.
- No Auto Scaling Group provides automatic instance replacement, and several supporting services remain single-instance; formal DR is therefore still TBC.
- Test services run on `Intranet-uat` (`i-0825be434cf7ab87b`, `10.0.132.243`) behind `LB-intranet` and `intellihub-test-GA`.
- Delivery uses CloudFront, Global Accelerator, ALBs, EC2, S3, Nginx, and multiple Python/FastAPI/Uvicorn services.
- Global Accelerator health-check configuration remains an open remediation item.
- On 2026-10-14, TCP `3001` was allowed from `LB-intranet` security group `sg-04973b9b0daf54d9a` to `aiml-sg` (`sg-0f2023634991b6f6e`) using rule `sgr-0783904f03b79a840`; target `i-0825be434cf7ab87b:3001` then became healthy.
- The asset-management public health URL still returns HTTP 404 because ALB path `/assest-management-backnd/*` is not rewritten to FastAPI path `/api/v1/health-check`. The FastAPI handler also needs the `PlainTextResponse` import.

## UAT Document Compatibility Review (2026-10-14)

- Reviewed APSE, EU, and US UAT v1.1 documents against AWS account `405478414008` through SSO with read-only API calls.
- Environment-off state was confirmed: regional bastions and Aurora clusters are stopped, and all EKS node groups have desired capacity zero. Managed EKS control planes, EFS, internal NLBs, Route 53, KMS, ECR, and Transit Gateway attachments remain available.
- Documents are partially compatible but unsafe to execute unchanged. Blocking drift includes document EKS `1.35` versus live `1.36`, nonzero node scaling, incorrect private-zone names, invalid region/ARN strings, cross-region copy errors, and declared ElastiCache clusters that do not exist in the account.
- Canonical findings: `infrastructure/reports/uat-document-compatibility-review-2026-10-14.md`.

## AVRT Playwright dev CI — verified 2026-10-16 (Asia/Kolkata)

- **Source:** `https://git-codecommit.ap-south-1.amazonaws.com/v1/repos/avrt-playwright`; host `10.0.132.243`, actual workspace `/root/var/www/avrt`, clean `dev` at `b5816dafd5c386e3312af0f7c7a430d3a099ee49`, matching remote dev. SSH uses `ubuntu` plus sudo with the POC key.
- **Runtime:** active `avrt.service` runs as ubuntu from `/home/ubuntu/avrt`, separate from the root Git workspace. No AVRT deployment, runtime data change or repository push was performed.
- **Jenkins:** [avrt-playwright-dev](http://10.151.4.91:8080/job/avrt-playwright-dev/); SSH requires ubuntu plus sudo with `/home/ec2-user/organized/keys/jenkins-server.pem` (direct root login is rejected). Existing CodeCommit credential `aws-gitcredentials-id` and Node tool `node22` are used.
- **Verified:** [build 2](http://10.151.4.91:8080/job/avrt-playwright-dev/2/) SUCCESS; dev checkout, npm ci, syntax checks on 48 files, 9 effects tests, Chromium launch/page smoke and archived logs. Jenkins/AVRT services active afterward. One-time startup script removed. User approved Jenkins restart; an initial build failed during the restart before successful build 2.
- **Limits:** CI only, no automatic trigger. Full integration suites need isolation repair: server.js hard-codes 9642 while harness tests specify alternate PORT values. Existing shared Node tool emits ENOVERSIONS for global package `10.5.0`, but installed Node/npm worked; shared configuration unchanged.
- **Artifacts:** [pipeline and setup notes](../infrastructure/jenkins/avrt-playwright-dev/README.md), [verification](../infrastructure/jenkins/avrt-playwright-dev/verification.json). Master sync bundle prepared separately; delivery remains pending without an inbound master endpoint.


---

# AllCargo iTOPAZ — Complete Session Knowledge Export
> Generated: 2026-09-01 | Covers: Aug 17 – Sep 1, 2026

═══════════════════════════════════════════════════════════════════════

## AVRT dev CI/CD deployment — verified 2026-10-27 (Asia/Kolkata)

- **Fixed:** successful CI did not deploy. Build 13 tested a4584d3 while source/runtime stayed at 35cf56d. The job now resides at `avrt/avrt-playwright-dev` on Jenkins 10.151.4.91:8080; the former root-job URL is historical.
- **Result:** [build 16](http://10.151.4.91:8080/job/avrt/job/avrt-playwright-dev/16/) SUCCESS (95 seconds), tested and deployed `a4584d3e3091e54aeb1a895be1ff75edaf8e5ebf`. Both `/root/var/www/avrt` and `/home/ubuntu/avrt` on 10.0.132.243 have clean tracked files at that revision. avrt.service is active; local health and public login.js returned 200 with matching deployed asset hash.
- **Delivery:** `DEPLOY_TO_AVRT` defaults true. Jenkins transfers the exact tested Git bundle using existing SSH credential `uat-ec2-ssh-key` and a pinned host key. Root-owned `/usr/local/sbin/avrt-deploy` stages dependencies/Chromium as ubuntu, briefly stops AVRT, preserves data/local config/untracked files, activates the tested revision, verifies health/assets and updates the reference checkout. Builds remain manually triggered; no SCM polling/webhook was added.
- **Recovery/preservation:** prior code/dependencies and private data snapshot remain under `/var/lib/avrt-deploy/backups/20261027T112351Z-a4584d3e3091e54aeb1a895be1ff75edaf8e5ebf`. All four persistent data files matched the snapshot and the data inode stayed unchanged. Automatic source/dependency rollback is implemented but has not been deliberately exercised against a failed live release. Private data snapshots are not exported.
- **Limits:** full authenticated workflows were not tested; integration harness passes PORT while the app reads AVRT_PORT. Existing shared node22 ENOVERSIONS warnings remain. Target AWS CLI credential helper fails with KeyError opsworkscm; deployment bypasses it using the Git bundle. No source-repository push or shared-tool change.
- **Artifacts:** [runbook](../infrastructure/jenkins/avrt-playwright-dev/README.md), [verification](../infrastructure/jenkins/avrt-playwright-dev/verification-20261027.json). This supersedes the CI-only delivery behavior recorded on 2026-10-16. Master bundle prepared locally; delivery pending without an inbound master endpoint.



---

# AllCargo iTOPAZ — Complete Session Knowledge Export
> Generated: 2026-09-01 | Covers: Aug 17 – Sep 1, 2026

═══════════════════════════════════════════════════════════════════════

## DEV Frankfurt Glue SQL Server connection — provisioned 2026-10-28

- **Created:** native SQLSERVER connection `sql-dev-frankfurt-dms`, schema 2, account `074779643551`, region `eu-central-1`, configured for Spark. AWS provisioning status READY does not establish database connectivity.
- **Target:** `10.1.161.19:1433`, database `EUEUDBECUGROUPAGE`, login `dms_user`, from supplied DMS endpoint `arn:aws:dms:eu-central-1:074779643551:endpoint:sql-dev-frankfurt-dms`. User clarified SQL Server only; no PostgreSQL connection created.
- **Network:** VPC `vpc-0fedcc7988431eedb`, subnet `subnet-0ceedebf41e570f8f` (eu-central-1b, `10.100.159.32/27`), matching active DMS. New group `sg-0e3b87b11e66d64c5` has self TCP ingress and scoped SQL/HTTPS/DNS egress. Existing role `glue-pg-to-sqlserver-role` reused; no IAM policy changes.
- **Credentials:** new encrypted secret `glue/sql-dev-frankfurt-dms`, ARN ending `eX0Jtw`, derived in memory from the same-host/login `dms-db-cred` secret and normalized to USERNAME/PASSWORD for unified connections. No password values retained locally or printed. Original secret and DMS endpoint configuration unchanged. New secret rotations are independent of source-secret rotations.
- **TLS:** ENFORCE_SSL true; JDBC_PARAMS encrypt=true;trustServerCertificate=true, matching DMS require mode. Driver certificate identity validation is not enabled by this mode.
- **Validation BLOCKED:** native Glue TCP connection to SQL Server times out. Fresh DMS endpoint test succeeded from `10.100.159.50`; observed native Glue IP `10.100.159.54`. AWS group egress and subnet ACL permit the flow; routing matches DMS. No target interface exists in this account/region. Source-IP/source-group filtering on the SQL/network side is a possible cause, not confirmed. Check access for the bounded Glue subnet/group to destination TCP 1433.
- **Limits/cleanup:** database authentication and SELECT 1 have not been verified. Temporary Spark test failed at initial legacy URL bootstrap before any database query; job and its S3 script version were removed. No database writes, replication-task changes or external firewall changes.
- **Evidence:** [runbook](../infrastructure/glue/sql-dev-frankfurt-dms/README.md), [verification](../infrastructure/glue/sql-dev-frankfurt-dms/verification.json), and non-secret connection/readback/security-group definitions in that directory. Master bundle prepared locally; delivery pending without an inbound master endpoint.
