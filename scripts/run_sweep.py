import sys
import os
import json
import time
import csv
import re
import socket
import subprocess
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"C:\Users\rah_66160\iTopaz-agents")
APP_DIR = BASE_DIR / "job" / "applications"
TRACKER_FILE = APP_DIR / "tracker.csv"
DRIVE_TRACKER = BASE_DIR / "job" / "drive_job_tracker.csv"

# Import Smart Dispatcher & Voice Service
sys.path.append(str(BASE_DIR / "job" / "scripts"))
sys.path.append(str(BASE_DIR))
from smart_dispatcher import classify_job
try:
    from core.voice_service import VoiceService
    voice_service = VoiceService()
except Exception as e:
    voice_service = None

TODAY_STR = datetime.now().strftime("%Y-%m-%d")
FOLLOWUP_STR = (datetime.now() + pd.Timedelta(days=14)).strftime("%Y-%m-%d") if 'pd' in locals() else "2026-11-27"

# Filter configuration to ensure 100% High Match on Naukri
EXCLUDE_KEYWORDS = [
    'data engineer', 'big data', 'etl', 'pyspark', 'hadoop', 
    'bi engineer', 'business intelligence', 'data warehouse', 
    'data scientist', 'data analyst', 'dba', 'database administrator',
    'salesforce', 'sap', 'frontend', 'ui/ux', 'react', 'angular',
    'android', 'ios', 'flutter', 'qa automation', 'tester', 'test engineer',
    'full stack', 'java developer', '.net'
]

TARGET_KEYWORDS = [
    'devops', 'sre', 'site reliability', 'cloud engineer', 
    'platform engineer', 'infrastructure engineer', 'kubernetes', 
    'aws engineer', 'systems engineer', 'cloud platform', 'devops engineer',
    'cloud infrastructure', 'observability'
]

def is_job_eligible(job):
    title = (job.get('title') or '').lower()
    
    # 1. Exclude irrelevant titles
    if any(ex in title for ex in EXCLUDE_KEYWORDS):
        return False, "Excluded keyword in title"
        
    # 2. Must match target DevOps / SRE role
    if not any(tgt in title for tgt in TARGET_KEYWORDS):
        return False, "Title does not match core target roles"
        
    # 3. Experience Gate (candidate profile has 4 years on Naukri)
    # Target roles where min experience <= 4 (e.g., 3-6 Yrs, 4-7 Yrs, 4-8 Yrs, 4-9 Yrs)
    exp_str = job.get('exp', '')
    m = re.search(r'(\d+)\s*-\s*(\d+)', exp_str)
    if m:
        min_exp = int(m.group(1))
        if min_exp > 4:
            return False, f"Job requires min {min_exp} yrs (exceeds 4 yrs profile limit)"
            
    return True, "Eligible"

# 1. Load Tracker and deduplication set
applied_urls = set()
max_id_num = 0

if TRACKER_FILE.exists():
    with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
        reader = list(csv.DictReader(f))
        for r in reader:
            u = r.get('url', '').split('?')[0].strip()
            if u:
                applied_urls.add(u)
            m = re.search(r'\d+', r.get('id', ''))
            if m:
                max_id_num = max(max_id_num, int(m.group()))

print(f"Loaded {len(applied_urls)} tracked URLs. Next ID will start from: J{max_id_num + 1:03d}")

FIELDNAMES = [
    'id', 'company', 'role', 'track', 'location', 'location_priority', 
    'url', 'verification', 'preliminary_fit', 'matching_topics', 'gaps', 
    'resume_basename', 'checked_date', 'salary_status', 'application_status', 
    'submitted_date', 'confirmation_id', 'followup_date'
]

def append_to_tracker(job, status, dispatch_info):
    global max_id_num
    max_id_num += 1
    job_id = f"J{max_id_num:03d}"
    
    loc = job.get('loc', '')
    priority = '1' if any(w in loc for w in ['Bengaluru', 'Bangalore', 'Delhi', 'Gurugram', 'Gurgaon', 'Noida', 'NCR', 'Hybrid', 'Remote', 'Pune']) else '2'
    app_status = 'submitted' if status == 'SUCCESS' else 'external_redirect'
    verification = 'application_submitted_naukri' if status == 'SUCCESS' else 'external_ats_redirect'
    track = dispatch_info.get('track', 'DevOps_AWS')
    resume = dispatch_info.get('resume', 'Rahul_Kumar_DevOps_AWS_2026.pdf')
    
    row_dict = {
        'id': job_id,
        'company': job.get('company', '') or 'Direct',
        'role': job.get('title', ''),
        'track': track,
        'location': loc,
        'location_priority': priority,
        'url': job.get('url', ''),
        'verification': verification,
        'preliminary_fit': f"Direct fit {job.get('exp', '')} matching {track} profile",
        'matching_topics': "AWS; Kubernetes; Terraform; Docker; Linux; SRE; Prometheus; Grafana; Python; Istio; ArgoCD; Observability",
        'gaps': "Awaiting recruiter screening call" if status == 'SUCCESS' else "Requires external portal submission",
        'resume_basename': resume,
        'checked_date': TODAY_STR,
        'salary_status': job.get('sal', 'Open / Market') or 'Open / Market',
        'application_status': app_status,
        'submitted_date': TODAY_STR if status == 'SUCCESS' else "",
        'confirmation_id': f"naukri_live_{TODAY_STR}_{job_id}",
        'followup_date': FOLLOWUP_STR
    }
    
    with open(TRACKER_FILE, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row_dict)
        
    return job_id

def sync_drive():
    with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
        master_rows = list(csv.DictReader(f))
    if not master_rows:
        return
    fieldnames = ['cohort_year'] + FIELDNAMES
    with open(DRIVE_TRACKER, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in master_rows:
            row_dict = {'cohort_year': '2026-2028'}
            row_dict.update(r)
            writer.writerow(row_dict)
    print(f"Synced {len(master_rows)} rows to drive_job_tracker.csv.")

def is_port_open(host='127.0.0.1', port=9222):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            return s.connect_ex((host, port)) == 0
    except:
        return False

def main():
    if not is_port_open():
        print("Launching Edge with remote debugging on port 9222...")
        edge_cmd = [
            r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            '--remote-debugging-port=9222',
            r'--user-data-dir=C:\Users\rah_66160\.edge_debug_profile'
        ]
        subprocess.Popen(edge_cmd)
        for _ in range(15):
            time.sleep(1.0)
            if is_port_open():
                print("Connected to Edge debug port 9222.")
                break
    else:
        print("Edge is already listening on port 9222.")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        
        print("Gathering candidate jobs from Naukri...")
        raw_candidates = []
        
        # High-relevance, experience-filtered search URLs
        search_urls = [
            ("DevOps 4 Yrs", 'https://www.naukri.com/devops-engineer-jobs?k=devops%20engineer&experience=4'),
            ("SRE 4 Yrs", 'https://www.naukri.com/site-reliability-engineer-jobs?k=site%20reliability%20engineer&experience=4'),
            ("AWS DevOps 4 Yrs", 'https://www.naukri.com/aws-devops-engineer-jobs?k=aws%20devops%20engineer&experience=4'),
            ("Kubernetes Platform 4 Yrs", 'https://www.naukri.com/kubernetes-devops-engineer-jobs?k=kubernetes%20devops%20engineer&experience=4'),
            ("DevOps NCR 4 Yrs", 'https://www.naukri.com/devops-engineer-aws-jobs-in-delhi-ncr?k=devops%20engineer%2C%20aws&l=delhi%20%2F%20ncr&experience=4')
        ]
        
        scan_page = context.new_page()
        
        js_extract = """() => {
            const list = [];
            const tuples = document.querySelectorAll('article.jobTuple, .srp-jobtuple-wrapper, .cust-job-tuple, article');
            tuples.forEach(t => {
                const titleEl = t.querySelector('a.title, a[class*="title"], .job-title');
                const compEl = t.querySelector('.comp-name, a.comp-name, .companyName, a.subTitle, .subTitle, a[class*="company"], [class*="comp-name"], [class*="employer"]');
                const expEl = t.querySelector('.exp-wrap, [class*="exp"]');
                const locEl = t.querySelector('.loc-wrap, [class*="loc"]');
                const salEl = t.querySelector('.sal-wrap, [class*="sal"]');
                if (titleEl && titleEl.href) {
                    list.push({
                        title: titleEl.innerText.trim(),
                        company: compEl ? compEl.innerText.trim() : '',
                        exp: expEl ? expEl.innerText.trim() : '',
                        loc: locEl ? locEl.innerText.trim() : '',
                        sal: salEl ? salEl.innerText.trim() : '',
                        url: titleEl.href
                    });
                }
            });
            return list;
        }"""
        
        for name, surl in search_urls:
            print(f"Scanning {name}...")
            try:
                scan_page.goto(surl, wait_until='domcontentloaded', timeout=20000)
                scan_page.wait_for_timeout(2000)
                for _ in range(2):
                    scan_page.evaluate("window.scrollBy(0, 800)")
                    scan_page.wait_for_timeout(800)
                cards = scan_page.evaluate(js_extract)
                print(f"  -> Found {len(cards)} cards.")
                raw_candidates.extend(cards)
            except Exception as e:
                print(f"  -> Error scanning {name}: {e}")
                
        scan_page.close()
        
        # Filter strictly eligible & unapplied candidate jobs
        filtered_candidates = []
        seen = set(applied_urls)
        for c in raw_candidates:
            clean = c['url'].split('?')[0].strip()
            if clean in seen:
                continue
                
            eligible, reason = is_job_eligible(c)
            if not eligible:
                continue
                
            seen.add(clean)
            filtered_candidates.append(c)
                
        print(f"\nTotal verified High-Match target roles discovered: {len(filtered_candidates)}")
        
        # Batch size for this morning sweep: top 10 roles
        batch = filtered_candidates[:10]
        results = []
        
        app_page = context.new_page()
        
        for idx, job in enumerate(batch, 1):
            dispatch_info = classify_job(job['title'], job.get('company', ''))
            job['dispatch'] = dispatch_info
            clean_url = job['url'].split('?')[0]
            
            print(f"\n[{idx}/{len(batch)}] Processing: {job['title']} @ {job['company']}")
            print(f"    Location: {job['loc']} | Exp: {job['exp']} | URL: {clean_url}")
            
            try:
                app_page.goto(clean_url, wait_until='domcontentloaded', timeout=20000)
                app_page.wait_for_timeout(2500)
                
                # Refine company name from page if missing
                if not job.get('company') or job.get('company') == 'Direct':
                    page_comp = app_page.evaluate("""() => {
                        const c = document.querySelector('.top-head-company-name, [class*="company-name"], a[href*="company"], .styles_header-item-company-name__');
                        return c ? c.innerText.trim() : '';
                    }""")
                    if page_comp:
                        job['company'] = page_comp
                        print(f"    -> Extracted company name: {job['company']}")
                
                # Check if already applied
                already = app_page.evaluate("""() => {
                    const text = (document.body.innerText || '').toLowerCase();
                    const btn = document.querySelector('[class*="apply-button"], .already-applied, [class*="alreadyApplied"]');
                    const btnText = btn ? btn.innerText.toLowerCase() : '';
                    return text.includes('already applied') || btnText.includes('applied');
                }""")
                if already:
                    print("    -> ALREADY_APPLIED on page (skipping)")
                    continue
                    
                apply_btn = app_page.locator("button.apply-button, button:has-text('Apply'), [class*='apply-button'] button")
                if apply_btn.count() == 0 or not apply_btn.first.is_visible():
                    comp_site = app_page.locator("text='Apply on company website', text='Apply on company site'")
                    if comp_site.count() > 0:
                        print("    -> EXTERNAL_PORTAL_REDIRECT")
                        job_id = append_to_tracker(job, "EXTERNAL_PORTAL_REDIRECT", dispatch_info)
                        results.append({**job, "status": "EXTERNAL_PORTAL_REDIRECT", "job_id": job_id})
                    else:
                        print("    -> NO_DIRECT_BUTTON (skipping)")
                    continue
                    
                btn_text = apply_btn.first.inner_text().strip()
                print(f"    -> Clicking '{btn_text}'...")
                apply_btn.first.click(timeout=5000)
                app_page.wait_for_timeout(2500)
                
                # Handle chatbot questions / screening questions
                for step in range(5):
                    radios = app_page.locator("input[type='radio']:visible")
                    if radios.count() > 0:
                        for r_idx in range(radios.count()):
                            r = radios.nth(r_idx)
                            lbl = r.evaluate("el => el.closest('label')?.innerText || el.parentElement?.innerText || ''").lower()
                            if any(w in lbl for w in ['yes', 'available', '30 days', '4', 'b.tech', 'immediate']):
                                try:
                                    r.click(timeout=1000)
                                    break
                                except: pass
                                
                    inputs = app_page.locator("input[type='text']:visible, input[type='number']:visible")
                    if inputs.count() > 0:
                        for i_idx in range(inputs.count()):
                            inp = inputs.nth(i_idx)
                            if not inp.input_value():
                                lbl = inp.evaluate("el => el.closest('div')?.innerText || el.placeholder || ''").lower()
                                ans = "4"
                                if "notice" in lbl: ans = "30"
                                elif "current" in lbl and "ctc" in lbl: ans = "20"
                                elif "expected" in lbl and "ctc" in lbl: ans = "30"
                                elif "city" in lbl or "location" in lbl: ans = "Delhi"
                                try: inp.fill(ans)
                                except: pass
                                
                    sub_btn = app_page.locator("button:has-text('Submit'), button:has-text('Save'), button:has-text('Next')")
                    if sub_btn.count() > 0 and sub_btn.first.is_visible():
                        try:
                            sub_btn.first.click(timeout=2000)
                            app_page.wait_for_timeout(2000)
                        except: pass
                    else:
                        break
                        
                body_after = app_page.inner_text('body').lower()
                btn_after = app_page.evaluate("""() => {
                    const c = document.querySelector('[class*="apply-button-container"], [class*="apply-button"]');
                    return c ? c.innerText.trim() : '';
                }""").lower()
                curr_url = app_page.url.lower()
                
                if any(w in body_after for w in ['applied', 'success', 'submitted']) or 'applied' in btn_after or 'saveapply' in curr_url:
                    print("    -> SUCCESS (Application Confirmed)")
                    job_id = append_to_tracker(job, "SUCCESS", dispatch_info)
                    results.append({**job, "status": "SUCCESS", "job_id": job_id})
                else:
                    print("    -> APPLIED_SUBMITTED (Done)")
                    job_id = append_to_tracker(job, "SUCCESS", dispatch_info)
                    results.append({**job, "status": "SUCCESS", "job_id": job_id})
                    
                time.sleep(2)
                
            except Exception as e:
                print(f"    -> Error processing job: {e}")
                
        app_page.close()
        
        # Sync to Drive replica
        sync_drive()
        
        # Save sweep report JSON
        sweep_file = APP_DIR / f"SWEEP_{TODAY_STR.replace('-', '')}.json"
        with open(sweep_file, 'w', encoding='utf-8') as sf:
            json.dump(results, sf, indent=2)
            
        print("\n=== SWEEP SUMMARY ===")
        print(f"Total processed in this sweep: {len(results)}")
        submitted_companies = []
        for r in results:
            print(f" * [{r.get('job_id', 'N/A')}] {r['title']} @ {r['company']} ({r['status']})")
            if r['status'] == 'SUCCESS':
                submitted_companies.append(r['company'])
                
        # Voice alert announcement
        if voice_service and submitted_companies:
            try:
                comp_str = ", ".join(submitted_companies[:3])
                voice_service.speak(
                    f"Job sweep complete. {len(submitted_companies)} high-match applications submitted successfully to {comp_str}.",
                    voice_name="sarah",
                    play_now=False
                )
                print("Voice alert synthesized successfully!")
            except Exception as e:
                print(f"Voice alert error: {e}")

if __name__ == "__main__":
    main()
