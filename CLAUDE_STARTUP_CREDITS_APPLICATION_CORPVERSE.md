# Corpverse Technologies - Claude for Startups & Cloud Credits Application Dossier

**Entity Name:** Corpverse Technologies (M/s VcorpTech)  
**Registered Email:** support@corpversetechnologies.com  
**Website:** https://corpversetechnologies.com  
**Founder & Technical Lead:** Rahul Kumar (Promoter / Director)  
**Institutional Backing / Incubator:** DTU Innovation and Incubation Foundation (DTU-IIF), Delhi Technological University  
**Incubation Ref:** File No. DTU-IIF/VcorpTech/83/2024-25/733 (Dated 24.02.2025)  
**Target Program:** Anthropic Claude for Startups ($1,000 - $25,000+ Credits & 1-Yr Team Plan) & AWS Activate Portfolio ($10k-$100k Bedrock Claude Credits)

---

## 1. Company & Founder Profile

* **Company Name:** Corpverse Technologies Private Limited / M/s VcorpTech
* **Corporate Email:** support@corpversetechnologies.com
* **Founding Date:** 2024 / 2025
* **Stage:** Pre-Seed / Incubated (DTU-IIF, Delhi Technological University)
* **Founder:** Rahul Kumar
* **Founder Education:** 
  - MBA in Business Analytics, Delhi Technological University (2023–2025)
  - B.Tech in Information Technology, Delhi Technological University (2016–2020)
* **Professional Experience:** 4+ Years DevOps / Cloud Infrastructure / Platform Security (AWS Certified DevOps Engineer - Professional DOP-C02 & AWS Data Engineer Associate)
* **Incubation Details:** Selected for Incubation by DTU Innovation and Incubation Foundation (DTU-IIF), 8th Floor, Room 805, Delhi Technological University, Shahbad Daulatpur, Delhi-110042.

---

## 2. Core Idea & Product Architecture: "NetSentience" (Autonomous AI Network Security & Forensics Agent)

### Executive Summary:
Corpverse Technologies is building an autonomous, agentic network security platform that combines kernel-level telemetry (eBPF and live packet capture) with Claude's advanced reasoning capabilities to detect, analyze, and autonomously mitigate complex network intrusions and zero-day threats in real time.

### The Problem:
Modern microservice architectures and distributed cloud environments generate gigabytes of raw network packet streams per minute. Traditional Signature-based Intrusion Detection Systems (IDS) and rule-based SIEM tools suffer from high false-positive rates, cannot detect novel multi-vector attack sequences, and require manual human intervention to draft and apply firewall or NetworkPolicy rules, creating critical dwell-time vulnerabilities.

### The Solution (How We Use Claude):
1. **Packet Capture & Telemetry Pipeline:** 
   Our lightweight edge daemon captures network packet flows and reconstructs protocol streams (HTTP/2, gRPC, DNS, TLS handshakes, TCP conntrack tables) using eBPF probes without degrading throughput.
2. **Claude 3.5 Haiku (Fast Triage & Anomaly Pre-Filtering):**
   High-frequency telemetry summaries and metadata are piped to Claude 3.5 Haiku for sub-second classification of suspicious sessions, anomalous payload structures, and protocol deviations.
3. **Claude 3.5 Sonnet (Deep Forensic Analysis & Attack Reconstruction):**
   Flagged PCAP sequences and application payload contexts (up to 200,000 tokens) are analyzed by Claude 3.5 Sonnet. Claude reconstructs the full attacker chain (reconnaissance, exploitation, C2 beaconing, and lateral movement attempts).
4. **Autonomous Remediation Synthesis (Tool-Calling & Rule Generation):**
   Using structured tool-calling, Claude synthesizes precise, non-breaking remediation policies:
   - Dynamic Linux `iptables` / `nftables` / eBPF XDP filters to drop malicious traffic at the kernel network interface.
   - Kubernetes `NetworkPolicy` declarations to isolate compromised pods.
   - AWS WAF and CloudFront rule sets to shield public ingress endpoints.
5. **Explainability & Human-in-the-Loop Audit:**
   Claude generates human-readable incident post-mortems with cryptographic packet evidence, explaining exact attack vectors and validating that benign traffic remains unblocked.

---

## 3. Pre-Filled Form Answers for Claude for Startups

### Q: What is your company's name and website?
> **Answer:**  
> Company: Corpverse Technologies (M/s VcorpTech)  
> Website: https://corpversetechnologies.com  
> Email: support@corpversetechnologies.com

### Q: Briefly describe what your startup does (1-2 sentences).
> **Answer:**  
> Corpverse Technologies builds an autonomous AI network defense agent that captures live packet telemetry via eBPF and leverages Claude to detect zero-day security threats, analyze forensic PCAP streams, and autonomously synthesize precision firewall and network policies.

### Q: How do you plan to use the Claude API in your product?
> **Answer:**  
> We integrate Claude 3.5 Haiku for high-throughput anomaly triage of packet metadata and Claude 3.5 Sonnet for deep forensic reconstruction of multi-vector network attacks. Claude's large 200k context window allows us to feed raw protocol dumps and session traces to pinpoint zero-day exploits, while its structured tool-use directly generates and verifies dynamic kernel eBPF rules, Kubernetes NetworkPolicies, and Cloud WAF configurations to remediate vulnerabilities in real time.

### Q: What stage is your company and what funding have you raised?
> **Answer:**  
> Stage: Pre-Seed / Incubated.  
> We are officially incubated at the DTU Innovation and Incubation Foundation (DTU-IIF) promoted by Delhi Technological University (Govt. of NCT of Delhi, Letter of Intent Ref: DTU-IIF/VcorpTech/83/2024-25/733).

### Q: What Claude models are you primarily interested in using?
> **Answer:**  
> Claude 3.5 Sonnet (for forensic analysis, code/policy generation, and complex threat reasoning) and Claude 3.5 Haiku (for low-latency streaming telemetry classification).

---

## 4. Application Channels & Submission Guide

### Channel A: Direct Anthropic "Claude for Startups"
* **Application Link:** https://claude.com/programs/startups
* **Important Network Note:** Corporate proxy (Zscaler) blocks `claude.com` on your current workstation with an AI policy warning. **Open the link from your personal laptop, mobile browser, or home network.**
* **Steps:**
  1. Go to https://claude.com/programs/startups
  2. Click **Apply Now**.
  3. Sign in or sign up using `support@corpversetechnologies.com`.
  4. Paste the pre-filled responses from Section 3 above.
  5. Mention DTU-IIF incubation backing.

### Channel B: AWS Activate Portfolio Tier ($10,000 - $100,000 in Credits)
* **Why this is critical:** AWS Activate promotional credits **directly cover Anthropic Claude on Amazon Bedrock** (Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus)!
* **How to leverage your DTU-IIF LOI:**
  1. Contact your DTU-IIF incubation coordinator or email `dtu.iif@gmail.com` / `dtuiif@dtu.ac.in` requesting the **DTU-IIF AWS Activate Organization ID / Partner Code**.
  2. Visit: https://aws.amazon.com/startups/credits
  3. Select **Portfolio Tier** and enter the DTU-IIF Org ID.
  4. Upload your DTU-IIF Letter of Intent (`DTU-IIF/VcorpTech/83/2024-25/733`) as proof of incubation.
  5. Once approved, enable Amazon Bedrock in your AWS account and run Claude models fully funded by AWS credits.

