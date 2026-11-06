import sys
import os
import json
import time
import csv
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"C:\Users\rah_66160\iTopaz-agents")
APP_DIR = BASE_DIR / "job" / "applications"
TRACKER_FILE = APP_DIR / "tracker.csv"

# Import Smart Dispatcher
sys.path.append(str(BASE_DIR / "job" / "scripts"))
from smart_dispatcher import classify_job

# Load past applied URLs to ensure 100% deduplication
applied_urls = set()
existing_rows = []
if TRACKER_FILE.exists():
    with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
        reader = list(csv.reader(f))
        if reader:
            existing_rows = reader
            for r in reader[1:]:
                if len(r) > 6 and r[6]:
                    applied_urls.add(r[6].split('?')[0].strip())

last_id_num = int(existing_rows[-1][0].replace('J', '')) if len(existing_rows) > 1 else 0
print(f"Loaded {len(applied_urls)} tracked URLs. Last Tracker ID: J{last_id_num:03d}")

# Targeted high-yield expansion queries for Nov 03, 2026
SEARCHES = [
    ("DevOps High-CTC 25-50L", "https://www.naukri.com/devops-engineer-jobs?k=devops%20engineer&experience=4&ctcFilter=25to50"),
    ("SRE Bangalore & Remote", "https://www.naukri.com/site-reliability-engineer-jobs?k=site%20reliability%20engineer&experience=4&cityTypeGid=9508&cityTypeGid=97"),
    ("Kubernetes Platform Engineer", "https://www.naukri.com/kubernetes-devops-engineer-jobs?k=kubernetes%20devops%20engineer&experience=4"),
    ("Cloud DevOps Architect", "https://www.naukri.com/aws-cloud-architect-jobs?k=aws%20cloud%20architect&experience=4")
]

TODAY_STR = "2026-11-03"
FOLLOWUP_STR = "2026-11-17"

def append_to_tracker(job, status, dispatch_info):
    global last_id_num
    last_id_num += 1
    job_id = f"J{last_id_num:03d}"
    
    loc = job.get('loc', '')
    priority = '1' if any(w in loc for w in ['Bengaluru', 'Bangalore', 'Hybrid', 'Remote', 'Pune']) else '2'
    app_status = 'submitted' if status == 'SUCCESS' else 'external_redirect'
    verification = 'application_submitted_naukri' if status == 'SUCCESS' else 'external_ats_redirect'
    track = dispatch_info.get('track', 'DevOps_AWS')
    resume = dispatch_info.get('resume', 'Rahul_Kumar_DevOps_AWS_2026.pdf')
    
    row = [
        job_id,
        job.get('company', ''),
        job.get('title', ''),
        track,
        loc,
        priority,
        job.get('url', ''),
        verification,
        f"Direct fit {job.get('exp', '')} matching {track} profile",
        "AWS; Kubernetes; Terraform; Docker; Linux; SRE; Prometheus; Grafana; Python",
        "Awaiting recruiter screening call" if status == 'SUCCESS' else "Requires external portal submission",
        resume,
        TODAY_STR,
        job.get('sal', 'Open / Market') or 'Open / Market',
        app_status,
        TODAY_STR if status == 'SUCCESS' else "",
        f"naukri_smart_{TODAY_STR}_{job_id}",
        FOLLOWUP_STR
    ]
    
    with open(TRACKER_FILE, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)
        
    return job_id

def run_expansion():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = context.new_page()

        print(f"\n--- PHASE 1: DISCOVERING FRESH ROLES TOWARDS 171 TARGET ---")
        candidates = []
        seen = set(applied_urls)

        js_extract = """
        () => {
            const list = [];
            document.querySelectorAll('a.title, a[class*="title"]').forEach(a => {
                if (a.href && a.href.includes('job-listings-')) {
                    let parent = a.closest('.srp-jobtuple-wrapper, .cust-job-tuple') || a.parentElement;
                    while (parent && !parent.className.includes('tuple') && parent !== document.body) {
                        parent = parent.parentElement;
                    }
                    const company = parent?.querySelector('a.comp-name, .companyName, .comp-name')?.innerText?.trim() || '';
                    const exp = parent?.querySelector('.exp-wrap, .expwdth, [class*="exp"]')?.innerText?.trim() || '';
                    const loc = parent?.querySelector('.loc-wrap, .locwdth, [class*="loc"]')?.innerText?.trim() || '';
                    const sal = parent?.querySelector('.sal-wrap, .salwdth, [class*="sal"]')?.innerText?.trim() || '';
                    const desc = parent?.querySelector('.job-desc, [class*="desc"]')?.innerText?.trim() || '';
                    list.push({ title: a.innerText.trim(), company, exp, loc, sal, desc, url: a.href });
                }
            });
            return list;
        }"""

        for label, url in SEARCHES:
            print(f"Scanning [{label}]...")
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=25000)
                page.wait_for_timeout(2500)
                batch = page.evaluate(js_extract)
                print(f"  -> Discovered {len(batch)} jobs on page.")
                for b in batch:
                    clean = b['url'].split('?')[0].strip()
                    if clean not in seen:
                        seen.add(clean)
                        candidates.append(b)
            except Exception as e:
                print(f"  -> Error: {e}")

        print(f"\nDiscovered {len(candidates)} brand new unapplied candidate roles.")

        # Batch limit: process top 15 high-match roles in this sweep
        batch_to_process = candidates[:15] if candidates else []
        print(f"Selecting top {len(batch_to_process)} roles for execution.\n")

        results = []
        for idx, job in enumerate(batch_to_process, 1):
            dispatch_info = classify_job(job['title'], job.get('desc', ''))
            job['dispatch'] = dispatch_info
            clean_url = job['url'].split('?')[0]
            
            print(f"[{idx}/{len(batch_to_process)}] {job['title']} @ {job['company']}")
            print(f"    -> Track: {dispatch_info['track']} | Target Resume: {dispatch_info['resume']}")
            print(f"    -> Location: {job['loc']} | Exp: {job['exp']} | Salary: {job.get('sal', 'N/A')}")

            try:
                page.goto(clean_url, wait_until='domcontentloaded', timeout=25000)
                page.wait_for_timeout(2000)

                already = page.evaluate("""() => {
                    const text = (document.body.innerText || '').toLowerCase();
                    const btn = document.querySelector('[class*="apply-button-container"], .already-applied, [class*="alreadyApplied"]');
                    const btnText = btn ? btn.innerText.toLowerCase() : '';
                    return text.includes('already applied') || btnText.includes('applied');
                }""")
                if already:
                    print("    -> Status: ALREADY_APPLIED (Skipping)")
                    continue

                apply_btn = page.locator("[class*='apply-button-container'] button, button:has-text('Apply'), .apply-button")
                if apply_btn.count() == 0 or not apply_btn.first.is_visible():
                    comp_site = page.locator("text='Apply on company website', text='Apply on company site'")
                    if comp_site.count() > 0:
                        print("    -> Status: EXTERNAL_PORTAL_REDIRECT")
                        job_id = append_to_tracker(job, "EXTERNAL_PORTAL_REDIRECT", dispatch_info)
                        results.append({**job, "status": "EXTERNAL_PORTAL_REDIRECT", "job_id": job_id})
                    else:
                        print("    -> Status: NO_DIRECT_BUTTON")
                    continue

                btn_text = apply_btn.first.inner_text().strip()
                print(f"    -> Clicking '{btn_text}'...")
                apply_btn.first.click(timeout=5000)
                page.wait_for_timeout(2500)

                # Form & Chatbot answers
                for _ in range(3):
                    radios = page.locator("input[type='radio']:visible")
                    if radios.count() > 0:
                        for r_idx in range(radios.count()):
                            r = radios.nth(r_idx)
                            lbl = r.evaluate("el => el.closest('label')?.innerText || el.parentElement?.innerText || ''").lower()
                            if any(w in lbl for w in ['yes', 'available', '30 days', '4', 'b.tech', 'immediate']):
                                try:
                                    r.click(timeout=1000)
                                    break
                                except: pass

                    inputs = page.locator("input[type='text']:visible, input[type='number']:visible")
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

                    submit_btn = page.locator("button:has-text('Submit'), button:has-text('Save'), button:has-text('Next')")
                    if submit_btn.count() > 0 and submit_btn.first.is_visible():
                        try:
                            submit_btn.first.click(timeout=2000)
                            page.wait_for_timeout(2000)
                        except: pass
                    else:
                        break

                body_after = page.inner_text('body').lower()
                btn_after = page.evaluate("""() => {
                    const c = document.querySelector('[class*="apply-button-container"], [class*="apply-button"]');
                    return c ? c.innerText.trim() : '';
                }""").lower()

                if any(w in body_after for w in ['applied', 'success', 'submitted']) or 'applied' in btn_after:
                    print("    -> Status: SUCCESS (Application Confirmed)")
                    job_id = append_to_tracker(job, "SUCCESS", dispatch_info)
                    results.append({**job, "status": "SUCCESS", "job_id": job_id})
                else:
                    print("    -> Status: APPLIED_PENDING")
                    job_id = append_to_tracker(job, "APPLIED_PENDING", dispatch_info)
                    results.append({**job, "status": "APPLIED_PENDING", "job_id": job_id})

            except Exception as e:
                print(f"    -> Error: {e}")

        page.close()

        # Step 4: Write Audit Run Report
        print(f"\n--- PHASE 4: AUDIT REPORT GENERATION ---")
        out_json = APP_DIR / f"EXPANSION_BATCH_{TODAY_STR.replace('-', '')}.json"
        out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"Expansion sweep finished. Processed {len(results)} jobs and updated tracker.csv.")

if __name__ == '__main__':
    run_expansion()

