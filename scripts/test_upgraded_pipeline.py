import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = Path(r"C:\Users\rah_66160\iTopaz-agents")
APP_DIR = BASE_DIR / "job" / "applications"
TRACKER_FILE = APP_DIR / "tracker.csv"

# Import our new Smart Dispatcher
sys.path.append(str(BASE_DIR / "job" / "scripts"))
from smart_dispatcher import classify_job

# Load past applied URLs to ensure 100% deduplication
applied_urls = set()
if TRACKER_FILE.exists():
    import csv
    with open(TRACKER_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for r in reader:
            if len(r) > 6 and r[6]:
                applied_urls.add(r[6].split('?')[0].strip())

print(f"Loaded {len(applied_urls)} tracked URLs to avoid any duplicate applications.")

SEARCHES = [
    ("SRE Bangalore & Remote", "https://www.naukri.com/site-reliability-engineer-jobs?k=site%20reliability%20engineer&experience=4"),
    ("AWS DevOps Pro", "https://www.naukri.com/aws-devops-engineer-jobs?k=aws%20devops%20engineer&experience=4"),
    ("Platform & Kubernetes", "https://www.naukri.com/kubernetes-devops-engineer-jobs?k=kubernetes%20devops%20engineer&experience=4")
]

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        
        # Find or create dedicated page
        page = context.new_page()

        # Step 1: Discover candidate jobs
        print("\n--- PHASE 1: SEARCH & SMART DISCOVERY ---")
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

        print(f"\nDiscovered {len(candidates)} brand new, unapplied candidate roles.")

        # Step 2: Apply Smart Dispatcher
        print("\n--- PHASE 2: SMART RESUME & TRACK CLASSIFICATION ---")
        test_batch = candidates[:5] if candidates else []
        for idx, job in enumerate(test_batch, 1):
            dispatch_info = classify_job(job['title'], job.get('desc', ''))
            job['dispatch'] = dispatch_info
            print(f"[{idx}] {job['title']} @ {job['company']}")
            print(f"    -> Track: {dispatch_info['track']} | Target Resume: {dispatch_info['resume']}")

        # Step 3: Execute Applications
        print("\n--- PHASE 3: APPLICATION EXECUTION ---")
        results = []
        for idx, job in enumerate(test_batch, 1):
            clean_url = job['url'].split('?')[0]
            print(f"\nProcessing [{idx}/{len(test_batch)}]: {job['title']} @ {job['company']} ({job['loc']})")
            try:
                page.goto(clean_url, wait_until='domcontentloaded', timeout=25000)
                page.wait_for_timeout(2000)

                already = page.evaluate("""() => {
                    const text = (document.body.innerText || '').toLowerCase();
                    return text.includes('already applied') || !!document.querySelector('.already-applied, [class*="alreadyApplied"]');
                }""")
                if already:
                    print("  -> Status: ALREADY_APPLIED")
                    results.append({**job, "status": "ALREADY_APPLIED"})
                    continue

                apply_btn = page.locator("#apply-button, .apply-button, button:has-text('Apply')")
                if apply_btn.count() == 0 or not apply_btn.first.is_visible():
                    comp_site = page.locator("text='Apply on company website'")
                    if comp_site.count() > 0:
                        print("  -> Status: EXTERNAL_PORTAL_REDIRECT")
                        results.append({**job, "status": "EXTERNAL_PORTAL_REDIRECT"})
                    else:
                        print("  -> Status: NO_DIRECT_BUTTON")
                        results.append({**job, "status": "NO_DIRECT_BUTTON"})
                    continue

                btn_text = apply_btn.first.inner_text().strip()
                print(f"  -> Clicking '{btn_text}' with Smart Track: {job['dispatch']['track']}...")
                apply_btn.first.click(timeout=5000)
                page.wait_for_timeout(2500)

                # Form & Chatbot handler
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
                if any(w in body_after for w in ['applied', 'success', 'submitted']):
                    print("  -> Status: SUCCESS (Application Confirmed)")
                    results.append({**job, "status": "SUCCESS"})
                else:
                    print("  -> Status: APPLIED_PENDING")
                    results.append({**job, "status": "APPLIED_PENDING"})

            except Exception as e:
                print(f"  -> Error: {e}")
                results.append({**job, "status": f"ERROR: {str(e)[:100]}"})

        page.close()

        # Step 4: Write Audit Test Report
        print("\n--- PHASE 4: AUDIT REPORT GENERATION ---")
        test_report = APP_DIR / "PIPELINE_TEST_RUN_20261102.json"
        test_report.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"Test run completed. Processed {len(results)} jobs.")
        for r in results:
            print(f"- {r['title']} @ {r['company']} -> {r['status']} [Track: {r['dispatch']['track']}]")

if __name__ == '__main__':
    run_test()

