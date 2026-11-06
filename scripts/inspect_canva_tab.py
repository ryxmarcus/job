import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    found = False
    for page in browser.contexts[0].pages:
        if 'oauth/authorize' in page.url or 'Connect to Canva' in page.title():
            found = True
            print('URL:', page.url)
            print('Title:', page.title())
            print('\n=== Body Text ===\n', page.inner_text('body'))
            print('\n=== Clickable Elements ===')
            for b in page.locator('button, [role="button"], input[type="submit"]').all():
                try:
                    txt = b.inner_text().strip()
                    if txt:
                        print(f"  - Button/Role: '{txt}' (Visible: {b.is_visible()})")
                except: pass
    if not found:
        print("No matching Canva OAuth page found.")

