import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context = browser.contexts[0]
    
    # Check AMEX tab
    for page in context.pages:
        if 'americanexpress' in page.url and 'apply' in page.url:
            print("Found AMEX Apply Tab:", page.url)
            page.wait_for_timeout(2000)
            email_inp = page.locator("input[type='email'], input[name*='email' i], input[id*='email' i]")
            print(f"AMEX Email Inputs found: {email_inp.count()}")
            if email_inp.count() > 0 and email_inp.first.is_visible():
                print("Filling AMEX Email: rk58743k@gmail.com")
                email_inp.first.fill("rk58743k@gmail.com")
                page.wait_for_timeout(1000)
                
            next_btn = page.locator("button:has-text('Next'), button:has-text('Continue'), button:has-text('Submit'), [type='submit']")
            print(f"AMEX Next/Submit Buttons: {next_btn.count()}")
            for i in range(next_btn.count()):
                t = next_btn.nth(i).inner_text().strip()
                print(f"  Button {i}: '{t}'")
            if next_btn.count() > 0 and next_btn.first.is_visible():
                print(f"Clicking AMEX button '{next_btn.first.inner_text().strip()}'...")
                next_btn.first.click()
                page.wait_for_timeout(3000)
                print("AMEX URL after next:", page.url)
