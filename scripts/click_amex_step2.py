import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    page = None
    for pg in context.pages:
        if 'americanexpress' in pg.url and 'section/2' in pg.url:
            page = pg
            break
            
    if page:
        print("Connected to AMEX Section 2...")
        next_btn = page.locator("button:has-text('Next'), button:has-text('Save and Continue')")
        print("Next buttons:", next_btn.count())
        for i in range(next_btn.count()):
            btn = next_btn.nth(i)
            print(f"  [{i}] '{btn.inner_text().strip()}' (Visible: {btn.is_visible()})")
            if btn.is_visible() and 'next' in btn.inner_text().lower():
                print(f"Clicking AMEX Step 2 Next button...")
                btn.click()
                page.wait_for_timeout(4000)
                print("AMEX Current URL after Step 2:", page.url)
                print("AMEX Current Title:", page.title())
                break

