import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    for page in browser.contexts[0].pages:
        if 'americanexpress' in page.url and 'apply' in page.url:
            print("=== AMEX FORM TEXT ===")
            print(page.inner_text('body'))
            print("\n=== Checkboxes ===")
            for cb in page.locator("input[type='checkbox']").all():
                print(f"  - Visible: {cb.is_visible()} | Checked: {cb.is_checked()}")
                if cb.is_visible() and not cb.is_checked():
                    cb.click()
                    print("  Clicked privacy checkbox!")
            
            # Re-click Next
            btn = page.locator("button:has-text('Next')")
            if btn.count() > 0:
                btn.first.click()
                page.wait_for_timeout(3000)
                print("AMEX URL after privacy consent:", page.url)
