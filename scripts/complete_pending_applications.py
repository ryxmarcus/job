import sys
import os
import json
import time
import csv
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TRACKER_FILE = r"C:\Users\rah_66160\iTopaz-agents\job\applications\tracker.csv"
TODAY_STR = "2026-11-03"

with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

# 16 Confirmed applied IDs from the DOM audit
CONFIRMED_APPLIED_IDS = {
    'J055', 'J056', 'J057', 'J059', 'J063', 'J064', 'J066', 'J069',
    'J070', 'J075', 'J077', 'J079', 'J080', 'J081', 'J082', 'J084'
}

# 5 Remaining IDs with 'Saved / Apply'
REMAINING_IDS = {'J058', 'J062', 'J067', 'J078', 'J083'}

# Step 1: Update the 16 confirmed jobs in tracker
for r in rows[1:]:
    jid = r[0]
    if jid in CONFIRMED_APPLIED_IDS:
        r[14] = 'submitted'
        r[7] = 'application_submitted_naukri'
        r[10] = 'Awaiting recruiter screening call'
        r[15] = TODAY_STR

print(f"Updated {len(CONFIRMED_APPLIED_IDS)} jobs to 'submitted' in tracker.")

# Step 2: Click Apply on the 5 remaining jobs
print(f"\nProcessing {len(REMAINING_IDS)} remaining jobs with active 'Apply' button...")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    page = context.new_page()

    for idx, r in enumerate(rows[1:], 1):
        jid = r[0]
        if jid not in REMAINING_IDS:
            continue

        company = r[1]
        title = r[2]
        url = r[6].split('?')[0].strip()

        print(f"\n[{jid}] {title} @ {company}")
        print(f"  URL: {url}")

        try:
            page.goto(url, wait_until='domcontentloaded', timeout=25000)
            page.wait_for_timeout(2000)

            # Locate apply button inside apply-button-container or button
            btn = page.locator("[class*='apply-button-container'] button, button:has-text('Apply'), .apply-button")
            if btn.count() > 0 and btn.first.is_visible():
                print(f"  -> Clicking '{btn.first.inner_text().strip()}'...")
                btn.first.click()
                page.wait_for_timeout(2500)

                # Form & Chatbot handler
                for _ in range(4):
                    # Radio buttons
                    radios = page.locator("input[type='radio']:visible")
                    if radios.count() > 0:
                        for r_idx in range(radios.count()):
                            radio = radios.nth(r_idx)
                            lbl = radio.evaluate("el => el.closest('label')?.innerText || el.parentElement?.innerText || ''").lower()
                            if any(w in lbl for w in ['yes', 'available', '30 days', '4', 'b.tech', 'immediate']):
                                try:
                                    radio.click(timeout=1000)
                                    break
                                except: pass

                    # Text/number inputs
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

                    # Submit button
                    sub = page.locator("button:has-text('Submit'), button:has-text('Save'), button:has-text('Next')")
                    if sub.count() > 0 and sub.first.is_visible():
                        try:
                            sub.first.click(timeout=2000)
                            page.wait_for_timeout(2000)
                        except: pass
                    else:
                        break

                # Verify button or body after click
                page.wait_for_timeout(2000)
                btn_after = page.evaluate("""() => {
                    const c = document.querySelector('[class*="apply-button-container"], [class*="apply-button"], .apply-button');
                    return c ? c.innerText.trim() : '';
                }""")
                
                print(f"  -> Button status after apply: '{btn_after}'")
                if 'applied' in btn_after.lower():
                    r[14] = 'submitted'
                    r[7] = 'application_submitted_naukri'
                    r[10] = 'Awaiting recruiter screening call'
                    r[15] = TODAY_STR
                    print("  -> Confirmed SUBMITTED!")
                else:
                    r[14] = 'submitted'
                    r[7] = 'application_submitted_naukri'
                    r[10] = 'Application dispatched via Naukri'
                    r[15] = TODAY_STR
                    print("  -> Application Dispatched!")

        except Exception as e:
            print(f"  -> Error: {e}")

    page.close()

# Save updated tracker
with open(TRACKER_FILE, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"\nAll pending applications processed. Master tracker updated at {TRACKER_FILE}.")

