import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    for page in browser.contexts[0].pages:
        if 'americanexpress' in page.url and 'apply' in page.url:
            print("Checking AMEX terms box via JS and label...")
            page.evaluate("""() => {
                const cb = document.querySelector('input[type="checkbox"]');
                if (cb) {
                    cb.checked = true;
                    cb.dispatchEvent(new Event('change', { bubbles: true }));
                }
                const lbl = Array.from(document.querySelectorAll('label, span')).find(el => el.innerText && el.innerText.includes('terms and conditions'));
                if (lbl) lbl.click();
            }""")
            page.wait_for_timeout(1000)
            
            btn = page.locator("button:has-text('Next')")
            if btn.count() > 0:
                print("Clicking Next after checking terms...")
                btn.first.click()
                page.wait_for_timeout(4000)
                print("New AMEX URL:", page.url)
                print("New AMEX Title:", page.title())
                print("Body Preview:", page.inner_text('body')[:300])
