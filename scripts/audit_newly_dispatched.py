import sys
import csv
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TRACKER_FILE = r"C:\Users\rah_66160\iTopaz-agents\job\applications\tracker.csv"
TODAY_STR = "2026-11-03"

with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

pending = [(i, r[0], r[1], r[2], r[6].split('?')[0]) for i, r in enumerate(rows[1:], 1) if r[14] == 'external_redirect']

print(f"Auditing {len(pending)} pending jobs on Naukri...")

updated = 0
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    page = context.new_page()

    for idx, jid, company, title, url in pending:
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=20000)
            page.wait_for_timeout(1800)
            
            btn_text = page.evaluate("""() => {
                const c = document.querySelector('[class*="apply-button-container"], [class*="apply-button"], .apply-button, button');
                return c ? c.innerText.trim() : '';
            }""").lower()
            
            if 'applied' in btn_text:
                rows[idx][14] = 'submitted'
                rows[idx][7] = 'application_submitted_naukri'
                rows[idx][10] = 'Awaiting recruiter screening call'
                rows[idx][15] = TODAY_STR
                updated += 1
                print(f"[{jid}] {company}: Confirmed APPLIED!")
            else:
                print(f"[{jid}] {company}: Button state = '{btn_text}'")
        except Exception as e:
            print(f"[{jid}] {company}: Error {e}")

    page.close()

if updated > 0:
    with open(TRACKER_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

print(f"\nAudit complete. Updated {updated} jobs to SUBMITTED in tracker.csv.")

