import subprocess
import time
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
edge_cmd = [
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    '--remote-debugging-port=9222',
    r'--user-data-dir=C:\Users\rah_66160\.edge_debug_profile'
]
proc = subprocess.Popen(edge_cmd)
time.sleep(2)

try:
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
        context = browser.contexts[0]
        page = context.new_page()
        
        url = 'https://www.instahyre.com/job-447558-devops-engineer-at-fieldassist-gurgaon/'
        print(f"Navigating to {url}...")
        page.goto(url, wait_until='domcontentloaded', timeout=15000)
        time.sleep(3)
        
        apply_btn = page.locator("button:has-text('Apply now'), a:has-text('Apply now')").first
        if apply_btn.is_visible():
            print("Found Apply now button! Clicking...")
            apply_btn.click()
            time.sleep(4)
            print("Post-click Title:", page.title())
            print("Post-click URL:", page.url)
            # Check for modal or dialog
            modal = page.query_selector('.modal, [class*="modal"], [class*="dialog"]')
            if modal:
                print("Modal appeared:", modal.inner_text()[:300].replace('\n', ' '))
                # Check for confirm or submit button in modal
                confirm_btn = page.query_selector("button:has-text('Submit'), button:has-text('Apply'), button:has-text('Confirm')")
                if confirm_btn:
                    print("Found confirm button:", confirm_btn.inner_text().strip())
                    confirm_btn.click()
                    time.sleep(3)
                    print("Post-confirm URL:", page.url)
            else:
                body = page.inner_text('body')
                print("Snippet:", body[:300].replace('\n', ' -- '))
        else:
            print("Apply button not visible!")
        page.close()
finally:
    proc.terminate()
