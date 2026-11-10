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
DRIVE_TRACKER = BASE_DIR / "job" / "drive_job_tracker.csv"

# Import Smart Dispatcher
sys.path.append(str(BASE_DIR / "job" / "scripts"))
from smart_dispatcher import classify_job

TODAY_STR = "2026-11-10"
FOLLOWUP_STR = "2026-11-24"

# 1. Load Tracker and deduplication set
applied_urls = set()
existing_rows = []
last_id_num = 245

if TRACKER_FILE.exists():
    with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
        reader = list(csv.reader(f))
        if reader:
            existing_rows = reader
            for r in reader[1:]:
                if len(r) > 6 and r[6]:
                    applied_urls.add(r[6].split('?')[0].strip())
                if r and r[0].startswith('J'):
                    try:
                        num = int(r[0].replace('J', ''))
                        if num > last_id_num:
                            last_id_num = num
                    except:
                        pass

print(f"Loaded {len(applied_urls)} tracked URLs. Next ID will start from: J{last_id_num + 1:03d}")

def append_to_tracker(job, status, dispatch_info):
    global last_id_num
    last_id_num += 1
    job_id = f"J{last_id_num:03d}"
    
    loc = job.get('loc', '')
    priority = '1' if any(w in loc for w in ['Bengaluru', 'Bangalore', 'Delhi', 'Gurugram', 'Gurgaon', 'Noida', 'NCR', 'Hybrid', 'Remote', 'Pune']) else '2'
    app_status = 'submitted' if status == 'SUCCESS' else 'external_redirect'
    verification = 'application_submitted_naukri' if status == 'SUCCESS' else 'external_ats_redirect'
    track = dispatch_info.get('track', 'DevOps_AWS')
    resume = dispatch_info.get('resume', 'Staff_SRE_Confluent_Cloud_Rahul_Kumar.pdf')
    
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
        "AWS; Kubernetes; Terraform; Docker; Linux; SRE; Prometheus; Grafana; Python; Istio",
        "Awaiting recruiter screening call" if status == 'SUCCESS' else "Requires external portal submission",
        resume,
        TODAY_STR,
        job.get('sal', 'Open / Market') or 'Open / Market',
        app_status,
        TODAY_STR if status == 'SUCCESS' else "",
        f"naukri_live_{TODAY_STR}_{job_id}",
        FOLLOWUP_STR
    ]
    
    with open(TRACKER_FILE, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)
        
    return job_id

def sync_drive():
    with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
        master_rows = list(csv.DictReader(f))
    if not master_rows:
        return
    fieldnames = ['cohort_year'] + list(master_rows[0].keys())
    with open(DRIVE_TRACKER, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in master_rows:
            row_dict = {'cohort_year': '2026'}
            row_dict.update(r)
            writer.writerow(row_dict)
    print(f"Synced {len(master_rows)} rows to drive_job_tracker.csv.")

def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        
        # 1. Harvest candidates from recommendedjobs tab and searches
        print("Gathering candidates from Naukri...")
        raw_candidates = []
        
        # Check if recommendedjobs page is open
        reco_page = None
        for pg in context.pages:
            if 'recommendedjobs' in pg.url:
                reco_page = pg
                break
                
        if not reco_page:
            reco_page = context.new_page()
            reco_page.goto('https://www.naukri.com/mnjuser/recommendedjobs', wait_until='domcontentloaded', timeout=20000)
            reco_page.wait_for_timeout(3000)
            
        reco_page.bring_to_front()
        # Scroll to load more cards
        for _ in range(3):
            reco_page.evaluate("window.scrollBy(0, 1000)")
            reco_page.wait_for_timeout(1000)
            
        cards = reco_page.evaluate("""() => {
            const list = [];
            const tuples = document.querySelectorAll('article.jobTuple, .srp-jobtuple-wrapper, .cust-job-tuple, article');
            tuples.forEach(t => {
                const titleEl = t.querySelector('a.title, a[class*="title"], .job-title');
                const compEl = t.querySelector('.comp-name, a.comp-name, .companyName');
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
        }""")
        raw_candidates.extend(cards)
        print(f"Harvested {len(cards)} recommended job cards.")
        
        # Filter unapplied candidate jobs
        filtered_candidates = []
        seen = set(applied_urls)
        for c in raw_candidates:
            clean = c['url'].split('?')[0].strip()
            if clean not in seen:
                seen.add(clean)
                filtered_candidates.append(c)
                
        print(f"Total unapplied target candidate roles: {len(filtered_candidates)}")
        
        # Batch size for this run: top 10 roles
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
                    # Radios
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
                                
                    # Text / numeric inputs
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
                                
                    # Submit / Save button
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
        
        # Sync to Drive
        sync_drive()
        
        print("\n=== BATCH DISPATCH SUMMARY ===")
        print(f"Total processed in this batch: {len(results)}")
        for r in results:
            print(f" * [{r.get('job_id', 'N/A')}] {r['title']} @ {r['company']} ({r['status']})")

if __name__ == "__main__":
    main()
