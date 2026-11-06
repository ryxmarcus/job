import sys
import csv
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TRACKER_FILE = r"C:\Users\rah_66160\iTopaz-agents\job\applications\tracker.csv"

with open(TRACKER_FILE, 'r', encoding='utf-8-sig') as f:
    rows = list(csv.reader(f))

pending = [(i, r[0], r[1], r[2], r[6].split('?')[0]) for i, r in enumerate(rows[1:], 1) if r[14] == 'external_redirect']

print(f"Checking {len(pending)} external redirect jobs using styles_jhc__apply-button-container selector...")

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    page = context.new_page()

    for idx, jid, company, title, url in pending:
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=20000)
            page.wait_for_timeout(2000)
            
            btn_info = page.evaluate("""() => {
                const c = document.querySelector('[class*="apply-button-container"], [class*="apply-button"], .apply-button');
                return {
                    text: c ? c.innerText.trim() : 'NONE',
                    html: c ? c.outerHTML.slice(0, 100) : ''
                };
            }""")
            print(f"[{jid}] {company} - {title[:30]}: Button Text = '{btn_info['text']}'")
        except Exception as e:
            print(f"[{jid}] {company}: Error {e}")

    page.close()

