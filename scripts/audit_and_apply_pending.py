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

# Load pending jobs from tracker
with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

headers = rows[0]
pending_indices = [i for i, r in enumerate(rows[1:], 1) if r[14] == 'external_redirect']

print(f"Loaded tracker. Found {len(pending_indices)} pending external redirect jobs to inspect & apply.")

TODAY_STR = "2026-11-03"

def run_pending_processor():
    updated_count = 0
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = context.new_page()

        for idx in pending_indices:
            row = rows[idx]
            job_id = row[0]
            company = row[1]
            title = row[2]
            url = row[6].split('?')[0].strip()

            print(f"\nProcessing [{job_id}] {title} @ {company}")
            print(f"  URL: {url}")

            try:
                page.goto(url, wait_until='domcontentloaded', timeout=25000)
                page.wait_for_timeout(2000)

                # Check if already applied
                body_text = page.inner_text('body').lower()
                is_already = page.evaluate("""() => {
                    const text = (document.body.innerText || '').toLowerCase();
                    const btn = document.querySelector('.already-applied, [class*="alreadyApplied"], #apply-button, .apply-button, button');
                    const btnText = btn ? btn.innerText.toLowerCase() : '';
                    return text.includes('already applied') || btnText === 'applied';
                }""")

                if is_already:
                    print("  -> Status: CONFIRMED_ALREADY_APPLIED on Naukri!")
                    row[14] = 'submitted'
                    row[7] = 'application_submitted_naukri'
                    row[10] = 'Awaiting recruiter screening call'
                    row[15] = TODAY_STR
                    updated_count += 1
                    continue

                # Look for Apply or Apply on company site button
                apply_btn = page.locator("#apply-button, .apply-button, button:has-text('Apply')")
                if apply_btn.count() > 0 and apply_btn.first.is_visible():
                    btn_text = apply_btn.first.inner_text().strip()
                    print(f"  -> Found button: '{btn_text}'. Clicking...")
                    
                    # Track if external page opens
                    new_tab = None
                    try:
                        with context.expect_page(timeout=4000) as new_page_info:
                            apply_btn.first.click()
                        new_tab = new_page_info.value
                    except:
                        pass

                    page.wait_for_timeout(2000)

                    # Handle chatbot / questionnaires if on same page
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

                    after_text = page.inner_text('body').lower()
                    if any(w in after_text for w in ['applied', 'success', 'submitted']):
                        print("  -> Status: SUCCESS (Application Confirmed)")
                        row[14] = 'submitted'
                        row[7] = 'application_submitted_naukri'
                        row[10] = 'Awaiting recruiter screening call'
                        row[15] = TODAY_STR
                        updated_count += 1
                    elif new_tab:
                        new_tab.wait_for_load_state('domcontentloaded', timeout=10000)
                        ext_url = new_tab.url
                        print(f"  -> Opened External ATS Tab: {ext_url[:80]}...")
                        row[10] = f"ATS URL: {ext_url[:120]}"
                        new_tab.close()
                    else:
                        print("  -> Status: PENDING / EXTERNAL")
                else:
                    print("  -> Status: NO_BUTTON")

            except Exception as e:
                print(f"  -> Error: {e}")

        page.close()

    # Save updated tracker
    with open(TRACKER_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"\nAudit complete. Successfully updated {updated_count} jobs to SUBMITTED in tracker.csv.")

if __name__ == '__main__':
    run_pending_processor()

